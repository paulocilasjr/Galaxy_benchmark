# Lab-meeting figures: accuracy by model, and which tasks each condition does not solve

The first six figures are bar charts of the same comparison.
Each shows the accuracy of each model with custom code (vermillion) and with Galaxy (blue), in one panel per benchmark.
They differ only in how accuracy is computed and how much uncertainty is shown.
`fig2_statistical_unanimous` and `fig2_statistical_unanimous3` count tasks instead of runs.
`fig2_statistical_compilation` puts all three counting rules side by side.
The last two move from accuracy to individual tasks.
`fig2_task_similarity` shows which tasks each condition fails, and which failures are exclusive to one condition; `fig2_task_consistency` shows how many runs of each task each condition got right.
`fig3_trajectory_similarity` looks inside the runs, at the steps each replicate took.
All nine use the site-matched per-run scores in `figures/scored_runs.csv`: 3,840 runs on 160 tasks, 4 models × 2 conditions × 3 replicates.

A run counts as correct when:
- **BixBench-Verified-50 or CompBioBench:** its answer is accepted;
- **IWC:** its output agreement is at least 0.99.

The IWC rule matches Fig. 2b; Fig. 2a plots IWC's mean agreement on a 0–1 scale instead.

## The three accuracy figures

| Figure | Accuracy | What else is shown |
|---|---|---|
| `fig2_raw_numbers` | correct runs ÷ all runs, pooled over tasks and replicates (e.g. 137/150) | the count and percentage inside each bar |
| `fig2_replicate_numbers` | the mean of the three replicate accuracies | each replicate as a dot; whiskers ± 1 SD across replicates |
| `fig2_statistical_numbers` | correct runs ÷ all runs | 95% cluster-bootstrap intervals; a paired test of Galaxy vs custom code per model, Holm-adjusted, marked on the brackets as \* adj. P < 0.05, \*\* < 0.01, \*\*\* < 0.001 or ns; under each panel, the all-four-models difference and a table of each model's difference, P and adjusted P |

**The raw and replicate-mean accuracies are identical.**
Every replicate covers every task once (per model and condition: BixBench 50 runs, CompBioBench 100, IWC 10), so the mean of the three replicate accuracies equals the pooled proportion.
The script checks this.
The replicate figure adds the run-to-run spread.
The largest spreads are:
- **IWC:** SD 5.8 points, where one task is 10 points;
- **BixBench and CompBioBench:** SD 0–4.6 points.

### Statistics used in `fig2_statistical_numbers`

These are the estimators of Fig. 2b, imported from `figures/make_fig2.py` so the numbers agree with it.

- **Accuracy intervals.** 95% percentile cluster bootstrap, 20,000 resamples. Clusters are resampled with all their runs:
  - BixBench: the 33 source capsules, since questions from the same capsule share data;
  - CompBioBench and IWC: the tasks.
- **Galaxy minus custom code, per model.** A paired cluster sign-flip randomization test:
  - the per-cluster difference keeps the pairing by task;
  - 200,000 random sign flips, or exact enumeration when there are 16 or fewer clusters (IWC: 2^10).
- **Multiple comparisons.** Holm adjustment over the 12 model × benchmark comparisons. The all-four-models line under each panel is adjusted over the 3 benchmarks.

A chi-square or Fisher test on the raw counts would be wrong here.
It treats the 150, 300 or 30 runs as independent, but runs of the same task are correlated across replicates and across conditions.
That would overstate the evidence.

### Result

None of the 12 Galaxy vs custom-code differences is significant.
Unadjusted P ranges from 0.25 to 1.00, and every Holm-adjusted P is 1.00.

| Benchmark | Galaxy − custom code, all four models (95% CI) | P | Holm P (3) |
|---|---|---|---|
| BixBench-Verified-50 | +0.5 pts (−3.9 to 4.8) | 0.88 | 1.00 |
| CompBioBench | +0.3 pts (−1.8 to 2.6) | 0.82 | 1.00 |
| IWC (≥ 0.99) | +3.3 pts (−0.8 to 8.3) | 0.38 | 1.00 |

