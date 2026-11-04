"""Audit integration conservation and evidence labels from saved outputs."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'output/recorded_occupancy_integration_v1'
    lock=json.loads((out/'lock.json').read_text())
    assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in lock['hashes'].items())
    rows=json.loads((out/'summary.json').read_text());assert len(rows)==42
    assert len({(r['trial'],r['time_s']) for r in rows})==42
    for r in rows:
        assert r['visible_all']==r['inside_roi_box']+r['outside_roi_box']
        if r['status']!='integrated':continue
        p=json.loads((out/f"{r['trial']}_{r['time_s']}.json").read_text())
        state=p['state'];comp=p['composition']
        assert 'hypothetical' in p['evidence']
        assert sum(z['count'] for z in state['zones'])==len(state['occupants'])==r['inside_roi_box']
        assert len({p['person_id'] for p in state['occupants']})==len(state['occupants'])
        for z,c in zip(state['zones'],comp):
            assert z['count']==c['observed_count']
            assert abs(z['density_people_m2']*z['area_m2']-z['count'])<1e-9
            assert 0<=c['expected_count']<=c['observed_count']
            assert abs(sum(c['pmf'])-1)<1e-10
        assert sum(p['planning']['allocation'])==6
    report=dict(passed=True,checkpoints=len(rows),integrated=sum(r['status']=='integrated' for r in rows),
                empirical_demographic_recognition=False,empirical_demand_validation=False)
    (out/'audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))


if __name__=='__main__':main()
