"""Static development pilot, synthetic metadata/demand; no motion validation."""
from pathlib import Path
import csv,hashlib,json,random,sys,statistics
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.mobility_probability import posterior
from src.resource_planning import plan,request_probability,realised_shortfall,allocations


def main():
    out=ROOT/'output/planning_pilot_v1';out.mkdir(parents=True,exist_ok=True)
    if (out/'lock.json').exists():raise RuntimeError('Preserve development results')
    counts=[20,20,20,20]
    lock=dict(purpose='development smoke pilot; not locked final hypothesis test',
        block_seeds=list(range(410000,410004)),replicas=10,zone_counts=counts,
        prevalence=0.2,error=0.2,request_rates=[0.1,0.4],budget=6,capacity=2,
        scenario='fixed zone rosters independent of movement; not a JuPedSim result',
        hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['src/resource_planning.py','src/mobility_probability.py','research/run_planning_pilot.py']})
    (out/'lock.json').write_text(json.dumps(lock,indent=2))
    rows=[];scenarios=[]
    for block in lock['block_seeds']:
        class_rng=random.Random(block+10000)
        classes=[[int(class_rng.random()<0.2) for _ in range(n)] for n in counts]
        for replica in range(10):
            noise=random.Random(block*100+replica+30000000)
            requests=random.Random(block*100+replica+60000000)
            obs=[[c^int(noise.random()<0.2) for c in group] for group in classes]
            demands=[sum(int(requests.random()<(0.4 if c else 0.1)) for c in group) for group in classes]
            ps=[[posterior(o,0.2,0.2) for o in group] for group in obs]
            variants={'homogeneous':[[0.2]*n for n in counts],'hard_observed':obs,
                'hard_posterior':[[int(p>0.5) for p in group] for group in ps],
                'probabilistic':ps,'mean_demand':ps,'known_class':classes}
            scenarios.append(dict(block=block,replica=replica,classes=classes,observations=obs,demands=demands))
            for name,memberships in variants.items():
                # Realised requests are never passed into deployable policies.
                q=[[request_probability(p) for p in group] for group in memberships]
                result=plan(q,6,2,mean_only=name=='mean_demand')
                loss=realised_shortfall(result['allocation'],demands,2)
                rows.append(dict(block=block,replica=replica,policy=name,allocation=list(result['allocation']),
                    expected_loss=result['expected_loss'],realised_unmet=loss,total_requests=sum(demands)))
            options=list(allocations(4,6))
            optimum=min(options,key=lambda a:(realised_shortfall(a,demands,2),a))
            rows.append(dict(block=block,replica=replica,policy='perfect_demand_reference',allocation=list(optimum),
                expected_loss=None,realised_unmet=realised_shortfall(optimum,demands,2),total_requests=sum(demands)))
    for row in rows:
        assert sum(row['allocation'])==6
        lower=next(x['realised_unmet'] for x in rows if x['block']==row['block'] and x['replica']==row['replica'] and x['policy']=='perfect_demand_reference')
        assert row['realised_unmet']>=lower
    summaries=[]
    for name in variants.keys()|{'perfect_demand_reference'}:
        values=[x['realised_unmet'] for x in rows if x['policy']==name]
        summaries.append(dict(policy=name,mean_unmet=statistics.mean(values),scenario_replicas=len(values)))
    effects=[]
    for block in lock['block_seeds']:
        means={name:statistics.mean(x['realised_unmet'] for x in rows if x['block']==block and x['policy']==name) for name in variants}
        effects.append(dict(block=block,prob_minus_hard_posterior=means['probabilistic']-means['hard_posterior'],
            prob_minus_hard_observed=means['probabilistic']-means['hard_observed']))
    (out/'scenarios.json').write_text(json.dumps(scenarios,indent=2))
    (out/'results.json').write_text(json.dumps(rows,indent=2))
    (out/'summary.json').write_text(json.dumps(dict(policies=sorted(summaries,key=lambda r:r['policy']),block_effects=effects),indent=2))
    print(json.dumps(dict(policies=summaries,block_effects=effects)))


if __name__=='__main__':main()
