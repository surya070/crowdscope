# Research plan: probabilistic mobility-aware crowd analysis

Date: 3 November 2026  
Update (5 November 2026): Implemented the exploratory calibrated detector and connected streaming framework. Nested person/trial calibration, separate coherent held-trial replay, local demo and 46 tests are complete. See `docs/calibrated_framework.md` and `research/calibrated_framework_results_v1.md`. Calibration and composition errors improve; the default planning outcome does not. The current seven-page manuscript now incorporates this extension and explains crowd-management use. Aggregate results, source and the privacy-preserving demo interface are prepared for the private GitHub update.

Status (4 November 2026): Seven-page IEEE-style CrowdScope manuscript and offline interactive demo prepared. All final outcomes retained;18 references,208-word abstract and7 required sections. See `paper/framework/main.tex`, `paper/framework/verification.json` and `app/README.md`. Framework extensibility is distinguished from use-case validation.  
Working title: **A Probabilistic Framework for Mobility-Aware Crowd Analysis and Resource Planning**.

## 1. What we are trying to build

Build a trajectory-driven research framework that estimates where crowds accumulate, how movement capabilities vary across zones, how uncertain those estimates are, and whether using that uncertainty improves a specific planning decision. Add a validated pedestrian simulator for controlled experiments and what-if analysis. CCTV detection is outside the first version.

The full system should eventually connect:

**Trajectories and geometry → quality checks → local movement features → probabilistic crowd state → density/composition maps → resource allocation and passage forecasts → simulator-based comparison → evidence and paper.**

This is a research programme, not a promise that every module will work. A dashboard joining existing methods is not enough to establish novelty. The proposed contribution is a tested method for propagating uncertainty about mobility into crowd estimates and planning decisions, with explicit limits on what trajectories can identify.

### Minimum defensible paper

1. Measure zone occupancy, density and movement from trajectories.
2. Estimate a probability distribution over supported mobility profiles; use semantic labels only when genuinely annotated and externally evaluated.
3. Propagate those probabilities into one resource-allocation problem.
4. Compare homogeneous, hard-label, probabilistic and oracle-information baselines on the same conditions.
5. Evaluate with recorded data where supported and clearly separate synthetic evidence elsewhere.
6. Report uncertainty, leakage controls, failed hypotheses and limitations.

Crowd-passage forecasting is a secondary endpoint. Assistance-link inference, age recognition, multi-floor buildings and CCTV are optional extensions, not prerequisites for the first paper.

## 2. Backup and reset record

Only the local workspace was reset. The private GitHub repository remains unchanged at https://github.com/surya070/crowdscope . Its existing contents describe the preceding study, not this proposed framework.

- Current-study archive: `backups/project_before_probabilistic_reset_20261103_224341.zip`.
- Verification: `backups/probabilistic_reset_verification_20261103_224341.json`.
- All **6,164 files**, totalling **394,213,816 uncompressed bytes**, were read back from the ZIP and checked against per-file SHA-256 hashes before deletion.
- ZIP SHA-256: `05f8ce17d93a51a971f34d5fce410765236731585dd78fa9df77248c8dfdf847`.
- The archive includes the manuscript, data, outputs, dependencies, simulator/demo and `tmp/github-update` publication checkout with Git history.
- Existing `backups/` was excluded from the new ZIP to avoid recursive archives and remains intact. The earlier pre-reset ZIP and its verification remain there.
- Files outside this workspace, including `C:/Surya/RVU/RM/RM_Paper_short.pdf`, were not modified or included in this workspace backup.
- A browser page or running process from the old demo may remain open; it is not an implementation of the new framework.

Restore selectively into a temporary recovery folder. Check the selected files against the verification manifest, then copy only needed components into the new structure with provenance notes. Never overwrite a newer experiment silently. To restore the complete preceding workspace, extract into a separate empty directory and verify it first.

## 3. What the previous project actually established

These are archived exploratory findings, not fresh test results for this proposal.

