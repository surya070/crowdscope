"""Nested width-group exploratory comparison. No simulator or future inputs."""
from pathlib import Path
import sys,os,csv,json,hashlib,itertools
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps/prediction-benchmark'))
os.environ.setdefault('OMP_NUM_THREADS','1')
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import GradientBoostingRegressor
import sklearn
BUNDLE=ROOT/'research/data/forecast_bundle'
OUT=ROOT/'output/empirical_comparison_v1'

def hsh(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def make_model(c):
 if c['family']=='ridge':return make_pipeline(StandardScaler(),Ridge(alpha=c['alpha']))
 if c['family']=='boosting':return GradientBoostingRegressor(random_state=113,loss='squared_error',learning_rate=c['learning_rate'],max_depth=c['max_depth'],n_estimators=c['n_estimators'])
 return None
def fit_predict(c,train,test,features):
 y=np.array([float(r['target_s']) for r in train])
 if c['family']=='constant':return np.full(len(test),np.median(y))
 if c['family']=='travel':return np.array([float(r['max_distance'])/max(float(r['mean_speed']),c['floor']) for r in test])
 model=make_model(c)
 model.fit(np.array([[float(r[f]) for f in features] for r in train]),y)
 return np.maximum(0,model.predict(np.array([[float(r[f]) for f in features] for r in test])))
def score(rows,preds):
 trials=sorted({r['trial'] for r in rows})
 return float(np.mean([np.mean([abs(float(r['target_s'])-float(p)) for r,p in zip(rows,preds) if r['trial']==t]) for t in trials]))
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if (OUT/'predictions.csv').exists():raise RuntimeError('Append-only run: predictions already exist; inspect before making a new run.')
 manifest=json.loads((BUNDLE/'manifest.json').read_text())
 assert hsh(BUNDLE/'features.csv')==manifest['features_sha256']
 data=list(csv.DictReader((BUNDLE/'features.csv').open()))
 grid=[{'family':'ridge','alpha':a} for a in [.1,1,10,100]]
 grid += [dict(family='boosting',learning_rate=lr,max_depth=d,n_estimators=n) for lr,d,n in itertools.product([.03,.1],[2,3],[50,100])]
 lock=dict(date='2026-11-02',scope='exploratory real-data observed-cohort passage; shared participants',features_sha256=hsh(BUNDLE/'features.csv'),manifest_sha256=hsh(BUNDLE/'manifest.json'),runner_sha256=hsh(Path(__file__)),sklearn=sklearn.__version__,candidates=grid,histories=[.4,1.,2.],primary_history=1.,primary_metric='equal-trial MAE',selection='inner leave-width-out pooled trial MAE; deterministic candidate order breaks ties',primary_contrast='H minus M MAE for validation-selected models',matched_family_contrasts=['ridge','boosting'],baselines=['training median','max_distance/max(mean_observed_speed,floor), inner-selected floor [.1,.2,.3]'],prediction_clip='lower bound zero for learned predictors',intervals='none: small repeated-population sample; report trial and width differences',noise_sensitivity='deferred, not part of this initial H/M run',simulator_used=False,prospective_independent_test=False)
 (OUT/'modelling_lock.json').write_text(json.dumps(lock,indent=2))
 predictions=[];trace=[];selections=[]
 for history in [.4,1.,2.]:
  subset=[r for r in data if float(r['history_s'])==history]
  for fold in manifest['folds']:
   train=[r for r in subset if r['trial'] in fold['training_trials']]
   test=[r for r in subset if r['trial'] in fold['evaluation_trials']]
   assert not {r['trial'] for r in train}&{r['trial'] for r in test}
   def inner_score(c,features):
    validation_rows=[];validation_preds=[]
    for inner in fold['inner_folds']:
     tr=[r for r in train if r['trial'] in inner['training_trials']]
     va=[r for r in train if r['trial'] in inner['validation_trials']]
     assert tr and va and not {r['trial'] for r in tr}&{r['trial'] for r in va}
     validation_rows+=va;validation_preds.extend(fit_predict(c,tr,va,features))
    return score(validation_rows,validation_preds)
   def save(condition,family,c,features):
    pred=fit_predict(c,train,test,features);assert np.isfinite(pred).all()
    selections.append(dict(history_s=history,evaluation_width=fold['evaluation_width'],condition=condition,reported_family=family,candidate=c))
    for r,p in zip(test,pred):predictions.append(dict(trial=r['trial'],time_s=float(r['time_s']),history_s=history,evaluation_width=fold['evaluation_width'],condition=condition,family=family,target_s=float(r['target_s']),prediction_s=float(p)))
   for condition,features in [('H',manifest['H']),('M',manifest['H']+manifest['M_additions'])]:
    scored=[]
    for c in grid:
     value=inner_score(c,features);scored.append((value,c))
     trace.append(dict(history_s=history,evaluation_width=fold['evaluation_width'],condition=condition,candidate=c,inner_trial_mae=value))
    chosen=min(scored,key=lambda x:x[0])[1]
    save(condition,'selected',chosen,features)
    for family in ['ridge','boosting']:
     c=min((s for s in scored if s[1]['family']==family),key=lambda x:x[0])[1]
     save(condition,family,c,features)
   save('baseline','constant',{'family':'constant'},manifest['H'])
   travel=min([{'family':'travel','floor':f} for f in [.1,.2,.3]],key=lambda c:inner_score(c,manifest['H']))
   save('baseline','travel',travel,manifest['H'])
 with (OUT/'predictions.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(predictions[0]));w.writeheader();w.writerows(predictions)
 (OUT/'selection_trace.json').write_text(json.dumps(trace,indent=2))
 (OUT/'selections.json').write_text(json.dumps(selections,indent=2))
 (OUT/'completion.json').write_text(json.dumps(dict(prediction_rows=len(predictions),candidate_inner_scores=len(trace),source_hashes_still_match=hsh(BUNDLE/'features.csv')==lock['features_sha256'],prediction_sha256=hsh(OUT/'predictions.csv')),indent=2))
 print(json.dumps({'saved_predictions':len(predictions),'inner_candidate_scores':len(trace)}))
if __name__=='__main__':main()
