# IWC: output agreement, execution evidence and the limits of inference

Retrospective analysis of the locally archived workbook cohort, revised 23 September 2026. This report follows [HISTORY_ANALYSIS_INSTRUCTIONS.md](../HISTORY_ANALYSIS_INSTRUCTIONS.md). It describes saved evaluator results; it is not a new execution and not an independent scientific revalidation. Previous versions are preserved in Git. The [scientific audit](iwc_scientific_audit.json) and [calculation script](audit_iwc_results.py) supersede the legacy aggregate extraction for every quantity below; the [sensitivity analysis](iwc_sensitivity_analysis.py) and its [results](iwc_sensitivity_results.json) supply the distribution, influence and mechanism checks in Sections 3 and 4. Original task evidence is unchanged.

## 1. Experimental design, variables and evidence availability

The cohort crosses three controlled variables, and every result below is reported at the level of one of them.

**Tasks** are the 10 supplied IWC workflow tasks. They span read QC, differential expression, host decontamination, amplicon denoising, chromatin accessibility, mitogenome assembly, antimicrobial-resistance detection, peptide verification, pseudobulk single-cell analysis and metadata retrieval. They differ in analytical length and in the object being scored, no independent difficulty grading was supplied, and they are a heterogeneous convenience set rather than a probability sample of biomedical analyses; task difficulty is therefore never used here as an explanatory variable.

**Model configurations** are the four agent set-ups evaluated on every task: GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and Codex + DeepSeek V4 Pro. Each is verified against runtime invocation records (Table 1). Reasoning settings are not uniform — Luna ran at `max` and the others at `high` — so model identity and its runtime configuration are confounded; we therefore write model configuration rather than model throughout.

**Execution environments** are the two settings in which the agent produced and ran code: Galaxy, in which the analysis was carried out through the Galaxy workbench API, and open-ended code, in which the agent executed code directly in its own runtime. Both were supplied with the same skill revision (`03e9f1b978de6128ded02086e43099799a87a5d5`). The archived evidence labels these as conditions.

**Replicates** are three repeat executions of each task by each model configuration in each environment. They were not a designed factor, seeds are not documented, and replicate independence was not established; they are used to quantify run-to-run variation within a fixed combination of the other variables, never as seed-matched pairs across environments. One **run** is a single execution of one task, by one model configuration, in one environment, for one replicate: 10 × 4 × 2 × 3 gives the **240 runs** audited here, 120 per environment and 30 per model configuration per environment. The three replicates of a fixed task, model configuration and environment form an **analysis cell**; there are 80 cells. The **solution path** — the tools and methods through which an agent reached its answer — is an outcome of a run, not a controlled variable, and is analysed separately in Section 7.

This is complete coverage of the supplied workbook, not evidence of coverage of an independently specified protocol. A prospective selection protocol, expected-run inventory, seeds and prior-feedback history were not established.

**Table 1 | Verified model configurations, runtime settings and wall-clock budgets.**

| Model configuration | Recorded runtime model | Reasoning setting | Galaxy runs at 6 h / 12 h | Open-ended-code runs at 6 h / 12 h |
|---|---|---|---:|---:|
| GPT-5.5 | `gpt-5.5` | high | 15 / 15 | 7 / 23 |
| GPT-5.6 Sol | `gpt-5.6-sol` | high | 18 / 12 | 26 / 4 |
| GPT-5.6 Luna | `gpt-5.6-luna` | max | 17 / 13 | 25 / 5 |
| Codex + DeepSeek V4 Pro | `deepseek-v4-pro` | high | 10 / 20 | 7 / 23 |

Each configuration contributes 30 runs per environment. Budgets are ceilings, not observed elapsed time, and are not evidence of censoring. Recorded starts span 27 August to 3 September 2026. Labels are not a capability ranking.
ᵃBudget allocation is unbalanced across configurations and environments, and prompts differ between environments by design, with open-ended-code prompts additionally specifying an execution-log format. Budget, prompt and harness differences are residual confounders, not matched controls; no result below isolates an environment effect from them.

**Table 2 | Evidence availability by category.**

| Evidence category | Observed | Note |
|---|---:|---|
| Runs represented in the workbook | 240/240 | Complete for the supplied inventory; expected protocol coverage unknown |
| Evaluator files present | 240/240 | All identify `iwc-final-answer-v2.2` |
| Numeric agreement scores | 237/240 | 120/120 Galaxy, 117/120 open-ended code |
| Unsupported-route outcomes | 3 | GPT-5.5 open-ended-code host removal r1–r3; null, **not** zeroᵃ |
| Harness status `complete` | 240/240 | An operational state, not a scientific outcome |
| Terminal token-usage records | 240/240 | Exactly one selected terminal record per run |
| Galaxy histories with detailed contents | 118/120 | Two amplicon-denoising histories are metadata-only |
| Evaluator/run-record score conflicts | 17/240 | 12 chromatin accessibility, 5 host removal (Section 6) |

ᵃNull scores are not imputed, and no null is treated as a failure or as a success. Unknown is not zero.

## 2. The scored endpoint, and why it is not answer accuracy

Every saved evaluator identifies `iwc-final-answer-v2.2`. We extract its `reference_accuracy` on the native 0–1 scale rather than the absent legacy `original_evaluator_score` field. **This endpoint is continuous output agreement against a saved reference, with a task-specific definition and tolerance (Table 3). It is not a binary answer-accuracy measure, and it must not be pooled with the answer-acceptance endpoints used in the BixBench or CompBioBench analyses.** No common pass threshold is supplied, so no run is classified as correct or incorrect here, and no "accuracy" percentage is computed.

