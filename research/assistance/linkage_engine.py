"""Separate multi-pair verification branch; fixed fixtures and candidates."""
from pathlib import Path
import sys,json,math,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
import jupedsim as jps
from shapely.geometry import box,Point
from shapely.ops import unary_union

def fixtures():
 def door(w):return unary_union([box(-6,-2,5,2),box(4.9,-w/2,7.1,w/2),box(7,-2,13,2)])
 pair=[((0,0),(-.85,0),.85,1.3),((-2,0),(-2.85,0),.85,1.3)]
 stagger=[((0,-.55),(-.85,-.55),.85,1.3),((-1, .55),(-1.85,.55),.85,1.3)]
 return [dict(name='single_mixed_regression',area=door(1),pairs=pair[:1],extras=[(2,-.6),(2,.6),(3.1,0),(-1.5,-.8),(-1.5,.8)],goal=(11.5,0),axis=0,plane=10),dict(name='two_serial_door_1m',area=door(1),pairs=pair,extras=[],goal=(11.5,0),axis=0,plane=10),dict(name='two_serial_door_1_2m',area=door(1.2),pairs=pair,extras=[],goal=(11.5,0),axis=0,plane=10),dict(name='staggered_merge',area=door(1),pairs=stagger,extras=[(2.5,0),(3.5,.5)],goal=(11.5,0),axis=0,plane=10),dict(name='two_pair_turn',area=unary_union([box(-6,-1,7,1),box(5,-1,7,11)]),pairs=pair,extras=[],goal=(6,9.5),axis=1,plane=8),dict(name='unequal_paces',area=door(1),pairs=[((0,0),(-.85,0),.7,1.1),((-2,0),(-2.85,0),.95,1.2)],extras=[(2.5,.5)],goal=(11.5,0),axis=0,plane=10)]

def run(case,dt,mode,engine='cfs',parameters=None,gain=1.15):
 parameters=parameters or {}
 model=jps.AnticipationVelocityModel(rng_seed=113) if engine=='avm' else jps.CollisionFreeSpeedModelV2()
 sim=jps.Simulation(model=model,geometry=case['area'],dt=dt)
 stage=sim.add_direct_steering_stage();journey=sim.add_journey(jps.JourneyDescription([stage]));native={};roster={};pairs=[];waiting={}
 def add(xy,r,v,role):
  params=jps.AnticipationVelocityModelAgentParameters if engine=='avm' else jps.CollisionFreeSpeedModelV2AgentParameters
  pid=len(roster)+1;aid=sim.add_agent(params(position=xy,radius=r,desired_speed=v,time_gap=.3 if role=='helper' else .8,journey_id=journey,stage_id=stage,**parameters));native[aid]=pid;roster[pid]=dict(radius=r,pace=v,ceiling=v,role=role);return pid
 for xy,hxy,v,hv in case['pairs']:
  c=add(xy,.3,v,'client');h=add(hxy,.22,hv,'helper');pace=min(v*gain,hv);roster[c]['ceiling']=pace;pairs.append((c,h,pace));waiting[c]=False
 for xy in case['extras']:add(xy,.22,1.1,'pedestrian')
 exited={};previous={};frames=[];wall=over=excess=0.;distances={str(c):[math.inf,0.] for c,h,v in pairs};fail=[]
 for step in range(round(60/dt)+1):
  now=step*dt;agents={native[a.id]:a for a in sim.agents()};pos={p:tuple(a.position) for p,a in agents.items()}
  if set(pos)&set(exited) or len(pos)+len(exited)!=len(roster):fail.append('counts');break
  if not pos:break
  for p,xy in pos.items():
   if not all(math.isfinite(v) for v in xy):fail.append('nonfinite')
   pt=Point(xy);r=roster[p]['radius'];wall=max(wall,r-pt.distance(case['area'].boundary) if case['area'].covers(pt) else r+pt.distance(case['area']))
   if p in previous:excess=max(excess,math.dist(xy,previous[p])/dt-roster[p]['ceiling'])
   for q,qxy in pos.items():
    if q>p:over=max(over,r+roster[q]['radius']-math.dist(xy,qxy))
  for p,a in agents.items():a.target=case['goal'];a.model.desired_speed=roster[p]['pace']
  for c,h,pace in pairs:
   if mode=='independent':continue
   if c in pos and h in pos:
    gap=math.dist(pos[c],pos[h]);d=distances[str(c)];d[0]=min(d[0],gap);d[1]=max(d[1],gap)
    agents[h].target=pos[c]
    if mode=='threshold':
     if gap>1.2:waiting[c]=True
     if gap<1.:waiting[c]=False
     agents[c].model.desired_speed=0 if waiting[c] else pace
     agents[h].model.desired_speed=0 if gap<.7 else roster[h]['pace']
    else:
     agents[c].model.desired_speed=pace*max(0,min(1,(1.2-gap)/.3))
     agents[h].model.desired_speed=roster[h]['pace']*max(0,min(1,(gap-.62)/.23))
  for p,a in agents.items():
   if pos[p][case['axis']]-roster[p]['radius']>=case['plane']:exited[p]=now;sim.mark_agent_for_removal(a.id)
  if step%max(1,round(.2/dt))==0:frames.append(dict(t=now,positions=pos,exited=sorted(exited)))
  if wall>.005 or over>.001:fail.append('spatial');break
  previous=pos
  if step==round(60/dt):break
  sim.iterate()
 if len(exited)!=len(roster):fail.append('incomplete')
 if mode!='independent' and any(lo<.519 or hi>1.4 for lo,hi in distances.values()):fail.append('pair_spacing')
 if excess>.02:fail.append('speed_ceiling')
 return dict(case=case['name'],mode=mode,dt=dt,occupants=len(roster),exited=len(exited),clearance_s=max(exited.values()) if len(exited)==len(roster) else None,max_wall=wall,max_overlap=over,max_speed_excess=excess,pair_distances=distances,failures=sorted(set(fail)),frames=frames)

def main():
 out=ROOT/'output/assistance_multipair_v1';out.mkdir(parents=True,exist_ok=True)
 if (out/'results.json').exists():raise RuntimeError('Preserve earlier results.')
 (out/'lock.json').write_text(json.dumps(dict(engine=jps.__version__,modes=['threshold','continuous'],cases=[c['name'] for c in fixtures()],steps=[.02,.01,.005],code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2))
 results=[]
 for mode in ['threshold','continuous']:
  for case in fixtures():
   for dt in [.02,.01,.005]:
    r=run(case,dt,mode);results.append(r);print(json.dumps({k:v for k,v in r.items() if k not in ['frames','pair_distances']}),flush=True)
 (out/'results.json').write_text(json.dumps(results));gates=[]
 for mode in ['threshold','continuous']:
  for case in fixtures():
   runs=[r for r in results if r['mode']==mode and r['case']==case['name']];times=[r['clearance_s'] for r in runs if r['clearance_s'] is not None];spread=max(times)-min(times) if len(times)==3 else None
   gates.append(dict(mode=mode,case=case['name'],movement=all(not r['failures'] for r in runs),spread_s=spread,stable=spread is not None and spread<=max(.2,.01*times[-1])))
 (out/'gate.json').write_text(json.dumps(gates,indent=2))
if __name__=='__main__':main()
