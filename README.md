# Customer Support Ticket Data Pipeline

## Overview

A small Python/pandas project that loads customer-support tickets from CSV, validates required columns, cleans invalid numeric values, records data-quality issues, calculates analytics, and exports reports.

## Project structure

```text
Day_1_Ticket_Data_Pipeline_RESUBMISSION/
├── data/
│   └── tickets.csv
├── src/
│   ├── __init__.py
│   ├── data_processor.py
│   └── analytics.py
├── tests/
│   ├── test_data_processor.py
│   └── test_analytics.py
├── outputs/                 # Created/populated by main.py
├── evidence/
│   ├── manual_metric_checks.md
│   └── test_output.txt
├── main.py
├── requirements.txt
├── DAILY_REPORT.md
├── README.md
└── .gitignore
```

## Requirements

- Python 3.10 or newer recommended
- pandas
- pytest

## Setup on macOS

Open Terminal in this project folder and run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run the pipeline

From the project root directory:

```bash
python main.py
```

The program prints data-quality findings and analytics. It writes these CSV reports into `outputs/`:

- `summary_metrics.csv`
- `tickets_by_category.csv`
- `tickets_by_priority.csv`
- `tickets_by_status.csv`
- `average_resolution_time_by_category.csv`
- `quality_issues.csv`

## Run tests

From the project root directory:

```bash
python -m pytest -v
```

The tests cover CSV loading and errors, required-column validation, duplicate handling, raw-data preservation, invalid numeric values, missing IDs, summary metrics, category-level resolution averages, unresolved statuses, and report exports.

## Data-cleaning policy

1. The raw DataFrame is not modified; cleaning works on a deep copy.
2. If a non-empty `ticket_id` appears more than once, the first row is retained and later duplicates are removed.
3. Rows with missing/blank ticket IDs are retained and flagged for investigation; they are not treated as duplicates.
4. Missing numeric values remain missing. Present but unparseable resolution times, negative resolution times, and ratings outside 1–5 are converted to missing values and recorded as row-level issues.
5. Unknown priority/status values are retained and flagged rather than silently discarded.
6. Missing category values are displayed as `Missing` in category reports.
7. Category average resolution time ignores missing/invalid resolution values. If a category has no valid resolution values, its average is blank/NaN.
8. Unresolved tickets are statuses `Open` and `In Progress`. `Resolved` and `Closed` are not unresolved.

## Sample dataset

The supplied CSV has 24 raw records. The cleaning policy removes later occurrences of duplicate non-empty ticket IDs; the pipeline reports raw and cleaned counts when run. Do not edit the raw CSV just to make the tests pass.

## Resubmission evidence

See `DAILY_REPORT.md` and `evidence/manual_metric_checks.md`. After committing the corrected files to your own GitHub repository, update the Git commit/PR details in `DAILY_REPORT.md` and include a screenshot or copied terminal output from your own run if your trainer requires it.
