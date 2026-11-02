"""Descriptive development analysis; no fitting, inference tests or new raw downloads."""
from pathlib import Path
import sys,zipfile,json,csv,re,hashlib
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[2]
import os
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.deps/matplotlib_cache'))
sys.path.insert(0,str(ROOT/'.deps/plotting'))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
OUT=ROOT/'research/data/movement';OUT.mkdir(exist_ok=True)
bands=[(-6,-4),(-4,-2),(-2,0),(0,2.4)]
def write(name,rows):
 with (OUT/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
labels=list(csv.DictReader((ROOT/'research/data/label_audit.csv').open()))
wc={(r['trial'],int(r['track_id'])) for r in labels if r['wheelchair_label']=='documented_wheelchair_id'}
persons=[];events=[];coverage=[];summary=[]
with zipfile.ZipFile(next((ROOT/'backups').glob('*.zip'))) as z:
 verify=json.loads((ROOT/'backups/backup_verification.json').read_text())
 for trial in ['501','507','1301','1307','1501','1503','1505','1507']:
  name=f'data/raw/sime2017/members/{trial}.txt';raw=z.read(name)
  assert hashlib.sha256(raw).hexdigest()==verify['files'][name]['sha256']
  tracks=defaultdict(list)
  for line in raw.decode().splitlines():
   if not line.strip() or line.startswith('#'):continue
   a=line.split();tracks[int(a[0])].append((int(a[1]),float(a[2]),float(a[3])))
  byframe=defaultdict(list);samples=[];cross=[]
  for tid,points in tracks.items():
   a=np.asarray(sorted(points));f=a[:,0].astype(int);xy=a[:,1:]
   for frame,p in zip(f,xy):
    if frame%5==0:byframe[frame].append((tid,p))
   for i in range(5,len(a)-5):
    if f[i]%5 or f[i+5]-f[i-5]!=10:continue
    speed=float(np.linalg.norm(xy[i+5]-xy[i-5])/.4)
    samples.append((tid,int(f[i]),float(xy[i,0]),speed))
   hits=np.where((a[:-1,1]<2.4)&(a[1:,1]>=2.4)&(np.diff(f)==1))[0]
   if len(hits):
    k=hits[0];t=float((f[k]+(2.4-a[k,1])/(a[k+1,1]-a[k,1]))/25)
    cross.append((t,tid))
  nn={}
  for frame,items in byframe.items():
   p=np.array([p for tid,p in items]);dist=np.linalg.norm(p[:,None,:]-p[None,:,:],axis=2);np.fill_diagonal(dist,np.inf)
   for j,(tid,pos) in enumerate(items):nn[tid,frame]=float(dist[j].min()) if len(items)>1 else np.nan
  for tid in tracks:
   group='wheelchair' if (trial,tid) in wc else 'other_in_wheelchair_trial' if trial in ['501','507'] else 'reference_trial' if trial.startswith('15') else 'heterogeneous_trial_unclassified'
   for bi,(lo,hi) in enumerate(bands):
    obs=[(s,nn.get((t,f),np.nan)) for t,f,x,s in samples if t==tid and lo<=x<hi]
    if not obs:continue
    speeds=np.array([s for s,d in obs]);spacing=np.array([d for s,d in obs]);spacing=spacing[np.isfinite(spacing)]
    persons.append(dict(trial=trial,track_id=tid,group=group,band=bi,band_start_m=lo,band_end_m=hi,n_samples=len(obs),median_speed_mps=float(np.median(speeds)),fraction_speed_below_0_1=float(np.mean(speeds<.1)),median_nearest_head_distance_m=float(np.median(spacing)) if len(spacing) else ''))
  cross.sort()
  for i,(t,tid) in enumerate(cross):events.append(dict(trial=trial,track_id=tid,time_s=t,preceding_headway_s=t-cross[i-1][0] if i else '',wheelchair=(trial,tid) in wc))
  for t in [0,2,5,10,20]:
   frame=t*25;visible=sum(p[0][0]<=frame<=p[-1][0] for p in tracks.values());already=sum(ct<=t for ct,tid in cross)
   coverage.append(dict(trial=trial,time_s=t,visible_tracks=visible,cohort_track_count=len(tracks),observed_crossings_so_far=already,not_yet_crossed_and_visible=sum(p[0][0]<=frame<=p[-1][0] and not any(tid==id_ and ct<=t for ct,id_ in cross) for tid,p in tracks.items())))
  summary.append(dict(trial=trial,tracks=len(tracks),observed_crossings=len(cross),median_headway_s=float(np.median(np.diff([t for t,id_ in cross]))),observed_span_flow_per_s=(len(cross)-1)/(cross[-1][0]-cross[0][0]),complete_target=len(cross)==len(tracks)))
write('person_band_metrics.csv',persons);write('crossing_events.csv',events);write('checkpoint_coverage.csv',coverage);write('trial_flow_summary.csv',summary)
groups=[]
for trial in ['501','507','1501','1503','1505','1507']:
 for group in sorted({p['group'] for p in persons if p['trial']==trial}):
  for bi in range(4):
   rows=[p for p in persons if p['trial']==trial and p['group']==group and p['band']==bi]
   if rows:groups.append(dict(trial=trial,group=group,band=bi,people=len(rows),median_of_person_speed_medians=float(np.median([r['median_speed_mps'] for r in rows])),median_of_person_spacing_medians=float(np.median([r['median_nearest_head_distance_m'] for r in rows if r['median_nearest_head_distance_m']!='']))))
write('group_band_summary.csv',groups)
fig,axes=plt.subplots(1,2,figsize=(11,4.2))
for ax,trial in zip(axes,['501','507']):
 for group,color,label in [('wheelchair','#b34b32','Documented wheelchair users'),('other_in_wheelchair_trial','#27689a','Other tracks in same trial')]:
  rows=[r for r in groups if r['trial']==trial and r['group']==group]
  ax.plot([r['band'] for r in rows],[r['median_of_person_speed_medians'] for r in rows],marker='o',color=color,label=label)
 ax.set(title=f'Trial {trial} (development)',xlabel='Position relative to bottleneck entrance',ylabel='Median of individual median speeds (m/s)',xticks=range(4),xticklabels=['−6 to −4 m','−4 to −2 m','−2 to 0 m','0 to 2.4 m']);ax.grid(alpha=.2)
axes[0].legend(fontsize=8);axes[1].text(.02,.96,'Wheelchair sample: 7 upstream; 6 in final two bands',transform=axes[1].transAxes,va='top',fontsize=8)
fig.suptitle('Observed movement by spatial band — descriptive, unequal crowd conditions',fontsize=12)
fig.tight_layout();fig.savefig(OUT/'speed_by_band.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7,4.2))
for trial in ['501','507','1501','1507']:
 ts=sorted(r['time_s'] for r in events if r['trial']==trial);ax.step(ts,range(1,len(ts)+1),where='post',label=f'{trial}'+(' (91/92 observed)' if trial=='507' else ''))
ax.set(xlabel='Recording time (s)',ylabel='Cumulative observed head-centre crossings',title='Recorded passage curves — cohorts and conditions differ');ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'passage_curves.png',dpi=180);plt.close(fig)
print(json.dumps(summary,indent=2));print('Files saved in',OUT)
