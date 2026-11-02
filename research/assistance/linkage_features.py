"""Past-only frozen-protocol features; targets remain outside this function."""
import math
import numpy as np
from shapely.geometry import Point,LineString
M=['count','mean_x','std_x','mean_y','std_y','mean_distance','max_distance','p90_distance','mean_speed','std_speed','p10_speed','p90_speed','stopped_fraction','speed_change','nearest_spacing','past_exit_count','elapsed','bottleneck_width','corridor_width','turn','client_count','helper_count','nominal_mean','nominal_min','nominal_std','radius_mean','radius_max','rear_nominal','free_time_mean','free_time_max','short_history_fraction']
COUNTS=['active_links','linked_client_fraction']
LINKS=COUNTS+['gap_mean','gap_max','speed_difference_mean','speed_difference_max','helper_minus_client_nominal','route_separation_max']
def roster(block):
 result={}
 for i,p in enumerate(block['pairs']):
  result[2*i+1]=dict(role='client',radius=.3,nominal=p['client_nominal_speed'])
  result[2*i+2]=dict(role='helper',radius=.22,nominal=p['helper_nominal_speed'])
 for i in range(len(block['extras'])):result[5+i]=dict(role='pedestrian',radius=.22,nominal=1.1)
 return result
def extract(frames,block,t,edges):
 past=[f for f in frames if f['t']<=t+1e-8];bytime={round(f['t'],6):f for f in past}
 now=bytime[round(t,6)];exited=set(now['exited']);pos={int(k):np.array(v) for k,v in now['positions'].items() if int(k) not in exited}
 if not pos:return None
 rr=roster(block);ids=sorted(pos);speed={};short={};changes=[]
 for i in ids:
  points=[]
  for offset in [1.,.8,.6,.4,.2,0.]:
   f=bytime.get(round(t-offset,6));p=None if f is None else f['positions'].get(str(i),f['positions'].get(i))
   points.append(None if p is None else np.array(p))
  short[i]=any(p is None for p in points)
  speed[i]=0. if short[i] else float(np.linalg.norm(points[-1]-points[0]))
  changes.append(0. if short[i] else float(np.linalg.norm(points[-1]-points[-3]))/.4-float(np.linalg.norm(points[-3]-points[0]))/.6)
 route=LineString(block['known_route']);exitpoint=(6,block['exit_plane']) if block['exit_axis']==1 else (block['exit_plane'],0)
 exit_s=route.project(Point(exitpoint));progress={i:route.project(Point(pos[i])) for i in ids}
 dist=np.array([max(0,exit_s-progress[i]+rr[i]['radius']) for i in ids]);xy=np.array([pos[i] for i in ids]);speeds=np.array([speed[i] for i in ids]);nom=np.array([rr[i]['nominal'] for i in ids]);rad=np.array([rr[i]['radius'] for i in ids])
 nn=[min((math.dist(pos[i],pos[j]) for j in ids if i!=j),default=0) for i in ids]
 before=bytime.get(round(t-1,6),{'exited':[]});past_exits=len(exited-set(before['exited']))
 values=[len(ids),xy[:,0].mean(),xy[:,0].std(),xy[:,1].mean(),xy[:,1].std(),dist.mean(),dist.max(),np.quantile(dist,.9),speeds.mean(),speeds.std(),np.quantile(speeds,.1),np.quantile(speeds,.9),np.mean(speeds<.1),np.mean(changes),np.mean(nn),past_exits,t,block['bottleneck_width_m'],block['corridor_width_m'],int(block['exit_axis']==1),sum(rr[i]['role']=='client' for i in ids),sum(rr[i]['role']=='helper' for i in ids),nom.mean(),nom.min(),nom.std(),rad.mean(),rad.max(),nom[np.argmax(dist)],np.mean(dist/nom),np.max(dist/nom),np.mean(list(short.values()))]
 row=dict(zip(M,map(float,values)))
 active=[(c,h) for c,h in edges if c in pos and h in pos];gaps=[math.dist(pos[c],pos[h]) for c,h in active];dv=[abs(speed[c]-speed[h]) for c,h in active]
 linkvalues=[len(active),len(active)/max(1,row['client_count']),np.mean(gaps) if gaps else 0,max(gaps,default=0),np.mean(dv) if dv else 0,max(dv,default=0),np.mean([rr[h]['nominal']-rr[c]['nominal'] for c,h in active]) if active else 0,max((abs(progress[c]-progress[h]) for c,h in active),default=0)]
 row.update(zip(LINKS,map(float,linkvalues)));assert all(np.isfinite(v) for v in row.values());return row
