# Benchmark Results Tables

Retrospective synthesis of the archived BixBench-50 and CompBioBench analyses. `BixBench50` below maps to the repository's `BixBench_50/` directory. The central questions are whether accepted answers are reliable, what execution records reveal about errors, and which measurable changes could improve Galaxy for agents and users.

**Readout:** Galaxy means the Galaxy application programming interface condition; open-ended code means the agent's own runtime. Intervals are 95% confidence intervals unless specified. Q1 and Q3 are the first and third quartiles. Unavailable never means zero. All GPT-5 configurations use the supplied Codex labels. Replicate numbers are not matched seeds. CompBio vectors are final campaign selections, including continuations/recoveries; they do not measure first-attempt performance.

[Reproduce and inspect](BixBench50_CompBio_analysis/README.md) | [Calculations and table values](BixBench50_CompBio_analysis/analysis.json) | [Task/run/finding source manifest](BixBench50_CompBio_analysis/source_manifest.json).

**Question guide:** exclusive task success and its cause (B11-B13); model capacity, reliability and cost (B14-B15, C9); common software and environmental friction (X9-X10); recurring diagnostics and task specification/workload (X5-X6, X11, X18); user-defined tool necessity versus choice (X12-X15); different routes to the same answer and evidence for the motivating observations (X16-X17). Tables report observations unless explicitly labelled as inference or a proposed intervention.

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

### Table B11. Model capacity: tasks accepted in only one execution condition

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

### Table B14. Model comparison: capacity, consistency, operational burden and cost

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

### Table C9. Model comparison: capacity, consistency, operational burden and cost

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

## 3) BixBench50 + CompBio analysis

**Finding:** input-token overhead appears in both archives, while evidence completeness and operational burden vary substantially. Shared evidence supports prioritizing observability and validated input/operation contracts. It does not establish a cross-benchmark accuracy benefit or that provenance benefits outweigh resource cost.

### Table X1. What can be combined fairly?

| Endpoint / population | BixBench50 | CompBio | Combined interpretation |
| --- | --- | --- | --- |
| Archived inventory | 50 tasks; 1,500 runs | 100 tasks; 2,500 runs | 150 task packages; 4,000 records, not 4,000 independent observations |
| Shared supplied GPT labels (primary cross-benchmark set) | 3 configurations; 900 runs | 3 configurations; 1,800 runs | 2,700 records; exact runtime/reasoning matching not established |
| DeepSeek | V4 Pro / Codex; superseded Claude Code separate | V4 Pro 0813 / Codex | Version equivalence unverified; excluded from primary cross-benchmark effects |
| Task-level accepted answers | 1,500 binary scores | 0/2,500 item scores | No combined accuracy, correct-per-token or correctness/recovery estimate |
| Paired input-token ratios | 250/250 all-configuration pairs | 386/400 all-configuration pairs | Comparable formula; report benchmark strata and shared-label comparisons |
| Path agreement | Recomputed strict observed/nonempty eligibility | Same strict eligibility | Compare benchmarks within each instrument; no Galaxy-versus-open-ended code consistency ranking |
| Run-linked operational errors | Detailed histories in 714/750 Galaxy records | Detailed histories in 1,198/1,200 Galaxy records | Available-case burden; collection and task composition confound contrasts |
| Full cost / human review time | Unavailable / unmeasured | Unavailable / unmeasured | Neither monetary efficiency nor faster human review is established |

The historical CompBio source composes final vectors from multiple campaigns, unlike a prospectively fixed independent replicate design. Prompt additions, harnesses, tools, model verification, domain mix and campaign selection remain confounders. No cross-benchmark pooled accuracy denominator is constructed.

### Table X2. Does relative input-token overhead generalize across benchmarks?

