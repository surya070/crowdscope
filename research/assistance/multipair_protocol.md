# Multi-pair development checks

2 November 2026, before execution. Evaluate two controllers: generalized v2 threshold/wait rule and a continuous speed-coordination candidate. Same JuPedSim1.4.2 engine and native direct steering; no position correction. Both remain escort approximations, not physical pushing.

Continuous candidate client desired speed is assisted pace multiplied by clip((1.2-gap)/.3,0,1); helper pace multiplied by clip((gap-.62)/.23,0,1). This replaces discontinuous on/off control with bounded continuous desired-speed changes. Helper native time gap remains .3 s. Client pace caps are min(1.15×nominal,helper pace). These are development assumptions, not empirical calibrations.

Six fixtures: original single mixed queue; two serial pairs through 1 m and 1.2 m doors; staggered pairs merging at 1 m door; two pairs turning; two pairs with unequal client/helper paces. Record .02/.01/.005 s runs for every mode/case before choosing a practical step. Gate remains complete exits in60s, exact counts, finite positions, nominal circle overlap<=.001m, wall penetration<=.005m, active-pair distance within radii sum−.001m and1.4m, speed ceiling excess<=.02m/s, clearance spread<=max(.2s,1% finest-step clearance).

All cases and both candidates are development tests, not independent validation. Preserve results for both controllers. Do not select a simulator by whether linkage features improve predictions. Do not reduce the test suite or relax tolerances after failures. If either controller passes, repeat checks over a finer bracket and extra arrangements before a forecasting protocol freeze.
