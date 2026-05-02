# Initial plan: parameterized BixBench task 8

Objective: When performing a Chi-square test of independence to examine the association between BCG vaccination status (BCG vs Placebo) and COVID-19 disease severity among healthcare workers who see 1-50 patients, what is the p-value of the statistical test?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: BCG parameter selection: use all adverse-event records with AESEV present; ordinal logit covariates TRTGRP_cat, expect_interact_cat, patients_seen_cat; chi-square strata as prompted.
