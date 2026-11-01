"""Weighted linear/RBF regressors and validation-only selection."""
from collections import defaultdict
import numpy as np


def feature_names(cfg, model):
    names = list(cfg["features"]["aggregate"])
    if model != "A":
        names += cfg["features"]["mobility_added"]
    if model.startswith("F"):
        names += cfg["features"]["links_added"]
    return names


def matrix(rows,cfg,model):
    names = feature_names(cfg,model)
    a = np.array([[r["features"][n] for n in names] for r in rows],float).reshape(-1,len(names))
    for j,n in enumerate(names):
        if model == "F_no_family" and "family" in n or model == "F_no_assistance" and ("assistance" in n or "helper_minus_client" in n):
            a[:,j] = 0
    return a


def weights(rows,all_runs=None):
    all_runs = rows if all_runs is None else all_runs
    geometries = {r["geometry"] for r in all_runs}
    blocks = {g:{r["block_id"] for r in all_runs if r["geometry"]==g} for g in geometries}
    runs = defaultdict(set)
    count = defaultdict(int)
    for r in all_runs:
        runs[r["block_id"]].add(r["run_id"])
    for r in rows:
        count[r["run_id"]] += 1
    w = np.array([1/(len(geometries)*len(blocks[r["geometry"]])*len(runs[r["block_id"]])*count[r["run_id"]]) for r in rows])
    return w/w.sum()


def score(rows,predictions,runs):
    errors = defaultdict(list)
    for r,p in zip(rows,predictions):
        errors[r["run_id"]].append(abs(r["target"]-p))
    per_run = {r["run_id"]:float(np.mean(errors[r["run_id"]])) if errors[r["run_id"]] else 0.0 for r in runs}
    by_block = defaultdict(list)
    by_geometry = defaultdict(list)
    for r in runs:
        by_block[r["geometry"],r["block_id"]].append(per_run[r["run_id"]])
    for (g,b),values in by_block.items():
        by_geometry[g].append(np.mean(values))
    return float(np.mean([np.mean(v) for v in by_geometry.values()]))


class Regressor:
    def __init__(self,kind,alpha,length=1):
        self.kind,self.alpha,self.length = kind,alpha,length

    def fit(self,x,y,w):
        x,y,w = np.asarray(x,float),np.asarray(y,float),np.asarray(w,float)
        if not np.isfinite(x).all() or not np.isfinite(y).all() or np.any(w<=0):
            raise ValueError("Invalid training arrays")
        w = w/w.sum()
        self.mean,self.ymean = w@x,float(w@y)
        self.scale = np.sqrt(w@((x-self.mean)**2))
        self.scale[self.scale<1e-12] = 1
        self.z = (x-self.mean)/self.scale
        y = y-self.ymean
        if self.kind == "ridge":
            self.coef = np.linalg.solve(self.z.T@(w[:,None]*self.z)+self.alpha*np.eye(x.shape[1]),self.z.T@(w*y))
        else:
            self.w = w
            k = self.kernel(self.z,self.z)
            self.kmean,self.kgrand = k@w,float(w@k@w)
            kc = k-self.kmean[:,None]-self.kmean[None,:]+self.kgrand
            sw = np.sqrt(w)
            b = np.linalg.solve(sw[:,None]*kc*sw[None,:]+self.alpha*np.eye(len(y)),sw*y)
            self.dual = sw*b
        return self

    def kernel(self,a,b):
        squared = np.maximum(0,np.sum(a*a,axis=1)[:,None]+np.sum(b*b,axis=1)[None,:]-2*a@b.T)
        return np.exp(-squared/(2*self.length**2*a.shape[1]))

    def predict(self,x):
        z = (np.asarray(x,float)-self.mean)/self.scale
        if self.kind == "ridge":
            return self.ymean+z@self.coef
        k = self.kernel(z,self.z)
        kc = k-(k@self.w)[:,None]-self.kmean[None,:]+self.kgrand
        return self.ymean+kc@self.dual


def clip(predictions,rows):
    return np.clip(predictions,0,[180-r["t"] for r in rows])


def select(cfg,train,validation,validation_runs,train_runs=None):
    if any(r["partition"]!="train" for r in train) or any(r["partition"]!="validation" for r in validation):
        raise ValueError("Selection received prohibited partition")
    selected,tuning = {},[]
    for model in cfg["predictors"]:
        best = None
        for kind in cfg["learners"]["candidates"]:
            lengths = [1] if kind=="ridge" else cfg["learners"]["rbf_length_grid"]
            for alpha in sorted(cfg["learners"]["alpha_grid"],reverse=True):
                for length in sorted(lengths,reverse=True):
                    estimator = Regressor(kind,alpha,length).fit(matrix(train,cfg,model),[r["target"] for r in train],weights(train,train_runs))
                    prediction = clip(estimator.predict(matrix(validation,cfg,model)),validation)
                    error = score(validation,prediction,validation_runs)
                    setting = {"kind":kind,"alpha":alpha,"length":length}
                    tuning.append({"model":model,**setting,"validation_mae":error})
                    if best is None or error < best[0]-1e-12:
                        best = error,setting
        selected[model] = best[1]
    return selected,tuning


def fit_final(cfg,rows,settings,all_runs=None):
    if any(r["partition"] not in ["train","validation"] for r in rows):
        raise ValueError("Final fitting received test rows")
    return {name:Regressor(**setting).fit(matrix(rows,cfg,name),[r["target"] for r in rows],weights(rows,all_runs)) for name,setting in settings.items()}


def simple_references(cfg,train,validation,validation_runs,train_runs=None):
    y = np.array([r["target"] for r in train])
    w = weights(train,train_runs)
    order = np.argsort(y,kind="stable")
    median = float(y[order[np.searchsorted(np.cumsum(w[order]),.5,side="left")]])
    candidates = [{"kind":"constant","value":median}]+[{"kind":"capacity","q":q} for q in cfg["simple_references"]["q_grid_per_m_s"]]
    scores = [{**s,"validation_mae":score(validation,predict_simple(s,validation),validation_runs)} for s in candidates]
    # Capacity q tie follows listed grid; scientific reference tie favours constant.
    best = scores[0]
    for s in scores[1:]:
        if s["validation_mae"] < best["validation_mae"]-1e-12:
            best = s
    return best,scores


def predict_simple(setting,rows):
    if setting["kind"]=="constant":
        p = np.full(len(rows),setting["value"])
    else:
        p = np.array([r["features"]["remaining_count"]/(r["features"]["exit_width_m"]*setting["q"]) for r in rows])
    return clip(p,rows)
