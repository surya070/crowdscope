# SiME saved-data audit

Date: 2 November 2026. Source DOI: https://doi.org/10.34735/ped.2017.1 . This stage audits the saved snapshot, without downloading or inspecting any new trial outcomes. It does not fit or calibrate a model.

Inputs were read directly from the verified pre-reset ZIP and checked against its per-file SHA-256 manifest. Raw files were not restored into the active project. `audit_saved_sime.py` reproduces the inventory with standard Python.

The official saved metadata contains 119 run entries; eight raw trial files are locally available. This metadata count does not resolve differing whole-project run totals in older documents. Units in raw headers are metres and 25 frames/s, with x already inverted toward the downstream direction. Coordinates represent tracked head positions, not full-body footprints. Avoid treating the z coordinate as an age or disability detector.

Eight trials contain 619 person-trial tracks. These are not 619 independent people. No missing internal frames or duplicate ID/frame records were found within the saved tracks; that does not rule out smoothing artifacts, identity errors or missing track ends.

Every saved trial was previously accessed and inspected. Reference trials 1501/1507 were used for calibration; 1503/1505 were tested and reported previously. All eight are exposed development evidence for a new study. Unavailable trials in metadata are not automatically independent or eligible tests; check prior exposure and participant reuse first.

Official documentation describes repeated runs and partial persistent identifiers in headers. Many header comments are empty, so a complete identity-disjoint partition is not established. The metadata `persons` field names researchers, not a participant age registry.

Labels: wheelchair persistent identifiers 34–40 are supported by archived documentation and map to seven tracks in each of 501/507. Those are seven unique documented wheelchair users, not 14. Other tracks are marked unestablished by this particular registry; absence from that registry is not a universal non-disabled label. No helper-track, family or age mapping is established here. Published individual ages must be linked through verified identifiers before use; matching article row order is insufficient.

Licensing and redistribution terms require a fresh source check before release. This audit uses locally saved evidence and does not establish current access/licence terms. New files contain no medical narratives. Do not upload raw tracks or participant mappings without checking source permissions.

Data quality issues:

- Trial 1307: metadata 83 versus 85 tracks. All 85 cross x=2.4 m; cohort membership must be reconciled.
- Trial 507: metadata and tracks both 92, but only 91 have observed forward crossings of x=2.4 m. Track 32 (documented wheelchair ID 36) ends at frame 938, x=-2.08068 m, upstream. Its later outcome is unobserved; do not impute its passage from the last recorded frame.
- Five trials have no common time interval shared by all tracks (latest first frame exceeds earliest last frame). A complete cohort snapshot/history is therefore not universally observed. Entrants can appear after others leave the field of view.

Files: `trial_inventory.csv`, `track_coverage.csv`, `label_audit.csv`, `metadata_inventory.csv`, `exposure_ledger.csv`, `audit_summary.json`. These are audit outputs, not trained-model data partitions.
