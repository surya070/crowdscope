# Frozen linkage benchmark: implementation and movement admission

2 November 2026. **All planned movement and numerical admission checks passed. Linkage forecasting models have not been trained.**

## Execution and provenance

The protocol,192-run scenario manifest, verified configuration and movement source were hashed before this benchmark. Generation, feature extraction and fitting implementation files were additionally hashed in `research/assistance/linkage_implementation_freeze_v1.json` before any new benchmark run was generated. All recorded hashes still match. The independent movement audit was written after generation; it does not change the design or fit models.

Executed all192 main runs at dt.005s and all48 preassigned finer replays at dt.0025s. No failed run was dropped, redrawn or replaced. Both gains1.0/1.15 and coordinated/independent movement were retained in every matched block. All initial placements were accepted.

## Admission results

-192 main runs complete with all recorded movement checks passing.
-48 finer runs complete and meet the unchanged timing tolerance.
-Maximum coarse/fine clearance difference:.005s (tolerance at least.2s).
-576 eligible forecast queries at2/5/8s; none moved or excluded for early completion.
-1,152 prefix-removal checks for correct and shuffled graph features pass exactly.
-M features remain identical when graph assignments are shuffled.
-15,883 saved-frame identity-union checks pass against the initial roster.

Checks cover native-step finite positions, separate occupant accounting, full nominal-circle crossings, disk overlaps/wall penetration, speed ceilings and coordinated-pair gaps. The saved-record audit verifies hashes, completion, finer-time differences and identity unions; it is not an independent reimplementation of every integration-step geometry check.

## Scientific interpretation

This is a prospective synthetic benchmark relative to previously developed movement rules, not an independent validation of human assistance. There are48 matched blocks, not240 independent populations. Independent gain variants can have identical motion because the assumed speed gain is used only by coordination; do not count that duplication as new behavioural evidence.

Primary forecasting stratum remains coordinated movement with zero assumed speed gain. Correct links must be compared against M, link counts and wrong assignments. A known target exists because the simulator records full nominal-circle crossing events. This is implementation ground truth, not proof that those times match real human evacuation.

The engine is a circular escort approximation with no physical wheelchair push/contact model and no observed helper calibration. Simulated findings must stay separate from the measured SiME cohort-passage results. Layouts are seen during training; held-out blocks test new sampled paces/placements within these layouts.

## Files and next stage

`runs/` contains all240 movement outputs. `movement_gate.json` records admission, hashes and fine differences; `movement_audit.json` records independent saved-output and causal-feature checks. Frozen source files live under `research/assistance/`.

Next: run the frozen fitting implementation, selecting settings only on validation blocks, and independently reconstruct evaluation metrics. Stop at this completed movement stage for user review. No linkage advantage, negative finding or paper-readiness conclusion is established yet.
