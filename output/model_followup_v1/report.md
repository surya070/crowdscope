# Five-family exploratory follow-up

Completed 3 November 2026. All previous outcomes were already exposed. This is a post-result sensitivity comparison, not an independent confirmatory test. The original experiments and headlines are unchanged.

## Design

Four candidate settings per family, fixed before fitting this attempt. Empirical: primary one-second history, identical H/M aggregates and original nested width folds. Synthetic: original coordinated train/validation/evaluation blocks at both gains, with M, count, correct-link and shuffled-link conditions. Train-only scaling and clipping below zero. MLP uses three fixed initializations (113/271/509), training-only target scaling, and mean validation error across seeds for configuration selection. Reported MLP scores average seed-wise errors rather than ensemble predictions. Other families use seed 113. Full grid and environment are in lock.json; all inner/validation scores are in selection_trace.json.

The four-candidate boosting grid uses 100 trees throughout, unlike the original eight-candidate grid. This is a bounded comparison, not exhaustive architecture optimization. An initial setup attempt stopped before fitting because Shapely was outside the import path; its lock remains under output/model_followup_v1_setup_aborted. Only the import path was corrected.

## Saved metrics

| Study | Gain | Information | Model | MAE (s) | Seed min | Seed max |
|---|---|---|---|---:|---:|---:|
| empirical | all-widths | H | ridge | 4.278143 | 4.278143 | 4.278143 |
| empirical | all-widths | H | rbf | 10.100098 | 10.100098 | 10.100098 |
| empirical | all-widths | H | boosting | 9.047663 | 9.047663 | 9.047663 |
| empirical | all-widths | H | forest | 10.009578 | 10.009578 | 10.009578 |
| empirical | all-widths | H | mlp | 4.693422 | 4.458885 | 5.072390 |
| empirical | all-widths | M | ridge | 2.591302 | 2.591302 | 2.591302 |
| empirical | all-widths | M | rbf | 7.811856 | 7.811856 | 7.811856 |
| empirical | all-widths | M | boosting | 6.703258 | 6.703258 | 6.703258 |
| empirical | all-widths | M | forest | 6.498283 | 6.498283 | 6.498283 |
| empirical | all-widths | M | mlp | 2.937823 | 2.833496 | 3.000701 |
| synthetic | 1.0 | M | ridge | 0.198372 | 0.198372 | 0.198372 |
| synthetic | 1.0 | M | rbf | 0.531320 | 0.531320 | 0.531320 |
| synthetic | 1.0 | M | boosting | 0.329451 | 0.329451 | 0.329451 |
| synthetic | 1.0 | M | forest | 0.460586 | 0.460586 | 0.460586 |
| synthetic | 1.0 | M | mlp | 0.164827 | 0.140037 | 0.189659 |
| synthetic | 1.0 | F_counts | ridge | 0.198372 | 0.198372 | 0.198372 |
| synthetic | 1.0 | F_counts | rbf | 0.531320 | 0.531320 | 0.531320 |
| synthetic | 1.0 | F_counts | boosting | 0.441758 | 0.441758 | 0.441758 |
| synthetic | 1.0 | F_counts | forest | 0.457668 | 0.457668 | 0.457668 |
| synthetic | 1.0 | F_counts | mlp | 0.153479 | 0.125806 | 0.167331 |
| synthetic | 1.0 | F_correct | ridge | 0.207677 | 0.207677 | 0.207677 |
| synthetic | 1.0 | F_correct | rbf | 0.619788 | 0.619788 | 0.619788 |
| synthetic | 1.0 | F_correct | boosting | 0.300581 | 0.300581 | 0.300581 |
| synthetic | 1.0 | F_correct | forest | 0.445257 | 0.445257 | 0.445257 |
| synthetic | 1.0 | F_correct | mlp | 0.174169 | 0.149201 | 0.195181 |
| synthetic | 1.0 | F_shuffled | ridge | 0.182173 | 0.182173 | 0.182173 |
| synthetic | 1.0 | F_shuffled | rbf | 0.652818 | 0.652818 | 0.652818 |
| synthetic | 1.0 | F_shuffled | boosting | 0.313341 | 0.313341 | 0.313341 |
| synthetic | 1.0 | F_shuffled | forest | 0.453849 | 0.453849 | 0.453849 |
| synthetic | 1.0 | F_shuffled | mlp | 0.153343 | 0.152564 | 0.154109 |
| synthetic | 1.15 | M | ridge | 0.200111 | 0.200111 | 0.200111 |
| synthetic | 1.15 | M | rbf | 0.458375 | 0.458375 | 0.458375 |
| synthetic | 1.15 | M | boosting | 0.246708 | 0.246708 | 0.246708 |
| synthetic | 1.15 | M | forest | 0.326426 | 0.326426 | 0.326426 |
| synthetic | 1.15 | M | mlp | 0.140595 | 0.090467 | 0.187796 |
| synthetic | 1.15 | F_counts | ridge | 0.200111 | 0.200111 | 0.200111 |
| synthetic | 1.15 | F_counts | rbf | 0.458375 | 0.458375 | 0.458375 |
| synthetic | 1.15 | F_counts | boosting | 0.324577 | 0.324577 | 0.324577 |
| synthetic | 1.15 | F_counts | forest | 0.312861 | 0.312861 | 0.312861 |
| synthetic | 1.15 | F_counts | mlp | 0.146047 | 0.114595 | 0.162316 |
| synthetic | 1.15 | F_correct | ridge | 0.387126 | 0.387126 | 0.387126 |
| synthetic | 1.15 | F_correct | rbf | 1.208845 | 1.208845 | 1.208845 |
| synthetic | 1.15 | F_correct | boosting | 0.262678 | 0.262678 | 0.262678 |
| synthetic | 1.15 | F_correct | forest | 0.327525 | 0.327525 | 0.327525 |
| synthetic | 1.15 | F_correct | mlp | 0.528923 | 0.282295 | 0.667105 |
| synthetic | 1.15 | F_shuffled | ridge | 0.177093 | 0.177093 | 0.177093 |
| synthetic | 1.15 | F_shuffled | rbf | 0.573035 | 0.573035 | 0.573035 |
| synthetic | 1.15 | F_shuffled | boosting | 0.297242 | 0.297242 | 0.297242 |
| synthetic | 1.15 | F_shuffled | forest | 0.323995 | 0.323995 | 0.323995 |
| synthetic | 1.15 | F_shuffled | mlp | 0.140238 | 0.131559 | 0.153327 |

## Interpretation

All five empirical families improve from H to M. Ridge remains lowest on the evaluation sample (M=2.591302 s), followed by MLP (mean M=2.937823 s). This ranking is descriptive, not a model selected using evaluation scores.

At synthetic zero gain, correct links outperform M/counts/shuffled within boosting and forest, with M-relative improvements of 0.028870 and 0.015329 s. Ridge, RBF and MLP do not show this joint control advantage. At gain 1.15, correct links worsen M errors for all five families. MLP gives the lowest mobility-only evaluation error at both gains, but this does not establish a general architecture advantage or realistic human timing accuracy. Constant count features can still change random/optimization behaviour without adding information.

No p-values or population confidence intervals are reported. MLP seed ranges are optimization sensitivity, not independent experimental samples. The same repeated participants and limited layouts remain. These findings qualify, rather than replace, the original selected-model result.

## Audit

audit_model_followup.py reconstructs 1,806 predictions and 50 metric groups, checks unique keys, targets, original evaluation membership, source/runner hashes, and exact reproduction of original empirical ridge predictions. No convergence warnings occurred. It does not independently reimplement the fitted learners.
