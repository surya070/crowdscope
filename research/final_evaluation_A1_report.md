# Fixed final synthetic evaluation A1 — 4 November 2026

## Execution and audit

The user requested continuation after validation. A dated release record bound the runner, probability/planning code, configuration, manifest and analysis source before scenario generation. The first invocation was rejected before generating any scenario because Windows native path keys differed from slash-separated release keys. The original release record was preserved, and equivalent path aliases were added without changing code, models, cases, seeds or analysis. See `research/evaluation_release_A1.json` and its pre-fix copy.

One outcome-generating execution followed: sixty reserved seed blocks (410060–410119), fourteen fixed conditions, ten paired replicas per block and seven policies. This yields 8,400 scenario replicas and **58,800 policy records**. There are sixty independent blocks, not 8,400 independent crowds; cells and replicas are paired/dependent.

Every saved realised loss, resource budget, grouping, perfect-demand lower bound and the three negative-control identities passed `research/audit_planning_evaluation.py`. All 42 project tests pass. The guard test now handles the authorised-release lifecycle while still refusing evaluation by default; it was updated after release, without changing prediction or analysis code. No model or scenario was revised after evaluation outcomes.

## Primary result

Base scenario mean unmet requests:

- Probabilistic: **3.176667**.
- Hard posterior and homogeneous population prior: **3.431667** each.
- Hard observed: **3.175000**.
- Mean-demand ablation: **3.176667**.
- Known-class information: **2.961667**.
- Perfect realised-demand reference: **1.963333**, non-deployable.

The predeclared primary difference (probabilistic minus hard posterior) is **−0.255 requests per scenario**, with paired seed-block percentile-bootstrap 95% interval **[−0.390, −0.126667]**, using 10,000 resamples and seed 9041. Thirty-five blocks improve, seven tie and eighteen worsen. The hard-posterior policy labels every primary observation negative under the original >0.5/tie-zero convention; its weakness must be stated beside this result.

Against the stronger hard-observed policy, the difference is **+0.001667**, interval **[0, 0.005]**. Allocations match in **599/600 replicas**; 59 block effects tie and one favours hard observed. The probabilistic and mean-demand policies choose identical allocations in all 600 base replicas. Therefore the primary gain does **not** establish added value from probability propagation beyond hard observed labels or distribution-aware planning beyond mean-only planning in the base setting.

Do not describe this as an evacuation-time reduction, real staffing accuracy or real mobility recognition result. No practically meaningful equivalence margin was prespecified; the exact allocation agreement and effect sizes are more informative than claiming formal equivalence.

## Secondary conditions

All fourteen cells remain in `output/planning_evaluation_A1/analysis.json` and the original raw results. Relative to hard observed:

- Unequal zones: −0.065 requests, descriptive interval [−0.100, −0.030]; allocations agree 79% of the time.
- High demand contrast: −0.045, descriptive interval [−0.073333, −0.016667]; agreement about 90.8%.
- More resources: −0.006667, descriptive interval [−0.015, 0]; agreement about 99.3%.
- Uninformative observations: +0.011667, descriptive interval [−0.105, 0.130]; probabilities correctly reduce to the prior, whereas hard observations introduce noise.
- The remaining cells predominantly tie or differ only trivially. Full results include the primary base cell and probability-distortion cells where hard observed is slightly better.

These are prespecified **secondary descriptive comparisons**, not multiplicity-adjusted confirmatory findings. Do not choose a favourable secondary cell as a replacement primary condition. The development low-prior harm did not reproduce as a mean disadvantage in this final sample; development patterns are not guaranteed population effects.

## Supported interpretation

Mobility/service-profile metadata can help relative to an uninformative population policy under the assumed model. Propagating probabilities often does not change the resource decision beyond a hard-observed policy. Their incremental value depends on zone occupancy, capacity and the relationship between class and request probability. Accurate/calibrated state estimates and improved decisions are different endpoints.

The benchmark uses fixed zone rosters and artificial metadata/requests, with conditional independence and known working channel assumptions. Recorded SiME data demonstrate occupancy/movement integration only. JuPedSim tests remain limited exploratory evidence with unresolved generic-clearance failures. No actual child/wheelchair recogniser or assistance-demand validation was performed.

## Next paper scope

A suitable candidate title is **Conditional Value of Mobility Uncertainty in Zone-Based Crowd Resource Planning: An Exploratory Benchmark**. Present a transparent framework and conditional/negative findings using established mathematical tools; do not claim an invented Bayes rule or a verified first framework. Include the 42-checkpoint recorded-data integration and simulator limitations as separate evidence.

Next stage: draft the eight-page IEEE-style course manuscript, with the teacher's seven major sections, all primary and stronger-control results, limitations, data/code availability and reproducibility. A demonstration should distinguish observed density, hypothetical profiles and planning assumptions on screen. Course acceptance or indexed publication remains unestablished.
