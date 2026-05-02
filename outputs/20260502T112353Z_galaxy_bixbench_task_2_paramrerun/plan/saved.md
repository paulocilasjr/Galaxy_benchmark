# Initial plan: parameterized BixBench task 2

Objective: What is the adjusted p-val threshold for neutrophil activation GO Process from an enrichment analysis (using enrichGO as method) using all significant (p<0.05) differentially expressed genes between ASXL1 mutation and control over all genes as background (from gencode), and after removing GO terms with similarity > 0.7?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: DESeq2/enrichGO parameter selection: use padj<0.05 DE genes, gencode background, simplify similarity cutoff 0.7; answer extracted from prepared GO evidence table.
