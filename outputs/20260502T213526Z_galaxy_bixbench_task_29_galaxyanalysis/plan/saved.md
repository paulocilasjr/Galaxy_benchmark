# BixBench task 29

Objective: In the provided data, what gene symbol has the strongest negative Spearman correlation between its expression and essentiality?

Galaxy plan: upload prepared tabular representation of the public task data and execute the scalar analysis using Galaxy Text reformatting with awk.

Parameter selection: Galaxy awk selects/counts from a per-gene Spearman table; raw matrix alignment was prepared locally because no stock Spearman tool is available.

Ground truth access deferred until result.json is written.
