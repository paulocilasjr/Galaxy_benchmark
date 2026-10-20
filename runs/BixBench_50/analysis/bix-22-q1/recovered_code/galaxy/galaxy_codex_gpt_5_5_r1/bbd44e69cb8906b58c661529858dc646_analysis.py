import csv
import math
import sys

counts_path, meta_path, sample_path, corr_out, answer_out = sys.argv[1:6]
target_celltypes = ["CD4", "CD8", "CD14", "CD19"]

# Map annotated samples to the requested immune-cell labels.
celltype_samples = {ct: [] for ct in target_celltypes}
with open(sample_path, newline='') as handle:
    reader = csv.DictReader(handle)
    required = {"sample", "celltype"}
    if not required.issubset(reader.fieldnames or []):
        raise SystemExit("Sample annotation must contain sample and celltype columns")
    for row in reader:
        ct = row["celltype"]
        if ct in celltype_samples:
            celltype_samples[ct].append(row["sample"])

# Protein-coding genes and their lengths define the analysis rows.
length_by_gene = {}
with open(meta_path, newline='') as handle:
    reader = csv.DictReader(handle)
    required = {"Geneid", "Length", "gene_biotype"}
    if not required.issubset(reader.fieldnames or []):
        raise SystemExit("Gene metadata must contain Geneid, Length, and gene_biotype columns")
    for row in reader:
        if row["gene_biotype"] == "protein_coding":
            gene = row["Geneid"]
            try:
                length = float(row["Length"])
            except ValueError:
                continue
            if math.isfinite(length):
                length_by_gene[gene] = length

# Match requested samples to expression columns.
with open(counts_path, newline='') as handle:
    reader = csv.reader(handle)
    header = next(reader)
    sample_to_index = {name: idx for idx, name in enumerate(header) if idx > 0}
    indices_by_celltype = {}
    for ct, samples in celltype_samples.items():
        indices = [sample_to_index[sample] for sample in samples if sample in sample_to_index]
        if not indices:
            raise SystemExit(f"No expression columns found for {ct}")
        indices_by_celltype[ct] = indices

    lengths = {ct: [] for ct in target_celltypes}
    means = {ct: [] for ct in target_celltypes}

    for row in reader:
        if not row:
            continue
        gene = row[0]
        if gene not in length_by_gene:
            continue
        gene_length = length_by_gene[gene]
        for ct in target_celltypes:
            vals = []
            for idx in indices_by_celltype[ct]:
                try:
                    val = float(row[idx])
                except (IndexError, ValueError):
                    continue
                if math.isfinite(val):
                    vals.append(val)
            if vals:
                lengths[ct].append(gene_length)
                means[ct].append(sum(vals) / len(vals))

def pearson(xs, ys):
    n = len(xs)
    if n != len(ys) or n < 2:
        raise SystemExit("Pearson correlation requires paired vectors with at least two rows")
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = 0.0
    syy = 0.0
    sxy = 0.0
    for x, y in zip(xs, ys):
        dx = x - mean_x
        dy = y - mean_y
        sxx += dx * dx
        syy += dy * dy
        sxy += dx * dy
    denom = math.sqrt(sxx * syy)
    if denom == 0.0:
        raise SystemExit("Pearson correlation undefined for zero-variance vector")
    return sxy / denom

results = []
for ct in target_celltypes:
    r = pearson(lengths[ct], means[ct])
    results.append({
        "celltype": ct,
        "n_genes": len(lengths[ct]),
        "n_samples": len(indices_by_celltype[ct]),
        "pearson_r": r,
        "abs_pearson_r": abs(r),
    })

weakest = min(results, key=lambda item: item["abs_pearson_r"])["celltype"]

with open(corr_out, "w", newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=["celltype", "n_genes", "n_samples", "pearson_r", "abs_pearson_r"], delimiter='\t')
    writer.writeheader()
    for item in results:
        writer.writerow({
            "celltype": item["celltype"],
            "n_genes": item["n_genes"],
            "n_samples": item["n_samples"],
            "pearson_r": format(item["pearson_r"], ".17g"),
            "abs_pearson_r": format(item["abs_pearson_r"], ".17g"),
        })

with open(answer_out, "w") as handle:
    handle.write(weakest + "\n")
