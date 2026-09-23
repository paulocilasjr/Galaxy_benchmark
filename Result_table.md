# Benchmark Results Tables

Retrospective synthesis of the archived BixBench-50, CompBioBench and IWC analyses. `BixBench50` below maps to the repository's `BixBench_50/` directory. **Scope:** IWC is the workflow-derived task stratum; BixBench and CompBio contain platform-neutral biomedical questions. Task origin is confounded with task selection, endpoints, prompts, budgets and exposed interfaces. These archives do not directly test whether workflow-derived tasks cause better Galaxy results or reduce the need for custom code. The tables distinguish evaluator acceptance or agreement, observed execution, and unresolved scientific interpretation. Proposed improvements are hypotheses for prospective evaluation, not measured benefits.

**Readout:** Galaxy and open-ended code are recorded condition assignments, not certifications of where every analytical operation ran. Intervals are 95% confidence intervals unless specified. Q1 and Q3 are the first and third quartiles. Unavailable never means zero. Displayed values are rounded: 1.0000 does not necessarily mean exact agreement. All GPT-5 configurations use the supplied Codex labels. Replicate numbers are not matched seeds. CompBio vectors are final campaign selections, including continuations/recoveries; they do not measure first-attempt performance. IWC scores are continuous output agreement (0-1), not acceptance; they are never pooled with BixBench acceptance or binarized.

[Reproduce and inspect](BixBench50_CompBio_analysis/README.md) | [Calculations and table values](BixBench50_CompBio_analysis/analysis.json) | [Task/run/finding source manifest](BixBench50_CompBio_analysis/source_manifest.json).

**Question guide:** condition-exclusive evaluator acceptance and a recorded version contrast (B11-B13); configuration outcomes and token use (B14-B15, C9); common software and environmental friction (X9-X10); recurring diagnostics and task specification/workload (X5-X6, X11, X18); user-defined tool necessity versus choice (X12-X15); different routes to the same answer and evidence for the motivating observations (X16-X17). IWC: agreement and sensitivity (I1-I5), score provenance (I6), observed helper and Tool Shed use (I11, X19), and non-interchangeable benchmark endpoints (X20). Tables report observations unless explicitly labelled as inference or a proposed intervention.

## 1) Bixbench50 analysis

**Finding:** high observed acceptance is compatible with Galaxy execution, but the environment difference is uncertain and sensitive to the superseded harness. The archive contains 50 questions in 33 capsules, five configurations, two environments and three replicates (1,500 scored runs).

### Table B1. Original-evaluator acceptance and paired environment difference

| Configuration | Galaxy accepted | open-ended code accepted | Galaxy - open-ended code, percentage points [95% confidence interval] |
| --- | --- | --- | --- |
| GPT-5.5 | 134/150 (89.3%) | 131/150 (87.3%) | 2.00 [0.00, 5.30] |
| GPT-5.6 Sol | 133/150 (88.7%) | 130/150 (86.7%) | 2.00 [-5.07, 9.52] |
| GPT-5.6 Luna | 129/150 (86.0%) | 129/150 (86.0%) | 0.00 [-7.05, 6.25] |
| DeepSeek V4 Pro (Codex) | 123/150 (82.0%) | 121/150 (80.7%) | 1.33 [-5.43, 7.80] |
| DeepSeek V4 Pro (Claude Code, superseded) | 120/150 (80.0%) | 104/150 (69.3%) | 10.67 [1.39, 21.15] |
| All five | 639/750 (85.2%) | 615/750 (82.0%) | 3.20 [-1.36, 7.86] |
| Four Codex configurations | 519/600 (86.5%) | 511/600 (85.2%) | 1.33 [-3.48, 6.34] |

Original binary evaluator scores are retained, including six scored missing answers (five Galaxy, one open-ended code). No regrading was performed. The superseded Claude Code configuration contributes 16 of the 24 extra accepted Galaxy runs; excluding it leaves eight. The original 100,000-resample audit interval was -1.41 to +7.91 percentage points; the fresh calculation above uses the common settings below.

Unless a table specifies otherwise, new intervals are exploratory 95% percentile cluster-bootstrap intervals (20,000 resamples; seed 20260922, with deterministic statistic-specific streams). BixBench resamples eligible source capsules (up to 33); CompBio resamples eligible tasks (up to 100), retaining configurations and replicate bundles. Estimates weight eligible task/configuration cells equally; capsule sizes remain unequal. Cross-benchmark draws are independent and stratified by benchmark. Intervals assume independent clusters, an assumption not established for shared biological inputs. They are pointwise, not multiplicity-adjusted simultaneous intervals. No confirmatory significance, equivalence, non-inferiority or causal claim is made; an interval spanning zero (differences) or one (ratios) is inconclusive.

### Table B2. Repeatability of accepted answers

| Configuration | Environment | 3/3 accepted | 1-2/3 accepted | 0/3 accepted | At least one accepted |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Galaxy | 44 | 1 | 5 | 45/50 (90.0%) |
| GPT-5.5 | Open-ended code | 43 | 1 | 6 | 44/50 (88.0%) |
| GPT-5.6 Sol | Galaxy | 43 | 2 | 5 | 45/50 (90.0%) |
| GPT-5.6 Sol | Open-ended code | 41 | 4 | 5 | 45/50 (90.0%) |
| GPT-5.6 Luna | Galaxy | 40 | 5 | 5 | 45/50 (90.0%) |
| GPT-5.6 Luna | Open-ended code | 38 | 8 | 4 | 46/50 (92.0%) |
| DeepSeek V4 Pro (Codex) | Galaxy | 38 | 7 | 5 | 45/50 (90.0%) |
| DeepSeek V4 Pro (Codex) | Open-ended code | 37 | 6 | 7 | 43/50 (86.0%) |
| DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | 32 | 13 | 5 | 45/50 (90.0%) |
| DeepSeek V4 Pro (Claude Code, superseded) | Open-ended code | 28 | 14 | 8 | 42/50 (84.0%) |

Each row contains 50 task cells; the middle three categories are mutually exclusive. At least one is an overlapping endpoint, not single-run accuracy. These are replicate-labelled archived runs, not best-of-three adaptive attempts.

### Table B3. Largest acceptance discordances and tasks rejected throughout

| Task | Question | Galaxy accepted | open-ended code accepted | Galaxy error/non-fetch jobs |
| --- | --- | --- | --- | --- |
| [bix-30-q3](BixBench_50/analysis/bix-30-q3/history_analysis.md) | Multiple-testing miRNA ratio | 15/15 | 6/15 | 23/51 |
| [bix-43-q2](BixBench_50/analysis/bix-43-q2/history_analysis.md) | gseapy enrichment odds ratio | 11/15 | 2/15 | 38/142 |
| [bix-45-q1](BixBench_50/analysis/bix-45-q1/history_analysis.md) | RCV Mann-Whitney p-value | 0/15 | 8/15 | 0/45 |
| [bix-53-q2](BixBench_50/analysis/bix-53-q2/history_analysis.md) | Differential expression after replicate exclusion | 0/15 | 0/15 | 15/88 |
| [bix-61-q5](BixBench_50/analysis/bix-61-q5/history_analysis.md) | Transition/transversion ratio | 0/15 | 0/15 | 0/19 |

Selection rule: absolute acceptance difference >=5/15 or zero acceptance in both environments; all five qualifying tasks are shown. Task-linked jobs are deduplicated within task. Operationally successful jobs do not establish a correct answer: RCV and transition/transversion results were rejected despite no recorded job errors. RCV means relative composition variability. The source reports implicate threshold choices, upstream gene sets and RCV input construction; those mechanisms are not independently adjudicated here.

### Table B4. Galaxy execution, missing evidence and recovery candidates

| Measure | Observed |
| --- | --- |
| Detailed Galaxy histories, run-linked | 714/750 (95.2%) |
| Metadata-only / unavailable run-linked histories | 32 / 4 |
| Distinct non-fetch creating jobs | 5,042 |
| Job states: ok / error / deleted / paused | 4,454 / 552 / 25 / 11 |
| Error jobs / non-fetch jobs | 552/5,042 (10.9%) |
| Runs with >=1 error job / detailed runs | 243/714 (34.0%) |
| Error jobs/run: median (Q1-Q3); range | 0.0 (0.0-1.0); 0-20 |
| Candidate recovery episodes / runs containing one | 93 / 49 |
| Adjudicated recovery rate; failures before correct answer | Unavailable; Unavailable |
| Certified Galaxy-only completion | Unavailable |

Jobs are deduplicated by server/native job ID and exclude data-fetch jobs, but include preparation and legacy upload. Histories may contain inherited/later state. A candidate is later same-tool/input success, not verified recovery of a scientific objective. 31/32 collection-limited runs had accepted answers. The original fresh-history check is false for all 750 Galaxy runs, despite retrieved history evidence; Galaxy-only completion remains unresolved.

### Table B5. Observable triplicate path agreement under the harmonized rule

| Environment | Configuration | Eligible/total | Identical | Two identical | All distinct | Mean Jaccard |
| --- | --- | --- | --- | --- | --- | --- |
| Galaxy | GPT-5.5 | 50/50 | 6 | 6 | 38 | 0.260 |
| Galaxy | GPT-5.6 Sol | 45/50 | 12 | 9 | 24 | 0.501 |
| Galaxy | GPT-5.6 Luna | 43/50 | 6 | 7 | 30 | 0.426 |
| Galaxy | DeepSeek V4 Pro (Codex) | 41/50 | 12 | 11 | 18 | 0.625 |
| Galaxy | DeepSeek V4 Pro (Claude Code, superseded) | 46/50 | 8 | 13 | 25 | 0.459 |
| Galaxy | All configurations | 225/250 | 44 | 46 | 135 | 0.447 |
| Open-ended code | GPT-5.5 | 50/50 | 4 | 7 | 39 | 0.669 |
| Open-ended code | GPT-5.6 Sol | 50/50 | 4 | 13 | 33 | 0.695 |
| Open-ended code | GPT-5.6 Luna | 50/50 | 4 | 12 | 34 | 0.663 |
| Open-ended code | DeepSeek V4 Pro (Codex) | 50/50 | 1 | 8 | 41 | 0.581 |
| Open-ended code | DeepSeek V4 Pro (Claude Code, superseded) | 49/50 | 3 | 10 | 36 | 0.649 |
| Open-ended code | All configurations | 249/250 | 16 | 50 | 183 | 0.651 |

One cell = task x configuration x environment with three replicate labels. This report harmonizes BOTH benchmarks: all three fingerprints must be observed and nonempty. Identical / two identical / all distinct partition evaluable cells. Jaccard = intersection/union, averaged over the three replicate pairs and then over eligible cells. Galaxy uses version-stripped job tool IDs (excluding data fetch, retaining legacy upload); code uses the archived closed command vocabulary. These instruments cannot rank scientific consistency across environments; order, most parameters and biological validity are unmeasured. BixBench counts differ from its legacy report because that report also admitted partly missing/empty fingerprints.

### Table B6. Does a consistent recorded path imply acceptance?

| Environment | Accepted replicates | Eligible cells | Tasks | Identical fingerprints | Mean Jaccard |
| --- | --- | --- | --- | --- | --- |
| Galaxy | All three | 177 | 45 | 27/177 (15.3%) | 0.413 |
| Galaxy | One or two | 25 | 20 | 7/25 (28.0%) | 0.488 |
| Galaxy | None | 23 | 5 | 10/23 (43.5%) | 0.663 |
| Open-ended code | All three | 187 | 44 | 14/187 (7.5%) | 0.654 |
| Open-ended code | One or two | 33 | 21 | 0/33 (0.0%) | 0.625 |
| Open-ended code | None | 29 | 12 | 2/29 (6.9%) | 0.661 |

Descriptive association conditional on observable nonempty paths. Cells share tasks; failure-prone task composition can drive the pattern. Agreement is neither correctness nor causal evidence that varied methods help. The retained rows allow inspection of both accepted and rejected consistent paths.

### Table B7. Input-token burden by configuration

| Configuration | Paired cells | Ratio median (Q1-Q3) | Ratio [95% confidence interval] | Median input Galaxy / open-ended code | Pairs with Galaxy > open-ended code |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 | 50 | 3.86 (2.51-6.78) | 3.86 [2.97, 5.81] | 1,190,227.0 / 316,911.0 | 47/50 (94.0%) |
| GPT-5.6 Sol | 50 | 5.03 (3.10-8.80) | 5.03 [4.06, 6.07] | 1,557,302.5 / 299,919.5 | 48/50 (96.0%) |
| GPT-5.6 Luna | 50 | 7.63 (4.56-19.99) | 7.63 [6.27, 13.60] | 5,026,010.5 / 670,132.0 | 49/50 (98.0%) |
| DeepSeek V4 Pro (Codex) | 50 | 4.50 (2.30-11.20) | 4.50 [2.51, 9.02] | 3,522,986.5 / 1,101,893.0 | 46/50 (92.0%) |
| DeepSeek V4 Pro (Claude Code, superseded) | 50 | 2.97 (1.49-5.12) | 2.97 [2.02, 4.42] | 2,068,134.5 / 703,056.5 | 44/50 (88.0%) |
| All configurations | 250 | 4.74 (2.45-9.62) | 4.74 [3.48, 6.25] | 2,163,883.5 / 526,530.0 | 234/250 (93.6%) |

Ratio = median input tokens of three Galaxy runs / median of three code runs for the same task and configuration; all six totals must be available. Q1-Q3 are quartile endpoints. Absolute medians use every available run in that row and are not the numerator/denominator of the paired median ratio. Cached input is already included. Output/reasoning are not added. Usage covers archived primary turns, not full campaign, compute or monetary cost. Failed runs are retained; missing usage is never zero.

### Table B8. Evaluator-mode composition and acceptance

| Recorded verifier | Accepted/all | Galaxy runs | open-ended code runs |
| --- | --- | --- | --- |
| None | 0/6 (0.0%) | 5 | 1 |
| llm_verifier_auto_code | 490/599 (81.8%) | 299 | 300 |
| range_verifier | 340/389 (87.4%) | 194 | 195 |
| str_verifier | 182/209 (87.1%) | 105 | 104 |
| str_verifier_auto_numeric | 240/286 (83.9%) | 142 | 144 |
| str_verifier_rounded_numeric | 2/11 (18.2%) | 5 | 6 |

Modes are observational and task/configuration-dependent; these are not randomized verifier comparisons. The source audit reports byte-identical answers with different scores under different modes. Rounded-numeric scoring occurs only in the two DeepSeek configurations. These evaluator effects limit interpreting rejection as a demonstrated analytical mistake.

### Table B9. Most frequently recorded Galaxy operations

