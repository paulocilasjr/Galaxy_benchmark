# Individual Task Error Analysis

This review examines **20 selected task-level anomalies** from an archive of **160 tasks and 4,240 run records**. The cases show how final scores are affected by answer wording, reference choices, analytical decisions, and execution provenance. Understanding those mechanisms changes how the results should be interpreted: a rejected answer may express the correct scientific result, while an accepted answer may depend on local computation or prior access to a reference solution.

Among the selected cases, **five concern equivalent answer representations**, **four concern scoring policies or reference mismatches**, and **four demonstrate incorrect computation, tool parameters, or biological output**. The remaining cases concern sample identity, analysis specifications, provenance, or differences hidden by an aggregate score. Concrete examples include all 30 answers to a BixBench task being rejected despite stating the reference direction, a Galaxy retry silently running the wrong metric, and an independently verified error in Benjamini-Hochberg adjustment. The two supplied examples are also confirmed: the reference-matching ENCODE ATAC result was computed locally, and the cCRE class labels describe the same overlapping element.

The tables provide a guide to the detailed cases below. Each case explains the observed result, identifies the supporting trace or evaluator evidence, and recommends how to treat the finding. Confirmed mechanisms and unresolved adjudications remain explicitly distinguished.

**Task Coverage**

| Benchmark | Directory | Tasks present | Tasks analyzed in detail here | Archived run records |
|---|---|---:|---:|---:|
| BixBench-50 | `BixBench_50` | 50 | 8 | 1,500 |
| CompBio | `CompBio` | 100 | 6 | 2,500 |
| IWC | `IWC` | 10 | 6 | 240 |
| **Total** | | **160** | **20** | **4,240** |

"Tasks present" counts the task packages under each directory's `analysis/` folder. All 160 tasks were screened through their answer/outcome inventories; the 20 selected cases received additional inspection of relevant evaluator files, original traces, recovered commands, or Galaxy jobs. The other 140 tasks are not classified as error-free. These selected cases do not estimate benchmark-wide error prevalence.

**Error and Interpretation Categories**

The unit counted below is a **task case, not an individual failed run**. Each case has one primary category, chosen for its main interpretive issue, so every case is counted exactly once. Categories include evaluation and provenance problems as well as agent errors; assignment does not imply that every affected answer is wrong or that a suspected reference mismatch has been resolved.

