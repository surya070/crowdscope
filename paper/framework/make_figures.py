"""Generate paper figures from aggregate results only."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/'figures';OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10.5,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(14,3.0));ax.set_xlim(0,14);ax.set_ylim(0,3);ax.axis('off')
stages=[('1  OBSERVE','Trajectories +\nwalkable geometry','Observed or\nsynthetic source'),
 ('2  MEASURE','Occupancy / density\n/ movement','Causal windows +\nquality flags'),
 ('3  INFER','Motion detector\n+ sigmoid calibration','Working probabilities\n+ flagged prior'),
 ('4  DECIDE','Capacity-constrained\nallocation','Explicit service model\n+ assumptions')]
for i,(title,body,note) in enumerate(stages):
 x=0.1+i*3.5
 ax.add_patch(FancyBboxPatch((x,0.8),3.25,2.0,boxstyle='round,pad=0.02',facecolor='#eef4fa',edgecolor='#2f597a',linewidth=1.2))
 ax.text(x+0.13,2.57,title,weight='bold',color='#193f60',fontsize=17,va='top')
 ax.text(x+0.13,2.08,body,fontsize=15,va='top',linespacing=1.2)
 ax.text(x+0.13,1.32,note,fontsize=13,color='#40566a',va='top',linespacing=1.2)
 if i<3:ax.annotate('',xy=(x+3.48,1.7),xytext=(x+3.26,1.7),arrowprops=dict(arrowstyle='->',lw=1.4,color='#294b68'))
ax.text(0.2,0.30,'Probabilities -> zone composition -> application',fontsize=13,color='#7c5530')
ax.text(7.7,0.30,'Audits and assumptions accompany outputs',fontsize=13,color='#40566a')
fig.savefig(OUT/'architecture.pdf',bbox_inches='tight');fig.savefig(OUT/'architecture.png',dpi=180,bbox_inches='tight');plt.close(fig)
data=json.loads((ROOT/'output/planning_evaluation_A1/analysis.json').read_text())['results']
labels={'base':'Base','unequal_zones':'Unequal zones','scarce':'3 units','abundant':'9 units','perfect_observation':'Perfect observation','uninformative':'Uninformative','prior_shift_low':'Low true prevalence','prior_shift_high':'High true prevalence','noise_misspecification':'Wrong noise rate','overconfident':'Overconfident','underconfident':'Underconfident','equal_demand_control':'Equal demand','demand_misspecification':'Wrong demand model','high_demand_contrast':'High demand contrast'}
fig,ax=plt.subplots(figsize=(4.9,5.0))
for i,row in enumerate(data):
 c=row['comparisons']['hard_observed'];m=c['mean_difference'];lo,hi=c['percentile_95_interval']
 ax.errorbar(m,i,xerr=[[max(0,m-lo)],[max(0,hi-m)]],fmt='o',ms=4,capsize=2,lw=1,color='#236b6b' if m<0 else '#af6936')
ax.axvline(0,color='#888888',lw=0.8,ls='--');ax.set_yticks(range(len(data)),[labels[r['case']] for r in data]);ax.invert_yaxis()
ax.set_xlabel('Difference in mean unmet requests\n(probabilistic - hard observed)');ax.grid(axis='x',alpha=.18);ax.spines[['top','right']].set_visible(False)
fig.tight_layout();fig.savefig(OUT/'effects.pdf');fig.savefig(OUT/'effects.png',dpi=200);plt.close(fig)
print('Generated architecture and all-condition comparison figures.')

models=json.loads((ROOT/'research/results/detector/benchmark_summary.json').read_text())['results']
cal=json.loads((ROOT/'research/results/calibrated_framework/calibration_summary.json').read_text())['crossed_person_trial']
fig,axes=plt.subplots(1,2,figsize=(7.2,3.7),gridspec_kw={'width_ratios':[1.15,1]},layout='constrained')
order=sorted(models,key=lambda n:models[n]['AP'])
axes[0].barh(range(len(order)),[models[n]['AP'] for n in order],color=['#146f83' if n=='Full logistic' else '#849da9' for n in order],height=.7)
axes[0].set(yticks=range(len(order)),yticklabels=order,xlim=(0,1.02),xlabel='Average precision (0 to 1)',title='(a) Fixed models / controls')
axes[0].tick_params(axis='both',labelsize=8);axes[0].set_xlabel('Average precision (0 to 1)',fontsize=9);axes[0].set_title('(a) Fixed models / controls',fontsize=10)
axes[0].grid(axis='x',alpha=.2)
axes[1].plot([0,1],[0,1],ls=':',color='grey',label='Ideal')
for key,col in [('raw','#9c6636'),('calibrated','#146f83')]:
 bins=cal[key]['reliability'];axes[1].plot([b['mean_probability'] for b in bins],[b['observed_fraction'] for b in bins],'-o',markersize=4,color=col,label=key.capitalize())
axes[1].set(xlim=(0,1),ylim=(0,1),xlabel='Mean predicted probability',ylabel='Observed wheelchair fraction')
axes[1].set_title('(b) Nested reliability',fontsize=10);axes[1].set_xlabel('Mean predicted probability',fontsize=9);axes[1].set_ylabel('Observed wheelchair fraction',fontsize=9);axes[1].tick_params(labelsize=8);axes[1].legend(fontsize=8);axes[1].grid(alpha=.2)
fig.savefig(OUT/'detection_calibration.pdf');fig.savefig(OUT/'detection_calibration.png',dpi=200);plt.close(fig)
print('Generated model-comparison and nested-calibration figure from aggregate records.')
