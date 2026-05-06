# BixBench task 32

Objective: Using a Spearman Rank correlation test and Benjamini-Hochberg multi-test correction, what percentage of genes show a statistically significant correlation between expression and essentiality, in either direction?

Galaxy plan: upload prepared tabular representation of the public task data and execute the scalar analysis using Galaxy Text reformatting with awk.

Parameter selection: Galaxy awk selects/counts from a per-gene Spearman table; raw matrix alignment was prepared locally because no stock Spearman tool is available.

Ground truth access deferred until result.json is written.
