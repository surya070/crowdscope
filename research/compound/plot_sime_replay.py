from pathlib import Path
import os,json
R=Path(__file__).resolve().parents[2];O=R/'output/sime_replay_v2'
os.environ['MPLCONFIGDIR']=str(R/'output/plot_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':160})
held=all((O/f'held_out_{t}.json').exists() for t in ['1503','1505'])
trials=['1503','1505'] if held else ['1501','1507']
prefix='held_out' if held else 'selected_development'
fig,axs=plt.subplots(1,3,figsize=(14,4.4),layout='constrained')
for ax,tid in zip(axs[:2],trials):
 r=json.loads((O/f'{prefix}_{tid}.json').read_text());origin=r['origin_s']
 source=np.sort(list(r['observed_crossings'].values()))-origin
 predicted=np.sort(list(r['crossings'].values()))-origin
 baseline=np.sort([a['t']+8.4/r['params']['speed'] for a in r['arrivals']])-origin
 for values,name,color in [(source,'Observed head crossings','#173244'),(predicted,'Calibrated 2D replay','#197B79'),(baseline,'No-interaction reference','#AD604A')]:
  ax.step(values,np.arange(1,len(values)+1),where='post',label=name,color=color)
 ax.set(xlabel='Time since first measured inlet arrival (s)',ylabel='Cumulative downstream crossings (people)',title=f'{"Held-out" if held else "Development"} trial {tid}')
 ax.legend(fontsize=8)
 ax=axs[2]
 ids=sorted(r['observed_crossings'],key=int)
 x=[r['observed_crossings'][i]-origin for i in ids];y=[r['crossings'][i]-origin for i in ids]
 ax.scatter(x,y,s=15,alpha=.65,label=tid)
ax=axs[2];bound=max(ax.get_xlim()[1],ax.get_ylim()[1]);ax.plot([0,bound],[0,bound],color='gray',linestyle='--',linewidth=1)
ax.set(xlabel='Observed crossing time after inlet origin (s)',ylabel='Simulated crossing time after inlet origin (s)',title='Individual timing agreement'+(' on test runs' if held else ' on development'))
ax.legend(title='Trial',fontsize=8)
fig.suptitle('Frozen SiME reference replay: held-out runs, observed inflow supplied' if held else 'Development calibration only: held-out SiME validation remains pending',fontsize=14)
fig.supxlabel('Source: SiME trials '+ '/'.join(trials)+'. Recorded inlet schedule is supplied. New JuPedSim reference backend; no wheelchair-helper validation.',fontsize=9)
dest=O/('held_out_replay.png' if held else 'development_replay.png')
fig.savefig(dest);plt.close(fig)
print(dest)
