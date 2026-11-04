"""Nested, group-aware sigmoid calibration; fixed base selected previously."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.deps/detector'),str(ROOT/'.deps/recovery-r1')]
import numpy as np,joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score,roc_auc_score
OUT=ROOT/'output/calibrated_framework_v1'

def base():
    return make_pipeline(StandardScaler(),LogisticRegression(C=.2,class_weight='balanced',max_iter=1500,random_state=7300))

def folds(indices,trial,pid,y,crossed):
    out=[]
    for t in sorted(set(trial[indices])):
        people=sorted(set(pid[indices][y[indices]==1])) if crossed else [None]
        for p in people:
            te=indices[(trial[indices]==t)&((y[indices]==0)|(pid[indices]==p))] if crossed else indices[trial[indices]==t]
            if not np.any(y[te]==1):continue
            tr=indices[trial[indices]!=t]
            if crossed:
                known=set(pid[te][pid[te]>=0]);tr=tr[~np.isin(pid[tr],list(known))]
                assert not set(pid[tr][pid[tr]>=0])&known
            assert not set(tr)&set(te) and not set(trial[tr])&set(trial[te])
            assert len(set(y[tr]))==2
            out.append((int(t),None if p is None else int(p),tr,te))
    counts={t:sum(t==tt for tt,p,tr,te in out) for t in set(trial[indices])}
    return [(t,p,tr,te,np.where(y[te]==1,1.,1./counts[t])) for t,p,tr,te in out]

def calibrator(scores,labels,weights):
    return LogisticRegression(C=1,class_weight=None,max_iter=1000,random_state=7300).fit(np.asarray(scores).reshape(-1,1),labels,sample_weight=weights)

def quality(records,key):
    y=np.array([r['y'] for r in records]);p=np.array([r[key] for r in records]);w=np.array([r['weight'] for r in records]);pc=np.clip(p,1e-12,1-1e-12)
    bins=[]
    edges=[0,.1,.2,.4,.6,.8,1.0000001]
    for lo,hi in zip(edges,edges[1:]):
        m=(p>=lo)&(p<hi)
        if m.any():bins.append(dict(lower=lo,upper=min(hi,1),weight=float(w[m].sum()),mean_probability=float(np.average(p[m],weights=w[m])),observed_fraction=float(np.average(y[m],weights=w[m]))))
    pred=p>=.5;tp=float(w[(y==1)&pred].sum());fp=float(w[(y==0)&pred].sum());fn=float(w[(y==1)&~pred].sum())
    return dict(Brier=float(np.average((y-p)**2,weights=w)),log_loss=float(np.average(-y*np.log(pc)-(1-y)*np.log1p(-pc),weights=w)),
        AP=float(average_precision_score(y,p,sample_weight=w)),ROC_AUC=float(roc_auc_score(y,p,sample_weight=w)),
        mean_probability=float(np.average(p,weights=w)),prevalence=float(np.average(y,weights=w)),
        precision=tp/(tp+fp) if tp+fp else 0,recall=tp/(tp+fn),
        reliability=bins,ECE_fixed_bins=sum(b['weight']*abs(b['mean_probability']-b['observed_fraction']) for b in bins)/sum(w))

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'calibration_summary.json').exists():raise RuntimeError('Preserve calibration outcomes')
    d=np.load(ROOT/'output/detector_v1/data_LOCAL_ONLY.npz');X=d['X'];y=d['y'];trial=d['trial'];pid=d['pid'];indices=np.arange(len(y))
    paths=[Path(__file__),ROOT/'research/calibrated_framework_protocol_v1.md',ROOT/'output/detector_v1/data_LOCAL_ONLY.npz']
    (OUT/'calibration_lock.json').write_text(json.dumps(dict(hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},method='fixed nested sigmoid; C=1',started=time.time()),indent=2))
    results={};audit=[];start=time.time()
    for mode,crossed in [('crossed_person_trial',True),('coherent_trial_only',False)]:
        records=[];outer=folds(indices,trial,pid,y,crossed)
        for fi,(t,p,tr,te,w) in enumerate(outer):
            ss=[];yy=[];ww=[];inner=folds(tr,trial,pid,y,crossed)
            for it,ip,itr,ite,iw in inner:
                assert not set(itr)&set(te) and not set(ite)&set(te)
                if crossed:assert p not in pid[itr] and p not in pid[ite]
                model=base().fit(X[itr],y[itr]);ss.extend(model.decision_function(X[ite]));yy.extend(y[ite]);ww.extend(iw)
            cal=calibrator(ss,yy,ww);model=base().fit(X[tr],y[tr]);score=model.decision_function(X[te]);cp=cal.predict_proba(score.reshape(-1,1))[:,1];raw=model.predict_proba(X[te])[:,1]
            for ix,a,b,weight in zip(te,raw,cp,w):records.append(dict(index=int(ix),trial=t,held_pid=p,y=int(y[ix]),raw=float(a),calibrated=float(b),prior=float(y[tr].mean()),weight=float(weight)))
            audit.append(dict(mode=mode,fold=fi,held_trial=t,held_pid=p,outer_train=tr.tolist(),outer_test=te.tolist(),
                inner=[dict(trial=it,pid=ip,train=itr.tolist(),test=ite.tolist()) for it,ip,itr,ite,iw in inner]))
            if not crossed:
                joblib.dump(dict(kind='sklearn',family='Full logistic',model=model,calibrator=cal,
                    feature_names=json.loads((ROOT/'output/detector_v1/data_audit.json').read_text())['features'],
                    columns=list(range(X.shape[1])),threshold=.5,training_prior=float(y[tr].mean()),held_trial=t,
                    calibration_scope='inner trial-held; people may repeat',window_seconds=4,fps=25),OUT/f'trial_{t}_model_LOCAL_ONLY.joblib')
            print(json.dumps(dict(mode=mode,fold=fi+1,total=len(outer),elapsed_s=round(time.time()-start,1))),flush=True)
        results[mode]=dict(folds=len(outer),**{key:quality(records,key) for key in ['prior','raw','calibrated']})
        (OUT/f'{mode}_predictions_LOCAL_ONLY.json').write_text(json.dumps(records))
    # Refit prototype calibration on original crossed out-of-fitting-set scores.
    previous=json.loads((ROOT/'output/detector_v1/predictions_LOCAL_ONLY.json').read_text())
    previous=[r for r in previous if r['family']=='Full logistic']
    pp=np.clip(np.array([r['score'] for r in previous]),1e-12,1-1e-12)
    cal=calibrator(np.log(pp/(1-pp)),[r['y'] for r in previous],[r['weight'] for r in previous])
    model=base().fit(X,y)
    joblib.dump(dict(kind='sklearn',family='Full logistic',model=model,calibrator=cal,
        feature_names=json.loads((ROOT/'output/detector_v1/data_audit.json').read_text())['features'],columns=list(range(X.shape[1])),
        threshold=.5,training_prior=float(y.mean()),calibration_scope='crossed out-of-fold calibration, all-development base refit',
        window_seconds=4,fps=25),OUT/'calibrated_model_LOCAL_ONLY.joblib')
    (OUT/'split_audit_LOCAL_ONLY.json').write_text(json.dumps(audit))
    (OUT/'calibration_summary.json').write_text(json.dumps(results,indent=2))
    print(json.dumps(results,indent=2))
if __name__=='__main__':main()
