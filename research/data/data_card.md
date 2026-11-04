# SiME feasibility audit — 4 November 2026

## Source and reproducibility

Dataset identifier: https://doi.org/10.34735/ped.2017.1 . Audit script: `research/data/audit_stage2.py`. Run with standard-library Python from any directory. It reads both verified local backup ZIPs directly, validates each selected input against its backup SHA-256 record, and writes `research/data/stage2/`. No raw files were extracted and no classifier, predictor or simulator was fitted.

The two snapshots supply eight original and six later-acquired trial files. These are the fourteen files behind the previous study, resolving the apparent eight-versus-fourteen discrepancy in old notes. The former primary forecasting analysis selected eleven; the current inventory deliberately retains excluded/problematic trials as diagnostics.

## Observations

- Fourteen trials, 1,151 person-trial tracks. These are not 1,151 independent people.
- Headers declare 25 fps, metre positions and an already inverted x-axis. Coordinates are tracked head positions. The z field is explicitly ambiguous in the source header and is excluded from proposed movement-only recognition.
- Fifty-six documented wheelchair person-trial observations correspond to seven persistent wheelchair IDs repeated across trials 501–508. The historical positive registry is preserved as such; its absence does not establish a negative disability label.
- 928 of 1,151 tracks lack a persistent ID in header comments. Consequently the number of unique people across all tracks cannot be established from these comments alone.
- Known persistent-ID connections place all fourteen trials in one connected component. This assumes the archived interpretation of numeric comments as cross-run identifiers; reconfirm namespace semantics before using them for splits. Missing identities could add dependence, not demonstrate independence.
- No internal missing frames or duplicate ID/frame pairs were found. This does not rule out tracking errors, interpolation, incomplete ends or ID switches.
- Trial 1307 has a metadata/track count mismatch. Trial 507 contains a track without an observed forward head crossing of x=2.4 m. Those diagnostics match the earlier audit.
- No verified per-track age, helper, family or assistance-demand annotations were established by this audit.

## Exposure and terms

All fourteen trial outcomes were previously inspected. None is a fresh independent test. New targets or code do not reset that exposure.

Current access/licensing remains unresolved: the attempted current archive documentation page failed to retrieve. The saved original source identity and integrity are documented, but do not constitute redistribution permission. Keep raw trajectories and identity mappings local. Check the authoritative current dataset terms before distributing derived person-level data.

## Intended use

Suitable for exploratory movement/zone-state checks, bounded simulator comparisons under matched geometry, and auditing whether a small mobility-inference pilot is possible. Insufficient by itself for broad unseen-population demographic recognition, operational staffing validation or full-building evacuation claims.

The generated label inventory contains local historical mappings and should not be published by default. The audit JSON lists exact input archive members and hashes.
