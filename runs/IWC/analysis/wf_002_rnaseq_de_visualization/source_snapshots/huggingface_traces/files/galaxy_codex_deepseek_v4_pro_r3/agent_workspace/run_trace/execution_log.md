# Differential expression execution log

- Assigned Galaxy history: bbd44e69cb8906b580c956d08721b679
- Inputs: two changed-condition count tables (SRR5085169, SRR5085170) and two reference-condition count tables (SRR5085167, SRR5085168)
- Pre-filter: kept genes with raw count >= 10 in at least 2 of the 4 samples; 2,526 genes retained
- Galaxy tool: DESeq2 2.11.40.8+galaxy4
- DESeq2 settings: count input, factor `condition`, changed level first vs reference level second; no LFC shrinkage; independent filtering off; pre-filter disabled inside DESeq2 because filtering was applied before submission
- Output: unshrunken DESeq2 log2 fold change (positive means higher in changed condition), raw Wald p-value, and BH adjusted p-value recomputed across the 2,526 retained genes
- Final files written to final_answer/differential_expression.tsv and final_answer/method.json
