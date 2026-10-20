import sys
import pandas as pd

counts_path, meta_path, sample_path, out_path = sys.argv[1:5]

samples = pd.read_csv(sample_path)
for col in ["sample", "celltype"]:
    if col not in samples.columns:
        raise SystemExit(f"missing sample annotation column: {col}")
cd14_samples = samples.loc[samples["celltype"].astype(str) == "CD14", "sample"].astype(str).tolist()
if not cd14_samples:
    raise SystemExit("no CD14 samples found")
if len(cd14_samples) != len(set(cd14_samples)):
    raise SystemExit("duplicate CD14 sample names in annotation")

count_header = pd.read_csv(counts_path, nrows=0).columns.tolist()
if not count_header:
    raise SystemExit("empty count matrix header")
gene_col = count_header[0]
missing = [s for s in cd14_samples if s not in count_header]
if missing:
    raise SystemExit("CD14 samples missing from count matrix: " + ",".join(missing[:10]))

counts = pd.read_csv(counts_path, usecols=[gene_col] + cd14_samples)
counts = counts.rename(columns={gene_col: "Geneid"})
if counts["Geneid"].duplicated().any():
    raise SystemExit("duplicate gene IDs in count matrix")
for s in cd14_samples:
    counts[s] = pd.to_numeric(counts[s], errors="raise")
counts["total_cd14"] = counts[cd14_samples].sum(axis=1)
counts["mean_expression"] = counts[cd14_samples].mean(axis=1)

meta = pd.read_csv(meta_path, usecols=["Geneid", "Length", "gene_biotype"])
if meta["Geneid"].duplicated().any():
    raise SystemExit("duplicate gene IDs in gene metadata")
meta["Length"] = pd.to_numeric(meta["Length"], errors="raise")

merged = counts.merge(meta, on="Geneid", how="inner", validate="one_to_one")
protein = merged[merged["gene_biotype"].astype(str) == "protein_coding"].copy()
expressed = protein[(protein["total_cd14"] >= 10) & protein["Length"].notna() & protein["mean_expression"].notna()].copy()
if len(expressed) < 2:
    raise SystemExit("fewer than two expressed protein-coding genes")

corr = expressed["Length"].corr(expressed["mean_expression"], method="pearson")
if pd.isna(corr):
    raise SystemExit("Pearson correlation is NaN")

rows = [
    ("pearson_correlation", format(float(corr), ".17g")),
    ("cd14_sample_count", str(len(cd14_samples))),
    ("count_gene_rows", str(len(counts))),
    ("metadata_gene_rows", str(len(meta))),
    ("matched_gene_rows", str(len(merged))),
    ("protein_coding_gene_rows", str(len(protein))),
    ("expressed_protein_coding_gene_rows", str(len(expressed))),
    ("expression_filter", "total_cd14_counts_ge_10"),
    ("expression_summary", "mean_across_cd14_samples"),
    ("correlation_method", "pearson_pandas_series_corr"),
]
with open(out_path, "w", encoding="utf-8") as out:
    out.write("metric\tvalue\n")
    for key, value in rows:
        out.write(f"{key}\t{value}\n")
