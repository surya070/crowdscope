"""Native JuPedSim coordinated-escort development fixtures; no prediction fitting."""
from pathlib import Path
import sys,math,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
import jupedsim as jps
from shapely.geometry import Point,box,LineString
from shapely.ops import unary_union

def cases():
 straight=LineString([(0,0),(11.5,0)])
 doorway=unary_union([box(-2,-2,5,2),box(4.9,-.5,7.1,.5),box(7,-2,13,2)])
 turn=unary_union([box(-2,-1,7,1),box(5,-1,7,11)])
 return [dict(name='free_pair',area=box(-2,-2,13,2),route=straight,axis=0,plane=10.,extras=[]),dict(name='doorway',area=doorway,route=straight,axis=0,plane=10.,extras=[]),dict(name='right_angle_turn',area=turn,route=LineString([(0,0),(6,0),(6,9.5)]),axis=1,plane=8.,extras=[]),dict(name='mixed_queue',area=doorway,route=straight,axis=0,plane=10.,extras=[(2.,-.6),(2.,.6),(3.1,0.),(-1.5,-.8),(-1.5,.8)])]

def run(case,dt):
 area=case['area'];route=case['route']
 sim=jps.Simulation(model=jps.CollisionFreeSpeedModelV2(),geometry=area,dt=dt)
 stage=sim.add_direct_steering_stage();journey=sim.add_journey(jps.JourneyDescription([stage]))
 roster={};native={}
 starts=[((0.,0.),.30,.85,'client'),((-.85,0.),.22,1.3,'helper')]+[(xy,.22,1.1,'pedestrian') for xy in case['extras']]
 for pid,(xy,r,v,role) in enumerate(starts,1):
  aid=sim.add_agent(jps.CollisionFreeSpeedModelV2AgentParameters(position=xy,radius=r,desired_speed=v,time_gap=.3 if role=='helper' else .8,journey_id=journey,stage_id=stage))
  native[aid]=pid;roster[pid]=dict(radius=r,speed=v,ceiling=.85*1.15 if role=='client' else v,role=role)
 exited={};frames=[];maxover=maxwall=maxspeed=0.;minsep=math.inf;maxsep=0.;wait=False;failures=[];previous={}
 for step in range(round(60/dt)+1):
  t=step*dt;agents={native[a.id]:a for a in sim.agents()};positions={pid:tuple(a.position) for pid,a in agents.items()}
  if set(positions)&set(exited) or len(positions)+len(exited)!=len(roster):failures.append('occupant_accounting');break
  if not positions:break
  for pid,xy in positions.items():
   if not all(math.isfinite(x) for x in xy):failures.append('nonfinite_position')
   point=Point(xy);r=roster[pid]['radius']
   wall=r-point.distance(area.boundary) if area.covers(point) else r+point.distance(area)
   maxwall=max(maxwall,wall)
   if pid in previous:maxspeed=max(maxspeed,math.dist(xy,previous[pid])/dt-roster[pid]['ceiling'])
   for other in positions:
    if other>pid:maxover=max(maxover,r+roster[other]['radius']-math.dist(xy,positions[other]))
  if 1 in positions and 2 in positions:
   separation=math.dist(positions[1],positions[2]);minsep=min(minsep,separation);maxsep=max(maxsep,separation)
   if separation>1.2:wait=True
   if separation<1.:wait=False
   agents[1].model.desired_speed=0. if wait else min(.85*1.15,1.3)
   # The client ceiling covers the explicit hypothetical assistance gain.
   agents[2].target=positions[1]
   agents[2].model.desired_speed=0. if separation<.70 else 1.3
  elif 1 in agents:agents[1].model.desired_speed=.85
  for pid,a in agents.items():
   if pid!=2 or 1 not in agents:
    end=route.coords[-1];a.target=end
   if positions[pid][case['axis']]-roster[pid]['radius']>=case['plane']:
    exited[pid]=t;sim.mark_agent_for_removal(a.id)
  if step%max(1,round(.1/dt))==0:frames.append(dict(t=round(t,6),positions={str(k):v for k,v in positions.items()},exited=sorted(exited)))
  if maxover>.001 or maxwall>.005:failures.append('spatial_gate');break
  previous=positions
  if step==round(60/dt):break
  sim.iterate()
 if len(exited)!=len(roster):failures.append('incomplete')
 if minsep<.519 or maxsep>1.4:failures.append('pair_spacing')
 if maxspeed>.02:failures.append('speed_ceiling')
 # Client's assisted bound is .9775 m/s rather than its unassisted .85.
 # Per-agent speed check is reconstructed below from saved native positions.
 result=dict(case=case['name'],dt=dt,occupants=len(roster),exited=len(exited),exit_times=exited,clearance_s=max(exited.values()) if len(exited)==len(roster) else None,max_overlap_m=maxover,max_wall_penetration_m=maxwall,min_pair_distance_m=minsep,max_pair_distance_m=maxsep,max_speed_excess_mps=maxspeed,failures=sorted(set(failures)),frames=frames)
 return result

def main():
 out=ROOT/'output/assistance_prototype_v2';out.mkdir(parents=True,exist_ok=True)
 if (out/'results.json').exists():raise RuntimeError('Preserve prior development outputs.')
 results=[]
 for case in cases():
  for dt in [.02,.01,.005]:
   result=run(case,dt);results.append(result)
   print(json.dumps({k:v for k,v in result.items() if k not in ['frames','exit_times']}),flush=True)
 (out/'results.json').write_text(json.dumps(results))
 summaries=[]
 for case in cases():
  r=[v for v in results if v['case']==case['name']];times=[v['clearance_s'] for v in r if v['clearance_s'] is not None]
  spread=max(times)-min(times) if len(times)==3 else None
  stable=spread is not None and spread<=max(.2,.01*times[-1])
  summaries.append(dict(case=case['name'],movement_checks_pass=all(not v['failures'] for v in r),clearance_spread_s=spread,stability_pass=stable))
 (out/'gate.json').write_text(json.dumps(dict(engine=jps.__version__,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=summaries,passed=all(r['movement_checks_pass'] and r['stability_pass'] for r in summaries)),indent=2))
if __name__=='__main__':main()
