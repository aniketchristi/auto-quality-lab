# Project plan

## Decision and scope

Support a quality analyst reviewing public owner-reported issues. The first decision is what to examine manually, not whether to issue a recall. Compare recent reporting with a model-year's own earlier reporting, inspect components and narratives, and keep uncertainty visible.

This environment provides a first working pipeline and workbench. It is not yet a finished resume project or validated early-warning system.

## Next milestones

1. Completed initial model-label audit: see coverage-audit.md for official lists and variant exclusions. Any future cohort expansion must preserve distinct complaint counting.
2. Profile reporting patterns and date quality. Separate receipt and incident time, inspect reporting lags and suspicious dates, and review missingness. Do not impute absent crash flags as false.
3. Manually review a sample of narratives. Record symptom definitions and ambiguous cases before considering a classifier. Keep any personal details out of public deliverables.
4. Evaluate screening rules against a simple volume baseline using historical receipt cutoffs. Manual adjudication and recall context are evidence, not complete ground truth. Avoid future-record leakage.
5. Build a Power BI semantic model on Windows using the prepared CSVs or local database. Verify bridge-table filters and distinct counts with the SQL outputs.
6. Write two evidence-based investigation case studies and a short recommendation memo. Explain the limits of public reports and what additional internal data an analyst would need.

## Completion criteria

- Reproducible ingestion and preserved source provenance.
- Reconciled complaint and campaign counts with documented date/coverage limitations.
- Evaluated monitoring rules and reviewed evidence behind highlighted groups.
- A dashboard someone can use to answer a defined question.
- Power BI model and measures independently checked against SQL.
- Public repository without raw narrative/VIN data or fabricated business outcomes.

## Sources

- https://www.nhtsa.gov/nhtsa-datasets-and-apis
- https://static.nhtsa.gov/odi/ffdd/cmpl/CMPL.txt
- https://www.nhtsa.gov/resources-investigations-recalls

The starter API does not expose every flat-file field. Mileage, towing, and richer fields should be added only after a documented flat-file ingestion stage, not inferred from missing API fields.
