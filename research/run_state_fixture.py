"""Generate a small deterministic measurement replay, not crowd simulation."""
from pathlib import Path
import csv
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.crowd_state import Point, Zone, load_csv, snapshot


def main():
    out=ROOT/'output/state_fixture_v1'
    out.mkdir(parents=True,exist_ok=True)
    # Four 2x2 m zones, walking agent a and stationary agent b.
    zones=[Zone(0,0,0,2,2),Zone(1,2,0,4,2),Zone(2,0,2,2,4),Zone(3,2,2,4,4)]
    path=out/'trajectories.csv'
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['person_id','time','x','y'])
        for step in range(21):
            t=step/10
            w.writerow(['a',t,0.5+t,1])
            w.writerow(['b',t,3,3])
    points=load_csv(path)
    states=[snapshot(points,zones,step/10,history=1,max_gap=0.11,crossing_x=2) for step in range(21)]
    assert all(sum(z['count'] for z in s['zones'])==2 for s in states)
    assert [z['count'] for z in states[-1]['zones']]==[0,1,0,1]
    assert states[-1]['forward_crossing_events']==1
    assert abs(states[-1]['occupants'][0]['mean_speed_m_s']-1)<1e-12
    payload={'source':'hand-authored measurement fixture; not JuPedSim or empirical evidence',
             'zones':[z.__dict__ for z in zones],'frames':states}
    (out/'replay.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    print('Fixture passed: 21 snapshots; two occupants conserved; 1 m/s walker; one forward crossing.')


if __name__=='__main__':main()
