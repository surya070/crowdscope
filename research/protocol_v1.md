# Development protocol v1 — 4 November 2026

Status: **development design frozen; evaluation release blocked pending verification**. No new experiment has been run. This is a simulation-led exploratory study with empirical movement checks. Novelty, independent real semantic recognition, real service-demand validation and current SiME terms remain unresolved. A software/demonstration milestone is not course or publication acceptance.

## Question and contribution

When does propagating uncertain mobility information improve zone-level crowd estimates and limited-resource allocation over using hard labels?

The framework accepts trajectories, geometry and optional uncertain mobility metadata. It outputs occupancy/density/movement, expected composition, uncertainty and one allocation decision. A later movement-based recogniser may supply the probabilities only after its separate feasibility gate. Version 1 uses a declared noisy metadata channel; it does not claim to detect wheelchairs or children from movement.

## Scope and resource definition

Primary experiment: allocate six abstract support units among four spatial zones at one observation time. Each unit can fulfil two simultaneous support requests during the planning epoch. Units are assumed prepositionable with no travel delay. Requests are realised after the decision and hidden from the planner. This is a capacity-allocation abstraction, not a trained staffing or clinical model. No allocation changes simulated walking speed in v1; therefore no claim that it shortens evacuation time is permitted.

Agents have binary **scenario mobility-profile membership** C, not inferred medical identity. Classes have overlapping desired-speed distributions and share crowd constraints. The support-request probability is scenario-defined and never equated to wheelchair status. Age, helpers, physical pushing, CCTV and sequence models are deferred.

## Mathematical specification

At t=10 s use only visible active agents and trajectories in [8,10] s. Four non-overlapping geometry-defined zones cover the walkable interior; exit handling and exact polygons must be committed before generating evaluation runs. A boundary belongs to the lowest numbered eligible zone; every active agent must be assigned exactly once. Compute count, density in people/m², mean speed and stopped fraction (speed below 0.1 m/s). Use causal differences; do not use future positions or z/height.

For controlled metadata experiments, C_i ~ Bernoulli(pi), and observed bit O_i has symmetric error eta. The primary pi=0.2 and eta=0.2 are illustrative assumptions, not empirical estimates. Conditional probabilities are:

```
P(C=1 | O=1) = pi*(1-eta) / (pi*(1-eta)+(1-pi)*eta)
P(C=1 | O=0) = pi*eta / (pi*eta+(1-pi)*(1-eta))
```

At eta=0.5 the observation is uninformative and posterior equals prior. At eta=0 it is perfect. Handle zero-denominator impossible events explicitly. Ground-truth C is stored for evaluation only. Scenario membership generation is independent across agents in the primary setting; movement/occupancy may nevertheless induce zone-specific composition. Because exiting selectively changes active prevalence, use the known initial pi only as a **working prior**, not claim perfect calibration among survivors. Measure this discrepancy; a sensitivity variant may use a development-estimated active-population prior frozen before evaluation. Never estimate a deployment prior using evaluation labels.

Expected zone composition is sum_i p_i for active i in zone z. Assess against the actual simulated class count. Use independent-Bernoulli count distributions as a working approximation and check coverage; do not assert independence after conditioning on crowd dynamics.

Scenario requests R_i | C_i ~ Bernoulli(r_C), with primary r_0=0.1, r_1=0.4. The planner uses q_i=r_0+(r_1-r_0)*p_i. True requests use true C and a separate seeded random stream. Conditional requests are independent in the primary mechanism. Expected loss is:

```
D_z = sum of requests in zone z
L(a,D) = sum_z max(0, D_z - 2*a_z)
a_z integer >= 0; sum_z a_z = 6
a* = argmin_a E[L(a,D) | available observations]
```

Compute each assumed zone demand distribution with a Poisson-binomial recursion; enumerate all feasible allocations for four zones and six units. Resolve ties lexicographically. Verify against hand-computable examples before interpreting results. Full-distribution planning can differ from planning only with expected demand because shortfall is nonlinear; benefit is a hypothesis, not guaranteed.

## Matched policies

1. **Homogeneous:** everyone uses fixed prior pi, with the same full-distribution planner.
2. **Hard observed labels:** p_i=O_i. This represents treating noisy supplied labels as certain, not classifier argmax.
3. **Hard posterior labels (primary comparator):** p_i=1[P(C_i=1|O_i)>0.5], ties assigned zero, same planner.
4. **Probabilistic (primary method):** retain p_i, same planner.
5. **Mean-demand ablation:** retain p_i but minimise sum_z max(0,E[D_z]-2*a_z).
6. **Known-class information:** p_i=C_i, but requests remain unknown. This is an information reference, not perfect foresight.
7. **Perfect-demand reference:** choose allocation after seeing realised D, clearly labelled non-deployable lower bound.

