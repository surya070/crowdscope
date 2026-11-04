# Calibrated CrowdScope framework — 5 November 2026

Publication update (5 November 2026): the current manuscript incorporates the detection/calibration extension. Statements below about publication status describe the earlier experiment stage; numerical outcomes are unchanged.

## Implemented connection

Recorded trajectories -> four-second movement features -> calibrated working
wheelchair probability -> geometry-aware occupancy/density/motion -> expected
zone composition and working count intervals -> configured service-demand model
-> exact finite-capacity resource allocation.

`src/calibrated_detector.py` loads a saved base/calibrator pair.
`src/crowd_framework.py` streams timestamped positions without receiving labels.
`research/run_framework_csv.py` connects canonical CSV to zones/configuration and
writes JSONL snapshots. `app/framework.html` is the interactive local replay.
The previous synthetic demo and frozen experiments remain unchanged.

## Probability evaluation: excluded people and trials

The already-selected full logistic detector was calibrated with a fixed sigmoid.
Each of 55 outer folds excludes the target wheelchair person and recording trial;
2,268 inner crossed folds produce calibration scores without outer-test access.
Known mapped test-control identities are excluded too. Unknown repeated controls
remain a limitation. All underlying data were previously explored and model
family selection used those exploratory results; this is not pristine external
validation or a preregistration.

- Raw Brier loss: 0.036226; calibrated: 0.021003 (42.0% reduction).
- Raw log loss: 0.123217; calibrated: 0.073115.
- Raw fixed-bin ECE: 0.057163; calibrated: 0.008216.
- Calibrated AP: 0.908361; ROC-AUC: 0.986640.
- At the unchanged 0.5 threshold: precision 84.3%, recall 83.6%.
- Mean calibrated probability: 0.084530; observed positive fraction: 0.077356.

Reliability is improved relative to raw scores but is not established for every
scene/subgroup. A prior-only predictor has low ECE by construction while providing
poor individual discrimination; Brier loss includes both calibration and
resolution. The fixed-bin curve is descriptive with only 55 positive track
observations of seven repeated people. No independent-sample significance or
calibration guarantee is claimed.

## Whole-crowd integration: a separate weaker generalisation task

We trained one coherent leave-one-trial-out model for each recorded trial,
calibrated inside that training set using seven inner trial folds (56 additional
inner folds). People may recur in training and test. This permits a realistic
whole-roster replay without secretly combining participant-specific models into
one deployable model. It must not be described as unseen-person whole-crowd
validation.

The stream processes the original 25Hz records and emits 759 one-second replay
snapshots. All 711 eligible streamed detector outputs match the corresponding
offline held-trial predictions. There are 48 fixed checkpoints and 192 zone
records (187 nonempty), with no geometry-withheld snapshots. Measurements use
walkable polygons clipped to [-6,-1.65,2.4,1.65], including obstacle exclusions.

Nonempty-zone wheelchair-count MAE (people / zone):

- Population prior: 0.601925.
- Raw detector plus prior before eligibility: 0.515605.
- Calibrated detector plus prior: 0.452015.
- Thresholded calibrated labels: 0.572193.

The mean detector coverage is 21.5% of visible occupants across
nonempty checkpoints, because many have not reached the validated x=-1 trigger.
Those people retain a flagged training prior; they are not silently classified.
A broader early/sliding-window recogniser needs its own evaluation.

Working 90% count intervals cover the recorded count in
97.9% of nonempty zone records. This is conservative in this small
sample, not proof of nominal coverage elsewhere. Poisson-binomial intervals
assume independent memberships and do not capture common model/calibration error.

## Conditional resource planning: retained negative result

Using budget6, capacity2 and assumed request rates .1/.4, mean expected unmet
requests evaluated under the label-conditioned hypothetical demand model are:

- Prior-only allocation: 0.085407953.
- Raw detector allocation: 0.085494400.
- Calibrated allocation: 0.085494400.
- Hard-label allocation: 0.084004217.
- Known-class reference: 0.074722639.

Calibration improves probability quality and composition estimates but does not
improve the default allocation result. Raw and calibrated policies have equal
mean loss here; prior-only is marginally better and hard labels also do slightly
better. These small differences are descriptive and depend on the declared
request model. No real requests, service times or actual assistance outcomes
were recorded. Wheelchair membership does not itself establish service need.

## Verification and reproducibility

- All 46 unit tests pass, including temporal gaps, prior fallback, direct use of
  calibrated probabilities, cached estimates and removal of absent occupants.
- Independent audit checks 63 outer folds, 2,324 inner folds, locked hashes,
  arithmetic Brier/log loss, count conservation, bounds and causal timestamps.
- 100 recorded-state Python/JavaScript planning fixtures agree exactly in their
  allocation and to numerical tolerance in expected loss.
- The local UI supports eight trials, time replay, probability-policy switching,
  budgets, capacity and explicit request-rate assumptions.

Model/card, predictions and participant-level replay files are local and ignored
by Git. The final model is refitted on all development data; it must not be used
to report new validation scores on those same records. The demo instead uses
held-trial models. The paper and remote GitHub were not changed in this stage.

## Interpretation

This is an implemented modular trajectory-to-decision framework with an
exploratory calibrated recognition component. It is not a validated general
demographic recogniser, child/age detector, operational staffing system or
evacuation-time predictor. Observed state, inferred membership and hypothetical
demand remain explicitly separate. Bayes is not applied again to the same
movement evidence after the calibrated posterior.

Next research priorities: independent participants and tracking systems; earlier
observation windows; failure/abstention and population-shift handling; spatially
correlated uncertainty; and empirically annotated service needs. Synthetic
augmentation cannot establish a real movement signature imposed by its generator.

Calibration guidance: https://scikit-learn.org/1.7/modules/calibration.html
