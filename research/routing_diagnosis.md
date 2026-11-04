# Routing and interaction diagnosis — 4 November 2026

All runs are development investigations after observing the earlier failures. None is an independent test or empirical calibration. Original scripts, locks, failures and outputs are preserved.

## Tested explanation

The pinned JuPedSim `Simulation.add_direct_steering_stage` docstring states that it bypasses tactical/strategic levels. This motivated a controlled routing ablation, not a conclusion that routing caused the jam. A waypoint at the existing final goal, radius 0.1 m, restores the standard routed stage. The manual downstream full-circle exit plane remains unchanged.

`research/diagnose_crowd_routing.py` compares direct steering with neighbour strength 8, waypoint with strength 2.6 and waypoint with strength 8, against the already saved direct/2.6 baseline. Same room/turn geometries, 80-person roster, speeds, body size, time gap and tolerance checks. Primary dt=0.005 s. Waypoint/8 also receives a predeclared dt=0.0025 refinement. The experiment lock precedes execution.

## Findings

- At each matched interaction strength and timestep, routing changes alone did not change the room/turn clearance outcomes. Thus the proposed routing explanation was **not supported** for these fixtures.
- Room with strength 2.6: waypoint and direct both leave 53 people unexited at 120 s.
- Room with strength 8: direct and waypoint both stop after four exits at dt=0.005 due to wall penetration 0.005214 m, exceeding the fixed 0.005 m limit. The finer waypoint run stops after eleven exits with wall penetration 0.005005 m. Neither is a valid completed run; do not replace the strict gate with a rounded value.
- Turn with strength 8: direct and waypoint both clear in 51.915 s at dt=0.005. Waypoint clears in 52.4325 s at dt=0.0025, difference 0.5175 s within its 0.524325 s (1%) tolerance. This is a narrowly passing development convergence pair, not proof of full convergence or a universal model improvement.
- Turn strength 2.6 remains 70.205 s at dt=0.005. Faster passage under another parameter is not evidence of better real-world accuracy.

The supported diagnosis is sensitivity to the interaction configuration and dense bottleneck dynamics. A unique mechanical cause of the jam has not been demonstrated. Waypoint routing remains a reasonable standard interface, but cannot be presented as the fix.

## Alternative model

After those development outcomes, `research/diagnose_avm.py` declares a separate candidate: JuPedSim 1.4.2 AVM with model seed 113, default time gap 1.06 s, neighbour strength 8, radius 0.22 m, other pinned AVM defaults, and the same room/turn geometry and roster. This changes a model bundle, so it is not an isolated interaction-strength comparison.

All four AVM runs (two geometries × two timesteps) stop on the wall-penetration check before reaching the 10 s checkpoint. No model is selected on the basis of its speed or advertised capabilities. The earlier CFS fixtures do not validate this alternative.

## Checkpoint availability correction

The inherited run wrapper calls the general snapshot routine even when the simulation has stopped before t=10. An empty observation list correctly yields zero visible observations in that routine, but the wrapper was failing to distinguish an unavailable checkpoint from a genuinely empty simulated crowd.

`research/audit_routing_diagnosis.py` independently checks saved trajectory timestamps. It writes `output/routing_diagnosis_audit.json`, with `checkpoint_available=false` and usable count `null` for early-terminated runs. Raw outputs remain unchanged. **All four AVM checkpoint summaries are unusable and must not enter planning or density comparisons.** Future engine wrappers must track integration termination time and exit roster explicitly; absence of observations cannot alone establish zero remaining occupants.

## Decision

The turn has a promising numerically stable development candidate. The room bottleneck remains unresolved, and no empirical realism check has been completed. Stage 6 and final evaluation release remain open. Do not proceed as though all layouts passed.

Next: inspect the dense bottleneck contact/flow pattern, test justified asymmetry or entrance geometry variations with declared configs, and define a matched empirical movement check before selecting a configuration. If a general stable crowd model cannot be established, restrict the paper's validated scope to measured zone-state analysis and a hypothetical allocation benchmark, with clearance forecasting explicitly withheld. That scope change requires a recorded protocol amendment and user review.
