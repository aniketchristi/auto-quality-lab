"""Test refresh behavior in a disposable schema, never in the user's analytical tables."""
import json
import os
import uuid
from pathlib import Path
import psycopg
from psycopg import sql
import pytest
from auto_quality import common, pipeline

pytestmark=pytest.mark.skipif(os.getenv('AUTO_QUALITY_INTEGRATION')!='1',reason='Set AUTO_QUALITY_INTEGRATION=1 with a running PostgreSQL server.')

@pytest.fixture
def isolated_db(monkeypatch,tmp_path):
    schema='aq_test_'+uuid.uuid4().hex
    original_connect=common.connect
    with original_connect() as conn:
        conn.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(schema)))
    def scoped_connect():
        conn=original_connect()
        conn.execute(sql.SQL('SET search_path TO {}').format(sql.Identifier(schema)))
        return conn
    monkeypatch.setattr(common,'connect',scoped_connect)
    monkeypatch.setattr(pipeline,'connect',scoped_connect)
    monkeypatch.setattr(pipeline,'ROOT',tmp_path)
    yield scoped_connect,tmp_path
    # Only the fixture-created schema is dropped, with an unpredictable test-only name.
    with original_connect() as conn:
        conn.execute(sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(schema)))

def make_entries(folder,invalid=False,empty=False):
    complaints=[] if empty else [{'odiNumber':101,'dateOfIncident':'03/01/2024','dateComplaintFiled':'03/03/2024','components':'ENGINE,ENGINE,ELECTRICAL SYSTEM','summary':'Test fixture, not a real report.'}]
    if invalid: complaints[0]['dateOfIncident']='invalid'
    recalls=[] if empty else [{'NHTSACampaignNumber':'TEST-CAMPAIGN','ReportReceivedDate':'25/03/2024','Component':'ENGINE','Summary':'Test fixture.'}]
    entries=[]
    for kind,records in [('complaints',complaints),('recalls',recalls)]:
        name=kind+'.json'
        (folder/name).write_text(json.dumps({'results':records}))
        entries.append({'kind':kind,'make':'TEST','model':'FIXTURE','year':2020,'path':name,'retrieved_at':'2024-04-01T00:00:00+00:00'})
    return entries

def load(folder,entries,run):
    pipeline.load_entries(entries,run,folder/'manifest.json','2024-04-01T00:00:00+00:00')

def counts(connect):
    with connect() as conn:
        return tuple(conn.execute(f'SELECT count(*) FROM {table}').fetchone()[0] for table in ['complaints','complaint_components','recalls','complaint_vehicles','recall_vehicles'])

def test_refresh_is_idempotent_and_component_counts_do_not_duplicate(isolated_db):
    connect,folder=isolated_db
    entries=make_entries(folder)
    load(folder,entries,'first')
    load(folder,entries,'second')
    assert counts(connect)==(1,2,1,1,1)
    with connect() as conn:
        assert conn.execute('SELECT count(DISTINCT odi_number) FROM component_detail').fetchone()[0]==1
        assert conn.execute('SELECT report_date FROM recalls').fetchone()[0].isoformat()=='2024-03-25'

def test_source_removals_are_reflected(isolated_db):
    connect,folder=isolated_db
    load(folder,make_entries(folder),'first')
    load(folder,make_entries(folder,empty=True),'second')
    assert counts(connect)==(0,0,0,0,0)

def test_failed_normalization_rolls_back_the_refresh(isolated_db):
    connect,folder=isolated_db
    load(folder,make_entries(folder),'first')
    with pytest.raises(ValueError):
        load(folder,make_entries(folder,invalid=True),'failed')
    assert counts(connect)==(1,2,1,1,1)
    with connect() as conn:
        assert conn.execute('SELECT count(*) FROM ingestion_runs').fetchone()[0]==1
