"""Execute only predeclared movement checks; preserve every result and source hash."""
import json
from pathlib import Path
from src.compound.cases import cases
from src.compound.movement import run
from src.recovery.common import ROOT, OUTPUT, read, write, sha


def main():
    folder=ROOT/"output/compound/feasibility_001"
    if folder.exists():
        raise ValueError("Verification folder exists; never overwrite an attempt")
    folder.mkdir(parents=True)
    design=ROOT/"research/compound/verification_design.md"
    sources=list((ROOT/"src/compound").glob("*.py"))+[Path(__file__).resolve()]
    write(folder/"context.json",{"verification_design_sha256":sha(design),
          "source_hashes":{p.relative_to(ROOT).as_posix():sha(p) for p in sources},
          "scope":"Movement feasibility only; no prediction protocol frozen, no predictors or held-out scenarios"})
    results={}
    failures=[]
    checks=[]
    for case in cases():
        for dt,resolution in [(.04,16),(.02,16),(.01,16),(.01,32)]:
            key=f"{case['name']}__dt{dt}__q{resolution}"
            try:
                result=run(case,dt,resolution)
                write(folder/(key+".json"),result)
                results[case["name"],dt,resolution]=result
                passed=result["complete"]==case["expected_complete"]
                if "analytic_s" in case:
                    passed=passed and abs(result["completion_s"]-case["analytic_s"])<=case.get("analytic_tolerance_steps",2)*dt+1e-8
                if not case["expected_complete"]:
                    passed=passed and not result["exits"] and len(result["remaining_ids"])==2
                passed=passed and result["verification"]["max_family_gap_m"]<=1.10
                checks.append({"case":case["name"],"dt":dt,"resolution":resolution,"passed":passed,
                               "complete":result["complete"],"completion_s":result["completion_s"],
                               "initial_occupants":result["initial_occupants"],"exited":len(result["exits"]),
                               "remaining":len(result["remaining_ids"]),"analytic_s":case.get("analytic_s")})
                print(key,"passed",passed,"complete",result["complete"],"time",result["completion_s"],flush=True)
            except Exception as exc:
                failure={"case":case["name"],"dt":dt,"resolution":resolution,"error":repr(exc)}
                failures.append(failure)
                write(folder/(key+"__failure.json"),failure)
                print("Failure",failure,flush=True)
    stability=[]
    for case in cases():
        for a,b in [((.04,16),(.02,16)),((.02,16),(.01,16)),((.01,16),(.01,32))]:
            first=results.get((case["name"],*a));second=results.get((case["name"],*b))
            if first is None or second is None:
                stability.append({"case":case["name"],"passed":False,"reason":"Missing valid run"})
                continue
            difference=abs(first["completion_s"]-second["completion_s"]) if first["complete"] and second["complete"] else None
            passed=first["complete"]==second["complete"] and (difference is None or difference<=.5)
            stability.append({"case":case["name"],"first":a,"second":b,"difference_s":difference,"passed":passed})
    original=read(ROOT/"research/protocol_freeze.json")
    assert all(sha(ROOT/p)==h for p,h in original["files"].items())
    summary={"status":"passed" if len(checks)==28 and all(c["passed"] for c in checks) and all(c["passed"] for c in stability) and not failures else "failed",
             "checks":checks,"stability":stability,"failures":failures,"original_inputs_unchanged":True,
             "study_predictors_fitted":0,"revised_prediction_protocol_frozen":False}
    write(folder/"verification.json",summary)
    print("Movement gate:",summary["status"],flush=True)


if __name__=="__main__":main()
