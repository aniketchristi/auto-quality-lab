from datetime import date
import pandas as pd
from auto_quality.review_sample import sample_groups, sample_complaints

def test_group_sample_is_stable_under_input_reordering():
    rows = pd.DataFrame([{'vehicle_key':str(i),'make':'X','model':'Y','model_year':2020,
        'component':'ENGINE','recent_complaints':20-i,'review_flag':i>=3} for i in range(6)])
    first = sample_groups(rows)
    second = sample_groups(rows.iloc[::-1])
    assert first.vehicle_key.tolist() == second.vehicle_key.tolist()
    assert set(first.stratum) == {'growth_only','volume_only'}

def test_sample_never_includes_later_receipts_or_duplicates():
    rows = pd.DataFrame({'odi_number':['1','1','2','3'],
        'received_date':['2025-01-01','2025-01-01','2025-04-01','2024-01-01']})
    selected = sample_complaints(rows,date(2025,3,31))
    assert selected.odi_number.tolist() == ['1']
