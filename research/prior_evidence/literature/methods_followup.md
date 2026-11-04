# Stage 1 methods follow-up and gate decision

Date: 2 November 2026. This completes the currently accessible scoping pass, not a comprehensive systematic review. Some full texts remain inaccessible. Their unobserved contents are unknown, not evidence of an absent method.

## Accessible full-text anchor: Uhlík, FEMTC 2024

Source: https://files.thunderheadeng.com/femtc/2024_d1-03-uhlik-paper.pdf

Title: Real-time RSET Prediction Based on Simulation Dataset Using Machine Learning: A Complex Geometry Case Study.

Methods/results inspected across the nine-page paper:

- Pathfinder generates 100 parameter configurations, each repeated 20 times.
- Seven inputs summarize count, exit distances, occupant spacing and mean walking speed. Output is mean RSET across repeats.
- Nine regression families are compared. The paper describes repeated nested five-fold cross-validation and also an 80/20 designation; the precise relationship deserves clarification before reproducing its splits.
- It tests one complex university geometry. The paper explicitly limits generalization to that task.
- Reported ANN test MAE is 3.81 s. This simulated mean-RSET error is not comparable directly with our former short-queue remaining-time errors.
- No short-history-versus-mobility-label experiment is presented in this paper. It motivates camera-derived inputs but evaluates simulation surrogates.

Implication: basic speed-aware surrogate prediction and broad learner comparisons are already established.

## Related full-text lead: Uhlík et al., DIBE 2024

DOI: https://doi.org/10.1016/j.dibe.2024.100461

Institutional PDF: https://dspace.vut.cz/bitstreams/b1b30790-e65a-4abe-9de9-170313f515db/download

The indexed institutional text exposes methods including mean speed, occupant/exit distances and train-fitted scaling. Direct retrieval encounters an Anubis access-denied page. Therefore this is a partial indexed-text extraction, not a claim that we obtained the entire article. The FEMTC paper cites it as preceding work, providing backward citation tracing. Full verification remains pending.

## Tunnel surrogate metadata resolved

Institutional source: https://portal.research.lu.se/sv/publications/real-time-prediction-of-tunnel-evacuation-time-using-machine-lear/

DOI: https://doi.org/10.1016/j.ssci.2026.107348

The institutional abstract reports 50,910 Pathfinder simulations, XGBoost and MLP, nested validation, and evaluation against ten full-scale experiments. It supports taking real-data validation and strong tree learners seriously. It does not establish a matched information-value test. Publisher and institutional date fields differ; use verified online publication metadata in a final bibliography.

## Closest competitor still unresolved: FCRR-Net

https://doi.org/10.1016/j.ress.2026.113346

Publisher preview describes temporal visual representations, structural descriptors and ablation experiments. We cannot determine exactly which descriptors or whether mobility information is ablated. Direct retrieval returns HTTP 403. No official code/dataset repository was identified by the targeted search; this does not prove none exists. Online-first chronology also remains unresolved given the January 2027 issue date.

## Additional close predecessor: Deng et al. 2022

https://doi.org/10.3390/fire5060204

Title directly addresses individual characteristics and real-time congestion in evacuation-time estimation. The publisher endpoint returned HTTP 429; the FEMTC primary paper discusses it as a Pathfinder stacking surrogate. Full input/label extraction is pending. Its title alone is sufficient to reject a broad claim of first individual-characteristics-aware forecasting, but insufficient to decide whether our precise ablation is new.

## Disability-model competitor

https://doi.org/10.1016/j.amc.2023.128297

Publisher preview describes crutch users, wheelchair users and other participants under a modified social-force model, with comparisons to experimental movement patterns. It addresses heterogeneous simulation, rather than establishing the proposed mobility-information comparison. Full calibration/validation design remains unknown.

## Gate outcome

**Conditional go for data feasibility; hold final novelty wording and large implementation.**

The proposed direction has enough specificity to justify checking SiME labels and targets. An empirical feasibility audit is useful even while the remaining full texts are sought. It is premature to claim a novel algorithm or rebuild a full relationship simulator.

Provisional focus: *Value and robustness of explicit mobility information for short-observation crowd-passage forecasting.*

Candidate comparisons to freeze only after data audit:

1. Identical recent trajectory history and geometry for every condition.
2. Add known mobility labels or independently measured capability, with their time-of-availability explicit.
3. Test uncertainty/missingness in that extra information, using realistic mechanisms established on development data.
4. Evaluate at several observation horizons, with grouped trial/cohort splits and composition transfer only if independent data permit.

Assistance and family features remain optional. They require verified labels and independent examples. Wheelchair recognition is a separate feasibility question; RGB-D and wearable recognition prior art does not establish trajectory-only recognition in a congested crowd.

Primary design insight: explicit labels may matter most with short or ambiguous observations; long histories may already reveal capability. This is a hypothesis to test, not a result or proven literature gap. Compare against a history baseline that has enough capacity to capture the same observable effects.

## Unfinished literature work carried forward

- Obtain S03–S07 and Deng full methods legally through institutional/open access when possible. No requests to authors were sent.
- Perform structured forward citation tracing and database exports if institutional access is available. No Scopus or Web of Science search is claimed.
- Extract prediction horizon, label availability, participant reuse, split unit and feature ablations from each closest paper.
- Revisit novelty before protocol freeze. If a direct predecessor exists, frame an empirical replication/robustness contribution or change the question.

Next stage, after the user's review: audit SiME raw metadata and identity mappings from the verified backup. Do not build or fit a model at that stage.
