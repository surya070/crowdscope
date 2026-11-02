# Causal query audit — 2 November 2026

Implemented the draft-v0 checkpoint rules at recording times 10, 20 and 30 s, requiring two seconds of continuous past observations and a current upstream position. All history-length conditions share the same observation-defined cohort. No future arrival or future roster is used to select it.

Results across eight saved trials:

- 24 candidate queries; 21 have complete observed-cohort outcomes.
- 18 pass outcome coverage and the existing metadata-count gate (six trials).
- Only three of those eligible queries contain verified wheelchair members, all from trial 501. Three checkpoints are not three independent wheelchair experiments.
- All three 507 queries include its incomplete wheelchair track, so their targets remain unknown. We did not delete that participant.
- All three 1307 queries are retained in audit output but fail the unresolved metadata-count gate.
- There are zero fresh test trials and no verified helper links. Known wheelchair membership is not equivalent to complete class mapping for every other participant.

Checks: cohort membership and draft observation summaries were identical after all future frames were removed for each of the 24 queries. Downstream crossing events matched the independently produced Stage 2 audit to numerical precision. These checks support the implemented summaries only, not a future feature extractor or simulator.

Draft observations currently include eligible counts, displacement-based past speed and distance summaries. Full H features, learner inputs, imputers, splits and noise conditions have not been implemented or fitted. These files are a feasibility audit, not a ready training benchmark.

A useful example: trial 501 at t=10 s has 68 eligible observed people, while its initial trial contains 88 recorded tracks. Its observed-cohort target is 83.674 s; the complete-trial last crossing is later. At t=20 s the target is 82.190 s. Because the observation-defined cohort can gain people, its remaining time need not decrease exactly with elapsed time. These are different query cohorts, not inconsistent clocks.

## Decision

Do not fit H/M/U on this small saved set and advertise a general mobility benefit. Additional wheelchair trials are necessary even for a useful exploratory comparison. Repeated people must remain explicit: more repeat runs improve within-cohort coverage, not unseen-person evidence.

Next stage: verify official metadata and archive availability for the remaining wheelchair bottleneck runs (502–506, 508), inspect documentation for class/identity completeness, and check prior exposure before acquiring raw outcomes. Use these as development/feasibility expansion until a defensible split can be justified. Corridor runs may support different geometry checks but cannot silently become equivalent bottleneck replicates. Do not silently tune targets or drop people to rescue coverage.

The partial prior-art check and SiME subset mapping remain unresolved before final novelty wording or protocol freeze. This query audit is complete and supports a concrete data-expansion decision. No simulator or predictor was trained.
