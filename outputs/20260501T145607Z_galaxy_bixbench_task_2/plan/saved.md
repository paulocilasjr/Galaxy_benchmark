# Initial plan: BixBench task 2

Objective: Use usegalaxy.org only to answer the BixBench prompt: identify the adjusted p-value threshold/value for the neutrophil activation GO Biological Process term from an enrichGO enrichment analysis using significant differential-expression genes (p < 0.05) between ASXL1 mutation and control, with all gencode genes as background, after removing GO terms with similarity > 0.7.

Input datasets: HGNC_05-09-19.txt, Issy_ASXL1_blood_coldata_gender.xlsx, Issy_ASXL1_blood_featureCounts_GeneTable_final.txt, and gencode.v31.primary_assembly.genes.csv from the task capsule. Ground truth will not be read until after the final submitted answer is fixed.

Intended workflow steps: create a Galaxy history, upload the task input files and a Galaxy-executed analysis script if an appropriate script-running tool is available, run the analysis in Galaxy, download and preserve Galaxy outputs, then fix the submitted answer in result artifacts before opening ground truth for scoring.

Intended tool choices: prefer usegalaxy.org installed tools for DESeq2 and GO enrichment. If no separate enrichGO/simplify tool chain is available, use a usegalaxy.org R execution tool to run Bioconductor DESeq2/clusterProfiler/org.Hs.eg.db inside Galaxy, because the prompt explicitly specifies enrichGO.

Expected result files: Galaxy-produced tabular enrichment output after simplify(similarity > 0.7 removed), a submitted-answer JSON naming the neutrophil activation adjusted p-value result, Galaxy trace snapshots, and reduced BixBench experiment_summary.json.

Anticipated risks: Galaxy tool availability for clusterProfiler/enrichGO may differ from local R package names; annotation identifiers may need Ensembl-version stripping and mapping to Entrez IDs; xlsx metadata may need conversion before upload or use by Galaxy-executed script; the target GO term may appear under an exact or closely related biological-process description.