- In eleven selected SiME trials, known wheelchair information improved the primary ridge passage-time MAE from **4.278 s to 2.591 s**. Seven wheelchair participants repeat across configurations. This was not generalisation to an independent population.
- Five learner families were examined: ridge, RBF kernel ridge, gradient boosting, random forest and a small MLP. All showed an empirical benefit from supplied mobility information in that comparison; ridge had the lowest empirical error.
- Artificial label flips substantially harmed forecasts. This motivates uncertainty modelling, but does not prove a probabilistic replacement will improve decisions.
- We did **not** build a validated wheelchair/child recogniser. Known labels came from dataset mappings, not movement-based recognition.
- A separate JuPedSim 1.4.2 CollisionFreeSpeedModelV2 escort experiment passed defined numerical movement checks. It did not validate real wheelchair pushing or assistance behaviour.
- Correct relationship features did not provide a consistent advantage across model families and assistance assumptions. Some tree-model configurations improved slightly; other models and the assumed-speed-gain condition did not support a general benefit.
- The empirical endpoint was last head-centre passage of a currently observed cohort. The synthetic endpoint was last full-circle exit of a known roster. These targets are different and their errors cannot be pooled.

Recover the old evidence matrix, data audits, trajectory parsing, feature code, leakage checks and movement fixtures where useful. Do not automatically reuse the old hypotheses, calibrated parameters, train/test partitions or headline results as validation of the new system.

## 4. Scope and interpretation boundaries

### Three different labels must stay separate

1. **Movement profile:** characteristics such as lower free-flow speed, frequent stopping, larger turning radius or sustained coordination. These may be estimated from movement, subject to context and validation.
2. **Semantic identity:** wheelchair user, child, older adult, walking-aid user. These require appropriate ground-truth labels. Slow movement alone does not identify disability or age.
3. **Assistance demand:** whether a person needs or requests a particular resource. Wheelchair use, age and low speed do not establish this automatically.

Use an unknown/unreliable state and abstain when evidence is insufficient. Do not rename slow-moving clusters as children or wheelchair users. Unsupervised clusters may only be described as movement patterns until independently interpreted.

### What is explicitly out of the initial scope

- Face/body-image classification, CCTV detection, identity recognition and surveillance deployment.
- Diagnosing disability or inferring an individual's age from speed alone.
- Operational evacuation guarantees, crowd-crush prediction or certification of safe staffing.
- Claiming that synthetic results establish real-world causal effects of assistance.
- Collecting new human data, contacting authors or recruiting participants without separate approval and the necessary institutional process.

## 5. Research questions, hypotheses and variables

Finalize these only after the literature and data feasibility gates. Record amendments before new outcome evaluation.

**RQ1 — Identifiability:** Can trajectories distinguish supported mobility profiles after accounting for congestion, geometry and repeated participants?

**RQ2 — Crowd state:** Does probabilistic membership improve zone-level composition estimates compared with hard classifications, especially under ambiguous observations?

**RQ3 — Planning (primary proposed contribution):** Does propagating calibrated uncertainty reduce unmet demand or decision regret compared with homogeneous and hard-label planning under the same resource budget?

**RQ4 — Forecasting (secondary):** Does probabilistic composition improve passage-time forecasts and uncertainty estimates beyond recent movement history?

Candidate hypotheses:

- H1: Context-aware inference improves held-out probabilistic scoring over speed-only inference. Predictive discrimination and calibration are separate requirements.
- H2: Summed class probabilities reduce zone-count error relative to argmax assignments under the selected deployment conditions.
- H3: Probabilistic allocation reduces mean unmet demand relative to both homogeneous and hard-label allocation under a fixed budget, with an uncertainty interval for the difference.
- H4: Probabilistic inputs improve passage forecasting or interval coverage. Improvement is not assumed and this is secondary to H3.

Independent variables: information representation, observation history, congestion, geometry, population mix, observation corruption and resource budget. Dependent variables: probability scores, zone-count errors, unmet demand/regret, passage MAE and interval coverage. Controls: shared observations, split groups, budget, action space, simulator version and matched scenario seeds. Confounders: participant identity, crowd condition, exit width, geometry, tracking quality and exposure to prior results.

Choose one primary planning endpoint and one primary comparator before the confirmatory run. Other comparisons are secondary. Determine the smallest practically meaningful improvement with a clearly described use case; do not invent an arbitrary threshold and call it a safety standard.

## 6. Mathematical model to develop

All expressions below specify a proposed model, not fitted results. Implement the simplest justified version first.

### 6.1 Observations and context

For person i at time t, observe position p_i(t)=(x_i(t),y_i(t)), timestamps and a tracking-quality indicator. Geometry defines walkable areas, obstacles, exits and zones z with usable area A_z. Keep positions in metres and time in seconds.

