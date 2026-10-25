#!/usr/bin/env python
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pydeseq2
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats


ROOT = Path("/workspace")
FINAL = ROOT / "final_answer"
TRACE = ROOT / "run_trace"

COUNT_FILES = [
    ("SRR5085167", "reference", ROOT / "data/inputs/counts_from_reference_condition/srr5085167_counts_table/srr5085167_counts_table.dat"),
    ("SRR5085168", "reference", ROOT / "data/inputs/counts_from_reference_condition/srr5085168_counts_table/srr5085168_counts_table.dat"),
    ("SRR5085169", "changed", ROOT / "data/inputs/counts_from_changed_condition/srr5085169_counts_table/srr5085169_counts_table.dat"),
    ("SRR5085170", "changed", ROOT / "data/inputs/counts_from_changed_condition/srr5085170_counts_table/srr5085170_counts_table.dat"),
]


def read_count_table(sample_id: str, path: Path) -> pd.Series:
    df = pd.read_csv(path, sep="\t", dtype={"Geneid": "string"})
    if list(df.columns) != ["Geneid", sample_id]:
        raise ValueError(f"{path} columns are {list(df.columns)}, expected ['Geneid', '{sample_id}']")
    if df["Geneid"].duplicated().any():
        dupes = df.loc[df["Geneid"].duplicated(), "Geneid"].head().tolist()
        raise ValueError(f"{path} contains duplicate gene IDs, e.g. {dupes}")
    counts = pd.to_numeric(df[sample_id], errors="raise")
    if (counts < 0).any() or not np.all(np.equal(counts, np.floor(counts))):
        raise ValueError(f"{path} contains non-integer or negative counts")
    return pd.Series(counts.astype(int).to_numpy(), index=df["Geneid"].astype(str), name=sample_id)


def benjamini_hochberg(pvalues: np.ndarray) -> np.ndarray:
    pvalues = np.asarray(pvalues, dtype=float)
    if np.any(~np.isfinite(pvalues)) or np.any((pvalues < 0) | (pvalues > 1)):
        raise ValueError("All p-values must be finite and in [0, 1] before BH adjustment")
    n = pvalues.size
    order = np.argsort(pvalues, kind="mergesort")
    ranked = pvalues[order] * n / np.arange(1, n + 1)
    adjusted_ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = np.minimum(adjusted_ranked, 1.0)
    return adjusted


def main() -> None:
    FINAL.mkdir(exist_ok=True)
    TRACE.mkdir(exist_ok=True)

    series = [read_count_table(sample, path) for sample, _, path in COUNT_FILES]
    count_matrix_genes = pd.concat(series, axis=1, join="inner")
    if count_matrix_genes.shape[0] != len(series[0]):
        raise ValueError("Count table gene IDs do not match exactly across samples")
    if count_matrix_genes.isna().any().any():
        raise ValueError("Merged count matrix contains missing values")

    keep = (count_matrix_genes >= 10).sum(axis=1) >= 2
    filtered_genes = count_matrix_genes.index[keep]
    filtered_counts = count_matrix_genes.loc[filtered_genes]
    if filtered_counts.empty:
        raise ValueError("No genes passed the count filter")

    counts_for_deseq = filtered_counts.T
    metadata = pd.DataFrame(
        {"condition": [condition for _, condition, _ in COUNT_FILES]},
        index=[sample for sample, _, _ in COUNT_FILES],
    )
    metadata["condition"] = pd.Categorical(
        metadata["condition"], categories=["reference", "changed"]
    )

    dds = DeseqDataSet(
        counts=counts_for_deseq,
        metadata=metadata,
        design="~condition",
        ref_level=["condition", "reference"],
        refit_cooks=False,
        n_cpus=1,
        quiet=True,
    )
    dds.deseq2()

    stats = DeseqStats(
        dds,
        contrast=["condition", "changed", "reference"],
        cooks_filter=False,
        independent_filter=False,
        n_cpus=1,
        quiet=True,
    )
    stats.summary()
    results = stats.results_df.copy()
    required_cols = {"log2FoldChange", "pvalue"}
    if not required_cols.issubset(results.columns):
        raise ValueError(f"PyDESeq2 result columns missing {required_cols - set(results.columns)}")

    results = results.reindex(filtered_genes)
    out = pd.DataFrame(
        {
            "gene_id": filtered_genes,
            "log2_fold_change": results["log2FoldChange"].to_numpy(dtype=float),
            "p_value": results["pvalue"].to_numpy(dtype=float),
        }
    )
    if np.any(~np.isfinite(out["log2_fold_change"].to_numpy(dtype=float))):
        bad = out.loc[~np.isfinite(out["log2_fold_change"].to_numpy(dtype=float)), "gene_id"].head().tolist()
        raise ValueError(f"Non-finite log2 fold changes for genes: {bad}")
    if np.any(~np.isfinite(out["p_value"].to_numpy(dtype=float))):
        bad = out.loc[~np.isfinite(out["p_value"].to_numpy(dtype=float)), "gene_id"].head().tolist()
        raise ValueError(f"Non-finite p-values for genes: {bad}")
    if np.any((out["p_value"] < 0) | (out["p_value"] > 1)):
        raise ValueError("P-values outside [0, 1]")
    out["fdr"] = benjamini_hochberg(out["p_value"].to_numpy(dtype=float))
    if np.any(~np.isfinite(out["fdr"].to_numpy(dtype=float))) or np.any((out["fdr"] < 0) | (out["fdr"] > 1)):
        raise ValueError("FDR values are not finite values in [0, 1]")

    out.to_csv(FINAL / "differential_expression.tsv", sep="\t", index=False, float_format="%.12g")
    with open(FINAL / "method.json", "w", encoding="utf-8") as handle:
        json.dump({"method": "DESeq2"}, handle, separators=(",", ":"))
        handle.write("\n")

    log_lines = [
        "Differential expression execution log",
        f"method: DESeq2 via PyDESeq2 {pydeseq2.__version__}",
        "contrast: changed vs reference",
        "log2 fold-change sign: positive means higher expression in changed condition",
        "count filter: retained genes with >=10 raw counts in at least 2 of 4 samples",
        f"input genes: {count_matrix_genes.shape[0]}",
        f"retained/tested genes: {out.shape[0]}",
        f"output rows: {out.shape[0]}",
        f"minimum raw p-value: {out['p_value'].min():.12g}",
        f"maximum raw p-value: {out['p_value'].max():.12g}",
        f"minimum BH FDR: {out['fdr'].min():.12g}",
        f"maximum BH FDR: {out['fdr'].max():.12g}",
    ]
    (TRACE / "execution_log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
