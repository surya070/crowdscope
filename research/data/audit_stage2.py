"""Audit archived SiME inputs without restoring raw tracks or fitting models.

Run from any directory with Python's standard library. Outputs are local study
records, not a claim that the source data may be redistributed.
"""
from pathlib import Path
from collections import defaultdict
import csv
import hashlib
import json
import re
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/data/stage2'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    old = json.loads((ROOT/'backups/backup_verification.json').read_text())
    recent = json.loads((ROOT/'backups/probabilistic_reset_verification_20261103_224341.json').read_text())
    recent_hashes = {x['path']: x['sha256'] for x in recent['files']}
    sources = [
        ('project_before_research_reset_20261102_113200.zip', {k:v['sha256'] for k,v in old['files'].items()}),
        (recent['archive'], recent_hashes),
    ]
    inputs = []
    trial_bytes = {}
    metadata = None
    for archive, hashes in sources:
        with zipfile.ZipFile(ROOT/'backups'/archive) as z:
            selected = [n for n in z.namelist() if re.fullmatch(r'data/raw/sime2017/members/\d+\.txt', n)]
            if archive == sources[0][0]:
                selected.append('research/data_search_20261030/sime_metadata_prefix.txt')
            for name in selected:
                b = z.read(name)
                digest = hashlib.sha256(b).hexdigest()
                assert digest == hashes[name], name
                inputs.append(dict(archive=archive, member=name, sha256=digest))
                if name.endswith('sime_metadata_prefix.txt'):
                    metadata = json.loads(b)['experiment']
                else:
                    trial = Path(name).stem
                    if trial in trial_bytes:
                        assert trial_bytes[trial][0] == b, 'Conflicting archive versions'
                    trial_bytes[trial] = (b, archive)
    assert metadata is not None
    runs = {str(x['run_name']): x for x in metadata['run']}
    inventory, labels, coverage = [], [], []
    identities = defaultdict(set)
    wheelchair_ids = set(range(34, 41))  # Historical documented registry; not inferred from speed.
    for trial, (b, archive) in sorted(trial_bytes.items(), key=lambda x:int(x[0])):
        text = b.decode('utf-8-sig').replace('\r', '')
        assert '# framerate: 25 fps' in text
        mapping = {int(a):int(v) for a,v in re.findall(r'^#\s*(\d+)\|\s*(\d+)\s*$', text, re.M)}
        tracks = defaultdict(list)
        for line in text.splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            a = line.split()
            tracks[int(a[0])].append((int(a[1]), float(a[2]), float(a[3])))
        crossing_count = missing = duplicates = positive = 0
        for tid, points in sorted(tracks.items()):
            points.sort()
            dup = len(points) - len({x[0] for x in points})
            gap = sum(max(0,v[0]-u[0]-1) for u,v in zip(points, points[1:]))
            crossed = any(u[1] < 2.4 <= v[1] and v[0]-u[0] == 1 for u,v in zip(points, points[1:]))
            pid = mapping.get(tid)
            known_wc = pid in wheelchair_ids
            positive += known_wc
            if pid is not None:
                identities[pid].add(trial)
            labels.append(dict(trial=trial, track_id=tid, persistent_id=pid if pid is not None else '',
                               wheelchair_status='historically_documented_positive' if known_wc else 'unverified_by_positive_registry',
                               age='', helper_track='', assistance_demand=''))
            coverage.append(dict(trial=trial, track_id=tid, first_frame=points[0][0], last_frame=points[-1][0],
                                 rows=len(points), gaps=gap, duplicates=dup, observed_forward_crossing=crossed))
            crossing_count += crossed
            missing += gap
            duplicates += dup
        run = runs[trial]
        inventory.append(dict(trial=trial, tracks=len(tracks), metadata_count=run['number_participants'],
                              count_matches=len(tracks)==run['number_participants'],
                              width_m=run['parameter'].get('bottleneck_width [m]', ''),
                              documented_wheelchair_tracks=positive,
                              crossings=crossing_count, gaps=missing, duplicates=duplicates,
                              exposure='previously inspected development evidence', fresh_test=False,
                              archive=archive, sha256=hashlib.sha256(b).hexdigest()))
    # Connected trial components through known persistent IDs: unknown IDs can
    # only add connections, so these are a lower bound on dependence.
    neighbours = {t:set() for t in trial_bytes}
    for group in identities.values():
        for t in group:
            neighbours[t].update(group-{t})
    components = []
    remaining = set(neighbours)
    while remaining:
        frontier = [min(remaining, key=int)]
        component = set()
        while frontier:
            t = frontier.pop()
            if t in component:
                continue
            component.add(t)
            frontier.extend(neighbours[t]-component)
        remaining -= component
        components.append(sorted(component, key=int))
    def save(name, rows):
        with (OUT/name).open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    save('trial_inventory.csv', inventory)
    save('label_inventory.csv', labels)
    save('track_coverage.csv', coverage)
    summary = dict(trials=len(inventory), person_trial_tracks=len(labels),
                   documented_wheelchair_person_trials=sum(x['documented_wheelchair_tracks'] for x in inventory),
                   unique_documented_wheelchair_ids=sorted(set(identities)&wheelchair_ids),
                   missing_persistent_id_tracks=sum(x['persistent_id']=='' for x in labels),
                   known_identity_trial_components=components,
                   count_mismatch_trials=[x['trial'] for x in inventory if not x['count_matches']],
                   incomplete_crossing_trials=[x['trial'] for x in inventory if x['crossings']!=x['tracks']],
                   internally_missing_frames=sum(x['gaps'] for x in inventory),
                   duplicate_frames=sum(x['duplicates'] for x in inventory),
                   independent_fresh_test_trials=0, verified_age_links=0, verified_helper_links=0,
                   verified_demand_labels=0, model_fitted=False,
                   caveat='Positive registry does not establish negative labels; archived source attribution needs current verification.')
    (OUT/'audit.json').write_text(json.dumps(dict(summary=summary, inputs=inputs), indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
