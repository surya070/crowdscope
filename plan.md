# Research plan: mobility and interactions in crowd-clearance forecasting

Date: 2 November 2026

Status: Complete IEEE-style working manuscript drafted in `paper/real_and_linkage/main.tex`, exported to `output/pdf/Crowd_Passage_Forecasting_Draft.pdf`. Five pages including references, with seven course sections; compiled and visually reviewed. Both empirical benefit and synthetic negative linkage result retained. Before submission, complete focused literature/data-term checks and confirm author declarations/venue requirements. No GitHub update or submission performed.

## 1. Objective and working question

Produce a defensible, reproducible research paper that tests whether mobility information and interpersonal interactions improve forecasts beyond recent observed movement.

Working question: **Does explicit mobility information improve remaining crowd-passage-time forecasts beyond trajectory history, and does verified assistance information provide further value?**

This question is provisional. Literature and data feasibility determine the final scope. SiME already shows that heterogeneous mobility affects movement and flow. Repeating that observation or merely using JuPedSim is not sufficient novelty. Wheelchair classification is optional and must earn its place through data availability and forecasting usefulness.

## 2. Reset and evidence preservation

- Only the local project was reset. The private GitHub repository remains unchanged.
- `backups/` contains the complete pre-reset ZIP, including manuscripts, original literature, code, raw data, results, dependencies, and the publication checkout with Git history.
- `backups/backup_verification.json` lists archived paths, sizes and SHA-256 hashes. All 7,472 files were read back and checked before clearing the local folder.
- Recover selected files when needed; do not silently reuse obsolete protocols or restore the entire old workspace into the new study.
- The old compound simulator's relationship benefit was unsupported. Broader learner comparisons did not establish a consistent benefit. Preserve these findings as prior exploratory evidence.
- The earlier SiME JuPedSim replay used reference trials without disabled participants and observed upstream arrivals. It did not validate wheelchair-assistant behaviour or an end-to-end forecast.
- Previously inspected SiME trials are development evidence, not newly untouched tests. Reconstruct the complete exposure ledger from archived records before reserving tests.

## 3. Execution rules

Work sequentially. At each stage, save findings and a go/no-go decision, explain them to the user, and pause before the next stage. Ask only for genuinely missing information. This plan does not authorize contacting researchers or recruiting participants.

Do not change hypotheses, test sets or success criteria after examining test outcomes. Date and justify amendments. Do not tune a simulator to force relationship features to win. Report unsuccessful models, non-completion and negative results.

## Stage 1 — Establish the literature gap

Read the original SiME publications and supplements in full. Search scholarly databases available to the university, plus accessible primary-source indexes. Record exact queries, dates, databases, filters and exported records. Example query families:

- evacuation OR crowd clearance OR bottleneck passage AND forecasting OR remaining time prediction;
- heterogeneous mobility OR wheelchair OR disability AND pedestrian simulation AND calibration OR validation;
- assistance OR companions OR social groups AND evacuation AND prediction;
- trajectory-based mobility classification AND wheelchair;
- observed movement history AND evacuation-time estimation.

Trace citations forward and backward from the strongest matches. Include direct forecasting studies, relevant calibrated simulators and trajectory-inference work; distinguish empirical studies from software documentation. Deduplicate and screen using documented eligibility criteria. Keep full-text exclusion reasons. Use PRISMA reporting where appropriate without inventing historical counts or forcing a fixed number of references. A citation map is useful if it reveals related research clusters; it is not a substitute for screening.

For each close paper record its question, population, data, target, observation horizon, features, movement model, validation split, baselines, findings, limitations, and differences from our proposal. Check whether it already tests the incremental value of labels or relationships beyond trajectory history.

Deliverables: `research/literature/search_log.md`, `screening.csv`, `evidence_matrix.csv`, bibliography and `novelty_assessment.md`.

Gate: identify a narrow, supportable contribution relative to the closest prior work. If the proposed comparison already exists, narrow or change the question before implementation. Novelty remains provisional rather than guaranteed.

### Source-attribution check requested by the user

Treat the supplied description of SiME's OSM/AVM/social-force adaptations as claims to verify, not established project history. Maintain a claim-to-source ledger separating empirical SiME observations, model capabilities, documented SiME implementations, and our proposed extensions.

Checks on 2 November 2026:

