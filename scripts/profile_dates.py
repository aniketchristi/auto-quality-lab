"""Write aggregate-only date audit, using a reproducible receipt cutoff."""
import argparse
import json
from datetime import date
from auto_quality.analysis import read, last_complete_month
from auto_quality.common import ROOT
from auto_quality.quality import date_profile

parser = argparse.ArgumentParser()
parser.add_argument('--as-of', type=date.fromisoformat, default=last_complete_month())
args = parser.parse_args()
records = read('SELECT odi_number, incident_date, received_date FROM complaints')
summary, distribution = date_profile(records, args.as_of)
report = {'summary': summary, 'lag_distribution': distribution.to_dict('records'),
          'interpretation': 'Current revised records, not historical snapshots. Lag excludes missing dates and negative intervals. Counts are owner reports, not failures.'}
target = ROOT / 'data/processed/date_profile.json'
target.parent.mkdir(parents=True, exist_ok=True)
target.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(summary, indent=2))
