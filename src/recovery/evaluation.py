"""Run/block aggregation; fixed-model uncertainty is descriptive only."""
from collections import defaultdict
import numpy as np


def run_metrics(rows,predictions,runs):
    values = defaultdict(list)
    for row,p in zip(rows,predictions):
        error = float(p-row["target"])
        values[row["run_id"]].append(error)
    output=[]
    for r in runs:
        e=np.array(values[r["run_id"]] or [0.0])
        output.append({"run_id":r["run_id"],"geometry":r["geometry"],"block_id":r["block_id"],"condition":r["condition"],
                       "mae":float(np.mean(abs(e))),"mse":float(np.mean(e*e)),"underprediction":float(np.mean(np.maximum(0,-e))),
                       "checkpoint_count":len(values[r["run_id"]])})
    return output


def blocks(metrics,key="mae"):
    acc=defaultdict(list)
    for r in metrics:
        acc[r["geometry"],r["block_id"]].append(r[key])
    return {k:float(np.mean(v)) for k,v in acc.items()}


def macro(values):
    by_geo=defaultdict(list)
    for (g,b),v in values.items():
        by_geo[g].append(v)
    return float(np.mean([np.mean(v) for v in by_geo.values()]))


def underprediction_p90(rows,predictions,runs):
    """Weighted inverse-CDF quantile with the same run/block/geometry hierarchy."""
    errors=defaultdict(list)
    for row,p in zip(rows,predictions):
        errors[row["run_id"]].append(max(0.0,float(row["target"]-p)))
    geometries={r["geometry"] for r in runs}
    block_counts={g:len({r["block_id"] for r in runs if r["geometry"]==g}) for g in geometries}
    condition_counts=defaultdict(int)
    for r in runs:condition_counts[r["block_id"]]+=1
    values,weights=[],[]
    for r in runs:
        e=errors[r["run_id"]] or [0.0]
        weight=1/(len(geometries)*block_counts[r["geometry"]]*condition_counts[r["block_id"]]*len(e))
        values.extend(e);weights.extend([weight]*len(e))
    order=np.argsort(values,kind="stable")
    cdf=np.cumsum(np.array(weights)[order]);cdf/=cdf[-1]
    return float(np.array(values)[order[min(np.searchsorted(cdf,.9,side="left"),len(order)-1)]])


def interval(reference,full,seed=2026102902,draws=10000):
    a,b=blocks(reference),blocks(full)
    if set(a)!=set(b):
        raise ValueError("Paired block mismatch")
    delta={k:a[k]-b[k] for k in a}
    by_geo=defaultdict(list)
    for (g,block),v in delta.items():
        by_geo[g].append(v)
    rng=np.random.default_rng(seed)
    samples=np.zeros(draws)
    for values in by_geo.values():
        values=np.array(values)
        samples+=rng.choice(values,size=(draws,len(values)),replace=True).mean(axis=1)/len(by_geo)
    return {"reduction_s":macro(delta),"conditional_interval_s":np.quantile(samples,[.025,.975]).tolist(),
            "block_count":len(delta),"refitting_in_bootstrap":False,"interpretation":"conditional descriptive; no fitting/selection or generator uncertainty"}
