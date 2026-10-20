import json
import os
import sys
import warnings

import numpy as np
import pandas as pd
import pydeseq2
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

counts_path, metadata_path, gene_meta_path, results_path, answer_path, info_path = sys.argv[1:]

counts_gene_by_sample = pd.read_csv(counts_path, index_col=0)
metadata = pd.read_csv(metadata_path)
gene_meta = pd.read_csv(gene_meta_path, index_col=0)

if not counts_gene_by_sample.index.is_unique:
    raise ValueError("Gene IDs in count matrix are not unique")
if not counts_gene_by_sample.columns.is_unique:
    raise ValueError("Sample IDs in count matrix are not unique")
if "sample" not in metadata.columns or "sex" not in metadata.columns or "batch" not in metadata.columns:
    raise ValueError("Metadata must contain sample, sex, and batch columns")
metadata = metadata.set_index("sample", drop=False)
if not metadata.index.is_unique:
    raise ValueError("Sample IDs in metadata are not unique")

missing_meta = sorted(set(counts_gene_by_sample.columns) - set(metadata.index))
missing_counts = sorted(set(metadata.index) - set(counts_gene_by_sample.columns))
if missing_meta or missing_counts:
    raise ValueError({"missing_meta": missing_meta[:10], "missing_counts": missing_counts[:10]})

metadata = metadata.loc[counts_gene_by_sample.columns].copy()
if set(metadata["sex"].astype(str).unique()) != {"F", "M"}:
    raise ValueError("Sex levels are not exactly F and M")
metadata["sex"] = pd.Categorical(metadata["sex"].astype(str), categories=["F", "M"])
batch_values = metadata["batch"].astype(str)
def batch_key(x):
    try:
        return (0, int(x))
    except ValueError:
        return (1, x)
batch_levels = sorted(batch_values.unique(), key=batch_key)
metadata["batch"] = pd.Categorical(batch_values, categories=batch_levels)

counts = counts_gene_by_sample.T
# PyDESeq2 validates non-negative integer-valued counts and casts to int internally.
# Check integer-valued input explicitly so no lossy correction is hidden.
counts_numeric = counts.apply(pd.to_numeric)
arr = counts_numeric.to_numpy(dtype=np.float64, copy=False)
if not np.isfinite(arr).all():
    raise ValueError("Counts contain non-finite values")
if (arr < 0).any():
    raise ValueError("Counts contain negative values")
if not np.allclose(arr, np.rint(arr), rtol=0, atol=1e-8):
    raise ValueError("Counts are not integer-valued")
counts_numeric = counts_numeric.astype(np.int64)

if "FAM138A" not in counts_numeric.columns:
    raise ValueError("FAM138A is absent from the count matrix")
if "FAM138A" not in gene_meta.index:
    warnings.warn("FAM138A is absent from gene metadata", UserWarning)

slots = os.environ.get("GALAXY_SLOTS")
try:
    n_cpus = max(1, int(slots)) if slots else None
except ValueError:
    n_cpus = None

dds = DeseqDataSet(
    counts=counts_numeric,
    metadata=metadata[["batch", "sex"]],
    design="~ batch + sex",
    n_cpus=n_cpus,
    quiet=False,
)
dds.deseq2()
stat_res = DeseqStats(
    dds,
    contrast=["sex", "M", "F"],
    n_cpus=n_cpus,
    quiet=False,
)
stat_res.summary()
coeffs = [str(c) for c in stat_res.LFC.columns]
preferred = ["sex[T.M]", "sex_M_vs_F", "sex_M_vs_F"]
coeff = None
for candidate in preferred:
    if candidate in coeffs:
        coeff = candidate
        break
if coeff is None:
    candidates = [c for c in coeffs if c != "Intercept" and "sex" in c and "M" in c]
    if len(candidates) == 1:
        coeff = candidates[0]
if coeff is None:
    raise ValueError({"message": "Could not identify sex M vs F coefficient", "coefficients": coeffs})
stat_res.lfc_shrink(coeff=coeff)

res = stat_res.results_df.copy()
res.index.name = "gene"
res["pass_abs_lfc_gt_0_5_baseMean_gt_10"] = (res["log2FoldChange"].abs() > 0.5) & (res["baseMean"] > 10)
res.to_csv(results_path, sep="\t")

target = res.loc["FAM138A"]
with open(answer_path, "w") as out:
    out.write(format(float(target["log2FoldChange"]), ".15g") + "\n")

info = {
    "pydeseq2_version": pydeseq2.__version__,
    "design": "~ batch + sex",
    "contrast": ["sex", "M", "F"],
    "sex_categories": list(metadata["sex"].cat.categories),
    "batch_categories": list(metadata["batch"].cat.categories),
    "lfc_shrink_coeff": coeff,
    "lfc_coefficients": coeffs,
    "n_samples": int(counts_numeric.shape[0]),
    "n_genes": int(counts_numeric.shape[1]),
    "target": {
        "gene": "FAM138A",
        "baseMean": None if pd.isna(target["baseMean"]) else float(target["baseMean"]),
        "log2FoldChange": None if pd.isna(target["log2FoldChange"]) else float(target["log2FoldChange"]),
        "lfcSE": None if pd.isna(target["lfcSE"]) else float(target["lfcSE"]),
        "stat": None if pd.isna(target["stat"]) else float(target["stat"]),
        "pvalue": None if pd.isna(target["pvalue"]) else float(target["pvalue"]),
        "padj": None if pd.isna(target["padj"]) else float(target["padj"]),
        "passes_filter": bool(target["pass_abs_lfc_gt_0_5_baseMean_gt_10"]),
    },
}
with open(info_path, "w") as out:
    json.dump(info, out, indent=2, sort_keys=True)
