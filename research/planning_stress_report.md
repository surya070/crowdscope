# Development planning stress checks — 4 November 2026

## Design and evidence level

The suite configuration and code hashes were saved before outcomes in `output/planning_stress_v1/lock.json`. Fourteen prespecified conditions, sixteen development seeds 410004–410019, ten paired observation/request replicas per seed, seven policies. Outputs contain 2,240 scenario replicas and 15,680 policy records. There are **sixteen independent class-roster blocks**, not 2,240 independent crowds; cells and replicas share streams and must remain grouped in future analysis. No validation/final-evaluation seed was opened.

This is a static, synthetic demand/metadata experiment with fixed zone rosters, not a mobility recogniser, empirical staffing validation or a JuPedSim intervention. It follows accepted scope amendment A1. The default scenario has 80 occupants, four equal zones, six units, capacity two per unit, prevalence/error 0.2 and request rates 0.1/0.4. All assumptions and changed factors are recorded in the lock.

Conditions: base; unequal counts [40,24,12,4]; budgets three/nine; perfect observations; uninformative observations; low/high true prevalence with unchanged working prior; underestimated observation error; probability temperatures 0.5/2; equal demand; misspecified demand; and higher class-demand contrast. Common underlying uniform draws support paired comparisons. All cells and policies are retained.

## Results

Base condition mean unmet requests: probabilistic 3.4375, hard observed 3.4375, hard posterior 3.5000, population-only 3.5000 and known-class 3.2375. Thus the small gain over hard posterior does not extend to the stronger hard-observed comparator in the base setting.

Probabilities have lower mean loss than hard observed in four cells (unequal zones, more resources, uninformative observations, high demand contrast) and tie in ten. Improvements range from 0.03125 to 0.0625 requests per scenario. These are small descriptive development effects; no superiority/significance claim follows, and cell counts are not independent statistical votes.

Under low true prevalence with the original working prior, probabilistic loss is 0.075 requests worse than hard posterior/population-only. Under misspecified demand it is 0.0375 worse. Under high true prevalence it improves on hard posterior by 0.18125 but still ties hard observed. Incorrect probability or demand assumptions can therefore remove or reverse a planning benefit relative to other baselines.

In the nine-unit setting, probabilities give 0.9625 unmet requests versus 0.99375 hard observed and 1.19375 mean-only. This is an illustrative difference between expected shortfall and shortfall of expected demand. It must not replace the primary six-unit condition retrospectively.

The hard-posterior comparator remains weak at the primary prevalence/noise: positive posterior is exactly 0.5 and the frozen tie rule assigns zero. Report hard observed and population-only results alongside it. Do not change the tie convention after inspecting results.

## Negative controls and audit

- With perfect observations, probabilistic, known-class and hard-observed full-distribution policies choose identical allocations.
- With error 0.5 correctly modelled, probabilities equal the prior and choose the population-only allocation. A noisy hard-label policy may still make unhelpful changes.
- With both true and modelled demand rates equal, mobility probabilities cannot affect the full-distribution planner; all information variants choose identical allocations. The mean-only policy is a different objective and can behave differently even with identical inputs.

`research/audit_planning_stress.py` checks source hashes, grouping, request totals, feasible budgets, every realised loss, perfect-demand lower bounds and the exact allocation identities above. Numerical equality on controls validates implementation, not scientific novelty.

## Decision and next gate

Stress implementation and controls pass; **broad benefit remains unestablished**. The defensible candidate finding is conditional value of uncertainty, including regimes where it changes nothing or harms decisions. Demand is assumed and conditional independence remains a model restriction. More model names would not resolve these limitations.

Before the final comparison: integrate occupancy derived from actual trajectories without assigning unsupported demographic labels; distinguish supplied/synthetic metadata; freeze a compatible revised run manifest under A1; retain the original primary comparison and all stronger baselines; finish closest-method literature checks. Do not inspect reserved final seeds until that release gate is explicit. Final inference must average within each seed and use paired block-level uncertainty, not frame/replica pseudo-replication.

An interactive demonstration and manuscript can then explain the complete density → probability → allocation pipeline with evidence-level labels. No operational evacuation-time improvement, reliable child/wheelchair recognition or acceptance claim is supported yet.
