import json
from pathlib import Path
from auto_quality.common import ROOT
from auto_quality.analysis import read, review_queue

out = ROOT / 'exports'
out.mkdir(exist_ok=True)
queries = {
    'vehicles': 'SELECT * FROM vehicles ORDER BY vehicle_key',
    'complaints': 'SELECT odi_number,incident_date,received_date,crash,fire,injuries,deaths FROM complaints',
    'complaint_vehicles': 'SELECT * FROM complaint_vehicles',
    'complaint_components': 'SELECT * FROM complaint_components',
    'recalls': 'SELECT campaign_number,report_date,component FROM recalls',
    'recall_vehicles': 'SELECT * FROM recall_vehicles',
    'monthly_reporting': 'SELECT * FROM monthly_reporting ORDER BY month,vehicle_key'
}
for name, query in queries.items():
    df = read(query)
    df.to_csv(out / f'{name}.csv', index=False)
    print(f'{name}: {len(df)} rows')
review_queue().to_csv(out / 'review_queue.csv',index=False)
(out / 'README.txt').write_text('Generated analytical extracts from NHTSA. Counts are owner reports, not failure rates. Narratives and VINs are excluded. Component and vehicle bridges require distinct complaint counts. Recall mappings provide model/year context, not VIN-level applicability. See docs/power-bi.md.\n')