From a past-only window [t-h,t], compute X_i: speed distribution, acceleration/change of speed, stopping fraction, heading changes, curvature/turning behaviour, neighbour distances, local density and available gap. Include feature availability/missingness explicitly. Use context E_i: local congestion, geometry, direction and time horizon.

Do not use future crossings, later trajectory segments, final clearance time or ground-truth identity as inference inputs. Long-term individual features may be used only if the intended observation setting actually provides them.

### 6.2 Density and movement maps

For complete tracks: N_z(t)=sum_i 1[p_i(t) in z] and rho_z(t)=N_z(t)/A_z. Compute mean speed, stopped fraction, directional flow and a congestion-duration measure. Document zone boundary conventions.

Compare fixed-zone/grid estimates with a suitable local-density estimator if that materially affects conclusions. Handle walls, boundary cells and partial field of view. With uncertain positions, weight occupancy by P(p_i in z | observations) instead of pretending each location is exact. Missing people cannot be recovered by an arbitrary multiplier without a measured detection model.

### 6.3 Conditional mobility probabilities

Let C_i be a supported class/profile. The conceptual Bayes model is:

P(C_i=c | X_i,E_i) = P(X_i | C_i=c,E_i) P(C_i=c | E_i) / sum_k [P(X_i | C_i=k,E_i) P(C_i=k | E_i)].

Specify how each likelihood/prior is estimated. Do not assume speed, acceleration and spacing are conditionally independent without checking. A regularised probabilistic classifier is an acceptable practical estimator of this conditional distribution; Bayes notation alone is not a new algorithm.

Start with multinomial/binary logistic regression and a transparent generative baseline. Compare a limited tree-based classifier if data supports it. Use neural/sequence models only when independent sequences and meaningful history justify their complexity. Fit probability calibration exclusively inside training/development folds; compare uncalibrated and calibrated versions.

For a persistent semantic label, accumulate evidence without allowing an individual to switch disability/age classes frame by frame. For a dynamic movement state, a separate Markov/HMM formulation is possible:

P(S_t | X_1:t) proportional to P(X_t | S_t,E_t) sum_s P(S_t | S_(t-1)=s,E_t) P(S_(t-1)=s | X_1:t-1).

Distinguish persistent C_i from changing movement state S_i(t). Overlapping windows are correlated; do not repeatedly multiply their likelihoods as independent evidence. A temporal model is an extension only if it demonstrably improves calibration or decisions.

### 6.4 Probabilistic zone composition

For observed occupants I_z(t):

E[N_(z,c) | observations] = sum_(i in I_z) p_(i,c).

This expectation does not require independent classifications. For a binary class:

Var(N_(z,c)) = sum_i p_i(1-p_i) + 2 sum_(i<j) Cov(I_i,I_j).

The independence approximation drops the covariance term and must be labelled. Shared congestion, family groups and model error can make it inaccurate. Prefer trial/scenario-level resampling or an explicit shared-context model when estimating uncertainty; test interval coverage. Report expected counts as expectations, not certain fractional people.

### 6.5 Optional coordination graph

Estimate P(L_ij=1 | separation, relative direction/speed, lagged following and waiting behaviour). Distance alone is insufficient: strangers in a queue are also close and speed-matched. Use nearest-neighbour candidate limits to avoid all-pairs scaling.

L_ij initially means sustained coordination, not verified caregiving or assistance. Assistance labels require independent annotation. Compare real edges, shuffled edges, edge counts and no edges using the same observation window. Infer the graph from observations; never give the predictor an oracle graph while calling it recognition.

### 6.6 Resource demand and allocation

Start with a **static, one-epoch allocation** of B interchangeable support units across zones. Define each unit, planning horizon and service capacity k_z before evaluation. This is a transparent planning abstraction, not a validated staffing rule.

Let R_i indicate a request/need for the specified service. Estimate:

q_i = P(R_i=1 | observations) = sum_c P(R_i=1 | C_i=c,E_i) p_(i,c),

only if the demand mechanism is separately justified. Without real demand labels, these conditional demand rates are declared scenario assumptions and varied broadly. Do not infer them from the desired outcome. Alternatively use documented requests directly and investigate uncertainty in movement/access instead.

Let D_z=sum_(i in I_z) R_i and a_z be integer resource allocations, with a_z>=0 and sum_z a_z<=B. A tractable loss is:

