"""Verify preassigned development members and draft checkpoint coverage."""
from pathlib import Path
import csv,json,hashlib,re,zlib
from collections import defaultdict

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/data/expansion';OUT.mkdir(exist_ok=True)
assignment=json.loads((ROOT/'research/data/expansion_assignment.json').read_text())
rows=[];queries=[];sources=[];labelrows=[]
for planned in assignment['trials']:
 t=planned['trial'];path=ROOT/f'data/raw/sime2017/members/{t}.txt'
 raw=path.read_bytes()
 assert len(raw)==planned['expected_bytes']
 assert zlib.crc32(raw)==planned['expected_zip_crc32']
 text=raw.decode('utf-8-sig').replace('\r','')
 mapping={int(a):int(b) for a,b in re.findall(r'^#\s*(\d+)\|\s*(\d+)\s*$',text,re.M)}
 tracks=defaultdict(dict)
 for line in text.splitlines():
  if not line.strip() or line.startswith('#'):continue
  a=line.split();tid,f=int(a[0]),int(a[1]);assert f not in tracks[tid]
  tracks[tid][f]=float(a[2])
 crossings={};missing=[];gaps=0
 for tid,track in tracks.items():
  frames=sorted(track);gaps+=sum(max(0,b-a-1) for a,b in zip(frames,frames[1:]))
  for f in frames:
   if f+1 in track and track[f]<2.4<=track[f+1]:
    crossings[tid]=(f+(2.4-track[f])/(track[f+1]-track[f]))/25;break
  if tid not in crossings:missing.append(tid)
  labelrows.append(dict(trial=t,track_id=tid,persistent_comment_id=mapping.get(tid,''),wheelchair_documented=mapping.get(tid) in range(34,41),other_class_status='not_verified_by_this_registry',helper_id='',age=''))
 wc=[tid for tid,pid in mapping.items() if pid in range(34,41)]
 rows.append(dict(trial=t,metadata_count=planned['metadata_participants'],tracks=len(tracks),count_matches=len(tracks)==planned['metadata_participants'],documented_wheelchair_tracks=len(wc),persistent_wheelchair_ids=';'.join(map(str,sorted(mapping[tid] for tid in wc))),crossings=len(crossings),missing_track_ids=';'.join(map(str,missing)),missing_internal_frames=gaps,width_m=planned['parameters']['bottleneck_width [m]']))
 for time in [10,20,30]:
  frame=time*25
  cohort=[tid for tid,tr in tracks.items() if all(f in tr for f in range(frame-50,frame+1)) and tr[frame]<2.4]
  absent=[tid for tid in cohort if tid not in crossings]
  queries.append(dict(trial=t,time_s=time,cohort_count=len(cohort),wheelchair_members=len(set(cohort)&set(wc)),missing_outcomes=len(absent),coverage_eligible=bool(cohort) and not absent and len(tracks)==planned['metadata_participants'],remaining_observed_cohort_passage_s=max(crossings[tid] for tid in cohort)-time if cohort and not absent else '',development_only=True))
 sources.append(dict(trial=t,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),crc32=zlib.crc32(raw),role=planned['role']))
def write(name,records):
 with (OUT/name).open('w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
write('trials.csv',rows);write('queries.csv',queries);write('labels.csv',labelrows)
summary=dict(acquired_trials=len(rows),person_trial_tracks=sum(r['tracks'] for r in rows),wheelchair_person_trial_mappings=sum(r['documented_wheelchair_tracks'] for r in rows),unique_documented_wheelchair_ids=sorted({int(v) for r in rows for v in r['persistent_wheelchair_ids'].split(';') if v}),count_consistent_trials=sum(r['count_matches'] for r in rows),complete_crossing_trials=sum(r['tracks']==r['crossings'] for r in rows),eligible_queries=sum(q['coverage_eligible'] for q in queries),candidate_queries=len(queries),fresh_independent_test_cohorts=0,learner_fitted=False)
(OUT/'acquisition_manifest.json').write_text(json.dumps({'sources':sources,'summary':summary},indent=2))
print(json.dumps(summary,indent=2));print(json.dumps(rows,indent=2))
