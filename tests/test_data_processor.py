import pandas as pd
import pytest

from src.data_processor import TicketDataProcessor


COLUMNS = [
    "ticket_id", "category", "priority", "description",
    "resolution_time_hours", "customer_rating", "status",
]


def sample_df():
    return pd.DataFrame([
        ["T001", " Billing ", "High", "Invoice", "4.5", "4", "Resolved"],
        ["T002", "Technical", "Low", "Login", "6", "2", "Open"],
    ], columns=COLUMNS)


def test_load_data_returns_dataframe_and_expected_rows():
    processor = TicketDataProcessor("data/tickets.csv")
    df = processor.load_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 24
    assert set(COLUMNS).issubset(df.columns)


def test_load_data_missing_file_raises_file_not_found():
    with pytest.raises(FileNotFoundError, match="Ticket CSV not found"):
        TicketDataProcessor("data/does_not_exist.csv").load_data()


def test_load_data_empty_file_raises_value_error(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("")
    with pytest.raises(ValueError, match="empty or has no header"):
        TicketDataProcessor(path).load_data()


def test_load_data_header_only_file_raises_value_error(tmp_path):
    path = tmp_path / "header_only.csv"
    path.write_text(",".join(COLUMNS) + "\n")
    with pytest.raises(ValueError, match="no ticket records"):
        TicketDataProcessor(path).load_data()


def test_validate_columns_rejects_missing_required_columns():
    processor = TicketDataProcessor("unused.csv")
    with pytest.raises(ValueError, match="Missing required columns"):
        processor.validate_columns(pd.DataFrame({"ticket_id": ["T001"]}))


def test_clean_data_removes_later_duplicate_and_keeps_first():
    processor = TicketDataProcessor("unused.csv")
    raw = pd.concat([sample_df(), sample_df().iloc[[0]]], ignore_index=True)
    cleaned = processor.clean_data(raw)
    assert len(cleaned) == 2
    assert cleaned["ticket_id"].tolist() == ["T001", "T002"]
    assert processor.quality_report["duplicate_row_count"] == 1


def test_clean_data_does_not_modify_raw_dataframe():
    processor = TicketDataProcessor("unused.csv")
    raw = sample_df()
    original = raw.copy(deep=True)
    processor.clean_data(raw)
    pd.testing.assert_frame_equal(raw, original)


def test_clean_data_converts_invalid_numeric_values_and_flags_them():
    processor = TicketDataProcessor("unused.csv")
    raw = sample_df()
    raw.loc[0, "resolution_time_hours"] = "not-a-number"
    raw.loc[1, "customer_rating"] = 8
    cleaned = processor.clean_data(raw)
    assert pd.isna(cleaned.loc[0, "resolution_time_hours"])
    assert pd.isna(cleaned.loc[1, "customer_rating"])
    assert processor.quality_report["invalid_resolution_time_count"] == 1
    assert processor.quality_report["invalid_customer_rating_count"] == 1


def test_clean_data_retains_and_flags_missing_ticket_id():
    processor = TicketDataProcessor("unused.csv")
    raw = sample_df()
    raw.loc[0, "ticket_id"] = None
    cleaned = processor.clean_data(raw)
    assert len(cleaned) == 2
    assert processor.quality_report["missing_ticket_id_count"] == 1
    assert "missing_ticket_id" in processor.quality_issues["issue"].tolist()

@pytest.mark.parametrize("invalid_value", ["inf", "-inf"])
def test_clean_data_rejects_infinite_resolution_times(invalid_value):
    processor = TicketDataProcessor("unused.csv")
    raw = sample_df()
    raw.loc[0, "resolution_time_hours"] = invalid_value

    cleaned = processor.clean_data(raw)

    assert pd.isna(cleaned.loc[0, "resolution_time_hours"])
    assert processor.quality_report["invalid_resolution_time_count"] == 1
    assert "invalid_resolution_time" in processor.quality_issues["issue"].tolist()


def test_clean_data_keeps_finite_non_negative_resolution_time():
    processor = TicketDataProcessor("unused.csv")
    raw = sample_df()

    cleaned = processor.clean_data(raw)

    assert cleaned.loc[0, "resolution_time_hours"] == 4.5
    assert cleaned.loc[1, "resolution_time_hours"] == 6.0
    assert processor.quality_report["invalid_resolution_time_count"] == 0

def test_load_data_malformed_csv_raises_value_error(tmp_path):
    path = tmp_path / "malformed.csv"
    path.write_text(
        'ticket_id,category,priority\n'
        '"T001,Billing,High\n'
    )

    processor = TicketDataProcessor(path)

    with pytest.raises(ValueError, match="invalid structure"):
        processor.load_data()