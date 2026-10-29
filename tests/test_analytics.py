import pandas as pd

from src.analytics import TicketAnalytics


def sample_df():
    return pd.DataFrame({
        "ticket_id": ["T001", "T002", "T003", "T004"],
        "category": ["Billing", "Technical", "Billing", None],
        "priority": ["High", "Low", "Medium", "Critical"],
        "description": ["Invoice", "Login", "Refund", "Account"],
        "resolution_time_hours": [4.0, 6.0, None, 2.0],
        "customer_rating": [4, 2, 5, 3],
        "status": ["Resolved", "Open", "In Progress", "Closed"],
    })


def test_summary_metrics_includes_missing_values_and_unresolved_statuses():
    summary = TicketAnalytics(sample_df()).summary_metrics()
    assert summary["total_tickets"] == 4
    assert summary["average_resolution_time_hours"] == 4.0
    assert summary["average_customer_rating"] == 3.5
    assert summary["open_tickets"] == 1
    assert summary["unresolved_tickets"] == 2
    assert summary["missing_resolution_times"] == 1
    assert summary["missing_customer_ratings"] == 0


def test_average_resolution_time_by_category():
    result = TicketAnalytics(sample_df()).average_resolution_time_by_category()
    averages = dict(zip(result["category"], result["average_resolution_time_hours"]))
    assert averages["Billing"] == 4.0  # Missing resolution time is excluded.
    assert averages["Technical"] == 6.0
    assert averages["Missing"] == 2.0


def test_ticket_counts_by_category_includes_missing_category():
    result = TicketAnalytics(sample_df()).tickets_by_category()
    counts = dict(zip(result["category"], result["ticket_count"]))
    assert counts["Billing"] == 2
    assert counts["Technical"] == 1
    assert counts["Missing"] == 1


def test_unresolved_count_excludes_resolved_and_closed():
    df = sample_df()
    result = TicketAnalytics(df).summary_metrics()
    assert result["unresolved_tickets"] == int(df["status"].isin({"Open", "In Progress"}).sum())
    assert result["unresolved_tickets"] == 2


def test_export_results_writes_all_expected_csv_files(tmp_path):
    analytics = TicketAnalytics(sample_df())
    analytics.export_results(tmp_path)
    expected = {
        "summary_metrics.csv",
        "tickets_by_category.csv",
        "tickets_by_priority.csv",
        "tickets_by_status.csv",
        "average_resolution_time_by_category.csv",
    }
    assert expected.issubset({p.name for p in tmp_path.iterdir()})
    summary = pd.read_csv(tmp_path / "summary_metrics.csv")
    assert {"metric", "value"}.issubset(summary.columns)


def test_all_missing_resolution_values_return_none_overall_and_nan_by_category():
    df = sample_df()
    df["resolution_time_hours"] = None
    analytics = TicketAnalytics(df)
    assert analytics.summary_metrics()["average_resolution_time_hours"] is None
    assert analytics.average_resolution_time_by_category()["average_resolution_time_hours"].isna().all()