| Recorded tool / version | Non-fetch jobs | Error jobs |
| --- | --- | --- |
| xlsx2tsv/0.2.0+galaxy0 | 644 | 0 |
| Cut1 | 557 | 7 |
| Filter1 | 397 | 0 |
| kegg_ora/0.1.0+galaxy1 | 269 | 62 |
| phykit_metrics/0.2.0+galaxy0 | 202 | 0 |
| csv_to_tabular | 163 | 0 |

Top six tool IDs by job count (ties sorted by full ID), among 5,042 deduplicated non-fetch jobs. Spreadsheet conversion, column selection and filtering accompany KEGG over-representation and PhyKIT metrics. KEGG is the Kyoto Encyclopedia of Genes and Genomes. Counts include preparation and inherited/later history state; operation frequency is not success attribution. Full IDs and event references are in the analysis JSON.

### Table B10. Task coverage versus within-configuration advantage

| Environment | Tasks with any accepted run | All 15 runs accepted | Tasks accepted only here | Task/configuration pairs with more accepted runs |
| --- | --- | --- | --- | --- |
| Galaxy | 47/50 (94.0%) | 25/50 (50.0%) | 0 | 33 |
| Open-ended code | 48/50 (96.0%) | 25/50 (50.0%) | 1 | 19 |

Task coverage pools five configurations and three replicates (15 runs/task/environment), whereas the last column compares three-replicate counts within each of 250 matched task/configuration pairs. There are 198 tied pairs, and two tasks with no accepted answer in either environment. These endpoints do not describe the reliability of a single run.

### Table B11. Tasks with evaluator acceptance in only one condition

| Exclusive condition | Task | Observed acceptance | Explanation supported by the archive |
| --- | --- | --- | --- |
| Galaxy | None | 0/50 tasks | No task met the specified exclusive-success rule |
| Open-ended code | [bix-45-q1](BixBench_50/analysis/bix-45-q1/history_analysis.md) | Galaxy 0/15; open-ended code 8/15 | Version-dependent relative composition variability; see B13 |

Exact rule: at least one accepted replicate across the five configurations in one condition and zero across all 15 runs in the other. Galaxy-only: zero tasks. Open-ended-code-only: one task, bix-45-q1. This is a task-level set comparison, not a test of superiority. Relative composition variability is the alignment statistic requested in the task. Model-specific counts are shown next.

### Table B12. Model dependence of the exclusive open-ended-code success

| Configuration | Galaxy accepted | Open-ended code accepted |
| --- | --- | --- |
| GPT-5.5 | 0/3 | 0/3 |
| GPT-5.6 Sol | 0/3 | 3/3 |
| GPT-5.6 Luna | 0/3 | 2/3 |
| DeepSeek V4 Pro (Codex) | 0/3 | 3/3 |
| DeepSeek V4 Pro (Claude Code, superseded) | 0/3 | 0/3 |

Single-task description: all 15 Galaxy answers were rejected, although all 45 retained non-fetch Galaxy jobs had state ok. An environment-wide missing execution capability is therefore not established. No benchmark-wide interval is estimated from one task.

### Table B13. Why bix-45-q1 differs: a version contrast retained within one original run

| Recorded analysis / source | Alignments: animal / fungal | Mann-Whitney statistic | Task p-value | Original final-answer status |
| --- | --- | --- | --- | --- |
| Open-ended code, Sol replicate 1, current PhyKIT calculation; event source line 24 | 241 / 255 | 5,483.5 | 1.5197572608715265e-56 | Matches the rejected Galaxy value |
| Same run, PhyKIT 2.0.3 reconstruction; event source line 33 | 241 / 255 | 6,115 | 7.6967608298013025e-54 | Matches the accepted submitted value |
| Same run, direct PhyKIT 2.0.3 check; event source line 45 | 241 / 255 | 6,115 | 7.6967608298013025e-54 | Saved output confirms reconstruction agreement |
| Galaxy, Sol replicate 1; PhyKIT metrics and rank-test wrappers | 241 / 255 | Not extracted here | 1.5197572608715265e-56 | Rejected |

These p-values are outputs of the biomedical task, not tests of an environment effect. The recorded checks use rounded per-alignment values and two-sided asymptotic/automatic Mann-Whitney tests with continuity correction. The agent attributed the change to version-dependent gap/ambiguous-residue handling; the archived numerical contrast supports a version explanation for this run. It does not prove the intended reference release, adjudicate biological validity, or explain every rejected run. Source: [task evidence](BixBench_50/analysis/bix-45-q1/history_analysis_evidence.json), `open_ended_code_codex_gpt_5_6_sol_r1`, source lines 24, 33 and 45; trace messages and hashes are in `results.deep.case_sources`. No calculation was replayed. The within-run version contrast narrows the possible explanation beyond a generic input-assembly difference.

### Table B14. Configuration outcomes, repeatability, operational markers and tokens

| Configuration | Environment | Accepted runs | Tasks with all accepted | Runs with Galaxy job error | Runs with nonzero shell exit | Median input tokens (millions); coverage |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Galaxy | 134/150 (89.3%) | 44/50 (88.0%) | 40/150 (26.7%) | 66/150 (44.0%) | 1.190; 150/150 |
| GPT-5.5 | Open-ended code | 131/150 (87.3%) | 43/50 (86.0%) | Not applicable | 99/150 (66.0%) | 0.317; 150/150 |
| GPT-5.6 Sol | Galaxy | 133/150 (88.7%) | 43/50 (86.0%) | 40/144 (27.8%) | 71/150 (47.3%) | 1.557; 150/150 |
| GPT-5.6 Sol | Open-ended code | 130/150 (86.7%) | 41/50 (82.0%) | Not applicable | 104/150 (69.3%) | 0.300; 150/150 |
| GPT-5.6 Luna | Galaxy | 129/150 (86.0%) | 40/50 (80.0%) | 67/134 (50.0%) | 131/150 (87.3%) | 5.026; 150/150 |
| GPT-5.6 Luna | Open-ended code | 129/150 (86.0%) | 38/50 (76.0%) | Not applicable | 133/150 (88.7%) | 0.670; 150/150 |
| DeepSeek V4 Pro (Codex) | Galaxy | 123/150 (82.0%) | 38/50 (76.0%) | 35/139 (25.2%) | 121/150 (80.7%) | 3.523; 150/150 |
| DeepSeek V4 Pro (Codex) | Open-ended code | 121/150 (80.7%) | 37/50 (74.0%) | Not applicable | 127/150 (84.7%) | 1.102; 150/150 |
| DeepSeek V4 Pro (Claude Code, superseded) | Galaxy | 120/150 (80.0%) | 32/50 (64.0%) | 61/147 (41.5%) | Unavailable | 2.068; 150/150 |
| DeepSeek V4 Pro (Claude Code, superseded) | Open-ended code | 104/150 (69.3%) | 28/50 (56.0%) | Not applicable | Unavailable | 0.703; 150/150 |

Each task contributes three runs/configuration/environment. Accepted-answer reliability is used for BixBench; CompBio can only report answer-text consistency, never correctness. Galaxy job errors and nonzero shell exits are different instruments. A shell exit may be a probe or failed search; Galaxy analysis is often offloaded to server jobs, so fewer shell exits do not establish easier execution. Shell denominators require at least one numeric recorded exit code: the superseded Claude Code traces contain no numeric exit codes and are unavailable, not zero failures. Tokens describe archived primary turns, not full execution cost. Missing data are excluded with explicit denominators; all observed outcomes are included.

### Table B15. Model trade-off: acceptance difference and token use relative to GPT-5.5

| Environment | Compared configuration | Acceptance difference (percentage points) [95% interval] | Input-token ratio to GPT-5.5 [95% interval] | Galaxy error-run difference (percentage points) [95% interval]; paired tasks |
| --- | --- | --- | --- | --- |
| Galaxy | GPT-5.6 Sol | -0.67 [-2.96, 1.45] | 1.33 [1.17, 1.59] | 1.48 [-8.70, 12.06]; 45 tasks |
| Galaxy | GPT-5.6 Luna | -3.33 [-8.18, 0.67] | 4.08 [2.94, 6.22] | 23.26 [9.76, 36.67]; 43 tasks |
| Galaxy | DeepSeek V4 Pro (Codex) | -7.33 [-14.81, -1.23] | 3.44 [2.48, 4.80] | -0.00 [-11.38, 11.36]; 43 tasks |
| Galaxy | DeepSeek V4 Pro (Claude Code, superseded) | -9.33 [-14.18, -4.65] | 1.54 [1.31, 1.84] | 17.02 [5.00, 28.99]; 47 tasks |
| Open-ended code | GPT-5.6 Sol | -0.67 [-5.67, 4.94] | 1.06 [0.92, 1.29] | Not applicable |
| Open-ended code | GPT-5.6 Luna | -1.33 [-5.45, 3.40] | 1.87 [1.59, 2.30] | Not applicable |
| Open-ended code | DeepSeek V4 Pro (Codex) | -6.67 [-15.48, 1.42] | 3.67 [1.97, 4.66] | Not applicable |
| Open-ended code | DeepSeek V4 Pro (Claude Code, superseded) | -18.00 [-29.76, -7.25] | 2.05 [1.68, 2.41] | Not applicable |

Reference is GPT-5.5 within the same environment and the same 50 tasks. Accuracy differences average all three replicates; token ratios divide task medians of three replicates and are then summarized by the median ratio. Error-run differences use the subset of tasks with all six detailed Galaxy runs and compare proportions with at least one error; the error column can therefore have a different task population from the other columns. Intervals use 20,000 paired capsule bootstrap resamples, seed 20260922. They are exploratory and pointwise. A difference interval containing zero does not establish equal performance or non-inferiority. Within Galaxy, Sol and Luna consumed more input tokens than GPT-5.5 without a resolved acceptance advantage; both DeepSeek configurations consumed more and had lower observed acceptance. These are selected-corpus associations, not general model rankings. Absolute pooled medians in B14 and median paired ratios here can order models differently because they are different estimands.

### Table B16. Configuration-specific exclusive task successes hidden by pooling models

| Task | Configuration | Galaxy accepted | Open-ended code accepted | Supported interpretation |
| --- | --- | --- | --- | --- |
| [bix-12-q4](BixBench_50/analysis/bix-12-q4/history_analysis.md) | DeepSeek V4 Pro (Claude Code, superseded) | 1/3 | 0/3 | Observed configuration-specific difference; mechanism unadjudicated |
| [bix-14-q1](BixBench_50/analysis/bix-14-q1/history_analysis.md) | DeepSeek V4 Pro (Codex) | 1/3 | 0/3 | Observed configuration-specific difference; mechanism unadjudicated |
| [bix-26-q5](BixBench_50/analysis/bix-26-q5/history_analysis.md) | DeepSeek V4 Pro (Claude Code, superseded) | 0/3 | 1/3 | Direction reverses between DeepSeek harnesses; mechanism unadjudicated |
| [bix-26-q5](BixBench_50/analysis/bix-26-q5/history_analysis.md) | DeepSeek V4 Pro (Codex) | 1/3 | 0/3 | Direction reverses between DeepSeek harnesses; mechanism unadjudicated |
| [bix-30-q3](BixBench_50/analysis/bix-30-q3/history_analysis.md) | GPT-5.6 Sol | 3/3 | 0/3 | Threshold / upstream gene-set differences discussed in B3 |
| [bix-30-q3](BixBench_50/analysis/bix-30-q3/history_analysis.md) | DeepSeek V4 Pro (Codex) | 3/3 | 0/3 | Threshold / upstream gene-set differences discussed in B3 |
| [bix-31-q2](BixBench_50/analysis/bix-31-q2/history_analysis.md) | DeepSeek V4 Pro (Claude Code, superseded) | 3/3 | 0/3 | Observed configuration-specific difference; mechanism unadjudicated |
| [bix-34-q5](BixBench_50/analysis/bix-34-q5/history_analysis.md) | DeepSeek V4 Pro (Claude Code, superseded) | 2/3 | 0/3 | Observed configuration-specific difference; mechanism unadjudicated |
| [bix-43-q2](BixBench_50/analysis/bix-43-q2/history_analysis.md) | GPT-5.5 | 3/3 | 0/3 | Threshold / upstream gene-set differences discussed in B3 |
| [bix-43-q2](BixBench_50/analysis/bix-43-q2/history_analysis.md) | DeepSeek V4 Pro (Claude Code, superseded) | 2/3 | 0/3 | Threshold / upstream gene-set differences discussed in B3 |
| [bix-45-q1](BixBench_50/analysis/bix-45-q1/history_analysis.md) | GPT-5.6 Luna | 0/3 | 2/3 | Version contrast documented in B13 |
| [bix-45-q1](BixBench_50/analysis/bix-45-q1/history_analysis.md) | GPT-5.6 Sol | 0/3 | 3/3 | Version contrast documented in B13 |
| [bix-45-q1](BixBench_50/analysis/bix-45-q1/history_analysis.md) | DeepSeek V4 Pro (Codex) | 0/3 | 3/3 | Version contrast documented in B13 |

Same rule as B11, but now applied within a task and configuration: one or more accepted replicates versus none. All 13 qualifying pairs are shown: nine Galaxy-exclusive pairs and four open-ended-code-exclusive pairs out of 250. These do not contradict B11 because another configuration can succeed in the other environment. A one-of-three result is weak repeatability, not a stable platform advantage. Cells share tasks and cannot be treated as independent observations in a simple binomial test. Rows without an audited mechanism remain unresolved rather than being attributed to missing tools or model knowledge.

## 2) CompBio analysis

**Finding:** the archive supports execution, answer-text consistency and token analyses, but does not support task-level accuracy or correct-answer recovery rates. It includes 2,400 records in four paired configurations over 100 tasks, plus 100 unpaired GPT-6 Astra records. All 2,500 item-level evaluator scores are unavailable.

### Table C1. Source-reported answer-vector scores, with provenance status

| Configuration | Galaxy | open-ended code |
| --- | --- | --- |
| GPT-5.5 | r1: 84/100 (O); r2: 89/100 (O; hash mismatch); r3: 87/100 (P; hash mismatch) | r1: 87/100 (O); r2: 88/100 (O; hash mismatch); r3: 84/100 (O; hash mismatch) |
| GPT-5.6 Sol | r1: 93/100 (O); r2: 91/100 (P; hash mismatch); r3: 91/100 (O; hash mismatch) | r1: 88/100 (O); r2: 90/100 (O); r3: 95/100 (O) |
| GPT-5.6 Luna | r1: 86/100 (P; vector absent); r2: 84/100 (P; vector absent); r3: 85/100 (P; vector absent) | r1: 84/100 (O); r2: 86/100 (O); r3: 85/100 (P) |
| DeepSeek V4 Pro 0813 (Codex) | r1: 83/100 (P; hash mismatch); r2: 87/100 (P); r3: 83/100 (P) | r1: 80/100 (P); r2: 87/100 (O; hash mismatch); r3: 86/100 (O; hash mismatch) |
| GPT-6 Astra (unpaired) | Not represented | r1: 93/100 (O) |

