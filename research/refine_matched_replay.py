"""Recheck a historically calibrated reference configuration; no new selection."""
from pathlib import Path
import csv,hashlib,importlib.util,io,json,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'.deps/recovery-r1'),str(ROOT)]
import numpy as np
from shapely import wkt
from research.matched_replay_engine import replay,first_crossing,metrics,free_flight


def load_trials():
    verification=json.loads((ROOT/'backups/backup_verification.json').read_text())
    with zipfile.ZipFile(ROOT/'backups/project_before_research_reset_20261102_113200.zip') as z:
        def read(name):
            b=z.read(name);assert hashlib.sha256(b).hexdigest()==verification['files'][name]['sha256'];return b
        meta=json.loads(read('research/data_search_20261030/sime_metadata_prefix.txt'))['experiment']
        result=[]
        for tid in ('1501','1507'):
            b=read(f'data/raw/sime2017/members/{tid}.txt');a=np.loadtxt(io.BytesIO(b))
            row=next(r for r in meta['run'] if str(r['run_name'])==tid)
            assert int(row['parameter']['subjects_with_disability'])==0
            arrivals=[];targets={}
            for pid in np.unique(a[:,0]).astype(int):
                track=a[a[:,0]==pid];track=track[np.argsort(track[:,1])]
                assert np.all(np.diff(track[:,1])==1)
                entry=first_crossing(track,-6);cross=first_crossing(track,2.4)
                assert entry is not None and cross is not None and entry['t']<cross['t']
                arrivals.append(dict(id=int(pid),t=entry['t'],position=[-6,entry['y']]))
                targets[int(pid)]=cross['t']
            assert len(arrivals)==row['number_participants']
            result.append(dict(id=tid,area=wkt.loads(row['wkt_geometry']),metadata=row,
                               arrivals=sorted(arrivals,key=lambda r:(r['t'],r['id'])),targets=targets,
                               source_sha256=hashlib.sha256(b).hexdigest()))
    return result


def main():
    out=ROOT/'output/matched_replay_refinement_v1';out.mkdir(parents=True,exist_ok=True)
    if (out/'lock.json').exists():raise RuntimeError('Preserve previous matched run')
    params=dict(speed=1.6,radius=0.18,time_gap=1.0)
    trials=load_trials()
    lock=dict(purpose='development finer timestep after inspecting matched replay failures; no retuning',
        trials=['1501','1507'],exposure='previous calibration trials, fully exposed',params=params,
        inherited_selection='archived output/sime_replay_v2/selected_freeze.json candidate13',
        dt=[0.0025],inlet_x=-6,measurement_x=2.4,conditional_future_arrivals=True,
        spatial_tolerance_m=dict(overlap=0.001,wall=0.005),checks='every step; saved positions every0.1s',
        comparison='individual head-crossing MAE and same-arrivals free-flight; passage and headways descriptive',
        selection='none; retain failures; no additional parameter candidates',
        hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['research/refine_matched_replay.py','research/matched_replay_engine.py']},
        inputs={t['id']:t['source_sha256'] for t in trials})
    (out/'lock.json').write_text(json.dumps(lock,indent=2))
    summaries=[]
    for trial in trials:
        for dt in (0.0025,):
            result=replay(trial['area'],trial['arrivals'],params,dt=dt,save_frames=True)
            result['metrics']=metrics(result,trial)
            result['baseline_metrics']=metrics(free_flight(trial,params['speed']),trial)
            result['trial']=trial['id']
            (out/(trial['id']+'_'+str(dt).replace('.','_')+'.json')).write_text(json.dumps(result))
            row={k:v for k,v in result.items() if k not in ['frames','admissions','crossings']}
            summaries.append(row);(out/'summary.json').write_text(json.dumps(summaries,indent=2))
            print(json.dumps(row),flush=True)


if __name__=='__main__':main()
