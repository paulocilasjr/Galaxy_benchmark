# RESULTS

We examined 1,500 archived run records for 50 BixBench questions drawn from 33 source capsules. Each question had three replicate-labelled runs for each of five model-harness configurations in two conditions: Galaxy-API with skills and open-ended code with skills. All 1,500 rows in the supplied link workbook were matched to the corresponding task, configuration, condition, replicate and archived trace URL. The analysis combined original evaluator and token-usage records, available Galaxy job snapshots, and a metadata-only assessment of histories whose detailed contents exceeded the collection limit. We distinguish three outcomes throughout: acceptance of the submitted answer, operational states of jobs or datasets, and the availability of provenance. These outcomes measure different aspects of performance. The results concern BixBench-50; they do not provide performance estimates for GalaxyBench or BioAgent.

## Agents achieve high answer acceptance when operating through Galaxy

The original evaluator accepted 639 of 750 Galaxy-condition answers (85.2%) and 615 of 750 open-code answers (82.0%), a difference of 3.2 percentage points. Galaxy had higher acceptance on 14 questions, open code on 10, and the conditions were tied on 26. Across the 250 question-by-configuration comparisons, the corresponding counts were 33, 19 and 198. These values describe the original binary `accuracy.score`, rather than an independent assessment of the scientific validity of every analysis. Five Galaxy runs and one open-code run had an original evaluator reason of `missing_answer`, accompanied by blank answer text and no answer path in the original result records. Their original zero scores were retained in the denominators; these cases were not missing scores imputed as failures.

**Table 1. Answer acceptance by model-harness configuration.** Each condition contains 150 runs per configuration: 50 questions with three replicate labels. Differences are calculated from unrounded proportions. The configurations include the same DeepSeek model family accessed through two harnesses.

| Configuration | Galaxy accepted / total (%) | Open code accepted / total (%) | Difference (percentage points) |
|---|---:|---:|---:|
| GPT-5.5 via Codex | 134/150 (89.3) | 131/150 (87.3) | +2.0 |
| GPT-5.6 Sol via Codex | 133/150 (88.7) | 130/150 (86.7) | +2.0 |
| GPT-5.6 Luna via Codex | 129/150 (86.0) | 129/150 (86.0) | 0.0 |
| DeepSeek V4 Pro via Codex | 123/150 (82.0) | 121/150 (80.7) | +1.3 |
| DeepSeek V4 Pro via Claude Code, superseded | 120/150 (80.0) | 104/150 (69.3) | +10.7 |

The superseded DeepSeek/Claude Code configuration accounted for 16 of the 24 additional accepted Galaxy answers. Excluding this configuration in a descriptive sensitivity analysis reduced the difference to 1.3 percentage points: 519/600 (86.5%) for Galaxy and 511/600 (85.2%) for open code. A post hoc source-capsule bootstrap gave an exploratory 95% interval of -1.4 to +7.9 percentage points for the full pooled difference (100,000 resamples of 33 capsules, retaining all questions and runs within each sampled capsule and preserving question weighting). This interval assumes independence between capsules and may not capture dependence from shared biological inputs.

Thus, high answer acceptance was achievable through the Galaxy condition, but the comparison does not establish superiority, equivalence or non-inferiority. The observed inventory lacked an independent protocol specifying selection, seeds and stopping rules; replicate labels do not establish matched random seeds. Condition-specific instructions and tools, differences between harnesses, and container revisions within GPT-5.5 also limit attribution to Galaxy alone. The execution evidence below identifies available computational routes that accompanied this performance, rather than experimentally isolating why agents performed well.

## Galaxy supports diverse analytical operations with inspectable execution records

At least one Galaxy run yielded an accepted answer for 47 of 50 questions, and all 15 Galaxy runs were accepted for 25 questions. Open code yielded at least one accepted answer for 48 questions and acceptance in all 15 runs for 25 questions. These are coverage measures across configurations and replicates, not single-run success probabilities. Questions accepted in every Galaxy run included treeness comparisons (`bix-11-q1`), filtered variant counts (`bix-17-q2`), colony circularity summaries (`bix-18-q1`), differential-expression counts (`bix-49-q4`) and logistic-regression AIC (`bix-51-q2`). No Galaxy answer was accepted for `bix-45-q1`, `bix-53-q2` or `bix-61-q5`; the latter two also had no accepted open-code answers.

The retained job records show how the workbench was used across these domains. Frequent operations included spreadsheet-to-tabular conversion (644 jobs for the recorded xlsx2tsv version), column selection (557 Cut1 jobs), filtering (397 Filter1 jobs), KEGG over-representation analysis (269 jobs for the recorded kegg_ora version), and phylogenetic metrics (202 jobs for the recorded phykit_metrics version). Other records contained DESeq2, enrichment, correlation and regression tools. Colony-summary histories contained grouping and Datamash operations, while the genome-coverage question `bix-61-q2` had BWA-MEM and samtools depth records. These counts identify observed creating jobs, including preparation steps, rather than the number of independent analyses or accepted answers. They document a workbench combining data manipulation with specialist computation; they do not establish that tool availability caused the observed accuracy.

