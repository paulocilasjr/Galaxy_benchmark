# Initial plan: BixBench task 66

Objective: Use usegalaxy.org to report the percent of total variance explained by PC1 after PCA on log10 gene expression with pseudocount 1, samples as rows and genes as columns.

Input datasets: ROSMAP_genexp_ad.csv and ROSMAP_meta_ad.csv. Ground truth will not be opened until the final submitted answer is fixed.

Intended path: prepare the prompt-specified numeric matrix orientation locally for Galaxy upload; upload source files and prepared matrix to Galaxy; run the Galaxy sklearn_pca tool if its API parameters are usable. If the PCA tool is not API-submittable for this matrix, use Galaxy tabular tooling on a preserved PCA-derived variance table and document the limitation. Download Galaxy outputs, fix submitted PC1 percentage, then open ground truth for scoring.

Expected output: PC1 explained variance percentage between 0 and 100.
