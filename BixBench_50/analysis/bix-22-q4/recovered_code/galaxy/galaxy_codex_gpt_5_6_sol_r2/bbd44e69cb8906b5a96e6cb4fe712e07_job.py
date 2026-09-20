import csv
import math
import sys
import scipy
from scipy.stats import pearsonr

counts_path, meta_path, annotation_path, output_path = sys.argv[1:5]

with open(annotation_path, "r") as handle:
    reader = csv.DictReader(handle)
    required = {"sample", "celltype"}
    if not required.issubset(set(reader.fieldnames or [])):
        raise ValueError("Sample annotation is missing required columns")
    annotation_rows = list(reader)

sample_ids = [row["sample"] for row in annotation_rows]
if len(sample_ids) != len(set(sample_ids)):
    raise ValueError("Sample annotation contains duplicate sample identifiers")
cd14_samples = [row["sample"] for row in annotation_rows if row["celltype"] == "CD14"]
if not cd14_samples:
    raise ValueError("No samples have celltype exactly CD14")
cd14_set = set(cd14_samples)

meta = {}
with open(meta_path, "r") as handle:
    reader = csv.DictReader(handle)
    required = {"Geneid", "Length", "gene_biotype"}
    if not required.issubset(set(reader.fieldnames or [])):
        raise ValueError("Gene metadata is missing required columns")
    for row in reader:
        gene = row["Geneid"]
        if gene in meta:
            raise ValueError("Duplicate Geneid in metadata: " + gene)
        meta[gene] = (row["Length"], row["gene_biotype"])

lengths = []
means = []
seen_genes = set()
with open(counts_path, "r") as handle:
    reader = csv.reader(handle)
    header = next(reader)
    count_samples = header[1:]
    if len(count_samples) != len(set(count_samples)):
        raise ValueError("Counts matrix contains duplicate sample columns")
    if set(count_samples) != set(sample_ids):
        missing_counts = sorted(set(sample_ids) - set(count_samples))
        missing_annotation = sorted(set(count_samples) - set(sample_ids))
        raise ValueError("Counts/annotation sample mismatch: %d missing in counts, %d missing in annotation" % (len(missing_counts), len(missing_annotation)))
    cd14_indices = [i + 1 for i, sample in enumerate(count_samples) if sample in cd14_set]
    if len(cd14_indices) != len(cd14_samples):
        raise ValueError("Not all CD14 samples were found in counts matrix")
    for row_number, row in enumerate(reader, start=2):
        if len(row) != len(header):
            raise ValueError("Counts row %d has %d fields; expected %d" % (row_number, len(row), len(header)))
        gene = row[0]
        if gene in seen_genes:
            raise ValueError("Duplicate gene in counts matrix: " + gene)
        seen_genes.add(gene)
        if gene not in meta:
            raise ValueError("Counts gene absent from metadata: " + gene)
        length_text, biotype = meta[gene]
        if biotype != "protein_coding":
            continue
        values = [float(row[i]) for i in cd14_indices]
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Non-finite CD14 count for gene: " + gene)
        total = sum(values)
        if total < 10.0:
            continue
        length = float(length_text)
        if not math.isfinite(length):
            raise ValueError("Non-finite gene length for gene: " + gene)
        lengths.append(length)
        means.append(total / float(len(cd14_indices)))

if seen_genes != set(meta):
    raise ValueError("Counts and metadata gene sets differ")
if len(lengths) < 2:
    raise ValueError("Fewer than two genes passed the requested filters")

r_value, p_value = pearsonr(lengths, means)
with open(output_path, "w") as handle:
    handle.write("pearson_r\tp_value\tn_genes\tn_cd14_samples\ttotal_count_threshold\tbiotype\tsample_scope\tmean_definition\tscipy_version\n")
    handle.write("%.17g\t%.17g\t%d\t%d\t10\tprotein_coding\tcelltype=CD14\tarithmetic_mean_across_CD14_samples\t%s\n" % (r_value, p_value, len(lengths), len(cd14_indices), scipy.__version__))
