/* Cross-language fixture validation: node app/check_planner.cjs fixtures.json */
const fs=require('node:fs'),assert=require('node:assert/strict');
const planner=require('./planner.js');
const fixtures=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
for(const f of fixtures){const result=planner.plan(f.groups,f.budget,f.capacity);assert.deepEqual(result.allocation,f.expected.allocation);assert.ok(Math.abs(result.expected_loss-f.expected.expected_loss)<1e-9);}
assert.ok(Math.abs(planner.posterior(1,.2,.2)-.5)<1e-12);
assert.ok(Math.abs(planner.posterior(0,.2,.2)-1/17)<1e-12);
console.log(`Passed ${fixtures.length} Python/JavaScript allocation and expected-loss comparisons.`);
