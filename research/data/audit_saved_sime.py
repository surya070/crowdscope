"""Read the verified pre-reset archive; audit only, without fitting or tuning."""
from pathlib import Path
import csv, hashlib, json, re, zipfile
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/data'
backup = next((ROOT / 'backups').glob('project_before_research_reset_*.zip'))
verification = json.loads((ROOT/'backups/backup_verification.json').read_text())

def save_csv(name, rows):
    with (OUT/name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

with zipfile.ZipFile(backup) as z:
    def read(name):
        data = z.read(name)
        assert hashlib.sha256(data).hexdigest() == verification['files'][name]['sha256']
        return data
    metadata_path='research/data_search_20261030/sime_metadata_prefix.txt'
    meta=json.loads(read(metadata_path))['experiment']
    runs={str(r['run_name']):r for r in meta['run']}
    registry=set(range(34,41))  # archived documentation wheelchair identifiers
    labels=[]; inventory=[]; tracks_out=[]; exposure=[]
    names=sorted(n for n in z.namelist() if re.fullmatch(r'data/raw/sime2017/members/\d+\.txt',n))
    for name in names:
        trial=Path(name).stem
        text=read(name).decode('utf-8-sig').replace('\r','')
        links={int(a):int(b) for a,b in re.findall(r'^#\s*(\d+)\|\s*(\d+)\s*$',text,re.M)}
        tracks=defaultdict(list)
        for line in text.splitlines():
            if not line.strip() or line.lstrip().startswith('#'): continue
            a=line.split(); tracks[int(a[0])].append((int(a[1]),float(a[2]),float(a[3])))
        crossings=[]; all_intervals=[]; duplicates=0; gaps=0
        for tid,track in sorted(tracks.items()):
            track.sort(); duplicate=len(track)-len({p[0] for p in track}); duplicates+=duplicate
            missing=sum(max(0,b[0]-a[0]-1) for a,b in zip(track,track[1:]));gaps+=missing
            crossing=None
            for a,b in zip(track,track[1:]):
                if a[1]<2.4<=b[1] and b[0]-a[0]==1:
                    crossing=(a[0]+(2.4-a[1])/(b[1]-a[1]))/25;break
            if crossing is not None: crossings.append(crossing)
            all_intervals.append((track[0][0],track[-1][0]))
            tracks_out.append(dict(trial=trial,track_id=tid,first_frame=track[0][0],last_frame=track[-1][0],rows=len(track),missing_frames=missing,duplicate_frames=duplicate,downstream_crossing_s=crossing))
            labels.append(dict(trial=trial,track_id=tid,persistent_comment_id=links.get(tid,''),wheelchair_label='documented_wheelchair_id' if links.get(tid) in registry else 'not_established_by_this_registry',helper_track_id='',age='',family_id=''))
        r=runs[trial];par=r['parameter']
        inventory.append(dict(trial=trial,metadata_count=r['number_participants'],tracked_count=len(tracks),count_matches=len(tracks)==r['number_participants'],metadata_disability_count=par.get('subjects_with_disability',''),width_m=par.get('bottleneck_width [m]',''),fps=25,wheelchair_mappings=sum(v in registry for v in links.values()),all_track_common_start_frame=max(a for a,b in all_intervals),all_track_common_end_frame=min(b for a,b in all_intervals),downstream_crossings=len(crossings),all_crossed=len(crossings)==len(tracks),first_crossing_s=min(crossings) if crossings else '',last_crossing_s=max(crossings) if crossings else '',passage_span_s=max(crossings)-min(crossings) if crossings else '',missing_frame_total=gaps,duplicate_frame_total=duplicates,source_sha256=hashlib.sha256(read(name)).hexdigest()))
        exposure.append(dict(trial=trial,prior_status='previously downloaded and inspected; not untouched',prior_use='reference replay calibration' if trial in ['1501','1507'] else 'reference replay evaluated test; now exposed' if trial in ['1503','1505'] else 'earlier inspection/validation',new_audit='coverage and outcome inspected',eligible_as_fresh_test=False))
    save_csv('trial_inventory.csv',inventory);save_csv('track_coverage.csv',tracks_out)
    save_csv('label_audit.csv',labels);save_csv('exposure_ledger.csv',exposure)
    # Full official metadata inventory, without opening additional trajectory outcomes.
    save_csv('metadata_inventory.csv',[dict(trial=t,participants=r['number_participants'],disabled=r['parameter'].get('subjects_with_disability',''),width=r['parameter'].get('bottleneck_width [m]',''),local_raw_available=t in {Path(n).stem for n in names}) for t,r in sorted(runs.items())])
    summary=dict(local_trials=len(names),metadata_trials=len(runs),person_trial_tracks=len(labels),documented_wheelchair_person_trial_labels=sum(x['wheelchair_label']=='documented_wheelchair_id' for x in labels),unique_documented_wheelchair_ids=len({x['persistent_comment_id'] for x in labels if x['wheelchair_label']=='documented_wheelchair_id'}),confirmed_helper_links=0,age_links=0,all_trials_have_complete_downstream_crossings=all(x['all_crossed'] for x in inventory),source_metadata_sha256=hashlib.sha256(read(metadata_path)).hexdigest())
    (OUT/'audit_summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary)); print(json.dumps(inventory,indent=2))
