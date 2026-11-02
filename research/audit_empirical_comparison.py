"""Independent saved-prediction metric reconstruction and coverage checks."""
from pathlib import Path
import csv,json,statistics,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/empirical_comparison_v1'
rows=list(csv.DictReader((OUT/'predictions.csv').open()))
source=list(csv.DictReader((ROOT/'research/data/forecast_bundle/features.csv').open()))
targets={(r['trial'],float(r['time_s']),float(r['history_s'])):float(r['target_s']) for r in source}
seen=set();summaries=[];trial_rows=[]
for r in rows:
 key=(r['trial'],float(r['time_s']),float(r['history_s']))
 assert abs(float(r['target_s'])-targets[key])<1e-10
 unique=key+(r['condition'],r['family']);assert unique not in seen;seen.add(unique)
for h in [.4,1.,2.]:
 for condition,family in [('H','selected'),('M','selected'),('H','ridge'),('M','ridge'),('H','boosting'),('M','boosting'),('baseline','constant'),('baseline','travel')]:
  selected=[r for r in rows if float(r['history_s'])==h and r['condition']==condition and r['family']==family]
  assert len(selected)==33
  trials=[]
  for t in sorted({r['trial'] for r in selected}):
   data=[r for r in selected if r['trial']==t];assert len(data)==3
   error=[float(r['prediction_s'])-float(r['target_s']) for r in data]
   entry=dict(history_s=h,condition=condition,family=family,trial=t,width=float(data[0]['evaluation_width']),mae=statistics.mean(map(abs,error)),bias=statistics.mean(error),underprediction_fraction=statistics.mean(e<0 for e in error))
   trial_rows.append(entry);trials.append(entry)
  summaries.append(dict(history_s=h,condition=condition,family=family,trial_mae=statistics.mean(r['mae'] for r in trials),bias=statistics.mean(r['bias'] for r in trials),worst_trial_mae=max(r['mae'] for r in trials)))
def write(name,data):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
write('metrics.csv',summaries);write('trial_metrics.csv',trial_rows)
(OUT/'audit.json').write_text(json.dumps(dict(predictions=len(rows),all_targets_match=True,all_conditions_cover_33_queries=True,unique_predictions=True,summary_groups=len(summaries),predictions_sha256=hashlib.sha256((OUT/'predictions.csv').read_bytes()).hexdigest()),indent=2))
print(json.dumps([r for r in summaries if r['history_s']==1.],indent=2))
