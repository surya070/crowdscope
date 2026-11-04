"""Prototype scoring of a four-second, 25 Hz, passage-aligned XY history.

Load only project-generated model artifacts. Outputs are uncalibrated scores;
this does not establish medical status, age or actual assistance need.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'.deps/detector'));sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
import numpy as np

def predict_motion(positions_m,times_s,artifact_path=None):
    import joblib
    from research.build_detector_data import features
    pos=np.asarray(positions_m,dtype=float);times=np.asarray(times_s,dtype=float)
    if pos.shape!=(101,2) or times.shape!=(101,):raise ValueError('Need exactly 101 XY samples and timestamps')
    if not np.isfinite(pos).all() or not np.isfinite(times).all():raise ValueError('Nonfinite observation')
    if not np.allclose(np.diff(times),.04,rtol=0,atol=1e-6):raise ValueError('Need contiguous 25 Hz observations; do not fill gaps silently')
    artifact=joblib.load(artifact_path or ROOT/'output/detector_v1/candidate_model_LOCAL_ONLY.joblib')
    f,n,seq=features(pos)
    if n!=artifact['feature_names']:raise ValueError('Feature definition mismatch')
    if artifact['kind']=='sklearn':
        model=artifact['model'];x=f[artifact['columns']][None]
        score=float(model.decision_function(x)[0]) if artifact['family']=='RBF SVM' else float(model.predict_proba(x)[0,1])
    else:
        import torch
        from research.run_detector_benchmark import Neural
        x=f[artifact['columns']][None] if artifact['family']=='MLP' else seq[None]
        model=Neural(artifact['family'],artifact['input_dim']);model.load_state_dict(artifact['state']);model.eval()
        with torch.no_grad():score=float(torch.sigmoid(model(torch.tensor((x-artifact['mean'])/artifact['sd'],dtype=torch.float32)))[0])
    return dict(score=score,positive_motion_pattern=bool(score>=artifact['threshold']),family=artifact['family'],
                interpretation='Uncalibrated exploratory wheelchair-associated motion score, not a confirmed identity or assistance request')