L(a,D) = sum_z w_z max(0,D_z-k_z a_z) + lambda C(a),

where weights and cost terms are justified in advance. The decision rule is:

a* = argmin_(a in A) E[L(a,D) | observations].

Use scenario sampling or exact enumeration for a small number of zones. Never round all expected counts before optimisation. Check whether uncertainty actually changes the optimal decision: if a linear formulation gives identical decisions from hard labels and probabilities, report that and use a genuinely justified nonlinear capacity/shortfall objective rather than redesigning until a preferred method wins.

An uncertainty-sensitive extension constrains P(D_z > k_z a_z | observations) <= alpha or minimises tail loss. If the budget makes constraints infeasible, return an explicit shortfall and feasible fallback; do not silently violate constraints. Choose alpha as an experimental policy parameter, not a certified acceptable risk.

Fairness constraints may impose minimum coverage or penalise worst-zone unmet demand. Do not assign a lower value to protecting any demographic group. Compare mean, worst-zone and group-specific outcomes.

Dynamic dispatch, travel times and resource reassignment are later extensions. A generic assistance-resource model cannot establish evacuation-time reductions unless its service-to-motion mechanism is separately validated.

### 6.7 Passage-time distribution

Define the target precisely: for a fixed observed cohort I_t, Y_t=max_(i in I_t) tau_i - t, where tau_i is the defined first forward crossing. Specify the line, head-centre/body convention and handling of incomplete tracks. Do not call partial-field passage time full-building RSET.

For uncertain latent state S:

P(Y_t > u | observations,a) = integral P(Y_t > u | S,a) P(S | observations) dS.

Approximate by posterior/scenario sampling if needed. Use a past-history baseline, hard-label composition, expected/probabilistic composition and oracle labels. Train point or quantile models with identical folds and tuning budgets. Predictive intervals need held-out coverage checks; a probability formula does not guarantee reliable intervals under distribution shift.

## 7. Sequential stages, deliverables and gates

Work in order. At the end of each stage, save evidence and a decision, explain what passed/failed, and pause for the user's review as in the earlier project. The present request authorises backup/reset and this plan, not an automatic run of every stage or a GitHub reset.

### Stage 0 — Preserve and reset (completed)

Verified backup, retained older backups, cleared local active files and wrote this plan. Do not erase the preceding study's negative findings. Before restoring code, record which archive member supplies it.

### Stage 1 — Literature and contribution gate

1. Recover earlier search logs and full-text notes. Audit attribution instead of trusting generated summaries.
2. Search trajectory-based mobility classification, crowd density/composition estimation, Bayesian crowd state estimation, uncertainty-aware resource allocation, accessible evacuation and group/escort behaviour.
3. Record exact queries, date, source, filters and exported records. Include empirical, simulation and methods papers with explicit relevance; record exclusions and deduplicate.
4. Compare nearest work on input modality, labels, contexts, uncertainty handling, planning objective, simulator, validation splits and evidence level.
5. Verify SiME's actual model/data claims. Do not describe OSM as JuPedSim-native or claim SiME used AVM/OSM/SFM adaptations without direct primary evidence. Confirm engine/version capabilities from official documentation at implementation time.
6. Use PRISMA reporting only for an actually documented search/screening process. Do not force the bibliography to 18 or reuse earlier selected-paper counts as new counts. A citation map is optional and cannot establish novelty by itself.

Deliver: `research/literature/search_log.md`, `screening.csv`, `evidence_matrix.csv`, `claim_source_ledger.md`, `novelty_assessment.md`.

Gate: a specific unresolved comparison, not simply “a complete framework.” If uncertainty-aware mobility planning is already well covered, narrow to a supported stress regime or target population, or reposition as a replication/benchmark. No publication or indexing guarantee.

### Stage 2 — Data and identifiability gate

1. Recover SiME provenance and audits; verify usage terms, schemas, frame rate, geometry, trajectories, wheelchair mappings, repeated identities and incomplete recordings.
2. Inventory any additional datasets by modality, participant-level labels, age labels, unique subjects, environments, licensing and annotation quality. Wearable-sensor datasets are not direct validation of position-only inference.
3. Create an exposure ledger: previous SiME trials and inspected results are development evidence. An old test is not fresh because the task name changed.
4. Audit whether classes overlap in observed motion once density and geometry are controlled. Quantify label counts by unique person and trial, not by frames.
5. Test whether meaningful person-disjoint splits exist. If participant-trial connections collapse the dataset into too few independent components, say so and restrict claims or obtain another source.
6. Record missing age/helper/demand annotations as missing. Never assume a healthy helper for every wheelchair user or a parent for every child.

