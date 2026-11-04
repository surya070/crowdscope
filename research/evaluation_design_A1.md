# Revised evaluation design under A1 — 4 November 2026

Status: **design frozen; execution not released**. This defines a fresh synthetic seed comparison after visible development pilots. It is not a preregistration of earlier work or independent real-world validation.

## Primary comparison

Maintain original primary endpoint: realised unmet requests, probabilistic minus hard posterior, budget six and capacity two. Base case: eighty independently assigned hypothetical profiles across four equal fixed zones, prevalence 0.2, symmetric observation error 0.2, request rates 0.1/0.4. Hard posterior uses the original >0.5 rule with ties assigned zero. The same working model drives all full-distribution planners; their information representations differ.

Report homogeneous and hard-observed comparators prominently: the original hard-posterior policy is weak in this setting and cannot alone establish added value. Mean-demand, known-class and perfect-demand references remain. The last reference is not deployable. The known-class policy does not see realised requests and need not win every finite draw.

## Partitions and scenarios

Use the existing reserved validation seeds 410040–410059 and evaluation seeds 410060–410119. All fourteen development stress definitions are retained without choosing the favourable cells. One row per seed/condition in `research/evaluation_manifest_A1.csv`; ten replicas per row. Layout/cell/replica variants share the seed block and remain in one partition.

The final synthetic benchmark uses fixed zone rosters, not clearance dynamics. Recorded-occupancy integration is a separate exposed-data demonstration with no empirical demand/recognition ground truth; do not pool its outcomes into the synthetic primary estimate. The old 80-agent motion tests remain diagnostic evidence of simulator limitations.

Validation is a software/consistency check only for this fixed-parameter planner. No training or new hyperparameter search is required. Any validation-driven scenario/implementation change must be recorded before evaluation, with a new compatible release lock. Do not change the primary comparison based on validation benefit.

## Randomness and analysis

Keep the exact class/noise/request stream rules from the audited stress runner. Under the base model, classes are sampled per seed then held fixed across ten observation/request replicas. Shared uniforms pair policies and stress variants. Do not let realised requests enter a deployable planning function.

Average replicas within seed before analysis. Report the base paired mean effect and a 95% paired block-bootstrap interval with 10,000 resamples, seed 9041; use all sixty evaluation blocks. Publish each policy's absolute mean, block effects, effect intervals and ties. Secondary cells/comparators are descriptive; no post hoc primary cell selection or multiple unqualified significance claims. Keep exclusions/failures explicit. The budget is computationally fixed, not a power justification.

Include probability Brier scores and input assumptions so calibrated inference can be distinguished from decision value. The Bayes/Poisson-binomial planner optimises an assumed loss by construction; empirical novelty cannot be claimed from an on-model expected-loss advantage alone. Demand/prior misspecification and strong controls matter, but remain synthetic.

## Release gates

1. Audited end-to-end occupancy integration and exact planning/negative-control tests.
2. A runner that consumes this manifest, blocks accidental evaluation access by default and records code/config hashes before execution.
3. Closed or explicitly bounded closest-method literature review. Current searches establish substantial prior art; no unique new algorithm or first framework claim is warranted yet.
4. A data-use statement: raw/derived participant tracks remain local pending source permissions; final benchmark inputs are synthetic.
5. A dated release record before opening evaluation outcomes. This design freeze alone does not authorise a final-result claim.

Next work: finish the targeted nearest-method comparison, implement/audit manifest-based execution on validation seeds, then make the explicit release decision. If the contribution proves to be an established method combination, present an exploratory reproducible benchmark and conditional/negative findings rather than claiming an invented optimisation algorithm.
