# BixBench task 30

Objective: What is the skewness characteristic of the gene expression (log2(TPM+1)) distribution across all cell lines in the dataset?

Galaxy plan: upload prepared tabular representation of the public task data and execute the scalar analysis using Galaxy Text reformatting with awk.

Parameter selection: Galaxy awk computes Fisher-Pearson skewness over all uploaded expression matrix values.

Ground truth access deferred until result.json is written.
