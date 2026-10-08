"""Shared screening rule and receipt-cutoff historical aggregation."""
from datetime import timedelta
import pandas as pd

GROUP = ['vehicle_key', 'make', 'model', 'model_year', 'component']


def apply_rule(counts, minimum=10):
    result = counts.copy()
    result['change'] = result.recent_complaints - result.baseline_complaints
    result['ratio'] = result.recent_complaints / result.baseline_complaints.replace(0, float('nan'))
    result['review_flag'] = ((result.recent_complaints >= minimum) & (result.change >= 5)
                            & ((result.ratio >= 2) | (result.baseline_complaints == 0)))
    return result


def historical_counts(records, as_of, window=90):
    cutoff = pd.Timestamp(as_of)
    recent = cutoff - timedelta(days=window - 1)
    baseline = recent - timedelta(days=window)
    rows = records.copy()
    rows['received_date'] = pd.to_datetime(rows.received_date)
    rows = rows[rows.received_date.between(baseline, cutoff)].drop_duplicates(['odi_number', 'vehicle_key', 'component'])
    rows['recent_complaints'] = (rows.received_date >= recent).astype(int)
    rows['baseline_complaints'] = (rows.received_date < recent).astype(int)
    severe = rows.crash.eq(True) | rows.fire.eq(True) | rows.injuries.fillna(0).gt(0) | rows.deaths.fillna(0).gt(0)
    rows['reported_severe'] = ((rows.received_date >= recent) & severe).astype(int)
    return rows.groupby(GROUP, as_index=False)[['recent_complaints', 'baseline_complaints', 'reported_severe']].sum()
