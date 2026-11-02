# Protocol draft v0 — value of mobility information in passage forecasting

Date: 2 November 2026. Status: **development draft, not frozen or preregistered**. Six development-only raw trials have been acquired and audited. A hashed causal feature/split bundle is prepared; no learner fitted. Changes remain permitted with an amendment record before a modelling lock.

## Research objective

Test whether explicit mobility information improves remaining-passage forecasts beyond the same observed motion history. The contribution is an information-value comparison, subject to the unfinished prior-art checks. A JuPedSim implementation or a wheelchair detector alone is not the novelty claim.

The original complete-crowd clearance question remains the eventual simulation target. The real-data pilot below has a narrower observed-cohort target because the saved SiME files do not always show the complete original crowd at once. Report these as distinct experiments; success on one does not validate the other.

### Prior-art and measurement constraints (2 November follow-up)

See `literature/focused_method_check.md`. Deng 2022 already incorporates individual characteristics and congestion, and RSET surrogate work already includes speed/count/spacing. Our proposed contribution is restricted to the incremental value of mobility information under fixed causal histories and uncertain labels, subject to full-text verification. Do not claim first mobility-aware forecasting.

SiME's published Voronoi/Delaunay and steady-state entry-plane measurements differ from our descriptive summaries. Matching those definitions is required for an exact replication; downstream cohort prediction is a separately defined target. No aggregate resemblance validates a wheelchair controller. Closed-paper input/ablation/split checks and SiME subset mapping remain open before freeze.

## A. Empirical pilot: observed-cohort passage

At recording times t = 10, 20 and 30 seconds, define C(t) as tracks that have an observation at t, are upstream of x=2.4 m, and have a continuous two-second history ending at t. Cohort selection uses past/current observations only. Use this identical C(t) for all history lengths. Candidate input histories are 0.4 s, 1 s and 2 s, all ending at t. Use backward-only differences; the centred speed smoothing used in Stage 3 is not permitted here.

Outcome: Y(t) = max downstream crossing time among C(t), minus t. Use first forward x=2.4 m head-centre crossings interpolated between adjacent frames. This is time until the currently observed eligible cohort passes, excluding later arrivals. Do not label it complete-building evacuation, full-body clearance or clearance of the entire initial crowd. Record excluded/short-history counts for each checkpoint.

If C(t) is empty, mark the query ineligible. If any member has no recorded downstream crossing, mark the cohort target incomplete; do not delete that person and compute a shorter target. Report missing outcome counts by trial and mobility group. Exclude such queries from complete-outcome MAE with an explicit coverage statement and censoring sensitivity; never imply that exclusion establishes actual clearance. No administrative time cap will be silently converted into an exit.

Trial 1307 remains outside primary pilot evaluation until its 83-versus-85 cohort discrepancy is reconciled. Trial 507 may produce incomplete cohort queries and remains a development diagnostic until this rule is implemented and audited. These rules were chosen after inspecting these trials, so their results remain exploratory.

## Inputs and information conditions

H: observed history and geometry. Candidate summaries: eligible count, x/y distributions, exit-distance quantiles, per-person speed quantiles and variability, backward acceleration, stopped fraction, visible-neighbour spacing, past crossing counts, corridor/bottleneck width and elapsed recording time. Visibility masks must be explicit. No stable person ID, run prefix or trial number enters a learner.

M: H plus verified wheelchair membership counts/fraction and interactions between membership and observed speed/distance. This is supplied-label information, not a trained recognition system. Neither exact nominal speed nor a universal category-to-speed constant is supplied. Restrict this comparison to trials with sufficiently complete documented class mapping; an unlabelled track is not automatically non-disabled. A valid training set must include enough independent labelled conditions to identify the effect.

U: H plus deliberately degraded supplied mobility labels. Candidate sensitivity conditions: independently mask 25%, 50% or 75% of labels, with an explicit unknown indicator; separately flip 10% or 25% of labels as a symmetric artificial stress test. Use a fixed 20-seed list shared across methods. These are controlled hypothetical errors, not measured detector performance. Select none as the best post-test condition. Retain the unknown denominator and missingness indicator.