O = archive-labelled official, not an independently verified leaderboard receipt; P = predicted. 15 vectors are O and 10 P; 13 advertised hashes match retained bytes, nine mismatch and three vectors are absent. All parsed answers match for the 22 available vectors. Sol Galaxy r1/r3 were previously 92/100 P; dated metadata changes them to 93/100 O and 91/100 O. Neither version is silently discarded. No pooled accuracy, uncertainty interval, or task-level all/some/none-correct inference is computed from this mixture. Source: [aggregate audit](CompBio/compBio_overview_audit.json), `score_vectors` and `score_conflicts`.

### Table C2. Usage completeness and repeated-answer consistency

| Configuration | Environment | Usage coverage | 1 distinct answer | 2 distinct | 3 distinct |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Galaxy | 297/300 (99.0%) | 84 | 11 | 5 |
| GPT-5.5 | Open-ended code | 300/300 (100.0%) | 82 | 15 | 3 |
| GPT-5.6 Sol | Galaxy | 300/300 (100.0%) | 87 | 11 | 2 |
| GPT-5.6 Sol | Open-ended code | 300/300 (100.0%) | 89 | 10 | 1 |
| GPT-5.6 Luna | Galaxy | 290/300 (96.7%) | 85 | 9 | 6 |
| GPT-5.6 Luna | Open-ended code | 300/300 (100.0%) | 78 | 19 | 3 |
| DeepSeek V4 Pro 0813 (Codex) | Galaxy | 300/300 (100.0%) | 77 | 15 | 8 |
| DeepSeek V4 Pro 0813 (Codex) | Open-ended code | 299/300 (99.7%) | 72 | 24 | 4 |

Usage denominators are 300 runs/row; answer counts partition 100 triplicate task cells/row. Answers use archived submitted text with outer whitespace removed, not raw-file hashes. Text identity does not establish semantic equivalence or correctness. Among all 12 answers/task/environment, 62/100 Galaxy tasks and 58/100 open-ended code tasks have one distinct answer; answer sets differ across environments in 43/100 tasks.

### Table C3. Galaxy execution and recovery evidence

| Measure | Observed |
| --- | --- |
| Detailed Galaxy histories, run-linked | 1,198/1,200 (99.8%) |
| Metadata-only / unavailable run-linked histories | 2 / 0 |
| Distinct non-fetch creating jobs | 16,686 |
| Job states: ok / error / deleted / paused | 13,517 / 3,097 / 58 / 14 |
| Error jobs / non-fetch jobs | 3,097/16,686 (18.6%) |
| Runs with >=1 error job / detailed runs | 702/1,198 (58.6%) |
| Error jobs/run: median (Q1-Q3); range | 1.0 (0.0-4.0); 0-32 |
| Candidate recovery episodes / runs containing one | 213 / 107 |
| Adjudicated recovery rate; failures before correct answer | Unavailable; Unavailable |
| Certified Galaxy-only completion | Unavailable |

The archive contains 22,067 distinct creating jobs: 5,381 data-fetch and 16,686 non-fetch (including 372 upload1 jobs). Non-fetch jobs are not independent scientific attempts. Nonzero shell exits occur in 676/1,188 available Galaxy transcripts and 882/1,200 open-ended code transcripts; probes/searches can return nonzero, so these are not comparative scientific-failure rates. The two metadata-only histories contain 196 error-state datasets in state_ids but zero in state_details, plus 17 unaccounted elements. Those dataset states are not added to creating-job totals.

### Table C4. Biological domain, answer convergence and operational burden

| Recorded domain | Tasks | Single-answer tasks Galaxy / open-ended code | Galaxy runs with error | Token ratio median (Q1-Q3) | Token pairs |
| --- | --- | --- | --- | --- | --- |
| Single-cell | 21 | 13 / 12 | 165/252 (65.5%) | 4.66 (1.72-9.80) | 82 |
| Epigenomics | 20 | 11 / 9 | 132/240 (55.0%) | 3.68 (1.92-8.78) | 77 |
| Genomics | 20 | 16 / 18 | 116/240 (48.3%) | 8.32 (3.69-12.64) | 77 |
| Transcriptomics | 17 | 6 / 9 | 106/204 (52.0%) | 6.67 (2.77-13.79) | 65 |
| Population Genetics | 12 | 8 / 6 | 97/142 (68.3%) | 3.23 (1.38-7.00) | 45 |
| Machine Learning | 7 | 7 / 2 | 66/84 (78.6%) | 1.71 (0.86-3.21) | 28 |
| Spatial | 2 | 1 / 2 | 14/24 (58.3%) | 2.52 (1.52-4.73) | 8 |
| Structure | 1 | 0 / 0 | 6/12 (50.0%) | 7.11 (1.79-14.34) | 4 |

Domains come from task metadata; these are not difficulty strata. All four paired configurations are included. Single-answer counts use 12 submitted answers per task/environment. Error denominators include only detailed Galaxy runs. Ratios require all six usage records; small domains are descriptive case groups, not evidence of domain superiority.

### Table C5. Observable triplicate path agreement

| Environment | Configuration | Eligible/total | Identical | Two identical | All distinct | Mean Jaccard |
| --- | --- | --- | --- | --- | --- | --- |
| Galaxy | GPT-5.5 | 99/100 | 2 | 3 | 94 | 0.089 |
| Galaxy | GPT-5.6 Sol | 100/100 | 1 | 4 | 95 | 0.125 |
| Galaxy | GPT-5.6 Luna | 97/100 | 1 | 5 | 91 | 0.190 |
| Galaxy | DeepSeek V4 Pro 0813 (Codex) | 94/100 | 2 | 5 | 87 | 0.203 |
| Galaxy | All configurations | 390/400 | 6 | 17 | 367 | 0.151 |
| Open-ended code | GPT-5.5 | 96/100 | 3 | 16 | 77 | 0.562 |
| Open-ended code | GPT-5.6 Sol | 95/100 | 1 | 16 | 78 | 0.597 |
| Open-ended code | GPT-5.6 Luna | 94/100 | 1 | 10 | 83 | 0.583 |
| Open-ended code | DeepSeek V4 Pro 0813 (Codex) | 97/100 | 2 | 7 | 88 | 0.587 |
| Open-ended code | All configurations | 382/400 | 7 | 49 | 326 | 0.583 |

One cell = task x configuration x environment with three replicate labels. This report harmonizes BOTH benchmarks: all three fingerprints must be observed and nonempty. Identical / two identical / all distinct partition evaluable cells. Jaccard = intersection/union, averaged over the three replicate pairs and then over eligible cells. Galaxy uses version-stripped job tool IDs (excluding data fetch, retaining legacy upload); code uses the archived closed command vocabulary. These instruments cannot rank scientific consistency across environments; order, most parameters and biological validity are unmeasured. BixBench counts differ from its legacy report because that report also admitted partly missing/empty fingerprints.

### Table C6. Input-token burden by configuration

| Configuration | Paired cells | Ratio median (Q1-Q3) | Ratio [95% confidence interval] | Median input Galaxy / open-ended code | Pairs with Galaxy > open-ended code |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 | 97 | 3.14 (1.68-5.81) | 3.14 [2.37, 3.75] | 1,734,835.0 / 491,109.0 | 85/97 (87.6%) |
| GPT-5.6 Sol | 100 | 6.63 (3.13-12.05) | 6.63 [5.46, 8.58] | 3,748,257.5 / 530,535.0 | 96/100 (96.0%) |
| GPT-5.6 Luna | 90 | 5.73 (2.09-16.09) | 5.73 [4.00, 8.38] | 10,238,154.5 / 1,448,621.0 | 80/90 (88.9%) |
| DeepSeek V4 Pro 0813 (Codex) | 99 | 3.53 (1.58-8.36) | 3.53 [2.79, 4.42] | 8,478,973.0 / 2,407,919.0 | 86/99 (86.9%) |
| All configurations | 386 | 4.42 (1.91-10.66) | 4.42 [3.53, 5.39] | 4,550,435.0 / 957,212.0 | 347/386 (89.9%) |

Ratio = median input tokens of three Galaxy runs / median of three code runs for the same task and configuration; all six totals must be available. Q1-Q3 are quartile endpoints. Absolute medians use every available run in that row and are not the numerator/denominator of the paired median ratio. Cached input is already included. Output/reasoning are not added. Usage covers archived primary turns, not full campaign, compute or monetary cost. Failed runs are retained; missing usage is never zero. Fourteen of 400 pairs are excluded (3 GPT-5.5, 10 Luna, 1 DeepSeek). The runtime-and-reasoning-verified sensitivity contains only 99 DeepSeek pairs (median 3.53), so it changes the configuration population. Astra usage is available in 100/100 unpaired open-ended code runs (median input 314,244.5); no Galaxy ratio is possible.

### Table C7. Adjudicated examples: correction versus changed objective

| Task / run | Failure | Later operation | Supported conclusion |
| --- | --- | --- | --- |
| [bedtools-chromhmm-q1](CompBio/analysis/bedtools-chromhmm-q1/history_analysis.md); DeepSeek Galaxy r2 | round(c1/c5*100): string columns | round(float(c1)/float(c5)*100); job ok | Operational type correction; biological denominator and answer correctness not validated |
| [perturb-seq-align-q1](CompBio/analysis/perturb-seq-align-q1/history_analysis.md); DeepSeek Galaxy r3 | AnnData chunk_X: sparse-matrix attribute error | Successful var metadata query | Same tool/input, different operation; not recovery of chunk_X |

Purposive positive and contradictory examples, not a random sample of 213 candidates. Exact event IDs, parameter changes, timestamps and excerpts are preserved in `case_reviews` in the [CompBio audit](CompBio/compBio_overview_audit.json). No recovery success percentage is inferred from these two cases.

### Table C8. Most frequently recorded Galaxy operations

| Recorded tool / version | Non-fetch jobs | Error jobs |
| --- | --- | --- |
| filter_tabular/3.3.1 | 627 | 12 |
| anndata_inspect/0.11.4+galaxy3 | 413 | 16 |
| Cut1 | 378 | 14 |
| datamash_ops/1.9+galaxy0 | 372 | 19 |
| upload1 | 372 | 56 |
| bedtools_intersectbed/2.31.1+galaxy0 | 346 | 26 |

Top six tool IDs by job count among 16,686 deduplicated non-fetch jobs. AnnData inspection and bedtools intersection appear alongside filtering, column selection, Datamash and legacy upload. This is evidence of operation availability/use, not correctness, independent analyses or exclusive use of installed domain tools. Full IDs and event references are in the analysis JSON.

### Table C9. Configuration outcomes, repeatability, operational markers and tokens

| Configuration | Environment | Accepted runs | Tasks with identical answer text | Runs with Galaxy job error | Runs with nonzero shell exit | Median input tokens (millions); coverage |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Galaxy | Unavailable | 84/100 (84.0%) | 195/300 (65.0%) | 131/293 (44.7%) | 1.735; 297/300 |
| GPT-5.5 | Open-ended code | Unavailable | 82/100 (82.0%) | Not applicable | 218/299 (72.9%) | 0.491; 300/300 |
| GPT-5.6 Sol | Galaxy | Unavailable | 87/100 (87.0%) | 146/300 (48.7%) | 91/288 (31.6%) | 3.748; 300/300 |
| GPT-5.6 Sol | Open-ended code | Unavailable | 89/100 (89.0%) | Not applicable | 195/300 (65.0%) | 0.531; 300/300 |
| GPT-5.6 Luna | Galaxy | Unavailable | 85/100 (85.0%) | 189/298 (63.4%) | 234/279 (83.9%) | 10.238; 290/300 |
| GPT-5.6 Luna | Open-ended code | Unavailable | 78/100 (78.0%) | Not applicable | 238/300 (79.3%) | 1.449; 300/300 |
| DeepSeek V4 Pro 0813 (Codex) | Galaxy | Unavailable | 77/100 (77.0%) | 172/300 (57.3%) | 220/295 (74.6%) | 8.479; 300/300 |
| DeepSeek V4 Pro 0813 (Codex) | Open-ended code | Unavailable | 72/100 (72.0%) | Not applicable | 231/297 (77.8%) | 2.408; 299/300 |

Each task contributes three runs/configuration/environment. Accepted-answer reliability is used for BixBench; CompBio can only report answer-text consistency, never correctness. Galaxy job errors and nonzero shell exits are different instruments. A shell exit may be a probe or failed search; Galaxy analysis is often offloaded to server jobs, so fewer shell exits do not establish easier execution. Shell denominators require at least one numeric recorded exit code: the superseded Claude Code traces contain no numeric exit codes and are unavailable, not zero failures. Tokens describe archived primary turns, not full execution cost. Missing data are excluded with explicit denominators; all observed outcomes are included.

### Table C10. Outlier case: what can actually be said about biomedical knowledge?

| Configuration | Environment | Submitted outlier index: replicate count | Runs with Galaxy job errors | Accepted answers |
| --- | --- | --- | --- | --- |
| GPT-5.5 | Galaxy | 4: 1/3; 9: 2/3 | 2/3 (66.7%) | Unavailable |
| GPT-5.5 | Open-ended code | 9: 3/3 | Not applicable | Unavailable |
| GPT-5.6 Sol | Galaxy | 1: 1/3; 4: 2/3 | 1/3 (33.3%) | Unavailable |
| GPT-5.6 Sol | Open-ended code | 4: 3/3 | Not applicable | Unavailable |
| GPT-5.6 Luna | Galaxy | 9: 3/3 | 1/3 (33.3%) | Unavailable |
| GPT-5.6 Luna | Open-ended code | 8: 1/3; 9: 2/3 | Not applicable | Unavailable |
| DeepSeek V4 Pro 0813 (Codex) | Galaxy | 4: 1/3; 8: 1/3; 9: 1/3 | 3/3 (100.0%) | Unavailable |
| DeepSeek V4 Pro 0813 (Codex) | Open-ended code | 1: 1/3; 4: 1/3; 8: 1/3 | Not applicable | Unavailable |

The task asks which of ten tagAlign files comes from a different assay. Missing item scores prevent saying that most agents were wrong or assigning a biomedical-knowledge error rate. In GPT-5.5 Galaxy replicate 1, the trace records an unsuccessful external checksum lookup, then binned coverage correlations, chromosome distribution, strand correlation and transcription-start-site enrichment; it explicitly considers cell-line copy-number differences as an alternative explanation. These are documented diagnostic choices, not proof that the final index 9 is correct. Source: [task evidence](CompBio/analysis/odd-one-out-q1/history_analysis_evidence.json); trace lines 29, 30, 38 and 44 in `results.deep.case_sources`. Operational errors and uncertain scientific interpretation must remain separate.

