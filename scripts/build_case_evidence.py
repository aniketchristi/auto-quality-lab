"""Reproduce aggregate evidence for the first case; no narrative export."""
import json
from datetime import date, timedelta
from auto_quality.analysis import read, review_queue
from auto_quality.common import ROOT

cutoff = date(2024,12,31)
recent_start = cutoff - timedelta(days=89)
baseline_start = recent_start - timedelta(days=90)
queue = review_queue(cutoff,90,10)
groups = queue[(queue.make=='HONDA') & (queue.model=='CIVIC') &
               queue.model_year.isin([2018,2019]) & (queue.component=='FUEL/PROPULSION SYSTEM')]
recalls = read('''SELECT DISTINCT campaign_number,report_date,component
    FROM recall_detail WHERE make=%s AND model=%s AND model_year=ANY(%s)
    AND report_date<=%s ORDER BY campaign_number''',('HONDA','CIVIC',[2018,2019],cutoff))
packet = json.loads((ROOT/'data/processed/manual_review_packet.json').read_text())
sample = [r for r in packet['reviews'] if r['cutoff']==str(cutoff)
          and r['vehicle_key'] in ['HONDA|CIVIC|2018','HONDA|CIVIC|2019']
          and r['component']=='FUEL/PROPULSION SYSTEM']
report = {'receipt_cutoff':str(cutoff), 'recent_window':[str(recent_start),str(cutoff)],
          'baseline_window':[str(baseline_start),str(recent_start-timedelta(days=1))],
          'source_manifest_sha256':packet['source_manifest_sha256'],
          'group_counts':groups.to_dict('records'), 'recall_context':recalls.to_dict('records'),
          'sample_ids':[r['odi_number'] for r in sample],
          'sample_dates':[{'odi_number':r['odi_number'],'received_date':r['received_date'],
                           'incident_date':r['incident_date']} for r in sample],
          'interpretation':'Narrative interpretation in the case study is assisted analysis, not completed user review. Recall context is restricted by report date but uses current revised source records.'}
(ROOT/'data/processed/case_01_evidence.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
print(json.dumps({'recent_window':report['recent_window'],'baseline_window':report['baseline_window'],
                  'groups':len(groups),'sample_complaints':len(sample),'campaigns':len(recalls)},indent=2))
