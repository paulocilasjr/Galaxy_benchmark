# Figure legends

Terms follow the glossary in `glossary/Glossary.md`, which is also given in the Supplementary Information.

Supplementary Table numbers follow `supplementary/Supplementary_Table_crosswalk.csv`.

Unless stated otherwise, intervals are exploratory 95% percentile cluster-bootstrap confidence intervals (20,000 resamples). Resampling units are source capsules for BixBench-Verified-50 and tasks for CompBioBench and IWC. Intervals are pointwise, not adjusted for multiplicity, and support no equivalence, non-inferiority or causal claim.

Visual conventions, the same in every figure:
- The open-ended code condition is the reference condition and is always shown first.
- A condition difference is always Galaxy condition minus open-ended code condition.
- Vermillion squares are the open-ended code condition; blue circles are the Galaxy condition.
- Colours come from the Okabe–Ito palette, which is distinguishable under common forms of colour-vision deficiency (Wong, B. *Nat. Methods* **8**, 441; 2011).
- Marker shape repeats the execution condition, so it survives greyscale printing.

## Main figures

**Fig. 1 | Study design: the same model configurations perform each task in the open-ended code condition and in the Galaxy condition.**
**a**, Open-ended code condition (open-ended code execution), the reference condition. The agent uses an unrestricted shell that can install and run any software. Its execution trace records commands, scripts, command output and final files, but no individual analysis jobs.
**b**, Galaxy condition (Galaxy-mediated execution). The same model configuration, run by the Codex agent harness, reaches the Galaxy server (usegalaxy.org) through the Galaxy interface, a Model Context Protocol server. The interface offers tool search, tool parameter descriptions, analysis-history inspection, job submission and monitoring, and user-defined tools. The execution trace and analysis history record tool identities and versions, requested and resolved parameters, datasets, job states and error messages. The condition label records assignment; it does not certify that every operation ran inside Galaxy.
**c**, Run populations. Each cell gives the number of runs (tasks × 3 replicate runs) per model configuration and execution condition.
- BixBench-Verified-50 and CompBioBench are platform-neutral benchmarks; IWC is a workflow-derived benchmark.
- Endpoints differ: accuracy for BixBench-Verified-50, reported benchmark scores for CompBioBench and output agreement for IWC. The benchmarks are therefore analysed separately and never pooled (Supplementary Table 1).
- DeepSeek V4 Pro (Claude Code, superseded) is reported separately. GPT-6 Astra is unpaired and excluded from condition differences.

Archive totals: 4,240 runs, 4,228 execution traces, 23,080 Galaxy analysis jobs and 69,812 Galaxy interface calls (Extended Data Fig. 1a).

**Fig. 2 | Performance is similar in the two execution conditions, and most scored-incorrect runs were not caused by Galaxy.**
**a–c**, Condition difference (Galaxy − open-ended code) for each benchmark, with 95% confidence intervals.
- Each estimate is printed beside its interval; positive values mean the Galaxy condition scored higher.
- Model configurations occupy the same rows in every panel, followed by the four Codex model configurations pooled.
- The line under each title gives the pooled condition-level summary for each execution condition.

**a**, BixBench-Verified-50: condition difference in accuracy, in percentage points (run population per condition: 50 tasks × 3 replicate runs per model configuration; Supplementary Table 2).
**b**, CompBioBench: condition difference in the mean reported benchmark score (answers credited, of 100) over three replicate runs per condition. Open points have no interval, because the archive keeps only reported benchmark scores, some labelled predicted. GPT-6 Astra (open-ended code condition only, not paired) scored 93 (Supplementary Tables 5 and 6).
**c**, IWC: condition difference in mean output agreement over the nine tasks scored in both conditions (Supplementary Table 7).
**d**, IWC output agreement of every run on all ten tasks. Ticks mark the mean of 12 replicate runs, and the axis is broken between 0.45 and 0.80. Numbered notes give the cause of every run below 0.5, established from its execution trace. Note 4 is a score conflict (Supplementary Table 18; Extended Data Fig. 2d).
**e**, Primary and secondary cause of every scored-incorrect BixBench-Verified-50 run (135 open-ended code condition, 111 Galaxy condition), adjudicated from execution traces (Supplementary Table 14; Supplementary Note 6).