| Shared supplied configuration | Bix pairs; median Galaxy/open-ended code [confidence interval] | CompBio pairs; median Galaxy/open-ended code [confidence interval] | CompBio/Bix median-ratio contrast [confidence interval] |
| --- | --- | --- | --- |
| GPT-5.5 | 50; 3.86 [2.97, 5.81] | 97; 3.14 [2.37, 3.75] | 0.81 [0.51, 1.11] |
| GPT-5.6 Sol | 50; 5.03 [4.06, 6.07] | 100; 6.63 [5.46, 8.58] | 1.32 [1.00, 1.83] |
| GPT-5.6 Luna | 50; 7.63 [6.27, 13.60] | 90; 5.73 [4.00, 8.38] | 0.75 [0.34, 1.20] |
| All three shared configurations | 150; 5.28 [4.06, 7.07] | 287; 4.83 [3.83, 5.87] | 0.91 [0.64, 1.28] |

The last column divides the two benchmark-specific medians of within-task ratios; it is not an absolute-token ratio. A value above one means greater relative overhead in CompBio. Benchmark strata are resampled separately, preserving tasks/configurations within clusters. Selection differs and these are observational comparisons. Unless a table specifies otherwise, new intervals are exploratory 95% percentile cluster-bootstrap intervals (20,000 resamples; seed 20260922, with deterministic statistic-specific streams). BixBench resamples eligible source capsules (up to 33); CompBio resamples eligible tasks (up to 100), retaining configurations and replicate bundles. Estimates weight eligible task/configuration cells equally; capsule sizes remain unequal. Cross-benchmark draws are independent and stratified by benchmark. Intervals assume independent clusters, an assumption not established for shared biological inputs. They are pointwise, not multiplicity-adjusted simultaneous intervals. No confirmatory significance, equivalence, non-inferiority or causal claim is made; an interval spanning zero (differences) or one (ratios) is inconclusive.

### Table X3. Does the same path instrument reproduce its agreement across benchmarks?

| Instrument / environment | Bix eligible cells; mean [confidence interval] | CompBio eligible cells; mean [confidence interval] | CompBio - Bix [confidence interval] |
| --- | --- | --- | --- |
| Galaxy | 138; 0.390 [0.284, 0.496] | 296; 0.134 [0.106, 0.166] | -0.256 [-0.366, -0.145] |
| Open-ended code | 150; 0.675 [0.638, 0.713] | 285; 0.581 [0.555, 0.607] | -0.094 [-0.141, -0.048] |

Primary population: three shared GPT labels; all three run fingerprints observed and nonempty. This holds the extraction rule and included supplied labels fixed; eligible configuration proportions can still differ. It does not control biological task complexity, command-vocabulary coverage, custom-wrapper identity or campaign selection. Lower agreement describes more variable recorded toolsets/command indicators, not worse science. Instrument values must not be directly compared across the two rows.

### Table X4. Run-level operational burden with the shared configuration mix

| Benchmark | Galaxy runs with >=1 non-fetch error / detailed runs | Percentage [95% confidence interval] | Resampling clusters |
| --- | --- | --- | --- |
| BixBench50 | 147/428 (34.3%) | 34.3 [26.4, 42.7] | 33 |
| CompBio | 530/898 (59.0%) | 59.0 [53.9, 64.0] | 100 |

Three shared GPT labels only; missing detailed histories are excluded explicitly. Each run contributes one binary indicator, preventing runs with many jobs from dominating this estimate. Histories may contain inherited/later state; this is recorded burden, not a causal benchmark/platform failure probability. No code-condition counterpart uses an equivalent job instrument.

### Table X5. Which operational error messages are observable?

| Exploratory indicator / observability | Bix error jobs (n=552) | CompBio error jobs (n=3,097) |
| --- | --- | --- |
| Dependency / executable | 15/552 (2.7%) | 42/3,097 (1.4%) |
| Type / numeric / attribute | 47/552 (8.5%) | 100/3,097 (3.2%) |
| File / path / access | 22/552 (4.0%) | 66/3,097 (2.1%) |
| Argument / syntax / encoding | 13/552 (2.4%) | 19/3,097 (0.6%) |
| Network / retrieval | 12/552 (2.2%) | 13/3,097 (0.4%) |
| Memory / resource | 1/552 (0.2%) | 20/3,097 (0.6%) |
| Error jobs with any retained stdout/stderr | 472/552 (85.5%) | 1,476/3,097 (47.7%) |
| Error jobs without retained stdout/stderr | 80/552 (14.5%) | 1,621/3,097 (52.3%) |
| Text present but no rule matched | 368/552 (66.7%) | 1,218/3,097 (39.3%) |
| Error state with recorded exit code zero | 8/552 (1.4%) | 57/3,097 (1.8%) |

