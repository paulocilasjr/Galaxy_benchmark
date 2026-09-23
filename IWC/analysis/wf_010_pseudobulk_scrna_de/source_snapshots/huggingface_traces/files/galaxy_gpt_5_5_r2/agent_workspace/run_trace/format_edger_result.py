import json
import math
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path("/workspace")
FINAL = ROOT / "final_answer"
TRACE = ROOT / "run_trace"


def bh_adjust(p_values):
    p = np.asarray(p_values, dtype=float)
    n = p.size
    order = np.argsort(p)
    ranked = p[order]
    adjusted = ranked * n / np.arange(1, n + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0.0, 1.0)
    out = np.empty_like(adjusted)
    out[order] = adjusted
    return out


def find_column(columns, patterns):
    for pat in patterns:
        regex = re.compile(pat, re.IGNORECASE)
        matches = [c for c in columns if regex.fullmatch(c) or regex.search(c)]
        if matches:
            return matches[0]
    raise ValueError(f"could not find any of columns matching {patterns}; available={list(columns)}")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: format_edger_result.py <downloaded-edgeR-tsv>")
    edge_path = Path(sys.argv[1])
    counts = pd.read_csv(FINAL / "pseudobulk_counts.tsv", sep="\t", usecols=["gene"])
    expected_genes = counts["gene"].astype(str)

    raw = pd.read_csv(edge_path, sep="\t")
    if raw.empty:
        raise ValueError("edgeR result is empty")
    gene_col = raw.columns[0]
    logfc_col = find_column(raw.columns, [r"logFC", r"log2.*fold", r"fold.*change"])
    p_col = find_column(raw.columns, [r"PValue", r"P\.Value", r"p[_ .-]?value"])

    res = raw[[gene_col, logfc_col, p_col]].copy()
    res.columns = ["gene", "log2_fold_change", "p_value"]
    res["gene"] = res["gene"].astype(str)
    res = res.set_index("gene", drop=False)
    if res.index.has_duplicates:
        raise ValueError("edgeR result contains duplicate gene identifiers")

    missing = sorted(set(expected_genes) - set(res.index))
    extra = sorted(set(res.index) - set(expected_genes))
    if missing or extra:
        raise ValueError(f"edgeR genes do not match filtered matrix; missing={len(missing)} extra={len(extra)}")

    res = res.loc[expected_genes].reset_index(drop=True)
    res["log2_fold_change"] = pd.to_numeric(res["log2_fold_change"], errors="coerce")
    res["p_value"] = pd.to_numeric(res["p_value"], errors="coerce")
    if not np.all(np.isfinite(res["log2_fold_change"])):
        raise ValueError("non-finite log2 fold change detected")
    if not np.all(np.isfinite(res["p_value"])):
        raise ValueError("non-finite p-value detected")
    if not np.all((res["p_value"] >= 0.0) & (res["p_value"] <= 1.0)):
        raise ValueError("p-values outside [0, 1] detected")
    res["fdr"] = bh_adjust(res["p_value"].to_numpy())
    if not np.all(np.isfinite(res["fdr"])):
        raise ValueError("non-finite FDR detected")

    res[["gene", "log2_fold_change", "p_value", "fdr"]].to_csv(
        FINAL / "differential_expression.tsv", sep="\t", index=False
    )
    (FINAL / "method.json").write_text(json.dumps({"method": "edgeR quasi-likelihood"}, indent=2) + "\n")


if __name__ == "__main__":
    main()
