# RESULTS

We retrospectively examined 2,500 workbook-linked CompBioBench run records for 100 tasks. The paired descriptive population comprises four configurations (GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro 0813 through Codex), two environments and three replicate labels: 2,400 records, 1,200 per environment and 800 triplicate cells. The remaining 100 GPT-6 Astra records comprise one open-ended-code run per task and are reported separately. All workbook rows match the retained task, model label, environment, replicate and trace URL. An independent selection and stopping protocol was unavailable. Replicate labels do not establish independent executions or matched seeds: the supplied campaign metadata assembles final vectors from initial, continuation and recovery campaigns. These are final archived selections, not measured first-attempt success rates. Runtime metadata, prompt hashes and source roots are retained per run. Submitted answers, original evaluator outcomes, operational states and auditor interpretations remain distinct.

## Accuracy and output agreement by execution condition

Per-task original evaluator scores are unavailable for all 2,500 records. The archived `evaluation.stdout.txt` files report submission-format validation, not scientific correctness. Additional source retrieval recovered 25 aggregate score labels: 15 official-labelled and 10 predicted (Table 1). Of the advertised vector hashes, 13 match retained bytes, 9 do not, and 3 have no corresponding downloaded vector. For every available vector, all parsed answers match the per-run submitted answers. This establishes content agreement with those files, but does not resolve disagreement with the advertised submission hash. Two Sol Galaxy entries change from predictions in `replicates.tsv` to official-labelled scores in the dated `paper_site_runs.json`, with numerical revisions from 92 to 93/100 for r1 and from 92 to 91/100 for r3; both versions are retained in the conflict ledger and shown in Table 1. The dated site metadata is displayed with explicit attribution, not treated as an independently verified leaderboard receipt. GPT-6 Astra has an archive-labelled 93/100 score for its single open-ended vector and no Galaxy counterpart. Task-level accuracy differences, all/some/none accepted counts, accuracy bootstrap intervals, outcome-versus-route associations and accepted results per token cannot be recovered from aggregate totals. No missing score is treated as failure, no predicted score substitutes for an official result, and no equivalence, non-inferiority or superiority claim follows from these records.

**Table 1. Source-reported answer-vector scores**

| Configuration | Galaxy | Open-ended code |
| --- | --- | --- |
| GPT-5.5 (Codex) | r1: 84/100 (O); r2: 89/100 (O; hash mismatch); r3: 87/100 (P; hash mismatch) | r1: 87/100 (O); r2: 88/100 (O; hash mismatch); r3: 84/100 (O; hash mismatch) |
| GPT-5.6 Sol (Codex) | r1: 93/100 (O; previously 92/100 P); r2: 91/100 (P; hash mismatch); r3: 91/100 (O; hash mismatch; previously 92/100 P) | r1: 88/100 (O); r2: 90/100 (O); r3: 95/100 (O) |
| GPT-5.6 Luna (Codex) | r1: 86/100 (P; vector unavailable); r2: 84/100 (P; vector unavailable); r3: 85/100 (P; vector unavailable) | r1: 84/100 (O); r2: 86/100 (O); r3: 85/100 (P) |
| DeepSeek V4 Pro 0813 (Codex) | r1: 83/100 (P; hash mismatch); r2: 87/100 (P); r3: 83/100 (P) | r1: 80/100 (P); r2: 87/100 (O; hash mismatch); r3: 86/100 (O; hash mismatch) |
| GPT-6 Astra (Codex; unpaired) | Not represented | r1: 93/100 (O) |

O = archive-labelled official leaderboard score; P = prediction. Labels are preserved, not independently regraded or promoted to item-level official outcomes. Scores refer to 100-answer vectors. Hash mismatch means retained vector bytes disagree with the advertised SHA-256 (9 entries); vector unavailable means no vector bytes were retrieved and zero answers were compared (3 Luna Galaxy entries). The other 13 hashes match. Parsed answers agree for all 22 available vectors. Previous Sol scores are from `replicates.tsv`; displayed scores are from the dated `paper_site_runs.json`. No pooled official comparison is calculated from this mixture.

**Table 2. Task coverage and submitted-answer convergence**

