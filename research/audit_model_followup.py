"""Reconstruct five-family scores independently from saved predictions."""
from pathlib import Path
import csv,json,statistics,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/model_followup_v1'
def read(p):return list(csv.DictReader(p.open()))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 rows=read(OUT/'predictions.csv');lock=json.loads((OUT/'lock.json').read_text())
 assert all(sha(ROOT/p)==h for p,h in lock['source_hashes'].items())
 assert sha(ROOT/'research/run_model_followup.py')==lock['runner_sha256']
 emp=read(ROOT/'research/data/forecast_bundle/features.csv');syn=read(ROOT/'output/linkage_benchmark_v1/features.csv')
 manifest=json.loads((ROOT/'research/data/forecast_bundle/manifest.json').read_text())
 targets={(r['trial'],float(r['time_s'])):float(r['target_s']) for r in emp if float(r['history_s'])==1}
 stargets={(r['trial'],float(r['time_s'])):r for r in syn}
 seen=set()
 for r in rows:
  key=tuple(r[k] for k in ['study','group','variant','family','seed','trial','time_s']);assert key not in seen;seen.add(key)
  if r['study']=='empirical':
   fold=next(f for f in manifest['folds'] if float(f['evaluation_width'])==float(r['group']))
   assert r['trial'] in fold['evaluation_trials']
   y=targets[(r['trial'],float(r['time_s']))]
  else:
   source=stargets[(r['trial'],float(r['time_s']))]
   assert source['split']=='evaluation' and source['mode']=='threshold' and float(source['gain'])==float(r['group'])
   y=float(source['target_s'])
  assert abs(float(r['target_s'])-y)<1e-10 and float(r['prediction_s'])>=0
 metrics=[]
 for study in ['empirical','synthetic']:
  for gain in (['all-widths'] if study=='empirical' else ['1.0','1.15']):
   for variant in (['H','M'] if study=='empirical' else ['M','F_counts','F_correct','F_shuffled']):
    for family in ['ridge','rbf','boosting','forest','mlp']:
     scores=[]
     for seed in ([113,271,509] if family=='mlp' else [113]):
      rs=[r for r in rows if r['study']==study and (study=='empirical' or r['group']==gain) and r['variant']==variant and r['family']==family and int(r['seed'])==seed]
      assert len(rs)==(33 if study=='empirical' else 24)
      trials=sorted({r['trial'] for r in rs});assert len(trials)==(11 if study=='empirical' else 8)
      scores.append(statistics.mean(statistics.mean(abs(float(r['prediction_s'])-float(r['target_s'])) for r in rs if r['trial']==t) for t in trials))
     metrics.append(dict(study=study,gain=gain,variant=variant,family=family,mae=statistics.mean(scores),seed_min=min(scores),seed_max=max(scores),seeds=len(scores)))
 with (OUT/'metrics.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(metrics[0]));w.writeheader();w.writerows(metrics)
 assert len(rows)==1806 and len(metrics)==50
 # Original matched ridge predictions must reproduce, not only aggregate scores.
 old=read(ROOT/'output/empirical_comparison_v1/predictions.csv')
 expected={(r['trial'],float(r['time_s']),r['condition']):float(r['prediction_s']) for r in old if r['family']=='ridge' and float(r['history_s'])==1}
 diff=max(abs(float(r['prediction_s'])-expected[(r['trial'],float(r['time_s']),r['variant'])]) for r in rows if r['study']=='empirical' and r['family']=='ridge');assert diff<1e-9
 a=dict(predictions=len(rows),metric_groups=len(metrics),unique_keys=True,targets_and_evaluation_membership=True,input_and_runner_hashes_match=True,original_empirical_ridge_max_difference=diff,convergence_warnings=len(json.loads((OUT/'warnings.json').read_text())),predictions_sha256=sha(OUT/'predictions.csv'))
 (OUT/'audit.json').write_text(json.dumps(a,indent=2))
 print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