**Fig. 3 | Agents use Galaxy as a structured analysis workbench whose records reveal input errors, parameter errors and parameter substitution.**
All panels show Galaxy-condition runs.
**a**, Share of Galaxy-condition runs that used each workbench operation, per benchmark (Supplementary Table 20).
**b**, The six most frequently used installed Galaxy tools per benchmark, by number of Galaxy analysis jobs. Dark bars are domain tools, light bars utility tools, and hatched segments Galaxy job errors. The headers give the share of Galaxy analysis jobs run with domain tools (Supplementary Tables 11 and 21–23).
**c**, Galaxy-condition runs that requested a user-defined tool (light bars), and those with at least one successful user-defined-tool job (dark bars), by model configuration. IWC runs were not offered user-defined tools (Supplementary Tables 24 and 27).
**d**, Recurring error messages, each as a share of all Galaxy job errors of the same tool; labels give counts (Supplementary Table 32).
**e**, Outcome of tool-run calls to the Galaxy interface (Codex agent harness). Parameter substitution occurred in 4,352 calls: the benchmark's check blocked 3,436 before submission, and 916 were executed. The table shows examples (Supplementary Table 37; Supplementary Data 3).

**Fig. 4 | Tool-set fingerprints vary by model configuration and benchmark; the Galaxy condition has fewer split replicate sets, and they split for different reasons.**
**a**, Software used, as a percentage of runs, for the three GPT model configurations shared by all benchmarks.
- Open-ended code condition: command names in shell commands.
- Galaxy condition: installed Galaxy tools in job records.

The two tool-set fingerprints are not directly comparable (Supplementary Table 39).
**b**, Galaxy tool-set similarity within replicate sets (mean pairwise Jaccard similarity; 1 = identical), by model configuration and benchmark (Supplementary Tables 41–43).
**c**, Split replicate sets, defined under the panel title. CompBioBench uses the 82 tasks with a strong consensus answer, a consensus proxy (Supplementary Table 44; Supplementary Note 8).
**d**, Divergence mechanism of every scored-incorrect replicate run in a split BixBench-Verified-50 replicate set (45 open-ended code condition, 36 Galaxy condition). Each was identified by comparing its execution trace with those of its scored-correct siblings (Supplementary Table 48).

**Fig. 5 | The Galaxy condition raises input-token usage, mostly for finding and inspecting tools, in exchange for an inspectable analysis record.**
**a**, Input-token ratio (Galaxy ÷ open-ended code) for each task × model configuration, on a log scale; black symbols give the median with its 95% confidence interval (Supplementary Tables 49–51).
**b**, Per-run share of Galaxy interface calls (solid boxes) and of text returned to the agent (hatched boxes) taken up by tool search and inspection. Boxes span the middle 50% of runs and mark the median; whiskers extend to 1.5 times the interquartile range; outliers are not shown (Supplementary Table 53).
**c**, Each model configuration against GPT-5.5 in the same execution condition, on the same 50 BixBench-Verified-50 tasks, with 95% confidence intervals:
- left, input-token usage as a ratio;
- right, model difference in accuracy, in percentage points.

Dashed lines mark GPT-5.5 (Supplementary Table 54).
**d**, Left, findings recoverable only from the Galaxy record. Right, the share of scored-incorrect replicate runs in split replicate sets whose divergence mechanism was a hand-written method or a software-version difference: 30 of 45 in the open-ended code condition and 5 of 36 in the Galaxy condition.

## Extended Data figures

