# A1 validation and evaluation readiness — 4 November 2026

## Runner and partition checks

`research/run_planning_manifest.py` defaults to validation, reads the frozen A1 configuration/manifest, verifies design hashes and requires exact seed/case/replica membership. Final evaluation requires both an explicit flag and an active hash-matched release record; none exists. No evaluation seeds were generated or inspected.

Twenty reserved validation blocks, fourteen cases, ten replicas, seven policies: 2,800 scenario replicas and 19,600 policy records. Code/config/manifest hashes were saved before execution in `output/planning_validation_A1/lock.json`. No planner parameters, cases or primary comparator were changed based on these results.

`research/audit_planning_validation.py` checks feasible budgets, grouping, demands, every realised loss, perfect-demand lower bounds and all three allocation-identity controls. All pass. Guard tests check default refusal, refusal without a release record even with the flag, and the exact validation schedule. These are pre-release tests; a future authorised release changes their expected state and needs a separately recorded test version.

## Validation interpretation

Base mean unmet requests: probabilistic/hard-observed/mean-demand 3.135, hard-posterior/population-only 3.330, known-class 3.060. This is consistent with a weak-comparator gain and no base advantage over hard observed. Do not select a different primary condition based on validation.

The equal-demand, uninformative-channel and perfect-observation identities pass exactly. Slight finite-sample differences against noisy policies in uninformative conditions are sampling variation, not evidence that random observations are informative. Replicas/cells share blocks and cannot be counted as independent experiments.

## Readiness decision

The software/validation gate passes. The immediate nearest-method comparison is explicitly bounded in `research/literature/closest_method_comparison_A1.md`: this is a reproducible exploratory benchmark of established methods, not a verified new optimisation algorithm or recognition model. Human tracks and derived person-level integration files remain local; final benchmark inputs are synthetic.

The final design remains unchanged and the release record has **not** been created. Next step: make a dated release that binds runner, core probability/planning code, analysis configuration and manifest, then run the fixed final comparison once and report grouped uncertainty and all controls. Preserve any failure rather than rerunning for a favourable result.
