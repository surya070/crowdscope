"""Fixed exploratory crossed person/trial holdouts. No test-guided tuning."""
from pathlib import Path
import hashlib,json,os,sys,time,warnings
os.environ['OMP_NUM_THREADS']='2'
os.environ['MKL_NUM_THREADS']='2'
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps/detector'))
sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
import numpy as np
import sklearn,torch
from torch import nn
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier,HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score,roc_auc_score,confusion_matrix

OUT=ROOT/'output/detector_v1'
torch.set_num_threads(2);torch.use_deterministic_algorithms(True)

class Neural(nn.Module):
    def __init__(self,kind,n):
        super().__init__();self.kind=kind
        if kind=='MLP':self.net=nn.Sequential(nn.Linear(n,32),nn.ReLU(),nn.Linear(32,16),nn.ReLU(),nn.Linear(16,1))
        elif kind=='CNN':self.net=nn.Sequential(nn.Conv1d(2,16,7,padding=3),nn.ReLU(),nn.Conv1d(16,16,5,padding=2),nn.ReLU(),nn.AdaptiveAvgPool1d(1),nn.Flatten(),nn.Linear(16,1))
        else:self.gru=nn.GRU(2,12,batch_first=True);self.head=nn.Linear(12,1)
    def forward(self,x):
        if self.kind=='GRU':
            h,_=self.gru(x);return self.head(h[:,-1]).flatten()
        return self.net(x.transpose(1,2) if self.kind=='CNN' else x).flatten()

def neural_fit(kind,x,y,xt,seed):
    torch.manual_seed(seed);rng=np.random.default_rng(seed)
    axes=(0,1) if x.ndim==3 else 0
    mean=x.mean(axis=axes);sd=x.std(axis=axes);sd=np.maximum(sd,1e-5)
    a=torch.tensor((x-mean)/sd,dtype=torch.float32);b=torch.tensor((xt-mean)/sd,dtype=torch.float32)
    target=torch.tensor(y,dtype=torch.float32)
    model=Neural(kind,x.shape[-1]);opt=torch.optim.AdamW(model.parameters(),lr=.01,weight_decay=.01)
    loss=nn.BCEWithLogitsLoss(pos_weight=torch.tensor(float((y==0).sum()/(y==1).sum())))
    for epoch in range(60):
        model.train();opt.zero_grad();l=loss(model(a),target);l.backward()
        nn.utils.clip_grad_norm_(model.parameters(),5);opt.step()
        if not torch.isfinite(l):raise RuntimeError('Nonfinite training loss')
    model.eval()
    with torch.no_grad():return torch.sigmoid(model(a)).numpy(),torch.sigmoid(model(b)).numpy(),float(l)

def metrics(y,s,w,pred=None):
    pred=(s>=.5) if pred is None else pred
    tn,fp,fn,tp=confusion_matrix(y,pred,sample_weight=w,labels=[0,1]).ravel()
    precision=tp/(tp+fp) if tp+fp else 0.;recall=tp/(tp+fn) if tp+fn else 0.
    return dict(AP=float(average_precision_score(y,s,sample_weight=w)),
                ROC_AUC=float(roc_auc_score(y,s,sample_weight=w)),
                precision=float(precision),recall=float(recall),F1=float(2*precision*recall/(precision+recall)) if precision+recall else 0.,
                balanced_accuracy=float((recall+tn/(tn+fp))/2),false_positive_rate=float(fp/(tn+fp)),
                weighted_confusion=dict(TN=float(tn),FP=float(fp),FN=float(fn),TP=float(tp)))

