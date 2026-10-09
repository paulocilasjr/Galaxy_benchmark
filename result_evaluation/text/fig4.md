# Figure 4 | Answer agreement and tool use vary across model configurations

This figure asks whether the four model configurations differ in what they ran in Galaxy and in how consistently their replicate runs answered, and whether consistent answers, consistent tool sets or self-checking go with correct answers. These run-to-run properties matter for reproducibility and auditability, which mean accuracy (Fig. 2) does not capture.

## Fig. 4a | Which kinds of Galaxy tools did each model run on each benchmark?
panel: fig4a

### Rationale
- **Data.** All 1,908 traced Galaxy-condition runs of the four models: 150 BixBench-Verified-50, 290–300 CompBioBench and 30 IWC runs per model. A tool counts when one of its jobs reached the completed (ok) state in the Galaxy job records captured in the agent trace. The unit is the run.
- **Variables.** The 397 installed tools with a completed job are assigned to 14 method families by ordered rules on the Tool Shed identifier (first match wins; codebook in Source Data): four data-handling and ten scientific-method families. Any completed UDT job (agent-written code run as a Galaxy job) forms its own row. Each cell is the percentage of a model's traced runs on that benchmark with at least one completed job in the family.
- **Analysis.** Descriptive only; no intervals or tests.
- **Reading the plot.** Columns are models within benchmarks; darker cells mean more runs. A run counts in every family it used, so columns do not sum to 100. UDTs were not offered on IWC, so that row is zero by design.

### Conclusion
Tool use differed by benchmark and by model. Tables-and-text or format-conversion tools were the most used installed tools for three of four models on BixBench-Verified-50 and for all four on CompBioBench. Among scientific families, statistics (19–35% of runs) and phylogenetics (12–21%) led on BixBench-Verified-50, and read processing and alignment (27–40%) on IWC. Reliance on UDTs varied widely: GPT-5.5 ran one in 66% of BixBench-Verified-50 runs, DeepSeek V4 Pro in 9%. The panel shows whether a family was used, not how much, how well, or what UDTs computed (Extended Data Fig. 4e).

## Fig. 4b | How often did three replicate runs give the same answer, and do models differ?
panel: fig4b

### Rationale
- **Data.** Submitted answers and grades of all BixBench-Verified-50 and CompBioBench runs, grouped into 1,200 replicate sets (three runs of one task by one model in one condition): 600 per condition, 50 or 100 sets per point.
- **Variables.** A set agrees when all three answers match under the task-aware rule: numbers within the benchmark verifier's tolerance (otherwise 0.1%), lists compared as sets, case and spacing ignored. A missing submission counts as disagreement. The y-axis is the percentage of agreeing sets; colour is model, squares are custom code and circles Galaxy.
- **Analysis.** 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Model effects are tested by permuting model labels within tasks (20,000 permutations). Primary tests pool both benchmarks within each condition (Holm over two); per-benchmark tests are secondary (Holm over four).
- **Reading the plot.** Thin grey lines join each model's two conditions. Per-benchmark *P* values sit under each facet; the bold line gives the primary tests. No test compares the conditions.

### Conclusion
Agreement was high but differed between models: 80–96% of sets on BixBench-Verified-50 and 74–89% on CompBioBench. Pooling both benchmarks, a model effect was detected in both conditions (custom code *P* = 0.009, Galaxy *P* = 0.007, Holm-adjusted). Per benchmark, only CompBioBench custom code stayed below 0.05 after adjustment (*P* = 0.04), where GPT-5.6 Sol agreed in 89% of sets (95% interval 83–95%) and DeepSeek V4 Pro in 74% (65–82%). Agreement is not correctness: sets that repeat the same rejected answer count as agreeing (Fig. 4e).

## Fig. 4c | Are tasks whose replicate runs used the same Galaxy tools solved more often?
panel: fig4c