Deliver: `research/data/data_card.md`, `label_inventory.csv`, `exposure_ledger.csv`, `split_feasibility.md`, `target_definitions.md`.

Gate paths:

- A: adequate real labels → semantic mobility inference with conservative external/generalisation claims.
- B: inadequate semantic labels → movement-profile inference only, with clearly labelled synthetic semantic tests.
- C: insufficient classification evidence → supplied/uncertain metadata as inputs; study propagation and planning without claiming automatic recognition.
- D: no credible real demand labels → planning is a controlled synthetic proof of concept, with empirically assessed observation/mobility components kept separate.

### Stage 3 — Freeze the minimum protocol

Choose the primary use case, class definitions, observation histories, zone scheme, planning horizon, target, budget, demand assumptions, hypothesis, primary metric and evaluation unit. Freeze splits, candidate models, calibration scheme, scenario generation, sensitivity ranges and stopping rules in a dated protocol with hashes.

Reserve genuinely unused data if available. Separate simulator calibration from evaluation scenarios. Fix what counts as meaningful benefit based on the use case. Plan precision using independent subjects/trials/scenario blocks; if power cannot be justified, label the study exploratory rather than manufacture a sample-size calculation from frames.

Deliver: `research/protocol_v1.md`, `configs/`, `research/split_manifest.csv`, `research/amendments.md`.

Gate: all outputs have independently defined ground truth or an explicitly bounded synthetic interpretation. No model fitting on test outcomes.

### Stage 4 — Trajectory and crowd-state foundation

Implement ingestion, unit conversion, geometry validation, past-only windows, track-gap handling, zone boundaries, counts, density, speed/stops and flows. Save feature definitions and quality flags.

Test empty scene, one person, stationary person, boundary crossing, duplicate timestamps, variable sampling, dropped frames, track fragmentation and partial visibility. Check conservation of occupants and crossing direction. Compare manual counts for small known fixtures.

Deliver: versioned parser/features, zone summaries, simple replay and meaningful integrity tests.

Gate: counts, units and target timing are correct before any classification or attractive dashboard work.

### Stage 5 — Probabilistic mobility inference

Fit speed-only and context-aware transparent baselines first. Compare a small predeclared model set, calibrate within development folds and retain all seeds/configurations. Quantify how uncertainty changes with history, density and missingness. Use abstention thresholds chosen on development data.

Evaluate log loss, Brier score, class-wise precision/recall, confusion matrices and reliability plots. Accuracy alone is inadequate with imbalance. Report calibration diagnostics cautiously with small samples; use participant/trial-level intervals, not independent-frame intervals.

Gate: probabilities must carry information beyond prior-only/speed-only baselines and have acceptable held-out calibration for the chosen use case. If not, use Stage 2 path B/C, retain unknowns and report the limitation.

### Stage 6 — Simulator construction and verification

Use an established pedestrian engine, initially recoverable JuPedSim/CFSV2, after checking suitability. Random waypoint may provide a free-space movement baseline; it is not by itself a validated crowded-exit/collision model. Do not swap engines simply because one gives a favourable result.

Start with one room/corridor, configurable bottleneck and a few zones. Add heterogeneous desired speeds, footprints and turning constraints only where supported. Sample overlapping within-profile parameter distributions, behavioural variation and nuisance factors so class is not trivially encoded by a fixed speed.

Required fixtures: single walker; two agents following; doorway; corner/turn; mixed queue; narrow passage; no-path/deadlock; timestep refinement; entry/exit conservation; reproducible seeds. Check overlap, wall penetration, plausible speeds, numerical stability and explicit non-completion.

Calibrate only on designated empirical development runs and independently assess speed/flow/headway/clearance distributions where matching observations exist. Numerical correctness is not behavioural validation. A reproduction using known future arrivals is a replay validation, not a blind forecast.

Recover the old escort controller only as an optional documented extension. Test linked/unlinked pairs with identical initial conditions, helper after client exit, gap hysteresis, queue obstruction and no assumed benefit. Physical wheelchair pushing needs a more appropriate representation and independent calibration.