All benchmark-specific paired configurations, not just shared GPT labels. Deduplicated non-fetch error jobs; case-insensitive regex matches on retained stderr/stdout excerpts, with overlapping categories. The exact codebook and every source event reference are in the analysis JSON. These are message indicators, not independently adjudicated root causes; missing/truncated logs suppress detection, and absent text does not mean no diagnostic existed on the server. No significance test compares these unequally observed taxonomies. Exit code zero does not override the recorded Galaxy error state.

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

Top five tool IDs ranked by error-job count within each benchmark (ties ordered by full ID); all non-fetch jobs and all configurations. These are triage targets, not tool-quality rankings: exposure, parameters, input quality, custom wrappers and task mix differ. In particular, udt-render-probe-v1 identifies a diagnostic probe; its error states cannot be assumed to be failed biomedical analyses. Full tool IDs and creating-job references are retained in `jobs` in the analysis JSON.

### Table X7. Galaxy improvements suggested by the observed evidence

| Priority / owner | Evidence and limitation | Proposed capability or integration | Prospective success measure |
| --- | --- | --- | --- |
| 1. Galaxy API + agent client: complete audit capture | B4/C3: 32 Bix and 2 CompBio metadata-only histories; CompBio state summaries disagree | Paginate/resume history collection; reconcile dataset/job states; export run-scoped graph with inherited-job flags and immutable submission/evaluator receipts | Missing-job rate, state disagreements, receipt/hash linkage, blinded audit reconstruction errors |
| 1. Tool wrappers + agent client: typed preflight | C7: string division corrected; X5: numeric/type and dependency indicators | Expose column types, sparse/dense matrix capabilities, required executable/version and typed argument checks before launch | Avoidable error jobs per task and accepted-answer rate in a paired ablation; track false rejections |
| 1. Agent client + Galaxy: objective-aware recovery | 93 Bix and 213 CompBio candidates; chunk_X to var is a counterexample | Attach objective IDs and output postconditions to attempts; show input/parameter diffs and require same-objective validation before marking recovery | Adjudicated recovery precision, unresolved objectives, attempts/tokens before a supported result |
| 2. Workflow authors + evaluators: scientific input contracts | B3: rejected RCV and transition/transversion answers despite successful jobs | Persist cohort/callset, reference release, coordinates, filter thresholds and denominator; validate final result against the declared contract | Scientifically wrong completed runs, parameter/reference mismatches and correct alternatives retained |
| 2. Galaxy API + agent client: compact state and usage ledger | B7/C6/X2: median token ratios above one; stage attribution is unavailable | Cache tool schemas, fetch state deltas, batch status queries and attach provider request usage to stages with a mixed/unattributed category | Input/output/cache tokens and latency per task, with acceptance and evidence completeness held to prespecified targets |
| 2. Galaxy reports + user interface: evidence-linked result review | B6/C2: consistency does not imply correctness; no human review study | Show answer, supporting datasets, tool/parameter versions, unresolved errors and score provenance in one reviewable report | Blinded randomized review time, reconstruction accuracy and reviewer agreement under equal information access |

