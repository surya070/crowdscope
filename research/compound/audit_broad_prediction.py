"""Separate-process reproduction and standard-library arithmetic audit."""
import os
for key in ['OMP_NUM_THREADS','MKL_NUM_THREADS','OPENBLAS_NUM_THREADS']:os.environ[key]='1'
import json,math,pickle,statistics,platform,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from src.recovery.common import ROOT,read,write,sha
from src.broad_prediction import inputs,FAMILIES
O=ROOT/'output/compound/broad_prediction_001'

def independent_mae(records):
 perrun=defaultdict(list);meta={}
 for r in records:
  perrun[r['run_id']].append(abs(r['prediction']-r['target']));meta[r['run_id']]=(r['geometry'],r['block_id'])
 byblock=defaultdict(list)
 for rid,errors in perrun.items():byblock[meta[rid]].append(statistics.mean(errors))
 bygeo=defaultdict(list)
 for (g,b),values in byblock.items():bygeo[g].append(statistics.mean(values))
 return statistics.mean(statistics.mean(v) for v in bygeo.values())

def main():
 from research.compound.run_broad_prediction import verify
 verify();rows=read(O/'fresh_rows.json');h=np.load(O/'fresh_history.npy');preds=read(O/'predictions.json');summary=read(O/'summary.json');manifest=read(O/'manifest.json')['runs']
 assert len(manifest)==144 and len({r['block_id'] for r in manifest})==36
 assert len({(r['run_id'],r['t']) for r in rows})==len(rows)
 assert len(preds)==len(rows)*18
 assert all(r['complete'] and not r['remaining'] for r in read(O/'outcomes.json'))
 for rid,digest in read(O/'trajectory_hashes.json').items():assert sha(O/'trajectories'/(rid+'.json'))==digest
 bykey=defaultdict(list)
 for p in preds:
  assert math.isfinite(p['prediction']) and 0<=p['prediction']<=180-p['t']
  bykey[p['partition'],p['family'],p['information']].append(p)
 maximum=0;metricerror=0
 for family in FAMILIES:
  for info in ['A','M','F']:
   model=pickle.loads((O/'models'/(family+'__'+info+'.pkl')).read_bytes())
   reproduced=np.clip(model.predict(inputs(h,info,family)),0,[180-r['t'] for r in rows])
   lookup={(p['run_id'],p['t']):p['prediction'] for p in preds if p['family']==family and p['information']==info}
   diff=max(abs(float(p)-lookup[r['run_id'],r['t']]) for r,p in zip(rows,reproduced));maximum=max(maximum,diff)
   assert diff<1e-5,(family,info,diff)
   for partition in ['fresh_geometry_test','fresh_known_test']:
    error=abs(independent_mae(bykey[partition,family,info])-summary[partition][family][info]['mae_s']);metricerror=max(metricerror,error);assert error<1e-10
 # Verify validation-only selection, candidate counts and absence of near ties.
 tuning=read(O/'tuning.json');selection=read(O/'selection.json');minimum_gap=math.inf
 assert len(tuning)==54
 for family in FAMILIES:
  for info in ['A','M','F']:
   group=[r for r in tuning if r['family']==family and r['information']==info];assert len(group)==3
   ordered=sorted(group,key=lambda r:r['validation_mae_s']);minimum_gap=min(minimum_gap,ordered[1]['validation_mae_s']-ordered[0]['validation_mae_s'])
   assert ordered[0]['setting']==selection['family_settings'][family+'__'+info]['setting']
 for info in ['A','M','F']:
  best=min(FAMILIES,key=lambda f:selection['family_settings'][f+'__'+info]['validation_mae_s']);assert best==selection['best_family'][info]
 assert minimum_gap>1e-12
 import sklearn,torch,scipy,shapely
 audit={'status':'passed','new_trajectories':144,'new_matched_blocks':36,'new_queries':len(rows),'models':18,'candidates':54,'independent_mae_max_difference_s':metricerror,'fresh_process_prediction_max_difference_s':maximum,'minimum_candidate_selection_gap_s':minimum_gap,'original_test_data_reclassified_as_development':True,'model_freeze_before_fresh_outcomes':True,'source_and_trajectory_hashes_verified':True,'input_checks':read(O/'input_checks.json'),'software':{'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'torch':torch.__version__,'shapely':shapely.__version__},'limitations':['Exploratory synthetic follow-up; no real evacuation forecast validation','Two new length-width combinations, same prescribed topology','Conditional fixed-model intervals exclude fitting and generator uncertainty','No multiplicity-adjusted population test or universal learner ranking']}
 write(O/'audit.json',audit);print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