| Environment | Tasks | Runs | Median distinct answers/task | Tasks with one answer | Tasks with accepted answers |
| --- | --- | --- | --- | --- | --- |
| Galaxy | 100 | 1200 | 1.0 | 62 | Unavailable |
| Open-ended code | 100 | 1200 | 1.0 | 58 | Unavailable |

Four paired configurations only: 12 answers per task and environment. Answer identity uses archived text with outer whitespace stripped, without numeric rounding. `run_summaries.answer_sha256` hashes raw answer-file bytes, whereas Tables 2-3 compare `outcome.submitted_answer`, already stripped during evidence construction; grouping by those hashes can therefore give different counts. It is not correctness or semantic agreement; BixBench six-significant-figure normalization is inappropriate for heterogeneous CompBio lists, identifiers and coordinates.

**Table 3. Triplicate answer consistency, distinct from acceptance**

| Environment | Configuration | One distinct answer | Two | Three | Scored triplicate cells |
| --- | --- | --- | --- | --- | --- |
| Galaxy | GPT-5.5 (Codex) | 84 | 11 | 5 | 0 |
| Galaxy | GPT-5.6 Sol (Codex) | 87 | 11 | 2 | 0 |
| Galaxy | GPT-5.6 Luna (Codex) | 85 | 9 | 6 | 0 |
| Galaxy | DeepSeek V4 Pro 0813 (Codex) | 77 | 15 | 8 | 0 |
| Open-ended code | GPT-5.5 (Codex) | 82 | 15 | 3 | 0 |
| Open-ended code | GPT-5.6 Sol (Codex) | 89 | 10 | 1 | 0 |
| Open-ended code | GPT-5.6 Luna (Codex) | 78 | 19 | 3 | 0 |
| Open-ended code | DeepSeek V4 Pro 0813 (Codex) | 72 | 24 | 4 | 0 |

Each row contains 100 task cells. The BixBench all/some/none accepted analysis remains unavailable; these counts describe answer text only.

## Analysis execution, failures and recovery

Detailed Galaxy contents were retained for 1198/1,200 runs; 2 histories have metadata only. Across the snapshots, 22,067 distinct creating jobs include 5,381 data-fetch jobs and 16,686 non-fetch jobs. The latter include 3,097 failed/error jobs (18.6%; Table 6). At least one failed non-fetch job appears in 702/1198 evaluable Galaxy runs. At least one nonzero shell exit appears in 676/1188 available Galaxy-condition transcripts and 882/1200 open-ended-code transcripts. These are counts of runs with a recorded shell exit, not counts of failed Galaxy jobs; a shell exit may represent a probe or search rather than a failed analysis. The retained records flag 213 candidate same-tool/input failure-to-success sequences across 107 Galaxy runs. They support investigation of recovery, not a comparative recovery benefit. The tool inventory combines installed tools with task-specific identifiers; custom identifiers alone cannot distinguish a standard domain tool from a user-defined wrapper. No run is certified Galaxy-only without an adjudicated event-level computation-location audit. Inherited input preparation, calls to external services, and local orchestration must be distinguished from substantive analysis. The full error/parameter records and candidate event IDs remain available in the numerical audit and task ledgers.

A concrete parameter correction is visible in `bedtools-chromhmm-q1`, DeepSeek Galaxy replicate 2. The column-making expression `round(c1/c5*100)` failed because both columns were strings. A later job on the same input used `round(float(c1)/float(c5)*100)`, reached `ok`, and reported that it computed the new column for all input lines. This supports an operational correction, without establishing correctness of the chosen biological denominator. A contradictory example shows why automated recovery counts need review: in `perturb-seq-align-q1`, DeepSeek Galaxy replicate 3, AnnData `chunk_X` failed with a sparse-matrix attribute error, while the later successful job requested `var` metadata. It used the same tool and input but performed a different operation, so success did not demonstrate recovery of the original objective. Both failed/later event pairs, exact parameters, timestamps and output excerpts are retained in `case_reviews` in the numerical audit.

**Table 4. Most frequent retained Galaxy creating-job tool IDs**

