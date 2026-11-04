# Entrance sensitivity and empirical preparation — 4 November 2026

## Declared development experiments

`research/diagnose_entrance.py` holds the roster, speeds, radius, interaction strength 2.6 and waypoint routing fixed. It changes starting positions by independent uniform offsets up to 0.04 m (seed 460000), width from 1.0 to 1.2 m, or both. The original regular-grid 1.0 m case is the previously saved baseline. Configurations and perturbed roster are saved before execution in `output/entrance_diagnosis_v1/lock.json`. All variants remain in development block 410000.

At dt=0.005 s, all new variants clear 80/80 agents without spatial/speed failures:

- 1.0 m, perturbed grid: 110.280 s.
- 1.2 m, regular grid: 83.080 s.
- 1.2 m, perturbed grid: 85.075 s.

The predeclared 1.0 m perturbed refinement at dt=0.0025 leaves 39 agents unexited at 120 s. Thus breaking grid regularity can remove a particular jam at one timestep, but does not establish a robust correction.

After those outcomes, a separately locked development extension (`research/refine_wide_entrance.py`, `output/wide_entrance_refinement_v1/`) checks both 1.2 m variants at dt=0.0025. Both complete without spatial/speed failures, in 85.065 s and 80.9375 s respectively. Differences from dt=0.005 are 1.985 s and 4.1375 s, exceeding their 1% tolerances. These runs cannot be promoted as stable clearance benchmarks. The extension was motivated by observed development outcomes and is not independent confirmation.

## Interpretation

The jam depends on initial conditions, width and numerical integration. The tests do not uniquely identify the cause or prove one representation realistic. Preserve the original failures, do not discard jammed seeds, and do not weaken the stability tolerance retrospectively. One development block cannot estimate a failure probability.

The t=10 density/state integration works in these runs: all eighty observations are assigned once, and paired timesteps retain the same four-zone counts for each initialisation. This is a count-consistency observation, not full trajectory convergence or proof of calibrated mobility probabilities.

## Empirical progress and gate

The verified SiME documentation and exact per-run geometries have now been inspected. A locked measurement script extracted crossing flow, headway and approach-speed diagnostics from all fourteen available trials. See `research/empirical_movement_targets.md`. These measurements establish concrete comparison targets; the generic room experiments have not been calibrated against them and cannot be called validated SiME simulations.

Stage 6 remains open. No final evaluation seeds or planner outcomes were accessed. The next simulator work must be a **matched empirical movement check**, with geometry, coordinate/body conventions and arrival treatment defined before fitting, rather than a growing search for a configuration that happens to clear quickly.

For paper scope review: density/composition estimation and finite-budget resource planning remain viable core objectives under the existing plan. Clearance forecasting was secondary and remains withheld. A bounded simulation-led allocation study can proceed only with explicit movement-model limitations and an amended gate; it cannot claim real evacuation safety, real staffing effectiveness or movement-based demographic recognition. Keep this option explicit if a general validated simulator cannot be achieved.
