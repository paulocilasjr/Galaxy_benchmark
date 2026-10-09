# Figure 1 | Study design and isolated execution pipeline

Figure 1 sets out what the study compares and how each run is produced and judged. It shows whether the custom code and Galaxy conditions are balanced in tasks, models and repeats, and which records each run leaves for scoring and audit. Every later figure depends on these choices.

## Fig. 1a | Which benchmarks, conditions and model configurations were compared, and how many runs and scores does the design yield?
panel: fig1a

### Rationale
- **Data.** The schematic summarises the design. The script reads the task counts from the repository (50 BixBench-Verified-50 questions from 33 analysis capsules, 100 CompBioBench questions across eight domains, 10 IWC workflow tasks) and the 4,240 archived runs from the per-run design metadata. The unit is one run: one task, model configuration, condition and replicate.
- **Variables.** Left: the three benchmarks and their scoring (evaluator acceptance, 0 or 1; reconstructed-key agreement, 0 or 1; workflow-output agreement, 0–1). Centre: where each condition ran the analysis, its tools, prompt and time limit, then four model configurations on the Codex agent with three independent runs per condition. Right: the five evaluation outputs.
- **Analysis.** None (schematic); counts only. 160 tasks × 4 model configurations × 2 conditions × 3 runs gives 3,840 primary runs, all of them scored. The IWC host-read removal task is scored from each run's run_record.json, the value the results site shows.
- **Reading the plot.** Read left to right; orange squares are custom-code runs and blue circles Galaxy runs. Footnote marks show that UDTs were not offered on IWC, the 120-min limit applies to CompBioBench custom-code runs and the 6 or 12 h limit to IWC.

### Conclusion
The design crosses 160 tasks with four model configurations, two conditions and three independent runs. This gives 3,840 primary runs, all of them scored. It is balanced in tasks, models and repeats. However, the conditions also differ in prompt (Galaxy adds an execution policy), container or environment, and stated time limit, so they are compared as deployed, not as a single-factor contrast. Replicates measure repeatability, not successive attempts. Scores are benchmark-specific and are not pooled. For CompBioBench, some replicate sets combine runs from different campaigns. One IWC score is self-referential: on the host-read removal task, the minimap2 reference output is byte-identical to the submission of GPT-5.5 custom-code replicate 3.

## Fig. 1b | What does every run go through, and which records does it leave for scoring and audit?
panel: fig1b

### Rationale
- **Data.** The schematic shows the pipeline applied to each of the 3,840 primary runs. It summarises the harness and the scoring procedure, not a measured quantity.
- **Variables.** Prepare puts the prompt and inputs in an isolated workspace, withholds the reference and, for Galaxy runs, creates a history; Execute runs shell commands, or Galaxy jobs and UDTs through MCP. Capture keeps the answer, output files, trace and token counts, plus history provenance for Galaxy runs; Evaluate compares the answer with the reference, and each task's three runs feed the benchmark score.
- **Analysis.** None (schematic).
- **Reading the plot.** Read left to right; blue marks elements of the Galaxy condition only. The lock between Capture and Evaluate is the gate: the reference is opened only after the answer is fixed. In Evaluate, the grid of ticks and crosses shows each run scored on its own before the runs are pooled into a benchmark score.

### Conclusion
Every run follows the same four steps. The reference is opened only after the answer is fixed, so scoring cannot feed back into the answer. Galaxy runs also keep history provenance (datasets, tools, versions, parameters and job states). Custom-code runs keep the answer, trace and token counts, but the benchmark did not retain the files their analysis steps wrote (Fig. 5d), and the CompBioBench host environment was not exported. Withholding the reference from the workspace did not block web access to public benchmark sources. Some runs reached benchmark answers during the run (Extended Data Fig. 6a).

# Extended Data Fig. 6 | Independent checks of the audits and of benchmark integrity

This figure tests two pieces of evidence behind the main results. First, it asks whether some runs reached benchmark answers during the run, and whether that changes the Galaxy–custom code comparison. Second, it asks whether an independent rater reproduces the failure-cause audit and the rule-based failure classes used in the main figures.

## Extended Data Fig. 6a | How many runs reached a source of benchmark answers during the run, and in which benchmark and condition?
panel: ed6a

