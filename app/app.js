'use strict';
const $=id=>document.getElementById(id), data=window.CROWD_DEMO;
let playing=false,lastTick=0;
$('timeline').max=data.frames.length-1;
function current(){return data.frames[Number($('timeline').value)];}
function render(){
 const frame=current(),previous=data.frames[Math.max(0,Number($('timeline').value)-1)];
 const prior=Number($('prior').value)/100,error=Number($('error').value)/100,budget=Number($('budget').value);
 $('priorValue').value=Math.round(prior*100)+'%';$('errorValue').value=Math.round(error*100)+'%';$('budgetValue').value=budget;
 $('time').textContent=frame.time.toFixed(1)+' s';
 const groups=[[],[],[],[]],counts=[0,0,0,0],composition=[0,0,0,0],speeds=[[],[],[],[]];
 for(const [id,xy] of Object.entries(frame.positions)){
  const z=xy[0]<=-6?0:xy[0]<=0?1:xy[0]<=6?2:3,person=data.people[id];
  const p=CrowdPlanner.posterior(person.observation,prior,error),mode=$('policy').value;
  const membership=mode==='homogeneous'?prior:mode==='hard_observed'?person.observation:mode==='hard_posterior'?Number(p>0.5):p;
  counts[z]++;composition[z]+=membership;groups[z].push(.1+.3*membership);
  if(previous.positions[id]&&frame.time>previous.time){const old=previous.positions[id];speeds[z].push(Math.hypot(xy[0]-old[0],xy[1]-old[1])/(frame.time-previous.time));}
 }
 const decision=CrowdPlanner.plan(groups,budget,2),densities=counts.map((n,z)=>n/data.zoneAreas[z]);
 $('occupants').textContent=counts.reduce((a,b)=>a+b,0);$('density').textContent=Math.max(...densities).toFixed(2);$('unmet').textContent=decision.expected_loss.toFixed(2);
 $('zones').replaceChildren();
 counts.forEach((n,z)=>{const item=document.createElement('div');item.className='zone';
  const speed=speeds[z].length?(speeds[z].reduce((a,b)=>a+b,0)/speeds[z].length).toFixed(2)+' m/s':'unknown';
  item.innerHTML=`<div class="zone-head"><span>Zone ${z+1} · ${n} agents</span><span>${decision.allocation[z]} units</span></div><small>${densities[z].toFixed(2)} /m² · mean speed ${speed}</small><small>Estimated profile count ${composition[z].toFixed(2)}</small><div class="bar"><i style="width:${Math.min(100,100*composition[z]/Math.max(1,n))}%"></i></div>`;$('zones').append(item);});
 draw(frame,densities);
}
function draw(frame,densities){
 const canvas=$('map'),ratio=window.devicePixelRatio||1,w=canvas.clientWidth,h=canvas.clientHeight;canvas.width=w*ratio;canvas.height=h*ratio;
 const ctx=canvas.getContext('2d');ctx.scale(ratio,ratio);ctx.clearRect(0,0,w,h);
 const sx=(w-40)/24,sy=(h-42)/8,X=x=>20+(x+12)*sx,Y=y=>h-22-(y+4)*sy;
 const cuts=[-12,-6,0,6,12];
 for(let z=0;z<4;z++){ctx.fillStyle=`rgba(21,117,117,${.05+Math.min(.45,densities[z]*.2)})`;ctx.fillRect(X(cuts[z]),Y(4),(cuts[z+1]-cuts[z])*sx,8*sy);ctx.fillStyle='#2b5265';ctx.font='12px system-ui';ctx.fillText('Z'+(z+1),X(cuts[z])+(cuts[z+1]-cuts[z])*sx/2-7,18);}
 // Mask inaccessible neck regions, then draw physical boundary.
 ctx.fillStyle='#e0e6e8';ctx.fillRect(X(4),Y(4),2*sx,3.4*sy);ctx.fillRect(X(4),Y(-.6),2*sx,3.4*sy);
 ctx.strokeStyle='#577181';ctx.lineWidth=2;ctx.beginPath();const outline=[[-12,-4],[4,-4],[4,-.6],[6,-.6],[6,-4],[12,-4],[12,4],[6,4],[6,.6],[4,.6],[4,4],[-12,4]];outline.forEach(([x,y],i)=>i?ctx.lineTo(X(x),Y(y)):ctx.moveTo(X(x),Y(y)));ctx.closePath();ctx.stroke();
 ctx.strokeStyle='#228263';ctx.setLineDash([5,4]);ctx.beginPath();ctx.moveTo(X(10),Y(-4));ctx.lineTo(X(10),Y(4));ctx.stroke();ctx.setLineDash([]);
 for(const [id,[x,y]] of Object.entries(frame.positions)){ctx.fillStyle=$('truth').checked&&data.people[id].profile?'#b97b38':'#286f97';ctx.beginPath();ctx.ellipse(X(x),Y(y),.22*sx,.22*sy,0,0,Math.PI*2);ctx.fill();}
 ctx.fillStyle='#5b6d7c';ctx.font='11px system-ui';ctx.fillText('Synthetic replay · metres · dashed line = diagnostic exit plane',24,h-5);
}
function animate(now){if(playing&&now-lastTick>220){let t=Number($('timeline').value);if(t>=data.frames.length-1){playing=false;$('play').textContent='Play replay';}else{$('timeline').value=t+1;render();}lastTick=now;}requestAnimationFrame(animate);}
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'Pause replay':'Play replay';};
$('reset').onclick=()=>{playing=false;$('play').textContent='Play replay';$('timeline').value=0;render();};
for(const id of ['timeline','prior','error','budget','policy','truth'])$(id).addEventListener('input',render);
window.addEventListener('resize',render);render();requestAnimationFrame(animate);
