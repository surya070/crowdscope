"""Observed-inflow-driven reference replay, separate from frozen compound sources."""
from pathlib import Path
import re,json,hashlib,math
import numpy as np
import shapely
from shapely import wkt
from shapely.geometry import Point,box
from shapely.ops import nearest_points
import jupedsim as jps

ROOT=Path(__file__).resolve().parents[1]
INLET=-6.0
MEASURE=2.4

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def first_crossing(a,plane):
 candidates=np.flatnonzero((a[:-1,2]<plane)&(a[1:,2]>=plane)&(np.diff(a[:,1])==1))
 if not len(candidates):return None
 j=int(candidates[0]);q=(plane-a[j,2])/(a[j+1,2]-a[j,2])
 return {'t':float((a[j,1]+q)/25),'y':float(a[j,3]+q*(a[j+1,3]-a[j,3]))}

def load_trial(tid):
 path=ROOT/'data/raw/sime2017/members'/f'{tid}.txt'
 a=np.loadtxt(path)
 if not np.isfinite(a).all():raise ValueError('Nonfinite trajectories')
 if len(np.unique(a[:,:2],axis=0))!=len(a):raise ValueError('Duplicate track/frame')
 text=path.read_text(encoding='utf-8')
 if '# framerate: 25 fps' not in text:raise ValueError('Unknown frame rate')
 meta=json.loads((ROOT/'research/data_search_20261030/sime_metadata_prefix.txt').read_text(encoding='utf-8'))['experiment']
 row=next(r for r in meta['run'] if r['run_name']==str(tid))
 area=wkt.loads(row['wkt_geometry'])
 if not area.is_valid:raise ValueError('Invalid supplied geometry')
 index=json.loads((ROOT/'data/raw/sime2017/archive_index.json').read_text())
 info=next(i for i in index['members'] if i['name']==f'{tid}.txt')
 import zlib
 if zlib.crc32(path.read_bytes())!=info['crc32']:raise ValueError('ZIP CRC mismatch')
 arrivals=[];targets={};missing=[];gaps=0
 for pid in np.unique(a[:,0]).astype(int):
  track=a[a[:,0]==pid];track=track[np.argsort(track[:,1])]
  if np.any(np.diff(track[:,1])!=1):gaps+=1
  entry=first_crossing(track,INLET);exit=first_crossing(track,MEASURE)
  if entry is None or exit is None or exit['t']<=entry['t']:missing.append(int(pid));continue
  arrivals.append({'id':int(pid),'t':entry['t'],'position':[INLET,entry['y']]})
  targets[int(pid)]=exit['t']
 counts_match=len(np.unique(a[:,0]))==row['number_participants']
 return {'id':str(tid),'source_sha256':sha(path),'area':area,'metadata':row,'arrivals':sorted(arrivals,key=lambda r:(r['t'],r['id'])),'targets':targets,'missing_ids':missing,'tracks':len(np.unique(a[:,0])),'metadata_count_agrees':counts_match,'gapped_tracks':gaps,'complete':not missing and counts_match}

