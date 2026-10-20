.libPaths(c("Rlib", .libPaths()))
suppressPackageStartupMessages({
  library(DESeq2)
  library(apeglm)
})
if (as.character(packageVersion("apeglm")) != "1.24.0") {
  stop("Unexpected apeglm version")
}

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2L) stop("Expected count matrix and sample metadata paths")

count_df <- read.table(
  args[[1]], header = TRUE, check.names = FALSE,
  stringsAsFactors = FALSE, comment.char = "", quote = ""
)
if (ncol(count_df) < 2L) stop("Count matrix has fewer than two columns")
gene_id <- count_df[[1]]
if (anyNA(gene_id) || anyDuplicated(gene_id)) stop("Gene identifiers are missing or duplicated")
count_mat <- as.matrix(count_df[, -1, drop = FALSE])
suppressWarnings(storage.mode(count_mat) <- "numeric")
if (anyNA(count_mat) || any(!is.finite(count_mat)) || any(count_mat < 0) ||
    any(count_mat != floor(count_mat))) {
  stop("Count matrix contains missing, non-finite, negative, or non-integer values")
}
storage.mode(count_mat) <- "integer"
rownames(count_mat) <- gene_id

meta <- read.delim(
  args[[2]], header = TRUE, check.names = FALSE,
  stringsAsFactors = FALSE, na.strings = c("", "NA")
)
needed <- c("sample", "condition", "sex")
if (!all(needed %in% colnames(meta))) stop("Metadata lacks sample, condition, or sex")
meta <- meta[
  !is.na(meta$sample) & nzchar(meta$sample) &
  !is.na(meta$condition) & nzchar(meta$condition) &
  !is.na(meta$sex) & nzchar(meta$sex),
  needed, drop = FALSE
]
if (anyDuplicated(meta$sample)) stop("Metadata sample identifiers are duplicated")

all_count_samples <- colnames(count_mat)
analyzed_samples <- all_count_samples[all_count_samples %in% meta$sample]
excluded_samples <- setdiff(all_count_samples, analyzed_samples)
if (length(analyzed_samples) < 2L) stop("Too few matched samples")
meta <- meta[match(analyzed_samples, meta$sample), , drop = FALSE]
if (anyNA(meta$sample) || !identical(meta$sample, analyzed_samples)) stop("Sample matching failed")
if (!setequal(unique(meta$condition), c("ASXL1", "Control"))) stop("Unexpected condition levels")
if (!setequal(unique(meta$sex), c("F", "M"))) stop("Unexpected sex levels")

meta$sex <- factor(meta$sex, levels = c("F", "M"))
meta$condition <- factor(meta$condition, levels = c("Control", "ASXL1"))
rownames(meta) <- meta$sample
count_mat <- count_mat[, analyzed_samples, drop = FALSE]

dds <- DESeqDataSetFromMatrix(
  countData = count_mat,
  colData = meta,
  design = ~ sex + condition
)
dds <- DESeq(dds)
target_coef <- "condition_ASXL1_vs_Control"
if (!(target_coef %in% resultsNames(dds))) {
  stop(paste("Expected coefficient not found; available:", paste(resultsNames(dds), collapse = ",")))
}

unshrunk <- results(
  dds,
  contrast = c("condition", "ASXL1", "Control"),
  alpha = 0.05,
  independentFiltering = TRUE
)
shrunk <- lfcShrink(dds, coef = target_coef, type = "apeglm")

result <- data.frame(
  gene_id = rownames(unshrunk),
  baseMean = unshrunk$baseMean,
  log2FoldChange = shrunk$log2FoldChange,
  lfcSE = shrunk$lfcSE,
  pvalue = unshrunk$pvalue,
  padj = unshrunk$padj,
  check.names = FALSE
)
write.table(result, file = "deseq2_apeglm_results.tsv", sep = "\t", quote = FALSE,
            row.names = FALSE, col.names = TRUE, na = "NA")

summary <- data.frame(
  deseq2_version = as.character(packageVersion("DESeq2")),
  apeglm_version = as.character(packageVersion("apeglm")),
  design = "~ sex + condition",
  contrast = "condition: ASXL1 vs Control",
  shrinkage = "apeglm",
  results_alpha = 0.05,
  independent_filtering = TRUE,
  input_gene_rows = nrow(count_mat),
  count_matrix_samples = length(all_count_samples),
  analyzed_samples_n = length(analyzed_samples),
  analyzed_samples = paste(analyzed_samples, collapse = ";"),
  excluded_count_samples_n = length(excluded_samples),
  excluded_count_samples = paste(excluded_samples, collapse = ";"),
  significant_genes_padj_lt_0_05 = sum(!is.na(result$padj) & result$padj < 0.05),
  stringsAsFactors = FALSE,
  check.names = FALSE
)
write.table(summary, file = "analysis_summary.tsv", sep = "\t", quote = FALSE,
            row.names = FALSE, col.names = TRUE, na = "NA")