## 3) IWC analysis

**Finding:** recorded output agreement is high on many IWC tasks, but is not uniformly high across runs. In the exploratory nine-task subset, Galaxy-minus-code mean differences range from about 0.001 to 0.082. The two larger differences are concentrated in tasks with zero-scored code runs; Sol and Luna change sign under leave-one-task-out analysis, and Luna's contrast reverses when conflicted host-removal scores are included. No explicit user-defined-tool helper requests were detected, but this does not establish native-tool sufficiency or Galaxy-only analysis. The archive contains 10 workflow tasks, four configurations, two environments and three replicates (240 runs). The endpoint is continuous task-specific output agreement (0-1), not binary acceptance, and is never pooled with BixBench acceptance.

### Table I1. Matched output agreement on the common nine IWC tasks

| Configuration | Galaxy: numeric runs; mean (median) | open-ended code: numeric runs; mean (median) | Exactly zero scores: Galaxy / open-ended code | Galaxy - open-ended code, nine matched tasks [95% confidence interval] |
| --- | --- | --- | --- | --- |
| GPT-5.5 | 27; 0.9493 (1.0000) | 27; 0.8675 (0.9997) | 1/27 / 3/27 | 0.0818 [0.0040, 0.2232] |
| GPT-5.6 Sol | 27; 0.9895 (1.0000) | 27; 0.9881 (0.9997) | 0/27 / 0/27 | 0.0014 [-0.0058, 0.0094] |
| GPT-5.6 Luna | 27; 0.9837 (0.9979) | 27; 0.9828 (1.0000) | 0/27 / 0/27 | 0.0010 [-0.0034, 0.0076] |
| DeepSeek V4 Pro (Codex, IWC) | 27; 0.9992 (1.0000) | 27; 0.9224 (1.0000) | 0/27 / 2/27 | 0.0768 [0.0019, 0.1849] |
| All four | 108; 0.9804 (1.0000) | 108; 0.9402 (1.0000) | 1/108 / 5/108 | 0.0402 [0.0095, 0.0775] |

Agreement is the saved `iwc-final-answer-v2.2` `reference_accuracy`. Its definition and tolerance are task-specific (I3), so a mean is a task-weighted summary, not biological accuracy. Every column uses the same nine tasks: 27 runs per environment/configuration, 108 per environment in All four. Host removal is excluded from both environments for all models because of null and conflicted route scores (I6). This is a post hoc sensitivity population, not a prespecified primary endpoint; all-ten-task summaries remain in I3 and I13. Three unsupported-route scores remain unknown, never zero. Differences average replicates within task, then weight tasks equally. For All four, it averages the 36 task/configuration differences. Intervals resample the nine tasks, 20,000 times, seed 20260922. The IWC report's 10,000-resample intervals (seed 20260923) differ slightly; the point estimates are identical and checked by the generator. With nine clusters, percentile coverage is approximate. No equivalence margin was prespecified.

### Table I2. Continuous replicate dispersion on the same nine tasks

| Configuration | Environment | Evaluable task cells | Within-cell range: median (Q1-Q3) | Largest within-cell range | Observed score range | Exactly zero scores / runs |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Galaxy | 9/9 | 0.0044 (0.0000-0.0372) | 1.0000 | 0.0000 to 1.0000 | 1/27 |
| GPT-5.5 | Open-ended code | 9/9 | 0.0086 (0.0000-0.1418) | 0.9961 | 0.0000 to 1.0000 | 3/27 |
| GPT-5.6 Sol | Galaxy | 9/9 | 0.0022 (0.0000-0.0049) | 0.0744 | 0.9079 to 1.0000 | 0/27 |
| GPT-5.6 Sol | Open-ended code | 9/9 | 0.0000 (0.0000-0.0026) | 0.0715 | 0.9227 to 1.0000 | 0/27 |
| GPT-5.6 Luna | Galaxy | 9/9 | 0.0035 (0.0000-0.0062) | 0.1148 | 0.8675 to 1.0000 | 0/27 |
| GPT-5.6 Luna | Open-ended code | 9/9 | 0.0000 (0.0000-0.0005) | 0.1684 | 0.7956 to 1.0000 | 0/27 |
| DeepSeek V4 Pro (Codex, IWC) | Galaxy | 9/9 | 0.0000 (0.0000-0.0006) | 0.0092 | 0.9908 to 1.0000 | 0/27 |
| DeepSeek V4 Pro (Codex, IWC) | Open-ended code | 9/9 | 0.0072 (0.0000-0.0648) | 0.9997 | 0.0000 to 1.0000 | 2/27 |

One cell is one task, configuration and environment with three numeric replicates; all columns use the I1 population. Within-cell range is maximum minus minimum across the three scores, summarized over nine cells. These continuous summaries introduce no pass threshold. Small dispersion can accompany consistently low agreement and is not correctness. With only three runs per cell, this is descriptive repeatability, not a stable variance estimate. Host-removal exclusions are retained in I6; replicate labels are not matched seeds.

### Table I3. Task-level agreement, zero-scored runs and Galaxy job errors

| Task | Scored object | Galaxy mean (minimum) | open-ended code mean (minimum) | Numeric runs Galaxy / open-ended code | Zero-scored runs Galaxy / open-ended code | Galaxy error/non-fetch jobs | Score conflicts |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [wf_001_short_read_qc_trim](IWC/analysis/wf_001_short_read_qc_trim/history_analysis.md) | Transformation and retained paired-read-ID F1 | 0.9989 (0.996) | 0.9997 (0.996) | 12 / 12 | 0 / 0 | 22/53 | 0 |
| [wf_002_rnaseq_de_visualization](IWC/analysis/wf_002_rnaseq_de_visualization/history_analysis.md) | Composite DE gene agreement | 0.9995 (0.994) | 1.0000 (1.000) | 12 / 12 | 0 / 0 | 14/134 | 0 |
| [wf_003_host_contamination_removal](IWC/analysis/wf_003_host_contamination_removal/history_analysis.md) | Transformation-aware paired-read score; route-registered | 0.8788 (0.273) | 1.0000 (1.000) | 12 / 9 | 0 / 0 | 21/83 | 5 |
| [wf_005_amplicon_dada2_pe_denoising](IWC/analysis/wf_005_amplicon_dada2_pe_denoising/history_analysis.md) | Exact ASV and sample-abundance F1 | 0.9586 (0.918) | 0.7967 (0.000) | 12 / 12 | 0 / 2 | 25/276 | 0 |
| [wf_006_atacseq_chromatin_accessibility](IWC/analysis/wf_006_atacseq_chromatin_accessibility/history_analysis.md) | Peak-interval F1, reciprocal overlap >=0.5 | 0.9978 (0.994) | 0.9903 (0.923) | 12 / 12 | 0 / 0 | 27/200 | 12 |
| [wf_007_vgp_mitogenome_assembly](IWC/analysis/wf_007_vgp_mitogenome_assembly/history_analysis.md) | Canonical 31-mer multiset F1 | 0.9133 (0.000) | 0.8255 (0.000) | 12 / 12 | 1 / 2 | 18/75 | 0 |
| [wf_008_amr_gene_detection](IWC/analysis/wf_008_amr_gene_detection/history_analysis.md) | Resistance-determinant F1, allele-specific | 1.0000 (1.000) | 1.0000 (1.000) | 12 / 12 | 0 / 0 | 0/39 | 0 |
| [wf_009_clinicalmp_peptide_verification](IWC/analysis/wf_009_clinicalmp_peptide_verification/history_analysis.md) | Peptide-UniProt accession pair F1 | 0.9579 (0.868) | 0.9394 (0.796) | 12 / 12 | 0 / 0 | 25/203 | 0 |
| [wf_010_pseudobulk_scrna_de](IWC/analysis/wf_010_pseudobulk_scrna_de/history_analysis.md) | Count-matrix and calibrated DE agreement | 0.9979 (0.977) | 0.9102 (0.000) | 12 / 12 | 0 / 1 | 50/204 | 0 |
| [wf_011_bioproject_metadata_sequence_retrieval](IWC/analysis/wf_011_bioproject_metadata_sequence_retrieval/history_analysis.md) | Project/run/layout, metadata and run-content F1 | 1.0000 (1.000) | 1.0000 (1.000) | 12 / 12 | 0 / 0 | 0/85 | 0 |

All ten tasks are shown because IWC has too few tasks for a selection rule. Each environment has 12 runs per task (four configurations x three replicates). Minimums expose low-scoring runs that means can conceal; no distributional modality is assumed. Host removal has different model composition (12 versus nine numeric runs) and is not a matched contrast. Jobs are deduplicated within task and include legacy upload. Error jobs coexist with near-ceiling agreement: short-read QC has 22 Galaxy error jobs yet a minimum Galaxy agreement of 0.996. Score conflicts are records whose evaluator and run-record scores differ by more than 1e-9, or where one is null. Definitions come from retained evaluator `metric` records and are abbreviated here.

### Table I4. How much of the environment difference rests on a few runs?

| Configuration | Galaxy - open-ended code, nine tasks | Leave-one-task-out range | Sign stable | Excluding tasks with a zero-scored run | Retaining host removal where fully scored |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 | 0.0818 | 0.0132 to 0.0920 | Yes | 0.0124 (2 removed) | 0.0818 (9 tasks; 9 pairs) |
| GPT-5.6 Sol | 0.0014 | -0.0018 to 0.0040 | No | 0.0014 (0 removed) | 0.0012 (10 tasks; 10 pairs) |
| GPT-5.6 Luna | 0.0010 | -0.0020 to 0.0021 | No | 0.0010 (0 removed) | -0.0476 (10 tasks; 10 pairs) |
| DeepSeek V4 Pro (Codex, IWC) | 0.0768 | 0.0447 to 0.0865 | Yes | 0.0037 (2 removed) | 0.0691 (10 tasks; 10 pairs) |
| All four | 0.0402 | 0.0250 to 0.0454 | Yes | 0.0041 (3 removed) | 0.0247 (10 tasks; 39 pairs) |

Four decimals are kept because several differences are about 1e-3. Sign stable means all nine leave-one-task-out estimates share the full estimate's sign. The zero-run column drops every task with a zero-scored run for that configuration in either environment. It is an outcome-selected influence diagnostic, not a mechanism test or an improved performance estimate; it never replaces the full estimate. The last column adds host removal wherever all six runs are numeric. This drops the unmatched GPT-5.5 cell, and Luna then includes the two conflicted Galaxy records (I6). The All four available-pair row weights 39 task/configuration pairs equally, so host removal has three configurations and other tasks four; it is not equal task weighting over ten tasks. The two larger positive differences shrink when tasks containing zero-scored runs are removed. Across configurations, the remaining differences range from 0.0010 to 0.0124.

### Table I5. Completion is not correctness: every run scoring below 0.5

| Task / run | Environment | Saved score / run-record score | Recorded evaluator reason or status | Galaxy error jobs in run |
| --- | --- | --- | --- | --- |
| [wf_003_host_contamination_removal](IWC/analysis/wf_003_host_contamination_removal/history_analysis.md); GPT-5.6 Luna r1 | Galaxy | 0.273 / 0.9999 | Score conflict: saved 0.273 versus run-record value; no evaluator route record despite a BWA-family declaration | 3 |
| [wf_003_host_contamination_removal](IWC/analysis/wf_003_host_contamination_removal/history_analysis.md); GPT-5.6 Luna r3 | Galaxy | 0.273 / 1.0000 | Score conflict: saved 0.273 versus run-record value; no evaluator route record despite a BWA-family declaration | 3 |
| [wf_005_amplicon_dada2_pe_denoising](IWC/analysis/wf_005_amplicon_dada2_pe_denoising/history_analysis.md); GPT-5.5 r1 | Open-ended code | 0.000 / 0.0000 | Evaluator error: required per-sample columns missing; the submitted sample identifiers changed letter case | Not applicable |
| [wf_005_amplicon_dada2_pe_denoising](IWC/analysis/wf_005_amplicon_dada2_pe_denoising/history_analysis.md); GPT-5.5 r3 | Open-ended code | 0.000 / 0.0000 | Evaluator error: required per-sample columns missing; the submitted sample identifiers changed letter case | Not applicable |
| [wf_007_vgp_mitogenome_assembly](IWC/analysis/wf_007_vgp_mitogenome_assembly/history_analysis.md); GPT-5.5 r1 | Galaxy | 0.000 / 0.0000 | Sequence-content (31-mer) agreement of zero; no evaluator error text | 0 |
| [wf_007_vgp_mitogenome_assembly](IWC/analysis/wf_007_vgp_mitogenome_assembly/history_analysis.md); DeepSeek V4 Pro (Codex, IWC) r2 | Open-ended code | 0.000 / 0.0000 | Sequence-content (31-mer) agreement of zero; no evaluator error text | Not applicable |
| [wf_007_vgp_mitogenome_assembly](IWC/analysis/wf_007_vgp_mitogenome_assembly/history_analysis.md); GPT-5.5 r1 | Open-ended code | 0.000 / 0.0000 | Sequence-content (31-mer) agreement of zero; no evaluator error text | Not applicable |
| [wf_010_pseudobulk_scrna_de](IWC/analysis/wf_010_pseudobulk_scrna_de/history_analysis.md); DeepSeek V4 Pro (Codex, IWC) r3 | Open-ended code | 0.000 / 0.0000 | Evaluator error: FDR is not a Benjamini-Hochberg adjustment of submitted p-values (maximum deviation 0.00342; tolerance 1e-6) | Not applicable |

All 240 harness records report `complete`; completion alone does not establish final-artifact validity. The <0.5 selection is an auditor screening rule for inspection, not a benchmark failure threshold. Five of the eight runs are open-ended code runs. The only zero-scored Galaxy run is mitogenome assembly GPT-5.5 r1, and the same configuration and replicate also scored zero in open-ended code. The other two Galaxy rows are score-conflicted host-removal records, not established scientific failures; final adjudicated values are unknown. Reasons summarize saved evaluator fields where present; casing is documented in the IWC report. No answer was repaired or regraded.

### Table I6. Score provenance that changes an IWC conclusion

| Issue | Records | Consequence |
| --- | --- | --- |
| Unsupported-route nulls | 3 (GPT-5.5 open-ended code host removal r1-r3) | Kept as unknown; the matched cell is unevaluable and host removal is excluded from the exploratory nine-task contrast |
| Host-removal evaluator/run-record conflicts | 5, including the three nulls | Luna's difference is 0.001 without host removal and -0.048 with it |
| Chromatin-accessibility conflicts | 12 | Saved evaluator version reported; lineage freeze required |
| All conflicts | 17/240 | Neither source is chosen as more favourable; both are retained in the audit |

