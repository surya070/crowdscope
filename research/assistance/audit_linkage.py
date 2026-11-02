"""Independent movement-record and prediction metric audit."""
from pathlib import Path
import json,csv,hashlib,statistics,math
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/linkage_benchmark_v1';P=ROOT/'research/assistance'
def main():
 manifest=json.loads((P/'linkage_manifest_v1.json').read_text());gate=json.loads((OUT/'movement_gate.json').read_text());assert gate['passed']
 planned={r['run_id']:r for r in manifest['runs']};assert len(gate['records'])==len(planned)==192
 for record in gate['records']:
  p=OUT/'runs'/f"{record['run_id']}.json";assert hashlib.sha256(p.read_bytes()).hexdigest()==record['sha256']
  r=json.loads(p.read_text());assert not r['failures'] and r['exited']==r['occupants']
  for frame in r['frames']:assert {int(i) for i in frame['positions']}|set(frame['exited'])==set(range(1,r['occupants']+1))
  if record['fine_pass'] is not None:
   fp=OUT/'runs'/f"{record['run_id']}_fine.json";assert hashlib.sha256(fp.read_bytes()).hexdigest()==record['fine_sha256']
   fine=json.loads(fp.read_text());assert not fine['failures'];assert abs(fine['clearance_s']-r['clearance_s'])<=max(.2,.01*fine['clearance_s'])
 rows=list(csv.DictReader((OUT/'predictions.csv').open()));seen=set();summaries=[];perrun=[]
 for r in rows:
  plan=planned[r['run']];assert plan['split']=='evaluation' and plan['mode']=='threshold' and float(r['gain'])==plan['gain']
  raw=json.loads((OUT/'runs'/f"{r['run']}.json").read_text());assert abs(float(r['target_s'])-(raw['clearance_s']-float(r['time_s'])))<1e-10
  assert math.isfinite(float(r['prediction_s'])) and float(r['prediction_s'])>=0
  key=(r['run'],r['time_s'],r['variant'],r['family'],r['seed']);assert key not in seen;seen.add(key)
 groups=sorted({(r['gain'],r['variant'],r['family'],r['seed']) for r in rows})
 for gain,variant,family,seed in groups:
  selected=[r for r in rows if (r['gain'],r['variant'],r['family'],r['seed'])==(gain,variant,family,seed)]
  assert len(selected)==24
  trialmetrics=[]
  for run in sorted({r['run'] for r in selected}):
   q=[r for r in selected if r['run']==run];assert len(q)==3
   errors=[float(r['prediction_s'])-float(r['target_s']) for r in q]
   entry=dict(gain=float(gain),variant=variant,family=family,seed=seed,run=run,layout=q[0]['layout'],mae=statistics.mean(map(abs,errors)),bias=statistics.mean(errors));perrun.append(entry);trialmetrics.append(entry)
  summaries.append(dict(gain=float(gain),variant=variant,family=family,seed=seed,runs=len(trialmetrics),mae=statistics.mean(r['mae'] for r in trialmetrics),bias=statistics.mean(r['bias'] for r in trialmetrics),worst_run_mae=max(r['mae'] for r in trialmetrics)))
 for name,data in [('metrics.csv',summaries),('run_metrics.csv',perrun)]:
  with (OUT/name).open('w',newline='') as fp:w=csv.DictWriter(fp,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 audit=dict(main_runs=192,fine_runs=48,movement_records_verified=True,predictions=len(rows),unique_prediction_keys=True,evaluation_only_predictions=True,targets_match=True,metric_groups=len(summaries),predictions_sha256=hashlib.sha256((OUT/'predictions.csv').read_bytes()).hexdigest())
 (OUT/'audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps([r for r in summaries if r['family']=='selected' and r['seed']==''],indent=2))
if __name__=='__main__':main()