Priorities are analyst proposals, not measured intervention effects or claims that these features are wholly absent. Galaxy already documents [history API and exports](https://docs.galaxyproject.org/en/release_26.1/_modules/galaxy/webapps/galaxy/api/histories.html), [error troubleshooting](https://training.galaxyproject.org/training-material/faqs/galaxy/analysis_troubleshooting.html), [datatype handling](https://training.galaxyproject.org/training-material/faqs/galaxy/datatypes_understanding_datatypes.html) and [workflow reports](https://training.galaxyproject.org/training-material/faqs/galaxy/workflows_report_view.html). The proposed work is to assess and extend these capabilities at the agent interface. Collection limits belong to this audit's collector and are not established Galaxy server limits. Documentation checked 2026-09-22; no deployed-server feature audit was performed.

### Table X8. Claim strength, remaining questions and evidence needed

| Question | Supported answer / strength | Evidence | What would resolve the gap? |
| --- | --- | --- | --- |
| Does Galaxy improve accuracy? | Bix difference is small/uncertain and harness-sensitive; CompBio unassessable | B1-B3; finding_accuracy in source manifest | Fixed prospective design, compatible prompts/runtime settings, item evaluator receipts and predefined equivalence/superiority estimand |
| Is overhead common? | Higher median input-token ratios in both archives; robust descriptive result for observed primary turns | B7/C6/X2; token_pairs and finding_cost_readability | All campaigns/subagents, cache accounting, per-call stage usage and compute/storage costs |
| Are consistent paths or answers valid? | Consistency is observable; validity is a separate endpoint | B6/C2/C5/X3; cells and finding_variability | CompBio item scores; common adjudicated biological-method codebook and intermediate outputs |
| Can error causes and recovery be quantified? | Job burden and message indicators yes; comparative scientific recovery rate no | B4/C3/C7/X4-X6; jobs and finding_execution | Complete diagnostics, common-stage attempt mapping, objective-linked endpoints and random adjudication of candidates/noncandidates |
| Does Galaxy make human review easier? | Inspectable provenance exists; improved review performance is unmeasured | Source task packages; X7 | Randomized blinded reconstruction study with equal evidence access and reviewer agreement |
| Do results generalize by difficulty? | No independent difficulty annotation or controlled prompt-version comparison | HISTORY_ANALYSIS_INSTRUCTIONS.md; task metadata | Prospectively defined task-complexity strata and independent benchmark replication |

All 150 task evidence paths, hashes, included run IDs and original finding IDs are linked in the [source manifest](BixBench50_CompBio_analysis/source_manifest.json). Table-specific display values and calculated statistics, run/cell denominators, job references and exclusion rules are in the [analysis JSON](BixBench50_CompBio_analysis/analysis.json). Source task evidence is unchanged; no hidden references, recovered agent code, new Galaxy runs or new correctness judgements were used.

### Table X9. Common software families: installed Galaxy wrappers versus code-command indicators

| Software family | BixBench Galaxy | BixBench open-ended code | CompBio Galaxy | CompBio open-ended code |
| --- | --- | --- | --- | --- |
| phykit | 60/428 (14.0%) | 54/450 (12.0%) | 0/898 (0.0%) | 0/900 (0.0%) |
| DESeq2 / PyDESeq2 | 29/428 (6.8%) | 78/450 (17.3%) | 1/898 (0.1%) | 0/900 (0.0%) |
| gseapy | 24/428 (5.6%) | 36/450 (8.0%) | 5/898 (0.6%) | 0/900 (0.0%) |
| samtools | 9/428 (2.1%) | 17/450 (3.8%) | 92/898 (10.2%) | 252/900 (28.0%) |
| bcftools | 9/428 (2.1%) | 10/450 (2.2%) | 41/898 (4.6%) | 105/900 (11.7%) |
| bedtools | 0/428 (0.0%) | 0/450 (0.0%) | 100/898 (11.1%) | 129/900 (14.3%) |
| anndata | 0/428 (0.0%) | 10/450 (2.2%) | 64/898 (7.1%) | 89/900 (9.9%) |
| scanpy | 0/428 (0.0%) | 3/450 (0.7%) | 33/898 (3.7%) | 79/900 (8.8%) |
| datamash | 33/428 (7.7%) | 0/450 (0.0%) | 82/898 (9.1%) | 0/900 (0.0%) |
| bwa | 9/428 (2.1%) | 9/450 (2.0%) | 52/898 (5.8%) | 126/900 (14.0%) |

Three shared GPT configurations. Galaxy counts runs whose retained jobs name a Tool Shed wrapper from the family; open-ended code uses a declared command-name codebook, including PyDESeq2 as a DESeq2-family implementation. This inventory codebook is separate from the unchanged path-fingerprint vocabulary; shared family labels do not imply equivalent implementations or versions. Denominators require detailed histories or retrieved transcripts, respectively. Indicators are nonexclusive and their visibility differs: libraries inside custom tools can be hidden, and a command mention is not a verified invocation. This answers which families are observable in both conditions; it is not a fair count of equivalent scientific operations or proof of absent software.

### Table X10. Environment comparison using a shared, limited operational marker

| Benchmark | Complete task/configuration pairs | Galaxy: runs with nonzero shell exit | Open-ended code: runs with nonzero shell exit | Galaxy minus open-ended code (percentage points) [95% interval] |
| --- | --- | --- | --- | --- |
| BixBench50 | 200 | 389/600 (64.8%) | 463/600 (77.2%) | -12.33 [-19.61, -4.50] |
| CompBio | 363 | 645/1,089 (59.2%) | 810/1,089 (74.4%) | -15.15 [-19.38, -10.76] |

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

An explicit request is a run_galaxy_udt_and_wait event. Linked execution requires a declared GalaxyUserTool identifier matching a retained Galaxy job tool ID in the same run; success requires job state ok. Matching IDs supports linkage but does not establish exact chronology or authorship for inherited jobs. Requests alone do not prove submission or execution; unobserved requests are unknown. Four YAML-string representations are not parsed and remain linkage gaps. Jobs invoked through other interfaces can be missed; these are lower-bound detections, not an exhaustive custom-tool inventory. The proposed 30-40% claim depends on its denominator: task coverage, run use and confirmed execution are not interchangeable. Official [user-defined tool documentation](https://galaxyproject.org/tools/user-defined-tools/) describes this capability and recommends existing published tools when suitable.

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

One cell is one task/configuration; all three transcripts must be present. The three usage categories partition cells. Same prompt means identical archived prompt-file hashes; the stricter subset additionally requires a single verified runtime ID and reasoning setting. Variation is compatible with stochastic or context-dependent choice, not proof of randomness: input provenance, tool catalogs, prior state, campaign selection and services were not controlled. Missing runtime metadata is not treated as verified agreement.

### Table X14. Workbench capabilities visibly exercised by agents

| Recorded interface operation | BixBench runs | CompBio runs |
| --- | --- | --- |
| Tool discovery | 693/750 (92.4%) | 919/1,188 (77.4%) |
| Parameter/schema inspection | 544/750 (72.5%) | 840/1,188 (70.7%) |
| History inspection | 685/750 (91.3%) | 1,119/1,188 (94.2%) |
| Ordinary-tool submission requests | 551/750 (73.5%) | 770/1,188 (64.8%) |
| User-defined-tool submission requests | 267/750 (35.6%) | 808/1,188 (68.0%) |
| Explicit waiting/status requests | 89/750 (11.9%) | 231/1,188 (19.4%) |

All Galaxy configurations with retrieved transcripts; nonexclusive run-level counts of named calls. A completed helper call does not by itself prove job success or scientific validity. History creation/copying is not universally measured by these named helpers; it is documented in selected traces and must not be inferred for every run from a linked history. These counts support feature use, not improved human readability.

### Table X15. Why choose a user-defined tool? Distinguishing capability gaps from interface friction

| Case and configuration | Observed evidence | Classification / inference | What it does not establish |
| --- | --- | --- | --- |
| [bix-11-q1](BixBench_50/analysis/bix-11-q1/history_analysis.md); GPT-5.5 Galaxy replicate 1 | Native PhyKIT found; transcript reports rejected parameter binding, then wrong resolved inputs, then a user-defined wrapper | Agent-reported interface/parameter-binding workaround; package capability existed | Not evidence that Galaxy lacked a treeness tool |
| [bix-11-q1](BixBench_50/analysis/bix-11-q1/history_analysis.md); GPT-5.5 Galaxy replicate 2 | Accepted answer, two retained PhyKIT jobs, no explicit user-defined-tool request | Counterexample to task-wide necessity of a user-defined tool | Does not show the same interface state or catalog across replicates |
| [bix-11-q1](BixBench_50/analysis/bix-11-q1/history_analysis.md); GPT-5.5 Galaxy replicate 3 | Native PhyKIT found; agent chooses a custom tool for archive handling, group medians and final difference | Agent-reported composition/data-shape preference | Not proof that native composition was impossible or that the decision was random |
| [borzoi-basic-q1](CompBio/analysis/borzoi-basic-q1/history_analysis.md); GPT-5.5 Galaxy replicate 1 | Agent states no ready-made TensorFlow parameter-counting wrapper was exposed, then requests a custom tool | Agent-reported exposed-wrapper gap; unverified catalog absence | No exhaustive contemporaneous catalog or alternative-workflow adjudication |

Purposive mechanism cases, not percentages of all custom-tool use. `results.deep.case_sources` retains exact trace paths, hashes and line-numbered agent statements. The native-only treeness counterexample is verified from task evidence. To distinguish necessity from choice prospectively, snapshot catalog/search results, record rejected alternatives and parameter errors, then compare repeated matched tasks with a fixed tool catalog and an independently validated native workflow. The current archive cannot estimate the fraction used because no suitable Galaxy tool existed.

### Table X16. Different recorded paths, identical submitted answers: does the observation hold?

| Benchmark | Environment | Observable path cells | Identical-answer cells | Identical answer with varied paths | Of these, all answers accepted |
| --- | --- | --- | --- | --- | --- |
| BixBench50 | Galaxy | 225 | 135 | 105 | 99 |
| BixBench50 | Open-ended code | 249 | 142 | 129 | 111 |
| CompBio | Galaxy | 390 | 324 | 318 | Unavailable |
| CompBio | Open-ended code | 382 | 303 | 296 | Unavailable |

All benchmark-specific paired configurations; three observed nonempty fingerprints are required. Answer identity uses exact archived submitted text after outer whitespace removal; it does not merge numerically close strings. Path variation means tool-ID/command-token sets differ, not independently adjudicated biological algorithms. BixBench can confirm acceptance; CompBio cannot confirm validity. The counts support multiple observed execution routes to the same answer, with these measurement limits.

### Table X17. Testing the five motivating observations

| Proposed observation | Evidence-based verdict | Supporting tables / unresolved experiment |
| --- | --- | --- |
| Agents can operate core Galaxy features | Supported for recorded discovery, inspection and submission requests; successful jobs separately observed | X14; B4/C3. Universal history creation and Galaxy-only execution still require event attribution |
| Different approaches produce the same valid result | Supported for different recorded paths and identical accepted BixBench answers; biological method equivalence unadjudicated | X16; B6. CompBio item-level validity remains unavailable |
| Custom tools fill missing Galaxy capabilities in 30-40% of tasks | Not supported as a task-rate or necessity claim; request/task/execution denominators differ | X12-X15. Native capability, parameter binding and workflow composition are distinct explanations |
| Wrong outlier answers reflect missing knowledge and technical mistakes | Cannot quantify from this archive; item-level correctness and independent error adjudication are absent | C10. Observed diagnostic choices contradict a blanket claim that agents found no useful analysis |
| Galaxy makes human validation easier | Plausible interface benefit; not measured in these benchmark records | X7. Randomized blinded reconstruction-time, error and agreement study required |

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

Counts are deduplicated creating jobs; tool versions are pooled within the named family. The denominator contains every error job for that family, including missing/truncated diagnostics. Exact regex rules and matching job/source-event IDs are retained in the analysis JSON. These messages support input, datatype, identifier and design-validation hypotheses; they do not alone assign blame to the model, wrapper or platform. Multiple signatures may overlap. No claim is made that a tool always fails: the diagnostic probe with 57/57 error states in X6 is not a biomedical-analysis success endpoint.
