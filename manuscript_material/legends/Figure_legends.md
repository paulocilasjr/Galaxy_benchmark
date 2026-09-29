# Figure legends

Terms follow the glossary in `glossary/Glossary.md`, which is also given in the Supplementary Information.

Supplementary Table numbers follow `supplementary/Supplementary_Table_crosswalk.csv` and match the citations in the Results text.

Unless stated otherwise, intervals are exploratory 95% percentile cluster-bootstrap confidence intervals (20,000 resamples). Resampling units are source capsules for BixBench-Verified-50 and tasks for CompBioBench and IWC. Intervals are pointwise, not adjusted for multiplicity, and support no equivalence, non-inferiority or causal claim (Supplementary Note 9).

Visual conventions, the same in every figure:
- The open-ended code condition is the reference condition and is always shown first.
- A condition difference is always Galaxy condition minus open-ended code condition.
- Vermillion squares are the open-ended code condition; blue circles are the Galaxy condition.
- Colours come from the Okabe–Ito palette, which is distinguishable under common forms of colour-vision deficiency (Wong, B. *Nat. Methods* **8**, 441; 2011).
- Marker shape repeats the execution condition, so it survives greyscale printing.

## Main figures

**Fig. 1 | Study design: the same model configurations perform each task in the open-ended code condition and in the Galaxy condition.**
**a**, Open-ended code condition, the reference condition. The model configuration and its agent harness write and run code and command-line tools in an unrestricted shell that can install any software. The execution trace records commands, scripts, command output and final files, but no individual analysis jobs.
**b**, Galaxy condition (Galaxy-mediated execution). The same model configuration and agent harness reach the Galaxy server (usegalaxy.org) through the Galaxy interface, a Model Context Protocol server. The interface offers tool search, tool parameter descriptions, analysis-history inspection, job submission and monitoring, and user-defined tools, which run agent-written code as Galaxy jobs. The local shell is meant only for staging files and extracting the answer. The execution trace and analysis history record tool identities and versions, requested and resolved parameters, datasets, job states and error messages. The condition label records assignment to an experimental arm; it does not certify that every operation ran inside Galaxy.
**c**, Run populations. Each cell gives the number of runs (tasks × 3 replicate runs) per model configuration and execution condition.
- BixBench-Verified-50 and CompBioBench are platform-neutral benchmarks; IWC is a workflow-derived benchmark built from published Galaxy workflows.
- Endpoints differ: accuracy for BixBench-Verified-50, reported benchmark scores for CompBioBench and output agreement for IWC. The benchmarks are therefore analysed separately and never pooled (Supplementary Table 1).
- DeepSeek V4 Pro (Claude Code, superseded) is reported separately. GPT-6 Astra is unpaired and excluded from condition differences.

Archive totals: 4,240 runs, 4,228 execution traces, 23,080 Galaxy analysis jobs and 69,812 Galaxy interface calls (Extended Data Fig. 1; Supplementary Notes 1 and 2; Supplementary Data 1).

**Fig. 2 | Galaxy-mediated execution preserves benchmark performance.**
In panels a, c and d, the left plot shows each replicate run (symbols) and the mean (tick) per model configuration and execution condition. The right plot shows the condition difference (Galaxy − open-ended code) with its 95% confidence interval, printed beside it. Rows repeat across panels: the four Codex model configurations, their pooled estimate and, separately, the superseded Claude Code agent harness (BixBench-Verified-50 only).
**a**, IWC: mean output agreement over the nine tasks scored in both conditions. Grey text gives the median output agreement per model configuration, open-ended code / Galaxy (Supplementary Table 7).
**b**, IWC output agreement of every run on all ten tasks, on an axis broken between 0.45 and 0.80. Ticks mark the mean of the 12 replicate runs per condition. Numbered notes give the traced cause of every run below 0.5. Notes 1 and 2 are failure modes seen only in the open-ended code condition; note 4 is a score conflict (Supplementary Tables 9 and 18; Extended Data Fig. 3).
**c**, BixBench-Verified-50: accuracy, the share of 50 tasks scored correct per replicate run, and the condition difference in percentage points (Supplementary Tables 2–4).
**d**, CompBioBench: reported benchmark scores (answers credited, of 100) of the three replicate runs per condition. Open symbols are scores labelled predicted in the archive. No interval is given, because the archive keeps reported benchmark scores but no per-run grades. GPT-6 Astra (open-ended code condition only, not paired) scored 93 (Supplementary Tables 5, 6 and 61; Extended Data Fig. 2).

