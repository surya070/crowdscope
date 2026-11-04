"""Calibrated working membership probabilities for the audited SiME domain."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'.deps/detector'),str(ROOT/'.deps/recovery-r1')]
import numpy as np

class CalibratedMotionDetector:
    def __init__(self,model_path=None):
        import joblib
        self.artifact=joblib.load(model_path or ROOT/'output/calibrated_framework_v1/calibrated_model_LOCAL_ONLY.joblib')
        if 'calibrator' not in self.artifact:raise ValueError('A calibrated model is required')
        self.training_prior=float(self.artifact['training_prior'])
        self.scope=self.artifact['calibration_scope']

    def predict(self,positions_m,times_s):
        from research.build_detector_data import features
        pos=np.asarray(positions_m,dtype=float);times=np.asarray(times_s,dtype=float)
        if pos.shape!=(101,2) or times.shape!=(101,):raise ValueError('Need 101 XY samples covering four seconds')
        if not np.isfinite(pos).all() or not np.isfinite(times).all():raise ValueError('Nonfinite input')
        if not np.allclose(np.diff(times),.04,rtol=0,atol=1e-6):raise ValueError('Need uninterrupted 25Hz observations')
        f,n,_=features(pos)
        if n!=self.artifact['feature_names']:raise ValueError('Feature schema mismatch')
        model=self.artifact['model'];x=f[self.artifact['columns']][None]
        score=float(model.decision_function(x)[0])
        p=float(self.artifact['calibrator'].predict_proba([[score]])[0,1])
        return dict(probability=p,raw_score=float(model.predict_proba(x)[0,1]),
            hard_label=int(p>=.5),calibration_scope=self.scope,
            interpretation='Working probability of wheelchair-associated membership within the studied trajectory domain; not assistance demand')
