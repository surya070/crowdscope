"""Frozen small-queue generator and prefix-only observation features."""
import copy
import numpy as np
from shapely.geometry import box
from src.recovery.common import ROOT,read,sha
from .movement import Member,Unit,run


def design():
    frozen=read(ROOT/"research/compound/prediction_freeze_v1.json")
    for p,h in frozen["files"].items():
        if sha(ROOT/p)!=h:raise ValueError("Frozen prediction design changed: "+p)
    validation=read(ROOT/"research/compound/movement_validation.json")
    if sha(ROOT/"research/compound/movement_validation.json")!=frozen["prior_feasibility_validation_sha256"] or validation["status"]!="passed":
        raise ValueError("Prior movement validation mismatch")
    for p,h in validation["source_hashes"].items():
        if sha(ROOT/p)!=h:raise ValueError("Verified movement source changed: "+p)
    return read(ROOT/"research/compound/prediction_config_v1.json"),read(ROOT/"research/compound/prediction_manifest_v1.json")


def scenario(cfg,row):
    rng=np.random.default_rng(row["seeds"]["capability"])
    k=1 if row["n"]==8 else 2
    counts={"adult":2*k+2,"child":k,"older":2,"wheelchair":k}
    people=[]
    for profile,n in counts.items():
        p=cfg["profiles"][profile]
        for _ in range(n):
            people.append({"id":len(people)+1,"profile":profile,"free_speed":float(rng.uniform(*p["speed"])),"radius":p["radius"]})
    by_id={p["id"]:p for p in people}
    ids=lambda kind:[p["id"] for p in people if p["profile"]==kind]
    adults=ids("adult")
    gain_rng=np.random.default_rng(row["seeds"]["gain"])
    low,high=(.7,1.4) if row["variant"]=="gain_stress" else (.85,1.2)
    reserved=[{"type":"assistance","adult":a,"dependent":d,"gain":float(low+(high-low)*gain_rng.random())}
              for a,d in zip(adults[:k],ids("wheelchair"))]
    reserved += [{"type":"family","adult":a,"dependent":d} for a,d in zip(adults[k:2*k],ids("child"))]
    used={i for e in reserved for i in [e["adult"],e["dependent"]]}
    blocks=[{"type":e["type"],"front":e["dependent"] if e["type"]=="assistance" else e["adult"],
             "back":e["adult"] if e["type"]=="assistance" else e["dependent"]} for e in reserved]
    blocks += [{"type":"single","front":p["id"]} for p in people if p["id"] not in used]
    perm=np.random.default_rng(row["seeds"]["placement"]).permutation(len(blocks))
    g=next(g for g in cfg["geometry"] if g["id"]==row["geometry"])
    y=g["width"]/2
    rear=None;rear_radius=None
    for index in perm:
        block=blocks[int(index)]
        front=block["front"]
        x=(10 if row["n"]==8 else 14) if rear is None else rear-rear_radius-.2-by_id[front]["radius"]
        by_id[front]["position"]=[float(x),y]
        back=block.get("back",front)
        if back!=front:by_id[back]["position"]=[float(x-.75),y]
        rear=by_id[back]["position"][0];rear_radius=by_id[back]["radius"]
    active_types={"independent":[],"family_only":["family"],"assistance_only":["assistance"],"family_and_assistance":["family","assistance"]}[row["condition"]]
    edges=[{key:e[key] for key in ["type","adult","dependent"]} for e in reserved if e["type"] in active_types]
    speeds={p["id"]:p["free_speed"] for p in people}
    coupled=set();units=[]
    endpoint=g["length"]+3
    for e in reserved:
        a,d=e["adult"],e["dependent"]
        if e["type"] not in active_types:continue
        if e["type"]=="family":
            speeds[a]=speeds[d]=min(speeds[a],speeds[d])
        else:
            supported=min(speeds[a],e["gain"]*speeds[d])
            x,cy=by_id[d]["position"]
            units.append(Unit(a,(Member(d,"wheelchair",by_id[d]["radius"],(0,0),max(by_id[d]["free_speed"],supported)),
                                 Member(a,"adult",by_id[a]["radius"],(-.75,0),by_id[a]["free_speed"])),
                              ((x,cy),(endpoint,cy)),supported,x,cy))
            coupled.update([a,d])
    for p in people:
        i=p["id"]
        if i in coupled:continue
        x,cy=p["position"]
        units.append(Unit(i,(Member(i,p["profile"],p["radius"],(0,0),p["free_speed"]),),
                          ((x,cy),(endpoint,cy)),speeds[i],x,cy))
    case={"name":row["run_id"],"area":box(0,0,g["length"]+4,g["width"]),"units":units,
          "exit_axis":0,"exit_plane":g["length"],"cap_s":cfg["horizon_s"],
          "family_links":[(e["adult"],e["dependent"]) for e in edges if e["type"]=="family"]}
    return case,people,edges,reserved,g


def simulate(cfg,row,dt=None):
    case,people,edges,reserved,g=scenario(cfg,row)
    result=run(case,cfg["dt_s"] if dt is None else dt,cfg["resolution"])
    result.update({"run":row,"people":people,"edges":edges,"private_reserved_edges":reserved,
                   "geometry":{"id":g["id"],"length_m":g["length"],"width_m":g["width"],"exit_width_m":g["width"]},
                   "capped_completion_s":result["completion_s"] if result["complete"] else cfg["horizon_s"]})
    return result


