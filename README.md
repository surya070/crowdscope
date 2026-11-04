# CrowdScope

### A modular framework for crowd-state analysis and uncertainty-aware resource planning

**Trajectories → spatial crowd state → uncertain composition → explicit decisions.**

**Updated paper and framework:** a calibrated movement detector is connected to
the complete streaming pipeline and documented in the current manuscript. See
the [framework guide](docs/calibrated_framework.md) and
[calibrated results](research/calibrated_framework_results_v1.md).

Define walkable zones, feed time-stamped trajectories, inspect density and
uncertain composition, then attach a management decision model. Current evidence
supports an exploratory SiME-domain recogniser; new scenes and service models
need their own validation.

[Paper PDF](paper/framework/CrowdScope_Paper.pdf) · [LaTeX source](paper/framework/main.tex) · [Demo guide](app/README.md) · [Final results](research/final_evaluation_A1_report.md)

![CrowdScope demonstration](app/preview.png)

A Research Methodology project at RV University by **Surya Maheswaran, Yashaswini Pawar, Sohan Kori and Seema B. Hegde**.

CrowdScope connects geometry-aware density measurement, causal movement summaries, calibrated wheelchair-associated motion probabilities and finite-capacity allocation through a common crowd-state interface. New applications can consume that state when their decision models and validation data are supplied. The current recognition component is exploratory and limited to the studied SiME domain. CCTV, child/age recognition, arbitrary-scene transfer, dynamic dispatch and reliable evacuation timing remain extensions.

## Implemented modules

- **Observe:** canonical trajectories, explicit units and track-quality checks.
- **Measure:** polygon/obstacle-aware counts, density, past-only motion and crossings.
- **Estimate:** calibrated trajectory-detector probabilities, flagged prior fallback, expected composition and count distributions.
- **Decide:** exact allocation with population, hard-label, probability and information-reference controls.
- **Audit:** fixed configurations, grouped partitions, paired uncertainty and negative controls.
- **Demonstrate:** the original shareable synthetic replay and a separate local recorded-SiME framework replay with held-trial detector probabilities.

## New detection and connected-framework evidence

- **711 eligible four-second windows**, including 55 wheelchair-associated observations of **seven repeated people**.
- Fifteen fixed models/controls, including an MLP, temporal CNN and GRU. Full logistic leads on exploratory crossed-holdout AP (**0.907**).
- Nested person/trial calibration reduces Brier loss **0.0362 → 0.0210**; calibrated precision/recall are **84.3% / 83.6%** at the preset threshold.
- A separate coherent held-trial replay reduces nonempty-zone count MAE **0.602 → 0.452 people/zone**. Participants may repeat in this weaker whole-crowd task.
- **No improvement in default hypothetical resource-planning loss.** Better estimates do not automatically improve a discrete decision.
- **46 tests**, nested-split and saved-output audits, and 100 recorded-state Python/JavaScript allocator checks pass.

![Movement-model comparison and nested calibration](paper/framework/figures/detection_calibration.png)

Run `python app/launch.py --page framework.html`. With the local recorded-data
package, this opens the eight-trial replay. A clean GitHub checkout shows the
included aggregate evidence view and links to the fully self-contained synthetic
demo. Human replay data, individual predictions and fitted recognition weights
are not bundled; see the guide for prerequisites and rebuilding.

## Paper and retained earlier evidence

**CrowdScope: A Modular Framework for Crowd-State Analysis and Uncertainty-Aware Resource Planning**

The IEEE-style course paper has **seven pages, eighteen references and seven required major sections**.

