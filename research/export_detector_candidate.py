"""Export an exploratory all-development-data refit, never a validation score."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'.deps/detector'));sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
import numpy as np
import joblib,torch
from torch import nn
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier,ExtraTreesClassifier,HistGradientBoostingClassifier
from research.run_detector_benchmark import Neural
OUT=ROOT/'output/detector_v1'

def main():
    summary=json.loads((OUT/'benchmark_summary.json').read_text());name=summary['best_observed_AP']
    assert name not in ['Permuted logistic','Prior'],'No usable detector candidate selected'
    d=np.load(OUT/'data_LOCAL_ONLY.npz');X=d['X'];y=d['y'];names=json.loads((OUT/'data_audit.json').read_text())['features']
    cols=[names.index(n) for n in ['s10_speed_mean','s10_speed_std','s10_speed_median','s10_stop']] if name=='Speed logistic' else [names.index('s10_side_median')] if name=='Lateral logistic' else [i for i,n in enumerate(names) if n.startswith('s20_')] if name=='Coarse logistic' else list(range(X.shape[1]))
    a=X[:,cols];seed=9301
    artifact=dict(family=name,feature_names=names,columns=cols,window_seconds=4,fps=25,
        target='wheelchair-associated motion in audited SiME cohort',
        caution='Exploratory all-data refit; score is not a calibrated probability; training data include all benchmark test tracks. Evaluate using crossed-holdout results, never this refit on its training data.')
    if name in ['MLP','CNN','GRU']:
        torch.manual_seed(seed);torch.set_num_threads(2)
        x=a if name=='MLP' else d['sequence'];axes=(0,1) if x.ndim==3 else 0
        mean=x.mean(axis=axes);sd=np.maximum(x.std(axis=axes),1e-5)
        inp=torch.tensor((x-mean)/sd,dtype=torch.float32);target=torch.tensor(y,dtype=torch.float32)
        model=Neural(name,x.shape[-1]);opt=torch.optim.AdamW(model.parameters(),lr=.01,weight_decay=.01)
        loss=nn.BCEWithLogitsLoss(pos_weight=torch.tensor(float(sum(y==0)/sum(y==1))))
        for epoch in range(60):
            opt.zero_grad();l=loss(model(inp),target);l.backward();nn.utils.clip_grad_norm_(model.parameters(),5);opt.step()
        artifact.update(kind='torch',mean=mean,sd=sd,state=model.state_dict(),input_dim=x.shape[-1],threshold=.5)
    else:
        if 'logistic' in name:model=make_pipeline(StandardScaler(),LogisticRegression(C=.2,class_weight='balanced',max_iter=1500,random_state=seed))
        elif name=='Gaussian NB':model=make_pipeline(StandardScaler(),GaussianNB(var_smoothing=1e-6))
        elif name=='kNN':model=make_pipeline(StandardScaler(),KNeighborsClassifier(n_neighbors=15,weights='distance'))
        elif name=='RBF SVM':model=make_pipeline(StandardScaler(),SVC(C=1,class_weight='balanced',gamma='scale'))
        elif name=='Random forest':model=RandomForestClassifier(n_estimators=120,min_samples_leaf=3,class_weight='balanced',n_jobs=2,random_state=seed)
        elif name=='Extra trees':model=ExtraTreesClassifier(n_estimators=120,min_samples_leaf=3,class_weight='balanced',n_jobs=2,random_state=seed)
        else:model=HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=7,min_samples_leaf=10,l2_regularization=2,class_weight='balanced',random_state=seed)
        model.fit(a,y);artifact.update(kind='sklearn',model=model,threshold=0. if name=='RBF SVM' else .5)
    joblib.dump(artifact,OUT/'candidate_model_LOCAL_ONLY.joblib')
    (OUT/'candidate_model_card.json').write_text(json.dumps({k:v for k,v in artifact.items() if k not in ['model','state','mean','sd']},indent=2))
    print('Exported exploratory all-data candidate:',name)
if __name__=='__main__':main()
