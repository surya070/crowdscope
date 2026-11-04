"""80-person development integration; no validation/evaluation partition access."""
from pathlib import Path
import hashlib,json,sys,csv,random,math
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'.deps/recovery-r1'),str(ROOT)]
import numpy as np
import shapely
from shapely.geometry import box
from shapely.ops import unary_union
import jupedsim as jps
from src.crowd_state import Point,snapshot
from src.polygon_zones import PolygonZone,validate_partition
from src.mobility_probability import zone_composition


def cases():
    result=[]
    for name,height in [('room',4),('corridor',3)]:
        area=unary_union([box(-12,-height,4,height),box(3.9,-0.5,6.1,0.5),box(6,-height,12,height)])
        result.append(dict(name=name,area=area,goal=(11,0),axis=0,plane=10))
    result.append(dict(name='turn',area=unary_union([box(-12,-3,6,3),box(2,-3,6,14)]),goal=(4,13),axis=1,plane=12))
    for c in result:
        xmin,ymin,xmax,ymax=c['area'].bounds
        cuts=[xmin,-6,0,2,xmax] if c['name']=='turn' else [xmin,-6,0,6,xmax]
        c['zones']=[PolygonZone(i,c['area'].intersection(box(cuts[i],ymin,cuts[i+1],ymax))) for i in range(4)]
        validate_partition(c['zones'],c['area'])
    return result


def roster(seed=410000):
    membership=random.Random(seed+10000);pace=random.Random(seed+20000)
    starts=[(-10+i*0.65,-2.275+j*0.65) for i in range(10) for j in range(8)]
    rows=[]
    for i,xy in enumerate(starts):
        c=int(membership.random()<0.2)
        rows.append(dict(person_id=str(i+1),xy=xy,latent_class=c,speed=pace.uniform(0.6,1.3) if c else pace.uniform(0.8,1.5)))
    return rows


def run(case,people,dt,out):
    sim=jps.Simulation(model=jps.CollisionFreeSpeedModelV2(),geometry=case['area'],dt=dt)
    stage=sim.add_direct_steering_stage();journey=sim.add_journey(jps.JourneyDescription([stage]));ids={}
    for row in people:
        aid=sim.add_agent(jps.CollisionFreeSpeedModelV2AgentParameters(position=row['xy'],radius=0.22,
            desired_speed=row['speed'],time_gap=0.8,strength_neighbor_repulsion=2.6,
            journey_id=journey,stage_id=stage))
        ids[aid]=row
    previous={};exited={};tracks=[];fail=[];max_wall=max_overlap=max_excess=0.0
    for step in range(round(120/dt)+1):
        now=round(step*dt,8);agents=list(sim.agents());native=[a.id for a in agents]
        xy=np.array([a.position for a in agents],dtype=float).reshape((-1,2))
        if set(native)&set(exited) or len(native)+len(exited)!=80:fail.append('counts');break
        if not len(native):break
        if not np.isfinite(xy).all():fail.append('nonfinite');break
        pts=shapely.points(xy)
        distances=shapely.distance(pts,case['area'].boundary)
        walls=np.where(shapely.covers(case['area'],pts),0.22-distances,0.22+shapely.distance(pts,case['area']))
        max_wall=max(max_wall,float(walls.max()))
        delta=xy[:,None,:]-xy[None,:,:];dist=np.sqrt((delta*delta).sum(axis=2));np.fill_diagonal(dist,np.inf)
        max_overlap=max(max_overlap,float((0.44-dist).max()))
        for aid,pos in zip(native,xy):
            if aid in previous:max_excess=max(max_excess,math.dist(pos,previous[aid])/dt-ids[aid]['speed'])
        if max_wall>0.005:fail.append('wall_penetration')
        if max_overlap>0.001:fail.append('overlap')
        if max_excess>0.02:fail.append('speed_excess')
        if step%round(0.1/dt)==0:
            tracks.extend(Point(ids[aid]['person_id'],now,float(pos[0]),float(pos[1])) for aid,pos in zip(native,xy))
        for a,pos in zip(agents,xy):
            a.target=case['goal']
            if pos[case['axis']]-0.22>=case['plane']:exited[a.id]=now;sim.mark_agent_for_removal(a.id)
        if fail or len(exited)==80:break
        previous={aid:tuple(pos) for aid,pos in zip(native,xy)}
        if step<round(120/dt):sim.iterate()
    if len(exited)!=80:fail.append('noncompletion')
    state=snapshot(tracks,case['zones'],10,history=2,max_gap=0.100001)
    noise=random.Random(440000)
    obs={p['person_id']:p['latent_class']^int(noise.random()<0.2) for p in people}
    composition=zone_composition(state,obs,0.2,0.2)
    stem=case['name']+'_'+str(dt).replace('.','_')
    with (out/(stem+'.csv')).open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['person_id','time','x','y']);w.writerows((p.person,p.time,p.x,p.y) for p in tracks)
    (out/(stem+'_state.json')).write_text(json.dumps(dict(state=state,composition=composition),indent=2))
    return dict(case=case['name'],dt=dt,exited=len(exited),clearance_s=max(exited.values()) if len(exited)==80 else None,
                max_overlap_m=max_overlap,max_wall_m=max_wall,max_speed_excess=max_excess,failures=sorted(set(fail)),
                checkpoint_occupants=len(state['occupants']),zone_counts=[z['count'] for z in state['zones']])


def main():
    out=ROOT/'output/crowd_development_v1';out.mkdir(parents=True,exist_ok=True)
    if (out/'lock.json').exists():raise RuntimeError('Preserve existing run; version changes explicitly')
    people=roster();layouts=cases()
    lock=dict(stage='development',seed=410000,evaluation_access=False,engine=jps.__version__,
        time_horizon_s=120,dt=[0.01,0.005],roster=people,metadata_seed=440000,
        parameters=dict(radius=0.22,time_gap=0.8,strength_neighbor_repulsion=2.6,range_neighbor_repulsion=0.1,
                        strength_geometry_repulsion=5.0,range_geometry_repulsion=0.02),
        layouts=[dict(name=c['name'],geometry=c['area'].wkt,zones=[z.geometry.wkt for z in c['zones']],goal=c['goal'],axis=c['axis'],plane=c['plane']) for c in layouts],
        hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['research/run_crowd_development.py','src/crowd_state.py','src/polygon_zones.py','src/mobility_probability.py']})
    (out/'lock.json').write_text(json.dumps(lock,indent=2))
    results=[]
    for case in layouts:
        for dt in (0.01,0.005):
            result=run(case,people,dt,out);results.append(result)
            (out/'results.json').write_text(json.dumps(results,indent=2));print(json.dumps(result),flush=True)
    gates=[]
    for c in layouts:
        a,b=[x for x in results if x['case']==c['name']]
        spread=abs(a['clearance_s']-b['clearance_s']) if a['clearance_s'] is not None and b['clearance_s'] is not None else None
        gates.append(dict(case=c['name'],pass_checks=not a['failures'] and not b['failures'],
                          spread_s=spread,stable=spread is not None and spread<=max(0.2,0.01*b['clearance_s'])))
    (out/'gates.json').write_text(json.dumps(gates,indent=2));print(json.dumps(gates),flush=True)


if __name__=='__main__':main()
