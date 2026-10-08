import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .common import ROOT, connect, initialize
from .normalize import complaint, recall, vehicle_key

def source_records(response):
    payload = response.json()
    # NHTSA returns HTTP 400 for some successful zero-result recall queries.
    # Accept only this explicit success payload, never a general HTTP error.
    zero_success = (response.status_code == 400 and payload.get('results') == []
                    and payload.get('Count', payload.get('count')) == 0
                    and payload.get('Message', payload.get('message')) == 'Results returned successfully')
    if not zero_success:
        response.raise_for_status()
    records = payload['results']
    expected = int(payload.get('count', payload.get('Count', -1)))
    if expected != len(records):
        raise ValueError(f'Source count mismatch: {response.url}')
    return records

def fetch(task, raw_dir):
    kind, make, model, year = task
    route = 'complaints/complaintsByVehicle' if kind == 'complaints' else 'recalls/recallsByVehicle'
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
    response = session.get(f'https://api.nhtsa.gov/{route}', params={'make': make, 'model': model, 'modelYear': year}, timeout=(15, 60))
    records = source_records(response)
    filename = f'{kind}_{make}_{model}_{year}.json'.replace(' ', '_')
    path = raw_dir / filename
    path.write_bytes(response.content)
    return {'kind': kind, 'make': make, 'model': model, 'year': year,
            'url': response.url, 'http_status':response.status_code,
            'path': str(path.relative_to(ROOT)), 'records': len(records),
            'sha256': hashlib.sha256(response.content).hexdigest(),
            'retrieved_at': datetime.now(timezone.utc).isoformat()}

def load_entries(entries, run_id, manifest_path, started_at):
    initialize()
    cohort_keys = {vehicle_key(e['make'], e['model'], e['year']) for e in entries}
    with connect() as conn:
        # One transaction: a failed normalization cannot leave a partially refreshed cohort.
        for e in entries:
            key = vehicle_key(e['make'], e['model'], e['year'])
            conn.execute('INSERT INTO vehicles VALUES (%s,%s,%s,%s) ON CONFLICT DO NOTHING', (key,e['make'],e['model'],e['year']))
        # Replace mappings for this refreshed cohort so source removals are reflected.
        conn.execute('DELETE FROM complaint_vehicles WHERE vehicle_key = ANY(%s)', (list(cohort_keys),))
        conn.execute('DELETE FROM recall_vehicles WHERE vehicle_key = ANY(%s)', (list(cohort_keys),))
        for e in entries:
            key = vehicle_key(e['make'], e['model'], e['year'])
            rows = json.loads((ROOT / e['path']).read_text())['results']
            for row in rows:
                if e['kind'] == 'complaints':
                    d = complaint(row)
                    conn.execute('''INSERT INTO complaints VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                      ON CONFLICT (odi_number) DO UPDATE SET incident_date=excluded.incident_date,
                      received_date=excluded.received_date, manufacturer=excluded.manufacturer,
                      crash=excluded.crash,fire=excluded.fire,injuries=excluded.injuries,
                      deaths=excluded.deaths,narrative=excluded.narrative,retrieved_at=excluded.retrieved_at''',
                      tuple(d[k] for k in ['odi_number','incident_date','received_date','manufacturer','crash','fire','injuries','deaths','narrative']) + (e['retrieved_at'],))
                    conn.execute('INSERT INTO complaint_vehicles VALUES (%s,%s) ON CONFLICT DO NOTHING', (d['odi_number'],key))
                    conn.execute('DELETE FROM complaint_components WHERE odi_number=%s', (d['odi_number'],))
                    for component in d['components']:
                        conn.execute('INSERT INTO complaint_components VALUES (%s,%s) ON CONFLICT DO NOTHING', (d['odi_number'],component))
                else:
                    d = recall(row)
                    conn.execute('''INSERT INTO recalls VALUES (%s,%s,%s,%s,%s,%s,%s)
                      ON CONFLICT (campaign_number) DO UPDATE SET report_date=excluded.report_date,
                      component=excluded.component,summary=excluded.summary,consequence=excluded.consequence,
                      remedy=excluded.remedy,retrieved_at=excluded.retrieved_at''',
                      tuple(d[k] for k in ['campaign_number','report_date','component','summary','consequence','remedy']) + (e['retrieved_at'],))
                    conn.execute('INSERT INTO recall_vehicles VALUES (%s,%s) ON CONFLICT DO NOTHING', (d['campaign_number'],key))
        conn.execute('DELETE FROM complaints WHERE NOT EXISTS (SELECT 1 FROM complaint_vehicles cv WHERE cv.odi_number=complaints.odi_number)')
        conn.execute('DELETE FROM recalls WHERE NOT EXISTS (SELECT 1 FROM recall_vehicles rv WHERE rv.campaign_number=recalls.campaign_number)')
        conn.execute('INSERT INTO ingestion_runs VALUES (%s,%s,%s,%s)', (run_id,started_at,'loaded',str(manifest_path.relative_to(ROOT))))

def run(offline_manifest=None):
    started = datetime.now(timezone.utc).isoformat()
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder = ROOT / 'reports/runs' / run_id
    folder.mkdir(parents=True, exist_ok=True)
    manifest_path = folder / 'manifest.json'
    if offline_manifest:
        previous = json.loads(Path(offline_manifest).read_text())
        entries = previous['files']
        for e in entries:
            if hashlib.sha256((ROOT / e['path']).read_bytes()).hexdigest() != e['sha256']:
                raise ValueError(f'Raw file hash mismatch: {e["path"]}')
    else:
        config = json.loads((ROOT / 'config/cohort.json').read_text())
        tasks = [(kind,v['make'],v['model'],year) for v in config['vehicles'] for year in config['model_years'] for kind in ['complaints','recalls']]
        raw_dir = ROOT / 'data/raw' / run_id
        raw_dir.mkdir(parents=True, exist_ok=True)
        entries = []
        with ThreadPoolExecutor(max_workers=2) as pool:
            for entry in pool.map(lambda task: fetch(task,raw_dir), tasks):
                entries.append(entry)
                print(f'{entry["kind"]}: {entry["make"]} {entry["model"]} {entry["year"]}: {entry["records"]}', flush=True)
    manifest = {'run_id':run_id,'started_at':started,'status':'downloaded','files':entries,
                'source':'NHTSA public vehicle APIs','offline_replay':bool(offline_manifest)}
    manifest_path.write_text(json.dumps(manifest,indent=2))
    load_entries(entries,run_id,manifest_path,started)
    manifest['status'] = 'loaded'
    manifest_path.write_text(json.dumps(manifest,indent=2))
    (ROOT / 'data/processed').mkdir(parents=True,exist_ok=True)
    (ROOT / 'data/processed/latest_manifest.json').write_text(json.dumps(manifest,indent=2))
    print(f'Loaded run {run_id}; {len(entries)} source responses.',flush=True)
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--offline-manifest')
    args = parser.parse_args()
    run(args.offline_manifest)
