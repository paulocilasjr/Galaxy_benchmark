Galaxy history: `bbd44e69cb8906b506613f878a4c8b76` (`run-9289486a3dc84321929e1b926990af72`)

- Combined the four assigned raw-count datasets in Galaxy by row and retained genes satisfying `(count >= 10)` in at least two samples.
- Retained/tested gene count: 2,526.
- Ran DESeq2 1.40.2 through Galaxy DESeq2 wrapper 2.11.40.8+galaxy4 with changed as factor level 1 and reference as factor level 2.
- Disabled wrapper prefiltering, independent filtering, outlier filtering/replacement, beta priors, and LFC shrinkage.
- Extracted Galaxy result columns 1, 3, 6, and 7 for gene ID, unshrunken log2 fold change, raw p-value, and BH-adjusted p-value.