Deliver: `src/simulation/`, fixtures, calibration report, validation report and frozen scenario generator.

Gate: failure blocks downstream claims based on that behaviour. Simplify the scenario or keep the analysis data-only; never tune for a desired hypothesis outcome.

### Stage 7 — Zone uncertainty and planning benchmark

Compute expected composition and uncertainty; validate against known counts. Implement the one-epoch allocation objective and explicit capacity/budget constraints. Start with enumeration for small instances; verify any optimiser against it.

Compare:

- Uniform/population-count allocation without mobility information.
- Hard classifications and otherwise identical planner.
- Probabilistic classifications and identical planner.
- Oracle true state, as an information reference (not automatically an attainable deployment benchmark).
- Noisy/miscalibrated probability variants and an uncertainty-ignorant expected-demand variant where informative.

Use identical scenarios, observations and budgets across policies. Evaluate decisions on realised demand hidden from the planner. Average over matched replicates; distinguish uncertainty in the predictor from randomness in outcomes. If demand is synthetic, disclose its generating equation and vary it independently of the inference model.

Deliver: allocation implementation, small optimality tests, scenario lock, pilot report.

Gate: the loss reflects a defensible use case and there is no oracle leakage or circular demand labelling. A demonstration of low loss under a hand-chosen mechanism is not real staffing validation.

### Stage 8 — Forecasting and optional linkage

Reuse verified past-history features with a newly frozen protocol. Compare history-only, hard mobility, probability-derived summaries and oracle inputs. Start with ridge/boosting; add forest/MLP only if justified by the sample size and a predeclared budget. No need to repeat every old architecture by default.

If coordination labels exist, compare observed inferred links with no links, counts and shuffled controls. Keep oracle-link results separate. Do not promote synthetic known links into claims of detecting assistance.

Deliver: secondary forecast results, intervals, control experiments and clear empirical/synthetic target definitions.

### Stage 9 — Locked evaluation and stress tests

Run once after development choices are frozen. Group splits at the strongest available unit: person, trial, venue and scenario block as appropriate. Keep observations from the same trajectory and paired scenario variants together. All transforms, calibration and tuning occur inside training/development partitions.

Use out-of-fold probability predictions when training downstream planners/predictors; training them on in-sample “perfect” classifier outputs creates a deployment mismatch. For cascaded models, nest this procedure inside each outer evaluation fold.

Priority stress tests: congestion shift, class-prior shift, held-out geometry, reduced history, dropped tracks, position noise, label noise, rare classes, budget shortage and demand-model misspecification. Add graph errors only if the graph module is included. Do not multiply a huge parameter grid without enough independent repetitions.

Report paired effect sizes and uncertainty intervals by independent trial/subject/scenario block. Use hierarchical resampling when appropriate; disclose few-cluster uncertainty. Treat multiple models/endpoints as secondary or address multiplicity. Publish every prespecified outcome, including non-completion and negative effects. Test failures must not disappear from averages.

Gate: proceed to claims matching the actual evidence. If no planning benefit exists, a careful boundary/negative-result paper may still be possible; do not tune against the final test to make H3 pass.

### Stage 10 — Integrated demonstration

Build a lightweight trajectory replay with zone density, expected composition, confidence/unknown state, allocation suggestions and optional passage intervals. Show recorded vs synthetic source, units, observation time and uncertainty. Clearly distinguish movement profiles from semantic labels.

Provide observed/predicted/true-state toggles in evaluation mode; never show ground truth as a prediction. Explain why a zone received resources in terms of the declared objective. Demonstrate one normal, one congested and one uncertain/failure scenario.

Deliver: local app, one-command launch, small redistributable demo and concise README. No CCTV integration or deployment claim is required.

### Stage 11 — Paper and reproducibility package

Draft around the evidence, not the intended headline. Preserve the teacher's seven major sections: Introduction; Literature Review and Related Work; Research Problem, Objectives and Hypotheses; Research Methodology; Results; Discussion; Conclusion and Future Work. Subsections are optional. Verify the original guideline text from the backup before final formatting.

Target at most eight IEEE-style pages if that remains the course requirement; use supplementary materials for full protocols and sensitivity results. Include an architecture figure, mathematical definitions, primary results with uncertainty, ablations, failure examples and limitations. Reference count must follow actual sources and the teacher's current requirement; never fabricate or distort review selection counts to match it.

