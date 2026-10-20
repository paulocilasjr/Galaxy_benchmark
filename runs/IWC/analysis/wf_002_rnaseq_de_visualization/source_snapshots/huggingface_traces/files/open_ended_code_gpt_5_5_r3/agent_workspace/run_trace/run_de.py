import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pydeseq2
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats


ROOT = Path("/workspace")
OUT_DIR = ROOT / "final_answer"
TRACE_DIR = ROOT / "run_trace"

COUNT_FILES = [
    ("SRR5085169", "changed", ROOT / "data/inputs/counts_from_changed_condition/srr5085169_counts_table/srr5085169_counts_table.dat"),
    ("SRR5085170", "changed", ROOT / "data/inputs/counts_from_changed_condition/srr5085170_counts_table/srr5085170_counts_table.dat"),
    ("SRR5085167", "reference", ROOT / "data/inputs/counts_from_reference_condition/srr5085167_counts_table/srr5085167_counts_table.dat"),
    ("SRR5085168", "reference", ROOT / "data/inputs/counts_from_reference_condition/srr5085168_counts_table/srr5085168_counts_table.dat"),
]


def read_count_table(sample_id, path):
    df = pd.read_csv(path, sep="\t", dtype={"Geneid": str})
    if df.columns.tolist() != ["Geneid", sample_id]:
        raise ValueError(f"Unexpected columns in {path}: {df.columns.tolist()}")
    if df["Geneid"].duplicated().any():
        raise ValueError(f"Duplicate gene IDs in {path}")
    if df[sample_id].isna().any() or (df[sample_id] < 0).any():
        raise ValueError(f"Invalid counts in {path}")
    df[sample_id] = df[sample_id].astype(int)
    return df


def bh_adjust(p_values):
    p = np.asarray(p_values, dtype=float)
    if np.isnan(p).any() or np.any((p < 0) | (p > 1)):
        raise ValueError("Raw p-values must be finite values between 0 and 1")
    n = p.size
    order = np.argsort(p)
    ranked = p[order]
    adjusted_ranked = ranked * n / np.arange(1, n + 1)
    adjusted_ranked = np.minimum.accumulate(adjusted_ranked[::-1])[::-1]
    adjusted_ranked = np.clip(adjusted_ranked, 0, 1)
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = adjusted_ranked
    return adjusted


def main():
    TRACE_DIR.mkdir(exist_ok=True)
    OUT_DIR.mkdir(exist_ok=True)

    merged = None
    metadata_rows = []
    for sample_id, condition, path in COUNT_FILES:
        df = read_count_table(sample_id, path)
        merged = df if merged is None else merged.merge(df, on="Geneid", how="inner", validate="one_to_one")
        metadata_rows.append({"sample": sample_id, "condition": condition})

    expected_rows = [read_count_table(sample_id, path).shape[0] for sample_id, _, path in COUNT_FILES]
    if merged.shape[0] != min(expected_rows) or len(set(expected_rows)) != 1:
        raise ValueError("Count tables do not contain the same gene universe")

    sample_ids = [sample_id for sample_id, _, _ in COUNT_FILES]
    count_matrix_genes = merged.set_index("Geneid")[sample_ids]
    keep = (count_matrix_genes >= 10).sum(axis=1) >= 2
    filtered_genes = count_matrix_genes.index[keep]
    filtered_counts = count_matrix_genes.loc[filtered_genes]

    counts_for_deseq = filtered_counts.T
    metadata = pd.DataFrame(metadata_rows).set_index("sample").loc[sample_ids]
    metadata["condition"] = pd.Categorical(metadata["condition"], categories=["reference", "changed"])

    dds = DeseqDataSet(
        counts=counts_for_deseq,
        metadata=metadata,
        design="~condition",
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

    if not filtered_genes.equals(results.index):
        results = results.loc[filtered_genes]

    output = pd.DataFrame(
        {
            "gene_id": results.index.astype(str),
            "log2_fold_change": results["log2FoldChange"].astype(float).to_numpy(),
            "p_value": results["pvalue"].astype(float).to_numpy(),
        }
    )
    output["fdr"] = bh_adjust(output["p_value"].to_numpy())

    if not np.isfinite(output["log2_fold_change"]).all():
        raise ValueError("Non-finite log2 fold changes produced")
    for col in ["p_value", "fdr"]:
        vals = output[col].to_numpy(dtype=float)
        if np.isnan(vals).any() or np.any((vals < 0) | (vals > 1)):
            raise ValueError(f"{col} contains invalid values")

    output.to_csv(OUT_DIR / "differential_expression.tsv", sep="\t", index=False, float_format="%.17g")
    with open(OUT_DIR / "method.json", "w", encoding="utf-8") as handle:
        json.dump({"method": "DESeq2"}, handle, separators=(",", ":"))
        handle.write("\n")

    trace = {
        "method": "DESeq2",
        "pydeseq2_version": pydeseq2.__version__,
        "samples": metadata_rows,
        "input_genes_per_table": expected_rows,
        "merged_genes": int(merged.shape[0]),
        "retained_genes": int(output.shape[0]),
        "filter": "retained genes with at least 10 raw counts in at least two of the four samples",
        "contrast": "condition changed vs reference; positive log2 fold change means higher expression in changed",
        "fdr": "Benjamini-Hochberg adjustment computed over retained genes",
        "outputs": [
            str(OUT_DIR / "differential_expression.tsv"),
            str(OUT_DIR / "method.json"),
        ],
    }
    with open(TRACE_DIR / "execution_log.json", "w", encoding="utf-8") as handle:
        json.dump(trace, handle, indent=2)
        handle.write("\n")


if __name__ == "__main__":
    main()