| Tool ID (recorded version) | Distinct jobs |
| --- | --- |
| toolshed.g2.bx.psu.edu/repos/iuc/filter_tabular/filter_tabular/3.3.1 | 627 |
| toolshed.g2.bx.psu.edu/repos/iuc/anndata_inspect/anndata_inspect/0.11.4+galaxy3 | 413 |
| Cut1 | 378 |
| upload1 | 372 |
| toolshed.g2.bx.psu.edu/repos/iuc/datamash_ops/datamash_ops/1.9+galaxy0 | 372 |
| toolshed.g2.bx.psu.edu/repos/iuc/bedtools/bedtools_intersectbed/2.31.1+galaxy0 | 346 |
| toolshed.g2.bx.psu.edu/repos/devteam/column_maker/Add_a_column1/2.1+galaxy0 | 290 |
| toolshed.g2.bx.psu.edu/repos/iuc/scanpy_inspect/scanpy_inspect/1.10.2+galaxy3 | 279 |
| wc_gnu | 248 |
| Grouping1 | 206 |
| toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_grep_tool/9.5+galaxy3 | 198 |
| toolshed.g2.bx.psu.edu/repos/goeckslab/gseapy_enrichr/gseapy_enrichr/0.1.0+galaxy2 | 192 |

Deduplicated by Galaxy server and native job ID across all histories. Excludes `__DATA_FETCH__`; includes 372 legacy `upload1` jobs as a table row. Preparation jobs are included, so these are not counts of independent scientific analyses.

**Table 5. Task-specific execution examples**

| Task | Domain | Distinct answers G / code | Recorded Galaxy operations (top 3, including ties; counts) | Official item outcomes |
| --- | --- | --- | --- | --- |
| [1000G-retrieve-genotype-q1](analysis/1000G-retrieve-genotype-q1/history_analysis.md) | Population Genetics | 3 / 2 | toolshed.g2.bx.psu.edu/repos/iuc/bcftools_query/bcftools_query/1.24+galaxy0 (7); toolshed.g2.bx.psu.edu/repos/iuc/bcftools_view/bcftools_view/1.24+galaxy0 (4); upload1 (4) | Unavailable |
| [annotate-variant-regulatory-overlap-q1](analysis/annotate-variant-regulatory-overlap-q1/history_analysis.md) | Epigenomics | 2 / 2 | toolshed.g2.bx.psu.edu/repos/iuc/bedtools/bedtools_intersectbed/2.31.1+galaxy0 (13); ucsc_bigbedtobed (5); upload1 (2) | Unavailable |
| [perturb-seq-align-q1](analysis/perturb-seq-align-q1/history_analysis.md) | Single-cell | 1 / 1 | toolshed.g2.bx.psu.edu/repos/iuc/anndata_inspect/anndata_inspect/0.11.4+galaxy3 (76); Grep1 (12); toolshed.g2.bx.psu.edu/repos/ebi-gxa/scanpy_find_markers/scanpy_find_markers/1.9.3+galaxy0 (11) | Unavailable |
| [deg-simple-q1](analysis/deg-simple-q1/history_analysis.md) | Transcriptomics | 1 / 1 | sort1 (21); toolshed.g2.bx.psu.edu/repos/iuc/featurecounts/featurecounts/2.1.1+galaxy1 (20); toolshed.g2.bx.psu.edu/repos/iuc/hisat2/hisat2/2.2.3+galaxy0 (19) | Unavailable |
| [reverse-search-gwas-q1](analysis/reverse-search-gwas-q1/history_analysis.md) | Population Genetics | 10 / 7 | toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_grep_tool/9.5+galaxy3 (34); toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_grep_tool/9.11+galaxy0 (30); toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_head_tool/9.5+galaxy3 (20); toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_sort_header_tool/9.5+galaxy3 (20) | Unavailable |
| [sample-swap-atac-q1](analysis/sample-swap-atac-q1/history_analysis.md) | Single-cell | 2 / 1 | Summary_Statistics1 (19); Cut1 (4); axolotl-atac-swap-diagnostic-v1 (4); toolshed.g2.bx.psu.edu/repos/iuc/filter_tabular/filter_tabular/3.3.1 (4) | Unavailable |

