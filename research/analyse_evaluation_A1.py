"""Frozen paired seed-block analysis; no model or case selection."""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
import numpy as np


def main():
    out=ROOT/'output/planning_evaluation_A1'
    config=json.loads((ROOT/'configs/evaluation_A1.json').read_text())
    rows=json.loads((out/'results.json').read_text())
    lock=json.loads((out/'lock.json').read_text())
    assert all(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h for n,h in lock['hashes'].items())
    seeds=config['evaluation_seeds'];assert len(seeds)==60 and lock['seeds']==seeds
    grouped=defaultdict(list);actions=defaultdict(dict)
    for row in rows:
        grouped[row['case'],row['policy'],row['block']].append(row['realised_unmet'])
        actions[row['case'],row['scenario']][row['policy']]=tuple(row['allocation'])
    rng=np.random.default_rng(config['bootstrap']['seed'])
    indices=rng.integers(0,len(seeds),size=(config['bootstrap']['replicates'],len(seeds)))
    summaries=[];block_rows=[]
    for case in config['cases']:
        name=case['name'];means={}
        for policy in config['policies']:
            values=[]
            for seed in seeds:
                v=grouped[name,policy,seed];assert len(v)==10
                values.append(sum(v)/len(v));block_rows.append(dict(case=name,policy=policy,block=seed,mean_unmet=values[-1]))
            means[policy]=np.array(values)
        policy_metrics={p:dict(mean=float(v.mean()),block_sd=float(v.std(ddof=1))) for p,v in means.items()}
        comparisons={}
        for comparator in ['hard_posterior','hard_observed','homogeneous','mean_demand','known_class']:
            diff=means['probabilistic']-means[comparator]
            boot=diff[indices].mean(axis=1)
            scenarios=[a for (c,_),a in actions.items() if c==name]
            comparisons[comparator]=dict(mean_difference=float(diff.mean()),
                percentile_95_interval=[float(x) for x in np.quantile(boot,[0.025,0.975])],
                better_blocks=int((diff< -1e-12).sum()),tied_blocks=int((abs(diff)<=1e-12).sum()),
                worse_blocks=int((diff>1e-12).sum()),
                identical_allocation_fraction=sum(a['probabilistic']==a[comparator] for a in scenarios)/len(scenarios))
        summaries.append(dict(case=name,policies=policy_metrics,comparisons=comparisons))
    payload=dict(analysis='paired block-bootstrap; secondary comparisons descriptive, not multiplicity-adjusted',
                 independent_seed_blocks=60,replicas_per_block=10,conditions=14,results=summaries)
    (out/'analysis.json').write_text(json.dumps(payload,indent=2))
    with (out/'block_metrics.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(block_rows[0]));w.writeheader();w.writerows(block_rows)
    primary=next(x for x in summaries if x['case']=='base')
    print(json.dumps(primary,indent=2))


if __name__=='__main__':main()
