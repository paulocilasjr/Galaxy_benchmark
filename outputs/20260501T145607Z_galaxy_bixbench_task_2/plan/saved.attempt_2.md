# Attempt 2 plan: Galaxy-native DESeq2 plus GO enrichment fallback

Change from attempt 1: usegalaxy.org RStudio is unavailable because Galaxy reports interactive tools are temporarily disabled. This retry uses installed Galaxy tools instead of the interactive Bioconductor environment.

Steps: upload per-sample count files and a sample sheet; create a Galaxy list collection; run Galaxy DESeq2 using condition as the factor with Control as reference and ASXL1 as target; use the DESeq2 result to identify p < 0.05 genes for downstream Galaxy enrichment. If exact enrichGO/simplify is unavailable as an installed Galaxy tool, preserve that limitation and use the nearest installed Galaxy GO enrichment tool for the submitted answer, without reading ground truth before submission.

Expected output: DESeq2 differential-expression table and enrichment output or documented Galaxy limitation.
