# Figure 2 | Agents show similar observed benchmark performance in Galaxy and custom code

This figure asks whether running an analysis through Galaxy, rather than in custom code, changes how often the same four models reach the benchmark answer. It tests this on three benchmarks with different scoring contracts, as paired differences, and then asks why runs fail where the two conditions disagree. The answer frames the rest of the study: Galaxy's provenance and tool-use properties matter only if using Galaxy does not by itself cost accuracy.

## Fig. 2a | Do the four models score similarly in Galaxy and in custom code on each benchmark?
panel: fig2a

### Rationale
- **Data.** All 3,840 scored primary runs, scored as shown on the public results site: BixBench-Verified-50 (50 tasks; the original evaluator's acceptance, with bix-53-q2 and bix-43-q2 regraded, changing 27 runs), CompBioBench (100 tasks) and IWC (10 tasks, including host-read removal), each run by four models in both conditions with three replicates. Each point summarizes one model in one condition: 150, 300 or 30 runs.
- **Variables.** The y axis is each benchmark's own score: the share of runs accepted (BixBench-Verified-50), the share agreeing with the reconstructed answer key (CompBioBench), and mean agreement with curated workflow outputs on a 0–1 scale (IWC). Orange squares are custom code and blue circles Galaxy; small open dots are replicate means (one run of every task).
- **Analysis.** The estimator is the mean score over the model's runs in that condition. Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Descriptive only; the paired tests are in panel b.
- **Reading the plot.** A grey line joins the two conditions of one model, so its slope shows the direction of the difference. Vertical bars are 95% intervals. IWC has its own 0–1 axis, so heights are not comparable across facets.

### Conclusion
Yes, on two benchmarks. On BixBench-Verified-50 and CompBioBench, each model's two conditions differ by at most 2.0 points, and the intervals overlap widely (for example, GPT-5.5 on BixBench-Verified-50: 90.0% in custom code, 91.3% in Galaxy). On IWC, GPT-5.6 Sol and GPT-5.6 Luna sit near ceiling in both conditions (0.98 to 0.99). GPT-5.5 (0.88 vs 0.95) and DeepSeek V4 Pro (0.93 vs 1.00) score higher in Galaxy, but their custom-code intervals are wide (0.72 to 0.99; 0.83 to 1.00) and their replicate dots spread widely. This panel does not test the differences; panel b does.

## Fig. 2b | How large is the Galaxy minus custom-code difference for each model and for the four models pooled?
panel: fig2b

### Rationale
- **Data.** The same 3,840 runs, paired by task and model; the reliability estimand uses the 1,280 replicate sets (one task × model × condition, three runs). The grey note drops 94 runs that a scan of the traces found had reached benchmark answers.
- **Variables.** The x axis is Galaxy minus custom code in percentage points. The left column is the mean score (share accepted, or IWC agreement × 100). The right column is the share of replicate sets with all three runs correct (IWC at agreement ≥ 0.99). Rows are the four models and their pooled estimate, grouped by benchmark.
- **Analysis.** Estimates are differences of pooled means with 95% percentile cluster-bootstrap intervals (20,000 resamples). *P* values come from paired cluster sign-flip tests on each cluster's summed task-level differences (200,000 draws; exact for IWC). Holm adjustment is within three families: 12 per-model mean-score tests, 6 pooled tests (runs correct and all three correct, per benchmark) and 12 per-model all-three-correct tests. The pooled IWC agreement difference is unadjusted; no equivalence test was run.
- **Reading the plot.** Open circles are single models, filled diamonds the four models pooled, and horizontal lines 95% intervals. Points right of the zero line mean Galaxy scored higher.

### Conclusion
The differences are small, and no difference was significant after Holm adjustment (smallest adjusted *P* = 0.19, GPT-5.5 on IWC: +7.4 points, 0.4 to 20.1). Pooled mean-score differences were +0.5 points (−3.9 to 4.8; *P* = 0.88) on BixBench-Verified-50 and +0.3 (−1.8 to 2.5; *P* = 0.82) on CompBioBench; without the 94 exposed runs they were +0.6 and +0.2. The pooled IWC agreement difference, +3.6 points (0.6 to 7.4), has an exact *P* of 0.055; with ten tasks its interval is too narrow. The pooled intervals exclude Galaxy deficits larger than 3.9 and 1.8 points, but this does not establish equivalence.

## Fig. 2c | For the same task and model, do the two conditions get the same number of correct runs out of three?
panel: fig2c

### Rationale
- **Data.** All task–model pairs: 200 on BixBench-Verified-50 (50 tasks × 4 models), 400 on CompBioBench and 40 on IWC (10 tasks, including host-read removal). Each pair holds one replicate set per condition, scored as in panel a.
- **Variables.** Rows give the Galaxy set's correct runs (0–3) and columns the custom-code set's; each cell counts pairs. A run is correct when it was accepted or, for IWC, at agreement ≥ 0.99. The text under each matrix gives the total pairs and the pairs with the same count, more correct runs in Galaxy, or more in custom code.
- **Analysis.** Descriptive only: counts of pairs, with no test. The paired tests on these sets are in panel b.
- **Reading the plot.** Grey shading encodes pairs per cell on a log scale; white cells are empty. The outlined diagonal (bold counts) marks equal counts; cells above it are pairs in which Galaxy had more correct runs, and cells below it pairs in which custom code had more. The top-right cell holds pairs correct in all six runs.

### Conclusion
Usually, yes. Most pairs have the same count in both conditions: 170 of 200 on BixBench-Verified-50, 307 of 400 on CompBioBench and 32 of 40 on IWC, most of them correct in all six runs (152, 283 and 28). Discordant pairs split almost evenly on BixBench-Verified-50 (17 with Galaxy higher, 13 with custom code higher) and CompBioBench (47 vs 46), and lean toward Galaxy on IWC (6 vs 2). Some pairs failed every run in both conditions (14, 13 and 4). Equal counts mean equal replicate success, not identical answers or methods.

## Fig. 2d | What caused the incorrect BixBench-Verified-50 runs where the two conditions disagree, and where they agree?
panel: fig2d

### Rationale
- **Data.** The 151 BixBench-Verified-50 runs graded incorrect on the results site, each with a primary and optional secondary cause from an AI-assisted run-level audit of the traces; 4 bix-43-q2 runs made incorrect only by the site's regrade take the task-level audit's cause (benchmark specification or scoring). An independent AI second rater, blind to the audit, re-coded 45 runs sampled before the regrades (7 now graded correct); the box shows all 24 runs of task bix-45-q1.
- **Variables.** Pair types come from panel c: incorrect custom-code runs where Galaxy had more correct runs (17 pairs; 26 runs), incorrect Galaxy runs where custom code had more (13 pairs; 22 runs), and both conditions' incorrect runs in the 18 same-count pairs with any failure (48 runs each). Bars give each primary cause's share of the row; segment labels are run counts. The seven incorrect runs of the better condition in discordant pairs are left out of the bars.
- **Analysis.** Descriptive counts and shares; no test. The subtitle gives the second rater's raw agreement on the primary cause group and Cohen's κ.
- **Reading the plot.** Colour is the primary cause. Hatching marks runs whose primary and secondary causes were answer validation and benchmark specification. Text at right gives runs and tasks per row; in the box, each dot is one run (filled, correct; open, incorrect).

### Conclusion
Shared failures dominate and are mostly attributed to the benchmark: in same-count pairs, 41 of 48 custom-code and 39 of 48 Galaxy failures were coded as benchmark specification or scoring. Where Galaxy did better, the custom-code failures were mostly missing answer validation (12 of 26) or specification (13). Where custom code did better, 3 of 22 Galaxy failures were coded as not able to use Galaxy; the traced case alone supplies 3 of these 13 pairs and 9 of their failures, coded as specification: a PhyKIT version difference encoded in the reference. The second rater agreed on 35 of 45 runs (κ = 0.56): these are moderately reliable attributions, not verified mechanisms.

# Extended Data Fig. 2 | Failure causes and sensitivity of the accuracy comparison

This figure checks two things that Fig. 2 condenses. It gives the full census of causes for incorrect BixBench-Verified-50 runs, and it asks whether the Galaxy minus custom-code difference holds under other correctness thresholds and run populations. The conclusion of Fig. 2 should not depend on one IWC threshold or on a few problematic tasks.

## Extended Data Fig. 2a | What caused each incorrect BixBench-Verified-50 run, by how many runs of its replicate set failed?
panel: ed2a

### Rationale
- **Data.** All 151 BixBench-Verified-50 runs graded incorrect on the results site (77 custom code, 74 Galaxy), with the primary cause assigned by the AI-assisted run-level audit; 4 bix-43-q2 runs made incorrect only by the site's regrade take the task-level audit's cause (benchmark specification or scoring). These are the same records as Fig. 2d, but rows are not split by pair type, so concordant and discordant pairs are pooled.
- **Variables.** Rows group runs by condition and by the number of incorrect runs in their replicate set (1, 2 or 3 of 3). Bars give each primary cause's share of the row; segment labels are run counts, and the column at right gives the row total. The note counts runs coded as under-specified, a subset of the green group, that also had missing answer validation as the secondary cause.
- **Analysis.** Descriptive counts and shares; no test.
- **Reading the plot.** Colours follow the five cause groups of Fig. 2d, without hatching. The unlabelled sliver in the Galaxy 3-of-3 row is one run with no answer submitted.

### Conclusion
Failures repeated in all three runs dominate, and the benchmark is the main attributed cause: 54 custom-code and 51 Galaxy runs come from sets that failed 3 of 3, and 48 and 46 of these were coded as benchmark specification or scoring. Isolated failures (1 of 3) were mostly missing answer validation (10 of 17 custom-code runs, 6 of 9 Galaxy runs). Not able to use Galaxy was the primary cause of 3 of 74 incorrect Galaxy runs. Most under-specified runs also lacked answer validation (74 of 94), so these two causes are not cleanly separable.

## Extended Data Fig. 2b | Does the Galaxy minus custom-code difference change with the IWC correctness threshold or the population analysed?
panel: ed2b

### Rationale
- **Data.** The pooled primary estimates of Fig. 2b; the 240 IWC runs and 80 IWC replicate sets (host-read removal included) re-scored at three agreement thresholds; and five population sensitivities, each dropping tasks or runs, recomputed on these scores with the primary estimator rather than read from the archive's accuracy_sensitivities.csv, which used its own grades and nine IWC tasks.
- **Variables.** The x axis is Galaxy minus custom code in percentage points (IWC agreement × 100). Threshold rows give runs correct and sets with 3/3 correct at agreement ≥ 0.95, ≥ 0.99 and = 1. Population rows drop BixBench-Verified-50 tasks whose failures the audit attributes to the benchmark (22 capsules left), CompBioBench campaigns whose names reference target scores or wrong answers, IWC tasks with a zero-scored run (7 tasks left) or agent-calibrated ATAC routes (9 left), or keep only IWC pairs with matching time budgets.
- **Analysis.** Estimators and 95% percentile cluster-bootstrap intervals are as in Fig. 2b. Threshold and population rows have unadjusted sign-flip *P* values in Source Data (exact for IWC). With ten or fewer IWC clusters the intervals are too narrow.
- **Reading the plot.** Bold diamonds mark the primary estimates and the ≥ 0.99 rows used in Fig. 2; open circles are alternatives. Lines are 95% intervals, and the text at right repeats each estimate and interval.

### Conclusion
The BixBench-Verified-50 and CompBioBench differences stay near zero when the flagged tasks or campaigns are dropped (−1.0, −3.4 to +1.0, *P* = 0.63; −0.3, −2.2 to +1.7, *P* = 0.84). Every IWC point estimate favours Galaxy, but its size depends on the definition: from +0.4 (−0.0 to +0.9; *P* = 0.44) without the three tasks with a zero-scored run to +15.0 (+2.5 to +27.5) for sets correct at ≥ 0.95. No IWC row reached *P* < 0.05 (primary, 0.055; smallest alternative, 0.06 for runs at ≥ 0.95 and for budget-matched pairs). The IWC advantage therefore rests on a few tasks and is not established.