Relationship and age inputs are excluded from this initial pilot because verified individual mappings are unavailable. Add them only through a dated protocol amendment and a new data/novelty check. No family labels are assumed from proximity.

## Hypotheses and estimands

H1: at the primary one-second history, M has lower trial-weighted held-out MAE than H. Null: expected improvement is zero or negative. Define improvement as MAE(H) minus MAE(M).

H2, exploratory: M's incremental value is larger with 0.4 s histories than with 2 s histories. This is an interaction hypothesis, not proof that short histories must benefit.

H3, sensitivity: quantify degradation under U relative to M and H. Do not interpret artificial errors as an empirical detector result.

Practical relevance threshold remains unresolved. Do not invent an operational safety tolerance. Report absolute seconds and relative improvement; obtain a justified task/venue threshold before any confirmatory interpretation.

## Models, evaluation and leakage controls

Baselines: a training-only constant predictor and a causal distance/speed travel-time estimate with a development-selected denominator floor; regularized regression; gradient-boosted trees; and a history-capable comparator if independent sample size supports it. The latter may be a compact history-summary regression rather than a neural network. No deep model is justified by counting correlated frames as samples.

Compare H/M using the same learners, histories, query cohorts and tuning budgets. Also report validation-selected learners for each condition. All scaling, imputation, feature selection and parameter choice belong inside training folds.

Candidate budget: ridge penalties [0.1,1,10,100]; boosting learning rates [0.03,0.1], depths [2,3], iteration counts [50,100], with fixed seeds. These settings may be revised on development feasibility before freeze, never using reserved outcomes.

Split unit is a complete trial; all its checkpoints, histories and noise variants stay together. The selected exploratory scope is within-cohort transfer across width configurations: the same wheelchair participants occur across folds. A participant-independent comparison is unavailable and is not claimed. All 14 audited trials are exposed development data; 11 enter the primary feature bundle. Repeated queries do not increase the independent trial count.

Primary metric: average absolute error within a trial, then average across eligible trials. Pair H/M errors at identical queries. Secondary: signed error, underestimation, worst trial error, and coverage. Report per-trial results and denominators. Conditional resampling intervals over a handful of trials are descriptive; they do not account for unknown cohort overlap or population uncertainty. No broad significance claim from two wheelchair trials.

No confirmatory split is assigned. `data/forecast_bundle/manifest.json` defines four outer leave-width-out development folds with inner leave-width-out model selection. Each width holds both available reference and wheelchair trials together. The bundle has 33 queries/99 history rows, 19 H features and five M additions. Because all outcomes were inspected and wheelchair people repeat, keep the entire study exploratory. Corridor width changes with bottleneck width; this does not isolate a causal doorway-width effect.

## B. JuPedSim study after empirical feasibility

Use an established pinned movement engine with documented calibration and verification. Simulate a known complete cohort, so the target can be the last full-footprint exit minus t. Keep that event distinct from head crossings in the empirical pilot.

First compare common versus mobility-specific parameters against development speed/spacing/headway observations; numerical checks must precede large generation. Collision-free speed and AVM are candidate engines, not assumed validated wheelchair models. Body footprint and assisted motion need explicit support and checks.

Freeze geometries, crowd compositions, seeds and parameters before test runs. Compare H/M under the same motion histories and include capability uncertainty. Relationship extensions require new evidence and a separate verification gate. Report simulator dependence and empirical transfer limitations; do not tune interactions until M or relationship features win.

## Conditions required before protocol freeze

1. Extract available query cohorts and report target eligibility without fitting models.
2. Reconcile 1307 and characterize 507 censoring; document any exclusions.
3. Verify additional wheelchair/free-motion trial metadata, class completeness, licensing and exposure; assign roles before opening new outcomes.
4. Finish the closest-paper feature/ablation checks or explicitly restrict the paper's novelty wording.
5. Establish a usable grouped evaluation design and justify practical relevance criteria; otherwise retain an exploratory scope.
6. Write the final feature list, dependency versions, noise seeds, split manifest and hashes; archive the frozen protocol before fitting.

Next permitted development task after stage review: build the causal observed-cohort query audit and verify additional metadata. This draft does not constitute a passed simulator-rebuild gate.
