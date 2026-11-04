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
 ('3  ESTIMATE','Profile probabilities\n+ composition','Supplied / hypothetical\nmetadata'),
 ('4  DECIDE','Capacity-constrained\nallocation','Explicit service model\n+ assumptions')]
for i,(title,body,note) in enumerate(stages):
 x=0.1+i*3.5
 ax.add_patch(FancyBboxPatch((x,0.8),3.25,2.0,boxstyle='round,pad=0.02',facecolor='#eef4fa',edgecolor='#2f597a',linewidth=1.2))
 ax.text(x+0.13,2.57,title,weight='bold',color='#193f60',fontsize=17,va='top')
 ax.text(x+0.13,2.08,body,fontsize=15,va='top',linespacing=1.2)
 ax.text(x+0.13,1.32,note,fontsize=13,color='#40566a',va='top',linespacing=1.2)
 if i<3:ax.annotate('',xy=(x+3.48,1.7),xytext=(x+3.26,1.7),arrowprops=dict(arrowstyle='->',lw=1.4,color='#294b68'))
ax.text(0.2,0.30,'Optional JuPedSim backend -> same interface',fontsize=13,color='#7c5530')
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
