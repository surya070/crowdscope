# Proposed targets — Stage 2, 4 November 2026

These definitions guide protocol design; they are not new model results.

- **Occupancy/density:** number of currently visible tracked head positions in a declared zone divided by its usable area. This is observed-area occupancy, not automatically the whole building population. Freeze geometry and boundary conventions.
- **Mobility composition:** independently supported class count, or a declared movement-profile count. Historical positive-only mappings cannot establish complete true negative labels. Report expected counts and their uncertainty if using probabilities.
- **Movement recognition:** conditional class/profile probability from past x/y motion and local context. Exclude z, identity, trial name, future trajectories and label-generating rules as shortcuts. Evaluate probabilities as well as discrimination.
- **Passage time:** remaining time until the last member of the fixed observed cohort has its first forward head-centre crossing of a stated plane. The previous study used x=2.4 m. Incomplete crossings are unknown/censored, not last observed timestamps. This is not whole-building RSET.
- **Synthetic clearance:** remaining time until the full simulated roster satisfies the declared body/exit convention. Keep separate from empirical head-centre passage.
- **Resource allocation:** realised unmet demand under a fixed budget and declared service capacity. Without actual requests/service outcomes, demand is synthetic and conclusions are conditional on its distribution. The planner cannot see realised demand when choosing an allocation.

Age, disability, movement capability and service demand are distinct constructs. Each needs its own annotation or explicit model assumptions.
