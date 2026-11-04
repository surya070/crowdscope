/* Exact synthetic demand planner; mirrors the audited Python mathematics. */
(function(root){
 'use strict';
 function posterior(bit,prior,error){
  if(![0,1].includes(bit)||![prior,error].every(v=>Number.isFinite(v)&&v>=0&&v<=1))throw Error('Invalid probability input');
  const a=prior*(bit?1-error:error), b=(1-prior)*(bit?error:1-error);
  if(a+b===0)throw Error('Impossible observation');return a/(a+b);
 }
 function distribution(ps){let pmf=[1];for(const p of ps){if(!Number.isFinite(p)||p<0||p>1)throw Error('Invalid probability');const next=Array(pmf.length+1).fill(0);pmf.forEach((v,k)=>{next[k]+=v*(1-p);next[k+1]+=v*p;});pmf=next;}return pmf;}
 function plan(groups,budget=6,capacity=2){
  if(!Number.isInteger(budget)||budget<0||!Number.isInteger(capacity)||capacity<1||!groups.length)throw Error('Invalid budget/capacity');
  const costs=groups.map(ps=>{const pmf=distribution(ps);return Array.from({length:budget+1},(_,a)=>pmf.reduce((s,p,k)=>s+p*Math.max(0,k-capacity*a),0));});
  let best=null,loss=Infinity;
  function search(prefix,left){if(prefix.length===groups.length-1){const a=prefix.concat(left);const value=a.reduce((s,v,z)=>s+costs[z][v],0);if(value<loss-1e-12){best=a;loss=value;}return;}for(let n=0;n<=left;n++)search(prefix.concat(n),left-n);}
  search([],budget);return {allocation:best,expected_loss:loss};
 }
 const api={posterior,distribution,plan};root.CrowdPlanner=api;if(typeof module!=='undefined')module.exports=api;
})(globalThis);
