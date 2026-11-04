# External data provenance

## Current CrowdScope recognition study

The calibrated detector uses SiME trials 501–508: 711 eligible four-second
windows, including 55 observations of seven repeated wheelchair participants.
The whole-crowd replay and the stricter person/trial detector evaluation are
separate tasks. Source-data and fitted-weight prerequisites are documented in
[the framework guide](../docs/calibrated_framework.md).

Raw human trajectories and participant-level derivatives are not mirrored here.
The included archive index and hashes are provenance metadata, not trajectories.
The four-file downloader described below belongs to an earlier reference replay;
it does not acquire the full current recognition cohort.

## Archived reference-replay provenance


The original compound and broader prediction studies use generated synthetic trajectories, included under `output/compound/`. These are simulator outcomes, not measured human evacuation ground truth.

The separate empirical replay uses **SiME 2017**:

- Dataset: https://doi.org/10.34735/ped.2017.1
- Accompanying study: Geoerg, Schumann, Boltes and Kinateder (2022), https://doi.org/10.1038/s41598-022-18142-7
- Development trials: 1501 and 1507.
- Frozen test trials: 1503 and 1505.
- Acquisition host: Forschungszentrum Jülich pedestrian data archive.

Run `python scripts/fetch_sime.py` from the repository root to obtain the original metadata and these four trajectory files. The script checks the expected metadata/trajectory hashes and the original ZIP-member CRCs. Source changes cause a failure rather than silently accepting different inputs. The archive index is included for provenance; original data are downloaded from the publisher's host, not mirrored here.

Consult the dataset's applicable terms and institutional reuse requirements before downloading or using it. No project-wide licence is asserted over these external data. Raw human tracks and participant-level crossing records are excluded from this repository artifact. Aggregate replay summaries and calibration traces are included.

The reference replay uses only unassisted trials and observed inlet schedules. Wheelchair identities documented in other inspected trials do not establish assistant links or individual ages. The replay cannot validate the compound wheelchair–helper controller or end-to-end forecasts.
