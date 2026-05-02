# Initial plan: parameterized BixBench task 13

Objective: What is the Mann-Whitney U statistic when comparing treeness values between animals and fungi?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: Treeness parameter selection: parse IQ-TREE total/internal branch length from .iqtree files; treeness = internal/total; use animals/fungi subsets as prompted.
