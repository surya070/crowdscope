"""Frozen-design extraction and prediction; refuses failed movement admission."""
from pathlib import Path
import importlib.util,json,csv,hashlib
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'research/assistance';OUT=ROOT/'output/linkage_benchmark_v1'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
lib=load('comparison',ROOT/'research/run_empirical_comparison.py');f=load('features',P/'linkage_features.py')
def dumpcsv(name,rows):
 with (OUT/name).open('w',newline='') as fp:
  w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
 gate=json.loads((OUT/'movement_gate.json').read_text());assert gate['passed'],'Movement gate failed: fitting forbidden'
 if (OUT/'predictions.csv').exists():raise RuntimeError('Preserve existing predictions.')
 lock=json.loads((P/'linkage_implementation_freeze_v1.json').read_text())
 for name,h in lock['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
 manifest=json.loads((P/'linkage_manifest_v1.json').read_text());blocks={b['block']:b for b in manifest['blocks']}
 rows=[];missing=[];checks=0;ineligible=[]
 for run in manifest['runs']:
  r=json.loads((OUT/'runs'/f"{run['run_id']}.json").read_text());block=blocks[run['block']]
  edges=[(1,2),(3,4)] if run['mode']=='threshold' else [];shuffled=[(1,4),(3,2)] if edges else []
  for t in manifest['query_times_s']:
   if t>=r['clearance_s']:ineligible.append(dict(run=run['run_id'],t=t));continue
   a=f.extract(r['frames'],block,t,edges);b=f.extract(r['frames'],block,t,shuffled)
   prefix=[v for v in r['frames'] if v['t']<=t+1e-8]
   assert a==f.extract(prefix,block,t,edges);assert b==f.extract(prefix,block,t,shuffled);checks+=2
   assert all(a[k]==b[k] for k in f.M)
   base=dict(trial=run['run_id'],block=run['block'],layout=block['layout'],split=run['split'],mode=run['mode'],gain=run['gain'],time_s=t,target_s=r['clearance_s']-t,**a)
   base.update({f'shuffled_{k}':b[k] for k in f.LINKS});rows.append(base)
   if run['mode']=='threshold' and run['split']=='evaluation':
    for seed in manifest['noise_seeds']:
     kept=[edge for i,edge in enumerate(edges) if int.from_bytes(hashlib.sha256(f'{seed}/{run["block"]}/{i}'.encode()).digest()[:8],'big')/2**64>=.5]
     x=f.extract(prefix,block,t,kept);assert all(a[k]==x[k] for k in f.M)
     missing.append(dict(base,seed=seed,**{k:x[k] for k in f.LINKS}))
 dumpcsv('features.csv',rows);dumpcsv('missing_features.csv',missing)
 (OUT/'feature_checks.json').write_text(json.dumps(dict(prefix_checks=checks,rows=len(rows),ineligible=ineligible,missing_rows=len(missing)),indent=2))
 variants={'M':f.M,'F_counts':f.M+f.COUNTS,'F_correct':f.M+f.LINKS,'F_shuffled':f.M+[f'shuffled_{k}' for k in f.LINKS]}
 grid=[{'family':'ridge','alpha':a} for a in [.1,1,10,100]]+[dict(family='boosting',learning_rate=lr,max_depth=d,n_estimators=n) for lr in [.03,.1] for d in [2,3] for n in [50,100]]
 preds=[];trace=[];selected=[]
 for gain in [1.,1.15]:
  data=[r for r in rows if r['mode']=='threshold' and r['gain']==gain];train=[r for r in data if r['split']=='train'];val=[r for r in data if r['split']=='validation'];test=[r for r in data if r['split']=='evaluation']
  assert not {r['block'] for r in train}&{r['block'] for r in val+test};assert not {r['block'] for r in val}&{r['block'] for r in test}
  def save(variant,family,c,features,targetrows=None,seed=None):
   tr=targetrows if targetrows is not None else test;pp=lib.fit_predict(c,train,tr,features)
   for row,pred in zip(tr,pp):preds.append(dict(run=row['trial'],block=row['block'],layout=row['layout'],gain=gain,time_s=row['time_s'],variant=variant,family=family,seed=seed if seed is not None else '',target_s=row['target_s'],prediction_s=float(pred)))
  for variant,features in variants.items():
   scores=[]
   for c in grid:
    score=lib.score(val,lib.fit_predict(c,train,val,features));scores.append((score,c));trace.append(dict(gain=gain,variant=variant,candidate=c,validation_mae=score))
   for family in ['selected','ridge','boosting']:
    pool=scores if family=='selected' else [s for s in scores if s[1]['family']==family];score,c=min(pool,key=lambda v:v[0]);save(variant,family,c,features);selected.append(dict(gain=gain,variant=variant,family=family,candidate=c,validation_mae=score))
    if variant=='F_correct' and family=='selected':
     for seed in manifest['noise_seeds']:save('F_missing','selected',c,features,[r for r in missing if r['gain']==gain and r['seed']==seed],seed)
  save('baseline','constant',{'family':'constant'},f.M)
  travel=min([{'family':'travel','floor':v} for v in [.1,.2,.3]],key=lambda c:lib.score(val,lib.fit_predict(c,train,val,f.M)));save('baseline','travel',travel,f.M)
 dumpcsv('predictions.csv',preds);(OUT/'selection_trace.json').write_text(json.dumps(trace,indent=2));(OUT/'selections.json').write_text(json.dumps(selected,indent=2));print('Saved predictions:',len(preds))
if __name__=='__main__':main()
