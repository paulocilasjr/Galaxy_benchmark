# IWC evidence overview

This directory holds a retrospective archive of the supplied IWC execution-link workbook and an evidence-grounded comparison of two execution environments, Galaxy and open-ended code. It is not a new benchmark execution. The scientific revision of 23 September 2026 preserves source snapshots and original task reports, corrects aggregate extraction errors, and separates archive completeness from scientific performance.

## Start here

- [Results and manuscript draft](result_section_iwc.md): design variables, endpoint definitions, environment comparisons with influence and mechanism diagnostics, failure case studies, solution paths, token usage and publication limits.
- [Recovery and completeness](iwc_recovery_summary.md): retained evidence, unresolved gaps, integrity checks and the limits of operational-recovery counting.
- [Scientific audit JSON](iwc_scientific_audit.json): all 240 run records, source paths and hashes, both conflicting score fields, model metadata, token records, paired comparisons and finding IDs.
- [Recalculation script](audit_iwc_results.py): `python3 IWC/audit_iwc_results.py` rebuilds the supplement without replaying archived code or editing reports.
- [Sensitivity analysis](iwc_sensitivity_analysis.py) and [its results](iwc_sensitivity_results.json): endpoint distribution, leave-one-task-out influence and zero-run mechanism checks.
- [Regression checks](test_iwc_scientific_audit.py), [analysis instructions](../HISTORY_ANALYSIS_INSTRUCTIONS.md) and [source workbook](iwc_execution_condition_links.xlsx).

Legacy `iwc_overview_audit.json`, `iwc_recovery_summary.json`, per-task `history_analysis.md` and tool-fingerprint consistency outputs remain historical extraction products. Their missing score and usage fields are extraction limitations, not evidence that the original records lack those data. Do not regenerate revised reports with legacy `build_iwc_overview.py`; the scientific supplement is the numerical source of truth for this revision. Previous Markdown versions are preserved in Git.

## Observed design

The cohort crosses three controlled variables — task, model configuration and execution environment — with replicates as repeat executions rather than a designed factor.

| Variable | Observed evidence |
|---|---|
| Tasks | 10 supplied IWC workflow tasks; heterogeneous, no independent difficulty grading |
| Model configurations | GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, Codex + DeepSeek V4 Pro; 60 runs each |
| Execution environments | Galaxy and open-ended code; 120 runs each |
| Replicates | Labels 1–3; seeds undocumented, independence not established |
| Runs | 240 = 10 × 4 × 2 × 3; 80 analysis cells of three replicates |
| Runtime identity | Invocation records verify all model IDs; Luna at `max`, others at `high` reasoning |
| Run starts | 27 August to 3 September 2026 |
| Time budgets | Six or twelve hours, unevenly distributed across configurations and environments |
| Expected coverage | Unknown outside the workbook; no prospective inventory established |

Pairing is at task and model-configuration level, retaining three-replicate bundles. Prompts differ between environments by design, logging requirements differ, and budget ceilings are unbalanced. Comparisons are exploratory observational contrasts, not randomized causal estimates. Reported input-tree hashes agree within each task, which is a harness attestation rather than a byte-level input audit.

## Scientific status

Archived `iwc-final-answer-v2.2` evaluators contain **237 numeric scores and three unsupported-route nulls**. The endpoint is task-specific continuous output agreement on a 0–1 scale, **not** binary answer accuracy, and it must not be pooled with the answer-acceptance endpoints used for BixBench or CompBioBench. All 240 harness statuses are `complete`; six runs nevertheless score zero. Evaluator and run-record scores disagree materially in 17 records, which must be resolved before any final official score table is claimed.

**The endpoint is near-saturated and bimodal.** The median run scores 1.0000 and 65.4% of runs score at least 0.999, while 8 of 237 runs (3.4%) score below 0.5. Replicates are usually near-identical: the median within-cell replicate range is 0.0001 in Galaxy and 0.0000 in open-ended code. Variation is concentrated in a few catastrophic runs rather than spread as continuous noise, so a mean is a poor summary of this distribution.

The primary comparison excludes host removal from both environments because of missing and unresolved route scores, retaining 27 runs per environment per configuration:

