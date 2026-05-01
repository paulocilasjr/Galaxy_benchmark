# Initial plan

Experiment: BixBench/task_1

Objective:
Use usegalaxy.org only for the scientific analysis. Starting from the provided RNA-seq count table and sample metadata, identify DESeq2 significant genes with adjusted p-value below 0.05, run GO Biological Process enrichment, simplify redundant GO terms with similarity cutoff greater than 0.7, and submit the adjusted p-value rounded to four decimals for "regulation of T cell activation".

Input datasets:
- Issy_ASXL1_blood_featureCounts_GeneTable_final.txt: gene count matrix with Ensembl gene IDs and sample columns.
- Issy_ASXL1_blood_coldata_gender.xlsx: sample metadata with condition, sex, age, and ancestry-related columns.
- gencode.v31.primary_assembly.genes.csv: Ensembl gene annotation including gene names and HGNC IDs.
- HGNC_05-09-19.txt: HGNC annotation table including approved symbols and Ensembl IDs.

Intended Galaxy execution path:
1. Create a new Galaxy history on usegalaxy.org for this run.
2. Upload the count table, metadata, and annotation files.
3. Use Galaxy tools to convert or normalize file formats as needed for tabular processing.
4. Run DESeq2 with condition as the main factor, comparing ASXL1 against Control, using the count table and sample metadata.
5. Filter DESeq2 results to padj < 0.05.
6. Map significant Ensembl IDs to gene symbols or Entrez-compatible identifiers using uploaded annotation files if the enrichment tool requires them.
7. Run GO Biological Process enrichment through a Galaxy-hosted R/clusterProfiler-capable tool or Galaxy R execution tool.
8. Apply clusterProfiler simplify with similarity cutoff above 0.7.
9. Preserve the original Galaxy outputs and extract the rounded adjusted p-value for "regulation of T cell activation".

Expected result files:
- Galaxy DESeq2 result table.
- Galaxy GO enrichment result table after simplify.
- A final result artifact containing the fixed submitted answer.

Anticipated risks:
- The metadata xlsx may need conversion to tabular form before Galaxy tools accept it.
- usegalaxy.org may not expose a direct clusterProfiler simplify wrapper; if so, use a Galaxy R execution tool while keeping the analysis inside Galaxy.
- Identifier mapping may require selecting the correct Ensembl version stripping behavior.
- The target GO term may appear only after redundancy simplification, so the preserved enrichment output must include the simplified table used for the answer.
