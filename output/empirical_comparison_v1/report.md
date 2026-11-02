# Real-data mobility-information comparison

2 November 2026. Exploratory SiME observed-cohort forecasting. No simulator used.

## Main result

At the preselected one-second history, nested-validation-selected models have equal-trial MAE **4.278 s with movement/geometry history (H)** and **2.591 s with added supplied wheelchair information (M)**. Improvement is **1.687 s, approximately 39.4%** relative to H. Ridge is selected in every primary outer fold for both conditions.

This supports investigating the incremental value of mobility information in this small real-data setting. It does not establish an independent-population effect, automatic wheelchair recognition, a relationship benefit, operational safety or publication readiness.

## Experiment

Eleven complete trials, 33 query cohorts, histories .4/1/2 s. H contains 19 summaries; M adds five label-conditioned summaries. Target is remaining time until the eligible currently observed group passes the downstream head-centre plane, excluding future arrivals. All conditions share observation histories and cohorts.

Outer folds omit one width configuration; inner folds omit remaining widths to choose settings. All queries/histories from a trial stay together. Scaling is fitted only on each training partition. Grid: ridge alpha .1/1/10/100; boosting learning rate .03/.1, depth 2/3, estimators 50/100, seed113. Predictions are clipped below at zero. The exact extraction, folds and modelling settings were saved before fitting; outcomes were previously inspected, so the study remains exploratory rather than preregistered confirmatory research.

## Other results and failures

Validation-selected H/M MAE is 4.034/2.784 s with .4 s history and 4.121/2.591 s with 2 s history. The gain is not largest at the shortest history; the exploratory hypothesis of a monotonically stronger short-history benefit is unsupported by these aggregates.

At one second, matched boosting H/M errors are 9.181/6.703 s. Training-median and simple distance/speed baselines give 18.594 and 24.102 s. The physical baseline is deliberately simple, not a comprehensive analytical evacuation model. Do not claim superiority to every existing method.

Primary H/M MAE by omitted configuration:

- 0.9 m: 5.378/3.609 s.
- 1.0 m: 5.266/1.782 s.
- 1.1 m: 3.095/1.595 s.
- 1.2 m: 2.922/3.772 s — mobility condition worsens.

M improves in 8/11 trials. Worst trial MAE is 6.999 s for H and 5.549 s for M. Bias is +.560 and -.068 s respectively. Per-trial errors and underprediction fractions are retained in `trial_metrics.csv` rather than hidden by the aggregate.

## Verification

Saved 792 predictions across histories, conditions, families and baselines. Independent reconstruction verifies unique prediction keys, exact source targets and 33-query coverage in each of 24 metric groups. The feature bundle passed 99 future-frame removal checks. The modelling lock and completion record retain input/code/output hashes and the selection trace stores all 288 candidate inner scores. No later retuning was performed.

The metric audit reconstructs saved outputs, not an independent reimplementation of model fitting. It does not validate the source labels or remove experimental confounds.

## Scientific limits

Seven repeated wheelchair users occur across evaluation folds; this is within-population transfer across runs/configurations. There are 11 trials, not 99 independent samples. Both corridor and bottleneck width vary, crowd sizes differ by condition, and labels can proxy crowd composition. All records were exposed before split design. We report per-width/trial errors without a significance or population confidence claim.

Supplied labels are an oracle/reference assumption. Helper/family/age features are absent. Noise sensitivity is deferred in this initial run. Broader prior-art verification is incomplete; the contribution is an exploratory information comparison, not a first-of-its-kind claim. No full-building or alarm-to-safety target was tested.

## Next stage

Before expanding the paper's claims: inspect mobility-label uncertainty and missingness, use a stronger motion-history comparator if sample size allows, investigate the 1.2 m failure on development evidence, and seek independent people/data for transfer assessment. Any follow-up settings must be dated and reported as development choices. Preserve this initial run unchanged. A simulator remains optional future work.
