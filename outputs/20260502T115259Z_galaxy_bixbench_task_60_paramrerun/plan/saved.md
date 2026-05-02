# Initial plan: parameterized BixBench task 60

Objective: What is the maximum treeness/RCV value in genes with >70% alignment gaps?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: Task 60 parameter selection: use max per-sequence alignment gap percent >70, then maximize treeness/RCV from prepared metric table.
