# Assistance branch

The active simulator is a native JuPedSim circular-agent escort approximation. It does not model mechanical wheelchair pushing and has no empirical helper calibration.

The numerically verified operational candidate is described in `verified_candidate.json`; development evidence is under `output/assistance_numerics_v1/`. Earlier failed versions remain preserved.

`linkage_protocol_v1.md` freezes the synthetic information-value study. `linkage_manifest_v1.json` defines48 matched blocks/192 runs plus48 finer-step replays. `linkage_freeze_v1.json` hashes design/movement source; `linkage_implementation_freeze_v1.json` hashes generation/features/fitting before benchmark outcomes. All240 planned movement runs now pass admission; see `output/linkage_benchmark_v1/movement_report.md`. Fitting and saved-output reconstruction are complete.

Primary question concerns correct helper–client assignment beyond mobility/history and link counts, using zero assumed assistance speed gain. The1.15 gain, independent movement, shuffled links and missing links are controls/sensitivities. Stop if any new movement/numerical gate fails; do not silently drop failed runs.

Forecasting comparison completed and audited: correct links do not improve primary selected forecasts beyond mobility/history or controls. See `output/linkage_benchmark_v1/report.md`. `fit_linkage.py` refuses failed admission and existing predictions. In the local restored runtime, its imports require `.deps/recovery-r1` on PYTHONPATH; normal dependency installation uses the root requirements.txt. `audit_linkage.py` reconstructs saved prediction metrics. The active manuscript is `paper/real_and_linkage/main.tex`.