Illustrative tasks selected by domain and evidence availability, not by inferred success. Counts are recorded analysis-type Galaxy job events across the 12 paired-configuration runs for each task. All tools tied at the third-entry count are included, ordered alphabetically within ties. Tool presence and completed jobs do not demonstrate an accepted final answer. Complete tool IDs, parameters, failures and submitted answers are linked in each task package.

**Table 6. Execution availability, states and operational recovery candidates**

| Measure | Count |
| --- | --- |
| Unique linked Galaxy histories | 1200 |
| Galaxy runs with detailed contents | 1198 |
| Metadata-only histories | 2 |
| All distinct creating jobs | 22067 |
| Data-fetch jobs | 5381 |
| Legacy upload1 jobs within non-fetch category | 372 |
| Non-fetch creating jobs | 16686 |
| Non-fetch job state: deleted | 58 |
| Non-fetch job state: error | 3097 |
| Non-fetch job state: ok | 13517 |
| Non-fetch job state: paused | 14 |
| Recovery candidates | 213 |
| Runs containing a recovery candidate | 107 |

Current snapshots can include inherited or later state. Failed jobs are not failures before a correct answer; that endpoint is unobserved. Same-tool, same-input later success identifies a candidate operational recovery, not an adjudicated scientific correction.

**Table 7. Environment comparisons and unavailable accuracy endpoints**

| Measure | Result |
| --- | --- |
| Task-level answer sets differ between environments | 43/100 |
| Task-level answer sets identical | 57/100 |
| Tasks with Galaxy-only accepted answers | Not assessable |
| Strict discordance (3 accepted versus 0) | Not assessable |
| Cross-configuration consistency of accuracy advantage | Not assessable |
| Verifier-mode effects | Not assessable |

Different submitted answers need not differ scientifically or in evaluation. Aggregate vector scores cannot locate discordant tasks.

## Solution-path variability across tasks and configurations

Among 390 evaluable Galaxy triplicate cells, 6 had identical recorded toolsets (1.5%); mean pairwise Jaccard agreement was 0.151. The corresponding open-ended-code counts were 7/382 (1.8%) and 0.583 (Table 9). Galaxy fingerprints come from structured version-stripped tool identifiers, while code fingerprints come from vocabulary matches in commands. These instruments differ in resolution and visibility, precluding a direct ranking of scientific solution consistency between environments. The closed vocabulary is intentionally unchanged from BixBench for side-by-side evaluation, but can omit CompBio-specific software. Tables 8-10 therefore describe observed indicators and configuration differences within an environment, not adjudicated biological methods. Task mean agreement was weakly correlated across environments (Spearman rho = -0.105, n = 97 tasks; Table 10). These indicators show little cross-environment correspondence in task rankings; they do not establish that task identity has no effect on path variability. Submitted-answer consistency is reported independently in Tables 2-3. Without item-level scores, convergent answers cannot be called correct, and divergent paths cannot be counted as valid alternative solutions. No independent difficulty strata or controlled prompt-version comparison were available.

**Table 8. Selected CompBio tool and library indicators**

| Environment | Configuration | bedtools | samtools | bcftools | anndata | scanpy | numpy | pandas | scipy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Galaxy | GPT-5.5 (Codex) | 25 | 24 | 7 | 19 | 13 | 0 | 0 | 1 |
| Galaxy | GPT-5.6 Sol (Codex) | 24 | 31 | 10 | 22 | 9 | 1 | 0 | 0 |
| Galaxy | GPT-5.6 Luna (Codex) | 52 | 37 | 24 | 24 | 15 | 0 | 0 | 1 |
| Galaxy | DeepSeek V4 Pro 0813 (Codex) | 66 | 43 | 20 | 37 | 28 | 1 | 1 | 1 |
| Open-ended code | GPT-5.5 (Codex) | 36 | 65 | 33 | 28 | 26 | 113 | 76 | 59 |
| Open-ended code | GPT-5.6 Sol (Codex) | 28 | 79 | 30 | 27 | 22 | 113 | 75 | 62 |
| Open-ended code | GPT-5.6 Luna (Codex) | 65 | 108 | 42 | 34 | 31 | 141 | 101 | 87 |
| Open-ended code | DeepSeek V4 Pro 0813 (Codex) | 56 | 104 | 38 | 41 | 44 | 153 | 129 | 105 |

