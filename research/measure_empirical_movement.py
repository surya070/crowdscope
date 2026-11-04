"""Descriptive SiME diagnostics from verified archives; no parameter fitting."""
from pathlib import Path
from collections import defaultdict
import csv,hashlib,json,math,statistics,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.deps/recovery-r1'))
from shapely import wkt


def main():
    out=ROOT/'output/empirical_movement_check_v1';out.mkdir(parents=True,exist_ok=True)
    if (out/'lock.json').exists():raise RuntimeError('Preserve previous measurements')
    old=json.loads((ROOT/'backups/backup_verification.json').read_text())
    new=json.loads((ROOT/'backups/probabilistic_reset_verification_20261103_224341.json').read_text())
    sources=[('project_before_research_reset_20261102_113200.zip',{k:v['sha256'] for k,v in old['files'].items()}),
             (new['archive'],{x['path']:x['sha256'] for x in new['files']})]
    lock=dict(purpose='exposed-data descriptive diagnostics; no calibration or validation claim',
        planes_m=[0,2.4],crossing='first forward head-centre crossing interpolated between adjacent frames',
        approach_band_x_m=[-3,-1],speed='duration weighted adjacent-frame segment speed, midpoint in x band; no y filter',
        fps=25,code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'lock.json').write_text(json.dumps(lock,indent=2))
    data={};inputs=[];meta=None
    for archive,hashes in sources:
        with zipfile.ZipFile(ROOT/'backups'/archive) as z:
            names=[n for n in z.namelist() if n.startswith('data/raw/sime2017/members/') and n.endswith('.txt')]
            if archive==sources[0][0]:names.append('research/data_search_20261030/sime_metadata_prefix.txt')
            for name in names:
                b=z.read(name);digest=hashlib.sha256(b).hexdigest();assert digest==hashes[name]
                inputs.append(dict(archive=archive,member=name,sha256=digest))
                if name.endswith('sime_metadata_prefix.txt'):meta=json.loads(b)['experiment']
                else:data[Path(name).stem]=b
    runs={str(x['run_name']):x for x in meta['run']}
    results=[];geometries={}
    for trial,b in sorted(data.items(),key=lambda x:int(x[0])):
        tracks=defaultdict(list)
        for line in b.decode('utf-8-sig').splitlines():
            if not line.strip() or line.lstrip().startswith('#'):continue
            a=line.split();tracks[int(a[0])].append((int(a[1]),float(a[2]),float(a[3])))
        distance=duration=0;cross={0:[],2.4:[]}
        for track in tracks.values():
            track.sort();found=set()
            for a,b in zip(track,track[1:]):
                if b[0]-a[0]!=1:continue
                if -3<=(a[1]+b[1])/2<=-1:
                    distance+=math.hypot(b[1]-a[1],b[2]-a[2]);duration+=1/25
                for plane in cross:
                    if plane not in found and a[1]<plane<=b[1]:
                        cross[plane].append((a[0]+(plane-a[1])/(b[1]-a[1]))/25);found.add(plane)
        geometry=wkt.loads(runs[trial]['wkt_geometry']);assert geometry.is_valid
        geometries[trial]=dict(wkt=geometry.wkt,source='archived official run metadata',parameters=runs[trial]['parameter'])
        for plane,times in cross.items():
            times.sort();headways=[b-a for a,b in zip(times,times[1:])]
            span=times[-1]-times[0] if len(times)>1 else None
            results.append(dict(trial=trial,tracks=len(tracks),plane_m=plane,observed_crossings=len(times),
                missing_crossings=len(tracks)-len(times),crossing_span_s=span,
                aggregate_flow_people_s=(len(times)-1)/span if span else None,
                median_headway_s=statistics.median(headways) if headways else None,
                approach_band_mean_speed_m_s=distance/duration if duration else None,
                note='all-record descriptive statistic, not published steady-state convention'))
    with (out/'metrics.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(results[0]));writer.writeheader();writer.writerows(results)
    (out/'geometry.json').write_text(json.dumps(geometries,indent=2))
    (out/'inputs.json').write_text(json.dumps(inputs,indent=2))
    print(json.dumps(dict(trials=len(data),measurements=len(results),models_fitted=0,
        incomplete=[dict(trial=x['trial'],plane=x['plane_m'],missing=x['missing_crossings']) for x in results if x['missing_crossings']])))


if __name__=='__main__':main()