Averaging across rows of Table 3 is a transparent task-weighted summary of normalized agreement, not a universal biological accuracy measure: the rows score different objects, from k-mer multisets to peptide–accession pairs.

**Table 3 | Task-specific scored object, tolerance and mean agreement by execution environment.**

| Task | Scored object and material tolerance | Galaxy mean | Open-ended-code mean | Numeric runs G / code |
|---|---|---:|---:|---:|
| 001 short-read QC | Geometric mean of transformation F1 and retained paired-read-ID F1 | 0.9989 | 0.9997 | 12 / 12 |
| 002 RNA-seq DE | Geometric mean of gene coverage, direction, magnitude concordance, effect ranking, evidence ranking; effect floor 0.5 | 0.9995 | 1.0000 | 12 / 12 |
| 003 host removalᵃ | Transformation-aware paired-read score; route registration affects evaluability | 0.8788 | 1.0000 | 12 / 9 |
| 005 amplicon denoising | Geometric mean of exact-sequence ASV detection F1 and sample-level abundance-weighted F1 | 0.9586 | 0.7967 | 12 / 12 |
| 006 chromatin accessibility | Peak-interval F1; one-to-one matching at reciprocal overlap ≥ 0.5 | 0.9978 | 0.9903 | 12 / 12 |
| 007 mitogenome assembly | Canonical 31-mer multiset F1; strand invariant, nearly origin invariantᵇ | 0.9133 | 0.8255 | 12 / 12 |
| 008 AMR detection | Normalized resistance-determinant F1, retaining allele specificity | 1.0000 | 1.0000 | 12 / 12 |
| 009 peptide verification | F1 of normalized peptide–UniProt accession pairs, duplicates collapsed | 0.9579 | 0.9394 | 12 / 12 |
| 010 pseudobulk DE | Geometric mean of count-matrix agreement and method-calibrated continuous DE agreement | 0.9979 | 0.9102 | 12 / 12 |
| 011 BioProject retrieval | Geometric mean of project/run/layout, stable-metadata and exact whole-run-content F1ᶜ | 1.0000 | 1.0000 | 12 / 12 |

Means are over all numeric runs in the environment (three replicates × four model configurations). Values are shown to four decimal places; exact values are in `task_results` of the scientific audit. Definitions come from retained evaluator `metric` and `details` records.
ᵃHost-removal environment means rest on different model composition and on unresolved reference routing, so **this row is not a matched environment contrast** (Section 6).
ᵇRotation alone can produce a small penalty, so an assembly score just below 1 need not indicate a biological failure.
ᶜContent agreement is scored per whole run, not per read.

## 3. The agreement endpoint is near-saturated and strongly bimodal

The shape of this endpoint governs how it should be summarized, and it is not well described by a mean. Across the 237 numeric runs the median agreement is **1.0000** and 155 runs (65.4%) score at least 0.999, yet six runs score exactly zero; the mean of 0.9577 sits between two modes that are not scientifically comparable (Table 4).

The consequence is that **only 8 of 237 runs (3.4%) score below 0.5**, and those eight runs carry almost all of the environment signal reported in Section 4. Three are Galaxy runs and five are open-ended-code runs — but two of the three Galaxy runs are among the 17 records whose evaluator and run-record scores conflict (Luna host removal r1 and r3, saved as 0.273 against run-record values of 0.9999 and 1.0). **Under one adjudication of those two records, Galaxy has a single sub-0.5 run in the cohort; under the other it has three.** No adjudication is performed here.

Replicates are correspondingly tight. The median within-cell replicate range is 0.0001 in Galaxy and 0.0000 in open-ended code, and 17 of 40 Galaxy cells and 18 of 39 open-ended-code cells have three identical scores. Dispersion is concentrated in a few cells rather than spread across the cohort: the maximum within-cell range is 1.0000 in Galaxy and 0.9997 in open-ended code. Replicate variability in this cohort is therefore not a continuous noise band but the occasional presence of a catastrophic run alongside two near-perfect ones.

**Table 4 | Distribution of the agreement endpoint and cell-level reliability.**

| Distribution of run-level agreement (n = 237 numeric runs) | Runs | % |
|---|---:|---:|
| Exactly 0 (recorded zeros) | 6 | 2.5 |
| 0.001–0.5 | 2 | 0.8 |
| 0.5–0.9 | 5 | 2.1 |
| 0.9–0.99 | 33 | 13.9 |
| 0.99–0.999 | 36 | 15.2 |
| ≥ 0.999 | 155 | 65.4 |

| Cell-level reliability | Galaxy | Open-ended code |
|---|---:|---:|
| Evaluable analysis cells (three numeric replicates) | 40 | 39ᵃ |
| Cells with all three replicates ≥ 0.99 | 31 (78%) | 27 (69%) |
| Cells with at least one replicate < 0.5 | 2 (5%) | 4 (10%) |
| Median within-cell replicate range | 0.0001 | 0.0000 |
| Third quartile / maximum within-cell range | 0.006 / 1.000 | 0.052 / 0.9997 |
| Cells with three identical replicate scores | 17 | 18 |

Median agreement is 1.0000 and mean agreement 0.9577; the mean is not a representative summary of this distribution. Calculations are reproducible with `iwc_sensitivity_analysis.py`.
ᵃThe GPT-5.5 open-ended-code host-removal cell has three unsupported-route nulls and therefore contributes no evaluable cell.
ᵇOf the eight runs scoring below 0.5, three are Galaxy (host removal Luna r1 and r3, mitogenome assembly GPT-5.5 r1) and five are open-ended code (amplicon denoising GPT-5.5 r1 and r3, mitogenome assembly GPT-5.5 r1 and DeepSeek r2, pseudobulk DeepSeek r3). The two Luna host-removal runs are score-conflicted.

