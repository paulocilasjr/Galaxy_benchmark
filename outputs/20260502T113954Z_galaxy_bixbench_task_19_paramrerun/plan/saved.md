# Initial plan: parameterized BixBench task 19

Objective: What is the maximum number of parsimony informative sites in any animal gene alignment?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: Parsimony parameter selection: use MAFFT alignment files only; exclude gaps/ambiguous residues from informative-site calls; compute percentages over alignment length.
