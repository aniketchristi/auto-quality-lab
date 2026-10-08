"""Deterministic, bounded evidence sampling for manual review."""
import hashlib
import pandas as pd
from .screening import GROUP

SEED = 'auto-quality-review-v1'

def stable_rank(value):
    return hashlib.sha256((SEED + '|' + value).encode()).hexdigest()

def sample_groups(screened, per_stratum=3):
    volume = screened[screened.recent_complaints >= 10].sort_values(
        ['recent_complaints'] + GROUP, ascending=[False] + [True] * len(GROUP))
    budget = int(screened.review_flag.sum())
    top_keys = set(map(tuple, volume.head(budget)[GROUP].to_numpy()))
    rows = screened.copy()
    rows['volume_selected'] = [tuple(row) in top_keys for row in rows[GROUP].to_numpy()]
    rows['stratum'] = ['both' if growth and volume else 'growth_only' if growth else 'volume_only' if volume else 'neither'
                      for growth, volume in zip(rows.review_flag, rows.volume_selected)]
    rows = rows[rows.stratum != 'neither'].copy()
    rows['sample_rank'] = rows[GROUP].astype(str).agg('|'.join, axis=1).map(stable_rank)
    return rows.sort_values(['stratum','sample_rank']).groupby('stratum', sort=True).head(per_stratum)

def sample_complaints(records, cutoff, window=90, limit=3):
    rows = records.drop_duplicates('odi_number').copy()
    received = pd.to_datetime(rows.received_date)
    end = pd.Timestamp(cutoff)
    rows = rows[received.between(end - pd.Timedelta(days=window-1), end)].copy()
    rows['sample_rank'] = rows.odi_number.astype(str).map(stable_rank)
    return rows.sort_values('sample_rank').head(limit)
