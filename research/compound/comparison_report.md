# Compact comparison completed and audited

29 October 2026. Saved study: output/compound/comparison_001. A separate eight-page course manuscript is in output/pdf/compound_simulation_paper.pdf; editable source: paper/compound/manuscript.md. Earlier manuscripts and failed studies remain intact.

## Actual finding

On 96 held-out main runs (24 matched base blocks in two fixed corridor configurations), aggregate-motion MAE was 2.659911 s, mobility-aware MAE was 1.222307 s and mobility-plus-relationship MAE was 2.396687 s. The known mobility roster and queue-aware features reduced MAE by 54.047% relative to aggregate motion. The primary M-minus-F contrast was -1.174380 s, with conditional descriptive interval [-1.486181,-0.882147] s. Full relationships increased error relative to mobility by 96.079% in this evaluation. The hypothesised positive incremental relationship benefit was not supported.

This does not show that real relationships are unimportant. The study is an uncalibrated synthetic single-lane generator with exact nominal speeds supplied to the predictor. Detailed relationship features can overfit or generalise poorly; this experiment does not establish the mechanism of the observed disadvantage. No learner or feature was changed after the test findings.

## Coverage and verification

All 240 frozen scenarios completed: 192 main, 32 support-gain stress and 16 finer-step counterparts. All 720 forecast queries were retained. The prospective development gate passed all 16 paired checks (32 trajectories), maximum clearance difference 0.08 s. Sixteen identical-step main training pilots were reused with logged source integrity, not treated as independent samples. The maximum matched production refinement difference was 0.16 s, with matching completion status. Twelve movement/study software tests passed before the batch.

The independent saved-result audit verified 240 trajectory hashes and occupant accounting over 31,143 saved frames, checked public feature/partition integrity and independently recomputed all 32 model/evaluation metric groups using standard-library aggregation. A separate fresh-process reproduction at the saved validation-selected settings matched 3,168 learned predictions within 6.84e-12 s; it did not retune hyperparameters. Both are internal same-runtime checks, not independent empirical validation.

## All planned tests retained

Full relationship MAE remained worse than M on the same-corridor test (1.615 versus 1.040 s), gain-stress subset (1.968 versus 1.062 s) and finer-step subset (1.584 versus 0.781 s). These subsets have different compositions; their raw errors cannot isolate a causal resolution or stress effect.

On the main held-out test, count-only MAE was 1.235 s, no-family 1.242 s and no-assistance 1.233 s. None established an advantage over M's 1.222 s. Fixed-model deletion of one supplied link per type yielded MAE 2.470 s; rewiring one per type gave 2.227 s, still worse than M. Realised corruption counts are saved; no refitting or changes to trajectories occurred.

Post-result descriptive movement checks found identical family-only/independent recorded clearance in 40/48 main blocks and identical assistance-only/independent clearance in 19/48. A slower occupant elsewhere can dominate the last exit in this generator. These observations do not replace the primary predictive contrast or establish a general human behavioural effect.

## Paper and boundaries

The paper is framed as an exploratory negative-result simulation study, with the intended mobility/relationship research question retained. It includes the research question and hypotheses, prospectively frozen protocol, verification, matched design, fitting/validation separation, complete results, uncertainty, discussion, limitations, declarations and six references. The final PDF was rendered and all eight pages visually checked; figure/table detail pages were inspected separately.

The numerical/citation checks compare manuscript tables against audited outputs and verify all references are cited. Source/config/manifest/trajectory hashes and the original empirical frozen inputs remain intact. Scientific figures are exported as PNG/SVG. No public repository, independent real-world validation, course-rubric acceptance or indexed-publication readiness is claimed. Author affiliations/contributions/conflicts and all-author approval remain pending external submission checks. Course-specific AI disclosure/review requirements must be handled by the authors.

This completes the requested compact comparison and supplies a course-paper draft for review. It does not turn a negative finding into a positive one or establish a novel validated operational system.