def replay(area,arrivals,params,dt=.02,save_frames=False,horizon=300):
 if not arrivals:raise ValueError('Empty inlet cohort')
 v=params['speed'];r=params['radius'];T=params['time_gap']
 start=min(x['t'] for x in arrivals)
 safe=area.buffer(-r-.005)
 if safe.is_empty:raise ValueError('No body-safe area')
 mapped=[]
 for entry in arrivals:
  p=Point(entry['position']);q=p if safe.covers(p) else nearest_points(safe,p)[0]
  displacement=p.distance(q)
  if displacement>.25+1e-9:raise ValueError(f'Head/body correction exceeds 0.25 m: {displacement}')
  if abs(q.x-INLET)>1e-7:raise ValueError('Lateral mapping unexpectedly changed x')
  mapped.append({**entry,'mapped_position':(q.x,q.y),'mapping_displacement_m':displacement})
 sim=jps.Simulation(model=jps.CollisionFreeSpeedModelV2(),geometry=area,dt=dt)
 stage=sim.add_exit_stage([(3.8,-.42),(4.7,-.42),(4.7,.42),(3.8,.42)])
 journey=sim.add_journey(jps.JourneyDescription([stage]))
 native_ids={};inserted=set();removed=set();crossings={};admissions={};previous={};frames=[]
 max_overlap=max_wall=0.;fail=None
 stride=max(1,round(.2/dt))
 for step in range(round(horizon/dt)+1):
  t=step*dt;absolute=start+t
  positions={native_ids[a.id]:tuple(a.position) for a in sim.agents()}
  newly_removed=set(previous)-set(positions)
  if any(i not in crossings for i in newly_removed):raise RuntimeError('Native removal before measurement crossing')
  removed|=newly_removed
  for pid,xy in positions.items():
   if pid in previous and previous[pid][0]<MEASURE<=xy[0] and pid not in crossings:
    q=(MEASURE-previous[pid][0])/(xy[0]-previous[pid][0]);crossings[pid]=start+(step-1+q)*dt
  for event in mapped:
   pid=event['id']
   if pid in inserted or event['t']>absolute+1e-9:continue
   point=event['mapped_position']
   # Native insertion constraints may use the preceding spatial-index snapshot.
   # Reserve one maximum movement step as well as the fixed separation margin.
   if any(math.dist(point,xy)<2*r+v*dt+.005 for xy in positions.values()):
    if absolute-event['t']>30:fail='Inlet delay exceeded fixed 30 s cap'
    continue
   aid=sim.add_agent(jps.CollisionFreeSpeedModelV2AgentParameters(position=point,desired_speed=v,radius=r,time_gap=T,journey_id=journey,stage_id=stage))
   native_ids[aid]=pid;inserted.add(pid);admissions[pid]=absolute;positions[pid]=point
  if len(positions)+len(removed)!=len(inserted):raise RuntimeError('Occupant conservation failure')
  if step%stride==0:
   ids=list(positions);xy=np.array([positions[i] for i in ids])
   if len(xy):
    if not np.isfinite(xy).all():raise RuntimeError('Nonfinite positions')
    pts=shapely.points(xy)
    if not np.all(shapely.covers(area,pts)):raise RuntimeError('Agent centre outside geometry')
    wall=float(max(0,np.max(r-shapely.distance(area.boundary,pts))))
    max_wall=max(max_wall,wall)
    if len(xy)>1:
     distance=np.linalg.norm(xy[:,None]-xy[None,:],axis=2);np.fill_diagonal(distance,np.inf)
     overlap=float(max(0,2*r-distance.min()));max_overlap=max(max_overlap,overlap)
     if overlap>.001:fail=f'Inter-agent overlap {overlap:.6f} m'
   if save_frames:frames.append({'t':absolute,'positions':{str(i):list(x) for i,x in positions.items()}})
  if fail:break
  if len(crossings)==len(arrivals) and len(removed)==len(arrivals):break
  previous=positions
  sim.iterate()
 if not fail and len(crossings)!=len(arrivals):fail='Not all measurement crossings completed within fixed horizon'
 return {'status':'failed' if fail else 'completed','failure':fail,'params':params,'dt':dt,'origin_s':start,'crossings':crossings,'admissions':admissions,'scheduled':len(arrivals),'inserted':len(inserted),'removed':len(removed),'max_sampled_overlap_m':max_overlap,'max_sampled_wall_penetration_m':max_wall,'mapping_max_m':max(x['mapping_displacement_m'] for x in mapped),'mapping_mean_m':float(np.mean([x['mapping_displacement_m'] for x in mapped])),'mapping_changed_count':sum(x['mapping_displacement_m']>1e-9 for x in mapped),'admission_delay_max_s':max([admissions[x['id']]-x['t'] for x in arrivals if x['id'] in admissions],default=0),'admission_delay_mean_s':float(np.mean([admissions[x['id']]-x['t'] for x in arrivals if x['id'] in admissions])) if admissions else None,'frames':frames}

def metrics(result,trial):
 ids=sorted(trial['targets']);pred={int(k):v for k,v in result['crossings'].items()};observed=trial['targets']
 if result['status']!='completed' or set(pred)!=set(ids):return None
 errors=np.array([pred[i]-observed[i] for i in ids]);p=np.array([pred[i] for i in ids]);y=np.array([observed[i] for i in ids])
 grid=np.arange(min(p.min(),y.min()),max(p.max(),y.max())+.1,.2)
 counts_p=np.array([sum(p<=t) for t in grid]);counts_y=np.array([sum(y<=t) for t in grid])
 orderp=np.argsort(np.argsort(p));ordery=np.argsort(np.argsort(y));rho=float(np.corrcoef(orderp,ordery)[0,1]) if len(ids)>1 else 1.
 return {'n':len(ids),'crossing_mae_s':float(np.mean(abs(errors))),'crossing_rmse_s':float(np.sqrt(np.mean(errors**2))),'crossing_bias_s':float(np.mean(errors)),'observed_passage_s':float(np.ptp(y)),'simulated_passage_s':float(np.ptp(p)),'passage_error_s':float(np.ptp(p)-np.ptp(y)),'last_crossing_error_s':float(max(p)-max(y)),'curve_mae_people':float(np.mean(abs(counts_p-counts_y))),'crossing_rank_correlation':rho}

def free_flight(trial,speed):
 return {'status':'completed','crossings':{x['id']:x['t']+(MEASURE-INLET)/speed for x in trial['arrivals']}}
