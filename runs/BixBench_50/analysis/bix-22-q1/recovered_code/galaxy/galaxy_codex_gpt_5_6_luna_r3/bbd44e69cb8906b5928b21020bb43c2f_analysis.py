import csv
import math
import sys

import numpy as np
from scipy.stats import pearsonr

expression_path, metadata_path, samples_path = sys.argv[1:4]
wanted = ("CD4", "CD8", "CD14", "CD19")

sample_to_celltype = {}
with open(samples_path, "r", newline="") as handle:
    reader = csv.DictReader(handle)
    required = {"sample", "celltype"}
    if not required.issubset(set(reader.fieldnames or [])):
        raise RuntimeError("Sample annotation lacks sample/celltype columns")
    for row in reader:
        sample = (row["sample"] or "").strip()
        celltype = (row["celltype"] or "").strip()
        if not sample:
            raise RuntimeError("Blank sample name in annotation")
        if sample in sample_to_celltype and sample_to_celltype[sample] != celltype:
            raise RuntimeError("Conflicting sample annotation: " + sample)
        sample_to_celltype[sample] = celltype

protein_meta = {}
with open(metadata_path, "r", newline="") as handle:
    reader = csv.reader(handle)
    header = next(reader)
    gene_col = header.index("Geneid")
    length_col = header.index("Length")
    biotype_col = header.index("gene_biotype")
    for row in reader:
        if len(row) <= max(gene_col, length_col, biotype_col):
            raise RuntimeError("Short row in gene metadata")
        gene_id = row[gene_col].strip()
        if not gene_id:
            raise RuntimeError("Blank gene identifier in metadata")
        if gene_id in protein_meta:
            raise RuntimeError("Duplicate gene identifier in metadata: " + gene_id)
        if row[biotype_col].strip() == "protein_coding":
            length = float(row[length_col])
            if not math.isfinite(length):
                raise RuntimeError("Non-finite gene length: " + gene_id)
            protein_meta[gene_id] = length

with open(expression_path, "r", newline="") as handle:
    reader = csv.reader(handle)
    expression_header = next(reader)
    if len(expression_header) < 2:
        raise RuntimeError("Expression matrix has no sample columns")
    selected_indices = {celltype: [] for celltype in wanted}
    seen_samples = set()
    for index, sample in enumerate(expression_header[1:], start=1):
        sample = sample.strip()
        if sample in seen_samples:
            raise RuntimeError("Duplicate expression sample column: " + sample)
        seen_samples.add(sample)
        celltype = sample_to_celltype.get(sample)
        if celltype in selected_indices:
            selected_indices[celltype].append(index)
    for celltype in wanted:
        if not selected_indices[celltype]:
            raise RuntimeError("No expression samples annotated as " + celltype)

    lengths = {celltype: [] for celltype in wanted}
    averages = {celltype: [] for celltype in wanted}
    seen_genes = set()
    for row in reader:
        if not row:
            continue
        gene_id = row[0].strip()
        if not gene_id:
            raise RuntimeError("Blank gene identifier in expression matrix")
        if gene_id in seen_genes:
            raise RuntimeError("Duplicate gene identifier in expression matrix: " + gene_id)
        seen_genes.add(gene_id)
        if gene_id not in protein_meta:
            continue
        for celltype in wanted:
            values = []
            for index in selected_indices[celltype]:
                if index >= len(row):
                    raise RuntimeError("Short expression row: " + gene_id)
                value = float(row[index])
                if not math.isfinite(value):
                    raise RuntimeError("Non-finite expression value: " + gene_id)
                values.append(value)
            average = float(np.mean(np.asarray(values, dtype=np.float64)))
            lengths[celltype].append(protein_meta[gene_id])
            averages[celltype].append(average)

results = []
for celltype in wanted:
    x = np.asarray(lengths[celltype], dtype=np.float64)
    y = np.asarray(averages[celltype], dtype=np.float64)
    if x.size < 3 or y.size != x.size:
        raise RuntimeError("Insufficient paired genes for " + celltype)
    correlation, unused_pvalue = pearsonr(x, y)
    correlation = float(correlation)
    results.append((celltype, len(selected_indices[celltype]), int(x.size), correlation, abs(correlation)))

with open("correlations.tsv", "w", newline="") as handle:
    writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    writer.writerow(("cell_type", "n_samples", "n_protein_coding_genes", "pearson_r", "absolute_pearson_r"))
    for result in results:
        writer.writerow((result[0], result[1], result[2], "%.17g" % result[3], "%.17g" % result[4]))

weakest = min(results, key=lambda result: result[4])
with open("weakest.txt", "w", newline="") as handle:
    handle.write(weakest[0] + "\n")