## 4. Environment contrasts are real but fragile, and are driven by a few catastrophic runs

For each model configuration, replicates are averaged within a task and environment, tasks are then weighted equally, and paired task bundles are resampled 10,000 times (seed 20260923) to give a percentile interval. The primary analysis excludes host removal from both environments for every configuration because of missing and unresolved route scores; this is an **exploratory auditor sensitivity choice, not a prespecified primary endpoint**. It retains 27 runs per environment per configuration, 216 runs overall (Table 5).

**Table 5 | Mean agreement difference between execution environments, common nine tasks.**

| Model configuration | Galaxy | Open-ended code | Difference (Galaxy − code) | 95% task-bootstrap intervalᵃ |
|---|---:|---:|---:|---:|
| GPT-5.5 | 0.949 | 0.868 | +0.082 | +0.004 to +0.222 |
| GPT-5.6 Sol | 0.989 | 0.988 | +0.001 | −0.006 to +0.009 |
| GPT-5.6 Luna | 0.984 | 0.983 | +0.001 | −0.003 to +0.008 |
| Codex + DeepSeek V4 Pro | 0.999 | 0.922 | +0.077 | +0.002 to +0.185 |

Nine paired tasks per configuration; 27 runs per environment per configuration. Exact values to five decimal places are in `comparisons.common_nine_tasks` of the scientific audit.
ᵃIntervals resample the nine paired task bundles with replacement, retaining all six runs of each task–configuration comparison; they quantify sensitivity to task composition **within this cohort of ten tasks**, not uncertainty over biomedical workflows in general. With nine independent units, percentile-bootstrap coverage is approximate. The four configurations share the same tasks, so the four intervals are not independent, and no multiple-comparison adjustment or confirmatory test is reported.

Two diagnostics show how little of this rests on a broad shift (Table 6). First, a **leave-one-task-out jackknife**: dropping the single most influential task moves the GPT-5.5 difference from +0.082 to +0.013 and the DeepSeek difference from +0.077 to +0.045. For Sol and Luna the direction of the difference is **not stable** — dropping one task is enough to reverse the sign — so those two near-zero contrasts carry no directional information.

Second, a **zero-run mechanism check**: excluding every task that contains any zero-scored run for that configuration reduces the GPT-5.5 difference from +0.082 to +0.012 and the DeepSeek difference from +0.077 to +0.004. Sol and Luna have no zero-scored runs and are unaffected. The per-task differences make the same point directly: GPT-5.5's contrast is carried by amplicon denoising (+0.631) and DeepSeek's by pseudobulk DE (+0.334) and mitogenome assembly (+0.332), each of which contains at least one open-ended-code run that scored zero.

**The supported interpretation is therefore narrow and mechanistic.** In this cohort the two configurations with an apparent Galaxy advantage do not show broadly higher agreement; they show the same near-ceiling agreement as the others on most tasks, plus a small number of open-ended-code runs that failed a final-artifact contract outright (Section 5). Where those failures are removed, the remaining differences are of order 0.004–0.013 on a 0–1 scale, which this design cannot distinguish from zero. Nothing here establishes equivalence either: no equivalence margin was prespecified, only nine task units are available, and prompt, budget and harness differences remain uncontrolled.

**Table 6 | Influence and mechanism diagnostics for the environment contrasts.**

| Model configuration | Difference, all nine tasks | Leave-one-task-out range | Most influential task | Sign stable under leave-one-outᵃ | Difference excluding tasks with any zero-scored runᵇ |
|---|---:|---:|---|:---:|---:|
| GPT-5.5 | +0.0818 | +0.0132 to +0.0920 | 005 amplicon denoising | yes | +0.0124 (2 tasks removed) |
| GPT-5.6 Sol | +0.0014 | −0.0018 to +0.0040 | 006 chromatin accessibility | **no** | +0.0014 (0 removed) |
| GPT-5.6 Luna | +0.0010 | −0.0020 to +0.0021 | 009 peptide verification | **no** | +0.0010 (0 removed) |
| Codex + DeepSeek V4 Pro | +0.0768 | +0.0447 to +0.0865 | 010 pseudobulk DE | yes | +0.0037 (2 removed) |

Four decimal places are retained here because the differences being compared are of order 10⁻³. Computed by `iwc_sensitivity_analysis.py`; full per-task differences are in `per_task_differences_common_nine`.
ᵃ"Sign stable" means every one of the nine leave-one-task-out estimates has the same sign as the full estimate. Where it is `no`, the observed direction is an artefact of task composition.
ᵇTasks containing a zero-scored run for that configuration are amplicon denoising and mitogenome assembly (GPT-5.5) and mitogenome assembly and pseudobulk DE (DeepSeek). This is a mechanism check, not a corrected estimate: removing a task because of its outcome is a post-hoc exclusion and is reported alongside, never in place of, the full-cohort value.

A second sensitivity retains host removal wherever all three replicates have numeric scores, giving 39 task–configuration pairs and 234 runs and excluding both environments of the unmatched GPT-5.5 host-removal cell (Table 7). Luna's difference changes sign between the two analyses, from +0.001 to −0.048, which is what makes the scoring adjudication in Section 6 consequential rather than clerical.

