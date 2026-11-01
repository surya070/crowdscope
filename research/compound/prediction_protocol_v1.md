# Prospective compact compound-model prediction study

29 October 2026. New exploratory study following the passed compound-movement feasibility stage. It does not revive the failed JuPedSim study. User authorised a quick comparison for the course paper. Freeze this design before any new study trajectory generation, model fitting or test outcome inspection. All original studies remain intact.

## Question and information

Does supplied parent-child/assistant-wheelchair relationship information reduce remaining-clearance-time prediction error beyond observed motion and a known individual mobility roster? Primary contrast is M-minus-F mean absolute error on two held-out straight corridor configurations. H0: the conditional mean reduction is <=0; H1: it is >0. This is exploratory, not a powered human-population hypothesis test; use descriptive conditional intervals, no p-values or practical safety threshold.

All models see the same causal sampled trajectory prefix and geometry. M additionally knows synthetic nominal individual speeds, radii and profile labels; F adds declared relationship endpoints/types. M includes queue-aware mobility summaries (minimum/rearmost speed and individual free-travel-time summaries) to avoid an unnecessarily weak mobility reference. Forbidden inputs: seed, condition/variant ID, actual unit count, compound membership, simulator support gain, future motion, final exit time and hidden controller state. F receives only the supplied edges, not their latent parameters.

## Generator and scope

Use the unchanged verified prescribed-route, conservative rigid-footprint engine in src/compound/movement.py. Every occupant follows the same straight centreline. No overtaking, route choice, stairs, emergency behaviour, searching or attachment discovery is modelled. Deterministic front-first swept-space reservations and synthetic capability ranges are assumptions, not empirical laws. These are small single-lane queues, not building-scale evacuations. The previously verified turn fixture is not claimed as a tested prediction setting.

Four corridor configurations: G1 length to measurement plane 18 m/width 1.0 m; G2 22/1.2; held-out G3 20/0.9 and G4 26/1.1. Walkable outflow extends four metres beyond the plane. Initial foremost centre is x=10 m for N8 and x=14 m for N12. Each unit/pair block is placed in a seeded random queue order with 0.20 m clearance between reserved bodies/blocks; paired centres are 0.75 m apart. All conditions/variants share identical people, nominal speeds, radii, initial coordinates, queue order and latent draws. Do not resample failed placement or difficult outcomes.

N8 contains one reserved assistance pair, one reserved parent-child pair, two older-profile and two additional adult-profile occupants. N12 contains two of each reserved pair, two older-profile and two additional adults. Helpers/parents are distinct adults and never double-counted. Child and older labels denote synthetic capability profiles. Uniform nominal speed ranges: adult [1.0,1.6], child [0.7,1.3], older [0.45,0.95], wheelchair [0.55,1.05] m/s. Radii: adult/older 0.24 m, child 0.20 m, wheelchair 0.36 m. No real demographic calibration or image inference is claimed.

Four matched conditions: independent, family only, assistance only, both. Family members remain separate collision units with both desired paces capped to the slower nominal pace; there is no rigid parent-child attachment. This approximates shared pace in a single lane only. An activated helper/client pair moves atomically with its conservative convex footprint and fixed 0.75 m spacing. Pair speed=min(helper nominal, gain*client nominal). Gain is a synthetic Uniform[0.85,1.20] draw shared across matched counterparts. This allows assistance to help or hinder. No preparation delay is modelled in this compact design; do not claim otherwise. The client's supported speed can exceed its unassisted nominal speed; its computational speed bound then uses the declared supported ceiling. The public roster still reports its original nominal speed.

Time step 0.04 s, saved frames 0.2 s, circle resolution 16/quadrant, 180 s horizon. Record individual full-circle exits; the compound footprint remains until both occupants clear. Retain every valid incomplete run with the capped target max(0,min(T,180)-t), using T=infinity when incomplete. Invalid geometry/accounting/speed/attachment outcomes stop the study, never become zero-error samples.

## Prospective partitions and sensitivities

