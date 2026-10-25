# BixBench-50 Metadata Recovery Summary

The supplied workbook's 1,500 run rows were matched to their archived task, model, condition, replicate and source trace URL. Workbook contents were treated as data. No workbook instructions were executed, and the workbook was not modified.

## General Findings

- The 32 collection-limited histories contain **41,304 total elements** in their archived metadata. Detailed contents remain intentionally unretrieved.
- State summaries report **40,722 ok**, **202 new**, **9 failed_metadata**, and **0 error** dataset states. **371 elements** are not accounted for by those summaries; their status is unknown here.
- Dataset states are not job counts or final-answer accuracy. A zero error-state count does not establish that no jobs failed, particularly when deleted objects or collection objects are outside the summary.
- The existing detailed snapshots expose 5,042 distinct creating jobs: 4,454 ok, 552 error, 25 deleted and 11 paused. These are partial, previously collected job records; they must not be added to dataset-state totals.
- Six absent submitted answers are confirmed as **missing_answer in the original evaluator**, with blank answer text and no answer path in the original result. This is not merely a missing local answer-file extraction; the underlying reason the agent did not submit remains unclassified.
- All 25,974 files listed in the trace manifests are marked retained. This describes the inventoried files, not an independently verified complete remote repository.
- Four histories previously returned HTTP 403. Public metadata-only retries in this recovery pass failed certificate validation; counts remain unavailable. Certificate verification was not disabled.
- The 26 binary/unsupported outputs remain unretrieved. No scientific analysis was rerun and no original answer score was changed.

## Collection-Limited Histories

Counts below are archived history metadata, not fresh remote counts. Tools are recovered from structured execution requests in already-retained traces, excluding searches and inspections. They identify requested tools, not adjudicated successful jobs. Custom tools have a custom: prefix. Full IDs and event references are in the companion JSON.

