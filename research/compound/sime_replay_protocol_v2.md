# SiME boundary-driven reference replay, revision 2

1 November 2026. New model-development and external-evaluation branch. The October 30 pilot and original compound engine remain preserved. The six pilot trials have already been inspected, including all crossing outcomes. Published SiME participant summaries and the documentation are prior information. This is exploratory calibration and subsequent held-out-run evaluation, not independent participant validation or preregistration of the original paper.

## Target and partitions

First establish an unassisted reference replay using current metadata, not an outdated documentation prefix table: development trials 1501 and 1507 (0.9 and 1.2 m). Test trials 1503 and 1505 (1.0 and 1.1 m) have not been acquired or inspected at this specification's creation. Do not use their outcomes to choose parameters or repair the model. They are new runs/configurations, not proven new participant groups. Record missing/invalid trials without replacing them. The October 30 pilot results remain development evidence only.

The simulated module spans the observed inlet x=-6 m to downstream head-centre crossing x=2.4 m, in the current trial metadata's actual wall geometry. Condition on empirical first-forward inlet crossing times and lateral positions (interpolate contiguous 25 Hz observations); these are exogenous boundary inputs. This is an observed-inflow-driven movement validation, not a complete evacuation forecast: future upstream arrival times are supplied. Compare individual transit times/crossing order, cumulative crossing curves and first-to-last passage duration. Include a no-interaction/free-flight reference using the same inlet inputs and desired speed.

Require finite unique id/frame records, continuous track crossings, inlet and downstream crossings for the entire tracked cohort and agreement with the metadata participant count before a trial can support a complete-cohort claim. Never replace a disappearing track with an exit. Do not feed downstream observations or future routes into simulation.

## Revised model and body interface

Use installed JuPedSim 1.4.2 CollisionFreeSpeedModelV2 as the established 2D movement backend. This replaces, rather than empirically validates, the rigid single-lane compound engine. Native pathfinding uses actual wall geometry; the exit-removal polygon is downstream of x=2.4 m so head-crossing observations remain comparable. No family/assistance controllers are active in this reference branch.

At an empirical inlet event, map the head projection to a circular body centre at x=-6 m. Clip lateral position only to the actual geometry eroded by radius+0.005 m, with a maximum allowed displacement of 0.25 m; record every conversion. Reject larger conversions. This is a declared head-to-body approximation, not an observed body measurement. When the inlet is occupied, delay admission at the same mapped point until collision-free; record waiting and retained identities, with a fixed 30 s maximum delay before declaring a failed replay. Never teleport an admitted agent or reduce radius per person to force insertion.

Calibrate only these 18 combinations on both development trials: global desired speed {1.2,1.4,1.6} m/s; common radius {0.18,0.22,0.24} m; time gap {0.6,1.0} s. Keep native agent/geometry repulsion defaults (8.0/0.1 m and 5.0/0.02 m). dt=0.02 s, observation samples every 0.2 s, horizon=300 s after the first inlet event (not chosen from target exits). All persons share the same speed; no empirical age/capability assignment is inferred. Failed/no-completion candidates remain in the tuning table and are ineligible for selection, not dropped as data.

Choose lowest equal-trial mean per-person absolute downstream crossing-time error, which is also transit-time error because inlet times are shared. Tie within 1e-9: larger radius, then time gap nearer 1.0, then speed nearer 1.4. Save all tuning results. Freeze selected parameters and all simulation/analysis sources before test retrieval/evaluation. Run selected parameters at dt=0.01 s as a numerical sensitivity; do not change selected parameters based on test outcomes. Audit conservation, admission times, finite positions, native geometry containment, and sampled inter-agent overlap (>0.001 m is a software-quality failure, not an accuracy result).

## Mapping and interpretation

Use raw header persID-to-PWD comments for confirmed identities; IDs are not stable between files. The full documentation identifies wheelchair PWD 34--40 and lists device dimensions and qualitative assistance state. It does not give assistant track identities or individual chronological ages for all participants. Preserve unknown values. Documented assistance need is not a per-trial assistant graph. Do not map ages by guessing correspondence with separately numbered article tables.

The first reference test omits disability and assistance. Wheelchair extension requires verified device mapping, body representation, assistant identity/state and a separately frozen protocol. Do not treat a circular agent with no escort as validation of a wheelchair-helper model. No indexed-publication, operational-safety or original A/M/F empirical performance claim follows from this test.

Report descriptive errors, individual crossing and flow discrepancies, count completeness and numerical sensitivity. No universal accuracy/pass threshold has been established. Compare against the free-flight reference rather than claiming success from completion or from passage duration alone (the known inflow may dominate it). Any poor test result is retained; do not retune and reuse the same trials as untouched tests.
