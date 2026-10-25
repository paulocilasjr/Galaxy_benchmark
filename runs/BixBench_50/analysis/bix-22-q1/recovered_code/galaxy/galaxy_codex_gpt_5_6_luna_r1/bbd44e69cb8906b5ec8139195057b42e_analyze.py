import csv
import sys

import numpy as np
from scipy.stats import pearsonr

count_path, gene_meta_path, sample_path = sys.argv[1:4]
cell_types = ["CD4", "CD8", "CD14", "CD19"]

with open(sample_path, newline="", encoding="utf-8") as handle:
    sample_rows = list(csv.DictReader(handle))

sample_names = [row["sample"] for row in sample_rows]
with open(count_path, newline="", encoding="utf-8") as handle:
    count_reader = csv.reader(handle)
    count_header = next(count_reader)

if count_header[1:] != sample_names:
    raise RuntimeError("count-matrix sample header does not exactly match annotation order")

header_index = {name: index for index, name in enumerate(count_header)}
sample_indices = {}
for cell_type in cell_types:
    names = [row["sample"] for row in sample_rows if row["celltype"] == cell_type]
    if not names:
        raise RuntimeError("no samples found for " + cell_type)
    sample_indices[cell_type] = [header_index[name] for name in names]

gene_meta = {}
with open(gene_meta_path, newline="", encoding="utf-8") as handle:
    for row in csv.DictReader(handle):
        gene_id = row["Geneid"]
        if gene_id in gene_meta:
            raise RuntimeError("duplicate Geneid in gene metadata: " + gene_id)
        gene_meta[gene_id] = (float(row["Length"]), row["gene_biotype"])

lengths = []
averages = {cell_type: [] for cell_type in cell_types}
seen_genes = set()

with open(count_path, newline="", encoding="utf-8") as handle:
    count_reader = csv.reader(handle)
    next(count_reader)
    for row in count_reader:
        gene_id = row[0]
        if gene_id not in gene_meta:
            continue
        seen_genes.add(gene_id)
        length, biotype = gene_meta[gene_id]
        if biotype != "protein_coding":
            continue
        try:
            values = {index: float(row[index]) for indices in sample_indices.values() for index in indices}
        except (ValueError, IndexError) as exc:
            raise RuntimeError("non-numeric or missing expression value for " + gene_id) from exc
        lengths.append(length)
        for cell_type in cell_types:
            cell_values = np.asarray(
                [values[index] for index in sample_indices[cell_type]],
                dtype=np.float64,
            )
            averages[cell_type].append(float(np.mean(cell_values)))

protein_coding_ids = {gene_id for gene_id, (_, biotype) in gene_meta.items() if biotype == "protein_coding"}
missing_ids = protein_coding_ids - seen_genes
if missing_ids:
    raise RuntimeError("protein-coding genes missing from count matrix: " + str(len(missing_ids)))

length_array = np.asarray(lengths, dtype=np.float64)
if length_array.size < 3:
    raise RuntimeError("fewer than three protein-coding genes available")

with open("correlations.tsv", "w", encoding="utf-8", newline="") as output:
    output.write("cell_type\tn_samples\tn_protein_coding_genes\tpearson_r\tabsolute_pearson_r\n")
    for cell_type in cell_types:
        expression_array = np.asarray(averages[cell_type], dtype=np.float64)
        if expression_array.size != length_array.size:
            raise RuntimeError("gene vector length mismatch for " + cell_type)
        correlation, _ = pearsonr(length_array, expression_array)
        output.write(
            cell_type
            + "\t"
            + str(len(sample_indices[cell_type]))
            + "\t"
            + str(int(length_array.size))
            + "\t"
            + format(float(correlation), ".17g")
            + "\t"
            + format(abs(float(correlation)), ".17g")
            + "\n"
        )