### Rationale
- **Data.** Galaxy task–model cells in which all three replicate runs completed at least one job: 180 of 200 on BixBench-Verified-50, 303 of 400 on CompBioBench and 27 of 40 on IWC (10 tasks, including host-read removal). Tool sets come from completed jobs in the agent traces. Accuracy uses the results-site grades, which regrade bix-53-q2 (75% of runs correct) and bix-43-q2 (50%).
- **Variables.** A run's tool set is its installed tools (identifier without version) plus one item for any UDT. Tool-set similarity is the mean pairwise Jaccard index (shared ÷ combined tools) of the three runs, averaged over a task's eligible cells. The x-axis is the share of the task's 24 runs (four models × two conditions × three replicates) that were correct; IWC runs count as correct at ≥ 0.99 output agreement.
- **Analysis.** Spearman ρ across tasks within each benchmark, with permutation *P* values (20,000 permutations); correlations are descriptive. The within-task comparison correlates task-centred similarity with task-centred Galaxy accuracy over 507 cells, permuting within tasks.
- **Reading the plot.** One point per task, jittered horizontally by up to 1.2 points; 1 means the same tool set in all three runs.

### Conclusion
The direction of the relation changed with the benchmark. Similarity was negatively correlated with accuracy on BixBench-Verified-50 (ρ = −0.47, *P* < 0.001; 50 tasks), no association was detected on CompBioBench (ρ = 0.06, *P* = 0.56; 100 tasks), and the correlation was positive on IWC (ρ = 0.74, *P* = 0.02; only 10 tasks), although host-read removal was solved by all 24 runs at low similarity (0.20). Comparing models on the same task, no association was detected (ρ = 0.03, *P* = 0.57). Consistent tool choice is therefore not a general marker of correct answers. The measure ignores order, versions and parameters (Extended Data Fig. 4b).

## Fig. 4d | Did correct runs check their own analyses more often than incorrect runs?
panel: fig4d

### Rationale
- **Data.** 80 BixBench-Verified-50 and CompBioBench runs, sampled at 10 per benchmark × condition × outcome, at most one run per task per stratum; DeepSeek V4 Pro supplied 29. AI coders read condensed transcripts blind to the grade; the condition was visible. Outcome is the current results-site grade: one run sampled as incorrect (D079, bix-53-q2) is correct after the regrade, so the groups hold 41 correct and 39 incorrect runs.
- **Variables.** Six check types coded present or absent from a fixed codebook: counts or denominators, second method (the same quantity recomputed by another tool or code path), sensitivity analysis, input assumption, plausibility and domain diagnostic; "any check" means at least one. One coded plausibility check, a download of the public answer file, was removed.
- **Analysis.** Percentages of runs with 95% Wilson intervals, 41 correct and 39 incorrect runs. Descriptive only; no test.
- **Reading the plot.** Black circles are correct runs, grey squares incorrect runs, horizontal bars intervals. Extended Data Fig. 7a splits the same codes by condition.

### Conclusion
Checks were common whatever the outcome: 87.8% of correct and 87.2% of incorrect runs had at least one (95% intervals 74–95% and 73–94%). Correct runs more often checked counts or denominators (61.0% vs 43.6%) and recomputed a result by a second method (41.5% vs 25.6%); incorrect runs more often checked input assumptions (71.8% vs 58.5%). Every pair of intervals overlaps and no test was run. The codes are AI-assisted, not human-validated, and sampling by outcome means these are not population rates.

## Fig. 4e | When replicate runs fail, do they repeat the same rejected answer, and does that track task difficulty?
panel: fig4e

### Rationale
- **Data.** All 1,200 BixBench-Verified-50 and CompBioBench replicate sets from both conditions, 300 per model, with each run's grade and submitted answer. Grades are the results site's; the bix-53-q2 and bix-43-q2 regrades move nine sets from the 11–21 bin to 3–10.
- **Variables.** Held-out difficulty is the number of incorrect runs among the task's other 21 runs, binned 0, 1–2, 3–10 and 11–21, so a set's own runs never define it. Each set has one outcome: all three accepted, missing submission, mixed (one or two accepted), all rejected with different answers, or the same rejected answer in all three runs (task-aware matching, as in Fig. 4b).
- **Analysis.** Outcome shares per model and bin. Error bars are 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks) for the same-rejected-answer share. Descriptive only; no test.
- **Reading the plot.** Pink segments are repeated rejected answers; numbers above bars are sets. The 0 bin is mostly tasks solved by all 24 runs (600 of its 624 sets were all accepted).

