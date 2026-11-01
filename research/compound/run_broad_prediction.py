"""Validation-selected follow-up; freeze models before generating fresh outcomes."""
import os
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[key]='1'
import copy,hashlib,pickle,sys,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import numpy as np
from src.recovery.common import ROOT,read,write,sha
from src.compound.study import design,simulate
from src.broad_prediction import Learner,FAMILIES,candidates,arrays,inputs,causal_history
from src.recovery.models import weights,score
from src.recovery.evaluation import run_metrics,blocks,macro,interval

OUT=ROOT/'output/compound/broad_prediction_001'
OLD=ROOT/'output/compound/comparison_001'
SOURCES=['src/broad_prediction.py','research/compound/run_broad_prediction.py',
 'research/compound/broad_prediction_protocol_v1.md','src/compound/study.py',
 'src/compound/movement.py','src/recovery/models.py','src/recovery/evaluation.py']
def hashes():return {p:sha(ROOT/p) for p in SOURCES}
def save(name,obj):write(OUT/name,obj)
def clip(p,rows):return np.clip(p,0,[180-r['t'] for r in rows])
def subset(rows,h,partition):
 ids=[i for i,r in enumerate(rows) if r['partition']==partition]
 return [rows[i] for i in ids],h[ids]
def check_coverage(rows,runs):
 assert {r['run_id'] for r in rows}=={r['run_id'] for r in runs},'Unqueried run: cannot silently assign zero error'
def development(cfg,manifest):
 results=[];provenance={};original_hashes=read(OLD/'trajectory_hashes.json')
 for row in manifest['runs']:
  if row['variant']!='main':continue
  p=OLD/'trajectories'/(row['run_id']+'.json')
  assert sha(p)==original_hashes[row['run_id']]
  provenance[row['run_id']]=sha(p)
  r=read(p);r['run']['partition']='train' if row['slot']<4 else 'validation';results.append(r)
 rows,h=arrays(results,cfg);runs=[r['run'] for r in results]
 check_coverage(rows,runs)
 # Meaningful causality check: outcomes, private gains and future frames cannot alter input.
 r=results[0];a=causal_history(r,5,cfg);changed=copy.deepcopy(r)
 changed['frames']=[f for f in changed['frames'] if f['t']<=4.8+1e-9]
 changed['completion_s']=999;changed['capped_completion_s']=999;changed['private_reserved_edges']=[]
 assert np.array_equal(a,causal_history(changed,5,cfg))
 train_blocks={r['block_id'] for r in runs if r['partition']=='train'}
 val_blocks={r['block_id'] for r in runs if r['partition']=='validation'}
 assert not train_blocks&val_blocks and len(train_blocks)==32 and len(val_blocks)==16
 save('development_provenance.json',provenance);save('development_rows.json',rows);save('development_runs.json',runs)
 np.save(OUT/'development_history.npy',h)
 save('input_checks.json',{'causal_future_mutation':True,'static_history_endpoint':True,'train_blocks':32,'validation_blocks':16,'queries':len(rows)})
 return rows,h,runs
def fresh_manifest(old):
 oldseeds={s for r in old['runs'] for s in r['seeds'].values()};newseeds=set();runs=[]
 conditions=['independent','family_only','assistance_only','family_and_assistance']
 for g in ['G5','G6','G1','G2','G3','G4']:
  for n in [8,12]:
   for slot in range(3):
    block=f'broad_{g}_n{n}_s{slot}'
    seeds={k:int.from_bytes(hashlib.sha256(f'rm-broad-20261101-v1:{block}:{k}'.encode()).digest()[:4],'big') for k in ['capability','placement','gain','corruption']}
    assert not set(seeds.values())&oldseeds and not set(seeds.values())&newseeds
    newseeds.update(seeds.values())
    for c in conditions:runs.append({'run_id':block+'__'+c,'block_id':block,'geometry':g,'n':n,'slot':slot,'condition':c,'variant':'broad_geometry' if g in ['G5','G6'] else 'broad_known','partition':'fresh_geometry_test' if g in ['G5','G6'] else 'fresh_known_test','seeds':seeds})
 return {'runs':runs,'namespace':'rm-broad-20261101-v1'}
