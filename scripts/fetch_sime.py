"""Acquire required external source inputs; do not mirror them in Git."""
from pathlib import Path
import hashlib,json,subprocess,sys,urllib.request
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 record=json.loads((ROOT/'data/sime_input_hashes.json').read_text())
 metadata=ROOT/'research/data_search_20261030/sime_metadata_prefix.txt';metadata.parent.mkdir(parents=True,exist_ok=True)
 if not metadata.exists():
  with urllib.request.urlopen(record['metadata_url'],timeout=60) as response:data=response.read()
  assert hashlib.sha256(data).hexdigest()==record['metadata_sha256'],'Source metadata changed'
  json.loads(data);metadata.write_bytes(data)
 assert sha(metadata)==record['metadata_sha256'],'Local metadata differs from study input'
 subprocess.run([sys.executable,'-m','research.recovery.sime_access',*[tid+'.txt' for tid in record['trials']]],cwd=ROOT,check=True)
 for tid,digest in record['trials'].items():assert sha(ROOT/f'data/raw/sime2017/members/{tid}.txt')==digest,tid
 print('Verified original metadata and all four source trials. Data remain locally ignored by Git.')
if __name__=='__main__':main()
