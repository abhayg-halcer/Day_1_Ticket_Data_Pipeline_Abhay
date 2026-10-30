# Day 01 Daily Report — Ticket Data Pipeline

- **Developer:** Abhay Gour
- **Assignment:** Day 01 — Python Engineering & Ticket Data Pipeline
- **Date:** 2026-10-29
- **Repository URL:** https://github.com/abhayg-halcer/Day_1_Ticket_Data_Pipeline_Abhay
- **Latest commit hash:** `9a26579`
- **Pull Request:** N/A — no pull request created

## Objective

Build a reproducible CSV data pipeline that validates and cleans support-ticket data, calculates required metrics, exports reports, and verifies behavior with automated tests.

## Work completed in this resubmission

- Aligned imports and package structure using `src/` and `tests/`.
- Added `main.py` as the executable entry point and `requirements.txt` for dependencies.
- Added category-wise average resolution-time analytics.
- Defined unresolved tickets as `Open` plus `In Progress`.
- Added row-level quality issue traceability and documented the duplicate, missing, and invalid-data policy.
- Expanded automated tests covering loading errors, missing columns, duplicate IDs, invalid numeric values, missing IDs, analytics, and exports.
- Updated README commands and project structure.
- Added a test verifying that unresolved-ticket analytics include both `Open` and `In Progress`.

## Verification

- **Test command:** `python3 -m pytest -v`
- **Test result:** 16 tests passed.
- **Test evidence:** `evidence/test_output.txt`
- **Manual metric checks:** `evidence/manual_metric_checks.md`

## What I learned

I learned how to organize a Python project using separate modules for data processing and analytics, and how to test a pipeline using pytest. During the resubmission, I corrected the project structure and imports, implemented category-wise average resolution-time analytics, and improved handling of missing resolution-time values. I also added a test to verify that unresolved-ticket counts include both `Open` and `In Progress` statuses. The final automated test run completed successfully with all 16 tests passing.

## Resubmission status

- [x] Corrected the project structure and package imports.
- [x] Added the pipeline entry point and dependency file.
- [x] Implemented category-wise average resolution-time analytics.
- [x] Verified unresolved-ticket logic for `Open` and `In Progress`.
- [x] Ran the automated test suite: 16 tests passed.
- [x] Updated and pushed `evidence/test_output.txt` to GitHub.
- [x] Pushed the latest code and test evidence to GitHub.

## Final checks before submission

- [x] Verify that `evidence/manual_metric_checks.md` contains two accurate manual calculations matching the pipeline outputs.
- [x] Verify that `README.md` and all generated output files are up to date.
- [x] Confirm the GitHub repository contains the latest files.
- [x] Review the category-average and unresolved-ticket calculations before the viva.
