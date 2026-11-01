# Pre-calibration implementation note

1 November 2026. Before any development replay score or test acquisition.

The two-agent inlet contract test exposed a native insertion constraint using a preceding spatial-index state. Admission therefore requires centre separation at least 2r+v0*dt+0.005 m, reserving one maximum movement step in addition to the fixed separation margin. This is a numerical safety margin, not a tuned parameter. The failing test and fix were made before fitting. The protocol's 30 s inlet-delay limit, candidate grid, target and partitions are unchanged. Three contract tests now pass: contiguous crossing interpolation, analytic one-agent travel, and collision-free occupied-inlet admission with identity conservation.
