# Reporting-date audit

Run `python scripts/profile_dates.py --as-of 2026-09-30` from the activated project environment. The aggregate JSON is written locally to `data/processed/date_profile.json`. The dashboard calculates the same audit for selected model families and years.

The October 8, 2026 source download contains 8,622 distinct complaints. Of these, 8,600 were received by September 30 and 22 afterward. No receipt or incident dates were missing among the 8,600 eligible reports. One incident date follows its receipt date; this record stays in the database but is excluded from lag statistics.

Among the 8,599 records with nonnegative reporting intervals, median reporting lag was 12 days and the 90th percentile was 326 days. There were 742 reports received more than 365 days after the stated incident date. Long lags are observations, not proof that dates are wrong.

These results describe this selected cohort. They do not estimate reporting delay for all vehicles or all incidents. Complaint records are current revised records, so a receipt cutoff does not recreate the database as it existed at that time.

## Consequence for monitoring

Receipt-time increases can include incidents from much earlier periods. During investigation, examine incident dates alongside receipt dates before describing a sudden increase as newly occurring failures. Historical screening should use receipt dates to determine which reports were available, while acknowledging that revision histories are unavailable. Do not use incident dates to pull later-received reports into an earlier evaluation cutoff.

The audit deduplicates complaint IDs before calculating statistics. Missing dates and negative reporting intervals are counted separately. Quantiles use pandas' default linear interpolation. Six interval bands are exhaustive for valid nonnegative lags, including zero-day reports.
