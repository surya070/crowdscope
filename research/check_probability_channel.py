"""Exact enumeration of a four-person artificial observation fixture.

Not a crowd simulation, fitted classifier or benchmark evaluation.
"""
from pathlib import Path
import itertools
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.mobility_probability import posterior, composition


def enumerate_case(true_prior,working_prior,error):
    metrics={k:dict(brier=0.0,zone_count_mae=0.0,interval_coverage=0.0)
             for k in ['prior_only','hard_observed','hard_posterior','probabilistic']}
    mass_total=0.0
    reliability={}
    for labels in itertools.product((0,1),repeat=4):
        for flips in itertools.product((0,1),repeat=4):
            mass=1.0
            for c,e in zip(labels,flips):
                mass*= (true_prior if c else 1-true_prior)*(error if e else 1-error)
            observed=[c^e for c,e in zip(labels,flips)]
            probs=[posterior(o,working_prior,error) for o in observed]
            for p,c in zip(probs,labels):
                bucket=reliability.setdefault(p,[0.0,0.0])
                bucket[0]+=mass/4
                bucket[1]+=mass*c/4
            variants={'prior_only':[working_prior]*4,'hard_observed':observed,
                      'hard_posterior':[int(p>0.5) for p in probs],'probabilistic':probs}
            mass_total+=mass
            for name,ps in variants.items():
                metrics[name]['brier']+=mass*sum((p-c)**2 for p,c in zip(ps,labels))/4
                for start in (0,2):
                    s=composition(ps[start:start+2]);truth=sum(labels[start:start+2])
                    metrics[name]['zone_count_mae']+=mass*abs(s['expected_count']-truth)/2
                    lo,hi=s['interval']
                    metrics[name]['interval_coverage']+=mass*int(lo<=truth<=hi)/2
    assert abs(mass_total-1)<1e-12
    bins=[dict(predicted=p,observation_mass=v[0],actual_class_frequency=v[1]/v[0])
          for p,v in sorted(reliability.items()) if v[0]>0]
    return dict(true_prior=true_prior,working_prior=working_prior,error=error,
                enumerated_states=256,total_probability=mass_total,metrics=metrics,
                reliability=bins,max_calibration_gap=max(abs(b['predicted']-b['actual_class_frequency']) for b in bins))


def main():
    cases=[enumerate_case(0.2,0.2,0.2),enumerate_case(0.5,0.2,0.2)]
    assert abs(cases[0]['metrics']['probabilistic']['brier']-2/17)<1e-12
    assert cases[0]['max_calibration_gap']<1e-12
    assert cases[1]['max_calibration_gap']>0.29
    out=ROOT/'output/probability_fixture_v1';out.mkdir(parents=True,exist_ok=True)
    payload={'evidence':'exact artificial channel checks; no crowd dynamics or real recognition',
             'seed_usage':'none; exhaustive enumeration; reserved benchmark seeds untouched','cases':cases}
    (out/'results.json').write_text(json.dumps(payload,indent=2)+'\n',encoding='utf-8')
    for case in cases:print(json.dumps(case))


if __name__=='__main__':main()