### Conclusion
Repeated rejected answers appeared only on harder tasks. No set repeated a rejected answer when two or fewer of the other 21 runs were incorrect (0 of 884 sets); the share was 5.6% (95% interval 2.5–8.9%; 214 sets) at 3–10 and 45.1% (28.1–63.0%; 102 sets) at 11–21. In the hardest bin every model showed it, from 36% (DeepSeek V4 Pro, 16–57%) to 52% (GPT-5.6 Luna, 30–74%). A repeated rejection can reflect a shared error, an ambiguous reference or the scorer, so on its own it does not measure rigor.

# Extended Data Fig. 4 | Tool inventory, route similarity, answer matching, difficulty and UDT methods

This figure gives the detail behind the Fig. 4 summaries and tests its main analytical choices: how a route is defined, how answers are matched and how difficulty is held out. It also shows what agent-written UDT code computed. Together these show which Fig. 4 results are robust to those choices.

## Extended Data Fig. 4a | Which installed Galaxy tools were run most often, and by which models?
panel: ed4a

### Rationale
- **Data.** The 1,908 traced Galaxy runs and completed jobs of Fig. 4a, pooled across the three benchmarks: 478 (GPT-5.5), 480 (GPT-5.6 Sol), 470 (GPT-5.6 Luna) and 480 (DeepSeek V4 Pro) runs.
- **Variables.** Installed tools are identified without version; UDTs are excluded. The 15 tools with completed jobs in the most runs (all models pooled) are shown; ranking counts runs, not jobs, so repeated jobs in one run count once. Bar length is the percentage of each model's traced Galaxy runs with at least one completed job of the tool.
- **Analysis.** Descriptive only; no intervals or tests.
- **Reading the plot.** One panel per model, all sharing the tool order (most-used first) and a 0–25% axis. Tool names are display labels; Source Data gives the Tool Shed identifiers.

### Conclusion
No installed tool was used widely. The most frequent, Cut columns, completed a job in 2.7–16.0% of a model's runs, and no bar exceeds 16.0%. Twelve of the 15 tools handle tables, text, format conversion or inspection; only PhyKIT metrics, BWA-MEM and Bedtools intersect are scientific-method tools. GPT-5.5 ran each listed tool in at most 4.0% of its runs, in line with its heavier UDT use (Fig. 4a). Installed-tool use was spread across many tools, mostly for data handling.

## Extended Data Fig. 4b | Do models differ in tool-set similarity, and does the Fig. 4c correlation hold under other route definitions?
panel: ed4b

### Rationale
- **Data.** The eligible Galaxy task–model cells of Fig. 4c (180 BixBench-Verified-50, 303 CompBioBench, 27 IWC; 4–100 per model and benchmark), with its results-site grades and 10 IWC tasks. The ordered, versioned and parameter variants use the completed analysis jobs in the retained Galaxy history records.
- **Variables.** The plot shows mean tool-set similarity per model and benchmark. The table gives Spearman ρ between task similarity and task accuracy (tasks in parentheses) under the Fig. 4c definition and six alternatives: UDT items dropped; cells using installed tools only; cells with any UDT; ordered steps (one minus the normalised edit distance between job sequences); tools distinguished by version; tools with identical non-dataset parameters.
- **Analysis.** 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Model effects are tested by permuting model labels within tasks (20,000 permutations), without adjustment. Table correlations are descriptive.
- **Reading the plot.** Points are model means, coloured by model, with vertical lines for 95% intervals; the *P* value under each benchmark tests the model effect. In the table, each row is one route definition, and a dash marks IWC cells with any UDT, as UDTs were not offered there.

### Conclusion
Models differed on BixBench-Verified-50 (*P* = 0.03; GPT-5.5 highest at 0.73, 95% interval 0.63–0.82) and CompBioBench (*P* = 0.003; GPT-5.6 Sol 0.52, 0.46–0.58, against 0.38 and 0.39 for GPT-5.6 Luna and DeepSeek V4 Pro); no difference was detected on IWC (*P* = 0.27; 4–9 cells per model). The negative BixBench-Verified-50 correlation weakened when order or versions counted (ρ = −0.25, −0.28) and vanished with parameters (ρ = −0.04). CompBioBench stayed between −0.01 and 0.20. IWC stayed positive with order or versions (ρ = 0.84, 0.82) and fell to 0.50 with parameters. Eligibility varied, so model means cover different tasks (31 of 50 BixBench-Verified-50 cells for DeepSeek V4 Pro).

