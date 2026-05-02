# Initial plan: parameterized BixBench task 23

Objective: Using DESeq2 to conduct differential expression analysis, how many genes have a dispersion estimate below 1e-05 prior to shrinkage? Account for Replicate, Strain, and Media effects in the model design.

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: RNA parameter selection: median-ratio normalization; Welch tests on log2 normalized counts; BH FDR<0.05; log2FC absolute cutoff only where prompted.
