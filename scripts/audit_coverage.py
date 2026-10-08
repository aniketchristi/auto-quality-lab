"""Archive NHTSA complaint/recall label lists and report exact-label coverage."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from auto_quality.common import ROOT
from auto_quality.pipeline import source_records

config = json.loads((ROOT / 'config/cohort.json').read_text())
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
folder = ROOT / 'data/raw' / ('coverage_' + stamp)
folder.mkdir(parents=True, exist_ok=True)
families = {}
for vehicle in config['vehicles']:
    families.setdefault(vehicle['make'], []).append(vehicle['model'])

def fetch(task):
    make, year, issue = task
    session = requests.Session()
    session.mount('https://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])))
    response = session.get('https://api.nhtsa.gov/products/vehicle/models',
        params={'make': make, 'modelYear': year, 'issueType': issue}, timeout=(15, 60))
    rows = source_records(response)
    path = folder / f'{make}_{year}_{issue}.json'
    path.write_bytes(response.content)
    labels = sorted({r['model'].strip().upper() for r in rows})
    matches = {family: [label for label in labels if family in label] for family in families[make]}
    return {'make': make, 'year': year, 'issue_type': issue, 'url': response.url,
            'retrieved_at': datetime.now(timezone.utc).isoformat(), 'path': str(path.relative_to(ROOT)),
            'sha256': hashlib.sha256(response.content).hexdigest(), 'raw_rows': len(rows),
            'distinct_labels': len(labels), 'family_candidates': matches,
            'configured_labels_present': {family: family in labels for family in families[make]}}

tasks = [(make, year, issue) for make in families for year in config['model_years'] for issue in ['c', 'r']]
with ThreadPoolExecutor(max_workers=2) as pool:
    entries = list(pool.map(fetch, tasks))
report = {'audit_time': stamp, 'files': entries,
          'method': 'Exact configured-label presence and substring family candidates. Candidate matching is for manual review, not automatic family merging. Lists are issue-specific and do not establish all manufactured variants.'}
(ROOT / 'data/processed/coverage_audit.json').write_text(json.dumps(report, indent=2) + '\n')
for make in families:
    for family in families[make]:
        selected = [e for e in entries if e['make'] == make]
        candidates = sorted({label for e in selected for label in e['family_candidates'][family]})
        absent = [(e['year'], e['issue_type']) for e in selected if not e['configured_labels_present'][family]]
        print(f'{make} {family}: candidates={candidates}; configured label absent={absent}', flush=True)
