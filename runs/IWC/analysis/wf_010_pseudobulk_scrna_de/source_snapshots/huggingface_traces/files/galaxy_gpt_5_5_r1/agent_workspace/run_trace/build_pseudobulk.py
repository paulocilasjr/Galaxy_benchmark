#!/usr/bin/env python3
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import h5py
import numpy as np
import pandas as pd


ROOT = Path("/workspace")
H5AD = ROOT / "data/inputs/source_anndata_file/Source%20AnnData%20file.h5ad"
FINAL = ROOT / "final_answer"
TRACE = ROOT / "run_trace"


def decode_array(arr):
    return [x.decode("utf-8") if isinstance(x, bytes) else str(x) for x in arr]


def read_categorical(f, key):
    group = f[f"obs/{key}"]
    categories = decode_array(group["categories"][()])
    codes = group["codes"][()]
    return np.array([categories[int(code)] if code >= 0 else "" for code in codes], dtype=object)


def final_sample_name(individual, cell_type):
    return f"{individual}_{cell_type}".replace(" ", "_").replace("-", "_")


def edge_sample_name(name):
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", name)
    if not re.match(r"^[A-Za-z]", cleaned):
        cleaned = "S_" + cleaned
    return cleaned


def make_unique(names):
    seen = Counter()
    out = []
    for name in names:
        seen[name] += 1
        out.append(name if seen[name] == 1 else f"{name}_{seen[name]}")
    return out


def main():
    FINAL.mkdir(exist_ok=True)
    TRACE.mkdir(exist_ok=True)

    with h5py.File(H5AD, "r") as f:
        individuals = read_categorical(f, "individual")
        diseases = read_categorical(f, "disease")
        cell_types = read_categorical(f, "cell_type")
        gene_symbols = decode_array(f["var/gene_symbol"][()])

        counts_group = f["layers/counts"]
        data = counts_group["data"][()]
        indices = counts_group["indices"][()]
        indptr = counts_group["indptr"][()]
        shape = tuple(int(x) for x in counts_group.attrs["shape"])

    if len(set(gene_symbols)) != len(gene_symbols):
        raise ValueError("gene_symbol values are not unique")
    if shape != (len(individuals), len(gene_symbols)):
        raise ValueError(f"counts layer shape {shape} does not match obs/var lengths")
    if np.any(data < 0):
        raise ValueError("counts layer contains negative values")
    rounded = np.rint(data)
    if not np.allclose(data, rounded, rtol=0, atol=1e-6):
        raise ValueError("counts layer contains non-integer values")
    data = rounded.astype(np.int64, copy=False)

    combo_counts = Counter(zip(individuals, cell_types))
    retained_combos = sorted([combo for combo, n in combo_counts.items() if n >= 10])
    combo_to_col = {combo: i for i, combo in enumerate(retained_combos)}
    group_for_row = np.array([combo_to_col.get((ind, ct), -1) for ind, ct in zip(individuals, cell_types)])

    pb = np.zeros((len(retained_combos), len(gene_symbols)), dtype=np.int64)
    for row_idx, group_idx in enumerate(group_for_row):
        if group_idx < 0:
            continue
        start, end = int(indptr[row_idx]), int(indptr[row_idx + 1])
        pb[group_idx, indices[start:end]] += data[start:end]

    sample_totals = pb.sum(axis=1)
    if np.any(sample_totals <= 0):
        raise ValueError("retained pseudobulk sample with zero total count")
    n_samples = pb.shape[0]
    median_total = float(np.median(sample_totals))
    sample_required = int(math.ceil(10 + 0.7 * (n_samples - 10)))
    cpm_threshold = 10.0 / median_total * 1_000_000.0
    cpm = pb / sample_totals[:, None] * 1_000_000.0
    keep_genes = (cpm >= cpm_threshold).sum(axis=0) >= sample_required
    keep_genes &= pb.sum(axis=0) >= 1000

    kept_idx = np.flatnonzero(keep_genes)
    kept_genes = [gene_symbols[i] for i in kept_idx]
    final_names = make_unique([final_sample_name(ind, ct) for ind, ct in retained_combos])
    edge_names = make_unique([edge_sample_name(name) for name in final_names])
    pb_keep = pb[:, kept_idx].T

    final_counts = pd.DataFrame(pb_keep, columns=final_names)
    final_counts.insert(0, "gene", kept_genes)
    final_counts.to_csv(FINAL / "pseudobulk_counts.tsv", sep="\t", index=False)

    edge_counts = pd.DataFrame(pb_keep, columns=edge_names)
    edge_counts.insert(0, "gene", kept_genes)
    edge_counts.to_csv(TRACE / "edger_counts.tsv", sep="\t", index=False)

    disease_by_sample = []
    cell_type_by_sample = []
    for individual, cell_type in retained_combos:
        mask = (individuals == individual) & (cell_types == cell_type)
        observed_diseases = sorted(set(diseases[mask]))
        if len(observed_diseases) != 1:
            raise ValueError(f"multiple diseases for {individual}/{cell_type}: {observed_diseases}")
        disease_by_sample.append(observed_diseases[0].replace("-", "_"))
        cell_type_by_sample.append(edge_sample_name(cell_type))

    factors = pd.DataFrame(
        {
            "Sample": edge_names,
            "disease": disease_by_sample,
            "cell_type": cell_type_by_sample,
        }
    )
    factors.to_csv(TRACE / "edger_factors.tsv", sep="\t", index=False)

    summary = {
        "input_h5ad": str(H5AD),
        "n_cells": int(shape[0]),
        "n_genes_input": int(shape[1]),
        "n_retained_samples": int(n_samples),
        "n_retained_genes": int(len(kept_genes)),
        "median_total_counts": median_total,
        "sample_required_S": sample_required,
        "cpm_threshold": cpm_threshold,
        "retained_samples": [
            {
                "final_name": final_name,
                "edgeR_name": edge_name,
                "individual": individual,
                "cell_type": cell_type,
                "disease": disease,
                "n_cells": int(combo_counts[(individual, cell_type)]),
                "total_counts": int(total),
            }
            for (individual, cell_type), final_name, edge_name, disease, total in zip(
                retained_combos, final_names, edge_names, disease_by_sample, sample_totals
            )
        ],
    }
    (TRACE / "pseudobulk_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    with (TRACE / "execution_log.txt").open("a", encoding="utf-8") as log:
        log.write(
            "Built pseudobulk from h5ad layers/counts; retained "
            f"{n_samples} samples and {len(kept_genes)} genes using global CPM/count filter.\\n"
        )


if __name__ == "__main__":
    main()
