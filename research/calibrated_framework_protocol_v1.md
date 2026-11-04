# Calibrated detector and connected framework — 5 November 2026

Exploratory extension; underlying data and family selection were already exposed.
The selected base model is the fixed full logistic detector (C=.2, balanced
classes, training-only standardisation). No new family or threshold search.

## Calibration evaluation

Primary: retain the 55 crossed trial/wheelchair-person outer folds. Within each
outer training set, generate inner crossed trial/person predictions, including
the known-identity exclusions used in the detector study. No outer test record,
person or trial can fit either the base model or calibrator. Fit a fixed sigmoid
logistic calibrator (C=1, natural class weighting) to inner held-out decision
scores. Reweight repeated control predictions to preserve cohort prevalence.
Refit the base on outer training only and evaluate the calibrated outer score.

Report Brier loss, log loss, AP, ROC-AUC, fixed-bin reliability, prevalence versus
mean probability, and preset-threshold precision/recall. Smaller Brier loss is
not alone proof of calibration; show reliability too. Unknown repeat controls
and seven wheelchair people still limit inference. No iid confidence claims.

For deployment prototype, refit base on all development data and fit its sigmoid
from the original crossed out-of-fold decision scores. This is an all-data refit,
not an untouched test model. Preserve the uncalibrated candidate.

## Coherent whole-crowd evaluation

A single deployable model cannot exclude all seven wheelchair identities while
learning wheelchair motion from these same seven. Therefore evaluate full crowd
replays with a separate coherent leave-one-trial-out model per trial, calibrated
on inner leave-one-trial-out scores. These trials contain previously seen people.
Do not merge these results with the stronger individual person/trial evaluation.

Use recorded 25Hz trajectories, actual walkable geometry clipped to the existing
ROI [-6,-1.65,2.4,1.65] and x cuts [-6,-3,-1,0,2.4]. Evaluate snapshots at
10,20,30,40,50,60 seconds. Detector runs only on the first forward x=-1 crossing,
using the last four seconds. Cache that probability as uncertain stable profile
information. Before that event or with inadequate history retain the training
prior with an explicit flag. Missing tracks never become current occupants.

Report occupancy conservation, probability bounds, detector coverage, expected
wheelchair-count MAE, signed bias and working 90% count-interval coverage. Working
Poisson-binomial intervals assume independent memberships; repeated model errors
can violate this. Comparators: supplied training prior, raw detector, calibrated
detector and calibrated hard threshold. Do not use real labels for inference.

Resource module: retain the exact allocator with budget6, capacity2 and assumed
request rates .1/.4. Compare allocations against the expected loss computed from
recorded class labels under this hypothetical demand model. This is conditional
service modelling, not observed human assistance outcomes. Keep true labels out
of inference and optimise only input probabilities. No new simulator required.

## Deliverables and boundaries

Reusable ingestion/inference/state/composition/planning API, CLI, input format,
saved calibrated model and model card, local recorded-data replay demo, aggregate
report and scientific calibration plot. Human trajectories, derived per-person
scores and local replay data remain ignored by Git. Keep the existing synthetic
demo and frozen planning results intact. The framework remains a modular research
prototype, not a universally validated demographic recogniser or safety system.
