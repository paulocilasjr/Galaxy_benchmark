suppressPackageStartupMessages({
  library(DESeq2)
  library(jsonlite)
})

workspace <- "/workspace"
changed_files <- c(
  file.path(workspace, "data/inputs/counts_from_changed_condition/srr5085169_counts_table/srr5085169_counts_table.dat"),
  file.path(workspace, "data/inputs/counts_from_changed_condition/srr5085170_counts_table/srr5085170_counts_table.dat")
)
reference_files <- c(
  file.path(workspace, "data/inputs/counts_from_reference_condition/srr5085167_counts_table/srr5085167_counts_table.dat"),
  file.path(workspace, "data/inputs/counts_from_reference_condition/srr5085168_counts_table/srr5085168_counts_table.dat")
)
all_files <- c(reference_files, changed_files)

read_count_file <- function(path) {
  x <- read.delim(path, check.names = FALSE, stringsAsFactors = FALSE)
  if (!identical(names(x)[1], "Geneid") || ncol(x) != 2) {
    stop("Unexpected count table format: ", path)
  }
  if (anyDuplicated(x[[1]]) > 0) {
    stop("Duplicate gene IDs in: ", path)
  }
  x
}

tables <- lapply(all_files, read_count_file)
gene_ids <- tables[[1]][[1]]
for (i in seq_along(tables)) {
  if (!identical(gene_ids, tables[[i]][[1]])) {
    stop("Gene IDs/order differ in: ", all_files[[i]])
  }
}

count_df <- data.frame(gene_id = gene_ids, stringsAsFactors = FALSE)
for (tbl in tables) {
  count_df[[names(tbl)[2]]] <- tbl[[2]]
}

sample_names <- names(count_df)[-1]
count_mat <- as.matrix(count_df[, sample_names, drop = FALSE])
storage.mode(count_mat) <- "integer"
rownames(count_mat) <- count_df$gene_id

condition <- factor(
  c(rep("reference", length(reference_files)), rep("changed", length(changed_files))),
  levels = c("reference", "changed")
)
col_data <- data.frame(condition = condition, row.names = sample_names)

keep <- rowSums(count_mat >= 10) >= 2
retained_count <- sum(keep)
if (retained_count == 0) {
  stop("No genes retained by the requested count filter")
}

dds <- DESeqDataSetFromMatrix(
  countData = count_mat[keep, , drop = FALSE],
  colData = col_data,
  design = ~ condition
)
dds <- DESeq(dds, quiet = TRUE)
res <- results(
  dds,
  contrast = c("condition", "changed", "reference"),
  independentFiltering = FALSE,
  cooksCutoff = FALSE
)

out <- data.frame(
  gene_id = rownames(res),
  log2_fold_change = res$log2FoldChange,
  p_value = res$pvalue,
  stringsAsFactors = FALSE
)
out$fdr <- p.adjust(out$p_value, method = "BH")

if (any(!is.finite(out$log2_fold_change))) {
  stop("Non-finite log2 fold change values produced")
}
if (any(is.na(out$p_value)) || any(out$p_value < 0 | out$p_value > 1)) {
  stop("Invalid raw p-values produced")
}
if (any(is.na(out$fdr)) || any(out$fdr < 0 | out$fdr > 1)) {
  stop("Invalid adjusted p-values produced")
}
if (nrow(out) != retained_count) {
  stop("Output row count does not match retained gene count")
}

dir.create(file.path(workspace, "final_answer"), showWarnings = FALSE)
write.table(
  out,
  file = file.path(workspace, "final_answer/differential_expression.tsv"),
  sep = "\t",
  quote = FALSE,
  row.names = FALSE,
  col.names = TRUE
)
write_json(
  list(method = "DESeq2"),
  path = file.path(workspace, "final_answer/method.json"),
  auto_unbox = TRUE
)

trace <- list(
  method = "DESeq2",
  samples = as.list(setNames(as.character(condition), sample_names)),
  total_genes = nrow(count_mat),
  retained_genes = retained_count,
  filter = "at least 10 raw counts in at least two of the four samples",
  contrast = "changed vs reference",
  deseq2_version = as.character(packageVersion("DESeq2"))
)
write_json(
  trace,
  path = file.path(workspace, "run_trace/execution_summary.json"),
  auto_unbox = TRUE,
  pretty = TRUE
)
