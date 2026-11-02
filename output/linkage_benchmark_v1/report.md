# Frozen synthetic linkage comparison — results

2 November 2026. **The assignment-specific forecasting hypothesis is unsupported in this benchmark.** Correct assistance links did not improve validation-selected forecasts beyond mobility/history, link counts or shuffled assignments. This does not establish that assistance relationships never matter.

## Primary zero-gain result

Tested eight held-out coordinated runs (24 correlated queries) at gain1.0. Equal-run MAE:

- M, mobility and observed history: **0.198372 s**.
- F-counts, adding number of active links: **0.198372 s**.
- F-correct, adding correct link-conditioned summaries: **0.207677 s**.
- F-shuffled, wrong helper assignments: **0.182173 s**.

Primary improvement defined as MAE(M)−MAE(F-correct) is **−0.009305 s**: correct-link error is slightly higher. No population significance or real-world equivalence claim is made from this small set. The shuffled variant's lower error also fails the protocol's assignment-specific interpretation check. Do not select it as a desirable wrong-link system on these evaluation results.

Ridge alpha.1 was validation-selected for all four primary conditions. Matched boosting M/F-correct error is.32945/.31926s, a small improvement for that family; correct links still do not beat shuffled boosting (.31334s). This family-level result does not replace the prespecified validation-selected comparison.

## Assumed-gain secondary stratum

At hypothetical gain1.15, selected M/F-counts/F-correct/F-shuffled MAE is **.200111/.200111/.262678/.177093s**. M/counts/shuffled select ridge; correct links select boosting on validation. Matched-family results also fail to establish a correct-link advantage. No settings were retuned after evaluation.

## Missing-link stress

The fixed selected F-correct model receives50%-probability edge removal over20 deterministic masks, without retraining:

- Gain1.0: mean MAE.318314s, seed range.199758–.437466s.
- Gain1.15: mean.268189s, range.229518–.299180s.

These ranges are artificial corruption variability, not population confidence intervals or measured graph-detector performance. Zero-edge defaults can shift feature distributions outside the clean training regime.

## Baselines and controls

At gain1.0 the training-median and simple travel-time references give2.41854/1.01785s MAE; at1.15,2.35458/.77374s. Stronger mobility/history predictors are already highly accurate for this simple generator. Exact nominal mobility is supplied to M as a synthetic oracle; that is more information than an uncontrolled camera system usually has.

All coordinated query graphs retain two active links, including shuffled graphs. Consequently counts are constant in these strata and add essentially no information. This is a frozen-design limitation, not evidence that counts never matter. Both true and wrong-link summaries encode geometric relationships; a wrong-link feature can act as another spatial descriptor. Its performance here is not proof that wrong physical assistance assignments would improve evacuation.

Matched movement outcomes across all48 blocks: coordinated minus independent clearance averages+.27896s at zero gain (range−.255 to+1.315s). At assumed gain1.15 it averages−1.77083s (range−2.755 to−.905s). These are descriptive generator outcomes, not clinical or real assistance-effect evidence. The latter explicitly contains a programmed speed benefit. Independent gain variants have identical control behaviour and must not be counted as independent evidence.

## Methods and admission

48 matched blocks over four known layouts;192 main runs and48 preassigned finer replays. All movement/admission checks passed; largest coarse/fine clearance difference.005s. One-second history, queries2/5/8s, whole synthetic roster and last nominal-circle crossing target. This differs from the empirical SiME observed-subset/head-crossing target.

Per gain, coordinated training/validation/evaluation sets contain32/8/8 runs. All matched variants share block splits. Candidate grid and tie rules were frozen before outcomes; selection uses validation only, with training-only fitting/scaling and no evaluation-driven refit. Both correct and shuffled graph conditions use the same M features. Initial information-condition results are prospective relative to this generator's new samples, but simulator design was adapted using prior development fixtures.

## Verification

Saved1,632 predictions. Independent saved-output audit checks unique keys, evaluation-only run membership, exact target reconstruction from generated crossings and equal-run metric reconstruction across68 groups. Movement/source hashes and fine checks were verified separately.1,152 correct/shuffled prefix-removal feature checks passed; M features were unchanged. Full selection traces and all failure-free generated runs remain saved. Metric reconstruction is not an independent reimplementation of the complete learning system.

## What belongs in the paper

Report two distinct evidence streams:

1. Measured SiME: supplied mobility information improves an exploratory aggregate forecast but is sensitive to label errors and crowd-condition confounding.
2. Synthetic escort extension: movement is numerically verified in the specified cases, but correct link-conditioned summaries show no consistent assignment-specific forecasting gain over a strong mobility/history baseline.

Do not pool their MAEs, claim that low synthetic error validates human evacuation times, or present this as physical wheelchair pushing. The circular agent model has no chair contact/force mechanics or empirical helper calibration. Small known layouts, two pairs, supplied nominal speeds, early queries, fixed link count and limited held-out seeds restrict external validity. This tests selected summary features and learners, not every possible relationship-aware method.

## Decision

Preserve the negative finding. Do not change targets, weaken M, or tune a simulator until correct links win. A publishable extension would need a justified new mechanism/data question and a fresh protocol, not post-hoc rescue of this result. The current material can support a narrowly framed exploratory paper combining measured mobility-information value with synthetic relationship-information limits, subject to the unresolved prior-art and submission-readiness checks.

Next stage: update the paper evidence outline and manuscript claims with this result. No automatic next experiment is required.