Non-exclusive numbers of runs out of 300 per row. Galaxy indicators are substring matches on structured job tool IDs; open-ended-code indicators use the unchanged BixBench closed command vocabulary. Absence of an indicator is not absence of the scientific method. Custom wrappers may conceal library use, and missing/empty fingerprints are excluded from primary agreement estimates.

**Table 9. Triplicate solution-path agreement**

| Environment | Configuration | Identical | Two identical | All distinct | Not evaluable | Identical % | Mean Jaccard |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Galaxy | GPT-5.5 (Codex) | 2 | 3 | 94 | 1 | 2.0 | 0.089 |
| Galaxy | GPT-5.6 Sol (Codex) | 1 | 4 | 95 | 0 | 1.0 | 0.125 |
| Galaxy | GPT-5.6 Luna (Codex) | 1 | 5 | 91 | 3 | 1.0 | 0.190 |
| Galaxy | DeepSeek V4 Pro 0813 (Codex) | 2 | 5 | 87 | 6 | 2.1 | 0.203 |
| Galaxy | All configurations | 6 | 17 | 367 | 10 | 1.5 | 0.151 |
| Open-ended code | GPT-5.5 (Codex) | 3 | 16 | 77 | 4 | 3.1 | 0.562 |
| Open-ended code | GPT-5.6 Sol (Codex) | 1 | 16 | 78 | 5 | 1.1 | 0.597 |
| Open-ended code | GPT-5.6 Luna (Codex) | 1 | 10 | 83 | 6 | 1.1 | 0.583 |
| Open-ended code | DeepSeek V4 Pro 0813 (Codex) | 2 | 7 | 88 | 3 | 2.1 | 0.587 |
| Open-ended code | All configurations | 7 | 49 | 326 | 18 | 1.8 | 0.583 |

Same fingerprint vocabulary and normalization as BixBench. Jaccard is the number of shared fingerprint elements divided by the number in their union; Mean Jaccard averages the three replicate-pair similarities per cell, then averages across eligible cells. Primary estimates require three observable nonempty fingerprints. Empty or missing records are not agreement. The numerical output also records the legacy BixBench inclusion-rule sensitivity. Astra has only one replicate and its 100 cells are explicitly excluded. Fingerprints ignore order and most parameters, so agreement is not workflow equivalence; magnitudes across environments use different instruments.

**Table 10. Descriptive associations with path variability**

| Measure | Galaxy | Open-ended code |
| --- | --- | --- |
| Task mean Jaccard standard deviation | 0.152 | 0.117 |
| Configuration mean Jaccard standard deviation | 0.047 | 0.013 |
| Spearman correlation: median_events | 0.155 (n=390) | 0.120 (n=382) |
| Spearman correlation: median_jobs | 0.214 (n=390) | Unavailable (n=0) |
| Spearman correlation: mean_fingerprint_size | 0.040 (n=390) | 0.261 (n=382) |
| Cells with a recorded failed Galaxy job | 0.114 (n=337) | Not applicable |
| Cells without a recorded failed Galaxy job | 0.383 (n=53) | Not applicable |
| Association with answer acceptance | Not assessable | Not assessable |

Across the 97 tasks with an evaluable task mean in both environments, Spearman rho between task mean Jaccard values was -0.105. Task means average eligible configuration cells; the contributing configurations can differ between environments. The two failure-group rows report mean Jaccard, not correlations. Cells share tasks and are not independent observations. Task difficulty is not inferred from failures or token use. Fingerprint-size-stratified failure associations are retained in the JSON; none establishes causality.

## Token cost, provenance and human readability

