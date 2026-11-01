"""Standard-library verification of the release and saved predictive metrics."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,statistics
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest=read('ARTIFACT_MANIFEST.json')
 for path,digest in manifest['files'].items():
  assert sha(ROOT/path)==digest,'Publication artifact changed: '+path
 freeze=read('research/compound/prediction_freeze_v1.json')
 for path,digest in freeze['files'].items():assert sha(ROOT/path)==digest,path
 assert sha(ROOT/'research/compound/movement_validation.json')==freeze['prior_feasibility_validation_sha256']
 for record in ['research/compound/movement_validation.json','output/compound/comparison_001/context.json']:
  for path,digest in read(record)['source_hashes'].items():assert sha(ROOT/path)==digest,path
 prefix='output/compound/broad_prediction_001/'
 frozen=read(prefix+'selection_freeze.json')
 for path,digest in frozen['source_hashes'].items():assert sha(ROOT/path)==digest,path
 for path,digest in frozen['models'].items():assert sha(ROOT/prefix/path)==digest,path
 predictions=read(prefix+'predictions.json');summary=read(prefix+'summary.json');groups=defaultdict(list)
 for r in predictions:groups[r['partition'],r['family'],r['information']].append(r)
 assert len(groups)==36
 maxdifference=0
 for (partition,family,information),rows in groups.items():
  errors=defaultdict(list);metadata={}
  for r in rows:
   errors[r['run_id']].append(abs(r['prediction']-r['target']));metadata[r['run_id']]=(r['geometry'],r['block_id'])
  blocks=defaultdict(list)
  for rid,values in errors.items():blocks[metadata[rid]].append(statistics.mean(values))
  geometries=defaultdict(list)
  for (geometry,block),values in blocks.items():geometries[geometry].append(statistics.mean(values))
  mae=statistics.mean(statistics.mean(values) for values in geometries.values())
  difference=abs(mae-summary[partition][family][information]['mae_s']);maxdifference=max(maxdifference,difference)
  assert difference<1e-10,(partition,family,information,difference)
 print(json.dumps({'status':'passed','files_verified':len(manifest['files']),'independent_metric_groups':len(groups),'maximum_mae_difference_s':maxdifference,'models_fitted':False,'external_downloads':False},indent=2))
if __name__=='__main__':main()