| Task | Configuration / replicate | Elements | ok | error | failed_metadata | new | Unaccounted | Answer score | Requested tools |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| bix-11-q1 | Codex GPT-5.6 Luna r2 | 8801 | 8796 | 0 | 0 | 0 | 5 | 1 | __FILTER_FROM_FILE__, custom:codex_scog_treeness_median_v1, unzip |
| bix-11-q2 | Codex GPT-5.6 Luna r2 | 2540 | 2538 | 0 | 0 | 0 | 2 | 1 | phykit_metrics, unzip |
| bix-11-q2 | Codex GPT-5.6 Luna r3 | 2539 | 2538 | 0 | 0 | 0 | 1 | 1 | cat1, custom:fungal-treeness-threshold-20260803-v1, tp_find_and_replace, tp_grep_tool, regex1, unzip, collapse_dataset |
| bix-12-q2 | Codex GPT-5.6 Sol r3 | 1047 | 1043 | 0 | 0 | 0 | 4 | 1 | __FILTER_FROM_FILE__, unzip, datamash_ops, collapse_dataset, phykit_alignment_based |
| bix-12-q2 | Codex GPT-5.6 Luna r1 | 1048 | 1043 | 0 | 0 | 0 | 5 | 1 | Summary_Statistics1, __FILTER_FROM_FILE__, unzip, collection_element_identifiers, datamash_ops, collapse_dataset, phykit_alignment_based |
| bix-12-q2 | Codex GPT-5.6 Luna r2 | 1051 | 1045 | 0 | 0 | 0 | 6 | 1 | custom:codex_phykit_cli_diagnostic_v1, custom:codex_phykit_parsimony_informative_sites_batch_v1, custom:codex_phykit_parsimony_informative_sites_batch_v2, custom:codex_phykit_parsimony_informative_sites_batch_v3, custom:codex_phykit_parsimony_informative_sites_batch_v5, unzip, collection_element_identifiers, phykit_alignment_based |
| bix-12-q2 | Codex GPT-5.6 Luna r3 | 533 | 532 | 0 | 0 | 0 | 1 | 1 | custom:fungal-parsimony-informative-sites, unzip, collection_element_identifiers, phykit_alignment_based |
| bix-12-q2 | DeepSeek V4 Pro via Codex r1 | 536 | 530 | 0 | 0 | 0 | 6 | 1 | unzip |
| bix-12-q2 | DeepSeek V4 Pro via Codex r2 | 541 | 532 | 0 | 0 | 0 | 9 | 1 | unzip, datamash_ops, collapse_dataset, phykit_alignment_based |
| bix-12-q2 | DeepSeek V4 Pro via Codex r3 | 1047 | 1043 | 0 | 0 | 0 | 4 | 1 | unzip, collection_element_identifiers, datamash_ops, collapse_dataset, phykit_alignment_based |
| bix-12-q4 | Codex GPT-5.6 Sol r2 | 1022 | 1016 | 0 | 0 | 0 | 6 | 1 | nonparametric_rank_tests, unzip, collapse_dataset, phykit_alignment_based |
| bix-12-q4 | Codex GPT-5.6 Luna r1 | 1519 | 1511 | 0 | 0 | 0 | 8 | 1 | custom:parsimony-mw-per-file-v1, custom:parsimony-mw-per-file-v2, unzip, phykit_alignment_based |
| bix-12-q4 | Codex GPT-5.6 Luna r2 | 507 | 504 | 0 | 0 | 0 | 3 | 1 | custom:pis-group-percentages-20260802, nonparametric_rank_tests, unzip, phykit_alignment_based |
| bix-12-q4 | Codex GPT-5.6 Luna r3 | 514 | 509 | 0 | 0 | 0 | 5 | 1 | custom:codex_parsimony_informative_sites_by_alignment_v1, custom:codex_parsimony_informative_sites_by_alignment_v2, custom:codex_parsimony_informative_sites_by_alignment_v3, custom:codex_parsimony_informative_sites_by_alignment_v4, custom:codex_phykit_cli_diagnostic_v1, custom:codex_phykit_cli_diagnostic_v2, custom:codex_phykit_cli_diagnostic_v3, nonparametric_rank_tests, unzip, phykit_alignment_based |
| bix-12-q5 | Codex GPT-5.6 Sol r2 | 991 | 988 | 0 | 0 | 0 | 3 | 1 | unzip, collection_element_identifiers, phykit_alignment_based |
| bix-12-q5 | Codex GPT-5.6 Luna r1 | 753 | 746 | 0 | 0 | 0 | 7 | 1 | custom:animal-parsimony-informative-sites-v1, custom:animal-parsimony-informative-sites-v2, custom:animal-parsimony-informative-sites-v3, custom:animal-parsimony-informative-sites-v4, custom:animal-parsimony-informative-sites-v5, custom:animal-pis-udt-preflight-v1, unzip, phykit_alignment_based |
| bix-12-q5 | Codex GPT-5.6 Luna r2 | 514 | 507 | 0 | 0 | 0 | 7 | 1 | custom:animal-alignment-pis-cmdhelp-v1, custom:animal-alignment-pis-debug-v1, custom:animal-alignment-pis-help-v1, custom:animal-alignment-pis-max-v1, custom:animal-alignment-pis-max-v2, custom:animal-alignment-pis-max-v3, unzip, collection_element_identifiers |
| bix-12-q5 | Codex GPT-5.6 Luna r3 | 752 | 748 | 0 | 0 | 0 | 4 | 1 | __FILTER_FROM_FILE__, custom:animal-parsimony-informative-sites-v1, unzip, phykit_alignment_based |
| bix-12-q5 | DeepSeek V4 Pro via Codex r2 | 504 | 503 | 0 | 0 | 0 | 1 | 1 | custom:max_parsimony_informative_animals_v1, unzip, datamash_ops, phykit_alignment_based |
| bix-12-q5 | DeepSeek V4 Pro via Claude Code (superseded) r1 | 504 | 503 | 0 | 0 | 0 | 1 | 1 | custom:parsimony-informative-sites-v1, unzip |
| bix-12-q6 | Codex GPT-5.6 Sol r1 | 1020 | 1015 | 0 | 0 | 0 | 5 | 1 | custom:phykit-pis-help-v1, custom:phykit-pis-help-v2, custom:raw-pi-counts-phykit-animals-fungi-v1, custom:raw-pi-counts-phykit-animals-fungi-v2, nonparametric_rank_tests, unzip, collection_element_identifiers |
| bix-12-q6 | Codex GPT-5.6 Sol r3 | 1023 | 1017 | 0 | 0 | 0 | 6 | 1 | nonparametric_rank_tests, unzip, collapse_dataset, phykit_alignment_based |
| bix-12-q6 | Codex GPT-5.6 Luna r1 | 1013 | 1007 | 0 | 0 | 0 | 6 | 1 | custom:codex-raw-parsimony-informative-sites-by-group, nonparametric_rank_tests, unzip, collection_element_identifiers, phykit_alignment_based |
| bix-12-q6 | Codex GPT-5.6 Luna r2 | 509 | 506 | 0 | 0 | 0 | 3 | 1 | custom:raw-pis-by-group-v1, nonparametric_rank_tests, unzip, phykit_alignment_based |
| bix-12-q6 | Codex GPT-5.6 Luna r3 | 1025 | 1019 | 0 | 0 | 0 | 6 | 1 | custom:phykit-pis-batch-20260803, custom:phykit-pis-batch-20260803-v2, custom:phykit-pis-batch-20260803-v3, custom:phykit-pis-help-20260803, custom:phykit-pis-probe-20260803, custom:phykit-pis-probe-20260803-v2, custom:phykit-pis-probe-20260803-v3, nonparametric_rank_tests, unzip, phykit_alignment_based |
| bix-12-q6 | DeepSeek V4 Pro via Codex r1 | 1750 | 1521 | 0 | 0 | 202 | 27 | 1 | __FILTER_FROM_FILE__, custom:mannwhitney-pis-v1, custom:mannwhitney-pis-v2, custom:mannwhitney-pis-v3, custom:mannwhitney-pis-v4, custom:mannwhitney-pis-v5, custom:mannwhitney-pis-v6, custom:phykit-preflight-v1, custom:pis-animals-fungi-v1, unzip, collection_element_identifiers, phykit_alignment_based |
| bix-14-q1 | DeepSeek V4 Pro via Claude Code (superseded) r1 | 779 | 604 | 0 | 0 | 0 | 175 | 1 | cat_multi_datasets, xlsx2tsv |
| bix-17-q2 | DeepSeek V4 Pro via Codex r1 | 345 | 300 | 0 | 0 | 0 | 45 | 1 | Not identified in structured calls |
| bix-31-q2 | DeepSeek V4 Pro via Codex r2 | 774 | 763 | 0 | 9 | 0 | 2 | 0 | Not identified in structured calls |
| bix-34-q2 | Codex GPT-5.6 Luna r3 | 2536 | 2535 | 0 | 0 | 0 | 1 | 1 | unzip, phykit_tree_based |
| bix-34-q5 | Codex GPT-5.6 Sol r1 | 724 | 718 | 0 | 0 | 0 | 6 | 1 | unzip, phykit_tree_based |
| bix-35-q2 | DeepSeek V4 Pro via Claude Code (superseded) r1 | 2543 | 2542 | 0 | 0 | 0 | 1 | 1 | phykit_metrics, unzip |