Provider-reported primary-turn usage was recovered for 2486/2,500 runs. Complete usage in both environments permitted 386/400 task-by-configuration comparisons. Their median Galaxy/open-ended-code input-token ratio was 4.42 (IQR 1.91-10.66; range 0.11-115.66; Table 11). An exploratory task-block bootstrap gave a 95% percentile interval of 3.53-5.39 (10,000 resamples, seed 20260921). This interval treats task bundles as independent; shared inputs and campaign selection may violate that assumption. Complete-case selection can also omit costly interrupted runs. The totals cover the archived primary turn, not all earlier campaigns or separately logged subagents, and thus do not measure the full cost of obtaining the final vectors. Missing or ambiguous terminal records remain null. Runtime-verified and runtime-plus-reasoning-verified subsets are retained as sensitivity summaries. Execution failures and token distributions are retained for all observable runs, but correct-only summaries cannot be computed without item scores. No per-call accounting permits attribution to retries, discovery, analysis or orchestration: 100% of these totals remains stage-unattributed. Dollar costs, review time, reconstruction errors and reviewer agreement were not measured. Structured histories and command traces support inspection; they do not demonstrate faster review or that provenance benefits outweigh token cost.

**Table 11. Galaxy/open-ended-code input-token ratios**

| Configuration | Eligible task comparisons | Median ratio | IQR |
| --- | --- | --- | --- |
| GPT-5.5 (Codex) | 97 | 3.14 | 1.68-5.81 |
| GPT-5.6 Sol (Codex) | 100 | 6.63 | 3.13-12.05 |
| GPT-5.6 Luna (Codex) | 90 | 5.73 | 2.09-16.09 |
| DeepSeek V4 Pro 0813 (Codex) | 99 | 3.53 | 1.58-8.36 |
| All paired configurations | 386 | 4.42 | 1.91-10.66 |

Each ratio divides the median of three Galaxy input totals by the median of three open-ended-code totals for the same task and supplied configuration. IQR columns report the first and third quartiles (Q1-Q3), rather than their difference. All six totals must be available; excluded pairs are listed in the audit. This is a median of task/configuration ratios, not a ratio of pooled totals or matched-seed runs. Cached input is already included and is not added again; output and reasoning fields remain separate.

**Supplementary Table S1. Absolute provider-token distributions**

| Configuration | Environment | Usage coverage | Median input | Input IQR | Median output |
| --- | --- | --- | --- | --- | --- |
| GPT-5.5 (Codex) | Galaxy | 297/300 | 1734835.0 | 629722.00-3895084.00 | 14727.0 |
| GPT-5.5 (Codex) | Open-ended code | 300/300 | 491109.0 | 152662.25-1487255.25 | 8538.0 |
| GPT-5.6 Sol (Codex) | Galaxy | 300/300 | 3748257.5 | 1438300.00-10355795.75 | 13832.5 |
| GPT-5.6 Sol (Codex) | Open-ended code | 300/300 | 530535.0 | 174902.75-1844343.25 | 6066.5 |
| GPT-5.6 Luna (Codex) | Galaxy | 290/300 | 10238154.5 | 3805712.50-20045945.50 | 36414.5 |
| GPT-5.6 Luna (Codex) | Open-ended code | 300/300 | 1448621.0 | 294212.75-6572374.75 | 15140.0 |
| DeepSeek V4 Pro 0813 (Codex) | Galaxy | 300/300 | 8478973.0 | 3579614.75-20014536.75 | 41476.5 |
| DeepSeek V4 Pro 0813 (Codex) | Open-ended code | 299/300 | 2407919.0 | 515198.50-8254517.00 | 24543.0 |
| GPT-6 Astra (Codex; unpaired) | Open-ended code | 100/100 | 314244.5 | 100895.00-691405.00 | 2788.0 |

All observable final selected runs, including those with operational errors. Medians retain one decimal place and linearly interpolated quartiles retain two, preserving fractional summary values from integer token counts. Input IQR reports Q1-Q3. Missing usage is excluded explicitly, never zero. The unpaired Astra population is separate. Correct-only and full multi-campaign costs are unavailable.

## Methods, provenance and limitations

The workbook defines the observed inventory, not an independent expected-run protocol. Matching uses task and supplied configuration; condition-specific prompt additions, runtime reasoning settings and campaign roots remain visible confounders. No individual replicate is paired by seed. Counts use all listed runs unless an explicit complete-case criterion is stated. Jobs are deduplicated by server/native job ID; data-fetch jobs are separate. Inputs are not assumed independent merely because they have distinct uploads or histories. Run-level input manifests and dataset IDs support inspection, but complete input-version equivalence and ownership within the original run time window have not been established. No recovered agent code was executed, no hidden reference was opened, no new benchmark was run, and no submitted answer was regraded.

