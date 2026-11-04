# Exploratory SiME wheelchair movement comparison — 5 November 2026

## Label audit and correction

The blanket statement that all unmarked tracks must remain unknown was too
conservative for a restricted, audited cohort. Archived official documentation
section 3.3 (page 9) says that PWD track IDs are commented in trajectory headers.
Pages 5 and 7–8 document the wheelchair registry, IDs 34–40. Current archived
per-run metadata declares seven participants with disabilities in each trial
501–508. All seven distinct wheelchair IDs are mapped to present tracks in each
file, and total track counts equal metadata counts in all eight trials.

Under the explicit assumption that the declared roster and header annotations
are complete, the complement can be used as non-wheelchair controls in these
eight trials. This conclusion does not transfer to every SiME trial or imply
that all controls are young, healthy, independent, or individually identifiable.
Historical PDF naming/tables differ from current metadata; use current run
metadata plus actual headers, not a guessed filename-to-table mapping.

There are 56 wheelchair person-trial observations of seven repeated people and
656 control person-trial tracks. These are not 712 independent participants.
No previously frozen audit, protocol, planning result, or paper was overwritten.

## Analysis

Script: `research/explore_wheelchair_patterns.py`. It reads two verified backup
ZIPs without extracting raw trajectories and verifies input SHA-256 values.
Raw labels and track features remain local; aggregate summaries can be reviewed.

Regions (x coordinate, metres): approach [-3,-1), bottleneck [0,2.4), departure
[2.4,4). Non-overlapping 0.4-second endpoint-displacement windows estimate planar
velocity. Both endpoints must be inside the same region. Track summaries require
at least 1.2 seconds of eligible windows and at least two windows. Speed, stopped
fraction (<0.1 m/s), speed IQR and absolute lateral velocity are calculated. Group
medians/IQRs weight eligible person-trial tracks equally, not individual frames.
The tracked points are head-centre projections, not wheelchair footprints.

A rough context control divides each region into 2-second time bins and compares
speed with other control windows in that bin, requiring at least three control
tracks. This does not constitute density matching or causal adjustment.

## Findings

Approach median track speed is 0.243 m/s for wheelchair tracks and 0.285 m/s for
controls. Wheelchair median speed is lower in six of eight trials; distributions
overlap substantially. In the bottleneck, corresponding medians are 0.804 and
0.777 m/s; ordering reverses between trials. Slow speed is not a reliable label.

The strongest explored feature is lower absolute lateral velocity: approach
medians 0.024 versus 0.121 m/s, and bottleneck medians 0.035 versus 0.109 m/s.
For randomly paired eligible wheelchair/control person-trial summaries, the
wheelchair lateral value is smaller in about 94.4% of approach pairs and 96.4%
of bottleneck pairs (ties half weighted). These are pooled descriptive rankings,
not held-out recognition accuracy and not independent-participant AUC estimates.

Window sensitivity: at 0.2, 0.4, 0.8 and 1.2 seconds, the corresponding approach
ranking probabilities are 95.8%, 94.4%, 94.7% and 89.2%; bottleneck values are
97.5%, 96.4%, 82.3% and 66.0%. The bottleneck signal weakens substantially with
longer windows. Walking head sway, smoother wheelchair motion, assisted movement,
measurement processing, and geometry may all contribute. This is a promising
feature to investigate, not proof of its physical cause or transportability.

Stop fraction and speed variability overlap. Departing people turn laterally,
so lateral velocity there describes route choice as well as movement style.
Eligibility varies by region; trial507 has one previously documented missing
crossing and only six eligible wheelchair tracks inside the bottleneck.

## Implications

There is sufficient evidence to justify a separate exploratory recogniser study
on this audited cohort. A defensible evaluation must hold out wheelchair people
and entire trials, account for controls with unknown repeated identities, compare
speed-only with lateral/temporal features, use past-only fixed observation
windows, and check tracking/smoothing sensitivity. Full-passage features used
here cannot be presented as a live early detector. All data were already exposed
in development; a newly declared split cannot become a pristine external test.
No children/older-adult detector or assistance-demand labels follow from this.

This analysis does not change the submitted framework results or the private
GitHub repository. Adding it to the paper requires a separately evaluated model,
updated claims and a clearly labelled exploratory result section.

## Sources

- Local verified backup: `project_before_research_reset_20261102_113200.zip`,
  `data/raw/sime2017/documentation_ranges/page_05.txt`, `page_07.txt`,
  `page_08.txt`, `page_09.txt`, actual 501–508 headers, and archived official
  run metadata. Second backup supplies additional trials; hashes in summary.
- Dataset DOI: https://doi.org/10.34735/ped.2017.1 (live landing access failed).
- Primary paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC9395390/ describes
  heterogeneous groups, head-projection tracking and speed adaptation by nearby
  non-disabled pedestrians. Paper participant numbering is not guessed to equal
  the archive PWD IDs.