This table plays the role of C1: score lineage is part of the result. The conflict tolerance is an absolute difference above 1e-9, or numeric versus null. Source: [IWC scientific audit](IWC/iwc_scientific_audit.json), `runs[*].score`, `run_record_acc` and `score_conflict_gt_1e_9`.

### Table I7. Galaxy execution, missing evidence and recovery candidates

| Measure | Observed |
| --- | --- |
| Detailed Galaxy histories, run-linked | 118/120 (98.3%) |
| Metadata-only / unavailable run-linked histories | 2 / 0 |
| Distinct non-fetch creating jobs | 1,352 |
| Job states: ok / error / deleted / paused | 1,134 / 202 / 16 / 0 |
| Error jobs / non-fetch jobs | 202/1,352 (14.9%) |
| Runs with >=1 error job / detailed runs | 75/118 (63.6%) |
| Error jobs/run: median (Q1-Q3); range | 1.0 (0.0-2.8); 0-14 |
| Candidate recovery episodes / runs containing one | 41 / 26 |
| Adjudicated recovery rate; failures before correct answer | Unavailable; Unavailable |
| Certified Galaxy-only completion | Unavailable |

Harmonized with B4/C3: jobs are deduplicated by server and native job ID, data fetch is excluded and legacy upload is kept. That gives 1,352 jobs, the IWC report's 1,330 non-acquisition jobs plus 22 upload1 jobs; error and deleted counts are identical. The two metadata-only histories are amplicon-denoising runs capped at 300 contents by the collector. Their failure counts are unknown, not zero. The 41 candidates collapse to 27 distinct successful endpoints and are not verified recoveries. No equivalent detector exists for open-ended code.

### Table I8. Observable triplicate path agreement under the harmonized rule

| Environment | Configuration | Eligible/total | Identical | Two identical | All distinct | Mean Jaccard |
| --- | --- | --- | --- | --- | --- | --- |
| Galaxy | GPT-5.5 | 10/10 | 4 | 2 | 4 | 0.720 |
| Galaxy | GPT-5.6 Sol | 10/10 | 2 | 2 | 6 | 0.547 |
| Galaxy | GPT-5.6 Luna | 9/10 | 1 | 2 | 6 | 0.576 |
| Galaxy | DeepSeek V4 Pro (Codex, IWC) | 9/10 | 2 | 4 | 3 | 0.628 |
| Galaxy | All configurations | 38/40 | 9 | 10 | 19 | 0.619 |
| Open-ended code | GPT-5.5 | 10/10 | 0 | 0 | 10 | 0.701 |
| Open-ended code | GPT-5.6 Sol | 10/10 | 0 | 2 | 8 | 0.688 |
| Open-ended code | GPT-5.6 Luna | 10/10 | 0 | 0 | 10 | 0.678 |
| Open-ended code | DeepSeek V4 Pro (Codex, IWC) | 10/10 | 0 | 0 | 10 | 0.662 |
| Open-ended code | All configurations | 40/40 | 0 | 2 | 38 | 0.683 |

One cell = task x configuration x environment with three replicate labels. This report harmonizes all three benchmarks: all three fingerprints must be observed and nonempty. Identical / two identical / all distinct partition evaluable cells. Jaccard = intersection/union, averaged over the three replicate pairs and then over eligible cells. Galaxy uses version-stripped job tool IDs (excluding data fetch, retaining legacy upload); code uses the archived closed command vocabulary. These instruments cannot rank scientific consistency across environments; order, most parameters and biological validity are unmeasured. The legacy IWC fingerprint output is not used. Declared biological routes are in I12.

### Table I9. Input-token burden by configuration

| Configuration | Paired cells | Ratio median (Q1-Q3) | Ratio [95% confidence interval] | Median input Galaxy / open-ended code | Pairs with Galaxy > open-ended code |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 | 10 | 1.66 (0.74-2.26) | 1.66 [0.55, 3.55] | 2,348,529.5 / 1,189,287.5 | 7/10 (70.0%) |
| GPT-5.6 Sol | 10 | 2.77 (0.99-4.45) | 2.77 [0.87, 4.70] | 4,228,502.0 / 1,434,707.5 | 7/10 (70.0%) |
| GPT-5.6 Luna | 10 | 2.41 (0.81-4.66) | 2.41 [0.67, 5.04] | 10,156,767.0 / 3,656,912.0 | 6/10 (60.0%) |
| DeepSeek V4 Pro (Codex, IWC) | 10 | 2.10 (0.62-6.01) | 2.10 [0.51, 7.61] | 6,343,374.5 / 2,077,086.5 | 6/10 (60.0%) |
| All configurations | 40 | 1.88 (0.74-4.78) | 1.88 [0.77, 4.87] | 4,709,837.5 / 2,020,078.0 | 26/40 (65.0%) |

Ratio = median input tokens of three Galaxy runs / median of three code runs for the same task and configuration; all six totals must be available. Q1-Q3 are quartile endpoints. Absolute medians use every available run in that row and are not the numerator/denominator of the paired median ratio. Cached input is already included. Output/reasoning are not added. Usage covers archived primary turns, not full campaign, compute or monetary cost. Failed runs are retained; missing usage is never zero. IWC usage is the audited terminal record, one per run, 240/240. Typical usage is higher in Galaxy, but summed input is lower: 815.8 million in Galaxy versus 919.6 million in open-ended code, because of a long open-ended code upper tail. The ratio medians reproduce the IWC report's 1.66-2.77 within-task ratios. With ten task clusters, every IWC interval includes one, so the typical direction is uncertain across the resampled task population. These intervals do not estimate monetary or causal overhead.

### Table I10. Most frequently recorded Galaxy operations

| Recorded tool / version | Non-fetch jobs | Error jobs |
| --- | --- | --- |
| tp_awk_tool/9.11+galaxy0 | 163 | 0 |
| fastp/1.3.6+galaxy0 | 94 | 44 |
| dada2_mergePairs/1.38.0+galaxy1 | 69 | 11 |
| dada2_filterAndTrim/1.38.0+galaxy1 | 65 | 10 |
| pepquery2/2.0.2+galaxy2 | 58 | 21 |
| pysradb_search/2.5.1+galaxy0 | 51 | 0 |

Top six tool IDs by job count among 1,352 deduplicated non-fetch jobs. Five of the six are domain workflow wrappers (read trimming, amplicon denoising, peptide verification, SRA metadata search), versus two of six in B9 and C8, where table utilities dominate. This fits tasks derived from Galaxy workflows. The top operation is still a text utility (awk). Counts include inherited or later history state; frequency is not success attribution.

### Table I11. Observed helper exposure and Tool Shed use in IWC

| Configuration | UDT helper in recorded list | Detected named-helper requests | Request-linked UDT jobs | Detailed histories with an ok Tool Shed job outside utility codebook | Interactive-tool histories / detailed histories | All-run Galaxy agreement: median (Q1-Q3); numeric n |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | 0/30 | 0 | 0 | 30/30 (100.0%) | 0/30 (0.0%) | 1.0000 (0.9853-1.0000); 30 |
| GPT-5.6 Sol | 0/30 | 0 | 0 | 30/30 (100.0%) | 0/30 (0.0%) | 1.0000 (0.9958-1.0000); 30 |
| GPT-5.6 Luna | 0/30 | 0 | 0 | 29/29 (100.0%) | 1/29 (3.4%) | 0.9972 (0.9852-1.0000); 30 |
| DeepSeek V4 Pro (Codex, IWC) | 0/30 | 0 | 0 | 29/29 (100.0%) | 1/29 (3.4%) | 1.0000 (1.0000-1.0000); 30 |
| All four | 0/120 | 0 | 0 | 118/118 (100.0%) | 2/118 (1.7%) | 1.0000 (0.9955-1.0000); 120 |

No named `run_galaxy_udt_and_wait` event or request-linked UDT job was detected. That helper is absent from all 120 recorded `galaxy_mcp_tools` lists. A helper-list omission is evidence about the recorded interface, not proof that every API or shell route to custom code was unavailable or unused. The Tool Shed classifier excludes the declared `UTILITY_REPOS` text/table codebook; it is not an independent audit of domain-tool coverage or task completion. Each of 118 detailed histories contains at least one qualifying successful job, which does not demonstrate that all required operations used such jobs. Two pseudobulk histories include Jupyter interactive-tool jobs. Local shell analysis, arbitrary code within utilities, and inherited jobs are not excluded. Native-tool sufficiency, agent preference and strict Galaxy-only execution remain unestablished; two metadata-only histories are excluded from job denominators (X19).

### Table I12. Declared solution routes versus agreement

| Task | Environment | Cells with three declarations | Cells with one / two / three routes | Mean agreement | Numeric runs contributing to mean |
| --- | --- | --- | --- | --- | --- |
| [wf_002_rnaseq_de_visualization](IWC/analysis/wf_002_rnaseq_de_visualization/history_analysis.md) | Galaxy | 4/4 | 3 / 1 / 0 | 0.9995 | 12 |
| [wf_002_rnaseq_de_visualization](IWC/analysis/wf_002_rnaseq_de_visualization/history_analysis.md) | Open-ended code | 4/4 | 4 / 0 / 0 | 1.0000 | 12 |
| [wf_003_host_contamination_removal](IWC/analysis/wf_003_host_contamination_removal/history_analysis.md) | Galaxy | 4/4 | 1 / 1 / 2 | 0.8788 | 12 |
| [wf_003_host_contamination_removal](IWC/analysis/wf_003_host_contamination_removal/history_analysis.md) | Open-ended code | 4/4 | 1 / 3 / 0 | 1.0000 | 9 |
| [wf_006_atacseq_chromatin_accessibility](IWC/analysis/wf_006_atacseq_chromatin_accessibility/history_analysis.md) | Galaxy | 4/4 | 2 / 2 / 0 | 0.9978 | 12 |
| [wf_006_atacseq_chromatin_accessibility](IWC/analysis/wf_006_atacseq_chromatin_accessibility/history_analysis.md) | Open-ended code | 4/4 | 0 / 3 / 1 | 0.9903 | 12 |
| [wf_010_pseudobulk_scrna_de](IWC/analysis/wf_010_pseudobulk_scrna_de/history_analysis.md) | Galaxy | 3/4 | 0 / 3 / 0 | 0.9979 | 12 |
| [wf_010_pseudobulk_scrna_de](IWC/analysis/wf_010_pseudobulk_scrna_de/history_analysis.md) | Open-ended code | 4/4 | 2 / 2 / 0 | 0.9102 | 12 |

Method declarations were extracted on four tasks; 95/96 are available. Route counts use complete three-declaration cells, whereas means use all numeric runs in each row, including the incompletely declared cell. Host-removal means have unequal model composition. Routes are normalized declarations (for example Bowtie2 plus MACS2, DESeq2 or edgeR), not verified executions. Different declared routes coexist with near-ceiling agreement, which supports scoring valid alternatives against route-specific references. Route-specific references also mean agreement is conditional on route registration (I6).

### Table I13. All-task agreement, replicate dispersion, operational markers and tokens

| Configuration | Environment | Mean agreement; numeric runs | Within-cell range: median (Q1-Q3); evaluable cells | Runs with Galaxy job error | Runs with nonzero shell exit | Median input tokens (millions); coverage |
| --- | --- | --- | --- | --- | --- | --- |
| GPT-5.5 | Galaxy | 0.9544; 30/30 | 0.0022 (0.0000-0.0337); 10 cells | 17/30 (56.7%) | 28/30 (93.3%) | 2.349; 30/30 |
| GPT-5.5 | Open-ended code | 0.8675; 27/30 | 0.0086 (0.0000-0.1418); 9 cells | Not applicable | 28/30 (93.3%) | 1.189; 30/30 |
| GPT-5.6 Sol | Galaxy | 0.9905; 30/30 | 0.0011 (0.0000-0.0046); 10 cells | 20/30 (66.7%) | 18/30 (60.0%) | 4.229; 30/30 |
| GPT-5.6 Sol | Open-ended code | 0.9893; 30/30 | 0.0000 (0.0000-0.0024); 10 cells | Not applicable | 29/30 (96.7%) | 1.435; 30/30 |
| GPT-5.6 Luna | Galaxy | 0.9369; 30/30 | 0.0047 (0.0000-0.0151); 10 cells | 20/29 (69.0%) | 22/30 (73.3%) | 10.157; 30/30 |
| GPT-5.6 Luna | Open-ended code | 0.9845; 30/30 | 0.0000 (0.0000-0.0004); 10 cells | Not applicable | 29/30 (96.7%) | 3.657; 30/30 |
| DeepSeek V4 Pro (Codex, IWC) | Galaxy | 0.9993; 30/30 | 0.0000 (0.0000-0.0005); 10 cells | 18/29 (62.1%) | 27/30 (90.0%) | 6.343; 30/30 |
| DeepSeek V4 Pro (Codex, IWC) | Open-ended code | 0.9302; 30/30 | 0.0054 (0.0000-0.0510); 10 cells | Not applicable | 27/30 (90.0%) | 2.077; 30/30 |

IWC counterpart to B14 and C9, using continuous agreement instead of acceptance. Luna ran at `max` reasoning and the others at `high`, so configuration and reasoning are confounded. Budgets were unbalanced: 6 h or 12 h ceilings differ by configuration and environment. Galaxy job errors and nonzero shell exits are different instruments, as in B14. These are all-ten-task available-case summaries, not the matched population in I1: GPT-5.5 code has nine scored tasks, other rows ten. Do not subtract unequal-population means. These are selected-corpus associations, not general model rankings or measured monetary costs.

## 4) BixBench50 + CompBio + IWC analysis

**Finding:** median within-task input-token ratios exceed one in each archive. Pointwise bootstrap intervals exclude one for the reported BixBench and CompBio configuration ratios, but include one for IWC. This is not a monetary-cost or causal overhead estimate. No common performance gap is estimable: BixBench measures evaluator acceptance, CompBio lacks item-level scores, and IWC measures continuous agreement with unresolved score conflicts. IWC helper-list omissions and observed Tool Shed jobs do not isolate tool coverage from agent capability. Shared evidence supports prioritizing observability, validated input/operation contracts and frozen score lineage. It does not establish a cross-benchmark accuracy benefit or that provenance benefits outweigh resource cost.

### Table X1. What can be combined fairly?

