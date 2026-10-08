# Data model and metric definitions

| Table | Grain | Key |
|---|---|---|
| vehicles | One configured make/model/model-year | vehicle_key |
| complaints | One NHTSA complaint reference | odi_number |
| complaint_vehicles | One complaint/queried vehicle relationship | odi_number + vehicle_key |
| complaint_components | One complaint/component assignment | odi_number + component |
| recalls | One recall campaign | campaign_number |
| recall_vehicles | One campaign/queried vehicle relationship | campaign_number + vehicle_key |
| ingestion_runs | One successful database load | run_id |

Each campaign's common description is stored once; its model-year applicability is a bridge. Complaint associations use the exact queried API cohort. Do not infer VIN, trim, engine, platform, build dates, or powertrain applicability from that association.

## Dates and missingness

- API complaint incident and filing dates: month/day/year.
- API recall report dates: day/month/year.
- received_date: API dateComplaintFiled, used as the reporting/receipt-time proxy.
- incident_date: owner's reported dateOfIncident.
- retrieved_at: UTC time of obtaining that source response.
- Empty boolean/count fields remain NULL. They are not zero or false.
- Unknown component values become UNSPECIFIED so the complaint is not lost.
- The 11-character VIN field is not imported into analytical tables.

## Metrics

Distinct complaints: distinct odi_number within the selected cohort and receipt cutoff. A record associated with multiple components remains one complaint in the overall metric.

Reported severe: distinct complaints mentioning crash, fire, injuries > 0, or deaths > 0. This is a report indicator, not confirmed severity or a severity-weighted risk score.

Component reporting: distinct complaints for each component. Component totals overlap and cannot be added to obtain a fleet total.

Review flag: recent reports ≥ minimum; recent minus baseline ≥ 5; recent/baseline ≥ 2 or baseline = 0. Equal windows are inclusive and adjacent, without overlap. Ratio is undefined for baseline zero and remains blank. A flag is a screening heuristic only.

Recall count: distinct campaign_number for selected model-years, with report date at or before the cutoff. Campaign counts across vehicle groups overlap. No direct complaint-to-recall relationship is modeled.

Historical cutoff: restricts receipt dates and recall report dates, but cannot reconstruct previous source corrections or previous source availability. Dates after the cutoff are excluded. Same-day times are unavailable.
