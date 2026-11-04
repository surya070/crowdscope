# Stage 7 planner verification and development pilot — 4 November 2026

## Implementation and verification

`src/resource_planning.py` converts membership probabilities to request probabilities using the declared conditional demand model, computes Poisson-binomial zone demand distributions and exhaustively searches feasible allocations. Four zones and six units have exactly 84 feasible allocations. Each unit handles two requests in the primary scenario. Cost is expected unmet requests; equal-cost allocations use the frozen lexicographic tie rule. Realised demands enter only the evaluation function, not a deployable planning policy.

Nine new tests cover feasible allocations, known demand, zero budget, empty zones, realised shortfall, the law of total probability, comparison against exhaustive binary request outcomes using exact rational arithmetic, a case where full-distribution and mean-only planning differ, and invalid inputs. All **39 tests** pass across the project. The initial brute-force test used float equality to select among exactly tied objectives; exact rational arithmetic corrected the test oracle, without changing planner policy or tolerance.

## Small pilot

`research/run_planning_pilot.py` freezes its code/configuration before execution in `output/planning_pilot_v1/lock.json`. Four development seeds (410000–410003), ten paired metadata/request replicas per block, 80 fixed occupants divided equally across four zones. Latent class prevalence 0.2; symmetric observation error 0.2; request probabilities 0.1/0.4. These are assumed scenario distributions, not measured assistance needs or recognised wheelchair identities. The pilot is static and does not depend on simulated movement.

Mean realised unmet requests over forty paired replicas:

- Homogeneous and hard posterior: 3.050 each.
- Probabilistic, hard observed and mean-demand: 2.975 each.
- Known-class information: 2.600.
- Perfect realised-demand reference: 1.550; this uses future requests and is not deployable.

The probabilistic-minus-hard-posterior mean is -0.075 requests, but block differences are +0.2, -1.3, +0.2 and +0.6. Three of four blocks favour the comparator. No robust or statistically established advantage is claimed. The pilot does not establish value beyond hard observed labels or the mean-demand method. At the primary prior/noise settings, hard posterior predicts no positive members under the fixed tie rule; its weakness must remain visible.

Forty replicas are not forty independent crowds: there are four independent class-roster blocks with ten conditional observations/requests each. No confirmatory interval or significance claim is appropriate from this smoke pilot. All seven policies and all realised outcomes are saved, including negative block effects.

## Gate and next work

**Planner implementation and small-case optimality checks pass. General benefit is unestablished.** Scope amendment A1 allows this work while clearance simulation remains limited. Final evaluation seeds are untouched.

Next development stress checks should vary zone occupancies, budget, prior/noise assumptions and demand misspecification, preserving all prespecified outcomes. Include equal-demand and uninformative-channel negative controls. Use a separately dated development configuration; do not replace the primary comparator or select favourable cells as headline results. Repeatedly tuning against the four pilot blocks will not create independent evidence.

Before a locked final comparison, freeze a compatible scenario manifest with grouped seeds, the one primary endpoint/comparator, all baseline policies, demand assumptions and treatment of uncertain/absent metadata. Finish the literature gate. The mathematical planner optimises the assumed distribution by construction; research value requires evaluating outcomes under independently specified truth, shifted mechanisms and explicit evidence limits.