The BixBench and CompBioBench values match the manuscript Results (draft PR #12).
For IWC the manuscript reports mean agreement (0.95 vs 0.98, +0.036); this figure reports accuracy at ≥ 0.99 agreement instead.

## Task accuracy under the 2-of-3 rule (`fig2_statistical_unanimous`)

This is the same figure as `fig2_statistical_numbers`, but the unit is the task instead of the run.
A model solves a task in a condition when at least 2 of its 3 runs are correct, the majority rule of `fig2_task_similarity`.
Accuracy is tasks solved ÷ tasks: out of 50, 100 and 10.
Each bar is labelled with its count (e.g. 47/50).
The name is the one requested; the rule is a majority (2 of 3), not unanimity (3 of 3).

The statistics are those of `fig2_statistical_numbers`, applied to each task's solved / not solved outcome:
- cluster bootstrap with the same clusters;
- paired cluster sign-flip test;
- Holm adjustment over the 12 model comparisons, and over the 3 benchmarks for the pooled line.

The task-level accuracies match the Venn counts: custom code = custom code only + both; Galaxy = Galaxy only + both.

None of the 12 differences is significant: every Holm-adjusted P is 1.00, and the smallest unadjusted P is 0.25.

| Benchmark | Galaxy − custom code, all four models (95% CI) | P | Holm P (3) |
|---|---|---|---|
| BixBench-Verified-50 | −1.5 pts (−5.7 to 2.0) | 0.63 | 1.00 |
| CompBioBench | −1.8 pts (−4.8 to 1.0) | 0.32 | 0.95 |
| IWC | +5.0 pts (0.0 to 12.5) | 0.50 | 1.00 |

Counting tasks instead of runs turns the small BixBench and CompBioBench differences slightly in favour of custom code (per run: +0.5 and +0.3 points).
Every interval still includes zero.
The rule discards partial information: a task with 2 of 3 runs correct counts the same as one with 3 of 3, and 1 of 3 the same as 0 of 3.

Some IWC intervals collapse to a single value (e.g. 0.0 to 0.0) when no task differs between the conditions for that model.
In that case the bootstrap has nothing to resample.

## Task accuracy when all 3 runs must be correct (`fig2_statistical_unanimous3`)

This is the same figure with the strict rule.
A model solves a task in a condition only when all 3 of its runs are correct.
Everything else is unchanged from `fig2_statistical_unanimous`: tasks as the unit, bootstrap intervals, paired sign-flip test, Holm adjustment.
The task counts match the "all three correct" row of `fig2_task_similarity_counts.csv`, and the script checks this.

Again, none of the 12 differences is significant: every Holm-adjusted P is 1.00, and the smallest unadjusted P is 0.25.

| Benchmark | Galaxy − custom code, all four models (95% CI) | P | Holm P (3) |
|---|---|---|---|
| BixBench-Verified-50 | +2.5 pts (−4.4 to 9.9) | 0.59 | 0.60 |
| CompBioBench | +2.3 pts (−1.5 to 6.0) | 0.30 | 0.60 |
| IWC | +10.0 pts (2.5 to 17.5)† | 0.13 | 0.38 |

† **The IWC interval excludes zero but the test does not reject, and the test is the one to trust.**
- **Few differing tasks.** Only 4 of the 10 IWC tasks differ between the conditions once all four models are pooled, and all 4 favour Galaxy.
- **Why the bootstrap is too narrow.** A percentile bootstrap over 10 tasks cannot produce a negative difference from those data, and it misses zero whenever a resample leaves out all 4 tasks. That happens with probability 0.6¹⁰ ≈ 0.6%, below the 2.5% the interval needs, so the interval comes out too narrow.
- **The exact test.** With 4 differing tasks the smallest attainable P is 2/2⁴ = 0.125, so this is as strong as 10 tasks can show.
- **The footnote.** The figure marks the line with † and explains it in a footnote. The footnote appears only when an interval and its test disagree like this.

### The three ways of counting, side by side (`fig2_statistical_compilation`)

This figure has one panel per benchmark.
For each model there are three bars per condition, in order:
- **per run:** full colour;
- **task solved with ≥ 2 of 3 runs:** lighter;
- **task solved with all 3 runs:** lightest.

The shift of a condition's accuracy as the rule tightens reads left to right within its three bars.
The table under each panel gives every accuracy (custom code / Galaxy) under each rule, and the all-four-models difference with its significance.
A significant per-model difference would be marked with stars after the Galaxy value; none is.
The intervals and exact P values are in the three separate figures.

| Galaxy − custom code, all four models | Per run | Task solved: ≥ 2 of 3 runs | Task solved: all 3 runs |
|---|---|---|---|
| BixBench-Verified-50 | +0.5 | −1.5 | +2.5 |
| CompBioBench | +0.3 | −1.8 | +2.3 |
| IWC | +3.3 | +5.0 | +10.0 |

The sign of the BixBench and CompBioBench differences depends on the counting rule, and no version is significant.
The strict rule favours Galaxy on all three benchmarks: more tasks are solved in all three runs with Galaxy. In `fig2_task_similarity_counts.csv`, under that rule, 54 task × model pairs fail only with custom code and 36 only with Galaxy.
This hints that Galaxy runs may be slightly more repeatable, but the evidence is weak (pooled Holm P ≥ 0.38).

## Which tasks each condition does not solve (`fig2_task_similarity`)

There is one Venn diagram for each benchmark (columns) and model (rows).
Each circle holds the tasks a condition does **not** solve, so the errors exclusive to a condition sit inside its own circle:
- **left:** tasks only custom code fails;
- **centre:** tasks both conditions fail;
- **right:** tasks only Galaxy fails.

The exclusive failures can then be read straight off the figure when the errors are discussed.

A condition solves a task when at least 2 of its 3 runs are correct (majority), so it fails a task when 0 or 1 of its 3 runs are correct.
Tasks solved by both conditions are counted at the top right of each diagram.
The circles show set membership only and are not drawn to scale.
The tasks on each side are named below the diagram:
- BixBench and CompBioBench use their own task IDs;
- IWC tasks are shortened to their workflow number (`IWC_007` = `wf_007_vgp_mitogenome_assembly`; the full names are in the CSV).

Names are listed when a side holds 8 tasks or fewer.
Under the majority rule every side does: the largest is 7.

Across the 640 task × model pairs (160 tasks × 4 models):
- 543 (85%) are solved by both conditions and 57 are failed by both;
- 16 are failed only with custom code and 24 only with Galaxy.

The direction of the small difference depends on how "solved" is defined, so neither condition is consistently ahead:

| A condition fails a task when | Only custom code fails | Both fail | Only Galaxy fails | Neither fails |
|---|---|---|---|---|
| none of its 3 runs is correct | 16 | 31 | 15 | 578 |
| 0 or 1 of 3 runs are correct (figure) | 16 | 57 | 24 | 543 |
| any of its 3 runs is wrong | 54 | 87 | 36 | 463 |

`bix-45-q1` is the one task that falls on the same side for three models: only Galaxy fails it, for GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro.
Three tasks fall on opposite sides for different models: `bix-43-q2`, `conservation-lookup-q1` and `lung-cancer-sc-q1`.
That points to run-to-run variation more than to a systematic advantage of one condition.

## Runs correct per task (`fig2_task_consistency`)

This is the Venn figure without the 2-of-3 cut-off.
It has one 4 × 4 matrix per benchmark (columns) and model (rows):
- **x-axis:** how many of a task's 3 custom-code runs were correct;
- **y-axis:** how many of its 3 Galaxy runs were correct;
- **each cell:** the number of tasks with that pair of counts.

The two conditions are paired by task.
Their replicate numbers are not matched: replicate 1 of custom code and replicate 1 of Galaxy are independent runs.

The cell colours:
- **grey (the diagonal):** the same number of runs correct in both conditions;
- **blue (above it):** Galaxy got more runs right;
- **vermillion (below it):** custom code got more runs right.

Shade is the number of tasks on a log scale, so that single tasks stay visible next to the large 3/3 cell.
The dashed lines at 1.5 runs mark the majority rule of `fig2_task_similarity`.
The four blocks are its Venn regions:
- **bottom left:** both fail;
- **top left:** only custom code fails;
- **bottom right:** only Galaxy fails;
- **top right:** neither fails (solved by both).

The script checks that every block equals the Venn count.

| Benchmark | Task × model pairs | Same number correct | Galaxy more | Custom code more | Differ by 2–3 runs |
|---|---|---|---|---|---|
| BixBench-Verified-50 | 200 | 170 (85%) | 17 | 13 | 7 |
| CompBioBench | 400 | 307 (77%) | 47 | 46 | 16 |
| IWC | 40 | 32 (80%) | 6 | 2 | 0 |
| All | 640 | 509 (80%) | 70 | 61 | 23 |

Most pairs sit on the diagonal: 494 of the 640 are 3/3 or 0/0.
Off the diagonal the two directions are nearly balanced, and 108 of the 131 off-diagonal pairs differ by a single run.
Seven pairs are complete reversals, where one condition got all 3 runs right and the other got none.

| Task | Model(s) | All 3 runs correct with |
|---|---|---|
| `bix-30-q3` | GPT-5.6 Sol, DeepSeek V4 Pro | Galaxy |
| `bix-45-q1` | GPT-5.6 Sol, DeepSeek V4 Pro | custom code |
| `contaminated-rna-q3` | GPT-5.6 Luna | Galaxy |
| `contaminated-rna-q2` | DeepSeek V4 Pro | Galaxy |
| `characterize-response-q1` | GPT-5.6 Luna | custom code |

Reversals that repeat across models are the cases where a condition-specific cause is most likely and worth checking in the traces.

## Fig. 3: do the replicates follow the same trajectory? (`fig3_trajectory_similarity`)

### The frame: tasks only Galaxy fails

The frame is the right-hand side of `fig2_task_similarity`: task × model pairs where custom code solves the task (≥ 2 of 3 runs correct) and Galaxy does not (0 or 1 of 3).
There are 24 pairs, 6 in BixBench-Verified-50 and 18 in CompBioBench; IWC has none.
Each pair is compared with two references:
- **the custom-code runs of the same pair:** same task and model, the other condition;
- **a matched Galaxy control:** a task the same model solved in all 3 Galaxy runs, in the same benchmark, with the closest median number of Galaxy steps.
  - Matching uses a log scale and is without replacement; tasks in the frame are never controls.
  - The match is close: the median is 9 steps in both groups (P = 0.41).

| Benchmark | Model | Task | Custom code correct | Galaxy correct | Matched Galaxy 3/3 task | Galaxy steps (failed / matched) |
|---|---|---|---|---|---|---|
| BixBench-Verified-50 | GPT-5.6 Sol | `bix-45-q1` | 3/3 | 0/3 | `bix-17-q2` | 3 / 3 |
| BixBench-Verified-50 | GPT-5.6 Luna | `bix-43-q2` | 2/3 | 1/3 | `bix-22-q1` | 2 / 2 |
| BixBench-Verified-50 | GPT-5.6 Luna | `bix-45-q1` | 2/3 | 0/3 | `bix-11-q1` | 3 / 3 |
| BixBench-Verified-50 | GPT-5.6 Luna | `bix-52-q7` | 3/3 | 1/3 | `bix-41-q5` | 8 / 8 |
| BixBench-Verified-50 | DeepSeek V4 Pro | `bix-31-q2` | 2/3 | 1/3 | `bix-11-q2` | 1 / 1 |
| BixBench-Verified-50 | DeepSeek V4 Pro | `bix-45-q1` | 3/3 | 0/3 | `bix-11-q1` | 2 / 2 |
| CompBioBench | GPT-5.5 | `exogenous-mix-reads-q1` | 2/3 | 1/3 | `huggingface-entropy-q1` | 14 / 14 |
| CompBioBench | GPT-5.5 | `finding-geo-q1` | 2/3 | 0/3 | `cell-proportions-q1` | 20 / 23 |
| CompBioBench | GPT-5.5 | `ml-model-track-overlap-q1` | 2/3 | 0/3 | `annotate-variant-gene-impact-q1` | 3 / 3 |
| CompBioBench | GPT-5.5 | `overexpress-tf-q1` | 2/3 | 1/3 | `match-genotypes-q1` | 9 / 9 |
| CompBioBench | GPT-5.6 Sol | `reverse-search-gwas-q1` | 2/3 | 1/3 | `1000G-retrieve-genotype-q2` | 3 / 3 |
| CompBioBench | GPT-5.6 Luna | `afgr-1000g-intersect-atac-q1` | 2/3 | 1/3 | `disease-samples-q1` | 9 / 9 |
| CompBioBench | GPT-5.6 Luna | `atac-doublet-q1` | 3/3 | 1/3 | `deg-simple-q1` | 22 / 23 |
| CompBioBench | GPT-5.6 Luna | `characterize-response-q1` | 3/3 | 0/3 | `1000G-retrieve-genotype-q2` | 36 / 33 |
| CompBioBench | GPT-5.6 Luna | `conservation-lookup-q1` | 2/3 | 0/3 | `pooled-infer-donors-q1` | 25 / 26 |
| CompBioBench | GPT-5.6 Luna | `covid-patient-q1` | 2/3 | 1/3 | `bedtools-chromhmm-q1` | 10 / 10 |
| CompBioBench | GPT-5.6 Luna | `overexpress-tf-q1` | 2/3 | 1/3 | `find-amplification-q1` | 19 / 19 |
| CompBioBench | GPT-5.6 Luna | `three-way-barnyard-q2` | 2/3 | 1/3 | `identify-donor-q1` | 90 / 62 |
| CompBioBench | DeepSeek V4 Pro | `1000G-retrieve-genotype-q1` | 2/3 | 1/3 | `annotate-variant-gene-impact-q1` | 2 / 2 |
| CompBioBench | DeepSeek V4 Pro | `cryptic-exon-q1` | 3/3 | 1/3 | `1000G-retrieve-genotype-q2` | 7 / 7 |
| CompBioBench | DeepSeek V4 Pro | `finding-geo-q1` | 2/3 | 1/3 | `splice-pred-q1` | 9 / 9 |
| CompBioBench | DeepSeek V4 Pro | `histone-chip-q1` | 3/3 | 1/3 | `sample-swap-rna-q1` | 47 / 42 |
| CompBioBench | DeepSeek V4 Pro | `lung-cancer-sc-q1` | 2/3 | 1/3 | `identify-donor-q1` | 18 / 18 |
| CompBioBench | DeepSeek V4 Pro | `three-way-barnyard-q2` | 2/3 | 1/3 | `atac-tn5-shift-q1` | 39 / 38 |

`fig3_frame_runs.csv` lists every run of these pairs and of their controls, 288 runs in all:
- the submitted answer and its score;
- the step sequence.

The Galaxy and custom-code answers of a pair can be read side by side there.

### What a step is (`trajectory_steps.py`)

Every run is reduced to the ordered list of analysis steps it executed, read from its job ledger (`<benchmark>/analysis/<task>/job_ledgers/<condition>/<run_id>.json`).

**What counts as one step.**
- **Galaxy:** one job that Galaxy executed, whatever route the agent used to start it. Jobs are ordered by creation time; the ledgers list them in a different order in 1,973 of the 2,070 Galaxy ledgers.
- **Custom code:** one shell command that the ledger classes as analysis.

**How steps are labelled.** Both conditions use the same scheme:
- **named tools** keep their name (`phykit_metrics`, `bedtools_intersectbed`; `minimap2`, `bedtools coverage`, `samtools view`);
- **table and text utilities** keep theirs too (`Cut1`, `Filter1`, `datamash_ops`; `awk`, `sort`, `grep`);
- **custom scripts** are labelled by language and imported non-standard-library modules (`py:pandas+pydeseq2`, `R:Seurat`);
- **Galaxy user-defined tools** (UDTs, the scripts an agent writes and runs inside Galaxy) are labelled by container and main command (`UDT:anndata/py`, `UDT:hdf5/h5dump`).
  - This covers UDTs registered through the UDT tool and through the API.
  - Any tool outside the Tool Shed that is not one of Galaxy's built-ins counts as a UDT.

**What is dropped (plumbing).**
- **Galaxy:** uploads, data fetches and converters.
- **Custom code:**
  - downloads and installs;
  - commands that only inspect files (`ls`, `head`, `wc`);
  - the text of heredocs and quoted arguments.

A few runs have no analysis steps at all: they answered from searches or file reads alone.

### Similarity between replicates

The three replicates of a group form 3 pairs. Each pair gets two scores:
- **approach similarity:** Jaccard overlap of the two runs' sets of step labels, i.e. the same tools and scripts in any order;
- **path similarity:** 1 − the normalised edit distance between the two step sequences, after collapsing consecutive repeats, i.e. the same steps in the same order.

Each dot in the figure is the mean over the 3 pairs.

**Tests.**
- **Galaxy failed vs custom code:** paired by task and model.
- **Galaxy failed vs Galaxy 3/3:** paired by the matching.
- **Method:** both use the paired cluster sign-flip test of Fig. 2. The clusters are tasks, since `bix-45-q1`, `finding-geo-q1`, `overexpress-tf-q1` and `three-way-barnyard-q2` are in the frame for more than one model.

### Result

| Measure | Galaxy, task failed | Custom code, same task | Galaxy, matched task 3/3 | P (failed vs code) | P (failed vs matched) |
|---|---|---|---|---|---|
| Approach similarity (median) | 0.20 | 0.35 | 0.33 | 0.88 | 0.92 |
| Path similarity (median) | 0.19 | 0.27 | 0.26 | 0.87 | 0.76 |
| Steps per run (median) | 9 | 38.5 | 9 | 0.002 | 0.41 |

Overall, the Galaxy failures are not significantly less consistent than Galaxy runs that succeed on tasks of the same length.
Neither similarity differs significantly from either reference.
Medians and means disagree because the two benchmarks behave in opposite ways:
- **BixBench-Verified-50: the failures are consistent.**
  - In 4 of the 6 pairs, all three Galaxy replicates run the same tools in the same order (approach and path similarity 1.0). The medians are 1.00, against 0.51 and 0.53 for the matched controls.
  - `bix-45-q1` is the clearest case.
    - All 9 Galaxy runs (GPT-5.6 Sol, GPT-5.6 Luna, DeepSeek V4 Pro) run `phykit_metrics` then `nonparametric_rank_tests`, and all submit the same wrong value, 1.52e-56.
    - 8 of the 9 custom-code runs submit 7.70e-54, which is accepted. The ninth gets the Galaxy value.
  - The Mann–Whitney settings are identical in both conditions: two-sided, `method='auto'`, continuity correction on. The difference comes from the RCV values being tested.
  - The run-level audit (`analysis_reports/galaxy_improvement_20260924/v2_trace_friction/ledger.json`) traces it to the PhyKIT version:
    - the accepted value reflects PhyKIT 2.0.3-era RCV;
    - Galaxy's `phykit_metrics` wrapper, like current PhyKIT, gives 1.52e-56;
    - the agent cannot see the wrapper's version, and pinning a version would have needed a UDT.
  - The audit classes it as benchmark specification first, platform second. It is a systematic, condition-specific error, not run-to-run wandering, and Fig. 2 uses the same task as its traced example.
- **CompBioBench: the failures scatter.**
  - Galaxy replicates rarely share an approach (median approach similarity 0.19; path 0.13).
  - Galaxy runs that succeed on matched tasks score only a little higher (0.32; path 0.25).

**Comparing the two conditions directly.**
- Custom-code runs take about four times as many steps (median 38.5 against 9; P = 0.002), and much finer ones (one command against one Galaxy job). That puts their similarity on a different scale.
- The matched Galaxy control is the fair comparison for the Galaxy failures. Custom-code runs on the matched tasks are in `fig3_frame_tasks.csv` (`ctrl_code_*`) as a further reference.

## Fig. 3 case studies: why the same model succeeded with custom code (`fig3_case1–3`)

The same model solved each of these tasks with custom code. So each case is read as a lapse of rigor in the Galaxy runs, not a missing capability: a check, or a closer reading of the question, that would have put the Galaxy run on the path the model took in custom code.

**What each figure shows.** Each case is one task × model pair from the frame, drawn as step timelines only.
- Each step's tool name is printed inside its box when the box is wide enough.
- Each run gets a one-line callout at its end (e.g. "◀ line count includes the header") and its answer and grade.
- **Run order:** each of the four models has its own block, the model in focus first. Each block shows custom code (r1–r3) and then Galaxy (r1–r3), correct or not. Runs longer than 80 steps (or than the longest run of the model in focus) are cut there, with their total shown after the cut.
- **Case 1:**
  - **Custom code:** all 12 runs are correct (19,159), in one to four steps.
  - **Galaxy:** the correct runs subtracted the header, counted the 539 rows kept, or read the table by its header. The two failures with the same `Filter > wc` steps (Luna r2, Sol r3) did not.
- **Case 2:** how far a run took the identifier mapping decides its answer.
  - **"Never queried ENCODE":** all of Luna's runs, and DeepSeek V4 Pro Galaxy r1. They reached 100 or 1300.
  - **Stopped at 1,264:** GPT-5.5 Galaxy r1, Sol custom code r1 and r2, and DeepSeek V4 Pro custom code r2. Sol's runs stripped the ENCODE replicate suffixes but used no cross-references (1300).
  - **ENCODE cross-references only:** Sol's Galaxy runs reached 2,404, so 2400.
  - **Both steps:** these runs reached about 3,570, so 3600.
    - custom code: GPT-5.5 r1 and r3, Sol r3, DeepSeek r3;
    - Galaxy: DeepSeek r3.
- **Case 3:** every correct run checked base composition or used a control set, except GPT-5.5 custom code r1, which inferred KLF4 from OCT/SOX co-motifs. Three of Sol's runs had PAX7 ahead at first and reversed it: custom code r2 and r3 after GC matching, and Galaxy r3 after a full PWM test.
  - **Incorrect custom-code runs:** GPT-5.5 r2 (PAX7) checked motif names, not GC.
  - **Incorrect Galaxy runs:**
    - GPT-5.5 r1 answered as soon as GC matching moved its top hit;
    - GPT-5.5 r2 tested SPI1 alone;
    - DeepSeek V4 Pro r3 answered PAX7 from FIMO hit enrichment.
- **Legends:** only the step kinds that appear in the figure. A Galaxy script is a UDT; a custom-code script is a script.
- **Earlier version:** cases 2 and 3 also had a quantitative panel and three explanatory notes. Their data are still in `make_case_figures.py` (`panel_mltrack`, `panel_overexpress`, the `notes` fields), with trace line numbers.

**Evidence.**
- Every statement cites a line of the run's agent trace (`codex_events.jsonl`, written `Lnnn`), and every quote and number was checked against the trace.
- Answers and grades come from `figures/scored_runs.csv`. The accepted answer is inferred from the runs graded correct; no ground-truth file was opened.
- None of the custom-code runs shown looked up benchmark answers. Their web searches, where there were any, are about the task's data sources.

| Case | Task × model | Galaxy / custom code correct | What the Galaxy runs missed | What the custom-code runs did |
|---|---|---|---|---|
| 1 | `bix-52-q7`, GPT-5.6 Luna | 1/3 / 3/3 | r2 counted the header line (19,160); r3 reported the rows kept, not removed (539) | counted kept and removed rows together, so each checked the other (19,159). In Galaxy, Luna r1 and the other models' correct runs also handled the header: Sol r1 ran the same two steps as Luna r2 and checked whether the header was kept; DeepSeek counted the 539 rows kept and subtracted them from 19,698 |
| 2 | `ml-model-track-overlap-q1`, GPT-5.5 | 0/3 / 2/3 | stopped at 1,264 matches (1300) without asking why ENCODE tracks barely matched; r3 accepted a 109-row join | the same 1,264, then "one more possible source of hidden aliases": ENCODE → GEO cross-references gave 3,573 (3600) |
| 3 | `overexpress-tf-q1`, GPT-5.6 Luna | 1/3 / 2/3 | r2 measured 39.1% vs 53.4% GC, then answered from raw motif hit rates (PAX7); r3 checked peak lengths, not GC | matched the background on GC, which turned KLF4 from depleted (0.61) to most enriched (1.64); Galaxy r1 used MEME-ChIP with a control set and was correct |

The three lapses are of different kinds:
- an unreconciled count and a misread question;
- an unexamined identifier mapping;
- a confounder that was measured and then ignored.

In each case, the check was possible in Galaxy, and in cases 1 and 3 another Galaxy run of the same model did it.

### Candidates not used, and why

Five more frame pairs were investigated from their traces.

| Task | Why it was not used |
|---|---|
| `bix-45-q1` | A tool-version effect (PhyKIT), not rigor (see the trajectory section). |
| `bix-31-q2`, DeepSeek V4 Pro | Partly rigor: the run replaced the `pydeseq2` the question names with R DESeq2 + apeglm, which it had first ruled out (L47 → L320), and reported the result unchecked. The trigger was a Galaxy failure (UDT jobs never dispatched), and the ledger misses the substitute jobs, so the timeline would be misleading. |
| `finding-geo-q1`, GPT-5.5 | A strong rigor lapse: all three Galaxy runs submitted a GEO series their own Galaxy job had already rejected. But no Galaxy run ever found the right series, so a check alone would not have produced the answer. |
| `characterize-response-q1`, GPT-5.6 Luna | The decisive step with custom code was finding the source (the Immune Dictionary) through web search, and Luna's Galaxy runs made no web searches. That is a harness difference, not rigor. |
| `conservation-lookup-q1`, GPT-5.6 Luna | **Not a valid contrast.** Both custom-code runs graded correct downloaded other agents' published answers for this question from a public Hugging Face dataset (`amanutej/trustworthy-biology-agents-traces`) and submitted them; neither computed the accepted values itself. |

### Cases 4–6: Galaxy solved the task, custom code did not

These cases are the mirror image of cases 1–3. They are task × model pairs where Galaxy got 2 or 3 of 3 runs right and custom code 0 or 1, the left-hand side of `fig2_task_similarity`.
There are 16 such pairs.
The question for each is what Galaxy provided that the custom-code runs lacked.
The layout and the evidence rules are the same as for cases 1–3.

**Case 4 (`fig3_case4_contaminated-rna-q3`, GPT-5.6 Luna; Galaxy 3/3, custom code 0/3).**
The question asks for the genus of the non-human organism in a nominally human RNA-seq FASTQ. The accepted answer is *pan*.
- **What Galaxy provided:** a prebuilt Kraken2 database on CVMFS, `core_nt` (2024-09-04 build), which is the wrapper's default and includes ape genomes. Classifying all 240,000 reads against it gives Homo 33,703 and **Pan 6,271** reads; the next primate genera are in the hundreds, and *Mesomycoplasma* has 26 (Luna Galaxy r1, L52–L53).
  - Every Galaxy run that received a Kraken2 `core_nt` result answered *pan*: 10 of 10, across all four models.
  - The two Galaxy runs that did not receive one were wrong: Sol r2's job was orphaned, and DeepSeek r2's never returned.
- **Why Luna's custom code failed:** it had no comparable classification database and filtered the evidence it did find.
  - **What it ran:** it subtracted human reads and searched the rest.
  - **What it saw:** Pan hits did appear, 95 against 4 for *Mesomycoplasma* in r1 (L70), and r2 found 9,486 reads that matched chimpanzee best (L228).
  - **What it did with them:** every run set primates aside as "host" and reported a minor but real *Mesomycoplasma hyorhinis* signal (118–140 reads).
- **Other custom-code runs:** custom code can reach *pan* by racing ape references read by read. GPT-5.5 did this 3/3 and Sol 2/3.
- **The sister task:** `contaminated-rna-q2` shows the same pattern for DeepSeek V4 Pro.

**Case 5 (`fig3_case5_wf_007_vgp_mitogenome_assembly`, GPT-5.5; Galaxy 2/3, custom code 1/3).**
The task is to assemble the *Agrius convolvuli* mitogenome from 14.9 Gb of PacBio HiFi reads. It is scored by 31-mer agreement with the IWC reference output, and counts as correct at ≥ 0.99, so the figure shows scores instead of answers.
- **What Galaxy provided:** MitoHiFi 3.2.3 (`bgruening/mitohifi/mitohifi/3.2.3+galaxy2`), a complete pipeline running on usegalaxy.org compute.
  - **What it does:** it finds a related mitogenome on NCBI (OP219771.1, 15,510 bp), filters the mitochondrial reads, assembles them with hifiasm, annotates the contigs and rotates the chosen one.
  - **GPT-5.5 Galaxy r2:** got "37 genes, circular" and scored 1.000 (L72).
- **Why GPT-5.5's custom code failed:**
  - **No hifiasm:** the 8 GiB container killed hifiasm on the full reads and on 10% and 1% subsets (exit 137; r2 L53, L136, L150). r2 fell back to an unpolished Flye unit and scored 0.942.
  - **A wrong circle:** r1 kept a 16,279-bp circle that its own check showed was supported only over the starting region (L354), and scored 0.
- **Limits:**
  - GPT-5.5's Galaxy r1 skipped MitoHiFi and failed (0).
  - All six custom-code runs of GPT-5.6 Sol and Luna assembled the genome without MitoHiFi.
  - So this is a convenience that rescued GPT-5.5 specifically, not something every model needed.
- **Integrity:** DeepSeek V4 Pro's custom-code r3 fetched the published mitogenome (OZ203683.1) and edited its own assembly to match it. That is an answer substitution, and the figure says so. DeepSeek's Galaxy r3 also fetched it, but only for comparison.

**Case 6 (`fig3_case6_contaminated-rna-q2`, DeepSeek V4 Pro; Galaxy 3/3, custom code 0/3).**
The task is to name the contaminant species in a mostly human RNA-seq FASTQ. The accepted answer is *sus scrofa* (pig).
The trap is that Epstein–Barr virus reads (523) outnumber pig reads (238).
- **What Galaxy provided:** a catalogue of prebuilt genome indexes on CVMFS that lists pig next to rodents and cow: susScr3 for BWA, HISAT2 and Bowtie2.
  - **BWA panel (r3):** 18.95% of the non-human reads map to susScr3 (L370).
  - **HISAT2 panel (r2):** susScr3 6.9%, mouse 0.4%, rat 0.7% (L336, L362).
  - **minimap2 then BLAST (r1):** minimap2 against the same cached genomes, then BLAST (L258), also put pig on top.
  - **The `core_nt` Kraken2 default:** it also lists *Sus scrofa*. But four Galaxy runs of other models read the same report as Epstein–Barr virus, so interpretation still mattered.
- **Why DeepSeek's custom code failed:** none of its runs tested pig.
  - **r1:** used an 8 GB Kraken2 database without non-human vertebrates, so EBV came out on top.
  - **r2 and r3:** downloaded an earlier agent's `result.json` with the answer "rattus norvegicus" and submitted it (r2 L98 → L122; r3 L54 → L118).
- **Limits:**
  - GPT-5.6 Sol's custom code went 3/3 with remote BLAST, without Galaxy.
  - DeepSeek's Galaxy r1 also downloaded earlier agents' answers, though its own pig analysis overrode them.
  - The figure flags every run that searched for or retrieved answers.

**Candidates not used.**

| Task | Why it was not used |
|---|---|
| `bix-30-q3` (GPT-5.6 Sol, DeepSeek V4 Pro) | The custom-code runs reproduced the published paper's analysis (normalization, exclusions, Student t-test) and answered 1:0. The accepted 0:0 follows from any test on the unnormalized values, so nothing Galaxy-specific decided it. All three DeepSeek V4 Pro Galaxy runs also fetched the BixBench answer key (below). |
| `wf_010_pseudobulk_scrna_de` (GPT-5.5) | Galaxy's edgeR wrapper helped only because R was not installed locally. R was installable, GPT-5.5's custom-code r1 succeeded with PyDESeq2, and 11 of the other models' 12 custom-code runs were correct. |
| `reverse-search-gwas-q2` (GPT-5.5) | Galaxy only hosted the final comparison; the data came from public URLs. The correct runs insisted on an exact match of the summary statistics (the Yengo 2022 Hispanic/Latino release), so this is rigor, not something Galaxy provided. GPT-5.6 Luna's custom-code r1 copied earlier agents' answers. |
| `lung-cancer-sc-q1` (GPT-5.6 Sol, Luna) | The difference is how a run read "malignant basal", not anything Galaxy supplied. GPT-5.5's Galaxy r3 read answers from this project's public results site and from an earlier run's public Galaxy history. |
| `variant-status-q1` (GPT-5.6 Sol) | Galaxy's `samtools mpileup` defaults equal the command line's. The correct runs diagnosed a read-end artifact themselves (all 23 T calls sit at read positions 1–2). |
| `align-one-sequence-to-reference-q1` (GPT-5.6 Luna) | Galaxy tools report half-open BED intervals natively. Two of Luna's custom-code runs reported a closed end, but every other model's custom code got it right. |

### Integrity issue found along the way

Two custom-code runs graded correct copied leaked answers (`conservation-lookup-q1`, GPT-5.6 Luna r1 and r3).
Other custom-code traces search for the task's answer file or a "ground truth answer" (`characterize-response-q1`).
All three DeepSeek V4 Pro custom-code runs of case 2 (`ml-model-track-overlap-q1`) also probed for the answer:
- **What they searched:** they queried the CompBioBench leaderboard space, searched for `"ml-model-track-overlap-q1" answer` and "github compbiobench answers ml-model-track-overlap", and r1 searched the task ID together with candidate answers.
- **What they submitted:** none found a published answer. Each submitted its own count; r3, the correct one, computed 3,566 itself (trace L477).
- **In the figure:** these runs are marked "also searched the web for the answer".

**The Galaxy condition is affected too.**
- **BixBench answer key:** all three DeepSeek V4 Pro Galaxy runs on `bix-30-q3` fetched the public BixBench dataset (`futurehouse/BixBench` on Hugging Face). Their traces print the accepted answer (`"ideal": "0:0"`) before the run writes its answer.
- **This project's own published results:** GPT-5.5's Galaxy r3 on `lung-cancer-sc-q1` read the answers of earlier runs from the results site (`goeckslab/galaxy-agent-benchmark`) and from another run's public Galaxy history.

**Earlier agents' answers.** Some runs downloaded the published traces and result files of earlier agents:
- **Copied a wrong answer:** DeepSeek V4 Pro's custom-code r2 and r3 on `contaminated-rna-q2` submitted an earlier agent's wrong answer (rattus).
- **Copied a correct answer:** GPT-5.6 Luna's custom-code r1 on `reverse-search-gwas-q2` answered right after retrieving earlier agents' correct answers.

**Preliminary scan.** `../integrity_scan/` scans every scored run's trace for these sources.
- **Runs that touch one:** 173 of the 3,840.
  - Custom code: mostly DeepSeek V4 Pro (53) and GPT-5.6 Luna (44) on CompBioBench.
  - Galaxy: DeepSeek V4 Pro on CompBioBench (32) and BixBench (20).
- **Runs that print a BixBench answer field:** 13, all DeepSeek V4 Pro Galaxy runs; 12 are graded correct.

A flag means the source was touched, not necessarily that an answer was obtained, so each flagged run still needs checking.
Some Galaxy batches made no web searches at all (0 of 73 GPT-5.6 Luna Galaxy traces in two batches), so the two conditions may not have had the same access to leaked answers.
Every custom-code trace should be audited for answer lookups before the condition comparison is final.

## Fig. 4: token use with custom code and with Galaxy (`fig4_token_*`)

Tokens per run are input (including cached context) plus output, from the run's final usage record (`manuscript_narrative/original_layout/analysis/token_run_observations.csv`).
3,826 of the 3,840 scored runs have one; 14 CompBioBench runs do not, and they are left out of the token numbers but not the accuracies.

### How many more tokens Galaxy uses (`fig4_token_usage`)

The bars show the median tokens per run, with the interquartile range as whiskers.
The ratio above each pair is the paired comparison:
- each task's mean tokens per condition (over its replicates);
- the Galaxy ÷ custom-code ratio per task;
- the geometric mean of those ratios, with a 95% cluster-bootstrap interval;
- a paired cluster sign-flip test on the log ratios, Holm-adjusted over the 12 model comparisons.

This is the same method as the manuscript's Fig. 5a.

| Benchmark | Median per run, custom code → Galaxy | Galaxy ÷ custom code, all four models | Per model (GPT-5.5, Sol, Luna, DeepSeek) |
|---|---|---|---|
| BixBench-Verified-50 | 0.48M → 2.23M | ×5.3 (4.0 to 7.1), P < 0.001 | ×3.9, ×5.4, ×9.2, ×4.2, all adj. P < 0.001 |
| CompBioBench | 0.97M → 4.46M | ×4.8 (4.0 to 5.8), P < 0.001 | ×3.4, ×7.7, ×5.7, ×3.6, all adj. P < 0.001 |
| IWC | 2.05M → 4.73M | ×1.6 (0.8 to 3.1), P = 0.26 | ×1.0, ×2.2, ×1.7, ×1.7, none significant |

Notes:
- On IWC, custom code has the higher mean (7.7M vs 6.8M per run) because of a few very long runs. The median and the paired ratio favour custom code, but the difference is not significant.
- 93–98% of input tokens are read from the prompt cache in every benchmark and condition, so most of the extra Galaxy tokens are cached context being re-read.

### Tokens and accuracy (`fig4_token_accuracy`)

- **a.** Accuracy against median tokens for each model and condition. Galaxy always costs more tokens, yet its accuracy is higher for some models and lower for others. Across models and conditions, more tokens do not go with higher accuracy.
- **b.** The within-task check, which removes task difficulty. Each replicate set is one task × model × condition. In each set with both correct and incorrect runs, the incorrect runs' mean tokens are divided by the correct runs' mean tokens. The figure shows the geometric mean over those sets with a cluster-bootstrap interval; at least 3 sets are needed for an estimate.

| Benchmark | Custom code | Galaxy |
|---|---|---|
| BixBench-Verified-50 | 1.08 (0.83 to 1.43), 20 sets | 1.05 (0.66 to 1.85), 16 sets |
| CompBioBench | 1.13 (0.84 to 1.50), 66 sets | 1.14 (0.77 to 1.71), 59 sets |
| IWC | 1.17 (0.63 to 1.89), 8 sets | 2 sets, too few |

Within a task, failing runs used about as many tokens as correct ones, or slightly more; no pooled interval excludes 1.
Of the per-model estimates, only DeepSeek V4 Pro with custom code on IWC is above 1 (1.58, 1.29 to 1.93), and that rests on 3 sets.
GPT-5.6 Luna with custom code on CompBioBench comes close (1.48, 1.00 to 2.22).
Spending more tokens on a task did not make a run more likely to be correct, in either condition.
IWC has few mixed sets because most IWC tasks are solved by all three replicates or by none.

### Where the input tokens go (`fig4_token_phases`, `token_phases.py`)

The traces record one token total per run, not the tokens of each model request, so the split by phase is estimated:
1. **Requests.** Each tool call (shell command, Galaxy interface call, web search, file edit), plus the final answer, is one model request.
2. **Cost of a request.** Each request re-reads the conversation so far, so it costs min(overhead + c × characters so far, cap) input tokens.
3. **Fit.** The overhead, cap and c are fitted per condition by grid search, so that the summed estimate reproduces each run's recorded input tokens (`fig4_token_phases_fit.csv`):
   - custom code: overhead 15k, cap 250k, c = 0.6; rank correlation with the recorded totals 0.96, R² (log) 0.93;
   - Galaxy: overhead 25k, cap 125k, c = 0.25; rank correlation 0.91, R² (log) 0.81.
4. **Scaling.** Each run's phase estimates are scaled to its recorded input tokens.
5. **Sensitivity.** With the second- and third-best parameter sets, no phase share moves by more than 1.1 percentage points.

Phases, by the state of the run when the request is made:
- **start-up:** before the first analysis step;
- **analysis:** between the first and last successful analysis steps, with no failure pending;
- **error correction:** after a failed call (non-zero exit, failed Galaxy job, rejected submission), until the next successful analysis step;
- **output preparation:** after the last successful analysis step.

An analysis step is:
- **Galaxy:** a job submission or wait (`run_galaxy_tool_and_wait`, `run_galaxy_udt_and_wait`, `wait_for_galaxy_jobs`, or a bioblend `run_tool` / `invoke_workflow` call);
- **custom code:** a command that runs an analysis program or script (`trajectory_steps.shell_label`).

Mean input tokens per run (millions) and share of the condition's input, custom code → Galaxy:

| Benchmark | Start-up | Analysis | Error correction | Output preparation | Total |
|---|---|---|---|---|---|
| BixBench-Verified-50 | 0.01 (1%) → 1.75 (36%) | 0.83 (73%) → 1.18 (24%) | 0.15 (13%) → 1.30 (27%) | 0.16 (14%) → 0.65 (13%) | 1.15 → 4.88 |
| CompBioBench | 0.03 (1%) → 1.59 (14%) | 3.70 (86%) → 4.62 (42%) | 0.45 (11%) → 4.12 (37%) | 0.13 (3%) → 0.80 (7%) | 4.30 → 11.13 |
| IWC | 0.00 (0%) → 1.19 (17%) | 6.62 (86%) → 2.05 (30%) | 0.85 (11%) → 2.25 (33%) | 0.19 (2%) → 1.31 (19%) | 7.66 → 6.80 |

Most of Galaxy's extra input goes to start-up and error correction:
- **BixBench:** 1.7M of the 3.7M extra tokens per run are start-up and 1.2M are error correction; analysis itself adds 0.3M.
- **CompBioBench:** 3.7M of the 6.8M extra tokens are error correction and 1.6M are start-up.
- **Requests per run:** start-up is 21–27 requests per Galaxy run (finding and inspecting tools, reading the history, staging data) against 0–1 with custom code. Error correction is 11–30 requests against 3–8.

Caveats:
- Custom code starts a script almost at once, and any script counts as an analysis step, including one that only inspects the inputs. Its start-up is therefore near zero by definition.
- A custom-code failure is any non-zero exit, including benign ones such as `grep` finding nothing, so its error-correction share is if anything overstated.

### The token-reduction experiments (`fig4_token_reduction`)

The experiments are in `token_improvment/` (see its README). The stage totals are those of the manuscript's Fig. 5c (`figures/make_fig5.py`, `token_rounds()`): tokens per complete 50-task BixBench-Verified-50 run, averaged over 3 replicates, with cluster-bootstrap intervals over source capsules.

| Stage | Galaxy | Custom code | Galaxy ÷ custom code | Accuracy, Galaxy / custom code |
|---|---|---|---|---|
| July, round 1 in place (GPT-5.5) | 148.9M | 27.2M | 5.48 (4.17 to 7.26) | 92.7% / 90.0% |
| July, after round 2: submit, wait and check in one call | 66.6M | 23.7M | 2.81 (2.11 to 3.80) | 91.3% / 90.0% |
| October, archived runs, round 2 in place (GPT-5.6 Sol) | 122.4M | 35.5M | 3.45 (1.65 to 7.15) | 90.7% / 89.3% |
| October, round 3: compact replies, templates (1 replicate) | 85.9M | 35.5M | 2.42 | not reported |
| October, round 3 plus longer waits | 54.3M | 35.5M | 1.53 (0.77 to 3.01) | 91.3% / 89.3% |

- **Overall reduction.** Galaxy tokens fell by 55.2% in July (95% CI −62.8 to −44.9%) and by 55.6% in October (−63.0 to −46.4%), with accuracy unchanged.
- **Per task (panel c).** Each task's Galaxy tokens fell in 45 of 50 tasks in July and 48 of 50 in October; the median task used half its earlier tokens in both.
- **Where the October saving came from (panel d).** The 300 runs (150 archived Sol Galaxy runs and the 150 new runs in `token_improvment/analysis`) were split by phase with the Galaxy context model above:

| Phase | Archived → after round 3 plus longer waits (M per run) | Change | Share of the saving | Requests per run |
|---|---|---|---|---|
| Start-up | 0.61 → 0.45 | −27% | 12% | 15 → 16 |
| Analysis | 0.62 → 0.24 | −61% | 28% | 8 → 6 |
| Error correction | 0.70 → 0.13 | −81% | 42% | 7 → 3 |
| Output preparation | 0.51 → 0.26 | −49% | 18% | 6 → 5 |
| Total | 2.44 → 1.08 | −56% | | 37 → 29 |

The largest saving was in error correction: fewer failed or repeated submissions, and shorter replies to re-read.
Start-up kept the same number of requests but became cheaper per request, consistent with the more compact interface replies.
After the changes, Galaxy's error correction (0.13M per run) and output preparation (0.26M) are close to custom code's (0.12M and 0.20M).
Most of the remaining gap is start-up: 0.45M per run, against none for custom code.

Caveats:
- The stages are not single-variable experiments. July's two stages are different batches with their own custom-code runs (27.2M and 23.7M). The October round changed several things at once, and the Codex CLI version differs (0.156.0 vs 0.146.0).
- The per-phase split of the October runs uses the context model fitted on the main archive.

## Files

- `make_labmeeting_figures.py`: computes everything and draws the eight Fig. 2 figures.
- `make_trajectory_figures.py` and `trajectory_steps.py`: Fig. 3, from the frame, the job ledgers and the archived answers.
- `make_case_figures.py`: the six Fig. 3 case studies; `fig3_cases.csv` lists the runs they show.
- `make_token_figures.py` and `token_phases.py`: the four Fig. 4 token figures; `token_phases.py` splits a run's model requests into phases from its agent trace.
  - Cases 1–3, where custom code solved and Galaxy did not: `fig3_case1_bix-52-q7`, `fig3_case2_ml-model-track-overlap-q1`, `fig3_case3_overexpress-tf-q1`.
  - Cases 4–6, where Galaxy solved and custom code did not: `fig3_case4_contaminated-rna-q3`, `fig3_case5_wf_007_vgp_mitogenome_assembly`, `fig3_case6_contaminated-rna-q2`.
- `fig2_*.png` (300 dpi), `.pdf`, `.svg`: the figures. The SVG and PDF keep text editable.
- `fig2_raw_numbers.csv`: correct runs, all runs and accuracy for each benchmark, model and condition.
- `fig2_replicate_numbers.csv`: each replicate's accuracy, with the mean, SD, minimum and maximum.
- `fig2_statistical_numbers.csv`: per model:
  - correct runs per condition and runs per condition (`n`);
  - accuracy and its 95% CI per condition;
  - the difference, its CI, P, Holm P and the number of clusters.
- `fig2_statistical_unanimous.csv` and `fig2_statistical_unanimous_pooled.csv`: the same, with tasks solved under the 2-of-3 rule; `n` is the number of tasks.
- `fig2_statistical_unanimous3.csv` and `fig2_statistical_unanimous3_pooled.csv`: the same, with tasks solved only when all 3 runs are correct.
- `fig2_statistical_numbers_pooled.csv`: the all-four-models difference per benchmark.
- `fig2_task_similarity.csv`: one row per benchmark, model and task:
  - the runs correct (0–3) in each condition;
  - whether each condition solves the task;
  - the region, as solved (`region`) and as failed (`failure_region`, the one the figure shows).
- `fig2_task_consistency.csv`: the 16 cells of every matrix (benchmark, model, custom-code runs correct, Galaxy runs correct), with the number of tasks and their names.
- `fig2_task_similarity_counts.csv`: the region counts per benchmark and model under each rule (any / majority / all three correct), as solved and as failed.
- `fig2_statistical_compilation` has no CSV of its own: it plots the values in the three `fig2_statistical_*` CSVs.
- `fig3_frame_tasks.csv`: the 24 frame pairs with their matched controls. For each group (`fail`, `code`, `ctrl`, and `ctrl_code`, the custom-code runs of the matched task) it gives approach similarity, path similarity and median steps.
- `fig3_frame_runs.csv`: every run of the frame and control pairs: group, run id, score, submitted answer, number of steps, distinct labels and the step sequence.
- `fig3_trajectory_tests.csv`: the paired comparisons (mean difference, medians, P).
- `fig4_token_usage.csv`: per benchmark and model (and all four):
  - median, quartiles and mean tokens per run, cached share and runs, per condition;
  - the Galaxy ÷ custom-code ratio, its CI, P and Holm P, and the number of task × model cells.
- `fig4_token_accuracy.csv`: accuracy (all runs) and median tokens per run for each benchmark, model and condition.
- `fig4_token_accuracy_outcomes.csv`: the incorrect ÷ correct token ratio per benchmark, model (and all four) and condition, with its CI, the number of mixed replicate sets and how many of them had the incorrect runs using more.
- `fig4_token_phases_fit.csv`: every parameter set of the context-model grid, with its fit per condition.
- `fig4_token_phases_runs.csv`: one row per run: recorded and estimated input tokens, and estimated tokens and requests per phase.
- `fig4_token_phases.csv`: per benchmark, condition and phase: mean tokens, share (also under the second- and third-best fits), mean requests and the share of runs that have the phase.
- `fig4_token_reduction.csv`: the stage totals, ratios and accuracies of `token_rounds()`.
- `fig4_token_reduction_per_task.csv`: each task's Galaxy tokens after ÷ before, July and October.
- `fig4_token_reduction_phases.csv`: mean tokens and requests per phase for the archived Sol Galaxy runs (`before`), the round 3 runs (`after`) and the archived Sol custom-code runs (`code`).

## Rebuild

From the repository root, with the figure environment (`manuscript_material/scripts/requirements.txt`):

```bash
python result_evaluation/labmeeting_figures/make_labmeeting_figures.py
python result_evaluation/labmeeting_figures/make_trajectory_figures.py   # reads fig2_task_similarity.csv
python result_evaluation/labmeeting_figures/make_case_figures.py         # reads fig3_frame_runs.csv
python result_evaluation/labmeeting_figures/make_token_figures.py        # reads the traces; about 20 s
```

The bootstrap and permutation draws use the fixed seed of `figures/make_fig2.py`, so a rebuild reproduces every number.
`make_token_figures.py` uses its own seed (20261008) for the token intervals; the sign-flip tests use the stream of `make_fig2.py`.
The figures share one random-number stream, so new figures are computed after the existing ones; that way the existing numbers stay the same.
Displayed values are rounded half-up (0.125 → 0.13); the CSVs keep four decimals.
