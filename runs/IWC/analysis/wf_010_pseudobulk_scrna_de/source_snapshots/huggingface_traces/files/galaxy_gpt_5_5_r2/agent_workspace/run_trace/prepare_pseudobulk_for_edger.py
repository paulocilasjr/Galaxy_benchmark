#!/usr/bin/env python
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path("/workspace")
TRACE = ROOT / "run_trace"
DOWNLOADS = TRACE / "galaxy_downloads"
FINAL = ROOT / "final_answer"


def sanitize(value):
    return str(value).replace(" ", "_").replace("-", "_")


def main():
    FINAL.mkdir(exist_ok=True)

    counts_path = DOWNLOADS / "pseudobulk_count_matrix.raw.tsv"
    sample_path = DOWNLOADS / "sample_metadata.raw.tsv"

    counts = pd.read_csv(counts_path, sep="\t", index_col=0)
    samples = pd.read_csv(sample_path, sep="\t", index_col=0)

    # Decoupler writes summed counts as floating-point strings; all are integer-valued.
    numeric = counts.apply(pd.to_numeric)
    rounded = np.rint(numeric.to_numpy()).astype(np.int64)
    if np.any(rounded < 0):
        raise ValueError("Negative pseudobulk counts found")
    if not np.allclose(numeric.to_numpy(), rounded):
        raise ValueError("Non-integer-valued pseudobulk counts found")
    counts = pd.DataFrame(rounded, index=counts.index, columns=counts.columns)

    if list(counts.columns) != list(samples.index):
        raise ValueError("Count matrix columns do not match sample metadata rows")

    expected_names = [
        f"{sanitize(row.individual)}_{sanitize(row.cell_type)}"
        for row in samples.itertuples()
    ]
    if expected_names != list(counts.columns):
        raise ValueError("Pseudobulk sample names do not match requested naming rule")

    totals = counts.sum(axis=0)
    n_samples = counts.shape[1]
    median_total = float(np.median(totals.to_numpy()))
    min_samples = int(math.ceil(10 + 0.7 * (n_samples - 10)))
    cpm_threshold = 10.0 / median_total * 1_000_000.0

    cpm = counts.div(totals, axis=1) * 1_000_000.0
    keep = ((cpm >= cpm_threshold).sum(axis=1) >= min_samples) & (
        counts.sum(axis=1) >= 1000
    )
    filtered = counts.loc[keep].copy()

    final_counts = filtered.reset_index(names="gene")
    final_counts.to_csv(FINAL / "pseudobulk_counts.tsv", sep="\t", index=False)
    final_counts.to_csv(TRACE / "edger_counts.tsv", sep="\t", index=False)

    factors = pd.DataFrame(
        {
            "Sample": counts.columns,
            "disease": samples["disease"].map({"normal": "normal", "COVID-19": "COVID_19"}).values,
            "cell_type": samples["cell_type"].map(sanitize).values,
        }
    )
    if factors["disease"].isna().any():
        raise ValueError("Unexpected disease label in sample metadata")
    factors.to_csv(TRACE / "edger_factors.tsv", sep="\t", index=False)

    summary = {
        "source_matrix_genes": int(counts.shape[0]),
        "retained_samples": int(n_samples),
        "median_total_counts_M": median_total,
        "min_samples_S": min_samples,
        "cpm_threshold": cpm_threshold,
        "retained_genes": int(filtered.shape[0]),
        "total_counts_match_metadata": bool(
            np.allclose(totals.to_numpy(), samples["psbulk_counts"].astype(float).to_numpy())
        ),
    }
    (TRACE / "pseudobulk_filter_summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
