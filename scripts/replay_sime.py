"""Evaluate saved SiME parameters without tuning or overwriting existing runs."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from research.compound.run_sime_replay import one
def main():
 out=ROOT/'output/sime_replay_v2';freeze=json.loads((out/'selected_freeze.json').read_text())
 for path,digest in freeze['files'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 for tid in ['1501','1507','1503','1505']:
  for fine in [False,True]:
   prefix=('development_fine' if fine else 'selected_development') if tid in ['1501','1507'] else ('held_out_fine' if fine else 'held_out')
   path=out/f'{prefix}_{tid}.json'
   if path.exists():print('Preserved existing',path.name);continue
   result=one(tid,freeze['selected']['params'],dt=.01 if fine else .02,frames=not fine)
   path.write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
   print(tid,'fine' if fine else 'production',result.get('status'),flush=True)
   assert result.get('status')=='completed','Preserved failure; inspect before continuing'
if __name__=='__main__':main()
