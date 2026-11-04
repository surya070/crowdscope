# Trajectory and state interface — 4 November 2026

Implementation: `src/crowd_state.py`. No external packages are required at this stage.

## Input and geometry contract

Canonical CSV: `person_id,time,x,y`, with explicit positive conversion scales supplied to `load_csv` when source units differ from seconds/metres. IDs are source track IDs, not guaranteed persistent identities. Duplicate person/timestamps and non-finite values are errors, not silently deduplicated. Input order may vary.

This first geometry adapter supports positive-area axis-aligned rectangular observable zones. Interior overlaps are rejected. Shared edges belong to the lowest numbered matching zone. Active points outside all zones raise an error. Unobserved space, obstacles and full building geometry must not be hidden inside rectangular area estimates. Polygonal JuPedSim/SiME geometry needs a separate checked adapter before empirical density claims. The demonstration's four rectangles are measurement fixtures, not frozen simulator layouts.

## Observation policy

Snapshot membership requires an observation at exactly the requested timestamp. Callers should query source frame timestamps; asynchronous tracks need an explicit separately tested synchronisation adapter. The implementation never carries forward disappeared people or interpolates using future positions. A missing person in the observation is unknown to this module, not evidence of physical departure from the building.

Use only points within the inclusive past window. A gap exceeding `max_gap` breaks motion continuity. Current movement uses the contiguous suffix ending at the snapshot, leaving older disconnected fragments out. No motion estimate is produced for a lone point. This also avoids treating a fragmented ID as a different person's known history, but does not repair ID switches.

## Features and units

- Occupancy: exact visible count per zone, including people without motion history.
- Density: count / supplied usable zone area, people/m².
- Person mean speed: travelled segment length / observed contiguous duration, m/s. Variable sampling is duration-weighted.
- Person stopped-time fraction: duration of valid segments with speed below 0.1 m/s / observed duration.
- Zone mean speed: arithmetic mean of available person mean speeds; denominator reported as `motion_observed_count`.
- Zone stopped fraction: fraction of motion-observed occupants whose window-mean speed is below 0.1 m/s. This differs from mean person stopped-time fraction; both concepts are named explicitly.
- Quality: history coverage in [0,1], complete-history flag, missing-motion count. Short history may yield a speed with a partial-coverage warning.
- Directional flow diagnostic: forward and reverse crossing event counts on contiguous observed segments in the window. Plane convention is `previous x < plane <= next x` and its reverse. Counts represent events, not distinct people, unique clearances, body exits or arrival/departure rosters. This module does not compute an evacuation target.

## Verification and execution

Run `python -m unittest discover -s tests -v` from the root. Fifteen checks cover empty/stationary scenes, analytic speed/density, shared boundaries and conservation, duplicate rejection, variable sampling, missing frames, fragmented IDs, partial visibility, future invariance, crossing direction, geometry validity, invalid values and unit conversion.

Run `python research/run_state_fixture.py` for a deterministic 21-frame CSV/JSON measurement replay in `output/state_fixture_v1/`. It has a 1 m/s walker and a stationary person, conserves both occupants, and contains one forward crossing. It is not real-data validation, JuPedSim output or a mobility recogniser.

## Stage 4 decision

**Pass for the canonical rectangular measurement foundation.** The CSV ingestion, causal windows, counts/density, speed/stops and crossing diagnostics are implemented and checked. The replay currently consists of saved timestamped states; a graphical viewer is deferred to the integration stage. Source-specific SiME ingestion, polygon/obstacle geometry and simulator event adapters remain integration requirements, not validated capabilities.

Next Stage 5 follows the selected uncertain-metadata route: implement/check the Bayesian probability channel and composition estimates. Do not fit a real wheelchair/child classifier without resolving Stage 2 label constraints. Simulator generation and numerical movement tests belong to Stage 6.