| Endpoint / population | BixBench50 | CompBio | IWC | Combined interpretation |
| --- | --- | --- | --- | --- |
| Task origin | Platform-neutral analysis questions | Platform-neutral computational-biology questions | Derived from published Galaxy IWC workflows | Origin is a descriptive stratum, confounded with endpoint, task set, prompts and tool exposure |
| Archived inventory | 50 tasks; 1,500 runs | 100 tasks; 2,500 runs | 10 tasks; 240 runs | 160 task packages; 4,240 records, not 4,240 independent observations |
| Shared supplied GPT labels (descriptive cross-benchmark set) | 3 configurations; 900 runs | 3 configurations; 1,800 runs | 3 configurations; 180 runs | 2,880 records; IWC runtime and reasoning are audited, the others are not all established |
| DeepSeek | V4 Pro / Codex; superseded Claude Code separate | V4 Pro 0813 / Codex | V4 Pro / Codex (runtime `deepseek-v4-pro`) | Version equivalence unverified; excluded from shared-label cross-benchmark effects |
| Scored endpoint | 1,500 binary acceptance scores | 0/2,500 item scores | 237/240 continuous agreement scores; 17 conflicts | No pooled accuracy, correct-per-token or recovery estimate; agreement is never converted to acceptance |
| Paired input-token ratios | 250/250 all-configuration pairs | 386/400 all-configuration pairs | 40/40 all-configuration pairs | Comparable formula; report benchmark strata and shared-label comparisons |
| Path agreement | Recomputed strict observed/nonempty eligibility | Same strict eligibility | Same strict eligibility | Compare benchmarks within each instrument; no Galaxy-versus-open-ended code consistency ranking |
| Run-linked operational errors | Detailed histories in 714/750 Galaxy records | Detailed histories in 1,198/1,200 Galaxy records | Detailed histories in 118/120 Galaxy records | Available-case burden; collection and task composition confound contrasts |
| User-defined-tool helper | Requested in 267/750 Galaxy transcripts | Requested in 808/1,188 Galaxy transcripts | Absent from 120/120 recorded helper lists | Zero named-helper detections are not proof of zero custom-code use or lack of necessity (X19) |
| Full cost / human review time | Unavailable / unmeasured | Unavailable / unmeasured | Unavailable / unmeasured | Neither monetary efficiency nor faster human review is established |

The historical CompBio source composes final vectors from multiple campaigns, unlike a prospectively fixed independent replicate design. IWC has unbalanced 6 h and 12 h budgets and environment-specific prompts. Prompt additions, harnesses, tools, model verification, domain mix and campaign selection remain confounders. No cross-benchmark pooled accuracy denominator is constructed.

### Table X2. Does relative input-token overhead generalize across benchmarks?

| Shared supplied configuration | Bix pairs; median Galaxy/open-ended code [confidence interval] | CompBio pairs; median Galaxy/open-ended code [confidence interval] | IWC pairs; median Galaxy/open-ended code [confidence interval] | CompBio/Bix median-ratio contrast [confidence interval] | IWC/Bix median-ratio contrast [confidence interval] |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 | 50; 3.86 [2.97, 5.81] | 97; 3.14 [2.37, 3.75] | 10; 1.66 [0.55, 3.55] | 0.81 [0.51, 1.11] | 0.43 [0.12, 0.87] |
| GPT-5.6 Sol | 50; 5.03 [4.06, 6.07] | 100; 6.63 [5.46, 8.58] | 10; 2.77 [0.87, 4.70] | 1.32 [1.00, 1.83] | 0.55 [0.17, 0.99] |
| GPT-5.6 Luna | 50; 7.63 [6.27, 13.60] | 90; 5.73 [4.00, 8.38] | 10; 2.41 [0.67, 5.04] | 0.75 [0.34, 1.20] | 0.32 [0.06, 0.70] |
| All three shared configurations | 150; 5.28 [4.06, 7.07] | 287; 4.83 [3.83, 5.87] | 30; 1.88 [0.82, 4.70] | 0.91 [0.64, 1.28] | 0.36 [0.15, 0.91] |

The contrast columns divide two benchmark-specific medians of within-task ratios; they are not absolute-token ratios. A value above one means greater relative overhead than in BixBench. IWC has ten task clusters, so its intervals are wide. Its lower point estimate cannot be attributed to installed wrappers: prompts, budgets, task selection and open-ended code tails also differ (I9). Benchmark strata are resampled separately, preserving tasks/configurations within clusters. Selection differs and these are observational comparisons. Unless a table specifies otherwise, new intervals are exploratory 95% percentile cluster-bootstrap intervals (20,000 resamples; seed 20260922, with deterministic statistic-specific streams). BixBench resamples eligible source capsules (up to 33); CompBio resamples eligible tasks (up to 100), retaining configurations and replicate bundles. Estimates weight eligible task/configuration cells equally; capsule sizes remain unequal. Cross-benchmark draws are independent and stratified by benchmark. Intervals assume independent clusters, an assumption not established for shared biological inputs. They are pointwise, not multiplicity-adjusted simultaneous intervals. No confirmatory significance, equivalence, non-inferiority or causal claim is made; an interval spanning zero (differences) or one (ratios) is inconclusive.

### Table X3. Does the same path instrument reproduce its agreement across benchmarks?

| Instrument / environment | Bix eligible cells; mean [confidence interval] | CompBio eligible cells; mean [confidence interval] | IWC eligible cells; mean [confidence interval] | CompBio - Bix [confidence interval] | IWC - Bix [confidence interval] |
| --- | --- | --- | --- | --- | --- |
| Galaxy | 138; 0.390 [0.284, 0.496] | 296; 0.134 [0.106, 0.166] | 29; 0.616 [0.493, 0.737] | -0.256 [-0.366, -0.145] | 0.225 [0.065, 0.386] |
| Open-ended code | 150; 0.675 [0.638, 0.713] | 285; 0.581 [0.555, 0.607] | 30; 0.689 [0.642, 0.740] | -0.094 [-0.141, -0.048] | 0.014 [-0.048, 0.077] |

Descriptive population: three shared GPT labels; all three run fingerprints observed and nonempty. This holds the extraction rule and included supplied labels fixed; eligible configuration proportions can still differ. IWC's higher Galaxy tool-set agreement fits workflow-defined tool chains, but rests on ten tasks. It does not control biological task complexity, command-vocabulary coverage, custom-wrapper identity or campaign selection. Lower agreement describes more variable recorded toolsets/command indicators, not worse science. Instrument values must not be directly compared across the two rows.

### Table X4. Run-level operational burden with the shared configuration mix

| Benchmark | Galaxy runs with >=1 non-fetch error / detailed runs | Percentage [95% confidence interval] | Resampling clusters |
| --- | --- | --- | --- |
| BixBench50 | 147/428 (34.3%) | 34.3 [26.4, 42.7] | 33 |
| CompBio | 530/898 (59.0%) | 59.0 [53.9, 64.0] | 100 |
| IWC | 57/89 (64.0%) | 64.0 [40.0, 85.6] | 10 |

Three shared GPT labels only; missing detailed histories are excluded explicitly. Each run contributes one binary indicator, preventing runs with many jobs from dominating this estimate. Histories may contain inherited/later state; this is recorded burden, not a causal benchmark/platform failure probability. No code-condition counterpart uses an equivalent job instrument.

### Table X5. Which operational error messages are observable?

| Exploratory indicator / observability | Bix error jobs (n=552) | CompBio error jobs (n=3,097) | IWC error jobs (n=202) |
| --- | --- | --- | --- |
| Dependency / executable | 15/552 (2.7%) | 42/3,097 (1.4%) | 0/202 (0.0%) |
| Type / numeric / attribute | 47/552 (8.5%) | 100/3,097 (3.2%) | 4/202 (2.0%) |
| File / path / access | 22/552 (4.0%) | 66/3,097 (2.1%) | 22/202 (10.9%) |
| Argument / syntax / encoding | 13/552 (2.4%) | 19/3,097 (0.6%) | 0/202 (0.0%) |
| Network / retrieval | 12/552 (2.2%) | 13/3,097 (0.4%) | 0/202 (0.0%) |
| Memory / resource | 1/552 (0.2%) | 20/3,097 (0.6%) | 4/202 (2.0%) |
| Error jobs with any retained stdout/stderr | 472/552 (85.5%) | 1,476/3,097 (47.7%) | 120/202 (59.4%) |
| Error jobs without retained stdout/stderr | 80/552 (14.5%) | 1,621/3,097 (52.3%) | 82/202 (40.6%) |
| Text present but no rule matched | 368/552 (66.7%) | 1,218/3,097 (39.3%) | 90/202 (44.6%) |
| Error state with recorded exit code zero | 8/552 (1.4%) | 57/3,097 (1.8%) | 21/202 (10.4%) |

All benchmark-specific paired configurations, not just shared GPT labels. Deduplicated non-fetch error jobs; case-insensitive regex matches on retained stderr/stdout excerpts, with overlapping categories. The exact codebook and every source event reference are in the analysis JSON. These are message indicators, not independently adjudicated root causes; missing/truncated logs suppress detection, and absent text does not mean no diagnostic existed on the server. No significance test compares these unequally observed taxonomies. Exit code zero does not override the recorded Galaxy error state. In IWC, fastp and Bowtie2 error jobs retain no text at all (X18), so the generic codebook under-detects its failures.

### Table X6. Where recorded error jobs concentrate

| Benchmark | Recorded tool / version | Error / all jobs for tool |
| --- | --- | --- |
| BixBench50 | kegg_ora/0.1.0+galaxy1 | 62/269 (23.0%) |
| BixBench50 | deseq2/2.11.40.8+galaxy4 | 44/101 (43.6%) |
| BixBench50 | deseq2/2.11.40.8+galaxy3 | 35/59 (59.3%) |
| BixBench50 | featurewise_correlation/0.1.0+galaxy3 | 34/127 (26.8%) |
| BixBench50 | Univariate/2.2.4 | 14/24 (58.3%) |
| CompBio | udt-render-probe-v1 | 57/57 (100.0%) |
| CompBio | upload1 | 56/372 (15.1%) |
| CompBio | anndata_export/0.11.4+galaxy3 | 41/73 (56.2%) |
| CompBio | bcftools_norm/1.24+galaxy0 | 41/76 (53.9%) |
| CompBio | CONVERTER_gz_to_uncompressed | 38/191 (19.9%) |
| IWC | fastp/1.3.6+galaxy0 | 44/94 (46.8%) |
| IWC | edger/3.36.0+galaxy7 | 24/36 (66.7%) |
| IWC | pepquery2/2.0.2+galaxy2 | 21/58 (36.2%) |
| IWC | bowtie2/2.5.5+galaxy0 | 18/48 (37.5%) |
| IWC | mitohifi/3.2.3+galaxy2 | 14/34 (41.2%) |

Top five tool IDs ranked by error-job count within each benchmark (ties ordered by full ID); all non-fetch jobs and all configurations. These are triage targets, not tool-quality rankings: exposure, parameters, input quality, custom wrappers and task mix differ. In particular, udt-render-probe-v1 identifies a diagnostic probe; its error states cannot be assumed to be failed biomedical analyses. IWC error concentrations sit in domain workflow wrappers, the tools its tasks were built around. Full tool IDs and creating-job references are retained in `jobs` in the analysis JSON.

### Table X7. Galaxy improvements suggested by the observed evidence

| Priority / owner | Evidence and limitation | Proposed capability or integration | Prospective success measure |
| --- | --- | --- | --- |
| 1. Galaxy API + agent client: complete audit capture | B4/C3/I7: 32 Bix, 2 CompBio and 2 IWC metadata-only histories; CompBio state summaries disagree | Paginate/resume history collection; reconcile dataset/job states; export run-scoped graph with inherited-job flags and immutable submission/evaluator receipts | Missing-job rate, state disagreements, receipt/hash linkage, blinded audit reconstruction errors |
| 1. Tool wrappers + agent client: typed preflight | C7: string division corrected; X5: numeric/type and dependency indicators; X18: IWC edgeR contrast-level and unset-threshold signatures | Expose column types, sparse/dense matrix capabilities, required executable/version and typed argument checks before launch | Avoidable error jobs per task and accepted-answer rate in a paired ablation; track false rejections |
| 1. Agent client + Galaxy: objective-aware recovery | 93 Bix, 213 CompBio and 41 IWC candidates (27 distinct IWC successes); chunk_X to var is a counterexample | Attach objective IDs and output postconditions to attempts; show input/parameter diffs and require same-objective validation before marking recovery | Adjudicated recovery precision, unresolved objectives, attempts/tokens before a supported result |
| 2. Workflow authors + evaluators: scientific input contracts | B3: rejected RCV and transition/transversion answers despite successful jobs; I5: completed IWC runs failed identifier, FDR and content contracts | Persist cohort/callset, reference release, coordinates, filter thresholds and denominator; validate final result against the declared contract | Scientifically wrong completed runs, parameter/reference mismatches and correct alternatives retained |
| 2. Galaxy API + agent client: compact state and usage ledger | B7/C6/I9/X2: median token ratios above one in all three archives; stage attribution is unavailable | Cache tool schemas, fetch state deltas, batch status queries and attach provider request usage to stages with a mixed/unattributed category | Input/output/cache tokens and latency per task, with acceptance and evidence completeness held to prespecified targets |
| 2. Galaxy reports + user interface: evidence-linked result review | B6/C2: consistency does not imply correctness; no human review study | Show answer, supporting datasets, tool/parameter versions, unresolved errors and score provenance in one reviewable report | Blinded randomized review time, reconstruction accuracy and reviewer agreement under equal information access |
| 1. Evaluators + benchmark maintainers: frozen score lineage | I6: 17 IWC evaluator/run-record conflicts; five host-removal records change the sign of one configuration difference | Freeze evaluator version, reference and route registry; emit one authoritative score with a receipt linking both sources | Conflict count, sign changes under alternative lineage, and reproducible regrading from receipts |
| 2. Agent client + evaluators: matched UDT exposure on Galaxy-native tasks | I11/X19: the IWC helper list omitted the user-defined-tool helper, so native-tool preference cannot be separated from interface design | Run a matched IWC arm with the helper exposed and record catalog search results and rejected alternatives | User-defined-tool request rate under matched exposure, agreement and tokens; audit all execution locations in both arms |

