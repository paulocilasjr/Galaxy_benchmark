# Figure legends

Supplementary Table numbers follow `supplementary/Supplementary_Table_crosswalk.csv`. Unless stated otherwise, intervals are exploratory 95% percentile cluster-bootstrap confidence intervals (20,000 resamples). Resampling units are source capsules for BixBench-Verified-50 and tasks for CompBioBench and IWC. Intervals are pointwise, not adjusted for multiplicity, and support no equivalence, non-inferiority or causal claim.

Visual conventions, the same in every figure:
- Open-ended code is the reference condition and is always shown first.
- Vermillion squares are open-ended code; blue circles are Galaxy.
- Colours come from the Okabe–Ito palette, which is distinguishable under common forms of colour-vision deficiency (Wong, B. *Nat. Methods* **8**, 441; 2011).
- Marker shape repeats the environment so that it survives greyscale printing.

## Main figures

**Fig. 1 | Study design: the same AI agents analyse biological data in open-ended code or through the Galaxy workbench.**
**a**, Open-ended code, the reference condition. The agent uses an unrestricted shell that can install and run any software. Commands, scripts, command output and final files are recorded, but there is no record of individual analysis jobs.
**b**, Galaxy-mediated condition. The same model and agent harness (Codex) reach the Galaxy server (usegalaxy.org) through a Model Context Protocol interface. The interface offers tool search, tool parameter descriptions, history inspection, job submission and monitoring, and user-defined tools, which run agent-written code as Galaxy jobs. Galaxy records tool identities and versions, requested and resolved parameters, datasets, job states and error messages.
**c**, Benchmarks and runs; numbers are archived runs (tasks × 3 replicates per configuration and environment). BixBench-Verified-50 and CompBioBench contain platform-neutral questions; IWC tasks are derived from published Galaxy workflows. Their endpoints differ, so the benchmarks are analysed separately and never pooled (Supplementary Table 1). The Claude Code harness for DeepSeek V4 Pro was superseded and is reported separately. GPT-6 Astra is unpaired and excluded from environment contrasts. Archive: 4,240 runs, 4,228 agent traces, 23,080 Galaxy analysis jobs and 69,812 Galaxy interface calls (Extended Data Fig. 1a).

**Fig. 2 | Agents reach similar accuracy in Galaxy and in open-ended code, and most of their failures are not caused by Galaxy.**
**a–c**, Galaxy minus open-ended code for each benchmark, with 95% confidence intervals; values are printed beside each estimate, and positive values mean Galaxy scored higher. Configurations appear in the same rows in every panel, followed by the four Codex configurations pooled. The line under each title gives the pooled scores in each environment.
**a**, BixBench-Verified-50: difference in accepted answers, in percentage points (Supplementary Table 2).
**b**, CompBioBench: difference in mean aggregate score (answers credited, of 100) over three archived score vectors per environment. Open points have no interval, because the archive keeps only aggregate scores, some labelled predicted. GPT-6 Astra, run only with open-ended code and not paired, scored 93 (Supplementary Tables 5 and 6).
**c**, IWC: difference in mean agreement with the workflow reference output over the nine tasks scored in both environments (Supplementary Table 7).
**d**, IWC agreement of every replicate on all ten tasks. Ticks mark means, and the axis is broken between 0.45 and 0.80. Numbered notes give the trace-established cause of every score below 0.5 (Supplementary Table 18; Extended Data Fig. 2d).
**e**, Primary and secondary cause of every rejected BixBench-Verified-50 run (135 open-ended code, 111 Galaxy), established call by call (Supplementary Table 14; Supplementary Note 6). Galaxy was a primary or secondary cause in 22 of 111 Galaxy rejections.

**Fig. 3 | Agents use Galaxy as a structured analysis environment whose records reveal input, parameter and silent-substitution errors.**
All panels show Galaxy runs.
**a**, Share of Galaxy runs that used each workbench operation, per benchmark (Supplementary Table 20).
**b**, The six most frequently used tools per benchmark, by number of Galaxy jobs. Dark bars are domain-analysis tools and light bars are file or table utilities; hatched segments are jobs that ended in error. Headers give the share of all Galaxy jobs run with domain-analysis tools (Supplementary Tables 11 and 21–23).
**c**, Galaxy runs that requested a user-defined tool (light bars) and that ran at least one successfully (dark bars). IWC runs were not offered the facility (Supplementary Tables 24 and 27).
**d**, Recurring error messages, each as a share of all error jobs of the same tool; labels give counts (Supplementary Table 32).
**e**, Outcome of tool-run calls to the Galaxy interface (Codex harness). Across benchmarks, 4,352 calls requested values that Galaxy would change or drop: the benchmark's check blocked 3,436 before submission, and 916 ran with the changed values. The right-hand table shows examples (Supplementary Table 37; Supplementary Data 3).

**Fig. 4 | Solution paths vary by model and benchmark, and Galaxy replicates agree more often and diverge for different reasons.**
**a**, Software used, as a percentage of runs, for the three GPT configurations shared by all benchmarks. For open-ended code, software is taken from names in shell commands; for Galaxy, from installed tools in job records. The two measures are not directly comparable (Supplementary Table 39).
**b**, Similarity of the Galaxy tool sets used by the three replicates of a task (mean pairwise Jaccard index; 1 = identical), by configuration and benchmark (Supplementary Tables 41–43).
**c**, Non-unanimous triplicates, which the text calls mixed cells: a task run three times with one configuration and environment, where only 1 or 2 replicates succeeded. Definitions of success by benchmark appear under the panel title. CompBioBench uses the 82 tasks with a strong consensus answer (Supplementary Table 44; Supplementary Note 8).
**d**, What separated each rejected replicate from its accepted siblings in non-unanimous BixBench-Verified-50 triplicates (45 open-ended code, 36 Galaxy), identified by comparing traces (Supplementary Table 48).

