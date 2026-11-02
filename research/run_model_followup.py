"""Exploratory five-family follow-up; never overwrites the original study."""
from pathlib import Path
import os,sys,csv,json,hashlib,itertools,warnings
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps/prediction-benchmark'))
sys.path.append(str(ROOT/'.deps/recovery-r1'))
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np
import sklearn
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import TransformedTargetRegressor
from sklearn.linear_model import Ridge
from sklearn.kernel_ridge import KernelRidge
from sklearn.ensemble import RandomForestRegressor,GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.exceptions import ConvergenceWarning
OUT=ROOT/'output/model_followup_v1'
SEEDS=[113,271,509]
GRID={
 'ridge':[dict(alpha=a) for a in [.1,1,10,100]],
 'rbf':[dict(alpha=a,gamma=g) for a,g in itertools.product([1,10],[.01,.1])],
 'boosting':[dict(learning_rate=lr,max_depth=d,n_estimators=100) for lr,d in itertools.product([.03,.1],[2,3])],
 'forest':[dict(n_estimators=200,max_depth=d,min_samples_leaf=l) for d,l in itertools.product([3,None],[1,3])],
 'mlp':[dict(hidden_layer_sizes=[h],alpha=a) for h,a in itertools.product([8,16],[.01,1.])]
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return list(csv.DictReader(p.open()))
def dump(name,rows):
 with (OUT/name).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def metric(rows,pred):
 return float(np.mean([np.mean([abs(float(r['target_s'])-v) for r,v in zip(rows,pred) if r['trial']==t]) for t in sorted({r['trial'] for r in rows})]))
WARN=[]
def predict(family,c,seed,tr,te,features):
 if family=='ridge': m=make_pipeline(StandardScaler(),Ridge(**c))
 elif family=='rbf': m=make_pipeline(StandardScaler(),KernelRidge(kernel='rbf',**c))
 elif family=='boosting': m=GradientBoostingRegressor(random_state=seed,**c)
 elif family=='forest': m=RandomForestRegressor(random_state=seed,n_jobs=1,**c)
 else:
  c=dict(c,hidden_layer_sizes=tuple(c['hidden_layer_sizes']))
  m=TransformedTargetRegressor(regressor=make_pipeline(StandardScaler(),MLPRegressor(solver='lbfgs',max_iter=2000,max_fun=50000,random_state=seed,**c)),transformer=StandardScaler())
 x=lambda rs:np.array([[float(r[k]) for k in features] for r in rs])
 with warnings.catch_warnings(record=True) as ws:
  warnings.simplefilter('always',ConvergenceWarning)
  m.fit(x(tr),np.array([float(r['target_s']) for r in tr]));p=np.maximum(0,m.predict(x(te)))
 for w in ws: WARN.append(dict(family=family,candidate=c,seed=seed,message=str(w.message)))
 assert np.isfinite(p).all()
 return p
def main():
 OUT.mkdir(exist_ok=True,parents=True)
 if (OUT/'lock.json').exists():raise RuntimeError('Preserve this attempt; lock exists.')
 bundle=ROOT/'research/data/forecast_bundle';manifest=json.loads((bundle/'manifest.json').read_text())
 syn=ROOT/'output/linkage_benchmark_v1/features.csv'
 sources=[bundle/'features.csv',bundle/'manifest.json',syn,ROOT/'research/assistance/linkage_features.py']
 lock=dict(date='2026-11-02',exploratory=True,prior_evaluation_outcomes_exposed=True,grid=GRID,mlp_seeds=SEEDS,other_seed=113,metric='equal-trial/run MAE; MLP mean of seed-wise errors, not ensemble errors',empirical='primary 1 s only; original nested leave-width-out folds',synthetic='both coordinated gain strata; original train/validation/evaluation blocks; no refit',selection='four candidates per family, deterministic first tie; MLP mean inner/validation MAE across all three seeds',mlp='one hidden layer, lbfgs, max_iter 2000, max_fun 50000; train-only input and target scaling',warning_policy='record all convergence warnings; retain predictions; no retry or grid change',original_headlines_unchanged=True,runner_sha256=sha(Path(__file__)),sklearn=sklearn.__version__,source_hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sources})
 (OUT/'lock.json').write_text(json.dumps(lock,indent=2))
 jobs=[]
 emp=[r for r in read(bundle/'features.csv') if float(r['history_s'])==1.]
 for fold in manifest['folds']:
  tr=[r for r in emp if r['trial'] in fold['training_trials']];te=[r for r in emp if r['trial'] in fold['evaluation_trials']]
  inner=[([r for r in tr if r['trial'] in f['training_trials']],[r for r in tr if r['trial'] in f['validation_trials']]) for f in fold['inner_folds']]
  for v,fs in [('H',manifest['H']),('M',manifest['H']+manifest['M_additions'])]:jobs.append(('empirical',str(fold['evaluation_width']),v,tr,te,inner,fs))
 import importlib.util
 spec=importlib.util.spec_from_file_location('linkfeatures',ROOT/'research/assistance/linkage_features.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
 data=read(syn)
 for gain in [1.,1.15]:
  rows=[r for r in data if r['mode']=='threshold' and float(r['gain'])==gain]
  tr=[r for r in rows if r['split']=='train'];va=[r for r in rows if r['split']=='validation'];te=[r for r in rows if r['split']=='evaluation']
  assert not {r['block'] for r in tr}&{r['block'] for r in va+te}
  assert not {r['block'] for r in va}&{r['block'] for r in te}
  for v,fs in {'M':f.M,'F_counts':f.M+f.COUNTS,'F_correct':f.M+f.LINKS,'F_shuffled':f.M+['shuffled_'+k for k in f.LINKS]}.items():jobs.append(('synthetic',str(gain),v,tr,te,[(tr,va)],fs))
 predictions=[];traces=[];selections=[]
 for study,group,variant,tr,te,inner,fs in jobs:
  assert not {r['trial'] for r in tr}&{r['trial'] for r in te}
  for family,grid in GRID.items():
   seeds=SEEDS if family=='mlp' else [113];scores=[]
   for c in grid:
    seed_scores=[]
    for seed in seeds:
     valrows=[];valpred=[]
     for it,iv in inner:
      assert not {r['trial'] for r in it}&{r['trial'] for r in iv}
      valrows+=iv;valpred.extend(predict(family,c,seed,it,iv,fs))
     seed_scores.append(metric(valrows,valpred))
    score=float(np.mean(seed_scores));scores.append(score)
    traces.append(dict(study=study,group=group,variant=variant,family=family,candidate=c,seed_scores=seed_scores,validation_mae=score))
   idx=min(range(len(scores)),key=lambda i:scores[i]);c=grid[idx]
   selections.append(dict(study=study,group=group,variant=variant,family=family,candidate=c,validation_mae=scores[idx]))
   for seed in seeds:
    for r,p in zip(te,predict(family,c,seed,tr,te,fs)):
     predictions.append(dict(study=study,group=group,variant=variant,family=family,seed=seed,trial=r['trial'],time_s=r['time_s'],target_s=r['target_s'],prediction_s=float(p)))
  print(study,group,variant,'complete',flush=True)
 dump('predictions.csv',predictions)
 for name,content in [('selection_trace.json',traces),('selections.json',selections),('warnings.json',WARN)]: (OUT/name).write_text(json.dumps(content,indent=2))
 assert all(sha(ROOT/p)==h for p,h in lock['source_hashes'].items())
 print('Saved',len(predictions),'predictions;',len(WARN),'fit warnings')
if __name__=='__main__':main()
