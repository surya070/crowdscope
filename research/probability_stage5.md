# Stage 5 probability foundation — 4 November 2026

Implemented `src/mobility_probability.py`: symmetric-channel Bayes posterior, Poisson-binomial class-count distribution, expected counts and equal-tail discrete intervals, plus a metadata-to-active-occupant join. Missing metadata retains the working prior and receives a flag. Extra metadata cannot create occupants. Invalid probabilities and impossible observations raise errors. The module takes no evaluation ground-truth labels.

No recogniser or probability-calibration model was trained. We are following protocol path C: explicitly uncertain supplied metadata. These probabilities describe scenario mobility-profile membership, not diagnosed disability or age. The independence assumption behind count intervals is explicit and may fail after crowd selection or shared observation errors.

## Verification

All 25 tests pass: the 15 state tests plus ten probability tests. New checks include analytical posterior values, perfect/uninformative channels, impossible observations, exact/brute-force count distributions, empty groups, probability validation, missing/extra metadata and interval probability mass.

`python research/check_probability_channel.py` exhaustively enumerates 256 class/noise assignments for four artificial people in two fixed zones. Results: `output/probability_fixture_v1/results.json`. No reserved benchmark seeds are used, no crowd dynamics are present and this is not an evaluation of the full research hypothesis.

With both true and assumed prevalence 0.2 and error 0.2:

- Probabilistic Brier score is 0.117647, versus 0.16 prior-only and 0.20 for either hard-label policy. Exact conditional calibration is checked, not inferred from a noisy sample.
- Zone count MAE is 0.376471 for probabilities, versus 0.3744 for hard observed labels and 0.40 for hard posterior labels. Thus the fixture does **not** establish superiority on every endpoint.
- Nominal 90% discrete count intervals cover 98.56% under this small matched fixture. Discreteness makes them conservative; this does not guarantee real-crowd coverage.

When true prevalence is 0.5 but the working prior remains 0.2, probabilistic Brier score worsens to 0.214965, compared with 0.20 for hard observed labels. Reliability diagnostics explicitly show miscalibration. Do not hide this shift result or use evaluation labels to repair priors.

At the primary illustrative settings, a positive observation has posterior 0.5; the frozen hard-posterior tie convention assigns it zero. Consequently that comparator predicts no positive members in this fixture. Retain the separately prespecified hard-observed comparator to make this weakness visible, and do not present a gain over hard posterior alone as a general result.

## Decision and next stage

**Pass for the declared-channel probability/composition foundation only.** No empirical recognition or crowd-planning benefit has been validated. Stage 6 can now build the JuPedSim development scenarios, source adapters and numerical fixtures. Final evaluation stays blocked until those checks and the remaining protocol gates pass. Resource optimisation remains Stage 7.
