"""Causal exploratory feature bundle; does not fit prediction models."""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,re,zipfile
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/data/forecast_bundle'
H=['count','mean_x','std_x','mean_y','std_y','mean_distance','max_distance','p90_distance','mean_speed','std_speed','p10_speed','p90_speed','stopped_fraction','mean_speed_change','mean_nearest_distance','past_exit_count','elapsed_s','bottleneck_width','corridor_width']
M=['wheelchair_count','wheelchair_fraction','wheelchair_mean_speed','wheelchair_max_distance','wheelchair_present']

def extract(tracks,frame,steps,width,corridor,wheelchair):
    # Only this function supplies observations; future outcomes are separate.
    cohort=sorted(t for t,p in tracks.items() if all(f in p for f in range(frame-50,frame+1)) and p[frame][0]<2.4)
    if not cohort:return cohort,None
    xy=np.array([tracks[t][frame] for t in cohort]);dist=2.4-xy[:,0]
    end=np.array([np.linalg.norm(np.array(tracks[t][frame])-tracks[t][frame-steps])/(steps/25) for t in cohort])
    # Two subwindows remain strictly inside each selected observation history.
    half=steps//2
    recent=np.array([np.linalg.norm(np.array(tracks[t][frame])-tracks[t][frame-half])/(half/25) for t in cohort])
    previous=np.array([np.linalg.norm(np.array(tracks[t][frame-half])-tracks[t][frame-steps])/((steps-half)/25) for t in cohort])
    # Nearest visible neighbours include people outside the selected target cohort.
    visible=np.array([p[frame] for p in tracks.values() if frame in p])
    nearest=[]
    for point in xy:
        d=np.sort(np.linalg.norm(visible-point,axis=1));nearest.append(d[1] if len(d)>1 else 0.)
    past_exits=0
    for p in tracks.values():
        past_exits+=any(f in p and f+1 in p and p[f][0]<2.4<=p[f+1][0] for f in range(frame-steps,frame))
    # Explicit named assembly avoids ambiguous x/y order.
    row=dict(count=len(cohort),mean_x=xy[:,0].mean(),std_x=xy[:,0].std(),mean_y=xy[:,1].mean(),std_y=xy[:,1].std(),mean_distance=dist.mean(),max_distance=dist.max(),p90_distance=np.quantile(dist,.9),mean_speed=end.mean(),std_speed=end.std(),p10_speed=np.quantile(end,.1),p90_speed=np.quantile(end,.9),stopped_fraction=np.mean(end<.1),mean_speed_change=np.mean(recent-previous),mean_nearest_distance=np.mean(nearest),past_exit_count=past_exits,elapsed_s=frame/25,bottleneck_width=width,corridor_width=corridor)
    mask=np.array([t in wheelchair for t in cohort]);n=int(mask.sum())
    row.update(wheelchair_count=n,wheelchair_fraction=n/len(cohort),wheelchair_mean_speed=float(end[mask].mean()) if n else 0.,wheelchair_max_distance=float(dist[mask].max()) if n else 0.,wheelchair_present=int(n>0))
    return cohort,{k:float(v) for k,v in row.items()}

def crossing_times(tracks):
    result={}
    for t,p in tracks.items():
        for f in sorted(p):
            if f+1 in p and p[f][0]<2.4<=p[f+1][0]:
                result[t]=(f+(2.4-p[f][0])/(p[f+1][0]-p[f][0]))/25;break
    return result

def main():
    OUT.mkdir(exist_ok=True);rows=[];audit=[];hashes={};checks=0
    with zipfile.ZipFile(next((ROOT/'backups').glob('*.zip'))) as z:
        meta=json.loads(z.read('research/data_search_20261030/sime_metadata_prefix.txt'))['experiment']
        runs={str(r['run_name']):r for r in meta['run']}
        primary=['501','502','503','504','505','506','508','1501','1503','1505','1507']
        for trial in primary:
            local=ROOT/f'data/raw/sime2017/members/{trial}.txt'
            raw=local.read_bytes() if local.exists() else z.read(f'data/raw/sime2017/members/{trial}.txt')
            hashes[trial]=hashlib.sha256(raw).hexdigest();text=raw.decode().replace('\r','')
            links={int(a):int(b) for a,b in re.findall(r'^#\s*(\d+)\|\s*(\d+)\s*$',text,re.M)}
            wc={t for t,p in links.items() if p in range(34,41)};tracks=defaultdict(dict)
            for line in text.splitlines():
                if not line.strip() or line.startswith('#'):continue
                a=line.split();t,f=int(a[0]),int(a[1]);assert f not in tracks[t]
                tracks[t][f]=(float(a[2]),float(a[3]))
            r=runs[trial];params=r['parameter']
            assert len(tracks)==r['number_participants']
            # Primary wheelchair runs map all seven documented disabled IDs;
            # reference runs have no disabled participants per official metadata.
            assert len(wc)==int(params['subjects_with_disability'])
            crosses=crossing_times(tracks);assert len(crosses)==len(tracks)
            for time in [10,20,30]:
                cohorts=[]
                for steps in [10,25,50]:
                    cohort,features=extract(tracks,time*25,steps,float(params['bottleneck_width [m]']),float(params['corridor_width [m]']),wc)
                    prefix={t:{f:p for f,p in tr.items() if f<=time*25} for t,tr in tracks.items()}
                    assert (cohort,features)==extract(prefix,time*25,steps,float(params['bottleneck_width [m]']),float(params['corridor_width [m]']),wc);checks+=1
                    assert all(np.isfinite(v) for v in features.values())
                    cohorts.append(cohort)
                    rows.append(dict(trial=trial,time_s=time,history_s=steps/25,target_s=max(crosses[t] for t in cohort)-time,**features))
                assert cohorts[0]==cohorts[1]==cohorts[2]
            audit.append(dict(trial=trial,role='exposed development',count=len(tracks),wheelchair_count=len(wc),width=float(params['bottleneck_width [m]'])))
    with (OUT/'features.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    folds=[]
    for width in [.9,1.,1.1,1.2]:
        evaluation=[r['trial'] for r in audit if r['width']==width]
        training=[r['trial'] for r in audit if r['width']!=width]
        assert not set(training)&set(evaluation)
        inner=[]
        for valwidth in sorted({r['width'] for r in audit if r['trial'] in training}):
            val=[r['trial'] for r in audit if r['trial'] in training and r['width']==valwidth]
            inner.append({'validation_width':valwidth,'validation_trials':val,'training_trials':[t for t in training if t not in val]})
        folds.append(dict(evaluation_width=width,training_trials=training,evaluation_trials=evaluation,inner_folds=inner))
    manifest=dict(status='exploratory extraction/split specification; not confirmatory preregistration',date='2026-11-02',target='remaining passage of currently observed eligible cohort',H=H,M_additions=M,non_features=['trial','time_s','history_s','target_s'],folds=folds,trials=audit,source_sha256=hashes,code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),features_sha256=hashlib.sha256((OUT/'features.csv').read_bytes()).hexdigest(),rows=len(rows),queries=len(rows)//3,prefix_invariance_checks=checks,fitted=False,unseen_person_claim=False)
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps({'rows':len(rows),'queries':len(rows)//3,'trials':len(audit),'prefix_checks':checks,'H_features':len(H),'M_additions':len(M),'folds':[(f['evaluation_width'],len(f['evaluation_trials'])) for f in folds]},indent=2))
if __name__=='__main__':main()
