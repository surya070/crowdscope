# Stage 6 — development movement checks, 4 November 2026

## Completed

Restored 216 dependency files from the verified current-study backup, checked per-file hashes, and confirmed JuPedSim 1.4.2 with Shapely 2.1.2. Dependencies remain ignored under `.deps/recovery-r1/`. Recovery record: `research/stage6_environment.json`.

`research/run_simulation_checks.py` builds five movement fixtures with CollisionFreeSpeedModelV2: one walker, two independent following agents, a 1 m doorway, a mixed-speed queue and a right-angle turn. A sixth fixture checks an invalid target outside the accessible area. These are development fixtures, not assistance-linked agents or validated wheelchair profiles.

For each fixture the script runs dt=0.01 and 0.005 s. All five valid fixtures completed and passed occupant conservation, finite positions, speed ceilings, circle spacing and wall checks. Maximum permitted overlap is 0.001 m, wall penetration 0.005 m and speed excess 0.02 m/s. Coarse/fine clearance differences were 0–0.005 s, within the predefined max(0.2 s, 1% fine clearance) tolerance. The doorway fine run repeated exactly, including saved frames. These results do not establish statistical robustness across crowds or behavioural realism.

The invalid target was rejected by the engine at both timesteps. This verifies explicit handling of an invalid destination, **not** successful simulation of a physical deadlock or blocked accessible exit.

Completed results: `output/simulation_checks_v2/{lock.json,results.json,summary.json}`. The lock records source hash, geometry WKT, starts, speeds and tolerances before the run. `doorway_trajectories.csv` exports metre/second source observations in the Stage 4 canonical format. No reserved benchmark seeds or evaluation outcomes were used.

## Parameters and targets

Agent radius 0.22 m; time gap 0.8 s; neighbour repulsion strength 2.6. Other parameters are the pinned engine defaults: neighbour range 0.1, geometry repulsion strength 5.0 and range 0.02. Speeds and exact geometry are recorded in the run lock. Native IDs are mapped to stable run-local IDs during export.

Direct steering guides agents to a goal within the connected walkable region. An agent exits only when its centre minus radius has crossed the specified downstream plane. This is a manual full-circle exit convention, not empirical head-centre passage. Sampled frames are at 0.1 s; collision, wall and count checks run every integration step. Removed agents remain in the exit ledger; exported occupancy includes only observations actually recorded.

## Development interruption preserved

The initial v1 execution passed the five valid fixtures, then stopped on the invalid-target engine exception before saving final results. Its initial lock is retained in `output/simulation_checks_v1/`. No final v1 result is claimed. Version 2 adds explicit handling of this expected rejection and incremental progress saving, then reruns the checks. This is a development harness correction after observing development outcomes; it does not alter a sealed evaluation result.

## Stage decision and remaining work

**Numerical fixture milestone passed; Stage 6 is not complete.** Before moving to the planning benchmark:

1. Implement checked polygon/obstacle zones and integrate canonical observations with the Stage 4/5 modules.
2. Specify the three larger 80-agent development layouts, four zone partitions, spawning constraints and all model parameters before generating them. Keep geometry variants sharing a seed in the same reserved partition.
3. Test a tighter accessible passage, an actual no-path/deadlock condition, high-density initialisation, timestep refinement and completed/failed-run reporting on those layouts. Do not infer this from small fixtures.
4. Recover the authoritative SiME geometry and measurement definitions; define empirical calibration/check partitions and metrics before fitting anything. Existing trajectories are exposed development evidence. Match measurement conventions and document future arrival information if replaying observed inlets.
5. Perform empirical speed/flow/headway checks where matching geometry/labels permit; otherwise document exactly which behaviours remain unvalidated. No current parameter is a calibrated wheelchair/child parameter.
6. Keep the final evaluation release blocked on these tasks and the unresolved literature/data-term gates. The all-pass numerical summary is not an evaluation-release flag.

The next work should finish this Stage 6 integration/calibration gate, rather than jumping directly to a favourable allocation result.
