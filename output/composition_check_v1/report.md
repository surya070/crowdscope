# Composition and feature-engineering check

2 November 2026. Post-result exploratory follow-up. Fixed one-second histories, the same 11 trials/33 queries and outer/inner width folds. Variant definitions and tuning grid were written to `lock.json` before this follow-up fitting. No new independent test data, simulator, participant recruitment or classifier.

## Comparisons and results

Each variant uses the same original 19 H features. Additional information is varied; models/settings are selected through the same inner folds.

- H: 4.278 s trial-weighted MAE.
- H plus wheelchair-presence indicator: 3.190 s.
- H plus count/fraction/presence: 3.231 s.
- H plus labelled wheelchair-group observed mean speed and maximum distance: 2.443 s.
- Original full M (all five additions): 2.591 s.
- H plus five anonymous movement summaries: 4.650 s.
- H plus anonymous summaries and all five M additions: 3.054 s.

Anonymous summaries are rearmost-person observed speed, minimum observed person speed, and maximum distance/speed estimates using denominator floors .1/.2/.3 m/s. They use each person's one-second displacement and do not require wheelchair membership. These are candidate stronger baselines, but their measured performance here is worse; do not describe them as successfully stronger models. No feature selection was tuned after observing these results.

The labelled-group-only variant has the lowest observed error in this follow-up, but was introduced after the initial experiment. It does not replace the prespecified initial headline result, and no final model is selected by these evaluation errors.

## What this says about composition

Presence alone captures a substantial part of the original aggregate gain. Its improvement over H is about 1.089 s, compared to the original full-M improvement of 1.687 s. That is a descriptive comparison of predictive gains, not a causal decomposition or a statement that 65% of human delay is caused by composition.

Labelled group motion improves beyond presence/count summaries in this aggregate. However, group speed/distance use zero defaults when the group is absent, so they also encode presence. This does not isolate the effect of knowing a specific person's mobility identity. Wheelchair and reference populations have different crowd sizes, and the same seven wheelchair users repeat across widths.

Population breakdown for models trained on mixed trial types:

- Wheelchair trials (seven): H 4.007 s, full M 2.921 s, presence 2.905 s, group-motion variant 2.457 s.
- Reference trials (four): H 4.753 s, full M 2.015 s, presence 3.688 s, group-motion variant 2.419 s.

These are subgroup summaries of cross-validated predictions from the mixed-population model, not separate within-population training experiments. Improvement in reference trials reinforces that the learned distinction between crowd conditions may matter. It does not establish that wheelchair-specific personal parameters explain the full gain.

## Checks

All 33 anonymous-feature extractions matched after future frames were removed. Original H and full-M predictions reproduced exactly (maximum saved prediction difference zero). The independent audit verifies all 231 unique predictions and their source targets, with 33 queries per variant. Per-trial metrics and full inner-score/selection traces are retained. Only model-input summaries are tested; no source label reannotation was performed.

## Interpretation for the paper

Defensible statement: *Within this small shared-population dataset, verified mobility-conditioned summaries improved exploratory passage forecasts, with a substantial contribution from identifying crowd composition. The benefit was inconsistent across width configurations and vulnerable to incorrect labels.*

Do not claim a general causal mobility effect, generalizable wheelchair recognition, first-ever mobility-aware forecasting, or a validated evacuation safety tool. The current data cannot cleanly separate person-level mobility, population composition, cohort identity and geometry. Additional independent populations or controlled composition data would be needed to address that limitation.

The study now has a positive aggregate result, explicit generalization limits and a demonstrated false-label failure. Further tuning on this same data will not make it independent evidence. Preserve the original results and use these analyses as explanatory development follow-ups.

Next stage: consolidate protocol, initial results and both robustness reports into the manuscript evidence outline. Keep inaccessible closest-paper methods and broader novelty verification listed as outstanding before submission claims.
