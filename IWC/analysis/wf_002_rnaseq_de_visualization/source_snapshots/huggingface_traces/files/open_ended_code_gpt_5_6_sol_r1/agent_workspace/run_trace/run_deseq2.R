suppressPackageStartupMessages(library(DESeq2))

changed_files <- c(
  "data/inputs/counts_from_changed_condition/srr5085169_counts_table/srr5085169_counts_table.dat",
  "data/inputs/counts_from_changed_condition/srr5085170_counts_table/srr5085170_counts_table.dat"
)
reference_files <- c(
  "data/inputs/counts_from_reference_condition/srr5085167_counts_table/srr5085167_counts_table.dat",
  "data/inputs/counts_from_reference_condition/srr5085168_counts_table/srr5085168_counts_table.dat"
)
all_files <- c(changed_files, reference_files)

read_count_table <- function(path) {
  tab <- read.delim(path, header = TRUE, sep = "\t", quote = "", comment.char = "",
                    stringsAsFactors = FALSE, check.names = FALSE)
  if (ncol(tab) != 2L || names(tab)[1] != "Geneid") {
    stop("Unexpected count-table structure: ", path)
  }
  if (anyDuplicated(tab[[1]]) || anyNA(tab[[1]]) || any(tab[[1]] == "")) {
    stop("Gene identifiers must be unique and nonempty: ", path)
  }
  x <- tab[[2]]
  if (!is.numeric(x) || anyNA(x) || any(!is.finite(x)) || any(x < 0) || any(x != floor(x))) {
    stop("Counts must be finite nonnegative integers: ", path)
  }
  tab
}

tables <- lapply(all_files, read_count_table)
gene_ids <- tables[[1]][[1]]
for (i in seq_along(tables)) {
  if (!setequal(gene_ids, tables[[i]][[1]])) {
    stop("Count tables do not contain identical gene identifier sets: ", all_files[[i]])
  }
  tables[[i]] <- tables[[i]][match(gene_ids, tables[[i]][[1]]), , drop = FALSE]
}

count_matrix <- do.call(cbind, lapply(tables, function(tab) tab[[2]]))
storage.mode(count_matrix) <- "integer"
rownames(count_matrix) <- gene_ids
colnames(count_matrix) <- vapply(tables, function(tab) names(tab)[2], character(1))

keep <- rowSums(count_matrix >= 10L) >= 2L
filtered_counts <- count_matrix[keep, , drop = FALSE]
if (nrow(filtered_counts) == 0L) stop("No genes passed the required count filter")

condition <- factor(c("changed", "changed", "reference", "reference"),
                    levels = c("reference", "changed"))
col_data <- data.frame(condition = condition, row.names = colnames(filtered_counts))

dds <- DESeqDataSetFromMatrix(countData = filtered_counts,
                              colData = col_data,
                              design = ~ condition)
dds <- DESeq(dds, betaPrior = FALSE, minReplicatesForReplace = Inf, quiet = TRUE)
res <- results(dds,
               contrast = c("condition", "changed", "reference"),
               independentFiltering = FALSE,
               cooksCutoff = FALSE)

p_value <- as.numeric(res$pvalue)
log2_fold_change <- as.numeric(res$log2FoldChange)
fdr <- p.adjust(p_value, method = "BH", n = length(p_value))

if (length(p_value) != nrow(filtered_counts) || anyNA(p_value) ||
    any(!is.finite(p_value)) || any(p_value < 0 | p_value > 1)) {
  stop("DESeq2 did not return a valid raw p-value for every retained gene")
}
if (anyNA(log2_fold_change) || any(!is.finite(log2_fold_change))) {
  stop("DESeq2 did not return a finite log2 fold change for every retained gene")
}
if (anyNA(fdr) || any(!is.finite(fdr)) || any(fdr < 0 | fdr > 1)) {
  stop("BH adjustment did not return a valid value for every retained gene")
}

out <- data.frame(
  gene_id = rownames(filtered_counts),
  log2_fold_change = log2_fold_change,
  p_value = p_value,
  fdr = fdr,
  check.names = FALSE,
  stringsAsFactors = FALSE
)

dir.create("final_answer", showWarnings = FALSE, recursive = TRUE)
options(digits = 17)
write.table(out, file = "final_answer/differential_expression.tsv",
            sep = "\t", quote = FALSE, row.names = FALSE, col.names = TRUE,
            na = "NA")
writeLines('{"method":"DESeq2"}', "final_answer/method.json")

log_lines <- c(
  paste0("method=DESeq2 ", as.character(packageVersion("DESeq2"))),
  "design=~condition; contrast=changed/reference",
  paste0("samples=", paste(colnames(count_matrix), collapse = ",")),
  paste0("input_genes=", nrow(count_matrix)),
  "prefilter=raw count >=10 in >=2 of 4 samples",
  paste0("retained_and_tested_genes=", nrow(filtered_counts)),
  "log2_fold_change=unshrunken DESeq2 coefficient",
  "testing=Wald test; independentFiltering=FALSE; cooksCutoff=FALSE; outlier replacement disabled",
  "fdr=Benjamini-Hochberg over all retained genes",
  paste0("finite_lfc=", all(is.finite(out$log2_fold_change))),
  paste0("valid_p_value=", all(out$p_value >= 0 & out$p_value <= 1)),
  paste0("valid_fdr=", all(out$fdr >= 0 & out$fdr <= 1))
)
writeLines(log_lines, "run_trace/analysis.log")
cat(paste(log_lines, collapse = "\n"), "\n")
