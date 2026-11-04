# Matched SiME reference replay — 4 November 2026

## Design and provenance

The verified historical reference replay engine was recovered as `research/prior_evidence/code/sime_replay.py`. Its parameters were selected in the preceding study, not in a new search: desired speed 1.6 m/s, radius 0.18 m, time gap 1 s, native CFSV2 interaction defaults. This is a reproduction/diagnostic on exposed reference trials 1501 and 1507. No new participants, unseen outcomes or wheelchair/helper validation are claimed.

A separate `research/matched_replay_engine.py` strengthens the old harness: check spatial errors every integration step and stop if circle-wall penetration exceeds 0.005 m; retain the 0.001 m inter-agent overlap limit. Old reference code sampled checks every 0.2 s and recorded wall penetration without making it a rejection criterion. Consequently old completion reports cannot be read as passing today's stricter checks.

`research/run_matched_replay.py` conditions on real first forward inlet times/lateral positions at x=-6, uses the actual archived geometry and compares centre-crossing proxies with head-centre observations at x=2.4. This supplies future inlet events. It is **conditional movement replay**, not an end-to-end forecast. Admission delay and head/body mapping adjustments are explicitly recorded.

Initial runs use dt=0.01/0.005. After observing their development outcomes, separately locked extensions test 0.0025 and then 0.00125 without changing parameters or selecting another candidate. Outcomes from all eight runs remain saved under `output/matched_replay_check_v1/`, `matched_replay_refinement_v1/` and `matched_replay_convergence_v1/`. Each lock records source/input hashes before execution.

## Outcomes

- Trial 1501: runs at 0.01 and 0.005 stop at wall penetration 0.007780 and 0.005917 m. No complete-cohort error is reported for these failed runs. At 0.0025 and 0.00125, all 67 occupants complete and pass spatial checks; crossing MAE is 4.237 and 5.814 s respectively. The same-arrivals free-flight MAE is 16.195 s.
- Trial 1507: 0.01 stops at wall penetration 0.005969 m. The 0.005, 0.0025 and 0.00125 runs complete all 69 occupants and pass spatial checks; crossing MAEs are 2.704, 2.720 and 2.495 s. Free-flight MAE is 10.656 s.
- At the two finest timesteps, first-to-last simulated crossing spans change from 58.338 to 59.893 s for 1501 and 41.628 to 40.090 s for 1507. Differences of 1.555 and 1.539 s exceed a max(0.2 s, 1%) stability criterion. Thus completion improves with finer integration but convergence is **not** established.
- Recorded spans are 53.284 and 40.037 s. The very close finest-step span in 1507 does not erase individual crossing errors, inlet conditioning or timestep sensitivity.

The model is better than no-interaction free flight for individual crossings in these completed reference replays. That is limited evidence for modelling interactions, not a general claim of predictive accuracy. All runs are previously exposed development evidence.

## Secondary movement diagnostics

For completed 1507 at dt=0.005, simulated aggregate flow is 1.630 people/s versus recorded 1.698; median headway is 0.814 s versus recorded 0.576. Simulated approach-band speed is approximately 0.345 m/s versus recorded 0.425, with different sampling intervals (simulation 0.1 s saved frames, empirical 0.04 s). These are descriptive checks, not formally matched steady-state metrics or extra tuning targets. Close aggregate flow does not establish correct individual behaviour.

## Decision

The matched empirical check is completed, with mixed evidence. It supports a **bounded reference replay**, while the general clearance-simulator release gate remains failed. Do not choose the best timestep retrospectively, call the old parameters newly calibrated, or treat this as wheelchair recognition/assistance validation.

The useful next research decision is scope, not an unlimited sequence of model tweaks. The original plan makes density/composition/resource planning the primary contribution and clearance a secondary endpoint. A concrete scope amendment is proposed in `research/proposed_scope_amendment.md`; it is not yet activated. The final evaluation remains sealed.
