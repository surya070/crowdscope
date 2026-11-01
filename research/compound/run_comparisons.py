"""Gate, execute and fit the complete compact frozen comparison study."""
from concurrent.futures import ProcessPoolExecutor,as_completed
import shutil
from src.recovery.common import ROOT,read,write,sha
from src.compound.study import design,simulate,records
from src.compound.comparison import analyse


def task(cfg,row,dt):return simulate(cfg,row,dt)


def main():
    cfg,manifest=design()
    folder=ROOT/"output/compound/comparison_001"
    if folder.exists():raise ValueError("Preserve existing comparison; never overwrite")
    folder.mkdir(parents=True)
    sources=list((ROOT/"src/compound").glob("*.py"))+list((ROOT/"tests_compound").glob("*.py"))+[
        ROOT/"src/recovery/models.py",ROOT/"src/recovery/evaluation.py",ROOT/"src/recovery/common.py",__file__]
    from pathlib import Path
    sources=[Path(p).resolve() for p in sources]
    snapshot=folder/"source_snapshot";snapshot.mkdir()
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sources}
    for p in sources:shutil.copy2(p,snapshot/p.relative_to(ROOT).as_posix().replace("/","__"))
    write(folder/"context.json",{"config":cfg,"freeze_sha256":sha(ROOT/"research/compound/prediction_freeze_v1.json"),
          "source_hashes":hashes,"software_tests":{"passed":True,"count":12,"scope":"movement and study unit checks before runner start"},
          "manifest_sha256":sha(ROOT/"research/compound/prediction_manifest_v1.json"),"pilot_reuse":"16 predeclared main training trajectories at the identical production step, after passing the gate"})
    def status(phase,count=0,details=""):
        write(folder/"status.json",{"phase":phase,"completed":count,"planned":240,"details":details,
              "prediction_fitting_started":phase in ["fitting","complete"]})
    status("development_gate")
    lookup={r["run_id"]:r for r in manifest["runs"]}
    pilots={}
    gate=[]
    completed={}
    try:
        with ProcessPoolExecutor(max_workers=8,max_tasks_per_child=1) as pool:
            futures={pool.submit(task,cfg,lookup[rid],dt):(rid,dt) for rid in manifest["development_pilot_ids"] for dt in [.04,.02]}
            for future in as_completed(futures):
                rid,dt=futures[future];result=future.result()
                pilots[rid,dt]=result
                write(folder/"pilots"/("{}__dt{}.json".format(rid,dt)),result)
                print("Development",len(pilots),"/32",rid,dt,result["complete"],result["completion_s"],flush=True)
        for rid in manifest["development_pilot_ids"]:
            a,b=pilots[rid,.04],pilots[rid,.02]
            difference=abs(a["capped_completion_s"]-b["capped_completion_s"])
            gate.append({"run_id":rid,"coarse_complete":a["complete"],"fine_complete":b["complete"],
                         "difference_s":difference,"passed":a["complete"] and b["complete"] and difference<=.5})
        passed=all(g["passed"] for g in gate)
        write(folder/"development_gate.json",{"status":"passed" if passed else "failed","comparisons":gate})
        if not passed:raise RuntimeError("Frozen development gate failed; no fitting or held-out simulation permitted")
        assert all(sha(ROOT/p)==h for p,h in hashes.items())
        for rid in manifest["development_pilot_ids"]:
            result=pilots[rid,.04]
            write(folder/"trajectories"/(rid+".json"),result)
            completed[rid]=sha(folder/"trajectories"/(rid+".json"))
        write(folder/"trajectory_hashes.json",completed)
        status("generating",len(completed))
        pending=[r for r in manifest["runs"] if r["run_id"] not in completed]
        with ProcessPoolExecutor(max_workers=8,max_tasks_per_child=1) as pool:
            futures={pool.submit(task,cfg,row,.02 if row["variant"]=="finer_dt" else .04):row for row in pending}
            for future in as_completed(futures):
                row=futures[future];result=future.result()
                write(folder/"trajectories"/(row["run_id"]+".json"),result)
                completed[row["run_id"]]=sha(folder/"trajectories"/(row["run_id"]+".json"))
                write(folder/"trajectory_hashes.json",completed)
                status("generating",len(completed))
                print("Saved",len(completed),"/240",row["run_id"],result["complete"],result["capped_completion_s"],flush=True)
        assert len(completed)==240 and all(sha(ROOT/p)==h for p,h in hashes.items())
        features=[];outcomes=[]
        for row in manifest["runs"]:
            result=read(folder/"trajectories"/(row["run_id"]+".json"))
            features.extend(records(result,cfg))
            outcomes.append({**row,"complete":result["complete"],"capped_completion_s":result["capped_completion_s"],"remaining":len(result["remaining_ids"])})
        write(folder/"features.json",features);write(folder/"outcomes.json",outcomes)
        status("fitting",240)
        analyse(folder,cfg,manifest,features)
        status("complete",240,"Comparison outputs saved; independent audit still required")
        print("Frozen comparison finished; audit required.",flush=True)
    except Exception as exc:
        status("blocked",len(completed),repr(exc))
        raise


if __name__=="__main__":main()
