"""Stream real SiME through coherent held-trial models; truth only in scoring."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.deps/detector'),str(ROOT/'.deps/recovery-r1')]
import numpy as np
from shapely import wkt
from shapely.geometry import box,Point as SP
from src.polygon_zones import PolygonZone,validate_partition
from src.calibrated_detector import CalibratedMotionDetector
from src.crowd_framework import CrowdFramework
from src.mobility_probability import composition,count_distribution
from src.resource_planning import plan,request_probability,expected_shortfall
OUT=ROOT/'output/calibrated_framework_v1'

def main():
    if (OUT/'pipeline_summary.json').exists():raise RuntimeError('Preserve pipeline outcomes')
    paths=[Path(__file__),ROOT/'src/crowd_framework.py',ROOT/'src/calibrated_detector.py',ROOT/'research/calibrated_framework_protocol_v1.md']
    (OUT/'pipeline_lock.json').write_text(json.dumps(dict(hashes={str(p.relative_to(ROOT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},checkpoints=[10,20,30,40,50,60],request_rates=[.1,.4],budget=6,capacity=2),indent=2))
    audit=json.loads((ROOT/'output/detector_v1/data_audit.json').read_text());raw={};meta=None
    archives=defaultdict(list)
    for s in audit['sources']:archives[s['archive']].append(s)
    for archive,entries in archives.items():
        with zipfile.ZipFile(ROOT/'backups'/archive) as z:
            for s in entries:
                b=z.read(s['member']);assert hashlib.sha256(b).hexdigest()==s['sha256'];raw[int(Path(s['member']).stem)]=b
            if meta is None:meta=json.loads(z.read('research/data_search_20261030/sime_metadata_prefix.txt'))['experiment']
    runs={int(r['run_name']):r for r in meta['run']};checkpoints=[];demos=[];invalid=[];pred_checks=0
    held=json.loads((OUT/'coherent_trial_only_predictions_LOCAL_ONLY.json').read_text())
    data=np.load(ROOT/'output/detector_v1/data_LOCAL_ONLY.npz')
    reference={(int(data['trial'][r['index']]),str(data['track'][r['index']])):r for r in held}
    for trial,b in sorted(raw.items()):
        text=b.decode('utf-8-sig');mapping={str(int(a)):int(p) for a,p in re.findall(r'^#\s*(\d+)\|\s*(\d+)\s*$',text,re.M)}
        frames=defaultdict(list)
        for line in text.splitlines():
            if not line.strip() or line.lstrip().startswith('#'):continue
            a=line.split();frames[int(a[1])].append((str(int(a[0])),float(a[2]),float(a[3])))
        rb=box(-6,-1.65,2.4,1.65);area=wkt.loads(runs[trial]['wkt_geometry']).intersection(rb);cuts=[-6,-3,-1,0,2.4]
        zones=[PolygonZone(i,area.intersection(box(cuts[i],-1.65,cuts[i+1],1.65))) for i in range(4)];validate_partition(zones,area)
        detector=CalibratedMotionDetector(OUT/f'trial_{trial}_model_LOCAL_ONLY.joblib')
        engine=CrowdFramework(zones,detector,roi_contains=lambda p:rb.covers(SP(p.x,p.y)))
        replay=[]
        for frame,observations in sorted(frames.items()):
            time=frame/25;engine.ingest_frame(time,observations)
            if frame%25 or frame<0:continue
            try:state=engine.analyse()
            except ValueError as e:
                invalid.append(dict(trial=trial,time_s=time,error=str(e)));continue
            state['trial']=trial
            for person in state['occupants']:
                person['truth_wheelchair']=int(34<=mapping.get(person['person_id'],-1)<=40)
            replay.append(state)
            if time in [10,20,30,40,50,60]:
                row=dict(trial=trial,time_s=time,occupants=len(state['occupants']),detector_coverage=state['detector_coverage'],zones=[])
                policies={k:[] for k in ['prior','raw','calibrated','hard','known_class']}
                true_groups=[]
                for zone in state['zones']:
                    people=[p for p in state['occupants'] if p['zone']==zone['zone']];truth=sum(p['truth_wheelchair'] for p in people)
                    groups=dict(prior=[detector.training_prior]*len(people),raw=[p['raw_detector_score'] for p in people],
                        calibrated=[p['wheelchair_probability'] for p in people],hard=[float(p['wheelchair_probability']>=.5) for p in people],known_class=[p['truth_wheelchair'] for p in people])
                    z=dict(zone=zone['zone'],n=len(people),truth=truth,coverage=zone['detected_count']/len(people) if people else 0,
                        predictions={k:sum(ps) for k,ps in groups.items() if k!='known_class'},interval=zone['interval'])
                    row['zones'].append(z)
                    for k,ps in groups.items():policies[k].append([request_probability(p,.1,.4) for p in ps])
                    true_groups.append(count_distribution(policies['known_class'][-1]))
                row['policies']={}
                for k,groups in policies.items():
                    dec=plan(groups,6,2);actual=sum(expected_shortfall(pmf,2*a) for pmf,a in zip(true_groups,dec['allocation']))
                    row['policies'][k]=dict(allocation=dec['allocation'],predicted_expected_loss=dec['expected_loss'],oracle_expected_hypothetical_loss=actual)
                oracle=row['policies']['known_class']['oracle_expected_hypothetical_loss']
                assert all(v['oracle_expected_hypothetical_loss']>=oracle-1e-10 for v in row['policies'].values())
                checkpoints.append(row)
        for pid,e in engine.estimates.items():
            ref=reference[(trial,pid)];assert abs(e['probability']-ref['calibrated'])<1e-8
            assert abs(e['raw_score']-ref['raw'])<1e-8;pred_checks+=1
        config=dict(observable_wkt=area.wkt,zones=[dict(id=z.id,wkt=z.geometry.wkt) for z in zones],budget=6,capacity=2,r0=.1,r1=.4)
        (OUT/f'trial_{trial}_config.json').write_text(json.dumps(config,indent=2))
        demos.append(dict(trial=trial,width_m=float(runs[trial]['parameter']['bottleneck_width [m]']),
            prior=detector.training_prior,zone_areas=[z.area for z in zones],frames=replay,
            evidence='Recorded SiME positions; coherent held-trial calibrated model; repeated people; assumed requests'))
        print(json.dumps(dict(trial=trial,frames=len(replay),detections=len(engine.estimates))),flush=True)
    allz=[z for r in checkpoints for z in r['zones']];nonempty=[z for z in allz if z['n']]
    def counts(zs):
        return {k:dict(MAE=float(np.mean([abs(z['predictions'][k]-z['truth']) for z in zs])),bias=float(np.mean([z['predictions'][k]-z['truth'] for z in zs]))) for k in ['prior','raw','calibrated','hard']}
    summary=dict(scope='Coherent leave-one-trial-out replay; participants can repeat across training/test; not unseen-person whole-crowd validation',
        checkpoints=len(checkpoints),zone_records=len(allz),nonempty_zone_records=len(nonempty),geometry_withheld=len(invalid),
        streamed_predictions_matching_offline=pred_checks,count_errors_all=counts(allz),count_errors_nonempty=counts(nonempty),
        working_interval_coverage_nonempty=float(np.mean([z['interval'][0]<=z['truth']<=z['interval'][1] for z in nonempty])),
        mean_detector_coverage_nonempty_snapshots=float(np.mean([r['detector_coverage'] for r in checkpoints if r['occupants']])),
        hypothetical_planning={k:float(np.mean([r['policies'][k]['oracle_expected_hypothetical_loss'] for r in checkpoints])) for k in ['prior','raw','calibrated','hard','known_class']},
        caveat='Planning loss is conditional on assumed independent request rates .1/.4; human service outcomes were not observed.')
    (OUT/'checkpoints_LOCAL_ONLY.json').write_text(json.dumps(checkpoints))
    (OUT/'replay_LOCAL_ONLY.json').write_text(json.dumps(demos))
    (OUT/'geometry_withheld.json').write_text(json.dumps(invalid,indent=2))
    (OUT/'pipeline_summary.json').write_text(json.dumps(summary,indent=2))
    (ROOT/'app/framework_data_LOCAL_ONLY.js').write_text('window.CROWD_FRAMEWORK_DATA='+json.dumps(dict(trials=demos,summary=summary,calibration=json.loads((OUT/'calibration_summary.json').read_text())))+';')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
