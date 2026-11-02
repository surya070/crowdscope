"""Deployment-only label stress test of fixed, clean-trained primary models."""
from pathlib import Path
import sys,os,csv,json,hashlib,zipfile,re,importlib.util
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps/prediction-benchmark'))
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor
BASE=ROOT/'output/empirical_comparison_v1';OUT=ROOT/'output/label_sensitivity_v1'
BUNDLE=ROOT/'research/data/forecast_bundle'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def uniform(seed,trial,tid):
 return int.from_bytes(hashlib.sha256(f'{seed}/{trial}/{tid}'.encode()).digest()[:8],'big')/2**64
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if (OUT/'predictions.csv').exists():raise RuntimeError('Existing sensitivity run is append-only.')
 manifest=json.loads((BUNDLE/'manifest.json').read_text());features=manifest['H']+manifest['M_additions']
 data=[r for r in csv.DictReader((BUNDLE/'features.csv').open()) if float(r['history_s'])==1]
 selections=json.loads((BASE/'selections.json').read_text())
 cases=[('missing_zero_fill',p) for p in [.25,.5,.75]]+[('symmetric_flip',p) for p in [.1,.25]]
 lock=dict(date='2026-11-02',history_s=1,seeds=list(range(101,121)),cases=cases,scope='fixed clean-trained selected M; deployment-only label perturbation',missing_handling='unknown labels receive zero-positive contribution; denominator remains full cohort; no uncertainty-aware retraining',sampling='stable SHA256-based trial/track mask, shared across checkpoints; not independent-person randomisation',selection='reuse existing selected model hyperparameters; no noise tuning',features_sha256=sha(BUNDLE/'features.csv'),original_predictions_sha256=sha(BASE/'predictions.csv'),runner_sha256=sha(Path(__file__)))
 (OUT/'lock.json').write_text(json.dumps(lock,indent=2))
 spec=importlib.util.spec_from_file_location('extractor',ROOT/'research/data/build_forecast_features.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 cohorts={}
 with zipfile.ZipFile(next((ROOT/'backups').glob('*.zip'))) as z:
  for trial in {r['trial'] for r in data}:
   local=ROOT/f'data/raw/sime2017/members/{trial}.txt'
   raw=local.read_bytes() if local.exists() else z.read(f'data/raw/sime2017/members/{trial}.txt')
   assert hashlib.sha256(raw).hexdigest()==manifest['source_sha256'][trial]
   text=raw.decode().replace('\r','');tracks=defaultdict(dict)
   links={int(a):int(b) for a,b in re.findall(r'^#\s*(\d+)\|\s*(\d+)\s*$',text,re.M)}
   wc={tid for tid,pid in links.items() if pid in range(34,41)}
   for line in text.splitlines():
    if not line.strip() or line.startswith('#'):continue
    a=line.split();tracks[int(a[0])][int(a[1])]=(float(a[2]),float(a[3]))
   for r in [r for r in data if r['trial']==trial]:
    frame=int(float(r['time_s'])*25)
    ids,clean=mod.extract(tracks,frame,25,float(r['bottleneck_width']),float(r['corridor_width']),wc)
    assert all(abs(clean[k]-float(r[k]))<1e-10 for k in features)
    speeds=np.array([np.linalg.norm(np.array(tracks[t][frame])-tracks[t][frame-25]) for t in ids])
    dist=np.array([2.4-tracks[t][frame][0] for t in ids]);truth=np.array([t in wc for t in ids])
    cohorts[trial,float(r['time_s'])]=(ids,speeds,dist,truth)
 predictions=[];clean_match=0
 previous=[r for r in csv.DictReader((BASE/'predictions.csv').open()) if r['condition']=='M' and r['family']=='selected' and float(r['history_s'])==1]
 for fold in manifest['folds']:
  tr=[r for r in data if r['trial'] in fold['training_trials']];te=[r for r in data if r['trial'] in fold['evaluation_trials']]
  c=next(s['candidate'] for s in selections if s['condition']=='M' and s['reported_family']=='selected' and s['history_s']==1 and s['evaluation_width']==fold['evaluation_width'])
  model=make_pipeline(StandardScaler(),Ridge(alpha=c['alpha'])) if c['family']=='ridge' else GradientBoostingRegressor(random_state=113,loss='squared_error',learning_rate=c['learning_rate'],max_depth=c['max_depth'],n_estimators=c['n_estimators'])
  model.fit([[float(r[k]) for k in features] for r in tr],[float(r['target_s']) for r in tr])
  cp=np.maximum(0,model.predict([[float(r[k]) for k in features] for r in te]))
  for r,p in zip(te,cp):
   saved=next(v for v in previous if v['trial']==r['trial'] and float(v['time_s'])==float(r['time_s']))
   assert abs(p-float(saved['prediction_s']))<1e-8;clean_match+=1
  for mode,rate in cases:
   for seed in lock['seeds']:
    modified=[];details=[]
    for r in te:
     ids,speeds,dist,truth=cohorts[r['trial'],float(r['time_s'])]
     affected=np.array([uniform(seed,r['trial'],tid)<rate for tid in ids])
     observed=truth&~affected if mode=='missing_zero_fill' else truth^affected
     n=int(observed.sum());new=dict(r)
     new.update(wheelchair_count=n,wheelchair_fraction=n/len(ids),wheelchair_mean_speed=float(speeds[observed].mean()) if n else 0.,wheelchair_max_distance=float(dist[observed].max()) if n else 0.,wheelchair_present=int(n>0))
     assert all(float(new[k])==float(r[k]) for k in manifest['H'])
     modified.append([float(new[k]) for k in features]);details.append((len(ids),int(affected.sum()),int(truth.sum()),n))
    pp=np.maximum(0,model.predict(modified));assert np.isfinite(pp).all()
    for r,p,d in zip(te,pp,details):predictions.append(dict(trial=r['trial'],time_s=float(r['time_s']),mode=mode,rate=rate,seed=seed,target_s=float(r['target_s']),prediction_s=float(p),cohort_count=d[0],affected_labels=d[1],true_wheelchair_count=d[2],observed_positive_count=d[3]))
 with (OUT/'predictions.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(predictions[0]));w.writeheader();w.writerows(predictions)
 (OUT/'checks.json').write_text(json.dumps(dict(clean_predictions_reproduced=clean_match,unchanged_history_features=True,rows=len(predictions),predictions_sha256=sha(OUT/'predictions.csv')),indent=2))
 print(json.dumps({'predictions':len(predictions),'clean_predictions_reproduced':clean_match}))
if __name__=='__main__':main()
