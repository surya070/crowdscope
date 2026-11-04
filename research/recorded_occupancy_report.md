# Recorded-occupancy integration — 4 November 2026

The complete pipeline now operates on fourteen recorded SiME trials at t=10/20/30 s: 42 checkpoints. `research/integrate_recorded_occupancy.py` verifies source hashes, reads metre/second trajectories and official obstacle geometry directly from the archives, and uses exact observed membership with a two-second causal history. No raw files are extracted.

Observable region: the official walkable area intersected with x in [-6,2.4] and y in [-1.65,1.65] m. Four zones split x at -6,-3,-1,0,2.4. Density denominators use actual polygon areas, subtracting walls. This region is a declared analysis window, not the whole recording or building. Outside-window observations are counted separately, not treated as exits. Shared boundaries use the existing lowest-ID rule.

All 42 checkpoints integrate without an in-window geometry mismatch. Count/density conservation, composition counts, probability mass and feasible budgets pass a separate saved-output audit. Metadata/track mismatch in trial 1307 remains flagged: local visible counts can be measured, but the trial cannot establish a reconciled full participant roster. Missing downstream passage in 507 likewise prevents a complete passage claim, not a local count.

**Evidence distinction:** positions, visible occupancy and motion are recorded observations. Service-profile observations are artificial, drawn using trial-local deterministic seeds and held fixed across its checkpoints. Membership is not an annotation of the actual person, disability or need. Request probabilities 0.1/0.4 and resource capacity are assumed. Planning output is expected hypothetical shortfall; no real request outcomes or realised staffing improvements exist here.

Outputs are in `output/recorded_occupancy_integration_v1/`: lock, source hashes, checkpoint summaries, states, expected composition and allocations. Per-person positions are derived human trajectories and remain local under ignored `output/`; do not upload these files without confirming data terms. A later distributable demo should use synthetic fixtures or permitted aggregate summaries.

Run `python research/audit_recorded_occupancy.py` to verify saved outputs. All trials were previously exposed. Checkpoints and repeated participants are dependent, so no 42-independent-samples inference is justified. This integration supports software functionality and recorded density diagnostics, not recognition calibration or external planning-effect validation.
