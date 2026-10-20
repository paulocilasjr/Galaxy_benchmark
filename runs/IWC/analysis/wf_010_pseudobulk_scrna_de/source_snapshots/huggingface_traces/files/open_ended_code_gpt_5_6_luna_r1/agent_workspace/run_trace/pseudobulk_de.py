from __future__ import annotations

import json
import math
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats


WORKSPACE = Path("/workspace")
SOURCE = WORKSPACE / "data/inputs/source_anndata_file/Source%20AnnData%20file.h5ad"
FINAL = WORKSPACE / "final_answer"
TRACE = WORKSPACE / "run_trace"


def decode_array(values: np.ndarray) -> np.ndarray:
    return np.asarray(
        [value.decode() if isinstance(value, bytes) else str(value) for value in values],
        dtype=object,
    )


def clean_component(value: str) -> str:
    return value.replace(" ", "_").replace("-", "_")


def bh_adjust(p_values: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg adjustment over exactly the supplied p-values."""
    p_values = np.asarray(p_values, dtype=np.float64)
    if not np.all(np.isfinite(p_values)) or np.any((p_values < 0) | (p_values > 1)):
        raise ValueError("DE p-values are not all finite values in [0, 1].")
    # Compute explicitly rather than inheriting any result filtering from the DE package.
    order = np.argsort(p_values, kind="mergesort")
    ranked = p_values[order] * len(p_values) / np.arange(1, len(p_values) + 1)
    ranked = np.minimum.accumulate(ranked[::-1])[::-1]
    adjusted = np.empty_like(p_values)
    adjusted[order] = np.clip(ranked, 0.0, 1.0)
    return adjusted


def main() -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    TRACE.mkdir(parents=True, exist_ok=True)
    log_lines: list[str] = []

    with h5py.File(SOURCE, "r") as h5:
        n_cells, n_genes = h5["layers/counts/indptr"].shape[0] - 1, h5["var/gene_symbol"].shape[0]
        cell_type_categories = decode_array(h5["obs/cell_type/categories"][()])
        disease_categories = decode_array(h5["obs/disease/categories"][()])
        individual_categories = decode_array(h5["obs/individual/categories"][()])
        cell_type = cell_type_categories[h5["obs/cell_type/codes"][()]]
        disease = disease_categories[h5["obs/disease/codes"][()]]
        individual = individual_categories[h5["obs/individual/codes"][()]]
        gene_symbols = decode_array(h5["var/gene_symbol"][()])

        count_data_raw = h5["layers/counts/data"][()]
        count_indices = h5["layers/counts/indices"][()]
        count_indptr = h5["layers/counts/indptr"][()]

    if np.any(count_data_raw < 0) or not np.all(count_data_raw == np.floor(count_data_raw)):
        raise ValueError("The counts layer contains negative or noninteger values.")
    count_data = count_data_raw.astype(np.int64, copy=False)
    if len(np.unique(gene_symbols)) != len(gene_symbols):
        raise ValueError("gene_symbol is not unique; output row identifiers would be ambiguous.")

    counts = csr_matrix(
        (count_data, count_indices, count_indptr),
        shape=(n_cells, n_genes),
        dtype=np.int64,
    )
    cell_meta = pd.DataFrame(
        {"individual": individual, "cell_type": cell_type, "disease": disease}
    )
    cell_meta["combination"] = list(zip(cell_meta["individual"], cell_meta["cell_type"]))
    combination_counts = cell_meta.groupby("combination", sort=False, observed=True).size()
    retained_combinations = [
        combination for combination, n in combination_counts.items() if int(n) >= 10
    ]
    if not retained_combinations:
        raise ValueError("No individual-cell-type combination passed the cell-count filter.")

    pseudobulk = np.vstack(
        [
            np.asarray(
                counts[
                    (cell_meta["individual"].to_numpy() == combination[0])
                    & (cell_meta["cell_type"].to_numpy() == combination[1])
                ].sum(axis=0)
            ).ravel()
            for combination in retained_combinations
        ]
    ).astype(np.int64, copy=False)

    sample_names: list[str] = []
    sample_records: list[dict[str, str]] = []
    for combination in retained_combinations:
        individual_name, cell_type_name = combination
        sample_name = f"{clean_component(individual_name)}_{clean_component(cell_type_name)}"
        sample_names.append(sample_name)
        combination_mask = (cell_meta["individual"] == individual_name) & (
            cell_meta["cell_type"] == cell_type_name
        )
        disease_values = cell_meta.loc[
            combination_mask, "disease"
        ].unique()
        if len(disease_values) != 1:
            raise ValueError(f"Combination {combination!r} has multiple disease labels.")
        sample_records.append(
            {
                "individual": individual_name,
                "cell_type": cell_type_name,
                "disease": disease_values[0],
            }
        )
    if len(set(sample_names)) != len(sample_names):
        raise ValueError("Sample-name sanitization produced duplicate column names.")

    sample_metadata = pd.DataFrame(sample_records, index=sample_names)
    # Preserve the source's declared level order; COVID-19 is the reference level.
    sample_metadata["cell_type"] = pd.Categorical(
        sample_metadata["cell_type"], categories=list(cell_type_categories)
    )
    sample_metadata["disease"] = pd.Categorical(
        sample_metadata["disease"], categories=["COVID-19", "normal"]
    )
    if sample_metadata["disease"].isna().any() or sample_metadata["cell_type"].isna().any():
        raise ValueError("Pseudobulk metadata contains an unrecognized factor level.")

    sample_totals = pseudobulk.sum(axis=1, dtype=np.int64)
    if np.any(sample_totals <= 0):
        raise ValueError("A retained pseudobulk sample has no counts.")
    n_samples = pseudobulk.shape[0]
    median_total = float(np.median(sample_totals))
    min_samples = int(math.ceil(10 + 0.7 * (n_samples - 10)))
    cpm_threshold = 10.0 / median_total * 1_000_000.0
    cpm = pseudobulk.astype(np.float64) / sample_totals[:, None] * 1_000_000.0
    expressed_in_enough_samples = (cpm >= cpm_threshold).sum(axis=0) >= min_samples
    summed_count_filter = pseudobulk.sum(axis=0, dtype=np.int64) >= 1_000
    retained_gene_mask = expressed_in_enough_samples & summed_count_filter
    retained_genes = gene_symbols[retained_gene_mask]
    filtered_counts = pseudobulk[:, retained_gene_mask]
    if filtered_counts.shape[1] == 0:
        raise ValueError("No genes passed the requested expression filter.")

    pseudobulk_table = pd.DataFrame(
        filtered_counts.T,
        index=pd.Index(retained_genes, name="gene"),
        columns=sample_names,
    ).reset_index()
    if not np.issubdtype(pseudobulk_table.iloc[:, 1:].dtypes.iloc[0], np.integer):
        raise ValueError("Pseudobulk output counts are not integer-valued.")
    pseudobulk_table.to_csv(FINAL / "pseudobulk_counts.tsv", sep="\t", index=False)

    # PyDESeq2 implements the DESeq2 size-factor, dispersion, Wald-test pipeline.
    dds = DeseqDataSet(
        counts=pd.DataFrame(filtered_counts, index=sample_names, columns=retained_genes),
        metadata=sample_metadata,
        design="~ cell_type + disease",
        quiet=True,
        n_cpus=1,
        refit_cooks=False,
        low_memory=False,
    )
    dds.deseq2()
    stats = DeseqStats(
        dds,
        contrast=["disease", "normal", "COVID-19"],
        cooks_filter=False,
        independent_filter=False,
        quiet=True,
        n_cpus=1,
    )
    stats.summary()
    results = stats.results_df.reindex(retained_genes)
    log2_fold_change = results["log2FoldChange"].to_numpy(dtype=np.float64)
    p_values = results["pvalue"].to_numpy(dtype=np.float64)
    if not np.all(np.isfinite(log2_fold_change)):
        raise ValueError("DESeq2 returned a nonfinite log2 fold change.")
    if not np.all(np.isfinite(p_values)):
        raise ValueError("DESeq2 returned a nonfinite p-value.")
    if np.any((p_values < 0) | (p_values > 1)):
        raise ValueError("DESeq2 returned a p-value outside [0, 1].")
    fdr = bh_adjust(p_values)

    de_table = pd.DataFrame(
        {
            "gene": retained_genes,
            "log2_fold_change": log2_fold_change,
            "p_value": p_values,
            "fdr": fdr,
        }
    )
    de_table.to_csv(FINAL / "differential_expression.tsv", sep="\t", index=False)
    with (FINAL / "method.json").open("w", encoding="utf-8") as handle:
        json.dump({"method": "DESeq2"}, handle, separators=(",", ":"))
        handle.write("\n")

    log_lines.extend(
        [
            f"source={SOURCE}",
            f"input_cells={n_cells}; input_genes={n_genes}; nonzero_entries={counts.nnz}",
            f"retained_pseudobulk_samples={n_samples}; retained_combinations_with_at_least_10_cells={n_samples}",
            f"disease_samples=COVID-19:{int((sample_metadata['disease'] == 'COVID-19').sum())},normal:{int((sample_metadata['disease'] == 'normal').sum())}",
            f"sample_total_median={median_total:.1f}; min_samples={min_samples}; cpm_threshold={cpm_threshold:.12g}",
            f"retained_genes={filtered_counts.shape[1]}; summed_count_min={int(filtered_counts.sum(axis=0).min())}",
            "method=DESeq2 Wald test; design=~ cell_type + disease; contrast=normal minus COVID-19",
            "cooks_filter=False; independent_filter=False; LFC shrinkage not applied",
            f"de_rows={len(de_table)}; finite_lfc={bool(np.all(np.isfinite(log2_fold_change)))}; finite_p={bool(np.all(np.isfinite(p_values)))}; finite_fdr={bool(np.all(np.isfinite(fdr)))}",
            "outputs=final_answer/pseudobulk_counts.tsv,final_answer/differential_expression.tsv,final_answer/method.json",
        ]
    )
    (TRACE / "pseudobulk_de.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
