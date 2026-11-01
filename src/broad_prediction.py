"""Bounded learner families and causal history extraction for the frozen follow-up."""
import copy,hashlib,itertools,json
from pathlib import Path
import numpy as np
from src.compound.study import observe,features,records
from src.recovery.models import Regressor

FAMILIES=['ridge','rbf','boosting','mlp','gru','history_ridge']
SEEDS=[113,227,331]
def candidates(family):
 if family in ['ridge','history_ridge']:return [{'alpha':a} for a in [.01,.1,1.]]
 if family=='rbf':return [{'alpha':.1,'length':l} for l in [.5,1.,2.]]
 if family=='boosting':return [{'depth':d} for d in [1,2,3]]
 if family=='mlp':return [{'width':h} for h in [16,32,64]]
 if family=='gru':return [{'width':h} for h in [8,16,32]]
 raise ValueError(family)

def causal_history(result,t,cfg):
 names=cfg['features']['aggregate']+cfg['features']['mobility_added']+cfg['features']['links_added']
 cutoff=round(t-.2,9);vectors=[]
 for k in range(9):
  observed_t=round(cutoff-(8-k)*.2,9)
  f=features(observe(result,round(observed_t+.2,9),cfg),cfg)
  if f is None:raise ValueError('A valid query has an already-completed earlier history')
  vectors.append([f[n] for n in names])
 return np.array(vectors,float)

def arrays(results,cfg):
 rows=[];history=[]
 for result in results:
  for row in records(result,cfg):
   a=causal_history(result,row['t'],cfg)
   names=cfg['features']['aggregate']+cfg['features']['mobility_added']+cfg['features']['links_added']
   if not np.allclose(a[-1],[row['features'][n] for n in names],rtol=0,atol=1e-12):raise ValueError('Static/history endpoint mismatch')
   rows.append(row);history.append(a)
 return rows,np.array(history,float)

def inputs(history,information,family):
 n={'A':14,'M':25,'F':34}[information];x=history[:,:,:n]
 return x if family in ['gru','history_ridge'] else x[:,-1,:]

def torch_parts(family,dim,width):
 import torch
 from torch import nn
 if family=='mlp':return nn.Sequential(nn.Linear(dim,width),nn.ReLU(),nn.Linear(width,1)),None
 return nn.GRU(dim,width,batch_first=True),nn.Linear(width,1)

class Learner:
 def __init__(self,family,setting):self.family,self.setting=family,setting
 def fit(self,x,y,w):
  x=np.asarray(x,float);y=np.asarray(y,float);w=np.asarray(w,float);w=w/w.sum()
  if self.family=='history_ridge':x=x.reshape(len(x),-1)
  if not np.isfinite(x).all() or not np.isfinite(y).all():raise ValueError('Nonfinite training values')
  if self.family=='gru':
   flat=x.reshape(-1,x.shape[-1]);ww=np.repeat(w/x.shape[1],x.shape[1])
  else:flat=x;ww=w
  self.mean=ww@flat;self.scale=np.sqrt(ww@((flat-self.mean)**2));self.scale[self.scale<1e-12]=1
  z=(x-self.mean)/self.scale
  if self.family in ['ridge','history_ridge','rbf']:
   kind='rbf' if self.family=='rbf' else 'ridge'
   self.model=Regressor(kind,self.setting['alpha'],self.setting.get('length',1)).fit(z,y,w);return self
  if self.family=='boosting':
   from sklearn.ensemble import GradientBoostingRegressor
   self.model=GradientBoostingRegressor(n_estimators=200,learning_rate=.05,max_depth=self.setting['depth'],min_samples_leaf=8,loss='squared_error',random_state=101).fit(z,y,sample_weight=w)
   return self
  import torch
  torch.set_num_threads(1);torch.use_deterministic_algorithms(True)
  self.ymean=float(w@y);self.yscale=max(1e-8,float(np.sqrt(w@((y-self.ymean)**2))))
  xx=torch.tensor(z,dtype=torch.float32);yy=torch.tensor((y-self.ymean)/self.yscale,dtype=torch.float32);weights=torch.tensor(w,dtype=torch.float32)
  self.states=[]
  for seed in SEEDS:
   torch.manual_seed(seed)
   body,head=torch_parts(self.family,z.shape[-1],self.setting['width'])
   params=list(body.parameters())+(list(head.parameters()) if head is not None else [])
   optim=torch.optim.AdamW(params,lr=.003,weight_decay=.01)
   for epoch in range(400):
    optim.zero_grad()
    pred=body(xx).squeeze(-1) if head is None else head(body(xx)[0][:,-1,:]).squeeze(-1)
    loss=(weights*(pred-yy)**2).sum()
    if not torch.isfinite(loss):raise ValueError('Nonfinite neural loss')
    loss.backward();optim.step()
   state={'body':{k:v.detach().numpy().copy() for k,v in body.state_dict().items()}}
   if head is not None:state['head']={k:v.detach().numpy().copy() for k,v in head.state_dict().items()}
   self.states.append(state)
  return self
 def predict(self,x):
  x=np.asarray(x,float)
  if self.family=='history_ridge':x=x.reshape(len(x),-1)
  z=(x-self.mean)/self.scale
  if self.family not in ['mlp','gru']:return self.model.predict(z)
  import torch
  torch.set_num_threads(1);xx=torch.tensor(z,dtype=torch.float32);preds=[]
  for state in self.states:
   body,head=torch_parts(self.family,z.shape[-1],self.setting['width'])
   body.load_state_dict({k:torch.tensor(v) for k,v in state['body'].items()});body.eval()
   if head is not None:head.load_state_dict({k:torch.tensor(v) for k,v in state['head'].items()});head.eval()
   with torch.no_grad():p=body(xx).squeeze(-1) if head is None else head(body(xx)[0][:,-1,:]).squeeze(-1)
   preds.append(p.numpy().astype(float)*self.yscale+self.ymean)
  return np.mean(preds,axis=0)