Dataset-bearing snapshots represented 711 distinct public histories linked to 714 Galaxy run records. A further 32 run records had history metadata but no detailed contents because their histories exceeded the collector's 300-item limit; four histories were unavailable. The additional metadata assessment retained this limit and recovered summary counts without downloading detailed contents or outputs. Across the 32 capped histories, metadata reported 41,304 elements. The state summaries accounted for 40,933 elements, leaving 371 outside the reported state totals (Table 2). Thirty-one of these 32 run records had accepted answers, demonstrating that the collection limit itself was not evidence of analytical failure.

**Table 2. Element states in the 32 collection-limited histories.** Values are from archived history metadata. The `ok` state indicates an operational dataset state, not scientific correctness. Elements outside the state summary remain unclassified; they are not assigned to either success or failure.

| Metadata measure | Elements |
|---|---:|
| Total history elements | 41,304 |
| `ok` | 40,722 |
| `new` | 202 |
| `failed_metadata` | 9 |
| `error` | 0 |
| Not accounted for by state summaries | 371 |

All 202 `new` states occurred in the capped DeepSeek/Codex replicate 1 for `bix-12-q6`, whose answer was accepted. All nine `failed_metadata` states occurred in DeepSeek/Codex replicate 2 for `bix-31-q2`, whose answer was not accepted. These co-occurrences do not establish whether those objects contributed to the submitted answer. In particular, the absence of `error` states in these metadata summaries does not establish the absence of failed jobs. Dataset counts cannot be added to job counts or interpreted as independent attempts.

Separately, the previously retrieved detailed snapshots contained 5,042 distinct creating jobs after deduplication by server and native job identifier: 4,454 were `ok`, 552 were `error` (10.9%), 25 were `deleted` and 11 were `paused`. The source audits' analytical category excludes `__DATA_FETCH__` but includes conversion, preprocessing and 102 legacy `upload1` jobs. The totals have incomplete coverage and may include inherited or later history state; they are not a complete count of jobs newly executed during the benchmark runs. Tool identifiers, parameters, dataset associations and recorded errors nevertheless provide concrete evidence that can be inspected after execution.

The audits flagged 93 candidate failure-to-success sequences across 49 Galaxy run records, defined by a later successful job with the same tool and input dataset identifiers. These sequences make corrective actions available for investigation, but were not independently adjudicated as scientific recoveries. They therefore do not establish that Galaxy improves recovery rates or parameter selection relative to open code. Moreover, the original evaluator marked `fresh_galaxy_history_recorded` false for all 750 Galaxy runs despite the available history evidence. Until this discrepancy and the location of substantive computations are reconciled, a verified count of tasks completed exclusively through Galaxy cannot be assigned. The demonstrated benefit is inspectable execution provenance accompanying diverse analytical operations, rather than certified end-to-end compliance or independently reproduced results.

## Recorded solution routes include installed and custom tools, with configuration-dependent usage

The original route classification identified different tool-use patterns across configurations (Table 3). PhyKIT appeared in 116 Galaxy and 100 open-code run labels; Datamash and Summary Statistics appeared in 55 and 17 Galaxy labels, respectively. Open-code labels also included Newick or branch parsing in 80 runs, IQ-TREE report parsing in 15 and Biopython in three. These are non-exclusive tool or command indicators. They do not establish that distinct wrappers represent different scientific methods, or that similar labels identify equivalent parameterizations.

**Table 3. Selected indicators from the original route classification.** Each column counts runs containing the specified label among 150 runs per condition and configuration. These counts retain the original classification and are not expanded using the selectively recovered requests from capped histories.

| Configuration | Galaxy: PhyKIT | Galaxy: Datamash | Galaxy: Summary Statistics | Open code: PhyKIT | Open code: Newick/branch parsing |
|---|---:|---:|---:|---:|---:|
| GPT-5.5 via Codex | 23 | 3 | 1 | 16 | 13 |
| GPT-5.6 Sol via Codex | 25 | 8 | 4 | 20 | 23 |
| GPT-5.6 Luna via Codex | 20 | 22 | 4 | 18 | 18 |
| DeepSeek V4 Pro via Codex | 25 | 14 | 7 | 30 | 13 |
| DeepSeek V4 Pro via Claude Code, superseded | 23 | 8 | 1 | 16 | 13 |

