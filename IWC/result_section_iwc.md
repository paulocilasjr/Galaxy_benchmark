# IWC Results Evidence Draft

We archived 240 workbook-listed IWC runs across 10 tasks, four model labels, two execution conditions, and three replicate labels. This document is an evidence inventory for later scientific analysis; it is not a re-evaluation of the benchmark.

| Task | Runs | Numeric scores | Distinct analytical jobs | Failed jobs | Selected Galaxy outputs |
|---|---:|---:|---:|---:|---:|
| wf_001_short_read_qc_trim | 24 | 0 | 53 | 22 | 232 |
| wf_002_rnaseq_de_visualization | 24 | 0 | 134 | 14 | 290 |
| wf_003_host_contamination_removal | 24 | 0 | 83 | 21 | 201 |
| wf_005_amplicon_dada2_pe_denoising | 24 | 0 | 276 | 25 | 1188 |
| wf_006_atacseq_chromatin_accessibility | 24 | 0 | 200 | 27 | 421 |
| wf_007_vgp_mitogenome_assembly | 24 | 0 | 75 | 18 | 264 |
| wf_008_amr_gene_detection | 24 | 0 | 39 | 0 | 252 |
| wf_009_clinicalmp_peptide_verification | 24 | 0 | 203 | 25 | 547 |
| wf_010_pseudobulk_scrna_de | 24 | 0 | 204 | 50 | 646 |
| wf_011_bioproject_metadata_sequence_retrieval | 24 | 0 | 85 | 0 | 545 |

The original evaluator fields and submitted answers remain in each task's `history_analysis_evidence.json`. Scores are not converted into a common metric here. Galaxy execution jobs, shell/API calls, and scientific attempts remain separate quantities. Detailed route, token, artifact, and recovery evidence is retained under each task directory.

## Limitations

The source workbook is an observed-link inventory and does not independently establish protocol coverage, matched seeds, or stopping rules. Two histories exceeded the configured detailed-content cap and are marked metadata-only. TLS certificate verification was disabled because the local CA certificate was rejected by Python; this limitation is recorded in the source manifests. Binary or oversized outputs are listed rather than silently substituted.
