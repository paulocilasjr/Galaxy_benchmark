import csv
import statistics
import sys
from pathlib import Path

counts_path, metadata_path, samples_path = sys.argv[1:4]

cd14_samples = []
with open(samples_path, "r", newline="") as handle:
    for row in csv.DictReader(handle):
        if row["celltype"].strip() == "CD14":
            cd14_samples.append(row["sample"].strip())

if not cd14_samples:
    raise RuntimeError("No CD14 samples found in sample annotation")
if len(cd14_samples) != len(set(cd14_samples)):
    raise RuntimeError("Duplicate CD14 sample names in sample annotation")

gene_metadata = {}
with open(metadata_path, "r", newline="") as handle:
    for row in csv.DictReader(handle):
        gene_id = row["Geneid"].strip()
        if gene_id in gene_metadata:
            raise RuntimeError(f"Duplicate gene metadata key: {gene_id}")
        gene_metadata[gene_id] = (
            float(row["Length"].strip()),
            row["gene_biotype"].strip(),
        )

lengths = []
means = []
seen_genes = set()

with open(counts_path, "r", newline="") as handle:
    reader = csv.reader(handle)
    header = next(reader)
    if len(header) < 2:
        raise RuntimeError("Counts matrix has no sample columns")
    header_indices = {}
    for index, name in enumerate(header[1:], start=1):
        sample = name.strip()
        if sample in header_indices:
            raise RuntimeError(f"Duplicate sample column: {sample}")
        header_indices[sample] = index
    missing = [sample for sample in cd14_samples if sample not in header_indices]
    if missing:
        raise RuntimeError("CD14 samples missing from counts matrix: " + ",".join(missing))
    selected_indices = [header_indices[sample] for sample in cd14_samples]

    for row_number, row in enumerate(reader, start=2):
        if len(row) != len(header):
            raise RuntimeError(
                f"Counts row {row_number} has {len(row)} fields; expected {len(header)}"
            )
        gene_id = row[0].strip()
        if gene_id in seen_genes:
            raise RuntimeError(f"Duplicate gene row: {gene_id}")
        seen_genes.add(gene_id)
        if gene_id not in gene_metadata:
            raise RuntimeError(f"Gene missing from metadata: {gene_id}")
        length, biotype = gene_metadata[gene_id]
        if biotype != "protein_coding":
            continue
        values = [float(row[index]) for index in selected_indices]
        total = sum(values)
        if total >= 10.0:
            lengths.append(length)
            means.append(total / len(selected_indices))

if len(lengths) < 2:
    raise RuntimeError("Fewer than two genes passed the requested filter")
if len(set(lengths)) < 2 or len(set(means)) < 2:
    raise RuntimeError("Pearson correlation is undefined for a constant input")
correlation = statistics.correlation(lengths, means, method="linear")
Path("answer.txt").write_text(format(correlation, ".17g") + "\n")
