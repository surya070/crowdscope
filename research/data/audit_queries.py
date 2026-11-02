"""Audit draft-v0 observation cohorts. No fitting or new trial acquisition."""
from pathlib import Path
import csv,hashlib,json,zipfile
from collections import defaultdict
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/data/queries';OUT.mkdir(exist_ok=True)
labels=list(csv.DictReader((ROOT/'research/data/label_audit.csv').open()))
wheelchair={(r['trial'],int(r['track_id'])) for r in labels if r['wheelchair_label']=='documented_wheelchair_id'}

def observe(tracks,frame):
    """Membership and summaries use only the two seconds ending at frame."""
    cohort={tid:track for tid,track in tracks.items() if all(k in track for k in range(frame-50,frame+1)) and track[frame][0]<2.4}
    out={}
    for steps in [10,25,50]:
        speeds=[float(np.linalg.norm(np.array(p[frame])-p[frame-steps]))/(steps/25) for p in cohort.values()]
        distances=[2.4-p[frame][0] for p in cohort.values()]
        out[str(steps/25)]={'eligible_count':len(cohort),'mean_observed_speed':float(np.mean(speeds)) if speeds else None,'max_distance_to_plane':max(distances) if distances else None}
    return sorted(cohort),out

rows=[];records=[];checks=0
with zipfile.ZipFile(next((ROOT/'backups').glob('*.zip'))) as z:
    verify=json.loads((ROOT/'backups/backup_verification.json').read_text())
    for trial in ['501','507','1301','1307','1501','1503','1505','1507']:
        path=f'data/raw/sime2017/members/{trial}.txt';raw=z.read(path)
        assert hashlib.sha256(raw).hexdigest()==verify['files'][path]['sha256']
        tracks=defaultdict(dict)
        for line in raw.decode().splitlines():
            if not line.strip() or line.startswith('#'):continue
            a=line.split();tid,f=int(a[0]),int(a[1]);assert f not in tracks[tid]
            tracks[tid][f]=(float(a[2]),float(a[3]))
        crossings={}
        for tid,track in tracks.items():
            for f in sorted(track):
                if f+1 in track and track[f][0]<2.4<=track[f+1][0]:
                    crossings[tid]=(f+(2.4-track[f][0])/(track[f+1][0]-track[f][0]))/25;break
        for t in [10,20,30]:
            frame=t*25;cohort,obs=observe(tracks,frame)
            prefix={tid:{f:p for f,p in tr.items() if f<=frame} for tid,tr in tracks.items()}
            assert (cohort,obs)==observe(prefix,frame);checks+=1
            visible=[tid for tid,tr in tracks.items() if frame in tr and tr[frame][0]<2.4]
            missing=[tid for tid in cohort if tid not in crossings]
            target=max(crossings[tid] for tid in cohort)-t if cohort and not missing else None
            # Recover old crossing audit independently to verify target inputs.
            old=list(csv.DictReader((ROOT/'research/data/track_coverage.csv').open()))
            for tid in cohort:
                old_t=next(r['downstream_crossing_s'] for r in old if r['trial']==trial and int(r['track_id'])==tid)
                assert (old_t=='')==(tid not in crossings)
                if old_t:assert abs(float(old_t)-crossings[tid])<1e-10
            flags=[]
            if not cohort:flags.append('empty')
            if missing:flags.append('incomplete_cohort_outcome')
            if trial=='1307':flags.append('metadata_count_mismatch')
            rows.append(dict(trial=trial,time_s=t,visible_upstream=len(visible),eligible_cohort=len(cohort),short_history_excluded=len(visible)-len(cohort),documented_wheelchair_members=sum((trial,tid) in wheelchair for tid in cohort),missing_outcomes=len(missing),remaining_observed_cohort_passage_s=target,complete_target=target is not None,coverage_eligible=not flags,flags=';'.join(flags),development_only=True))
            records.append(dict(trial=trial,time_s=t,cohort=cohort,missing_crossing_tracks=missing,past_only_summaries=obs))
with (OUT/'query_eligibility.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'cohort_records.json').write_text(json.dumps(records,indent=2))
summary=dict(queries=len(rows),complete_outcomes=sum(r['complete_target'] for r in rows),coverage_eligible=sum(r['coverage_eligible'] for r in rows),prefix_invariance_checks_passed=checks,all_crossings_match_independent_stage2_audit=True,coverage_eligible_with_documented_wheelchair_members=sum(r['coverage_eligible'] and r['documented_wheelchair_members']>0 for r in rows),fresh_test_trials=0,learner_fitted=False)
(OUT/'audit.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2));print('\n'.join(str(r) for r in rows if r['trial'] in ['501','507']))
