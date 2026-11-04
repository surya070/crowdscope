"""Predeclared development stress suite; evaluation seeds remain sealed."""
from pathlib import Path
import csv,hashlib,json,math,random,statistics,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src.mobility_probability import posterior
from src.resource_planning import plan,request_probability,realised_shortfall,allocations


def configurations():
    base=dict(counts=[20]*4,true_prior=0.2,working_prior=0.2,true_error=0.2,working_error=0.2,
              true_rates=[0.1,0.4],working_rates=[0.1,0.4],budget=6,temperature=1.0)
    changes=[('base',{}),('unequal_zones',dict(counts=[40,24,12,4])),
             ('scarce',dict(budget=3)),('abundant',dict(budget=9)),
             ('perfect_observation',dict(true_error=0,working_error=0)),
             ('uninformative',dict(true_error=0.5,working_error=0.5)),
             ('prior_shift_low',dict(true_prior=0.05)),('prior_shift_high',dict(true_prior=0.5)),
             ('noise_misspecification',dict(true_error=0.3,working_error=0.1)),
             ('overconfident',dict(temperature=0.5)),('underconfident',dict(temperature=2.0)),
             ('equal_demand_control',dict(true_rates=[0.1,0.1],working_rates=[0.1,0.1])),
             ('demand_misspecification',dict(true_rates=[0.1,0.1])),
             ('high_demand_contrast',dict(true_rates=[0.05,0.6],working_rates=[0.05,0.6]))]
    return [dict(base,**change,name=name) for name,change in changes]


def distorted(p,temperature):
    if p in (0,1):return p
    return 1/(1+math.exp(-math.log(p/(1-p))/temperature))


def main():
    out=ROOT/'output/planning_stress_v1';out.mkdir(parents=True,exist_ok=True)
    if (out/'lock.json').exists():raise RuntimeError('Preserve the run; do not tune against saved outcomes')
    cases=configurations();seeds=list(range(410004,410020));replicas=10
    lock=dict(purpose='development stress suite, not confirmatory evidence',seeds=seeds,replicas=replicas,cases=cases,
              common_random_numbers='same class/noise/request uniform streams across cases; zone slot regrouping is explicit',
              primary_comparator_unchanged=True,selection='none; retain all cells and policies',
              hashes={n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['research/run_planning_stress.py','src/resource_planning.py','src/mobility_probability.py']})
    (out/'lock.json').write_text(json.dumps(lock,indent=2))
    records=[];scenarios=[];summary=[]
    for case in cases:
        cell=[]
        for seed in seeds:
            rng=random.Random(seed+10000);class_uniforms=[rng.random() for _ in range(80)]
            for replica in range(replicas):
                nr=random.Random(seed*100+replica+30000000);rr=random.Random(seed*100+replica+60000000)
                labels=[int(u<case['true_prior']) for u in class_uniforms]
                observations=[c^int(nr.random()<case['true_error']) for c in labels]
                requests=[int(rr.random()<case['true_rates'][c]) for c in labels]
                probs=[distorted(posterior(o,case['working_prior'],case['working_error']),case['temperature']) for o in observations]
                def groups(values):
                    result=[];start=0
                    for count in case['counts']:result.append(values[start:start+count]);start+=count
                    return result
                demand=[sum(g) for g in groups(requests)]
                variants=dict(homogeneous=[case['working_prior']]*80,hard_observed=observations,
                    hard_posterior=[int(p>0.5) for p in probs],probabilistic=probs,mean_demand=probs,known_class=labels)
                scenario_id=f"{case['name']}_{seed}_{replica}"
                scenarios.append(dict(id=scenario_id,case=case['name'],block=seed,replica=replica,
                    labels=labels,observations=observations,requests=requests,demands=demand,
                    probabilistic_brier=sum((p-c)**2 for p,c in zip(probs,labels))/80))
                for name,ps in variants.items():
                    q=[[request_probability(p,*case['working_rates']) for p in g] for g in groups(ps)]
                    decision=plan(q,case['budget'],2,mean_only=name=='mean_demand')
                    row=dict(scenario=scenario_id,case=case['name'],block=seed,replica=replica,policy=name,
                        allocation=list(decision['allocation']),realised_unmet=realised_shortfall(decision['allocation'],demand),
                        expected_loss=decision['expected_loss'])
                    records.append(row);cell.append(row)
                optimum=min(allocations(4,case['budget']),key=lambda a:(realised_shortfall(a,demand),a))
                row=dict(scenario=scenario_id,case=case['name'],block=seed,replica=replica,policy='perfect_demand_reference',
                    allocation=list(optimum),realised_unmet=realised_shortfall(optimum,demand),expected_loss=None)
                records.append(row);cell.append(row)
        means={name:statistics.mean(x['realised_unmet'] for x in cell if x['policy']==name)
               for name in list(variants)+['perfect_demand_reference']}
        effects=[]
        for seed in seeds:
            values={name:statistics.mean(x['realised_unmet'] for x in cell if x['block']==seed and x['policy']==name) for name in variants}
            effects.append(dict(block=seed,vs_hard_posterior=values['probabilistic']-values['hard_posterior'],
                               vs_hard_observed=values['probabilistic']-values['hard_observed']))
        row=dict(case=case['name'],means=means,block_effects=effects,
                 probabilistic_minus_hard_posterior=means['probabilistic']-means['hard_posterior'],
                 probabilistic_minus_hard_observed=means['probabilistic']-means['hard_observed'],
                 mean_brier=statistics.mean(s['probabilistic_brier'] for s in scenarios if s['case']==case['name']))
        summary.append(row);print(json.dumps({k:v for k,v in row.items() if k!='block_effects'}),flush=True)
    (out/'scenarios.json').write_text(json.dumps(scenarios))
    (out/'results.json').write_text(json.dumps(records))
    (out/'summary.json').write_text(json.dumps(summary,indent=2))


if __name__=='__main__':main()
