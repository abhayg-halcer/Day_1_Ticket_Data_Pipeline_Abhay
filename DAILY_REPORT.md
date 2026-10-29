# Day 01 Daily Report — Ticket Data Pipeline

> Before submitting, fill in the GitHub repository URL, commit hash/PR, and your own name/date. Do not claim a remote commit exists until you have pushed it.

- **Developer:** Abhay Gour
- **Assignment:** Day 01 — Python Engineering & Ticket Data Pipeline
- **Date:** 2026-10-29
- **Repository URL:** [Paste your GitHub repository URL]
- **Commit hash / Pull Request:** [Paste after committing and pushing]

## Objective
Build a reproducible CSV data pipeline that validates and cleans support-ticket data, calculates required metrics, exports reports, and verifies behavior with automated tests.

## Work completed in this resubmission
- Aligned imports and package structure using `src/` and `tests/`.
- Added `main.py` as the executable entry point and `requirements.txt` for dependencies.
- Added category-wise average resolution time.
- Defined unresolved tickets as `Open` plus `In Progress`.
- Added row-level quality issue traceability and documented the duplicate/missing/invalid-data policy.
- Expanded automated coverage for loading errors, missing columns, duplicate IDs, invalid numeric values, missing IDs, analytics, and exports.
- Updated README commands and project structure.

## Verification
- **Test command:** `python -m pytest -v`
- **Test result:** See `evidence/test_output.txt` (regenerate after any code changes).
- **Manual metric checks:** See `evidence/manual_metric_checks.md`.

## What I learned
## What I learned

I learned how to organize a Python project using separate modules for data processing and analytics, and how to test the pipeline using pytest. In the first submission, some required analytics and project structure were incomplete, and one test failed because missing resolution-time values were not handled correctly. I corrected the project structure, improved the category-wise average resolution-time calculation to handle missing values, and verified that all 15 tests passed successfully.

## Remaining submission actions
- [ ] Commit and push the corrected project to GitHub.
- [ ] Replace the repository URL and commit/PR placeholders above.
- [ ] Review the terminal test output and capture any evidence required by the trainer.
- [ ] Explain the category-average and unresolved-ticket calculations in your own words before the viva.