**Table 7 | Available-pair sensitivity, retaining host removal where fully scored.**

| Model configuration | Paired tasks | Galaxy | Open-ended code | Difference | 95% interval |
|---|---:|---:|---:|---:|---:|
| GPT-5.5 | 9 | 0.949 | 0.868 | +0.082 | +0.004 to +0.222 |
| GPT-5.6 Sol | 10 | 0.991 | 0.989 | +0.001 | −0.005 to +0.008 |
| GPT-5.6 Luna | 10 | 0.937 | 0.984 | **−0.048** | −0.147 to +0.006 |
| Codex + DeepSeek V4 Pro | 10 | 0.999 | 0.930 | +0.069 | +0.001 to +0.167 |

Three numeric Galaxy host-removal scores excluded from the matched analysis remain in the full inventory. Neither analysis is a corrected version of the other; they bracket the effect of an unresolved scoring question.

## 5. Completion is not correctness: completed runs fail final-artifact contracts

All 240 harness records report `complete`, yet six runs score exactly zero and three have unsupported-route nulls. Process monitoring alone would have reported a fully successful cohort. The zeros are not noise: each has a specific, diagnosable cause recorded in the evaluator, and the causes are different in kind.

- **Identifier casing.** Amplicon denoising, GPT-5.5 open-ended code r1 and r3 score zero because all 17 submitted sample identifiers have altered letter case. The evaluator rejects sample identity, not ASV ordering. This is an output-contract failure, not a denoising failure; no repaired answer is substituted ([r1 evaluator](analysis/wf_005_amplicon_dada2_pe_denoising/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/evaluation.json)).
- **Statistical self-inconsistency.** Pseudobulk DE, DeepSeek open-ended code r3 scores zero because submitted FDR values are inconsistent with Benjamini–Hochberg adjustment of the submitted p-values, with a maximum deviation of 0.00342 against a tolerance of 1 × 10⁻⁶. The analysis completed; its reported statistics do not cohere ([evaluator](analysis/wf_010_pseudobulk_scrna_de/source_snapshots/huggingface_traces/files/open_ended_code_codex_deepseek_v4_pro_r3/evaluation.json)).
- **Sequence content.** Three mitogenome assembly runs score zero: GPT-5.5 r1 **in both environments** and DeepSeek open-ended code r2. The endpoint is sequence-content agreement, not exit status. That the same configuration failed in both environments contradicts any blanket claim that the Galaxy environment prevents scientific failure ([assembly archive](analysis/wf_007_vgp_mitogenome_assembly/source_snapshots/huggingface_traces/files/)).

These three failure modes — identifier normalization, statistical self-consistency and content agreement — are invisible to exit status, job state and harness completion alike. Read with Section 4, they are also the substance of the environment contrast: the measurable difference between environments in this cohort is largely the difference between occasionally emitting an uninterpretable final artifact and not doing so.

**Near-unity agreement does not guarantee identical scientific decisions.** GPT-5.5 open-ended code r1 on RNA-seq DE scores 0.999966, yet its saved diagnostic reports **12 significant genes against 13 in the reference, with significant-set Jaccard 0.9231** ([evaluator](analysis/wf_002_rnaseq_de_visualization/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/evaluation.json)). A composite agreement score of 0.99997 and a one-gene difference in the thresholded result set are both true of the same run. Component metrics and thresholded findings should therefore accompany any headline agreement score; the evaluator file does not establish independent biological truth.

## 6. Scoring provenance is itself a result

The status of these numbers as final, publication-frozen official scores **remains to be confirmed**: 17 of 240 run records conflict materially with their evaluator files — 12 chromatin accessibility and 5 host removal. Conflict tolerance is an absolute difference greater than 1 × 10⁻⁹, or numeric-versus-null disagreement; smaller differences are treated as rounding. Both fields are retained in the audit and no record was regraded, replaced or resolved in favour of the more convenient source.

The host-removal conflicts are consequential rather than cosmetic. Galaxy Luna r1 and r3 declare BWA-MEM and BWA-MEM2 but their evaluator records carry no route provenance and score approximately 0.273, whereas `run_record.acc` gives 0.9999 and 1.0. GPT-5.5 open-ended-code r1–r3 receive explicit unsupported-route nulls for BWA, minimap2 and minimap2. Those five records determine both whether Luna's environment difference is +0.001 or −0.048 (Tables 5 and 7) and whether Galaxy has one or three sub-0.5 runs in the entire cohort (Section 3). A frozen route registry and evaluator lineage are required before the host-removal difference can be interpreted as biological inferiority, and nothing here authorizes assigning nulls a value of zero or one. See the [host-removal archive](analysis/wf_003_host_contamination_removal/source_snapshots/huggingface_traces/files/).

This is a transferable finding for benchmark reporting: where an evaluation pipeline emits more than one score field, the choice between them can reverse a headline comparison, so score lineage belongs in the results rather than in a data-availability statement.

## 7. Execution, failures and operational recovery

Across detailed Galaxy snapshots there are **1,607 distinct creating jobs**, deduplicated by server and job ID: **277 acquisition jobs** (255 `__DATA_FETCH__`, 22 `upload1`) and **1,330 other creating jobs**, of which 1,112 are `ok`, 202 `error` and 16 `deleted`. Deleted is not automatically failure. Other jobs include domain tools, text utilities, converters and 19 Jupyter interactive-tool jobs (17 `ok`, 2 `deleted`); this is not a count of 1,330 independent scientific attempts. An earlier 1,352-job label included 22 uploads and is corrected here.

