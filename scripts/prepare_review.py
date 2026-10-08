"""Create a local-only narrative packet. Never implies completed adjudication."""
import hashlib
import json
from datetime import date
from auto_quality.analysis import read, review_queue
from auto_quality.common import ROOT
from auto_quality.review_sample import sample_groups, sample_complaints, SEED

cutoffs = [date(2024,12,31), date(2025,6,30), date(2025,12,31)]
packet = []
inventory = []
for cutoff in cutoffs:
    queue = review_queue(cutoff, 90, 10)
    selected = sample_groups(queue)
    for group in selected.itertuples():
        evidence = read('SELECT odi_number, received_date, incident_date, narrative FROM component_detail WHERE vehicle_key=%s AND component=%s', (group.vehicle_key,group.component))
        sample = sample_complaints(evidence, cutoff)
        inventory.append({'cutoff':str(cutoff),'vehicle_key':group.vehicle_key,'component':group.component,
            'stratum':group.stratum,'recent_complaints':int(group.recent_complaints),
            'baseline_complaints':int(group.baseline_complaints),'sampled_complaints':len(sample)})
        for record in sample.to_dict('records'):
            packet.append({'review_id':f'{cutoff}|{group.vehicle_key}|{group.component}|{record["odi_number"]}',
                'cutoff':str(cutoff),'vehicle_key':group.vehicle_key,'component':group.component,
                'stratum':group.stratum, **{k:str(v) if v is not None else None for k,v in record.items() if k!='sample_rank'},
                'review_status':'pending', 'symptom_code':None, 'component_consistent':None,
                'evidence_specificity':None, 'reporting_delay_note':None, 'review_note':None})
source = ROOT / 'data/processed/latest_manifest.json'
report = {'seed':SEED, 'source_manifest_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
          'cutoffs':[str(c) for c in cutoffs], 'window':90,'minimum':10,
          'groups':inventory, 'reviews':packet,
          'limitations':'Purposeful selection comparison, not representative prevalence or defect labels. Narratives are local only. No review has been completed by this script.'}
target = ROOT / 'data/processed/manual_review_packet.json'
if target.exists():
    existing = json.loads(target.read_text())
    if any(r.get('review_status') != 'pending' for r in existing['reviews']):
        raise SystemExit('Existing packet contains review work. Preserve it before generating a new packet.')
target.write_text(json.dumps(report,indent=2) + '\n')
print(json.dumps({'groups':len(inventory),'review_assignments':len(packet),
                  'unique_complaints':len({r['odi_number'] for r in packet}),
                  'strata':{s:sum(g['stratum']==s for g in inventory) for s in ['growth_only','volume_only','both']}},indent=2))