- The current official JuPedSim model catalogue lists collision-free speed, anticipation velocity, generalized centrifugal force and social-force models, among others. It does not list OSM. The Pedestrian Dynamics OSM documentation points to Vadere. Do not call OSM a native JuPedSim engine based on these sources.
- The cited arXiv:1708.03080 is a general pedestrian-model paper by Kang and Han; its abstract does not substantiate a SiME wheelchair-specific OSM adaptation.
- The cited TRID record 1285783 is a 2013 review of crowd-motion models, not evidence that SiME implemented a particular extension.
- The reviewed SiME empirical papers establish heterogeneous movement and interaction effects. They do not establish the supplied claims of heavy AVM use or customized crushing/friction simulations. Broader project implementation claims require identifiable primary methods papers, reports or code. Lack of evidence here is not proof that no simulation work occurred elsewhere in the programme.
- The supplied TUM PDF could not be retrieved during this check (HTTP 429); other unexamined links remain leads for Stage 1, not verified support.

Sources: https://www.jupedsim.org/stable/pedestrian_models/ ; https://pedestriandynamics.org/models/optimal_steps_model/ ; https://arxiv.org/abs/1708.03080 ; https://trid.trb.org/View/1285783 .

## Stage 2 — Audit SiME data and labels

Recover prior provenance, downloads and access records. Inspect official metadata, raw headers, documentation, papers and supplements together. Record inconsistencies rather than assuming run-prefix conventions are reliable.

Inventory trials, geometry, widths, frame rates, timestamps, trajectory coverage, participant counts, movement conditions, disability labels and missing tracks. Establish which identities repeat across trials. Separate unique people from person-trial observations.

Verify wheelchair identity mappings, device types and dimensions. Investigate the published ages of listed participants with disabilities; do not generalize these to a complete age-labelled cohort. Verify whether assistant identities can actually be linked to trajectories. A statement that assistance occurred does not identify a helper track. Do not assume every wheelchair user has a helper, or that nearby people are relatives.

Determine whether free-movement trials can be mapped to group trials. Measure missingness and label confidence. Check licensing and redistribution conditions; keep sensitive participant details out of public outputs.

Define a feasible outcome: remaining time until the last member of a specified tracked cohort crosses a fixed plane. Distinguish this from full-body clearance and alarm-to-building-evacuation time. Specify how unseen arrivals and incomplete field-of-view are handled. Future measured inlet schedules are allowed only for an explicitly conditional replay, not as forecast inputs.

Deliverables: `research/data/data_card.md`, `trial_inventory.csv`, `label_audit.csv`, `exposure_ledger.csv`, `target_definition.md` and `feasibility_decision.md`.

Gate: enough independent units and reliable targets for the chosen claim. If helper labels are unavailable, remove empirical helper-link claims or make them a separate, openly synthetic sensitivity study. If participant identities cannot be separated, do not claim unseen-person generalization.

## Stage 3 — Reproduce empirical movement patterns

On development data, reproduce free-speed distributions where available, speed versus local density, spacing, bottleneck headways and cumulative crossing curves. Separate wheelchair users, other participants and crowd compositions when labels permit. Compare with published findings using matching measurement definitions.

Quantify uncertainty at the participant/trial level rather than treating video frames as independent samples. Investigate coordinate units, smoothing, tracking gaps and selection effects before interpreting discrepancies.

Deliverables: reproducible extraction code, empirical figures, audit checks and `empirical_replication.md`.

Gate: measurements are consistent and their limits understood. Published mean speeds are evidence for this sample, not universal class constants.

## Stage 4 — Freeze the research protocol

Finalize the question, contribution and estimand after Stages 1–3. Candidate hypotheses:

- H1: adding mobility information lowers held-out forecast error beyond recent motion history.
- H2: adding verified relationship information lowers error beyond mobility and motion history, if the data support this test.
- Optional H3: inferred mobility retains useful forecasting performance compared with known labels.

Specify the null/no-improvement alternatives. Set a practically meaningful error threshold justified by the task, not chosen after results. Freeze primary metric, cohort weighting, query times, observation windows, splits, model budget, uncertainty method and secondary analyses. Define eligibility/non-completion rules and how censored runs are handled.

Reserve untouched trials where feasible; separate participants/cohorts and scenario blocks to the extent metadata permits. If all suitable data have already been inspected, use transparent grouped validation and reserve any new independent dataset for confirmation. Never call previously inspected data a prospective holdout.

Deliverables: dated protocol, fixed split manifest, data/source hashes and amendment log.

Gate: credible question, available data and adequate independent evaluation units. No fixed one-day completion promise; estimate effort once the audit establishes scope.

## Stage 5 — Build and verify the JuPedSim extension

Pin an established JuPedSim movement model and version. Begin with the existing reference replay as recoverable groundwork. Compare a common-parameter baseline with mobility-specific parameters calibrated only on development evidence. Use measured geometry and defensible body footprints; document limitations of circular wheelchair approximations.