Keep empirical findings, synthetic validation and proposed extensions explicitly separate. Include data/code availability, funding and confirmed author contributions/declarations. Prior author list is Surya Maheswaran, Yashaswini Pawar, Sohan Kori and Seema B. Hegde; reconfirm contributions for the new work rather than inventing them.

Use one dependency file, pinned versions, seeds, run configurations and audits. Keep raw participant data private unless redistribution is explicitly permitted. Exclude dependencies, temporary files, old backups and secrets from GitHub. Keep the repository private unless the user changes that preference. Update it only when requested; do not overwrite the old paper as though it never existed.

Final checks: figures readable, equations defined, no unsupported novelty/safety claims, results regenerate, citations resolve, source compiles, PDF within page limit and visual inspection completed. A completed course paper does not guarantee acceptance at an indexed venue; check a named venue's current requirements separately.

## 8. Error and workaround register

This covers foreseeable issues; new issues require documented amendments, not silent workarounds.

- **No age labels:** remove child/older-adult classification from empirical claims; use annotated external data or explicitly synthetic age-related scenarios. Do not estimate age from a low-speed threshold.
- **Too few distinct wheelchair users:** report limited feasibility, person-disjoint checks where possible and wide uncertainty. More frames or augmentation do not create new people.
- **Congestion mistaken for impairment:** condition on density/geometry, evaluate matched conditions, include unrestricted-motion windows and allow unknown. If still inseparable, use movement profiles.
- **Synthetic class is encoded by speed:** overlap class distributions, vary nuisance factors, hold out parameter regimes and test on supported real data. Perfect synthetic classification may expose a trivial generator.
- **Shared participants contaminate folds:** group by identity and trial; audit connected groups. If no viable split remains, acknowledge within-population evaluation or obtain independent evidence.
- **Downstream model sees overly accurate training probabilities:** use out-of-fold predictions and nested calibration; never fit the stack using test labels.
- **New class or environment:** monitor low confidence/out-of-distribution indicators, abstain and fall back to movement-only/count-based planning. Confidence scores alone do not reliably detect all shift.
- **Class-prior shift:** evaluate sensitivity and any prior adjustment with separate development evidence. Do not estimate test priors from unavailable ground truth.
- **Track gaps/ID switches:** quality flags, bounded interpolation only when justified, continuity requirements and explicit exclusions; compare corrupted-track robustness. Never splice arbitrary people.
- **Uncertain zone boundary or changing usable area:** use consistent geometry, sensitivity to zone resolution and probabilistic occupancy if supported. Report boundary effects.
- **Correlated class errors:** use clustered resampling/shared-context modelling; independent Bernoulli intervals can be too narrow.
- **No true assistance demand:** use documented requests, or explicitly assumed demand scenarios with sensitivity bounds. Cannot claim real staffing accuracy.
- **Impossible resource constraints:** report shortage, use a feasible fallback and show residual unmet demand. No silent constraint relaxation.
- **Planner benefits only under one cost function:** evaluate predeclared alternatives and report dependence on weights/capacity assumptions.
- **Oracle does not outperform learned policy in a finite run:** inspect solver equivalence, objective mismatch and sampling variance; an oracle information benchmark need not win every realised draw.
- **Simulator collision/deadlock/numerical instability:** stop affected benchmark, retain failure evidence, fix and version the engine/controller, rerun verification before comparisons. Do not exclude hard scenarios just to improve averages.
- **No behavioural calibration for assistance:** restrict assistance to a hypothetical what-if module; do not claim validated evacuation improvement.
- **Observed trajectory ends before crossing:** mark target unknown/censored; never equate last recorded frame with clearance. Use a supported censoring method or report complete-case limitations and exclusions.
- **Conditional replay is confused with prediction:** record whether future arrivals or states were supplied and label the experiment accordingly.
- **Little/no probabilistic advantage:** check calibration, sample size and whether decisions are sensitive to uncertainty; preserve the negative result. Do not redesign solely to make probabilities win.
- **Compute/runtime limit:** prioritise transparent baselines, fewer predeclared scenarios and more independent repetitions over a large neural-model catalogue. Cache immutable features and profile first.
- **Dependencies or licensing prevent recovery:** recreate a pinned environment, check engine compatibility, choose an available alternative with a new validation record. Do not silently compare results from different engine versions.
- **Literature already answers the proposed question:** change the contribution before implementation, or conduct an explicit replication with a new boundary condition. A different model name is not sufficient novelty.
- **Deadline shorter than evidence collection:** deliver a clearly labelled proposal/pilot plus demo and limitations. Never present synthetic recognition as real validation or reuse old outcomes as fresh confirmation.