**Fig. 3 | Model configurations achieve similar performance through different Galaxy strategies.**
All panels show Galaxy-condition runs.
**a**, Performance by model configuration on each benchmark: IWC mean output agreement over all ten tasks; BixBench-Verified-50 accuracy; CompBioBench reported benchmark scores (open symbols labelled predicted). Symbols are replicate runs; the tick and number give the mean. The superseded Claude Code agent harness ran BixBench-Verified-50 only (Supplementary Tables 55, 58 and 61).
**b**, Galaxy-condition runs that requested a user-defined tool, by model configuration. User-defined tools were not offered for IWC tasks (Supplementary Table 24).
**c**, Input-token usage per Galaxy-condition run (millions, log scale). Boxes span the middle 50% of runs and mark the median, which is printed at right; whiskers extend to 1.5 times the interquartile range; outliers are not shown (Supplementary Table 49; Extended Data Fig. 6).

**Fig. 4 | Replicate agreement separates model configurations that run-level accuracy conflates.**
A replicate set is the three replicate runs of one task × model configuration × execution condition (Supplementary Note 8).
**a**, BixBench-Verified-50 replicate sets per model configuration and execution condition (50 tasks each): all three replicate runs scored correct (3/3), split (1–2/3) or none scored correct (0/3). The note under the panel gives the totals over all five model configurations (Supplementary Table 56).
**b**, CompBioBench replicate sets by the number of distinct normalized answers among their three replicate runs (100 tasks per model configuration). This measures answer consistency, not correctness (Supplementary Tables 44 and 60).
**c**, Divergence mechanism of every scored-incorrect replicate run in a split BixBench-Verified-50 replicate set (45 open-ended code condition, 36 Galaxy condition), identified by comparing its execution trace with those of its scored-correct siblings (Supplementary Table 48; Extended Data Fig. 5a).
**d**, BixBench-Verified-50 run-level accuracy (open symbols) and unanimous accuracy, the share of tasks with 3/3 replicate runs scored correct (filled symbols), per model configuration. The right column gives the Galaxy-condition difference, unanimous − run-level. The note gives the condition difference on both measures for the same pooled model configurations (Supplementary Table 56).

**Fig. 5 | Trace-level analysis distinguishes benchmark artifacts from platform and agent failures.**
**a**, Primary cause of each of the 93 audited task cases: every task with at least one wrong, scored-incorrect or low-scoring run (33 BixBench-Verified-50, 53 CompBioBench and 7 IWC task cases, including one IWC workflow whose near-perfect output agreement concealed a changed significant-gene set). Each task case has one primary cause. The bracket marks the 30 cases whose primary cause lies with the reference or evaluator. The note lists flags recorded in addition to the primary cause (Supplementary Table 14; Supplementary Note 6; Extended Data Fig. 8).
**b**, bix-35-q1, an interface-binding failure. The executed metric of every PhyKIT job was read from the command line of its archived Galaxy job record; request shapes come from the execution traces (Extended Data Fig. 7).
**c**, contaminated-rna-q1, a missing resource. Read counts are from the Kraken2 reports returned to the agents, as recorded in the execution traces. Two scored-incorrect Galaxy-condition runs fell back to the standard-16 database and answered Epstein–Barr virus; the third fell back to a mitochondrion-only BLAST search and answered *Artemia franciscana*.

## Extended Data figures

**Extended Data Fig. 1 | Evidence archive and trace-level audit pipeline.**
**a**, Archived evidence per benchmark; Galaxy analysis jobs are counted once per server and job identifier. The last row gives the task cases audited trace by trace (Fig. 5a).
**b**, Audit pipeline from execution traces to the task-level audit (Supplementary Notes 1, 2, 6 and 8).

