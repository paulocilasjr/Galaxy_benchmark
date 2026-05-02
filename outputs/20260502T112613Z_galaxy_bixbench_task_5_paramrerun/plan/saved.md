# Initial plan: parameterized BixBench task 5

Objective: In which patient volume group (number of patients seen) do healthcare workers show statistically significant differences (p<0.05) in COVID-19 severity between BCG vaccination and placebo groups based on chi-square analysis?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: BCG parameter selection: use all adverse-event records with AESEV present; ordinal logit covariates TRTGRP_cat, expect_interact_cat, patients_seen_cat; chi-square strata as prompted.
