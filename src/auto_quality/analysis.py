from datetime import date, timedelta
import pandas as pd
from .common import connect

def read(query, params=None):
    with connect() as conn:
        cur = conn.execute(query, params)
        return pd.DataFrame(cur.fetchall(),columns=[d.name for d in cur.description])

def last_complete_month():
    return date.today().replace(day=1) - timedelta(days=1)

def review_queue(as_of=None, window=90, minimum=10):
    as_of = as_of or last_complete_month()
    recent_start = as_of - timedelta(days=window-1)
    baseline_start = recent_start - timedelta(days=window)
    result = read('''SELECT vehicle_key,make,model,model_year,component,
        count(DISTINCT odi_number) FILTER (WHERE received_date >= %(recent)s) AS recent_complaints,
        count(DISTINCT odi_number) FILTER (WHERE received_date < %(recent)s) AS baseline_complaints,
        count(DISTINCT odi_number) FILTER (WHERE received_date >= %(recent)s
          AND (crash OR fire OR injuries > 0 OR deaths > 0)) AS reported_severe
        FROM component_detail WHERE received_date BETWEEN %(baseline)s AND %(as_of)s
        GROUP BY 1,2,3,4,5''', {'recent':recent_start,'baseline':baseline_start,'as_of':as_of})
    if result.empty:
        return result
    result['change'] = result.recent_complaints - result.baseline_complaints
    result['ratio'] = result.recent_complaints / result.baseline_complaints.replace(0,float('nan'))
    result['review_flag'] = (result.recent_complaints >= minimum) & (result.change >= 5) & ((result.ratio >= 2) | (result.baseline_complaints == 0))
    result['reason'] = result.apply(lambda r: 'Increase merits manual review' if r.review_flag else 'Below screening thresholds',axis=1)
    result['as_of'] = str(as_of)
    return result.sort_values(['review_flag','change','recent_complaints'],ascending=False).reset_index(drop=True)
