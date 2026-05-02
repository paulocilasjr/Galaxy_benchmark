# Initial plan: parameterized BixBench task 22

Objective: Using DESeq2 to conduct differential expression analysis relative to strain JBX1, how many genes are uniquely and statistically significantly differentially expressed in JBX98 but not in either JBX97 or JBX99? Use a Benjamini-Hochberg False Discovery Rate correction threshold of 0.05.

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: RNA parameter selection: median-ratio normalization; Welch tests on log2 normalized counts; BH FDR<0.05; log2FC absolute cutoff only where prompted.
