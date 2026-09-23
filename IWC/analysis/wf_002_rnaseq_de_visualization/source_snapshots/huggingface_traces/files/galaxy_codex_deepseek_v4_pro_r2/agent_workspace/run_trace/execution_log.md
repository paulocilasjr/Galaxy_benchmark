# Differential-expression execution log

- Assigned Galaxy history: `bbd44e69cb8906b5f2cf59d7503d7258`
- Inputs: four raw count tables (SRR5085169, SRR5085170 changed; SRR5085167, SRR5085168 reference)
- Pre-filtering in Galaxy:
  - Joined the four count tables on gene identifiers.
  - Kept the `Geneid` column and the four sample count columns.
  - Retained genes with counts >= 10 in at least 2 of 4 samples using Table Compute.
  - Split the filtered matrix back into per-sample count tables and restored the `Geneid` header.
- Differential expression in Galaxy:
  - Tool: DESeq2 `toolshed.g2.bx.psu.edu/repos/iuc/deseq2/deseq2/2.11.40.8+galaxy4`
  - Design: one factor `condition`, level `changed` vs level `reference`
  - DESeq2 pre-filtering: disabled
  - Independent filtering: disabled so BH-adjusted p-values are computed across all retained genes
  - Reported columns: gene id, unshrunken log2 fold change, Wald-test p-value, BH-adjusted p-value
- Output: 2,526 retained genes in `final_answer/differential_expression.tsv`.
