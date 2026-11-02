# Stage 3: descriptive movement development analysis

Date: 2 November 2026. Analysis reads the eight previously inspected raw files from the verified backup. It fits no predictor, calibrates no simulator, and inspects no newly acquired trajectory outcomes.

## Measurements and scope

Speed is displacement over a centred 0.4 s window, sampled every 0.2 s. This retrospective smoothing is for descriptive analysis only and must not become a causal forecast feature without modification. Spatial bands are [-6,-4), [-4,-2), [-2,0), [0,2.4) metres. We compute each person's median in each band, then the median across people. A person contributes once per band, avoiding frame-count weighting of group summaries.

Spacing is each track's nearest contemporaneously visible head-centre distance, summarized the same way. It is not wheelchair-body clearance, a verified helper distance, or a Voronoi density. Neighbours outside the camera view are absent. No speed-density diagram is claimed: reconstructing the published Voronoi measurements and steady-state intervals requires a separately specified procedure.

Crossings use first forward head-centre passage at x=2.4 m. Span flow is (observed crossings minus one)/(last minus first crossing), the inverse mean inter-crossing gap. Median headway is reported separately. These whole-recording summaries differ from published steady-state bottleneck-entry flow measurements. Results are descriptive development diagnostics, not an exact numerical reproduction of the published study.

## Findings

- Trial 501 (0.9 m width): upstream band [-6,-4) median-of-person speed medians is 0.214 m/s for the seven documented wheelchair tracks versus 0.315 m/s for 81 other tracks. In the bottleneck band these are 0.758 and 0.797 m/s. This is consistent with location-dependent movement differences, not a universal speed constant.
- Trial 507 (1.2 m width): wheelchair tracks are faster in the upstream band in this summary (0.807 versus 0.267 m/s). Only six wheelchair tracks reach the final two bands. Start order, density, assistance and missing coverage can affect this contrast; it neither disproves SiME nor establishes a general wheelchair speed advantage.
- Trial 501 has 88 recorded crossings, median headway 0.941 s and whole-passage span flow 0.911 people/s. Reference 1501 has 67 crossings, median headway 0.863 s and span flow 1.239 people/s. Crowd sizes and conditions differ; do not attribute the difference causally to disability.
- Reference 1507's span flow is 1.698 people/s. Trial 507's observed 91-person span flow is 1.208 people/s, but its full 92-person clearance remains unknown.
- At recording time zero only 62/88 tracks in 501 and 75/92 in 507 are visible. A complete initial feature vector cannot be constructed by quietly importing later positions. This is a major reason to specify the forecast boundary before modelling.

The contrasting speed patterns strengthen the case for context-aware histories and uncertain capability estimates rather than fixed category-to-speed rules. They do not yet establish classification feasibility or a forecasting benefit.

## Recording discrepancies investigated

The original documentation explicitly states that trajectory IDs are not preserved across files; selected participant identifiers are provided through header comments. Accordingly, track numbers alone cannot define unseen-person splits.

Trial 507 track 32 (wheelchair persistent ID 36) has continuous recorded frames -4 through 938 and ends at x=-2.08068 m. It never reaches the downstream plane in this recording. No internal-frame gap explains the missing exit. The saved evidence cannot distinguish tracking termination, departure from the route or another recording issue. Keep this outcome missing/censored; do not remove it to manufacture full completion.

Trial 1307 contains 85 distinct continuous tracks and 85 recorded downstream crossings, versus 83 participants in current metadata. This confirms the inconsistency but does not identify two tracks to exclude. The older documentation's prefix table also conflicts with current metadata for heterogeneous/reference groups. No speculative reassignment was made. Geometry, raw headers and current metadata must be reconciled before a confirmatory use.

## Additional data leads, without new outcome inspection

Saved metadata and the remote ZIP index list additional 5xx wheelchair bottleneck and 6xx wheelchair corridor runs. They share the same experimental programme and likely repeat people, so they are not automatically independent cohorts. The 500 entry is a candidate special run whose role must be checked; its number alone does not establish a free-speed calibration trial.

Documentation states that wheelchair IMUs were recorded at 100 Hz and synchronized with cameras. This is a promising separate motion-sensing lead, but synchronization files, availability and participant labels are not audited here. IMU recognition cannot be presented as recognition from overhead trajectories.

No new raw trial was downloaded. `movement/additional_trial_candidates.csv` records metadata/index availability only, leaving assignment and exposure verification pending.

## Gate decision and next stage

Stage 3 development measurements are complete for the saved files. **Conditional go to protocol design; hold large simulator generation and definitive efficacy tests.**

Before freezing the protocol, resolve or exclude incomplete/mismatched trials using predeclared criteria, establish a causal observation boundary, inspect further metadata and assign additional trial roles before opening their outcomes. Retrieve unresolved closest prior methods. A forecast for already-observed people may be feasible but is a different target from the entire original cohort's clearance.

Do not frame this analysis as statistical confirmation: there are only two mapped wheelchair trials, seven repeated labelled individuals, no verified helper graph and confounded conditions. No independent-frame significance tests or inflated sample-size claims were performed.

Reproducible outputs are in `movement/`: individual band summaries, group summaries with sample counts, crossing events, headways, checkpoint coverage, and two figures. Plotting dependencies alone were selectively restored from backup; prior research code/results remain archived.