Before selecting the engine, document which empirical behaviours it must reproduce: free-speed heterogeneity, slowing upstream, spacing, yielding/overtaking, doorway headways and verified companion coordination. Assess collision-free speed and AVM as candidates using the installed version's actual capabilities. Consider OSM/Vadere only if it offers a necessary capability that justifies changing platforms. Do not assume any model is a validated wheelchair controller. Select on prespecified development checks, not forecast-test performance. Heterogeneous parameters are a baseline capability, not our novelty claim. Separate the physical effects of size/speed from behavioural coordination through controlled ablations where feasible.

Add assistance or yielding only when necessary for the frozen question and supported by evidence. Make controller assumptions explicit. Random waypoint is not the default evacuation engine; use it only for a justified pre-movement scenario.

Test free motion, one pair, accessible/inaccessible openings, turns, merging and mixed queues. Check occupant conservation, overlaps, boundary penetration, exit definitions, deadlocks and several time steps. Choose numerical tolerances before evaluating candidates. Maintain a record of failures.

Validate multiple observables: crossing-time errors, flow, speed distributions, spacing and completion. Fit on development trials; evaluate on reserved trials without retuning. A matching final passage time alone is insufficient. Separate conditional replay from causal forecasting.

Deliverables: versioned simulator/configuration, verification tests, calibration trace and validation report.

Gate: acceptable physical/numerical checks and documented empirical agreement. If the extension fails, simplify or report failure instead of generating a large forecasting dataset with it.

## Stage 6 — Run the forecasting comparison

Use identical past-only observation windows and targets across information conditions:

1. Motion history and geometry baseline.
2. Baseline plus known mobility information.
3. Mobility plus verified relationship information, when feasible.
4. Optional inferred mobility/relationships evaluated separately from supplied labels.

Include simple travel-time/flow estimates and regularized regression; compare a small justified set of nonlinear/history models under the same tuning budget. Select learners using development validation only. Labels must not leak free speeds measured using future test movements. Show what is observed, supplied or inferred at prediction time.

If simulation is required for controlled relationship experiments, include matched scenarios, multiple seeds and uncertainty in plausible parameters. Label synthetic findings separately. Do not claim simulator-generated samples increase the number of independent real participants.

Report MAE, bias and appropriate tail errors; use paired, grouped uncertainty for incremental differences. Report total trial clearance separately from individual crossing error. Examine generalization across crowd composition and geometry where the data permit. Retain negative findings and failed cases.

Deliverables: frozen models, predictions, complete metrics, independent reconstruction audit and results report.

## Stage 7 — Optional mobility inference

Proceed only if independently labelled participants and valid splits are sufficient. Compare speed-only classification against richer past-trajectory features such as acceleration, stopping, turning and density response. Exclude identity, cap colour, recording artifacts and future information.

Report per-class precision/recall, PR-AUC where appropriate, probability calibration and uncertainty. Prevent the same person's windows from leaking across partitions. Test whether inferred features improve forecasting, not just classification accuracy. Synthetic-only recognition cannot establish real-world wheelchair detection. If identity classification is unsupported, consider estimating motion capacity instead, subject to another novelty check.

Deliverable: feasibility or evaluation report; explicitly omit the component if it does not support a defensible claim.

## Stage 8 — Write and audit the complete paper

Write around the actual contribution and outcomes. Include motivation, reviewed gap, hypotheses, dataset and label provenance, target, model assumptions, calibration, verification, leakage controls, baselines, results, uncertainty, limitations, ethics/data handling and reproducibility.

Use the course's required main sections after recovering the actual template from backup. Prepare an appropriately sized conference manuscript only after selecting a venue and checking its current requirements and indexing. Scopus indexing does not guarantee acceptance. Confirm authorship/contributions and declarations without inventing approvals.

Independently reproduce headline numbers from saved outputs. Audit citations, figure captions and claims. Distinguish prior exploratory work, real-data findings, conditional replay and synthetic evidence. Archive code/configuration versions and provide a clean README and one dependency file. Publish or update GitHub only on further authorization; raw participant data must follow source terms.

Final deliverables: manuscript source, verified PDF, figures, supplementary methods/results, reproducibility package and presentation. No claim of publishability solely because tests pass or a hypothesis is supported.

## Starting sources

- Geoerg et al., *The influence of individual impairments in crowd dynamics*: https://doi.org/10.1002/fam.2789
- Geoerg et al., *How people with disabilities influence crowd dynamics of pedestrian movement through bottlenecks*: https://doi.org/10.1038/s41598-022-18142-7
- SiME trajectory dataset: https://doi.org/10.34735/ped.2017.1
- JuPedSim model documentation: https://www.jupedsim.org/

Next action: execute Stage 1 and report the strongest competing papers and a go/no-go novelty assessment before rebuilding.
