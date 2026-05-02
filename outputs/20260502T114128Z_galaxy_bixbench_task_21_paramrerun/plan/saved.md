# Initial plan: parameterized BixBench task 21

Objective: What percentage of the genes significantly differentially expressed (logfold cutoff either > 1.5 or < -1.5 and FDR<0.05) in strain JBX97 are also significantly differentially expressed in strain JBX99, and not in any other strain (all relative to JBX1)?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: RNA parameter selection: median-ratio normalization; Welch tests on log2 normalized counts; BH FDR<0.05; log2FC absolute cutoff only where prompted.
