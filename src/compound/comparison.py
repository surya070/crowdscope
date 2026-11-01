"""Fixed learners and planned comparisons; no held-out tuning."""
import numpy as np
from src.recovery.common import read,write
from src.recovery.models import Regressor,weights,score,predict_simple,simple_references
from src.recovery.evaluation import run_metrics,blocks,macro,interval
from .study import records,observe,perturb


def matrix(rows,cfg,model):
    names=list(cfg["features"]["aggregate"])
    if model!="A":names+=cfg["features"]["mobility_added"]
    if model.startswith("F"):names+=cfg["features"]["links_added"]
    x=np.array([[r["features"][n] for n in names] for r in rows],float).reshape(-1,len(names))
    for j,name in enumerate(names):
        zero=(model=="F_no_family" and "family" in name or
              model=="F_no_assistance" and ("assistance" in name or "helper_minus_client" in name) or
              model=="F_counts" and name in cfg["features"]["links_added"] and "_per_remaining" not in name)
        if zero:x[:,j]=0
    return x


def clipped(prediction,rows):return np.clip(prediction,0,[180-r["t"] for r in rows])


def analyse(folder,cfg,manifest,rows):
    main=[r for r in rows if r["variant"]=="main"]
    train=[r for r in main if r["partition"]=="train"]
    validation=[r for r in main if r["partition"]=="validation"]
    tr=[r for r in manifest["runs"] if r["variant"]=="main" and r["partition"]=="train"]
    va=[r for r in manifest["runs"] if r["variant"]=="main" and r["partition"]=="validation"]
    assert train and validation and set(r["run_id"] for r in train).isdisjoint(r["run_id"] for r in validation)
    tuning=[];selected={};fitted={}
    w=weights(train,tr)
    for model in cfg["predictors"]:
        best=None
        for kind in cfg["learners"]["candidates"]:
            lengths=[1] if kind=="ridge" else sorted(cfg["learners"]["rbf_length_grid"],reverse=True)
            for alpha in sorted(cfg["learners"]["alpha_grid"],reverse=True):
                for length in lengths:
                    setting={"kind":kind,"alpha":alpha,"length":length}
                    est=Regressor(**setting).fit(matrix(train,cfg,model),[r["target"] for r in train],w)
                    error=score(validation,clipped(est.predict(matrix(validation,cfg,model)),validation),va)
                    tuning.append({"model":model,**setting,"validation_mae":error})
                    if best is None or error<best[0]-1e-12:best=(error,setting)
        selected[model]=best[1]
        fitting=train+validation
        fitted[model]=Regressor(**best[1]).fit(matrix(fitting,cfg,model),[r["target"] for r in fitting],weights(fitting,tr+va))
    simple,simple_tuning=simple_references(cfg,train,validation,va,tr)
    fitting=train+validation
    y=np.array([r["target"] for r in fitting]);w=weights(fitting,tr+va);order=np.argsort(y,kind="stable")
    constant={"kind":"constant","value":float(y[order[np.searchsorted(np.cumsum(w[order]),.5)]])}
    capacity=min([r for r in simple_tuning if r["kind"]=="capacity"],key=lambda r:r["validation_mae"])
    write(folder/"selection.json",{"settings":selected,"tuning":tuning,"simple_tuning":simple_tuning,
          "simple_selected_on_validation":simple["kind"],"constant_final":constant,"capacity":capacity,
          "train_run_ids":[r["run_id"] for r in tr],"validation_run_ids":[r["run_id"] for r in va]})
    groups=sorted({(r["variant"],r["partition"]) for r in manifest["runs"] if r["partition"] in ["test","held_out_geometry_test"]})
    output=[]
    for variant,partition in groups:
        query=[r for r in rows if r["variant"]==variant and r["partition"]==partition]
        runs=[r for r in manifest["runs"] if r["variant"]==variant and r["partition"]==partition]
        metrics={}
        for model in cfg["predictors"]+["constant","capacity"]:
            pred=(predict_simple(constant if model=="constant" else capacity,query) if model in ["constant","capacity"]
                  else clipped(fitted[model].predict(matrix(query,cfg,model)),query))
            metrics[model]=run_metrics(query,pred,runs)
            write(folder/"predictions"/f"{variant}__{partition}__{model}.json",
                  [{"run_id":r["run_id"],"t":r["t"],"target":r["target"],"prediction":float(p)} for r,p in zip(query,pred)])
        output.append({"variant":variant,"partition":partition,"models":{model:{"mae":macro(blocks(m)),
                       "rmse":float(np.sqrt(macro(blocks(m,"mse")))),"mean_underprediction":macro(blocks(m,"underprediction"))} for model,m in metrics.items()},
                       "M_minus_F":interval(metrics["M"],metrics["F"]),"counts_minus_full":interval(metrics["F_counts"],metrics["F"]),"run_metrics":metrics})
    corruptions=[]
    runs=[r for r in manifest["runs"] if r["variant"]=="main" and r["partition"]=="held_out_geometry_test"]
    for mode in ["drop_one_each_type","rewire_one_each_type"]:
        query=[];attained=[]
        for row in runs:
            result=read(folder/"trajectories"/(row["run_id"]+".json"))
            query.extend(records(result,cfg,mode))
            _,counts=perturb(observe(result,2,cfg),mode,row["seeds"]["corruption"])
            attained.append({"run_id":row["run_id"],**counts})
        pred=clipped(fitted["F"].predict(matrix(query,cfg,"F")),query)
        corruptions.append({"mode":mode,"mae":score(query,pred,runs),"attained_supplied_link_corruption":attained,"refitted":False})
        write(folder/"predictions"/("corruption__"+mode+".json"),[{"run_id":r["run_id"],"t":r["t"],"target":r["target"],"prediction":float(p)} for r,p in zip(query,pred)])
    write(folder/"results.json",output);write(folder/"corruption.json",corruptions)
    return output
