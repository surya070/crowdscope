# Compound movement feasibility stage

29 October 2026. **Movement feasibility passed for the declared fixtures. Pause before a revised prediction-protocol freeze.**

## What was built

An independent, prescribed-route, rigid-footprint kinematic model. The attached wheelchair user and helper share one conservative collision footprint while remaining separately identified and counted. Their centres stay 0.75 m apart. Translation and pivot turns reserve swept space, and helpers obey their stated speed ceiling. No person is teleported, clamped or silently removed. This is an original engineering approximation, not a reproduction of JuPedSim or a published CA model. The full prior methods were read; motivation and differences are in verification_design.md.

## Results

All 28 predeclared scenario/resolution checks passed, along with 21 stability comparisons and 7 software/adversarial checks. At dt=0.01 s and polygon resolution 16:

- single_pedestrian: cleared in 5.200 s, 1/1 occupants counted out.
- single_wheelchair: cleared in 7.950 s, 1/1 occupants counted out.
- attached_pair_free: cleared in 6.190 s, 2/2 occupants counted out.
- accessible_doorway: cleared in 6.190 s, 2/2 occupants counted out.
- inaccessible_doorway: correctly blocked at 40 s; 2 occupants retained, no artificial exits.
- right_angle_turn: cleared in 10.570 s, 2/2 occupants counted out.
- mixed_single_lane_queue: cleared in 11.830 s, 7/7 occupants counted out.

Largest clearance-time difference across adjacent time steps and doubled polygon resolution: 0.080000 s, below the predeclared 0.5 s engineering criterion. The total coarsest-to-finest clearance spread was at most 0.090000 s. Maximum pair-separation error: 4.4408921e-16 m. Maximum member speed excess: 2.35367281e-14 m/s (floating-point scale). Maximum family centre gap in the single-lane fixture: 0.750000 m against 1.10 m. Free-space and turn times satisfied their predeclared independent distance/speed/turn-time checks.

All accepted moves checked swept-space exclusion. Every update checked full-footprint geometry, overlap, attachment spacing, speed and occupant conservation. The saved-frame audit independently recomputed active-plus-exited counts. Adversarial tests verify that a translation cannot tunnel through a stationary occupant and that a rotation sweep includes an obstacle missed by endpoint-only checking. A dense intermediate-angle check supports the conservative sweep construction. The client and helper receive separate exit events; the unit's computational outflow footprint persists until both have crossed.

The original empirical frozen inputs were verified unchanged. Earlier failed models and results remain preserved. Source/trajectory hashes are in movement_validation.json; exact case/resolution values are in output/compound/feasibility_001/verification_table.csv. No new prediction protocol was frozen, no predictor fitted and no held-out study scenario run.

## What this pass does and does not establish

This is bounded software and numerical feasibility evidence. Routes are prescribed; the scheduler is deterministic front-first reservation; pair footprints are rigid and conservative; the mixed queue is single lane. The family test uses shared pace between separate individuals and does not establish general parent-child cohesion, searching or overtaking behaviour. Preparation, support gains, spontaneous assistance and automatic relationship recognition are not tested in this stage. Chosen radii, speeds and spacing are synthetic fixture assumptions, not empirical demographic norms. The negative doorway control verifies geometric impossibility rather than a realistic behavioural response.

The pass is not empirical crowd validation, a proof of general convergence or scalability, a prediction-improvement result, or evidence of publication novelty/readiness. A revised study must disclose these constraints and test its own broader development cases before final comparisons. The geometry/time criteria are engineering choices, not safety or Scopus standards.

## Next authorised stage, after review

Freeze a separate prospective prediction protocol for this movement model, including prescribed routes, family/assistance rules, scenario generator, information assumptions, train/validation/test separation, development gate, model selection, censoring, ablations and uncertainty. Preserve the previous frozen studies; do not reuse a failed gate to authorise the new implementation. Then run comparisons and write the paper around all actual findings. The user's stage-pause instruction remains in force, so stop here before freezing.
