# Stage 1 checkpoint: conditional research direction

Date: 2 November 2026. Decision: **conditional go for data feasibility; hold the final novelty claim and simulator rebuild.** The accessible scoping pass and follow-up are recorded in `methods_followup.md`; unavailable full texts and systematic-search tasks remain explicit prerequisites before protocol freeze.

## What is already covered

SiME provides empirical evidence for heterogeneous movement and interactions. Modified social-force disability models and controlled social-group clearance experiments also exist. Neural evacuation surrogates, graph flow predictors, and mobility-aid recognition already exist. Consequently none of the following suffices as our contribution: different speeds by category; family/group effects; a JuPedSim implementation; adding a neural model; or wheelchair recognition alone. See the linked primary-source records in `evidence_matrix.csv`.

The most direct forecasting competitor found is FCRR-Net (S05): its indexed publisher description explicitly concerns remaining evacuation time from short video sequences, with real and simulated videos. The full methods and online publication date require verification. We cannot claim first remaining-time forecasting, or assume it lacks mobility/group cues from the abstract.

S07 is also significant: its indexed publisher description includes walking-speed statistics and explicitly distinguishes fixed geometry, detectable states and assumed population properties. Thus merely including speed statistics or uncertainty is unlikely to distinguish our work.

## Candidate contribution worth checking

**Measure the incremental forecasting value of explicit mobility information beyond the same recent movement history, under changes in crowd composition, and quantify the loss when that information is uncertain.**

Suggested narrow question: At a fixed observation horizon, do mobility labels or estimated motion-capacity features improve held-out cohort passage-time predictions relative to a strong trajectory-history baseline?

This is our inference about a possible gap, not an established absence from prior literature. The closest full texts must be checked for exactly this comparison. Use the same learners/tuning budgets for information ablations, and also compare validation-selected learners fairly. Distinguish labels from actual capability: a wheelchair label does not uniquely determine speed.

Assistance links are conditional secondary scope. Without verified helper trajectories and enough independent pairs, make no real-data relationship claim. Family coordination is a separate mechanism with no established family labels in SiME. Avoid expanding one small project into three unsupported tasks.

## Why a simulator rebuild is conditional

An established engine can improve credibility but cannot by itself establish novelty. First determine whether SiME already provides enough complete trajectories and targets for a direct empirical forecast comparison. If yes, that can be the primary experiment; a calibrated simulator can support controlled robustness analyses. If not, use explicitly limited conditional replay or simulation evidence and narrow the claim accordingly.

Any new simulator needs calibration and numerical checks. Do not presume its outputs are realistic because it can reproduce a published average speed or aggregate clearance time. Do not tune interactions until the preferred feature set wins.

## Full-text questions that decide the gate

1. Does S05 compare history alone against demographic/mobility/group inputs? What real data and participant/scenario splits does it use?
2. What population inputs and test independence do S06/S07 use? Is their output total RSET or remaining time at an observed checkpoint?
3. Does S03 validate mobility-specific trajectories, spacing and crossings, and does it compare information availability?
4. Can S04 or SiME supply reliable companion/group identity and independent repeat groups?
5. Has trajectory-only wheelchair recognition been tested on unseen people in comparable congestion? RGB-D appearance and wearable sensor recognition do not answer that question directly.

## Practical recommendation

Keep mobility-aware forecasting as the primary direction. Treat relationship features and recognition as optional extensions. First audit real data, with complete-cohort targets and a prior-exposure ledger. Prefer grouped validation over frame-level random splits. If no unique contribution survives full-text checks, consider a focused reproducibility/benchmark study and assess venue suitability honestly rather than advertising a novel model.

No new models were built or fitted at this checkpoint. No publication acceptance or final novelty is established. Next work within Stage 1 is full-text retrieval/extraction and citation tracing; Stage 2 begins only after review of this checkpoint.
