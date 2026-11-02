# Wheelchair-trial expansion — completed 2 November 2026

Six trials (502, 503, 504, 505, 506, 508) were assigned development roles in `../expansion_assignment.json` before acquiring their raw trajectories. None is designated a new independent test cohort. Public official source: https://ped.fz-juelich.de/data/experiments/2017.06.10_Wermelskirchen_SiME/data/2017sime/2017sime_trajectories_txt.zip . Dataset DOI: https://doi.org/10.34735/ped.2017.1 .

Current catalogue/terms retrieval failed through browsing. We rely on the archived official acquisition/provenance records for source identity and keep the data local. No redistribution licence or current access terms have been established by this stage. Raw files are ignored by Git and have not been published.

The first download attempt timed out after 502. The downloader was updated to use resumable 64 KiB segments and bounded retries. All six extracted files pass both the remote ZIP CRC checks and the saved pre-acquisition index's expected CRC/size checks. SHA-256 hashes are recorded in `acquisition_manifest.json`. This verifies file integrity, not scientific validity.

## Audit results

- 532 additional person-trial tracks; metadata/track counts agree in all six trials.
- All recorded tracks have a forward head-centre crossing of x=2.4 m.
- No internal missing frames or duplicate ID/frame records were found by the parser.
- Seven documented wheelchair mappings per run, 42 person-trial mappings total.
- Every run contains the same persistent wheelchair identifiers 34–40: seven unique people.
- All 18 candidate observed-cohort checkpoints at 10/20/30 s pass the current coverage/count rules.
- Widths: 502 at 0.9 m; 503/504 at 1.0 m; 505/506 at 1.1 m; 508 at 1.2 m.

Together with earlier trial 501, there are now seven complete, count-consistent wheelchair trials and 21 coverage-eligible wheelchair-trial queries. Trial 507 remains incomplete and is retained as a diagnostic. Query counts are not independent participant or experiment counts. Other participants' complete persistent identities and mobility-class labels still require verification; the wheelchair registry alone does not label everyone else as non-disabled.

## Decision

This removes the immediate obstacle of having only one complete wheelchair trial. It supports designing a limited exploratory cross-run/width comparison. It does not create unseen-person evidence, resolve helper/age labels, or finish prior-art verification.

Next stage: combine these development records with the saved reference trials through one causal cohort/feature extractor; verify class completeness from metadata/documentation; define run/width grouping and primary scope before fitting. If a comparison uses shared wheelchair participants across train and evaluation, explicitly describe it as within-cohort transfer across runs/widths. Do not reinterpret these newly inspected outcomes as prospective held-out tests later.

For a new simulator branch, perform development calibration and numerical verification before generating a forecasting benchmark. This stage calibrates neither JuPedSim nor a predictor.

Outputs: `trials.csv`, `queries.csv`, `labels.csv`, and `acquisition_manifest.json`. Acquisition and audit scripts are `../fetch_sime.py` and `../audit_expansion.py`. The prior ZIP backup remains intact.
