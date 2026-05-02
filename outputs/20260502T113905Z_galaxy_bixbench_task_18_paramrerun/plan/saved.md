# Initial plan: parameterized BixBench task 18

Objective: What is the Mann-Whitney U statistic when comparing parsimony informative site percentages between animals and fungi?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: Parsimony parameter selection: use MAFFT alignment files only; exclude gaps/ambiguous residues from informative-site calls; compute percentages over alignment length.
