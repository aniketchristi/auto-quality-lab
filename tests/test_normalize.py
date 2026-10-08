from datetime import date
import pytest
from auto_quality.normalize import complaint, recall, boolean, parse_date

def test_source_date_conventions_differ():
    assert parse_date('03/04/2021')==date(2021,3,4)
    assert parse_date('03/04/2021',recall=True)==date(2021,4,3)

def test_unknown_is_not_false_or_zero():
    row=complaint({'odiNumber':1,'components':'ENGINE,ENGINE, ELECTRICAL SYSTEM'})
    assert row['crash'] is None and row['injuries'] is None
    assert row['components']==['ELECTRICAL SYSTEM','ENGINE']

def test_no_component_is_preserved():
    assert complaint({'odiNumber':1})['components']==['UNSPECIFIED']

def test_invalid_date_rejected():
    with pytest.raises(ValueError): parse_date('not-a-date')

def test_unknown_boolean_rejected():
    with pytest.raises(ValueError): boolean('unknown')

def test_negative_severity_rejected():
    with pytest.raises(ValueError): complaint({'odiNumber':1,'numberOfDeaths':-1})

def test_vin_excluded_from_analytical_record():
    assert 'vin' not in complaint({'odiNumber':1,'vin':'example'})
