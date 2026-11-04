# Empirical movement targets — 4 November 2026

`research/measure_empirical_movement.py` reads fourteen archived SiME trial files and official metadata, verifying their hashes before use. It saves original metadata geometry, input provenance and 28 descriptive plane/trial summaries under `output/empirical_movement_check_v1/`. No raw tracks are extracted or redistributed, and no simulator parameter is fitted.

The dated measurement lock precedes this extraction. For each person, interpolate the first forward crossing between adjacent frames at x=0 and x=2.4 m, using 25 Hz. Report crossing span, median successive headway and aggregate event flow `(crossings-1)/span`. Compute duration-weighted segment speed where segment midpoint x is between -3 and -1 m. These full-record diagnostics are not a reproduction of the paper's Voronoi/steady-state measurements, and they are not full-building evacuation time.

All tracks cross both planes in thirteen trials; trial 507 has one unobserved crossing at each. Missing outcomes remain missing. Full-record means may include start-up, late arrivals and variable visible cohorts. They are not independent frame samples.

Examples at x=2.4 m: reference trials 1501/1503/1505/1507 have aggregate flows about 1.239/1.387/1.568/1.698 people/s. Trial 501 has 0.911 people/s. Different crowd composition and width confound a causal comparison; these are target descriptions, not effect estimates.

Official archived metadata includes thin physical barriers as polygon holes, a 2.4 m restricted passage, an upstream approach corridor and widths varying by run. The current generic 80-agent room/turn fixtures are **not** this geometry. Do not compare their total clearance times with SiME crossing spans as if they were matched validation.

Before calibration: specify a verified coordinate transform, head-centre measurement mapping, compatible body-size assumptions, arrival/roster treatment and measurement windows. Use recorded arrivals only in an explicitly conditional replay; known future inlet schedules cannot validate blind forecasting. Reference trials can provide development targets, while wheelchair behaviours and current data-use terms need separate checks. All available trials are already exposed, so subsequent fit checks remain exploratory.

Documentation text was read from the verified older backup, including `data/raw/sime2017/documentation.txt`. Geometry is from `research/data_search_20261030/sime_metadata_prefix.txt`; its hash is in the extraction inputs manifest. Do not infer experimental type or participant labels from a run-number prefix or an ambiguously extracted PDF table alone.
