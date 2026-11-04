# Using the calibrated CrowdScope framework

The framework connects measured trajectories, calibrated working membership
probabilities, crowd-state measurement and an application-specific planner.
Current inference is an exploratory wheelchair-associated motion detector, not
age/child recognition, identity confirmation or observed assistance demand.

## Local demo

```powershell
python app/launch.py --page framework.html
```

Open the printed localhost URL. The existing server at port8770 can serve
`/framework.html` directly. The replay contains all eight SiME trials. Use the
trial selector, playback/timeline, composition policy, budget, capacity and
request-rate controls. Grey points have only prior information; rings identify
detector evidence and increase with working probability. The person list always
shows the underlying calibrated estimates; the policy selector changes the
composition/planning comparison. The default rates .1/.4 are hypothetical.

When the recorded-data file is absent, the page shows the included aggregate evidence view and links to the self-contained synthetic demo. It does not substitute fake human trajectories.

The recorded demo plays precomputed outputs of the actual streaming pipeline, using one
held-trial model per recording. It does not make backend inference calls or
change movement when planning controls change. The measured density uses exact
walkable polygons; the browser floor plan is schematic. The earlier synthetic
what-if demonstration remains at `/index.html`.

## Actual streaming API

```python
from src.calibrated_detector import CalibratedMotionDetector
from src.crowd_framework import CrowdFramework

detector = CalibratedMotionDetector()
engine = CrowdFramework(zones, detector, budget=6, capacity=2, r0=.1, r1=.4)

# Feed one increasing timestamp at a time; observations are (run-local ID, x, y).
engine.ingest_frame(time_seconds, observations)
state = engine.analyse()
```

Supply a complete non-overlapping partition of the observed walkable region as
`Zone` or `PolygonZone` objects. A custom `roi_contains` predicate can distinguish
out-of-region people from geometry conflicts. Visible people are assigned once,
with shared boundaries owned by the lowest zone ID. Absent tracks are excluded.
Past histories use seconds/metres and must have uninterrupted 25Hz sampling for
detection. Do not silently interpolate gaps.

The trained detector is validated only for a four-second history at the first
forward x=-1 crossing in this passage-aligned coordinate system. It is not a
validated arbitrary-window recogniser. The framework caches the estimate as
uncertain stable profile information. Before eligibility or after a history gap,
it uses a flagged training prior. Changing population composition or recording
conditions can invalidate calibration; no automatic prior-shift correction is
implemented. The all-development refit is for experimentation, not validation.

The output separates:

- `occupants`: positions, past speed, probability, source and estimate timestamp.
- `zones`: usable area, count, density, motion summaries, expected membership,
  variance, working count interval and detector/prior coverage.
- `composition`: expected total membership and a working independent-count interval.
- `planning`: exact allocation and expected unmet hypothetical requests.
- `assumptions`: request rates, capacity, budget, evidence and validity limits.

The calibrated posterior is used directly; there is no second Bayesian update
with the same movement evidence. Each request probability is
`r0 + (r1-r0)*membership_probability`; those service rates require empirical
justification in a deployment. The current allocator assumes independent
requests, simultaneous static allocation and no travel/service-duration costs.

## CSV entry point

Input CSV columns are `person_id,time,x,y`, with seconds and metres. Files may
contain positions outside the analysis region; the current observation region
determines occupancy. Config JSON contains `observable_wkt` and a list of
`zones`, each with `id` and `wkt`, plus optional budget/capacity/r0/r1.

```powershell
python research/run_framework_csv.py input.csv config.json --output output/my_run.jsonl
```

Use `--model` for a specific saved held-trial model and `--every` for snapshot
spacing. The configuration examples for each SiME trial are generated in
`output/calibrated_framework_v1/trial_501_config.json` etc. Input coordinates
must be aligned to the studied passage direction and trigger. An adapter and
new validation are necessary for different geometries/orientations or sampling.

## Rebuilding the research evidence

With the verified original local archives available:

1. `research/build_detector_data.py` builds local fixed-window features.
2. `research/run_detector_benchmark.py` preserves the original family comparison.
3. `research/calibrate_detector.py` performs nested calibration and saves final
   and held-trial models. Existing outputs are protected from overwriting.
4. `research/evaluate_calibrated_framework.py` streams the real recordings,
   verifies offline/online agreement and writes the local replay package.
5. `research/audit_calibrated_framework.py` checks splits, scores and conservation.
6. `research/summarise_calibrated_framework.py` writes the report/model card/figures.

Use the pinned root `requirements.txt`. This workspace also restores verified
local dependency packages from the earlier project backups. Models, human
trajectories and participant-level derived records are local-only and ignored
by Git pending redistribution confirmation. Aggregate results and research code
are separate from those data. Do not upload a generated replay file by accident.

## Results and boundaries

Read `research/calibrated_framework_results_v1.md` for both positive and negative
results. Calibration improves probability metrics and the separate whole-trial
replay improves composition-count error. The default resource-planning outcome
does not improve. The full-roster replay has seen-participant overlap and must
not be confused with the stronger individual person/trial holdouts. Future
applications should consume the state through their own validated decision
modules; this architecture does not validate every possible crowd use case.
