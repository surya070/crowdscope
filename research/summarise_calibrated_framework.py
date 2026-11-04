"""Scientific calibration plots, complete report and model card."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
for folder in ['authoring','detector','recovery-r1']:sys.path.insert(0,str(ROOT/'.deps'/folder))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=ROOT/'output/calibrated_framework_v1'

def main():
    cal=json.loads((OUT/'calibration_summary.json').read_text());pipeline=json.loads((OUT/'pipeline_summary.json').read_text());c=cal['crossed_person_trial']
    fig,axes=plt.subplots(1,2,figsize=(10,4.2),layout='constrained')
    axes[0].plot([0,1],[0,1],ls=':',color='grey',label='Ideal reliability')
    for k,col in [('raw','#9c6636'),('calibrated','#146f83')]:
        bins=c[k]['reliability'];axes[0].plot([b['mean_probability'] for b in bins],[b['observed_fraction'] for b in bins],'-o',color=col,label=k.capitalize())
    axes[0].set(xlabel='Mean predicted probability in bin',ylabel='Observed wheelchair fraction',title='Nested person + trial holdouts',xlim=(0,1),ylim=(0,1));axes[0].legend(fontsize=8);axes[0].grid(alpha=.2)
    names=['Prior only','Raw detector','Calibrated detector'];axes[1].bar(names,[c[k]['Brier'] for k in ['prior','raw','calibrated']],color=['#acb6bd','#9c6636','#146f83'])
    axes[1].set(ylabel='Weighted Brier loss (lower is better)',title='Probability quality on excluded records');axes[1].tick_params(axis='x',labelsize=9);axes[1].grid(axis='y',alpha=.2)
    fig.savefig(OUT/'calibration.png',dpi=170);fig.savefig(OUT/'calibration.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4),layout='constrained');names=['Prior only','Raw detector','Calibrated','Hard labels'];vals=[pipeline['count_errors_nonempty'][k]['MAE'] for k in ['prior','raw','calibrated','hard']]
    ax.bar(names,vals,color=['#acb6bd','#9c6636','#146f83','#718c9e']);ax.set(ylabel='Mean absolute count error (people / zone)',title='Whole-trial replay: 187 nonempty zone checkpoints');ax.grid(axis='y',alpha=.2)
    fig.savefig(OUT/'composition.png',dpi=170);fig.savefig(OUT/'composition.pdf');plt.close(fig)
    model=OUT/'calibrated_model_LOCAL_ONLY.joblib'
    card=dict(target='Wheelchair-associated membership in audited SiME trials 501–508',
        input='101 contiguous XY positions at 25Hz, four seconds, ending at first forward x=-1 crossing in passage-aligned metres',
        base='Full logistic, C=.2, balanced; 54 past-only features; training-only standardisation',
        calibration='Fixed regularised sigmoid, C=1; natural prevalence; original crossed out-of-fold decisions for final calibrator',
        calibration_evaluation='Separate nested 55 crossed trial/person outer folds; all outer test data excluded from calibration',
        data='711 track windows, 55 positive repeated observations of seven wheelchair people; conditional roster-complement controls',
        scope='All-development refit; not a held-out demonstration model; use the saved held-trial artifacts for replay evaluation',
        unseen_control_people_guaranteed=False,independent_external_validation=False,
        assistance_demand_validated=False,age_recognition=False,calibration_under_population_shift_validated=False,
        hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in [model,ROOT/'research/build_detector_data.py',ROOT/'src/calibrated_detector.py',ROOT/'research/calibrated_framework_protocol_v1.md']},
        evaluation=c,limits=['Head-motion and tracking confounding','Very small repeated-participant cohort','Prior until first qualifying trigger','Unknown repeat controls','Cached estimates and scene transfer require validation'])
    (OUT/'model_card.json').write_text(json.dumps(card,indent=2))
    q=pipeline['hypothetical_planning'];raw=c['raw'];cp=c['calibrated'];reduction=(raw['Brier']-cp['Brier'])/raw['Brier']
    report=f'''# Calibrated CrowdScope framework — 5 November 2026

## Implemented connection

Recorded trajectories -> four-second movement features -> calibrated working
wheelchair probability -> geometry-aware occupancy/density/motion -> expected
zone composition and working count intervals -> configured service-demand model
-> exact finite-capacity resource allocation.

`src/calibrated_detector.py` loads a saved base/calibrator pair.
`src/crowd_framework.py` streams timestamped positions without receiving labels.
`research/run_framework_csv.py` connects canonical CSV to zones/configuration and
writes JSONL snapshots. `app/framework.html` is the interactive local replay.
The previous synthetic demo and frozen experiments remain unchanged.

## Probability evaluation: excluded people and trials

The already-selected full logistic detector was calibrated with a fixed sigmoid.
Each of 55 outer folds excludes the target wheelchair person and recording trial;
2,268 inner crossed folds produce calibration scores without outer-test access.
Known mapped test-control identities are excluded too. Unknown repeated controls
remain a limitation. All underlying data were previously explored and model
family selection used those exploratory results; this is not pristine external
validation or a preregistration.

- Raw Brier loss: {raw['Brier']:.6f}; calibrated: {cp['Brier']:.6f} ({100*reduction:.1f}% reduction).
- Raw log loss: {raw['log_loss']:.6f}; calibrated: {cp['log_loss']:.6f}.
- Raw fixed-bin ECE: {raw['ECE_fixed_bins']:.6f}; calibrated: {cp['ECE_fixed_bins']:.6f}.
- Calibrated AP: {cp['AP']:.6f}; ROC-AUC: {cp['ROC_AUC']:.6f}.
- At the unchanged 0.5 threshold: precision {100*cp['precision']:.1f}%, recall {100*cp['recall']:.1f}%.
- Mean calibrated probability: {cp['mean_probability']:.6f}; observed positive fraction: {cp['prevalence']:.6f}.

Reliability is improved relative to raw scores but is not established for every
scene/subgroup. A prior-only predictor has low ECE by construction while providing
poor individual discrimination; Brier loss includes both calibration and
resolution. The fixed-bin curve is descriptive with only 55 positive track
observations of seven repeated people. No independent-sample significance or
calibration guarantee is claimed.

## Whole-crowd integration: a separate weaker generalisation task

We trained one coherent leave-one-trial-out model for each recorded trial,
calibrated inside that training set using seven inner trial folds (56 additional
inner folds). People may recur in training and test. This permits a realistic
whole-roster replay without secretly combining participant-specific models into
one deployable model. It must not be described as unseen-person whole-crowd
validation.

The stream processes the original 25Hz records and emits 759 one-second replay
snapshots. All 711 eligible streamed detector outputs match the corresponding
offline held-trial predictions. There are 48 fixed checkpoints and 192 zone
records (187 nonempty), with no geometry-withheld snapshots. Measurements use
walkable polygons clipped to [-6,-1.65,2.4,1.65], including obstacle exclusions.

Nonempty-zone wheelchair-count MAE (people / zone):

- Population prior: {pipeline['count_errors_nonempty']['prior']['MAE']:.6f}.
- Raw detector plus prior before eligibility: {pipeline['count_errors_nonempty']['raw']['MAE']:.6f}.
- Calibrated detector plus prior: {pipeline['count_errors_nonempty']['calibrated']['MAE']:.6f}.
- Thresholded calibrated labels: {pipeline['count_errors_nonempty']['hard']['MAE']:.6f}.

The mean detector coverage is {100*pipeline['mean_detector_coverage_nonempty_snapshots']:.1f}% of visible occupants across
nonempty checkpoints, because many have not reached the validated x=-1 trigger.
Those people retain a flagged training prior; they are not silently classified.
A broader early/sliding-window recogniser needs its own evaluation.

Working 90% count intervals cover the recorded count in
{100*pipeline['working_interval_coverage_nonempty']:.1f}% of nonempty zone records. This is conservative in this small
sample, not proof of nominal coverage elsewhere. Poisson-binomial intervals
assume independent memberships and do not capture common model/calibration error.

## Conditional resource planning: retained negative result

Using budget6, capacity2 and assumed request rates .1/.4, mean expected unmet
requests evaluated under the label-conditioned hypothetical demand model are:

- Prior-only allocation: {q['prior']:.9f}.
- Raw detector allocation: {q['raw']:.9f}.
- Calibrated allocation: {q['calibrated']:.9f}.
- Hard-label allocation: {q['hard']:.9f}.
- Known-class reference: {q['known_class']:.9f}.

Calibration improves probability quality and composition estimates but does not
improve the default allocation result. Raw and calibrated policies have equal
mean loss here; prior-only is marginally better and hard labels also do slightly
better. These small differences are descriptive and depend on the declared
request model. No real requests, service times or actual assistance outcomes
were recorded. Wheelchair membership does not itself establish service need.

## Verification and reproducibility

- All 46 unit tests pass, including temporal gaps, prior fallback, direct use of
  calibrated probabilities, cached estimates and removal of absent occupants.
- Independent audit checks 63 outer folds, 2,324 inner folds, locked hashes,
  arithmetic Brier/log loss, count conservation, bounds and causal timestamps.
- 100 recorded-state Python/JavaScript planning fixtures agree exactly in their
  allocation and to numerical tolerance in expected loss.
- The local UI supports eight trials, time replay, probability-policy switching,
  budgets, capacity and explicit request-rate assumptions.

Model/card, predictions and participant-level replay files are local and ignored
by Git. The final model is refitted on all development data; it must not be used
to report new validation scores on those same records. The demo instead uses
held-trial models. The paper and remote GitHub were not changed in this stage.

## Interpretation

This is an implemented modular trajectory-to-decision framework with an
exploratory calibrated recognition component. It is not a validated general
demographic recogniser, child/age detector, operational staffing system or
evacuation-time predictor. Observed state, inferred membership and hypothetical
demand remain explicitly separate. Bayes is not applied again to the same
movement evidence after the calibrated posterior.

Next research priorities: independent participants and tracking systems; earlier
observation windows; failure/abstention and population-shift handling; spatially
correlated uncertainty; and empirically annotated service needs. Synthetic
augmentation cannot establish a real movement signature imposed by its generator.

Calibration guidance: https://scikit-learn.org/1.7/modules/calibration.html
'''
    (ROOT/'research/calibrated_framework_results_v1.md').write_text(report,encoding='utf-8')
    print('Saved model card, complete framework report and scientific figures.')
if __name__=='__main__':main()
