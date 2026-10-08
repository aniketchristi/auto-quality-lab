# Historical screening workload

Evaluated January 2023 through September 2026 at 45 monthly receipt cutoffs. Each cutoff uses adjacent equal-length windows of 90, 180, or 365 days, with minimum recent counts of 5, 10, or 20. This produces 405 settings. All 135 distinct cutoff/window aggregations reconciled against the production SQL for recent counts, baseline counts, and owner-reported severe outcomes.

The evaluation excludes receipts after each cutoff, even when an incident date precedes it. Duplicate complaint/component/model-year assignments are removed before aggregation. The records were downloaded in October 2026 and may have been revised since earlier cutoffs. This is a retrospective workload exercise, not an exact historical replay.

## Results

| Window | Minimum recent reports | Mean growth-rule groups/month | Maximum | Mean volume-baseline groups/month |
| --- | --- | --- | --- | --- |
| 90 days | 5 | 6.42 | 22 | 24.91 |
| 90 days | 10 | 2.96 | 13 | 9.42 |
| 90 days | 20 | 0.91 | 7 | 3.44 |
| 180 days | 5 | 13.00 | 38 | 47.49 |
| 180 days | 10 | 7.38 | 24 | 21.60 |
| 180 days | 20 | 2.91 | 12 | 8.22 |
| 365 days | 5 | 30.47 | 57 | 89.33 |
| 365 days | 10 | 20.31 | 39 | 43.11 |
| 365 days | 20 | 10.00 | 20 | 20.53 |

The growth rule requires the minimum count, at least five extra reports, and twice the earlier count (or a zero earlier count). The volume baseline only requires the same minimum recent count. An additional equal-budget comparison ranks eligible groups by recent count and selects as many groups as the growth rule, with deterministic ties. Overlap counts are preserved in the local evaluation JSON.

At the current default, the growth rule produces about three review groups in an average month, with a maximum of 13. This is a manageable starting workload for a portfolio investigation. It is not evidence that these thresholds detect defects well. Longer windows count more receipts and produce larger queues; these means do not compare equally demanding thresholds.

Across these 45 cutoffs, the default produced 133 monthly group flags across 39 unique model-year/component groups. Of those monthly selections, 66 also appeared in the equal-budget volume baseline. The methods therefore select different groups in roughly half the slots; whether those differences help an investigator needs evidence review. The most frequently recurring group was 2018 Civic steering (10 monthly flags). That is a sampling lead, not a reliability ranking or confirmed defect finding.

## What this evaluation cannot establish

No confirmed defect labels, non-reporting vehicle populations, mileage exposure, or complete revision history are available here. Precision, recall, false-positive rate, and recall-prediction lead time are therefore not estimated. Component groups may share complaints, so their counts must not be summed into distinct incident totals. Monthly windows overlap; repeated flags are recurring workload, not independent discoveries.

Threshold settings were examined on the same retrospective period. There is no holdout validation or optimal-threshold claim. A higher minimum reduces workload and can omit uncommon serious reports. Severe outcomes must also be reviewed outside the growth queue.

## Reproduce and next step

Run `python scripts/evaluate_screening.py` with the project database running. Aggregate outputs contain group counts, not narratives or VINs, and are written to `data/processed/screening_evaluation.json`. `tests/test_screening.py` checks window boundaries, cutoff exclusion, duplicate handling, and threshold boundaries.

Next, inspect a fixed sample from growth flags and equal-budget volume selections. Record symptom consistency, ambiguous narratives, reporting delays, and relevant recall documents. Decide whether the growth-selected groups provide better investigation leads before revising the rule.