Report both hard-label policies to avoid a weak-comparator-only claim. Use identical initial conditions, active occupants, observations and realised requests for all policies. The planner cannot access C, future movement or realised requests except in the explicitly labelled references.

## Primary endpoint and analysis

Primary endpoint: realised unmet requests per scenario block, probabilistic minus hard posterior policy. Negative differences favour probabilities. Average over ten preassigned metadata/request replicates within each crowd block; the independent evaluation unit remains the crowd block. Do not count replicas or frames as independent experiments.

Report paired mean difference and a 95% block-bootstrap interval (10,000 resamples, seed 9041), plus absolute means, standard deviations, raw block differences and worst-block results. Report all matched policies and clarify the single primary comparator. No minimum practical effect is asserted without an external service definition; this exploratory endpoint measures magnitude and precision, not a safety threshold.

Secondary endpoints: zone composition MAE and Brier score; 90% count-interval coverage/width; density summaries; mean-demand ablation; computational runtime. Passage forecasting is deferred until these modules pass; adding it requires a dated secondary protocol. Recognition accuracy is not an endpoint for this metadata-channel experiment.

## Simulation design and grouping

Candidate engine: JuPedSim 1.4.2 CFSV2, preserving prior recoverability. This is a pinned development choice, not a claim it is latest or best. Verify engine availability, boundary behaviour, per-agent parameters and empirical plausibility before releasing an evaluation lock. Do not switch engine because one yields favourable hypotheses.

Development settings: 80 agents, class prevalence 0.2, overlapping desired speeds (class 0 uniform 0.8–1.5 m/s; class 1 uniform 0.6–1.3 m/s). These are deliberately illustrative movement profiles, not validated wheelchair/child parameters. Use a shared radius of 0.22 m initially so size does not encode class. Layouts: room-to-door, corridor-to-door and a turn-to-door geometry. Development widths 1.0 and 1.2 m; sensitivity widths 0.9 and 1.4 m. Exact dimensions, spawn sampling and model defaults remain release-blocking configuration items.

Reserve 120 seed blocks: 40 development, 20 validation and 60 sealed evaluation. All layouts, widths, observation corruptions and demand variants sharing an initial seed stay in the same partition. Seed reservation alone is not a run-level frozen manifest. Independent seeds are synthetic replications, not new human participants or a validated target population. Final precision will depend on block variability; this is a fixed computational budget, not a power-derived sample size.

Use separate deterministic streams for spawn, membership, motion parameters, metadata and requests. For each block preserve all ten replicas, including ties and no-benefit cases. Paired policy variants never regenerate movement.

## Predeclared sensitivity priorities

After the primary mechanism, change one factor at a time: eta in {0,0.1,0.3,0.5}; pi in {0.05,0.5}; budgets {3,9}; request probabilities {(0.1,0.1),(0.05,0.6)}. Use common random numbers where mathematically appropriate. Include prior misspecification and probability distortion (logit temperature 0.5 and 2) as explicitly secondary stress tests. The equal-demand setting is an important negative control: mobility information should have no systematic allocation value there.

Correlated demand, correlated metadata errors and held-out geometry are optional extensions requiring a specific release amendment. Do not expand a large grid before core verification. Report sensitivity dependence and do not select the most favourable cell as the new primary outcome.

## Real-data role and leakage controls

All fourteen archived SiME trials are exposed development data. Recover geometry and final label provenance before using them. Match head-position measurement conventions when comparing speed/spacing/flow; circular bodies in simulation are not head positions. Empirical calibration and subsequent same-trial fit checks are not external validation. Record metrics and data partitions before calibration.

No person-disjoint semantic recognition claim is supported currently. A future recogniser requires independently supported positives/negatives, identity-aware grouping, nested calibration and out-of-fold probabilities for downstream training. It cannot inherit synthetic-channel calibration claims.

## Failure handling and release gates

Missing active agents, invalid geometry, overlaps, wall penetration, duplicate assignments, count non-conservation, undefined posterior events and incomplete simulations are explicit failures. Preserve them and their causes. No silent failure exclusions. A t=10 snapshot after everyone exits produces zero demand and is retained. Low occupancy or one occupied zone is retained and reported; do not filter it after seeing method differences.

Release requires: trajectory/count fixture tests; numerical simulator tests including timestep refinement; exact planning checks; zero oracle leakage; exact geometry/spawn/parameter manifests; resolved software availability; explicit empirical-terms status; and closure or bounded reporting of the nearest-method literature checks. Until then no sealed evaluation outcomes may be inspected. A bug fix after evaluation access requires an amendment and the results remain exploratory.

## Stage decision

Stage 3 design is documented and hashed. Proceed to Stage 4 ingestion/state fixtures after user review. Do not call this a confirmatory preregistration or a final benchmark freeze. The first implementation should establish units, counts and causal observations before building the recogniser, optimiser or polished app.
