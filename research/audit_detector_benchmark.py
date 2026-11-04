"""Independent arithmetic and split checks for the exploratory detector."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
import numpy as np
OUT=ROOT/'output/detector_v1'

def main():
    lock=json.loads((OUT/'benchmark_lock.json').read_text())
    for name,h in lock['hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    data=np.load(OUT/'data_LOCAL_ONLY.npz');y=data['y'];trial=data['trial'];pid=data['pid']
    records=json.loads((OUT/'predictions_LOCAL_ONLY.json').read_text())
    summary=json.loads((OUT/'benchmark_summary.json').read_text())
    for family,reported in summary['results'].items():
        rows=[r for r in records if r['family']==family]
        weights=np.array([r['weight'] for r in rows]);ys=np.array([r['y'] for r in rows]);scores=np.array([r['score'] for r in rows])
        assert abs(weights.sum()-len(y))<1e-8
        assert abs(weights[ys==1].sum()-sum(y))<1e-8
        seen={}
        for r in rows:
            ix=r['index'];assert int(y[ix])==r['y'] and int(trial[ix])==r['trial']
            seen[ix]=seen.get(ix,0)+r['weight']
        assert len(seen)==len(y) and all(abs(w-1)<1e-8 for w in seen.values())
        # Independent weighted AP integration, including tied scores.
        order=np.argsort(-scores,kind='stable');s=scores[order];w=weights[order];v=ys[order]
        ends=np.r_[np.flatnonzero(np.diff(s)!=0),len(s)-1]
        tp=np.cumsum(w*v)[ends];total=np.cumsum(w)[ends]
        ap=float(np.sum(np.diff(np.r_[0,tp])/tp[-1]*(tp/total)))
        assert abs(ap-reported['AP'])<1e-10,(family,ap)
        pos=scores[ys==1];neg=scores[ys==0];nw=weights[ys==0]
        auc=float(np.sum(((pos[:,None]>neg)+.5*(pos[:,None]==neg))*nw)/(len(pos)*sum(nw)))
        assert abs(auc-reported['ROC_AUC'])<1e-10
        for fold in sorted({r['fold'] for r in rows}):
            rr=[r for r in rows if r['fold']==fold];t=rr[0]['trial'];p=rr[0]['held_pid']
            te=np.array([r['index'] for r in rr]);known=set(pid[te][pid[te]>=0])
            tr=(trial!=t)&(pid!=p)&~np.isin(pid,list(known))
            assert not (trial[tr]==t).any() and not (pid[tr]==p).any()
            assert not set(pid[tr][pid[tr]>=0])&known
            assert len([r for r in rr if r['y']])==1
    result=dict(passed=True,families=len(summary['results']),folds=summary['folds'],
                prediction_records=len(records),effective_tracks=len(y),
                checks=['source hashes','weighted track coverage','known-identity/trial separation',
                        'independent weighted AP','independent pairwise ROC-AUC'],
                unresolved='Unknown persistent identities among controls; no unseen-control-person guarantee.')
    (OUT/'audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