Of the 118 runs with detailed linked histories, **75 (63.6%) contain at least one observed error job**, with a median of 1 error job per observed run (IQR 0–2.75, range 0–14), including error-free runs. These are history-associated counts, not established agent-owned events: shared upstream jobs and actions before or after the original run must be resolved before attributing chronology or cost. The two unavailable histories are not assigned zero errors.

Legacy transcript extraction records nonzero shell exits in 95/120 Galaxy and 113/120 open-ended-code runs, with medians of 2 (IQR 1–3, range 0–10) and 4 (IQR 2–6, range 0–24). A shell call may perform discovery, orchestration, validation or several analyses, and a nonzero exit can be an intentional diagnostic. These counts are extraction-limited where JSONL is malformed or partial. They are **not comparable scientific-failure rates** and cannot demonstrate superior recovery in either environment.

The archive contains **41 same-tool/same-input failure-to-later-success candidate links across 26 Galaxy runs**, connecting 41 failed endpoints to only **27 distinct successful endpoints**, because several failures share one success. These are neither 41 verified recoveries nor a recovery fraction: a denominator such as "41/202 recovered" would be unjustified. Root cause, corrective action and identity of scientific objective all still require adjudication. Failed attempts before a first correct answer remain unavailable because no validated attempt definition or endpoint chronology exists, and **no equivalent detector exists for the open-ended-code environment**, so these counts support no cross-environment recovery comparison.

One sequence illustrates what the evidence does and does not show. In short-read QC, GPT-5.5 Galaxy r3, fastp jobs created at 12:48:04 and 12:49:29 on 28 August entered `error`; a job created at 12:50:11 with the same read HDA IDs completed successfully. The collection association changed while quality settings stayed at Q20, 40% unqualified bases, at most five Ns and minimum length 15. The successful command processed 377,961 paired reads, retained 277,113 pairs, and the run's final agreement was 1.0. Failed-job stderr and launch commands are absent, so the cause cannot be attributed to a specific parameter or to Galaxy guidance, and two candidate links share this single success ([task evidence](analysis/wf_001_short_read_qc_trim/history_analysis_evidence.json), run `galaxy_gpt_5_5_r3`; [job snapshots](analysis/wf_001_short_read_qc_trim/source_snapshots/galaxy/bbd44e69cb8906b57bab7c688e55a3a0/jobs/)). This is a capability case study, not a comparative recovery experiment.

## 8. Solution paths and replicate agreement

Method declarations are available for **95/96 runs on four tasks** (RNA-seq DE, host removal, chromatin accessibility, pseudobulk DE). Of 32 task–configuration–environment cells, 31 have all three declarations: **13 use a single declared route, 15 use two and 3 use three**. The incomplete cell is GPT-5.5 Galaxy pseudobulk, which has no retained `method.json` for r2 and is excluded from the agreement denominator rather than counted as agreement. These are coarse declarations, not verified execution routes; the remaining six tasks are not assigned biological methods inferred from generic shell commands.

RNA-seq declarations converge on DESeq2 in 23/24 runs, with edgeR in Galaxy Luna r1. Chromatin accessibility shows the widest declared variation: Galaxy commonly declares Bowtie2 with MACS2 or Genrich, whereas open-ended code also declares BWA-MEM, minimap2 and MACS3. Pseudobulk declarations include edgeR, DESeq2 and an unspecific negative-binomial GLM. Different declared routes coexist with high agreement, so a declared route alone is not a performance guarantee (Table 8).

Route-specific references change what agreement means. GPT-5.5 open-ended code r1 on chromatin accessibility declares BWA-MEM with MACS3 and scores 1.0 against a calibrated route whose evaluator provenance records BWA-MEM 0.7.19, MACS3 3.0.4, hg19 paired-end processing, MAPQ 30, mitochondrial and duplicate filtering, and q = 0.05 without control ([evaluator](analysis/wf_006_atacseq_chromatin_accessibility/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/evaluation.json)). This supports evaluating valid alternatives against declared methods rather than assuming one toolchain is uniquely correct. It does not resolve the 12 chromatin-accessibility score conflicts or demonstrate independent reference calibration. Difficulty-dependent variability cannot be assessed: no independently defined difficulty labels were supplied.

**Table 8 | Declared solution paths by replicate.**

| Task | Model configuration | Galaxy r1 / r2 / r3 | Open-ended code r1 / r2 / r3 |
|---|---|---|---|
| RNA-seq DE | GPT-5.5 | D / D / D | D / D / D |
| RNA-seq DE | Sol | D / D / D | D / D / D |
| RNA-seq DE | Luna | E / D / D | D / D / D |
| RNA-seq DE | DeepSeek | D / D / D | D / D / D |
| Host removal | GPT-5.5 | B2 / B2 / B2 | BWA / minimap2 / minimap2 |
| Host removal | Sol | BM2 / BM / B2 | B2 / BM / B2 |
| Host removal | Luna | BM / B2 / BM2 | B2 / B2 / B2 |
| Host removal | DeepSeek | BM / B2 / B2 | BM / BM / B2 |
| Chromatin accessibility | GPT-5.5 | B2+M2 / B2+M2 / B2+Genrich | BM+M3 / B2+M3 / B2+M3 |
| Chromatin accessibility | Sol | B2+M2 / B2+Genrich / B2+M2 | B2+M3 / B2+M3 / B2+M2 |
| Chromatin accessibility | Luna | B2+M2 / B2+M2 / B2+M2 | B2+M3 / BM+M2 / B2+M3 |
| Chromatin accessibility | DeepSeek | B2+M2 / B2+M2 / B2+M2 | Bowtie+M3 / B2+M2 / minimap2+M2 |
| Pseudobulk DE | GPT-5.5 | E / unavailable / E | D / NB / D |
| Pseudobulk DE | Sol | E / E / D | E / D / D |
| Pseudobulk DE | Luna | E / D / E | D / D / D |
| Pseudobulk DE | DeepSeek | E / D / D | D / D / D |

