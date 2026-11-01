# SiME revised reference replay

**Development and preselected held-out reference replays completed. The results provide limited support for an unassisted, observed-inflow-driven module; the original rigid wheelchair-helper model remains empirically unvalidated.**

## What changed

The replay uses the installed JuPedSim 1.4.2 CollisionFreeSpeedModelV2, actual wall geometry, explicit observed inlet events at x=-6 m, collision-free delayed admission, and individual head-centre crossing measurements at x=2.4 m. The original source and synthetic A/M/F comparison are preserved. Every planned development candidate, including failed completion cases, is saved.

The previous frame-0 overlap problem is handled through a different experimental boundary: people enter the model when they cross the upstream inlet, instead of pretending the full cohort is visible at frame 0. This conditions on real upstream arrival times, including future inlet events. It is therefore a module replay under measured inputs, not an end-to-end clearance forecast.

## Development results

All 136 person-trial records in trials 1501 and 1507 were admitted, crossed the downstream measurement plane and left the simulation, with no sampled inter-agent overlap. All measured source crossings and reported errors were independently reconstructed from the raw TXT records. Of 18 predeclared parameter combinations, 13 completed both development trials and were eligible for selection.

Selected parameters: desired speed 1.6 m/s, common radius 0.18 m, time gap 1.0 s. The equal-trial mean individual crossing-time error was 5.412 s, compared with 13.425 s for independent free flight under the same inlet inputs. These are calibration errors; they are not held-out accuracy estimates.

- Trial 1501 (67 people): crossing MAE 7.511 s; observed first-to-last passage 53.284 s, simulated 65.974 s; last-crossing error +12.655 s; maximum inlet admission delay 3.330 s.
- Trial 1507 (69 people): crossing MAE 3.313 s; observed first-to-last passage 40.037 s, simulated 42.477 s; last-crossing error +1.964 s; maximum inlet admission delay 2.433 s.

The largest sampled nominal-body wall penetration was 2.86 cm despite native agent centres remaining inside geometry. This warning is retained: the calibrated circular body representation is not a strict full-footprint geometry guarantee. One inlet head-to-body conversion in trial 1507 shifted lateral position by approximately 3 cm; all conversions are logged. Do not describe completion as proof of realistic body mechanics or safety.

## Numerical sensitivity

- Trial 1501: fine-step status completed; MAE changed by +0.262 s and final crossing by -1.880 s at dt=0.01 versus 0.02 s.
- Trial 1507: fine-step status completed; MAE changed by -0.080 s and final crossing by -0.080 s at dt=0.01 versus 0.02 s.

## Frozen held-out evaluation

The selected model was applied without retuning to trials 1503 and 1505 at widths 1.0 and 1.1 m. All 135 tracked person-trial records had source inlet and downstream crossings, agreed with metadata counts, were admitted, crossed the simulated measurement plane and left the model. Source and parameter hashes still match the pre-test freeze. The equal-trial mean crossing MAE was **4.736 s**, versus **13.576 s** for free flight, a **65.1%** reduction against that simple reference. This is not a comparison against every established crowd model.

- Trial 1503 (66 people): MAE 5.343 s, bias +4.934 s; observed first-to-last passage 46.850 s versus simulated 52.767 s; last crossing +5.629 s late.
- Trial 1505 (69 people): MAE 4.129 s, bias +2.348 s; observed first-to-last passage 43.358 s versus simulated 45.788 s; last crossing +1.875 s late.

The model generally overestimated crossing times. Maximum sampled nominal-body wall penetration on test trials was 2.82 cm; inter-agent overlap was zero at sampled checks. This limits physical fidelity despite successful accounting and centre containment.

### Held-out time-step sensitivity

- Trial 1503: fine-step status completed; MAE changed by +0.617 s and final crossing by -1.224 s at dt=0.01 versus 0.02 s.
- Trial 1505: fine-step status completed; MAE changed by +1.078 s and final crossing by +3.098 s at dt=0.01 versus 0.02 s.

The fine-step equal-trial MAE was 5.583 s. Parameters were not retuned. Numerical convergence is not established, and the coarse result must not be reported as time-step independent.

## Participant mapping

Raw headers were linked to the official documentation to identify all seven wheelchair users in each of two previously inspected trials (14 track-to-PWD mappings). Device length/width and qualitative assistance descriptions are recorded without copying medical diagnoses. Assistant track identities and individual chronological-age mappings remain unknown. An assistance description is not an observed per-trial helper graph. The reference replay uses current metadata indicating zero disabled participants; a wheelchair/assistance extension is not silently inferred from it.

The older documentation has a run-prefix table inconsistent with current metadata and headers. Current raw-file labels take precedence for run classification, while header PWD identities and documented device descriptions support role mapping.

## Interpretation and remaining work

These are held-out runs at intermediate widths, not proven independent participant groups. The observed inlet schedule includes future upstream arrivals, so these errors do not validate an end-to-end remaining-clearance predictor. Head-centre crossings do not measure full-body clearance or alarm-to-evacuation time. The evidence supports limited conditional reference-model transfer to two new runs while retaining body-geometry and numerical limitations. No universal acceptance tolerance, operational-safety certification, original A/M/F empirical ranking or wheelchair-assistance benefit is established.


## Files and sources

- `selected_freeze.json`: selected settings and source hashes before test acquisition.
- `calibration_trace.json`: all 18 candidates, including failures.
- `report_summary.json`: independently audited metrics and sensitivity.
- Dataset: https://doi.org/10.34735/ped.2017.1
- Official documentation: https://ped.fz-juelich.de/data/experiments/2017.06.10_Wermelskirchen_SiME/data/2017sime/2017sime_documentation.pdf
- Movement model: https://pedestriandynamics.org/models/collision_free_speed_model/

Publication note: raw inputs and participant-level records are not redistributed. Use the original-source acquisition and replay scripts to regenerate crossing records. The documented wheelchair-mapping investigation is historical context, not a role assignment used by the unassisted replay.
