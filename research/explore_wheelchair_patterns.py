"""Post-hoc descriptive analysis, separate from the frozen planning experiment.

Only trials 501--508: seven documented wheelchair IDs and metadata count seven.
Other tracks are conditional roster-complement controls, not medically verified
individual diagnoses. No training/test classification or independent-sample tests.
"""
from pathlib import Path
from collections import defaultdict
import csv, hashlib, json, re, sys, zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.deps/recovery-r1'))
import numpy as np

STEP = int(sys.argv[1]) if len(sys.argv)>1 else 10
assert STEP in [5,10,20,30]
DT = STEP / 25
OUT = ROOT / ('output/wheelchair_patterns_exploratory' if STEP==10 else f'output/wheelchair_patterns_exploratory/sensitivity_{STEP}frames')
REGIONS = {'approach': (-3., -1.), 'bottleneck': (0., 2.4), 'departure': (2.4, 4.)}
WHEELCHAIR = set(range(34, 41))

def describe(values):
    a = np.asarray(values, dtype=float)
    return dict(n=len(a), median=float(np.median(a)), q25=float(np.quantile(a,.25)),
                q75=float(np.quantile(a,.75))) if len(a) else None

def run():
    OUT.mkdir(parents=True, exist_ok=True)
    old = json.loads((ROOT/'backups/backup_verification.json').read_text())
    recent = json.loads((ROOT/'backups/probabilistic_reset_verification_20261103_224341.json').read_text())
    sources = [('project_before_research_reset_20261102_113200.zip',
                {k:v['sha256'] for k,v in old['files'].items()}),
               (recent['archive'], {x['path']:x['sha256'] for x in recent['files']})]
    raw = {}; provenance = []; meta = None
    for archive, hashes in sources:
        with zipfile.ZipFile(ROOT/'backups'/archive) as z:
            for name in z.namelist():
                if not re.fullmatch(r'data/raw/sime2017/members/50[1-8]\.txt',name):
                    continue
                b=z.read(name); digest=hashlib.sha256(b).hexdigest()
                assert digest==hashes[name]
                trial=Path(name).stem
                if trial in raw: assert raw[trial]==b
                raw[trial]=b
                provenance.append(dict(archive=archive,member=name,sha256=digest))
            if meta is None:
                meta=json.loads(z.read('research/data_search_20261030/sime_metadata_prefix.txt'))['experiment']
    runs={str(r['run_name']):r for r in meta['run']}
    features=[]; roster=[]; speed_context=defaultdict(list)
    for trial, b in sorted(raw.items()):
        text=b.decode('utf-8-sig')
        mapping={int(a):int(v) for a,v in re.findall(r'^#\s*(\d+)\|\s*(\d+)\s*$',text,re.M)}
        tracks=defaultdict(list)
        for line in text.splitlines():
            if not line.strip() or line.lstrip().startswith('#'): continue
            a=line.split();tracks[int(a[0])].append([int(a[1]),float(a[2]),float(a[3])])
        positives=[tid for tid,pid in mapping.items() if pid in WHEELCHAIR]
        r=runs[trial]; assert len(positives)==int(r['parameter']['subjects_with_disability'])==7
        assert len(tracks)==r['number_participants']
        roster.append(dict(trial=trial,tracks=len(tracks),wheelchair=len(positives),
                           controls=len(tracks)-len(positives),width=float(r['parameter']['bottleneck_width [m]'])))
        pending=[]
        for tid, points in tracks.items():
            a=np.asarray(sorted(points)); assert np.all(np.diff(a[:,0])==1)
            group='wheelchair' if tid in positives else 'roster_complement'
            # Non-overlapping endpoint-displacement windows; smoothing sensitivity.
            ix=np.arange(0,len(a)-STEP,STEP); start=a[ix]; end=a[ix+STEP]
            velocity=(end[:,1:]-start[:,1:])/DT
            speed=np.linalg.norm(velocity,axis=1)
            for region,(lo,hi) in REGIONS.items():
                mask=(start[:,1]>=lo)&(start[:,1]<hi)&(end[:,1]>=lo)&(end[:,1]<hi)
                # At least 1.2 s of within-region movement per track.
                if mask.sum()<max(2,int(np.ceil(1.2/DT))): continue
                v=velocity[mask]; s=speed[mask]; times=(start[mask,0]+end[mask,0])/2
                f=dict(trial=trial,track_id=tid,persistent_id=mapping.get(tid),group=group,
                       region=region,windows=int(mask.sum()),median_speed=float(np.median(s)),
                       stop_fraction=float(np.mean(s<.1)),speed_iqr=float(np.quantile(s,.75)-np.quantile(s,.25)),
                       lateral_speed=float(np.median(np.abs(v[:,1]))))
                features.append(f)
                for t,sp in zip(times,s): pending.append((t,float(sp),f))
        # Context control: compare speed to all control windows in same region
        # and 2 s time bin, at least three controls represented. Descriptive only.
        pools=defaultdict(list)
        for t,sp,f in pending:
            if f['group']=='roster_complement': pools[(f['region'],int(t//50))].append((f['track_id'],sp))
        ratios=defaultdict(list)
        for t,sp,f in pending:
            pool=[(tid,v) for tid,v in pools[(f['region'],int(t//50))] if tid!=f['track_id']]
            if len(set(tid for tid,v in pool))>=3:
                med=float(np.median([v for tid,v in pool]))
                if med>.1: ratios[(f['track_id'],f['region'])].append(sp/med)
        for f in features:
            if f['trial']==trial:
                vals=ratios.get((f['track_id'],f['region']),[])
                f['context_speed_ratio']=float(np.median(vals)) if len(vals)>=3 else None
    summary={}; pertrial=[]
    metrics=['median_speed','stop_fraction','speed_iqr','lateral_speed','context_speed_ratio']
    for region in REGIONS:
        summary[region]={}
        for metric in metrics:
            groups={g:[f[metric] for f in features if f['region']==region and f['group']==g and f[metric] is not None]
                    for g in ['wheelchair','roster_complement']}
            x=np.array(groups['wheelchair']);y=np.array(groups['roster_complement'])
            lower=float(np.mean((x[:,None]<y[None,:])+.5*(x[:,None]==y[None,:]))) if len(x)*len(y) else None
            summary[region][metric]={**{g:describe(v) for g,v in groups.items()},
                'probability_wheelchair_value_lower':lower}
        for trial in sorted(raw):
            row=dict(trial=trial,region=region)
            for g in ['wheelchair','roster_complement']:
                vals=[f['median_speed'] for f in features if f['trial']==trial and f['region']==region and f['group']==g]
                row[g]=describe(vals)
            if row['wheelchair'] and row['roster_complement']:
                row['median_speed_difference']=row['wheelchair']['median']-row['roster_complement']['median']
            pertrial.append(row)
    participant=[]
    for pid in sorted(WHEELCHAIR):
        participant.append(dict(persistent_id=pid,**{region:describe([f['median_speed'] for f in features
            if f['persistent_id']==pid and f['region']==region]) for region in REGIONS}))
    result=dict(scope='Exploratory same-trial movement comparison, not classifier validation',
        labels='Seven mapped wheelchair users vs conditional roster complement; complete disability roster assumption supported by per-run counts and archived documentation section 3.3; no inference for other trial families.',
        method=f'{DT} s endpoint-displacement windows; endpoints in region; >=1.2 s and >=2 windows per track; equal track weighting; no Z/height or identity as movement features',
        caveats=['Seven wheelchair individuals repeated across eight trials, not 56 independent people.',
                 'Unknown repeat identities among controls; no iid p-values or random-row train/test splits.',
                 'Observed head-centre trajectories; congestion/assistance and tracking noise affect features.',
                 'Context uses 2 s same-region bins and is approximate, not density-matched causal inference.',
                 'Incomplete crossing of trial507 retained; regional availability reported.',
                 'Eight descriptive development trials, no held-out evaluation.'],
        roster=roster,summary=summary,per_trial=pertrial,participant_speed=participant,
        sources=provenance,code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'summary.json').write_text(json.dumps(result,indent=2))
    with (OUT/'track_features_LOCAL_ONLY.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(features[0]));w.writeheader();w.writerows(features)
    print(json.dumps(dict(roster=roster,summary=summary,per_trial=pertrial),indent=2))

if __name__=='__main__': run()
