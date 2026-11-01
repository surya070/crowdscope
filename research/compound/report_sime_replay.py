"""Independent saved-output arithmetic plus clearly scoped replay report."""
from pathlib import Path
import json,math,csv,statistics,hashlib
R=Path(__file__).resolve().parents[2];O=R/'output/sime_replay_v2'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
freeze=json.loads((O/'selected_freeze.json').read_text())
assert all(sha(R/p)==h for p,h in freeze['files'].items())
def independently_extract(path):
 prev={};entry={};exit={}
 for line in path.read_text().splitlines():
  if not line or line.startswith('#'):continue
  row=list(map(float,line.split()));pid=int(row[0]);frame=int(row[1]);x,y=row[2:4]
  if pid in prev:
   f0,x0,y0=prev[pid]
   if frame==f0+1:
    for plane,store in [(-6,entry),(2.4,exit)]:
     if x0<plane<=x and pid not in store:
      q=(plane-x0)/(x-x0);store[pid]=((f0+q)/25,y0+q*(y-y0))
  prev[pid]=(frame,x,y)
 return entry,exit
def audit_result(result):
 if result['status']!='completed':return {'status':'not completed; preserved'}
 tid=result['trial'];entry,exit=independently_extract(R/'data/raw/sime2017/members'/f'{tid}.txt')
 observed={int(k):v for k,v in result['observed_crossings'].items()};pred={int(k):v for k,v in result['crossings'].items()}
 assert set(entry)==set(exit)==set(observed)==set(pred)
 assert all(abs(exit[i][0]-observed[i])<1e-9 for i in observed)
 assert all(abs(entry[e['id']][0]-e['t'])<1e-9 for e in result['arrivals'])
 err=[pred[i]-observed[i] for i in observed]
 calc={'crossing_mae_s':statistics.mean(abs(e) for e in err),'crossing_rmse_s':math.sqrt(statistics.mean(e*e for e in err)),'crossing_bias_s':statistics.mean(err),'observed_passage_s':max(observed.values())-min(observed.values()),'simulated_passage_s':max(pred.values())-min(pred.values()),'last_crossing_error_s':max(pred.values())-max(observed.values())}
 assert all(abs(v-result['metrics'][k])<1e-9 for k,v in calc.items())
 assert result['scheduled']==result['inserted']==result['removed']==len(observed)
 return {'status':'passed','actual_crossings_independently_reconstructed':True,'metrics_match':True,'identities_conserved':True,'source_sha256':sha(R/'data/raw/sime2017/members'/f'{tid}.txt')}
trace=json.loads((O/'calibration_trace.json').read_text());results=[];audits={};csvrows=[]
for tid in ['1501','1507']:
 p=O/f'selected_development_{tid}.json';r=json.loads(p.read_text());results.append(r);audits[tid]=audit_result(r)
 actual={int(k):v for k,v in r['observed_crossings'].items()};pred={int(k):v for k,v in r['crossings'].items()}
 for e in r['arrivals']:
  pid=e['id'];csvrows.append({'partition':'development','trial':tid,'track_id':pid,'observed_inlet_s':e['t'],'admitted_s':r['admissions'][str(pid)],'observed_downstream_s':actual[pid],'simulated_downstream_s':pred[pid],'crossing_error_s':pred[pid]-actual[pid]})
fine={}
for r in results:
 tid=r['trial'];p=O/f'development_fine_{tid}.json'
 if p.exists():
  f=json.loads(p.read_text());fine[tid]={'status':f['status']}
  if f['status']=='completed':
   audits['fine_'+tid]=audit_result(f)
   fine[tid].update(crossing_mae_s=f['metrics']['crossing_mae_s'],mae_difference_s=f['metrics']['crossing_mae_s']-r['metrics']['crossing_mae_s'],last_crossing_difference_s=max(f['crossings'].values())-max(r['crossings'].values()))
held=[]
held_fine={}
for tid in ['1503','1505']:
 p=O/f'held_out_{tid}.json'
 if p.exists():
  r=json.loads(p.read_text());held.append(r);audits['held_out_'+tid]=audit_result(r)
  if r['status']=='completed':
   actual={int(k):v for k,v in r['observed_crossings'].items()};pred={int(k):v for k,v in r['crossings'].items()}
   for e in r['arrivals']:
    pid=e['id'];csvrows.append({'partition':'held_out','trial':tid,'track_id':pid,'observed_inlet_s':e['t'],'admitted_s':r['admissions'][str(pid)],'observed_downstream_s':actual[pid],'simulated_downstream_s':pred[pid],'crossing_error_s':pred[pid]-actual[pid]})
   fp=O/f'held_out_fine_{tid}.json'
   if fp.exists():
    f=json.loads(fp.read_text());audits['held_out_fine_'+tid]=audit_result(f)
    held_fine[tid]={'status':f['status']}
    if f['status']=='completed':held_fine[tid].update(crossing_mae_s=f['metrics']['crossing_mae_s'],mae_difference_s=f['metrics']['crossing_mae_s']-r['metrics']['crossing_mae_s'],last_crossing_difference_s=max(f['crossings'].values())-max(r['crossings'].values()))
