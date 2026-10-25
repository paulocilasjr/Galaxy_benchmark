import json
import math
import re
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scipy.sparse as sp


ROOT = Path("/workspace")
INPUT = ROOT / "data/inputs/source_anndata_file/Source%20AnnData%20file.h5ad"
FINAL = ROOT / "final_answer"
TRACE = ROOT / "run_trace"


def final_sample_name(individual, cell_type):
    return f"{individual}_{cell_type}".replace(" ", "_").replace("-", "_")


def r_safe_name(value):
    value = re.sub(r"[^0-9A-Za-z_]", "_", str(value))
    value = re.sub(r"_+", "_", value).strip("_")
    if not value or not re.match(r"^[A-Za-z]", value):
        value = "S_" + value
    return value


def as_integer_counts(matrix):
    arr = np.asarray(matrix).ravel()
    if np.any(~np.isfinite(arr)):
        raise ValueError("counts contain non-finite values")
    if np.any(arr < 0):
        raise ValueError("counts contain negative values")
    rounded = np.rint(arr)
    if not np.allclose(arr, rounded, rtol=0, atol=1e-5):
        raise ValueError("counts layer contains non-integer values")
    return rounded.astype(np.int64)


def main():
    FINAL.mkdir(exist_ok=True)
    TRACE.mkdir(exist_ok=True)

    adata = ad.read_h5ad(INPUT)
    required_obs = {"individual", "cell_type", "disease"}
    missing_obs = sorted(required_obs.difference(adata.obs.columns))
    if missing_obs:
        raise ValueError(f"missing obs columns: {missing_obs}")
    if "counts" not in adata.layers:
        raise ValueError("missing AnnData layer: counts")
    if adata.var_names.name != "gene_symbol":
        raise ValueError(f"expected var index named gene_symbol, found {adata.var_names.name!r}")
    if not adata.var_names.is_unique:
        raise ValueError("gene_symbol values are not unique")

    counts = adata.layers["counts"]
    if not sp.issparse(counts):
        counts = sp.csr_matrix(counts)
    else:
        counts = counts.tocsr()

    obs = adata.obs[["individual", "cell_type", "disease"]].astype(str).copy()
    obs["_row"] = np.arange(obs.shape[0])

    grouped = (
        obs.groupby(["individual", "cell_type"], sort=True, observed=True)
        .agg(n_cells=("_row", "size"), rows=("_row", list), disease=("disease", lambda x: sorted(set(x))))
        .reset_index()
    )
    grouped = grouped[grouped["n_cells"] >= 10].reset_index(drop=True)
    if grouped.empty:
        raise ValueError("no individual-cell_type combinations retained")
    mixed = grouped[grouped["disease"].map(len) != 1]
    if not mixed.empty:
        raise ValueError("at least one retained individual-cell_type combination has mixed disease labels")

    sample_records = []
    pseudobulk_cols = []
    used_final_names = set()
    used_edge_names = set()
    for _, row in grouped.iterrows():
        summed = counts[np.asarray(row["rows"], dtype=np.int64), :].sum(axis=0)
        vec = as_integer_counts(summed)
        final_name = final_sample_name(row["individual"], row["cell_type"])
        edge_name = r_safe_name(final_name)
        if final_name in used_final_names:
            raise ValueError(f"duplicate final sample name after sanitizing spaces/hyphens: {final_name}")
        if edge_name in used_edge_names:
            raise ValueError(f"duplicate edgeR sample name after R-safe sanitizing: {edge_name}")
        used_final_names.add(final_name)
        used_edge_names.add(edge_name)
        pseudobulk_cols.append(vec)
        sample_records.append(
            {
                "sample": final_name,
                "edger_sample": edge_name,
                "individual": row["individual"],
                "cell_type": row["cell_type"],
                "cell_type_edger": r_safe_name(row["cell_type"]),
                "disease": row["disease"][0],
                "disease_edger": "COVID_19" if row["disease"][0] == "COVID-19" else r_safe_name(row["disease"][0]),
                "n_cells": int(row["n_cells"]),
            }
        )

    mat = np.vstack(pseudobulk_cols).T
    sample_totals = mat.sum(axis=0).astype(np.float64)
    if np.any(sample_totals <= 0):
        raise ValueError("at least one retained pseudobulk sample has zero total counts")
    n_samples = mat.shape[1]
    median_total = float(np.median(sample_totals))
    min_samples = int(math.ceil(10 + 0.7 * (n_samples - 10)))
    cpm_threshold = 10.0 / median_total * 1_000_000.0

    cpm = mat / sample_totals.reshape(1, -1) * 1_000_000.0
    keep = ((cpm >= cpm_threshold).sum(axis=1) >= min_samples) & (mat.sum(axis=1) >= 1000)
    if not np.any(keep):
        raise ValueError("gene filter retained no genes")

    genes = np.asarray(adata.var_names)[keep]
    kept_mat = mat[keep, :]
    samples = pd.DataFrame(sample_records)

    final_df = pd.DataFrame(kept_mat, columns=samples["sample"].tolist())
    final_df.insert(0, "gene", genes)
    final_df.to_csv(FINAL / "pseudobulk_counts.tsv", sep="\t", index=False)

    edger_df = pd.DataFrame(kept_mat, columns=samples["edger_sample"].tolist())
    edger_df.insert(0, "GeneID", genes)
    edger_df.to_csv(TRACE / "edger_counts.tsv", sep="\t", index=False)

    factor = samples[["edger_sample", "disease_edger", "cell_type_edger"]].rename(
        columns={"edger_sample": "Sample", "disease_edger": "disease", "cell_type_edger": "cell_type"}
    )
    factor.to_csv(TRACE / "edger_factors.tsv", sep="\t", index=False)
    pd.DataFrame({"Contrast": ["normal-COVID_19"]}).to_csv(TRACE / "edger_contrasts.tsv", sep="\t", index=False)
    samples.to_csv(TRACE / "pseudobulk_samples.tsv", sep="\t", index=False)

    summary = {
        "input_shape": [int(adata.n_obs), int(adata.n_vars)],
        "retained_samples": int(n_samples),
        "retained_genes": int(kept_mat.shape[0]),
        "median_total_counts": median_total,
        "min_samples_S": min_samples,
        "cpm_threshold": cpm_threshold,
        "sample_total_min": int(sample_totals.min()),
        "sample_total_max": int(sample_totals.max()),
        "disease_counts": samples["disease"].value_counts().to_dict(),
        "cell_type_counts": samples["cell_type"].value_counts().to_dict(),
    }
    (TRACE / "pseudobulk_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
