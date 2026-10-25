suppressPackageStartupMessages(library(DESeq2))
suppressPackageStartupMessages(library(jsonlite))
options(digits = 15)

changed_files <- c(
  "data/inputs/counts_from_changed_condition/srr5085169_counts_table/srr5085169_counts_table.dat",
  "data/inputs/counts_from_changed_condition/srr5085170_counts_table/srr5085170_counts_table.dat"
)
reference_files <- c(
  "data/inputs/counts_from_reference_condition/srr5085167_counts_table/srr5085167_counts_table.dat",
  "data/inputs/counts_from_reference_condition/srr5085168_counts_table/srr5085168_counts_table.dat"
)
all_files <- c(reference_files, changed_files)

read_count_table <- function(path) {
  x <- read.delim(
    path,
    header = TRUE,
    sep = "\t",
    quote = "",
    comment.char = "",
    check.names = FALSE,
    stringsAsFactors = FALSE
  )
  stopifnot(ncol(x) == 2L, identical(colnames(x)[1], "Geneid"))
  stopifnot(!anyNA(x[[1]]), !anyDuplicated(x[[1]]))
  stopifnot(is.numeric(x[[2]]), !anyNA(x[[2]]), all(is.finite(x[[2]])))
  stopifnot(all(x[[2]] >= 0), all(x[[2]] == floor(x[[2]])))
  x
}

tables <- lapply(all_files, read_count_table)
gene_ids <- tables[[1]][[1]]
stopifnot(all(vapply(tables, function(x) identical(x[[1]], gene_ids), logical(1))))

count_matrix <- do.call(cbind, lapply(tables, `[[`, 2L))
storage.mode(count_matrix) <- "integer"
rownames(count_matrix) <- gene_ids
colnames(count_matrix) <- vapply(tables, function(x) colnames(x)[2], character(1))

condition <- factor(
  c(rep("reference", length(reference_files)), rep("changed", length(changed_files))),
  levels = c("reference", "changed")
)
sample_data <- data.frame(condition = condition, row.names = colnames(count_matrix))

keep <- rowSums(count_matrix >= 10L) >= 2L
filtered_counts <- count_matrix[keep, , drop = FALSE]
stopifnot(nrow(filtered_counts) > 0L)

dds <- DESeqDataSetFromMatrix(
  countData = filtered_counts,
  colData = sample_data,
  design = ~ condition
)
dds <- DESeq(dds, betaPrior = FALSE, minReplicatesForReplace = Inf, quiet = TRUE)

res <- results(
  dds,
  contrast = c("condition", "changed", "reference"),
  alpha = 0.1,
  pAdjustMethod = "BH",
  independentFiltering = FALSE,
  cooksCutoff = FALSE
)

# Recompute BH explicitly over exactly the retained/tested gene universe.
fdr <- p.adjust(res$pvalue, method = "BH")
output <- data.frame(
  gene_id = rownames(res),
  log2_fold_change = res$log2FoldChange,
  p_value = res$pvalue,
  fdr = fdr,
  check.names = FALSE,
  stringsAsFactors = FALSE
)

stopifnot(identical(output$gene_id, gene_ids[keep]))
stopifnot(nrow(output) == sum(keep), !anyDuplicated(output$gene_id))
stopifnot(all(is.finite(output$log2_fold_change)))
stopifnot(all(is.finite(output$p_value)), all(output$p_value >= 0 & output$p_value <= 1))
stopifnot(all(is.finite(output$fdr)), all(output$fdr >= 0 & output$fdr <= 1))

dir.create("final_answer", showWarnings = FALSE)
write.table(
  output,
  file = "final_answer/differential_expression.tsv",
  sep = "\t",
  quote = FALSE,
  row.names = FALSE,
  col.names = TRUE,
  na = "NA"
)
write_json(
  list(method = "DESeq2"),
  path = "final_answer/method.json",
  auto_unbox = TRUE,
  pretty = FALSE
)
cat("\n", file = "final_answer/method.json", append = TRUE)

log_lines <- c(
  paste0("timestamp_utc: ", format(Sys.time(), tz = "UTC", usetz = TRUE)),
  paste0("R: ", R.version.string),
  paste0("DESeq2: ", as.character(packageVersion("DESeq2"))),
  "method: DESeq2 negative-binomial GLM, Wald test",
  "design: ~ condition; contrast changed/reference",
  "samples: reference=SRR5085167,SRR5085168; changed=SRR5085169,SRR5085170",
  "prefilter: raw count >= 10 in >= 2 of 4 samples",
  paste0("input_genes: ", nrow(count_matrix)),
  paste0("retained_and_tested_genes: ", nrow(filtered_counts)),
  paste0("library_sizes: ", paste(names(colSums(count_matrix)), colSums(count_matrix), sep = "=", collapse = ",")),
  paste0("size_factors: ", paste(names(sizeFactors(dds)), signif(sizeFactors(dds), 8), sep = "=", collapse = ",")),
  "log2_fold_change: unshrunken maximum-likelihood estimate",
  "p_value: Wald-test p-value; Cook's cutoff disabled",
  "fdr: BH adjustment across all retained genes; independent filtering disabled",
  "validation: exact columns/row universe; all statistics finite and in required ranges"
)
dir.create("run_trace", showWarnings = FALSE)
writeLines(log_lines, "run_trace/execution.log", useBytes = TRUE)