**Extended Data Fig. 2 | Validation of the CompBioBench consensus proxy.**
**a**, For the 22 CompBioBench reported benchmark scores with retained answers, the number of answers matching the consensus answer, plotted against the reported score. Open symbols are scores labelled predicted; the dashed line is identity. Mean absolute error 2.6 of 100; mean bias +2.0.
**b**, Runs per task that gave the consensus answer. The 82 tasks where at least 20 of 25 runs agree define the strong consensus, used to identify probable failures and split replicate sets (Supplementary Table 6; Supplementary Note 7).

**Extended Data Fig. 3 | Sensitivity of the IWC condition difference, and every IWC run below 0.5.**
**a**, Condition difference in mean output agreement per model configuration on the nine matched tasks (black circles), with the range obtained by leaving one task out (grey bars), after removing the three tasks with a zero-scored open-ended code run (diamonds), and retaining host-read removal where it was scored (triangles). Values at right: nine tasks → tasks without a zero-scored run (Supplementary Table 12).
**b**, Every IWC run with output agreement below 0.5, with its execution condition, model configuration, replicate run and the cause traced from its execution trace. The two host-read removal runs are score conflicts: their BWA-MEM output matches the BWA-route reference but was scored against the Bowtie2-route reference (Supplementary Table 18; Supplementary Note 6).

**Extended Data Fig. 4 | Domain-skill uptake and scripting of the Galaxy interface library (BixBench-Verified-50).**
**a**, Share of runs that opened the relevant domain skill, on the 38 tasks with a relevant skill (114 runs per bar). A skill is relevant to a task when scored-correct runs of that task opened it.
**b**, Galaxy-condition runs (Codex execution traces) that imported the Galaxy interface library into a shell script instead of calling the Galaxy interface directly, and runs that only read its source code (Supplementary Table 20).

**Extended Data Fig. 5 | Divergence mechanisms by model configuration, and the split IWC replicate sets.**
**a**, Divergence mechanisms of Fig. 4c by model configuration and execution condition; numbers at right give scored-incorrect replicate runs in split replicate sets (Supplementary Table 48).
**b**, The five split IWC Galaxy-condition replicate sets (within-set range of output agreement above 0.05), with the output agreement of each replicate run and the difference traced between them (Supplementary Tables 8 and 9).

**Extended Data Fig. 6 | Input-token usage did not track performance.**
**a**, Galaxy-condition performance against median input-token usage per run (log scale), per model configuration and benchmark. On no benchmark was the model configuration with the lowest input-token usage the least accurate.
**b**, BixBench-Verified-50: each model configuration against GPT-5.5 in the same execution condition, on the same 50 tasks. Left, input-token usage as a ratio (log scale); right, model difference in accuracy (percentage points); lines are 95% confidence intervals and dashed lines mark GPT-5.5 (Supplementary Tables 49 and 54).

**Extended Data Fig. 7 | bix-35-q1: the metric each PhyKIT job executed.**
**a**, Every PhyKIT metrics job in the analysis history of each Galaxy-condition run, in order of creation, coloured by the metric in its command line, with the submitted answer (reference 0.0471; the scored-incorrect answer is in bold). One GPT-5.5 run used a user-defined tool and has no PhyKIT wrapper job.
**b**, Tool-state request shapes submitted by the agents and the metric Galaxy executed for each. Every job returned the state "ok" (Fig. 5b).

**Extended Data Fig. 8 | Integrity problems found by the task-level audit.**
**a**, Task cases in which agents retrieved, or tried to retrieve, benchmark answers online, by what was obtained and by benchmark.
**b**, Galaxy-condition CompBioBench runs whose answer was computed in the local shell after user-defined-tool execution became unavailable on the server, by model configuration and scored outcome.
**c**, The two runs that copied answers from other runs through the shared Galaxy account (Supplementary Table 14b,d; Supplementary Note 6).
