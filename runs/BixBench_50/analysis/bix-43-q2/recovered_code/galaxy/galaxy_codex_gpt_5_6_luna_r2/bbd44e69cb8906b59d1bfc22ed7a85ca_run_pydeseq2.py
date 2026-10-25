import os, sys
from pathlib import Path
import numpy as np
import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
counts_path, mapping_path, layout_path = sys.argv[1:4]
counts_raw = pd.read_csv(counts_path, index_col=0)
counts_raw.index = counts_raw.index.astype(str)
if counts_raw.index.has_duplicates: raise ValueError("Duplicate Ensembl identifiers in counts matrix")
counts = counts_raw.apply(pd.to_numeric, errors="raise")
if counts.shape[1] != 30: raise ValueError(f"Expected 30 count samples, found {counts.shape[1]}")
if (counts < 0).to_numpy().any(): raise ValueError("Counts must be non-negative")
if not np.equal(counts.to_numpy(), np.floor(counts.to_numpy())).all(): raise ValueError("Counts must be integer-valued")
counts = counts.astype("int64")
counts_prefiltered = counts.loc[(counts > 10).any(axis=1)].copy()
layout = pd.read_csv(layout_path, dtype=str)
if not {"SampleID","Group"}.issubset(layout.columns): raise ValueError("sample_layout.csv must contain SampleID and Group columns")
layout["count_id"] = layout["SampleID"].str.replace("-", "_", regex=False)
if layout["count_id"].duplicated().any(): raise ValueError("Duplicate count sample identifiers in sample layout")
if set(layout["count_id"]) != set(counts.columns): raise ValueError("Sample IDs in sample_layout.csv do not match count columns")
mapping = pd.read_csv(mapping_path, sep="\t", dtype=str).iloc[:, :2].copy()
if mapping.shape[1] < 2: raise ValueError("Annotation mapping must have at least two columns")
mapping.columns = ["gene_id","gene_name"]
mapping["gene_id"] = mapping["gene_id"].astype(str).str.strip()
mapping["gene_name"] = mapping["gene_name"].fillna("").astype(str).str.strip()
if mapping["gene_id"].duplicated().any():
    conflicts = mapping[mapping["gene_id"].duplicated(keep=False)].groupby("gene_id")["gene_name"].nunique()
    if (conflicts > 1).any(): raise ValueError("Conflicting gene-name mappings for an Ensembl identifier")
    mapping = mapping.drop_duplicates("gene_id", keep="first")
gene_to_name = mapping.set_index("gene_id")["gene_name"]
model_groups = ["DMSO","DMSO_Serum_starvation","Cisplatin_IC50_CBD_IC50","Cisplatin_IC50_CBD_IC50_Serum_starvation_16h"]
layout_by_count = layout.set_index("count_id").loc[counts_prefiltered.columns]
selected = layout_by_count["Group"].isin(model_groups)
if int(selected.sum()) != 12: raise ValueError(f"Expected 12 samples in requested groups, found {int(selected.sum())}")
# PyDESeq2's count convention is observations (samples) by genes.
counts_model = counts_prefiltered.loc[:, selected.to_numpy()].T.copy()
metadata = layout_by_count.loc[selected, ["Group"]].copy()
metadata["Group"] = pd.Categorical(metadata["Group"], categories=model_groups, ordered=False)
metadata = metadata.loc[counts_model.index]
n_cpus = max(1, int(os.environ.get("GALAXY_SLOTS","1")))
dds = DeseqDataSet(counts=counts_model, metadata=metadata, design="~Group", refit_cooks=True, n_cpus=n_cpus)
dds.deseq2()
stat_res = DeseqStats(dds, contrast=["Group","Cisplatin_IC50_CBD_IC50","DMSO"], alpha=0.05, n_cpus=n_cpus)
stat_res.summary()
results = stat_res.results_df.copy()
if len(results) != len(counts_model.columns): raise ValueError("Unexpected PyDESeq2 result row count")
results.index = counts_model.columns.astype(str)
results.index.name = "gene_id"
results.insert(0, "gene_id", results.index.astype(str))
results.insert(1, "gene_name", results["gene_id"].map(gene_to_name))
result_columns = ["gene_id","gene_name","baseMean","log2FoldChange","lfcSE","stat","pvalue","padj"]
for col in result_columns:
    if col not in results.columns: raise ValueError(f"Missing expected PyDESeq2 result column: {col}")
results[result_columns].to_csv("deseq_results.tsv", sep="\t", index=False, na_rep="NA")
foreground = results.loc[results["padj"].notna() & results["log2FoldChange"].notna() & results["baseMean"].notna() & (results["padj"] <= 0.05) & (results["log2FoldChange"].abs() >= 0.5) & (results["baseMean"] >= 10), "gene_name"]
foreground = foreground[foreground.notna() & foreground.ne("")]
foreground = pd.unique(foreground.astype(str))
Path("foreground_genes.txt").write_text("\n".join(sorted(foreground)) + ("\n" if len(foreground) else ""))
background = gene_to_name.reindex(counts_prefiltered.index)
background = background[background.notna() & background.ne("")]
background = pd.unique(background.astype(str))
Path("background_genes.txt").write_text("\n".join(sorted(background)) + ("\n" if len(background) else ""))
