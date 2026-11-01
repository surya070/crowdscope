"""Generate the full, unfiltered supplementary benchmark report and figure."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.recovery.common import ROOT,read,write,sha
from src.broad_prediction import FAMILIES
O=ROOT/'output/compound/broad_prediction_001'
NAMES={'ridge':'Ridge','rbf':'RBF ridge','boosting':'Boosting','mlp':'MLP','gru':'GRU','history_ridge':'History ridge'}
def main():
 audit=read(O/'audit.json');assert audit['status']=='passed'
 s=read(O/'summary.json');sel=read(O/'selection.json')
 fig,axes=plt.subplots(1,2,figsize=(12,4.4),sharey=True)
 for ax,partition,title in zip(axes,['fresh_geometry_test','fresh_known_test'],['New length–width combinations (48 runs)','Known configurations, fresh seeds (96 runs)']):
  x=np.arange(6)
  for j,(info,color) in enumerate(zip(['A','M','F'],['#8a9bad','#167d9a','#bd6946'])):
   ax.bar(x+(j-1)*.24,[s[partition][f][info]['mae_s'] for f in FAMILIES],width=.23,label=info,color=color)
  ax.set_xticks(x,[NAMES[f] for f in FAMILIES],rotation=30,ha='right');ax.set_title(title,fontsize=11);ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
 axes[0].set_ylabel('Hierarchical MAE (seconds)');axes[1].legend(title='Information set',ncols=3,loc='upper left')
 fig.suptitle('Synthetic follow-up: validation-selected settings; all families shown',fontsize=13)
 fig.tight_layout();fig.savefig(O/'learner_comparison.png',dpi=200);plt.close(fig)
 text='# Broader prediction comparison: completed exploratory follow-up\n\n'
 text+='This extends the learning comparison, not the empirical validity of the generator. A uses aggregate motion; M adds the known nominal mobility roster; F adds supplied family and assistance links. The original 240-run study and its negative primary result remain unchanged.\n\n'
 p=s['fresh_geometry_test']['validation_selected'];delta=p['M_minus_F'];ci=delta['conditional_interval_s']
 text+=f"Validation selected A: {NAMES[sel['best_family']['A']]}, M: {NAMES[sel['best_family']['M']]}, F: {NAMES[sel['best_family']['F']]}. On the new configurations, MAE was A {p['metrics']['A']['mae_s']:.3f} s, M {p['metrics']['M']['mae_s']:.3f} s and F {p['metrics']['F']['mae_s']:.3f} s. The selected M-minus-F contrast was {delta['reduction_s']:+.3f} s, conditional descriptive 95% interval [{ci[0]:+.3f}, {ci[1]:+.3f}] s. Positive contrasts favour F.\n\n"
 text+='## Design and protection against test reuse\n\nThe already-inspected 192 original main trajectories became development data: 128 fitting and 64 validation runs, split by complete four-condition matched blocks across G1–G4. Three candidate settings were evaluated per family and information set (54 candidates). Settings and 18 fitted models were frozen before generating any of the 144 fresh test trajectories.\n\nThe primary test comprises 48 runs/12 matched blocks on G5 (24 m, 1.05 m) and G6 (28 m, 1.15 m). The secondary test comprises 96 runs/24 blocks on G1–G4 under fresh seeds. All '+str(audit['new_queries'])+' queries and all 144 completed runs were retained. The two new configurations change length/width, not route topology.\n\n'
 text+='Static ridge, RBF ridge, gradient boosting and MLP see the same last causal vector. GRU and history ridge receive nine causal vectors over 1.6 seconds. History ridge controls for additional history. MLP and GRU each average three fixed initialisations. All models use identical train/validation partitions and hierarchical sample weights; search counts are equal within each A/M/F family, not equal runtime budgets across families.\n\n'
 text+='## Complete results\n\n'
 for partition,title in [('fresh_geometry_test','New configurations: primary follow-up'),('fresh_known_test','Known configurations with fresh seeds: secondary')]:
  text+='### '+title+'\n\n| Learner | A MAE (s) | M MAE (s) | F MAE (s) | M minus F (s) | Conditional 95% interval (s) |\n|---|---:|---:|---:|---:|---|\n'
  for f in FAMILIES:
   r=s[partition][f];d=r['M_minus_F'];lo,hi=d['conditional_interval_s']
   text+=f"| {NAMES[f]} | {r['A']['mae_s']:.3f} | {r['M']['mae_s']:.3f} | {r['F']['mae_s']:.3f} | {d['reduction_s']:+.3f} | [{lo:+.3f}, {hi:+.3f}] |\n"
  r=s[partition]['validation_selected'];d=r['M_minus_F'];lo,hi=d['conditional_interval_s']
  text+=f"| Validation-selected family per information set | {r['metrics']['A']['mae_s']:.3f} | {r['metrics']['M']['mae_s']:.3f} | {r['metrics']['F']['mae_s']:.3f} | {d['reduction_s']:+.3f} | [{lo:+.3f}, {hi:+.3f}] |\n\n"
 text+='![All learner results](learner_comparison.png)\n\n## Selection and audit\n\n| Family | Information | Selected setting | Validation MAE (s) |\n|---|---|---|---:|\n'
 for f in FAMILIES:
  for i in ['A','M','F']:
   r=sel['family_settings'][f+'__'+i];text+=f"| {NAMES[f]} | {i} | {json.dumps(r['setting'])} | {r['validation_mae_s']:.6f} |\n"
 text+=f"\nIndependent standard-library MAE calculations agreed within {audit['independent_mae_max_difference_s']:.2g} s. Fresh-process predictions from all 18 saved models agreed within {audit['fresh_process_prediction_max_difference_s']:.2g} s. Source, fitted-model and trajectory hashes passed. Static/history endpoints matched, and removing future frames and hidden outcomes did not alter the tested input prefix. Full metrics, candidate traces and predictions are saved alongside this report.\n\n"
 text+='## Interpretation and limitations\n\nNo family-matched comparison produced a conditional interval wholly favouring F. Several families had small favourable point estimates on the new configurations, but these were uncertain and did not consistently recur on the fresh-seed test. The validation-selected F was slightly worse on the new configurations and slightly better on the secondary set; both selected-system intervals spanned zero. These findings support a mixed/inconclusive incremental relationship result rather than a demonstrated benefit. GRU and boosting did not consistently outperform the simpler references in this bounded search.\n\nThis follow-up addresses the narrow concern that results depended only on ridge. Any improvement is conditional on this synthetic generator, exact nominal capabilities and supplied links. It does not establish realistic assistance gains, infer ages or relationships, or validate real evacuation times. The SiME replay remains a separate unassisted reference-model test. The expanded development set differs from the original study, so scores from the two studies cannot isolate a learner effect.\n\nIntervals resample matched blocks within fixed configurations and keep the selected models fixed. They exclude training, selection, generator and real-population uncertainty; the exploratory contrasts are not multiplicity-adjusted. Three settings and small neural architectures are a bounded benchmark, not exhaustive tuning or proof of universal superiority. New human data with mapped helper and mobility roles remain the main empirical need.\n\n'
 text+='## Reproduction\n\nUse the saved models for evaluation; do not retrain or overwrite the freeze. Project-local sklearn 1.7.2, joblib 1.5.2, threadpoolctl 3.6.0 and mpmath 1.3.0 accompany the existing CPU PyTorch runtime. Run `research/compound/run_broad_prediction.py evaluate`, then `research/compound/audit_broad_prediction.py` and this report generator with the project root and local dependency folders on PYTHONPATH. `train` refuses an existing model freeze.\n'
 (O/'report.md').write_text(text,encoding='utf-8')
 write(O/'status.json',{'phase':'complete','audit':'passed','new_runs':144,'new_queries':audit['new_queries'],'report_sha256':sha(O/'report.md')})
 print(text[:1250])
if __name__=='__main__':main()
