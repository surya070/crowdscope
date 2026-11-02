"""Post-result development ablations and anonymous movement baseline."""
from pathlib import Path
import csv,json,hashlib,zipfile,importlib.util
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('comparison',ROOT/'research/run_empirical_comparison.py');lib=importlib.util.module_from_spec(spec);spec.loader.exec_module(lib)
np=lib.np
BUNDLE=ROOT/'research/data/forecast_bundle';BASE=ROOT/'output/empirical_comparison_v1';OUT=ROOT/'output/composition_check_v1'
ANON=['rear_observed_speed','minimum_person_speed','max_person_travel_estimate_floor_0_1','max_person_travel_estimate_floor_0_2','max_person_travel_estimate_floor_0_3']
def anonymous(tracks,frame):
 ids=sorted(t for t,p in tracks.items() if all(f in p for f in range(frame-50,frame+1)) and p[frame][0]<2.4)
 distance=np.array([2.4-tracks[t][frame][0] for t in ids]);speed=np.array([np.linalg.norm(np.array(tracks[t][frame])-tracks[t][frame-25]) for t in ids])
 return {ANON[0]:float(speed[np.argmax(distance)]),ANON[1]:float(speed.min()),**{name:float(np.max(distance/np.maximum(speed,floor))) for name,floor in zip(ANON[2:],[.1,.2,.3])}}
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if (OUT/'predictions.csv').exists():raise RuntimeError('Existing development result; do not overwrite.')
 m=json.loads((BUNDLE/'manifest.json').read_text());data=[r for r in csv.DictReader((BUNDLE/'features.csv').open()) if float(r['history_s'])==1]
 assert lib.hsh(BUNDLE/'features.csv')==m['features_sha256']
 variants={'H':m['H'],'H_presence':m['H']+['wheelchair_present'],'H_counts':m['H']+['wheelchair_count','wheelchair_fraction','wheelchair_present'],'H_group_motion':m['H']+['wheelchair_mean_speed','wheelchair_max_distance'],'H_M':m['H']+m['M_additions'],'H_anonymous':m['H']+ANON,'H_anonymous_M':m['H']+ANON+m['M_additions']}
 lock=dict(date='2026-11-02',scope='post-result exploratory confound/feature-engineering analysis; no causal identification',history=1,variants=variants,grid=json.loads((BASE/'modelling_lock.json').read_text())['candidates'],folds=m['folds'],feature_hash=lib.hsh(BUNDLE/'features.csv'),code_hash=lib.hsh(Path(__file__)),subgroup_reporting=['wheelchair trials','reference trials'],independent_people=False)
 (OUT/'lock.json').write_text(json.dumps(lock,indent=2));checks=0
 with zipfile.ZipFile(next((ROOT/'backups').glob('*.zip'))) as z:
  for trial in {r['trial'] for r in data}:
   local=ROOT/f'data/raw/sime2017/members/{trial}.txt';raw=local.read_bytes() if local.exists() else z.read(f'data/raw/sime2017/members/{trial}.txt')
   assert hashlib.sha256(raw).hexdigest()==m['source_sha256'][trial]
   tracks=defaultdict(dict)
   for line in raw.decode().splitlines():
    if not line.strip() or line.startswith('#'):continue
    a=line.split();tracks[int(a[0])][int(a[1])]=(float(a[2]),float(a[3]))
   for r in [r for r in data if r['trial']==trial]:
    frame=int(float(r['time_s'])*25);extra=anonymous(tracks,frame)
    assert extra==anonymous({t:{f:p for f,p in tr.items() if f<=frame} for t,tr in tracks.items()},frame);checks+=1
    r.update(extra)
 preds=[];trace=[];selection=[]
 for fold in m['folds']:
  train=[r for r in data if r['trial'] in fold['training_trials']];test=[r for r in data if r['trial'] in fold['evaluation_trials']]
  for variant,features in variants.items():
   scores=[]
   for c in lock['grid']:
    vr=[];vp=[]
    for inner in fold['inner_folds']:
     tr=[r for r in train if r['trial'] in inner['training_trials']];va=[r for r in train if r['trial'] in inner['validation_trials']]
     assert not {r['trial'] for r in tr}&{r['trial'] for r in va}
     vr+=va;vp.extend(lib.fit_predict(c,tr,va,features))
    score=lib.score(vr,vp);scores.append((score,c));trace.append(dict(width=fold['evaluation_width'],variant=variant,candidate=c,inner_mae=score))
   c=min(scores,key=lambda x:x[0])[1];selection.append(dict(width=fold['evaluation_width'],variant=variant,candidate=c))
   pp=lib.fit_predict(c,train,test,features)
   for r,p in zip(test,pp):preds.append(dict(trial=r['trial'],time_s=r['time_s'],variant=variant,width=fold['evaluation_width'],population='wheelchair_trial' if int(r['trial'])<1000 else 'reference_trial',target_s=float(r['target_s']),prediction_s=float(p)))
 with (OUT/'predictions.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(preds[0]));w.writeheader();w.writerows(preds)
 (OUT/'selection_trace.json').write_text(json.dumps(trace,indent=2));(OUT/'selections.json').write_text(json.dumps(selection,indent=2))
 (OUT/'checks.json').write_text(json.dumps(dict(anonymous_prefix_checks=checks,predictions=len(preds),sha256=lib.hsh(OUT/'predictions.csv')),indent=2))
 print('Saved',len(preds),'predictions; anonymous prefix checks:',checks)
if __name__=='__main__':main()
