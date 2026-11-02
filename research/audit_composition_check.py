"""Independent metrics and reproduction checks for the development ablations."""
from pathlib import Path
import csv,json,statistics
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/composition_check_v1'
rows=list(csv.DictReader((OUT/'predictions.csv').open()))
old=[r for r in csv.DictReader((ROOT/'output/empirical_comparison_v1/predictions.csv').open()) if r['family']=='selected' and float(r['history_s'])==1 and r['condition'] in ['H','M']]
targets={(r['trial'],float(r['time_s'])):float(r['target_s']) for r in old};seen=set();maxdiff=0.
for r in rows:
 key=(r['trial'],float(r['time_s']));assert float(r['target_s'])==targets[key]
 full=key+(r['variant'],);assert full not in seen;seen.add(full)
 if r['variant'] in ['H','H_M']:
  c='H' if r['variant']=='H' else 'M';p=next(o for o in old if o['trial']==r['trial'] and float(o['time_s'])==float(r['time_s']) and o['condition']==c)
  maxdiff=max(maxdiff,abs(float(r['prediction_s'])-float(p['prediction_s'])))
assert maxdiff<1e-8
trials=[];summary=[]
for variant in sorted({r['variant'] for r in rows}):
 selected=[r for r in rows if r['variant']==variant];assert len(selected)==33
 for trial in {r['trial'] for r in selected}:
  tr=[r for r in selected if r['trial']==trial];assert len(tr)==3
  trials.append(dict(variant=variant,trial=trial,width=tr[0]['width'],population=tr[0]['population'],mae=statistics.mean(abs(float(r['prediction_s'])-float(r['target_s'])) for r in tr)))
 for pop in ['all','wheelchair_trial','reference_trial']:
  tr=[r for r in trials if r['variant']==variant and (pop=='all' or r['population']==pop)]
  summary.append(dict(variant=variant,population=pop,trials=len(tr),trial_mae=statistics.mean(r['mae'] for r in tr)))
for name,data in [('metrics.csv',summary),('trial_metrics.csv',trials)]:
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(OUT/'audit.json').write_text(json.dumps(dict(unique_predictions=len(seen),targets_match=True,original_H_M_max_prediction_difference=maxdiff),indent=2))
print(json.dumps(summary,indent=2))
