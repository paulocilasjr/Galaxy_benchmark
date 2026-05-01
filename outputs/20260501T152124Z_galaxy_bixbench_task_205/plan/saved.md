# Initial plan: BixBench task 205

Objective: Use usegalaxy.org only to answer which tissue type has the highest number of significantly differentially expressed genes for bad responders versus controls, using lfc > 0.5 and basemean > 10.

Input dataset: Data_deposition_RNAseq_Paroxetine_2017.xlsx. Ground truth is hidden and will not be opened until the final submitted answer is fixed.

Intended path: upload the workbook and a tidy TSV derived from its DESeq result blocks into Galaxy; run Galaxy tabular filtering/counting tools to count qualifying bad-responder-vs-control genes by tissue; download/preserve Galaxy outputs; fix submitted answer; then open ground truth for scoring.

Expected result: one tissue label with the largest count, plus Galaxy output files supporting the count.

Risks: comparison numbering must be mapped correctly to tissue and responder/control groups; the prompt says lfc > 0.5 and basemean > 10, which I interpret as absolute log2FoldChange greater than 0.5 unless Galaxy output evidence clearly indicates signed-only filtering is intended.
