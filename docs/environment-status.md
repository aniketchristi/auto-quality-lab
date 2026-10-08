# Environment verification — October 8, 2026

The first working environment is installed and populated.

- Python 3.12.14; dependencies installed in the project's virtual environment and pinned in requirements.lock.txt.
- PostgreSQL 18.6 running on loopback port 55432 with a project-owned cluster.
- 60 NHTSA API response snapshots: complaints and recalls for 30 model-year combinations.
- 8,622 distinct complaints; 12,777 complaint/component assignments.
- 53 distinct recall campaigns; 107 campaign/model-year relationships.
- 62 source reconciliation and integrity checks passed.
- Thirteen automated tests passed, including normalization/API handling, database idempotency, source removal, and failed-refresh rollback in isolated test schemas.
- Dashboard default scope, empty selection, and historical single-family scope passed application tests.
- Saved-source replay completed; complaint and campaign counts stayed unchanged and reconciliation passed again.
- Analytical CSV exports generated for Power BI.

The dashboard defaults to September 30, 2026. It shows 8,600 complaints at that cutoff; the full loaded dataset includes 22 additional reports received later. This is expected date filtering, not a count discrepancy.

One source complaint has an incident date after its receipt date. It remains in the dataset and is recorded as a data-quality observation. No missing receipt dates or missing severity fields were observed in the starter cohort.

Update: reporting-date audit and 40-response model-label coverage audit completed; see date-audit.md and coverage-audit.md. Fifteen local tests pass. Separately named variants remain excluded, and GOLF 2022 has no label in either audited list.

Not completed: manually labeled narrative sample, validated monitoring policy, finished analytical case studies, or a native Power BI file. Power BI Desktop needs Windows access.