def train():
 if (OUT/'selection_freeze.json').exists():raise RuntimeError('Models already frozen; no retraining allowed in this output')
 cfg,manifest=design();OUT.mkdir(parents=True,exist_ok=True)
 cfg=copy.deepcopy(cfg);cfg['geometry'] += [{'id':'G5','length':24,'width':1.05},{'id':'G6','length':28,'width':1.15}]
 save('config.json',cfg);save('manifest.json',fresh_manifest(manifest))
 initial=hashes();save('source_freeze.json',initial)
 rows,h,runs=development(cfg,manifest);tr,ht=subset(rows,h,'train');va,hv=subset(rows,h,'validation')
 rt=[r for r in runs if r['partition']=='train'];rv=[r for r in runs if r['partition']=='validation']
 tuning=[];chosen={};validation=[];models={};started=time.time()
 for family in FAMILIES:
  for info in ['A','M','F']:
   xt=inputs(ht,info,family);xv=inputs(hv,info,family);scores=[]
   for setting in candidates(family):
    model=Learner(family,setting).fit(xt,np.array([r['target'] for r in tr]),weights(tr,rt))
    p=clip(model.predict(xv),va);mae=score(va,p,rv);scores.append(mae)
    tuning.append({'family':family,'information':info,'setting':setting,'validation_mae_s':mae})
    validation.extend({ 'family':family,'information':info,'setting':setting,'run_id':r['run_id'],'t':r['t'],'target':r['target'],'prediction':float(v)} for r,v in zip(va,p))
    print('Candidate',family,info,setting,round(mae,6),'elapsed',round(time.time()-started),flush=True)
   index=int(np.argmin(scores));setting=candidates(family)[index]
   chosen[family+'__'+info]={'setting':setting,'validation_mae_s':scores[index]}
   model=Learner(family,setting).fit(inputs(h,info,family),np.array([r['target'] for r in rows]),weights(rows,runs))
   path=OUT/'models'/(family+'__'+info+'.pkl');path.parent.mkdir(exist_ok=True);path.write_bytes(pickle.dumps(model,protocol=5))
   loaded=pickle.loads(path.read_bytes());assert np.allclose(model.predict(inputs(hv,info,family)),loaded.predict(inputs(hv,info,family)),rtol=0,atol=1e-10)
   models[path.relative_to(OUT).as_posix()]=sha(path)
   save('tuning.json',tuning)
 best={i:min(FAMILIES,key=lambda f:chosen[f+'__'+i]['validation_mae_s']) for i in ['A','M','F']}
 assert hashes()==initial
 save('validation_predictions.json',validation);save('selection.json',{'family_settings':chosen,'best_family':best,'selection_data':'development validation only','training_seconds':time.time()-started})
 save('selection_freeze.json',{'source_hashes':initial,'models':models,'selection_sha256':sha(OUT/'selection.json'),'manifest_sha256':sha(OUT/'manifest.json'),'config_sha256':sha(OUT/'config.json'),'frozen_before_fresh_generation':True})
 print('FROZEN',best,flush=True)
def verify():
 frozen=read(OUT/'selection_freeze.json');assert hashes()==frozen['source_hashes']
 for p,h in frozen['models'].items():assert sha(OUT/p)==h
 for name in ['selection','manifest','config']:assert sha(OUT/(name+'.json'))==frozen[name+'_sha256']
def task(cfg,row):return simulate(cfg,row)
def generate():
 verify();cfg=read(OUT/'config.json');runs=read(OUT/'manifest.json')['runs'];completed={}
 if (OUT/'trajectory_hashes.json').exists():completed=read(OUT/'trajectory_hashes.json')
 for rid,h in completed.items():assert sha(OUT/'trajectories'/(rid+'.json'))==h
 pending=[r for r in runs if r['run_id'] not in completed]
 with ProcessPoolExecutor(max_workers=4,max_tasks_per_child=1) as pool:
  jobs={pool.submit(task,cfg,r):r for r in pending}
  for future in as_completed(jobs):
   r=jobs[future];result=future.result();p=OUT/'trajectories'/(r['run_id']+'.json');write(p,result);completed[r['run_id']]=sha(p);save('trajectory_hashes.json',completed)
   save('status.json',{'phase':'generating','completed':len(completed),'planned':len(runs)})
   print('Fresh',len(completed),'/',len(runs),r['run_id'],result['complete'],result['capped_completion_s'],flush=True)
 verify();assert len(completed)==144
 results=[read(OUT/'trajectories'/(r['run_id']+'.json')) for r in runs]
 rows,h=arrays(results,cfg);check_coverage(rows,runs)
 save('fresh_rows.json',rows);np.save(OUT/'fresh_history.npy',h)
 save('outcomes.json',[{'run':r['run'],'complete':r['complete'],'capped_completion_s':r['capped_completion_s'],'remaining':r['remaining_ids']} for r in results])
def evaluate():
 verify();rows=read(OUT/'fresh_rows.json');h=np.load(OUT/'fresh_history.npy');runs=read(OUT/'manifest.json')['runs'];selection=read(OUT/'selection.json')
 predictions=[];summary={};metricsets={}
 for partition in ['fresh_geometry_test','fresh_known_test']:
  rr,hh=subset(rows,h,partition);rs=[r for r in runs if r['partition']==partition];summary[partition]={}
  for family in FAMILIES:
   summary[partition][family]={}
   for info in ['A','M','F']:
    model=pickle.loads((OUT/'models'/(family+'__'+info+'.pkl')).read_bytes());p=clip(model.predict(inputs(hh,info,family)),rr)
    metrics=run_metrics(rr,p,rs);metricsets[partition,family,info]=metrics
    summary[partition][family][info]={'mae_s':macro(blocks(metrics)),'rmse_s':float(np.sqrt(macro(blocks(metrics,'mse')))),'mean_underprediction_s':macro(blocks(metrics,'underprediction'))}
    predictions.extend({**{k:r[k] for k in ['run_id','block_id','geometry','t','target']},'partition':partition,'family':family,'information':info,'prediction':float(v)} for r,v in zip(rr,p))
   summary[partition][family]['M_minus_F']=interval(metricsets[partition,family,'M'],metricsets[partition,family,'F'])
  best=selection['best_family'];summary[partition]['validation_selected']={'families':best,'metrics':{i:summary[partition][best[i]][i] for i in ['A','M','F']},'M_minus_F':interval(metricsets[partition,best['M'],'M'],metricsets[partition,best['F'],'F'])}
 save('predictions.json',predictions);save('summary.json',summary)
 save('status.json',{'phase':'evaluated','completed':144,'audit_required':True})
 print('RESULT',summary['fresh_geometry_test']['validation_selected'],flush=True)
if __name__=='__main__':
 mode=sys.argv[1]
 {'train':train,'generate':generate,'evaluate':evaluate}[mode]()
