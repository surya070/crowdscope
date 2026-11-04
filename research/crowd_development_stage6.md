# Stage 6 large-crowd integration — 4 November 2026

## What was built

Three declared development layouts (room, corridor and turn), each with 80 agents, explicit four-zone polygons and the same matched roster. Initial positions, overlapping mobility-profile speeds, latent memberships, per-agent parameters, observation seed and geometry were written before outcomes in `output/crowd_development_v1/lock.json`. Seed 410000 is a reserved **development** seed, used once as a matched block across layouts/timesteps. Validation/evaluation seeds remain unused.

`src/polygon_zones.py` adds obstacle-aware usable area and validates that zones cover the observable walkable geometry without interior overlap. Shared boundaries retain the lowest-ID convention. The state pipeline now accepts these polygons. Five new tests check hole area/obstacle exclusion, shared edges, missing coverage, overlap rejection and the three layout partitions. All **30 unit tests passed**.

`research/run_crowd_development.py` saves canonical trajectories, t=10 s past-only state features and probabilistic composition estimates for each run. The metadata channel remains artificial; true class membership is not a movement-recognition result. No support planner or interventions were run.

## Results and failed gate

At dt 0.01 and 0.005 s, respectively:

- Room: 27/80 and 27/80 agents exited by 120 s; both runs failed completion.
- Corridor: 27/80 and 40/80 exited; both runs failed completion.
- Turn: all 80 exited in 67.260 s and 70.205 s. The 2.945 s difference exceeds max(0.2 s, 1% fine time), so the timestep-stability gate failed.

Per-step overlap, wall and speed tolerances passed in all six runs. That does not override the failed completion/stability checks. A diagnostic of the room fine run found all 53 remaining agents moving less than 0.01 m/s by displacement over the final ten seconds, near the bottleneck. This suggests a persistent jam in this setup; it does not establish its physical realism or a single causal mechanism.

At t=10 s, counts across four zones were [1,46,30,3] for room/corridor and [4,55,13,8] for turn, summing to 80 in every run. The densities differ because usable zone areas differ. These are development snapshots, not independent statistical findings or recogniser validation.

**Decision: gate failed; do not release the clearance-time benchmark or claim simulator readiness.** Retain every failed run. Do not substitute last observed time for clearance or omit jammed cases from averages. The probability/state integration works at the checkpoint, but later planning experiments using these snapshots would be conditional development analyses and would not validate evacuation interventions.

## Passage-limit diagnostics

`research/check_passage_limits.py` uses a single 0.44 m diameter agent. The 0.6 m neck cleared at 8.230/8.225 s; the 0.3 m neck had no exit by 60 s at either timestep and no wall/overlap violations. The latter is expected body-inaccessible non-completion, preserved as `noncompletion` in raw diagnostic output, not a valid traversable-layout success. Exact fixture geometry comes from `run_simulation_checks.py`; the script's run lock records widths and intent. Source files must remain with outputs for reproduction.

These diagnostics differ from the earlier invalid-target rejection: here the centre-line destination is inside the connected area, but the body cannot fit through the neck. They do not establish that the 80-agent room jam is physically correct.

## Next diagnostic sequence within Stage 6

1. Keep these results unchanged. Analyse arrival/exit flow and positions around the jam; inspect how direct-steering routing, contact geometry and interaction parameters contribute.
2. Predeclare a small development-only comparison of the pinned default CFSV2 parameters versus the earlier inherited settings. The inherited neighbour strength 2.6 was verified for small escort fixtures, not calibrated for this crowd. Any changed model/parameter gets a new config and output directory; completion alone cannot select a realistic model.
3. Test timestep refinement on the turn and congested cases, including speed/flow curves and checkpoint composition, not just final time. Preserve failure rates and runtime. Do not relax the tolerance merely to pass.
4. Evaluate a justified routing/model alternative if necessary, using the same fixtures and explicit versions. Avoid engine claims based solely on attractive animations.
5. Recover matched SiME geometry and measurement definitions and predeclare calibration metrics/partitions before fitting. Establish current terms/provenance. Since existing data are exposed, any fit is exploratory; use compatible external evidence where possible.
6. Amend the development record with outcome exposure. Freeze a run-level manifest only after numerical and empirical gates are satisfied or the scope is explicitly reduced to a bounded hypothetical model.

No empirical calibration or external validation occurred in this stage. Stage 6 remains open; Stage 7 planning and final evaluation remain gated.
