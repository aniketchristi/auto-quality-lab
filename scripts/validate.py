import json
from auto_quality.common import ROOT
from auto_quality.analysis import read

manifest = json.loads((ROOT / 'data/processed/latest_manifest.json').read_text())
checks = []
for e in manifest['files']:
    table = 'complaint_vehicles' if e['kind']=='complaints' else 'recall_vehicles'
    field = 'odi_number' if e['kind']=='complaints' else 'campaign_number'
    source_field = 'odiNumber' if e['kind']=='complaints' else 'NHTSACampaignNumber'
    source = json.loads((ROOT / e['path']).read_text())['results']
    expected = len({str(r[source_field]) for r in source})
    key = f'{e["make"]}|{e["model"]}|{e["year"]}'
    actual = int(read(f'SELECT count(DISTINCT {field}) AS n FROM {table} WHERE vehicle_key=%s',(key,)).iloc[0]['n'])
    checks.append({'check':f'{e["kind"]}:{key}','expected':expected,'actual':actual,'passed':expected==actual})
missing = int(read('SELECT count(*) n FROM complaints WHERE received_date IS NULL').iloc[0]['n'])
checks.append({'check':'received_dates_complete','actual':missing,'expected':0,'passed':missing==0})
missing_components = int(read('SELECT count(*) n FROM complaints c WHERE NOT EXISTS (SELECT 1 FROM complaint_components x WHERE x.odi_number=c.odi_number)').iloc[0]['n'])
checks.append({'check':'components_present','actual':missing_components,'expected':0,'passed':missing_components==0})
flags = read('''SELECT count(*) FILTER (WHERE incident_date > received_date) AS incident_after_receipt,
count(*) FILTER (WHERE injuries IS NULL OR deaths IS NULL OR crash IS NULL OR fire IS NULL) AS missing_severity
FROM complaints''').to_dict('records')[0]
report={'source_reconciliation_checks':checks,'data_quality_observations':flags,'passed':all(c['passed'] for c in checks)}
(ROOT / 'data/processed/validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'checks':len(checks),'passed':report['passed'],'missing_received_dates':missing,'observations':flags},indent=2))
if not report['passed']:
    raise SystemExit(1)