**Fig. 5 | Galaxy raises input-token use, mostly for finding and inspecting tools, in exchange for an inspectable analysis record.**
**a**, Ratio of Galaxy to open-ended-code input tokens for each paired task and configuration (median of three runs per environment; log scale). Black symbols give the median with 95% confidence interval (Supplementary Tables 49–51).
**b**, Per-run share of Galaxy interface calls (solid boxes) and of text returned to the agent (hatched boxes) taken up by tool search and inspection. Boxes span the middle 50% of runs with the median marked; whiskers extend to 1.5 times the interquartile range; outliers are not shown (Supplementary Table 53).
**c**, For each configuration relative to GPT-5.5 in the same environment on the same 50 BixBench-Verified-50 tasks: input tokens as a ratio (left) and accepted answers in percentage points (right), with 95% confidence intervals. Dashed lines mark GPT-5.5 (Supplementary Table 54).
**d**, Findings recoverable only from the Galaxy record (left). Right, share of divergent rejected replicates caused by hand-written methods or software-version differences (open-ended code, 30 of 45; Galaxy, 5 of 36).

## Extended Data figures

**Extended Data Fig. 1 | Evidence archive, audit pipeline and validation of the CompBioBench consensus proxy.**
**a**, Archived evidence per benchmark; jobs are counted once per server and job identifier.
**b**, Trace-level audit pipeline (Supplementary Notes 1–3, 6 and 8).
**c**, For the 22 archived CompBioBench score vectors with retained answers: answers matching the most common answer across the 25 runs of each task, plotted against the archived score. Open symbols are scores labelled predicted in the archive. Dashed line, identity. Mean absolute error 2.6 of 100; mean bias +2.0.
**d**, Number of the 25 runs per task that gave the most common answer. The 82 tasks where at least 20 runs agree define the strong consensus used for probable failures and non-unanimous triplicates (Supplementary Table 6; Supplementary Note 7).

**Extended Data Fig. 2 | Tool-set similarity across benchmarks and four cases that explain environment-specific outcomes.**
**a**, Similarity of replicate tool sets (mean pairwise Jaccard index, 95% confidence interval) for the three shared GPT configurations; numbers of triplicates are given in the labels. The two environments are measured differently, so compare benchmarks within an environment (Supplementary Table 10).
**b**, bix-45-q1: submitted Mann–Whitney *P* value for every run; open symbols were rejected. The dashed line is the accepted reference, reproduced by PhyKIT 2.0.3. The dotted line is the value from the current PhyKIT release and from the Galaxy tool, whose software version is not shown to the agent (Supplementary Tables 15 and 16).
**c**, bix-43-q2: submitted odds ratios. The blue band is the accepted range. Grey rows (both DeepSeek V4 Pro configurations) were scored by the rounded-numeric verifier; other rows by the tolerance verifier. One value of 7.17 lies off scale (Supplementary Table 17).
**d**, Re-examination of low IWC scores.
- Left: overlap of each submitted mitochondrial contig with the public *Agrius convolvuli* genome OZ203683.1 (F1 score of shared 31-base sequences; n = 24).
- Right: read pairs kept after host-read removal by the Galaxy output that scored 0.273, and by the two reference routes (Supplementary Tables 13 and 18).

**Extended Data Fig. 3 | Reliability of user-defined tools, causes of failed Galaxy interface calls, and engineering targets.**
**a**, Top, status of 4,960 calls that ran a user-defined tool (Codex harness). Bottom left, failed jobs by tool type, failure phase and presence of an error message (black: none). Bottom right, the next call after a failure with no error message (Supplementary Table 28).
**b**, Failed Galaxy interface calls per 1,000 calls, by cause and benchmark, grouped by whether a job had been created; 258 calls matching no cause are not shown (Supplementary Table 34; Supplementary Note 3).
**c**, The 14 tools with the most calls whose requested parameter values Galaxy changed or dropped (Supplementary Table 37).
**d**, Engineering targets, each with the evidence in the traces and a measure of success on a replay of the same tasks (Supplementary Table 38).

**Extended Data Fig. 4 | Replicate outcomes by configuration, and no support for a task-difficulty explanation.**
**a**, BixBench-Verified-50 triplicate outcomes per configuration and environment (50 tasks each); the right-hand column counts non-unanimous triplicates (Supplementary Table 44).
**b**, Spearman correlation, with 95% confidence interval, across tasks between task description length or recorded workload and failure markers. Three shared GPT configurations; 5,000 bootstrap resamples with ties re-ranked. Prompt length measures specification burden, not difficulty (Supplementary Table 45).

**Extended Data Fig. 5 | Token overhead across benchmarks, and direct use of Galaxy's programming interface.**
**a**, Median Galaxy ÷ open-ended-code input-token ratio, with 95% confidence interval, per configuration and benchmark and pooled over the three shared configurations. IWC-to-BixBench-Verified-50 overhead contrast: 0.36 (0.15–0.91; Supplementary Table 52).
**b**, Share of Galaxy runs (Codex harness) that performed each operation by calling Galaxy's programming interface from the shell (BioBlend library or direct web requests) rather than through the agent interface. The provided input history exists only in BixBench-Verified-50 (Supplementary Table 53).
