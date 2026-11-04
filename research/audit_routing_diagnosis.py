"""Read-only audit; masks unavailable checkpoints without rewriting raw runs."""
from pathlib import Path
import csv,json,hashlib

ROOT=Path(__file__).resolve().parents[1]


def main():
    audit=[]
    for folder,source in [('routing_diagnosis_v1','diagnose_crowd_routing.py'),('avm_diagnosis_v1','diagnose_avm.py')]:
        out=ROOT/'output'/folder
        lock=json.loads((out/'lock.json').read_text())
        assert hashlib.sha256((ROOT/'research'/source).read_bytes()).hexdigest()==lock['code_sha256']
        results=json.loads((out/'results.json').read_text())
        for result in results:
            stem=result['case']+'_'+result['routing']+'_'+str(result['strength'])+'_'+str(result['dt']).replace('.','_')
            with (out/(stem+'.csv')).open(newline='') as f:rows=list(csv.DictReader(f))
            times=[float(r['time']) for r in rows]
            available=10.0 in times
            current=sum(float(r['time'])==10 for r in rows)
            if available:
                assert current==result['checkpoint_occupants']
            audit.append(dict(folder=folder,case=result['case'],routing=result['routing'],strength=result['strength'],
                              dt=result['dt'],last_saved_observation_s=max(times) if times else None,
                              checkpoint_available=available,
                              usable_checkpoint_count=current if available else None,
                              note='Raw zero checkpoint is unavailable, not an empty scene' if not available else 'Observed checkpoint',
                              failures=result['failures']))
    target=ROOT/'output/routing_diagnosis_audit.json'
    target.write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps({'runs_audited':len(audit),'unavailable_checkpoints':sum(not x['checkpoint_available'] for x in audit)}))


if __name__=='__main__':main()
