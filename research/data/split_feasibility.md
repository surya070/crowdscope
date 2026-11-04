# Split feasibility and decision — 4 November 2026

## Finding

The current SiME snapshots do not establish a clean, joint trial-disjoint and person-disjoint evaluation for the full dataset. Known cross-run ID links connect all fourteen trials, and most tracks have no persistent ID. A random split of frames/windows would severely overstate independence. Holding out exit width does not remove repeated participants or demographic/condition confounding.

Holding out known wheelchair individuals could test a narrow positive-class transfer question, but would not establish person-disjoint negative controls while their identities/classes remain incomplete. Mixed-person trials also share crowd context. Do not train a binary wheelchair classifier by labelling every unregistered track negative.

## Decision

**Conditional go for Stage 3 protocol design using both real and synthetic evidence. No-go for a claim of validated wheelchair/child recognition or an independent real staffing benchmark.**

Recommended primary route: probabilistic crowd-state estimation and one capacity-limited planning problem, initially with explicitly uncertain supplied mobility metadata (plan path C) and scenario-defined demand (path D). A movement-only recogniser is a separately gated exploratory module. If it cannot outperform context-aware baselines with defensible labels, keep movement profiles/unknown states and retain the result.

JuPedSim supplies controlled trajectories, true simulated states, congestion, scenario changes and intervention comparisons. Use an established model with a frozen version; CFSV2 is recoverable from the prior study. Current official documentation lists CFSV2 with per-agent parameters and describes V3 as a different steering variant: https://www.jupedsim.org/stable/pedestrian_models/ . Selecting a newer model requires its own validation rather than assuming it improves the study.

Do not use a synthetic training/test generator that makes wheelchair status equivalent to a fixed speed threshold. Overlap parameter distributions, vary density/geometry within class and test shifts. Keep simulator calibration runs separate from evaluation scenario blocks. Synthetic success establishes behaviour under stated assumptions, not real demographic recognition.

## Remaining actions before freezing a protocol

1. Verify authoritative label semantics and available negative/control annotations; reconcile persistent-ID namespace.
2. Verify source terms and whether an additional genuinely independent, compatible trajectory dataset is available. No new trajectories or outcomes were opened in this stage.
3. Specify the resource/service and demand mechanism; test sensitivity to assumed need rather than equating wheelchair presence with assistance need.
4. Finish the closest-method literature checks recorded in Stage 1 before claiming novelty.
5. Predeclare the exploratory/confirmatory evidence level, grouped splits and reuse of all previously exposed trials.

If independent semantic labels remain unavailable, write a transparent simulation-led framework paper with empirical movement checks and explicit recognition limitations. A wider simulator does not erase those limits.
