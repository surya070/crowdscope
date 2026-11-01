from pathlib import Path
import json,itertools,hashlib,sys,time
import numpy as np
from src.sime_replay import ROOT,load_trial,replay,metrics,free_flight,sha
O=ROOT/'output/sime_replay_v2';O.mkdir(exist_ok=True)
DEVELOPMENT=['1501','1507'];TEST=['1503','1505']
SOURCE=['src/sime_replay.py','research/compound/sime_replay_protocol_v2.md','research/compound/sime_replay_implementation_note_v2.md','research/compound/run_sime_replay.py']
def save(path,obj):path.write_text(json.dumps(obj,indent=2,allow_nan=False),encoding='utf-8')
def one(tid,p,dt=.02,frames=False):
 trial=load_trial(tid)
 if not trial['complete']:return {'trial':tid,'status':'ineligible','missing_ids':trial['missing_ids'],'metadata_count_agrees':trial['metadata_count_agrees']}
 if int(trial['metadata']['parameter']['subjects_with_disability'])!=0:raise ValueError('Reference replay cannot infer disability assignments')
 try:
  result=replay(trial['area'],trial['arrivals'],p,dt,frames)
 except Exception as exc:
  return {'trial':tid,'status':'failed','failure':str(exc),'params':p,'dt':dt}
 result.update(trial=tid,input_sha256=trial['source_sha256'],metrics=metrics(result,trial),baseline_metrics=metrics(free_flight(trial,p['speed']),trial),observed_crossings=trial['targets'],arrivals=trial['arrivals'])
 return result
def development():
 rows=[]
 for k,(v,r,T) in enumerate(itertools.product([1.2,1.4,1.6],[.18,.22,.24],[.6,1.0])):
  p={'speed':v,'radius':r,'time_gap':T};results=[]
  for tid in DEVELOPMENT:
   path=O/f'development_{k:02d}_{tid}.json'
   if path.exists():result=json.loads(path.read_text())
   else:result=one(tid,p);save(path,result)
   results.append(result)
  valid=all(x.get('status')=='completed' and x.get('metrics') for x in results)
  score=float(np.mean([x['metrics']['crossing_mae_s'] for x in results])) if valid else None
  row={'candidate':k,'params':p,'eligible':valid,'score_s':score,'trial_statuses':[x['status'] for x in results]};rows.append(row)
  save(O/'calibration_trace.json',rows)
  print(json.dumps(row),flush=True)
 eligible=[x for x in rows if x['eligible']]
 if not eligible:
  save(O/'development_stop.json',{'status':'no eligible development candidate','action':'Do not evaluate test trials or relax criteria; preserve failures.'});return
 best=min(eligible,key=lambda x:(round(x['score_s'],9),-x['params']['radius'],abs(x['params']['time_gap']-1),abs(x['params']['speed']-1.4)))
 freeze={'status':'selected on development only, before test acquisition/evaluation','selected':best,'files':{p:sha(ROOT/p) for p in SOURCE},'development_sources':{tid:sha(ROOT/'data/raw/sime2017/members'/f'{tid}.txt') for tid in DEVELOPMENT},'test_trials':TEST,'limitations':'Held-out runs and intermediate widths; not proven independent participants. Observed future inlet events are exogenous inputs, not end-to-end forecasts.'}
 if (O/'selected_freeze.json').exists():raise RuntimeError('Selection already frozen; do not overwrite')
 save(O/'selected_freeze.json',freeze)
 for tid in DEVELOPMENT:
  result=one(tid,best['params'],frames=True);save(O/f'selected_development_{tid}.json',result)
 print(json.dumps({'selected':best}),flush=True)
def test():
 freeze=json.loads((O/'selected_freeze.json').read_text())
 for path,h in freeze['files'].items():assert sha(ROOT/path)==h,path
 p=freeze['selected']['params'];summary=[]
 for tid in TEST:
  path=O/f'held_out_{tid}.json'
  if path.exists():result=json.loads(path.read_text())
  else:result=one(tid,p,frames=True);save(path,result)
  summary.append({k:v for k,v in result.items() if k not in ['frames','arrivals','observed_crossings','crossings','admissions']})
  print(json.dumps(summary[-1]),flush=True)
  finepath=O/f'held_out_fine_{tid}.json'
  if not finepath.exists():save(finepath,one(tid,p,dt=.01))
 save(O/'held_out_summary.json',summary)
if __name__=='__main__':
 {'develop':development,'test':test}[sys.argv[1]]()
