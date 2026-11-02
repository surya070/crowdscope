# Candidate target and observation restrictions

The audited reference event is the first forward crossing of the head-centre plane x=2.4 m, linearly interpolated between adjacent recorded frames at 25 Hz. This matches the earlier replay measurement. It is not full-body exit or alarm-to-evacuation time. Adjacent-frame interpolation avoids silently bridging missing sections.

For a completely observed, predeclared cohort C, T_C is its last crossing and the remaining-passage target at t is max(0,T_C-t). Define t against the trial recording clock or an explicit observation anchor. A first-to-last crossing span is a descriptive duration and is not itself the remaining time at an arbitrary checkpoint.

Trial 507 cannot currently supply a verified all-92-person T_C. The maximum of its 91 observed crossings is not a complete-crowd clearance label. Excluding the missing person after seeing the outcome would change the estimand and potentially remove a particularly important wheelchair user. Treat it as incomplete; resolve source coverage or use a prospectively defined alternative target with explicit limitations.

Motion inputs must come only from frames at/before the query. Do not use the final roster, future arrival times, whole-track free speed or future-observed labels unless their availability is explicitly an oracle/reference condition. Inlet schedules used by the old replay include future information and cannot serve as live forecast inputs.

Candidate designs to evaluate at protocol stage:

1. Known-cohort forecasting, only if an independently available roster and adequate past observations exist. Roster membership alone does not reveal unobserved future positions.
2. Forecasting for a cohort defined at an observation boundary, with later entrants excluded by a predeclared rule. This is a different target and must be named accordingly.
3. Conditional arrival-driven replay for simulator validation. Report it as a conditional module test rather than forecasting.

Do not choose the measurement plane or cohort rule to maximize a model's observed advantage. All trial outcomes inspected in this audit belong to development evidence.
