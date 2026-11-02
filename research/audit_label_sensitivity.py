"""Reconstruct sensitivity metrics from saved predictions, without fitting."""
from pathlib import Path
import csv,json,statistics,itertools
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/label_sensitivity_v1'
rows=list(csv.DictReader((OUT/'predictions.csv').open()))
base=list(csv.DictReader((ROOT/'output/empirical_comparison_v1/metrics.csv').open()))
H=float(next(r['trial_mae'] for r in base if r['condition']=='H' and r['family']=='selected' and float(r['history_s'])==1))
M=float(next(r['trial_mae'] for r in base if r['condition']=='M' and r['family']=='selected' and float(r['history_s'])==1))
targets={(r['trial'],r['time_s']):float(r['target_s']) for r in csv.DictReader((ROOT/'output/empirical_comparison_v1/predictions.csv').open()) if r['condition']=='M' and r['family']=='selected' and float(r['history_s'])==1}
seen=set();summary=[];seedrows=[]
for r in rows:
 key=(r['trial'],r['time_s'],r['mode'],r['rate'],r['seed']);assert key not in seen;seen.add(key)
 assert float(r['target_s'])==targets[r['trial'],r['time_s']]
for mode,rate in sorted({(r['mode'],float(r['rate'])) for r in rows}):
 maes=[]
 for seed in range(101,121):
  data=[r for r in rows if r['mode']==mode and float(r['rate'])==rate and int(r['seed'])==seed];assert len(data)==33
  trialmaes=[]
  for trial in {r['trial'] for r in data}:
   tr=[r for r in data if r['trial']==trial];assert len(tr)==3
   trialmaes.append(statistics.mean(abs(float(r['prediction_s'])-float(r['target_s'])) for r in tr))
  mae=statistics.mean(trialmaes);maes.append(mae);seedrows.append(dict(mode=mode,rate=rate,seed=seed,trial_mae=mae))
 summary.append(dict(mode=mode,rate=rate,mean_trial_mae=statistics.mean(maes),min_seed_mae=min(maes),max_seed_mae=max(maes),H_reference_mae=H,M_clean_mae=M,seeds_better_than_H=sum(x<H for x in maes)))
for name,data in [('summary.csv',summary),('seed_metrics.csv',seedrows)]:
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
(OUT/'audit.json').write_text(json.dumps(dict(unique_rows=len(seen),target_matches=True,queries_per_seed_case=33,cases=5,seeds=20,interval_interpretation='min/max over artificial corruptions; not population confidence intervals'),indent=2))
print(json.dumps(summary,indent=2))
