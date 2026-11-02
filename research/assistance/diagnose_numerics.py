"""Bounded operational-model development screen using unchanged fixtures/gates."""
from pathlib import Path
import importlib.util,json,hashlib,time
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('multi',ROOT/'research/assistance/run_multipair.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
CANDIDATES=[dict(name='cfs_default',engine='cfs',parameters={}),dict(name='cfs_lower_repulsion',engine='cfs',parameters={'strength_neighbor_repulsion':2.6}),dict(name='cfs_wider_interaction',engine='cfs',parameters={'strength_neighbor_repulsion':2.6,'range_neighbor_repulsion':.3}),dict(name='avm_default',engine='avm',parameters={})]

def main():
 out=ROOT/'output/assistance_numerics_v1';out.mkdir(parents=True,exist_ok=True)
 if (out/'results.json').exists():raise RuntimeError('Preserve previous screen.')
 lock=dict(date='2026-11-02',scope='development operational-model screen; not empirical calibration',candidates=CANDIDATES,controller='threshold',steps=[.02,.01,.005],cases=[c['name'] for c in m.fixtures()],selection='all movement and timing gates in full suite; if multiple pass prefer least parameter change; retain all failures',module_sha256=hashlib.sha256((ROOT/'research/assistance/run_multipair.py').read_bytes()).hexdigest(),runner_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
 (out/'lock.json').write_text(json.dumps(lock,indent=2));results=[];gates=[]
 for candidate in CANDIDATES:
  for case in m.fixtures():
   rr=[]
   for dt in lock['steps']:
    started=time.monotonic()
    try:r=m.run(case,dt,'threshold',candidate['engine'],candidate['parameters'])
    except Exception as e:r=dict(case=case['name'],dt=dt,clearance_s=None,failures=['runtime_exception'],error=str(e),frames=[])
    r.update(candidate=candidate['name'],wallclock_s=time.monotonic()-started);rr.append(r);results.append(r)
   times=[r['clearance_s'] for r in rr];spread=max(times)-min(times) if all(t is not None for t in times) else None
   gate=dict(candidate=candidate['name'],case=case['name'],clearances=times,movement=all(not r['failures'] for r in rr),spread_s=spread,stable=spread is not None and spread<=max(.2,.01*times[-1]));gates.append(gate);print(json.dumps(gate),flush=True)
 (out/'results.json').write_text(json.dumps(results));(out/'gate.json').write_text(json.dumps(gates,indent=2))
 summary=[dict(candidate=c['name'],movement_cases=sum(g['movement'] for g in gates if g['candidate']==c['name']),stable_cases=sum(g['stable'] for g in gates if g['candidate']==c['name']),passed=all(g['movement'] and g['stable'] for g in gates if g['candidate']==c['name'])) for c in CANDIDATES]
 (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary),flush=True)
if __name__=='__main__':main()