with (O/'individual_crossings.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=csvrows[0].keys());w.writeheader();w.writerows(csvrows)
summary={'status':'development replay complete; held-out evaluation pending' if len(held)<2 else 'development and held-out replay evaluated','development_trials':2,'development_track_trial_count':sum(r['scheduled'] for r in results),'candidate_count':len(trace),'eligible_candidates':sum(x['eligible'] for x in trace),'selected_parameters':freeze['selected']['params'],'development_mean_crossing_mae_s':statistics.mean(r['metrics']['crossing_mae_s'] for r in results),'development_free_flight_mae_s':statistics.mean(r['baseline_metrics']['crossing_mae_s'] for r in results),'held_out_completed_trials':sum(x['status']=='completed' for x in held),'held_out_not_yet_acquired':[tid for tid in ['1503','1505'] if not (R/'data/raw/sime2017/members'/f'{tid}.txt').exists()],'development_numerical_sensitivity':fine,'audits':audits,'frozen_sources_unchanged':True,'wall_footprint_warning_m':max(r['max_sampled_wall_penetration_m'] for r in results),'scope':'Observed-inflow-conditioned unassisted reference model with JuPedSim backend. Not validation of original compound assistance model or end-to-end evacuation forecasts.'}
if len(held)==2 and all(x['status']=='completed' for x in held):
 summary.update(held_out_track_trial_count=sum(r['scheduled'] for r in held),held_out_mean_crossing_mae_s=statistics.mean(r['metrics']['crossing_mae_s'] for r in held),held_out_free_flight_mae_s=statistics.mean(r['baseline_metrics']['crossing_mae_s'] for r in held),held_out_numerical_sensitivity=held_fine,held_out_trial_metrics={r['trial']:r['metrics'] for r in held},held_out_wall_footprint_warning_m=max(r['max_sampled_wall_penetration_m'] for r in held))
 summary['held_out_relative_mae_reduction']=1-summary['held_out_mean_crossing_mae_s']/summary['held_out_free_flight_mae_s']
(O/'report_summary.json').write_text(json.dumps(summary,indent=2))
lines=['# SiME revised reference replay','',
'**Development and preselected held-out reference replays completed. The results provide limited support for an unassisted, observed-inflow-driven module; the original rigid wheelchair-helper model remains empirically unvalidated.**' if len(held)==2 else '**Development replay completed; held-out evaluation pending.**','',
'## What changed','',
'The replay uses the installed JuPedSim 1.4.2 CollisionFreeSpeedModelV2, actual wall geometry, explicit observed inlet events at x=-6 m, collision-free delayed admission, and individual head-centre crossing measurements at x=2.4 m. The original source and synthetic A/M/F comparison are preserved. Every planned development candidate, including failed completion cases, is saved.','',
'The previous frame-0 overlap problem is handled through a different experimental boundary: people enter the model when they cross the upstream inlet, instead of pretending the full cohort is visible at frame 0. This conditions on real upstream arrival times, including future inlet events. It is therefore a module replay under measured inputs, not an end-to-end clearance forecast.','',
'## Development results','',
f"All {summary['development_track_trial_count']} person-trial records in trials 1501 and 1507 were admitted, crossed the downstream measurement plane and left the simulation, with no sampled inter-agent overlap. All measured source crossings and reported errors were independently reconstructed from the raw TXT records. Of {len(trace)} predeclared parameter combinations, {summary['eligible_candidates']} completed both development trials and were eligible for selection.",'',
f"Selected parameters: desired speed {summary['selected_parameters']['speed']:.1f} m/s, common radius {summary['selected_parameters']['radius']:.2f} m, time gap {summary['selected_parameters']['time_gap']:.1f} s. The equal-trial mean individual crossing-time error was {summary['development_mean_crossing_mae_s']:.3f} s, compared with {summary['development_free_flight_mae_s']:.3f} s for independent free flight under the same inlet inputs. These are calibration errors; they are not held-out accuracy estimates.",'']
for r in results:
 m=r['metrics'];lines.append(f"- Trial {r['trial']} ({r['scheduled']} people): crossing MAE {m['crossing_mae_s']:.3f} s; observed first-to-last passage {m['observed_passage_s']:.3f} s, simulated {m['simulated_passage_s']:.3f} s; last-crossing error {m['last_crossing_error_s']:+.3f} s; maximum inlet admission delay {r['admission_delay_max_s']:.3f} s.")
lines+=['',
f"The largest sampled nominal-body wall penetration was {summary['wall_footprint_warning_m']*100:.2f} cm despite native agent centres remaining inside geometry. This warning is retained: the calibrated circular body representation is not a strict full-footprint geometry guarantee. One inlet head-to-body conversion in trial 1507 shifted lateral position by approximately 3 cm; all conversions are logged. Do not describe completion as proof of realistic body mechanics or safety.",'',
'## Numerical sensitivity','']
for tid,f in fine.items():lines.append(f"- Trial {tid}: fine-step status {f['status']}; "+(f"MAE changed by {f['mae_difference_s']:+.3f} s and final crossing by {f['last_crossing_difference_s']:+.3f} s at dt=0.01 versus 0.02 s." if f['status']=='completed' else 'No complete sensitivity result.'))
if len(held)==2:
 lines+=['','## Frozen held-out evaluation','',f"The selected model was applied without retuning to trials 1503 and 1505 at widths 1.0 and 1.1 m. All {summary['held_out_track_trial_count']} tracked person-trial records had source inlet and downstream crossings, agreed with metadata counts, were admitted, crossed the simulated measurement plane and left the model. Source and parameter hashes still match the pre-test freeze. The equal-trial mean crossing MAE was **{summary['held_out_mean_crossing_mae_s']:.3f} s**, versus **{summary['held_out_free_flight_mae_s']:.3f} s** for free flight, a **{100*summary['held_out_relative_mae_reduction']:.1f}%** reduction against that simple reference. This is not a comparison against every established crowd model.",'']
 for r in held:
  m=r['metrics'];lines.append(f"- Trial {r['trial']} ({r['scheduled']} people): MAE {m['crossing_mae_s']:.3f} s, bias {m['crossing_bias_s']:+.3f} s; observed first-to-last passage {m['observed_passage_s']:.3f} s versus simulated {m['simulated_passage_s']:.3f} s; last crossing {m['last_crossing_error_s']:+.3f} s late.")
 lines+=['',f"The model generally overestimated crossing times. Maximum sampled nominal-body wall penetration on test trials was {summary['held_out_wall_footprint_warning_m']*100:.2f} cm; inter-agent overlap was zero at sampled checks. This limits physical fidelity despite successful accounting and centre containment.",'','### Held-out time-step sensitivity','']
 for tid,f in held_fine.items():lines.append(f"- Trial {tid}: fine-step status {f['status']}; "+(f"MAE changed by {f['mae_difference_s']:+.3f} s and final crossing by {f['last_crossing_difference_s']:+.3f} s at dt=0.01 versus 0.02 s." if f['status']=='completed' else 'No complete fine-step replay.'))
 if all(f['status']=='completed' for f in held_fine.values()):lines+=['',f"The fine-step equal-trial MAE was {statistics.mean(f['crossing_mae_s'] for f in held_fine.values()):.3f} s. Parameters were not retuned. Numerical convergence is not established, and the coarse result must not be reported as time-step independent."]
lines+=['','## Participant mapping','',
'Raw headers were linked to the official documentation to identify all seven wheelchair users in each of two previously inspected trials (14 track-to-PWD mappings). Device length/width and qualitative assistance descriptions are recorded without copying medical diagnoses. Assistant track identities and individual chronological-age mappings remain unknown. An assistance description is not an observed per-trial helper graph. The reference replay uses current metadata indicating zero disabled participants; a wheelchair/assistance extension is not silently inferred from it.','',
'The older documentation has a run-prefix table inconsistent with current metadata and headers. Current raw-file labels take precedence for run classification, while header PWD identities and documented device descriptions support role mapping.','',
'## Interpretation and remaining work','',
'These are held-out runs at intermediate widths, not proven independent participant groups. The observed inlet schedule includes future upstream arrivals, so these errors do not validate an end-to-end remaining-clearance predictor. Head-centre crossings do not measure full-body clearance or alarm-to-evacuation time. The evidence supports limited conditional reference-model transfer to two new runs while retaining body-geometry and numerical limitations. No universal acceptance tolerance, operational-safety certification, original A/M/F empirical ranking or wheelchair-assistance benefit is established.','',
'The earlier download approval timeouts were resolved following the user\'s explicit retry instruction. Both test files were obtained with ZIP CRC checks before evaluation; no test-driven parameter or source changes occurred. For further improvement, resolve helper identities and age mappings, use a defensible mobility-specific body representation, and establish stability on separate development data before any new test.','',
'## Files and sources','',
'- `selected_freeze.json`: selected settings and source hashes before test acquisition.',
'- `calibration_trace.json`: all 18 candidates, including failures.',
'- `individual_crossings.csv`: actual inlet, admission and actual/simulated downstream times.',
'- `participant_mapping.json`: verified wheelchair identities with missing helper/age fields explicit.',
'- `report_summary.json`: independently audited metrics and sensitivity.',
'- Dataset: https://doi.org/10.34735/ped.2017.1',
'- Official documentation: https://ped.fz-juelich.de/data/experiments/2017.06.10_Wermelskirchen_SiME/data/2017sime/2017sime_documentation.pdf',
'- Movement model: https://pedestriandynamics.org/models/collision_free_speed_model/']
(O/'report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
