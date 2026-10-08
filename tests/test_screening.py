from datetime import date
import pandas as pd
from auto_quality.screening import historical_counts, apply_rule


def test_receipt_cutoff_and_adjacent_windows():
    dates = ['2023-12-27', '2023-12-28', '2024-01-06', '2024-01-07', '2024-01-16', '2024-01-17']
    rows = pd.DataFrame([{'odi_number':str(i),'received_date':d,'vehicle_key':'X|Y|2020',
        'make':'X','model':'Y','model_year':2020,'component':'ENGINE','crash':True,
        'fire':False,'injuries':0,'deaths':0} for i,d in enumerate(dates)])
    rows = pd.concat([rows, rows.iloc[[3]]], ignore_index=True)
    counts = historical_counts(rows, date(2024,1,16), 10)
    assert counts.iloc[0].recent_complaints == 2
    assert counts.iloc[0].baseline_complaints == 2
    assert counts.iloc[0].reported_severe == 2


def test_rule_threshold_boundaries():
    counts = pd.DataFrame({'recent_complaints':[10,10,10,9,20],
                           'baseline_complaints':[5,6,0,0,15]})
    result = apply_rule(counts, 10)
    assert result.review_flag.tolist() == [True,False,True,False,False]