## Unavailable Histories

| Task | Configuration / replicate | Archived result | Current retry | Requested tools from saved trace |
|---|---|---|---|---|
| bix-32-q2 | DeepSeek V4 Pro via Codex r1 | HTTP 403 | TLS validation failed | Cut1, Filter1, kegg_ora, rds_to_tabular |
| bix-32-q2 | DeepSeek V4 Pro via Codex r2 | HTTP 403 | TLS validation failed | Filter1, kegg_ora, rds_to_tabular |
| bix-32-q2 | DeepSeek V4 Pro via Codex r3 | HTTP 403 | TLS validation failed | Filter1, kegg_ora, rds_to_tabular |
| bix-55-q1 | DeepSeek V4 Pro via Codex r3 | HTTP 403 | TLS validation failed | Cut1, comp1, busco, busco, filter_tabular |

## Original Missing Answers

| Task | Condition | Configuration / replicate | Original evaluator |
|---|---|---|---|
| bix-26-q5 | galaxy | DeepSeek V4 Pro via Codex r1 | missing_answer; score 0 |
| bix-27-q5 | galaxy | DeepSeek V4 Pro via Codex r1 | missing_answer; score 0 |
| bix-34-q5 | galaxy | DeepSeek V4 Pro via Claude Code (superseded) r3 | missing_answer; score 0 |
| bix-43-q2 | galaxy | DeepSeek V4 Pro via Codex r3 | missing_answer; score 0 |
| bix-46-q4 | galaxy | DeepSeek V4 Pro via Codex r2 | missing_answer; score 0 |
| bix-52-q7 | open_ended_code | DeepSeek V4 Pro via Claude Code (superseded) r3 | missing_answer; score 0 |

