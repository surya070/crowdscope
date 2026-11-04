(()=>{'use strict';
const $=id=>document.getElementById(id),data=window.CROWD_FRAMEWORK_DATA;
if(!data){
 const results=window.CROWD_FRAMEWORK_RESULTS;
 if(!results){$('main').innerHTML='<div class="error"><h2>Research result package is missing</h2><p>See the framework guide for rebuilding the local demonstration.</p></div>';return;}
 const c=results.calibration.crossed_person_trial,s=results.summary;
 $('main').innerHTML=`<div class="intro"><div><h2>Calibrated crowd-analysis framework</h2><p class="muted">Aggregate results are included in this checkout. Recorded participant trajectories and fitted recognition weights remain local.</p></div><span class="label">Aggregate evidence view</span></div><div class="flow"><span>Trajectories + geometry</span><span>Past-only movement detector</span><span>Calibrated probabilities</span><span>Zone composition</span><span>Configured resource planning</span></div><div class="bottom"><section class="panel"><h3>Person + trial held out</h3><div class="result">${c.raw.Brier.toFixed(4)} → ${c.calibrated.Brier.toFixed(4)}</div><p>Raw to calibrated Brier loss. AP ${c.calibrated.AP.toFixed(3)}; precision ${(100*c.calibrated.precision).toFixed(1)}%, recall ${(100*c.calibrated.recall).toFixed(1)}% at the preset threshold.</p><p class="muted">Seven repeated wheelchair participants; unknown repeat controls remain. This is exploratory evaluation, not general demographic recognition.</p></section><section class="panel"><h3>Separate whole-trial replay</h3><div class="result">${s.count_errors_nonempty.prior.MAE.toFixed(3)} → ${s.count_errors_nonempty.calibrated.MAE.toFixed(3)}</div><p>Prior-only to calibrated count MAE (people per nonempty zone). Recording trials are excluded; participants may repeat.</p><p>Default hypothetical resource-planning loss did not improve.</p></section></div><section class="panel" style="margin-top:20px"><h3>Using the framework</h3><p>Define walkable analysis zones; supply time-stamped trajectories in metres and seconds; inspect density, motion, probability coverage and expected composition; then configure a decision module and its service assumptions.</p><p>The full recorded replay requires the locally generated <code>framework_data_LOCAL_ONLY.js</code>. The detector runs at a validated four-second crossing window; missing evidence retains a prior. See <code>docs/calibrated_framework.md</code> and the research scripts for the streaming API and authorised-data rebuild steps.</p><a href="index.html">Open the self-contained synthetic planning demonstration →</a></section>`;
 return;
}
let trial=data.trials[0],index=40,timer=null;
for(const t of data.trials){const o=document.createElement('option');o.value=t.trial;o.textContent=`Trial ${t.trial} · ${t.width_m.toFixed(1)} m bottleneck`;$('trial').append(o);}
const cp=data.calibration.crossed_person_trial;$('brier').textContent=`${cp.raw.Brier.toFixed(4)} → ${cp.calibrated.Brier.toFixed(4)}`;
const summary=data.summary;$('mae').textContent=`${summary.count_errors_nonempty.prior.MAE.toFixed(3)} → ${summary.count_errors_nonempty.calibrated.MAE.toFixed(3)}`;
$('planningfinding').textContent='Default planning loss did not improve with calibrated input. Better composition estimates do not necessarily change or improve an allocation.';
function stop(){clearInterval(timer);timer=null;$('play').textContent='Play replay';}
function selected(p){const mode=$('policy').value;return mode==='prior'?trial.prior:mode==='raw'?p.raw_detector_score:mode==='hard'?Number(p.wheelchair_probability>=.5):p.wheelchair_probability;}
function countInterval(ps){const pmf=CrowdPlanner.distribution(ps);let s=0,lo=0,hi=pmf.length-1,found=false;for(let k=0;k<pmf.length;k++){s+=pmf[k];if(!found&&s>=.05-1e-12){lo=k;found=true;}if(s>=.95-1e-12){hi=k;break;}}return[lo,hi];}
function render(){
 index=Math.min(index,trial.frames.length-1);const f=trial.frames[index],ps=f.occupants.map(selected),r0=+$('r0').value/100,r1=+$('r1').value/100;
 const budget=+$('budget').value,capacity=+$('capacity').value,groups=f.zones.map(z=>f.occupants.filter(p=>p.zone===z.zone).map(p=>r0+(r1-r0)*selected(p))),decision=CrowdPlanner.plan(groups,budget,capacity);
 $('time').textContent=`${f.time_s.toFixed(0)} s`;$('timeline').max=trial.frames.length-1;$('timeline').value=index;
 $('occupants').textContent=f.occupants.length;$('density').textContent=Math.max(...f.zones.map(z=>z.density_people_m2)).toFixed(2);
 const expected=ps.reduce((a,b)=>a+b,0),ci=countInterval(ps);$('expected').textContent=expected.toFixed(2);$('coverage').textContent=`${(100*f.detector_coverage).toFixed(0)}%`;
 $('countnote').textContent=`Working 90% count interval: ${ci[0]}–${ci[1]} people. Composition mode: ${$('policy').selectedOptions[0].textContent}.`;
 $('budgetout').textContent=budget;$('capacityout').textContent=capacity;$('r0out').textContent=$('r0').value+'%';$('r1out').textContent=$('r1').value+'%';$('unmet').textContent=decision.expected_loss.toFixed(3);
 $('zones').innerHTML=f.zones.map((z,i)=>{const p=f.occupants.filter(p=>p.zone===z.zone),n=p.reduce((s,p)=>s+selected(p),0);return `<div class="zone"><b><span>Zone ${i+1}</span><span>${decision.allocation[i]} units</span></b><small>${z.count} people · ${z.density_people_m2.toFixed(2)} /m² · mean speed ${z.mean_speed_m_s===null?'unavailable':z.mean_speed_m_s.toFixed(2)+' m/s'}</small><div class="bar"><i style="width:${Math.min(100,z.density_people_m2/3*100)}%"></i></div><small>Expected wheelchair-associated count: ${n.toFixed(2)} · ${z.detected_count}/${z.count} detected</small></div>`;}).join('');
 const people=[...f.occupants].sort((a,b)=>Number(a.probability_source==='training_prior')-Number(b.probability_source==='training_prior')||Math.abs(a.wheelchair_probability-.5)-Math.abs(b.wheelchair_probability-.5)).slice(0,8);
 $('people').innerHTML=people.map(p=>`<tr><td>${p.person_id}</td><td>${p.zone+1}</td><td>${(p.wheelchair_probability*100).toFixed(1)}%</td><td>${p.probability_source==='training_prior'?'Prior only':'Calibrated detector'}</td></tr>`).join('');
 draw(f);
}
function draw(f){const c=$('map'),r=c.getBoundingClientRect(),dpr=devicePixelRatio||1;c.width=r.width*dpr;c.height=r.height*dpr;const ctx=c.getContext('2d');ctx.scale(dpr,dpr);const w=r.width,h=r.height;
 const sx=x=>35+(x+6)/8.4*(w-65),sy=y=>h/2-y/3.8*(h-55),cuts=[-6,-3,-1,0,2.4];ctx.clearRect(0,0,w,h);
 f.zones.forEach((z,i)=>{const half=i===3?trial.width_m/2:1.65;ctx.fillStyle=`rgba(18,110,112,${.04+Math.min(.46,z.density_people_m2*.15)})`;ctx.fillRect(sx(cuts[i]),sy(half),sx(cuts[i+1])-sx(cuts[i]),sy(-half)-sy(half));ctx.strokeStyle='#ccdadd';ctx.strokeRect(sx(cuts[i]),sy(half),sx(cuts[i+1])-sx(cuts[i]),sy(-half)-sy(half));ctx.fillStyle='#3c5c6b';ctx.font='12px system-ui';ctx.fillText(`Zone ${i+1}`,sx(cuts[i])+8,21);});
 ctx.setLineDash([5,4]);ctx.strokeStyle='#a87031';ctx.beginPath();ctx.moveTo(sx(-1),sy(1.65));ctx.lineTo(sx(-1),sy(-1.65));ctx.stroke();ctx.setLineDash([]);
 f.occupants.forEach(p=>{const detected=p.probability_source==='calibrated_detector',prob=p.wheelchair_probability;ctx.beginPath();ctx.fillStyle=detected?'#216f78':'#8b98a2';ctx.arc(sx(p.x),sy(p.y),detected?3.3:2.8,0,2*Math.PI);ctx.fill();if(detected){ctx.beginPath();ctx.strokeStyle=`rgba(18,110,112,${.3+.7*prob})`;ctx.lineWidth=1.5;ctx.arc(sx(p.x),sy(p.y),4+5*prob,0,2*Math.PI);ctx.stroke();}});
 ctx.fillStyle='#627583';ctx.font='11px system-ui';ctx.fillText('−6 m',sx(-6),h-10);ctx.fillText('Detection line −1 m',sx(-1)-60,h-10);ctx.fillText('2.4 m',sx(2.4)-25,h-10);
}
$('trial').onchange=()=>{stop();trial=data.trials.find(t=>t.trial===+$('trial').value);index=Math.min(40,trial.frames.length-1);render();};
$('timeline').oninput=()=>{stop();index=+$('timeline').value;render();};$('reset').onclick=()=>{stop();index=0;render();};
function play(){timer=setInterval(()=>{if(index>=trial.frames.length-1){stop();return;}index++;render();},+$('speed').value);$('play').textContent='Pause replay';}
$('play').onclick=()=>timer?stop():play();$('speed').onchange=()=>{if(timer){stop();play();}};
for(const id of ['policy','budget','capacity','r0','r1'])$(id).oninput=render;
window.addEventListener('resize',render);render();
})();
