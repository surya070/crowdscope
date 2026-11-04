"""Development diagnostics: tight traversable vs body-inaccessible neck."""
from pathlib import Path
import sys,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.deps/recovery-r1')]
from shapely.geometry import box
from shapely.ops import unary_union
from research.run_simulation_checks import run


def main():
    out=ROOT/'output/passage_limits_v1';out.mkdir(parents=True,exist_ok=True)
    if (out/'lock.json').exists():raise RuntimeError('Preserve previous diagnostics')
    lock=dict(widths_m=[0.6,0.3],body_diameter_m=0.44,dt=[0.01,0.005],
        expected='0.6m traversable; 0.3m body-inaccessible, no fabricated exit',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'lock.json').write_text(json.dumps(lock,indent=2))
    results=[]
    for width in (0.6,0.3):
        area=unary_union([box(-5,-2,4,2),box(3.9,-width/2,6.1,width/2),box(6,-2,10,2)])
        c=dict(name=f'neck_{width}',area=area,starts=[(0,0)],speeds=[1.0],goal=(9,0),axis=0,plane=8)
        for dt in (0.01,0.005):
            result=run(c,dt);results.append(result)
            print(json.dumps({k:v for k,v in result.items() if k!='frames'}),flush=True)
    (out/'results.json').write_text(json.dumps(results))


if __name__=='__main__':main()