Priorities are analyst proposals, not measured intervention effects or claims that these features are wholly absent. Galaxy already documents [history API and exports](https://docs.galaxyproject.org/en/release_26.1/_modules/galaxy/webapps/galaxy/api/histories.html), [error troubleshooting](https://training.galaxyproject.org/training-material/faqs/galaxy/analysis_troubleshooting.html), [datatype handling](https://training.galaxyproject.org/training-material/faqs/galaxy/datatypes_understanding_datatypes.html) and [workflow reports](https://training.galaxyproject.org/training-material/faqs/galaxy/workflows_report_view.html). The proposed work is to assess and extend these capabilities at the agent interface. Collection limits belong to this audit's collector and are not established Galaxy server limits. Documentation checked 2026-09-23; no deployed-server feature audit was performed.

### Table X8. Claim strength, remaining questions and evidence needed

| Question | Supported answer / strength | Evidence | What would resolve the gap? |
| --- | --- | --- | --- |
| Does Galaxy improve accuracy? | Bix difference is small/uncertain and harness-sensitive; CompBio unassessable; IWC mean agreement differences are positive on nine matched tasks but carried by a few zero-scored open-ended code runs, sign-unstable for Sol and Luna, and reversed for Luna with host removal | B1-B3; I1-I4; X20; finding_accuracy in source manifest | Fixed prospective design, compatible prompts/runtime settings, item evaluator receipts and predefined equivalence/superiority estimand |
| Is input-token usage typically higher in Galaxy? | Observed median ratios exceed one in all archives; pointwise intervals exclude one for BixBench/CompBio but not IWC. IWC summed input is larger in open-ended code; no monetary comparison | B7/C6/I9/X2; token_pairs and finding_cost_readability | All campaigns/subagents, cache accounting, per-call stage usage and compute/storage costs |
| Are consistent paths or answers valid? | Consistency is observable; validity is a separate endpoint | B6/C2/C5/X3; cells and finding_variability | CompBio item scores; common adjudicated biological-method codebook and intermediate outputs |
| Can error causes and recovery be quantified? | Job burden and message indicators yes; comparative scientific recovery rate no | B4/C3/C7/I7/X4-X6; jobs and finding_execution | Complete diagnostics, common-stage attempt mapping, objective-linked endpoints and random adjudication of candidates/noncandidates |
| Does Galaxy make human review easier? | Inspectable provenance exists; improved review performance is unmeasured | Source task packages; X7 | Randomized blinded reconstruction study with equal evidence access and reviewer agreement |
| Do results generalize by difficulty? | No independent difficulty annotation or controlled prompt-version comparison | HISTORY_ANALYSIS_INSTRUCTIONS.md; task metadata | Prospectively defined task-complexity strata and independent benchmark replication |
| Do workflow-derived tasks need fewer user-defined tools? | Not established. Zero named-helper detections and omission from recorded lists do not demonstrate necessity, preference or native-tool sufficiency | I11; X12; X19 | Matched IWC arm with the helper exposed, fixed catalog snapshot and recorded rejected alternatives |
| Is Galaxy more consistent on workflow-derived tasks? | Not established. Continuous replicate dispersion is configuration- and task-dependent; tool fingerprints and score repeatability are different instruments | I2; I4; X20 | More IWC tasks, balanced budgets and prompts, and a prespecified consistency endpoint |

All 160 task evidence paths, hashes, included run IDs and original finding IDs are linked in the [source manifest](BixBench50_CompBio_analysis/source_manifest.json). Table-specific display values and calculated statistics, run/cell denominators, job references and exclusion rules are in the [analysis JSON](BixBench50_CompBio_analysis/analysis.json). Source task evidence is unchanged; no hidden references, recovered agent code, new Galaxy runs or new correctness judgements were used.

### Table X9. Common software families: installed Galaxy wrappers versus code-command indicators

| Software family | BixBench Galaxy | BixBench open-ended code | CompBio Galaxy | CompBio open-ended code | IWC Galaxy | IWC open-ended code |
| --- | --- | --- | --- | --- | --- | --- |
| phykit | 60/428 (14.0%) | 54/450 (12.0%) | 0/898 (0.0%) | 0/900 (0.0%) | 0/89 (0.0%) | 0/90 (0.0%) |
| DESeq2 / PyDESeq2 | 29/428 (6.8%) | 78/450 (17.3%) | 1/898 (0.1%) | 0/900 (0.0%) | 10/89 (11.2%) | 18/90 (20.0%) |
| gseapy | 24/428 (5.6%) | 36/450 (8.0%) | 5/898 (0.6%) | 0/900 (0.0%) | 0/89 (0.0%) | 0/90 (0.0%) |
| samtools | 9/428 (2.1%) | 17/450 (3.8%) | 92/898 (10.2%) | 252/900 (28.0%) | 11/89 (12.4%) | 36/90 (40.0%) |
| bcftools | 9/428 (2.1%) | 10/450 (2.2%) | 41/898 (4.6%) | 105/900 (11.7%) | 0/89 (0.0%) | 7/90 (7.8%) |
| bedtools | 0/428 (0.0%) | 0/450 (0.0%) | 100/898 (11.1%) | 129/900 (14.3%) | 2/89 (2.2%) | 12/90 (13.3%) |
| anndata | 0/428 (0.0%) | 10/450 (2.2%) | 64/898 (7.1%) | 89/900 (9.9%) | 6/89 (6.7%) | 9/90 (10.0%) |
| scanpy | 0/428 (0.0%) | 3/450 (0.7%) | 33/898 (3.7%) | 79/900 (8.8%) | 0/89 (0.0%) | 9/90 (10.0%) |
| datamash | 33/428 (7.7%) | 0/450 (0.0%) | 82/898 (9.1%) | 0/900 (0.0%) | 0/89 (0.0%) | 1/90 (1.1%) |
| bwa | 9/428 (2.1%) | 9/450 (2.0%) | 52/898 (5.8%) | 126/900 (14.0%) | 4/89 (4.5%) | 23/90 (25.6%) |
| fastp | 0/428 (0.0%) | 0/450 (0.0%) | 0/898 (0.0%) | 44/900 (4.9%) | 18/89 (20.2%) | 25/90 (27.8%) |
| bowtie2 | 0/428 (0.0%) | 1/450 (0.2%) | 24/898 (2.7%) | 123/900 (13.7%) | 18/89 (20.2%) | 20/90 (22.2%) |
| minimap2 | 0/428 (0.0%) | 5/450 (1.1%) | 21/898 (2.3%) | 169/900 (18.8%) | 1/89 (1.1%) | 24/90 (26.7%) |
| MACS2 / MACS3 | 0/428 (0.0%) | 0/450 (0.0%) | 12/898 (1.3%) | 44/900 (4.9%) | 7/89 (7.9%) | 9/90 (10.0%) |
| edgeR | 2/428 (0.5%) | 20/450 (4.4%) | 2/898 (0.2%) | 0/900 (0.0%) | 9/89 (10.1%) | 13/90 (14.4%) |
| dada2 | 0/428 (0.0%) | 0/450 (0.0%) | 0/898 (0.0%) | 0/900 (0.0%) | 8/89 (9.0%) | 9/90 (10.0%) |

Three shared GPT configurations. The last six families were added for IWC workflows; earlier rows are unchanged. Galaxy counts runs whose retained jobs name a Tool Shed wrapper from the family; open-ended code uses a declared command-name codebook, including PyDESeq2 as a DESeq2-family implementation. This inventory codebook is separate from the unchanged path-fingerprint vocabulary; shared family labels do not imply equivalent implementations or versions. Denominators require detailed histories or retrieved transcripts, respectively. Indicators are nonexclusive and their visibility differs: libraries inside custom tools can be hidden, and a command mention is not a verified invocation. This answers which families are observable in both conditions; it is not a fair count of equivalent scientific operations or proof of absent software. Workflow-derived task origin motivates checking tool coverage, but does not establish that every required tool/version was available on the recorded server.

### Table X10. Environment comparison using a shared, limited operational marker

| Benchmark | Complete task/configuration pairs | Galaxy: runs with nonzero shell exit | Open-ended code: runs with nonzero shell exit | Galaxy minus open-ended code (percentage points) [95% interval] |
| --- | --- | --- | --- | --- |
| BixBench50 | 200 | 389/600 (64.8%) | 463/600 (77.2%) | -12.33 [-19.61, -4.50] |
| CompBio | 363 | 645/1,089 (59.2%) | 810/1,089 (74.4%) | -15.15 [-19.38, -10.76] |
| IWC | 40 | 95/120 (79.2%) | 113/120 (94.2%) | -15.00 [-24.17, -5.81] |

Each pair requires six transcripts with at least one numeric shell exit code per run. The superseded Claude Code configuration is excluded because its exit codes are unobserved. Intervals resample capsules/tasks with all eligible configuration bundles. Only the shell channel is compared: searches, probes and package checks can return nonzero, while Galaxy job failures can be returned as successful API calls. Thus this marker does not answer whether Galaxy has more scientific failures or is intrinsically harder. Higher Galaxy input-token use (B7/C6), server-job errors (B4/C3) and concrete wrapper-binding friction (X15) are distinct, supported forms of burden.

### Table X11. Task specification size and recorded workload versus operational failure markers

| Benchmark | Environment | Exposure | Response | Complete tasks | Spearman correlation [95% interval] |
| --- | --- | --- | --- | --- | --- |
| BixBench50 | Galaxy | Prompt word count | Runs with Galaxy job error | 42 | 0.473 [0.159, 0.713] |
| BixBench50 | Galaxy | Median recorded non-fetch jobs/run | Error jobs / recorded jobs | 42 | 0.067 [-0.286, 0.378] |
| BixBench50 | Open-ended code | Prompt word count | Runs with nonzero shell exit | 50 | 0.502 [0.241, 0.680] |
| CompBio | Galaxy | Prompt word count | Runs with Galaxy job error | 99 | 0.187 [-0.015, 0.382] |
| CompBio | Galaxy | Median recorded non-fetch jobs/run | Error jobs / recorded jobs | 99 | 0.006 [-0.206, 0.208] |
| CompBio | Open-ended code | Prompt word count | Runs with nonzero shell exit | 99 | 0.175 [-0.033, 0.366] |
| IWC | Galaxy | Prompt word count | Runs with Galaxy job error | 9 | 0.103 [-0.695, 0.803] |
| IWC | Galaxy | Median recorded non-fetch jobs/run | Error jobs / recorded jobs | 9 | 0.193 [-0.858, 0.802] |
| IWC | Open-ended code | Prompt word count | Runs with nonzero shell exit | 10 | 0.539 [-0.062, 0.926] |

Three shared GPT configurations; nine observed runs are required per task/environment. Prompt word count is a pre-execution task-description-size proxy, not a validated difficulty score. Median job count is a post-execution workload measure; retries increase it, creating reverse causation. The job response divides recorded errors by recorded jobs to reduce the automatic opportunity effect of simply counting failures. Intervals use 5,000 capsule/task bootstrap resamples, seed 20260922, with ties reranked within each resample. These exploratory, unadjusted associations cannot establish that task complexity causes errors. Independent difficulty labels, budgets and attempt-level chronology are needed.

### Table X12. User-defined tools: explicit requests, tasks reached and linked execution

| Benchmark | Configuration | Requesting runs / retrieved transcripts | Tasks with request | Runs with linked job / requesting runs | Tasks with linked job | Runs with linked successful job |
| --- | --- | --- | --- | --- | --- | --- |
| BixBench50 | GPT-5.5 | 100/150 (66.7%) | 40/50 (80.0%) | 100/100 | 40 | 99 |
| BixBench50 | GPT-5.6 Sol | 52/150 (34.7%) | 26/50 (52.0%) | 51/52 | 26 | 51 |
| BixBench50 | GPT-5.6 Luna | 59/150 (39.3%) | 29/50 (58.0%) | 46/59 | 23 | 46 |
| BixBench50 | DeepSeek V4 Pro (Codex) | 14/150 (9.3%) | 6/50 (12.0%) | 12/14 | 6 | 12 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | 42/150 (28.0%) | 25/50 (50.0%) | 40/42 | 25 | 38 |
| BixBench50 | All configurations | 267/750 (35.6%) | 41/50 (82.0%) | 249/267 | 41 | 246 |
| CompBio | GPT-5.5 | 263/298 (88.3%) | 96/100 (96.0%) | 260/263 | 96 | 132 |
| CompBio | GPT-5.6 Sol | 239/300 (79.7%) | 91/100 (91.0%) | 239/239 | 91 | 224 |
| CompBio | GPT-5.6 Luna | 176/290 (60.7%) | 72/100 (72.0%) | 175/176 | 71 | 114 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | 130/300 (43.3%) | 62/100 (62.0%) | 128/130 | 61 | 97 |
| CompBio | All configurations | 808/1,188 (68.0%) | 97/100 (97.0%) | 802/808 | 97 | 567 |
| IWC | GPT-5.5 | 0/30 (0.0%) | 0/10 (0.0%) | Not applicable (no detected requests) | 0 | 0 |
| IWC | GPT-5.6 Sol | 0/30 (0.0%) | 0/10 (0.0%) | Not applicable (no detected requests) | 0 | 0 |
| IWC | GPT-5.6 Luna | 0/30 (0.0%) | 0/10 (0.0%) | Not applicable (no detected requests) | 0 | 0 |
| IWC | DeepSeek V4 Pro (Codex, IWC) | 0/30 (0.0%) | 0/10 (0.0%) | Not applicable (no detected requests) | 0 | 0 |
| IWC | All configurations | 0/120 (0.0%) | 0/10 (0.0%) | Not applicable (no detected requests) | 0 | 0 |

An explicit request is a run_galaxy_udt_and_wait event. Linked execution requires a declared GalaxyUserTool identifier matching a retained Galaxy job tool ID in the same run; success requires job state ok. Matching IDs supports linkage but does not establish exact chronology or authorship for inherited jobs. Requests alone do not prove submission or execution; unobserved requests are unknown. Four YAML-string representations are not parsed and remain linkage gaps. Jobs invoked through other interfaces can be missed; these are lower-bound detections, not an exhaustive custom-tool inventory. The proposed 30-40% claim depends on its denominator: task coverage, run use and confirmed execution are not interchangeable. IWC has zero detected named-helper requests and the helper is absent from its 120 recorded lists; alternative interfaces and unparsed/missing events are not excluded (X19). Official [user-defined tool documentation](https://galaxyproject.org/tools/user-defined-tools/) describes this capability and recommends existing published tools when suitable.

### Table X13. Are user-defined tool choices stable across repeat executions?

| Benchmark | Configuration | Observable triplicate cells | No replicate requests | Some request | All request | Variable cells: same prompt / same prompt + runtime + reasoning |
| --- | --- | --- | --- | --- | --- | --- |
| BixBench50 | GPT-5.5 | 50 | 10 | 14 | 26 | 14 / 14 |
| BixBench50 | GPT-5.6 Sol | 50 | 24 | 19 | 7 | 19 / 19 |
| BixBench50 | GPT-5.6 Luna | 50 | 21 | 17 | 12 | 17 / 17 |
| BixBench50 | DeepSeek V4 Pro (Codex) | 50 | 44 | 2 | 4 | 2 / 2 |
| BixBench50 | DeepSeek V4 Pro (Claude Code, superseded) | 50 | 25 | 21 | 4 | 21 / 21 |
| BixBench50 | All configurations | 250 | 124 | 73 | 53 | 73 / 73 |
| CompBio | GPT-5.5 | 98 | 4 | 19 | 75 | 2 / 2 |
| CompBio | GPT-5.6 Sol | 100 | 9 | 26 | 65 | 2 / 2 |
| CompBio | GPT-5.6 Luna | 90 | 26 | 20 | 44 | 19 / 19 |
| CompBio | DeepSeek V4 Pro 0813 (Codex) | 100 | 38 | 39 | 23 | 38 / 38 |
| CompBio | All configurations | 388 | 77 | 104 | 207 | 61 / 61 |
| IWC | GPT-5.5 | 10 | 10 | 0 | 0 | 0 / 0 |
| IWC | GPT-5.6 Sol | 10 | 10 | 0 | 0 | 0 / 0 |
| IWC | GPT-5.6 Luna | 10 | 10 | 0 | 0 | 0 / 0 |
| IWC | DeepSeek V4 Pro (Codex, IWC) | 10 | 10 | 0 | 0 | 0 / 0 |
| IWC | All configurations | 40 | 40 | 0 | 0 | 0 / 0 |

One cell is one task/configuration; all three transcripts must be present. The three usage categories partition cells. Same prompt means identical archived prompt-file hashes; the stricter subset additionally requires a single verified runtime ID and reasoning setting. Variation is compatible with stochastic or context-dependent choice, not proof of randomness: input provenance, tool catalogs, prior state, campaign selection and services were not controlled. Missing runtime metadata is not treated as verified agreement. IWC runtime and reasoning come from invocation records; its all-zero cells describe this detector under different recorded helper lists, not a stable agent preference.

### Table X14. Workbench capabilities visibly exercised by agents

| Recorded interface operation | BixBench runs | CompBio runs | IWC runs |
| --- | --- | --- | --- |
| Tool discovery | 693/750 (92.4%) | 919/1,188 (77.4%) | 118/120 (98.3%) |
| Parameter/schema inspection | 544/750 (72.5%) | 840/1,188 (70.7%) | 118/120 (98.3%) |
| History inspection | 685/750 (91.3%) | 1,119/1,188 (94.2%) | 117/120 (97.5%) |
| Ordinary-tool submission requests | 551/750 (73.5%) | 770/1,188 (64.8%) | 112/120 (93.3%) |
| User-defined-tool submission requests | 267/750 (35.6%) | 808/1,188 (68.0%) | 0/120 (0.0%) |
| Explicit waiting/status requests | 89/750 (11.9%) | 231/1,188 (19.4%) | 43/120 (35.8%) |

All Galaxy configurations with retrieved transcripts; nonexclusive run-level counts of named calls. A completed helper call does not by itself prove job success or scientific validity. History creation/copying is not universally measured by these named helpers; it is documented in selected traces and must not be inferred for every run from a linked history. These counts support feature use, not improved human readability. IWC user-defined-tool detections are zero and that helper is absent from recorded lists; this association does not establish why custom code was or was not used.

### Table X15. Why choose a user-defined tool? Distinguishing capability gaps from interface friction

| Case and configuration | Observed evidence | Classification / inference | What it does not establish |
| --- | --- | --- | --- |
| [bix-11-q1](BixBench_50/analysis/bix-11-q1/history_analysis.md); GPT-5.5 Galaxy replicate 1 | Native PhyKIT found; transcript reports rejected parameter binding, then wrong resolved inputs, then a user-defined wrapper | Agent-reported interface/parameter-binding workaround; package capability existed | Not evidence that Galaxy lacked a treeness tool |
| [bix-11-q1](BixBench_50/analysis/bix-11-q1/history_analysis.md); GPT-5.5 Galaxy replicate 2 | Accepted answer, two retained PhyKIT jobs, no explicit user-defined-tool request | Accepted run without a detected named-helper request; custom-tool necessity remains unresolved | Does not show the same interface state or catalog across replicates |
| [bix-11-q1](BixBench_50/analysis/bix-11-q1/history_analysis.md); GPT-5.5 Galaxy replicate 3 | Native PhyKIT found; agent chooses a custom tool for archive handling, group medians and final difference | Agent-reported composition/data-shape preference | Not proof that native composition was impossible or that the decision was random |
| [borzoi-basic-q1](CompBio/analysis/borzoi-basic-q1/history_analysis.md); GPT-5.5 Galaxy replicate 1 | Agent states no ready-made TensorFlow parameter-counting wrapper was exposed, then requests a custom tool | Agent-reported exposed-wrapper gap; unverified catalog absence | No exhaustive contemporaneous catalog or alternative-workflow adjudication |

Purposive mechanism cases, not percentages of all custom-tool use. `results.deep.case_sources` retains exact trace paths, hashes and line-numbered agent statements. The treeness counterexample establishes accepted output with retained PhyKIT jobs and no detected named UDT request, not an exhaustive native-only execution chain. To distinguish necessity from choice prospectively, snapshot catalog/search results, record rejected alternatives and parameter errors, then compare repeated matched tasks with a fixed tool catalog and an independently validated native workflow. The current archive cannot estimate the fraction used because no suitable Galaxy tool existed.

### Table X16. Different recorded paths, identical submitted answers: does the observation hold?

| Benchmark | Environment | Observable path cells | Identical-answer cells | Identical answer with varied paths | Of these, all answers accepted |
| --- | --- | --- | --- | --- | --- |
| BixBench50 | Galaxy | 225 | 135 | 105 | 99 |
| BixBench50 | Open-ended code | 249 | 142 | 129 | 111 |
| CompBio | Galaxy | 390 | 324 | 318 | Unavailable |
| CompBio | Open-ended code | 382 | 303 | 296 | Unavailable |

All benchmark-specific paired configurations; three observed nonempty fingerprints are required. Answer identity uses exact archived submitted text after outer whitespace removal; it does not merge numerically close strings. Path variation means tool-ID/command-token sets differ, not independently adjudicated biological algorithms. BixBench can confirm acceptance; CompBio cannot confirm validity. The counts support multiple observed execution routes to the same answer, with these measurement limits. IWC is excluded: its final chat message is not the scored artifact; declared routes versus continuous agreement are in I12.

### Table X17. Testing the six motivating observations

| Proposed observation | Evidence-based verdict | Supporting tables / unresolved experiment |
| --- | --- | --- |
| Agents can operate core Galaxy features | Supported for recorded discovery, inspection and submission requests; successful jobs separately observed | X14; B4/C3. Universal history creation and Galaxy-only execution still require event attribution |
| Different approaches produce the same valid result | Observed for different fingerprints and identical evaluator-accepted BixBench text; independent scientific validity and biological-method equivalence remain unassessed | X16; B6. CompBio item-level validity remains unavailable |
| Custom tools fill missing Galaxy capabilities in 30-40% of tasks | Not supported as a task-rate or necessity claim; request/task/execution denominators differ | X12-X15. Native capability, parameter binding and workflow composition are distinct explanations |
| Wrong outlier answers reflect missing knowledge and technical mistakes | Cannot quantify from this archive; item-level correctness and independent error adjudication are absent | C10. Observed diagnostic choices contradict a blanket claim that agents found no useful analysis |
| Galaxy makes human validation easier | Plausible interface benefit; not measured in these benchmark records | X7. Randomized blinded reconstruction-time, error and agreement study required |
| On Galaxy-designed tasks, user-defined tools are rarely needed and Galaxy results are consistent and high | Not established as a combined claim. High median IWC agreement and zero detected named-helper requests are observations, not proof of native-tool sufficiency or lack of need for custom code. The nine-task contrasts depend on configuration and low-scoring tasks; two change sign under task omission and Luna reverses with conflicted host-removal scores. Continuous replicate dispersion is reported without a correctness threshold | I1-I4, I11, X19-X20. A matched IWC arm with the helper exposed would test whether agents choose native tools when both are available |

These verdicts evaluate the motivating statements, not a prespecified hypothesis set. All statistical intervals are exploratory. Model capacity, workbench functionality, operational friction, scientific correctness and execution cost remain separate endpoints.

### Table X18. Specific recurring diagnostics and the mechanisms they suggest

| Benchmark | Tool family | Retained diagnostic | Matching / family error jobs | Interpretation and actionable check |
| --- | --- | --- | --- | --- |
| BixBench50 | kegg_ora | Empty background after pathway intersection | 27/62 (43.5%) | Gene identifiers/background did not overlap pathway mappings; validate namespace and background before enrichment. |
| BixBench50 | kegg_ora | Mapping table has too few columns | 19/62 (30.6%) | Input table schema did not match wrapper requirements; validate columns and delimiter. |
| BixBench50 | kegg_ora | Empty foreground after intersection | 10/62 (16.1%) | Selected gene set did not overlap the analysis universe/mappings; inspect upstream selection and identifiers. |
| BixBench50 | deseq2 | Missing factor-list element | 34/79 (43.0%) | Factor configuration was absent or misbound; the message does not identify whether the agent, helper or wrapper caused it. |
| BixBench50 | deseq2 | Duplicate row names or factor levels | 20/79 (25.3%) | Sample labels or factor encoding were not unique; validate the design table before submission. |
| CompBio | CONVERTER_gz_to_uncompressed | Invalid gzip magic | 35/38 (92.1%) | Bytes were not recognized as gzip by the converter; check declared datatype against bytes before conversion. |
| CompBio | bcftools_norm | Unrecognized or unindexable input | 28/41 (68.3%) | Input format or compression/index compatibility failed; check the variant-file format and index prerequisites. |
| CompBio | anndata_export | DataFrame construction failure | 37/41 (90.2%) | The exported matrix did not fit the expected table representation; inspect matrix presence/type and export mode. |
| CompBio | deseq2 | No residual degrees of freedom | 3/4 (75.0%) | Model design could not estimate dispersion; validate replication and design rank before fitting. |
| IWC | fastp | No retained stdout/stderr | 47/47 (100.0%) | This family has the largest observed IWC error count, but no retained stdout/stderr for those jobs; this is not an exposure-adjusted tool-quality ranking or proof that no diagnostic existed. |
| IWC | edger | Contrast names a missing factor level | 11/24 (45.8%) | Contrast strings did not match design-level names; validate contrast levels against the factor encoding before launch. |
| IWC | edger | Count-matrix header/column mismatch | 7/24 (29.2%) | The count matrix did not match the wrapper table contract; validate header and delimiter. |
| IWC | deseq2 | Missing factor-list element | 4/14 (28.6%) | Same signature as BixBench50: factor configuration absent or misbound; the message does not identify the responsible layer. |
| IWC | mitohifi | Empty NCBI Entrez query | 12/14 (85.7%) | The reference lookup received an empty species/accession term; validate lookup parameters before launch. |
| IWC | dada2_mergePairs | Mismatched dereplication and denoising objects | 11/11 (100.0%) | Forward/reverse or sample pairing was inconsistent between steps; validate collection pairing and order. |
| IWC | decoupler_pseudobulk | Unset numeric filter threshold | 11/14 (78.6%) | A threshold parameter reached arithmetic as None; supply explicit numeric filter values. |
| IWC | pepquery2 | Protein FM-index mapping exception | 19/21 (90.5%) | Java exception in protein-database mapping; retained text does not identify the input cause; check database format and size. |

Counts are deduplicated creating jobs; tool versions are pooled within the named family. The denominator contains every error job for that family, including missing/truncated diagnostics. Exact regex rules and matching job/source-event IDs are retained in the analysis JSON. These messages support input, datatype, identifier and design-validation hypotheses; they do not alone assign blame to the model, wrapper or platform. Multiple signatures may overlap. No claim is made that a tool always fails: the diagnostic probe with 57/57 error states in X6 is not a biomedical-analysis success endpoint.

### Table X19. Task origin, recorded helper exposure and detected tool use

| Benchmark | Task origin | Recorded UDT helper list | Runs with detected request / retrieved transcripts | Tasks with detected request / listed tasks | Request-linked job detections / listed runs | Tool Shed jobs outside utility codebook / non-fetch jobs | Interactive-tool histories / detailed histories |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BixBench50 | Platform-neutral | Not recorded; requests show availability | 267/750 (35.6%) | 41/50 (82.0%) | 249/750 (lower-bound count) | 1,393/5,042 (27.6%) | 0/714 (0.0%) |
| CompBio | Platform-neutral | Not recorded; requests show availability | 808/1,188 (68.0%) | 97/100 (97.0%) | 802/1,200 (lower-bound count) | 6,707/16,686 (40.2%) | 0/1,198 (0.0%) |
| IWC | Galaxy workflow-derived | Absent in 120/120 recorded lists | 0/120 (0.0%) | 0/10 (0.0%) | 0/120 (lower-bound count) | 935/1,352 (69.2%) | 2/118 (1.7%) |

All benchmark-specific paired configurations. Requests, linkage and success use the X12 rules. BixBench and CompBio exposure lists were not archived; observed requests show that the helper was available in at least those runs. Request rates and listed-run linkage counts have different denominators. A linkage count divided by all listed runs is a detected lower bound, not an estimate that treats missing transcripts/histories as zero use. IWC has no named-helper detections and its recorded lists omit that helper; neither observation establishes absence of alternative custom-code interfaces. Tool Shed jobs outside the utility codebook (I11) form a larger observed job share in IWC, but this classifier does not prove native completion of every task. Task origin and helper exposure are not experimentally separated. Local shell and interactive computation remain possible; Galaxy-only execution is uncertified in every benchmark.

### Table X20. Distinct benchmark endpoints in the shared-label descriptive set

| Benchmark | Analysis population per environment | Endpoint | Galaxy | open-ended code | Galaxy - open-ended code [95% confidence interval] | Zero recorded scores: Galaxy / open-ended code (benchmark-specific meaning) |
| --- | --- | --- | --- | --- | --- | --- |
| BixBench50 | 50 tasks; 3 configurations; 450 runs | Binary evaluator acceptance | 396/450 (88.0%) | 390/450 (86.7%) | 1.33 [-3.35, 6.50] percentage points | 54/450 (12.0%) / 60/450 (13.3%) |
| CompBio | 100 tasks; 3 configurations; 900 records | Item scores unavailable | Unavailable | Unavailable | Unavailable | Unavailable |
| IWC | 9 tasks; 3 configurations; 81 runs | Continuous agreement (mean) | 0.9742 | 0.9461 | 0.0280 [0.0020, 0.0747] | 1/81 (1.2%) / 3/81 (3.7%) |

Three shared supplied GPT labels, not verified identical runtime/reasoning settings across benchmarks. Endpoints differ, so read rows side by side, never pooled or ranked. BixBench differences are percentage points of acceptance; IWC differences are agreement units on 0-1. All IWC columns use the same nine-task subset as I1; host-removal nulls and conflicts are documented in I6, not relabelled as failures. A BixBench zero denotes evaluator rejection; an IWC zero can reflect a contract check or output disagreement and is not an interchangeable scientific-failure endpoint. CompBio answer-text identity is omitted from this outcome table because it is neither a ceiling score nor correctness (see C2). Task sets, prompts, budgets, interfaces and endpoints differ; whether workflow-derived task origin narrows an environment effect is not identifiable from this comparison.
