"""Aggregate-only evidence for the volume-selected Accord engine case."""
import json
from datetime import date, timedelta
from auto_quality.analysis import review_queue
from auto_quality.common import ROOT

packet = json.loads((ROOT/'data/processed/manual_review_packet.json').read_text())
report = {'source_manifest_sha256':packet['source_manifest_sha256'], 'cutoffs':[],
          'interpretation':'Assisted exploratory case; no confirmed defect labels or completed user adjudication.'}
for cutoff in [date(2025,6,30),date(2025,12,31)]:
    counts = review_queue(cutoff,90,10)
    row = counts[(counts.vehicle_key=='HONDA|ACCORD|2018') & (counts.component=='ENGINE')]
    selected = [r for r in packet['reviews'] if r['cutoff']==str(cutoff)
                and r['vehicle_key']=='HONDA|ACCORD|2018' and r['component']=='ENGINE']
    recent = cutoff-timedelta(days=89)
    report['cutoffs'].append({'cutoff':str(cutoff), 'recent_window':[str(recent),str(cutoff)],
        'baseline_window':[str(recent-timedelta(days=90)),str(recent-timedelta(days=1))],
        'counts':row.to_dict('records'),
        'sample':[{'odi_number':r['odi_number'], 'stratum':r['stratum'],
                   'incident_date':r['incident_date'],'received_date':r['received_date']} for r in selected]})
(ROOT/'data/processed/case_02_evidence.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
print(json.dumps({'cutoffs':len(report['cutoffs']), 'sample_assignments':sum(len(c['sample']) for c in report['cutoffs'])}))
