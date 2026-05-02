# Initial plan: parameterized BixBench task 66

Objective: After performing principal component analysis (PCA) on the log10-transformed gene expression matrix (with pseudocount of 1, samples as rows and genes as columns), what percentage of the total variance in the dataset is explained by the first principal component (reported as a percentage between 0 and 100)?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: Task 66 parameter selection: log10(x+1), samples as rows and genes as columns; compute PCA variance explained from Galaxy PCA score output.
