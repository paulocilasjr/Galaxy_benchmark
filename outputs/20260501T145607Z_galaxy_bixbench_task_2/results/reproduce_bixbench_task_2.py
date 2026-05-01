# Reproduction notes for BixBench task 2
# This run used usegalaxy.org API history bbd44e69cb8906b54f9e30b8f8913e66.
# Steps: upload task files; attempt Galaxy RStudio (failed because interactive tools disabled); prepare per-sample count TSVs from the provided count matrix; upload them; run Galaxy DESeq2 with Control and ASXL1 count sets; filter Galaxy DESeq2 output to genes with raw p < 0.05; upload significant-gene and gencode-background lists; run Galaxy gProfiler GOSt GO:BP with custom background and FDR correction; submit GO:0042119 neutrophil activation p-value from the Galaxy output.
