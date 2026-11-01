# External data provenance

The original compound and broader prediction studies use generated synthetic trajectories, included under `output/compound/`. These are simulator outcomes, not measured human evacuation ground truth.

The separate empirical replay uses **SiME 2017**:

- Dataset: https://doi.org/10.34735/ped.2017.1
- Accompanying study: Geoerg, Schumann, Boltes and Kinateder (2022), https://doi.org/10.1038/s41598-022-18142-7
- Development trials: 1501 and 1507.
- Frozen test trials: 1503 and 1505.
- Acquisition host: Forschungszentrum Jülich pedestrian data archive.

Run `python scripts/fetch_sime.py` from the repository root to obtain the original metadata and these four trajectory files. The script checks the expected metadata/trajectory hashes and the original ZIP-member CRCs. Source changes cause a failure rather than silently accepting different inputs. The archive index is included for provenance; original data are downloaded from the publisher's host, not mirrored here.

Consult the dataset's applicable terms and institutional reuse requirements before downloading or using it. No project-wide licence is asserted over these external data. Raw human tracks and participant-level crossing records are excluded from this public artifact. Aggregate replay summaries and calibration traces are included.

The reference replay uses only unassisted trials and observed inlet schedules. Wheelchair identities documented in other inspected trials do not establish assistant links or individual ages. The replay cannot validate the compound wheelchair–helper controller or end-to-end forecasts.
