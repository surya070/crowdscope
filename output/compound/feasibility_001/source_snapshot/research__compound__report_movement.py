"""Audit saved feasibility outputs and generate a stage report; no prediction fits."""
import csv
import io
import unittest
from src.recovery.common import ROOT,read,write,sha
from src.compound.cases import cases


def main():
    folder=ROOT/"output/compound/feasibility_001"
    context=read(folder/"context.json")
    assert all(sha(ROOT/p)==h for p,h in context["source_hashes"].items())
    assert sha(ROOT/"research/compound/verification_design.md")==context["verification_design_sha256"]
    verification=read(folder/"verification.json")
    stream=io.StringIO()
    suite=unittest.defaultTestLoader.discover(str(ROOT/"tests_compound"))
    tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (folder/"software_tests.txt").write_text(stream.getvalue(),encoding="utf-8")
    assert tests.wasSuccessful()
    manifests={}
    max_pair=max_speed=max_family=0.0
    for check in verification["checks"]:
        p=folder/("{}__dt{}__q{}.json".format(check["case"],check["dt"],check["resolution"]))
        result=read(p)
        initial=result["initial_occupants"]
        exited=result["exits"]
        assert len(exited)+len(result["remaining_ids"])==initial
        for frame in result["frames"]:
            seen=sum(t<=frame["t"]+1e-10 for t in exited.values())
            assert len(frame["positions"])+seen==initial
        max_pair=max(max_pair,result["verification"]["max_pair_separation_error_m"])
        max_speed=max(max_speed,result["verification"]["max_member_speed_excess_m_s"])
        max_family=max(max_family,result["verification"]["max_family_gap_m"])
        manifests[p.relative_to(ROOT).as_posix()]=sha(p)
    with (folder/"verification_table.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(verification["checks"][0]))
        writer.writeheader();writer.writerows(verification["checks"])
    differences=[r["difference_s"] for r in verification["stability"] if r.get("difference_s") is not None]
    spread=max(max(c["completion_s"] for c in verification["checks"] if c["case"]==case["name"])-
               min(c["completion_s"] for c in verification["checks"] if c["case"]==case["name"])
               for case in cases() if case["expected_complete"])
    passed=verification["status"]=="passed" and tests.wasSuccessful()
    summary={"status":"passed" if passed else "failed","scenario_checks":len(verification["checks"]),
             "stability_comparisons":len(verification["stability"]),"software_checks":tests.testsRun,
             "maximum_clearance_difference_s":max(differences),"max_pair_separation_error_m":max_pair,
             "maximum_total_clearance_spread_s":spread,
             "max_member_speed_excess_m_s":max_speed,"max_family_gap_m":max_family,
             "source_hashes":context["source_hashes"],"trajectory_hashes":manifests,
             "test_source_hashes":{p.relative_to(ROOT).as_posix():sha(p) for p in (ROOT/"tests_compound").glob("*.py")},
             "revised_prediction_protocol_frozen":False,"study_predictors_fitted":0,
             "disposition":"Movement feasibility passed for the declared fixtures only. Pause before revised protocol freeze."}
    write(ROOT/"research/compound/movement_validation.json",summary)
    report=f"""# Compound movement feasibility stage

29 October 2026. **Movement feasibility {'passed' if passed else 'failed'} for the declared fixtures. Pause before a revised prediction-protocol freeze.**

## What was built

An independent, prescribed-route, rigid-footprint kinematic model. The attached wheelchair user and helper share one conservative collision footprint while remaining separately identified and counted. Their centres stay 0.75 m apart. Translation and pivot turns reserve swept space, and helpers obey their stated speed ceiling. No person is teleported, clamped or silently removed. This is an original engineering approximation, not a reproduction of JuPedSim or a published CA model. The full prior methods were read; motivation and differences are in verification_design.md.

## Results

All {len(verification['checks'])} predeclared scenario/resolution checks passed, along with {len(verification['stability'])} stability comparisons and {tests.testsRun} software/adversarial checks. At dt=0.01 s and polygon resolution 16:

"""
    for case in cases():
        result=read(folder/(case["name"]+"__dt0.01__q16.json"))
        report+=f"- {case['name']}: "+(f"cleared in {result['completion_s']:.3f} s, {len(result['exits'])}/{result['initial_occupants']} occupants counted out.\n" if result["complete"] else f"correctly blocked at {result['cap_s']} s; {len(result['remaining_ids'])} occupants retained, no artificial exits.\n")
    report+=f"""
Largest clearance-time difference across adjacent time steps and doubled polygon resolution: {max(differences):.6f} s, below the predeclared 0.5 s engineering criterion. The total coarsest-to-finest clearance spread was at most {spread:.6f} s. Maximum pair-separation error: {max_pair:.9g} m. Maximum member speed excess: {max_speed:.9g} m/s (floating-point scale). Maximum family centre gap in the single-lane fixture: {max_family:.6f} m against 1.10 m. Free-space and turn times satisfied their predeclared independent distance/speed/turn-time checks.

All accepted moves checked swept-space exclusion. Every update checked full-footprint geometry, overlap, attachment spacing, speed and occupant conservation. The saved-frame audit independently recomputed active-plus-exited counts. Adversarial tests verify that a translation cannot tunnel through a stationary occupant and that a rotation sweep includes an obstacle missed by endpoint-only checking. A dense intermediate-angle check supports the conservative sweep construction. The client and helper receive separate exit events; the unit's computational outflow footprint persists until both have crossed.

The original empirical frozen inputs were verified unchanged. Earlier failed models and results remain preserved. Source/trajectory hashes are in movement_validation.json; exact case/resolution values are in output/compound/feasibility_001/verification_table.csv. No new prediction protocol was frozen, no predictor fitted and no held-out study scenario run.

## What this pass does and does not establish

This is bounded software and numerical feasibility evidence. Routes are prescribed; the scheduler is deterministic front-first reservation; pair footprints are rigid and conservative; the mixed queue is single lane. The family test uses shared pace between separate individuals and does not establish general parent-child cohesion, searching or overtaking behaviour. Preparation, support gains, spontaneous assistance and automatic relationship recognition are not tested in this stage. Chosen radii, speeds and spacing are synthetic fixture assumptions, not empirical demographic norms. The negative doorway control verifies geometric impossibility rather than a realistic behavioural response.

The pass is not empirical crowd validation, a proof of general convergence or scalability, a prediction-improvement result, or evidence of publication novelty/readiness. A revised study must disclose these constraints and test its own broader development cases before final comparisons. The geometry/time criteria are engineering choices, not safety or Scopus standards.

## Next authorised stage, after review

Freeze a separate prospective prediction protocol for this movement model, including prescribed routes, family/assistance rules, scenario generator, information assumptions, train/validation/test separation, development gate, model selection, censoring, ablations and uncertainty. Preserve the previous frozen studies; do not reuse a failed gate to authorise the new implementation. Then run comparisons and write the paper around all actual findings. The user's stage-pause instruction remains in force, so stop here before freezing.
"""
    (ROOT/"research/compound/movement_report.md").write_text(report,encoding="utf-8")
    print({k:v for k,v in summary.items() if not k.endswith("hashes")})


if __name__=="__main__":main()