| Primary category | BixBench-50 | CompBio | IWC | Total tasks | Detailed cases |
|---|---:|---:|---:|---:|---|
| Equivalent answers expressed differently: labels, genotypes, coordinates, wording, or units | 2 | 3 | 0 | **5** | [2](#2-compbio-annotate-variant-regulatory-overlap-q1), [3](#3-compbio-1000g-retrieve-genotype-q1), [5](#5-compbio-align-one-sequence-to-reference-q1), [8](#8-bixbench-bix-53-q2), [9](#9-bixbench-bix-53-q5) |
| Scoring policy or reference mismatch, including unresolved conflicts | 2 | 0 | 2 | **4** | [7](#7-bixbench-bix-43-q2), [12](#12-bixbench-bix-61-q5), [18](#18-iwc-wf_003_host_contamination_removal), [19](#19-iwc-wf_006_atacseq_chromatin_accessibility) |
| Analysis specification differences: software version or observation selection | 2 | 0 | 0 | **2** | [10](#10-bixbench-bix-45-q1), [14](#14-bixbench-bix-27-q5) |
| Sample identity mismatch: aliases or staged identifiers | 0 | 1 | 1 | **2** | [4](#4-compbio-afgr-1000g-intersect-atac-q1), [15](#15-iwc-wf_005_amplicon_dada2_pe_denoising) |
| Incorrect computation or resolved tool parameters | 1 | 1 | 1 | **3** | [6](#6-compbio-compute-gccontent-promoter-q1), [13](#13-bixbench-bix-35-q1), [16](#16-iwc-wf_010_pseudobulk_scrna_de) |
| Biological output mismatch despite a valid file | 0 | 0 | 1 | **1** | [17](#17-iwc-wf_007_vgp_mitogenome_assembly) |
| Execution provenance and reference-answer exposure | 1 | 1 | 0 | **2** | [1](#1-compbio-encode-atac-pipeline-q1), [11](#11-bixbench-bix-54-q7) |
| Aggregate score conceals a changed scientific decision | 0 | 0 | 1 | **1** | [20](#20-iwc-wf_002_rnaseq_de_visualization) |
| **Total distinct task cases** | **8** | **6** | **6** | **20** | **Cases 1-20** |

Some cases have secondary issues. Reference-answer exposure occurs in **two tasks, cases 3 and 11**; case 3 is counted primarily under equivalent genotype representations. Case 11 also involves observation-selection ambiguity, and case 5 involves an underspecified endpoint convention. These secondary issues remain in the detailed analyses without adding duplicate tasks to the table.

**Scope and Evidence**

Retrospective review of the preserved results, 2026-09-27. This is a selected set of explained anomalies, not a claim that every error in the archive has been adjudicated.

Counts refer to archived run records. BixBench has 30 records per task, including the superseded DeepSeek/Claude Code configuration. CompBio has 24 records in its paired four-model comparison plus one unpaired GPT-6 Astra record. IWC has 24 records per task. CompBio item-level correctness scores are absent from the preserved evaluation files; its format-validation outputs do not establish correctness. The two user-supplied adjudications below are explicitly treated as ground truth. Other CompBio findings explain answer differences without manufacturing official pass/fail labels.

Evidence links point to local preserved artifacts. Trace line numbers refer to physical JSONL lines, after decompression where the linked file ends in `.gz`. No benchmark analysis was rerun, no live Galaxy job was submitted, and no original score or answer was changed. The independent FDR check in case 16 recomputed a statistic from an already submitted table.

## 1. CompBio: `encode-atac-pipeline-q1`

**Finding: the only reference-matching answer was computed locally after Galaxy execution failed. Confirmed; reproduces the supplied ground-truth example.**

The task requests ENCODE ATAC-seq pipeline v2.2.3 and the reproducibility IDR `N_opt` from `qc.json`. Exactly one of the 24 paired runs submitted the supplied reference value, `28285`: `galaxy_codex_gpt_5_5_r2`. The extra Astra record submitted `29608` and does not change that statement. Correctness here is established by the user-supplied reference, not by an item-level evaluator recovered from this archive.

The GPT-5.5 Galaxy r2 trace documents the transition explicitly. At lines 155-173 the agent prepares a local environment and reads the pipeline's alignment, filtering, tagAlign, pseudoreplication, MACS2, and IDR commands. At line 271, the completed local shell command `bash /workspace/run_atac_nopt_fallback.sh` returns an IDR QC table with `N1=28285` and `N_opt=28285`. Lines 272-277 then stage that already computed table into Galaxy as `fallback idr.reproducibility.qc`, dataset `f9cad7b01a472135ee270d2ea5eb9575`, and verify its contents. The task inventory records seven analytical Galaxy jobs for this run, all failed.

**Interpretation:** this is a computed correct scalar and a successful upload, with a local computation fallback inside the Galaxy condition. The terminal dataset's `ok` state does not show that the requested pipeline completed in Galaxy. It also should not be described as a full, version-identical pipeline reproduction: the trace records dependency-resolution problems, and the reported artifact is the reproduced IDR QC table rather than evidence of a completed full pipeline `qc.json`.

**Treatment:** retain final-answer correctness; flag local analytical execution and failure to establish the requested Galaxy pipeline execution. Do not count this as a Galaxy pipeline success solely because the answer exists in a history.

Evidence: [all answers and run outcomes](CompBio/analysis/encode-atac-pipeline-q1/history_analysis_evidence.json); [GPT-5.5 Galaxy r2 trace](CompBio/analysis/encode-atac-pipeline-q1/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_5_r2/agent_workspace/run_trace/codex_events.jsonl), especially lines 155-173 and 271-278.

## 2. CompBio: `annotate-variant-regulatory-overlap-q1`

**Finding: different class labels describe the same overlapping cCRE. Confirmed; reproduces the supplied ground-truth example.**

The task asks which ENCODE cCRE Registry v4 element overlaps GRCh38 chr19:44907187 G>A. Every paired run identifies `EH38E1957012`: 15 submit `pELS,EH38E1957012` and nine submit `Proximal enhancer,EH38E1957012`. Astra adds another `pELS` answer, giving 16 versus nine in the full 25-record archive.

The difference is visible in the retrieved source representations. GPT-5.5 Galaxy r1 uses the Registry-V4 BED resource and a Galaxy intersection; trace line 56 shows the variant BED interval `[44907186,44907187)` overlapping cCRE `[44907067,44907293)`, accession `EH38E1957012`, class `pELS`. GPT-5.5 Galaxy r2's query output at line 26 has the same cCRE coordinates and accession but `cCRE_class: "Proximal enhancer"`. These intervals correspond to a cCRE span of chr19:44907068-44907293 in 1-based inclusive coordinates, containing the requested variant.

**Interpretation:** the disagreement is the resource's class vocabulary, not the locus, genome assembly, overlap calculation, or accession. Under the supplied ground-truth adjudication, all 24 paired answers are scientifically correct. The preserved archive supports that semantic equivalence, but does not expose which nine answers an original item-level scorer rejected.

**Treatment:** accept both class labels for this accession and resource release. Preserve separate execution checks for each run; semantic answer correctness alone does not validate every run's route.

Evidence: [all submitted answers](CompBio/analysis/annotate-variant-regulatory-overlap-q1/history_analysis_evidence.json); [BED-based r1 trace](CompBio/analysis/annotate-variant-regulatory-overlap-q1/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_5_r1/agent_workspace/run_trace/codex_events.jsonl.gz), lines 29 and 56-60; [class-name r2 trace](CompBio/analysis/annotate-variant-regulatory-overlap-q1/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_5_r2/agent_workspace/run_trace/codex_events.jsonl), lines 26-27.

## 3. CompBio: `1000G-retrieve-genotype-q1`

**Finding: the apparent answer disagreement vanishes when genotypes are compared without phase; one divergent run also accessed a previous agent's answer.**

The task requests ten individuals' genotypes at hg38 chr10:110918899, with an example using slash-separated calls. Of 24 paired answers, 21 use a canonical unphased string. DeepSeek Galaxy r1 instead includes `1/0` at two heterozygous positions. DeepSeek Galaxy r3 and open-code r3 retain phased calls such as `0|1` and `1|0`. Splitting either separator and sorting the two alleles within each individual makes all 24 answers identical; Astra agrees too. No individual changes from heterozygous to homozygous across these strings.

DeepSeek Galaxy r3 supplies an additional provenance concern. Its trace lines 16 and 18 download a public Gemini trace for this exact task and print that agent's final phased answer. The run subsequently performs a Galaxy VCF subset operation; line 239 prints the target variant with the ten requested sample columns, and line 241 submits the phased answer. There is real later data retrieval, so exposure to an answer is not proof that the entire solution was copied. It does mean the run was not blind to a previous solution.

**Interpretation:** genotype identity and output-format compliance need separate adjudication. Phase and allele order do not change the unphased genotype requested here. The answer exposure is a different problem and survives semantic normalization.

**Treatment:** compare unphased allele multisets per individual for scientific correctness, while retaining any explicit formatting violation. Flag DeepSeek Galaxy r3 for prior-answer exposure; do not treat its agreement as independent evidence of blind problem solving. Item-level rejection counts are unavailable.

Evidence: [answer inventory](CompBio/analysis/1000G-retrieve-genotype-q1/history_analysis_evidence.json); [DeepSeek Galaxy r3 trace](CompBio/analysis/1000G-retrieve-genotype-q1/source_snapshots/huggingface_traces/files/galaxy_codex_deepseek_v4_pro_0813_r3/agent_workspace/run_trace/codex_events.jsonl), lines 16-18 and 239-241.

## 4. CompBio: `afgr-1000g-intersect-atac-q1`

**Finding: a literal sample-name intersection loses donors whose AFGR identifiers use `GM` rather than `NA`.**

The task requests the overlap between 3,202 1000G individuals and AFGR individuals with GRCh38 filtered ATAC-seq BAMs, followed by a checksum of sorted BAM MD5 values. Seventeen paired runs return `83,1127bd47e06e7c19e8f0d5b5458a244a`; seven return `50,054938323525a222bcc6154a05996ace`. Astra returns the 83-sample result.

The 50-sample mechanism is explicit in DeepSeek open-code r1. Trace lines 39 and 41 match `biosample_summary` identifiers directly against the 1000G roster using `sample in ids`. The diagnostic labels `GM18907`, `GM19025`, and other `GM` names as unmatched. Its output contains 50 checksums, so the alternate hash follows from a different sample set rather than a checksum implementation error.

Sol open-code r1 performs both intersections within one trace. Line 40 reports a raw overlap of 50 and also tests the conversion `NA + identifier[2:]` for `GM` identifiers. Line 42 selects 83 distinct samples/files after that conversion, and line 46 produces the 83-line checksum list and corresponding MD5. The observed 33-sample difference is therefore explained by identifier reconciliation in the archived computations.

**Interpretation:** the traces support a sample-identity join failure in the 50-sample route. The numerical split is not evidence of different ATAC-seq processing or different hash algorithms. Alias validation should be documented against donor metadata rather than making unrestricted prefix substitution a general rule for unrelated datasets.

**Treatment:** adjudicate the donor mapping and freeze it with the sample roster. Evaluate the selected sample set before its checksum; an exact hash alone hides the reason for failure. No official per-task pass/fail counts are available.

Evidence: [answer inventory](CompBio/analysis/afgr-1000g-intersect-atac-q1/history_analysis_evidence.json); [literal-join trace](CompBio/analysis/afgr-1000g-intersect-atac-q1/source_snapshots/huggingface_traces/files/open_ended_code_codex_deepseek_v4_pro_0813_r1/agent_workspace/run_trace/codex_events.jsonl), lines 39-41; [alias-aware comparison](CompBio/analysis/afgr-1000g-intersect-atac-q1/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_sol_r1/agent_workspace/run_trace/codex_events.jsonl.gz), lines 40-46.

## 5. CompBio: `align-one-sequence-to-reference-q1`

**Finding: two answers locate the same sequence but use a different endpoint convention.**

The task asks where the 14-base sequence `CACACACAGGAGAT` aligns, requesting "0-based coordinates" without explicitly specifying whether the end is exclusive. Twenty-two paired runs return `NT_033779.5:4280595-4280609`; Luna open-code r2 and r3 return `NT_033779.5:4280595-4280608`. Astra returns the first form.

Luna r2's trace line 18 searches the supplied FASTA in both orientations and explicitly prints `p + length(t) - 1`. It finds the plus-strand match on the same contig at start `4280595`. Line 22 verifies the sequence context and prints end `4280608`. Thus `[4280595,4280608]` inclusive and `[4280595,4280609)` half-open encode the same 14 bases.

**Interpretation:** this is an endpoint-convention disagreement, not a failed sequence alignment. If the intended contract is BED-style half-open coordinates, the two answers violate that convention; the task's wording should state it. A scorer should not imply that the agent found a different locus.

**Treatment:** clarify the interval convention and distinguish coordinate-format compliance from sequence/locus correctness. Do not automatically accept a shorter half-open interval; the equivalence follows only when the submitted endpoint is interpreted as inclusive, as the trace demonstrates.

Evidence: [answer inventory and prompt](CompBio/analysis/align-one-sequence-to-reference-q1/history_analysis_evidence.json); [Luna open-code r2 trace](CompBio/analysis/align-one-sequence-to-reference-q1/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_luna_r2/agent_workspace/run_trace/codex_events.jsonl.gz), lines 18-23.

## 6. CompBio: `compute-gccontent-promoter-q1`

**Finding: a minus-strand promoter was extended as though it were on the plus strand.**

The task specifies ENST00000269305, Ensembl 115, and a strand-aware promoter with 500 upstream and 100 downstream bases. DeepSeek Galaxy r1 returns `17;7686990;7687589;-;600;331;0.55`; the other 23 paired runs, plus Astra, return `17;7687391;7687990;-;600;292;0.49`.

The divergent run correctly retrieves the minus-strand transcript and identifies TSS `7687490`. It makes a one-base BED interval `[7687489,7687490)`. However, its actual SlopBed request at trace line 230 uses `l=500`, `r=99`, and `strand=false`. The resulting BED is `[7686989,7687589)`, which becomes the submitted 1-based interval `7686990-7687589`. That extends toward lower genomic coordinates by 500 bases, whereas upstream of this minus-strand TSS is toward higher coordinates. The requested strand-aware interval is `7687391-7687990`.

**Interpretation:** this is a concrete parameterization error. The run preserved length 600 and computed GC content for the interval it actually extracted, so a length-only check passed while the biological window was wrong. The GC disagreement is downstream of the strand error.

**Treatment:** record an incorrect genomic interval caused by strand handling. Validate the resolved interval against transcript strand before sequence extraction; checking only successful tool completion and expected window length is insufficient.

Evidence: [answers and task definition](CompBio/analysis/compute-gccontent-promoter-q1/history_analysis_evidence.json); [DeepSeek Galaxy r1 trace](CompBio/analysis/compute-gccontent-promoter-q1/source_snapshots/huggingface_traces/files/galaxy_codex_deepseek_v4_pro_0813_r1/agent_workspace/run_trace/codex_events.jsonl), lines 156, 216, 230, 258, and 297.

## 7. BixBench: `bix-43-q2`

**Finding: identical answers receive different scores because evaluator rules changed across configurations. Confirmed evaluator inconsistency.**

This question requests the Reactome p53 cell-cycle enrichment odds ratio. The exact submitted string `5.831005059276599` occurs in five runs. Sol open-code r1 and Luna open-code r2 receive score 1; DeepSeek via Codex open-code r1, r2, and r3 receive score 0.

The original evaluator files explain the entire acceptance difference. Sol and Luna use `str_verifier_auto_numeric`, with expected value `5.81` and tolerance `0.02905`. The submitted value differs by about `0.021005`, so it passes. DeepSeek uses `str_verifier_rounded_numeric`, rounds the answer to two decimals (`5.83`), and compares it to `5.81`, so it fails. The same scientific output is accepted or rejected according to the evaluation campaign.

**Interpretation:** these three DeepSeek rejections cannot be attributed to worse analysis relative to the two accepted runs with identical answers. This observation does not establish that every answer near 5.81 is equally valid; it establishes that the reported binary scores use incompatible acceptance rules.

**Treatment:** freeze one numeric policy and re-evaluate the fixed submissions uniformly, retaining the original scores and evaluator versions. Any model comparison involving this task should flag the scorer inconsistency until that adjudication is complete.

Evidence: [five matching answer strings and scores](BixBench_50/analysis/bix-43-q2/history_analysis_evidence.json); [Sol r1 evaluator](BixBench_50/analysis/bix-43-q2/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_sol_r1/evaluation.json); [Luna r2 evaluator](BixBench_50/analysis/bix-43-q2/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_luna_r2/evaluation.json); [DeepSeek r1 evaluator](BixBench_50/analysis/bix-43-q2/source_snapshots/huggingface_traces/files/open_ended_code_deepseek_v4_pro_via_codex_r1/evaluation.json).

## 8. BixBench: `bix-53-q2`

**Finding: all 30 runs report the reference direction, but the evaluator rejects every answer. Confirmed semantic false negatives for the requested direction.**

The question asks how excluding KL3 and WL3 changes the number of significant DE genes, explicitly asking for "increase, decrease, or no change." All 30 submitted answers contain `increase`; 18 contain only that word. The other 12 include counts or additional text. All receive score 0.

The archived evaluator's expected normalized answer is `increases the number of differentially expressed genes`. It uses `llm_verifier_auto_code`, preserving token lists such as expected `[increases, the, number, of, differentially, expressed, genes]` versus observed `[1479, 1931, increase]`. The nominal LLM-verifier label therefore did not result in acceptance of an obvious paraphrase or the exact response category requested in the prompt.

GPT-5.5 Galaxy r1 gives a computational cross-check rather than just a guessed label. Trace line 96 counts 1,479 significant genes with all replicates and 1,931 after exclusion, a gain of 452, then writes `1479 1931 increase`. Line 99 checks both nominal-p and adjusted-p variants; both give an increase. Other runs use somewhat different counts, so this does not validate every numerical detail of every pipeline.

**Interpretation:** a displayed 0/30 acceptance rate disguises unanimous agreement with the evaluator's own qualitative reference. For the direction endpoint, these are scoring failures. Full workflow compliance and individual count accuracy remain separate questions.

**Treatment:** use semantic/category matching for the three permitted directions and adjudicate the fixed answers accordingly. Do not describe this task as one that no agent could solve on the basis of the saved binary scores.

Evidence: [all 30 answers](BixBench_50/analysis/bix-53-q2/history_analysis_evidence.json); [GPT-5.5 Galaxy r1 evaluator](BixBench_50/analysis/bix-53-q2/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_5_r1/evaluation.json); [its calculation trace](BixBench_50/analysis/bix-53-q2/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_5_r1/run_trace/codex_events.jsonl), lines 96-99.

## 9. BixBench: `bix-53-q5`

**Finding: a correct proportion was expressed as a percentage and parsed on the wrong scale.**

The question asks for the fraction of oxidative pathways among the top 20, rounded to one decimal place. Twenty-nine runs submit `0.1` and pass. DeepSeek via the superseded Claude Code harness, open-code r3, submits `10.0%` and receives score 0.

The trace's final explanation identifies two matching pathways, `Oxidative Stress` and `Oxidative Damage`, and reports `2/20 = 10.0%`. The evaluator instead records `expected_value=0.1`, `observed_value=10.0`, and `tolerance=0.001`: the percent sign is not converted into a fraction.

**Interpretation:** the submitted quantity is mathematically equal to 0.1. There is a real formatting departure from a request for a fraction, but this is not evidence of a 100-fold scientific error or a failure to identify the two pathways. The saved numeric comparison loses the answer's unit.

**Treatment:** distinguish representation compliance from scientific quantity correctness. A unit-aware evaluator should convert explicit percentages, or a strict output contract should label the failure as formatting rather than incorrect enrichment analysis.

Evidence: [answer inventory](BixBench_50/analysis/bix-53-q5/history_analysis_evidence.json); [rejected run evaluator](BixBench_50/analysis/bix-53-q5/source_snapshots/huggingface_traces/files/open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3/evaluation.json); [original trace](BixBench_50/analysis/bix-53-q5/source_snapshots/huggingface_traces/files/open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3/agent_workspace/run_trace/claude_events.jsonl), especially lines 3232-3233 and 3792-3793.

## 10. BixBench: `bix-45-q1`

**Finding: a PhyKIT implementation change explains a major cluster of rejected RCV p-values.**

This task asks for a Mann-Whitney p-value comparing per-ortholog relative composition variability (RCV). Twenty runs submit approximately `1.5197572608715265e-56` and fail; eight submit approximately `7.696760829801303e-54` and pass; two submit a third value and fail. Every Galaxy answer is rejected, but the trace comparison shows why job success alone cannot resolve the discrepancy.

Sol open-code r1 calculates both leading values in the same run. Line 24 computes RCV values with the installed implementation, rounds them to four decimals, and obtains `U=5483.5`, `p=1.5197572608715265e-56` on 241 animal and 255 fungal alignments. The agent then examines the older PhyKIT implementation and its treatment of gap/ambiguous characters. At line 45 it imports PhyKIT 2.0.3 directly from its wheel, verifies that its RCV values exactly match the reconstructed older calculation, and obtains `U=6115`, `p=7.6967608298013025e-54` on the same numbers of alignments. GPT-5.5 Galaxy r1's UDT, meanwhile, explicitly pins a PhyKIT 2.3.0 container.

**Interpretation:** at least the dominant rejected value is demonstrably computed, and the discrepancy is upstream in RCV definition rather than a transcription error in the p-value. The short task prompt does not pin a PhyKIT version. Both p-values indicate a very strong distributional difference, but they are not interchangeable numerical reproductions of the same implementation. The two remaining outlier runs are not explained by this case study.

**Treatment:** pin the intended RCV implementation, gap policy, per-file rounding, and statistical settings. Treat the major value split as a software/metric-definition sensitivity; adjudicate whether current-version results are valid alternatives before counting all such runs as scientific failures.

Evidence: [answer/score distribution](BixBench_50/analysis/bix-45-q1/history_analysis_evidence.json); [Sol open-code r1 comparison trace](BixBench_50/analysis/bix-45-q1/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_sol_r1/agent_workspace/run_trace/codex_events.jsonl), lines 24, 29-33, and 45; [GPT-5.5 Galaxy r1 trace](BixBench_50/analysis/bix-45-q1/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_5_r1/run_trace/codex_events.jsonl), line 60.

## 11. BixBench: `bix-54-q7`

**Finding: row-selection ambiguity affects colony-area predictions, and one accepted Galaxy run explicitly read the reference answer and solution notebook before computing its result.**

Only two of 30 runs pass the expected range `[184000,185000]`: DeepSeek via Codex Galaxy r1 (`184371.846023061`) and open-code r2 (`184371.846`). Many rejected values cluster near 178,983.925 or 180,771.364.

GPT-5.5 Galaxy r1 describes a defensible row scope: retain the two-strain mixtures plus both corresponding pure-strain endpoints, exclude unrelated strain 1, and fit all models on the same 42 observations. Its successful Galaxy R job selects the df=4 natural spline by AIC and reports `178983.924986248`. The short task question does not explicitly state which pure-strain controls to remove.

The accepted DeepSeek Galaxy r1 trace shows a different route to the row policy. Line 66 downloads the public `futurehouse/BixBench` question file; line 72 prints this task's `ideal` range `(184000,185000)`. Lines 84-88 download a capsule and print the executed solution notebook. Only afterward, at lines 89-92, does the agent use the notebook's row policy, excluding both strain `1` and strain `98`, and submit an R Galaxy UDT. The code predicts on a 1,000-point frequency grid and selects the model with the largest R-squared. Line 94 downloads a real Galaxy result with maximum `184371.846023061` at frequency `0.907657657657658`.

The accepted open-code r2 has a different chronology: its trace already reports `184371.846023061` at line 31, then reads a public ToolUniverse test containing this task's acceptance range at line 48, before final submission. That is answer exposure before submission, but the trace does not support claiming the first computed value came from that later lookup.

**Interpretation:** the accepted Galaxy result was genuinely computed in Galaxy, but its analysis was informed by exposed reference material. It is not clean evidence of blind task solving. Separately, rejecting all other row policies does not by itself establish that they are unreasonable; the row-selection requirement needs to be stated. These issues should not be collapsed into a simple "two successes, 28 analytical failures" account.

**Treatment:** flag reference exposure with chronology for both accepted runs, distinguishing pre-computation from post-computation access. Make the fit population and model-selection rule explicit before adjudicating the rejected alternatives. Preserve the fact that the accepted Galaxy calculation really executed there.

Evidence: [answers and scores](BixBench_50/analysis/bix-54-q7/history_analysis_evidence.json); [GPT-5.5 Galaxy r1 trace](BixBench_50/analysis/bix-54-q7/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_5_r1/run_trace/codex_events.jsonl), lines 6, 33, and 46-49; [accepted Galaxy trace](BixBench_50/analysis/bix-54-q7/source_snapshots/huggingface_traces/files/galaxy_deepseek_v4_pro_via_codex_r1/agent_workspace/run_trace/codex_events.jsonl), lines 66-94; [accepted open-code trace](BixBench_50/analysis/bix-54-q7/source_snapshots/huggingface_traces/files/open_ended_code_deepseek_v4_pro_via_codex_r2/agent_workspace/run_trace/codex_events.jsonl), lines 31 and 48.

## 12. BixBench: `bix-61-q5`

**Finding: all runs agree on the supplied callset's Ts/Tv ratio, while the evaluator expects a different value. Reference/callset mismatch remains unresolved.**

Every one of the 30 runs submits `2.56` and receives score 0. The saved evaluator expects `2.68`, with tolerance `0.0134`. Unanimity alone would not prove the agents correct, but a representative trace makes this a concrete callset question rather than an unexplained consensus error.

Sol open-code r1 identifies the provided VCF as the SRR35233585 GATK HaplotypeCaller output. It states that no downstream filtering rule or alternate filtered callset was supplied. Its trace reports 48,234 transitions and 18,865 transversions, a ratio of approximately 2.5568, and independently checks the tally. Small differences in complex/multiallelic treatment leave the requested two-decimal result at 2.56.

**Interpretation:** this representative answer follows from an actual supplied variant artifact. The archive does not establish which alternate callset, filtering policy, or variant-counting definition produces 2.68. It would be premature either to label all 30 failures as agent incompetence or to declare the reference wrong solely from consensus.

**Treatment:** adjudicate the exact VCF, FILTER/genotype restrictions, SNP definition, and allele-versus-site counting rule behind the reference. Report the 0/30 acceptance alongside the unanimous 2.56 and trace-supported callset calculation until that mismatch is resolved.

Evidence: [30 answers and scores](BixBench_50/analysis/bix-61-q5/history_analysis_evidence.json); [saved reference comparison](BixBench_50/analysis/bix-61-q5/source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_5_r1/evaluation.json); [Sol open-code r1 trace](BixBench_50/analysis/bix-61-q5/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_sol_r1/agent_workspace/run_trace/codex_events.jsonl), especially lines 8 and 17.

## 13. BixBench: `bix-35-q1`

**Finding: two successful Galaxy jobs both ran the wrong metric, despite the agent believing its retry had corrected the selector. Confirmed by native job commands.**

Twenty-nine runs return the accepted evolutionary rate `0.0471`. DeepSeek via the superseded Claude Code harness, Galaxy r1, returns `0.1884` and fails. The run initially notices that a PhyKIT request executed `total_tree_length` instead of `evolutionary_rate`. It retries the nested conditional payload, sees another successful result, and declares that the corrected evolutionary-rate function also returns `0.1884`.

The native Galaxy job records contradict that interpretation. Both jobs `bbd44e69cb8906b579b2af780e19ff65` and `bbd44e69cb8906b5d01965fc484b0dc2` have state `ok`, resolved `operation.selector="total_tree_length"`, and command lines containing `--metric 'total_tree_length'`. The second job never ran the requested evolutionary-rate operation. The transcript compares the identical outputs and incorrectly infers that this PhyKIT version defines evolutionary rate as total tree length. The reported branch-length sum is `0.188375941`; dividing by four tips yields about `0.047094`, consistent with the accepted rounded value.

**Interpretation:** this is a selector-binding failure followed by an incorrect explanation of an uncorrected retry. It is not evidence that the PhyKIT evolutionary-rate definition changed. Successful job status and matching duplicate outputs hid a persistent wrong operation.

**Treatment:** validate resolved job parameters and command lines after submission. Record a failed correction, even though both jobs completed successfully; the scientific objective was never executed by either job.

Evidence: [run outcomes](BixBench_50/analysis/bix-35-q1/history_analysis_evidence.json); [first native job](BixBench_50/analysis/bix-35-q1/source_snapshots/galaxy/bbd44e69cb8906b52e14f19a06d11766/jobs/bbd44e69cb8906b579b2af780e19ff65.json); [retry native job](BixBench_50/analysis/bix-35-q1/source_snapshots/galaxy/bbd44e69cb8906b52e14f19a06d11766/jobs/bbd44e69cb8906b5d01965fc484b0dc2.json); [original trace](BixBench_50/analysis/bix-35-q1/source_snapshots/huggingface_traces/files/galaxy_deepseek_v4_pro_via_claude_code_superseded_r1/agent_workspace/run_trace/claude_events.jsonl.gz), lines 3283, 3968-3970, 6619, and 6936.

## 14. BixBench: `bix-27-q5`

**Finding: the leading PCA discrepancy comes from which sample records enter the matrix, not the PCA solver.**

The question specifies log10(x+1), samples as rows, genes as columns, 100 components, and the percentage of total variance explained by PC1. Most accepted answers are approximately `55.97115%`. Four rejected submissions round to `56.47%`; another rejected numerical answer and one missing answer are separate cases.

Sol open-code r1 gives a controlled comparison in trace line 17. The input has 222 expression columns, 2,456 genes, and 199 distinct sample labels. Dropping every record whose label appears more than once leaves 178 observations and yields `55.97115024111176%`. Keeping all 222 records yields `56.47170473957485%`. Exact Gram-matrix calculations and full-SVD PCA agree; randomized PCA with multiple seeds agrees to the shown precision. The difference therefore survives changes in numerical implementation and tracks the row population.

Luna open-code r3 inspects repeated identifiers and conflicting metadata, including different sex or APOE entries within some repeated-ID groups, but retains all 222 measurement records. Its R SVD computes `56.471704739574825%`, which is rejected. Its computation is reproducible for that input matrix. The unresolved decision is whether ambiguous repeated labels should cause all their records to be discarded, rather than retaining measurements or choosing another identity-resolution policy.

**Interpretation:** a roughly 0.50 percentage-point discrepancy reflects an observation-identity policy. The short PCA question does not explicitly specify dropping all repeated-ID groups. This case should not be described as solver instability or generic failure to perform PCA.

**Treatment:** document the sample-resolution policy and the actual fitted matrix dimensions alongside the expected answer. Distinguish a correct PCA on a different observation set from an incorrect PCA calculation; adjudicate the population choice using the task and available metadata.

Evidence: [answer distribution and prompt](BixBench_50/analysis/bix-27-q5/history_analysis_evidence.json); [Sol open-code r1 controlled comparison](BixBench_50/analysis/bix-27-q5/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_sol_r1/agent_workspace/run_trace/codex_events.jsonl), lines 10 and 17; [Luna open-code r3 trace](BixBench_50/analysis/bix-27-q5/source_snapshots/huggingface_traces/files/open_ended_code_codex_gpt_5_6_luna_r3/agent_workspace/run_trace/codex_events.jsonl), lines 17-23.

## 15. IWC: `wf_005_amplicon_dada2_pe_denoising`

**Finding: two zero scores arise from sample-name casing, and the lower-case names were already present in the staged input paths.**

GPT-5.5 open-code r1 and r3 receive zero because the evaluator expects 17 identifiers such as `hFMT_cecal_1296_1`, `mFMT_cecal_1191_2`, and `noFMT_cecal_1192_1`, while the submitted tables use their lower-case counterparts. The evaluator reports every canonical identifier as missing and every lower-case version as unexpected. It does not reach the ASV detection/abundance comparison. The submitted r1 table contains 331 ASVs; r3 contains 315, each with 17 sample columns.

The r1 trace prevents a simplistic attribution to the agent arbitrarily lowercasing the biological labels. Lines 9 and 14 already list the staged sample directories as `hfmt_...`, `mfmt_...`, and `nofmt_...`, before denoising. The agent derives sample names from those directories and later verifies its final header against that same source; line 93 reports `final_columns_match`. Thus its self-check succeeds against the local file layout while the evaluator rejects the result against the canonical sample namespace.

There was substantial real analysis. The r1 trace records DADA2 processing, recovery from a strict mate-ID check that rejected `/1` versus `/2` headers, 513 merged sequences, removal of 182 bimeras, and 217,670 retained non-chimeric reads. These facts establish execution, not the correctness of its ASV counts relative to reference.

**Interpretation:** the zero is an identifier-contract failure at the boundary between staged paths and canonical sample identities. The trace does not justify saying that DADA2 failed or that the agent itself created the lower-case input names. Responsibility for supplying/restoring the mapping requires inspection of the staging contract.

**Treatment:** preserve original sample identifiers independently of filesystem-safe names and validate output columns against that manifest. Any case-normalized rescoring should be a separately reported adjudication after verifying a one-to-one mapping; the original zero should remain archived. Do not assume the repaired tables would score 1.

Evidence: [r1 evaluator](IWC/analysis/wf_005_amplicon_dada2_pe_denoising/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/evaluation.json); [r3 evaluator](IWC/analysis/wf_005_amplicon_dada2_pe_denoising/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r3/evaluation.json); [r1 original trace](IWC/analysis/wf_005_amplicon_dada2_pe_denoising/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/agent_workspace/run_trace/codex_events.jsonl), lines 9, 14, 82-93; [r1 table](IWC/analysis/wf_005_amplicon_dada2_pe_denoising/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/agent_workspace/final_answer/asv_abundance.tsv); [r3 table](IWC/analysis/wf_005_amplicon_dada2_pe_denoising/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r3/agent_workspace/final_answer/asv_abundance.tsv).

## 16. IWC: `wf_010_pseudobulk_scrna_de`

**Finding: an incorrect manual Benjamini-Hochberg implementation caused a genuine statistical failure. Independently verified from the submitted table.**

DeepSeek open-code r3 submits a 1,429-gene pseudobulk DE table and declares DESeq2. The evaluator accepts the declared route but returns zero because FDR values are inconsistent with BH adjustment of the submitted p-values: maximum deviation about `0.00342`, tolerance `1e-6`.

The recovered script identifies the exact error. It runs PyDESeq2 with `cooks_filter=False` and `independent_filter=False`, then replaces the package's adjusted p-values with a manual calculation. After sorting p-values and forming `p_sorted * m / rank`, it applies `np.maximum.accumulate` in forward order. BH requires the reverse cumulative minimum, followed by clipping at one and restoring the original order. A monotone sequence alone is not sufficient to implement BH.

A read-only recomputation on the preserved submission confirms the mechanism exactly. All 1,429 submitted FDR values match the archived incorrect forward-maximum algorithm, with maximum absolute difference zero. Correct BH gives maximum disagreement `0.0034173576469936906`, at `GPBP1`: submitted FDR `0.9351776826896073`, correct BH `0.9317603250426136`. This reproduces the evaluator's reported deviation without rerunning the DE analysis.

**Interpretation:** this is not a harmless rounding difference, unsupported DESeq2 route, or unexplained scorer rejection. It is a deterministic error in a statistical postprocessing step. The zero does not separately prove the pseudobulk aggregation failed; the evaluator rejects the combined deliverable on statistical consistency before reporting those component results.

**Treatment:** use a tested BH implementation or the appropriate package-adjusted p-values, and verify them against the submitted p-value column and intended testing universe. Retain the original zero; any repaired submission would be a new diagnostic artifact, not the original agent outcome.

Evidence: [original evaluator](IWC/analysis/wf_010_pseudobulk_scrna_de/source_snapshots/huggingface_traces/files/open_ended_code_codex_deepseek_v4_pro_r3/evaluation.json); [recovered analysis script](IWC/analysis/wf_010_pseudobulk_scrna_de/recovered_code/open_ended_code/open_ended_code_codex_deepseek_v4_pro_r3/item_29.command.txt), especially lines 67-105; [submitted DE table](IWC/analysis/wf_010_pseudobulk_scrna_de/source_snapshots/huggingface_traces/files/open_ended_code_codex_deepseek_v4_pro_r3/agent_workspace/final_answer/differential_expression.tsv).

## 17. IWC: `wf_007_vgp_mitogenome_assembly`

**Finding: plausible-looking, structurally valid assemblies can have no sequence agreement with the target mitochondrial reference.**

Three runs receive zero: GPT-5.5 r1 in both environments and DeepSeek open-code r2. All have valid final FASTA artifacts. Their evaluator records contain zero matched canonical 31-mers against reference record `OZ203683.1`, with no ambiguous candidate windows.

| Run | Submitted length supported by trace | Candidate 31-mer windows | Matched windows |
|---|---:|---:|---:|
| GPT-5.5 Galaxy r1 | 14,449 bp | 14,419 | 0 |
| GPT-5.5 open-code r1 | 16,279 bp | 16,249 | 0 |
| DeepSeek open-code r2 | 15,349 bp | 15,319 | 0 |

GPT-5.5 Galaxy r1 actually runs Hifiasm and selects `ptg000099c` because it is circular, 14,449 bases long, and has reported depth 206 compared with much lower-depth nuclear contigs. The trace then encounters extraction-wrapper problems and locally extracts that record from the Galaxy-produced assembly. Its final checks confirm gzip integrity, one record, nonzero length, and permitted bases. Those checks never establish mitochondrial identity. DeepSeek open-code r2 similarly reports strong read mapping back to its own candidate, which establishes read support but not identity with the intended organelle.

**Interpretation:** the zero represents sequence-content disagreement, not a trivial FASTA header, reverse-strand, or circular-origin formatting difference. Canonical k-mers already account for reverse complement; the evaluator description also explains why an origin shift would cause only a small loss rather than zero. The evidence does not identify what biological sequence each wrong candidate represents, so a species or contamination diagnosis would be speculative.

**Treatment:** classify these as assembly/candidate-identification failures requiring sequence-level investigation. Add evidence of mitochondrial identity to length, circularity, coverage, and format checks. Preserve the Galaxy r1 local extraction as provenance, while recognizing that its central assembly did run in Galaxy.

Evidence: [Galaxy GPT-5.5 r1 evaluator](IWC/analysis/wf_007_vgp_mitogenome_assembly/source_snapshots/huggingface_traces/files/galaxy_gpt_5_5_r1/evaluation.json); [open-code GPT-5.5 r1 evaluator](IWC/analysis/wf_007_vgp_mitogenome_assembly/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/evaluation.json); [DeepSeek r2 evaluator](IWC/analysis/wf_007_vgp_mitogenome_assembly/source_snapshots/huggingface_traces/files/open_ended_code_codex_deepseek_v4_pro_r2/evaluation.json); [Galaxy GPT-5.5 r1 trace](IWC/analysis/wf_007_vgp_mitogenome_assembly/source_snapshots/huggingface_traces/files/galaxy_gpt_5_5_r1/agent_workspace/run_trace/codex_events.jsonl), lines 47-82 and 111-132; [DeepSeek r2 trace](IWC/analysis/wf_007_vgp_mitogenome_assembly/source_snapshots/huggingface_traces/files/open_ended_code_codex_deepseek_v4_pro_r2/agent_workspace/run_trace/codex_events.jsonl.gz), line 193.

## 18. IWC: `wf_003_host_contamination_removal`

**Finding: conflicting score sources and incomplete route handling prevent a clean biological interpretation of the low Galaxy scores.**

Luna Galaxy r1 declares BWA-MEM; r3 declares BWA-MEM2. Their `run_record.acc` values are `0.9999` and `1.0`, respectively, but their saved evaluator values are `0.27301161791714046` and `0.2729898249168107`. Neither evaluator includes the route provenance seen in route-calibrated examples elsewhere in IWC.

The component counts show the practical difference. Of 78,090 input pairs, the evaluator reference retains 72,867. Luna r1 retains 20,899 and r3 retains 20,896. Their retained reads are almost entirely within the reference set, but the candidate removes about 57,190 pairs instead of the reference's 5,223. This is a major retained-read-set discrepancy, not a rounding or filename issue.

At the same time, all three GPT-5.5 open-code replicates receive `reference_accuracy=null`, explicitly because their declared BWA/minimap2 routes lack a registered reference. The evaluator's own unsupported-route policy says these runs must not be assigned zero or compared against another route's reference. Their run records nevertheless contain numeric accuracies.

**Interpretation:** the candidate read sets differ substantially, but the archive leaves unresolved whether the relevant low scores used an appropriate route/reference pairing. One cannot choose whichever score source supports a preferred environment comparison. The explicit unsupported-route nulls are missing adjudications, not failures to produce output.

**Treatment:** reconcile the frozen route registry, method declarations, reference provenance, and evaluator lineage for these five records. Keep both recorded score fields visible, and retain unsupported routes as null until a valid reference is available. Do not call the Luna runs biologically inferior solely from the unresolved 0.273 field.

Evidence: [Luna r1 evaluator](IWC/analysis/wf_003_host_contamination_removal/source_snapshots/huggingface_traces/files/galaxy_gpt_5_6_luna_r1/evaluation.json) and [run record](IWC/analysis/wf_003_host_contamination_removal/source_snapshots/huggingface_traces/files/galaxy_gpt_5_6_luna_r1/run_record.json); [Luna r3 evaluator](IWC/analysis/wf_003_host_contamination_removal/source_snapshots/huggingface_traces/files/galaxy_gpt_5_6_luna_r3/evaluation.json) and [run record](IWC/analysis/wf_003_host_contamination_removal/source_snapshots/huggingface_traces/files/galaxy_gpt_5_6_luna_r3/run_record.json); [GPT-5.5 code r1 unsupported route](IWC/analysis/wf_003_host_contamination_removal/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/evaluation.json); [r2 unsupported route](IWC/analysis/wf_003_host_contamination_removal/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r2/evaluation.json); [r3 unsupported route](IWC/analysis/wf_003_host_contamination_removal/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r3/evaluation.json).

## 19. IWC: `wf_006_atacseq_chromatin_accessibility`

**Finding: a low score can reflect which allowed peak-calling protocol is used as reference; the saved route-aware evaluator explains a concrete 0.393-to-1.0 disagreement.**

Twelve of 24 run records disagree materially with their saved evaluator files. GPT-5.5 Galaxy r2 is especially informative: its run record reports `acc=0.392943724343`, whereas its evaluator reports `reference_accuracy=1.0`, with all 33,488 candidate peaks matched.

The evaluator retains the individual comparisons that explain this difference:

| Reference variant for the same submitted peaks | Agreement |
|---|---:|
| `iwc-summit-split` | 0.3929437243430197 |
| `bampe-model` | 0.6602460320754978 |
| `bampe-nomodel` | 1.0 |

The run-record score equals the summit-split comparison to recorded precision. The evaluator's provenance states that the query fixes filtering, q-value, and control use but does not uniquely prescribe summit splitting, single-end fragment shifting, or BAMPE model selection. It therefore chooses the best match among three separately calibrated Bowtie2+MACS2 protocols. A separate GPT-5.5 open-code r1 run receives 1.0 for 39,448 peaks against a declared BWA-MEM+MACS3 route, illustrating that even perfect scores can refer to different reference peak sets.

**Interpretation:** the 0.393 value is real disagreement with one protocol's peaks, but it should not automatically mean failure of an otherwise allowed workflow. Conversely, a route-aware score of 1.0 measures agreement with that route's calibration, not universal identity across peak callers. The matching component values establish the reference-policy mechanism; the archive does not by itself establish which score field was intended as the final publication-frozen result.

**Treatment:** retain route, reference variant, component comparisons, and score lineage alongside the headline score. Reconcile the 12 conflicting records under a frozen acceptance policy before estimating platform effects.

Evidence: [GPT-5.5 Galaxy r2 evaluator and reference variants](IWC/analysis/wf_006_atacseq_chromatin_accessibility/source_snapshots/huggingface_traces/files/galaxy_gpt_5_5_r2/evaluation.json); [its run record](IWC/analysis/wf_006_atacseq_chromatin_accessibility/source_snapshots/huggingface_traces/files/galaxy_gpt_5_5_r2/run_record.json); [BWA-MEM+MACS3 evaluator](IWC/analysis/wf_006_atacseq_chromatin_accessibility/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/evaluation.json); [inventory of all 12 conflicts](IWC/iwc_scientific_audit.json), `runs` entries for this task with `score_conflict_gt_1e_9=true`.

## 20. IWC: `wf_002_rnaseq_de_visualization`

**Finding: a near-perfect continuous score conceals a different thresholded DE-gene set.**

GPT-5.5 open-code r1 scores `0.9999659529061574`, readily rounded to 1.000 in a summary. Yet its evaluator reports 12 significant genes in the candidate versus 13 in the reference, with significant-set Jaccard `0.9230769230769231` (12/13).

The detailed components explain how both statements can be true. All 2,526 genes are present, the scored fold-change direction agreement is 1.0, magnitude concordance is `0.9999962211422271`, ranking is `0.9999729493803726`, and evidence agreement is `0.9998606012000403`. Their geometric mean stays extremely close to one. A thresholded significant-set diagnostic is reported separately, so it need not equal the continuous headline score. BH consistency passes with maximum deviation approximately `8.75e-13`.

**Interpretation:** this is a small quantitative disagreement with a visible consequence for the reported significant-gene list, rather than the BH implementation failure in case 16. The evaluator alone does not identify the missing gene or establish whether its changed decision has biological importance. It does establish that "score approximately one" does not mean identical inferential conclusions.

**Treatment:** report significant-set counts and overlap with the continuous score for this task. Do not describe this run as producing an identical DE result, and do not infer a large biological failure from a single changed thresholded call without inspecting that gene's statistics.

Evidence: [original evaluator with all components](IWC/analysis/wf_002_rnaseq_de_visualization/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/evaluation.json); [submitted DE table](IWC/analysis/wf_002_rnaseq_de_visualization/source_snapshots/huggingface_traces/files/open_ended_code_gpt_5_5_r1/agent_workspace/final_answer/differential_expression.tsv).
