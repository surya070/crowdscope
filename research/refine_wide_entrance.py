"""Development refinement after inspecting entrance_diagnosis_v1 outcomes."""
from pathlib import Path
import json,hashlib,sys,random
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.diagnose_entrance import cases,roster,run,box,unary_union,PolygonZone,validate_partition

def main():
 out=ROOT/'output/wide_entrance_refinement_v1';out.mkdir(parents=True,exist_ok=True)
 if (out/'lock.json').exists():raise RuntimeError('Preserve previous outputs')
 lock=dict(purpose='development extension after narrow fine-step failure; not independent confirmation',width=1.2,dt=0.0025,jitter_variants=[False,True],code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (out/'lock.json').write_text(json.dumps(lock,indent=2));results=[]
 coarse=json.loads((ROOT/'output/entrance_diagnosis_v1/results.json').read_text())
 for jitter in (False,True):
  c=dict(next(c for c in cases() if c['name']=='room'),name='room_w1.2_jitter'+str(jitter),routing='waypoint',strength=2.6)
  c['area']=unary_union([box(-12,-4,4,4),box(3.9,-0.6,6.1,0.6),box(6,-4,12,4)])
  cuts=[-12,-6,0,6,12];c['zones']=[PolygonZone(i,c['area'].intersection(box(cuts[i],-4,cuts[i+1],4))) for i in range(4)];validate_partition(c['zones'],c['area'])
  people=roster();rng=random.Random(460000)
  if jitter:people=[dict(p,xy=(p['xy'][0]+rng.uniform(-0.04,0.04),p['xy'][1]+rng.uniform(-0.04,0.04))) for p in people]
  result=run(c,people,0.0025,out);old=next(x for x in coarse if x['case']==c['name'])
  spread=abs(old['clearance_s']-result['clearance_s']) if old['clearance_s'] is not None and result['clearance_s'] is not None else None
  result['coarse_fine_spread_s']=spread;result['stable']=spread is not None and spread<=max(0.2,0.01*result['clearance_s'])
  results.append(result);(out/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(result),flush=True)

if __name__=='__main__':main()
