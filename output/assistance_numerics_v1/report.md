# Operational configuration diagnosis and verification

2 November 2026. **A practical development configuration passed the retained and extended movement gate. This is numerical verification of an escort approximation, not empirical validation of wheelchair pushing.**

## Diagnosis

Previous failures persisted without assistance links, so the pairing rule was not their sole cause. Screened four prelisted operational configurations with the same six fixtures, threshold controller and .02/.01/.005 s steps: collision-free speed defaults; neighbour repulsion strength reduced from8 to2.6; reduced strength plus interaction range widened from.1 to.3m; and fixed-seed AVM defaults.

Default collision-free speed completed all six cases but failed mixed-queue timing. Reduced repulsion passed all six. Wider interaction produced incomplete runs and pair-spacing failures. The tested AVM configuration produced spatial-gate failures in some cases. All results are preserved, including failures. This does not establish that AVM is generally unsuitable.

Reducing neighbour repulsion removed the observed queue timing sensitivity in this screen. That supports a parameter-dependent interaction explanation. It does not isolate a source-code defect or prove an analytical stiffness mechanism. This changes the behavioural model as well as its numerical performance: faster clearance is not evidence of greater realism.

## Selected configuration

JuPedSim1.4.2 CollisionFreeSpeedModelV2; neighbour repulsion strength2.6; other installed native defaults; helper native time gap.3s, other agents.8s; existing threshold coordination rule; candidate integration step.005s. No positions overwritten, no extra gap correction, no tolerance relaxed. Configuration and source hash recorded in `research/assistance/verified_candidate.json`.

Same assumed circular bodies and assistance gain as earlier. This is escorting with an illustrative speed effect, not a contact/force/elongated-footprint model of wheelchair pushing. No real helper data calibrated this parameter choice.

## Full verification

After selection, tested all six original multi-pair fixtures, all four earlier single-pair fixtures including their original geometry, and two queue perturbations shifting extra pedestrians by ±.05m. Steps .01/.005/.0025s; no failed case dropped.

All twelve cases passed at every step. Largest clearance spread is .010s, below the unchanged max(.2s,1%) criterion. The formerly problematic mixed queue completes in12.28s across all tested steps. Shifted queues give12.34/12.33/12.33s. Serial two-pair doorway clearance is13.270/13.270/13.2675s; two-pair turn16.080/16.075/16.0725s. These are synthetic fixture outcomes, not expected human evacuation times.

Each run checks finite positions, occupant conservation, nominal-circle overlap/wall intrusion, pair spacing and speed bounds at every native integration step. All reported checks pass for the selected candidate. Native positions remain controlled by JuPedSim. Counting uses separate people; removal follows each nominal circle's downstream crossing.

## Records and interpretation

72 initial screen runs and36 verification runs are saved. The selected candidate accounts for54 passing runs across both stages. An independent saved-record audit checks completion, identity unions and timing summaries; it does not independently reimplement all integration-step geometry.

Locks, source snapshots, all native sampled trajectories and gate records are preserved. Earlier failed versions remain unchanged. The selection and verification are adaptive development, not independent human validation or a prospective forecasting benchmark. A deterministic twelve-fixture suite does not establish arbitrary-crowd, geometry or population validity.

## Next stage

The numerical gate now permits designing a **separate synthetic linkage-information experiment**. Before generating comparison data, fix scenarios, pair assignments, observation features, training/validation/test seeds and analysis rules. Compare mobility plus observed history against additional correct links and include missing/shuffled-link controls. Do not select the movement model by forecast-feature advantage. Test zero assumed speed gain as a sensitivity: a positive assistance effect is not established by programming a positive gain.

Keep real SiME forecasts as empirical evidence and any new relationship results explicitly synthetic. Mechanical pushing or empirical assistance-validation claims remain outside this candidate's support.

API references: https://www.jupedsim.org/v1.4.2/_modules/jupedsim/models/collision_free_speed_v2.html and https://www.jupedsim.org/v1.4.2/_modules/jupedsim/models/anticipation_velocity_model.html . These document parameters; they do not validate the parameter choice.
