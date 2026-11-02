# Label-quality sensitivity — 2 November 2026

Deployment stress test of the primary one-second-history mobility-informed model. No simulator, classifier or newly selected predictor was used.

## Design

Reused the original four outer width folds and selected model settings. Reconstructed clean-trained models and reproduced all 33 original M predictions within 1e-8 s before perturbing labels. Kept all 19 H features, cohorts, targets and training labels unchanged. Cases/seeds were saved in `lock.json` before this run.

Three cases independently mark each trial/track label unavailable with probabilities .25/.50/.75. Missing labels contribute no positive wheelchair membership; the full cohort remains the denominator. The existing model has no missingness indicator and receives no uncertainty-aware retraining. This is a specific zero-fill fallback, not principled missing-data inference. Missing non-wheelchair labels have no numerical effect under this coding.

Two additional cases flip each binary person label with probabilities .10/.25. This affects both classes and creates false positives among pedestrians without wheelchair labels. Masks are deterministic by seed/trial/track and shared across a trial's three checkpoints. Twenty seeds (101–120) are used for each case. They represent artificial perturbations, not 20 independent human experiments. Repeat identities across trials are not jointly masked, so this is a within-record stress model rather than persistent-person sensor failure.

## Results

Reference trial-weighted MAE: motion-only H 4.278 s; clean-label M 2.591 s.

- 25% label-unavailability probability: mean MAE 2.517 s; seed range 2.226–2.939 s. All 20 seeds below H.
- 50% unavailability: 2.674 s; range 2.322–3.649 s. All 20 below H.
- 75% unavailability: 3.782 s; range 2.570–5.463 s. Fifteen of 20 below H.
- 10% binary-flip probability: 8.148 s; range 7.628–8.730 s. None below H.
- 25% binary-flip probability: 11.437 s; range 10.550–12.094 s. None below H.

The slight average improvement in the first missing-label case is not evidence that missing information helps generally. It is a finite-sample result from perturbing a particular fitted model. Do not select that setting after observing results or recommend deliberately hiding labels.

## Interpretation

The initial benefit is conditional on label reliability. Sparse positive membership is especially vulnerable to false positives: symmetric binary flips can introduce many spurious wheelchair labels, including in reference crowds with no wheelchair users. These shifted inputs are outside aspects of the clean training distribution. This study measures that vulnerability, not the accuracy of any real detector.

No automatic inference system has been evaluated. The artificial error mechanism need not match a real classifier; rates are per-label probabilities, not exact realised percentages, and equal error rates do not imply equal class precision/recall. Seed ranges are not population confidence intervals. The shared seven wheelchair participants, eleven trials, differing crowd compositions and width confounding remain limitations.

The experiment suggests preserving an unknown state and testing high-precision information or uncertainty-aware training in future work. It does not establish a safe threshold, fix the current model, or justify deployment. Any further method adaptation after these results must be labelled development work and evaluated without presenting this set as a fresh test.

## Verification and records

Saved 3,300 perturbed predictions (33 queries × five cases × 20 seeds). Independent metric reconstruction checks exact target matches, unique query/case/seed keys, and complete 33-query coverage in every case/seed. History features were asserted unchanged. Clean prediction reproduction is a fitting-consistency check; it does not validate source participant labels.

Files: `lock.json`, `predictions.csv`, `checks.json`, `summary.csv`, `seed_metrics.csv`, `audit.json`. The original clean experiment remains unchanged.

Conclusion: verified mobility labels improve the aggregate forecast in the first exploratory experiment, but mistaken labels can make forecasts substantially worse than using movement history alone. Both findings belong in the paper.
