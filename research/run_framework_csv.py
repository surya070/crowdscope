"""Run the saved calibrated framework on canonical trajectory CSV and zone JSON."""
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.deps/detector'),str(ROOT/'.deps/recovery-r1')]
from itertools import groupby
from shapely import wkt
from shapely.geometry import Point as SP
from src.crowd_state import load_csv
from src.polygon_zones import PolygonZone,validate_partition
from src.calibrated_detector import CalibratedMotionDetector
from src.crowd_framework import CrowdFramework

def main():
    a=argparse.ArgumentParser();a.add_argument('csv');a.add_argument('config');a.add_argument('--output',required=True);a.add_argument('--model');a.add_argument('--every',type=float,default=1.);args=a.parse_args()
    if args.every<=0:raise ValueError('Snapshot interval must be positive')
    config=json.loads(Path(args.config).read_text());area=wkt.loads(config['observable_wkt'])
    zones=[PolygonZone(z['id'],wkt.loads(z['wkt'])) for z in config['zones']];validate_partition(zones,area)
    detector=CalibratedMotionDetector(args.model)
    engine=CrowdFramework(zones,detector,roi_contains=lambda p:area.covers(SP(p.x,p.y)),
        budget=config.get('budget',6),capacity=config.get('capacity',2),r0=config.get('r0',.1),r1=config.get('r1',.4))
    points=sorted(load_csv(args.csv),key=lambda p:(p.time,p.person));last=-float('inf')
    with Path(args.output).open('w') as f:
        for time,group in groupby(points,key=lambda p:p.time):
            engine.ingest_frame(time,[(p.person,p.x,p.y) for p in group])
            if time-last>=args.every-1e-9:f.write(json.dumps(engine.analyse())+'\n');last=time
    print('Saved causal crowd-state and planning snapshots to',args.output)
if __name__=='__main__':main()
