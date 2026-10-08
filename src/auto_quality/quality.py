"""Receipt-time date audit; no narrative or vehicle identifiers in outputs."""
import pandas as pd


def date_profile(records, as_of):
    rows = records.drop_duplicates('odi_number').copy()
    incident = pd.to_datetime(rows.incident_date, errors='coerce')
    received = pd.to_datetime(rows.received_date, errors='coerce')
    cutoff = pd.Timestamp(as_of)
    eligible = received.notna() & (received <= cutoff)
    lag = (received - incident).dt.days
    valid_lag = lag[eligible & lag.notna() & (lag >= 0)]
    summary = {
        'receipt_cutoff': str(as_of),
        'distinct_records_in_scope': len(rows),
        'records_received_by_cutoff': int(eligible.sum()),
        'missing_receipt_date': int(received.isna().sum()),
        'received_after_cutoff': int((received > cutoff).sum()),
        'missing_incident_date_by_cutoff': int((eligible & incident.isna()).sum()),
        'incident_after_receipt_by_cutoff': int((eligible & (lag < 0)).sum()),
        'nonnegative_lag_records': len(valid_lag),
        'median_reporting_lag_days': float(valid_lag.median()) if len(valid_lag) else None,
        'p90_reporting_lag_days': float(valid_lag.quantile(.9)) if len(valid_lag) else None,
        'reported_more_than_365_days_later': int((valid_lag > 365).sum()),
    }
    bands = pd.cut(valid_lag, [-1, 0, 7, 30, 90, 365, float('inf')],
                   labels=['Same day', '1–7 days', '8–30 days', '31–90 days',
                           '91–365 days', 'Over 365 days'])
    distribution = bands.value_counts(sort=False).rename_axis('reporting_lag').reset_index(name='complaints')
    return summary, distribution
