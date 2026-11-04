"""Observed SiME occupancy with explicitly hypothetical planning inputs."""
from pathlib import Path
import csv,hashlib,json,random,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'.deps/recovery-r1'),str(ROOT)]
from shapely import wkt
from shapely.geometry import box,Point as ShapePoint
from src.polygon_zones import PolygonZone,validate_partition
from src.crowd_state import Point,snapshot
from src.mobility_probability import posterior,zone_composition
from src.resource_planning import plan,request_probability


def main():
    out=ROOT/'output/recorded_occupancy_integration_v1';out.mkdir(parents=True,exist_ok=True)
    if (out/'lock.json').exists():raise RuntimeError('Preserve previous integration outputs')
    lock=dict(purpose='observed occupancy plus hypothetical service-profile metadata; no empirical recognition or demand claim',
        checkpoints_s=[10,20,30],history_s=2,roi_bounds=[-6,-1.65,2.4,1.65],zone_x_cuts=[-6,-3,-1,0,2.4],
        metadata='Bernoulli service-profile prior0.2 with symmetric bit error0.2; per-trial local IDs fixed across times',
        seed_rule='910000+integer trial ID; not reserved evaluation seeds',demand_rates=[0.1,0.4],budget=6,capacity=2,
        geometry_mismatch_policy='report and withhold state; do not clip observations into walkable geometry',
        hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['research/integrate_recorded_occupancy.py','src/crowd_state.py','src/polygon_zones.py','src/mobility_probability.py','src/resource_planning.py']})
    (out/'lock.json').write_text(json.dumps(lock,indent=2))
    old=json.loads((ROOT/'backups/backup_verification.json').read_text())
    recent=json.loads((ROOT/'backups/probabilistic_reset_verification_20261103_224341.json').read_text())
    sources=[('project_before_research_reset_20261102_113200.zip',{k:v['sha256'] for k,v in old['files'].items()}),
             (recent['archive'],{x['path']:x['sha256'] for x in recent['files']})]
    data={};meta=None;inputs=[]
    for archive,hashes in sources:
        with zipfile.ZipFile(ROOT/'backups'/archive) as z:
            names=[n for n in z.namelist() if n.startswith('data/raw/sime2017/members/') and n.endswith('.txt')]
            if archive==sources[0][0]:names.append('research/data_search_20261030/sime_metadata_prefix.txt')
            for name in names:
                b=z.read(name);digest=hashlib.sha256(b).hexdigest();assert digest==hashes[name]
                inputs.append(dict(archive=archive,member=name,sha256=digest))
                if name.endswith('sime_metadata_prefix.txt'):meta=json.loads(b)['experiment']
                else:data[Path(name).stem]=b
    runs={str(r['run_name']):r for r in meta['run']};summaries=[]
    roi_box=box(*lock['roi_bounds'])
    for trial,b in sorted(data.items(),key=lambda x:int(x[0])):
        area=wkt.loads(runs[trial]['wkt_geometry']);observable=area.intersection(roi_box)
        cuts=lock['zone_x_cuts']
        zones=[PolygonZone(i,observable.intersection(box(cuts[i],-1.65,cuts[i+1],1.65))) for i in range(4)]
        validate_partition(zones,observable)
        points=[];all_ids=set()
        for line in b.decode('utf-8-sig').splitlines():
            if not line.strip() or line.lstrip().startswith('#'):continue
            a=line.split();pid=a[0];all_ids.add(pid);frame=int(a[1]);t=frame/25
            if any(time-2<=t<=time for time in lock['checkpoints_s']):points.append(Point(pid,t,float(a[2]),float(a[3])))
        rng=random.Random(910000+int(trial));hypothetical={}
        for pid in sorted(all_ids,key=int):
            profile=int(rng.random()<0.2);hypothetical[pid]=profile^int(rng.random()<0.2)
        for time in lock['checkpoints_s']:
            present=[p for p in points if p.time==time]
            inside=[p for p in present if roi_box.covers(ShapePoint(p.x,p.y))]
            invalid=[p for p in inside if not observable.covers(ShapePoint(p.x,p.y))]
            summary=dict(trial=trial,time_s=time,visible_all=len(present),inside_roi_box=len(inside),
                         outside_roi_box=len(present)-len(inside),geometry_mismatch=len(invalid),
                         metadata_count_matches=len(all_ids)==runs[trial]['number_participants'])
            if invalid:
                summary.update(status='geometry_mismatch_state_withheld',zone_counts=None)
            else:
                cohort={p.person for p in inside}
                state=snapshot([p for p in points if p.person in cohort],zones,time,history=2,max_gap=0.040001)
                assert len(state['occupants'])==len(inside)
                comp=zone_composition(state,hypothetical,0.2,0.2)
                q=[[request_probability(posterior(hypothetical[p['person_id']],0.2,0.2))
                    for p in state['occupants'] if p['zone']==z.id] for z in zones]
                decision=plan(q,6,2)
                payload=dict(evidence='observed positions; hypothetical service-profile metadata and demand',
                    state=state,composition=comp,planning=decision,zone_wkts=[z.geometry.wkt for z in zones])
                (out/f'{trial}_{time}.json').write_text(json.dumps(payload,indent=2))
                summary.update(status='integrated',zone_counts=[z['count'] for z in state['zones']],
                               allocation=decision['allocation'],expected_hypothetical_unmet=decision['expected_loss'])
            summaries.append(summary)
    (out/'inputs.json').write_text(json.dumps(inputs,indent=2))
    (out/'summary.json').write_text(json.dumps(summaries,indent=2))
    print(json.dumps(dict(checkpoints=len(summaries),integrated=sum(s['status']=='integrated' for s in summaries),
        geometry_mismatches=sum(s['geometry_mismatch'] for s in summaries),metadata_count_mismatch_trials=sorted({s['trial'] for s in summaries if not s['metadata_count_matches']}))))


if __name__=='__main__':main()