## 9. Optional extensions, ordered by evidence needed

1. **Temporal probabilistic filtering:** useful if short windows are noisy; needs leakage-safe sequence evaluation and handling of correlated windows.
2. **Multi-resolution density maps:** useful if zone boundaries change rankings; needs spatial robustness and runtime checks.
3. **Robust/chance-constrained allocation:** useful if mean demand hides shortages; needs calibrated uncertainty, feasibility handling and transparent policy parameters.
4. **Coordination/assistance graphs:** requires labelled links for semantic validation, queue confounder controls and shuffled/count-only baselines.
5. **Dynamic resource dispatch:** requires travel/service-time models, reassignment costs, finite-capacity tracking and a closed-loop evaluation.
6. **Route/exit intervention:** requires validated response/compliance assumptions and congestion feedback; cannot infer causal benefit from a static forecast alone.
7. **Child/older-adult classes:** requires appropriate trajectory-level demographics, ethics/usage review, adequate independent subjects and an abstention policy.
8. **More realistic wheelchair geometry:** requires body/device footprints, turning constraints and empirical manoeuvre evidence; circles may be inadequate in tight turns.
9. **Sequence or graph neural models:** requires enough independent data and fair comparisons; no automatic benefit from architecture complexity.
10. **External venue/population validation:** strongest route to broader claims, but needs compatible labels, geometry and independent participants.
11. **CCTV input:** a separate later project covering detection/tracking errors, consent/privacy, camera calibration and robustness. It plugs into the trajectory interface only after the current pipeline works.
12. **Multi-floor/RSET analysis:** needs pre-movement, stairs, arrivals, route choice and full-roster observation assumptions; cannot be obtained by renaming bottleneck passage time.

Select at most one substantial extension before the core benchmark is complete. Record what new question it answers and which evidence would falsify its usefulness.

## 10. Proposed clean project structure

Create directories only as stages need them:

```text
plan.md
README.md
requirements.txt                  # one file, pinned when implementation starts
backups/                          # local only; never committed
research/
  literature/
  data/                           # data cards, provenance, exposure/split ledgers
  protocol_v1.md
  amendments.md
configs/
src/
  ingestion/
  features/
  inference/
  crowd_state/
  planning/
  simulation/
  evaluation/
tests/
data/
  raw/                            # private/ignored unless redistribution permitted
  processed/
output/
  development/
  evaluation_v1/                  # immutable locked-run outputs
app/
paper/
```

Every result should link to input provenance, split, configuration, code version and seed. Separate development from locked evaluation. Prefer small reproducible fixtures to copying all previous outputs into the active project.

## 11. Timing and decision checkpoints

These are planning ranges, not completion promises; obtaining suitable labels may dominate elapsed time.

- Literature/data feasibility: approximately 2–5 focused working days, longer if primary sources or permissions are unavailable.
- Protocol plus trajectory/state foundation: approximately 2–4 days once data is usable.
- Inference/calibration and minimal planning pilot: approximately 4–8 days, depending on label quality and split viability.
- Simulator verification/calibration and locked benchmark: approximately 4–10 days, with substantial extension if the movement model fails validation.
- Integration, reproducibility audit and paper: approximately 3–5 days after results are stable.

A one-day exercise can produce a bounded pilot or illustrative prototype, not establish all recognition, calibration, planning and real-world validation claims. If there is a new deadline, choose the scope at the next checkpoint rather than pretending all modules fit it.

## 12. Immediate next action

Begin **Stage 1**, recovering only the previous literature evidence and data audit notes from the verified archive. Build a comparison matrix for the nearest uncertainty-aware crowd/planning work and an initial label-feasibility summary. End that stage with a recommended narrow contribution and explicit unresolved questions before committing to a new simulator or classification claim.

The first decision is whether the paper can support **semantic mobility inference**, only **movement-profile inference**, or **planning with uncertain supplied metadata**. All three are legitimate research routes when accurately labelled; their evidence requirements and claims differ.