Prior task reports and evidence are retained exactly under `analysis/<task>/versions/pre_compbio_synthesis/`. The existing schema and full source hash/reference checks validate the updated packages. The aggregate JSON references all 100 evidence hashes, included run IDs, finding IDs, source files and software hashes. Initial trace/history collection did not verify TLS certificates; the supplemental metadata fetch verified the certificate chain and hostname with strict CA-extension checking disabled for the host proxy. Neither byte hashes nor successful schema validation resolve score-source disagreements.

For `reverse-search-gwas-q1`, the [424-element snapshot](analysis/reverse-search-gwas-q1/source_snapshots/galaxy/bbd44e69cb8906b5201e75f3364aad9c/history.json) lists 394 `ok` and 21 `error` elements in `state_ids`, leaving 9 elements unaccounted for by those state-ID lists. For `reverse-search-gwas-q1`, the [799-element snapshot](analysis/reverse-search-gwas-q1/source_snapshots/galaxy/bbd44e69cb8906b5a8a6f27aa8b4f67a/history.json) lists 616 `ok` and 175 `error` elements in `state_ids`, leaving 8 elements unaccounted for by those state-ID lists. Together these metadata-only histories record 196 error-state elements and 17 elements without a listed state ID. The snapshots' `state_details` fields report 0 errors in total, contradicting their `state_ids`; both representations and their discrepancy are retained in the audit. These are dataset-state observations, not deduplicated creating-job counts or answer outcomes, and are not added to Table 6 job totals. Detailed contents remain excluded under the collection limit. Capping does not establish experiment failure, but it does not erase the recorded error states.

Exact per-task official evaluator outputs, versioned scoring definitions and submission receipts matching advertised vector hashes are needed for BixBench-equivalent accuracy, reliability and outcome-versus-route tables. Missing primary traces/usage, independent campaign-selection records, and event-level location/recovery adjudication are needed to quantify complete computational cost and exclusively Galaxy-derived solutions. A blinded review study is required for readability claims. These missing results are explicitly unavailable rather than replaced by plausible answers.

**Claim-to-evidence map**

| Finding ID | Supported claim | Evidence |
| --- | --- | --- |
| compbio_inventory | 100 tasks; 2,500 supplied rows; 2,400 paired records | compBio_overview_audit.json: inventory, task_manifest |
| compbio_accuracy | Aggregate score claims retained; no item-level accuracy | score_vectors, score_conflicts; downloaded metadata manifests |
| compbio_execution | Observed deduplicated job states and recovery candidates | execution.job_refs; each task finding_execution |
| compbio_variability | Instrument-specific fingerprint agreement | solution_path_consistency_results.json: cells and drivers |
| compbio_cost | Complete-case ratios of primary-turn provider input totals | token_pairs, token_excluded, tokens; run_summaries.usage source lines |

Every task evidence path and SHA-256 is enumerated in task_manifest. Run IDs are scoped by task; job references include server. Aggregate calculations never place multiple tasks into a singular task evidence record.

## Abstract-ready paragraph

We audited 2,500 CompBioBench records spanning 100 tasks, including 2,400 records across four paired model configurations and 100 unpaired GPT-6 Astra records. The archive supplied no item-level evaluator scores; 15 aggregate scores were labelled official and 10 predicted. Galaxy snapshots exposed 16,686 distinct non-fetch creating jobs, including 3,097 failures. Input-token totals were recovered for 2486 records; the median Galaxy/open-ended-code ratio was 4.42 across 386 complete task-by-configuration comparisons. These retrospectively selected records support execution and provenance comparisons, while missing item outcomes and incomplete campaign accounting limit accuracy, recovery and total-cost conclusions.

Reproduce with `python3 scripts/audit_compbio_overview.py --validate` from the repository root. [Numerical audit](compBio_overview_audit.json), [path analysis](solution_path_consistency_analysis.py), [path results](solution_path_consistency_results.json), [source recovery](compBio_recovery_summary.md), [source manifest](source_snapshots/aggregate_metadata/manifest.json), and [task packages](analysis/) retain the evidence.
