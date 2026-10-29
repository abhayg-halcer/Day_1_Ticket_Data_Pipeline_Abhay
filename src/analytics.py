"""Analytics and CSV exports for cleaned support ticket data."""

from pathlib import Path
from typing import Any

import pandas as pd


class TicketAnalytics:
    """Calculate summary metrics and grouped ticket analytics."""

    UNRESOLVED_STATUSES = {"Open", "In Progress"}

    def __init__(self, cleaned_df: pd.DataFrame):
        self.df = cleaned_df.copy(deep=True)

    @staticmethod
    def _rounded_mean(series: pd.Series) -> float | None:
        mean = series.mean()
        return round(float(mean), 2) if pd.notna(mean) else None

    def summary_metrics(self) -> dict[str, Any]:
        """Return overall metrics; unresolved includes Open and In Progress."""
        return {
            "total_tickets": int(len(self.df)),
            "average_resolution_time_hours": self._rounded_mean(self.df["resolution_time_hours"]),
            "average_customer_rating": self._rounded_mean(self.df["customer_rating"]),
            "open_tickets": int(self.df["status"].eq("Open").sum()),
            "unresolved_tickets": int(self.df["status"].isin(self.UNRESOLVED_STATUSES).sum()),
            "missing_resolution_times": int(self.df["resolution_time_hours"].isna().sum()),
            "missing_customer_ratings": int(self.df["customer_rating"].isna().sum()),
        }

    def tickets_by_category(self) -> pd.DataFrame:
        return (self.df.assign(category=self.df["category"].fillna("").replace("", "Missing"))
                .groupby("category", dropna=False).size().reset_index(name="ticket_count")
                .sort_values("category", kind="stable").reset_index(drop=True))

    def average_resolution_time_by_category(self) -> pd.DataFrame:
        """Calculate average resolution time for each category."""
        frame = self.df.copy()

        frame["category"] = (
            frame["category"].fillna("").replace("", "Missing")
        )

        # Ensure missing values are represented as numeric NaN.
        frame["resolution_time_hours"] = pd.to_numeric(
            frame["resolution_time_hours"], errors="coerce"
        )

        result = (
            frame.groupby("category", dropna=False)["resolution_time_hours"]
            .mean()
            .round(2)
            .reset_index(name="average_resolution_time_hours")
        )

        return result.sort_values(
            "category", kind="stable"
        ).reset_index(drop=True)

    def tickets_by_priority(self) -> pd.DataFrame:
        return (self.df.assign(priority=self.df["priority"].fillna("").replace("", "Missing"))
                .groupby("priority", dropna=False).size().reset_index(name="ticket_count")
                .sort_values("priority", kind="stable").reset_index(drop=True))

    def tickets_by_status(self) -> pd.DataFrame:
        return (self.df.assign(status=self.df["status"].fillna("").replace("", "Missing"))
                .groupby("status", dropna=False).size().reset_index(name="ticket_count")
                .sort_values("status", kind="stable").reset_index(drop=True))

    def export_results(self, output_dir: str | Path) -> None:
        """Export summary, breakdowns, and category-level resolution averages."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        summary = pd.DataFrame(list(self.summary_metrics().items()), columns=["metric", "value"])
        summary.to_csv(output_path / "summary_metrics.csv", index=False)
        self.tickets_by_category().to_csv(output_path / "tickets_by_category.csv", index=False)
        self.tickets_by_priority().to_csv(output_path / "tickets_by_priority.csv", index=False)
        self.tickets_by_status().to_csv(output_path / "tickets_by_status.csv", index=False)
        self.average_resolution_time_by_category().to_csv(
            output_path / "average_resolution_time_by_category.csv", index=False
        )
