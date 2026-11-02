# Exploratory causal forecasting bundle

Built 2 November 2026. No learner fitted. Run `research/data/build_forecast_features.py` from the project root with Python and NumPy. The script reads saved raw trials from backup and the six locally acquired members; it creates the feature CSV and hashed manifest.

## Dataset and target

Eleven complete, count-consistent trials: wheelchair 501–506/508 and reference 1501/1503/1505/1507. Three checkpoints per trial (10,20,30 s), with three history lengths (.4,1,2 s): 33 queries represented by 99 correlated rows. The target is the remaining head-centre passage time for the currently observed upstream cohort with two seconds of continuous past data. Future arrivals are excluded by definition. It is not total initial-crowd or building evacuation time.

507 is incomplete; 1307 has count inconsistencies; 1301 has a heterogeneous population outside the currently verified class scope. They remain diagnostics. The primary wheelchair registry maps seven distinct documented wheelchair participants and accounts for the metadata's seven disabled participants in each included wheelchair trial. Zero-disability reference metadata support the reference condition. These checks do not supply age, helper or family labels, nor validate the metadata independently.

## Feature conditions

H contains 19 supplied motion/geometry summaries: observed cohort count; x/y means and spreads; distance-to-plane mean/max/90th percentile; displacement-speed mean/spread/10th/90th percentile; fraction below .1 m/s; average speed change between two subdivisions of the selected history; mean distance to the nearest currently visible track; past-window crossing count; elapsed time; bottleneck width; corridor width.

M adds five supplied-label summaries: wheelchair count/fraction, wheelchair-group mean observed speed and maximum exit distance, and a presence indicator. If no wheelchair member is present the group summaries are zero and the presence indicator is zero. It is an oracle-label comparison, not automatic recognition or diagnosis. All matched conditions share the identical cohort and past observations.

Metadata columns trial/time/history/target are excluded from model matrices through the manifest's explicit feature lists. Elapsed recording time is intentionally allowed through `elapsed_s`; no ID or run-prefix feature is permitted. Some geometric summaries are correlated; regularization is needed. Neither exact free speed nor future positions are available to extraction.

## Evaluation design

Four outer development folds hold out all trials at one bottleneck width (0.9,1.0,1.1,1.2 m). Three inner folds hold out one of the remaining widths for model/settings selection. Every checkpoint, history and noise variant from a trial follows its trial assignment. With only three/four width groups, estimates will be unstable; show each width and each trial, with trial-weighted primary metrics. Use identical folds across H/M conditions and histories. Avoid averaging across histories as if they were independent samples.

This is exploratory transfer across runs/width configurations **within a shared experimental population**, not independent-person testing. The same seven wheelchair identities occur across width folds. The earlier draft's aspiration to separate all repeated people cannot be met here; this scope change is documented explicitly. All outcomes were inspected before these folds were defined. No claim of prospective testing, unseen-person generalization or a sample of 99 independent experiments is permitted.

Both bottleneck and corridor widths change together in these runs, so width transfer is a configuration test, not identification of the isolated causal effect of doorway width. Population sizes also differ between reference and wheelchair conditions. Labels may proxy crowd condition; report those confounds and compare against count/history/geometry baselines.

## Verification and status

All 99 cohort/feature extractions were repeated after future frames were removed; outputs matched exactly. All three histories use the same cohort. Feature values are finite. Trial/width outer assignments are disjoint. Source, feature-file and extractor hashes are in `manifest.json`.

No scaler, imputer, model, tuning or prediction was fitted. The current manifest fixes this extraction/split bundle, not a complete preregistered study. Complete modelling/metric/noise settings and the unresolved prior-art check before the next stage. Data reuse makes eventual results exploratory even after settings are locked.
