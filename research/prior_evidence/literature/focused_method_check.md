# Focused method check — 2 November 2026

This access-qualified follow-up does not establish comprehensive coverage or a verified first contribution.

## Individual-characteristics predecessor: Deng 2022

https://www.mdpi.com/2571-6255/5/6/204 ; https://doi.org/10.3390/fire5060204

Publisher-indexed article sections expose age, sex, normal speed, shoulder width, exit distance, passage characteristics and people-distribution density as inputs. Pathfinder supplies targets; an 85/15 random train/test split and stacking approach are described. The target addresses movement/waiting. Experimental verification is acknowledged as a limitation. Direct retrieval returns 429, so full ablation extraction remains incomplete. Its 3.63 s reported average error is not directly comparable to our proposed cohort task.

Decision: individual-characteristics-aware or dynamic-congestion-aware evacuation prediction is established prior art. The retrieved sections do not settle whether our exact matched short-history comparison was performed. Missing sections cannot establish absence.

## RSET surrogates: Uhlík 2024

https://doi.org/10.1016/j.dibe.2024.100461

Primary institutional indexed text describes count, minimum/mean/maximum exit distances, minimum/mean occupant distances and mean speed, with training-fitted scaling. Correct publisher PII is S266616592400142X, resolved from the DOI; an earlier attempted PII ending 0801 was unverified. Full direct retrieval remains blocked. Split grouping and complete ablations remain unverified.

The accessible FEMTC companion paper provides a full methods anchor: https://files.thunderheadeng.com/femtc/2024_d1-03-uhlik-paper.pdf . Its seven-summary-feature Pathfinder surrogate predicts mean RSET over repeated simulations and compares regression families with nested validation. This rules out generic speed/count/spacing surrogates as sufficient novelty. Its target differs from fixed-cohort remaining passage time.

## Closest temporal competitor: FCRR-Net

https://doi.org/10.1016/j.ress.2026.113346

Publisher preview describes video sequences, visual/structural features, temporal learning and ablation experiments. Exact structural inputs, observation horizons, video grouping across splits and mobility/group ablations remain unknown. Direct 403 access persists. Online-first chronology requires checking against its January 2027 issue date. Do not claim it lacks mobility information or our comparison without full methods.

## EvacuNet: scene prediction and a naming collision

https://doi.org/10.1016/j.eswa.2026.132898

Publisher abstract describes 5,400 simulated scenarios varying buildings, exits, density and distribution, with time and exit-utilization outputs. Exact input encoding and split independence remain unverified. A different 2025 stadium fire-alarm classifier also uses the name EvacuNet: its reported split must not be attributed to this regression study. Identify papers by DOI.

## SiME measurement comparison

https://pmc.ncbi.nlm.nih.gov/articles/PMC9395390/ , Methods and Table 1.

Positions come from 25 Hz overhead tracking. Published speed aggregation uses Voronoi cells; interpersonal distance uses Delaunay neighbours with geometry and cutoff restrictions. Entry-plane headways use x=0. Group comparisons use specified steady-state intervals. Behavioural actions are coded from video.

Our full-recording medians, nearest visible-head spacing and downstream x=2.4 crossings differ. They remain descriptive diagnostics. Exact reproduction needs the published subset-to-raw-file mapping, measurement areas and intervals. Do not use similar numerical flow values to imply equivalence, or claim our smoothing is the published convention.

## Decision

Candidate contribution: incremental value of explicit mobility information at fixed causal observation horizons, including robustness to missing/incorrect labels. This is a hypothesis about a possible gap, not an established novelty claim. Age/speed heterogeneity, neural prediction, a simulator implementation and generic recognition alone do not distinguish the work.

Completed: direct predecessor identified, accessible methods compared, measurement mismatches recorded and protocol implications specified. Incomplete: full feature/ablation/split extraction for the closest closed papers, exact SiME subset mapping, and systematic database/citation coverage. The novelty gate remains conditional.

Next useful independent work is causal query eligibility and metadata mapping without fitting. Before freezing confirmatory experiments, resolve the closest methods through institutional/open access where possible or adopt an explicitly exploratory scope with qualified prior-art claims. No authors were contacted or subscription access assumed.
