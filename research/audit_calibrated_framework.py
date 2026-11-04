"""Independent metric, group separation, temporal and count audit."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
import numpy as np
OUT=ROOT/'output/calibrated_framework_v1'

def main():
    for lock in [OUT/'calibration_lock.json',OUT/'pipeline_lock.json',ROOT/'output/detector_v1/benchmark_lock.json']:
        for name,h in json.loads(lock.read_text())['hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
    d=np.load(ROOT/'output/detector_v1/data_LOCAL_ONLY.npz');trial=d['trial'];pid=d['pid'];split=json.loads((OUT/'split_audit_LOCAL_ONLY.json').read_text())
    inner_count=0
    for s in split:
        tr=np.array(s['outer_train']);te=np.array(s['outer_test']);t=s['held_trial'];p=s['held_pid']
        assert not set(tr)&set(te) and not (trial[tr]==t).any()
        if p is not None:assert p not in pid[tr]
        for i in s['inner']:
            itr=np.array(i['train']);ite=np.array(i['test']);inner_count+=1
            assert set(itr)<=set(tr) and set(ite)<=set(tr)
            assert not set(itr)&set(ite) and not set(trial[itr])&set(trial[ite])
            if p is not None:
                assert p not in pid[itr] and p not in pid[ite]
                assert not set(pid[itr][pid[itr]>=0])&set(pid[ite][pid[ite]>=0])
    summary=json.loads((OUT/'calibration_summary.json').read_text())
    for mode in summary:
        r=json.loads((OUT/f'{mode}_predictions_LOCAL_ONLY.json').read_text());y=np.array([a['y'] for a in r]);w=np.array([a['weight'] for a in r]);assert abs(w.sum()-len(d['y']))<1e-8
        for key in ['prior','raw','calibrated']:
            p=np.array([a[key] for a in r]);assert np.all((p>=0)&(p<=1))
            brier=float(sum(w*(p-y)**2)/sum(w));assert abs(brier-summary[mode][key]['Brier'])<1e-12
            p=np.clip(p,1e-12,1-1e-12);loss=float(-sum(w*(y*np.log(p)+(1-y)*np.log1p(-p)))/sum(w))
            assert abs(loss-summary[mode][key]['log_loss'])<1e-12
    replays=json.loads((OUT/'replay_LOCAL_ONLY.json').read_text());frames=0
    for r in replays:
        last=-float('inf')
        for f in r['frames']:
            frames+=1;assert f['time_s']>last;last=f['time_s']
            assert sum(z['count'] for z in f['zones'])==len(f['occupants'])
            assert abs(sum(z['expected_count'] for z in f['zones'])-f['composition']['expected_count'])<1e-8
            assert sum(f['planning']['allocation'])==6
            for p in f['occupants']:
                assert 0<=p['wheelchair_probability']<=1
                assert p['probability_observed_at_s'] is None or p['probability_observed_at_s']<=f['time_s']
    result=dict(passed=True,outer_folds=len(split),inner_folds=inner_count,replay_frames=frames,
        checks=['locked source hashes','nested trial/person exclusions','independent Brier/logloss','probability bounds','count conservation','causal estimate timestamps','capacity-budget conservation'],
        limitation='Unknown control identities; whole-trial replay has repeated participants; request outcomes are hypothetical')
    (OUT/'audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
if __name__=='__main__':main()