Entries are declarations for replicates 1 / 2 / 3, not independently verified execution. B2, Bowtie2; BM, BWA-MEM; BM2, BWA-MEM2; M2/M3, MACS2/MACS3; D, DESeq2; E, edgeR; NB, unspecific negative-binomial GLM. `Bowtie` is retained literally rather than silently corrected to Bowtie2.
ᵃFunctional distinctions are alignment-based host-read exclusion, alignment plus peak calling, and count-based differential-expression modelling. Within these labels, preprocessing, references, contrasts and parameters can still differ; sample identity and the multiplicity-adjustment universe are scientifically consequential even when the declared algorithm is unchanged. The legacy tool/command fingerprint output (`solution_path_consistency_results.json`) is not used as evidence of biological-method agreement.

## 9. Token usage, provenance and readability

Exactly one terminal `turn.completed` usage event is selected per run. Where a compressed trace is retained it takes precedence over a partial plain counterpart, and representations are never summed. Input and output are reported separately; cached input and reasoning output are preserved as reported fields and not added as extra tokens. Counts include repeated context, are not unique prompt lengths, and are not a universal unit of work across providers.

All 240 runs are included, including zero- and null-scored runs (Table 9). Typical within-task input usage is higher in Galaxy for every configuration, with median within-task ratios of 1.66–2.77. **Higher typical usage does not imply higher total usage**: summed reported input is 815,782,106 tokens for Galaxy against 919,621,843 for open-ended code, and summed output is 3,450,209 against 3,678,015. Open-ended code carries a long upper tail, including a single chromatin-accessibility run (DeepSeek, open-ended code r2) at 67,050,893 input tokens. These are archive-accounting totals, not costs: pricing, cache discounts, compute charges and a common billing basis are unavailable.

**Table 9 | Provider-reported token usage by model configuration and execution environment.**

| Model configuration | Galaxy input, median [IQR], millions | Code input, median [IQR], millions | Median within-task ratio G/codeᵃ | Galaxy output, median [IQR], thousands | Code output, median [IQR], thousands |
|---|---:|---:|---:|---:|---:|
| GPT-5.5 | 2.35 [1.53, 3.51] | 1.19 [0.61, 3.44] | 1.66 | 16.7 [12.7, 20.3] | 14.8 [12.2, 28.4] |
| GPT-5.6 Sol | 4.23 [2.05, 6.09] | 1.44 [0.81, 3.08] | 2.77 | 16.7 [14.2, 21.5] | 14.9 [9.2, 20.1] |
| GPT-5.6 Luna | 10.16 [5.61, 12.00] | 3.66 [1.75, 15.32] | 2.41 | 36.7 [28.3, 46.6] | 31.7 [18.3, 65.7] |
| Codex + DeepSeek V4 Pro | 6.34 [3.32, 11.74] | 2.08 [1.05, 8.95] | 2.10 | 31.5 [25.1, 49.8] | 25.3 [20.0, 36.9] |

Thirty runs per environment per configuration, spanning the same ten tasks.
ᵃThe median, across the ten tasks, of each task's Galaxy three-replicate input median divided by its open-ended-code three-replicate input median. This is a median of within-task ratios, **not** the ratio of the pooled medians shown in the adjacent columns.

Usage is **unattributed to analytical stages**: a single terminal total cannot separate discovery, repeated context, polling, retries, analysis and validation, so 100% of these totals is stage-unattributed and no share of the Galaxy excess can be assigned to retries. No adjusted performance-versus-usage association is claimed given heterogeneous tasks, unequal reasoning settings, unequal budgets and unresolved score adjudication. There is no correct-only token analysis because no binary correctness threshold is defined for this endpoint.

Galaxy histories expose parameters, creating jobs, input/output links and failure states; open-ended-code archives preserve scripts, commands and transcripts. This demonstrates **inspectable provenance in both environments, not measured improvement in human readability**. No blinded reviewer study, reconstruction time, reconstruction-error rate or inter-reviewer agreement was measured, so benefit-versus-cost claims remain untested.

## 10. Input sharing, computation location and reproducibility

The 2,173 saved Galaxy job-file entries collapse to 1,607 server-scoped job IDs, so shared creating-job provenance exists and copies must not be charged as independent executions. This does not establish how many unique inputs were independently downloaded or which outputs were reused; one upload job is not necessarily one dataset. Each task reports a single input-tree hash across its 24 runs, which is harness-attested input consistency rather than a new byte-level verification.

Environment labels are assignments, not compliance certifications. Snapshots include text-processing wrappers and interactive environments alongside domain tools, and successful creation of an interactive environment does not reveal the computation inside it. Galaxy API calls from a local shell may be orchestration, whereas local data transformation may be analysis; these must be classified from original commands. External reference retrieval is distinct from remote analytical computation. **The number of strictly Galaxy-only scientific runs is not established**, and current execution rules are not applied retroactively to original prompts.

Source traces were collected from a Hugging Face `main` reference rather than a pinned collection-wide commit, so retained hashes anchor the local snapshot but cannot recover unrecorded upstream history. Galaxy snapshots were collected after execution, so current state is not immutable original chronology. All 120 Galaxy manifests record `tls_certificate_verified: false`; matching local hashes demonstrate preservation since collection, not authenticated transport at collection. Linked artifacts and the two metadata-only histories limit independent reconstruction. No agent code, evaluator or biological pipeline was rerun for this report.