For each geometry and N8/N12, use six seed slots and four matched conditions: 192 main runs. G1/G2 slots 0–2 train (48 runs), slot3 validation (16), slots4–5 same-corridor test (32). All G3/G4 slots0–5 are held-out-configuration tests (96 runs; 24 matched base blocks across two fixed configurations). SHA256-derived independent streams are fixed in the manifest. Fit/tune only main development partitions.

Add 32 support-gain stress runs: G3/G4, both N, slots4–5, four conditions, gain range [0.70,1.40] using the same latent uniform draws. Add 16 time-resolution runs: G3/G4, both N, slot5, four conditions at dt=0.02 s. Main-fitted models are applied without refitting. Total 240 trajectories. Stress copies are matched synthetic counterparts, not additional human subjects. They do not validate independent movement mechanisms or real-world transfer.

Before fitting or held-out simulation, verify 16 main development cases (both G1/G2 and N, slot0, four conditions) at dt=0.04/0.02 s: all must clear, satisfy every physical/accounting check, and differ <=0.5 s in clearance. This is a gate chosen before results. A failed gate stops production and is reported. Do not reuse the already observed seven feasibility fixtures as the study test set. Do not relax criteria or drop scenarios to meet the deadline. Every production trajectory must satisfy source integrity and per-update movement checks; retained cap censoring is distinct from an invalid simulation.

## Observations and features

Queries at 2,5,10 s. Observations end 0.2 s earlier and use backward 0.2 s velocity differences. Skip only already-observably-complete queries. Keep a zero target if actual completion is between observation cutoff and query. No future interpolation. Public links are active for feature calculation only while both endpoints remain in the permitted prefix.

Use the exact feature names in prediction_config_v1.json: fourteen aggregate summaries, eleven added mobility summaries, nine added relationship summaries. Distances are longitudinal distances to the measurement plane, not the earlier JuPedSim exit rectangle. Individual nominal free-travel times use max(0,L-x+radius)/nominal speed. The roster is known scenario information; it is not inferred from demographic appearance. No unit count or simulator support gain enters any feature.

## Learners, references and estimands

Models: A aggregate; M aggregate+mobility; F M+relationships; F_no_family; F_no_assistance; F_counts (M plus only the two edge-count features, all other link columns zero). Count-only is a predeclared check on whether any gain is merely coarse relationship composition rather than specific dyads. All share weighted ridge and RBF kernel ridge candidates, alpha [.01,.1,1] and RBF length [.5,1,2]. Reuse the previously tested numerical regressors, train-only weighted standardisation, weighted kernel centring and unpenalised intercept. Select on validation MAE only, ties within 1e-12 favour ridge, then larger alpha/length. Refit at fixed settings on train+validation; clip to [0,180-t]. No test-driven feature, hyperparameter or algorithm changes.

Also evaluate the fitting-weighted median and N/(width*q) with q [.5,1,1.5,2,3,4], selected on validation. Report A/M/F plus both simple references rather than replacing the primary M-versus-F contrast with whichever result looks best.

Average checkpoint errors within run, four conditions within base block, blocks within corridor, then corridors equally. Report MAE, RMSE, mean underprediction, ablations and count-only performance. Primary effect is M-minus-F MAE on main held-out configurations. Descriptive 95% percentile interval: 10,000 paired complete-base-block resamples within each of the two fixed corridors, with fitted models fixed, seed2026102902. It excludes fitting/selection, generator and real-population uncertainty. No significance or safety claim.

Fixed-model metadata sensitivities on main held-out trajectories: remove one supplied link per type when present, and rewire one per type to a distinct appropriate adult while preserving unique adult roles. Log realised corruption. These are deliberately substantial errors, not advertised as 25% noise. Do not alter motion/outcomes or refit. Independent conditions remain no-link. Compare F_counts with F to limit claims about dyad-specific information.

## Integrity, report and boundary

Save config, manifest, all source hashes, trajectory hashes, queries, tuning traces, all predictions, completion/censoring and all planned results. An independent saved-result audit recomputes per-run/hierarchical errors and checks counts/hash coverage without refitting. Preserve failed earlier studies as methodological history, not evidence of predictor failure or success. This compact conditional simulation can support an exploratory course paper; novelty, external validity and indexed-publication readiness remain unestablished. Do not claim effects measured in real young/older/wheelchair populations.
