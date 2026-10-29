"""Run the ticket data pipeline from the repository root."""
from pathlib import Path

from src.analytics import TicketAnalytics
from src.data_processor import TicketDataProcessor

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "tickets.csv"
OUTPUT_DIR = BASE_DIR / "outputs"


def main() -> None:
    processor = TicketDataProcessor(DATA_PATH)
    raw_df = processor.load_data()
    cleaned_df = processor.clean_data(raw_df)

    print("=== Data Quality ===")
    for key, value in processor.quality_report.items():
        print(f"{key}: {value}")
    print("\n=== Row-Level Quality Issues ===")
    if processor.quality_issues.empty:
        print("No row-level issues found.")
    else:
        print(processor.quality_issues.to_string(index=False))

    analytics = TicketAnalytics(cleaned_df)
    print("\n=== Summary Metrics ===")
    for key, value in analytics.summary_metrics().items():
        print(f"{key}: {value}")
    print("\n=== Tickets by Category ===")
    print(analytics.tickets_by_category().to_string(index=False))
    print("\n=== Average Resolution Time by Category ===")
    print(analytics.average_resolution_time_by_category().to_string(index=False))
    print("\n=== Tickets by Priority ===")
    print(analytics.tickets_by_priority().to_string(index=False))
    print("\n=== Tickets by Status ===")
    print(analytics.tickets_by_status().to_string(index=False))

    analytics.export_results(OUTPUT_DIR)
    processor.quality_issues.to_csv(OUTPUT_DIR / "quality_issues.csv", index=False)
    print(f"\nAnalytics and quality reports saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
