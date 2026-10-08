import pytest
import requests
from auto_quality.pipeline import source_records

class Response:
    url='https://api.nhtsa.gov/example'
    def __init__(self,status,payload):
        self.status_code=status
        self.payload=payload
    def json(self): return self.payload
    def raise_for_status(self):
        if self.status_code>=400: raise requests.HTTPError('source error')

def test_nhtsa_successful_empty_400():
    assert source_records(Response(400,{'Count':0,'Message':'Results returned successfully','results':[]}))==[]

def test_other_400_is_not_silently_empty():
    with pytest.raises(requests.HTTPError):
        source_records(Response(400,{'Count':0,'Message':'Invalid vehicle','results':[]}))

def test_mismatched_source_count_rejected():
    with pytest.raises(ValueError):
        source_records(Response(200,{'count':2,'results':[{}]}))