| Model configuration | Galaxy | Open-ended code | Difference | Leave-one-task-out range | Excluding tasks with a zero-scored run |
|---|---:|---:|---:|---:|---:|
| GPT-5.5 | 0.949 | 0.868 | +0.082 | +0.013 to +0.092 | +0.012 |
| GPT-5.6 Sol | 0.989 | 0.988 | +0.001 | −0.002 to +0.004 (sign unstable) | +0.001 |
| GPT-5.6 Luna | 0.984 | 0.983 | +0.001 | −0.002 to +0.002 (sign unstable) | +0.001 |
| Codex + DeepSeek V4 Pro | 0.999 | 0.922 | +0.077 | +0.045 to +0.087 | +0.004 |

These are task-weighted summaries of normalized scores whose biological meanings differ by task. The two positive differences are carried by single tasks containing open-ended-code runs that scored zero; once those tasks are set aside the differences fall to +0.012 and +0.004. The two near-zero differences reverse sign when any single task is dropped and therefore carry no directional information. Retaining host removal where fully scored changes Luna's difference from +0.001 to −0.048, driven by five conflicted or null records. **No equivalence, general superiority or environment-purity claim is established, in either direction.**

## Task packages

Every task has 24 observed workbook runs. Score counts are numeric records, not successful tasks. Selected outputs are retained Galaxy output files, not dataset metadata entries.

| Task package | Numeric scores | Retained Galaxy output files |
|---|---:|---:|
| [001 short-read QC](analysis/wf_001_short_read_qc_trim/) | 24/24 | 14 |
| [002 RNA-seq DE](analysis/wf_002_rnaseq_de_visualization/) | 24/24 | 174 |
| [003 host removal](analysis/wf_003_host_contamination_removal/) | 21/24 | 5 |
| [005 amplicon denoising](analysis/wf_005_amplicon_dada2_pe_denoising/) | 24/24 | 83 |
| [006 chromatin accessibility](analysis/wf_006_atacseq_chromatin_accessibility/) | 24/24 | 112 |
| [007 mitogenome assembly](analysis/wf_007_vgp_mitogenome_assembly/) | 24/24 | 84 |
| [008 AMR detection](analysis/wf_008_amr_gene_detection/) | 24/24 | 219 |
| [009 peptide verification](analysis/wf_009_clinicalmp_peptide_verification/) | 24/24 | 255 |
| [010 pseudobulk DE](analysis/wf_010_pseudobulk_scrna_de/) | 24/24 | 197 |
| [011 BioProject retrieval](analysis/wf_011_bioproject_metadata_sequence_retrieval/) | 24/24 | 135 |
| Total | 237/240 | 1,278 |

Each package retains run and input manifests, task metadata, `history_analysis_evidence.json`, `history_analysis.md`, `source_snapshots/`, `recovered_code/`, `job_ledgers/` and `selected_outputs/` where collected. Original evaluators and submitted artifacts are under `source_snapshots/huggingface_traces/files/<run_id>/`; source manifests distinguish retained from remotely linked files. The supplement links to these packages rather than replacing them.

## Archive and audit status

The trace archive contains 5,645 retained files totalling 2,932,706,102 bytes, plus 123 linked large-file records without local bytes. Galaxy snapshots cover 118 detailed histories and two metadata-only histories. There are 1,278 selected Galaxy output files and 190 explicitly skipped output records, which is not an exhaustive inventory of unretained datasets. Only 286 of 360 evaluator-listed final-answer file references resolve to retained bytes.

Deduplicated Galaxy provenance contains 1,607 creating jobs: 277 acquisition jobs and 1,330 others, with 202 error and 16 deleted states. Forty-one heuristic failure-to-success links across 26 runs collapse to 27 distinct successful endpoints and do not establish 41 scientific recoveries. **No equivalent detector exists for the open-ended-code environment**, so these counts support no cross-environment recovery comparison. Current-history ownership and chronology remain partly unresolved.

Terminal usage is available for 240/240 runs. Typical within-task input usage is higher in Galaxy (median within-task ratios 1.66–2.77), yet total reported input is higher in open-ended code because of a long upper tail. No monetary cost or human-readability advantage was measured.

The supplement verified 9,096 retained trace, output and job-file entries against collection hashes with no mismatches, and indexed 1,667 hashed source files. This supports local integrity, not independent biological validity. All Galaxy manifests disclose disabled TLS verification during collection. Original evidence remains unchanged; no benchmark rerun, hidden-reference access, commit or push was performed for this revision.

The scientifically useful result is an inspectable separation of agreement, failure, provenance and resource use, with the specific evidence gaps named rather than an assumed environment benefit.