### Rationale
- **Data.** The panel covers all 3,840 scored primary runs: 600 per condition on BixBench-Verified-50, 1,200 on CompBioBench and 120 on IWC. A rule-based scan searched each trace for web searches, commands and connector calls that touched benchmark sources. Twelve CompBioBench Galaxy runs have no trace and are counted as no search.
- **Variables.** Each run takes its highest tier: *answers seen* (the reference answer, or other agents' recorded answers, appeared in a command or connector output); *opened a page with answers* (the public BixBench dataset or a published archive of agent traces, whose content is not logged); *searched for the benchmark*; or *no benchmark search*. A run is exposed if it falls in either of the first two tiers.
- **Analysis.** Descriptive only (counts and percentages).
- **Reading the plot.** Each bar is 100% of one benchmark × condition, split by tier. The numbers on the right are exposed runs over scored runs.

### Conclusion
Of 3,840 scored runs, 94 (2.4%) were exposed. On BixBench-Verified-50, 12 of 600 custom-code runs and 22 of 600 Galaxy runs were exposed; on CompBioBench, 40 of 1,200 and 20 of 1,200; on IWC, none of 120 in either condition. Another 277 runs searched for the benchmark without opening an answer source. Searching was most common in CompBioBench custom-code runs (223 of 1,200 in any tier). DeepSeek V4 Pro accounts for 79 of the 94 exposed runs. Page content is not logged, so the middle tier is probable exposure, not confirmed exposure.

## Extended Data Fig. 6b | Does the Galaxy–custom code difference in runs correct change when runs that reached or searched for benchmark answers are removed?
panel: ed6b

### Rationale
- **Data.** The panel uses scored runs on BixBench-Verified-50 (1,200) and CompBioBench (2,400). IWC is omitted because no IWC run was exposed. Each benchmark has three populations: all runs; runs outside the two exposure tiers (1,166 and 2,340); and runs with no benchmark search (1,124 and 2,105).
- **Variables.** The estimate is the share of Galaxy runs correct minus the share of custom-code runs correct, in percentage points, with runs pooled within each benchmark. A run is correct when its score is 1.
- **Analysis.** Intervals are 95% cluster-bootstrap percentile intervals. The bootstrap resamples analysis capsules for BixBench-Verified-50 and tasks for CompBioBench.
- **Reading the plot.** Filled diamonds are all runs and open circles are the reduced populations. Horizontal lines are 95% intervals. Points right of zero favour Galaxy.

### Conclusion
Removing exposed runs left the condition difference almost unchanged. On BixBench-Verified-50 it was +0.5 points (95% interval −3.9 to 4.8) with all runs and +0.6 (−4.0 to 5.1) without exposed runs. On CompBioBench it was +0.3 (−1.8 to 2.5) and +0.2 (−2.0 to 2.4). Removing every run that searched gave +0.9 (−3.7 to 5.3) on BixBench-Verified-50 and −1.3 (−3.9 to 1.1) on CompBioBench. No difference was detected in any population. The removed runs are not a random subset (mostly DeepSeek V4 Pro runs), so these are sensitivity checks, not unbiased estimates.

## Extended Data Fig. 6c | Does an independent rater assign the same primary failure cause as the original audit to incorrect BixBench-Verified-50 runs?
panel: ed6c

### Rationale
- **Data.** The sample is 45 BixBench-Verified-50 runs graded incorrect at the time of the audit (23 Galaxy, 22 custom code), stratified by the original audit's cause and by condition. Seven of them (six on bix-53-q2, one on bix-43-q2) are graded correct on the results site after the regrades of those two tasks, so the check measures agreement on the cause as audited. The second rater was an AI coder, blind to the audit, that read each run's transcript, submitted answer and reference answer.
- **Variables.** Rows give the original audit's primary cause and columns the second rater's. Causes are grouped as in Fig. 2d: Validation (no answer validation), Benchmark (specification or scoring), Knowledge, Galaxy (platform) and No answer. Cells count runs.
- **Analysis.** Percent agreement and Cohen's κ on the primary cause group. A second measure also counts a run as agreeing when one rater's secondary cause matches the other's primary cause.
- **Reading the plot.** Agreements lie on the diagonal (bold). Darker cells hold more runs.

### Conclusion
The second rater chose the same primary cause group in 35 of 45 runs (78%; κ = 0.56), or 96% when secondary causes count. It confirmed 27 of the 30 runs that the audit attributed to the benchmark, including all seven runs now graded correct after the regrades. Most disagreements were between Validation and Benchmark (3 runs each way). One of the two Galaxy-attributed runs was recoded as Validation. Agreement on the Knowledge, Galaxy and No answer groups rests on two or three runs each. This is an AI-assisted second rating, not human validation, and the original audit was also AI-assisted, so the two raters may share biases.

## Extended Data Fig. 6d | Does an independent rater reproduce the rule-based failure classes of failed Galaxy requests?
panel: ed6d

### Rationale
- **Data.** The sample is 150 failed Galaxy requests, 10 from each of 15 rule-based classes. A1–A8 are requests rejected before a job ran, B1–B5 are jobs that failed, X is other exceptions and Z is unclassified. An AI coder, blind to the rule's class, assigned a class and one or more changes that would plausibly have prevented the failure.
- **Variables.** Each bar is the percentage of a class's 10 requests that the rater put in the same class. The subtitle also compares the rater's prevention choices with the improvement group the rule links to each class, over the 120 requests whose class has a group (B3, X and Z have none).
- **Analysis.** Percent agreement and Cohen's κ over the 130 requests in classes A1–B5. The panel also gives the share of requests judged agent error only and the share with more than one plausible improvement.
- **Reading the plot.** A full bar means all 10 requests were reproduced. X and Z have no bars because they have no rule definition to reproduce.

### Conclusion
The rater reproduced the rule's class for 92% of classified requests (κ = 0.92). It matched every request in 8 of 13 classes. Agreement was lowest for B4, input format (60%), and A4, parameter value or datatype (70%). For 89% of the requests whose class has an improvement group (107 of 120), the rule's group was among the rater's choices. This match is lenient, because the rater could name several improvements and did so in 35% of requests. It judged only 3% of failures to be agent error alone. This is an AI-assisted second rating, not human validation.

# Extended Data Fig. 7 | Verification, recovery and selected cases

This figure looks at what agents did inside their runs. It asks whether they checked their own analyses, whether they re-ran failed steps without error, and what such checks look like in two worked cases. These results bear on the paper's claim that verification, more than execution, limits reliable agent analyses.

## Extended Data Fig. 7a | How often did agents check their own analysis, and did checks differ between correct and incorrect runs or between conditions?
panel: ed7a

### Rationale
- **Data.** The sample is 80 primary runs, drawn at 10 per benchmark (BixBench-Verified-50, CompBioBench) × condition × outcome, with at most one run per task in each stratum; IWC is not sampled. The outcome plotted is the current grade: one run drawn as incorrect (bix-53-q2, GPT-5.6 Luna, Galaxy, replicate 1) is correct after that task's regrade. AI coders read condensed transcripts, blind to the grade but not to the condition.
- **Variables.** Six kinds of check, plus *any check*, each counted only when the agent explicitly tested something its answer depended on. The left plot compares correct and incorrect runs (41 and 39) and the centre plot custom code and Galaxy (40 each); the text on the right gives the runs in which a check changed the method or the answer.
- **Analysis.** Percentages with 95% Wilson intervals. Descriptive only; no tests. One plausibility code was removed because it recorded a download of the BixBench answer file.
- **Reading the plot.** Each point is the share of runs with the check, and each line is its 95% interval.

### Conclusion
Checks were about as common in correct as in incorrect runs (any check, 87.8%, 95% interval 74.5–94.7, vs 87.2%, 73.3–94.4). Count checks (61.0% vs 43.6%) and independent recomputation (41.5% vs 25.6%) were more frequent in correct runs, but the intervals overlap. Custom-code runs had more checks than Galaxy runs (any check, 95.0%, 83.5–98.6, vs 80.0%, 65.2–89.5). The intervals do not overlap for count checks (70.0% vs 35.0%) or sensitivity analyses (62.5% vs 25.0%). A check changed the method or answer in 6 of 41 correct and 11 of 39 incorrect runs. The sample was drawn balanced, not representative of all runs, so these are not population rates or causal effects.

## Extended Data Fig. 7b | How often was a failed step re-run without error later in the same run, and did those runs end correct more often?
panel: ed7b

### Rationale
- **Data.** The panel covers 6,114 failed steps in scored primary runs on all three benchmarks, 53 of them on the IWC host-read removal task. These are 1,068 installed-tool and 1,922 UDT Galaxy jobs in the error state, and 884 failed shell commands in Galaxy runs and 2,240 in custom-code runs. A shell command counts only if it ran a named analysis program or script.
- **Variables.** A Galaxy job is resolved if a later job of the same tool completed (for UDTs, any later UDT job), and a shell command if a later command of the same program or script exited 0. The right-hand column is the share of failed steps whose run ended correct, for resolved and unresolved steps; it is weighted by failed step, so runs with many failures count more.
- **Analysis.** Intervals are 95% cluster-bootstrap intervals; clusters are analysis capsules for BixBench-Verified-50 and tasks otherwise. The right-hand shares are descriptive.
- **Reading the plot.** Blue bars are Galaxy runs and the orange bar is custom-code runs. Black lines are 95% intervals.

### Conclusion
In every channel, 54–62% of failed steps were later re-run without error. The shares were 62% (95% interval 54.7–68.0) for installed-tool jobs and 56% (46.7–64.1) for UDT jobs. For shell commands they were 56% (50.2–60.8) in Galaxy runs and 54% (50.1–56.9) in custom-code runs. The intervals overlap and no formal comparison was made. Final correctness differed by less than 7 points between resolved and unresolved failures, and not in a consistent direction (82% vs 76% for installed-tool jobs, 71% vs 77% for custom-code shell commands). Resolution means the step later ran without error, not that the error was understood or the result was right.

## Extended Data Fig. 7c | What happens when the Galaxy interface detects that a request would not set the parameter the agent asked for?
panel: ed7c

### Rationale
- **Data.** One selected run: bix-43-q4 (Reactome enrichment), GPT-5.5, Galaxy condition, replicate 1. The script hard-codes this run and, from its trace, extracts the first gseapy_enrichr request that the interface stopped with a parameter mismatch, and the next request to that tool that completed (trace lines 63 and 70).
- **Variables.** The rows give the task, the tool and version, and the structure of the first request. They then give the interface check (requested value against the value Galaxy would bind), the agent's response and the second request.
- **Analysis.** None; this is a worked example. The repository records no rule for choosing this run; it illustrates the mechanism.
- **Reading the plot.** Read the rows from top to bottom as the order of events in the run.

### Conclusion
In this run, the agent first put the gene-set library inside a nested structure. The interface found that Galaxy would bind gene_sets|library_name to an empty value instead of Reactome_2022, so it did not submit the job. The agent resubmitted with flat parameter keys, the parameters matched and the job ran. The case shows that the interface check can stop a job that would otherwise run silently with a wrong parameter. It is one selected case. It does not estimate how often this happens, and matching parameters do not show that the analysis was scientifically appropriate.

## Extended Data Fig. 7d | In a task where read-end artefacts mimic an alternate allele, which runs ran a read-position diagnostic, and which were accepted?
panel: ed7d

### Rationale
- **Data.** All 24 primary runs on one selected CompBioBench task, variant-status-q1 (4 model configurations × 2 conditions × 3 replicates). The task is one of the worked cases from the failure-cause audit, in which read-end artefacts were taken for alleles and contrasted with a read-position audit.
- **Variables.** Filled circles are accepted runs and open circles rejected runs. A box marks a run that ran a read-position diagnostic (blue, a UDT in Galaxy; orange, a command in custom code). Runs are flagged by a text pattern (read position, cycle or end) in a UDT call or shell command, so diagnostics inside separately written scripts may be missed.
- **Analysis.** Descriptive only (counts).
- **Reading the plot.** Rows are model configurations. Within each condition, the three markers are replicates 1–3. Answers are not shown.

### Conclusion
Four of 24 runs were accepted. Five runs ran the read-position diagnostic, and three of these were accepted. GPT-5.6 Sol in Galaxy ran it as a UDT in replicates 2 and 3, and both were accepted. Of the three custom-code runs with the diagnostic, one was accepted (DeepSeek V4 Pro, replicate 2). Only one of the 19 runs without a detected diagnostic was accepted. The case shows that a UDT let an agent run a domain diagnostic inside Galaxy. With five diagnostic runs on one selected task, it cannot show that the diagnostic causes acceptance or how often agents run such checks.
