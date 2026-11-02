"""Independent admission and causal extraction audit; does not train models."""
from pathlib import Path
import json,hashlib,importlib.util,sys
ROOT=Path(__file__).resolve().parents[2];P=ROOT/'research/assistance';OUT=ROOT/'output/linkage_benchmark_v1'
sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
spec=importlib.util.spec_from_file_location('features',P/'linkage_features.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
def main():
 manifest=json.loads((P/'linkage_manifest_v1.json').read_text());blocks={b['block']:b for b in manifest['blocks']};runs={r['run_id']:r for r in manifest['runs']};gate=json.loads((OUT/'movement_gate.json').read_text());assert gate['passed']
 for lockfile in ['linkage_freeze_v1.json','linkage_implementation_freeze_v1.json']:
  for name,digest in json.loads((P/lockfile).read_text())['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest
 assert len(gate['records'])==192 and sum(r['fine_pass'] is not None for r in gate['records'])==48
 identity_checks=prefix_checks=eligible=0;ineligible=[];maxdifference=0.
 for rec in gate['records']:
  run=runs[rec['run_id']];b=blocks[run['block']];p=OUT/'runs'/f"{rec['run_id']}.json";assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256'];r=json.loads(p.read_text());assert not r['failures'] and r['exited']==r['occupants']
  for frame in r['frames']:assert {int(i) for i in frame['positions']}|set(frame['exited'])==set(range(1,r['occupants']+1));identity_checks+=1
  if rec['fine_pass'] is not None:
   fp=OUT/'runs'/f"{rec['run_id']}_fine.json";assert hashlib.sha256(fp.read_bytes()).hexdigest()==rec['fine_sha256'];fine=json.loads(fp.read_text());assert not fine['failures'] and fine['exited']==fine['occupants']
   diff=abs(fine['clearance_s']-r['clearance_s']);assert diff<=max(.2,.01*fine['clearance_s']);maxdifference=max(maxdifference,diff)
  edges=[(1,2),(3,4)] if run['mode']=='threshold' else [];shuffled=[(1,4),(3,2)] if edges else []
  for t in [2,5,8]:
   if t>=r['clearance_s']:ineligible.append({'run':run['run_id'],'time':t});continue
   prefix=[v for v in r['frames'] if v['t']<=t+1e-8]
   a=f.extract(r['frames'],b,t,edges);sw=f.extract(r['frames'],b,t,shuffled)
   assert a==f.extract(prefix,b,t,edges);assert sw==f.extract(prefix,b,t,shuffled);prefix_checks+=2
   assert all(a[k]==sw[k] for k in f.M);assert a['count']==r['occupants']-len(next(v for v in prefix if abs(v['t']-t)<1e-8)['exited']);eligible+=1
 audit=dict(main_runs=192,fine_runs=48,source_and_output_hashes_match=True,identity_checks=identity_checks,eligible_queries=eligible,ineligible_queries=ineligible,correct_and_shuffled_prefix_checks=prefix_checks,unchanged_M_under_shuffled_links=True,maximum_fine_clearance_difference_s=maxdifference,all_movement_records_pass=True,learner_fitted=False)
 (OUT/'movement_audit.json').write_text(json.dumps(audit,indent=2));print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
