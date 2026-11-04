"""Audit saved stress outcomes, grouping, provenance and negative controls."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.resource_planning import realised_shortfall


def main():
    out=ROOT/'output/planning_stress_v1'
    lock=json.loads((out/'lock.json').read_text())
    assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in lock['hashes'].items())
    cases={c['name']:c for c in lock['cases']}
    scenarios=json.loads((out/'scenarios.json').read_text());rows=json.loads((out/'results.json').read_text())
    assert len(scenarios)==14*16*10 and len(rows)==len(scenarios)*7
    lookup={s['id']:s for s in scenarios};assert len(lookup)==len(scenarios)
    grouped=defaultdict(dict)
    for s in scenarios:
        counts=cases[s['case']]['counts'];assert len(s['labels'])==len(s['observations'])==len(s['requests'])==sum(counts)==80
        assert s['block'] in lock['seeds'] and 410004<=s['block']<=410019
        start=0;demand=[]
        for n in counts:demand.append(sum(s['requests'][start:start+n]));start+=n
        assert demand==s['demands']
    for row in rows:
        s=lookup[row['scenario']];case=cases[s['case']]
        assert row['block']==s['block'] and row['replica']==s['replica'] and row['case']==s['case']
        assert row['policy'] not in grouped[s['id']]
        grouped[s['id']][row['policy']]=row
        assert len(row['allocation'])==4 and sum(row['allocation'])==case['budget']
        assert all(isinstance(a,int) and a>=0 for a in row['allocation'])
        assert realised_shortfall(row['allocation'],s['demands'])==row['realised_unmet']
    for sid,policies in grouped.items():
        lower=policies['perfect_demand_reference']['realised_unmet']
        assert len(policies)==7 and all(row['realised_unmet']>=lower for row in policies.values())
        case=lookup[sid]['case']
        if case=='uninformative':
            assert policies['probabilistic']['allocation']==policies['homogeneous']['allocation']
        if case=='perfect_observation':
            assert policies['probabilistic']['allocation']==policies['known_class']['allocation']==policies['hard_observed']['allocation']
        if case=='equal_demand_control':
            assert len({tuple(policies[p]['allocation']) for p in ['homogeneous','probabilistic','hard_observed','hard_posterior','known_class']})==1
    result=dict(pass_checks=True,scenario_replicas=len(scenarios),policy_records=len(rows),
                independent_development_blocks=16,conditions=14,
                negative_controls=['uninformative','perfect_observation','equal_demand_control'],final_evaluation_access=False)
    (out/'audit.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))


if __name__=='__main__':main()
