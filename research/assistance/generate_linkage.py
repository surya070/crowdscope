"""Frozen-design movement admission. Stop on first failure, without fitting."""
from pathlib import Path
import json,hashlib,importlib.util,time
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'research/assistance';OUT=ROOT/'output/linkage_benchmark_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'runs').mkdir(exist_ok=True)
 if (OUT/'movement_gate.json').exists():raise RuntimeError('Movement admission already recorded.')
 freeze=json.loads((P/'linkage_freeze_v1.json').read_text())
 for name,h in freeze['files'].items():assert sha(ROOT/name)==h,name
 implementation=json.loads((P/'linkage_implementation_freeze_v1.json').read_text())
 for name,h in implementation['files'].items():assert sha(ROOT/name)==h,name
 spec=importlib.util.spec_from_file_location('linkage_engine',P/'linkage_engine.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 from shapely import wkt
 manifest=json.loads((P/'linkage_manifest_v1.json').read_text());blocks={b['block']:b for b in manifest['blocks']};records=[]
 started=time.monotonic()
 for i,run in enumerate(manifest['runs']):
  b=blocks[run['block']];case=dict(name=run['run_id'],area=wkt.loads(b['geometry_wkt']),pairs=[(tuple(p['client_start']),tuple(p['helper_start']),p['client_nominal_speed'],p['helper_nominal_speed']) for p in b['pairs']],extras=[tuple(x) for x in b['extras']],goal=tuple(b['goal']),axis=b['exit_axis'],plane=b['exit_plane'])
  path=OUT/'runs'/f"{run['run_id']}.json"
  if path.exists():raise RuntimeError('Unexpected partial run; inspect before resuming.')
  try:r=m.run(case,run['dt'],run['mode'],'cfs',{'strength_neighbor_repulsion':2.6},gain=run['gain'])
  except Exception as e:r=dict(failures=['runtime_exception'],error=str(e),clearance_s=None)
  path.write_text(json.dumps(r));record=dict(run_id=run['run_id'],block=run['block'],split=run['split'],failures=r['failures'],fine_pass=None,sha256=sha(path));records.append(record)
  if r['failures']:
   (OUT/'movement_gate.json').write_text(json.dumps(dict(passed=False,reason='movement_failure',failed_run=run,completed_records=records),indent=2));print('STOP: movement gate failed',run['run_id'],r['failures'],flush=True);return
  if run['fine_step_audit']:
   try:f=m.run(case,.0025,run['mode'],'cfs',{'strength_neighbor_repulsion':2.6},gain=run['gain'])
   except Exception as e:f=dict(failures=['runtime_exception'],error=str(e),clearance_s=None)
   fp=OUT/'runs'/f"{run['run_id']}_fine.json";fp.write_text(json.dumps(f));record['fine_sha256']=sha(fp)
   difference=abs(f['clearance_s']-r['clearance_s']) if f['clearance_s'] is not None else None
   record['fine_difference_s']=difference;record['fine_pass']=not f['failures'] and difference is not None and difference<=max(.2,.01*f['clearance_s'])
   if not record['fine_pass']:
    (OUT/'movement_gate.json').write_text(json.dumps(dict(passed=False,reason='numerical_failure',failed_run=run,completed_records=records),indent=2));print('STOP: numerical gate failed',run['run_id'],difference,flush=True);return
  if (i+1)%16==0:print(f'{i+1}/192 main runs admitted; elapsed {time.monotonic()-started:.1f}s',flush=True)
 (OUT/'movement_gate.json').write_text(json.dumps(dict(passed=True,main_runs=len(records),fine_runs=sum(r['fine_pass'] is not None for r in records),records=records),indent=2));print('Movement gate passed.',flush=True)
if __name__=='__main__':main()