**Extended Data Fig. 1 | Evidence archive, audit pipeline and validation of the CompBioBench consensus proxy.**
**a**, Archived evidence per benchmark; Galaxy analysis jobs are counted once per server and job identifier.
**b**, Audit pipeline from execution traces to adjudicated causes and divergence mechanisms (Supplementary Notes 1–3, 6 and 8).
**c**, For the 22 CompBioBench reported benchmark scores with retained answers, the number of answers matching the consensus answer, plotted against the reported score. Open symbols are scores labelled predicted; the dashed line is identity. Mean absolute error 2.6 of 100; mean bias +2.0.
**d**, Runs per task that gave the consensus answer. The 82 tasks where at least 20 of 25 runs agree define the strong consensus (Supplementary Table 6; Supplementary Note 7).

**Extended Data Fig. 2 | Tool-set similarity across benchmarks and four cases that explain condition-specific outcomes.**
**a**, Tool-set similarity within replicate sets (mean pairwise Jaccard similarity, 95% confidence interval) for the three shared GPT model configurations; numbers of replicate sets are given in the labels. Tool-set fingerprints are measured differently in the two conditions, so compare benchmarks within a condition (Supplementary Table 10).
**b**, bix-45-q1, a task-level condition difference: the submitted Mann–Whitney *P* value of every run; open symbols are scored incorrect. The dashed line is the reference answer, which PhyKIT 2.0.3 reproduces. The dotted line is the value from the current PhyKIT release and from the installed Galaxy tool, whose software version the agent could not see (Supplementary Tables 15 and 16).
**c**, bix-43-q2: submitted odds ratios. The blue band is the range scored correct. Grey rows (both DeepSeek V4 Pro model configurations) were scored under the rounded-numeric verifier mode, other rows under the tolerance verifier mode. One value of 7.17 lies off scale (Supplementary Table 17).
**d**, Low IWC output agreement re-examined.
- Left: overlap of each submitted mitochondrial contig with the public *Agrius convolvuli* genome OZ203683.1 (F1 score of shared 31-base sequences; n = 24).
- Right: a score conflict in host-read removal, shown as read pairs kept by the Galaxy output and by the two reference routes (Supplementary Tables 13 and 18).

**Extended Data Fig. 3 | Reliability of user-defined tools, causes of failed Galaxy interface calls, and engineering targets.**
**a**, Top, status of 4,960 user-defined-tool calls (Codex agent harness). Bottom left, Galaxy job errors by tool type, phase and presence of an error message; black bars mark errors with no message. Bottom right, the next call after a Galaxy job error with no error message (Supplementary Table 28).
**b**, Failed Galaxy interface calls per 1,000 calls, by cause and benchmark, grouped by whether a job was created. 258 unclassified calls are not shown (Supplementary Table 34; Supplementary Note 3).
**c**, The 14 installed Galaxy tools with the most parameter substitution (Supplementary Table 37).
**d**, Engineering targets, each with its evidence in the execution traces and a measure of success on a replay of the same tasks (Supplementary Table 38).

**Extended Data Fig. 4 | Repeatability categories by model configuration, and no support for a task-difficulty explanation.**
**a**, Repeatability categories of BixBench-Verified-50 replicate sets per model configuration and execution condition (50 tasks each): 3/3, split (1–2/3) or 0/3 replicate runs scored correct (Supplementary Table 44).
**b**, Spearman correlation, with 95% confidence interval, between prompt length or workload and operational errors (nonzero shell exits or Galaxy job errors), computed across tasks. It uses the three shared GPT model configurations and 5,000 bootstrap resamples with ties re-ranked. Prompt length measures how much the task specifies, not its difficulty (Supplementary Table 45).

**Extended Data Fig. 5 | Input-token ratio across benchmarks, and direct Galaxy API calls.**
**a**, Median input-token ratio (Galaxy ÷ open-ended code) with 95% confidence interval, per model configuration and benchmark and for the three shared model configurations pooled. The IWC-to-BixBench-Verified-50 contrast is 0.36 (0.15–0.91; Supplementary Table 52).
**b**, Share of Galaxy-condition runs (Codex agent harness) that performed each operation through a direct Galaxy API call, using the BioBlend library or web requests outside the Galaxy interface. A provided analysis history exists only in BixBench-Verified-50 (Supplementary Table 53).
