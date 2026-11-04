# Exploratory SiME motion detector protocol — 5 November 2026

Status: specified before fitting this detector benchmark. The underlying data
and lateral-motion signal were already examined: this is exploratory development,
not a preregistration or untouched external validation.

## Target and cohort

Recognise documented wheelchair-associated motion versus the conditional
non-wheelchair roster complement in trials 501–508 only. Each run declares seven
participants with disabilities and maps all seven wheelchair IDs 34–40. Require
unique mappings, matching metadata/observed counts and continuous tracks. Do not
infer age, diagnosis, independence or service demand. Seven wheelchair people are
repeated, and many controls lack persistent identities.

## Observation and inputs

One four-second window per track, ending on the first observed forward crossing
of x=-1 metre. This is an online-detectable trigger, not a full-future-trajectory
summary. Require 101 consecutive frames at 25 Hz and a start point below x=-1.
Report all exclusions. Models receive past-window displacement/velocity summaries
or the 100 velocity vectors only. No Z/height, absolute position, identifier,
frame number, trial number or passage time is a predictor.

Tabular features include speed/lateral summaries at several temporal scales,
stopping, variability, directional changes, acceleration and lateral spectral
power. These are candidate movement features, not verified biomechanical causes.
Coordinates are fixed to this passage orientation; arbitrary new scenes require
orientation alignment and validation.

## Splits

56 crossed holdouts: every combination of one excluded trial and one excluded
wheelchair participant. Train on the other seven trials excluding that participant
from every training trial. Also remove all known mapped training identities that
appear among held-trial controls. Test on the held participant in the held trial
and its control tracks; discard the other six test-trial wheelchair users for
that fold. Assert track, trial and known-identity separation.

Each positive track is tested once; controls receive seven out-of-training-trial
predictions from seven different fitted models. For pooled scores, weight each
control prediction by 1/7 and each positive prediction by 1, preserving cohort
prevalence. This estimates a crossed-holdout ensemble of prediction tasks, not
one deployed model. Report all fold and participant results. Unknown repeat
control identities cannot be excluded: do not claim all people are unseen.

## Fixed model comparison

Population-prior baseline; speed-only logistic regression; lateral-only logistic;
full-feature logistic; Gaussian naive Bayes; k-nearest neighbours; RBF SVM;
random forest; extra trees; histogram gradient boosting; feature MLP; temporal
1-D CNN; temporal GRU. Fixed modest configurations, no test-guided tuning.
MLP/CNN/GRU use fixed epoch budgets and one deterministic seed per fold. Scaling
is fitted on training data only. Class balancing is restricted to training.
Add training-label-permuted full logistic as a sanity control. A coarse-time
feature ablation tests sensitivity to higher-frequency movement features.

Primary descriptive ranking: weighted pooled average precision (AP); report
ROC-AUC, balanced accuracy, precision/recall/F1, false-positive rate and training
AP. Hard operating thresholds are fixed (0.5 probability; zero SVM margin), not
tuned on test outcomes. Raw class-balanced neural/tree outputs are scores, not
calibrated probabilities. No probability-to-demand integration is claimed yet.

The family with highest crossed-holdout AP is the best observed candidate on
this exploratory comparison. Selection optimism remains; no assertion that it
will be the best model for new people, scenes or recording systems. No iid
frame-level significance intervals or artificial sample-size inflation.

## Simulator gate and scope

Do not automatically manufacture extra labelled data after disappointing results.
JuPedSim's current point-motion model does not generate measured gait/head sway,
tracking artefacts, wheelchair biomechanics or independently verified assistance
behaviour. It cannot substitute for additional labelled people. A future
augmentation study must specify an observation model, calibrate on training-only
recordings and compare real-only against real+synthetic on unchanged held-out
real data. Current timestep failures also remain unresolved.

The current paper, frozen planning experiment and GitHub remain unchanged during
this exploratory comparison. Preserve all outcomes, including failures.