## 11. Audit and statistical methods

Run `python3 IWC/audit_iwc_results.py` from the repository root to regenerate the supplemental JSON, and `python3 IWC/iwc_sensitivity_analysis.py` to regenerate the distribution, jackknife and zero-run analyses in Sections 3 and 4. Neither regenerates this editorial report. Do not use the legacy `build_iwc_overview.py`, whose older extraction reinstates missing-score and dataset-count errors. Run `python3 IWC/test_iwc_scientific_audit.py` for regression checks covering source hashes, local links, raw-score extraction, paired denominators, bootstrap results, displayed rounding, recovery-link chronology and route/usage coverage.

- **Inventory.** Join workbook task/run IDs to ten packages; assert 240 unique runs and 80 observed three-run cells. Expected protocol coverage remains unknown.
- **Scores.** Extract evaluator `reference_accuracy`, metric, version, error and route; preserve `run_record.acc` separately. Do not impute nulls, repair answers, select best replicates or binarize agreement.
- **Reported precision.** Agreement means are displayed to four decimal places and differences to three or four, chosen so that displayed digits do not exceed what nine to ten task units support; exact values are retained in the supplement. Percentages are given to one decimal place.
- **Comparisons.** Average three replicates within a task and environment, then average equally across matched tasks within a configuration. Resample task pairs with replacement 10,000 times using Python's seeded generator, seed 20260923, reporting linearly interpolated 2.5th and 97.5th percentiles. Configurations share tasks; no pooled analysis assumes their contrasts are independent.
- **Sensitivity.** Leave-one-task-out estimates recompute the contrast over the remaining eight tasks. The zero-run check removes every task containing a zero-scored run for that configuration; it is an outcome-dependent exclusion, reported only beside the full estimate.
- **Distributions.** Medians and IQRs use linear interpolation at (n − 1)q. All visible runs enter operational summaries except histories without detailed jobs. Unknown is never zero.
- **Native jobs.** Deduplicate by server and job ID. Fetch and upload are acquisition; other jobs retain original tool IDs and status. Event sequence numbers do not substitute for timestamps. Recovery links remain candidates without adjudicated causal chains.
- **Routes.** Normalize only spelling and case in retained `method.json`, preserving method families and aligner generations. The 31 complete cells, not all 32, supply the replicate-agreement denominator.
- **Tokens.** Use one terminal usage record per run, preserve its file hash and line, and never add cached or reasoning subsets. Selected traces contain 25 unparseable lines across 25 runs; event completeness is limited even where terminal usage is present.
- **Integrity.** 9,096 retained trace/output/job-file entries were checked against collection-manifest hashes, with sizes checked where recorded; all passed. This verifies archival integrity, not scientific validity, remote authenticity or completeness of unretained files.

## 12. Claim-to-evidence map

Finding IDs resolve to explicit run sets in `finding_run_sets` of [iwc_scientific_audit.json](iwc_scientific_audit.json); `runs.sources` resolves to hashed original records. Contradictory evidence remains in the archive.

| ID | Supported statement | Calculation / source | Qualification or counterevidence |
|---|---|---|---|
| IWC-F1 | 237/240 runs have numeric saved agreement scores | `runs[*].score`, `inventory` | Three unsupported-route nulls; expected protocol inventory unknown |
| IWC-F2 | The endpoint is near-saturated and bimodal; 8/237 runs score below 0.5 | `endpoint_shape` in sensitivity results | Two of three sub-0.5 Galaxy runs are score-conflicted |
| IWC-F3 | Environment differences vary by configuration and are carried by few tasks | `comparisons.common_nine_tasks`; `jackknife_common_nine` | Sol and Luna signs are unstable; budget/prompt confounding |
| IWC-F4 | Removing tasks containing zero-scored runs reduces the two positive differences to ≤0.013 | `zero_run_sensitivity_common_nine` | Outcome-dependent exclusion; reported only alongside full estimates |
| IWC-F5 | Scoring provenance changes a headline contrast | `runs[*].score_conflict_gt_1e_9`; `comparisons.available_pairs` | 17 conflicts unresolved; no official freeze or independent adjudication |
| IWC-F6 | Completed runs fail identifier, statistical and content contracts | Zero-score run set; denoising, assembly and pseudobulk evaluators | One zero is a Galaxy run; zeros differ in scientific meaning |
| IWC-F7 | Near-unity composite agreement can mask a different significant-gene set | RNA-seq GPT-5.5 open-ended-code r1 evaluator | Single case; evaluator is not independent biological truth |
| IWC-F8 | Histories preserve failures and candidate recovery sequences | `jobs`, `operational`, `recovery_candidates` | Two histories incomplete; candidates unverified; no code-side detector |
| IWC-F9 | Declared routes vary within and across environments | `route_cells` | One missing declaration; four tasks only; declarations do not certify execution |
| IWC-F10 | Within-task input-token ratios exceed one for all configurations | `token_results` | Open-ended-code totals are larger; no costs or stage attribution |

## 13. What this cohort can and cannot support

The methodological contribution supported here is the separation of four outcomes that a single "success rate" would merge: continuous output agreement, operational execution state, provenance completeness and adjudication uncertainty. The archive makes specific, transferable failure modes visible — identifier preservation, statistical self-consistency, route-sensitive references, missing bytes and conflicting score sources — and shows that a near-ceiling agreement distribution can conceal all of them.

