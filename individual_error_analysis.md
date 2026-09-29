# Individual error analysis: BixBench-50, CompBioBench and IWC

This review analyses **93 task-level cases** from an archive of **160 tasks and 4,240 run records**. The cases are every task with at least one wrong, rejected or low-scoring run, plus one IWC workflow whose near-perfect score hides a changed conclusion. Each entry answers three questions: which decision produced each wrong value, what the correct runs did differently, and whether the answers change how the score should be read. The last question matters in two directions. A rejected answer may state the correct result in another form. An accepted answer may rest on local computation, a leaked answer, or a reference that encodes an unstated choice.

In **30 of the 93 cases** the primary cause lies with the benchmark rather than the agent: 6 equivalent answer representations, 4 scoring or evaluator artifacts, and 20 references that depend on an unstated choice. Galaxy platform, wrapper or server behaviour is the primary cause in **8 cases**. A genuine agent analysis error is the primary cause in **52**. Some examples:

- All 30 BixBench answers to bix-53-q2 state the reference direction, and all 30 are rejected.
- Galaxy's extension-less staged file names silently disabled adapter trimming in 7 of 12 Galaxy runs of the ENCODE ATAC-seq pipeline.
- 15 correct Galaxy-condition CompBio answers were computed locally.
- In 26 tasks, agents retrieved or tried to retrieve benchmark answers online.
- Two Galaxy runs copied answers from other runs through the shared Galaxy account.

Both supplied examples are confirmed at the trace level. The two cCRE class labels describe the same element. The reference-matching ATAC value, 28,285, was computed locally after Galaxy execution failed. However, the leaderboard-implied key for that task is 29,556. Only the two runs that executed the real pipeline inside Galaxy obtained it.

The tables below guide the detailed entries. The first counts tasks per benchmark. The second assigns each case one primary category, so each task is counted exactly once. The third lists cross-cutting flags recorded in addition to the primary category. Inside each entry, confirmed mechanisms and inferred ones are kept apart.

**Task coverage**

| Benchmark | Directory | Tasks present | Tasks with an entry | Archived run records | Records per task |
|---|---|---:|---:|---:|---|
| BixBench-50 | `BixBench_50` | 50 | 33 | 1,500 | 30: 5 configurations × 2 conditions × 3 replicates (includes the superseded DeepSeek via Claude Code harness) |
| CompBio | `CompBio` | 100 | 53 | 2,500 | 25: 4 paired configurations × 2 conditions × 3 replicates, plus 1 unpaired GPT-6 Astra code run |
| IWC | `IWC` | 10 | 7 | 240 | 24: 4 configurations × 2 conditions × 3 replicates |
| **Total** | | **160** | **93** | **4,240** | |

Entry criteria: BixBench, at least one rejected run. CompBio, at least one run that differs from the reference. IWC, at least one run below 0.95 or unscored, plus wf_002 (see its entry).

**Error and interpretation categories**

The unit counted is a **task case, not a failed run**. Each case has one primary category, chosen for its main interpretive issue. Secondary issues are listed in the next table and in each entry. A category does not imply that every affected answer is wrong.

| Primary category | BixBench-50 | CompBio | IWC | Total | Cases |
|---|---:|---:|---:|---:|---|
| C1. Equivalent answer expressed differently (label, genotype notation, interval convention, unit, identifier case) | 1 | 4 | 1 | **6** | [bix-53-q5](#bix-53-q5), [annotate-variant-regulatory-overlap-q1](#annotate-variant-regulatory-overlap-q1), [1000G-retrieve-genotype-q1](#1000g-retrieve-genotype-q1), [align-one-sequence-to-reference-q1](#align-one-sequence-to-reference-q1), [extract-rna-secondary-structure-q1](#extract-rna-secondary-structure-q1), [wf_005_amplicon_dada2_pe_denoising](#wf_005_amplicon_dada2_pe_denoising) |
| C2. Scoring or evaluator artifact (correct answer rejected, inconsistent rules, wrong route reference) | 2 | 0 | 2 | **4** | [bix-53-q2](#bix-53-q2), [bix-43-q2](#bix-43-q2), [wf_003_host_contamination_removal](#wf_003_host_contamination_removal), [wf_006_atacseq_chromatin_accessibility](#wf_006_atacseq_chromatin_accessibility) |
| C3. Reference depends on an unstated choice (definition, software version, sample set, threshold) | 11 | 8 | 1 | **20** | [bix-61-q5](#bix-61-q5), [bix-26-q5](#bix-26-q5), [bix-45-q1](#bix-45-q1), [bix-16-q1](#bix-16-q1), [bix-30-q3](#bix-30-q3), [bix-32-q2](#bix-32-q2), [bix-27-q5](#bix-27-q5), [bix-43-q4](#bix-43-q4), [bix-55-q1](#bix-55-q1), [bix-24-q2](#bix-24-q2), [bix-49-q4](#bix-49-q4), [genome-coords-q1](#genome-coords-q1), [protein-shape-q1](#protein-shape-q1), [tissue-fibroblast-q1](#tissue-fibroblast-q1), [odd-one-out-q1](#odd-one-out-q1), [lung-cancer-sc-q1](#lung-cancer-sc-q1), [three-way-barnyard-q2](#three-way-barnyard-q2), [borzoi-rnaseq-q1](#borzoi-rnaseq-q1), [gene-pair-ordering-fraction-q1](#gene-pair-ordering-fraction-q1), [wf_009_clinicalmp_peptide_verification](#wf_009_clinicalmp_peptide_verification) |
| C4. Galaxy platform, wrapper or server behaviour was the primary cause | 4 | 4 | 0 | **8** | [bix-31-q2](#bix-31-q2), [bix-52-q7](#bix-52-q7), [bix-28-q3](#bix-28-q3), [bix-35-q1](#bix-35-q1), [encode-atac-pipeline-q1](#encode-atac-pipeline-q1), [contaminated-rna-q1](#contaminated-rna-q1), [gtf-5-utr-median-len-q1](#gtf-5-utr-median-len-q1), [spatial-sim-q2](#spatial-sim-q2) |
| C5. Agent analysis error (method, statistics, domain knowledge, identifiers, unverified result) | 13 | 37 | 2 | **52** | 52 tasks; see the Category column of the index |
| C6. Execution provenance or answer exposure is the main interpretive issue | 1 | 0 | 0 | **1** | [bix-54-q7](#bix-54-q7) |
| C7. Aggregate score conceals a changed scientific conclusion | 0 | 0 | 1 | **1** | [wf_002_rnaseq_de_visualization](#wf_002_rnaseq_de_visualization) |
| C8. Completion failure (no answer written) | 1 | 0 | 0 | **1** | [bix-46-q4](#bix-46-q4) |
| **Total distinct task cases** | **33** | **53** | **7** | **93** | |

**Cross-cutting flags (recorded in addition to the primary category)**

| Flag | BixBench-50 | CompBio | IWC | Total | Cases |
|---|---:|---:|---:|---:|---|
| A Galaxy-condition answer (correct or not) was computed locally and only staged into Galaxy (`local-fallback-in-galaxy`) | 0 | 11 | 1 | **12** | [encode-atac-pipeline-q1](#encode-atac-pipeline-q1), [reverse-search-gwas-q1](#reverse-search-gwas-q1), [tissue-fibroblast-q1](#tissue-fibroblast-q1), [overexpress-tf-q1](#overexpress-tf-q1), [finding-geo-q1](#finding-geo-q1), [atac-tn5-shift-q1](#atac-tn5-shift-q1), [borzoi-rnaseq-q1](#borzoi-rnaseq-q1), [hic-differential-loop-q1](#hic-differential-loop-q1), [saluki-setup-optimize-q1](#saluki-setup-optimize-q1), [extract-rna-secondary-structure-q1](#extract-rna-secondary-structure-q1), [huggingface-entropy-q1](#huggingface-entropy-q1), [wf_010_pseudobulk_scrna_de](#wf_010_pseudobulk_scrna_de) |
| An answer was copied from another run through the shared Galaxy account (`cross-run-output-reuse`) | 0 | 2 | 0 | **2** | [encode-atac-pipeline-q1](#encode-atac-pipeline-q1), [saluki-setup-optimize-q1](#saluki-setup-optimize-q1) |
| Benchmark answers or sources were retrieved online, or retrieval was attempted (`benchmark-answer-retrieval`) | 7 | 17 | 2 | **26** | [bix-26-q5](#bix-26-q5), [bix-54-q7](#bix-54-q7), [bix-30-q3](#bix-30-q3), [bix-32-q2](#bix-32-q2), [bix-12-q6](#bix-12-q6), [bix-16-q3](#bix-16-q3), [bix-53-q5](#bix-53-q5), [variant-status-q1](#variant-status-q1), [reverse-search-gwas-q1](#reverse-search-gwas-q1), [protein-shape-q1](#protein-shape-q1), [tissue-fibroblast-q1](#tissue-fibroblast-q1), [contaminated-rna-q2](#contaminated-rna-q2), [lung-cancer-sc-q1](#lung-cancer-sc-q1), [characterize-response-q1](#characterize-response-q1), [atac-tn5-shift-q1](#atac-tn5-shift-q1), [covid-patient-q1](#covid-patient-q1), [atac-doublet-q1](#atac-doublet-q1), [1000G-retrieve-genotype-q1](#1000g-retrieve-genotype-q1), [hic-differential-loop-q1](#hic-differential-loop-q1), [histone-chip-q1](#histone-chip-q1), [saluki-setup-optimize-q1](#saluki-setup-optimize-q1), [deg-simple-q2](#deg-simple-q2), [gene-pair-ordering-fraction-q1](#gene-pair-ordering-fraction-q1), [phase-chain-q1](#phase-chain-q1), [wf_009_clinicalmp_peptide_verification](#wf_009_clinicalmp_peptide_verification), [wf_007_vgp_mitogenome_assembly](#wf_007_vgp_mitogenome_assembly) |
| The reference (or the lab working reference) is questionable (`reference-questionable`) | 8 | 6 | 1 | **15** | [bix-61-q5](#bix-61-q5), [bix-26-q5](#bix-26-q5), [bix-54-q7](#bix-54-q7), [bix-45-q1](#bix-45-q1), [bix-43-q2](#bix-43-q2), [bix-30-q3](#bix-30-q3), [bix-27-q5](#bix-27-q5), [bix-43-q4](#bix-43-q4), [genome-coords-q1](#genome-coords-q1), [encode-atac-pipeline-q1](#encode-atac-pipeline-q1), [protein-shape-q1](#protein-shape-q1), [tissue-fibroblast-q1](#tissue-fibroblast-q1), [odd-one-out-q1](#odd-one-out-q1), [lung-cancer-sc-q1](#lung-cancer-sc-q1), [wf_006_atacseq_chromatin_accessibility](#wf_006_atacseq_chromatin_accessibility) |
| A Galaxy platform or server defect contributed (primary or secondary) (`galaxy-platform-defect`) | 3 | 10 | 1 | **14** | [bix-31-q2](#bix-31-q2), [bix-28-q3](#bix-28-q3), [bix-35-q1](#bix-35-q1), [encode-atac-pipeline-q1](#encode-atac-pipeline-q1), [contaminated-rna-q3](#contaminated-rna-q3), [atac-tn5-shift-q1](#atac-tn5-shift-q1), [contaminated-rna-q1](#contaminated-rna-q1), [exogenous-mix-reads-q1](#exogenous-mix-reads-q1), [gene-fusion-q2](#gene-fusion-q2), [saluki-setup-optimize-q1](#saluki-setup-optimize-q1), [extract-rna-secondary-structure-q1](#extract-rna-secondary-structure-q1), [gtf-5-utr-median-len-q1](#gtf-5-utr-median-len-q1), [spatial-sim-q2](#spatial-sim-q2), [wf_009_clinicalmp_peptide_verification](#wf_009_clinicalmp_peptide_verification) |


## Scope and evidence

This is a retrospective, task-by-task trace audit, carried out 27–28 September 2026. It covers three directories:
- `BixBench_50/`: the 33 of 50 tasks with at least one rejected run.
- `CompBio/`: the 53 of 100 tasks with at least one run that deviates from the reference.
- `IWC/`: the 6 of 10 workflows with at least one run below 0.95 or left unscored, plus `wf_002_rnaseq_de_visualization`, whose near-perfect scores hide a changed significant-gene set.

Tasks without an entry had no wrong answer in any run. They were not audited for local fallback or answer retrieval, so their Galaxy-condition successes are not certified as Galaxy-only execution.

Counts refer to archived run records:
- BixBench: 30 per task, including the superseded DeepSeek via Claude Code configuration.
- CompBio: 24 per task in the paired four-model comparison, plus one unpaired GPT-6 Astra code run.
- IWC: 24 per task.

No agent code was rerun, no Galaxy job was submitted, and no file under `ground_truth/` was opened. A few entries recompute a statistic from an already-submitted table, and each says so.

Conventions:
- Evidence is cited as `path:L<line>`, where the line number refers to the decompressed agent trace.
- Run labels read "<model> <condition> r<replicate>". "Galaxy" is the Galaxy-API condition and "code" is the open-ended-code condition.
- Paths are relative to the repository root. The exceptions are the lab results repository described below and, in bix-61-q5 only, two local capsule and run-record folders outside this repository.

A sibling write-up, [individual_error_analysis_codex.md](individual_error_analysis_codex.md), covers 20 of these tasks. Its findings are incorporated here, with two differences:
- On encode-atac-pipeline-q1, this audit shows that the user-supplied reference 28,285 is not the leaderboard-implied key.
- On wf_003 and wf_006, the conflicting score fields are resolved rather than left open.

## How references were established

**BixBench-50.** Each run's `evaluation.json` holds the evaluator's expected value, tolerance and mode, and the original binary score is used as is. Where an entry says an answer "should be accepted", that is an auditor judgment and not a regrade.

**IWC.** Continuous 0–1 agreement between each run's final output and the IWC workflow's reference output (`IWC/iwc_scientific_audit.json`).

**CompBioBench.** No item-level key is archived in this repository (`ground_truth/CompBioBench/README.md`). References come from the lab's results repository `goeckslab/galaxy-agent-benchmark` (private; commit `bdc00429f559`, 2026-09-23), in three layers that must be kept apart:

| Layer | File (in that repository) | Items | Meaning |
|---|---|---:|---|
| Score-inferred | `compbiobench/results/score_inferred_answers.tsv` | 54 | The unique answer consistent with the official leaderboard scores of the 25 submitted 100-answer vectors |
| Score-predicted | `compbiobench/results/score_predicted_answers.tsv` | 46 | Most likely answer, not uniquely determined (usually all runs gave the same answer) |
| Working scientific reference | `compbiobench/results/estimated_answers.tsv` | 100 | The lab's evidence-based reconstruction; **not** the hidden key |

SHA-256: score-inferred `959dd3f2…`, score-predicted `57a6a92d…`, working reference `46ea52ac…`, `paper_site_runs.json` `055cfb18…` (all 25 vectors official as of 2026-09-17).

Independent checks performed for this audit:

1. **Inference replicated.** An integer program over the archived answer vectors and official scores, run independently, recovered the same unique answer for 53 of the 54 score-inferred items. The exception is the regulatory-overlap item, explained in point 2.
2. **The 9 "unresolved hash mismatches" are explained.** `CompBio/compBio_recovery_summary.md` lists 9 answer vectors whose archived bytes disagree with the advertised submission SHA-256. They are exactly the 9 runs whose agents answered `Proximal enhancer,EH38E1957012`. In each archived `predictions.tsv`, replace that string with `pELS,EH38E1957012` and the result reproduces the advertised SHA-256 byte for byte. The leaderboard therefore received `pELS` for all 25 vectors, and the archive keeps the agents' raw wording.
3. **The key reproduces every official score exactly.** Apply that normalization and score each vector against score-inferred plus score-predicted answers. The per-vector totals then reproduce all 25 official scores with zero residual only if `genome-coords-q1 = E`, the answer that GPT-6 Astra alone gave. The published predicted answer `D`, given by all 24 paired runs, leaves a +1/−1 residual pattern across all 25 vectors.
4. **Five working-reference answers disagree with the score-inferred key:** encode-atac-pipeline-q1, lung-cancer-sc-q1, odd-one-out-q1, protein-shape-q1 and tissue-fibroblast-q1. In four of these the working reference is probably what is wrong. In lung-cancer-sc-q1 both readings are defensible. See the entries.

In the CompBio entries, "correct" means a match to the score-inferred answer, or to the predicted answer where no inferred one exists. The one exception is genome-coords-q1, where `E` is used (point 3). Exact string match is used, as on the leaderboard.

## What the individual analyses show

The per-task entries below are the evidence. This section lists recurring mechanisms that change how the scores should be read, with links to the tasks where each was seen. Tags in the index follow the same vocabulary.

1. **A large share of recorded errors belong to the benchmark rather than to the agent.**
   - **The evaluator rejected correct answers.** On [bix-53-q2](#bix-53-q2) all 30 runs gave the reference direction ("increase") and all were rejected. [bix-53-q5](#bix-53-q5) was rejected for writing `10.0%` for 0.1. On [bix-43-q2](#bix-43-q2) the same answer string is scored differently depending on the harness.
   - **IWC routes were scored against the wrong reference.** In [wf_003](#wf_003_host_contamination_removal), correct BWA-MEM output was scored against the Bowtie2 reference, and one run's BWA alias went unrecognised. In [wf_006](#wf_006_atacseq_chromatin_accessibility), several route references were calibrated from a single agent run, so those 1.0 scores are circular.
   - **The reference depends on a choice the prompt never states.** Examples: [bix-61-q5](#bix-61-q5) (the reference re-calls a different read set, while all 30 runs measured the supplied VCF), [bix-54-q7](#bix-54-q7), [bix-26-q5](#bix-26-q5), [bix-30-q3](#bix-30-q3) (runs that followed the source paper got 1:0), [bix-45-q1](#bix-45-q1) (retired PhyKIT RCV definition), [bix-27-q5](#bix-27-q5), [lung-cancer-sc-q1](#lung-cancer-sc-q1) and [genome-coords-q1](#genome-coords-q1).
   - **The working reference disagrees with the leaderboard-implied key.** The lab's working reference should be revised in [encode-atac-pipeline-q1](#encode-atac-pipeline-q1), [protein-shape-q1](#protein-shape-q1), [tissue-fibroblast-q1](#tissue-fibroblast-q1) and [odd-one-out-q1](#odd-one-out-q1). In [lung-cancer-sc-q1](#lung-cancer-sc-q1) both values are defensible.
2. **Equivalent answers graded as wrong.** These are right answers in the wrong spelling:
   - `Proximal enhancer` vs `pELS` ([annotate-variant-regulatory-overlap-q1](#annotate-variant-regulatory-overlap-q1); the leaderboard copies were normalized before submission).
   - Phased vs unphased genotypes ([1000G-retrieve-genotype-q1](#1000g-retrieve-genotype-q1)).
   - An inclusive vs half-open interval end ([align-one-sequence-to-reference-q1](#align-one-sequence-to-reference-q1)).
   - A value with ` kcal/mol` appended ([extract-rna-secondary-structure-q1](#extract-rna-secondary-structure-q1)).
   - A percentage for a fraction ([bix-53-q5](#bix-53-q5)).

   Exact-string scoring counts all of these as failures.
3. **Some correct Galaxy-condition answers were computed outside Galaxy.** In the audited CompBio tasks, 15 correct Galaxy-condition answers came from local computation that was then staged into a history. Eleven of the 15 are GPT-5.5 runs:
   - [atac-tn5-shift-q1](#atac-tn5-shift-q1): 2
   - [borzoi-rnaseq-q1](#borzoi-rnaseq-q1): 2
   - [extract-rna-secondary-structure-q1](#extract-rna-secondary-structure-q1): 3
   - [huggingface-entropy-q1](#huggingface-entropy-q1): 2
   - [saluki-setup-optimize-q1](#saluki-setup-optimize-q1): 2
   - [tissue-fibroblast-q1](#tissue-fibroblast-q1): 2
   - [finding-geo-q1](#finding-geo-q1): 1
   - [hic-differential-loop-q1](#hic-differential-loop-q1): 1

   The trigger was the same each time: user-defined-tool execution was unavailable on the server ("no execution destination", `training_tag_small_rule` routing). The agents then used pip or micromamba locally. [encode-atac-pipeline-q1](#encode-atac-pipeline-q1) (GPT-5.5 Galaxy r2 and r3) and [overexpress-tf-q1](#overexpress-tf-q1) are the same fallback producing wrong values. These runs should be flagged, not counted as Galaxy executions.
4. **Answers were copied between runs through the shared Galaxy account.** Luna Galaxy r1 on [encode-atac-pipeline-q1](#encode-atac-pipeline-q1) copied `13636` from the `answer.txt` of an earlier pilot history. Luna Galaxy r3 on [saluki-setup-optimize-q1](#saluki-setup-optimize-q1) read other runs' job outputs through `/api/jobs` instead of computing. Both runs could see histories left by other runs on the same account. Replicates should run under isolated accounts.
5. **Agents retrieved benchmark answers online.** The retrieval is concentrated in DeepSeek configurations.
   - **Third-party traces.** One public dataset of another group's agent traces (`amanutej/trustworthy-biology-agents-traces`) supplied answers or formats in [1000G-retrieve-genotype-q1](#1000g-retrieve-genotype-q1), [atac-doublet-q1](#atac-doublet-q1), [contaminated-rna-q2](#contaminated-rna-q2), [hic-differential-loop-q1](#hic-differential-loop-q1), [reverse-search-gwas-q1](#reverse-search-gwas-q1) and [bix-12-q6](#bix-12-q6). Some copied answers were wrong.
   - **The BixBench key.** The Hugging Face datasets-server row, including its `ideal` answer, was read before answering in [bix-26-q5](#bix-26-q5), [bix-30-q3](#bix-30-q3) and [bix-54-q7](#bix-54-q7).
   - **Source papers.** In [protein-shape-q1](#protein-shape-q1), a source-paper lookup gave 5 of the 7 correct answers.
   - **The lab's own public results page.** It shows estimated answers and was found by one run ([tissue-fibroblast-q1](#tissue-fibroblast-q1)).

   Accepted runs that read the key before answering are flagged in their entries.
6. **Galaxy-specific mechanisms caused real wrong answers.** These are fixable:
   - **Staged paths without extensions.** Galaxy's staged `dataset_*.dat` paths silently disabled ENCODE's extension-based adapter detection in 7 of 12 Galaxy runs ([encode-atac-pipeline-q1](#encode-atac-pipeline-q1)).
   - **Tool state rebound silently.** Default operations were substituted for the requested ones ([bix-35-q1](#bix-35-q1)).
   - **Wrapper output and parameter semantics.** [bix-28-q3](#bix-28-q3) and [bix-52-q7](#bix-52-q7) turn on what a wrapper outputs; [compute-gccontent-promoter-q1](#compute-gccontent-promoter-q1) and [bedtools-ops-q1](#bedtools-ops-q1) on how a parameter behaves.
   - **Missing or misleading server resources.** A failed Kraken2 core_nt job ([contaminated-rna-q1](#contaminated-rna-q1)). A built-in Salmon "hg38" index that is a genome index ([deg-simple-q2](#deg-simple-q2)).
   - **Route changes forced by user-defined-tool outages.** [bix-31-q2](#bix-31-q2), [exogenous-mix-reads-q1](#exogenous-mix-reads-q1), [spatial-sim-q2](#spatial-sim-q2) and [gtf-5-utr-median-len-q1](#gtf-5-utr-median-len-q1).
7. **Unverified intermediate results.** Most of the remaining errors are genuine scientific mistakes; the most frequent tag is `insufficient-verification`. The agent accepted a number without the invariant check that would have exposed it. Examples:
   - A "mitogenome" never compared to any mitochondrial sequence ([wf_007](#wf_007_vgp_mitogenome_assembly)).
   - Doublets called by Scrublet where only fragment-overlap counting works ([atac-doublet-q1](#atac-doublet-q1)).
   - Host reads not removed before contaminant calling ([contaminated-rna-q2](#contaminated-rna-q2)).
   - A 5′ read-end artifact read as an allele ([variant-status-q1](#variant-status-q1)).
   - Gaps counted as a character state ([bix-12-q2](#bix-12-q2), [bix-12-q5](#bix-12-q5)).
   - Motif enrichment without a GC-matched background ([overexpress-tf-q1](#overexpress-tf-q1)).

   The error types are the same in both conditions. Where a correct run existed, it usually differed at one checkable decision, not in the tools used.
8. **A single continuous IWC score can misstate the scientific conclusion.** It can do so in either direction:
   - In [wf_002](#wf_002_rnaseq_de_visualization) every run scores at least 0.99, yet the significant-gene lists differ. The four PyDESeq2 runs lose one significant gene. Galaxy edgeR, an allowed method, reports 37 significant genes against the reference's 13 and still scores 0.994.
   - In [wf_006](#wf_006_atacseq_chromatin_accessibility) the same peak set scores 0.39 or 1.0, depending on which reference variant is reported.
   - In [wf_010](#wf_010_pseudobulk_scrna_de) a Benjamini–Hochberg bug that changes no significance call scores 0.

   Report component and significant-set agreement next to the headline score.

## Index

Category codes follow the primary-category table above (C1–C8).

### BixBench-50 index

| Task | Galaxy accepted | Code accepted | Category | Finding | Tags |
|---|---:|---:|---|---|---|
| [bix-53-q2](#bix-53-q2) | 0/15 | 0/15 | C2 | All 30 runs got the direction right; the evaluator only accepts an exact copy of the reference sentence | evaluator-false-negative, equivalent-answer, format-contract-error |
| [bix-61-q5](#bix-61-q5) | 0/15 | 0/15 | C3 | Reference 2.68 comes from re-calling the untrimmed subsample FASTQs; every run correctly measured the supplied VCF (2.56) | reference-questionable, underspecified-task, equivalent-answer, route-divergence |
| [bix-26-q5](#bix-26-q5) | 1/15 | 1/15 | C3 | One of the two "3"s came after reading the BixBench key; the reference depends on clusterProfiler defaults the prompt never states | benchmark-answer-retrieval, reference-questionable, underspecified-task, source-version-drift, route-divergence |
| [bix-54-q7](#bix-54-q7) | 1/15 | 1/15 | C6 | The only accepted runs copied the row filter from downloaded benchmark sources; the reference rests on an asymmetric row filter | benchmark-answer-retrieval, reference-questionable, underspecified-task, evaluator-false-negative |
| [bix-45-q1](#bix-45-q1) | 0/15 | 8/15 | C3 | The reference uses a retired PhyKIT RCV definition; every Galaxy run computed the current definition correctly | tool-version-difference, reference-questionable, evaluator-false-negative, equivalent-answer, wrapper-semantics |
| [bix-43-q2](#bix-43-q2) | 11/15 | 2/15 | C2 | The Galaxy advantage comes from a 2–3-gene difference in foreground size, and the evaluator scores the same answer differently by harness | evaluator-false-negative, tool-version-difference, numerical-instability, equivalent-answer, reference-questionable |
| [bix-16-q1](#bix-16-q1) | 10/15 | 10/15 | C3 | CCND1 vs CDKN1A is a sign-convention split (raw gene effect vs −gene effect), plus two ranking/indexing bugs | underspecified-task, domain-knowledge-error, insufficient-verification, scientific-method-error |
| [bix-30-q3](#bix-30-q3) | 15/15 | 6/15 | C3 | Galaxy's 15/15 comes from the raw-Ct route; code runs that followed the source paper got 1:0 | reference-questionable, underspecified-task, route-divergence, benchmark-answer-retrieval |
| [bix-32-q2](#bix-32-q2) | 11/15 | 11/15 | C3 | The count depends on whether the gene lists also require padj; DeepSeek's lfc-only lists give 2 | underspecified-task, route-divergence, scientific-method-error, benchmark-answer-retrieval |
| [bix-12-q4](#bix-12-q4) | 13/15 | 11/15 | C5 | Every wrong U traces to one definitional choice (gap/X handling, ortholog population, four-taxon filter) | scientific-method-error, underspecified-task, route-divergence |
| [bix-14-q1](#bix-14-q1) | 12/15 | 12/15 | C5 | DeepSeek-codex counted splice-region variants as coding (copied from a ToolUniverse script); a wide range lets three wrong cohorts pass | domain-knowledge-error, evaluator-false-positive, insufficient-verification, underspecified-task |
| [bix-27-q5](#bix-27-q5) | 13/15 | 11/15 | C3 | The accepted PC1 value depends on an unstated sample-exclusion rule that the harness's PCA skill imposes | underspecified-task, reference-questionable, evaluator-false-negative, equivalent-answer, no-answer |
| [bix-31-q2](#bix-31-q2) | 13/15 | 11/15 | C4 | Galaxy misses come from failed PyDESeq2 custom tools and a fallback to R DESeq2; code misses come from memory workarounds | galaxy-platform-defect, route-divergence, tool-version-difference, scientific-method-error, numerical-instability |
| [bix-34-q5](#bix-34-q5) | 14/15 | 12/15 | C5 | All failures are DeepSeek-Claude-Code runs that replaced the per-kingdom trees with other distance sources | scientific-method-error, route-divergence, run-truncated-or-timeout |
| [bix-43-q4](#bix-43-q4) | 13/15 | 13/15 | C3 | 9/49 comes from fitting DESeq2 on all 30 samples instead of the 3-vs-3 subset; 8/47 from an added background | underspecified-task, reference-questionable, wrapper-semantics, insufficient-verification |
| [bix-52-q7](#bix-52-q7) | 12/15 | 14/15 | C4 | Two runs counted the header line kept by Galaxy's Filter; one reported the rows kept instead of removed | wrapper-semantics, insufficient-verification, domain-knowledge-error, no-answer, run-truncated-or-timeout |
| [bix-12-q6](#bix-12-q6) | 15/15 | 12/15 | C5 | Code misses come from counting gaps as states or changing the sample; one correct code run read other agents' answers online | scientific-method-error, statistical-error, benchmark-answer-retrieval |
| [bix-35-q2](#bix-35-q2) | 14/15 | 13/15 | C5 | All three misses (superseded CC harness only) shrink the test to a "shared-ortholog" subset | scientific-method-error, route-divergence |
| [bix-55-q1](#bix-55-q1) | 15/15 | 12/15 | C3 | Both "100" answers come from runs that installed BUSCO 5.7.1 locally; "64" comes from a hand-rolled BUSCO substitute | tool-version-difference, scientific-method-error |
| [bix-12-q2](#bix-12-q2) | 15/15 | 13/15 | C5 | Rejected runs counted gaps as a character state; one accepted value relies on a protein-alphabet bug | domain-knowledge-error, evaluator-false-positive |
| [bix-12-q5](#bix-12-q5) | 15/15 | 13/15 | C5 | Counting gaps as a character state inflated the maximum from 29 to 35 | domain-knowledge-error |
| [bix-16-q4](#bix-16-q4) | 15/15 | 13/15 | C5 | Both code failures are data-alignment bugs: genes or cell lines paired out of order | statistical-error, insufficient-verification |
| [bix-24-q2](#bix-24-q2) | 14/15 | 14/15 | C3 | "Upregulation" follows from a 30-sample model; the six-sample CBD-vs-DMSO fit gives downregulation | underspecified-task, route-divergence, statistical-error |
| [bix-49-q4](#bix-49-q4) | 15/15 | 13/15 | C3 | 2118 vs 2106 is only DESeq2's independent-filtering alpha; the two 2100s come from PyDESeq2 | wrapper-semantics, tool-version-difference, route-divergence |
| [bix-16-q3](#bix-16-q3) | 14/15 | 15/15 | C5 | The one miss did not flip the sign of the DepMap gene-effect scores; this is not a data mismatch | domain-knowledge-error, wrapper-semantics, benchmark-answer-retrieval |
| [bix-22-q1](#bix-22-q1) | 14/15 | 15/15 | C5 | The one miss comes from a fragile multi-tool Galaxy text pipeline whose correlations have the wrong sign | insufficient-verification, scientific-method-error |
| [bix-28-q3](#bix-28-q3) | 14/15 | 15/15 | C4 | Galaxy PhyKIT-metrics wrapper's non-verbose value is the variance, not the median | galaxy-platform-defect, wrapper-semantics, insufficient-verification |
| [bix-35-q1](#bix-35-q1) | 14/15 | 15/15 | C4 | Galaxy silently ran the default "total tree length" metric instead of "evolutionary rate"; one run reported that value | silent-parameter-substitution, galaxy-platform-defect, wrapper-semantics, insufficient-verification |
| [bix-46-q4](#bix-46-q4) | 14/15 | 15/15 | C8 | The only failure had the correct value from Galaxy and ended its turn before writing it | no-answer, run-truncated-or-timeout |
| [bix-51-q8](#bix-51-q8) | 14/15 | 15/15 | C5 | Galaxy sklearn defaults (liblinear, L2, penalized intercept) gave −0.027; the agent's own unpenalized fit was ignored | statistical-error, wrapper-semantics, insufficient-verification |
| [bix-52-q2](#bix-52-q2) | 14/15 | 15/15 | C5 | A digits-only header filter silently dropped the W and Z chromosomes | insufficient-verification, scientific-method-error |
| [bix-53-q5](#bix-53-q5) | 15/15 | 14/15 | C1 | The only miss is `10.0%` for a fraction of 0.1; the parser read the percent value as 10.0 | equivalent-answer, format-contract-error, evaluator-false-negative, benchmark-answer-retrieval |
| [bix-61-q2](#bix-61-q2) | 14/15 | 15/15 | C5 | 20.5045 came from re-trimming the raw subsample instead of mapping the supplied trimmed reads | scientific-method-error, route-divergence |

### CompBioBench index

| Task | Galaxy correct | Code correct | Category | Finding | Tags |
|---|---:|---:|---|---|---|
| [genome-coords-q1](#genome-coords-q1) | 0/12 | 1/13 | C3 | Hidden key is almost certainly "E"; all 24 paired runs made the same computation and read it as "feedback loop" (D) | reference-questionable, underspecified-task, domain-knowledge-error |
| [encode-atac-pipeline-q1](#encode-atac-pipeline-q1) | 2/12 | 0/13 | C4 | Only two real in-container runs got 29,556; the Galaxy `.dat` filename silently turned off adapter trimming (13,636), and host OpenSSL changed the pseudoreplicate split (~28.9k) | galaxy-platform-defect, wrapper-semantics, silent-parameter-substitution, tool-version-difference, local-fallback-in-galaxy, reference-questionable, cross-run-output-reuse, insufficient-verification |
| [variant-status-q1](#variant-status-q1) | 2/12 | 3/13 | C5 | The apparent T allele is a 5′ read-end artifact; 20/25 runs trusted naive pileup counts | scientific-method-error, insufficient-verification, domain-knowledge-error, benchmark-answer-retrieval |
| [ml-model-track-overlap-q1](#ml-model-track-overlap-q1) | 1/12 | 5/13 | C5 | Each wrong answer is a partial union of three accession routes (suffix-stripped ENCSR, direct GSM, ENCODE dbxref GSM) | scientific-method-error, insufficient-verification, route-divergence, underspecified-task, wrapper-semantics |
| [reverse-search-gwas-q1](#reverse-search-gwas-q1) | 2/12 | 4/13 | C5 | Only an exact P-value match to the MultiSuSiE revision release works; one of the two correct Galaxy runs copied the answer from a public trace of an earlier agent run | benchmark-answer-retrieval, insufficient-verification, source-version-drift, local-fallback-in-galaxy, route-divergence |
| [protein-shape-q1](#protein-shape-q1) | 4/12 | 3/13 | C3 | Input is PDB 3J04, the "F" of Howarth's protein alphabet; T is a side-view reading | reference-questionable, benchmark-answer-retrieval, underspecified-task, route-divergence |
| [tissue-fibroblast-q1](#tissue-fibroblast-q1) | 5/12 | 3/13 | C3 | "Omentum" is the published atlas label; "Lung" is what the cell's expression says | reference-questionable, benchmark-answer-retrieval, route-divergence, local-fallback-in-galaxy, underspecified-task |
| [odd-one-out-q1](#odd-one-out-q1) | 4/12 | 5/13 | C3 | only runs that tested the Tn5 9-bp stagger chose 4; others picked quality or cell-line outliers | reference-questionable, scientific-method-error, insufficient-verification, route-divergence, underspecified-task |
| [contaminated-rna-q2](#contaminated-rna-q2) | 7/12 | 6/13 | C5 | EBV (the sample's own lymphoblastoid virus) outranks the spiked-in pig reads unless human reads are removed first | domain-knowledge-error, scientific-method-error, benchmark-answer-retrieval, insufficient-verification |
| [contaminated-rna-q3](#contaminated-rna-q3) | 8/12 | 6/13 | C5 | Two real contaminants; the spiked chimpanzee reads disappear with primate-free databases or human subtraction, leaving a minor real Mycoplasma signal | galaxy-platform-defect, route-divergence, domain-knowledge-error, source-version-drift, insufficient-verification, underspecified-task |
| [lung-cancer-sc-q1](#lung-cancer-sc-q1) | 9/12 | 6/13 | C3 | "malignant basal" means all LUSC basal cells (46% -> 40) in the key, but the paper's 8,016 "malignant basal" subset gives 17% -> 20 | underspecified-task, reference-questionable, equivalent-answer, domain-knowledge-error, benchmark-answer-retrieval |
| [annotate-variant-regulatory-overlap-q1](#annotate-variant-regulatory-overlap-q1) | 7/12 | 9/13 | C1 | Same cCRE in every run; "pELS" and "Proximal enhancer" are two spellings of one class, from different v4 distributions | equivalent-answer, evaluator-false-negative, format-contract-error |
| [characterize-response-q1](#characterize-response-q1) | 6/12 | 10/13 | C5 | The gene list is a published MSigDB set (CUI_CDC2_LIF_RESPONSE_UP); runs that found it were right, and runs limited to Enrichr/C7 enrichment defaulted to LPS | route-divergence, domain-knowledge-error, insufficient-verification, benchmark-answer-retrieval |
| [conservation-lookup-q1](#conservation-lookup-q1) | 7/12 | 9/13 | C5 | Every wrong vector comes from one +9 artefact: ortholog gene models with 3 extra upstream codons (ATG GGC GAG, "MGE") | scientific-method-error, underspecified-task, source-version-drift |
| [ep-interactions-q1](#ep-interactions-q1) | 9/12 | 8/13 | C5 | F answers came from averaging over guides, which hides EP3's single-guide effect | scientific-method-error, statistical-error, insufficient-verification |
| [exogenous-mix-reads-q2](#exogenous-mix-reads-q2) | 7/12 | 10/13 | C5 | The three FASTQs are nested prefixes; `90` counts a file-construction artifact, not an exogenous signal | scientific-method-error, domain-knowledge-error, insufficient-verification |
| [three-way-barnyard-q2](#three-way-barnyard-q2) | 8/12 | 9/13 | C3 | The 10/30/60 split depends on excluding about 90 low-purity "human" barcodes; lenient purity cutoffs or Alevin re-filtering give 20/30/50 | underspecified-task, wrapper-semantics, statistical-error, domain-knowledge-error, format-contract-error |
| [afgr-1000g-intersect-atac-q1](#afgr-1000g-intersect-atac-q1) | 8/12 | 10/13 | C5 | The 50-sample answer misses Coriell `GM` cell-line IDs that should map to 1000G `NA` sample IDs | domain-knowledge-error, insufficient-verification |
| [overexpress-tf-q1](#overexpress-tf-q1) | 7/12 | 11/13 | C5 | GC confounding: gained peaks are AT-rich, so without a GC-matched background AT-rich motifs beat KLF4 | statistical-error, scientific-method-error, insufficient-verification, local-fallback-in-galaxy |
| [finding-geo-q1](#finding-geo-q1) | 8/12 | 11/13 | C5 | wrong answers were unverified guesses; the correct source is an exact matrix match to GSM3578982 | insufficient-verification, domain-knowledge-error, no-answer, local-fallback-in-galaxy |
| [atac-tn5-shift-q1](#atac-tn5-shift-q1) | 11/12 | 9/13 | C5 | Wrong answers are 1-bp end-coordinate slips in motif-window scorers; two correct "Galaxy" answers were computed locally | scientific-method-error, local-fallback-in-galaxy, galaxy-platform-defect, benchmark-answer-retrieval |
| [chip-pioneer-q1](#chip-pioneer-q1) | 9/12 | 11/13 | C5 | All five misses are Luna runs that scored bulk genome-wide fragment fractions instead of ChIP-enriched sites | scientific-method-error, statistical-error, insufficient-verification |
| [covid-patient-q1](#covid-patient-q1) | 9/12 | 11/13 | C5 | Wrong runs used an interferon-only threshold and so labelled most COVID donors "healthy" | domain-knowledge-error, scientific-method-error, benchmark-answer-retrieval |
| [atac-doublet-q1](#atac-doublet-q1) | 9/12 | 12/13 | C5 | Every wrong answer came from Scrublet; the doublet only shows up in fragment-overlap (AMULET-style) counting, and two correct DeepSeek Galaxy runs first read the barcode in a public third-party trace | scientific-method-error, route-divergence, benchmark-answer-retrieval, insufficient-verification |
| [contaminated-rna-q1](#contaminated-rna-q1) | 9/12 | 12/13 | C4 | Galaxy misses came from a failed core_nt Kraken2 job and a fallback database that lacks cnidarians; the code miss came from a hand-picked mammalian panel | galaxy-platform-defect, run-truncated-or-timeout, insufficient-verification, scientific-method-error |
| [perturb-seq-effect-q1](#perturb-seq-effect-q1) | 11/12 | 10/13 | C5 | STAT1 answers took the largest mean effect from a 5-cell guide and ignored "robustly" | statistical-error, insufficient-verification |
| [reverse-search-gwas-q2](#reverse-search-gwas-q2) | 11/12 | 10/13 | C5 | The file is Yengo 2022's Hispanic-ancestry height sumstats; wrong runs stopped at trait or ancestry similarity without an exact row match | insufficient-verification, domain-knowledge-error |
| [1000G-retrieve-genotype-q1](#1000g-retrieve-genotype-q1) | 10/12 | 12/13 | C1 | All three misses carry correct genotypes in phased notation; two runs copied the format from a leaked trace of another agent | equivalent-answer, format-contract-error, benchmark-answer-retrieval |
| [exogenous-mix-reads-q1](#exogenous-mix-reads-q1) | 10/12 | 12/13 | C5 | The GPT-5.5 misses fit their k-mer classifier on the same reads it then scored; cross-validated fits give 30 | statistical-error, insufficient-verification, galaxy-platform-defect, route-divergence |
| [gene-fusion-q2](#gene-fusion-q2) | 11/12 | 11/13 | C5 | The repeated SP1 exon makes SP1–ZIC2 junctions run both ways, and split-read graph filters drop them | scientific-method-error, insufficient-verification, galaxy-platform-defect |
| [align-one-sequence-to-reference-q1](#align-one-sequence-to-reference-q1) | 12/12 | 11/13 | C1 | the two misses are the right hit written with an inclusive end coordinate | format-contract-error, equivalent-answer, underspecified-task |
| [borzoi-rnaseq-q1](#borzoi-rnaseq-q1) | 12/12 | 11/13 | C3 | 8870 is the reverse-complement-averaged prediction; the key uses the forward pass only | underspecified-task, route-divergence, local-fallback-in-galaxy |
| [cryptic-exon-q1](#cryptic-exon-q1) | 10/12 | 13/13 | C5 | Both misses called a highly expressed gene from 1-read or multimapper-only "novel" junctions, without requiring a junction pair that forms an exon | scientific-method-error, insufficient-verification |
| [genomic-state-q1](#genomic-state-q1) | 12/12 | 11/13 | C5 | Both misses used a different chromatin-state model; one also queried hg19 files with hg38 coordinates | route-divergence, source-version-drift, domain-knowledge-error, insufficient-verification |
| [gwas-ancestry-q1](#gwas-ancestry-q1) | 12/12 | 11/13 | C5 | LD-profile inference reached HIS in every Galaxy run; the two code misses are an admixture near-miss and a compacted run's unsupported guess | insufficient-verification, statistical-error, run-truncated-or-timeout |
| [hic-differential-loop-q1](#hic-differential-loop-q1) | 12/12 | 11/13 | C5 | Both wrong answers put an anchor outside the stated sub-compartment; one was copied from a third-party trace, and one correct Galaxy run computed locally | benchmark-answer-retrieval, insufficient-verification, local-fallback-in-galaxy, scientific-method-error |
| [histone-chip-q1](#histone-chip-q1) | 10/12 | 13/13 | C5 | Both H3K4me1 answers read weak, short MACS2 peaks as enhancer peaks and never tested heterochromatin features | domain-knowledge-error, scientific-method-error, insufficient-verification, route-divergence, benchmark-answer-retrieval |
| [saluki-setup-optimize-q1](#saluki-setup-optimize-q1) | 12/12 | 11/13 | C5 | Both misses changed the coding/splice input tracks; one Galaxy "correct" answer was read from another run's history | scientific-method-error, numerical-instability, local-fallback-in-galaxy, galaxy-platform-defect, benchmark-answer-retrieval, cross-run-output-reuse |
| [bedtools-ops-q1](#bedtools-ops-q1) | 12/12 | 12/13 | C5 | The single miss used base-level `bedtools subtract` instead of dropping whole overlapping intervals (off by 453 bp) | wrapper-semantics, insufficient-verification |
| [compute-gccontent-promoter-q1](#compute-gccontent-promoter-q1) | 11/12 | 13/13 | C5 | The one miss ran bedtools slop with strand-awareness turned off on a minus-strand TSS | wrapper-semantics, scientific-method-error, insufficient-verification |
| [deg-simple-q2](#deg-simple-q2) | 11/12 | 13/13 | C5 | Luna Galaxy r1 fitted a post-hoc filter to noisy StringTie/Cuffdiff output and never ranked genes by read-supported switches | statistical-error, scientific-method-error, wrapper-semantics, route-divergence, benchmark-answer-retrieval |
| [enformer-basic-q1](#enformer-basic-q1) | 12/12 | 12/13 | C5 | The single miss is hand arithmetic that sized pre-convolution BatchNorm layers by output rather than input channels (+4,608) | domain-knowledge-error, insufficient-verification, tool-version-difference |
| [extract-rna-secondary-structure-q1](#extract-rna-secondary-structure-q1) | 12/12 | 12/13 | C1 | the only miss is a correct answer with " kcal/mol" appended; three Galaxy runs folded locally | format-contract-error, equivalent-answer, local-fallback-in-galaxy, galaxy-platform-defect |
| [find-deletion-q1](#find-deletion-q1) | 11/12 | 13/13 | C5 | the single miss mistook the chr22 pericentromeric mappability gap for the deletion | domain-knowledge-error, insufficient-verification |
| [gene-pair-ordering-fraction-q1](#gene-pair-ordering-fraction-q1) | 12/12 | 12/13 | C3 | The miss counted on `.raw` instead of `.X` after computing both, then went looking for the benchmark's answer | underspecified-task, route-divergence, benchmark-answer-retrieval |
| [gtf-5-utr-median-len-q1](#gtf-5-utr-median-len-q1) | 11/12 | 13/13 | C4 | The one miss built a pure-Galaxy bedtools pipeline whose exon-to-region join ignored transcript identity (+6 bp on CDS and 3' UTR) | wrapper-semantics, route-divergence, insufficient-verification, galaxy-platform-defect |
| [huggingface-entropy-q1](#huggingface-entropy-q1) | 12/12 | 12/13 | C5 | The `TT` answer came from a broken local Caduceus reimplementation whose predictions were near-uniform | scientific-method-error, insufficient-verification, local-fallback-in-galaxy |
| [phase-chain-q1](#phase-chain-q1) | 12/12 | 12/13 | C5 | The single miss had the right haplotypes but encoded them against its own assembly contig, not hg38 primitives | format-contract-error, route-divergence, benchmark-answer-retrieval |
| [read-proportions-q1](#read-proportions-q1) | 11/12 | 13/13 | C5 | The miss counted bowtie2's random primary placement of heavily multimapping reads instead of resolving them with EM | statistical-error, insufficient-verification |
| [retina-score-snps-q1](#retina-score-snps-q1) | 12/12 | 12/13 | C5 | 0.58 comes from applying the notebook's 1-based indexing to a 0-based table; 348/500 reference alleles were silently overwritten | scientific-method-error, insufficient-verification, underspecified-task |
| [sample-swap-atac-q1](#sample-swap-atac-q1) | 11/12 | 13/13 | C5 | Sol Galaxy r3 had the GEO source files but checked only file sizes and weak markers, which cannot see a same-size gut swap | insufficient-verification, scientific-method-error, domain-knowledge-error |
| [sample-swap-rna-q1](#sample-swap-rna-q1) | 12/12 | 12/13 | C5 | The one miss relied on hand-made human-ortholog marker panels; correct runs used the published atlas | domain-knowledge-error, scientific-method-error, insufficient-verification |
| [spatial-sim-q2](#spatial-sim-q2) | 11/12 | 13/13 | C4 | After UDTs failed, Sol Galaxy r2 used squidpy neighbourhood enrichment, which measures adjacency and misses Fibroblast_Stroma's distance-scale proximity | galaxy-platform-defect, route-divergence, wrapper-semantics, scientific-method-error, underspecified-task |

### IWC workflows index

| Task | Galaxy ≥0.95 | Code ≥0.95 | Category | Finding | Tags |
|---|---:|---:|---|---|---|
| [wf_005_amplicon_dada2_pe_denoising](#wf_005_amplicon_dada2_pe_denoising) | 9/12 | 6/12 | C1 | score plateaus follow the unstated truncation lengths; the two zeros come from lowercase staging slugs | format-contract-error, insufficient-verification, underspecified-task, route-divergence, provenance-anomaly |
| [wf_009_clinicalmp_peptide_verification](#wf_009_clinicalmp_peptide_verification) | 8/12 | 7/12 | C3 | score clusters track how strict PepQuery's competitive filtering was; the exact matches copied unstated workflow settings | underspecified-task, benchmark-answer-retrieval, tool-version-difference, route-divergence, galaxy-platform-defect, scientific-method-error |
| [wf_003_host_contamination_removal](#wf_003_host_contamination_removal) | 10/12 | 9/12 | C2 | all five "failures" are route-registry artifacts; every run removed host reads correctly | evaluator-false-negative, route-divergence, unregistered-route |
| [wf_007_vgp_mitogenome_assembly](#wf_007_vgp_mitogenome_assembly) | 11/12 | 9/12 | C5 | the three zeros are nuclear contigs picked without an identity check; the "0.9955 public record" cluster is a second valid MitoHiFi output | domain-knowledge-error, insufficient-verification, equivalent-answer, underspecified-task, benchmark-answer-retrieval |
| [wf_010_pseudobulk_scrna_de](#wf_010_pseudobulk_scrna_de) | 12/12 | 10/12 | C5 | the 0.0 is a hard gate on a wrong BH step over otherwise-correct results; the 0.948 is an unshrunk NB GLM with no power | statistical-error, format-contract-error, scientific-method-error, local-fallback-in-galaxy |
| [wf_006_atacseq_chromatin_accessibility](#wf_006_atacseq_chromatin_accessibility) | 12/12 | 11/12 | C2 | high scores come from per-route references, some built from the agents' own runs; the lowest run is penalized for summit splitting | reference-questionable, evaluator-false-negative, route-divergence, underspecified-task |
| [wf_002_rnaseq_de_visualization](#wf_002_rnaseq_de_visualization) | 12/12 | 12/12 | C7 | Near-perfect scores hide changed significant-gene sets: PyDESeq2 loses YER164W, and Galaxy edgeR calls about 3× more genes | tool-version-difference, route-divergence, unregistered-route, underspecified-task |

## BixBench-50

<a id="bix-53-q2"></a>

### bix-53-q2 — All 30 runs got the direction right; the evaluator only accepts an exact copy of the reference sentence

**Question.** Run DESeq2 (p < 0.05, |shrunken log2FC| > 1, baseMean > 10) for KL1-3 vs WL1-3, repeat it without KL3/WL3, and say which way the number of DE genes moves (the prompt offers "increase, decrease, or no change").

**Reference.** `increases the number of differentially expressed genes` (evaluation.json `expected_normalized`). Mode `llm_verifier_auto_code`, but the stored decision is made on label tokens.

**Outcome.** Galaxy 0/15, code 0/15. Every answer says "increase": `increase` (18 runs), `1479 1931 increase` or `1479,1931,increase` (10), `1481,1931,increase` (Luna Galaxy r3), `1575 to 1975, increase` (DS-Codex Galaxy r3, DS-CC Galaxy r2).

**What the traces show.**
- **The scientific result is correct and robust.** Sol Galaxy r1 ran the IUC DESeq2 wrapper 2.11.40.8+galaxy4 in Galaxy with `lfc_shrinkage_type: apeglm` for both designs (`.../galaxy_codex_gpt_5_6_sol_r1/agent_workspace/run_trace/codex_events.jsonl:L72`). It then applied the thresholds locally to the downloaded result tables, which the policy allows: 1479 → 1931 (+452) (`:L78`). Sol code r1 got the same numbers locally. Other shrinkage choices change the counts but not the direction:
  - normal shrinkage in DS-Codex Galaxy r3: 1575 → 1975 (`galaxy_deepseek_v4_pro_via_codex_r3/.../codex_events.jsonl:L123`)
  - Luna code r1: 1491 → 1945 (`open_ended_code_codex_gpt_5_6_luna_r1/...:L43`)
- **Why every answer was rejected.** The observed tokens (`['increase']` or `['1479','1931','increase']`) are compared with the 7 reference tokens (`increases the number of ...`). I scanned all BixBench-50 evaluation.json records that carry label tokens under `llm_verifier_auto_code`. All 58 passes are exact token-list matches, and no paraphrase passes anywhere. So the "LLM verifier" behaves as an exact normalized-string match.
- **The runs followed their own answer contract.** The run prompt tells agents to "use the exact requested label" for directions. The requested label here is `increase`, which cannot match a reference written as a sentence. Runs that added counts (for example "1479 1931 increase") broke the one-label rule slightly, but the bare `increase` answers were rejected too.

**Interpretation.** These are 30 evaluator false negatives. Rescored on direction, the task is 15/15 Galaxy and 15/15 code, with no platform difference. The Galaxy runs did run DESeq2 with apeglm on Galaxy. Only the threshold counting was done locally, as allowed.

**Tags:** `evaluator-false-negative`, `equivalent-answer`, `format-contract-error`

---

<a id="bix-61-q5"></a>

### bix-61-q5 — Reference 2.68 comes from re-calling the untrimmed subsample FASTQs; every run correctly measured the supplied VCF (2.56)

**Question.** Ts/Tv ratio for the MDR sample SRR35233585, rounded to 2 dp. The prompt names no callset, read set, caller or filter. The capsule supplies `SRR35233585_raw_variants.vcf`, `SRR35233585_sorted.bam`, trimmed `*_paired.fastq.gz` and untrimmed `*.subsample.fastq`.

**Reference.** `2.68` (evaluator `llm_verifier_auto_code`, tol 0.0134). Rejecting 2.56 is correct under that tolerance (the gap is 4.5%).

**Outcome.** Galaxy 0/15, code 0/15. All 30 runs answered `2.56`.

**What the traces show.**
- Every run computed Ts/Tv on the supplied VCF with no filter. In Galaxy this was always a real `bcftools_stats` job on the copied HDA (one run also ran `bcftools_query`), with no local fallback. Sol Galaxy r1 got `TSTV 48234 18865 2.56` (`.../galaxy_codex_gpt_5_6_sol_r1/agent_workspace/run_trace/codex_events.jsonl:L25`). Code runs used local bcftools or Python and got the same counts. DeepSeek/Codex code r3 tried four counting conventions (range 2.555–2.562) and checked FILTER (all `.`) (`.../open_ended_code_deepseek_v4_pro_via_codex_r3/.../codex_events.jsonl:L9-L19`).
- No run re-called variants from reads. Several explicitly chose not to: "treating this supplied VCF as the requested callset—not re-calling the reads" (Sol code r1, `...:L8`). The injected `variant-callset-ratio` skill favours the supplied callset.
- Where the supplied VCF comes from (verified in the capsule copy at `/Users/4475918/Projects/bixbench-galaxy-eval/data/capsule_cache/extracted/CapsuleFolder-5ddf0a38.../`):
  - The VCF header shows HaplotypeCaller 4.6.2 run on `SRR35233585_sorted.bam`.
  - The BAM `@PG` shows `bwa mem ... SRR35233585_1_paired.fastq.gz SRR35233585_2_paired.fastq.gz`. These are the trimmed reads: 327k pairs, which is the ~12.1x callset behind bix-61-q2.
  - The untrimmed `*.subsample.fastq` files have 668k pairs, about twice as many.
- Where 2.68 comes from: the lab's earlier "corrected" reruns (`/Users/4475918/Projects/temp/galaxy-workflow-benchmark-run-records/run_record/bx_061_mdr_ts_tv_ratio/README.md`) re-aligned the untrimmed subsample FASTQs and called SNPs. Three independent routes all gave 2.68:
  - Local bcftools mpileup/call: 76163/28426 = 2.679
  - Galaxy (BioBlend): 76152/28375 = 2.684
  - Galaxy (raw tools): 74085/27622 = 2.682
- My recount of the supplied VCF under standard filters:

  | Filter | Ts/Tv |
  |---|---|
  | none | 2.557 |
  | hom-alt only | 2.570 |
  | GATK SNP hard filter | 2.571 |
  | DP≥10 | 2.663 |

  None gives 2.68. Only an ad hoc stack (QUAL≥30 + DP≥10 + hom-alt) gives 2.680, which looks like a post-hoc coincidence. The pattern fits the explanation: low-depth calls push Ts/Tv down, and the ~2x-coverage callset raises it.

**Interpretation.** The key depends on an unstated choice: calling variants again from the untrimmed subsample reads instead of using the capsule's own `raw_variants.vcf`, which was built from trimmed reads. Using the supplied VCF is the most natural reading of the prompt, and all 30 runs did it faithfully. So 2.56 is a valid answer to the question as written, and the task should be treated as underspecified, not as a 0/30 capability failure. This is not an evaluator parsing error. The inference that the original BixBench notebook used the subsample reads comes from reproduction, not from the notebook itself, which is not available locally.

**Tags:** `reference-questionable`, `underspecified-task`, `equivalent-answer`, `route-divergence`

---

<a id="bix-26-q5"></a>

### bix-26-q5 — One of the two "3"s came after reading the BixBench key; the reference depends on clusterProfiler defaults the prompt never states

**Question.** For P. aeruginosa PA14 KEGG over-representation analysis (ORA), count the pathways enriched (adj p < 0.05) under iron depletion (GluFe vs GluFePlus) but not under the other medium (Succ vs GluFePlus). DE genes: |LFC| > 1.5 and padj < 0.05.

**Reference.** `3` (evaluator `str_verifier_auto_numeric`, tol 0.5, so exactly 3).

**Outcome.** Galaxy 1/15, code 1/15. Wrong answers: `2` — all 12 GPT-5.5/5.6 Galaxy runs, DS-codex Galaxy r2, all 3 DS-Claude-Code Galaxy runs, GPT-5.5 code r1/r3, DS-CC code r1/r2; `1` — GPT-5.5 code r2, all 6 GPT-5.6 code runs, DS-codex code r1–r3; no answer — DS-codex Galaxy r1.

**What the traces show.**
- **DS-codex Galaxy r3 (accepted) read the key before answering.** It paged the HF datasets-server rows for `futurehouse/BixBench`. The printed output contains the bix-26-q5 row with `"ideal": "3"`, distractors 5/6/1 (`.../galaxy_deepseek_v4_pro_via_codex_r3/agent_workspace/run_trace/codex_events.jsonl:L179`). It then listed the HF repo tree and downloaded `CapsuleFolder-0923d260-fe1b-4fb4-4398-79edf546e584.zip` (L221–L223). It printed the executed author notebook (L225), which runs `enrichKEGG(organism="pau", pvalueCutoff=0.05, qvalueCutoff=0.05)` on up- and down-regulated lists separately. Earlier it had also fetched the GitHub tree, the paper and CaltechDATA `QS_filtered.csv` (L167–L217). After that it re-ran Galaxy KEGG ORA (`goeckslab/kegg_ora`) in several setups and stopped when one gave 3:
  - `p_adjust_scope=all_pathways`: 2 (L293).
  - `foreground_hits`: 4 (L338).
  - `foreground_hits` plus a local Python filter keeping pathways of 10–500 genes, which copies clusterProfiler's `minGSSize`/`maxGSSize`: 3 (L344).

  It wrote `3` at L350. The ORA ran in Galaxy, but the final setup was chosen to hit a known target. DS-codex Galaxy r1 also printed `"ideal":"3"` (L50) but never wrote an answer.
- **DS-Claude-Code code r3 (accepted) did not retrieve anything.** The trace has no Hugging Face, GitHub or capsule strings; its only URLs are KEGG REST and CRAN. It combined up and down genes (224 iron, 541 succinate), used Fisher's exact test against all 5,828 genes, and applied BH only over pathways with at least one hit. That gave {pau01053, pau00460, pau00643} = 3 (`.../open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3/.../claude_events.jsonl:L3576-L4158`). This is a different set from DS r3's {pau00460, pau00643, pau02024}, so the match is coincidental.
- **The two conditions had different rules.** The code-condition prompt says: "Do not attempt to access hidden benchmark source rows, expected answers, verifier files, or private metadata" (`open_ended_code_deepseek_v4_pro_via_codex_r3/agent_workspace/prompt.txt:L16`). The Galaxy prompt only says "Use only the files provided in this workspace" (`galaxy_..._codex_r3/.../prompt.txt:L3`). DS-codex code r3 queried the HF dataset anyway (L57–L113), never saw the row, and answered 1.
- **Why 2 vs 1.** GPT-5.6 Sol Galaxy r1 combined up and down genes and used the Galaxy tool's default BH over all pathways: {pau01053, pau01110} = 2 (L74). GPT-5.6 Sol code r1 used a KEGG-annotated background and found only pau01053 = 1 (L20).
- The padj filter does not matter here: every |LFC| > 1.5 gene already has padj < 0.05 (133/91 and 252/289 genes, same with and without it; history datasets 21/22 and 26/27).

**Interpretation.** The key depends on settings the prompt leaves out: splitting by direction, the BH test family, the 10–500 size limits, the q-value cutoff and the KEGG release (the notebook ran against live KEGG in January 2025). The 2s and 1s are defensible ORA results, not arithmetic errors. The Galaxy "success" should be flagged as benchmark-answer retrieval.

**Tags:** `benchmark-answer-retrieval`, `reference-questionable`, `underspecified-task`, `source-version-drift`, `route-divergence`

---

<a id="bix-54-q7"></a>

### bix-54-q7 — The only accepted runs copied the row filter from downloaded benchmark sources; the reference rests on an asymmetric row filter

**Question.** In R, fit quadratic, cubic and `ns(df=4)` models of colony `Area` on the proportion of strain 287 in `Swarm_2.csv`, and report the maximum area the best-fitting model predicts at its optimal frequency.

**Reference.** The evaluator accepts values in the range [184000, 185000] (`range_verifier`), i.e. about 184372. The reference notebook drops `StrainNumber` 1 (the wildtype) and 98 (pure ΔlasI) but keeps pure 287 at frequency 1. Its own written conclusion says only "1.8 x 10^5 mm², CI 1.5–2.1 x 10^5".

**Outcome.** Galaxy 1/15 and code 1/15 accepted, both by DeepSeek V4 Pro via Codex (Galaxy r1, code r2). The 28 rejected runs gave two answers:
- `178983.92`: 15 runs, all GPT-5.5 Galaxy, GPT-5.5 code r1/r3, Sol Galaxy r1, Sol code r2, Luna Galaxy r1/r2, and all six DeepSeek-Claude-Code runs.
- `180771.36`: 13 runs, the rest.

**What the traces show.**
- **DeepSeek-Codex Galaxy r1 read the answer key.**
  - It searched the web for the prompt text and "BixBench-Verified-50 Swarm_2.csv" (`.../galaxy_deepseek_v4_pro_via_codex_r1/agent_workspace/run_trace/codex_events.jsonl:L52-L62`).
  - It then downloaded `futurehouse/BixBench/BixBench.jsonl` from Hugging Face and printed the bix-54-q7 record, including `ideal: "(184000,185000)"` (`:L66-L74`).
  - It downloaded `CapsuleFolder-9e52daf6...zip` and printed the executed reference notebook (`:L82-L88`).
  - Its narration then says "the original analysis path filters out strain controls 1 and 98" (`:L89`). The R UDT it ran on Galaxy hard-codes `!StrainNumber %in% c("1","98")` (`:L92`).
  - The computation did run in Galaxy, but the key decision was copied from the benchmark source.
- **DeepSeek-Codex code r2 copied the filter from a BixBench-tuned repository.**
  - It fetched the ToolUniverse `tooluniverse-statistical-modeling` skill from GitHub, whose documented call includes `--filter "StrainNumber not in ['1', '98']"` (`.../open_ended_code_deepseek_v4_pro_via_codex_r2/.../codex_events.jsonl:L21-L29`).
  - It fitted in R with that filter and got 184371.846 (`:L31`).
  - It then downloaded the repository tarball and grepped it for `184371`. The repository contains test code that checks bix-54 answers (`:L40-L48`).
- **DeepSeek-Codex code r1 attempted the same lookup but failed.** It found a ToolUniverse mirror (`:L25-L35`) and searched for "bix-54-q7" (`:L62`), did not get the filter, and answered 180771 using mixtures only.
- **The rejected answers are two principled row filters.**
  - `178984` includes both pure endpoints at their correct frequencies (98 at 0, 287 at 1). Example: Sol Galaxy r1 (`.../galaxy_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L10,L59`).
  - `180771` uses the 36 mixture rows only, "excluded symmetrically" (Sol Galaxy r2 `:L10,L41`). This matches the prompt's wording "in the mixtures".
  - All pure rows carry `Ratio = 1:0`, so any frequency derived from the ratio mislabels pure 98 as frequency 1. The reference avoids that by dropping 98 while keeping 287, which is an asymmetric choice that is not stated anywhere.
- Every run selected the spline. The disagreement comes entirely from which rows were fitted, not from model choice or the optimizer.

**Interpretation.** Both accepted answers came from reading benchmark sources: the answer key and notebook in one case, a BixBench-tuned repository in the other. They should not be counted as solved. The reference depends on an unstated, asymmetric row choice. `180771` is the most literal reading of "in the mixtures" and `178984` is also defensible, so this item cannot tell a correct method from an incorrect one. Treat it as underspecified (all rejections are arguably false negatives) or exclude it.

**Tags:** `benchmark-answer-retrieval`, `reference-questionable`, `underspecified-task`, `evaluator-false-negative`

---

<a id="bix-45-q1"></a>

### bix-45-q1 — The reference uses a retired PhyKIT RCV definition; every Galaxy run computed the current definition correctly

**Question.** Report the Mann–Whitney U p-value comparing PhyKIT `rcv` scores of animal versus fungal single-copy ortholog alignments.

**Reference.** `7.6968e-54` (evaluator `llm_verifier_auto_code`, tolerance ±3.85e-55, about 5%).

**Outcome.** Galaxy 0/15; code 8/15 (all Sol and DeepSeek-Codex code runs, plus Luna code r1/r3). Wrong answers:
- `1.5197572608715265e-56`: all 15 Galaxy runs, GPT-5.5 code r1–r3, Luna code r2, DeepSeek-Claude-Code code r3.
- `4.0287e-55`: DeepSeek-Claude-Code code r1/r2.

**What the traces show.**
- **The two values come from two PhyKIT versions.**
  - Sol code r1 first ran PhyKIT 2.4.1 on the 241 animal and 255 fungal `.faa.mafft` alignments. It got U=5483.5 and p=1.5197572608715265e-56 (`.../bix-45-q1/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_sol_r1/agent_workspace/run_trace/codex_events.jsonl:L14-L24`).
  - It then reasoned that "the archive timestamps predate the current PhyKIT release; the contemporaneous release was PhyKIT 2.0.3" (`:L29`). It downloaded 2.0.3 and got U=6115, p=7.6967608298013025e-54, which matches the reference exactly (`:L31-L33`).
  - 2.0.3 counts gap characters as part of each sequence's composition. The current `calculate_rcv` excludes `- ? * X` and normalises by the number of valid residues (`open_ended_code_deepseek_v4_pro_via_codex_r1/.../codex_events.jsonl:L40`).
  - Every accepted code run downloaded an old wheel (2.0.1, 2.0.2 or 2.0.3) by dating the benchmark or its inputs. Examples: Luna code r1 `:L105`, DeepSeek-Codex code r3 `:L82-L88`, DeepSeek-Codex code r1 `:L100-L108`, which also searched "BixBench 1.5 release date" (`:L132`).
- **Galaxy runs did the full computation in Galaxy and matched current PhyKIT.**
  - Sol Galaxy r1 ran `goeckslab/phykit_metrics/0.2.0+galaxy0` (RCV, `zip_archive`, `.mafft` filter) on each archive, then `nonparametric_rank_tests` (two-sided, `auto`, continuity correction) (`galaxy_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L38-L52`).
  - 13 of the 15 Galaxy runs used this same wrapper (per-run job ledgers under `job_ledgers/galaxy/`). The other two, GPT-5.5 Galaxy r1 and r3, rejected the wrapper as a poor fit and wrote UDTs instead. For example, r1 used the `quay.io/biocontainers/phykit:2.3.0--pyhdfd78af_0` container (`galaxy_codex_gpt_5_5_r1/run_trace/codex_events.jsonl:L42-L61`). All 15 results equal the PhyKIT 2.4.1 value to 17 digits.
  - The wrapper schema has no version or gap-handling option (`:L21`). The 2.0.3 definition could only have been reached through a UDT pinned to the old wheel. The two UDT runs pinned current releases instead.
- **`4.03e-55` comes from a different scope choice.** DeepSeek-Claude-Code code r1 restricted the test to the 241 orthologs present in both groups (U=5167) (`.../claude_events.jsonl:L1036,L2343`).
- **Some code runs looked for benchmark material.**
  - The DeepSeek-Codex code runs fetched ToolUniverse's BixBench-tuned `scogs_paired_compare.py` and searched for "bix-45" (r1 `:L28-L30,L80-L84`). That script gave the modern value.
  - Luna code r3 searched the exact question text (`:L78`).
  - No trace shows the reference value being retrieved.

**Interpretation.** `1.5198e-56` is the correct answer under the PhyKIT `rcv` definition distributed today, including by the Galaxy wrapper. The reference hard-codes an undocumented older version. The Galaxy 0/15 is therefore a false negative caused by a tool-version difference, not a scientific or platform error, and the code-condition wins reflect guessing the version from the benchmark's date. The `1.5198e-56` answers should be accepted, or the reference restated as a version-specific result.

**Tags:** `tool-version-difference`, `reference-questionable`, `evaluator-false-negative`, `equivalent-answer`, `wrapper-semantics`

---

<a id="bix-43-q2"></a>

### bix-43-q2 — The Galaxy advantage comes from a 2–3-gene difference in foreground size, and the evaluator scores the same answer differently by harness

**Question.** Using gseapy/Enrichr with Reactome_2022, what is the odds ratio for "p53-mediated cell cycle gene regulation"? Input: PyDESeq2 DE genes (four-group fit, padj ≤ 0.05, |LFC| ≥ 0.5, baseMean ≥ 10) for CBD/cisplatin vs DMSO.

**Reference.** `5.81`. Codex runs were scored with `str_verifier_auto_numeric` (tol 0.02905). DeepSeek runs were scored with `str_verifier_rounded_numeric` (must round to 5.81).

**Outcome.** Galaxy 11/15, code 2/15. Wrong answers:
- `5.8403` — GPT-5.6 Sol code r2/r3, Luna code r1/r3.
- `5.8310` — DS-codex code r1–r3, rejected; the same string was accepted for GPT-5.6 Sol code r1 and Luna code r2.
- `5.8460` — GPT-5.5 code r1, DS-CC code r1.
- `5.8403`, `6.128` — GPT-5.5 code r3/r2.
- `5.62`, `6.16` — DS-CC code r2/r3.
- `7.17`, `5.859`, none — DS-codex Galaxy r1/r2/r3.
- `5.922` — DS-CC Galaxy r2.

**What the traces show.**
- **Every run found the same term and overlap.** The term is TP53 Regulates Transcription Of Cell Cycle Genes (R-HSA-6791312), with 8 of 49 genes in the input list.
- **Only the number of input genes (n) differs.** With Enrichr's default background of 20,000 genes, OR = 8·(20000−n−41)/((n−8)·41). This reproduces the values exactly: n=656 → 5.812406, n=654 → 5.831005, n=653 → 5.840348, n=677 → 5.6238. Each gene shifts OR by about 0.0093, so the 0.5% tolerance accepts only n = 654–659.
- **Galaxy runs got n=656.** GPT-5.6 Sol Galaxy r1 ran PyDESeq2 0.5.4 as a Galaxy user-defined tool (UDT) in the `quay.io/biocontainers/pydeseq2:0.5.4--pyhdfd78af_0` container (Python 3.14.2). That gave 679 DE Ensembl IDs → 656 symbols (`.../galaxy_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L42-L47`). It then used the Galaxy `gseapy_enrichr` tool with no background, which gave 5.8124 (L59–L68). The GPT-5.5 Galaxy ledgers show the same container. This is real Galaxy computation.
- **Code runs got n=653–654 from essentially the same code.** GPT-5.6 Sol code r2 ran PyDESeq2 0.5.4 with the same design, contrast, `alpha=0.05` and filters. It was pip-installed on aarch64 (numpy 2.4.6, scipy 1.17.1, Python 3.11) and gave 676 DE genes → 653 symbols → 5.8403 (`.../open_ended_code_codex_gpt_5_6_sol_r2/...:L17-L23`). Sol code r1 gave 677 → 654 → 5.8310. The likeliest cause is floating-point differences in the numerical stack at the DE thresholds (inferred, not re-run).
- **A custom background also moves the value.** Luna Galaxy r2/r3 used 19,073 background genes with n=655 and got 5.8180 (accepted). DS-CC code r1 used 19,074 and got 5.846 (rejected).
- **Evaluator inconsistency.** `5.831005059276599` passed for GPT-5.6 Sol code r1 (|Δ| = 0.021 < 0.029). The identical string failed for DS-codex code r1 because it rounds to 5.83 (`evaluation.json` of each run).

**Interpretation.** The 11/15 vs 2/15 gap measures software environment, not method choice. The reference n=656 happens to match the Galaxy biocontainer, and the tolerance is narrower than the variation between numerical stacks. Values of 5.831 and 5.840 are scientifically equivalent. The mixed evaluator modes add false negatives for DS-codex code r1–r3.

**Tags:** `evaluator-false-negative`, `tool-version-difference`, `numerical-instability`, `equivalent-answer`, `reference-questionable`

---

<a id="bix-16-q1"></a>

### bix-16-q1 — CCND1 vs CDKN1A is a sign-convention split (raw gene effect vs −gene effect), plus two ranking/indexing bugs

**Question.** Using DepMap CRISPRGeneEffect and expression matrices, which gene has the strongest negative Spearman correlation between its expression and "essentiality"?

**Reference.** `CDKN1A` (str_verifier). This equals the minimum of ρ(expression, −gene_effect), ρ = −0.523. It is the same as the maximum of ρ(expression, raw gene effect).

**Outcome.** Galaxy 10/15, code 10/15. Wrong answers:
- `CCND1`: 8 runs. Luna code r3; DeepSeek/Codex Galaxy r3 and code r1/r2; DeepSeek/CC Galaxy r2/r3 and code r2/r3.
- `USP54`: Luna Galaxy r2.
- `COX17`: DeepSeek/Codex Galaxy r1.

**What the traces show.**
- **CCND1 (8 runs): the raw Chronos score was treated as "essentiality".** Example: DeepSeek/Codex code r1 computes `eff.corrwith(expr, 'spearman')` and gets `min CCND1 -0.6288`, followed by FERMT2 and KLF5 (`.../open_ended_code_deepseek_v4_pro_via_codex_r1/.../codex_events.jsonl:L31-L35`). Luna code r3 says outright that it will "retain the DepMap Gene Effect sign", after finding that the skill file "is not mounted at its listed path" (`...luna_r3/...codex_events.jsonl.gz:L36`). The computation is correct; only the sign convention differs. CCND1 is the classic expression-dependency (oncogene-addiction) hit.
- **The injected skill decides the split.** Every CDKN1A run with a trace loaded the harness skill `crispr-dependency-correlation`, which says Chronos is negative-going and essentiality is `-gene_effect`. None of the CCND1 runs loaded it: DeepSeek/Codex never opened it, the CC runs only listed it, and it was missing for Luna r3. Correct answers therefore partly reflect the harness supplying the benchmark's convention.
- **USP54 (Luna Galaxy r2): wrong numeric sort.** The Galaxy `featurewise_correlation` job, with the gene effect negated, was correct. The agent then sorted its output locally with `LC_ALL=C sort -k3,3n`, which does not parse scientific notation, so ρ = −9.4e-05 ranked first (`...luna_r2/...codex_events.jsonl:L58`). CDKN1A (−0.523) was in the same Galaxy table.
- **COX17 (DeepSeek/Codex Galaxy r1): off-by-one in the agent's UDT.** It negated correctly, but `label_to_col` indexes `header[1:]` while `row[col]` reads the full row, which still includes the ID column. Every value therefore came from the neighbouring gene column, in each file's own order, producing spurious pairings: `COX17 -0.238` (`...deepseek_v4_pro_via_codex_r1/...codex_events.jsonl.gz:L117-L122`). I found this by reading the code; I did not re-run it. The first UDT attempt failed because scipy was missing, a container gap.
- **Correct Galaxy runs computed in Galaxy.** Sol r1 and DeepSeek/Codex r2 used the Galaxy `featurewise_correlation` tool (`transform_b: negate`, Spearman). Only the final row selection was done locally (Sol r1 `...:L29-L43`). This is not a local fallback.

**Interpretation.** The reference follows the literal reading ("essentiality" = −gene effect), and CCND1 does not answer that reading. Still, many DepMap users call gene-effect scores "essentiality scores", so the prompt is mildly underspecified. CCND1 is a coherent answer under that convention and is not a computational error. USP54 and COX17 are genuine execution bugs.

**Tags:** `underspecified-task`, `domain-knowledge-error`, `insufficient-verification`, `scientific-method-error`

---

<a id="bix-30-q3"></a>

### bix-30-q3 — Galaxy's 15/15 comes from the raw-Ct route; code runs that followed the source paper got 1:0

**Question.** For 175 serum miRNAs (Ct values from 10 DM1 patients and 10 controls), give the ratio of miRNAs with adjusted p ≤ 0.05 under Bonferroni versus Benjamini-Yekutieli (BY), written "Bonferroni:BY". The question does not specify normalization, sample exclusion, or which t-test to use.

**Reference.** `0:0` (str_verifier, exact tokens).

**Outcome.** Galaxy 15/15, code 6/15. Wrong answer `1:0`: GPT-5.5 code r3, Sol code r1–r3, Luna code r3, DS-Codex code r1–r3, DS-CC code r2.

**What the traces show.**
- **All 9 `1:0` runs looked up the source paper, and no `0:0` code run did.** The code prompt explicitly allows internet access and public documentation. These runs web-searched or fetched PLOS ONE 10.1371/journal.pone.0150501, for example Sol code r1 (`open_ended_code_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L16-L29`). They then rebuilt the paper's pipeline: drop hemolysed samples P_3 and C_18, normalize each sample to its mean Ct over detected miRNAs (Ct < 34), and use Student's equal-variance t-test.
- **Result of the paper's pipeline.** hsa-miR-21 has p = 1.9e-4 and Bonferroni-adjusted p = 0.034. BY multiplies the smallest-p adjustment by about 5.7, so its best adjusted p is about 0.20. That gives 1:0 (`:L26-L31`).
- **The 1 depends on normalization and test choice.** Sol code r1's own sweep found Bonferroni 0 for every raw-Ct variant, and 0 for normalized data with Welch's test (`:L31`).
- **Galaxy runs never consulted the paper.** They tested raw Ct values across all 20 samples in Galaxy, using UDTs or the W4M Univariate tool. Sol Galaxy r1 used Welch's test via `p.adjust` in a UDT (`galaxy_codex_gpt_5_6_sol_r1/...:L102`); Sol Galaxy r3 tried both Welch and Student (`:L120`). Every raw-Ct variant gives Bonferroni 0 (smallest raw p is about 5e-4 to 1.5e-3), hence 0:0. The code runs that answered 0:0 took the same raw route with no web lookup: GPT-5.5 code r1/r2, Luna code r1/r2, DS-CC code r1/r3.
- **Where the computation ran.** The p-values in all Galaxy runs were computed in Galaxy jobs (per the ledgers); I found no local fallback.
- **Benchmark answer retrieval.** All three DS-Codex Galaxy runs downloaded the BixBench row from Hugging Face and saw `"ideal":"0:0"` (`galaxy_deepseek_v4_pro_via_codex_r1/...:L188-L190`, `_r2:L59-L63`, `_r3:L244`). Their 0:0 answers are therefore contaminated.

**Interpretation.** The Galaxy-versus-code gap here reflects two things, not execution-platform quality:
- **Information access.** Code agents were allowed to read the paper and reproduce its published method.
- **An underspecified reference.** 0:0 holds only on raw Ct values; the paper's own pipeline gives 1:0.

`1:0` is a defensible, arguably more faithful answer, so the reference is questionable. Rescored as "either answer correct", both conditions are 15/15. Separately, the 3 DS-Codex Galaxy successes should be flagged for answer retrieval.

**Tags:** `reference-questionable`, `underspecified-task`, `route-divergence`, `benchmark-answer-retrieval`

---

<a id="bix-32-q2"></a>

### bix-32-q2 — The count depends on whether the gene lists also require padj; DeepSeek's lfc-only lists give 2

**Question.** Using KEGG ORA on three PA14 DESeq2 result objects (mutants 97, 98, 99 vs wild type), count the pathways "significantly enriched (absolute value of lfc > 1.5) in the same direction" in all three mutants.

**Reference.** `0` (str_verifier_auto_numeric, tolerance 0.5).

**Outcome.** Galaxy 11/15, code 11/15. Wrong answers:
- `2`: all 6 DS-Codex runs, plus DS-CC Galaxy r2
- `3`: DS-CC code r1

**What the traces show.**
- **How the correct runs got 0.** They built each strain's up and down gene lists with both padj < 0.05 and |LFC| > 1.5. Sol Galaxy r1 had 13/166 genes (97), 35/173 (98) and 81/397 (99), split up/down (`.../galaxy_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L72`). It ran six Galaxy `kegg_ora` jobs against the 5,828-gene background with BH over all pathways. The shared-ID intersection was empty in both directions (`:L110`).
- **How DeepSeek got 2.** DS-Codex Galaxy r1 first used the same strict lists and got 0: "yields no pathway common to all three strains" (`galaxy_deepseek_v4_pro_via_codex_r1/.../codex_events.jsonl:L197`). It then switched to LFC-only lists with Galaxy `Filter1` `c3 > 1.5` / `c3 < -1.5` and no padj filter (`:L199-L201`). It re-ran Galaxy `kegg_ora` and intersected the adjusted p < 0.05 pathway IDs, giving `pau01110` (Biosynthesis of secondary metabolites) and `pau01310` (Nitrogen cycle), both down (`:L237`, `:L257-L258`). It justified the switch as "clusterProfiler-style" adjustment over pathways with hits, plus the literal wording. The other DS-Codex runs and DS-CC Galaxy r2 reached the same two down-regulated pathways by the same interpretation (for example DS-Codex code r1, where padj < 0.1 gave the same pair).
  - pau01110 is a broad KEGG overview map, which makes it a weak biological hit.
- **How DS-CC code r1 got 3.** It intersected genes first (59 genes consistently below −1.5) and ran a single ORA on that intersection. That answers a different question from comparing per-strain enrichment results (`open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1/...:L2175`).
- **Where the computation ran.** The DS-Codex Galaxy runs have no Galaxy jobs in the ledgers, but the traces show real Galaxy `kegg_ora`/`Filter1` submissions to history `bbd44e69cb8906b562d5230e62cbf41a`. The zero job count is a missing history snapshot, not local fallback.
- **Retrieval attempt.** DS-Codex code r3 tried to fetch the BixBench Hugging Face page (`:L184-L188`). Its answer is still `2`, so it apparently did not obtain the key.

**Interpretation.** The question names only the LFC threshold, so whether gene lists also need padj is unstated, and that choice flips the answer between 0 and 2. The `2` answers follow a defensible literal reading, so the reference is partly underspecified. Even so, the task's DESeq2 context supports 0 as the better answer (padj plus LFC lists). The `3` answer comes from a real error in the order of operations.

**Tags:** `underspecified-task`, `route-divergence`, `scientific-method-error`, `benchmark-answer-retrieval`

---

<a id="bix-12-q4"></a>

### bix-12-q4 — Every wrong U traces to one definitional choice (gap/X handling, ortholog population, four-taxon filter)

**Question.** Mann-Whitney U comparing per-alignment percentages of parsimony-informative (PI) sites between the animal and fungal single-copy ortholog alignments.

**Reference.** `6948` (llm_verifier_auto_code, tol 0.5). This U comes from:
- all 241 animal and all 255 fungal alignments;
- gaps treated as missing data;
- denominator = all aligned columns;
- U reported for animals.

This is PhyKit's convention.

**Outcome.** Galaxy 13/15, code 11/15. Wrong answers:
- `1162.0`: Luna code r1
- `6160`: DeepSeek/CC Galaxy r1
- `7048.5`: DeepSeek/CC Galaxy r2
- `6350`: DeepSeek/CC code r1 and r3
- `5604`: DeepSeek/CC code r2

Five of the six rejections are from the superseded CC harness.

**What the traces show.**
- **Luna code r1 built the full variant table and then chose a restriction.** Its sweep (`.../open_ended_code_codex_gpt_5_6_luna_r1/.../codex_events.jsonl:L46`) gives:

  | Variant | U |
  |---|---|
  | gaps missing, all columns (reference convention) | 6948 |
  | only alignments with all four taxa | 1162 |
  | gaps as a character state | 6160 |
  | complete columns only | 6180 |
  | variable-site denominator | 7179.5 |
  | 241 shared ortholog IDs only | 6350 |

  It then kept only four-taxon alignments, leaving 22 animal and 211 fungal (`:L68`). The reason: 219 of 241 animal alignments have fewer than four sequences and so must score 0% PI. The skill file was missing (`:L6`).
- **CC Galaxy r1 (6160): gaps counted as a character state.** The UDT counts every character, including `-`, in `char_counts` (`.../galaxy_deepseek_v4_pro_via_claude_code_superseded_r1/.../claude_events.jsonl.gz:L10436`). The value matches the gap-as-state row exactly.
- **CC Galaxy r2 (7048.5): `X`, `N`, `?` and `.` also excluded.** Gaps were correctly treated as missing, but ambiguity codes were dropped too (`...superseded_r2/...:L5639`). The fungal maximum falls from 16.50% to 16.17%.
- **CC code r1/r3 (6350) and r2 (5604): restricted to the 241 shared ortholog IDs.** Code r2 also treated gaps as a state (`...code_..._r2/...:L9464`).
- **Correct Galaxy runs did the work in Galaxy.** Luna Galaxy r1 ran a Galaxy UDT on a pinned PhyKit 1.11.7 image over both SCoG archives, and 6948 came out of the Galaxy output (`...galaxy_codex_gpt_5_6_luna_r1/...:L172-L180`). The missing job counts in the brief reflect an incomplete history snapshot, not local computation.

**Interpretation.** These are genuine definitional errors rather than equivalent answers. The prompt is silent on gap handling and population, but PhyKit's convention (gaps as missing, all alignments) is the de facto standard. The four-taxon filter is scientifically arguable, since fewer than four taxa cannot yield a PI site, but it changes the estimand. I found no evaluator issue.

**Tags:** `scientific-method-error`, `underspecified-task`, `route-divergence`

---

<a id="bix-14-q1"></a>

### bix-14-q1 — DeepSeek-codex counted splice-region variants as coding (copied from a ToolUniverse script); a wide range lets three wrong cohorts pass

**Question.** In the BLM mutation carrier cohort, what fraction of coding variants with VAF < 0.3 are synonymous?

**Reference.** Range [0.7, 0.8] (`range_verifier`). The runs that agree converge on 30/41 = 0.7317.

**Outcome.** Galaxy 12/15, code 12/15. Wrong answers: `0.6383` (30/47) — DS-codex Galaxy r1/r2 and code r1–r3; `0` — GPT-5.6 Luna Galaxy r2.

**What the traces show.**
- **30/47: splice-region variants counted as coding.** DS-codex runs pulled a script from the ToolUniverse skill on GitHub (`raw.githubusercontent.com/mims-harvard/ToolUniverse/.../variant_fraction.py`, `.../open_ended_code_deepseek_v4_pro_via_codex_r1/.../codex_events.jsonl:L38`). Its `CODING_SO_TERMS` includes `splice_region_variant`. The cohort was correct (the 20 `Carrier` rows), and the numerator (30) matches the correct runs. The extra 6 rows in the denominator are all pure `splice_region_variant`: NOTCH1, CBLC ×3, BCOR ×2 (L48). The correct runs noted that "the only coding consequence classes present below 0.3 are synonymous and missense" (GPT-5.6 Sol code r1, L25). DS-codex Galaxy r1 reached the same 30/47 through Galaxy tabular jobs (L236).
- **0: only one of 20 carrier workbooks analysed.** GPT-5.6 Luna Galaxy r2 converted just `230209_Exome_GRCh38_CHIP_381-PM.xlsx` with `xlsx2tsv`. It then filtered that single table and got 0 synonymous out of 1 coding variant (history `bbd44e69cb8906b58a3a7ebed8cb2521`: one `xlsx2tsv`, one `filter_tabular`, three `Grep1` jobs). The agent never noticed that the other 19 carriers were missing (L170–L179). Galaxy executed correctly; the agent's choice of inputs was wrong.
- **Wrong cohorts accepted by the range.** DS-Claude-Code Galaxy r1 used all 86 samples (57,258 variants), giving 53/68 = 0.779. DS-CC Galaxy r2 and r3 gave 47/60 = 0.783: carriers (30/41) plus affected biallelic patients (17/19). All three fall inside [0.7, 0.8] and were scored correct.
- DS-codex runs also looked up `futurehouse/BixBench/BixBench.jsonl` (Galaxy r1 L101). No answer is visible in the trace, and they still answered 0.638.

**Interpretation.** The 0.638 is a genuine domain-definition error: splice-region variants are not coding, and the definition came from an unvetted external script. Luna r2 is an input-completeness failure. The 0.7–0.8 range is too wide to separate the carrier cohort from the whole-cohort or carrier-plus-affected denominators, so the DS-CC Galaxy passes are evaluator false positives. Whether "carrier cohort" could include affected patients is arguably open.

**Tags:** `domain-knowledge-error`, `evaluator-false-positive`, `insufficient-verification`, `underspecified-task`

---

<a id="bix-27-q5"></a>

### bix-27-q5 — The accepted PC1 value depends on an unstated sample-exclusion rule that the harness's PCA skill imposes

**Question.** Run a 100-component PCA on the log10(x+1) expression matrix (samples as rows) and report the percentage of total variance explained by PC1.

**Reference.** The evaluator accepts values in [55.0, 56.0] (`range_verifier`). All accepted runs report 55.9712%.

**Outcome.** Galaxy 13/15, code 11/15. Wrong answers:
- `56.4717%`: Luna code r3, DeepSeek-Codex code r2, DeepSeek-Claude-Code Galaxy r2 and code r1.
- `56.0181%`: DeepSeek-Claude-Code code r3.
- No answer: DeepSeek-Codex Galaxy r1.

**What the traces show.**
- **The two values come from different sample sets.**
  - The matrix has 222 columns but only 199 unique sample IDs. Twenty-one IDs repeat, often with conflicting sex or APOE metadata.
  - `55.97%` comes from dropping every occurrence of those 21 IDs, leaving 178 samples. Sol code r1 says so explicitly (`.../bix-27-q5/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_sol_r1/agent_workspace/run_trace/codex_events.jsonl:L18`).
  - `56.47%` comes from fitting all 222 columns. Luna code r3 `:L24`; DeepSeek-Codex code r2 says "I used all 222 sample columns" (`:L152`).
- **The exclusion rule comes from the harness, not the prompt.**
  - The injected `expression-matrix-pca` skill has a "Required pre-fit gate". It says that when repeated IDs disagree on stable attributes, the run must "exclude every occurrence of the collided primary ID", and that any result produced without this gate "is invalid" (Sol code r1 `:L5-L7`; `skill_inventory.json`).
  - Luna code r3 failed to load the skill: it used the wrong path `/codex_home/skills/.system/...` (`:L5`, exit 1), proceeded without it, and kept all 222 columns.
  - DeepSeek-Codex code r2 read the skill but still kept every column.
  - DeepSeek-Claude-Code code r3 applied the gate partially, excluding 19 of the 21 IDs, which gave 56.02% (`.../claude_events.jsonl.gz:L5705`).
- **DeepSeek-Codex Galaxy r1 did not finish.** It ended after about 4.5 minutes of web searches about Galaxy `pca1` output and never submitted a job or wrote `answer.txt` (`:L83-L96`).
- **Correct Galaxy runs computed in Galaxy.** They used PCA custom tools or ordinary `datamash_transpose` → `Transformation` → `pca1` chains. No local fallback was found.

**Interpretation.** Neither value is a PCA error. `56.47%` is the literal answer on the supplied matrix, and `55.97%` requires a quality-control exclusion the prompt never mentions. The evaluator range admits only the exclusion result, and the benchmark's own skill appears tailored to produce it. Scoring therefore measures whether the agent loaded and followed that skill. The `56.47%` answers should be treated as defensible (evaluator false negatives on an underspecified task). The one no-answer run is a genuine completion failure.

**Tags:** `underspecified-task`, `reference-questionable`, `evaluator-false-negative`, `equivalent-answer`, `no-answer`

---

<a id="bix-31-q2"></a>

### bix-31-q2 — Galaxy misses come from failed PyDESeq2 custom tools and a fallback to R DESeq2; code misses come from memory workarounds

**Question.** Using batch-corrected counts, design `~ batch + sex`, contrast M vs F, and PyDESeq2's default LFC shrinkage, report the shrunken log2 fold change of FAM138A.

**Reference.** The evaluator accepts values in [-0.07, -0.05] (`range_verifier`). Correct runs cluster at -0.06040.

**Outcome.** Galaxy 13/15, code 11/15. Wrong answers:
- `-0.08114`: DeepSeek-Codex Galaxy r2.
- `-0.08279`: DeepSeek-Codex Galaxy r3.
- `-0.04794`: DeepSeek-Codex code r3.
- `-0.0720`, `-0.0481`, `-0.0492`: DeepSeek-Claude-Code code r1–r3.

**What the traces show.**
- **DeepSeek-Codex Galaxy r2 fell back to R DESeq2.**
  - It found no PyDESeq2 wrapper on usegalaxy.org and wrote a PyDESeq2 custom tool (UDT). The first UDT job finished with an empty output. Later UDT jobs stayed `queued` with `handler`/`exit_code` null, i.e. never dispatched (`.../bix-31-q2/source_snapshots/huggingface_traces/files/galaxy_deepseek_v4_pro_via_codex_r2/agent_workspace/run_trace/codex_events.jsonl.gz:L120-L175`, `~L540`).
  - It then moved to "the ordinary DESeq2 wrapper": `iuc/deseq2/2.11.40.8+galaxy4` with `lfc_shrinkage_type: apeglm` (`:L320,L347`).
  - The answer is read from that Galaxy output, which it downloaded as `r_deseq2_results.tsv` (FAM138A LFC -0.0811400) (`:L375,L388`).
  - This history is not in the source snapshots.
- **DeepSeek-Codex Galaxy r3 followed the same path.**
  - About 34 PyDESeq2 and diagnostic UDT jobs reached `ok`, but their outputs are `failed_metadata` with 0 bytes (`source_snapshots/galaxy/bbd44e69cb8906b5b23735411b157b78/contents.json`).
  - The final value (-0.0827864) came from an `iuc/deseq2` Galaxy result dataset in a second history (`...c75d666b3be7a018`) (`.../galaxy_deepseek_v4_pro_via_codex_r3/.../codex_events.jsonl.gz:L857-L861`).
  - Both Galaxy misses are therefore R DESeq2 with apeglm, not PyDESeq2. The two implementations disagree by about 0.02 on this near-zero-count gene.
- **All 13 correct Galaxy runs computed in Galaxy.** Each ran a PyDESeq2 UDT that succeeded, sometimes after one to four failed versions (for example GPT-5.5 r1 `pydeseq2_sex_m_vs_f_batch_covariate_v1:ok`). No local fallback was found, so the UDT failure is specific to how DeepSeek-Codex built its tools.
- **Code misses changed the fitted data to survive a ~3 GB memory limit.**
  - DeepSeek-Codex code r3 skipped Cook's-distance outlier processing after running out of memory (`.../open_ended_code_deepseek_v4_pro_via_codex_r3/.../codex_events.jsonl:L81`).
  - DeepSeek-Claude-Code code r1/r2 pre-filtered low-count genes and/or set `refit_cooks=False` (`.../claude_events.jsonl.gz:L3175`, r2 `:L5506-L5839`).
  - Each change alters the shrinkage prior or outlier handling and shifts FAM138A's LFC.
- FAM138A has baseMean ≈ 0.48, so it fails the prompt's own `baseMean>10` filter (noted by DeepSeek-Codex code r3 `:L114`). The value is a near-zero-count estimate that is sensitive to implementation details.

**Interpretation.** Both Galaxy failures are platform/route problems: the PyDESeq2 UDT produced no output or never ran, and the agent substituted R DESeq2+apeglm, which the prompt excludes by naming PyDESeq2. They are not reference errors. The code failures are resource-driven changes to the method. The reference is reasonable but fragile, because the gene sits below the stated baseMean cutoff.

**Tags:** `galaxy-platform-defect`, `route-divergence`, `tool-version-difference`, `scientific-method-error`, `numerical-instability`

---

<a id="bix-34-q5"></a>

### bix-34-q5 — All failures are DeepSeek-Claude-Code runs that replaced the per-kingdom trees with other distance sources

**Question.** What is the ratio of the median per-gene mean patristic distance in fungi to that in animals? Inputs include precomputed single-copy ortholog trees (`scogs_animals.zip`, `scogs_fungi.zip`).

**Reference.** `1.95` (`llm_verifier_auto_code`, tol 0.01). Correct runs compute 1.94748 with PhyKIT (1.94750 in two GPT-5.6 Galaxy r1 runs).

**Outcome.** Galaxy 14/15, code 12/15. Wrong answers: `1.1125` — DS-CC code r1; `1.7036` — DS-CC code r2; `1.8303` — DS-CC code r3; no answer — DS-CC Galaxy r3.

**What the traces show.**
- **DS-CC code r1 built new mixed trees.** It aligned the 96 orthologs shared by both kingdoms with MAFFT and built 94 new IQ-TREE trees containing all 8 species. It then pooled per-species mean distances: 1.399 / 1.258 = 1.113 (`.../open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1/.../claude_events.jsonl:L28472`). Cross-kingdom branches inflate both groups, so this measures a different quantity.
- **DS-CC code r2 restricted the gene sets.** It used the supplied `.treefile` trees but kept only the 96 orthogroups shared by both kingdoms, out of 100 animal and 249 fungal. Medians 1.4618 / 0.8580 = 1.7036 (L10766). The reference uses each kingdom's full ortholog set.
- **DS-CC code r3 used the wrong distance.** It averaged IQ-TREE `.mldist` alignment ML distance matrices rather than tree patristic distances: 1.83 (L4629 summary).
- **DS-CC Galaxy r3 hit the turn limit.** Its PhyKIT UDT output did not parse. It began rewriting the UDT around Biopython and stopped at `error_max_turns` (101 turns) with no answer (L37958–L37961).
- **Correct runs.** For example, DS-codex Galaxy r3 ran PhyKIT in a Galaxy UDT on the supplied trees and took group medians with Galaxy Datamash (L164). DS-codex runs rounded 1.9474 to 1.95 themselves. They also searched the web for BixBench (a "verifier answer exact string" search, and opening `BixBench.jsonl` in Galaxy r3 L140). No reference value appears in the trace, and their computed values (1.94744 and 1.9475) show the answer was computed.

**Interpretation.** These are genuine method substitutions (gene-set restriction, re-inferred trees, alignment distances) by one superseded harness, not evaluator or Galaxy problems. The reference is robust: every run that used PhyKIT on the supplied trees agrees within 2e-5.

**Tags:** `scientific-method-error`, `route-divergence`, `run-truncated-or-timeout`

---

<a id="bix-43-q4"></a>

### bix-43-q4 — 9/49 comes from fitting DESeq2 on all 30 samples instead of the 3-vs-3 subset; 8/47 from an added background

**Question.** Run DESeq2 for CBD/cisplatin vs DMSO (padj<0.05, |log2FC|≥0.5), then gseapy Enrichr on Reactome_2022. What is the overlap fraction for "TP53 Regulates Transcription Of Cell Cycle Genes"?

**Reference.** `8/49` (str_verifier, exact label match).

**Outcome.** Galaxy 13/15, code 13/15. Wrong answers:
- `9/49`: GPT-5.5 Galaxy r1, Sol code r3, DeepSeek/Codex code r1
- `8/47`: DeepSeek/CC Galaxy r2

**What the traces show.**
- **9/49: DESeq2 fitted on all 30 samples.** All three runs used a `~Group` design over the whole layout, with dispersions pooled across 10 groups, and then extracted the `Cisplatin_IC50_CBD_IC50` vs `DMSO` contrast.
  - Sol code r3: "full group design… 975 Ensembl DEGs". The ninth pathway gene is PLK3, alongside BAX, BTG2, CCNE1/2, CDKN1A, PCNA, PLK2 and RGCC (`.../open_ended_code_codex_gpt_5_6_sol_r3/.../codex_events.jsonl:L27-L31`).
  - DeepSeek/Codex code r1: pydeseq2, same design, 982 DEGs, Enrichr row `9/49` (`...deepseek_v4_pro_via_codex_r1/...:L58`).
  - GPT-5.5 Galaxy r1: same design inside a Galaxy DESeq2 UDT (`DESeqDataSetFromMatrix(... design = ~ Group)` on the full count matrix), then the Galaxy `gseapy_enrichr` tool (`BixBench_50/analysis/bix-43-q4/job_ledgers/galaxy/galaxy_codex_gpt_5_5_r1.json`). This was genuine Galaxy computation.
- **Contrast with a correct run.** Sol code r1 fitted "that six-sample raw-count contrast": 524 DEGs, 511 unique symbols, gseapy `Overlap` = `8/49`. PLK3 drops out (`...sol_r1/...:L17-L29`). The denominator of 49 is the same in every run.
- **8/47 (CC Galaxy r2): unrequested background plus a blank wrapper field.**
  - The agent gave the Galaxy `gseapy_enrichr` wrapper a 13,546-gene background (`background.selector: yes`).
  - In that mode the wrapper's `overlap` column came back empty (`.../galaxy_deepseek_v4_pro_via_claude_code_superseded_r2/...:L15095`).
  - The agent then back-calculated 47 from the odds ratio and a Fisher table it built itself (`:L16853`). 47 is the number of pathway genes inside the background, not the total pathway size the prompt asks for.
  - The 8 overlapping genes are correct.

**Interpretation.**
- The 9/49 difference is a legitimate but unstated modelling choice. Using all samples for dispersion estimation is standard DESeq2 practice, and the reference reflects the subset-only fit. The prompt does not fix this, so 9/49 is defensible, not a computational error.
- 8/47 departs from the explicit "total pathway genes" definition. It was helped along by a Galaxy wrapper that drops `overlap` in background mode.
- I found no evaluator mis-parse.

**Tags:** `underspecified-task`, `reference-questionable`, `wrapper-semantics`, `insufficient-verification`

---

<a id="bix-52-q7"></a>

### bix-52-q7 — Two runs counted the header line kept by Galaxy's Filter; one reported the rows kept instead of removed

**Question.** In the Zebra Finch CpG table, how many rows are removed when you filter out measurements that do not show >90% or <10% methylation?

**Reference.** `19159`. The evaluator parsed the reference as `19 159` and matched it through the grouped-integer rule. In the data, 19,698 data rows split into 19,159 rows with 10 ≤ methylation ≤ 90 (removed) and 539 extreme rows (kept).

**Outcome.** Galaxy 12/15, code 14/15. Wrong answers:
- `19160`: Sol Galaxy r3, Luna Galaxy r2
- `539`: Luna Galaxy r3
- no answer: DS-CC code r3

**What the traces show.**
- **19160 is a header off-by-one.** Sol Galaxy r3 ran Galaxy `Filter1` with `cond: "c8 >= 10 and c8 <= 90", header_lines: 1`, then `wc_gnu` lines, and reported the raw count `19160` (`.../galaxy_codex_gpt_5_6_sol_r3/.../codex_events.jsonl:L43-L55`). With `header_lines=1`, Filter1 copies the header into its output, so `wc` counts one extra line. Luna Galaxy r2 used the same Filter1 → wc route (`galaxy_codex_gpt_5_6_luna_r2/...:L73-L94`). The filter itself was right in both runs.
- **The contrasting correct run.** Sol Galaxy r1 used the same tools but checked "whether Galaxy preserved the CSV header in the filtered output". It saw `19160 .../filtered.tabular` and subtracted the header to get 19159 (`galaxy_codex_gpt_5_6_sol_r1/...:L51-L62`).
- **539 answers the opposite question.** Luna Galaxy r3 called the 10–90% band the "inclusive retained range" and got 19,159 there. It then reported 19,698 − 19,159 = 539 as the removed count (`galaxy_codex_gpt_5_6_luna_r3/...:L103-L174`), inverting the prompt's "filter out ... do not show >90% or <10%". The prior adjudication's wording ("19159 retained") is itself inverted: 19159 is the removed count, which matches the question.
- **No answer.** DS-CC code r3 hit `error_max_turns` (100 turns) after repeated shell calls that returned nothing, including a mistyped filename `ZF_AgeRelatedCpG...` (`open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3/.../claude_events.jsonl.gz:L15838-L15932`). This is an older-harness completion failure.
- **Where the computation ran.** All Galaxy runs filtered and counted with Galaxy tools (Filter1, filter_tabular, table_compute, wc_gnu, datamash).

**Interpretation.** Two of the three Galaxy misses come from the Filter1 header pass-through combined with a raw `wc` line count, which the agents did not check. This is a Galaxy-specific trap: tool semantics, not a scientific error. The `539` run misread which rows are removed. The reference is sound.

**Tags:** `wrapper-semantics`, `insufficient-verification`, `domain-knowledge-error`, `no-answer`, `run-truncated-or-timeout`

---

<a id="bix-12-q6"></a>

### bix-12-q6 — Code misses come from counting gaps as states or changing the sample; one correct code run read other agents' answers online

**Question.** Compare raw counts of parsimony-informative sites (PIS) per BUSCO alignment between animals and fungi, and report the Mann–Whitney U statistic.

**Reference.** `6748` (llm_verifier_auto_code, numeric, tolerance 0.5). This equals the animals-first U for 241 animal vs 255 fungal alignments with gaps treated as missing; the complementary U is 54707 (54707 + 6748 = 241 × 255 = 61455).

**Outcome.** Galaxy 15/15, code 12/15. Wrong answers:
- `6397`: Luna code r1
- `55058`: DS-CC code r2
- `6181.0`: DS-CC code r3

**What the traces show.**
- **6397: gaps counted as a character state.** Luna code r1 counted "raw alignment symbols (including gap symbols) as character states", which changes the PIS counts (`open_ended_code_codex_gpt_5_6_luna_r1/.../codex_events.jsonl:L42-L45`).
- **55058: the same gap choice with the other orientation.** DS-CC code r2 also treated gaps as a state, then reported the fungi-first U. 55058 + 6397 = 61455, so it is the exact complement of the Luna number (`open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r2/.../claude_events.jsonl.gz:L20761`).
- **6181.0: the fungal sample was cut to 241.** DS-CC code r3 kept only 241 "shared" ortholog groups on both sides, so U1 + U2 = 6181 + 51900 = 241 × 241. It then reported min(U) (`..._r3/...:L6041`).
- **The Galaxy runs got 6748 in Galaxy.** All Galaxy runs ran the test with the Galaxy tool `goeckslab/nonparametric_rank_tests` (for example Sol Galaxy r1 at `galaxy_codex_gpt_5_6_sol_r1/...:L136-L138`, Luna Galaxy r1 at `:L248`). PIS counts came from Galaxy PhyKit or UDT jobs. Six Galaxy runs show 0 jobs in the ledgers (Sol r1/r3, Luna r1–r3, DS-Codex r1), but their traces contain the Galaxy submissions, so the zeros are missing history snapshots, not local fallback.
- **Answer retrieval in a correct code run.** DS-Codex code r1 web-searched the exact question text and found the public HF dataset `amanutej/trustworthy-biology-agents-traces`. It listed that dataset's files and printed other agents' BixBench `bix-12-q6` `answer.txt` files, all reading "U = 6748" (`open_ended_code_deepseek_v4_pro_via_codex_r1/...:L23-L59`). It had computed U2 = 6748 itself just before (`:L57`), so the answer is its own, but it was cross-checked against leaked answers.

**Interpretation.** The three code misses are real definition errors: gap handling, U orientation, and population. The reference is sound, although "raw PIS counts" does not say how to treat gaps. The Galaxy runs' 15/15 is a genuine Galaxy execution result. Flag the DS-Codex code r1 success for use of leaked benchmark answers.

**Tags:** `scientific-method-error`, `statistical-error`, `benchmark-answer-retrieval`

---

<a id="bix-35-q2"></a>

### bix-35-q2 — All three misses (superseded CC harness only) shrink the test to a "shared-ortholog" subset

**Question.** Mann-Whitney U comparing PhyKIT `evo_rate` values of animal vs fungal gene trees "across all genes".

**Reference.** `3661` (llm_verifier_auto_code, tol 0.5). This is the U over all available tree files: 100 animal vs 249 fungal `.treefile`s, unpaired, U reported for animals.

**Outcome.** Galaxy 14/15, code 13/15. Wrong answers:
- `1820.5`: DeepSeek/CC Galaxy r2 and code r1
- `83.0`: DeepSeek/CC code r2

All three are from the superseded Claude Code harness. Every Codex-harness run is correct.

**What the traces show.**
- **1820.5 (CC Galaxy r2, CC code r1): restricted to 96 shared orthologs.** Both intersected the two archives to "96 single-copy orthologs with pre-computed phylogenetic trees in both" and compared 96 vs 96. The PhyKIT rates themselves were computed correctly; in Galaxy r2 this was the Galaxy `phykit_metrics` evolutionary_rate job on filtered ZIPs (`.../galaxy_deepseek_v4_pro_via_claude_code_superseded_r2/.../claude_events.jsonl.gz:L8621-L12229`).
- **83.0 (CC code r2): restricted to 19 BUSCO genes.** The agent kept only the 19 BUSCO genes complete and single-copy in all eight species, then compared 19 vs 19 (`...code_..._r2/.../claude_events.jsonl.gz`, final summary).
- The error is the same in both answers: an unrequested paired or matched-gene design. The prompt says "across all genes", and the two kingdom archives are independent SCoG sets, so the populations should not be intersected.
- **Correct Galaxy runs used Galaxy tools throughout.**
  - Sol Galaxy r1 ran `goeckslab/phykit_metrics` (evolutionary_rate, ZIP mode, `.treefile` filter) once per kingdom, then the Galaxy `nonparametric_rank_test`, which returned `n_a=100, n_b=249, u_statistic=3661` (`...galaxy_codex_gpt_5_6_sol_r1/...codex_events.jsonl:L84-L97`).
  - CC Galaxy r1 did the same with grouped archives. It ran scipy locally only as a cross-check (`...:L16888`), so this is not a local fallback.

**Interpretation.** These are genuine population-definition errors confined to the superseded harness, not equivalent answers. I found no evaluator or reference issue.

**Tags:** `scientific-method-error`, `route-divergence`

---

<a id="bix-55-q1"></a>

### bix-55-q1 — Both "100" answers come from runs that installed BUSCO 5.7.1 locally; "64" comes from a hand-rolled BUSCO substitute

**Question.** How many eukaryota_odb10 BUSCOs are Complete single-copy in all four proteomes (C. elegans, G. gallus, N. crassa, S. cerevisiae)?

**Reference.** `101` (tol 0.5, so exact).

**Outcome.** Galaxy 15/15, code 12/15. Wrong answers: `100` — GPT-5.6 Sol code r1 and Luna code r3; `64` — DS-Claude-Code code r2.

**What the traces show.**
- **100: the only two BUSCO 5.7.1 runs.** Both runs installed BUSCO 5.7.1 in the workspace with HMMER 3.4 and ran protein mode against the supplied offline lineage (`.../open_ended_code_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L40`; `..._luna_r3/...:L48-L101`). Both got single-copy counts of 222 (Cele) and 129 (Ggal), with 237/237 for the fungi, and an intersection of 100 (Sol r1 L47; Luna r3 L101). Every run on another BUSCO version got 101:
  - Galaxy `iuc/busco` 5.8.0+galaxy2, used by all 15 Galaxy runs; DS-codex Galaxy r3 also tried 5.5.0 and 6.1.0.
  - Local 5.5.0 (GPT-5.6 Sol code r2: 223/131/237/237, L48–L56).
  - Local 5.8.x and 6.1.0 (other code runs).

  The version is the only difference between the runs that got 100 and those that got 101. The underlying mechanism (1–2 borderline markers in the two animal proteomes) is inferred, not re-run.
- **64: BUSCO re-implemented by hand.** DS-CC code r2 never ran BUSCO. It ran pyhmmer against the 255 profiles and called a marker "Complete single-copy" when its bit score passed `scores_cutoff` with exactly one hit. BUSCO's length-profile checks and hit handling were skipped, so far too many markers came out duplicated (Ggal 153) and the intersection fell to 64 (`.../claude_events.jsonl` final summary, before L6012).
- **Galaxy runs are genuine Galaxy computation.** Every Galaxy run's job ledger has successful BUSCO `galaxy_job` events (`job_ledgers/galaxy/*.json`). DS-codex r3 ran `busco/5.5.0+galaxy0` four times, then `filter_tabular`, `Cut1` and `comp1` in Galaxy. No Galaxy run fell back to local BUSCO.

**Interpretation.** The 100 answers are correct BUSCO runs that are sensitive to the BUSCO version. The reference matches BUSCO 5.5–6.1 (including Galaxy's 5.8.0), so there is no Galaxy defect, but "exact 101" silently assumes a version. The 64 is a genuine method substitution.

**Tags:** `tool-version-difference`, `scientific-method-error`

---

<a id="bix-12-q2"></a>

### bix-12-q2 — Rejected runs counted gaps as a character state; one accepted value relies on a protein-alphabet bug

**Question.** Report the median percentage of parsimony-informative sites across the fungal single-copy ortholog alignments.

**Reference.** `3.5` (evaluator `llm_verifier_auto_code`, tolerance ±0.5, so 3.0–4.0 is accepted). With gaps treated as missing, the value is 3.5385% over 255 `.faa.mafft` alignments.

**Outcome.** Galaxy 15/15, code 13/15. The only wrong answer is `5.437%`, from DeepSeek-Claude-Code (superseded) code r1 and r2.

**What the traces show.**
- **The wrong runs chose to count gaps.** DeepSeek-Claude-Code code r1 computed both gap treatments side by side: "Gaps as state: median = 5.437352% / Gaps as missing: median = 3.538462%" (`.../bix-12-q2/source_snapshots/huggingface_traces/files/open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1/agent_workspace/run_trace/claude_events.jsonl.gz:L4615-L4616`). It then submitted the gaps-as-state value with no recorded justification (`:L9331`). Treating gaps as missing is the standard definition (and PhyKIT's), so this is a definition error.
- **One accepted value is only accepted because of the tolerance.**
  - GPT-5.5 code r1 reported 3.2692% (`.../open_ended_code_codex_gpt_5_5_r1/run_trace/codex_events.jsonl:L20,L34`).
  - Its "missing" set was `'-?XxNn'`, which drops `N`. In a protein alignment `N` is asparagine, not an ambiguity code.
  - In the same run, excluding only gaps gave 3.5385%. Its own character check showed the alignments contain only standard amino acids plus gaps (`:L23-L28`), so the 0.27-point gap is caused entirely by that alphabet bug.
  - 3.269 passes only because of the ±0.5 tolerance.
- All 15 Galaxy runs computed the value with parsimony-informative-site custom tools (UDTs) inside Galaxy. No local fallback was found.

**Interpretation.** The two rejections are genuine definition errors: gaps counted as states. The reference is sound. GPT-5.5 code r1 is a lenient-tolerance false positive: a wrong protein alphabet produced a different number that still fell inside the window.

**Tags:** `domain-knowledge-error`, `evaluator-false-positive`

---

<a id="bix-12-q5"></a>

### bix-12-q5 — Counting gaps as a character state inflated the maximum from 29 to 35

**Question.** Report the maximum number of parsimony-informative sites in any animal single-copy ortholog alignment.

**Reference.** `29` (evaluator `llm_verifier_auto_code`, tolerance ±0.5, so effectively exact).

**Outcome.** Galaxy 15/15, code 13/15. The only wrong answer is `35`, from DeepSeek-Claude-Code (superseded) code r1 and r3. Both name gene 1428854at2759 as the maximum.

**What the traces show.**
- **Code r1 counted gaps as states.** Its counter tallies `Counter(column)` over every character in the column, gaps included, so a column with two or more gaps counts `-` as a state (`.../bix-12-q5/source_snapshots/huggingface_traces/files/open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1/agent_workspace/run_trace/claude_events.jsonl`; result 35 at `:L1166`).
- **Code r3 raised the gap question but did not act on it.** It explicitly asked "gaps are a state, but does '-' count?", yet its final counter still admitted gaps, and it reported 35 (`.../open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3/.../claude_events.jsonl:L2353,L3145`).
- **This is the same mechanism as bix-12-q2**, where the same model computed both gap policies and submitted the gaps-as-state value.
- **Correct runs.** DeepSeek-Claude-Code code r2 and every other run treat gaps as missing and get 29. All Galaxy runs used PhyKIT or custom parsimony-informative-site tools (UDTs) run in Galaxy (for example `phykit-pis-animal-batch-...-v4:ok`). No local fallback was found.

**Interpretation.** This is a genuine definition error: gap characters were counted as a state. It is not an equivalent answer, and the reference is sound. The failure is confined to the superseded DeepSeek-Claude-Code harness.

**Tags:** `domain-knowledge-error`

---

<a id="bix-16-q4"></a>

### bix-16-q4 — Both code failures are data-alignment bugs: genes or cell lines paired out of order

**Question.** Across DepMap cell lines, what percentage of genes show a BH-significant Spearman correlation between expression and CRISPR gene effect (either direction)?

**Reference.** Range [20, 25]% (`range_verifier`). The runs that agree converge on 3,854/17,676 = 21.8036%.

**Outcome.** Galaxy 15/15, code 13/15. Wrong answers: `6.885%` — DS-codex code r2; `0.5827%` — DS-Claude-Code code r1.

**What the traces show.**
- **DS-codex code r2: genes (columns) never put in a common order.** Correct GPT-5.6 Luna code r1 selected columns explicitly (`cr.loc[ids, common]`, `ex.loc[ids, common]`) and got 3,854 significant genes, 1,336 positive and 2,518 negative (`.../open_ended_code_codex_gpt_5_6_luna_r1/.../codex_events.jsonl:L32-L41`). DS-codex r2 used the same 1,103 cell lines, 17,676 genes and Spearman+BH. It read each file with `usecols=[id]+common`, which keeps each file's own column order, and reordered only rows (`cd.loc[common_ids]; ed.loc[common_ids]`, L33). It then correlated the `.to_numpy()` arrays column by column, so column i of one file was paired with column i of the other. Its "independent" SciPy check used the same `iloc[:, i]` pairing, so it agreed with itself (L35). Result: 1,220 → 1,217 significant genes, split symmetrically (609 positive / 611 negative, L33). A symmetric split is what random gene pairs produce, whereas true same-gene correlations lean negative. The column-order mismatch is inferred from the code plus this pattern; column orders were not re-read.
- **DS-CC code r1: cell lines (rows) paired out of order.** Its "fix" at L6930 gave each common cell line a position in its own file's row order. The two files order rows differently (1,178 vs 1,673 rows), so row k of the CRISPR matrix and row k of the expression matrix are different cell lines. Only 103 genes were significant, split 55/48 (L7035).
- **Why Galaxy was 15/15.** 14 Galaxy runs used the ordinary Galaxy tool `featurewise_correlation`, which pairs features by name and samples by ID itself (`job_ledgers/galaxy/*.json`). That is exactly the step that broke in the code failures. DS-CC Galaxy r1 used a UDT (`spearman-bh-gene-correlation`, 6 failed attempts, then ok) and got 21.8068%. All computation ran as Galaxy jobs.
- GPT-5.6 Sol code r1/r2 matched genes by symbol (17,864 genes) and got 21.67% and 21.69%. This is a legitimate variant inside the range.

**Interpretation.** These are genuine implementation errors that passed self-validation because the check reused the same misaligned indexing. The reference and evaluator behaved correctly.

**Tags:** `statistical-error`, `insufficient-verification`

---

<a id="bix-24-q2"></a>

### bix-24-q2 — "Upregulation" follows from a 30-sample model; the six-sample CBD-vs-DMSO fit gives downregulation

**Question.** Using DE (padj<0.05, |log2FC|>0.5) and GO Biological Process enrichment, does up- or downregulation mainly drive CBD's metabolic effects in CRC cells?

**Reference.** `downregulation` (llm_verifier_auto_code, label match).

**Outcome.** Galaxy 14/15, code 14/15. Wrong answers: `upregulation` from Sol code r1 and Luna Galaxy r3.

**What the traces show.**
- **Sol code r1 had both results and kept the one that disagreed with the reference.**
  - Its matched six-sample DESeq2 fit (CBD_IC50 vs DMSO) gave 57 up / 112 down DEGs and pointed to downregulation (`.../open_ended_code_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L26`).
  - It then refitted a 10-level `~ Group` model on all 30 libraries, which "points to upregulation". It declared that the "primary" model (`:L29-L34`) and reported 20 significant metabolic GO-BP terms for up and none for down (`:L39`).
- **Luna Galaxy r3 used edgeR on all 30 samples, then counted terms.**
  - Galaxy edgeR: 10-level factor, TMM, and CBD vs DMSO gave 53 up / 64 down (`...galaxy_codex_gpt_5_6_luna_r3/...:L247-L259`).
  - Galaxy `annotateMyIDs` and Enrichr GO_Biological_Process_2023 with a 63,677-gene background followed.
  - It concluded upregulation from 41 up vs 4 down significant terms, and 4 vs 1 metabolic terms (`:L321`).
  - All of this ran in Galaxy, with no local fallback. The decision rested on a handful of terms from a different DE engine and design.
- **Contrast.** Sol code r2 ran the same two fits but made the six-sample analysis decisive. It got 112 down vs 57 up and 33 metabolic GO-BP terms for down (glycolysis, pyruvate, ATP generation) vs 8 for up, and answered downregulation (`...sol_r2/...:L46-L56`).
- This is the same dataset and the same design sensitivity as bix-43-q4. Pooling all 30 samples for dispersion changes the DEG set enough to flip the conclusion.

**Interpretation.** The reference reflects the matched six-sample CBD-vs-DMSO analysis. Both misses chose a whole-experiment model, which is statistically defensible but unstated in the prompt. Luna also switched to edgeR. The directional conclusion is therefore fragile to an unstated design choice. I would not count these as clear scientific errors; the task is somewhat underspecified. I found no evaluator issue.

**Tags:** `underspecified-task`, `route-divergence`, `statistical-error`

---

<a id="bix-49-q4"></a>

### bix-49-q4 — 2118 vs 2106 is only DESeq2's independent-filtering alpha; the two 2100s come from PyDESeq2

**Question.** Run DESeq2 with apeglm shrinkage for ASXL1 vs control with sex as a covariate, and count genes with padj < 0.05.

**Reference.** `2106`. The evaluator also accepts `2118` (`accepted_answers ['2118','2106']`, tolerance 0.5).

**Outcome.** Galaxy 15/15, code 13/15. The only rejected answer is `2100`, from DS-CC code r2 and r3 (older harness).

**What the traces show.**
- **Why there are two accepted values.** apeglm does not change padj. The split comes from the `alpha` passed to `results()`, which sets DESeq2's independent-filtering cutoff.
  - Sol code r1 fit `~ sex + condition` on the 19 samples that have metadata, with `alpha=0.05`, and got 2106. Its sensitivity check printed `default_alpha_significant 2118` (`open_ended_code_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L42-L50`).
  - Every run that used the IUC Galaxy DESeq2 wrapper (2.11.40.8+galaxy4) reported 2118: GPT-5.5 Galaxy r2/r3, Sol Galaxy r1, Luna Galaxy r1/r2, DS-Codex Galaxy.
  - Sol Galaxy r1 believed it had set "alpha=0.05", but the only alpha it passed was `output_options|alpha_ma: 0.05`, the MA-plot option (`galaxy_codex_gpt_5_6_sol_r1/...:L71-L83`). The wrapper's result matching the default-alpha (0.1) count suggests `alpha_ma` never reaches `results()`. This is inferred from the numbers; I did not read the wrapper source.
  - Galaxy UDTs that called R DESeq2 1.40.2 with `alpha=0.05` returned 2106 (Sol Galaxy r2 `:L78-L93`, GPT-5.5 Galaxy r1).
- **Why 2100 was rejected.** Both DS-CC code runs gave up on installing R DESeq2 and used **PyDESeq2** instead (`open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r2/.../claude_events.jsonl.gz:L1094`; `_r3:L3980`). They ran it with `alpha=0.05` and reported 1,156 up and 944 down, 2,100 in total. PyDESeq2 is a reimplementation with its own dispersion and filtering details, and it does not provide R's apeglm. So 2100 is not the requested DESeq2/apeglm estimator, although it is scientifically very close (0.3%).
- **Where the computation ran.** All Galaxy runs fitted DESeq2 in Galaxy jobs, either the wrapper or an R UDT.

**Interpretation.** The reference key already covers the one real ambiguity, whether independent filtering targets 0.05 or the default. In practice the Galaxy wrapper decides it: its alpha field is easy to misread and appears to leave the default in place. The 2100 rejections are defensible, since the named method was replaced, but they are close to correct. There is no evaluator error.

**Tags:** `wrapper-semantics`, `tool-version-difference`, `route-divergence`

---

<a id="bix-16-q3"></a>

### bix-16-q3 — The one miss did not flip the sign of the DepMap gene-effect scores; this is not a data mismatch

**Question.** Across cell lines, how many genes show a Spearman correlation ≥ 0.6 between expression and essentiality? The inputs are the DepMap CRISPRGeneEffect and expression matrices.

**Reference.** `3` (str_verifier_auto_numeric, tolerance 0.5).

**Outcome.** Galaxy 14/15, code 15/15. Wrong answer `0`: DS-CC Galaxy r1 (older harness).

**What the traces show.**
- **The sign choice decides the answer.** DepMap gene effect becomes more negative as dependency gets stronger, so essentiality = −GeneEffect.
  - Sol Galaxy r1 applied this explicitly: "using biological essentiality strength (`-GeneEffect`) ... The threshold therefore applies to Spearman(expression, `-GeneEffect`)" (`.../galaxy_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L8`).
  - It then ran the Galaxy tool "Feature-wise Correlation Tests" with its built-in `transform_b = negate` ("Multiply by -1") and got 3 genes (`:L23-L42`).
  - DS-CC Galaxy r2 used the same tool and negation on the same 1,103 matched cell lines and 17,676 genes, and got 3.
- **The failing run left the scores unchanged.** DS-CC Galaxy r1 used the same tool and the same 1,103 × 17,676 overlap. It left `transform_b` at its default `none`, which is visible in the tool form it inspected (`galaxy_deepseek_v4_pro_via_claude_code_superseded_r1/.../claude_events.jsonl.gz:L2274`). It correlated expression with raw gene effect and reported a maximum rho of 0.523 for CDKN1A, so 0 genes passed (`:L6027-L6061`). Higher CDKN1A expression going with a *less negative* gene effect is a known pattern, which confirms that raw scores were used.
- **The prior audit's label is wrong.** The earlier adjudication ("unresolved data/reference mismatch; sample matching") does not hold: sample matching and the gene overlap are identical to the correct runs. The only difference is the sign of the essentiality variable.
- **Retrieval attempts.** DS-Codex Galaxy r3 searched the public HF traces dataset `amanutej/trustworthy-biology-agents-traces` and the BixBench datasets-server (`galaxy_deepseek_v4_pro_via_codex_r3/...:L71-L99`). It only obtained directory listings and one truncated rows page without this question, then computed 3 in Galaxy with negation. The attempt appears unsuccessful but should be noted.

**Interpretation.** This is a genuine domain-knowledge error: DepMap's negative-going gene-effect scale was not converted to essentiality. The Galaxy tool's default hides this, since negation must be switched on. The reference is sound. Where the computation ran is not a concern: all runs computed the correlations in Galaxy.

**Tags:** `domain-knowledge-error`, `wrapper-semantics`, `benchmark-answer-retrieval`

---

<a id="bix-22-q1"></a>

### bix-22-q1 — The one miss comes from a fragile multi-tool Galaxy text pipeline whose correlations have the wrong sign

**Question.** Correlate protein-coding gene length with mean expression (Pearson) in CD4, CD8, CD14 and CD19 cells. Which cell type has the weakest absolute correlation?

**Reference.** `CD14` (str_verifier).

**Outcome.** Galaxy 14/15, code 15/15. Wrong answer: `CD4`, from DeepSeek/CC Galaxy r1 (superseded harness).

**What the traces show.**
- **CC Galaxy r1 assembled the analysis from about 40 generic Galaxy text jobs.** These included Filter, per-cell-type column extraction, row means, sequential `Paste1`, `join1` on gene ID, `filter_tabular`, and four `featurewise_correlation` runs.
  - Along the way it admitted a paste mistake: "I made a sequencing error. Let me paste the step 3 output…" (`.../galaxy_deepseek_v4_pro_via_claude_code_superseded_r1/.../claude_events.jsonl.gz:L23763`).
  - It also redid means "with proper header handling" (`:L22918`).
  - It ended with 19,954 joined genes; correct runs had 19,942.
- **Its results are implausible compared with every correct run.** It reported r = −0.0228 (CD4), −0.0252 (CD8), −0.0237 (CD14) and −0.0250 (CD19) (`:L28004`). All four are negative and nearly identical.
- **The correct values are positive and well separated.** Sol Galaxy r1, a single Galaxy UDT over the three copied datasets, gave CD4 0.0617, CD8 0.0551, CD19 0.0471 and CD14 0.0317 (`...galaxy_codex_gpt_5_6_sol_r1/...codex_events.jsonl:L46`). That UDT ran in Galaxy, not locally.
- The sign flip and the collapsed spread point to broken gene-level pairing somewhere in the paste/join chain. I infer this from the outputs; I did not find the exact misaligned step. The agent did not sanity-check the magnitudes or signs.

**Interpretation.** This is a genuine execution error. Chaining many row-order-dependent Galaxy text tools (Paste/Join with header juggling) is error-prone, and the agent accepted a result with an anomalous sign. There is no issue with the reference or the evaluator. Every Codex-harness run is correct.

**Tags:** `insufficient-verification`, `scientific-method-error`

---

<a id="bix-28-q3"></a>

### bix-28-q3 — Galaxy PhyKIT-metrics wrapper's non-verbose value is the variance, not the median

**Question.** Report the median PhyKIT long-branch score for fungal gene 996662at2759, a 4-taxon tree.

**Reference.** `-30.4551` (llm_verifier_auto_code, ±0.152).

**Outcome.** Galaxy 14/15, code 15/15. Wrong answer: `146.3023` from Sol Galaxy r1.

**What the traces show.**
- **Verbose run.** Sol Galaxy r1's verbose `phykit_metrics` 0.2.0+galaxy0 job returned −29.4826, −32.1541, −31.4275 and −6.9357. Their median is −30.45505 (`.../galaxy_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L44`).
- **Non-verbose rerun.** The agent reran with `verbose:false` "to report the per-tree median directly" (`:L45-L47`). It got `146.3023` (`:L49`) and submitted it, although a median cannot lie outside the four scores (`:L66`).
- **Verified: 146.3023 is the sample variance.** The ddof=1 variance of the four scores is 146.302. PhyKIT's non-verbose `lb_score` prints eight summary lines, with `variance` last (source read in DS-Codex Galaxy r1, `:L128-L130`). So the wrapper's single `value` column evidently takes the last line. This is inferred; the wrapper source was not archived.
- **Other runs rejected the same output.** DS-Codex Galaxy r1 and r2 also got `146.3023` and reported the median instead (`r1:L120,L144`; `r2:L97,L202`).

**Interpretation.** A Galaxy wrapper defect: the variance is mislabelled as the metric value. It was compounded by a missing range check. The reference is sound.

**Tags:** `galaxy-platform-defect`, `wrapper-semantics`, `insufficient-verification`

---

<a id="bix-35-q1"></a>

### bix-35-q1 — Galaxy silently ran the default "total tree length" metric instead of "evolutionary rate"; one run reported that value

**Question.** Report PhyKIT's `evolutionary_rate` for BUSCO gene 156083at2759 in animals.

**Reference.** `0.0471` (evaluator `llm_verifier_auto_code`, tolerance ±1%).

**Outcome.** Galaxy 14/15, code 15/15. The only wrong answer is `0.1884`, from DeepSeek-Claude-Code (superseded harness) Galaxy r1.

**What the traces show.**
- **Both Galaxy jobs in the failing run executed the wrong metric.**
  - The run's two `phykit_metrics/0.2.0+galaxy0` jobs have `--metric 'total_tree_length'` and resolved params `"selector": "total_tree_length"` (`.../bix-35-q1/source_snapshots/galaxy/bbd44e69cb8906b52e14f19a06d11766/jobs/bbd44e69cb8906b579b2af780e19ff65.json`, `...d01965fc484b0dc2.json`).
  - Submission 1 used flat `operation|selector: evolutionary_rate` keys with `input_format: 21.01`. The harness flagged `parameter_mismatch` (expected `evolutionary_rate`, resolved `total_tree_length`) (`.../galaxy_deepseek_v4_pro_via_claude_code_superseded_r1/agent_workspace/run_trace/claude_events.jsonl.gz:L3091-L3092`).
  - Submission 2 used a nested payload with `__current_case__: 0` and no `selector` key. Galaxy again applied the default metric. The harness had "no_explicit_non_dataset_parameters" to compare, so it reported `ok` (`:L3914-L3915`).
- **The agent had the right number and discarded it.** In its own reasoning it computed 0.188376 / 4 taxa = 0.04709 and noted "the output is 0.1884, which is the total tree length". It then ran a total-tree-length comparison, got 0.1884 from both jobs, and concluded the wrapper "must" define the rate that way (`:L6145-L6936`).
- **The same silent default hit about half the Galaxy runs.**
  - 7 of 15 Galaxy histories contain at least one `total_tree_length` job: Sol r1/r2, Luna r1/r3, DeepSeek-Codex r1, and DeepSeek-Claude-Code r1/r2.
  - Every `21.01` payload shape collapsed to `total_tree_length` / `single`: flat pipe keys, nested with `selector`, and nested with `__current_case__`. Examples: Sol r1 `.../galaxy_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L24,L33`; Luna r1 `:L44,L47,L62`.
  - Only `legacy` flat keys bound correctly (Sol r1 `:L36-L52`, Luna r1 `:L77`).
  - The other six runs recovered because the harness's parameter-provenance check flagged the mismatch.
- The 14 correct Galaxy answers came from Galaxy `evolutionary_rate` jobs. No local-computation fallback was needed.

**Interpretation.** The prior adjudication is confirmed. Galaxy's `21.01` input binding for this wrapper's nested conditional silently replaced the requested metric with the default, and returned a successful job. The failing run's agent made two mistakes: it removed the explicit selector, and it trusted a result it had already shown to be inconsistent. The harness check also misses payloads that carry no explicit parameters. This is a genuine Galaxy/wrapper usability defect, not a reference problem.

**Tags:** `silent-parameter-substitution`, `galaxy-platform-defect`, `wrapper-semantics`, `insufficient-verification`

---

<a id="bix-46-q4"></a>

### bix-46-q4 — The only failure had the correct value from Galaxy and ended its turn before writing it

**Question.** Report the log2 fold change of phenazine gene PA14_35160 in the ΔrhlI mutant, rounded to 2 decimal places.

**Reference.** `-4.10` (evaluator `llm_verifier_auto_code`).

**Outcome.** Galaxy 14/15, code 15/15. The single failure is DeepSeek-Codex Galaxy r2, which produced no answer.

**What the traces show.**
- **The run had the right number.** It used the Galaxy `rds_to_tabular` wrapper to convert the provided DESeq2 `res_1vs97.rds` and `res_1vs98.rds` objects (`.../bix-46-q4/source_snapshots/huggingface_traces/files/galaxy_deepseek_v4_pro_via_codex_r2/agent_workspace/run_trace/codex_events.jsonl:L36-L42`). It then downloaded the tables, whose `res_1vs97` row reads `PA14_35160 ... log2FoldChange -4.09911354408172` (`:L48`). That rounds to the reference -4.10.
- **It then spent the rest of the run searching the web.**
  - It searched for which comparison (strain 97 vs 98) is the ΔrhlI mutant: "res_1vs97" "res_1vs98", "PA14_35160" "ΔrhlI", and PLOS / PMC supplementary tables (`:L52-L72`).
  - It also searched for its own exact value, `"-4.09911354408172"` (`:L70`).
- **The turn ended without an answer.** It stopped after about 4 minutes with every todo item still marked incomplete. No `codex_output/answer.txt` was written, and the runner logged "no last agent message" (`:L73-L74`; `runner.log`; `completion.json`).
- **Other runs got it right in Galaxy.** The other 14 Galaxy runs reached -4.10 through the same Galaxy RDS-to-table route.

**Interpretation.** This is a completion failure, not a scientific or platform error. The correct Galaxy-computed value was already in the workspace. The mapping from strain number to mutant was arguably underspecified in the inputs, which sent the agent to the web, but the DeepSeek-Codex agent ended its turn early rather than committing an answer.

**Tags:** `no-answer`, `run-truncated-or-timeout`

---

<a id="bix-51-q8"></a>

### bix-51-q8 — Galaxy sklearn defaults (liblinear, L2, penalized intercept) gave −0.027; the agent's own unpenalized fit was ignored

**Question.** Fit a simple logistic regression of camrelizumab response on age and report the age coefficient (log-odds).

**Reference.** Range [−0.084, −0.064] (range_verifier). The unpenalized MLE is −0.074954.

**Outcome.** Galaxy 14/15, code 15/15. Wrong answer: `-0.02708784` from DeepSeek-Claude-Code (superseded) Galaxy r3.

**What the traces show.**
- **Wrapper defaults.** DS-CC Galaxy r3 ran `sklearn_generalized_linear` 1.0.11.2 LogisticRegression with no model options. The job ran with `solver=liblinear`, `penalty=l2`, `C=1.0` (job ledger). Liblinear also penalizes the intercept, which is about 4.45 here with raw age. That biases the slope to −0.02709, which the run wrote before verifying (`.../claude_events.jsonl.gz:L11484`).
- **The ignored check.** Its local `penalty=None` fit gave −0.0749538 (`:L11508-L11511`). A sweep found lbfgs −0.07491 and liblinear −0.02709 (`:L11692`), and a final check matched liblinear to the Galaxy value (`:L11931`). It kept the regularized answer anyway (this corrects the prior note).
- **Contrast.** Sol Galaxy r1 and DS-Codex Galaxy r2 set `penalty=none, solver=lbfgs` in the same Galaxy tool and got −0.0749538. DS-CC Galaxy r1 used lbfgs with L2 and got −0.07491, inside the range. All of these fits were Galaxy jobs.

**Interpretation.** An estimand error. The wrapper's defaults do not match "simple logistic regression", and the agent kept them despite its own contradicting fit. The reference is sound.

**Tags:** `statistical-error`, `wrapper-semantics`, `insufficient-verification`

---

<a id="bix-52-q2"></a>

### bix-52-q2 — A digits-only header filter silently dropped the W and Z chromosomes

**Question.** Compute the mean per-chromosome density (filtered unique CpGs / chromosome length) for Jackdaw age-related CpGs with methylation >90% or <10%, over the chromosomes that have at least one such CpG.

**Reference.** Range [1.03e-7, 1.23e-7] (range_verifier). The consensus value is 1.1282568e-7.

**Outcome.** Galaxy 14/15, code 15/15. Wrong answer: `9.5074614121924e-08` from Luna Galaxy r3.

**What the traces show.**
- **The drop.** Luna Galaxy r3 filtered and counted correctly, giving 20 chromosome groups (Datamash, HID 10). To strip the length table's header it used `tp_grep_tool` with `^[0-9]+\t` (`.../galaxy_codex_gpt_5_6_luna_r3/.../codex_events.jsonl:L89`). That also removed the non-numeric chromosomes W and Z, so the `join1` inner join kept 18 rows (`:L91`). The agent accepted "18 eligible chromosomes" (`:L135`).
- **Contrast.** Luna Galaxy r1 joined all 20 chromosomes, including W (4.45e-7) and Z (1.00e-7), and got 1.1282568e-7 (`galaxy_codex_gpt_5_6_luna_r1/...:L195`). Removing those two rows gives exactly r3's 9.5075e-8. This resolves the prior "unresolved join/denominator" note.
- **Computation location.** Every r3 step ran as a Galaxy job.

**Interpretation.** A genuine agent error, not a Galaxy defect: a header filter also dropped real chromosome rows without any error, and the count mismatch went unchecked. The reference is sound.

**Tags:** `insufficient-verification`, `scientific-method-error`

---

<a id="bix-53-q5"></a>

### bix-53-q5 — The only miss is `10.0%` for a fraction of 0.1; the parser read the percent value as 10.0

**Question.** Using gseapy with WikiPathways_2019_Mouse, what fraction of the top 20 enriched pathways (from DE genes with p < 0.05, |shrunken LFC| > 1, baseMean > 10) have "oxidative" in the name? Round to 1 decimal.

**Reference.** `0.1` (str_verifier_auto_numeric, tolerance 0.001).

**Outcome.** Galaxy 15/15, code 14/15. Wrong answer `10.0%`: DS-CC code r3 (older harness).

**What the traces show.**
- **The failing run had the right result.** DS-CC code r3 found 2 of the top 20 pathways containing "oxidative" (one is Oxidative Damage, WP1496) and reported "Fraction: 2/20 = 10.0%" (`open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3/.../claude_events.jsonl.gz:L3793`). The science matches every other run.
- **The answer broke the output contract.** Its own prompt says to add "%" only "when the question asks for a percentage" (`.../agent_workspace/prompt.txt:40`). The question asks for a fraction rounded to one decimal.
- **The parser ignored the % sign.** evaluation.json shows `observed_value: 10.0` against `expected_value: 0.1`: "%" was dropped without dividing by 100. A percent-aware parser would have read 0.1 and accepted it.
- **Where the computation ran.** The Galaxy runs used Galaxy DESeq2 (the wrapper or a UDT) plus the Galaxy `gseapy_enrichr` tool (ledgers, for example Sol Galaxy r1). None computed the enrichment locally.
- **Failed retrieval attempt.** DS-Codex Galaxy r2 tried to pull the `phylobio/BixBench-Verified-50` rows from the HF datasets-server, filtering for this question, and got `HTTP Error 401: Unauthorized` (`galaxy_deepseek_v4_pro_via_codex_r2/.../codex_events.jsonl:L167-L169`). It answered 0.1 from its own Galaxy analysis.

**Interpretation.** The answer is scientifically equivalent to the reference. The zero comes from the agent's format error combined with an evaluator that does not handle percentages. Rescored on the science, the task is 15/15 in both conditions.

**Tags:** `equivalent-answer`, `format-contract-error`, `evaluator-false-negative`, `benchmark-answer-retrieval`

---

<a id="bix-61-q2"></a>

### bix-61-q2 — 20.5045 came from re-trimming the raw subsample instead of mapping the supplied trimmed reads

**Question.** Report the mean genome-wide depth for SRR35233585 after mapping the *trimmed* reads with BWA-MEM (given read group) and computing depth with samtools.

**Reference.** `12.1283` (llm_verifier_auto_code, ±0.061).

**Outcome.** Galaxy 14/15, code 15/15. Wrong answer: `20.5045` from DeepSeek-Claude-Code (superseded) Galaxy r1.

**What the traces show.**
- **Wrong input.** The seed history holds the trimmed `SRR35233585_{1,2}_paired.fastq.gz` (about 22 MB gz each) and the raw `.subsample.fastq` files (252 MB each). DS-CC Galaxy r1 chose to "trim the raw reads" (`.../claude_events.jsonl.gz:L1021`). It re-trimmed the raw subsample with Galaxy Trimmomatic SLIDINGWINDOW:4:20 and mapped those reads (`:L6438`).
- **Consequence.** Its BAM is 67.8 MB; DS-CC Galaxy r2, which mapped the supplied `_paired` files, has a 32.1 MB BAM (history `contents.json`). The arithmetic 95,174,581 / 4,641,652 = 20.5045 is correct (`:L7393`). This resolves the prior "unresolved upstream difference" note.
- **Computation location.** Trimmomatic, BWA-MEM and `samtools depth -a` all ran as Galaxy jobs.
- **Accepted near-miss.** DS-CC code r2/r3 answered 12.0906 by using `bwa mem -M`. That flag makes split hits secondary, which `samtools depth` skips. r1 omitted `-M` and got 12.1283.

**Interpretation.** A genuine input-selection error, not a Galaxy defect. The reference is sound.

**Tags:** `scientific-method-error`, `route-divergence`
## CompBioBench

<a id="genome-coords-q1"></a>

### genome-coords-q1 — Hidden key is almost certainly "E"; all 24 paired runs made the same computation and read it as "feedback loop" (D)

**Question.** From 600 simulated cell trajectories (250 frames each) with enhancer/promoter 3D coordinates and a 0/1 transcription call, define contact as distance <= 260 nm and pick the "single most defensible conclusion" (A independent, B transcription -> proximity, C proximity -> transcription, D feedback loop, E alternate explanation).

**Reference.** `E`: the lead auditor's correction, not the brief's `D`. The brief's `D` came from `score_predicted_answers.tsv`, which is only the most likely answer and not unique. Once the 9 hash-mismatched vectors are normalized ("Proximal enhancer" -> "pELS"), the combined key reproduces all 25 official leaderboard scores with zero residual only when this item is `E`. The working reference (`D`) also looks wrong.

**Outcome.** Galaxy 0/12, code 1/13 correct against `E`. Only GPT-6 Astra (code r1) answered `E`. All 24 paired runs (12 Galaxy, 12 code, 4 models) answered `D`.

**What the traces show.**
- Every run computed the same numbers. Same-frame association is null: P(T|C)=0.155 vs P(T|no C)=0.154. There is a positive one-frame lag in both directions: P(T_t+1 | C_t)=0.201 vs 0.151, and P(C_t+1 | T_t)=0.094 vs 0.046. Neither series is autocorrelated (P(T_t+1 | T_t) 0.151 vs 0.151; P(C_t+1 | C_t) 0.046 vs 0.046). There is no signal at lag ±2 or beyond. Sol Galaxy r1 put cluster-bootstrap CIs on both one-frame effects (C->T risk difference 0.050, 95% CI 0.040-0.061) inside a Galaxy UDT (`.../genome-coords-q1/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_6_sol_r1/agent_workspace/run_trace/codex_events.jsonl:L16-L22`). Sol Galaxy r2 reports the same 0.1513->0.2013 and 0.0460->0.0936 (`.../galaxy_codex_gpt_5_6_sol_r2/.../codex_events.jsonl:L224`).
- The D runs all reasoned the same way: bidirectional one-step prediction means a feedback loop. For example, DeepSeek Galaxy r2 says it checks "whether the reverse spike survives conditioning ... before calling it feedback" (`.../galaxy_codex_deepseek_v4_pro_0813_r2/.../codex_events.jsonl:L85`).
- Astra ran the same analysis (`.../open_ended_code_codex_gpt_6_astra_r1/agent_workspace/run_trace/codex_events.jsonl.gz:L9`, `L11`). Its only extra step was checking that the ±1-lag pattern holds in each block of 100 cells (`L14`). It said the associations appear "in both directions, but barely at the same time point" (`L12`) and then answered `E` (`L15`). It used 280 reasoning tokens and gave no rationale, so its `E` cannot be traced to any computation the others lacked.

**Interpretation.** This is not a computation or platform error. Galaxy and code runs agree exactly on the statistics, and the Galaxy runs did the computation in UDT jobs. The miss is interpretive: the intended answer apparently treats the lag-only, persistence-free coupling (no same-frame co-occurrence, no autocorrelation, no multi-step propagation) as something other than a feedback loop. The prompt never defines what separates D from E, and the data are a reasonable fit for D. Astra's lone `E` may reflect a different reading of the prompt rather than better evidence. This item says little about the Galaxy-vs-code comparison.

**Tags:** `reference-questionable`, `underspecified-task`, `domain-knowledge-error`

---

<a id="encode-atac-pipeline-q1"></a>

### encode-atac-pipeline-q1 — Only two real in-container runs got 29,556; the Galaxy `.dat` filename silently turned off adapter trimming (13,636), and host OpenSSL changed the pseudoreplicate split (~28.9k)

**Question.** Run the ENCODE ATAC-seq pipeline v2.2.3 on paired-end FASTQs, using an input JSON like the ENCSR356KRQ example but without `atac.enable_xcor`, and report the IDR `N_opt` from `qc.json`.

**Reference.** `29556` (score-inferred). The lab's working reference `28285` comes from a partial local rerun (GPT-5.5 Galaxy r2), so it is less reliable than the key.

**Outcome.** Galaxy 2/12, code 0/13. Wrong answers: `13636` (GPT-5.5 G r1; Sol G r2, r3; DeepSeek G r2; Luna G r1–r3); `13653` (DeepSeek G r3); `28285`/`28301` (GPT-5.5 G r2/r3); `28869`–`28965` (all code runs except the two below); `29608` (Astra code); `108` (Sol code r3).

**What the traces show.** (Paths are relative to `.../encode-atac-pipeline-q1/source_snapshots/huggingface_traces/files/<run>/agent_workspace/run_trace/codex_events.jsonl[.gz]`.)
- **Correct runs.** Both ran the full v2.2.3 WDL with Cromwell inside the official container as one Galaxy UDT job. DeepSeek G r1 used Caper 1.0.0/Cromwell; its final job took 4,579 s and the log ends `Workflow ... status=Succeeded` (L294). Sol G r1 used Cromwell 82 (L131; provenance in `selected_outputs/galaxy/bbd44e69cb8906b544a9177160597894/`). No local shortcut. Both first linked the Galaxy inputs to `*.R1.fq.gz`/`*.R2.fq.gz` names (DeepSeek r1 L248; Sol r1 input.json L131). Result: 4,999,816 reads, 98.2% mapped, NFR 0.343.
- **13,636 (Galaxy platform/wrapper interaction).** These runs passed Galaxy's `dataset_*.dat` paths straight into the pipeline JSON (Sol r2 L190; Luna r2 L453). ENCODE's `detect_adapter.py` picks gzip only by file extension: `gzip.open(f) if f.endswith('.gz') else open(f)` (code r2 L128). So no adapter was found and nothing was trimmed. Every run in this cluster shows exactly 5,000,000 reads, 75.4% mapped and NFR 0.098 (GPT-5.5 r1 L134), so fewer peaks and N_opt 13,636. Each ran the real pipeline in its own history, except Luna G r1. All 9 of Luna r1's jobs failed; it then searched the shared Galaxy account and copied `13636` from the `answer.txt` of a July pilot history (`bbd44e69cb8906b5b91ef9ffef4660f0`, L295–L306).
- **13,653.** DeepSeek G r3 has the same untrimmed alignment. It also switched to the older `genome_tsv/v1/hg38_caper.tsv`, which uses the `hg38.blacklist.bed.gz` blacklist (L137, L294).
- **~28.9k code cluster.** All code runs ran on a macOS host with conda tools at the pinned versions (MACS2 2.2.4, IDR 2.0.4.2), and trimming worked. The official Dockerfile downgrades to OpenSSL 1.0.2t "to get the same random number for SPR" (Astra L89). These runs used OpenSSL 1.1.1w or 3.6.3 (code r2 L256). That likely changed the `shuf --random-source=<(openssl enc ...)>` pseudoreplicate split (inferred). Astra alone installed openssl 1.0.2 (L90) and landed at 29,608, 52 off. Its alignment matches the reference (2,499,908 pairs, 98.19%, 3.83% duplicates; L181–L286).
- **28,285/28,301: local fallbacks, including the user-supplied example.** In GPT-5.5 G r2, all 7 analytical Galaxy jobs failed. The UDTs failed before command rendering, even for a one-line probe (L23–L110). The agent then built a local micromamba environment on the aarch64 workspace: bowtie2 2.5.5, samtools 1.20, macs2 **2.2.9.1**, idr 2.0.4, cutadapt 5.1 and picard, with a Picard 2.20.7 jar swapped in later (L155–L158, L241–L249). It re-implemented the alignment → filtering → pseudoreplicate MACS2 → IDR path locally with `bash /workspace/run_atac_nopt_fallback.sh`, which returned `N_opt = 28285` (L271). It then only *staged* the QC table into Galaxy as `fallback idr.reproducibility.qc` (dataset `f9cad7b01a472135ee270d2ea5eb9575`, state `ok`, L272–L277). That dataset's `ok` state does not show a completed Galaxy pipeline. GPT-5.5 G r3 took the same route after 4/4 failed jobs (L88–L277) and noted that MACS2 2.2.4, the pipeline's pinned version, was unavailable (L280). These are computed answers from a partial, version-substituted local reproduction. They are not Galaxy pipeline executions, and they are not the full pipeline's `qc.json`. This plausibly explains why they miss the key by 1,255–1,271 peaks.
- **108.** Sol code r3 ran a macOS port with repeated resumes and `shuf`/`wc`/`zcat` shims. It got overlap N_opt 1,683 and IDR 108, and accepted them without a sanity check (L654–L681).

**Interpretation.** The key 29,556 is reproducible: two independent, real Galaxy container runs produced it. The dominant Galaxy failure (7 of 12 runs) is a silent interaction: Galaxy's extension-less staged paths disable ENCODE's extension-based adapter autodetection. Unlike a failed tool, this can be avoided and is invisible in job states. Code-condition deviations are environment-reproducibility effects, not scientific errors. The working reference should be retired.

**Tags:** `galaxy-platform-defect`, `wrapper-semantics`, `silent-parameter-substitution`, `tool-version-difference`, `local-fallback-in-galaxy`, `reference-questionable`, `cross-run-output-reuse`, `insufficient-verification`

---

<a id="variant-status-q1"></a>

### variant-status-q1 — The apparent T allele is a 5′ read-end artifact; 20/25 runs trusted naive pileup counts

**Question.** From a single-end hg38 RNA-seq BAM, give the likely genotype at chrX:154,398,500 (answer as `x/y`).

**Reference.** `C/C` (score-inferred; the working reference is the same).

**Outcome.** Galaxy 2/12, code 3/13. Wrong answers: `C/T` in 20 runs (every GPT-5.5 Galaxy run, all Luna runs, all DeepSeek Galaxy runs, Sol code r1-r3, Sol Galaxy r1, GPT-5.5 code r2/r3, DeepSeek code r1/r3).

**What the traces show.**
- **The raw pileup is misleading.** At the site there are 38 reads: 15 C and 23 T, all high quality and MAPQ 255 (`open_ended_code_codex_gpt_5_5_r1/.../codex_events.jsonl.gz:L14-L22`). Every T sits at read position 0-1 of a forward read that starts at 154398499-154398500. Once the first two cycles are excluded, the count is C=15, T=0 (`...gpt_5_5_r1...:L42`). Astra finds the same pattern: T only at cycles 1-2, C spread across cycles 4-70 (`open_ended_code_codex_gpt_6_astra_r1/...:L15`). DeepSeek code r2 names the cause: STAR's forced 5′ extension (`alignEndsType Extend5pOfRead1`) aligns untemplated leading Ts instead of soft-clipping them (`open_ended_code_codex_deepseek_v4_pro_0813_r2/...:L80`, genome-wide 5′ mismatch tally at `L164`). A dbSNP entry (rs782251683, C/T) at this position makes the false call look plausible.
- **Wrong runs stop at allele counts.** GPT-5.5 Galaxy r1 runs a single Galaxy `samtools_mpileup/2.2.0` job, sees C and T, and answers C/T (`galaxy_codex_gpt_5_5_r1/...:L31-L38`). Sol code r1 does the same with one local mpileup (`...sol_r1...:L11-L12`). None of the 20 wrong traces mentions read position, cycle or end bias; some use `bcftools call`, which also reports 0/1. Luna Galaxy r2 spent 11.7M tokens on Galaxy mechanics and never inspected read positions. It hit a reference-cache alias mismatch and the mpileup wrapper ignoring its advanced-options conditional, so it discarded that output (`...luna_r2...:L161-L180`), then called C/T from a default pileup (`L235`).
- **Correct Galaxy runs computed in Galaxy.** Sol Galaxy r2 and r3 ran the Galaxy mpileup wrapper, noticed that "T observations cluster at read positions 1–2" (`galaxy_codex_gpt_5_6_sol_r2/...:L25-L28`), and ran a read-position audit UDT (`read_position_audit.py`) as a Galaxy job (`L40`). In r3 that UDT was fixed once (a job-local BAI) and rerun (`...sol_r3...:L37-L59`). Neither run fell back to local computation.
- **Answer-search attempt.** Before answering, DeepSeek code r2 tried to retrieve the benchmark's answers: the Genentech HF dataset/results repos, the leaderboard Space API and a third-party trace dataset (`L94-L162`). It got only 401 errors and aggregate leaderboard rows, so its C/C was computed, not retrieved.

**Interpretation.** This is a genuine scientific-judgment failure, not an evaluator or reference problem. The reference is well supported by the read-position evidence. The task tests whether an agent checks for alignment-end artifacts. Galaxy was not the limiting factor for Sol, but for Luna r2 the wrapper friction pushed out the diagnostic step.

**Tags:** `scientific-method-error`, `insufficient-verification`, `domain-knowledge-error`, `benchmark-answer-retrieval`

---

<a id="ml-model-track-overlap-q1"></a>

### ml-model-track-overlap-q1 — Each wrong answer is a partial union of three accession routes (suffix-stripped ENCSR, direct GSM, ENCODE dbxref GSM)

**Question.** Of the Sei tracks linked to a specific Cistrome ID (19,905 of 21,907), how many share provenance with any Borzoi track? Round to the nearest 100.

**Reference.** `3600` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 1/12, code 5/13 correct. Wrong answers: `1300` from GPT-5.5 Galaxy r1, Sol code r1 and r2, DeepSeek Galaxy r1 and code r2, Luna code r2 and r3. `2400`/`2,400` from GPT-5.5 Galaxy r2 and code r2, Sol Galaxy r1–r3, DeepSeek Galaxy r2. `100` from GPT-5.5 Galaxy r3, Luna Galaxy r1–r3 and code r1. `3400` from DeepSeek code r1.

**What the traces show.** Every run resolved the Sei IDs through the Cistrome sample API. That gives 1,662 ENCODE-type records (as `ENCSRxxx_N`, with a replicate suffix) and 18,243 GEO/GSM-type records. The key equals the union of three disjoint routes:
- **Route 1: direct GSM match.** 102 GSM IDs appear directly in Borzoi.
- **Route 2: ENCSR match after stripping `_N`.** 1,162 more.
- **Route 3: GSM reached through Borzoi's ENCODE experiment `dbxrefs`.** About 2,302 more.

DeepSeek Galaxy r3 got 1,162 ENCSR + 2,404 GSM = 3,566, which rounds to 3,600. It computed this in Galaxy UDTs (`galaxy_codex_deepseek_v4_pro_0813_r3/.../codex_events.jsonl:L298`, `L316`), so it is a genuine Galaxy computation. GPT-5.5 code r1 first got 1,264 (`L145-L148`), then added the dbxrefs and got 3,573 (`L184-L199`).

How each wrong answer falls short:
- **`100`: exact whole-token join, no suffix stripping, no dbxrefs.** Only 102 GSM + 7 ENCODE = 109 match (Luna Galaxy r1 `L100`: "exact whole-token equality"). GPT-5.5 Galaxy r3 reached the same 109 with Galaxy's Join tool (`L227`).
- **`1300`: routes 1 and 2 only.** 102 + 1,162 = 1,264 (GPT-5.5 Galaxy r1 `L98`; Sol code r1 `L55`). No ENCODE cross-reference expansion.
- **`2400`: routes 1 and 3, but the `_N` suffix was not stripped.** Sol Galaxy r3's diagnostic shows `direct_encode_experiment_overlap 7`, `encode_dbxref_only 2302`, `expanded 2411` (`L100`, `L108`). Sol Galaxy r1 got 2,404 (`L183`) and GPT-5.5 code r2 got 2,418 (`L140`).
- **`3400`: file-level (ENCFF) matching.** DeepSeek code r1 lost about 150 ENCODE matches this way and got 3,402–3,424 (`L452-L458`).

**Interpretation.** None of the wrong answers is equivalent to the key. Each one misses one or two legitimate provenance routes, which is a genuine identifier-normalisation error, not a platform defect. It does hit the Galaxy condition harder (1/12). Galaxy runs relied more often on exact-match Join tools or UDT joins that kept the suffixes. The key is plausible but depends on a choice the task leaves open: whether ENCODE dbxrefs count as "shared provenance", which accounts for roughly 2,300 of the 3,600 tracks.

**Tags:** `scientific-method-error`, `insufficient-verification`, `route-divergence`, `underspecified-task`, `wrapper-semantics`

---

<a id="reverse-search-gwas-q1"></a>

### reverse-search-gwas-q1 — Only an exact P-value match to the MultiSuSiE revision release works; one of the two correct Galaxy runs copied the answer from a public trace of an earlier agent run

**Question.** Give the PMID of the study that produced a scrubbed GWAS file: 12.77 M variants, PLINK2 `#CHROM POS ID REF ALT A1 TEST P`, IDs as chr:pos:ref:alt.

**Reference.** `41491094` (score-inferred; the working reference agrees). This is Rossen et al., *Nat Genet* 2026, MultiSuSiE in All of Us WGS. The file equals the `protein_density_P` column of `eur115620.zip` in the revision release (Zenodo 14458399/17370173).

**Outcome.** Galaxy 2/12, code 4/13 correct. Wrong answers:
- `40593539` — Luna Galaxy r2, Luna code r1/r2, DeepSeek code r1
- `29403010` — GPT-5.5 Galaxy r1, Sol Galaxy r1
- `38798542` — Sol Galaxy r3, Sol code r1
- `32929287`, `28628107`, `33462484` — 2 runs each
- 5 other PMIDs — 1 run each

**What the traces show.**
- **The file was only identified by an exact match.** Sol code r2 read chr17:16939677 by HTTP range reads and got `protein_density_P` 3.14755e-12 in the original v1 `eur94082` release versus 1.4221e-16 in the revision `eur115620`. The revision value equals the query (`.../open_ended_code_codex_gpt_5_6_sol_r2/.../codex_events.jsonl.gz:L109`, `L116`).
- **Same study, preprint PMID (`38798542`).** Sol Galaxy r3 matched only the lead variant IDs against the v1 `pips.tsv` fine-mapping table, not P values. It then picked the medRxiv preprint PMID (`.../galaxy_codex_gpt_5_6_sol_r3/.../codex_events.jsonl:L56-L77`). Sol code r1 did extract the `eur115620` row (`L787`) and had already looked up 41491094 (`L700`). It still answered the preprint PMID (`L794`), apparently because the Zenodo record says "Please cite ... medRxiv (2024)" (`L791`). These two runs found the right study but the wrong record; the data themselves belong to the revision.
- **Approximate single-variant match (`40593539`).** These runs matched rs34562254 to the rounded GWAS Catalog value "1e-16" for an N-glycome trait. Luna Galaxy r2 then called the supplement's 1.41e-16 (N=7,081, GRCh37 position) an "exact match" to 1.4221e-16 (`.../galaxy_codex_gpt_5_6_luna_r2/.../codex_events.jsonl.gz:L802-L803`).
- **Locus-pattern guesses.** The other wrong PMIDs are studies that share FCGR/HLA/TNFRSF13B loci. GPT-5.5 Galaxy r1 admits there is no exact match and relies on "trait/sample-size" similarity (`.../galaxy_codex_gpt_5_5_r1/...:L295`).
- **Correct Galaxy runs.** Sol Galaxy r2 found the study by web search. It established the exact match locally with `remotezip` (`L144-L164`), then imported the 4.15 GB archive into Galaxy and re-verified it in a UDT (`L174-L229`). Luna Galaxy r1 had run about 2,000 steps of failed candidate-by-candidate comparison. It then searched the benchmark filename and found the CompBioBench Hugging Face data. From a third-party Hugging Face dataset (`amanutej/trustworthy-biology-agents-traces`) it read an earlier gpt-5.5 run's `trace.md` for this question, whose answer was 41491094 (`.../galaxy_codex_gpt_5_6_luna_r1/.../codex_events.jsonl.gz:L2007-L2043`). It downloaded `eur115620.zip` locally and answered while the Galaxy import was still running (`L2049-L2059`). Several other runs also probed the CompBioBench Hugging Face repo, leaderboard or GitHub runner without getting answers (for example Sol code r1 `L666-L693`).
- **The two metadata-only histories.** Luna Galaxy r1 has 424 items, 67 GB, 21 errors. Luna Galaxy r3 has 799 items, 59.5 GB, 175 errors. Both come from brute-force sourcing: whole candidate summary-statistics files (Fenland, blood-cell, IgA, UKB protein, IgG-glycan archives) were imported into Galaxy and scanned with filter jobs mapped over collections. That is 61 and 240 tool runs, respectively. In Luna r3 the final 77-job UDT comparison failed at command rendering (`L6258-L6264`). It then answered `32128391` from the archive's citation without verification (`L6297`). Across these two runs, 1.04 billion input tokens were spent without a Galaxy-verified answer.

**Interpretation.** This is a retrieval task. Galaxy adds little and is often bypassed; the decisive step is an exact P-value lookup against a public release. Luna Galaxy r1's correct answer is benchmark-answer retrieval and should not count as a Galaxy success. `38798542` identifies the correct study but the preprint record; the key's choice is defensible because the values match only the revision release.

**Tags:** `benchmark-answer-retrieval`, `insufficient-verification`, `source-version-drift`, `local-fallback-in-galaxy`, `route-divergence`

---

<a id="protein-shape-q1"></a>

### protein-shape-q1 — Input is PDB 3J04, the "F" of Howarth's protein alphabet; T is a side-view reading

**Question.** Which uppercase letter (B, D, F, H, J, L, N, P, R, T, V, X, Z) does the protein in `protein.shape.q1.pdb` most resemble, over all projections?

**Reference.** `F` (score-inferred). The lab's working reference `T` is the plurality answer (14/25). The traces show it is the wrong proxy.

**Outcome.** Galaxy 4/12, code 3/13 correct. Wrong answers: `T` from all GPT-5.5 runs except galaxy r2, all Sol runs, Luna galaxy r2, Luna code r3 and Astra; `N` from GPT-5.5 galaxy r2; `Z` from Luna galaxy r1; `P` from Luna code r1; `J` from Luna code r2.

**What the traces show.**
- **The file is an anonymized copy of PDB 3J04.** All residues are renamed ALA and the headers are stripped. The six chains have 903/143/148/903/143/148 CA atoms. DeepSeek code r1 found the benchmark's likely source, Howarth 2015 NSMB "Say it with proteins: an alphabet of crystal structures". That paper's supplementary table lists **F = 3j04** (myosin-11 fragments with light chains) (`open_ended_code_codex_deepseek_v4_pro_0813_r1/.../codex_events.jsonl:L34`). Its CA counts match 3j04 exactly (`:L38`). DeepSeek galaxy r1 staged 3j04.pdb into Galaxy and ran a UDT comparison: 2,388/2,388 CA atoms identical, **RMSD 0 Å** (`galaxy_codex_deepseek_v4_pro_0813_r1/.../codex_events.jsonl:L60-L78`).
- **5 of the 7 F answers came from looking up the source.** DeepSeek galaxy r1 and r3 and code r1–r3 all read the nsmb.3011 supplement or howarthgroup.org/alphabet. Galaxy r3 then fetched 3J04 with the Galaxy `get_pdb` tool (`galaxy_..._r3/...:L79-L103`).
- **Only 2 F answers were derived from the geometry.** DeepSeek galaxy r2 matched projections against DejaVuSans letter shapes using an overlap (Jaccard) score. It ran locally first (F 0.617 > L 0.574 > P 0.526 > T 0.521), then reran the same script as a Galaxy UDT (`galaxy_..._deepseek_..._r2/...:L116-L120`). Luna galaxy r3 inspected Galaxy-rendered views and saw "a left vertical stem with a long upper arm and a shorter middle arm" (`galaxy_codex_gpt_5_6_luna_r3/...:L91`).
- **What distinguishes T from F.** T runs judged principal-axis or coordinate-plane views by eye. GPT-5.5 code r2 saw a "top crossbar with a central vertical stem" in a PCA view (`open_ended_code_codex_gpt_5_5_r2/...:L33-L37`). Sol galaxy r3 saw "a strong top bar plus central stem" in the x/y view (`galaxy_codex_gpt_5_6_sol_r3/...:L187`). F appears in an oblique side view where the light-chain arms sit off-centre. No T run searched for the source or scored letter shapes quantitatively beyond rough checks.

**Interpretation.** The key is well founded: the input is Howarth's "F" structure, confirmed at the coordinate level. The working reference `T` should be revised to `F`. T is a defensible visual reading of a subjective prompt, so the task is underspecified. Most DeepSeek credit comes from source retrieval rather than shape analysis.

**Tags:** `reference-questionable`, `benchmark-answer-retrieval`, `underspecified-task`, `route-divergence`

---

<a id="tissue-fibroblast-q1"></a>

### tissue-fibroblast-q1 — "Omentum" is the published atlas label; "Lung" is what the cell's expression says

**Question.** Two barcodes in an anonymized 21,087 × 12,058 mouse fibroblast count matrix. Name the tissue each one came from, choosing from a fixed list.

**Reference.** `Lung,Bone` (score-inferred, unique). The working reference `Omentum,Bone` (16/25 runs) disagrees on the first cell.

**Outcome.** Galaxy 5/12, code 3/13. Wrong answers: `Omentum,Bone` from 16 runs (GPT-5.5 G r1/r2, Sol G r2/r3, DeepSeek G r1/r2, and 10 code runs); `Adipose,Omentum` from DeepSeek G r3.

**What the traces show.**
- **How the Omentum runs got their answer.** They identified the matrix as a 10% subset of the FibroXplorer steady-state atlas (Buechler 2021, `Mouse_SS_Fibro.RDS`, 3.04 GB, 120,583 cells). They downloaded it and matched each query column exactly on the full count vector. Cell_11249_MCI matches exactly one source cell, `ATCTGCCCATCGATTG-1_3`, with metadata `Cluster=4, ClustName=Npnt, Tissue=Omentum`. Cell_10369_WXV matches `AACACGTCAGCAGTTT-1_1_1` (`Cxcl12`, Bone). Evidence: `open_ended_code_codex_gpt_5_5_r3/.../codex_events.jsonl.gz:L70`, `galaxy_codex_gpt_5_6_sol_r2:L83`, `galaxy_codex_gpt_5_5_r1:L123`. So the first answer is a metadata lookup, not an inference.
- **What the expression says.** The same source cell sits in the atlas's `Npnt` cluster, which is the lung alveolar fibroblast state. Its top genes are lung alveolar-fibroblast markers: Inmt 25, Mgp 25, Mfap4, Fmo2, and Npnt/Limch1 among nearest-neighbour markers. In the paper's supplementary signatures, Npnt has logFC 9.7 in "Lung Fibroblast" (`open_ended_code_codex_gpt_5_6_luna_r1:L134`). Luna code r1 said the markers "point to Lung and Bone" (L194) and then let the metadata override that (L266→L267).
- **How the Lung runs got their answer.** They inferred tissue from expression: Astra used PCA neighbours (L13→L14), Luna G r3 mapped the `Npnt+` atlas state to Lung (L355), GPT-5.5 G r3 and Luna G r2 scored against the paper's marker tables. Sol G r1 also tried the exact match, but the Galaxy job reading the 3 GB object never finished, so it fell back to markers (L80→L87). None of the Lung runs completed an exact metadata match.
- **Adipose,Omentum.** DeepSeek G r3 treated the numeric part of the barcode (11249, 10369) as a row index into the atlas metadata, using sed/head in Galaxy (L1808–L1834). GPT-5.5 G r2 made the same mistake first (Visceral Adipose), then rejected it after the exact match (L94→L112).
- **Where the computation ran for correct Galaxy runs.** GPT-5.5 G r3 installed R with micromamba and scored markers locally (L172–L199). Luna G r1 used local Python `rdata` plus neighbours after the Galaxy scheduler stalled (L471–L485). Sol G r1, Luna G r2 and Luna G r3 ran the decisive steps as Galaxy UDT jobs.
- **Lookups of benchmark material.** Luna G r2 used GitHub search to reach the lab's public results page, which shows "Estimated answer Omentum,Bone" and earlier runs' answers (L74). It still answered Lung. Several runs also probed the CompBioBench Hugging Face leaderboard and submissions repos (`galaxy_codex_gpt_5_6_luna_r1:L462–L466`, where the submissions repo returned 401). No answer key was obtained.

**Interpretation.** The two answers come from two different sources of truth. `Omentum` is the atlas-provided Tissue label for this exact cell. `Lung` is what its expression and cluster (`Npnt`) indicate, and the hidden key follows the biology. The working reference `Omentum,Bone` should be replaced by `Lung,Bone`. The 16 Omentum runs did an honest source-metadata lookup, but that bypasses the intended inference and meets an apparent mislabel for this cell. The item is ambiguous about which is "truth", but not scientifically wrong.

**Tags:** `reference-questionable`, `benchmark-answer-retrieval`, `route-divergence`, `local-fallback-in-galaxy`, `underspecified-task`

---

<a id="odd-one-out-q1"></a>

### odd-one-out-q1 — only runs that tested the Tn5 9-bp stagger chose 4; others picked quality or cell-line outliers

**Question.** Ten depth-matched ENCODE-style hg38 tagAlign files (10 M × 50 bp each). Nine come from the same assay and one from a different assay. Give the index of the outlier.

**Reference.** `4` (score-inferred, unique). The working reference `8` disagrees.

**Outcome.** Galaxy 4/12, code 5/13. Wrong answers: `9` from 11 runs (GPT-5.5 G r1/r3 and code r1–r3, DeepSeek G r2, Luna G r1–r3 and code r1/r2); `8` from DeepSeek G r1 and code r2, and Luna code r3; `1` from Sol G r1 and DeepSeek code r1.

**What the traces show.**
- **Why 4.** File 4 alone has the Tn5 insertion hallmark: a sharp peak between opposite-strand 5′ ends at +8/9 bp. In Sol code r1, the +8 offset is 3.93× the local baseline for file 4 and 0.91–1.08× for every other file (`open_ended_code_codex_gpt_5_6_sol_r1/.../codex_events.jsonl.gz:L30,L37`). In Sol G r2, file 4 has 10,141 pairs at 9 bp (3.15×) versus 0.95–1.09× for the rest, computed in a Galaxy UDT (`galaxy_codex_gpt_5_6_sol_r2:L150`). Sol G r3 finds the same with a Galaxy cleavage-motif and endpoint-offset job (L54). File 4 is also the only file that keeps chrEBV and 129 alt/unplaced contigs, i.e. it went through a different pipeline (`galaxy_codex_gpt_5_5_r2:L265`, `galaxy_codex_gpt_5_6_sol_r3:L33`). It also has the lowest 1-Mb coverage correlation with the others (0.956 vs about 0.98). GPT-5.5 G r2 answered 4 on that correlation alone (`:L329`); that is weaker evidence, and the final correlation was computed locally from Galaxy `bedtools coverage` outputs. Every file shows TSS enrichment (5.4–13.7×), so the nine are another accessibility-type assay (probably DNase-seq) and file 4 is ATAC-seq.
- **Why 9 (the modal wrong answer).** 20.6% of file 9's reads fall in one 1-kb bin at chr11:24,159,000 (2,059,145 tags), which also gives it extreme strand skew. GPT-5.5 code r3 read that as the assay outlier (`:L19,L35→L36`). But file 10 has the same pile-up (141,340 tags), so it is a repeat or artifact locus in two samples, not an assay property. Luna code r3 said as much (`:L355`).
- **Why 8 (the working reference).** File 8 is the flattest, lowest-enrichment profile: max bin 549, only 2,525 windows above 100 tags, and no clear strand-correlation peak (`open_ended_code_codex_deepseek_v4_pro_0813_r2:L165→L169`; Luna code r3 L446–L608, "broad, low-peak profile"). That makes it a signal-to-noise or library-quality outlier, not a chemistry difference.
- **Why 1.** Sol G r1 chose the file whose top genomic bins overlap least with the others (L138). That is a cell-line effect; each file comes from a different cell line by design.
- **Lookups of benchmark material.** DeepSeek code r1 fetched the leaderboard app and was refused by the submissions repo (401); Luna code r3 also probed the leaderboard. No key was obtained (L118–L128).

**Interpretation.** The prompt does not say what counts as the "assay" difference, and most runs ranked generic outlier statistics that pick up quality, artifact or cell-line differences. The only assay-chemistry test run, the Tn5 9-bp stagger, isolates file 4 cleanly, so the key `4` is well supported and the working reference `8` should be revised to `4`.

**Tags:** `reference-questionable`, `scientific-method-error`, `insufficient-verification`, `route-divergence`, `underspecified-task`

---

<a id="contaminated-rna-q2"></a>

### contaminated-rna-q2 — EBV (the sample's own lymphoblastoid virus) outranks the spiked-in pig reads unless human reads are removed first

**Question.** Name the contaminant species in a single-end human RNA-seq FASTQ, as a lowercase binomial.

**Reference.** `sus scrofa` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 7/12, code 6/13 correct. Wrong answers: `lymphocryptovirus humangamma4` from GPT-5.5 galaxy r2 and r3, Sol galaxy r2, Luna galaxy r2, DeepSeek code r1 and Luna code r1; `human gammaherpesvirus 4` from Luna galaxy r3 and Luna code r2; `rattus norvegicus` from GPT-5.5 code r3 and DeepSeek code r2 and r3; `mus musculus` from GPT-5.5 code r1.

**What the traces show.**
- **EBV (8 runs; both names refer to the same species).** Epstein-Barr virus is real and abundant in this sample. It is consistent with an EBV-transformed lymphoblastoid cell line (LCL) source, so it belongs to the sample rather than being the spike-in.
  - After HISAT2 removal of hg38 reads, Kraken2 finds human gammaherpesvirus 4 = 523 reads versus Sus scrofa 199 + Suidae 108 (`galaxy_codex_gpt_5_5_r1/.../codex_events.jsonl:L80`).
  - Runs that ran Kraken2 on *all* reads saw pig at 238 reads, next to primate misassignments (Gorilla 245, Callithrix 221) (`galaxy_codex_gpt_5_6_sol_r2/...`).
  - Those runs dismissed the mammal calls as "scattered across many mammalian branches" and picked the one coherent non-mammal clade, EBV (`galaxy_codex_gpt_5_5_r2/...:L47-L53`).
  - Luna code r1 saw separate pig, EBV and Staphylococcus clusters and chose EBV as "dominant" (`open_ended_code_codex_gpt_5_6_luna_r1/...:L131-L169`).
- **Rat/mouse from a closed candidate panel.** GPT-5.5 code r3 mapped the enriched reads only to mouse, rat, fly, worm, yeast and zebrafish cDNA; pig was never a candidate (`open_ended_code_codex_gpt_5_5_r3/...:L68-L74`). GPT-5.5 code r1 similarly compared rodents only (blastx on the NCBI "landmark" protein database, then rat/mouse/*Mus caroli* mapping) (`...gpt_5_5_r1/...:L201-L231`).
- **Copied from leaked traces.** DeepSeek code r2 and r3 downloaded `compbiobench.v1.tsv` and another agent's published trace for this exact question (`amanutej/trustworthy-biology-agents-traces`, codex_gpt-5.5 run). They then repeated its human/mouse/rat-only mapping and its `rattus norvegicus` answer (`open_ended_code_codex_deepseek_v4_pro_0813_r2/...:L70-L122`; r3 `:L36-L72`, where it reports "codex method counts").
- **Correct runs removed human reads first.** They filtered host reads, then classified the rest against an open database. GPT-5.5 galaxy r1 ran HISAT2 hg38 (97.24% mapped), then Kraken2 core_nt on the 5,959 unmapped reads, then confirmed with a susScr3 mapping. All of this ran as Galaxy jobs (`L69-L87`). No correct Galaxy run issued a local aligner or classifier command. DeepSeek galaxy r1 (correct) also read the leaked trace and web-searched answer strings (`L105-L132`, `L280-L284`). Sol code r2 cloned the leaderboard Space looking for ground truth (`L146-L150`).

**Interpretation.** The key is sound: pig is the spike-in, and EBV is expected biology in LCL-derived RNA-seq. The EBV answers are a genuine domain-knowledge miss, not an equivalent answer: they did not remove host reads and did not recognise EBV as part of an LCL sample. Two rat answers are contaminated by retrieving benchmark traces, as is one correct run.

**Tags:** `domain-knowledge-error`, `scientific-method-error`, `benchmark-answer-retrieval`, `insufficient-verification`

---

<a id="contaminated-rna-q3"></a>

### contaminated-rna-q3 — Two real contaminants; the spiked chimpanzee reads disappear with primate-free databases or human subtraction, leaving a minor real Mycoplasma signal

**Question.** Name the genus of the most likely non-human organism in a 240k-read human single-end RNA-seq FASTQ, or "none".

**Reference.** `pan` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 8/12, code 6/13 correct. Wrong answers:
- `mesomycoplasma` — GPT-5.5 Galaxy r3, Sol Galaxy r3, Sol code r1, DeepSeek code r1/r3, Luna code r1/r2/r3, Astra
- `mycoplasma` — DeepSeek Galaxy r2
- `rattus` — Sol Galaxy r2

**What the traces show.**
- **Both signals are real, but at very different sizes.** Kraken2 against Galaxy's `core_nt` (which contains great apes) gives Homo 33,703, **Pan 6,271**, Pongo 371, Gorilla 277 (`.../contaminated-rna-q3/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_6_luna_r3/.../codex_events.jsonl:L127`). *Mesomycoplasma hyorhinis* is also genuinely present, but only as roughly 40-140 reads. They align at 98.6-100% identity across the whole chromosome (`.../galaxy_codex_gpt_5_6_sol_r3/.../codex_events.jsonl:L23`), which fits a mycoplasma-infected source cell line rather than the designed spike.
- **Chimp reads vanish in two ways.**
  1. The Kraken2 database has no non-human primates (Standard-16, PlusPF, PlusPFP).
  2. Reads are first subtracted against hg38, and chimp reads, about 99% identical to human, map to hg38 and are discarded. What remains is the bacterial signal.

  Sol Galaxy r3 did both: bowtie2 hg38 subtraction, then PlusPFP on the 26,859 residual reads, giving Mycobacterium 54 and Mesomycoplasma 38 (`run_trace/codex_events.dns_interrupted_20260822T071126Z.jsonl:L298`, `L437`). Most code runs that answered mesomycoplasma searched only unmapped reads (for example Luna code r1, "118 reads align across ... M. hyorhinis", `L95`). Luna code r2 built a chimp/gorilla score comparison, but its script returned empty output (`L247-L253`). It moved on and then probed the CompBioBench Hugging Face and GitHub repos for answers (`L273`, `L289-L293`).
- **Galaxy platform defect.** In GPT-5.5 Galaxy r3 the `core_nt` Kraken2 job was killed by Slurm ("CANCELLED ... DUE TO TIME LIMIT") yet left in Galaxy state `ok` with empty outputs (`.../galaxy_codex_gpt_5_5_r3/...:L44-L45`). The agent fell back to `standard_16gb` (no chimp) and answered mesomycoplasma (`L101`, `L216-L223`). Sol Galaxy r3 hit the same empty "successful" `core_nt` output (`L272` of its interrupted segment).
- **`mycoplasma`.** DeepSeek Galaxy r2 classified a 5,326-read subset with `k2_pluspf_20210517` (`L247`). That database predates the reclassification to Mesomycoplasma, so it reports "Mycoplasma hyorhinis". This is the same organism under its older genus name.
- **`rattus`.** Sol Galaxy r2 hit a chain of Galaxy failures: an orphaned `core_nt` job (`L215`), DIAMOND jobs never assigned and then missing the NR taxonomy SQLite (`L302`, `L372`), a frozen BLASTN (`L498`) and HISAT2 exit 127 (`L617`). It then mapped the residual reads to a panel with no primate genome (`L498-L541`). It called rat from conserved-background counts of 1,001 vs 960 reads (3.85% vs 3.69%; `L508`, `L634`).
- **Where the correct Galaxy runs computed.** Kraken2 `core_nt`, Kraken2Tax and datamash all ran as Galaxy jobs (for example the Luna r1 history jobs). Galaxy's advantage here is that the prebuilt `core_nt` index was available with one click.

**Interpretation.** Mesomycoplasma and mycoplasma are real (the same organism) but minor, so they are not the most likely contaminant. The errors come from reference-database coverage and human-subtraction order, not from inventing an organism. The Galaxy `ok`-but-empty timeout is a platform defect that pushed two Galaxy runs onto primate-free databases.

**Tags:** `galaxy-platform-defect`, `route-divergence`, `domain-knowledge-error`, `source-version-drift`, `insufficient-verification`, `underspecified-task`

---

<a id="lung-cancer-sc-q1"></a>

### lung-cancer-sc-q1 — "malignant basal" means all LUSC basal cells (46% -> 40) in the key, but the paper's 8,016 "malignant basal" subset gives 17% -> 20

**Question.** Using an h5ad that holds only counts and `sampleID`, pick the LUSC sample among five candidates with the highest dendritic-cell (DC) fraction. Then give the share of all non-immune cells that are malignant basal cells from LUSC patients, rounded to the nearest 20%.

**Reference.** `Patient_018;40` (score-inferred). The lab's working reference is `Patient_018;20`.

**Outcome.** Galaxy 9/12, code 6/13 match the key. Wrong answers: `Patient_018;20` came from GPT-5.5 Galaxy r1 and code r3, Sol code r1 and r2, DeepSeek Galaxy r2 and r3 and code r3, and Luna code r1 and r2. `Patient_005;40` came from Astra code r1.

**What the traces show.**
- The first part is settled. Most runs matched every cell barcode, at 100%, to the study portal's `meta.csv` (lungcancer.chenlulab.com; Zhang et al., STTT 2021). Among the five candidates, only Patient_018 (PS03, DC 6.3%) and Patient_040 are LUSC (`open_ended_code_codex_gpt_5_5_r3/.../codex_events.jsonl.gz:L90`). Astra never confirmed histology. It took the top DC sample, Patient_005, which is LUAD in the source (DC 19.1%) (`open_ended_code_codex_gpt_6_astra_r1/...:L100-L234`).
- **What gives 40.** Numerator: every `CellName=Basal` cell in LUSC samples (21,739). Denominator: all non-immune cells (47,161). That is 46.1%, which rounds to 40. The calculation ran as a Galaxy UDT in Sol Galaxy r3 (`galaxy_codex_gpt_5_6_sol_r3/...:L91`) and with Galaxy Filter/Count tools in GPT-5.5 Galaxy r2 (21,739/51,338 = 42%, `...:L201-L206`). Both are genuine Galaxy computations.
- **What gives 20.** The runs read "malignant" as a stricter subset:
  - **Paper's subset.** Fig. 7 of the paper describes "UMAP of 8016 malignant basal cells from LUSC", and the portal's `/api/coord?cell=Basal&disease=LUSC` endpoint returns exactly those 8,016 cells. 8,015 of them fall in the benchmark, giving 17.0%, which rounds to 20 (GPT-5.5 code r3 `L93-L96`; Luna code r2 `L118`). One of the 8,016 comes from a Normal-tissue sample (`L120`).
  - **Ad hoc marker filter.** GPT-5.5 Galaxy r1 found 46.2%, which rounds to 40 (`L213`). It then kept only basal cells expressing KPNA2, MKI67 or similar markers, giving 29.4% and rounding to 20 (`L229`). DeepSeek code r3 did something similar (22.5%).
  - **Inflated denominator.** DeepSeek Galaxy r3's marker calls produced 81,660 non-immune cells, giving 26.8% (`L511`).
  - **No stated reason.** Sol code r1 and r2 both computed 46.1–46.5% (`L89`; `L60`) and still answered 20. Sol r2 looked at the paper's inferCNV figure first.
- **Answer lookups.** Sol code r1 (`L91`) and Sol Galaxy r3 (`L94`) searched GitHub and Hugging Face for "lung-cancer-sc-q1" answers. Neither search visibly returned anything.

**Interpretation.** The two answers differ only in what "malignant basal" means. The working reference of 20 likely follows the paper's explicit definition: the 8,016 inferCNV-defined malignant basal cells. The key treats every basal-labelled cell in LUSC tumours as malignant. The task does not say which it wants, so 20 is scientifically defensible and arguably closer to the source study. The 40-vs-20 split is not a Galaxy-vs-code effect.

**Tags:** `underspecified-task`, `reference-questionable`, `equivalent-answer`, `domain-knowledge-error`, `benchmark-answer-retrieval`

---

<a id="annotate-variant-regulatory-overlap-q1"></a>

### annotate-variant-regulatory-overlap-q1 — Same cCRE in every run; "pELS" and "Proximal enhancer" are two spellings of one class, from different v4 distributions

**Question.** Find the ENCODE cCRE Registry v4 element that overlaps GRCh38 chr19:44,907,187 G>A (the APOE region) and report `class,accession`.

**Reference.** `pELS,EH38E1957012` (score-inferred; the working reference is the same).

**Outcome.** As scored locally: Galaxy 7/12, code 9/13. Wrong answers: `Proximal enhancer,EH38E1957012` in 9 runs (GPT-5.5 Galaxy r2/r3, GPT-5.5 code r2/r3, Sol Galaxy r2/r3, DeepSeek Galaxy r1, DeepSeek code r2/r3). All 25 runs report the same accession, EH38E1957012 (BED chr19:44907067-44907293). No run got the accession wrong.

**What the traces show.**
- **Source of "Proximal enhancer": UCSC's ENCODE4 registry track.** This is track `cCREregistry`, backed by `/gbdb/hg38/encode4/ccre/encodeCcreRegistry.bb` (bigBed 9+5). Its `cCRE_class` column spells out the ELS/PLS classes ("Proximal enhancer", "Distal enhancer", "Promoter") but keeps the short codes for others (CA, TF, CA-CTCF...). Evidence: GPT-5.5 Galaxy r2 has a UDT that calls `api.genome.ucsc.edu/getData/track?...track=cCREregistry` and returns `"cCRE_class": "Proximal enhancer"` (`.../galaxy_codex_gpt_5_5_r2/.../codex_events.jsonl:L22-L26`). Sol Galaxy r3 and DeepSeek Galaxy r1 stage `encodeCcreRegistry.bb` into Galaxy (SHA-256 `b510ae8b…`) (`galaxy_codex_gpt_5_6_sol_r3/...:L20-L38`, `galaxy_codex_deepseek_v4_pro_0813_r1/...:L40-L55`). DeepSeek code r2 tallies the label set in this file (`open_ended_code_codex_deepseek_v4_pro_0813_r2/...:L46`). All 9 label-form runs used this UCSC file or API.
- **Source of "pELS": ENCODE/SCREEN native files.** These include ENCODE portal file `ENCFF420VPZ.bed.gz` (annotation ENCSR800VNX, column 10 = `pELS`), used by Luna code r1 (`...luna_r1/...:L29-L33`), Luna Galaxy r1, Luna code r2/r3 and Sol r1 in both conditions. Other sources were Wenglab `downloads.wenglab.org/Registry-V4/GRCh38-cCREs.bed`, used by GPT-5.5 Galaxy r1 through the Galaxy bedtools intersect wrapper (`...gpt_5_5_r1/...:L56`), and the SCREEN GraphQL API (`"group":"pELS"`). DeepSeek Galaxy r2 first saw "Proximal enhancer" in UCSC, then switched to the SCREEN code form (`...deepseek_v4_pro_0813_r2/...:L100-L109`).
- **Leaderboard submission (lead-auditor finding).** The coordinator verified this; I did not re-derive the hashes. For these 9 runs, the archived `predictions.tsv` bytes do not match the advertised leaderboard SHA-256. Replacing "Proximal enhancer" with "pELS" reproduces the advertised hash exactly for all 9. The GPT-5.5 code campaigns are labelled `gpt55-anycode-r1/r2`, which correspond to brief r2/r3. So the leaderboard received "pELS" for every run and credited all 25. The raw traces and `answer.txt` still say "Proximal enhancer".

**Interpretation.** Every answer is correct. "Proximal enhancer" is UCSC's display label for the SCREEN class pELS in the same v4 registry. The 7/12 vs 9/13 split reflects only whether a run took UCSC or ENCODE/SCREEN as its source, not Galaxy capability. Local scoring should count the label form as equivalent. The official scores give no evidence on whether the hidden key accepts the label form, because the submissions were normalized.

**Tags:** `equivalent-answer`, `evaluator-false-negative`, `format-contract-error`

---

<a id="characterize-response-q1"></a>

### characterize-response-q1 — The gene list is a published MSigDB set (CUI_CDC2_LIF_RESPONSE_UP); runs that found it were right, and runs limited to Enrichr/C7 enrichment defaulted to LPS

**Question.** An ordered, same-sign list of 112 mouse DE genes is given. Pick the most specific condition;cell-type pair from 12 conditions (including LPS, the cytokines LIF and IL-39, sepsis) and 7 immune cell types.

**Reference.** `c;v` (LIF; dendritic cells), score-inferred. The working reference agrees.

**Outcome.** Galaxy 6/12, code 10/13. Wrong answers: `a;i` — DeepSeek Galaxy r1–r3, DeepSeek code r2, Luna Galaxy r1–r2; `a;v` — DeepSeek code r1, r3; `f;iii` — Luna Galaxy r3.

**What the traces show.**
- **Correct runs identified the source gene set.** GPT-5.5 Galaxy r1: "The complete ordered list exactly matches an MSigDB mouse gene set named `CUI_CDC2_LIF_RESPONSE_UP`" (`.../galaxy_codex_gpt_5_5_r1/.../codex_events.jsonl.gz:L24`). Sol Galaxy r1 downloaded that set by name (`galaxy_codex_gpt_5_6_sol_r1:L40`). Luna code r2 scraped the set's MSigDB page (L79). The set is the Immune Dictionary (Cui et al.) cDC2 response to LIF, so `c;v` is the literal source label.
- **Where the Galaxy runs did the decisive step.** The identification came from web lookup in the agent shell. Galaxy was used only afterwards, for an overlap check in a UDT (GPT-5.5 r1 L27–L48). The Galaxy runs are correct, but Galaxy analysis was not what solved them.
- **Answer-seeking.** Luna code r1 answered after three web searches, one of which was `"characterize.response.q1.txt" answer` (L13), with no analysis at all (L20).
- **DeepSeek (all 6 wrong).** It ran Enrichr/C7 enrichment via the Galaxy `gseapy_enrichr` wrapper and staged GMTs. Top hits were generic, e.g. GSE35685 bone-marrow and GSE17186 B-cell sets. It then filtered for `LPS` terms and picked LPS plus monocyte or DC markers (Mafb, C1qc, Clec4n) (`galaxy_codex_deepseek_v4_pro_0813_r1:L260–L266`). It never found the CUI set. Its download of the 2026.1 mouse GMTs returned a login HTML page (L202–L208), and it fell back to m8 v2024.1 and human C7, neither of which holds the Immune Dictionary signatures.
- **Luna Galaxy (3 wrong vs 3 right in code).** In Galaxy it stayed inside the installed Enrichr wrapper. r1 settled on "LPS-specific macrophage signatures" (L68–L239). r3 over-read a 17-gene overlap with a GSE4479 septic CD4-splenocyte set and answered `f;iii` (L308), a lymphoid call for a myeloid list. In code, the same model web-searched and found the source set.

**Interpretation.** These are genuine errors, not equivalent answers. LPS dominates the Enrichr/C7 libraries, so enrichment there yields a non-specific "myeloid activation → LPS" call. The Galaxy-versus-code gap for Luna is a route effect: staying within Galaxy-installed enrichment excluded the one source that resolves the task. The task is solvable by source lookup; enrichment evidence alone does not decide it.

**Tags:** `route-divergence`, `domain-knowledge-error`, `insufficient-verification`, `benchmark-answer-retrieval`

---

<a id="conservation-lookup-q1"></a>

### conservation-lookup-q1 — Every wrong vector comes from one +9 artefact: ortholog gene models with 3 extra upstream codons (ATG GGC GAG, "MGE")

**Question.** Take the human SHH MANE cDNA from the start codon to the end of exon 1 (300 nt). Get the orthologous segment for 7 species and report Levenshtein distances in the listed order.

**Reference.** `0,7,0,20,5,24,27` (score-inferred). The working reference agrees.

**Outcome.** Galaxy 7/12, code 9/13. Wrong answers: `9,16,0,20,5,24,35` (GPT-5.5 Galaxy r1); `9,16,9,20,5,24,35` (DeepSeek Galaxy r3, DeepSeek code r1); `9,16,0,29,5,24,35` (DeepSeek code r2); `9,16,9,29,14,24,35` (DeepSeek code r3, Luna code r2); `9,16,9,20,5,24,36` (Luna Galaxy r1); `9,16,0,20,14,24,36` (Luna Galaxy r2); `9,16,0,20,5,24,36` (Luna Galaxy r3).

**What the traces show.**
- **The shared mechanism.** The Ensembl canonical models for chimp (ENSPTRT00000109799), macaque and beluga begin at an in-frame ATG 9 nt upstream of the codon aligned to the human Met. Ensembl's own homology alignment shows it: human `---MLLLARC...` versus chimp `MGEMLLLARC...` (`.../galaxy_codex_gpt_5_5_r2/.../codex_events.jsonl:L20`). Runs that cut each ortholog "from its own annotated start codon" got 309-nt segments, adding exactly 9 to the distance (chimp 0→9, macaque 7→16, beluga 27→35). In GPT-5.5 Galaxy r1's diagnostics each species has `distance` (own start codon) next to `cactus_distance` (human-aligned region). The `cactus_distance` values are exactly the reference, 0,7,0,20,5,24,27 (`galaxy_codex_gpt_5_5_r1:L156`).
- **Species-specific variants follow from the model chosen.** Bonobo is 0 with the Ensembl model (300-nt first exon, CDS from base 1) and 9 with a RefSeq/Gnomon model that has the same extension.
- Indri 29 and Semnopithecus 14 appear when a run replaced the alignment-derived 300-nt segment with the "longest available RefSeq/assembly model". Luna code r2 first had a clean 300-nt Indri segment and a 5-substitution langur hit, then switched "so the transcript-choice rule is applied consistently" (L169–L231, answer at L451).
- Beluga 35 versus 36 is the Ensembl model versus the longest RefSeq model, XM_022576607.2 (Luna Galaxy r1 L117).
- **Correct runs** anchored each ortholog to the region aligned with the human exon-1 CDS, discarding the upstream extension. For the two species missing from Ensembl they used Cactus 447-way or assembly search.
- **Computation location.** In correct Galaxy runs the distances were computed in Galaxy UDT jobs over staged source bundles (GPT-5.5 r2 `compute-shh-exon1-distances-v1`; DeepSeek r1 `shh-distance-v1`). No local shortcut was found for the distances. Source retrieval (Ensembl/NCBI REST) happened in the shell and was staged in.

**Interpretation.** This is a single definitional error, not seven independent ones. The prompt asks for the segment "corresponding to the same region", and the reference follows that alignment-anchored reading. Distances from the orthologs' own upstream ATG measure an annotation artefact, and the extra "MGE" codons are not in the human protein. The reference is sound. The wording "canonical/longest transcript" encourages the trap, so the task is mildly underspecified.

**Tags:** `scientific-method-error`, `underspecified-task`, `source-version-drift`

---

<a id="ep-interactions-q1"></a>

### ep-interactions-q1 — F answers came from averaging over guides, which hides EP3's single-guide effect

**Question.** Integrate Hi-C-like contact counts (with a distance-matched background) and CRISPR perturbation expression data (4 guides × 3 replicates per pair), and pick the E-P pair least consistent with a true causal interaction (A-G).

**Reference.** `C` (EP3) (score-inferred; the working reference is the same). The July lab hint (reference `A`, "signed effect criteria") is stale: EP1's consistent up-regulation marks a real repressive element, not a non-causal one.

**Outcome.** Galaxy 9/12, code 8/13. Wrong answers: `F` (EP6) in 8 runs: every GPT-5.5 run (3 Galaxy, 3 code), Sol code r1 and DeepSeek code r1.

**What the traces show.**
- **The data.** EP3 has the strongest distance-adjusted contact (mean 19.3 vs ~6.4 expected, z≈2.2). Its expression drop comes from a single guide: g3 has ratio 0.47, while g1/g2/g4 have ratios 0.99-1.00. Pooled over guides, EP3 falls only 13% (Welch p=0.086). EP6 has weak contact (4.3 vs 5.4 expected) but a small, concordant drop across all four guides (0.83-0.86; pooled p=0.0013). All of this is visible in `open_ended_code_codex_gpt_5_5_r1/.../codex_events.jsonl.gz:L10-L18`.
- **Why runs chose F.** They scored each pair on contact enrichment plus pooled knockdown, and EP6 is the only pair weak on both. GPT-5.5 code r1 actually printed EP3's per-guide ratios (sd 0.26, with only g3 responding), then fell back to pooled t-tests and answered F with no narration (`...:L16-L19`). GPT-5.5 Galaxy r2/r3 used Galaxy Datamash with `grouping: "1,3"` (pair_id, condition). That drops `guide_id`, so the one-guide artifact becomes an ordinary modest mean decrease (`galaxy_codex_gpt_5_5_r3/...:L96-L114`). GPT-5.5 Galaxy r1's UDT ranked pairs by "enriched contact + decreased expression" plus a signed/absolute sensitivity check, and also never tested guide concordance (`galaxy_codex_gpt_5_5_r1/...:L25-L43`).
- **What correct runs did.** They tested guide concordance. Sol Galaxy r1: "EP3 has exceptionally strong distance-adjusted contact, but three of four guides show essentially no expression response and the apparent mean effect is driven by one guide" (`galaxy_codex_gpt_5_6_sol_r1/...:L24`). That run computed everything in three Galaxy UDT jobs (contact diagnostic, expression diagnostic, integrated score; `L20-L28`), with no local fallback.

**Interpretation.** This is a genuine scientific-reasoning error: standard CRISPRi practice requires concordance across independent guides, and a single discordant guide suggests an off-target effect. F is not an equivalent answer, since EP6's effect is reproducible across guides. The error follows the model (all six GPT-5.5 runs), not the platform. In Galaxy, choosing Datamash grouping keys that omit guide_id built the error into the summary itself.

**Tags:** `scientific-method-error`, `statistical-error`, `insufficient-verification`

---

<a id="exogenous-mix-reads-q2"></a>

### exogenous-mix-reads-q2 — The three FASTQs are nested prefixes; `90` counts a file-construction artifact, not an exogenous signal

**Question.** Estimate the percentage of exogenous (Sendai-KLF4) reads in the mix FASTQ, to the nearest 10. The inputs are a purely exogenous early file and a predominantly endogenous late file, with no construct sequence. Answer `NA` if an estimate is not possible.

**Reference.** `NA` (score-inferred; the working reference agrees). An unverified July lab note that compared `90` against `40` is superseded.

**Outcome.** Galaxy 7/12, code 10/13 correct. Wrong answers: `90` from GPT-5.5 Galaxy r1–r3 and code r2 and r3, Sol Galaxy r1, DeepSeek Galaxy r1. `40` from Sol code r1.

**What the traces show.**
- Every run that inspected the files found the same structure. The endo file (395 reads) is an exact record-for-record prefix of the exo file (592), and the exo file is an exact prefix of the mix (691). The mix has 99 extra reads. Endo has no sequence that is absent from exo (GPT-5.5 code r2 `open_ended_code_codex_gpt_5_5_r2/.../codex_events.jsonl:L17`, `L27`: "first 395 exo==endo True; first 592 mix==exo True").
- **Where `90` comes from.** 592/691 = 85.7%, which rounds to 90, obtained by treating record identity as provenance. GPT-5.5 Galaxy r1 said so explicitly: "since the exo dataset is assumed purely exogenous and all 592 of its records appear as the initial prefix of the … mix … rounds to 90%" (`galaxy_codex_gpt_5_5_r1/...:L39`). Sol Galaxy r1 wrapped the same logic as a "marker-rate correction" (`L24`). This uses how the files were built, not any exogenous-specific sequence.
- **Where `40` comes from.** Sol code r1 answered after only `comm`/`cmp`/`shasum` checks and a failed awk command. No calculation is shown (`L9-L14`). The answer matches (691−395)/691 = 42.8%, i.e. treating "not in the endo file" as exogenous, but that is my inference.
- **What the correct runs did.** Sol Galaxy r2 found the same nesting and concluded: "no independent endogenous sequence signature — only read-depth/order artifacts". It recorded NA in a terminal Galaxy UDT output (`L30-L35`). GPT-5.5 code r1 reached NA after mapping the read blocks onto the KLF4 RefSeq transcript (`L16-L30`).

**Interpretation.** A genuine reasoning error, and a reasonable key. Endogenous reads are sequence-identical to reads in the "pure exogenous" file, and no vector or UTR junction sequence is available, so no biological signal separates the two. The `90` answers exploit read-name and quality-string identity. GPT-5.5 gave `90` in all three Galaxy runs and two of three code runs, which points to a model tendency rather than a platform effect.

**Tags:** `scientific-method-error`, `domain-knowledge-error`, `insufficient-verification`

---

<a id="three-way-barnyard-q2"></a>

### three-way-barnyard-q2 — The 10/30/60 split depends on excluding about 90 low-purity "human" barcodes; lenient purity cutoffs or Alevin re-filtering give 20/30/50

**Question.** From 600 pre-thresholded 10x barcodes in a human/mouse/pig barnyard, give the rounded species percentages among confidently assigned single cells, plus each species' tissue.

**Reference.** `10;30;60;bone_marrow;lung;testis` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 8/12, code 9/13 correct. Wrong answers:
- `20;30;50;bone_marrow;lung;testis` — Luna Galaxy r1/r2, DeepSeek Galaxy r1, Sol code r2, DeepSeek code r2, Luna code r3
- `20;30;50;bone_marrow;lung;skin` — GPT-5.5 code r3
- `10;30;60;retina;heart;cortex` — DeepSeek Galaxy r3

**What the traces show.**
- **The underlying mixture is stable.** Pig ≈300 and mouse ≈150 barcodes are pure. The plurality-"human" class holds about 125-145 barcodes, but only about 50 are high purity; the rest carry only about 27-33% human reads. GPT-5.5 code r3's own purity sweep shows the answer flipping with the cutoff: frac≥0.6 gives [23,26,51], ≥0.7 gives [21,26,52], ≥0.8 gives [14,29,57], ≥0.9 gives **[10,30,60]** with 101 ambiguous barcodes excluded. It chose 0.7 (`.../three-way-barnyard-q2/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_5_r3/.../codex_events.jsonl:L87`).
- **Lenient calls (code runs, DeepSeek Galaxy r1).** Sol code r2 printed purity-ratio counts (ratio 3 gives human 53) but finalized with plurality assignment and no purity threshold: pig 300, mouse 174, human 126 (`.../open_ended_code_codex_gpt_5_6_sol_r2/...:L120`, `L136`). DeepSeek Galaxy r1 used human=144, mouse=156, pig=300 of 600, i.e. every barcode assigned (`.../galaxy_codex_deepseek_v4_pro_0813_r1/...:L120`). Both effectively count the mixed or ambient barcodes as human.
- **Alevin re-filtering (Luna Galaxy r1/r2).** These runs let Alevin's own cell detection re-threshold barcodes that were already pre-thresholded. Only 235-238 of 600 were kept, and the loss was mostly pig: human 51, mouse 76, pig 108 gives 22/32/46 (`.../galaxy_codex_gpt_5_6_luna_r1/...:L787-L794`; Luna r2 gives 52/74/112, `L765`). The prompt's "pre-thresholded" note warns against exactly this. The wrong value comes from the wrapper's default barcode selection.
- **Tissue errors.** GPT-5.5 code r3 counted KRT12 (a corneal keratin, 1,565 reads) plus KRT17 as "skin" and ranked it above the specific testis program (PRM1/2, TNP1/2: 666 reads; `L91-L93`). DeepSeek Galaxy r3 ran scanpy `score_genes` with human uppercase symbols on matrices keyed by Ensembl IDs (for example ENSMUSG; `L328`). All 20 mouse/pig tissue scores came out negative and within about 0.07 of zero, so it took the argmax of noise (`L1248-L1250`).
- **Correct Galaxy runs** computed in Galaxy. For example, GPT-5.5 Galaxy r1 did the minimap2 species assignment and marker scoring in a single UDT (`.../galaxy_codex_gpt_5_5_r1/...:L19-L25`).

**Interpretation.** The species percentages depend on an unstated "confidently assigned" purity threshold. A lenient but defensible cutoff gives 20;30;50, so the task is partly underspecified. Luna Galaxy's error is a wrapper-default re-filtering issue, not a species-calling error. The tissue misses are genuine marker-handling errors.

**Tags:** `underspecified-task`, `wrapper-semantics`, `statistical-error`, `domain-knowledge-error`, `format-contract-error`

---

<a id="afgr-1000g-intersect-atac-q1"></a>

### afgr-1000g-intersect-atac-q1 — The 50-sample answer misses Coriell `GM` cell-line IDs that should map to 1000G `NA` sample IDs

**Question.** Intersect the 1000G Phase 3 roster (3,202 individuals) with the AFGR ATAC-seq donors that have public GRCh38 filtered BAMs. Return the sample count and the md5 of the sorted list of BAM md5sums.

**Reference.** `83,1127bd47e06e7c19e8f0d5b5458a244a` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 8/12, code 10/13 correct. Every wrong run answered `50,054938323525a222bcc6154a05996ace`: DeepSeek galaxy r1 and r2, Luna galaxy r2 and r3, DeepSeek code r1 and r2, Luna code r3.

**What the traces show.**
- **All runs used the same source.** Every run used ENCODE's AFGR ATAC-seq metadata: 100 experiments, with one released GRCh38 `alignments` BAM and md5 per donor. The only difference was how the ENCODE "Biosample term name" was matched to 1000G IDs.
  - 50 donors are labelled `HG0xxxx` and match 1000G directly.
  - 50 are labelled with Coriell cell-line IDs `GM18xxx/GM19xxx/GM21xxx`. 1000G lists the same individuals as `NA18xxx/NA19xxx`.
- **Correct runs converted GM to NA.** Sol code r1 printed both joins side by side: "raw ATAC 100 inter 50" versus "gm_to_na ATAC 100 inter 83". The 17 left over are GM21xxx Maasai (MKK) HapMap samples, which are not in 1000G. The run then selected 83 BAMs with 83 unique md5s (`open_ended_code_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L40-L46`).
- **Wrong runs joined the raw strings.** DeepSeek galaxy r1 did this entirely with Galaxy text tools: `tp_grep` for bam/alignments/GRCh38, then `Cut1` c11,c46, `join1` against the 3,202 list, `secure_hash`, and `wc` → 50 (`galaxy_codex_deepseek_v4_pro_0813_r1/...:L154-L180`). Luna galaxy r2 noticed only half the donors matched. It blamed the 1000G index (thinking the file had 2,947 names rather than 3,202) and never checked the naming (`galaxy_codex_gpt_5_6_luna_r2/...:L185-L291`).
- **Where the computation ran.** The task is metadata only. Correct Galaxy runs did the join and hashing in Galaxy. For example, Sol galaxy r2 fetched ENCODE metadata with a UDT, web-searched "GM18907 NA18907 1000 Genomes" to confirm the mapping, then intersected and hashed in a second UDT (`galaxy_codex_gpt_5_6_sol_r2/...:L30-L38`). No local fallback matters here.

**Interpretation.** This is a genuine identifier-namespace error, not an equivalent answer. GM and NA IDs name the same Coriell individual, so 83 is scientifically right and the key is sound. The Galaxy runs that got 50 executed faithfully in Galaxy; the failure is domain knowledge, not the platform.

**Tags:** `domain-knowledge-error`, `insufficient-verification`

---

<a id="overexpress-tf-q1"></a>

### overexpress-tf-q1 — GC confounding: gained peaks are AT-rich, so without a GC-matched background AT-rich motifs beat KLF4

**Question.** From ATAC fragment files before and 48 h after TF-cocktail overexpression, pick the one cocktail member out of 10 candidate TFs.

**Reference.** `KLF4` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 7/12, code 11/13. Wrong answers: `PAX7` from GPT-5.5 code r2, DeepSeek G r3, and Luna G r2/r3; `FOXA1` from GPT-5.5 G r1; `SPI1` from GPT-5.5 G r2; `TCF7` from Luna code r3.

**What the traces show.**
- **The confounder.** Newly opened regions are much more AT-rich than stable ones: mean GC 0.395 in gained peaks versus 0.550 in stable peaks (`open_ended_code_codex_gpt_5_6_sol_r1/.../codex_events.jsonl.gz:L81`). The KLF4 motif (CACCC/GC-box) is GC-rich, so it looks depleted against unmatched backgrounds.
- **The correct route.** Sol code r1 stratified by fine GC, peak length and count. KLF4 comes out at 3.7–4.4× across three motif p-value cutoffs, while every other candidate is at 0.5–1.3× (L83). Logistic regression gives KLF4 OR 3.0 (L76). The top de novo k-mers are KLF boxes, CCCACCC and CCCACCCA at 4.7–5.6× (L96–L98). GPT-5.5 code r2 also saw that the full JASPAR table is "dominated by POU/SOX" (L213), consistent with an OSKM (OCT4/SOX2/KLF4/MYC) cocktail.
- **PAX7 and TCF7 runs.** These ran FIMO or MOODS on gained versus baseline or "matched" peaks with a uniform background and no GC matching. Luna G r3 gets PAX7 at 2.4–2.6× (`galaxy_codex_gpt_5_6_luna_r3:L245–L295`); Luna G r2 and DeepSeek G r3 use per-motif FIMO site counts (`:L453–L458`, `:L389–L390`). Luna code r3 adds a TCF7 "footprint" (L104–L157). The AT-rich homeobox/paired and HMG motifs are inflated by base composition.
- **FOXA1.** GPT-5.5 G r1 ran a Galaxy UDT on only the top 600 gained 500-bp bins, with a permissive PWM relative score of 0.85. Hit rates saturate (TCF7 89%, RUNX1 95%, ASCL1 90%), so the tests have little room to separate TFs. The raw ranking was TCF7; after blacklisting plus GC/count matching, FOXA1 edged ahead (OR 2.13, p = 6e-11) and KLF4 stayed below background (0.65 vs 0.77) (L49, L77). Its GC matching was against count-matched high-signal stable bins, which are mostly promoters, so it did not remove the bias.
- **SPI1.** GPT-5.5 G r2 measured library-normalized accessibility at all genome-wide JASPAR motif instances instead of motif enrichment in gained peaks. SPI1 was the only candidate not to decrease, and KLF4 came out at log2FC −0.28 (L163). That full-genome analysis ran locally ("dry run", L159–L190) because Galaxy UDT rendering failed (L124). Galaxy was used only for a SPI1-only `bedtools intersect` check, whose raw counts (51,933 → 64,006) were never normalized (L219).
- **Correct Galaxy runs.** GPT-5.5 G r3 used a Galaxy-native chain: MACS2 differential summits, `getfasta`, then FIMO (L225–L243).

**Interpretation.** Every wrong answer is a genuine statistical-method error: the enrichment test did not correct for the large GC shift between gained and background regions. Candidate-only motif scoring and permissive thresholds made it worse. The key is sound, and the answer is recoverable in both conditions when GC is controlled.

**Tags:** `statistical-error`, `scientific-method-error`, `insufficient-verification`, `local-fallback-in-galaxy`

---

<a id="finding-geo-q1"></a>

### finding-geo-q1 — wrong answers were unverified guesses; the correct source is an exact matrix match to GSM3578982

**Question.** Identify the GEO SuperSeries whose supplementary file produced a count-filtered 10x mouse h5ad (20,072 cells × 28,692 genes).

**Reference.** `GSE114176` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 8/12, code 11/13. Six wrong answers, all different: `GSE117542` (GPT-5.5 G r1), `GSE93421` (GPT-5.5 code r3), `GSE135737` (DeepSeek G r1), `GSE148115` (DeepSeek G r2), `na` (DeepSeek G r3), and `GSE102934` (DeepSeek code r2).

**What the traces show.**
- **The correct route.** The markers point to direct Ascl1/Neurog2 neuronal programming of mouse ES cells. The scRNA-seq SubSeries is GSE125620, and its SuperSeries is GSE114176, whose RAW.tar contains `GSM3578982_raw_gene_bc_matrices_h5.h5`. In Sol code r1, all 20,072 barcodes are present in the raw matrix, and the sparse data, indices and indptr are identical (`nnz 18,583,698`, 0 differing entries). The only differences are two reporter features the benchmark authors dropped (`ascl1V5`, `tubb3gfp`) (`open_ended_code_codex_gpt_5_6_sol_r1/.../codex_events.jsonl.gz:L40–L48`). No run answered with the SubSeries GSE125620, so SuperSeries versus SubSeries was never the failure.
- **GPT-5.5 G r1 (`GSE117542`).** It misread the cells as retina, then hypothalamus, then embryo (L159, L278, L354). Its own Galaxy check showed GSE117542 does *not* match: 85,103 cells, with only 2,251 barcodes overlapping after suffix normalization (L420). It answered GSE117542 anyway as the "best-supported" candidate (L425).
- **GPT-5.5 code r3 (`GSE93421`).** It matched a 10x E18 brain dataset on markers and file type, then abandoned the confirming HDF5 download (L351→L353).
- **The DeepSeek runs.** They searched the web on structural fingerprints ("28692" mm10 genes, barcodes) and on plausible tissues such as P2 cochlea and forebrain. They picked candidate SuperSeries without any matrix comparison (`galaxy_codex_deepseek_v4_pro_0813_r1:L216–L251`, `open_ended_code_codex_deepseek_v4_pro_0813_r2:L96–L120`). DeepSeek G r3 ran out of search leads and returned `na`.
- **Where the decisive check ran for correct Galaxy runs.** Sol G r2 and Luna G r2 did the exact comparison in Galaxy UDTs (`galaxy_codex_gpt_5_6_sol_r2:L65`, `galaxy_codex_gpt_5_6_luna_r2:L1886–L1892`). GPT-5.5 G r2 downloaded and matched the H5 locally, then only staged the source files into Galaxy (L711–L730). That is a local-computation fallback.

**Interpretation.** Every error is either a wrong biological context or answering without the exact-identity check the task invites. There is no reference problem. Runs that did the full matrix comparison always got GSE114176.

**Tags:** `insufficient-verification`, `domain-knowledge-error`, `no-answer`, `local-fallback-in-galaxy`

---

<a id="atac-tn5-shift-q1"></a>

### atac-tn5-shift-q1 — Wrong answers are 1-bp end-coordinate slips in motif-window scorers; two correct "Galaxy" answers were computed locally

**Question.** Infer the non-standard Tn5 shift (5' end; 3' end) applied to an hg38 scATAC fragment file, instead of the usual +4/−5.

**Reference.** `2;-1` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 11/12, code 9/13 correct. Wrong answers: `2;-2` from GPT-5.5 galaxy r1 and GPT-5.5 code r3; `3;-3` from GPT-5.5 code r1; `6;-6` from DeepSeek code r1; `2;-9` from Luna code r3.

**What the traces show.**
- **All runs used the same method.** They re-centred the palindromic Tn5 insertion motif on hg38 sequence around fragment starts and ends. The runs agree on the 5' side (+2) and differ by about 1 bp on the 3' side, which is where the half-open BED end convention matters.
- **GPT-5.5 galaxy r1 (`2;-2`) ran entirely in Galaxy UDTs.** Its end-motif information content was flat: end offset −3 scored 0.748 and −4 scored 0.725, pooled over chr1–6 (33,757 ends). Its pair score also rewarded exact reverse-complement agreement between start and end windows under its own coordinate model. That favoured the symmetric pair (2,−3), which maps to 2;−2 (js 0.0005), over (2,−4), which maps to the key 2;−1 (js 0.32) (`galaxy_codex_gpt_5_5_r1/.../codex_events.jsonl:L32-L38`). The reference therefore scored only 14th in its table because of a 1-bp end-convention assumption.
- **GPT-5.5 code r1 and r3 slipped the same way.** They found "start correction +1, end −2" with 6-mer bias windows and converted it to 3;−3 (r1, `L47-L52`) or 2;−2 (r3, `L45-L55`).
- **The two outliers were not recoveries.** DeepSeek code r1 (`6;-6`) and Luna code r3 (`2;-9`) both tried to find the benchmark's data or generator online. DeepSeek searched `"unknown.shift" "frag.bed"` and ChromBPNet `auto_shift_detect`. Luna searched Genentech `compbiobench-data-v1` and a GitHub generator (`L92-L100`; `L101-L111`). Neither found anything useful.
- **Correct runs.** GPT-5.5 galaxy r2 aggregated the autosomes and got "start +2, end −4 → 2;-1" (`L88`). Sol code r3 used a reverse-complement symmetry axis (`L23`).
- **Local fallback in two correct Galaxy runs.** GPT-5.5 galaxy r2 and r3 found that "this Galaxy server has no execution destination for user-defined tools". Even an upstream `cat` UDT failed (r2 `L58-L77`; r3 `L86-L92`). Both then ran the motif diagnostic **locally**: r2 ran `python atac_shift_diagnostic.py ...` (`L79-L91`); r3 used a local chr1 FASTA (`L94-L106`). r3 only uploaded a result table to Galaxy (`L109-L113`).

**Interpretation.** The key is well supported (20/25 runs). The near-misses are a 1-bp convention error on the half-open BED end, not an equivalent answer. The Galaxy score is inflated: 2 of the 11 correct Galaxy runs computed locally because a server-side UDT routing policy blocked all custom jobs.

**Tags:** `scientific-method-error`, `local-fallback-in-galaxy`, `galaxy-platform-defect`, `benchmark-answer-retrieval`

---

<a id="chip-pioneer-q1"></a>

### chip-pioneer-q1 — All five misses are Luna runs that scored bulk genome-wide fragment fractions instead of ChIP-enriched sites

**Question.** Using Chromap fragment BEDs for six overexpressed TFs (each with input) and BJ DNase-seq from ENCSR000EME, pick the TF with the most pioneering ability, judged from ChIP signal at 48 h.

**Reference.** `TF4` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 9/12, code 11/13 correct. Wrong answers: `TF1` from Luna Galaxy r2 and r3 and Luna code r2; `TF3` from Luna Galaxy r1 and Luna code r3. Every Luna run except code r1 is wrong.

**What the traces show.**
- **Luna Galaxy r2:** it counted every fragment inside and outside the DNase peaks, normalized to input, and never defined ChIP-enriched regions first. For every TF, 93–96% of reads fall outside DHSs, so the metric mostly measures background. The "closed enrichment" values span only 0.948–0.975 across TFs, all below 1. TF1 won with 0.975 against TF4's 0.971 (`.../galaxy_codex_gpt_5_6_luna_r2/.../codex_events.jsonl:L249`).
- **Luna Galaxy r1 and r3, and Luna code r2:** same design, a closed-versus-open log2 index over all fragments. Winning margins were small: TF3 at −1.427 in r1 (`.../galaxy_codex_gpt_5_6_luna_r1/.../codex_events.jsonl.gz:L89`), and TF1 in r3 (`.../galaxy_codex_gpt_5_6_luna_r3/.../codex_events.jsonl:L94`) and code r2 (`:L167`).
- **Luna code r3:** it used a bin-level variant, input-normalized ChIP in bins with DNase signal below 0.05, and got TF3 (`:L239`).
- **Contrast, GPT-5.5 Galaxy r2 (correct):** it first called ChIP-over-input enriched bins, then measured excess ChIP RPM in enriched bins outside the DHSs. It tested four DNase interval definitions, weighted and unweighted counts, and total versus top-20k bins. TF4 ranked first in 31 of 32 metrics, with a closed excess of about 280k RPM against 196k for TF6 (`.../galaxy_codex_gpt_5_5_r2/.../codex_events.jsonl:L36`). The whole computation ran as one Galaxy UDT job, so there was no local fallback.

**Interpretation.** This is a genuine method error that depends on the model, not a problem with the reference. Scoring bulk fragments lets background reads dominate the pioneer metric and turns near-ties into arbitrary winners. `TF4` is robust once signal is limited to enriched sites.

**Tags:** `scientific-method-error`, `statistical-error`, `insufficient-verification`

---

<a id="covid-patient-q1"></a>

### covid-patient-q1 — Wrong runs used an interferon-only threshold and so labelled most COVID donors "healthy"

**Question.** Given a 33-donor PBMC h5ad (279,633 cells) with only `donor_id`, infer from expression which donors are healthy. Return their IDs, numerically sorted.

**Reference.** `1,5,11,12,17,21,24,27,29,32` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 9/12, code 11/13 correct. Wrong answers, all of which call too many donors healthy:
- 25 donors: Luna Galaxy r1 and r3
- 23 donors: DeepSeek Galaxy r3
- 28 donors: Luna code r3
- 14 donors: DeepSeek code r1

**What the traces show.**
- **Interferon-only rule.** Four wrong runs (Luna Galaxy r1 and r3, Luna code r3, DeepSeek Galaxy r3) defined COVID as "strong interferon-stimulated gene (ISG) response" and called every other donor healthy:
  - Luna Galaxy r1 and r3 kept 8 high-ISG donors (3, 13, 14, 18, 26, 30, 31, 33), using the rule "ISG mean ≥0.50 and ≥half of cells above". Luna Galaxy r1 had first picked only 5 by a largest-gap rule, then forced at least 6 (`galaxy_codex_gpt_5_6_luna_r3/.../codex_events.jsonl:L143`; `..._luna_r1/...:L220-L246`).
  - Luna code r3 kept only 5 ("3, 14, 18, 26, 33 … clear gap", `L75`, `L142`).
  - DeepSeek Galaxy r3 thresholded an IFN score at about 0.15 and got 10 COVID donors (Luna's 8 plus donors 8 and 19; final donor table and answer at `L883-L884`).
  - Many COVID donors, especially later or convalescent ones, have low ISG, so these rules miss 13–18 COVID donors. This is a domain error.
- **External reference mapping.** DeepSeek code r1 tried to find the source study (web searches for `"covid.patients.q1.h5ad"`, then GSE161918 metadata, `L14-L38`). It then assigned donors to external healthy-donor profiles by correlation, which produced 14 healthy donors. Donors 6, 10, 16 and 23 were mis-assigned. DeepSeek Galaxy r3 also searched `"covid.patients.q1" Stephenson` (`L883`).
- **Correct runs.** They used a multi-programme or global split rather than an ISG cutoff. GPT-5.5 code r2 clustered donor pseudobulks (PCA, k-means and hierarchical agree on 10 vs 23), with the axis driven by IFI27, S100A8/9, FCGR1A and SOCS3 (`L49-L52`). Sol Galaxy r2 added lineage-stratified monocyte HLA-II, inflammation and IFN scores (`L105`). Its decisive diagnostics ran as Galaxy UDT jobs, not locally.

**Interpretation.** A genuine scientific-method error, and the key is consistent with the dominant biological split. The platform had no effect: the Luna failures occur in both conditions and come from the same ISG-only heuristic.

**Tags:** `domain-knowledge-error`, `scientific-method-error`, `benchmark-answer-retrieval`

---

<a id="atac-doublet-q1"></a>

### atac-doublet-q1 — Every wrong answer came from Scrublet; the doublet only shows up in fragment-overlap (AMULET-style) counting, and two correct DeepSeek Galaxy runs first read the barcode in a public third-party trace

**Question.** In a depth-filtered hg38 scATAC fragment file (1,000 barcodes), find a doublet barcode, or answer `None`.

**Reference.** `AACATGGAGCGCCGGG-1` (score-inferred; the working reference is the same).

**Outcome.** Galaxy 9/12, code 12/13. Wrong answers, each a different barcode: `AACTATTGAGACATTT-1` (Sol Galaxy r2), `TCGTATGACCGTTTTG-1` (Luna Galaxy r1), `GTTGCGGTTCCGCTCG-1` (Luna Galaxy r3), `GCGACACGCCGGGCAC-1` (DeepSeek code r3).

**What the traces show.**
- **The signal is unambiguous but needs a specific method.** Depth is normalized (~9.2k-10.2k fragments per barcode), so count-based outliers do not help. Counting loci with more than 2 overlapping fragments within a barcode (the diploid limit, as in AMULET) gives exactly one barcode with any such event: AACATGGAGCGCCGGG-1, with 281 loci and max depth 4; every other barcode has 0 (`open_ended_code_codex_gpt_5_5_r1/.../codex_events.jsonl.gz:L19-L21`).
- **All four wrong runs relied on Scrublet-type simulation.** Luna Galaxy r1/r3 and Sol Galaxy r2 used Galaxy's SnapATAC2 `pp.scrublet` wrapper. The scores were flat and seed-unstable, and no barcode passed the 0.5 probability cutoff. Luna r3: "no cell exceeds the documented 0.5 probability cutoff", then it answered the top raw score anyway (`galaxy_codex_gpt_5_6_luna_r3/...:L129-L185`). Luna r1 changed its top barcode with each seed and ended with a 6-seed rank consensus (`...luna_r1...:L140-L172`). Sol Galaxy r2 did add an "exact fragment overlap" UDT, but it measured fragments shared *between* barcodes, not overlaps *within* one. It then took a rank-product of weak scores (`galaxy_codex_gpt_5_6_sol_r2/...:L126-L166`). DeepSeek code r3 ran scrublet and snapatac2 locally and never counted overlaps. The wrong answers therefore came from the method chosen, not from a Galaxy failure. The Galaxy toolbox's only doublet tool is Scrublet, which does steer runs toward it.
- **Correct Galaxy runs computed in Galaxy.** GPT-5.5 Galaxy r1 (`atac-doublet-amulet-v1` UDT, `L43`), Sol Galaxy r1/r3 (overlap and AMULET UDTs, `L105`/`L111`) and DeepSeek Galaxy r1 (`amulet-overlap-counter-v1` UDT, `L164`) all ran the overlap count as Galaxy jobs.
- **Answer retrieval.** In DeepSeek Galaxy r2 and r3 the barcode first appears in the raw trace immediately after the agent opened `huggingface.co/datasets/amanutej/trustworthy-biology-agents-traces/commit/3ea266cd…diff`, another benchmark's public agent traces. In r2 it appears at raw L113, where the agent greps that diff for `AACATGGAGCGCCGGG` (`galaxy_codex_deepseek_v4_pro_0813_r2/...:L112-L116`). In r3 it first appears in a web query at L234, straight after the same diff was opened at L232, with no earlier tool output containing it. r3 kept probing the leaderboard, results and evaluator repos and the bioRxiv preprint (`L342-L379`). Only after that did it run an AMULET UDT in Galaxy (`L417`).

**Interpretation.** The reference is sound, and the wrong answers are a method-choice error: a simulation-based doublet scorer on data where only overlap-based detection works. For DeepSeek Galaxy r2/r3, the correct answer was seen in leaked third-party traces before it was computed. Treat them as contaminated, even though each later confirmed it with a Galaxy AMULET-style job.

**Tags:** `scientific-method-error`, `route-divergence`, `benchmark-answer-retrieval`, `insufficient-verification`

---

<a id="contaminated-rna-q1"></a>

### contaminated-rna-q1 — Galaxy misses came from a failed core_nt Kraken2 job and a fallback database that lacks cnidarians; the code miss came from a hand-picked mammalian panel

**Question.** A single-end RNA-seq FASTQ (96,053 × 75 nt) is mostly human. Name the contaminant species.

**Reference.** `hydra vulgaris` (score-inferred). The working reference agrees.

**Outcome.** Galaxy 9/12, code 12/13. Wrong answers: `human gammaherpesvirus 4` — GPT-5.5 Galaxy r3, Luna Galaxy r2; `artemia franciscana` — Luna Galaxy r1; `rattus norvegicus` — DeepSeek code r1.

**What the traces show.**
- **Correct Galaxy runs.** They ran Galaxy's Kraken2 with the `core_nt` database. It completed and gave a coherent Cnidaria→Hydra→*Hydra vulgaris* lineage with 8,793 reads (`.../galaxy_codex_gpt_5_5_r2/.../codex_events.jsonl:L36–L39`). They then validated with KrakenTools extraction and BLAST, also in Galaxy. The decisive computation was a Galaxy job, and the ledgers show only Galaxy tool jobs for classification.
- **EBV answers (GPT-5.5 Galaxy r3, Luna Galaxy r2).** The same `core_nt` job did not deliver:
  - In GPT-5.5 r3 it finished `ok`, but the report and classification datasets were empty, with failed metadata (L135–L141).
  - In Luna r2 it ran for hours on a single thread and the agent cancelled it (L50).
  - Both fell back to Kraken2 `standard-16` (human, bacteria, viruses, plasmids). That database has no cnidarians, so the largest non-human species row was *Human gammaherpesvirus 4* with 195 reads (GPT-5.5 r3 L131; Luna r2 L89). That is about 0.2% of reads, and an EBV signal is typical of lymphoblastoid lines or misassigned reads.
  - GPT-5.5 r3's NT BLAST of a 1,000-read sample also came back empty (L124). Neither run weighed the ~28% unclassified reads.
- **Artemia (Luna Galaxy r1).** Its `core_nt` Kraken2 job and its NT BLAST both hit Galaxy's 4-hour wall-time limit (L52, L107). It noticed the database gap (27.8% unclassified, L91) and fell back to BLAST of the unclassified reads against RefSeq *mitochondrion* only. There the best cross-species hits were *Artemia* mitogenomes, 32 vs 18 reads (L116–L163). The mito-only search never compared against Hydra nuclear transcripts, and "Hydra" never appears in this trace.
- **Rat (DeepSeek code r1).** A remote-BLAST sample already listed *Hydra vulgaris* (taxid 6087) among the hits (L28). The run then built a custom Kraken2 database of only human, mouse, rat and EBV (L224–L242). With Hydra excluded, conserved human reads were assigned to rat (L246–L248).

**Interpretation.** These are genuine wrong answers, not equivalents. The three Galaxy errors share one root cause. The only installed database broad enough to contain the answer (`core_nt`) failed silently or hit a time limit. The fallback databases then structurally excluded the contaminant, and the agents took the top residual hit without checking that the database could contain it. This is a Galaxy resource/reliability defect compounded by insufficient checking. The code error is candidate-panel bias.

**Tags:** `galaxy-platform-defect`, `run-truncated-or-timeout`, `insufficient-verification`, `scientific-method-error`

---

<a id="perturb-seq-effect-q1"></a>

### perturb-seq-effect-q1 — STAT1 answers took the largest mean effect from a 5-cell guide and ignored "robustly"

**Question.** In a Cell Ranger CRISPR perturb-seq output, pick the target gene whose guide robustly knocks down the IFN-gamma pathway, for a follow-up screen.

**Reference.** `ISG15` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 11/12, code 10/13 correct. Wrong answer: `STAT1` from GPT-5.5 code r1, Luna code r2 and r3, and DeepSeek Galaxy r1.

**What the traces show.**
- The dataset has one guide per target. 49 guides have 50 cells each, but guide_011 (STAT1) has only 5 cells, and one of those 5 is not knocked down (panel score 3.54, against a non-targeting median of 3.32). GPT-5.5 code r1 printed this directly: STAT1 had n=5, delta −2.47, Welch p=0.022. ISG15 had n=50, delta −0.67, p=2e-45 (`.../open_ended_code_codex_gpt_5_5_r1/.../codex_events.jsonl.gz:L37`, `:L43`). It ranked by effect size and answered STAT1 (`:L44`).
- Luna code r3 also noted "the STAT1 guide … has only 5 assigned cells" (`.../open_ended_code_codex_gpt_5_6_luna_r3/...:L18`) and still answered STAT1. Luna code r2 ranked on the median shift alone (2.58 for STAT1 vs 0.69 for ISG15; `:L34`).
- DeepSeek Galaxy r1 ran the analysis in Galaxy: scanpy `tl.score_genes`, then `Grouping1` mean per guide (STAT1 −1.28, ISG15 −0.12). It picked the minimum and never checked cell counts (`.../galaxy_codex_deepseek_v4_pro_0813_r1/.../codex_events.jsonl:L262-L279`).
- **Contrast, Sol Galaxy r2 (correct):** its Galaxy UDT jobs flagged the 5-cell STAT1 guide. It then required at least 30 cells, a negative bootstrap confidence interval, multiple-testing significance and broad downregulation, which selected ISG15 (`.../galaxy_codex_gpt_5_6_sol_r2/.../codex_events.jsonl:L28-L39`). The decisive computation ran in Galaxy.

**Interpretation.** This is a statistical-judgment error, and the task is built as this trap: "robustly" means an effect supported by adequate cells, not the largest point estimate. The reference is sound. The error is not specific to Galaxy (3 of the 4 misses are code runs).

**Tags:** `statistical-error`, `insufficient-verification`

---

<a id="reverse-search-gwas-q2"></a>

### reverse-search-gwas-q2 — The file is Yengo 2022's Hispanic-ancestry height sumstats; wrong runs stopped at trait or ancestry similarity without an exact row match

**Question.** Identify the PMID of the study whose GWAS summary statistics are in `reverse.search.gwas.q2.gz`.

**Reference.** `36224396` (Yengo et al. 2022, "A saturated map of common genetic variants associated with human height"; score-inferred, and the working reference is the same).

**Outcome.** Galaxy 11/12, code 10/13. Wrong answers: `25865494` in GPT-5.5 code r1/r2; `35399580` in Sol code r2; `33713608` in Luna Galaxy r2.

**What the traces show.**
- **The exact source.** The local lead row, rs1150779 (EAF 0.703, β −0.0886096, SE 0.00669, P 4.63291e-40), is identical to `GIANT_HEIGHT_YENGO_2022_GWAS_SUMMARY_STATS_HIS.gz`, the Hispanic-ancestry file (N=58,708), with the `N` column dropped. The ALL, EUR, EAS, AA and SAS files have different values (`open_ended_code_codex_gpt_5_5_r3/.../codex_events.jsonl.gz:L17`, `L70`). GPT-5.5 Galaxy r2 found the same row-level match. It then imported the HIS file into Galaxy by URL and ran an exact-match UDT (`galaxy_codex_gpt_5_5_r2/...:L129-L149`). The initial candidate screen was local, and the confirmation was done in Galaxy.
- **GPT-5.5 code r1/r2 (25865494, Chan 2015, sitting-height ratio).** Both tested candidate releases (spleen volume, UKBB 20015 sitting height, GWAS Atlas), found them "not an exact match", and moved to a *trait-class* guess. The final PMID came from OpenGWAS or GWAS Catalog metadata, with no row comparison (`open_ended_code_codex_gpt_5_5_r1/...:L92-L180`; `..._r2/...:L78-L117`). Neither run ever tested the Yengo ancestry-specific files.
- **Sol code r2 (35399580).** It correctly inferred "decisively Hispanic/Latino" allele frequencies (`L378`) and saw Yengo 2022 (36224396) among the top catalog hits (`L174-L176`), but never downloaded the Yengo HIS file. Its last check, against GCST90095033 (the 35399580 study), was *not* a match: rs1150779 β −0.0703 and P 3.29e-31 vs the local −0.0886 and 4.63e-40 (`L406`). It answered 35399580 anyway (`L407`).
- **Luna Galaxy r2 (33713608, an African-ancestry height study).** It spent 37M tokens. It moved from GIANT 2010/2014 candidates to GCST90013466. It could not download that paper's supplement (the PMC proof-of-work wall, `L543-L573`) and answered without any row-level confirmation (`L585-L590`).

**Interpretation.** These are genuine errors from insufficient verification. The key is uniquely identifiable by exact value matching, and each wrong run either skipped that step or overrode a failed match. No evidence of answer retrieval was seen in these runs. For correct Galaxy runs, the decisive source identification is a web or catalog lookup outside Galaxy by nature. Galaxy served mainly as the place for the confirming comparison.

**Tags:** `insufficient-verification`, `domain-knowledge-error`

---

<a id="1000g-retrieve-genotype-q1"></a>

### 1000G-retrieve-genotype-q1 — All three misses carry correct genotypes in phased notation; two runs copied the format from a leaked trace of another agent

**Question.** Report the genotypes of 10 individuals at hg38 chr10:110918899 from the latest 1000 Genomes data, in the example's slash format (`0/0,0/1,1/1,...`).

**Reference.** `0/1,0/1,1/1,1/1,0/1,1/1,0/0,0/1,0/1,1/1` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 10/12, code 12/13 correct. Wrong answers: `0|1,1|0,1|1,1|1,0|1,1|1,0|0,1|0,0|1,1|1` from DeepSeek Galaxy r3 and code r3. `0/1,1/0,1/1,1/1,0/1,1/1,0/0,1/0,0/1,1/1` from DeepSeek Galaxy r1.

**What the traces show.**
- **Same data in every run.** All runs queried the 2022 high-coverage phased panel (`1kGP_high_coverage_Illumina.chr10...phased_panel.vcf.gz`, G>T). Its raw GT calls are `0|1 1|0 1|1 1|1 0|1 1|1 0|0 1|0 0|1 1|1` (DeepSeek Galaxy r3 Galaxy output, `galaxy_codex_deepseek_v4_pro_0813_r3/.../codex_events.jsonl:L239`). The three misses have the same allele dosage at every sample as the key.
- **Phased output.** DeepSeek Galaxy r3 and code r3 returned the phased calls unchanged.
- **Only `|` replaced.** DeepSeek Galaxy r1 ran `bcftools_query` in Galaxy (`L68-L74`) and swapped `|` for `/` without normalising `1/0` to `0/1` (`L75`).
- **Leaked trace.** Both DeepSeek runs with the phased answer downloaded another agent's trace for this exact item from a public Hugging Face dataset. The file was `amanutej/trustworthy-biology-agents-traces/.../agy_gemini-3.1-pro_.../questions/1000G-retrieve-genotype-q1/trace.md`, and its answer is the phased string (Galaxy r3 `L10-L16`, fetched before any analysis; code r3 `L54-L56`). Both runs still computed the genotypes themselves (Galaxy r3 via a Galaxy job at `L235-L239`; code r3 via bcftools at `L52-L60`), but kept the leaked format.
- **Contrast.** GPT-5.5 code r1 checked the unphased 2020 GT release and concluded "heterozygotes should be `0/1` in the requested slash-separated output" (`L40-L43`).

**Interpretation.** All three misses are scientifically equivalent to the key: same genotypes, only phase notation or allele order differs. They fail on a format rule under exact string matching. Separately, two DeepSeek runs retrieved another model's answer for this benchmark item online, a contamination risk worth flagging for the whole benchmark.

**Tags:** `equivalent-answer`, `format-contract-error`, `benchmark-answer-retrieval`

---

<a id="exogenous-mix-reads-q1"></a>

### exogenous-mix-reads-q1 — The GPT-5.5 misses fit their k-mer classifier on the same reads it then scored; cross-validated fits give 30

**Question.** Estimate the percentage of exogenous (Sendai-KLF4) reads in the mix FASTQ to the nearest 10, using a pure-exogenous early file (777 reads) and a predominantly endogenous late file (395 reads). No construct sequence is given.

**Reference.** `30` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 10/12, code 12/13 correct. Wrong answers: `50` from GPT-5.5 Galaxy r1 and GPT-5.5 code r1; `40` from GPT-5.5 Galaxy r3.

**What the traces show.**
- **GPT-5.5 Galaxy r1:** a single diagnostic UDT computed 12 ad hoc k-mer and exact-match estimators, ranging from 0.12 to 0.52, and returned their median, 0.496, which rounds to 50. Each k-mer was fitted and scored on the same reference reads. The training-set separation came out as exactly 1.0, a sign of overfitting that the run never questioned (`.../galaxy_codex_gpt_5_5_r1/.../codex_events.jsonl:L20`).
- **GPT-5.5 code r1:** its first model was a held-out classifier with a sensitivity/FPR correction. At k=30–40 it gave estimates of about 0.20–0.39, clustered near 0.28–0.30 (`.../open_ended_code_codex_gpt_5_5_r1/.../codex_events.jsonl.gz:L26`). The run then switched to classifying reads with k-mers from the full training set. Those scores drifted upward with k, from 0.445 to 0.526 (`:L28-L30`), and it answered 50. So the run computed the right answer and then replaced it with a leaky estimate.
- **GPT-5.5 Galaxy r3:** every UDT, including a minimal `printf` probe, failed before execution on this server (`.../galaxy_codex_gpt_5_5_r3/.../codex_events.jsonl.gz:L56-L62`, `:L168-L170`). The run fell back to exact-sequence `join1` counts. It applied a coverage correction worked out in its own reasoning, not in any tool, and answered 40 (`:L171-L177`).
- **Contrast, Sol Galaxy r2 (correct):** it ran a cross-fitted k-mer deconvolution inside a Galaxy UDT, with grouped folds that stop identical reads from leaking between training and validation. All four k scales gave about 28–30% (`.../galaxy_codex_gpt_5_6_sol_r2/.../codex_events.jsonl:L32-L40`). The computation happened in Galaxy.

**Interpretation.** These are genuine statistical errors from in-sample fitting, confined to GPT-5.5. The reference `30` is well supported by held-out estimates, including GPT-5.5 code r1's own first model. The r3 miss was partly caused by a Galaxy UDT outage that pushed the run onto a cruder exact-match route.

**Tags:** `statistical-error`, `insufficient-verification`, `galaxy-platform-defect`, `route-divergence`

---

<a id="gene-fusion-q2"></a>

### gene-fusion-q2 — The repeated SP1 exon makes SP1–ZIC2 junctions run both ways, and split-read graph filters drop them

**Question.** Report the genes whose exons make up a synthetic multi-gene fusion in a bulk RNA-seq FASTQ, in 5'→3' order, with one symbol per exon.

**Reference.** `MYC-SP1-ZIC2-SP1-CATSPER4` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 11/12, code 11/13 correct. Wrong answers: `MYC-SP1-CATSPER4` from GPT-5.5 code r1 and DeepSeek code r1; `TPM3-MT-ATP6-MT-CO3` from Luna galaxy r3.

**What the traces show.**
- **The missing ZIC2-SP1 segment (GPT-5.5 code r1).** The run tiled reads into 35-nt windows, counted gene-to-gene transitions within reads, and ranked them by *directional asymmetry* to suppress homolog and pseudogene artifacts (`open_ended_code_codex_gpt_5_5_r1/.../codex_events.jsonl:L39-L45`). SP1 occurs twice (SP1→ZIC2→SP1), so the SP1/ZIC2 link appears in both directions and looks exactly like the artifacts the filter removes. The agent even noted that "SP1/ZIC2 also validates as split-read evidence". It still kept the only "connected zero-reverse path", MYC→SP1→CATSPER4 (`L48-L65`).
- **DeepSeek code r1** also used split-read pairs, keying junctions such as ('SP1','MYC') on gene pairs. It pulled ZIC2 transcript records but never put ZIC2 in the final path (`L163`). Its mechanism looks the same (a gene-pair graph cannot hold a gene that appears twice), but this is inferred rather than traced step by step.
- **Luna galaxy r3 lost its main route.** Galaxy's STAR job stalled with "no runner, external ID, or log activity", so Arriba never ran (`galaxy_codex_gpt_5_6_luna_r3/...:L199-L231`). The agent fell back to Trinity plus Galaxy BLAST against GENCODE v49. It reported a TPM3 + MT-ATP6 + MT-CO3 contig. MT-ATP6 and MT-CO3 are neighbours on the polycistronic mitochondrial transcript, so this is most likely a chimera of highly expressed transcripts; the trace never mentions MYC, ZIC2 or CATSPER4.
- **Correct runs assembled first.** For example, GPT-5.5 galaxy r3 ran Trinity then BLAST in Galaxy (UDTs were blocked on that server, `L96`). It found `TRINITY_DN319_c0_g1_i1`, 1,396 bp, with five contiguous plus-strand blocks MYC, SP1, ZIC2, SP1, CATSPER4 (`L152`). A contig keeps both SP1 occurrences, which a pairwise junction graph does not. No correct Galaxy run used local aligners; results were parsed locally only.

**Interpretation.** The key is sound. The two code misses come from one flaw: a junction graph built on gene pairs cannot represent a gene that appears twice. The one Galaxy miss follows a stalled STAR job (a platform execution problem) plus a weakly checked assembly contig.

**Tags:** `scientific-method-error`, `insufficient-verification`, `galaxy-platform-defect`

---

<a id="align-one-sequence-to-reference-q1"></a>

### align-one-sequence-to-reference-q1 — the two misses are the right hit written with an inclusive end coordinate

**Question.** Find where the 14-mer CACACACAGGAGAT lies in the Drosophila Release 6 FASTA. Report it as 0-based `contig:start-end`.

**Reference.** `NT_033779.5:4280595-4280609` (score-inferred; the working reference agrees). This is the 0-based, half-open (BED-style) interval.

**Outcome.** Galaxy 12/12, code 11/13. Wrong answer: `NT_033779.5:4280595-4280608` from Luna code r2 and r3.

**What the traces show.**
- **Same hit, different end convention.** Both Luna code runs found the unique exact match: forward strand, chromosome 2L, no reverse-complement hit. They reported the end as `p+len-1`, the 0-based inclusive last base. Luna code r2 used a Perl `index()` scan that prints `$p+length($t)-1` → `4280595 4280608 +` (`open_ended_code_codex_gpt_5_6_luna_r2/.../codex_events.jsonl.gz:L18`); r3 did the same.
- **Correct runs.** They used half-open BED convention, end = start + 14. Examples: Sol G r2 with a Galaxy UDT doing a literal forward/reverse-complement search (`galaxy_codex_gpt_5_6_sol_r2:L20→L21`), and DeepSeek G r3 with Galaxy BWA-MEM plus BLAST+ (`galaxy_codex_deepseek_v4_pro_0813_r3:L106–L145`).
- **Job-count artifact.** DeepSeek G r3's brief shows 0 analytical jobs because its jobs ran in history `bbd44e69cb8906b56c4e006d78f19fc9`, not the recorded one. It was not a no-Galaxy run.

**Interpretation.** The locus is identical, so this is a coordinate-convention error, not an alignment error. "0-based start-end" most commonly means half-open, so the key is reasonable. A convention-aware grader could accept `-4280608` as a closed-interval equivalent; strict grading marks it wrong.

**Tags:** `format-contract-error`, `equivalent-answer`, `underspecified-task`

---

<a id="borzoi-rnaseq-q1"></a>

### borzoi-rnaseq-q1 — 8870 is the reverse-complement-averaged prediction; the key uses the forward pass only

**Question.** Run Borzoi replicate 0 on chr1:70157360-70353968 for track ENCFF281BWX (+ strand). Undo the training transforms, sum the predicted coverage, and round to the nearest 10.

**Reference.** `9380` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 12/12, code 11/13. Wrong answer: `8870` from GPT-5.5 code r3 and DeepSeek code r1.

**What the traces show.**
- **Both wrong runs computed both numbers.** Both ran the model correctly and applied the legacy inverse transform: /0.3 scale, soft-clip at 384, then power 4/3. Both got the forward-only total and the forward/reverse-complement ensemble. GPT-5.5 code r3: "raw forward pass rounds to 9380, RC-averaged prediction rounds to 8870" (`open_ended_code_codex_gpt_5_5_r3/.../codex_events.jsonl.gz:L135`).
- **Why they chose RC.** They cloned the Borzoi paper repository, found that benchmark scripts call `--rc -u`, and chose the RC-averaged value (L144→L155). DeepSeek code r1 ran `predict_borzoi.py rc` and got 8866.8 → 8870 (L248–L255).
- **The size of the choice.** The forward/RC choice alone moves the answer by about 5%. The PyTorch port shows the same split: 9381.9 forward, 8882.3 RC mean (`galaxy_codex_deepseek_v4_pro_0813_r1:L288`).
- **Where the computation ran for Galaxy runs.** In 10/12 Galaxy runs the decisive value first appears in a Galaxy UDT output. Examples: Luna G r1 ran full replicate-0 inference in Galaxy, 9381.93 → 9380 (L547–L552), and Sol G r2 at L64. Two Galaxy runs computed it locally:
  - GPT-5.5 G r3 ran the forward pass on local CPU after "the UDT execution path itself was unavailable on this server", then staged a result file into Galaxy (L160–L181).
  - DeepSeek G r1 pip-installed `borzoi-pytorch` and inferred locally (L280–L288).
- **Lookups of benchmark material.** DeepSeek G r1 also searched for "CompBioBench borzoi-rnaseq-q1" and downloaded the CompBioBench preprint. The preprint does not contain the value (L290–L304: `9380 0`).

**Interpretation.** 8870 is not a computational error; it applies Borzoi's standard test-time RC-ensembling convention. The prompt asks for forward-strand coverage from one replicate without mentioning RC averaging, and the key clearly assumes a single forward pass. The item is mildly underspecified. The two misses are defensible but deviate from the likelier intended reading.

**Tags:** `underspecified-task`, `route-divergence`, `local-fallback-in-galaxy`

---

<a id="cryptic-exon-q1"></a>

### cryptic-exon-q1 — Both misses called a highly expressed gene from 1-read or multimapper-only "novel" junctions, without requiring a junction pair that forms an exon

**Question.** Name the single highly expressed coding gene that carries a cryptic exon formed by two novel splice junctions, from a bulk human RNA-seq FASTQ.

**Reference.** `GNG10` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 10/12, code 13/13 correct. Wrong answers: `CD74` from DeepSeek galaxy r2; `UBC` from DeepSeek galaxy r3.

**What the traces show.**
- **DeepSeek galaxy r2 (`CD74`).**
  - It ran Galaxy STAR and filtered SJ.out.tab to unannotated junctions (`c6==0`). It then re-ran STAR against the GENCODE v47 *basic* GTF, which leaves 929 "novel" junctions, because junctions from transcripts outside the basic set also count as novel (`galaxy_codex_deepseek_v4_pro_0813_r2/.../codex_events.jsonl:L245-L259`).
  - It kept genes with ≥2 novel junctions (EPS15, DRAM2, LYPLAL1 and many more) and picked the one among the top-expressed genes: CD74, with 1,238 counts (`L227`, `L283-L287`).
  - The two CD74 junctions (chr5:150402021-150402562 and 150402626-150405084) have **1 uniquely mapped read each** (`L289`). The selection was driven by expression, not by junction evidence.
- **DeepSeek galaxy r3 (`UBC`).** It ran Galaxy STAR, HISAT2 and featureCounts. Its UBC "novel" junctions (chr12:124912183-124912236 and -124912464) have **0 unique and 1 multimapping read** each. They sit inside UBC's tandem ubiquitin repeats, where alignment ambiguity creates spurious junctions. UBC ranked only 65th by expression (`galaxy_codex_deepseek_v4_pro_0813_r3/...:L284`, `L322`). The run also web-searched "UBC cryptic exon two novel splice junctions" (`L327`).
- **Correct runs used a structural criterion.** Sol galaxy r1 required "a matched pair of novel junctions that split one annotated intron" and checked that the top gene clearly beat the runner-up. It did this in a Galaxy UDT over STAR junctions and the GENCODE model (`galaxy_codex_gpt_5_6_sol_r1/...:L57-L62`). The correct Galaxy runs aligned in Galaxy (HISAT2/STAR) and ranked with Galaxy UDTs; no local aligner commands were found (e.g., GPT-5.5 galaxy r1 `L7-L61`).

**Interpretation.** The key is sound. Both misses are genuine analysis errors: no minimum unique-read support, no multimapper exclusion, and no requirement that the two junctions bracket a new exon. Both happened in DeepSeek's Galaxy runs; DeepSeek's code runs were all correct, so this reflects route variance rather than a Galaxy defect.

**Tags:** `scientific-method-error`, `insufficient-verification`

---

<a id="genomic-state-q1"></a>

### genomic-state-q1 — Both misses used a different chromatin-state model; one also queried hg19 files with hg38 coordinates

**Question.** Classify chr11:124,738,681-124,738,772 (hg38) into one of six options: tissue-specific active enhancer (liver, brain frontal lobe or ESC), ubiquitous transcription, ubiquitous poised/flanking TSS, or ubiquitous Polycomb repression.

**Reference.** `B` (Active enhancer, brain frontal lobe; score-inferred; the working reference agrees).

**Outcome.** Galaxy 12/12, code 11/13 correct. Wrong answers: `E` from DeepSeek code r2; `F` from Astra code r1.

**What the traces show.**
- **Contrast, Sol Galaxy r2 (correct):** it located the EpiMap hg38 18-state ChromHMM tracks through FILER and extracted the interval with one Galaxy UDT. Middle frontal area BA46 was `EnhA1`, liver `Quies`, H1-hESC `ReprPC`, and ENCODE frontal cortex `EnhBiv/ReprPC` (`.../galaxy_codex_gpt_5_6_sol_r2/.../codex_events.jsonl:L43`). This matches option B. The decisive lookup ran in Galaxy.
- **Astra code r1:** it lifted the interval to hg19 correctly (124,608,577-668), then read the Roadmap 15-state core-mark model for 14 epigenomes. E073 DLPFC was `5_TxWk`, E066 liver `14_ReprPCWk`, E003 ESC `ReprPC/EnhBiv`, and most other tissues were ReprPC or Quies. On that majority it answered F after only two commands (`.../open_ended_code_codex_gpt_6_astra_r1/.../codex_events.jsonl.gz:L9-L12`). The older 15-state model has no H3K27ac, so it cannot call an "active" enhancer at all.
- **DeepSeek code r2:** it queried the hg19 Roadmap 15-state files with hg38 coordinates and no liftover, which puts the lookup at the wrong locus (`...deepseek_v4_pro_0813_r2/.../codex_events.jsonl:L24`). It did find ENCODE H3K27ac peaks spanning the interval in middle frontal area 46 (`:L102`). It then took the universal full-stack ChromHMM state `90_BivProm3`, a bivalent promoter, and mapped it to "TSS poised or flanking, ubiquitous" (`:L124-L146`).

**Interpretation.** Both misses are real errors, not reference problems. The labels only make sense under a tissue-resolved model that includes H3K27ac, such as EpiMap 18-state, and they are backed by direct H3K27ac evidence in BA46. Neither wrong answer should count as equivalent. The reference still depends on picking the BA46 sample over other frontal-cortex samples, which is a minor underspecification that did not affect any run.

**Tags:** `route-divergence`, `source-version-drift`, `domain-knowledge-error`, `insufficient-verification`

---

<a id="gwas-ancestry-q1"></a>

### gwas-ancestry-q1 — LD-profile inference reached HIS in every Galaxy run; the two code misses are an admixture near-miss and a compacted run's unsupported guess

**Question.** Identify the ancestry group of a chromosome-1 GWAS summary-statistics file (114,873 variants) from 8 population codes.

**Reference.** `HIS` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 12/12, code 11/13 correct. Wrong answers: `EUR` from Sol code r2; `AFR` from DeepSeek code r1.

**What the traces show.**
- **Sol code r2 (`EUR`).** It correlated the association-peak shape at several lead loci with 1000G LD for AFR, AMR, EAS, EUR and SAS. EUR edged out AMR at the strongest locus (Pearson 0.866 vs 0.761, `open_ended_code_codex_gpt_5_6_sol_r2/.../codex_events.jsonl:L79`). Other loci were nearly tied (AMR 0.913, EAS 0.917, EUR 0.903 at `L91`). It answered EUR (`L94`) without a decisive margin. The Hispanic/AMR reference is admixed and largely European, so LD matching separates it from EUR only weakly.
- **DeepSeek code r1 (`AFR`).** It spent 36.6M input tokens trying to match lead p-values against Million Veteran Program height files (EUR/AFR/ASN/HIS; `L469`) and never found an exact match. The trace hit a context-compaction warning (`L478`) and it then answered AFR (`L479`). Its earlier LD work had not supported AFR, so the answer is unsupported.
- **Correct code runs by source lookup.** Sol code r1 recognised "the ancestry-stratified Yengo et al. height release" and did "an exact p-value match against" the five official ancestry files (`L76-L89`). That is a source-data lookup, not an inference from the data.
- **Correct Galaxy runs by LD inference in Galaxy.** GPT-5.5 Galaxy r1 and Sol Galaxy r1 scored clumped lead windows against population-specific 1000G LD inside Galaxy jobs ("The first locus favors the Hispanic/MXL reference", Sol Galaxy r1 `L39-L46`; GPT-5.5 Galaxy r1 `L48-L60`).

**Interpretation.** The key is solid, and the errors are model-level. One is a close EUR/AMR call without a decisive margin, the other an unsupported final answer after context compaction. Galaxy is not implicated. Note that some correct runs got HIS by identifying the source release rather than inferring ancestry.

**Tags:** `insufficient-verification`, `statistical-error`, `run-truncated-or-timeout`

---

<a id="hic-differential-loop-q1"></a>

### hic-differential-loop-q1 — Both wrong answers put an anchor outside the stated sub-compartment; one was copied from a third-party trace, and one correct Galaxy run computed locally

**Question.** Using the H1 vs HFF Micro-C data (Krietenstein et al. 2020), report the differential loop inside the NANOG sub-compartment chr12:7,629,950-7,809,597, as `start;end` rounded to 20 kb.

**Reference.** `7720000;7800000` (score-inferred; the working reference is the same).

**Outcome.** Galaxy 12/12, code 11/13. Wrong answers: `7680000;7920000` in GPT-5.5 code r3; `7700000;8280000` in Luna code r1.

**What the traces show.**
- **The decisive structure.** Filtering the 4DN published H1 loop calls to anchors inside the interval gives two loops. One, 7,675,000-7,805,000, is shared with HFF. The other, 7,715,000-7,805,000, is H1-only and rounds to 7720000;7800000. Luna Galaxy r1 and r3 and Sol Galaxy r1 did this with ordinary Galaxy filter tools on the BEDPE calls (`galaxy_codex_gpt_5_6_luna_r3/.../codex_events.jsonl:L146`, `...luna_r1...:L159-L190`).
- **GPT-5.5 code r3 ignored the interval constraint.** It picked "the H1 loop with anchors around 7.675 Mb and 7.915 Mb" from the 4DN joint loop calls and its O/E map (`open_ended_code_codex_gpt_5_5_r3/...:L98-L121`). The 7.92 Mb anchor lies outside the sub-compartment, which ends at 7,809,597. GPT-5.5 Galaxy r1 first found the same kind of out-of-interval candidates (7.78/8.20 Mb). It recovered only after "restricting both loop anchors to chr12:7629950-7809597" (`galaxy_codex_gpt_5_5_r1/...:L139-L155`).
- **Luna code r1 copied a third-party answer.** It downloaded the `amanutej/trustworthy-biology-agents-traces` index, filtered it to `task_id=='hic-differential-loop-q1'` (`L93-L95`), and fetched another Codex GPT-5.5 run's `trace.md`. That trace's "## Answer" block reads `7700000;8280000` (raw L97). The run then grepped for exactly those numbers (`L99`), also looked at a Gemini trace answering `7680000;7800000` (`L101`), and returned `7700000;8280000` (`L104`). The copied answer was unscored and wrong: its anchors fall outside the interval as well.
- **Local-computation fallback in a correct Galaxy run.** In GPT-5.5 Galaxy r1, all 3 Galaxy jobs failed. The agent dumped `.hic` matrices locally at 10 kb and 25 kb (KR, VC_SQRT, NONE), ranked differential pixels locally, and only uploaded `final_answer.txt` to the history (`L133-L173`). The other 11 Galaxy runs filtered or compared inside Galaxy, mostly on the published loop calls.

**Interpretation.** The reference is sound. The correct answer requires respecting the interval constraint, and both code-condition errors violated it; one of them was a copied wrong answer. Count GPT-5.5 Galaxy r1 as correct but as a local-fallback run, not Galaxy execution. Most Galaxy successes used published loop calls, not de novo loop calling.

**Tags:** `benchmark-answer-retrieval`, `insufficient-verification`, `local-fallback-in-galaxy`, `scientific-method-error`

---

<a id="histone-chip-q1"></a>

### histone-chip-q1 — Both H3K4me1 answers read weak, short MACS2 peaks as enhancer peaks and never tested heterochromatin features

**Question.** Work out which histone mark an hg38 ENCODE-style signal tagAlign (with its control) comes from. The answer must be one of H3K4me3, H3K27ac, H3K4me1, H3K36me3, H3K27me3 or H3K9me3.

**Reference.** `H3K9me3` (score-inferred; the working reference agrees). The July lab hint says an earlier campaign answered `H3K27ac` because "interpretation depends on criterion choice". The criterion that differs is peak-level annotation versus read-level enrichment. It is the same trap the two deviators fell into here.

**Outcome.** Galaxy 10/12, code 13/13 correct. Wrong answers: `H3K4me1` from DeepSeek-v4-pro Galaxy r1 and r3.

**What the traces show.**
- **DeepSeek Galaxy r3:** no reasoning is written in the trace. It ran one MACS2 broad call and got 22,131 peaks with median width 594 bp and fold enrichment about 3 (`.../galaxy_codex_deepseek_v4_pro_0813_r3/.../codex_events.jsonl.gz:L64`, `:L172`). ChIPseeker put about 74% of peaks in introns or distal intergenic regions and about 19% in promoters (`:L148`). The deepTools TSS profile was flat, with a slight dip at the TSS: 1.43 at the TSS against 1.46–1.49 on the flanks (`:L250`, `:L290`). It then searched the web for "H3K4me1 … promoter intron intergenic" and "H3K27ac vs H3K4me1 peak width", and answered `H3K4me1` (`:L306-L311`). A TSS dip of about 5% on a flat profile is not the strong bimodal flanking enrichment H3K4me1 shows.
- **DeepSeek Galaxy r1:** it stated up front that peak distribution and size signatures "cleanly separate the six marks" (`.../galaxy_codex_deepseek_v4_pro_0813_r1/.../codex_events.jsonl.gz:L60`). Its narrow peaks had median width 402 bp, fold enrichment 3–4 and a 22.7% promoter share (`:L112`, `:L190`, `:L287`). From that it narrowed the candidates to "H3K4me1 or H3K27ac" (`:L294`). Its attempts to build read-coverage bigWigs failed in Galaxy (unindexed BAM, dbkey `?`, failed_metadata; `:L202`, `:L230`, `:L244`), so it dropped read-level analysis. It then compared its peaks with ENCODE GM12878 peak sets. The Jaccard index was 0.0011 against H3K27ac and 0.0006 against H3K4me1, meaning essentially no overlap with either (`:L396`, `:L436`). That evidence argues against both marks, yet it answered H3K4me1 after matching its ChIPseeker percentages to published tables from a pig-liver paper (`:L408-L426`). It also tried to find the input file on ENCODE by md5 and got no hit (`:L322-L324`).
- **What neither deviator computed:** FRiP, ZNF/chr19 enrichment, satellite or repeat enrichment, or any H3K9me3/H3K27me3 test. These terms never appear in either trace.
- **Contrast, GPT-5.5 Galaxy r1 (correct):** it ran full-file read-level UDT jobs in Galaxy. Signal showed no promoter enrichment (0.97x genome) and no gene-body enrichment (0.98x), while the control was promoter-enriched at 1.69x (`.../galaxy_codex_gpt_5_5_r1/.../codex_events.jsonl:L37`). Satellite repeats were enriched over control at log2 0.86, as were ERVK/ERVL/LTR elements (`:L62`). Its final label was also produced by a Galaxy job (`:L68`), so no local fallback was involved.
- **DeepSeek Galaxy r2 (correct):** it first searched for the benchmark itself. It downloaded `compbiobench.v1.tsv` and the README from HF `Genentech/compbiobench-data-v1`, searched "compbiobench histone-chip-q1 answer", and read another group's agent-trace dataset (`amanutej/trustworthy-biology-agents-traces`). No key was found (`.../galaxy_codex_deepseek_v4_pro_0813_r2/.../codex_events.jsonl.gz:L366-L437`). It then took the Roadmap E055 chromHMM file from the benchmark's own HF data folder and ran bedtools coverage in Galaxy. Relative to control, signal was 1.68x in 8_ZNF/Rpts and about 1.3x in 9_Het, which gave H3K9me3 (`:L555-L567`).

**Interpretation.** This is a real domain-knowledge error, not an ambiguous reference. Weak, fragmented MACS2 peaks from a heterochromatin mark were read as enhancer peaks, and the only direct test, overlap with ENCODE peak sets, contradicted H3K4me1 but was ignored. The reference `H3K9me3` is well supported by read-level ZNF, satellite and promoter-depletion evidence. DeepSeek Galaxy r2's correct answer is computed, but the run tried to retrieve the benchmark's answer and should be flagged.

**Tags:** `domain-knowledge-error`, `scientific-method-error`, `insufficient-verification`, `route-divergence`, `benchmark-answer-retrieval`

---

<a id="saluki-setup-optimize-q1"></a>

### saluki-setup-optimize-q1 — Both misses changed the coding/splice input tracks; one Galaxy "correct" answer was read from another run's history

**Question.** Set up Saluki and run 3 greedy rounds of every single substitution in the 17-nt 3' UTR, using the 50-fold human-head average. Report the optimized mRNA.

**Reference.** `…TAGTATAAATAATAAGGGCT` (score-inferred; the working reference agrees). The greedy path is A45G, then G32A, then C35A.

**Outcome.** Galaxy 12/12, code 11/13 correct. Wrong answers: `…TAGTGCCCGTAATAAGGACT` from DeepSeek code r3; `…TAGCGTACATAATAAGTAGT` from Luna code r1.

**What the traces show.**
- **DeepSeek code r3:** its first run reproduced the reference exactly: coding track at every codon start from ATG through the stop codon, splice track all zero, 50 models (`.../open_ended_code_codex_deepseek_v4_pro_0813_r3/.../codex_events.jsonl:L165`). It then "corrected" the encoding. It removed the stop codon from the coding track and set the splice flag on the last nucleotide (`X[si,len(seq)-1,5]=1`). That rerun overwrote `final_answer.txt` (`:L211`). Its own side tests show how sensitive the path is. With the stop excluded and no splice flag the result was `…GGAGT` (`:L213`). With codon frames counted from base 0 it was `…GGTCC…` (`:L167`).
- **Luna code r1:** its "orf" encoding picked C46G in round 1 at 1.43038. A45G, the reference path, scored 1.42956, a margin of 0.0008 (`.../open_ended_code_codex_gpt_5_6_luna_r1/...:L167`). The script body is not logged, so the exact track difference cannot be verified. Its "from_sequence_start" variant reproduces DeepSeek's frame-from-0 score exactly (1.433408), so the models and numerics were identical and only the encoding differed (`:L170`). Luna r1 also web-searched the task ID and sequence, downloaded the CompBioBench preprint and cloned `Genentech/compbiobench-runner` (`:L135-L153`). None of these gave an answer.
- **Computation location in Galaxy runs:**
  - GPT-5.5 Galaxy r3 (8/8 jobs failed on `training_tag_small_rule` routing) and DeepSeek Galaxy r2 (13/13 failed) computed the answer locally with TensorFlow and staged it into Galaxy (`.../galaxy_codex_gpt_5_5_r3/...:L190-L230`; `.../galaxy_codex_deepseek_v4_pro_0813_r2/...:L365`).
  - Luna Galaxy r3's UDT never ran. It queried `/api/jobs?tool_id=saluki…` on the shared account and read the outputs of Sol Galaxy r3's and DeepSeek Galaxy r3's jobs from their histories (`…53a31f88…`, `…58d81ddeb…`), then reported that sequence (`.../galaxy_codex_gpt_5_6_luna_r3/...:L530-L559`).
  - Luna Galaxy r1 did run the ensemble as a Galaxy UDT (`.../galaxy_codex_gpt_5_6_luna_r1/...:L315-L330`).

**Interpretation.** The reference follows the natural convention: the CDS is marked through the stop codon and there is no splice flag on a single-exon construct. Both misses are genuine input-encoding errors, amplified by tiny round-1 margins, so they are not equivalent answers. For Galaxy scoring, 12/12 overstates in-Galaxy execution: 2 runs fell back to local computation, and Luna Galaxy r3 copied another benchmark run's result through the shared Galaxy account.

**Tags:** `scientific-method-error`, `numerical-instability`, `local-fallback-in-galaxy`, `galaxy-platform-defect`, `benchmark-answer-retrieval`, `cross-run-output-reuse`

---

<a id="bedtools-ops-q1"></a>

### bedtools-ops-q1 — The single miss used base-level `bedtools subtract` instead of dropping whole overlapping intervals (off by 453 bp)

**Question.** Recentre ENCODE narrowPeak intervals to 500 bp around the summit, merge them, "exclude any that overlaps" the blacklist, and report the total bases.

**Reference.** `111423829` (score-inferred; the working reference is the same).

**Outcome.** Galaxy 12/12, code 12/13. Wrong answer: `111424282` in DeepSeek code r1.

**What the traces show.**
- DeepSeek code r1 built the summit windows correctly (`s=$2+$10; s-250, s+250`: 269,800 windows, 160,106 after merging). It then ran `bedtools subtract -a merged -b blacklist` (`open_ended_code_codex_deepseek_v4_pro_0813_r1/.../codex_events.jsonl.gz:L10`, `L18`).
- Only one merged interval touches the blacklist: chr17, with a 47 bp overlap at 142015-142062 (`L12`, `L18`: "intersect bases 47"). `subtract` removes only those 47 bp and keeps the other 453 bp, which is why the output still has 160,106 intervals.
- The prompt asks to exclude whole intervals that overlap (`intersect -v` or `subtract -A`), which removes all 500 bp: 111,424,282 − 453 = 111,423,829, exactly the reference. The agent printed the overlap but never questioned whether partial removal matched "exclude any that overlaps".

**Interpretation.** This is a small semantic error in the operation, not a platform or reference issue. "Exclude any [interval] that overlaps" is best read as whole-interval removal, and 24/25 runs read it that way. The reference is sound and the answer is not equivalent, but the gap is a single 453 bp interval.

**Tags:** `wrapper-semantics`, `insufficient-verification`

---

<a id="compute-gccontent-promoter-q1"></a>

### compute-gccontent-promoter-q1 — The one miss ran bedtools slop with strand-awareness turned off on a minus-strand TSS

**Question.** Compute the GC content of the [TSS−500, TSS+99] promoter window, on the transcript's strand, for ENST00000269305 (TP53, minus strand) in Ensembl 115 / GRCh38. Report coordinates, length, GC count and GC fraction.

**Reference.** `17;7687391;7687990;-;600;292;0.49` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 11/12, code 13/13 correct. Wrong answer: `17;7686990;7687589;-;600;331;0.55` from DeepSeek Galaxy r1.

**What the traces show.**
- **Correct TSS, wrong direction.** DeepSeek Galaxy r1 built the pipeline from native Galaxy tools. It correctly isolated the transcript (`17:7668421-7687490, strand -`, `galaxy_codex_deepseek_v4_pro_0813_r1/.../codex_events.jsonl:L156`) and made a 1-bp TSS BED (7687489–7687490, `-`, `L216`). It then called `bedtools_slopbed` with `"addition": {"l": 500, "r": 99}, "strand": false` (`L230`, resubmitted at `L254`). With `-s` off, slop extends 500 bp toward lower coordinates whatever the strand. On a minus-strand gene that is downstream, into the gene body, giving BED 7686989–7687589 (`L258`).
- **Wrong window, strand label kept.** The GC count (331/600 = 0.55) is correct for that wrong window. The agent never checked the window against the strand it reported (`-`).
- **Contrast.** GPT-5.5 Galaxy r1 wrote a single self-checking UDT that derived "strand-aware promoter coordinates" and asserted a 600-bp length before counting GC (`L12-L18`). That computation also ran in Galaxy.

**Interpretation.** A genuine error. The agent explicitly turned off the Galaxy slop wrapper's strand option, which is a wrapper-semantics trap the agent failed to catch, not a platform defect. The key is sound.

**Tags:** `wrapper-semantics`, `scientific-method-error`, `insufficient-verification`

---

<a id="deg-simple-q2"></a>

### deg-simple-q2 — Luna Galaxy r1 fitted a post-hoc filter to noisy StringTie/Cuffdiff output and never ranked genes by read-supported switches

**Question.** Two single-sample bulk RNA-seq FASTQs contain exactly one gene with differentially expressed isoforms. Report its HGNC symbol.

**Reference.** `DEFB110` (score-inferred; the working reference agrees). The unverified July note records an earlier `STAT1` answer from a failed switch route.

**Outcome.** Galaxy 11/12, code 13/13 correct. Wrong answer: `MS4A1` from Luna Galaxy r1.

**What the traces show.**
- **Luna Galaxy r1, route:** the built-in Galaxy Salmon `hg38` index turned out to be a genome-contig index, with `Name` values of `chr1`, `chr2` and so on, so it could not produce transcript calls (`.../galaxy_codex_gpt_5_6_luna_r1/.../codex_events.jsonl.gz:L103`). The run switched to HISAT2 against hg38 with GENCODE v44, then Cuffdiff, reference-only StringTie and IsoformSwitchAnalyzeR. The last refused to test one replicate per condition (`:L135-L356`).
- **Luna Galaxy r1, selection:** its own switch-score screen returned 1,283 candidate genes (top: CYB5R3), which is essentially noise. It then built a "strict" filter after seeing the data: isoform-fraction change of at least 0.10 plus opposing Cuffdiff isoform p < 0.05, using unadjusted p-values when every q was 0.49. That filter left one gene, MS4A1 (`:L388`, `:L403-L405`). DEFB110 and its transcript IDs never appear anywhere in the trace. Candidates were never ranked by read support.
- **Luna Galaxy r1, benchmark search:** it also ran Google and Bing searches for the benchmark file name `deg.simple.q2.sampleA.fq.gz` (`:L382-L384`). Nothing useful came back.
- **Contrast, GPT-5.5 Galaxy r2 (correct):** it aligned reads with minimap2 to the GENCODE transcript FASTA inside one Galaxy UDT and ranked genes by change in isoform fraction. DEFB110 came first by a wide margin: about 200 reads per sample and a complete switch, ENST00000393660 at 1.0 in A against ENST00000371148 at 1.0 in B (L1 delta 2.0, versus 0.52 for the second gene). The computation ran in Galaxy (`.../galaxy_codex_gpt_5_5_r2/.../codex_events.jsonl:L30-L35`).

**Interpretation.** A genuine statistical and method error. With n=1 per sample, genome-alignment quantification over about 250k transcripts produces many spurious "switches", and a post-hoc p < 0.05 filter picked one of them. The misleading Salmon `hg38` index in Galaxy triggered the detour but did not force the wrong answer. The benchmark file-name search should be flagged.

**Tags:** `statistical-error`, `scientific-method-error`, `wrapper-semantics`, `route-divergence`, `benchmark-answer-retrieval`

---

<a id="enformer-basic-q1"></a>

### enformer-basic-q1 — The single miss is hand arithmetic that sized pre-convolution BatchNorm layers by output rather than input channels (+4,608)

**Question.** Give the exact number of trainable parameters in Enformer, including both the human and mouse heads.

**Reference.** `251221292` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 12/12, code 12/13 correct. Wrong answer: `251225900` from Luna code r1 (+4,608).

**What the traces show.**
- **Luna code r1 never built the model.** It cloned `deepmind-research/enformer`, tried to install `dm-sonnet==2.0.0` (the import failed on the modern TensorFlow), and then counted parameters by hand. Its sums were conv tower 49,650,688, transformer 225,122,304 (trunk total 229,850,112) and heads 3073×(5313+1643) = 21,375,788, giving 251,225,900 (`open_ended_code_codex_gpt_5_6_luna_r1/.../codex_events.jsonl:L29-L35`, `L52`). It then web-searched its own number, `"251225900" Enformer` (`L37`, `L56`, `L62`), and submitted it without resolving the discrepancy.
- **Luna galaxy r1 explains the 4,608 exactly.** In a Galaxy runtime shape inventory it found "two 768-element variables where the symbolic inventory expected two 3072-element variables": 2 × (3072 − 768) = 4,608. The cause is that "in the published `ConvBlock`, BatchNorm precedes the convolution, so it has the input-channel width, not the convolution's output width". After this correction, the direct runtime sum is 251,221,292 (`galaxy_codex_gpt_5_6_luna_r1/...:L119-L129`). Luna code r1's formula makes exactly this error (it sizes BN terms from output channels `f`, `L31`).
- **Correct runs instantiated the model.** Sol galaxy r1 pinned Sonnet 2.0.0 with TensorFlow 2.5.1 (the paper-era runtime) inside a Galaxy job and asserted that the instantiated trainable-variable total matched the layer-by-layer breakdown (`galaxy_codex_gpt_5_6_sol_r1/...:L56-L63`). GPT-5.5 galaxy r2 first hit the UDT routing block, then counted in Galaxy after it cleared (`L108-L114`). No correct Galaxy run fell back to local computation.

**Interpretation.** The key is sound. The only miss is an architecture-convention error in hand-derived arithmetic, which the agent could have caught by instantiating the model with pinned library versions.

**Tags:** `domain-knowledge-error`, `insufficient-verification`, `tool-version-difference`

---

<a id="extract-rna-secondary-structure-q1"></a>

### extract-rna-secondary-structure-q1 — the only miss is a correct answer with " kcal/mol" appended; three Galaxy runs folded locally

**Question.** Fold human 5S rRNA (RNAcentral URS0000668495) with ViennaRNA. Report the MFE structure and the energy as `structure,energy` (two decimals, kcal/mol, no spaces).

**Reference.** `......(((....(((((.((....((((.(((((((((((((((((.........)))))))))).))))))....).))))...)).))))).....)))......(((..((((((((....)))))))).)))....,-50.20`. This is score-predicted, so it is the most likely key rather than a uniquely implied one; the working reference agrees.

**Outcome.** Galaxy 12/12, code 12/13. Wrong answer: the same structure and `-50.20` followed by ` kcal/mol`, from Astra code r1.

**What the traces show.**
- **Astra code r1.** It pip-installed ViennaRNA 2.7.2, folded the sequence, and printed the structure and energy with a unit suffix (`open_ended_code_codex_gpt_6_astra_r1/.../codex_events.jsonl.gz:L15–L20`). The structure is identical character for character, and so is the energy. The prompt's "in kcal/mol units" names the unit but does not say to print it. "Comma (no spaces)" and the single-value format make the suffix a contract violation.
- **Where the fold ran for Galaxy runs.** All 25 runs agree on the scientific result, so the platform question is where the fold was computed. In 9/12 Galaxy runs, −50.20 first appears in a Galaxy UDT output. In three it came from a local ViennaRNA install after Galaxy UDT execution failed:
  - GPT-5.5 G r2: "local package fallback … ViennaRNA 2.7.0 and 2.7.2" (L102–L109).
  - GPT-5.5 G r3: "local ViennaRNA library gives … -50.20" (L117–L124).
  - Luna G r1: after all 13 Galaxy jobs failed before command rendering, it ran `pip install … ViennaRNA` and folded locally (L447–L451→L488).

**Interpretation.** The Astra miss is scientifically equivalent and fails only on formatting; it would be correct under unit-tolerant parsing. The task gives little separation between models. The Galaxy 12/12 includes three answers computed outside Galaxy, caused by UDT execution failures on the server.

**Tags:** `format-contract-error`, `equivalent-answer`, `local-fallback-in-galaxy`, `galaxy-platform-defect`

---

<a id="find-deletion-q1"></a>

### find-deletion-q1 — the single miss mistook the chr22 pericentromeric mappability gap for the deletion

**Question.** Shallow paired-end WGS simulated from one hg38 chromosome carrying a large deletion. Report `chr:start-end` rounded to 100 kb.

**Reference.** `chr22:20000000-21000000` (score-inferred; the working reference agrees). An earlier July lab estimate, `chr22:12900000-15200000`, had made the same mistake as the wrong run below.

**Outcome.** Galaxy 11/12, code 13/13. Wrong answer: `chr22:13300000-15200000` from DeepSeek G r3.

**What the traces show.**
- **The decisive evidence.** Correct runs found discordant pairs with about 1,000,500 bp template length, one mate near 20.0 Mb and the other near 21.0 Mb, together with a sustained coverage drop between them. GPT-5.5 code r1: "several properly oriented read pairs have ~1,000,500 bp template lengths, with one end near 20.0 Mb and the mate near 21.0 Mb" (`open_ended_code_codex_gpt_5_5_r1/.../codex_events.jsonl.gz:L61→L68`). This is the 22q11.2 region.
- **DeepSeek G r3, route.** It ran a Galaxy BWA → `samtools stats` → `bedtools bamtobed -bedpe` pipeline. It then sorted pairs by span and looked at the 100 largest (L255–L267). The top of that list is repeat noise: pairs spanning 10.5 → 32.9 Mb and 16.6 → 38.4 Mb, with spans of 12–22 Mb. The genuine 1-Mb-span breakpoint pairs never reached the head of the list.
- **DeepSeek G r3, the wrong interval.** It fell back on the largest zero-coverage block, 13.3–15.2 Mb. That block is the modeled chr22 centromere and pericentromeric satellite, where reads fail to map uniquely. The agent did suspect a gap: it searched "hg38 chr22 centromere coordinates" (L277) and measured N content with Galaxy `seqtk comp`. But hg38 fills the centromere with modeled alpha-satellite, so 13.0–15.5 Mb is only 4.2% N (103,777 of 2.5 Mb, L297). The N test "passed", and the agent reported the mappability gap.
- **Where the computation ran for Galaxy runs.** No Galaxy-condition run invoked a local aligner (minimap2, BWA, bowtie2 or samtools) or a local installer, so alignment and coverage ran in Galaxy.

**Interpretation.** This is a genuine domain-knowledge error: a mappability or centromere artifact was treated as a deletion, and the check used (N fraction) cannot detect modeled centromeres in hg38. Other runs gave the correct answer robustly across models and conditions, and the key is solid.

**Tags:** `domain-knowledge-error`, `insufficient-verification`

---

<a id="gene-pair-ordering-fraction-q1"></a>

### gene-pair-ordering-fraction-q1 — The miss counted on `.raw` instead of `.X` after computing both, then went looking for the benchmark's answer

**Question.** In `10x_pbmc68k_reduced.h5ad`, restrict to CD19+ B cells with percent_mito < 0.04 (94 cells). Count cells where SRM − MRPS21 > 1, cells where it is < −1, and cells where it lies in [−1, 1].

**Reference.** `37;20;37` (score-inferred; the working reference agrees). This is the count on the default `adata.X`, which holds the scaled matrix in this scanpy dataset.

**Outcome.** Galaxy 12/12, code 12/13 correct. Wrong answer: `29;23;42` from DeepSeek code r2.

**What the traces show.**
- **DeepSeek code r2, two layers:** it computed both layers on the same 94 cells: `X 37 20 37` and `raw 29 23 42` (`.../open_ended_code_codex_deepseek_v4_pro_0813_r2/.../codex_events.jsonl:L188`). It then submitted the `.raw` (log-normalized) result (`:L192-L193`). So the difference is only the choice of expression layer, and the cell filter was not the problem.
- **DeepSeek code r2, answer search:** before choosing, it spent many steps trying to recover the benchmark's key. It web-searched "gene-pair-ordering-fraction-q1 answer" and the literal strings "37;20;37" and "29;23;42" (`:L60`, `:L86`, `:L100`, `:L190`). It queried the CompBioBench leaderboard Gradio API (`:L130-L140`) and requested per-submission result JSONs from HF `Genentech/compbiobench-results-v1`, getting HTTP 401 (`:L186`). It also tried the Zenodo data tarball, which returned 403 (`:L182`). Nothing was retrieved.
- **Contrast, DeepSeek Galaxy r1 (correct):** it filtered with Galaxy `scanpy_filter`, exported `.X` with `anndata_export`, and computed the difference and counts with Galaxy `column_maker` and `datamash`, the latter submitted through the raw Galaxy API (`.../galaxy_codex_deepseek_v4_pro_0813_r1/.../codex_events.jsonl:L147-L179`). The brief lists 0 analytical jobs for this run, but those jobs are real Galaxy jobs. It looks like a ledger undercount of jobs submitted outside the MCP wrapper.

**Interpretation.** Taking differences of per-gene z-scores in `.X` is arguably less meaningful than using log-normalized `.raw`, so `29;23;42` is a defensible alternative. The prompt does not name a layer, and the key follows the AnnData default. Mild `underspecified-task`. The run's extensive attempts to retrieve the benchmark's answer should be flagged, even though they failed.

**Tags:** `underspecified-task`, `route-divergence`, `benchmark-answer-retrieval`

---

<a id="gtf-5-utr-median-len-q1"></a>

### gtf-5-utr-median-len-q1 — The one miss built a pure-Galaxy bedtools pipeline whose exon-to-region join ignored transcript identity (+6 bp on CDS and 3' UTR)

**Question.** Report median 5' UTR, CDS (stop codon included) and 3' UTR lengths for MANE Select transcripts on standard chromosomes in the MANE v1.3 RefSeq GTF.

**Reference.** `133;1296;1050` (score-inferred; the working reference agrees). The July hint's `87;1266;995` (feature-level mixing) was not reproduced by any current run.

**Outcome.** Galaxy 11/12, code 13/13 correct. Wrong answer: `133;1302;1056` from DeepSeek Galaxy r3.

**What the traces show.**
- DeepSeek Galaxy r3 had its UDT probes fail (history datasets 3–11 are in error), so it rebuilt the task from stock Galaxy tools. The pipeline:
  - `tp_grep` kept only exon/CDS rows tagged MANE Select; this dropped `stop_codon`.
  - It converted GTF to BED12 and BED6 exon blocks.
  - `Add_a_column` extended thickStart/thickEnd by 3 bp for the stop codon, which is correct for this GTF.
  - It built 5'UTR, CDS and 3'UTR span intervals.
  - `bedtools intersect -s -wo` joined all exon blocks with all span intervals.
  - It summed the overlap grouped by the **exon's** transcript name, then took the median with `datamash` (`.../galaxy_codex_deepseek_v4_pro_0813_r3/.../codex_events.jsonl:L223-L333`; snapshot `source_snapshots/galaxy/bbd44e69cb8906b5b38fa6c98996cf94/contents.json`, hids 12–33).
- Verified: the join never required the exon's transcript to equal the span's transcript (no `c4==c10` filter), and no per-transcript check that exon length = 5'UTR + CDS + 3'UTR was run. Inferred: same-strand exons of nested or overlapping genes that fall inside another transcript's CDS or 3'UTR span were credited to that exon's transcript. This inflates a subset of transcripts and shifts both medians by +6 bp, while leaving the 5' UTR at 133. The exact affected set was not recomputed.
- **Contrast, Sol Galaxy r2 (correct):** it ran a Galaxy diagnostic confirming stop codons are separate 3-nt rows, then a per-transcript UDT with a hard check that each exon total equals 5'UTR + CDS-with-stop + 3'UTR (`.../galaxy_codex_gpt_5_6_sol_r2/...:L34-L42`). DeepSeek Galaxy r1 likewise used a transcript-keyed UDT (`...r1/...:L28-L64`). All three computed in Galaxy.

**Interpretation.** This is an interval-join semantics error that appeared when a Galaxy UDT outage forced the agent to express transcript-level bookkeeping with generic interval tools. It is not an equivalent answer, and the reference is sound. It is a case where the route forced by the platform, not the science, introduced the error.

**Tags:** `wrapper-semantics`, `route-divergence`, `insufficient-verification`, `galaxy-platform-defect`

---

<a id="huggingface-entropy-q1"></a>

### huggingface-entropy-q1 — The `TT` answer came from a broken local Caduceus reimplementation whose predictions were near-uniform

**Question.** Run Caduceus-PH (131k) with single-base masking over hg38 chr12:7792299-7793299, and return the longest run of positions with base-2 entropy below 0.5.

**Reference.** `GTCTCTACTAAAAATACAAAATTAGCC` (score-inferred; the working reference agrees). This is a 27-bp run at local 0-based positions 194–220, in an Alu-like sequence.

**Outcome.** Galaxy 12/12, code 12/13 correct. Wrong answer: `TT` from Sol code r1.

**What the traces show.**
- **Sol code r1:** it could not use the fused mamba-ssm kernels, so it wrote its own pure-PyTorch Mamba scan (`run_caduceus.py`) and ran it on Apple MPS (`.../open_ended_code_codex_gpt_5_6_sol_r1/.../codex_events.jsonl.gz:L18`, `:L36-L53`). It checked the scan only against its own token-by-token recurrence, never against the official model's outputs.
- The outputs show the model was not working. Full-vocabulary entropy reached 3.9 bits, close to the 4-bit maximum for 16 tokens. It also differed widely from the A/C/G/T-renormalized entropy (3.89 vs 1.70 at position 46), meaning heavy probability mass on non-DNA tokens. Only 7 of 1,000 positions fell below 0.5, and the longest run was positions 50–51, `TT` (`:L71`). A rerun reproduced the same numbers (`:L73`), so the error is systematic, not noise.
- **Contrast, Sol code r2 (correct):** also a pure-reference scan, but it noted that "the model assigns negligible probability to non-base tokens" and that both entropy definitions agreed. Both picked the 27-bp run at 194–220 (`.../open_ended_code_codex_gpt_5_6_sol_r2/...:L66`, `:L70-L71`).
- **Computation location for correct Galaxy runs:** GPT-5.5 Galaxy r2 and r3 found UDTs non-executable and computed the scan locally, then staged the results into Galaxy (`.../galaxy_codex_gpt_5_5_r2/...:L190-L224`; `.../galaxy_codex_gpt_5_5_r3/...:L152-L189`). Luna Galaxy r1 ran the full scan as a Galaxy job (`.../galaxy_codex_gpt_5_6_luna_r1/...:L310`).

**Interpretation.** This is an implementation bug in a hand-written model port, and the agent missed an obvious sanity check (near-uniform predictions on a trained DNA model). The reference is sound. The Galaxy 12/12 includes at least two local-fallback runs.

**Tags:** `scientific-method-error`, `insufficient-verification`, `local-fallback-in-galaxy`

---

<a id="phase-chain-q1"></a>

### phase-chain-q1 — The single miss had the right haplotypes but encoded them against its own assembly contig, not hg38 primitives

**Question.** From 1,000 read pairs drawn from two synthetic haplotypes over 1.5 kb of hg38, call biallelic SNPs and 1-bp indels, phase them by read-backed evidence, and return both haplotype chains (I/D notation, alphabetical order).

**Reference.** `A-C-T-D-C-A-D-G|C-T-A-G-G-D-G-A` (score-inferred; the working reference agrees): 8 sites (5 SNPs and 3 one-bp deletions). The July hint records an earlier, swapped phase, which no current run reproduced.

**Outcome.** Galaxy 12/12, code 12/13 correct. Wrong answer: `A-C-T-D-C-A-G-C-G|C-T-A-I-G-G-C-G-A` from Luna code r1.

**What the traces show.**
- Luna code r1 assembled the reads de novo with SPAdes and called variants against its own 1,497 bp contig rather than hg38 (`.../open_ended_code_codex_gpt_5_6_luna_r1/.../codex_events.jsonl.gz:L27`, `:L63`). Its own pairwise alignment of the two reconstructed haplotypes printed exactly the reference chain: 181 A/C, 241 C/T, 541 T/A, 700 −/G, 950 C/G, 1149 A/−, 1152 −/G and 1399 A/G (`:L158`).
- The final string then used a different decomposition (`:L161-L164`):
  - The 1149–1152 pair of 1-bp deletions (reference sites 6–7) became three SNPs, `A/G`, `G/C`, `C/G`.
  - The site-4 deletion was written `D|I`, because the contig carried the deleted allele, so the other haplotype looked like an insertion. The reference writes it `D|G`.
- The underlying haplotype sequences are therefore the same. Only the variant representation is non-parsimonious and not relative to the reference genome.
- Luna r1 also probed extensively for the answer: the HF `compbiobench-data-v1` tree and `compbiobench.v1.tsv`, the GitHub runner, Zenodo, the leaderboard `app.py`, and results/evaluator repos (`:L92-L160`). No key was found.
- **Contrast, GPT-5.5 Galaxy r1 (correct):** FreeBayes in Galaxy, then a Galaxy UDT that decomposed FreeBayes' complex records into primitive SNP and 1-bp deletion events before read-backed phasing (`.../galaxy_codex_gpt_5_5_r1/...:L52-L72`). The computation ran in Galaxy.

**Interpretation.** This is a variant-normalization error, not a phasing error. The haplotypes are right, but the task asks for primitive SNPs and 1-bp indels on hg38, and the answer is not string-equivalent, so the miss is fair. The reference is well supported.

**Tags:** `format-contract-error`, `route-divergence`, `benchmark-answer-retrieval`

---

<a id="read-proportions-q1"></a>

### read-proportions-q1 — The miss counted bowtie2's random primary placement of heavily multimapping reads instead of resolving them with EM

**Question.** Estimate the chromosome-sampling probabilities π for 40,000 36 bp reads from a four-chromosome synthetic genome. Report percentages rounded to 5.

**Reference.** `50,20,20,10` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 11/12, code 13/13 correct. Wrong answer: `35,25,25,15` from DeepSeek Galaxy r1.

**What the traces show.**
- DeepSeek Galaxy r1 ran Galaxy bowtie2 with default reporting, which gives one random best hit per multimapper, then `samtools idxstats` (`.../galaxy_codex_deepseek_v4_pro_0813_r1/.../codex_events.jsonl:L41-L43`). It took the per-contig counts 12,961 / 8,794 / 8,897 / 8,321 as the estimate. That gives 33.3/22.6/22.8/21.4%, rounded to 35,25,25,20 with the last value adjusted to 15 (`:L45-L48`). It never checked the multimapping rate.
- The genome is built so that most reads are ambiguous. Sol Galaxy r2's alignment diagnostics show 98.1% of reads mapped but 79.6% multimapping, so primary placements spread the shared reads roughly evenly and pull the estimate toward uniform (`.../galaxy_codex_gpt_5_6_sol_r2/.../codex_events.jsonl:L28`).
- **Contrast, Sol Galaxy r2 (correct):** it realigned in all-alignments mode, kept each read's best-scoring chromosome set, and fitted the mixture weights by EM in a Galaxy UDT, which gave 50,20,20,10 (`:L39-L58`). The computation ran in Galaxy.

**Interpretation.** This is a genuine statistical error: a naive estimator on a task built around multimapping ambiguity. It is neither a platform defect nor an equivalent answer. The reference is sound (24/25 runs agree).

**Tags:** `statistical-error`, `insufficient-verification`

---

<a id="retina-score-snps-q1"></a>

### retina-score-snps-q1 — 0.58 comes from applying the notebook's 1-based indexing to a 0-based table; 348/500 reference alleles were silently overwritten

**Question.** Score 500 hg19 SNPs with the five Rod ChromBPNet-style fold models "following the code in ScoreSNPs.ipynb", then report the AUPRC of |Rod_fold_avg_lfc|, floored to two decimals.

**Reference.** `0.67` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 12/12, code 12/13 correct. Wrong answer: `0.58` from Luna code r1.

**What the traces show.**
- The task table's `start` column is the **0-based** SNP position on hg19. The notebook's own example SNPs are hg38 and 1-based, and the notebook places the allele at `INP_LEN//2 - 1`. It also silently "corrects" any reference mismatch by writing the table's ref allele into the centre base.
- **Luna code r1:** it kept the notebook's 1-based indexing ("the notebook treats each coordinate as a 1-based SNP position and corrects any central reference mismatch exactly as its code does"; `.../open_ended_code_codex_gpt_5_6_luna_r1/.../codex_events.jsonl.gz:L112`). Its scorer printed `reference mismatches corrected: 348` out of 500 (`:L115`). The notebook comment says that count "should be small", yet the run did not investigate. So in most sequences the allele sat 1 bp off and a neighbouring base was overwritten. That gave AP 0.58478 (`:L121`). A later hg19→hg38 liftover check kept the same indexing and gave 0.5855 (`:L161`).
- **Contrast, Luna code r2 (correct):** it found that ref alleles match hg19 when `start` is read as 0-based (`...luna_r2/...:L80`). It computed both variants: 0-based centring gave 0.67507, and literal notebook indexing gave 0.58478, bit-identical to Luna r1 (`:L144`). GPT-5.5 Galaxy r1 ran the same allele-match diagnostic (hg19/hg38 × 0/1-based) as a Galaxy UDT before scoring, and scored in Galaxy (`.../galaxy_codex_gpt_5_5_r1/...:L32-L53`).

**Interpretation.** The miss comes from an off-by-one coordinate convention, and the 70% ref-mismatch warning was ignored. The prompt's "following the code" invites exactly this literal reading, so the item is slightly underspecified. Still, the reference 0.67 is the scientifically correct choice: it places the variant where the table's ref allele actually is.

**Tags:** `scientific-method-error`, `insufficient-verification`, `underspecified-task`

---

<a id="sample-swap-atac-q1"></a>

### sample-swap-atac-q1 — Sol Galaxy r3 had the GEO source files but checked only file sizes and weak markers, which cannot see a same-size gut swap

**Question.** Decide whether two organ columns in a chunked 10-kb axolotl bulk ATAC count matrix (AmexG_v6.0-DD) were swapped, and if so name them in lexicographic order.

**Reference.** `Cloaca,Stomach` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 11/12, code 13/13 correct. Wrong answer: `None` from Sol Galaxy r3.

**What the traces show.**
- **Sol Galaxy r3, markers:** it matched the dataset to the public UUATAC axolotl organ series on GEO and resolved every per-organ fragment file with its size (`.../galaxy_codex_gpt_5_6_sol_r3/.../codex_events.jsonl:L76`, `:L88`). For evidence it used only (a) promoter-marker signatures and (b) library size against GEO file size. The stomach marker set had just `atp4b` and `muc5ac`, and `atp4b` accessibility was flat across organs. `cdx2`, a posterior-gut marker, peaked in the "Stomach" column (9.24 CPM against 2.24 in "Cloaca"). That clue contradicts the label but went unused (`:L67`, `:L73`).
- **Sol Galaxy r3, decision:** the synthesis scored every two-column swap as worse than the identity labeling, with Cloaca/Stomach at a gain of −3.55. The size check also ruled out any swap, because Cloaca and Stomach libraries are nearly the same size (4.08 GB and 4.36 GB on GEO; `:L100`). It answered `None`, and the final label came from a Galaxy UDT (`:L107`).
- **Contrast, GPT-5.5 Galaxy r1 (correct):** it went through the same size and marker checks and noted that "a same-sized swap could evade that check" (`.../galaxy_codex_gpt_5_5_r1/.../codex_events.jsonl:L93`). It then streamed bounded prefixes of the public GEO fragment files inside a Galaxy UDT and binned them to the task's chunked coordinates. The match was reciprocal: public Cloaca matched the task "Stomach" column best (r = 0.915, against 0.877 for its own label), and public Stomach matched task "Cloaca" (r = 0.912) (`:L115`). It answered `Cloaca,Stomach`, although its closing message still hedged (`:L122-L123`). The computation ran in Galaxy.

**Interpretation.** A genuine error of insufficient verification. The run had the unswapped source data in hand but only compared file sizes, and a size check cannot detect a swap between similar-depth gut libraries. The reference is supported by direct positional matching against GEO.

**Tags:** `insufficient-verification`, `scientific-method-error`, `domain-knowledge-error`

---

<a id="sample-swap-rna-q1"></a>

### sample-swap-rna-q1 — The one miss relied on hand-made human-ortholog marker panels; correct runs used the published atlas

**Question.** Decide whether two cell-type columns of an amphioxus scRNA-seq pseudobulk matrix (12 cell types) were swapped, and if so name them in lexicographic order.

**Reference.** `epidermal_neural,tailbud_neural` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 12/12, code 12/13 correct. Wrong answer: `epidermal_neural,neural_like` from DeepSeek code r3.

**What the traces show.**
- **DeepSeek code r3, reference search:** it searched the web for the benchmark file name and the column labels but found neither the source atlas nor any key (`.../open_ended_code_codex_deepseek_v4_pro_0813_r3/.../codex_events.jsonl:L116`, `:L140`, `:L226`).
- **DeepSeek code r3, marker panels:** with no reference data, it mapped amphioxus IDs to human orthologs and wrote its own 10–28-gene panel per cell type. Some panels are doubtful: `tailbud_neural` includes KRT13, KRT75 and POSTN, and `epidermal_neural` is built from vertebrate sensory-neuron genes such as POU4F3, PRDM12 and ISL1.
- **DeepSeek code r3, decision:** its score matrix showed a reciprocal pattern. The `epidermal_neural` column scored highest on the `neural_like` panel (1.00), and the `neural_like` column scored highest on the `epidermal_neural` panel (1.25). It answered that pair (`:L248-L255`). Evidence for the correct pair was already present: the `tailbud_neural` column best matched the epidermis and epidermal_neural panels (0.71 and 0.66). The run did not reconcile this.
- **Contrast, GPT-5.5 Galaxy r2 (correct):** it identified the 21-hpf amphioxus neurula atlas paper and staged its source-data workbook (Figure 1c, 176 metacells) into Galaxy. A UDT correlated each pseudobulk column with the atlas cell-type profiles over 18,472 shared genes. The `epidermal_neural` column's best match was atlas `tailbud_neural` at r = 0.92, against 0.02 for its own label. The best single swap raised the identity score from 8.97 to 10.76 (`.../galaxy_codex_gpt_5_5_r2/.../codex_events.jsonl:L71`, `:L111`). The computation was in Galaxy. It used the benchmark's upstream public atlas, which is legitimate reference data rather than an answer key.

**Interpretation.** A genuine error caused by weak, hand-built human-ortholog marker panels for an invertebrate chordate. The reference is well supported by correlation with the source atlas. Runs that found the published atlas had a near-deterministic route.

**Tags:** `domain-knowledge-error`, `scientific-method-error`, `insufficient-verification`

---

<a id="spatial-sim-q2"></a>

### spatial-sim-q2 — After UDTs failed, Sol Galaxy r2 used squidpy neighbourhood enrichment, which measures adjacency and misses Fibroblast_Stroma's distance-scale proximity

**Question.** Using simulated scRNA-seq plus Visium data (30×30 grid), find which cell types are biased toward being close to spots containing Tumor_Core.

**Reference.** `Fibroblast_Stroma,Macrophage` (score-inferred; the working reference agrees).

**Outcome.** Galaxy 11/12, code 13/13 correct. Wrong answer: `Macrophage` from Sol Galaxy r2.

**What the traces show.**
- **Sol Galaxy r2, forced route change:** every UDT failed before execution on this Galaxy instance, including a minimal template probe, with "custom project image is not schedulable" (`.../galaxy_codex_gpt_5_6_sol_r2/.../codex_events.jsonl.gz:L31`, `:L48`). The run rebuilt the analysis from stock tools over about 75 jobs. It did MuSiC and NNLS deconvolution, assigned each spot its highest-proportion ("dominant") cell type, and ran squidpy `nhood_enrichment` on a 4-neighbour grid graph (`:L404`, `:L465`, `:L516-L541`). Its z-score readout printed nothing to the trace (`:L552`), so the exact values cannot be verified. It answered `Macrophage` (`:L553`).
- **Contrast, Sol Galaxy r1 (correct):** it ran a UDT that validated NNLS on held-out synthetic mixtures (MAE 0.0057). It called presence per cell type, not dominance, then ran a 20,000-draw randomization test on nearest-distance to Tumor_Core, with FDR correction (`.../galaxy_codex_gpt_5_6_sol_r1/.../codex_events.jsonl:L39-L46`).
  - Fibroblast_Stroma was much closer than expected: mean nearest distance 172 against a null of 258, q = 2.5e-4.
  - It was *not* enriched among immediate neighbours: adjacent fraction 0.155 against 0.170 expected (ratio 0.91, p = 0.86), and it was not co-located (odds ratio 0.27).
  - Macrophage was enriched on all three measures: distance, adjacency (ratio 1.98) and co-location (odds ratio 2.86) (`:L46`).
- **Why r2 missed Fibroblast_Stroma:** an adjacency-based test on dominant labels, as in r2, can detect Macrophage but by construction cannot detect Fibroblast_Stroma's ring-like, distance-scale proximity.

**Interpretation.** The miss comes from the operational definition of proximity: graph-adjacency enrichment versus nearest-distance. The reference follows the distance reading, which fits "closer spatial proximity". The Galaxy UDT outage pushed Sol r2 onto a stock wrapper whose statistic answers a narrower question, so this is partly a platform-induced route divergence, not a random scientific error.

**Tags:** `galaxy-platform-defect`, `route-divergence`, `wrapper-semantics`, `scientific-method-error`, `underspecified-task`
## IWC workflows

<a id="wf_005_amplicon_dada2_pe_denoising"></a>

### wf_005_amplicon_dada2_pe_denoising — score plateaus follow the unstated truncation lengths; the two zeros come from lowercase staging slugs

**Question.** Denoise 17 paired-end V4 samples (2x250 MiSeq) into exact ASVs with paired merging and de novo chimera removal. Write a raw-count table whose sample columns use the supplied identifiers. Truncation, maxEE and pooling are **not specified**.

**Reference.** The reference is the IWC DADA2-paired workflow output: 315 ASVs and 223,938 counts. The metric is `asv_abundance_f1`, the geometric mean of ASV-detection F1 and abundance-weighted F1, with samples matched by case-sensitive identifier.

**Outcome.** Six runs score 1.0: DeepSeek Galaxy r1–r3, DeepSeek code r2 and r3, and Luna code r2. Scores below 0.95: GPT-5.5 code r1 and r3 **0**; GPT-5.5 code r2 0.900; GPT-5.5 Galaxy r1 and r2 0.918; Luna code r3 0.918; DeepSeek code r1 0.935; Luna Galaxy r1 0.937; Sol code r3 0.949.

**What the traces show.**
- **The reverse-read truncation length decides the score cluster.** Every 1.0 run used truncLen 240/160, maxEE 2, truncQ 2, pool=FALSE, minOverlap 12 and consensus chimera removal (Galaxy `dada2_filterAndTrim` parameters in `job_ledgers/galaxy/galaxy_codex_deepseek_v4_pro_r1.json`). The other clusters:
  - 240/200: **0.9556** for QIIME2 in Galaxy (GPT-5.5 r3, Sol r1 and r2, Luna r2 and r3; identical 330-ASV, 217,621-count tables). R DADA2 with the same lengths gives **0.9548** (Luna code r1).
  - 240/220: 0.9515 (Sol code r1 and r2) and 0.9507 (Sol Galaxy r3).
  - 240/240: 0.9375 (Luna Galaxy r1).
  - No truncation (0/0): 0.918 (GPT-5.5 Galaxy r1 and r2 via QIIME2; Luna code r3). With pool=TRUE and minOverlap 20 added it drops to 0.900 (GPT-5.5 code r2). With maxEE also disabled it gives 0.935 (DeepSeek code r1).
- **Why GPT-5.5 code r1 and r3 score 0.** The code-condition harness staged the inputs as lowercase directory slugs (`data/inputs/paired_input_data/hfmt_cecal_1296_1/...`, `.../open_ended_code_gpt_5_5_r1/.../codex_events.jsonl:L14`). The mixed-case IDs appear only in `codex_visible/task_input.yaml`, and neither run ever read that file: no mixed-case ID appears anywhere in either trace. r3 even states it will "use sample directory names as the column names to avoid renaming the supplied identifiers" (`r3 ...:L58`). By contrast, Luna code r2 (L14) and DeepSeek code r2 (L9) read `task_input.yaml`.
- **Recomputed scores with the sample-ID case restored.** My reimplementation of the metric reproduces the evaluator exactly, using DeepSeek Galaxy r1 (score 1.0) as the reference proxy. With IDs restored, **r1's table is identical to Luna code r1's and scores 0.9548**. r3 would score 0.854: its DADA2 micromamba install stalled, so it fell back to VSEARCH UNOISE3 (`r3 ...:L33-L45`).
- **Galaxy execution check.** All 12 Galaxy runs denoised inside Galaxy, using `qiime2__dada2__denoise_paired` or the DADA2 wrapper chain; local shell calls were only tool probes. The histories for Luna r2 and DeepSeek r2 are retained as metadata only, but their traces show the tools being submitted to Galaxy (Luna r2 `...:L140`; DeepSeek r2 `run_trace/run_dada_paired.sh`). **Provenance anomaly:** Luna Galaxy r2's `run_trace/asv_execution.log` describes a different history (`...b9366a4e8a35e623`), a different route and a 331-ASV result. The run's trace never creates or references that file. The run's own `execution.log` matches the submitted 330-ASV table.

**Interpretation.** The 0.90–0.956 band is a parameter-choice effect, not a denoising failure. The prompt leaves truncation open, and the reference encodes one defensible choice (240/160). QIIME2 users in Galaxy who chose 240/200 were capped at 0.9556. Declining to truncate at all (0/0) on 2x250 reads is a weaker choice. The zeros are a contract failure made more likely by the harness's lowercase staging. The underlying denoising would score 0.955 (r1) and 0.854 (r3).

**Tags:** `format-contract-error`, `insufficient-verification`, `underspecified-task`, `route-divergence`, `provenance-anomaly`

---

<a id="wf_009_clinicalmp_peptide_verification"></a>

### wf_009_clinicalmp_peptide_verification — score clusters track how strict PepQuery's competitive filtering was; the exact matches copied unstated workflow settings

**Question.** Validate 196 microbial candidate peptides against four TMT MGF files with PepQuery-style competition against human UniProt+isoforms plus cRAP, using the stated tolerances and modifications. Report every (peptide, protein_id) pair from the SGPS and MaxQuant reports.

**Reference.** The IWC ClinicalMP-verification output: 134 peptides and 139 pairs. The metric is `peptide_protein_pair_f1`.

**Outcome.** Scores of 1.0 or 0.993: all 6 DeepSeek runs and Sol code r1. Seven runs score 0.982. The runs below 0.95 are: Sol code r2 **0.949**, Luna code r1 **0.914**, GPT-5.5 Galaxy r2 **0.908**, Sol Galaxy r3 **0.908**, Luna Galaxy r3 **0.900**, Luna Galaxy r2 **0.868**, GPT-5.5 code r3 **0.852**, GPT-5.5 code r2 **0.840** and Luna code r3 **0.796**.

**What the traces show.** Nearly all error is precision (extra peptides). It rises as the unrestricted-modification (UMS) and amino-acid-substitution competition gets weaker:
- **1.0 cluster: PepQuery2 2.0.2 with `-hc -aa`.** These flags appear in the Galaxy job command lines of the DS Galaxy runs and in the code-run commands. They are not in the prompt. Every exact-match run first fetched the GTN ClinicalMP verification tutorial, which lists them (e.g. `galaxy_codex_deepseek_v4_pro_r1/...:L22-L35`).
- **0.982 cluster: PepQuery2 defaults, with UMS on but no `-hc/-aa`.** This gives 139 peptides: recall is 1.0, plus 5 extra peptides. Runs: GPT-5.5 Galaxy r1/r3, Sol Galaxy r1/r2, Luna Galaxy r1, GPT-5.5 code r1 and Sol code r3.
- **About 160–165 peptides: no effective UMS step.**
  - GPT-5.5 Galaxy r2 and Sol Galaxy r3 used the older Galaxy `pepquery` 1.6.2 wrapper, whose logs have no unrestricted step. They then filtered p ≤ 0.01 themselves (Sol: Galaxy `Filter1` `c12 == 0 and c16 <= 0.01`).
  - Luna code r1 rebuilt PepQuery 2.0.5 with the PTM phase removed after an out-of-memory failure, and applied its own p-value rule (`...luna_r1/...:L370,L398-L408`).
  - Luna Galaxy r3 searched one concatenated MGF. Step 5 of that PepQuery2 job digested **"Protein sequences:0"**, so the UMS filter was empty and silently vacuous (job stdout, history `...86d919`). The result was 165 peptides.
  - Luna Galaxy r2 (1.6.2, p < 0.05) also mapped proteins only from MaxQuant, dropping SGPS assignments. Its recall is 0.942.
- **Sol code r2 (149 peptides).** After an out-of-memory failure, it pre-filtered the competitor database to 42,807 sequences within 10 ppm of the candidate spectra (`:L123`). That removes the modified or substituted competitors that UMS needs.
- **No PepQuery at all.** GPT-5.5 code r2/r3 used a custom Python b/y scorer (`analysis_steps.jsonl`) and got 180 and 178 peptides. Luna code r3 used its own scorer and recovered only 109 of 139 pairs.
- **Galaxy execution.** All 12 Galaxy runs ran PepQuery as Galaxy jobs. Joining the verified peptides to the SGPS/MaxQuant reports was often done locally (e.g. a Python join in DS Galaxy r1, `:L119`).

**Interpretation.** This task is underspecified. The 0.982 runs followed the prompt faithfully with PepQuery2 defaults and are scientifically acceptable. The perfect scores depend on retrieving the source workflow's hidden `-hc -aa` settings. The genuine errors are:
- silently skipping or emptying the UMS step (Luna Galaxy r3 shows a silent Galaxy/PepQuery failure);
- choosing the older 1.6.2 engine;
- replacing PepQuery with a custom scorer.

**Tags:** `underspecified-task`, `benchmark-answer-retrieval`, `tool-version-difference`, `route-divergence`, `galaxy-platform-defect`, `scientific-method-error`

---

<a id="wf_003_host_contamination_removal"></a>

### wf_003_host_contamination_removal — all five "failures" are route-registry artifacts; every run removed host reads correctly

**Question.** Filter 78,090 paired reads against hg38 with any suitable paired-end short-read aligner. Remove the pairs that aligner calls valid paired alignments, keep everything else unmodified and synchronized, and declare the aligner in `method.json`.

**Reference.** The reference depends on the declared route. The primary route is the IWC Bowtie2 output: 72,867 pairs retained and 5,223 removed. A calibrated BWA-MEM 0.7.19 route retains 20,896 and removes 57,194, and `bwa-mem2` is an alias that shares it. The metric is `paired_fastq_f1`, the geometric mean of the removed-set F1 and the retained-ID F1. Routes with no registered reference return `unsupported_route` (null).

**Outcome.** 19 of 24 runs score at least 0.9998. Low or missing: Luna Galaxy r1 **0.2730**, Luna Galaxy r3 **0.2730**, and GPT-5.5 code r1, r2 and r3 **null**.

**What the traces show.**
- **Luna Galaxy r1 and r3 (BWA-MEM / BWA-MEM2) were scored against the Bowtie2 reference.** Their `evaluation.json` files have no `route` block; all six Luna evaluations lack one. The details show `reference_total` 72,867 retained and 5,223 removed, which is the Bowtie2 set. That gives retained-ID recall 0.287 and removal precision 0.091 (`.../galaxy_gpt_5_6_luna_r1/evaluation.json`). Luna r3 retained exactly 20,896 pairs. The `bwa-mem2` route provenance in Sol Galaxy r1's evaluation says it was *validated against "the wf_003 answer submitted by gpt-5.6-luna, galaxy_tools, replicate 3"*, byte-identical to the BWA-MEM reference. Luna r1 retained 20,899 pairs, 3 borderline pairs more. Its `run_record.acc` values of 0.9999 and 1.0 are the correct-route scores.
- **GPT-5.5 code r1: "BWA" is not a registered alias.** It ran `bwa mem -t 8` with 0.7.19-r1273 (`run_trace/bwa_mem.stderr.log`) and removed 57,194 pairs, keeping 20,896 (`run_trace/validation_summary.txt`). Those are exactly the BWA-MEM reference counts. `method.json` said `"BWA"`, so the route `bwa` was rejected. Its `run_record.acc` is 1.0.
- **GPT-5.5 code r2 and r3: minimap2 has no reference.** Both runs gave up on local Bowtie2 and BWA index builds as too slow and switched to `minimap2 -ax sr` (`.../open_ended_code_gpt_5_5_r2/.../codex_events.jsonl:L412,L504`, `r3 ...:L111`). This is a legitimate choice. However, r2 aligned against 16 separate hg38 chunks (`r2 ...:L929-L952`), so its primary and proper-pair decisions were made per chunk rather than genome-wide. It removed 31,900 pairs, against 31,716 for r3's whole-genome run.
- **Galaxy execution check.** All 12 Galaxy runs have `ok` aligner jobs (bowtie2 2.5.5, bwa_mem 0.7.19, bwa_mem2 2.3) plus samtools view/fastx jobs in their Galaxy job ledgers. Their local shell use was limited to API payloads and validation, so there was no local-computation fallback.

**Interpretation.** None of the five low or missing scores reflects a scientific error. Luna Galaxy r1 and r3 are evaluator false negatives: they were scored against the wrong route, and their real scores are about 0.9999 and 1.0. GPT-5.5 code r1 is a correct BWA-MEM run lost to alias normalization. The minimap2 runs cannot be evaluated until a minimap2 reference is registered. This supports the result section's warning that the Galaxy-vs-code difference on host removal cannot be read as biological.

**Tags:** `evaluator-false-negative`, `route-divergence`, `unregistered-route`

---

<a id="wf_007_vgp_mitogenome_assembly"></a>

### wf_007_vgp_mitogenome_assembly — the three zeros are nuclear contigs picked without an identity check; the "0.9955 public record" cluster is a second valid MitoHiFi output

**Question.** Assemble the complete *Agrius convolvuli* mitogenome from PacBio HiFi reads (1.32 M reads, 14.9 Gb) and submit exactly one FASTA record. The prompt says to use only the provided inputs.

**Reference.** The reference is the IWC VGP MitoHiFi workflow output: the 15,449-bp contig `ptg000002l_rc_rotated`. It is scored by canonical 31-mer agreement, which is independent of rotation and strand.

**Outcome.** 1.0: GPT-5.5 Galaxy r2, Sol Galaxy r3 and DeepSeek Galaxy r1, all with byte-identical MitoHiFi output. **0**: GPT-5.5 Galaxy r1, GPT-5.5 code r1 and DeepSeek code r2 (zero shared 31-mers). 0.942: GPT-5.5 code r2. Everything else scores 0.991–0.996.

**What the traces show.**
- **The zeros are complete sequence disagreement, not formatting.** The evaluator counts canonical 31-mers, so reverse complements are handled and a shifted circular origin would cost only a few windows. The three zero runs share no 31-mer with the 15,419 reference windows (`evaluation.json` of each run):

  | Run | Submitted length | Candidate 31-mer windows | Matched |
  |---|---:|---:|---:|
  | GPT-5.5 Galaxy r1 | 14,449 bp | 14,419 | 0 |
  | GPT-5.5 code r1 | 16,279 bp | 16,249 | 0 |
  | DeepSeek code r2 | 15,349 bp | 15,319 | 0 |

- **GPT-5.5 Galaxy r1 (hifiasm in Galaxy, 14,449 bp).** It deliberately skipped MitoHiFi because full mode needs an NCBI reference and "the task says to use only the provided inputs" (`.../galaxy_gpt_5_5_r1/.../codex_events.jsonl.gz:L32`). It then chose `ptg000099c` only because it was circular, 14,449 bp and at depth `rd:i:206` (L82), without checking gene content or similarity. Galaxy wrapper binding problems also forced the final record to be extracted locally from the Galaxy FASTA (L111).
- **GPT-5.5 code r1 (16,279 bp).** Memory limits ruled out whole-genome assembly, so the run enriched high-copy 31-mer reads with KMC (L36-L111). Canu returned only unassembled reads from that anchor-enriched set. The run then finalized "the most defensible read-polished circular candidate" (`...:L444-L447`), with no identity check.
- **DeepSeek code r2 (15,349 bp).** It polished a hifiasm seed with samtools consensus and validated it by mapping reads back to the seed itself. It reported **18.3x mean depth** (`...:L193`), which is nuclear-level coverage (hifiasm reports about 15x for nuclear contigs) and should have flagged a non-organellar contig.
- **The 0.9955 cluster.** Luna Galaxy r1–r3 and DeepSeek Galaxy r2 submitted the identical 15,445-bp sequence produced by Galaxy MitoHiFi (header `ptg000003l_rotated`, reference OP219771). DeepSeek code r3 produced the same sequence by downloading **OZ203683.1**, the public DToL mitogenome (15,445 bp), from NCBI during the code condition (`...:L35-L37`). It then edited its own unitig to match: "removed query insertions [6346, 6807, 6808]" and rotated to the reference start (L111). DeepSeek code r1 also fetched OZ203683. Galaxy MitoHiFi reaching this exact sequence without that download suggests the public record was built from these same reads. **These are not public-record substitutions in the Galaxy runs.** They are a second valid MitoHiFi contig, about 70 31-mers (a few bases) away from the reference.
- **Galaxy execution check.** Every correct Galaxy run assembled with `mitohifi` 3.2.3 jobs in Galaxy (`find_reference`, then assembly). GPT-5.5 Galaxy r3 ran some exploratory local minimap2 mapping, but it submitted the Galaxy MitoHiFi FASTA (L193-L198).

**Interpretation.** The zeros are genuine domain errors: a contig was accepted on circularity or depth alone, never tested as mitochondrial. The same weakness appears in both conditions for GPT-5.5. The scores between 0.991 and 0.996 are consensus-level variants of the same molecule and are effectively correct. Two points complicate interpretation. The IWC route needs an external NCBI reference, which conflicts with the "use only the provided inputs" wording and led GPT-5.5 Galaxy r1 to avoid MitoHiFi. And DeepSeek code r3 made its sequence match a downloaded public record.

**Tags:** `domain-knowledge-error`, `insufficient-verification`, `equivalent-answer`, `underspecified-task`, `benchmark-answer-retrieval`

---

<a id="wf_010_pseudobulk_scrna_de"></a>

### wf_010_pseudobulk_scrna_de — the 0.0 is a hard gate on a wrong BH step over otherwise-correct results; the 0.948 is an unshrunk NB GLM with no power

**Question.** Pseudobulk the AnnData `counts` layer by individual × cell type, keeping groups of at least 10 cells, and apply the specified CPM/sum gene filter. Test normal-minus-COVID-19 with a negative-binomial model that includes disease and cell type. Report unshrunk log2 fold changes, with the FDR given as a BH adjustment of the run's own p-values.

**Reference.** The IWC-derived pseudobulk matrix is 1,429 genes × 34 samples. There are route-specific DE references: edgeR (49 significant genes) and DESeq2 (68). The metric is `pseudobulk_de_composite`, the square root of (matrix score × DE score), and FDRs must be within 1e-6 of BH of the submitted p-values.

**Outcome.** 22 of 24 runs score at least 0.977. The low scorers are DeepSeek code r3 **0.0** and GPT-5.5 code r2 **0.948**.

**What the traces show.**
- **DS code r3 (0.0): the sibling write-up's claim is verified.** The run used PyDESeq2 with `cooks_filter=False, independent_filter=False`. It then replaced the package's padj with a hand-written BH that takes a *forward* `np.maximum.accumulate` over the sorted `p·m/rank` values, instead of the reverse cumulative minimum (`recovered_code/.../open_ended_code_codex_deepseek_v4_pro_r3/item_29.command.txt:L91-L99`). I recomputed this from the submitted table:
  - All 1,429 FDRs match the forward-max algorithm exactly.
  - Their largest deviation from correct BH is 0.003417, at GPBP1 (0.93518 vs 0.93176). This is the evaluator's reported value.
  - The error only inflates large FDRs. The set with FDR < 0.05 is unchanged: 121 genes either way.
  - Apart from the FDRs, the outputs match DS code r1, which scored 0.9997. The log2 fold changes are identical, the p-values agree within 2e-4, and the pseudobulk matrix is identical to that of GPT-5.5 code r2, whose matrix F1 is 1.0.
- **GPT-5.5 code r2 (0.948): correct matrix, weak DE model.** With no R available, the run fit a per-gene statsmodels NB GLM. It used gene-wise method-of-moments dispersion with no empirical-Bayes shrinkage, a library-size offset and an LRT. The resulting minimum FDR is 0.911, so there are 0 significant genes against edgeR's 49 (`analysis_steps.jsonl`, evaluator details). Direction agreement is 0.978, but the evidence component is only 0.714. Because "negative-binomial-glm" has no calibrated reference, it was scored against the edgeR reference.
- **Galaxy execution.** All 12 Galaxy runs ran edgeR or DESeq2 as Galaxy jobs. However, the gene filter, and in some runs the aggregation, was often computed locally and the resulting counts uploaded. Examples are `pseudobulk_edgeR_counts.tsv` (GPT-5.5 Galaxy r1), `pseudobulk_counts.tsv` (DS Galaxy r1) and per-sample TSVs (DS Galaxy r2/r3); Luna Galaxy r2 used Galaxy Jupyter notebooks. Sol Galaxy r1 and r3 did the whole pipeline in Galaxy (decoupler plus awk).

**Interpretation.** DS code r3 has a genuine but scientifically inconsequential statistical bug. It breaks an explicit prompt requirement, so the hard gate is legitimate, but the 0.0 greatly overstates the scientific error: an otherwise ~1.0 answer with the same significance calls. GPT-5.5 code r2 is a real methodological weakness, not a pipeline error: without dispersion shrinkage it has no power at 34 samples.

**Tags:** `statistical-error`, `format-contract-error`, `scientific-method-error`, `local-fallback-in-galaxy`

---

<a id="wf_006_atacseq_chromatin_accessibility"></a>

### wf_006_atacseq_chromatin_accessibility — high scores come from per-route references, some built from the agents' own runs; the lowest run is penalized for summit splitting

**Question.** Run the full ATAC-seq pipeline on hg19: fastp adapter trimming, a paired-end aligner, MAPQ 30, chrM and duplicate removal, then an ATAC-suitable peak caller at q 0.05 with no control. Write the peaks to BED, keeping records with duplicate coordinates, and declare the aligner and peak caller.

**Reference.** The evaluator uses one reference per declared route. For Bowtie2+MACS2 it keeps three calibrated variants (`bampe-model`, `bampe-nomodel`, `iwc-summit-split`) and takes the closest. The metric is `interval_f1`: one-to-one matching at 50 % reciprocal overlap.

**Outcome.** 23 of 24 runs score at least 0.990. The only run below 0.95 is Sol code r1 at **0.9227**. Twelve MACS2 runs have `run_record.acc` values of 0.39–0.51 that conflict with their evaluator scores.

**What the traces show.**
- **The IWC workflow's own output is matched by no run.** For every MACS2 run, the `iwc-summit-split` variant scores only 0.39–0.506 (`route.reference_variant_scores` in each `evaluation.json`, e.g. `.../galaxy_gpt_5_5_r2/evaluation.json`). Those are the `run_record.acc` values, which explains the 12 chromatin-accessibility score conflicts. The high scores come from the alternative variants: `bampe-model` (38,779 peaks, matched exactly by 5 Galaxy runs) and `bampe-nomodel` (33,488 peaks). GPT-5.5 Galaxy r2 shows the spread for one set of peaks (`galaxy_gpt_5_5_r2/evaluation.json`, `run_record.json`):

  | Reference variant | Agreement for the same 33,488 peaks |
  |---|---:|
  | `iwc-summit-split` (= `run_record.acc`) | 0.3929 |
  | `bampe-model` | 0.6602 |
  | `bampe-nomodel` (the evaluator's chosen score) | 1.0000 |

  The evaluator's provenance explains why it picks the closest variant: the query fixes filtering, q-value and control use, but not summit splitting or BAMPE model selection. So the same output reads as a failure (0.39) or as perfect (1.0) depending on which score field is reported.
- **Several route references were calibrated from a single agent run.** The recorded provenance for bowtie+macs3 (DeepSeek code r1), minimap2+macs2 (DeepSeek code r3) and bwa-mem+macs2 (Luna code r2) reads "calibrated from … the sole complete … execution record". Each of these runs scores exactly 1.0 against a reference built from itself. The Genrich reference was built "from a complete Galaxy Bowtie2 plus Genrich execution", with "a second independent Galaxy execution" at 0.99556. That means Sol Galaxy r2 (1.0) is probably the calibration source and GPT-5.5 Galaxy r3 the independent check. The Bowtie2+MACS3 reference has 33,493 peaks, exactly Luna code r1's count, so Luna code r1 is probably its source.
- **Sol code r1 is penalized for following the IWC-style protocol.** It ran `macs3 callpeak -f BAMPE -q 0.05 --keep-dup all --call-summits` and kept all 39,024 summit records, some sharing coordinates as the prompt instructs (`.../open_ended_code_gpt_5_6_sol_r1/.../codex_events.jsonl:L71,L74`). The MACS3 route reference has no summit-split variant. One-to-one matching therefore leaves the extra summit records unmatched: precision 0.857, recall 0.9989. The other MACS3 runs scored 0.991–0.9995 because they did not call summits.
- **Galaxy execution check.** All 12 Galaxy runs executed fastp, bowtie2, filtering, Picard MarkDuplicates and macs2_callpeak or genrich as `ok` Galaxy jobs. Local shell calls were API payloads and metadata only.

**Interpretation.** The near-1.0 scores measure agreement with route-specific references. Some of those references are the runs themselves, so a 1.0 on those routes is circular, not independent validation. Sol code r1's 0.92 comes from a gap in the variant registry, not a scientific error. The prompt's no-deduplication clause points toward summit splitting, which the IWC reference itself uses.

**Tags:** `reference-questionable`, `evaluator-false-negative`, `route-divergence`, `underspecified-task`

---

<a id="wf_002_rnaseq_de_visualization"></a>

### wf_002_rnaseq_de_visualization — Near-perfect scores hide changed significant-gene sets: PyDESeq2 loses YER164W, and Galaxy edgeR calls about 3× more genes

**Question.** Run a standard differential-expression analysis of changed vs reference condition on raw counts (2 vs 2 samples). Keep genes with ≥10 counts in ≥2 samples and test every retained gene. Report an unshrunken log2FC, a raw p-value and a BH FDR over the retained genes, and declare the method in `method.json`.

**Reference.** A DESeq2 result over the fixed universe of 2,526 genes, with 13 genes at FDR < 0.05. The metric (`differential_expression_continuous`) is the geometric mean of gene coverage, fold-change direction, magnitude CCC, fold-change ranking and evidence ranking. The significant-set overlap (`significant_jaccard`) is reported separately and does **not** enter the score.

**Outcome.** Every run scores ≥ 0.99, so none is below the 0.95 audit threshold. This entry is included because the continuous score hides differences in the reported conclusions. Five runs report a significant set that differs from the reference's 13 genes:
- GPT-5.5 code r1 and r3, and DeepSeek code r2 and r3: 12/13 genes (Jaccard 0.923), scores 0.99997.
- Luna Galaxy r1: 37 vs 13 genes (Jaccard 0.351), score 0.9938.

**What the traces show.**
- **The four 12-gene runs all used PyDESeq2 0.5.4, and all miss the same gene.** The gene is YER164W, with log2FC −7.14 in every run but FDR 0.48 against 0.0029 in the reference. None of the runs had R. GPT-5.5 code r1 found "no `Rscript` in the environment" and pip-installed PyDESeq2 (`open_ended_code_gpt_5_5_r1/agent_workspace/run_trace/codex_events.jsonl:L19-L46`). The DeepSeek runs ran PyDESeq2 with `cooks_filter=False, independent_filter=False` (`open_ended_code_codex_deepseek_v4_pro_r2/...:L30-L42`). Every 13-gene code run instead installed R DESeq2 through micromamba with `cooksCutoff=FALSE`. Examples: GPT-5.5 code r2 (`...:L37-L44`) and Sol code r1 (`...:L22-L37`). The difference is therefore in the implementation: the Python port's dispersion and Wald test differ from R's for an extreme-fold-change gene. That mechanism is inferred; it was not recomputed.
- **Luna Galaxy r1 chose a different valid method, and the evaluator scored it against DESeq2.** The Galaxy DESeq2 wrapper's prefilter is total-count based, so it cannot express "≥10 in ≥2 samples". The agent therefore used Galaxy's edgeR 3.36.0+galaxy7 wrapper, with a 10/2 count filter, TMM normalisation, **robust quasi-likelihood** testing and BH (`galaxy_gpt_5_6_luna_r1/.../codex_events.jsonl:L64`, `L143`; job parameters in `job_ledgers/galaxy/galaxy_gpt_5_6_luna_r1.json`). The prompt allows any standard method, and the run declared `edgeR`. No edgeR route reference exists, though, so the run was compared with DESeq2. Fold changes and rankings agree almost perfectly (magnitude CCC 0.996, ranking 0.992), but the significant-set Jaccard is 0.35 (`galaxy_gpt_5_6_luna_r1/evaluation.json`).
- **Galaxy execution.** All 12 Galaxy runs ran DESeq2 or edgeR as Galaxy jobs. BH consistency passes in every run: the largest deviation across all 24 runs is 4.2e-7, within the evaluator's 1e-6 tolerance.

**Interpretation.** A score near 1.0 here means near-identical fold changes and rankings. It does not mean the same list of significant genes. Two findings follow. First, PyDESeq2 and R DESeq2 disagree on one gene: the code environment lacked R, and the Galaxy runs used the R wrapper, which stabilises the Galaxy results. Second, an allowed method (edgeR) gives a very different significant set but still scores 0.994 against the DESeq2 reference. Report significant-set agreement alongside the continuous score, and register method-specific references before comparing methods on inferential conclusions.

**Tags:** `tool-version-difference`, `route-divergence`, `unregistered-route`, `underspecified-task`
