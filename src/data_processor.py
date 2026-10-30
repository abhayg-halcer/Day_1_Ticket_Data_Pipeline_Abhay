"""Load, validate, and clean customer-support ticket CSV data."""

from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd


class TicketDataProcessor:
    """Load ticket records and apply documented data-quality rules.

    Cleaning contract:
    - The input DataFrame is never modified; a deep copy is cleaned.
    - For duplicate non-empty ticket IDs, keep the first row and drop later rows.
    - Rows with missing ticket IDs are retained and flagged for investigation.
    - Missing numeric values remain NaN; present but invalid values become NaN
      and are flagged in ``quality_issues``.
    - Unknown priority/status values are retained but flagged, not silently
      rewritten or dropped.
    """

    REQUIRED_COLUMNS = {
        "ticket_id",
        "category",
        "priority",
        "description",
        "resolution_time_hours",
        "customer_rating",
        "status",
    }
    VALID_PRIORITIES = {"Low", "Medium", "High", "Critical"}
    VALID_STATUSES = {"Open", "In Progress", "Resolved", "Closed"}

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.quality_report: dict[str, Any] = {}
        self.quality_issues = pd.DataFrame()

    def load_data(self) -> pd.DataFrame:
        """Load CSV data or raise a clear error for missing/invalid/empty files."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Ticket CSV not found: {self.file_path}")
        try:
            df = pd.read_csv(self.file_path)
        except pd.errors.EmptyDataError as exc:
            raise ValueError("The CSV is empty or has no header.") from exc
        except pd.errors.ParserError as exc:
            raise ValueError("The CSV has an invalid structure.") from exc
        if df.empty:
            raise ValueError("The CSV contains no ticket records.")
        self.validate_columns(df)
        return df

    def validate_columns(self, df: pd.DataFrame) -> bool:
        """Raise ValueError if any required ticket column is missing."""
        missing_columns = self.REQUIRED_COLUMNS - set(df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Missing required columns: {missing}")
        return True

    def clean_data(self, raw_df: pd.DataFrame) -> pd.DataFrame:
        """Return cleaned data and store aggregate plus row-level quality issues."""
        self.validate_columns(raw_df)
        cleaned = raw_df.copy(deep=True)
        original_index = cleaned.index

        text_columns = ["ticket_id", "category", "priority", "description", "status"]
        for column in text_columns:
            cleaned[column] = cleaned[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )

        ticket_id = cleaned["ticket_id"]
        missing_id_mask = ticket_id.isna() | ticket_id.eq("")
        duplicate_mask = (
            ~missing_id_mask & ticket_id.duplicated(keep="first")
        )

        resolution_raw = cleaned["resolution_time_hours"]
        rating_raw = cleaned["customer_rating"]
        resolution_missing = resolution_raw.isna() | resolution_raw.astype("string").str.strip().eq("")
        rating_missing = rating_raw.isna() | rating_raw.astype("string").str.strip().eq("")
        resolution_numeric = pd.to_numeric(resolution_raw, errors="coerce")
        rating_numeric = pd.to_numeric(rating_raw, errors="coerce")

        invalid_resolution_mask = (
            (~resolution_missing & resolution_numeric.isna())
            | (
                resolution_numeric.notna()
                & (
                    ~np.isfinite(resolution_numeric)
                    | resolution_numeric.lt(0)
                )
            )
        )
        invalid_rating_mask = (
            (~rating_missing & rating_numeric.isna())
            | (rating_numeric.notna() & ~rating_numeric.between(1, 5))
        )
        resolution_numeric = resolution_numeric.mask(invalid_resolution_mask)
        rating_numeric = rating_numeric.mask(invalid_rating_mask)
        cleaned["resolution_time_hours"] = resolution_numeric
        cleaned["customer_rating"] = rating_numeric

        priority_unknown_mask = (
            cleaned["priority"].notna()
            & cleaned["priority"].ne("")
            & ~cleaned["priority"].isin(self.VALID_PRIORITIES)
        )
        status_unknown_mask = (
            cleaned["status"].notna()
            & cleaned["status"].ne("")
            & ~cleaned["status"].isin(self.VALID_STATUSES)
        )

        issue_rows: list[dict[str, Any]] = []
        masks = {
            "missing_ticket_id": missing_id_mask,
            "missing_category": cleaned["category"].isna() | cleaned["category"].eq(""),
            "missing_priority": cleaned["priority"].isna() | cleaned["priority"].eq(""),
            "missing_description": cleaned["description"].isna() | cleaned["description"].eq(""),
            "missing_status": cleaned["status"].isna() | cleaned["status"].eq(""),
            "missing_resolution_time": resolution_missing,
            "missing_customer_rating": rating_missing,
            "duplicate_ticket_id_dropped": duplicate_mask,
            "invalid_resolution_time": invalid_resolution_mask,
            "invalid_customer_rating": invalid_rating_mask,
            "unrecognized_priority": priority_unknown_mask,
            "unrecognized_status": status_unknown_mask,
        }
        for issue_name, mask in masks.items():
            for index in original_index[mask.to_numpy()]:
                issue_rows.append({
                    "source_row_index": int(index),
                    "ticket_id": raw_df.loc[index, "ticket_id"] if "ticket_id" in raw_df else None,
                    "issue": issue_name,
                    "action": (
                        "drop later duplicate; keep first"
                        if issue_name == "duplicate_ticket_id_dropped"
                        else "retain and flag"
                    ) if issue_name != "invalid_resolution_time" and issue_name != "invalid_customer_rating"
                    else "replace invalid numeric value with NaN and flag",
                })
        self.quality_issues = pd.DataFrame(
            issue_rows,
            columns=["source_row_index", "ticket_id", "issue", "action"],
        )

        self.quality_report = {
            "raw_row_count": int(len(raw_df)),
            "cleaned_row_count": int(len(cleaned) - int(duplicate_mask.sum())),
            "duplicate_ids": cleaned.loc[duplicate_mask, "ticket_id"].tolist(),
            "duplicate_row_count": int(duplicate_mask.sum()),
            "missing_ticket_id_count": int(missing_id_mask.sum()),
            "invalid_resolution_time_count": int(invalid_resolution_mask.sum()),
            "invalid_customer_rating_count": int(invalid_rating_mask.sum()),
            "unrecognized_priorities": sorted(cleaned.loc[priority_unknown_mask, "priority"].dropna().unique().tolist()),
            "unrecognized_statuses": sorted(cleaned.loc[status_unknown_mask, "status"].dropna().unique().tolist()),
            "raw_missing_values_by_column": raw_df.isna().sum().astype(int).to_dict(),
            "cleaned_missing_values_by_column": cleaned.loc[~duplicate_mask].isna().sum().astype(int).to_dict(),
            "row_level_issue_count": int(len(self.quality_issues)),
            "duplicate_policy": "Keep first occurrence of each non-empty ticket_id; drop later duplicates.",
            "missing_id_policy": "Retain rows with missing IDs and flag them for investigation.",
        }
        return cleaned.loc[~duplicate_mask].copy()