The metadata recovery exposed a limitation of those labels. Although detailed job snapshots were unavailable for the 32 capped histories, already-retained traces identified structured tool-execution requests in 30 of the corresponding runs. Requests included archive extraction, collection filtering and aggregation, PhyKIT alignment and tree wrappers, Datamash and nonparametric rank tests. Seventeen of the 32 runs contained requests for custom Galaxy tools, including tools for treeness and parsimony-site calculations. For example, the capped Luna replicate for `bix-11-q1` requested archive extraction, collection filtering and a custom treeness-summary tool, while the capped Sol replicate 3 for `bix-12-q2` requested installed PhyKIT and Datamash tools. Searches and tool inspections were excluded from this request inventory. A recorded execution request is not proof of a successful job, and the selected large-history subset does not estimate custom-tool prevalence across the benchmark.

At the original classification stage, 572/750 Galaxy runs (76.3%) were unclassified and 610/750 open-code runs (81.3%) were labelled as local shell or script with method unclassified. The newly identified requests improve interpretability for selected runs but do not constitute a uniform reclassification of the corpus. Consequently, the available evidence supports differences in recorded tool use, but cannot rank configurations by scientific solution diversity. No independent difficulty strata were available, so consistency across difficulty levels also remains undetermined.

Outcome comparisons further separate route labels from correctness. All 30 runs for `bix-11-q1` were accepted despite differing route indicators. Conversely, all 15 Galaxy answers for `bix-45-q1` were rejected, compared with eight accepted open-code answers, even though Galaxy routes shared a PhyKIT indicator and the retrieved creating jobs were all `ok`. For `bix-61-q5`, neither condition produced an accepted answer despite all 19 retrieved Galaxy creating jobs being `ok`. These cases show that operational completion and agreement at the tool-family level are insufficient to establish answer correctness. They leave open whether discrepancies arose from input selection, analytical settings, interpretation or evaluator behavior.

## Galaxy provides structured provenance alongside higher reported input-token use

Across 250 question-by-configuration comparisons, the median Galaxy/open-code input-token ratio was 4.74, corresponding to a 374% increase (interquartile range, 2.45-9.62; range, 0.265-56.94). Each comparison divides the median provider-reported input tokens of three Galaxy runs by the median of three open-code runs for the same question and configuration. The reported summary is the median of these ratios, rather than a ratio of pooled totals or a median of seed-matched replicate ratios. Calculations used unrounded archived usage values.

**Table 4. Input-token ratios by configuration.** Each row summarizes 50 question-level ratios of condition medians. Quartiles use linear interpolation. Input totals include cached input; cached tokens were not added a second time. Output tokens are outside this endpoint.

| Configuration | Median Galaxy/open-code ratio | Interquartile range |
|---|---:|---:|
| GPT-5.5 via Codex | 3.86 | 2.51-6.78 |
| GPT-5.6 Sol via Codex | 5.03 | 3.10-8.80 |
| GPT-5.6 Luna via Codex | 7.63 | 4.56-19.99 |
| DeepSeek V4 Pro via Codex | 4.50 | 2.30-11.20 |
| DeepSeek V4 Pro via Claude Code, superseded | 2.97 | 1.49-5.12 |

GPT-5.6 Luna had the largest median relative input-token use but did not have the highest answer acceptance. Thus, the observed ordering does not support a simple relationship in which greater relative token use indicates greater capability or fewer mistakes. Ratios also depend on the open-code denominator, provider accounting, caching and harness behavior. They do not directly measure monetary cost, and no independent capability ranking was evaluated.

The traces contain tool discovery, parameter specification, history inspection, execution and waiting operations, but the available summaries do not attribute token consumption to these stages. Nor do they provide a common cross-condition count of scientific attempts: failed Galaxy jobs and nonzero shell exits are different operational observations. The additional token use therefore cannot be quantitatively partitioned into retries versus routine orchestration, and the data do not establish that open code used fewer tokens because it failed less often.

Galaxy's contribution to inspectability is concrete: the retained evidence links tools and parameters to datasets and execution states, and metadata summaries characterize large histories without retrieving every output. Open-code traces also preserve commands and outputs, so the comparison does not establish that provenance is unique to Galaxy. No blinded readability assessment, review-time comparison or cost-effectiveness analysis was conducted. The supported result is the coexistence of high answer acceptance, structured Galaxy execution evidence and increased reported input-token use. Whether that evidence reduces human review effort enough to offset the additional cost remains an empirical question.

Source data and reproducibility: the [50 task analyses](analysis/), [numerical audit](bixBench50_overview_audit.json), and [metadata recovery summary](bixBench50_recovery_summary.md) provide the underlying evidence; the [recovery data](bixBench50_recovery_summary.json) retain workbook rows, source URLs, snapshot dates, tool IDs and event references. The [audit script](../scripts/audit_bixbench50_overview.py) reproduces the numerical summaries and exploratory bootstrap, and the [recovery script](../scripts/summarize_bixbench50_recovery.py) summarizes the workbook-linked archives. Detailed contents of collection-limited histories and 26 binary/unsupported outputs remain intentionally unretrieved. Four histories remain unavailable after archived HTTP 403 responses and certificate-validation failures during metadata-only retries. Neither recovery nor synthesis reran agent analyses or changed original answer scores.
