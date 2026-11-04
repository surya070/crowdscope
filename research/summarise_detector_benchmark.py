"""Create the exploratory detector report and scientific figures."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
for folder in ['authoring','detector','recovery-r1']:sys.path.insert(0,str(ROOT/'.deps'/folder))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve
OUT=ROOT/'output/detector_v1'

def main():
    s=json.loads((OUT/'benchmark_summary.json').read_text());rr=s['results']
    order=sorted(rr,key=lambda k:rr[k]['AP'],reverse=True)
    fig,ax=plt.subplots(figsize=(9,6.2),layout='constrained')
    for i,name in enumerate(order):
        ax.plot([rr[name]['AP'],rr[name]['mean_training_AP']],[i,i],color='#b6bcc2',lw=2)
    ax.scatter([rr[n]['mean_training_AP'] for n in order],range(len(order)),marker='x',color='#7b838b',label='Mean training AP')
    ax.scatter([rr[n]['AP'] for n in order],range(len(order)),color='#146f83',label='Crossed-holdout AP',zorder=3)
    ax.set(yticks=range(len(order)),yticklabels=order,xlim=(0,1.03),xlabel='Average precision (AP, 0 to 1)',ylabel='Model / control',title='SiME exploratory detector: training versus crossed holdouts')
    ax.invert_yaxis();ax.grid(axis='x',alpha=.2);ax.legend(loc='lower right')
    fig.savefig(OUT/'model_comparison.png',dpi=170);fig.savefig(OUT/'model_comparison.pdf');plt.close(fig)
    records=json.loads((OUT/'predictions_LOCAL_ONLY.json').read_text());fig,ax=plt.subplots(figsize=(7.5,5),layout='constrained')
    for name in ['Full logistic','Random forest','MLP','CNN','GRU','Speed logistic']:
        r=[a for a in records if a['family']==name]
        p,rec,_=precision_recall_curve([a['y'] for a in r],[a['score'] for a in r],sample_weight=[a['weight'] for a in r])
        ax.step(rec,p,where='post',label=f'{name}: AP {rr[name]["AP"]:.3f}')
    ax.axhline(s['effective_prevalence'],color='grey',ls=':',label=f'Cohort prevalence {s["effective_prevalence"]:.3f}')
    ax.set(xlim=(0,1),ylim=(0,1.02),xlabel='Recall (fraction of positive observations detected)',ylabel='Precision (fraction of alerts correct)',title='Exploratory crossed-holdout precision-recall')
    ax.legend(fontsize=8);ax.grid(alpha=.2);fig.savefig(OUT/'precision_recall.png',dpi=170);fig.savefig(OUT/'precision_recall.pdf');plt.close(fig)
    lines=['# Exploratory wheelchair-associated motion detector — 5 November 2026','',
    '## Outcome','',
    'Full-feature logistic regression has the highest observed crossed-holdout AP (0.9074). Random forest has the highest observed F1 at the fixed model thresholds (0.8270). These are different selection criteria, not one universal best model.',
    '', '## Cohort and evaluation','',
    'Trials 501–508 yield 711 four-second observation windows: 55 wheelchair person-trial records and 656 conditional non-wheelchair controls. One track (trial507, documented wheelchair participant36) never has an observed forward x=-1 crossing and is excluded. Seven wheelchair people are repeated; 55 observations are not 55 different wheelchair people.',
    '', 'Each of 55 crossed folds excludes the test trial and target wheelchair person from all training records. All known mapped test-control identities are excluded too. Unknown repeated controls remain a limitation. Each positive is tested once. Controls receive six or seven out-of-trial predictions; inverse-fold-count weights preserve one effective observation per control. The reported 68,430 prediction records across 15 families have only 711 effective tracks, not 68,430 independent people.',
    '', 'The four-second windows end at an observable approach-line crossing. Features/sequence values use no future frames and no height, absolute position, IDs, trial label or passage duration. Scaling uses training data only. There is no random-frame split. Fixed parameters and epochs are recorded before outcome generation. Data exploration preceded this protocol; model family ranking also uses this comparison, so no untouched external-test claim is made.',
    '', '## All retained results','',
    'AP measures ranking over recall thresholds; it is not classification accuracy. The positive prevalence is 7.74%. Precision, recall and F1 below use preset thresholds, which do not imply equal operating costs across models. Class-balanced scores are uncalibrated. Training AP is an unweighted mean over fitting sets; the holdout AP uses the declared weighting, so the gap is descriptive rather than a formal overfitting statistic.','']
    for n in order:
        r=rr[n];lines.append(f'- **{n}:** AP {r["AP"]:.4f}; ROC-AUC {r["ROC_AUC"]:.4f}; precision {r["precision"]:.4f}; recall {r["recall"]:.4f}; F1 {r["F1"]:.4f}; control false-positive rate {r["false_positive_rate"]:.4f}; mean training AP {r["mean_training_AP"]:.4f}.')
    lines += ['', '## Interpretation and limits','',
    'Full logistic detects 52 of 55 held-out positive observations at the preset threshold, with 64.2% weighted precision and 4.41% weighted control false-positive rate. Its recall varies from 85.7% to 100% across the seven wheelchair people; per-trial AP ranges from 0.802 to 1.000. Neither apparent perfection in a small trial nor the pooled ROC-AUC establishes real-world accuracy.',
    '', 'Speed-only AP is 0.1024, lateral-only AP 0.7047 and coarse-time-feature AP 0.5556. Full logistic combines multiple time scales, temporal structure and lateral summaries; its advantage is not attributable to one isolated feature. The coarse ablation changes both feature content and time scale, so it is not a clean proof that high-frequency sway alone causes recognition.',
    '', 'The shuffled-training-label control has AP 0.1271 and ROC-AUC 0.5797. This is much lower than the leading model but not exactly the prevalence/chance line. One permutation is a sanity check, not a formal permutation test or p-value.',
    '', 'The MLP, CNN and GRU were evaluated under fixed small configurations and one seed per fold. They did not lead this comparison. Their results do not rule out better neural architectures or tuning. Trying increasingly many models on the same observations would also increase selection optimism.',
    '', 'SiME tracking research already documents walking head-sway fluctuations (Schumann et al., Hybrid Tracking System for Pedestrians in Dense Crowds, results section). The present signal is consistent with a recorded motion cue, but tracking differences, occlusion, height-related measurement processing, assistance and scene orientation remain possible confounders. We have not verified identical processing for every class/window or validated transfer to a different tracking system.',
    '', '## Prototype and framework integration','',
    '`src/motion_detector.py` scores a valid 101-position, 25Hz history. `research/export_detector_candidate.py` refits the selected family on all development records and saves a local-only model/card. This all-data refit is a prototype for future observations, not an independent validation model. Functional checks confirm translated-window inference agrees with direct model predictions and that sampling gaps are rejected.',
    '', 'Raw scores must not simply replace calibrated composition probabilities in the resource planner. The next study should assess/calibrate probabilities within training-only splits, test failure/abstention behaviour, and evaluate downstream decisions under explicitly hypothetical demand. The existing frozen planning experiment remains valid as its original separate experiment, and has not been silently rerun or reinterpreted.',
    '', '## Simulation decision','',
    'Do not synthesize extra training people yet. Current real-data holdouts support a useful exploratory candidate, while the larger source limitations require independent labelled people/recordings. JuPedSim CFSV2 is an operational pedestrian model, not a generator of measured head sway, wheelchair biomechanics or class-specific observation noise. It is not established as the generating model of the real SiME trajectories. Adding a handcrafted wheelchair-specific wobble would risk training the desired answer into synthetic labels.',
    '', 'If augmentation is pursued later, develop a training-only observation model, keep the real holdouts unchanged, compare real-only with real-plus-synthetic, and report failures. Synthetic success cannot validate an imposed class signature. A different real tracking setup and new wheelchair participants would be stronger evidence.',
    '', '## Reproducibility','',
    'Protocol: `research/detector_protocol_v1.md`. Build: `research/build_detector_data.py`. Benchmark: `research/run_detector_benchmark.py`. Independent audit: `research/audit_detector_benchmark.py`. Local results: `output/detector_v1/`. All source/data hashes, fixed settings, seed, versions and the dependency-only retry are retained. Independent AP/ROC arithmetic, weighted coverage, split assertions and inference checks pass. Participant-level artifacts are ignored by Git; no GitHub or manuscript update was made in this stage.',
    '', 'Primary tracking source: https://juser.fz-juelich.de/record/866598/files/SchumannJ.pdf?subformat=pdfa&version=1',
    'Grouped-validation guidance: https://scikit-learn.org/stable/modules/cross_validation.html',
    'Calibration guidance: https://scikit-learn.org/stable/modules/calibration.html','']
    (ROOT/'research/detector_results_v1.md').write_text('\n'.join(lines),encoding='utf-8')
    print('Saved complete report and four scientific figure files.')
if __name__=='__main__':main()
