# Original scope amendment A1 proposal — accepted

Accepted by the user on 4 November 2026. Active decision record: `research/scope_amendment_A1.md`. The proposal text below is retained as history.

Date: 4 November 2026. Motivation: repeated generic-crowd numerical failures and residual timestep sensitivity in matched empirical replay. All this development evidence was visible when proposing this amendment. Original protocol and locks remain unchanged.

## Recommended next route

Keep the paper's primary question: whether uncertain mobility information improves zone composition estimates and finite-budget allocation compared with hard labels. Implement and verify the resource planner next. Use recorded trajectories for observed occupancy/movement; use controlled artificial metadata and demand for the mathematical planning benchmark. Keep their evidence levels explicit.

Treat JuPedSim as a documented, exploratory what-if component with retained failure cases. Do not require a universal clearance simulator to implement a static planner, and do not use its unstable clearance times as the primary endpoint. Do not claim that allocations improve evacuation speed or staffing safety.

The first planner benchmark can use fixed controlled zone rosters, then recorded or synthetic snapshot occupancies, with scenario membership/demand assumptions stated separately. Neither a simulated class assignment nor unknown SiME labels become real recognition ground truth. Report uncertainty, shifted priors and both hard-label controls.

This amendment changes the dependency gate: Stage 7's exact mathematical and conditional planning checks may proceed before a validated general-purpose crowd-motion backend. It does **not** release final evaluation or change primary endpoint/comparator, relax spatial tolerances, repair tests using evaluation labels, or declare novelty established. Before an independent evaluation, freeze a new compatible scenario/run manifest and update the evidence/limitations statements.

## Alternative

Keep the original simulator prerequisite and continue numerical/behavioural engineering before planner work. This may require a different supported backend or geometry treatment and fresh verification. No reliable completion date is established.

Pending decision: adopt the recommended planning-first scope or continue simulator validation first. No implementation dependent on this amendment has run.
