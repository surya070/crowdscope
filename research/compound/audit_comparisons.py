"""Saved-result audit using independent standard-library metric aggregation."""
import csv
import math
import statistics
from collections import defaultdict
from src.recovery.common import ROOT,read,write,sha
from src.compound.study import design


def average(records,key):
    block=defaultdict(list)
    for r in records:block[r["geometry"],r["block_id"]].append(r[key])
    geo=defaultdict(list)
    for (g,_),v in block.items():geo[g].append(statistics.mean(v))
    return statistics.mean(statistics.mean(v) for v in geo.values())


def close(a,b):
    if not math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-9):raise ValueError(f"Audit mismatch {a}, {b}")


def main():
    cfg,manifest=design()
    folder=ROOT/"output/compound/comparison_001"
    context=read(folder/"context.json")
    assert context["config"]==cfg
    assert all(sha(ROOT/p)==h for p,h in context["source_hashes"].items())
    hashes=read(folder/"trajectory_hashes.json")
    planned={r["run_id"]:r for r in manifest["runs"]}
    assert set(hashes)==set(planned) and len(hashes)==240
    completed=0;frame_count=0;completion=defaultdict(lambda:[0,0]);all_results={}
    for rid,h in hashes.items():
        p=folder/"trajectories"/(rid+".json")
        assert sha(p)==h
        r=read(p);all_results[rid]=r
        assert r["run"]==planned[rid]
        n=r["initial_occupants"]
        assert n==planned[rid]["n"] and len(r["exits"])+len(r["remaining_ids"])==n
        assert set(r["exits"]).isdisjoint(str(i) for i in r["remaining_ids"])
        assert {str(p["id"]) for p in r["people"]}==set(r["exits"])|{str(i) for i in r["remaining_ids"]}
        assert r["complete"]==(not r["remaining_ids"])
        close(r["capped_completion_s"],max(r["exits"].values()) if r["complete"] else 180)
        g=r["geometry"]
        roster={str(p["id"]):p for p in r["people"]}
        for frame in r["frames"]:
            frame_count+=1
            assert len(frame["positions"])+sum(t<=frame["t"]+1e-9 for t in r["exits"].values())==n
            positions=frame["positions"]
            ids=list(positions)
            for i,xy in positions.items():
                radius=roster[i]["radius"]
                assert xy[0]-radius>=-1e-8 and xy[0]+radius<=g["length_m"]+4+1e-8
                assert xy[1]-radius>=-1e-8 and xy[1]+radius<=g["width_m"]+1e-8
            for a,i in enumerate(ids):
                for j in ids[a+1:]:
                    assert math.dist(positions[i],positions[j])+1e-8>=roster[i]["radius"]+roster[j]["radius"]
            for e in r["edges"]:
                a,d=str(e["adult"]),str(e["dependent"])
                if e["type"]=="assistance" and a in positions and d in positions:close(math.dist(positions[a],positions[d]),.75)
        assert r["verification"]["accounting_checked_every_update"] and r["verification"]["sweeps_checked_every_accepted_move"]
        completed+=r["complete"]
        key=r["run"]["variant"],r["run"]["geometry"],r["run"]["condition"]
        completion[key][0]+=1;completion[key][1]+=r["complete"]
    rows=read(folder/"features.json");by_run=defaultdict(list)
    for f in rows:
        rid=f["run_id"];r=all_results[rid]
        assert all(f[k]==planned[rid][k] for k in ["variant","partition","condition","geometry","block_id"])
        assert set(f["features"])==set(sum(cfg["features"].values(),[]))
        close(f["target"],max(0,r["capped_completion_s"]-f["t"]))
        cutoff=f["t"]-.2
        frame=next(frame for frame in r["frames"] if abs(frame["t"]-cutoff)<1e-8)
        close(f["features"]["remaining_count"],len(frame["positions"]))
        by_run[rid].append(f)
    selection=read(folder/"selection.json")
    assert len(selection["train_run_ids"])==48 and len(selection["validation_run_ids"])==16
    assert set(selection["train_run_ids"]).isdisjoint(selection["validation_run_ids"])
    for model in cfg["predictors"]:
        candidates=[r for r in selection["tuning"] if r["model"]==model]
        best=candidates[0]
        for c in candidates[1:]:
            if c["validation_mae"]<best["validation_mae"]-1e-12:best=c
        assert selection["settings"][model]=={k:best[k] for k in ["kind","alpha","length"]}
    groups=read(folder/"results.json");table=[]
    assert len(groups)==4
    for group in groups:
        runs=[r for r in manifest["runs"] if r["variant"]==group["variant"] and r["partition"]==group["partition"]]
        assert len(runs)>0
        for model in cfg["predictors"]+["constant","capacity"]:
            predictions=read(folder/"predictions"/f"{group['variant']}__{group['partition']}__{model}.json")
            lookup={(p["run_id"],p["t"]):p for p in predictions}
            assert len(lookup)==len(predictions)
            expected={(r["run_id"],f["t"]) for r in runs for f in by_run[r["run_id"]]}
            assert set(lookup)==expected
            metrics=[];saved={r["run_id"]:r for r in group["run_metrics"][model]}
            for run in runs:
                errors=[]
                for row in by_run[run["run_id"]]:
                    p=lookup[row["run_id"],row["t"]]
                    close(p["target"],row["target"])
                    assert 0<=p["prediction"]<=180-row["t"]
                    errors.append(p["prediction"]-p["target"])
                m={**run,"mae":statistics.mean(abs(e) for e in errors) if errors else 0,
                   "mse":statistics.mean(e*e for e in errors) if errors else 0,
                   "underprediction":statistics.mean(max(0,-e) for e in errors) if errors else 0}
                for key in ["mae","mse","underprediction"]:close(m[key],saved[run["run_id"]][key])
                assert saved[run["run_id"]]["checkpoint_count"]==len(errors)
                metrics.append(m)
            reported=group["models"][model]
            close(average(metrics,"mae"),reported["mae"])
            close(math.sqrt(average(metrics,"mse")),reported["rmse"])
            close(average(metrics,"underprediction"),reported["mean_underprediction"])
            table.append({"variant":group["variant"],"partition":group["partition"],"model":model,**reported})
        close(group["models"]["M"]["mae"]-group["models"]["F"]["mae"],group["M_minus_F"]["reduction_s"])
    refinement=[]
    for row in manifest["runs"]:
        if row["variant"]=="finer_dt":
            a=all_results[row["run_id"].replace("finer_dt__","main__")];b=all_results[row["run_id"]]
            refinement.append({"run_id":row["run_id"],"difference_s":abs(a["capped_completion_s"]-b["capped_completion_s"]),"status_agrees":a["complete"]==b["complete"]})
    condition_effect=[]
    mainblocks=defaultdict(dict)
    for r in all_results.values():
        if r["run"]["variant"]=="main":mainblocks[r["run"]["block_id"]][r["run"]["condition"]]=r["capped_completion_s"]
    for block,conditions in mainblocks.items():
        condition_effect.append({"block_id":block,"family_minus_independent_s":conditions["family_only"]-conditions["independent"],
                                 "assistance_minus_independent_s":conditions["assistance_only"]-conditions["independent"],
                                 "both_minus_independent_s":conditions["family_and_assistance"]-conditions["independent"]})
    for name,data in [("audited_metrics.csv",table),("refinement_differences.csv",refinement),("matched_condition_effects.csv",condition_effect)]:
        with (folder/name).open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]));writer.writeheader();writer.writerows(data)
    # Publication copy: the unrelated earlier empirical branch is not distributed.
    # All compound protocol, source and trajectory hashes are verified above.
    summary={"status":"passed","trajectory_hashes_verified":240,"completed":completed,"censored":240-completed,
             "saved_frames_accounted":frame_count,"checkpoint_rows":len(rows),"metric_groups_recomputed":len(table),
             "max_production_refinement_difference_s":max(r["difference_s"] for r in refinement),
             "refinement_status_agrees":all(r["status_agrees"] for r in refinement),
             "primary":next(g["M_minus_F"] for g in groups if g["variant"]=="main" and g["partition"]=="held_out_geometry_test"),
             "compound_frozen_inputs_unchanged":True,"audit_did_not_refit":True,
             "audit_source_sha256":sha(__file__),"scope":"Internal saved-result audit; not independent empirical validation"}
    write(folder/"independent_audit.json",summary)
    print(summary)


if __name__=="__main__":main()
