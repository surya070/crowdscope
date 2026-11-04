"""Development-only JuPedSim movement verification; no benchmark seed access."""
from pathlib import Path
import hashlib
import importlib.metadata
import itertools
import json
import math
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'.deps/recovery-r1'),str(ROOT)]
import jupedsim as jps
from shapely.geometry import Point, box
from shapely.ops import unary_union


def fixtures():
    door=unary_union([box(-5,-2,4,2),box(3.9,-0.5,6.1,0.5),box(6,-2,10,2)])
    turn=unary_union([box(-5,-1,5,1),box(3,-1,5,9)])
    return [
        dict(name='single',area=box(-5,-2,10,2),starts=[(-2,0)],speeds=[1.0],goal=(9,0),axis=0,plane=8),
        dict(name='following_pair',area=box(-5,-2,10,2),starts=[(0,0),(-1,0)],speeds=[0.8,1.2],goal=(9,0),axis=0,plane=8),
        dict(name='doorway',area=door,starts=[(-1,-0.4),(-1,0.4),(-2,0)],speeds=[0.8,1.1,1.2],goal=(9,0),axis=0,plane=8),
        dict(name='mixed_queue',area=door,starts=[(0,0),(-1,0),(-2,0),(-3,0)],speeds=[0.7,1.3,0.9,1.1],goal=(9,0),axis=0,plane=8),
        dict(name='turn',area=turn,starts=[(0,0),(-1,0),(-2,0)],speeds=[0.8,1.1,1.2],goal=(4,8),axis=1,plane=7),
        dict(name='blocked_target',area=box(-2,-1,2,1),starts=[(0,0)],speeds=[1.0],goal=(5,0),axis=0,plane=4,blocked=True),
    ]


def run(case,dt):
    radius=0.22
    sim=jps.Simulation(model=jps.CollisionFreeSpeedModelV2(),geometry=case['area'],dt=dt)
    stage=sim.add_direct_steering_stage()
    journey=sim.add_journey(jps.JourneyDescription([stage]))
    roster={}
    for i,(xy,v) in enumerate(zip(case['starts'],case['speeds'])):
        aid=sim.add_agent(jps.CollisionFreeSpeedModelV2AgentParameters(position=xy,radius=radius,
            desired_speed=v,time_gap=0.8,strength_neighbor_repulsion=2.6,
            journey_id=journey,stage_id=stage))
        roster[aid]=dict(person_id=str(i+1),speed=v)
    exited={};previous={};max_overlap=max_wall=max_excess=0.0;frames=[];failures=[];rejected=None
    limit=15 if case.get('blocked') else 60
    for step in range(round(limit/dt)+1):
        now=step*dt
        agents={a.id:a for a in sim.agents()}
        positions={aid:tuple(a.position) for aid,a in agents.items()}
        if set(positions)&set(exited) or len(positions)+len(exited)!=len(roster):
            failures.append('occupant_conservation');break
        for aid,xy in positions.items():
            if not all(math.isfinite(v) for v in xy):
                failures.append('nonfinite');break
            point=Point(xy)
            intrusion=radius-point.distance(case['area'].boundary) if case['area'].covers(point) else radius+point.distance(case['area'])
            max_wall=max(max_wall,intrusion)
            if aid in previous:
                max_excess=max(max_excess,math.dist(xy,previous[aid])/dt-roster[aid]['speed'])
        for a,b in itertools.combinations(positions,2):
            max_overlap=max(max_overlap,2*radius-math.dist(positions[a],positions[b]))
        if max_wall>0.005:failures.append('wall_penetration')
        if max_overlap>0.001:failures.append('agent_overlap')
        if max_excess>0.02:failures.append('speed_ceiling')
        if step%round(0.1/dt)==0:
            frames.append(dict(time=round(now,8),positions={roster[a]['person_id']:xy for a,xy in positions.items()},exited=len(exited)))
        for aid,a in agents.items():
            a.target=case['goal']
            if positions[aid][case['axis']]-radius>=case['plane']:
                exited[aid]=now
                sim.mark_agent_for_removal(aid)
        if failures:break
        if len(exited)==len(roster):break
        previous=positions
        if step<round(limit/dt):
            try:
                sim.iterate()
            except RuntimeError as exc:
                if case.get('blocked') and 'outside of accessible area' in str(exc):
                    rejected=str(exc)
                    break
                raise
    complete=len(exited)==len(roster)
    if not complete and not case.get('blocked'):failures.append('noncompletion')
    return dict(case=case['name'],dt=dt,occupants=len(roster),exited=len(exited),
                clearance_s=max(exited.values()) if complete else None,
                expected_noncompletion=bool(case.get('blocked')),expected_invalid_target_rejection=rejected,max_wall_penetration_m=max_wall,
                max_overlap_m=max_overlap,max_speed_excess_m_s=max_excess,
                failures=sorted(set(failures)),frames=frames)


def main():
    assert jps.__version__=='1.4.2'
    out=ROOT/'output/simulation_checks_v2';out.mkdir(parents=True,exist_ok=True)
    if (out/'results.json').exists():raise RuntimeError('Preserve existing results; use a new version for reruns.')
    cases=fixtures()
    lock=dict(purpose='development numerical checks only',benchmark_seeds_used=False,
              engine=jps.__version__,dt_values=[0.01,0.005],radius_m=0.22,time_gap_s=0.8,
              strength_neighbor_repulsion=2.6,other_parameters='JuPedSim 1.4.2 defaults',
              tolerances=dict(overlap_m=0.001,wall_m=0.005,speed_excess_m_s=0.02,clearance='max(0.2s,1% fine result)'),
              cases=[dict(**{k:v for k,v in c.items() if k!='area'},geometry_wkt=c['area'].wkt) for c in cases],
              code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'lock.json').write_text(json.dumps(lock,indent=2),encoding='utf-8')
    results=[];gates=[]
    for c in cases:
        runs=[run(c,dt) for dt in (0.01,0.005)]
        results.extend(runs)
        fine=runs[1];coarse=runs[0]
        if c.get('blocked'):
            stable=all(x['clearance_s'] is None and x['exited']==0 and x['expected_invalid_target_rejection'] for x in runs)
            spread=None
        else:
            spread=abs(coarse['clearance_s']-fine['clearance_s']) if all(x['clearance_s'] is not None for x in runs) else None
            stable=spread is not None and spread<=max(0.2,0.01*fine['clearance_s'])
        gate=dict(case=c['name'],movement_pass=all(not x['failures'] for x in runs),timestep_stable=stable,clearance_difference_s=spread)
        gates.append(gate);print(json.dumps(gate),flush=True)
        (out/'progress.json').write_text(json.dumps(dict(results=results,gates=gates)),encoding='utf-8')
    repeated=run(cases[2],0.005)
    repeat_match=repeated==next(x for x in results if x['case']=='doorway' and x['dt']==0.005)
    summary=dict(gates=gates,repeatability_pass=repeat_match,
                 all_pass=repeat_match and all(g['movement_pass'] and g['timestep_stable'] for g in gates),
                 empirical_validation=False)
    (out/'results.json').write_text(json.dumps(results),encoding='utf-8')
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    # Canonical adapter example: source native IDs mapped to stable run-local IDs.
    sample=next(x for x in results if x['case']=='doorway' and x['dt']==0.005)
    import csv
    with (out/'doorway_trajectories.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['person_id','time','x','y'])
        for frame in sample['frames']:
            for pid,xy in frame['positions'].items():w.writerow([pid,frame['time'],*xy])
    print(json.dumps(summary),flush=True)


if __name__=='__main__':main()
