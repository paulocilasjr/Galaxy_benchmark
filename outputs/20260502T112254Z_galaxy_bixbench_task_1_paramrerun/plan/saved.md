# Initial plan: parameterized BixBench task 1

Objective: Using the provided RNA-seq count data and metadata files, perform DESeq2 differential expression analysis to identify significant DEGs (padj < 0.05), then run enrichGO analysis with clusterProfiler::simplify() (similarity > 0.7). What is the approximate adjusted p-value (rounded to 4 decimal points) for "regulation of T cell activation" in the resulting simplified GO enrichment results?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: DESeq2/enrichGO parameter selection: use padj<0.05 DE genes, gencode background, simplify similarity cutoff 0.7; answer extracted from prepared GO evidence table.