def main():
    if (OUT/'benchmark_summary.json').exists():raise RuntimeError('Preserve benchmark; do not overwrite outcomes')
    d=np.load(OUT/'data_LOCAL_ONLY.npz');X=d['X'];seq=d['sequence'];y=d['y'];trial=d['trial'];pid=d['pid'];track=d['track']
    names=json.loads((OUT/'data_audit.json').read_text())['features']
    speed=[names.index(n) for n in ['s10_speed_mean','s10_speed_std','s10_speed_median','s10_stop']]
    lateral=[names.index('s10_side_median')];coarse=[i for i,n in enumerate(names) if n.startswith('s20_')]
    allcols=list(range(X.shape[1]))
    families=['Prior','Speed logistic','Lateral logistic','Full logistic','Gaussian NB','kNN','RBF SVM',
              'Random forest','Extra trees','Gradient boosting','MLP','CNN','GRU','Coarse logistic','Permuted logistic']
    folds=[]
    for t in sorted(set(trial)):
        for p in range(34,41):
            positive=(trial==t)&(pid==p)&(y==1)
            if not positive.any():continue
            test=(trial==t)&((y==0)|positive)
            known=set(int(a) for a in pid[test] if a>=0)
            train=(trial!=t)&(pid!=p)&~np.isin(pid,list(known))
            assert not set(trial[train])&set(trial[test])
            assert not set(pid[train][pid[train]>=0])&set(pid[test][pid[test]>=0])
            assert (y[test]==1).sum()==1 and (y[train]==1).sum()>0
            folds.append((int(t),p,np.flatnonzero(train),np.flatnonzero(test)))
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [Path(__file__),ROOT/'research/build_detector_data.py',ROOT/'research/detector_protocol_v1.md',OUT/'data_LOCAL_ONLY.npz']}
    (OUT/'benchmark_lock.json').write_text(json.dumps(dict(started=time.strftime('%Y-%m-%dT%H:%M:%S'),hashes=hashes,
        families=families,folds=len(folds),neural_epochs=60,seed=7300,sklearn=sklearn.__version__,
        torch=torch.__version__,numpy=np.__version__,tuning='none; fixed parameters',primary='weighted pooled AP'),indent=2))
    fold_counts={int(t):sum(a==t for a,p,tr,te in folds) for t in set(trial)}
    records=[];training=[];start=time.time()
    with (OUT/'progress.jsonl').open('w') as progress:
      for fi,(t,p,tr,te) in enumerate(folds):
        seed=7300+fi;yt=y[tr]
        for family in families:
            cols=speed if family=='Speed logistic' else lateral if family=='Lateral logistic' else coarse if family=='Coarse logistic' else allcols
            a=X[tr][:,cols];b=X[te][:,cols];threshold=.5;lastloss=None
            if family=='Prior':
                s=np.full(len(te),yt.mean());st=np.full(len(tr),yt.mean())
            elif family in ['MLP','CNN','GRU']:
                st,s,lastloss=neural_fit(family,a if family=='MLP' else seq[tr],yt,b if family=='MLP' else seq[te],seed)
            else:
                if 'logistic' in family:
                    model=make_pipeline(StandardScaler(),LogisticRegression(C=.2,class_weight='balanced',max_iter=1500,random_state=seed))
                elif family=='Gaussian NB':model=make_pipeline(StandardScaler(),GaussianNB(var_smoothing=1e-6))
                elif family=='kNN':model=make_pipeline(StandardScaler(),KNeighborsClassifier(n_neighbors=15,weights='distance'))
                elif family=='RBF SVM':model=make_pipeline(StandardScaler(),SVC(C=1,class_weight='balanced',gamma='scale'));threshold=0.
                elif family=='Random forest':model=RandomForestClassifier(n_estimators=120,min_samples_leaf=3,class_weight='balanced',n_jobs=2,random_state=seed)
                elif family=='Extra trees':model=ExtraTreesClassifier(n_estimators=120,min_samples_leaf=3,class_weight='balanced',n_jobs=2,random_state=seed)
                else:model=HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=7,min_samples_leaf=10,l2_regularization=2,class_weight='balanced',random_state=seed)
                fit_y=yt.copy()
                if family=='Permuted logistic':
                    rng=np.random.default_rng(seed)
                    for tt in set(trial[tr]):
                        ix=np.flatnonzero(trial[tr]==tt);fit_y[ix]=rng.permutation(fit_y[ix])
                model.fit(a,fit_y)
                if family=='RBF SVM':st=model.decision_function(a);s=model.decision_function(b)
                else:st=model.predict_proba(a)[:,1];s=model.predict_proba(b)[:,1]
            assert np.isfinite(s).all()
            training.append(dict(fold=fi,trial=t,held_pid=p,family=family,n_train=len(tr),positive_train=int(yt.sum()),
                train_AP=float(average_precision_score(yt,st)),loss=lastloss))
            for ix,score in zip(te,s):
                records.append(dict(fold=fi,trial=t,held_pid=p,index=int(ix),y=int(y[ix]),family=family,
                    score=float(score),prediction=int(score>=threshold),weight=1. if y[ix] else 1./fold_counts[t]))
        line=dict(fold=fi+1,total=len(folds),held_trial=t,held_pid=p,elapsed_s=round(time.time()-start,1))
        progress.write(json.dumps(line)+'\n');progress.flush();print(json.dumps(line),flush=True)
    results={}
    for family in families:
        r=[a for a in records if a['family']==family]
        results[family]=metrics(np.array([a['y'] for a in r]),np.array([a['score'] for a in r]),
                               np.array([a['weight'] for a in r]),np.array([a['prediction'] for a in r]))
        results[family]['mean_training_AP']=float(np.mean([a['train_AP'] for a in training if a['family']==family]))
        results[family]['participant_recall']={str(p):float(np.mean([a['prediction'] for a in r if a['y'] and a['held_pid']==p])) for p in range(34,41)}
    (OUT/'predictions_LOCAL_ONLY.json').write_text(json.dumps(records))
    (OUT/'training.json').write_text(json.dumps(training))
    result=dict(scope='Exploratory crossed trial/wheelchair-person holdouts; unknown repeat controls remain',
        rows=len(y),positives=int(y.sum()),folds=len(folds),effective_prevalence=float(y.mean()),
        best_observed_AP=max(results,key=lambda k:results[k]['AP']),results=results,elapsed_s=time.time()-start,
        caution='Scores are not calibrated probabilities; model-family selection uses this exploratory comparison; no pristine external test.')
    (OUT/'benchmark_summary.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
