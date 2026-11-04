"""Create local-only fixed-history features; see detector_protocol_v1.md."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,re,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
import numpy as np
OUT=ROOT/'output/detector_v1'

def features(pos):
    values=[];names=[]
    def put(name,v): names.append(name);values.append(float(v))
    raw=np.diff(pos,axis=0)*25
    for step in [1,5,10,20]:
        ix=np.arange(0,101-step,step)
        v=(pos[ix+step]-pos[ix])/(step/25)
        speed=np.linalg.norm(v,axis=1);side=np.abs(v[:,1])
        for name,a in [('speed',speed),('side',side)]:
            for stat,fn in [('mean',np.mean),('std',np.std),('q25',lambda a:np.quantile(a,.25)),
                            ('median',np.median),('q75',lambda a:np.quantile(a,.75))]:
                put(f's{step}_{name}_{stat}',fn(a))
        put(f's{step}_stop',np.mean(speed<.1))
        put(f's{step}_forward',np.mean(v[:,0]))
    length=np.linalg.norm(np.diff(pos,axis=0),axis=1).sum()
    put('straightness',np.linalg.norm(pos[-1]-pos[0])/max(length,1e-9))
    put('side_reversals',np.mean(raw[1:,1]*raw[:-1,1]<0))
    put('lateral_accel_std',np.std(np.diff(raw[:,1])*25))
    # Remove linear trend before spectral summaries of head lateral position.
    t=np.arange(len(pos));res=pos[:,1]-np.polyval(np.polyfit(t,pos[:,1],1),t)
    power=np.abs(np.fft.rfft(res))**2;freq=np.fft.rfftfreq(len(pos),1/25)
    for lo,hi in [(.25,1.),(1.,3.),(3.,8.)]:
        put(f'lateral_power_{lo}_{hi}',np.log1p(power[(freq>=lo)&(freq<hi)].sum()))
    return np.array(values),names,raw

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    old=json.loads((ROOT/'backups/backup_verification.json').read_text())
    new=json.loads((ROOT/'backups/probabilistic_reset_verification_20261103_224341.json').read_text())
    sources=[('project_before_research_reset_20261102_113200.zip',{k:v['sha256'] for k,v in old['files'].items()}),
             (new['archive'],{x['path']:x['sha256'] for x in new['files']})]
    raw={};provenance=[];meta=None
    for archive,hashes in sources:
        with zipfile.ZipFile(ROOT/'backups'/archive) as z:
            for n in z.namelist():
                if re.fullmatch(r'data/raw/sime2017/members/50[1-8]\.txt',n):
                    b=z.read(n);digest=hashlib.sha256(b).hexdigest();assert digest==hashes[n]
                    if Path(n).stem in raw:assert raw[Path(n).stem]==b
                    raw[Path(n).stem]=b;provenance.append(dict(archive=archive,member=n,sha256=digest))
            if meta is None:meta=json.loads(z.read('research/data_search_20261030/sime_metadata_prefix.txt'))['experiment']
    runs={str(r['run_name']):r for r in meta['run']}
    X=[];seq=[];rows=[];excluded=[];names=None
    for trial,b in sorted(raw.items()):
        text=b.decode('utf-8-sig');mapping={int(a):int(p) for a,p in re.findall(r'^#\s*(\d+)\|\s*(\d+)\s*$',text,re.M)}
        assert {p for p in mapping.values() if 34<=p<=40}==set(range(34,41))
        assert sum(34<=p<=40 for p in mapping.values())==7
        assert int(runs[trial]['parameter']['subjects_with_disability'])==7
        tracks=defaultdict(list)
        for l in text.splitlines():
            if not l.strip() or l.lstrip().startswith('#'):continue
            a=l.split();tracks[int(a[0])].append([int(a[1]),float(a[2]),float(a[3])])
        assert len(tracks)==runs[trial]['number_participants']
        for tid,pts in sorted(tracks.items()):
            a=np.asarray(sorted(pts));pid=mapping.get(tid,-1);y=int(34<=pid<=40)
            cross=np.flatnonzero((a[:-1,1]<-1)&(a[1:,1]>=-1))+1
            reason=None
            if not len(cross):reason='no observed forward x=-1 crossing'
            elif cross[0]<100:reason='less than four seconds recorded before trigger'
            else:
                k=cross[0];window=a[k-100:k+1]
                if not np.all(np.diff(window[:,0])==1):reason='gap in window'
            if reason:
                excluded.append(dict(trial=int(trial),track=tid,pid=pid,y=y,reason=reason));continue
            f,n,s=features(window[:,1:]);assert np.isfinite(f).all()
            if names is None:names=n
            assert n==names
            X.append(f);seq.append(s);rows.append(dict(trial=int(trial),track=tid,pid=pid,y=y))
    np.savez_compressed(OUT/'data_LOCAL_ONLY.npz',X=np.array(X),sequence=np.array(seq),
        trial=[r['trial'] for r in rows],track=[r['track'] for r in rows],pid=[r['pid'] for r in rows],y=[r['y'] for r in rows])
    (OUT/'data_audit.json').write_text(json.dumps(dict(rows=len(rows),positives=sum(r['y'] for r in rows),
        trials=sorted({r['trial'] for r in rows}),features=names,exclusions=excluded,
        sources=provenance,window_seconds=4,fps=25,trigger='first observed forward x=-1 crossing',
        code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2))
    print(json.dumps(dict(rows=len(rows),positives=sum(r['y'] for r in rows),excluded=len(excluded),features=len(names))))
if __name__=='__main__':main()
