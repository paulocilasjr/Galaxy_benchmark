import sys
import pandas as pd

counts_path, meta_path, sample_path = sys.argv[1:4]
celltypes = ["CD4", "CD8", "CD14", "CD19"]

meta = pd.read_csv(meta_path, index_col=0)
counts = pd.read_csv(counts_path, index_col=0)
samples = pd.read_csv(sample_path)

required_meta = {"Length", "gene_biotype"}
missing_meta = required_meta - set(meta.columns)
if missing_meta:
    raise SystemExit(f"Missing metadata columns: {sorted(missing_meta)}")
required_sample = {"sample", "celltype"}
missing_sample = required_sample - set(samples.columns)
if missing_sample:
    raise SystemExit(f"Missing sample columns: {sorted(missing_sample)}")

meta = meta[meta["gene_biotype"].astype(str).eq("protein_coding")].copy()
meta["Length"] = pd.to_numeric(meta["Length"], errors="coerce")
common_genes = meta.index.intersection(counts.index)
if common_genes.empty:
    raise SystemExit("No protein-coding genes shared between metadata and counts")

lengths = meta.loc[common_genes, "Length"]
results = []
for celltype in celltypes:
    annotated = samples.loc[samples["celltype"].astype(str).eq(celltype), "sample"].astype(str).tolist()
    sample_cols = [s for s in annotated if s in counts.columns]
    if not sample_cols:
        raise SystemExit(f"No count columns found for {celltype}")
    expr = counts.loc[common_genes, sample_cols].apply(pd.to_numeric, errors="coerce")
    avg_expr = expr.mean(axis=1, skipna=True)
    paired = pd.concat([lengths.rename("Length"), avg_expr.rename("average_expression")], axis=1).dropna()
    corr = paired["Length"].corr(paired["average_expression"], method="pearson")
    if pd.isna(corr):
        raise SystemExit(f"Pearson correlation is NA for {celltype}")
    results.append({
        "celltype": celltype,
        "n_samples": len(sample_cols),
        "n_genes": int(paired.shape[0]),
        "pearson": float(corr),
        "abs_pearson": float(abs(corr)),
    })

weakest = min(results, key=lambda row: (row["abs_pearson"], celltypes.index(row["celltype"])))
for row in results:
    row["weakest"] = "yes" if row["celltype"] == weakest["celltype"] else "no"

out = pd.DataFrame(results, columns=["celltype", "n_samples", "n_genes", "pearson", "abs_pearson", "weakest"])
out.to_csv("correlations.tsv", sep="\t", index=False, float_format="%.17g")
with open("answer.txt", "w") as handle:
    handle.write(weakest["celltype"] + "\n")
