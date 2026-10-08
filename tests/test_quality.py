from datetime import date
import pandas as pd
from auto_quality.quality import date_profile


def test_date_audit_cutoff_duplicates_and_invalid_intervals():
    rows = pd.DataFrame([
        ('1', '2024-01-01', '2024-01-01'),
        ('1', '2024-01-01', '2024-01-01'),
        ('2', '2024-01-01', '2024-01-08'),
        ('3', '2024-02-01', '2024-01-09'),
        ('4', None, '2024-01-09'),
        ('5', '2024-01-01', None),
        ('6', '2024-01-01', '2024-02-01'),
    ], columns=['odi_number', 'incident_date', 'received_date'])
    summary, distribution = date_profile(rows, date(2024, 1, 31))
    assert summary['distinct_records_in_scope'] == 6
    assert summary['records_received_by_cutoff'] == 4
    assert summary['missing_receipt_date'] == 1
    assert summary['received_after_cutoff'] == 1
    assert summary['incident_after_receipt_by_cutoff'] == 1
    assert summary['missing_incident_date_by_cutoff'] == 1
    assert summary['median_reporting_lag_days'] == 3.5
    assert distribution.complaints.sum() == 2


def test_empty_date_audit_has_no_invented_lag():
    rows = pd.DataFrame(columns=['odi_number', 'incident_date', 'received_date'])
    summary, distribution = date_profile(rows, date(2024, 1, 31))
    assert summary['median_reporting_lag_days'] is None
    assert distribution.complaints.sum() == 0
