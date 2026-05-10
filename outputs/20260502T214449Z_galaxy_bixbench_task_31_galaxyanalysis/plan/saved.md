# BixBench task 31

Objective: How many genes in the provided data show strong positive Spearman correlation between expression and essentiality across cell lines, with a correlation coefficient >= 0.6?

Galaxy plan: upload prepared tabular representation of the public task data and execute the scalar analysis using Galaxy Text reformatting with awk.

Parameter selection: Galaxy awk selects/counts from a per-gene Spearman table; raw matrix alignment was prepared locally because no stock Spearman tool is available.

Ground truth access deferred until result.json is written.
