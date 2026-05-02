# Initial plan: parameterized BixBench task 3

Objective: What is the odds ratio of higher COVID-19 severity (encoded in the column AESEV) associated with BCG vaccination in a multivariable ordinal logistic regression model that includes patient interaction frequency variables as covariates?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: BCG parameter selection: use all adverse-event records with AESEV present; ordinal logit covariates TRTGRP_cat, expect_interact_cat, patients_seen_cat; chi-square strata as prompted.
