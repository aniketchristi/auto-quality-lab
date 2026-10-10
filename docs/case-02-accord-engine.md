# Accord engine reports: what a growth-only queue misses

Status: assisted exploratory analysis of six fixed-sample narratives, pending user review. Owner statements about diagnosis and causation remain allegations. This case does not establish a common defect or estimate its frequency.

## Queue comparison

The 2018 Accord ENGINE group appeared in the equal-budget volume baseline but not the growth queue at two sample cutoffs.

| Receipt cutoff | Recent 90-day reports | Earlier 90-day reports | Growth-rule decision | Recent reports with severe-outcome fields |
| --- | --- | --- | --- | --- |
| June 30, 2025 | 25 | 31 | Not flagged | 1 |
| December 31, 2025 | 59 | 63 | Not flagged | 0 |

The rule correctly implements its stated purpose: counts did not double or increase by five. But the result says nothing about whether the existing volume contains issues worth investigating. Recent intervals are April 2–June 30 and October 3–December 31; earlier intervals are January 2–April 1 and July 5–October 2, respectively.

The severe-outcome count checks reported crash, fire, injury, or death fields. It does not count every narrative describing a dangerous situation. Zero in those fields must not be described as zero safety concerns.

## Fixed sample evidence

| Public complaint ID | Sample cutoff | Assisted reading | What remains unresolved |
| --- | --- | --- | --- |
| 11656200 | June 2025 | Owner reports head-gasket and related engine damage, plus loss of power | Repair findings and causal explanation are not independently verified |
| 11666538 | June 2025 | Misfire and reduced-power operation; owner attributes coolant intrusion to a head-gasket issue | The reported mechanic assessment is not an inspected repair record |
| 11655531 | June 2025 | Stalling and shuddering reportedly persisted after maintenance repairs | No head-gasket diagnosis is given; it should not be grouped into that symptom without evidence |
| 11699077 | December 2025 | Low acceleration, jolting, and head-gasket concerns | Several symptoms and references to other owners do not prove a shared cause |
| 11695378 | December 2025 | Coolant loss and overheating, attributed to a head-gasket issue | A feared engine fire is not an account of an actual fire |
| 11699792 | December 2025 | Highway stall, reported head-gasket repair, then another stall and a reported turbo diagnosis | Repeated symptoms could have more than one cause |

Five accounts mention head-gasket or coolant concerns. One describes persistent symptoms without that diagnosis. This is a reason to inspect repair evidence, not to combine all engine complaints into a head-gasket defect count. The narratives describe several operating symptoms, so a symptom taxonomy should allow more than one code and explicit uncertainty.

The three December sample reports were received 103, 1, and 221 days after their stated incident dates. Reports arriving in the same quarter can describe events from different periods. Receipt-time volume is useful for workload planning but cannot establish the timing of failure onset.

## Recommendation

Retain a volume-review lane alongside the growth lane. Reserve a small review budget for high-volume groups even if their counts are stable or falling. Keep an outcome-based safety review outside both count thresholds. The current public data cannot determine an optimal review budget or replace a company's safety process.

For this group, request diagnostic codes, repair orders, replaced-part findings, engine/variant/build-date information, and exposure data. Treat references to other owners as leads to investigate, not independent confirmation. Do not publish a manufacturer reliability ranking or calculate a failure rate from these counts.

## Reproduce

Run `python scripts/build_comparison_evidence.py` against the preserved project database and fixed sample. The local output contains cutoff boundaries, counts, public complaint IDs, and dates without narratives. Read the original evidence in the Manual evidence review tab before adopting these interpretations.

Source: [official 2018 Accord complaint query](https://api.nhtsa.gov/complaints/complaintsByVehicle?make=HONDA&model=ACCORD&modelYear=2018), preserved in the October 8, 2026 download. Historical receipt filters use current revised records, not historical database snapshots. Six assignments are not a representative sample of all reports.