What the cohort cannot support: any claim of general superiority of an execution environment, of equivalence between environments, of environment purity, of improved recovery, of reduced human review effort or of cost benefit. Ten tasks, four configurations and unmatched prompts and budgets do not license a causal environment effect, and the two positive environment differences shrink by roughly an order of magnitude once a handful of catastrophic runs is set aside.

Priority additions, in order of what would change conclusions most: (1) resolution of all 17 score conflicts with a frozen evaluator and reference registry with authenticated provenance, starting with host removal; (2) a dated protocol and prospective selection manifest with seeds and independence metadata; (3) independently justified reference calibration plus component-level scientific assessment, since composite scores demonstrably mask thresholded differences; (4) recovery of the two capped histories and the scientifically necessary linked bytes under authenticated transport; (5) run-owned event windows and a common stage/attempt/recovery codebook applied to **both** environments, since the recovery detector is currently Galaxy-only; (6) controlled budgets, prompts and harnesses, or an explicitly observational framing; and (7) a prespecified blinded reconstruction study with contemporaneous cost accounting before any readability or cost-benefit claim. A larger, independently selected task set is required for any generalization beyond these ten workflows.

## Abstract-ready paragraph

We audited 240 archived executions of ten IWC workflow tasks across four model configurations and two execution environments. Saved evaluators supplied continuous output-agreement scores for 237 runs, with three unsupported-route nulls and 17 records whose evaluator and run-record scores conflict. Agreement was near-saturated and bimodal: the median run scored 1.0000 and 65.4% scored at least 0.999, while eight runs (3.4%) scored below 0.5. Mean Galaxy-minus-open-ended-code differences across nine matched tasks ranged from +0.001 to +0.082, but leave-one-task-out analysis showed the two positive differences were carried by single tasks and fell to +0.012 and +0.004 once tasks containing a zero-scored run were removed, while the two near-zero differences were not sign-stable. Completed runs failed final-artifact contracts in three distinct ways — altered sample-identifier casing, FDR values inconsistent with Benjamini–Hochberg adjustment, and assembly sequence content — none detectable from harness status, and one run with 0.99997 composite agreement nevertheless reported 12 significant genes against 13 in the reference. These records support reporting agreement, execution state, provenance and adjudication uncertainty as separate outcomes, and identify score-lineage resolution as a prerequisite for comparative claims.

## Results draft

The observed IWC cohort comprised ten workflow tasks, four runtime-verified model configurations and three replicate labels in each of two execution environments (240 runs). All harness records reported completion, but only 237 runs carried numeric archived agreement scores; three GPT-5.5 open-ended-code host-removal runs returned unsupported-route nulls, and six completed runs scored exactly zero. The scored endpoint is continuous, task-specific output agreement against a saved reference and is not interchangeable with binary answer accuracy.

The endpoint was near-saturated. The median run scored 1.0000, 155 of 237 runs (65.4%) scored at least 0.999, and replicates within a cell were usually near-identical (median within-cell range 0.0001 in Galaxy and 0.0000 in open-ended code). Variation was concentrated rather than continuous: only eight runs scored below 0.5, three in Galaxy and five in open-ended code, and two of the three Galaxy cases are among the 17 records whose evaluator and run-record scores conflict.

Across nine matched tasks, mean Galaxy-minus-code differences were +0.082 (95% task-bootstrap interval +0.004 to +0.222) for GPT-5.5, +0.001 (−0.006 to +0.009) for Sol, +0.001 (−0.003 to +0.008) for Luna and +0.077 (+0.002 to +0.185) for DeepSeek. These contrasts proved fragile. Leave-one-task-out analysis moved the GPT-5.5 difference to +0.013 and the DeepSeek difference to +0.045, and reversed the sign of both near-zero differences; excluding tasks containing any zero-scored run reduced the two positive differences to +0.012 and +0.004. Retaining host removal where fully scored changed Luna's difference from +0.001 to −0.048, a reversal driven by five conflicted or null records. The environment difference in this cohort is therefore not a broad agreement gradient but the occasional absence of a catastrophic final-artifact failure.

Those failures were diagnosable and heterogeneous. Two amplicon-denoising runs scored zero because all 17 sample identifiers had altered letter case; one pseudobulk run scored zero because submitted FDR values deviated from Benjamini–Hochberg adjustment of the submitted p-values by up to 0.00342 against a 1 × 10⁻⁶ tolerance; three mitogenome runs scored zero on sequence content, including one GPT-5.5 run in each environment. None is visible in harness status or job state. Conversely, an RNA-seq run scoring 0.999966 reported 12 significant genes against 13 in the reference (significant-set Jaccard 0.9231), showing that composite agreement can mask a different thresholded result.

Execution and usage records were kept as separate outcomes. Among 118 detailed Galaxy histories, 75 contained at least one error job, and 202 errors occurred among 1,330 non-acquisition creating jobs; 41 same-tool/same-input failure-to-success candidate links across 26 runs collapsed to 27 successful endpoints and were not treated as verified recoveries, and no equivalent detector exists for the open-ended-code environment. Median within-task input-token ratios favoured lower usage in open-ended code (1.66–2.77), yet open-ended code accumulated the larger total input count because of a long upper tail. Histories, scripts and transcripts support inspection of all of these differences; no reconstruction study or monetary accounting was performed. Together the observations motivate an evaluation framework that retains scientific agreement, operational state, provenance completeness and resource use as distinct outcomes rather than collapsing them into a single success claim.