## All-Task Overview

Job counts refer only to already-retrieved creating-job snapshots, with incomplete coverage for capped or inaccessible histories. Accepted answers are out of 15 per condition. The top five job tool IDs are shortened for readability; the JSON retains the complete inventory.

| Task | Galaxy accepted | Code accepted | Observed jobs | ok jobs | error jobs | Other job states | Most frequent observed job tools |
|---|---:|---:|---:|---:|---:|---:|---|
| bix-11-q1 | 15 | 15 | 39 | 38 | 1 | 0 | phykit_metrics (30), datamash_ops (3), Summary_Statistics1 (2), batch-treeness-v1 (2), codex_treeness_diff_v1 (1) |
| bix-11-q2 | 15 | 15 | 29 | 27 | 2 | 0 | phykit_metrics (17), table_compute (6), Cut1 (3), fungal-treeness-threshold-v3 (1), fungal-treeness-threshold-v2 (1) |
| bix-12-q2 | 15 | 13 | 11 | 8 | 3 | 0 | fungal-pis-median-v1 (1), fungal_pis_median_20260716_v1 (1), fungal_pi_median_phykit_20260716 (1), fungal-pis-median-20260801-v2 (1), fungal-pis-median-20260801-v1 (1) |
| bix-12-q4 | 13 | 11 | 32 | 27 | 4 | 1 | nonparametric_rank_tests (11), codex_phykit_pis_batch_v1 (2), phykit_alignment_based (2), parsimony-informative-batch-v2 (2), Cut1 (2) |
| bix-12-q5 | 15 | 13 | 18 | 10 | 8 | 0 | animal-pis-max-20260716-v3 (1), animal-pis-max-20260716-v2 (1), animal-pis-max-20260716 (1), animal_pis_max_20260716_v1 (1), animal_pis_max_20260716_v2 (1) |
| bix-12-q6 | 15 | 12 | 33 | 26 | 7 | 0 | nonparametric_rank_tests (10), addValue (2), cat1 (2), pis-counter-v1 (2), upload1 (2) |
| bix-14-q1 | 12 | 12 | 452 | 443 | 7 | 2 | xlsx2tsv (200), table_compute (51), Remove beginning1 (42), Filter1 (31), Grouping1 (24) |
| bix-16-q1 | 10 | 10 | 20 | 19 | 1 | 0 | featurewise_correlation (15), datamash_transpose (2), expression_essentiality_spearman_v3 (1), expression_essentiality_spearman_v2 (1), expression_essentiality_spearman_v1 (1) |
| bix-16-q3 | 14 | 15 | 24 | 24 | 0 | 0 | featurewise_correlation (17), csv_to_tabular (2), Show beginning1 (2), depmap_expr_essentiality_spearman_count_v1 (1), tp_grep_tool (1) |
| bix-16-q4 | 15 | 13 | 22 | 15 | 7 | 0 | featurewise_correlation (16), spearman-bh-gene-correlation (6) |
| bix-17-q2 | 15 | 15 | 248 | 227 | 21 | 0 | xlsx2tsv (86), Filter1 (48), addValue (15), Remove beginning1 (13), join1 (8) |
| bix-18-q1 | 15 | 15 | 55 | 47 | 8 | 0 | csv_to_tabular (17), Grouping1 (14), datamash_ops (13), Remove beginning1 (4), tp_tail_tool (1) |
| bix-18-q3 | 15 | 15 | 68 | 61 | 7 | 0 | csv_to_tabular (15), Grouping1 (13), Summary_Statistics1 (10), datamash_ops (7), Grep1 (5) |
| bix-20-q3 | 15 | 15 | 475 | 467 | 7 | 1 | xlsx2tsv (256), Filter1 (103), Count1 (23), Cut1 (21), Remove beginning1 (20) |
| bix-22-q1 | 14 | 15 | 212 | 197 | 15 | 0 | table_compute (39), featurewise_correlation (38), Cut1 (26), filter_tabular (24), Remove beginning1 (17) |
| bix-22-q4 | 15 | 15 | 109 | 95 | 14 | 0 | Cut1 (24), table_compute (17), featurewise_correlation (10), csv_to_tabular (7), Add_a_column1 (5) |
| bix-24-q2 | 14 | 14 | 187 | 164 | 21 | 2 | Cut1 (44), gprofiler_gost (42), Filter1 (19), deseq2 (12), deseq2 (11) |
| bix-26-q3 | 15 | 15 | 76 | 57 | 19 | 0 | kegg_ora (32), rds_to_tabular (15), Filter1 (9), Cut1 (2), upload1 (2) |
| bix-26-q5 | 1 | 1 | 345 | 293 | 39 | 13 | kegg_ora (133), Filter1 (74), rds_to_tabular (38), Cut1 (38), upload1 (29) |
| bix-27-q5 | 13 | 11 | 74 | 59 | 15 | 0 | table_compute (17), datamash_transpose (8), csv_to_tabular (5), column_remove_by_header (4), Cut1 (4) |
| bix-28-q3 | 14 | 15 | 48 | 47 | 1 | 0 | phykit_metrics (42), phykit-lbs-996662at2759-v2 (1), phykit-lbs-help-996662at2759-v1 (1), phykit-help-996662at2759-v2 (1), phykit-lbs-996662at2759-v1 (1) |
| bix-30-q3 | 15 | 6 | 51 | 28 | 23 | 0 | Univariate (24), table_compute (3), mirna-de-bonferroni-by-v1 (2), mirna_ct_ttest_adjust_v1 (1), mirna-correction-ratio-v1 (1) |
| bix-31-q2 | 13 | 11 | 71 | 46 | 19 | 6 | diagexact-1786875452 (2), pydeseq2-sex-de-v2 (2), pydeseq2-sex-de-v3 (2), pydeseq2-sex-de-v1 (2), pydeseq2_sex_m_vs_f_batch_covariate_v1 (1) |
| bix-32-q2 | 11 | 11 | 186 | 149 | 33 | 4 | kegg_ora (104), rds_to_tabular (27), Filter1 (24), Cut1 (13), upload1 (4) |
| bix-34-q2 | 15 | 15 | 35 | 24 | 11 | 0 | phykit_tree_based (8), unzip (3), median-patristic-981902at2759-v1 (2), patristic-distance-v2 (2), fungal-gene-patristic-median-981902-v1 (1) |
| bix-34-q5 | 14 | 12 | 48 | 38 | 9 | 1 | unzip (3), datamash_ops (3), phykit_tree_based (2), Summary_Statistics1 (2), patristic_means_from_zip (2) |
| bix-35-q1 | 14 | 15 | 31 | 31 | 0 | 0 | phykit_metrics (30), phykit_tree_based (1) |
| bix-35-q2 | 14 | 13 | 45 | 42 | 3 | 0 | phykit_metrics (27), nonparametric_rank_tests (14), unzip (2), phykit-evo-rate-mwu-v1 (1), phykit_tree_based (1) |
| bix-37-q1 | 15 | 15 | 36 | 34 | 2 | 0 | xlsx2tsv (14), filter_tabular (6), Grep1 (4), Cut1 (3), Add_a_column1 (2) |
| bix-37-q4 | 15 | 15 | 30 | 29 | 1 | 0 | xlsx2tsv (14), filter_tabular (7), Add_a_column1 (5), Filter1 (2), Cut1 (1) |
| bix-38-q1 | 15 | 15 | 33 | 33 | 0 | 0 | phykit_metrics (31), datamash_ops (2) |
| bix-41-q5 | 15 | 15 | 122 | 115 | 7 | 0 | Summary_Statistics1 (26), filter_tabular (23), Filter1 (14), csv_to_tabular (10), datamash_ops (9) |
| bix-43-q2 | 11 | 2 | 142 | 103 | 38 | 1 | Cut1 (20), gseapy_enrichr (12), upload1 (7), Filter1 (5), tp_sort_header_tool (5) |
| bix-43-q4 | 13 | 13 | 183 | 167 | 16 | 0 | Cut1 (47), upload1 (40), gseapy_enrichr (20), deseq2 (13), join1 (7) |
| bix-45-q1 | 0 | 8 | 45 | 45 | 0 | 0 | phykit_metrics (25), nonparametric_rank_tests (16), upload1 (2), codex-phykit-rcv-table-v1 (1), phykit-rcv-scores-v1 (1) |
| bix-46-q4 | 14 | 15 | 49 | 48 | 1 | 0 | rds_to_tabular (31), filter_tabular (7), Grep1 (2), csv_to_tabular (2), deseq-results-inspect-pa14-35160-v1 (1) |
| bix-47-q3 | 15 | 15 | 124 | 109 | 10 | 5 | xlsx2tsv (27), Filter1 (16), tp_sort_header_tool (11), filter_tabular (10), Count1 (8) |
| bix-49-q4 | 15 | 13 | 203 | 172 | 31 | 0 | Cut1 (137), deseq2 (20), deseq2 (18), xlsx2tsv (9), asxl1-deseq2-apeglm-sex-v1 (2) |
| bix-51-q2 | 15 | 15 | 42 | 33 | 9 | 0 | xlsx2tsv (12), sklearn_generalized_linear (3), logistic-aic-v1 (2), logistic-bmi-pr-aic-v2 (1), logistic-bmi-pr-aic-v1 (1) |
| bix-51-q8 | 14 | 15 | 84 | 75 | 9 | 0 | sklearn_generalized_linear (15), xlsx2tsv (11), Cut1 (8), sklearn_estimator_attributes (7), filter_tabular (7) |
| bix-52-q2 | 14 | 15 | 151 | 143 | 8 | 0 | csv_to_tabular (23), Add_a_column1 (19), Filter1 (14), join1 (14), datamash_ops (14) |
| bix-52-q6 | 15 | 15 | 106 | 103 | 3 | 0 | csv_to_tabular (23), Grouping1 (14), Add_a_column1 (14), Remove beginning1 (12), join1 (12) |
| bix-52-q7 | 12 | 14 | 56 | 55 | 1 | 0 | wc_gnu (13), csv_to_tabular (12), Filter1 (9), table_compute (8), filter_tabular (6) |
| bix-53-q2 | 0 | 0 | 88 | 73 | 15 | 0 | Cut1 (35), deseq2 (29), deseq2 (16), csv_to_tabular (5), Convert characters1 (1) |
| bix-53-q5 | 15 | 14 | 187 | 161 | 26 | 0 | Cut1 (58), gseapy_enrichr (34), deseq2 (26), csv_to_tabular (20), annotatemyids (19) |
| bix-54-q7 | 1 | 1 | 35 | 18 | 17 | 0 | colony-area-model-fitting-v1 (3), colony-area-model-fitting-v2 (2), colony-area-model-fit-v1 (1), codex-colony-area-r-fit-v1 (1), codex_swarm_model_fit_v1 (1) |
| bix-55-q1 | 15 | 12 | 107 | 82 | 25 | 0 | busco (27), filter_tabular (18), tp_grep_tool (8), Cut1 (4), busco-eukaryota-odb10-prot-v4 (4) |
| bix-6-q4 | 15 | 15 | 114 | 86 | 28 | 0 | featurewise_correlation (31), Cut1 (29), xlsx2tsv (14), Remove beginning1 (6), add_line_to_file (4) |
| bix-61-q2 | 14 | 15 | 42 | 42 | 0 | 0 | bwa_mem (18), samtools_depth (14), samtools_coverage (4), Summary_Statistics1 (2), datamash_ops (2) |
| bix-61-q5 | 0 | 0 | 19 | 19 | 0 | 0 | bcftools_stats (13), bcftools_stats (5), bcftools_query (1) |

## Source and Interpretation

Source: bixbench_execution_condition_links.xlsx, BixBench links!A1:H1501; per-task history metadata and trace snapshots under analysis/. Workbook row numbers, source URLs, metadata snapshot dates, tool IDs and event references are retained in [the summary JSON](bixBench50_recovery_summary.json).

These summaries preserve the distinction between history-element states, creating-job states and original answer acceptance. History snapshots may include inherited or later objects. Counts that cannot be reconciled are reported as unknown rather than inferred failures or successes. The uniformly false fresh-history evaluator check remains a separate unresolved issue; this metadata summary does not change that check.
