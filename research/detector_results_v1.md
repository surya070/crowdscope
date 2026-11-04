# Exploratory wheelchair-associated motion detector — 5 November 2026

Publication update (5 November 2026): the current manuscript incorporates the detection/calibration extension. Statements below about publication status describe the earlier experiment stage; numerical outcomes are unchanged.

## Outcome

Full-feature logistic regression has the highest observed crossed-holdout AP (0.9074). Random forest has the highest observed F1 at the fixed model thresholds (0.8270). These are different selection criteria, not one universal best model.

## Cohort and evaluation

Trials 501–508 yield 711 four-second observation windows: 55 wheelchair person-trial records and 656 conditional non-wheelchair controls. One track (trial507, documented wheelchair participant36) never has an observed forward x=-1 crossing and is excluded. Seven wheelchair people are repeated; 55 observations are not 55 different wheelchair people.

Each of 55 crossed folds excludes the test trial and target wheelchair person from all training records. All known mapped test-control identities are excluded too. Unknown repeated controls remain a limitation. Each positive is tested once. Controls receive six or seven out-of-trial predictions; inverse-fold-count weights preserve one effective observation per control. The reported 68,430 prediction records across 15 families have only 711 effective tracks, not 68,430 independent people.

The four-second windows end at an observable approach-line crossing. Features/sequence values use no future frames and no height, absolute position, IDs, trial label or passage duration. Scaling uses training data only. There is no random-frame split. Fixed parameters and epochs are recorded before outcome generation. Data exploration preceded this protocol; model family ranking also uses this comparison, so no untouched external-test claim is made.

## All retained results

AP measures ranking over recall thresholds; it is not classification accuracy. The positive prevalence is 7.74%. Precision, recall and F1 below use preset thresholds, which do not imply equal operating costs across models. Class-balanced scores are uncalibrated. Training AP is an unweighted mean over fitting sets; the holdout AP uses the declared weighting, so the gap is descriptive rather than a formal overfitting statistic.

- **Full logistic:** AP 0.9074; ROC-AUC 0.9868; precision 0.6424; recall 0.9455; F1 0.7650; control false-positive rate 0.0441; mean training AP 0.9735.
- **Gradient boosting:** AP 0.9014; ROC-AUC 0.9730; precision 0.7603; recall 0.8364; F1 0.7965; control false-positive rate 0.0221; mean training AP 1.0000.
- **Extra trees:** AP 0.8917; ROC-AUC 0.9884; precision 0.7985; recall 0.8545; F1 0.8256; control false-positive rate 0.0181; mean training AP 0.9999.
- **Random forest:** AP 0.8656; ROC-AUC 0.9838; precision 0.8359; recall 0.8182; F1 0.8270; control false-positive rate 0.0135; mean training AP 0.9937.
- **RBF SVM:** AP 0.8607; ROC-AUC 0.9844; precision 0.6387; recall 0.8909; F1 0.7440; control false-positive rate 0.0422; mean training AP 0.9972.
- **MLP:** AP 0.8517; ROC-AUC 0.9741; precision 0.7587; recall 0.8182; F1 0.7873; control false-positive rate 0.0218; mean training AP 0.9980.
- **kNN:** AP 0.8087; ROC-AUC 0.9578; precision 0.8788; recall 0.5273; F1 0.6591; control false-positive rate 0.0061; mean training AP 1.0000.
- **CNN:** AP 0.7687; ROC-AUC 0.9335; precision 0.4870; recall 0.8909; F1 0.6297; control false-positive rate 0.0787; mean training AP 0.9207.
- **Lateral logistic:** AP 0.7047; ROC-AUC 0.9134; precision 0.3006; recall 0.8182; F1 0.4396; control false-positive rate 0.1596; mean training AP 0.7402.
- **Gaussian NB:** AP 0.6294; ROC-AUC 0.9401; precision 0.4533; recall 0.8364; F1 0.5879; control false-positive rate 0.0846; mean training AP 0.7189.
- **GRU:** AP 0.5693; ROC-AUC 0.9053; precision 0.3447; recall 0.8364; F1 0.4882; control false-positive rate 0.1333; mean training AP 0.7023.
- **Coarse logistic:** AP 0.5556; ROC-AUC 0.9133; precision 0.2877; recall 0.7636; F1 0.4179; control false-positive rate 0.1585; mean training AP 0.6919.
- **Permuted logistic:** AP 0.1271; ROC-AUC 0.5797; precision 0.1083; recall 0.5091; F1 0.1786; control false-positive rate 0.3516; mean training AP 0.1232.
- **Speed logistic:** AP 0.1024; ROC-AUC 0.5255; precision 0.1050; recall 0.4000; F1 0.1663; control false-positive rate 0.2860; mean training AP 0.1595.
- **Prior:** AP 0.0745; ROC-AUC 0.4873; precision 0.0000; recall 0.0000; F1 0.0000; control false-positive rate 0.0000; mean training AP 0.0787.

