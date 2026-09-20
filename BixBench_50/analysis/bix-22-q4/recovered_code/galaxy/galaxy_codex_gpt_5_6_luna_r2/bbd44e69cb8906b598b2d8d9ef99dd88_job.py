import csv
import sys
from pathlib import Path

import numpy as np

counts_path = Path(sys.argv[1])
gene_meta_path = Path(sys.argv[2])
sample_meta_path = Path(sys.argv[3])

with sample_meta_path.open("r", newline="") as fh:
    sample_reader = csv.DictReader(fh)
    required = {"sample", "celltype"}
    if not required.issubset(set(sample_reader.fieldnames or [])):
        raise ValueError("Sample metadata lacks sample/celltype columns")
    cd14_samples = [
        row["sample"]
        for row in sample_reader
        if row.get("celltype") == "CD14"
    ]
if not cd14_samples:
    raise ValueError("No CD14 samples found")

gene_meta = {}
with gene_meta_path.open("r", newline="") as fh:
    gene_reader = csv.DictReader(fh)
    required = {"Geneid", "Length", "gene_biotype"}
    if not required.issubset(set(gene_reader.fieldnames or [])):
        raise ValueError("Gene metadata lacks Geneid/Length/gene_biotype columns")
    for row in gene_reader:
        gene_id = row["Geneid"]
        if not gene_id:
            raise ValueError("Blank Geneid in gene metadata")
        if gene_id in gene_meta:
            raise ValueError("Duplicate Geneid in gene metadata: " + gene_id)
        gene_meta[gene_id] = (
            int(float(row["Length"])),
            row["gene_biotype"],
        )

kept = 0
seen_counts = set()
with counts_path.open("r", newline="") as fh:
    count_reader = csv.reader(fh)
    header = next(count_reader)
    if len(header) < 2:
        raise ValueError("Count matrix has no sample columns")
    count_samples = header[1:]
    if len(set(count_samples)) != len(count_samples):
        raise ValueError("Duplicate sample names in count matrix header")
    sample_to_col = {sample: idx + 1 for idx, sample in enumerate(count_samples)}
    missing = [sample for sample in cd14_samples if sample not in sample_to_col]
    if missing:
        raise ValueError("CD14 samples missing from count matrix: " + ",".join(missing[:5]))
    selected_cols = [sample_to_col[sample] for sample in cd14_samples]

    with Path("gene_lengths.tsv").open("w") as length_out, Path("gene_means.tsv").open("w") as mean_out:
        length_out.write("gene_id\tgene_length\n")
        mean_out.write("gene_id\tmean_expression\n")
        for row in count_reader:
            if not row:
                continue
            gene_id = row[0]
            if gene_id in seen_counts:
                raise ValueError("Duplicate gene in count matrix: " + gene_id)
            seen_counts.add(gene_id)
            meta = gene_meta.get(gene_id)
            if meta is None:
                raise ValueError("Count gene missing from gene metadata: " + gene_id)
            length, biotype = meta
            if biotype != "protein_coding":
                continue
            if len(row) != len(header):
                raise ValueError("Count row has wrong number of columns for " + gene_id)
            values = np.fromiter(
                (row[col] for col in selected_cols),
                dtype=np.float64,
                count=len(selected_cols),
            )
            total_counts = np.sum(values, dtype=np.float64)
            if total_counts < 10.0:
                continue
            mean_expression = np.mean(values, dtype=np.float64)
            length_out.write(gene_id + "\t" + str(length) + "\n")
            mean_out.write(
                gene_id + "\t" + format(float(mean_expression), ".17g") + "\n"
            )
            kept += 1

if kept < 3:
    raise ValueError("Fewer than three genes passed the filter")
print("CD14 samples:", len(cd14_samples), file=sys.stderr)
print("Protein-coding genes passing total-count filter:", kept, file=sys.stderr)

