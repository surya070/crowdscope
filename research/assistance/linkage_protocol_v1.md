# Synthetic linkage-information protocol v1

Frozen design date: 2 November 2026. Prospective with respect to the new benchmark outcomes, **not** independent of prior simulator development. Movement is a numerically verified circular-agent escort approximation, not calibrated wheelchair pushing. This study is separate from measured SiME forecasting.

## Question and primary claim boundary

Does knowing the helper–client assignment improve synthetic remaining-clearance forecasts beyond individual mobility, motion history and the number of assistance links?

Primary stratum: coordinated movement with **zero assumed speed gain** (gain1.0). Secondary stratum: coordinated movement with hypothetical gain1.15. Independent movement is a matched behavioural control; it does not supply a meaningful true assistance graph. No result is predetermined, and a negative finding remains valid within the tested generator.

## Engine and preparation gate

JuPedSim1.4.2 CollisionFreeSpeedModelV2, neighbour repulsion2.6, threshold controller, dt.005s, helper time gap.3s, others.8s. Retain all other checked parameters. Source/config hashes are in `linkage_freeze_v1.json`. Separate `linkage_engine.py` adds configurable gain without modifying the earlier verified module. Its nominal-gain clearance/failure outputs reproduced all six base fixtures. Zero-gain verification passed all six cases at .02/.01/.005s, maximum spread.025s; records are in `output/assistance_linkage_design/`.

These checks permit a development benchmark; they do not validate assistance mechanics against humans. The engine retains distinct occupants and removes each only after its nominal disk crosses the plane.

## Frozen scenario manifest

Four layouts: two serial pairs through1m and1.2m doors, staggered two-pair merge, and two-pair turn. Twelve seed blocks per layout. Each block has identical starting people/nominal speeds across independent/coordinated conditions and gains1.0/1.15, giving192 runs. There are48 matched blocks, not192 independent populations.

For each block, client nominal speeds are uniform[.70,.95]m/s, helper paces uniform[1.1,1.3]m/s. Small common-per-pair lateral offsets uniform[-.02,.02]m perturb each client/helper together; other actor starts remain unchanged. Draws are realized once and saved in `linkage_manifest_v1.json`; no outcome-dependent regeneration. Circle radii stay.30/.22m, other pedestrian radius.22m and pace1.1m/s. No imported age/family/helper identities from SiME.

Per layout, seed slots0–7 train,8–9 validation,10–11 evaluation. All movement/gain variants and checkpoints from a block follow that block's split. Layouts appear in every split; this measures new-seed/pace transfer within known layouts, not new geometry or real people. No source outcome inspected before this design was frozen.

## Movement and numerical admission

Every generated run must pass the unchanged finite-position, occupant-count, full-circle exit, overlap<=.001m, wall penetration<=.005m, speed-excess<=.02m/s and coordinated-pair spacing<=1.4m checks within60s. Initial placement exceptions are failed runs, not permission to redraw seeds.

Predetermined slots0,8,10 in every layout, for both modes/gains, are also replayed at dt.0025s (48 fine runs). Require clearance difference<=max(.2s,1% finer clearance) and both movement checks. This subset check is not universal convergence proof.

If any run fails, preserve the full failure record and pause before fitting. Do not silently discard failed runs, change the cap, or relax tolerances. A revised generator requires a new version and fresh prospective design. Forecast queries that occur after completion are reported as ineligible under the fixed rule, never moved to better times.

## Observation and target

Queries at2,5,8s with a one-second history sampled at.2s. Target=max(0,last full-circle crossing time−query). Complete synthetic initial roster is known, unlike the empirical observed-subset target. Remove already-exited occupants from active features; short histories use explicit availability indicators and past-only values. The extraction must pass future-frame-removal checks. Target/failure data remain outside feature calculation.

## Information conditions

M: aggregate/history summaries plus supplied individual role, radius and nominal unassisted speed summaries. Fixed inputs: active count; x/y mean/spread; mean/max/90th-percentile distance to plane; mean/spread/10th/90th-percentile observed speed; stopped fraction; recent speed change; nearest visible spacing; past exit count; elapsed time; bottleneck/corridor width; turn indicator; remaining client/helper counts; nominal speed mean/min/spread; radius mean/max; rearmost nominal speed; mean/max distance divided by nominal speed; short-history fraction. Role/roster inputs are supplied exactly, not detected. No actual link, controller waiting state or gain label is included in M.

F-counts adds active-link count (both endpoints active) and linked-client fraction. F-correct adds these plus pair-gap mean/max, absolute observed speed-difference mean/max, helper-minus-client nominal-speed mean, and largest along-route separation. Route separation must use known route projection, not future trajectories.

F-shuffled uses the same feature definitions but swaps the two helper assignments in each two-pair coordinated run. Shuffle is fixed throughout that run, preserving initial edge count and each endpoint's degree; active-edge counts can diverge after exits and must be reported. No IDs enter model inputs. F-shuffled is trained/validated/evaluated with its own wrong-link features under the same budget.

F-missing is a deployment-only stress of the selected F-correct model: each edge withheld with probability.5, deterministic by block/edge and20 fixed seeds101–120; use the same zero-edge defaults as training and retain counts. It does not establish robust uncertainty-aware inference. Empty edge sets have zero summaries. M features are identical for all conditions.

## Prediction and evaluation

Fit each gain's coordinated stratum separately. For each information condition, use ridge alpha[.1,1,10,100] and boosting learning rate[.03,.1]×depth[2,3]×estimators[50,100], seed113. Fit scalers/imputers on training data only. Choose candidate by validation equal-run MAE, with fixed grid order resolving ties. Clip predictions below zero. Include training-median and simple distance/speed references. No outer-evaluation-driven learner, feature or parameter selection.

Primary contrast at gain1.0: MAE(M)−MAE(F-correct) on held-out coordinated runs. Necessary interpretation checks: F-correct versus F-counts and F-shuffled. If correct links do not improve over those controls, do not claim assignment-specific value. Report matched-family and validation-selected results. Secondary: gain1.15, layout/run errors, signed errors, underprediction and F-missing stress.

Queries first average within run; runs average equally within the reported stratum. Matched mode/gain variants are not treated as independent evidence. Report per-layout/run results without population-significance claims from this small synthetic set. Conditional intervals, if added later, must be explicitly labelled post-design; none is specified as primary. Define no operational safety tolerance without justification.

Matched independent runs assess movement differences under the same roster, not real-world effectiveness of assistance. The programmed gain cannot be used as proof of real speed benefit. No independent-model assistance-link performance claim is made for an empty true graph.

## Freeze, stop and reporting

`linkage_freeze_v1.json` hashes the protocol, scenario manifest, engine, verified candidate and zero-gain record. This freezes design and movement source, not an as-yet-unwritten fitting implementation. Implementing code must be separately hashed before outcome generation/fitting, then independently audited against this protocol. Do not claim an executable experiment has already run.

Pause after protocol review; next stage is implementation and full movement admission before any fitting. Report results as synthetic escort-model evidence alongside, not as empirical validation of, the SiME findings. Novelty and venue readiness remain unresolved.