## Extended Data Fig. 4c | Does the answer-matching rule change how often replicate runs agree?
panel: ed4c

### Rationale
- **Data.** The 1,200 replicate sets of Fig. 4b, 600 per condition (150 tasks × four models).
- **Variables.** The percentage of sets whose three submitted answers match under four rules: exact text after trimming and lower-casing; numbers rounded to three or to two significant digits, which changes only answers that parse as a single number (others stay exact text); and the primary task-aware rule of Fig. 4b (benchmark tolerance or 0.1%, lists as sets, identifier versions ignored). A missing submission never matches.
- **Analysis.** Descriptive only; pooled percentages without intervals or tests.
- **Reading the plot.** Orange squares are custom code and blue circles Galaxy; one row per rule, with the primary rule last. The x-axis starts at 70%, which magnifies small gaps.

### Conclusion
The rule moved agreement by 8–9 points, more than the gap between conditions. Exact text gave 74.2% (custom code) and 76.2% (Galaxy); three significant digits 81.0% and 82.2%; two significant digits 82.8% and 83.5%; the task-aware rule 83.0% and 84.3%. The gain over exact text comes from numeric answers that differed only in format or in later digits. Galaxy sets agreed slightly more often under every rule (by 0.7–2.0 points), but this comparison has no interval or test.

## Extended Data Fig. 4d | Does the difficulty pattern of Fig. 4e hold when the same model's runs are left out of difficulty?
panel: ed4d

### Rationale
- **Data.** The 1,200 BixBench-Verified-50 and CompBioBench replicate sets of Fig. 4e, all models and both conditions pooled, with the results-site grades.
- **Variables.** The share of sets with the same rejected answer in all three runs, by held-out difficulty defined two ways: incorrect runs among the task's other 21 runs (bins 0, 1–2, 3–10, 11–21, as in Fig. 4e) or among the other three models' 18 runs (bins 0, 1–2, 3–8, 9–18). The second removes the same model's runs in the other condition. Bins are labelled None, Few, Some and Most.
- **Analysis.** 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Descriptive only; no test.
- **Reading the plot.** Filled black circles use the 21-run definition, open grey squares the 18-run definition; bins hold 102–658 sets.

### Conclusion
Yes. In the hardest bin, 45.1% of sets (95% interval 28.1–63.0%; 102 sets) repeated the same rejected answer under the 21-run definition and 41.8% (25.0–59.0%; 110 sets) under the 18-run definition. In the easiest bin the shares were 0% and 0.5% (0–1.2%). The link between difficulty and repeated rejected answers therefore does not depend on the same model's runs in the other condition. Bin edges differ between the definitions, so the middle bins are not strictly comparable.

## Extended Data Fig. 4e | What did the completed UDT jobs compute?
panel: ed4e

### Rationale
- **Data.** Completed UDT jobs in traced Galaxy runs: 116, 59, 96 and 20 on BixBench-Verified-50 and 573, 729, 748 and 413 on CompBioBench for GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro. Each job's UDT definition (container and command) is read from the archived trace.
- **Variables.** Each job gets one of 13 classes: the nine scientific method families of Fig. 4a, tables and text, other methods, environment probe or set-up, and script supplied as a dataset. Cells give the percentage of a model's completed UDT jobs on that benchmark.
- **Analysis.** Deterministic, ordered keyword rules: probes first, then the command when it contains the code, then a container named after a specific tool, then a script passed as an input dataset, then table and text handling. Descriptive only.
- **Reading the plot.** Each column sums to 100% before rounding; parentheses give jobs per column. "Script supplied as a dataset" marks jobs whose code sits in the Galaxy history, not in the request, so their method is not classified.

### Conclusion
Many UDT jobs implemented recognisable scientific methods, which differed by benchmark. On BixBench-Verified-50, phylogenetics (14–25% for the GPT models; 75% of DeepSeek V4 Pro's 20 jobs) and expression and differential testing (17–25% for the GPT models) were the largest classes. On CompBioBench, 41–52% of each model's jobs ran a script supplied as a dataset, so their method is unknown from the request; classified jobs spanned statistics, single-cell, variant calling and other analyses. Probes and set-up took 0–18% of jobs. Classes come from keyword rules, not manual review, and each job gets one class.