## Interpretation and limits

Full logistic detects 52 of 55 held-out positive observations at the preset threshold, with 64.2% weighted precision and 4.41% weighted control false-positive rate. Its recall varies from 85.7% to 100% across the seven wheelchair people; per-trial AP ranges from 0.802 to 1.000. Neither apparent perfection in a small trial nor the pooled ROC-AUC establishes real-world accuracy.

Speed-only AP is 0.1024, lateral-only AP 0.7047 and coarse-time-feature AP 0.5556. Full logistic combines multiple time scales, temporal structure and lateral summaries; its advantage is not attributable to one isolated feature. The coarse ablation changes both feature content and time scale, so it is not a clean proof that high-frequency sway alone causes recognition.

The shuffled-training-label control has AP 0.1271 and ROC-AUC 0.5797. This is much lower than the leading model but not exactly the prevalence/chance line. One permutation is a sanity check, not a formal permutation test or p-value.

The MLP, CNN and GRU were evaluated under fixed small configurations and one seed per fold. They did not lead this comparison. Their results do not rule out better neural architectures or tuning. Trying increasingly many models on the same observations would also increase selection optimism.

SiME tracking research already documents walking head-sway fluctuations (Schumann et al., Hybrid Tracking System for Pedestrians in Dense Crowds, results section). The present signal is consistent with a recorded motion cue, but tracking differences, occlusion, height-related measurement processing, assistance and scene orientation remain possible confounders. We have not verified identical processing for every class/window or validated transfer to a different tracking system.

## Prototype and framework integration

`src/motion_detector.py` scores a valid 101-position, 25Hz history. `research/export_detector_candidate.py` refits the selected family on all development records and saves a local-only model/card. This all-data refit is a prototype for future observations, not an independent validation model. Functional checks confirm translated-window inference agrees with direct model predictions and that sampling gaps are rejected.

Raw scores must not simply replace calibrated composition probabilities in the resource planner. The next study should assess/calibrate probabilities within training-only splits, test failure/abstention behaviour, and evaluate downstream decisions under explicitly hypothetical demand. The existing frozen planning experiment remains valid as its original separate experiment, and has not been silently rerun or reinterpreted.

## Simulation decision

Do not synthesize extra training people yet. Current real-data holdouts support a useful exploratory candidate, while the larger source limitations require independent labelled people/recordings. JuPedSim CFSV2 is an operational pedestrian model, not a generator of measured head sway, wheelchair biomechanics or class-specific observation noise. It is not established as the generating model of the real SiME trajectories. Adding a handcrafted wheelchair-specific wobble would risk training the desired answer into synthetic labels.

If augmentation is pursued later, develop a training-only observation model, keep the real holdouts unchanged, compare real-only with real-plus-synthetic, and report failures. Synthetic success cannot validate an imposed class signature. A different real tracking setup and new wheelchair participants would be stronger evidence.

## Reproducibility

Protocol: `research/detector_protocol_v1.md`. Build: `research/build_detector_data.py`. Benchmark: `research/run_detector_benchmark.py`. Independent audit: `research/audit_detector_benchmark.py`. Local results: `output/detector_v1/`. All source/data hashes, fixed settings, seed, versions and the dependency-only retry are retained. Independent AP/ROC arithmetic, weighted coverage, split assertions and inference checks pass. Participant-level artifacts are ignored by Git; no GitHub or manuscript update was made in this stage.

Primary tracking source: https://juser.fz-juelich.de/record/866598/files/SchumannJ.pdf?subformat=pdfa&version=1
Grouped-validation guidance: https://scikit-learn.org/stable/modules/cross_validation.html
Calibration guidance: https://scikit-learn.org/stable/modules/calibration.html