- Recorded SiME trajectories integrate at **42 checkpoints from fourteen trials**. This verifies occupancy processing, not real profile recognition or service demand.
- The fixed synthetic evaluation covers **60 independent seed blocks, fourteen conditions and 58,800 policy records**.
- Probabilities reduce base unmet requests by **0.255** versus hard posterior, paired 95% interval **[−0.390, −0.127]**. The paper identifies that comparator's threshold weakness.
- Against hard observed labels, base allocations match in **599/600 replicas**, with no probability advantage. Small secondary gains depend on zone balance and demand contrast.
- Dense-crowd jams and timestep sensitivity remain in the JuPedSim record. No general evacuation or safety validation is claimed.

[Full interpretation and limitations](research/final_evaluation_A1_report.md). Established mathematical tools support a transparent information-to-decision benchmark; no invented Bayesian algorithm or verified first-framework claim is made.

## Try the demonstrations

```bash
python app/launch.py --page framework.html
```

The framework page uses the local recorded replay when available and otherwise shows the included aggregate evidence. For the fully self-contained synthetic what-if app, use `python app/launch.py --page index.html` or open `app/index.html` directly. Its optional colours show simulation truth, not recognised disability. No external service is needed. [Demo details](app/README.md).

## Reproduce

Python 3.12 is recommended. Core planning uses the standard library; geometry, recognition, neural comparisons, simulation and figures use the single root requirements file.

```bash
python -m venv .venv
# Activate the environment for your operating system, then:
python -m pip install -r requirements.txt
python -m unittest discover -s tests
python research/audit_planning_evaluation.py
python research/analyse_evaluation_A1.py
```

The guard denies evaluation by default. The dated release permits the fixed final run. Saved experiment folders refuse overwrite: regenerate in a clean source/configuration copy without that experiment's pre-existing output folder.

```bash
python research/run_planning_manifest.py --partition evaluation --enable-evaluation
```

The release binds original source/configuration bytes. `.gitattributes` disables line-ending conversion so hash checks remain reproducible. Analysis averages replicas within seed and uses a paired block bootstrap; frames, replicas and cells are not independent crowds.

## Build the paper

```bash
python paper/framework/make_figures.py
tectonic paper/framework/main.tex
```

The [compiled PDF](paper/framework/CrowdScope_Paper.pdf) and figures are included. Figures use aggregate results only. The paper links this private repository; reviewers need access permission.

## Repository guide

- `src/crowd_state.py`, `polygon_zones.py`: observed state and geometry.
- `src/mobility_probability.py`, `resource_planning.py`: uncertainty and allocation.
- `src/calibrated_detector.py`, `crowd_framework.py`: calibrated inference and connected streaming API.
- `app/`: framework evidence/replay interface, synthetic demo and launcher.
- `docs/calibrated_framework.md`: usage, schema and data prerequisites.
- `research/results/`: publication-safe aggregate recognition/calibration results.
- `configs/`, `research/evaluation_*`: design, partitions and release record.
- `output/planning_evaluation_A1/`: synthetic outcomes, analysis and audit.
- `research/literature/`: scoped evidence and closest-method comparison.
- `paper/framework/`: current manuscript and verification record.

## Data boundaries

The original fixed planning benchmark and self-contained what-if demo are synthetic. The new detection/calibration results use recorded SiME trajectories, with aggregate results included. Raw tracks, identity registries, fitted recognition weights, and derived participant-level prediction/integration/replay files are excluded pending confirmation of redistribution terms. The framework UI therefore has an aggregate-only view for a clean checkout.

Raw-data audit/replay scripts require the local verified archives documented in `plan.md`; those archives are not uploaded. A fresh clone reproduces synthetic planning and its audits but needs separately acquired source data to reproduce raw-data measurements. Hypothetical profiles and request rates are not real demographic or staffing labels.

## History

Earlier studies remain under `paper/real_and_linkage/`, `paper/compound/`, `research/compound/`, `research/assistance/` and related historical source/output folders. Their targets, environments and results differ from CrowdScope. Current entry points are listed above; historical dependency pins remain in Git history.

No external funding was received. Third-party data retain their source terms; no new blanket licence is asserted. Author and venue declarations need confirmation before formal submission.
