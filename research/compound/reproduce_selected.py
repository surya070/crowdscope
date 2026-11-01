"""Fresh-process reproduction at saved validation-selected settings, without retuning."""
import numpy as np
from src.compound.study import design
from src.compound.comparison import matrix,clipped
from src.recovery.models import Regressor,weights
from src.recovery.common import ROOT,read,write,sha


def main():
    cfg,manifest=design()
    folder=ROOT/"output/compound/comparison_001"
    assert read(folder/"independent_audit.json")["status"]=="passed"
    rows=read(folder/"features.json")
    fitting=[r for r in rows if r["variant"]=="main" and r["partition"] in ["train","validation"]]
    runs=[r for r in manifest["runs"] if r["variant"]=="main" and r["partition"] in ["train","validation"]]
    settings=read(folder/"selection.json")["settings"]
    groups=read(folder/"results.json")
    checks=[]
    for model in cfg["predictors"]:
        estimator=Regressor(**settings[model]).fit(matrix(fitting,cfg,model),[r["target"] for r in fitting],weights(fitting,runs))
        for group in groups:
            query=[r for r in rows if r["variant"]==group["variant"] and r["partition"]==group["partition"]]
            pred=clipped(estimator.predict(matrix(query,cfg,model)),query)
            saved=read(folder/"predictions"/f"{group['variant']}__{group['partition']}__{model}.json")
            assert [(r["run_id"],r["t"]) for r in query]==[(r["run_id"],r["t"]) for r in saved]
            difference=float(np.max(np.abs(pred-np.array([r["prediction"] for r in saved]))))
            assert difference<=1e-10
            checks.append({"model":model,"variant":group["variant"],"partition":group["partition"],"predictions":len(pred),"max_difference":difference})
    report={"status":"passed","checks":checks,"prediction_values_reproduced":sum(r["predictions"] for r in checks),
            "max_difference":max(r["max_difference"] for r in checks),"hyperparameters_retuned":False,
            "prior_test_results_seen":True,"scope":"Internal same-runtime reproduction at fixed saved settings, not independent external validation",
            "source_sha256":sha(__file__)}
    write(folder/"selected_model_reproduction.json",report)
    print({k:v for k,v in report.items() if k!="checks"})


if __name__=="__main__":main()
