"""Full-suite fine bracket plus retained original cases and fixed perturbations."""
from pathlib import Path
import importlib.util,json,hashlib,copy
ROOT=Path(__file__).resolve().parents[2]
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
m=load('multi',ROOT/'research/assistance/run_multipair.py');old=load('old',ROOT/'research/assistance/run_prototype.py')
def main():
 out=ROOT/'output/assistance_numerics_v1';path=out/'verification_results.json'
 if path.exists():raise RuntimeError('Verification exists.')
 cases=m.fixtures()
 for c in old.cases():cases.append(dict(name='original_'+c['name'],area=c['area'],pairs=[((0,0),(-.85,0),.85,1.3)],extras=c['extras'],goal=tuple(c['route'].coords[-1]),axis=c['axis'],plane=c['plane']))
 for delta in [-.05,.05]:
  c=copy.deepcopy(m.fixtures()[0]);c['name']=f'mixed_y_shift_{delta}'
  c['extras']=[(x,y+delta) for x,y in c['extras']];cases.append(c)
 lock=dict(date='2026-11-02',selection='cfs_lower_repulsion passed initial unchanged six-case gate',parameters={'strength_neighbor_repulsion':2.6},controller='threshold',steps=[.01,.005,.0025],cases=[c['name'] for c in cases],tolerances='unchanged',development=True,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),module_sha256=hashlib.sha256((ROOT/'research/assistance/run_multipair.py').read_bytes()).hexdigest())
 (out/'verification_lock.json').write_text(json.dumps(lock,indent=2));results=[];gates=[]
 for c in cases:
  rr=[m.run(c,dt,'threshold','cfs',lock['parameters']) for dt in lock['steps']];results+=rr
  times=[r['clearance_s'] for r in rr];spread=max(times)-min(times) if all(v is not None for v in times) else None
  g=dict(case=c['name'],clearances_s=times,movement=all(not r['failures'] for r in rr),spread_s=spread,stable=spread is not None and spread<=max(.2,.01*times[-1]));gates.append(g);print(json.dumps(g),flush=True)
 path.write_text(json.dumps(results));(out/'verification_gate.json').write_text(json.dumps(dict(cases=gates,passed=all(g['movement'] and g['stable'] for g in gates)),indent=2))
if __name__=='__main__':main()
