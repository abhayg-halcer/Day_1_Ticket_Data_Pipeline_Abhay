# Manual Verification — Day 01 Ticket Pipeline

These checks were calculated from `data/tickets.csv` after applying the documented cleaning policy (keep the first occurrence of a non-empty ticket ID; drop later duplicates; convert invalid numeric values to missing).

## Check 1 — Average resolution time for Billing

Valid Billing resolution times after duplicate removal and invalid-value cleaning:

`4.5, 12.0, 1.5, 7.0, 9.0, 3.5, 4.5`

- Sum = `42.0` hours
- Number of valid values = `7`
- Average = `42.0 / 7 = 6.00` hours
- Program output: `Billing = 6.00` hours

The invalid/missing resolution value is excluded from the average rather than treated as zero.

## Check 2 — Average resolution time for Technical

Valid Technical resolution times:

`8.0, 6.5, 18.0, 5.0, 6.0, 8.5, 10.0`

- Sum = `62.0` hours
- Number of valid values = `7`
- Average = `62.0 / 7 = 8.857...`, rounded to `8.86` hours
- Program output: `Technical = 8.86` hours

## Additional cross-check — row counts and unresolved status

- Raw records = `24`
- Duplicate ID `T021`: one later duplicate row is removed
- Cleaned records = `23`
- In the supplied dataset, `Open = 5` and `In Progress = 0`, so unresolved = `5 + 0 = 5`.
- The automated analytics tests separately include both `Open` and `In Progress`, and verify that both count as unresolved while `Resolved` and `Closed` do not.

## Reproduce the checks

From the project root, run:

```bash
python main.py
python -m pytest -v
```
