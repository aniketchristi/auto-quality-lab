# Civic fuel-system reporting: investigate repair access as well as symptoms

Status: assisted exploratory analysis of six sampled narratives. The owner has not yet completed the manual reviews. This case does not validate the screening rule or confirm individual defects.

## Why this group entered the queue

At the December 31, 2024 receipt cutoff, the 2018 Civic FUEL/PROPULSION SYSTEM group increased from 5 reports in the earlier 90-day window to 13 in the recent window. The 2019 group increased from 5 to 11. Both met the default minimum of 10 recent reports, an increase of at least five, and at least twice the baseline.

These are reports received, not failure rates. The recent window is October 3–December 31, 2024; the baseline is July 5–October 2, 2024. Three complaints from each group were selected by the fixed hash-based review protocol. They are a small investigation sample, not a representative estimate of all 24 recent group reports.

## What the sample says

| Public complaint ID | Model year | Assisted interpretation | Limit |
| --- | --- | --- | --- |
| 11621835 | 2018 | Recall repair unavailable because of parts access | No operating failure is described in this short account |
| 11623507 | 2018 | Repeated difficulty starting; diagnosis unresolved | The account does not establish a fuel-pump cause |
| 11624600 | 2018 | Stalling and unexpected airbag deployment; owner suspects recall relevance | Several symptoms require separate investigation; no common cause is established |
| 11623524 | 2019 | Repeated attempts to schedule recall repair without parts availability | Service-access complaint; no operating symptom stated |
| 11623488 | 2019 | Recall replacement unavailable; account describes the recall mechanism | Describing a recall does not establish that this vehicle suffered that failure |
| 11621349 | 2019 | Insufficient narrative detail | Incident date precedes receipt by 526 days |

This reading separates three repair-access accounts, two symptom accounts, and one insufficient account. Categories describe these six narratives only. No quotations, personal contact details, VINs, or raw narratives are included in this public case study. Public complaint IDs allow checking the accounts in the official model/year source queries.

## Recall context available at the cutoff

Campaign 23V858000 was reported on December 18, 2023. NHTSA describes a fuel-pump issue with a potential stalling consequence. Its current record says owner letters were mailed September 6, 2024. The campaign predates the recent reporting window, so this case cannot be presented as detecting a new defect before its recall. The timing of notifications is a plausible explanation to investigate for later repair-access reports; these data do not establish causation. [Official campaign record](https://api.nhtsa.gov/recalls/campaignNumber?campaignNumber=23V858000).

The loaded current records also contain a campaign reported in 2026. That later campaign is excluded from this historical case. Even date-filtered campaign descriptions may have been revised since 2024, so they are context rather than an exact historical snapshot.

The base CIVIC recall response contains campaign descriptions mentioning hatchbacks and other body styles. An exact API query label does not guarantee a base-trim-only population. Build dates, actual variants, and individual applicability require additional evidence.

## Analyst recommendation

Split the investigation into repair-access and operating-symptom questions. For repair access, an automaker would need parts availability, dealer scheduling, notification dates, and recall-completion records. For reported symptoms, obtain diagnostic codes, repair findings, variant/build-date details, and exposure data. The public reports cannot supply these internal measures.

Keep this group in a manual investigation queue, but do not label its increase as 24 new fuel-pump failures. Do not infer that the two symptom narratives describe the same defect. A reporting increase after an existing recall can be useful for service operations while still being weak evidence of newly emerging failures.

## Reproduce and challenge

Run `python scripts/build_case_evidence.py` against the preserved project dataset and review packet. It writes aggregate counts, complaint IDs/dates, source-manifest hash, and cutoff-filtered campaign identifiers locally, without narratives. Read the six original accounts in the Manual evidence review tab and challenge the interpretations before adopting this case as your own analysis.

Sources: [2018 Civic complaints](https://api.nhtsa.gov/complaints/complaintsByVehicle?make=HONDA&model=CIVIC&modelYear=2018), [2019 Civic complaints](https://api.nhtsa.gov/complaints/complaintsByVehicle?make=HONDA&model=CIVIC&modelYear=2019), and the preserved October 8, 2026 download manifest. Counts refer to the preserved download, not future live API totals.
