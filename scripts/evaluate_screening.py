"""Aggregate workload evaluation, without defect/recall prediction claims."""
import json
import pandas as pd
from auto_quality.analysis import read, review_queue
from auto_quality.common import ROOT
from auto_quality.screening import historical_counts, apply_rule, GROUP

records = read('SELECT odi_number,received_date,vehicle_key,make,model,model_year,component,crash,fire,injuries,deaths FROM component_detail')
cutoffs = pd.date_range('2023-01-31', '2026-09-30', freq='ME')
results = []
flags = []
for cutoff in cutoffs:
    for window in [90, 180, 365]:
        counts = historical_counts(records, cutoff.date(), window)
        # Independently reconcile pandas historical counts with production SQL.
        sql = review_queue(cutoff.date(), window, 10)
        cols = GROUP + ['recent_complaints', 'baseline_complaints', 'reported_severe']
        left = counts[cols].sort_values(GROUP).reset_index(drop=True)
        right = sql[cols].sort_values(GROUP).reset_index(drop=True)
        pd.testing.assert_frame_equal(left, right, check_dtype=False)
        for minimum in [5, 10, 20]:
            screened = apply_rule(counts, minimum)
            selected = screened[screened.review_flag]
            volume = screened[screened.recent_complaints >= minimum]
            # Equal-budget baseline: largest recent report counts, deterministic ties.
            top = volume.sort_values(['recent_complaints'] + GROUP, ascending=[False] + [True]*len(GROUP)).head(len(selected))
            selected_keys = set(map(tuple, selected[GROUP].to_numpy()))
            top_keys = set(map(tuple, top[GROUP].to_numpy()))
            results.append({'cutoff':str(cutoff.date()), 'window':window, 'minimum':minimum,
                'active_groups':len(screened), 'growth_review_groups':len(selected),
                'volume_review_groups':len(volume), 'equal_budget_overlap':len(selected_keys & top_keys),
                'zero_baseline_flags':int((selected.baseline_complaints == 0).sum())})
            for row in selected.to_dict('records'):
                flags.append({**{k:row[k] for k in GROUP + ['recent_complaints','baseline_complaints','reported_severe','change']},
                              'cutoff':str(cutoff.date()),'window':window,'minimum':minimum})
report = {'method':'45 monthly receipt cutoffs; three windows; three minimum counts. Current revised records, not point-in-time snapshots. Workload evaluation only; no precision, recall, or defect detection accuracy is estimated.',
          'sql_reconciliations':len(cutoffs)*3, 'workload':results, 'flagged_groups':flags}
(ROOT / 'data/processed/screening_evaluation.json').write_text(json.dumps(report, indent=2) + '\n')
frame = pd.DataFrame(results)
print(frame.groupby(['window','minimum'])[['growth_review_groups','volume_review_groups','zero_baseline_flags']].agg(['mean','max']).round(2).to_string())
print(f'SQL reconciliations passed: {len(cutoffs)*3}; evaluated settings: {len(results)}')