def observe(result,t,cfg):
    cutoff=round(t-cfg["observation_lag_s"],9)
    return {"t":t,"cutoff":cutoff,"roster":[{k:p[k] for k in ["id","profile","free_speed","radius"]} for p in result["people"]],
            "frames":[{"t":f["t"],"positions":copy.deepcopy(f["positions"])} for f in result["frames"] if f["t"]<=cutoff+1e-9],
            "exits":{i:v for i,v in result["exits"].items() if v<=cutoff+1e-9},
            "edges":copy.deepcopy(result["edges"]),"geometry":result["geometry"]}


def perturb(observation,mode,seed):
    o=copy.deepcopy(observation)
    if mode is None:return o,{"selected":0,"changed":0}
    rng=np.random.default_rng(seed)
    selected=[]
    for kind in ["family","assistance"]:
        candidates=[i for i,e in enumerate(o["edges"]) if e["type"]==kind]
        if candidates:selected.append(int(rng.choice(candidates)))
    if mode=="drop_one_each_type":
        o["edges"]=[e for i,e in enumerate(o["edges"]) if i not in selected]
        return o,{"selected":len(selected),"changed":len(selected)}
    if mode!="rewire_one_each_type":raise ValueError("Unknown corruption")
    used={e["adult"] for e in o["edges"]};changed=0
    for i in selected:
        edge=o["edges"][i]
        available=[p["id"] for p in o["roster"] if p["profile"]=="adult" and p["id"] not in used]
        if available:
            replacement=int(rng.choice(available))
            used.remove(edge["adult"]);edge["adult"]=replacement;used.add(replacement);changed+=1
    return o,{"selected":len(selected),"changed":changed}


def features(o,cfg):
    if len(o["exits"])==len(o["roster"]):return None
    frame=o["frames"][-1]
    if abs(frame["t"]-o["cutoff"])>1e-8:raise ValueError("Missing observation frame")
    previous=next(f for f in o["frames"] if abs(f["t"]-(o["cutoff"]-.2))<1e-8)["positions"]
    xy={int(i):np.asarray(v) for i,v in frame["positions"].items()}
    roster={p["id"]:p for p in o["roster"]}
    v={i:float(np.linalg.norm(p-previous[str(i)])/.2) for i,p in xy.items()}
    speed=list(v.values());g=o["geometry"];n=len(xy)
    distance={i:max(0,g["length_m"]-p[0]) for i,p in xy.items()}
    d=list(distance.values());nominal=[roster[i]["free_speed"] for i in xy]
    free_times=[max(0,g["length_m"]-p[0]+roster[i]["radius"])/roster[i]["free_speed"] for i,p in xy.items()]
    values=[n,n/(g["length_m"]*g["width_m"]),np.mean(speed),np.std(speed),np.quantile(speed,.1),
            np.mean(np.asarray(speed)<.3),np.mean(d),max(d),sum(x<=2 for x in d),
            sum(o["cutoff"]-1<t<=o["cutoff"] for t in o["exits"].values()),o["t"],g["length_m"],g["width_m"],g["exit_width_m"]]
    f=dict(zip(cfg["features"]["aggregate"],values))
    values=[sum(roster[i]["profile"]==kind for i in xy)/n for kind in ["child","older","wheelchair"]]
    values += [np.mean(nominal),np.std(nominal),np.quantile(nominal,.1),np.mean([roster[i]["radius"] for i in xy]),
               min(nominal),roster[min(xy,key=lambda i:xy[i][0])]["free_speed"],np.mean(free_times),max(free_times)]
    f.update(zip(cfg["features"]["mobility_added"],values))
    groups={"family":[],"assistance":[]}
    for e in o["edges"]:
        a,d=e["adult"],e["dependent"]
        if a in xy and d in xy:
            groups[e["type"]].append([np.linalg.norm(xy[a]-xy[d]),abs(v[a]-v[d]),roster[a]["free_speed"]-roster[d]["free_speed"],v[d]<.3])
    fa,ass=groups["family"],groups["assistance"]
    avg=lambda rows,k:np.mean([r[k] for r in rows]) if rows else 0
    values=[len(fa)/n,len(ass)/n,avg(fa,0),max([r[0] for r in fa],default=0),avg(fa,1),avg(ass,0),avg(ass,1),avg(ass,2),avg(ass,3)]
    f.update(zip(cfg["features"]["links_added"],values))
    f={k:float(v) for k,v in f.items()}
    if not np.isfinite(list(f.values())).all():raise ValueError("Nonfinite feature")
    return f


def records(result,cfg,mode=None):
    output=[]
    for t in cfg["checkpoints"]:
        o,_=perturb(observe(result,t,cfg),mode,result["run"]["seeds"]["corruption"])
        f=features(o,cfg)
        if f is None:continue
        row=result["run"]
        output.append({k:row[k] for k in ["run_id","block_id","geometry","partition","variant","condition"]}|
                      {"t":t,"target":max(0,result["capped_completion_s"]-t),"features":f})
    return output
