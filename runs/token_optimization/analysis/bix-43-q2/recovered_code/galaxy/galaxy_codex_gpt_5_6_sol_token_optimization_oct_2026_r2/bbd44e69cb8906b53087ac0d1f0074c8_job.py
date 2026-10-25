import json
import os
import sys
import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats
from pydeseq2.default_inference import DefaultInference

counts_path, layout_path, mapping_path = sys.argv[1:4]
counts_all = pd.read_csv(counts_path, index_col=0)
counts_all.index = counts_all.index.astype(str)
counts_all.columns = counts_all.columns.astype(str)
if counts_all.index.has_duplicates:
    raise ValueError("Duplicate Ensembl IDs in count matrix")
if counts_all.isna().any().any():
    raise ValueError("Missing values in count matrix")
counts_all = counts_all.astype(int)
if (counts_all < 0).any().any():
    raise ValueError("Negative counts found")

prefilter = (counts_all > 10).any(axis=1)
counts_filtered = counts_all.loc[prefilter].copy()

layout = pd.read_csv(layout_path)
expected = {"SampleID", "Group"}
if not expected.issubset(layout.columns):
    raise ValueError(f"Sample layout missing columns: {expected - set(layout.columns)}")
layout["count_column"] = layout["SampleID"].astype(str).str.replace("-", "_", regex=False)
related_groups = [
    "DMSO",
    "DMSO_Serum_starvation",
    "Cisplatin_IC50_CBD_IC50",
    "Cisplatin_IC50_CBD_IC50_Serum_starvation_16h",
]
meta = layout.loc[layout["Group"].isin(related_groups), ["count_column", "Group"]].copy()
if len(meta) != 12 or meta["Group"].value_counts().to_dict() != {g: 3 for g in related_groups}:
    raise ValueError(f"Unexpected related-group sample counts: {meta['Group'].value_counts().to_dict()}")
missing_samples = [x for x in meta["count_column"] if x not in counts_filtered.columns]
if missing_samples:
    raise ValueError(f"Layout samples absent from count matrix: {missing_samples}")

sample_order = meta["count_column"].tolist()
counts_model = counts_filtered.loc[:, sample_order].T
meta = meta.set_index("count_column").loc[sample_order]
meta["Group"] = pd.Categorical(meta["Group"], categories=related_groups)

n_cpus = max(1, int(os.environ.get("GALAXY_SLOTS", "1")))
inference = DefaultInference(n_cpus=n_cpus)
dds = DeseqDataSet(
    counts=counts_model,
    metadata=meta,
    design="~Group",
    refit_cooks=True,
    inference=inference,
)
dds.deseq2()
comparison = "Cisplatin_IC50_CBD_IC50"
control = "DMSO"
stats = DeseqStats(
    dds,
    contrast=["Group", comparison, control],
    alpha=0.05,
    cooks_filter=True,
    independent_filter=True,
    inference=inference,
)
stats.summary()
res = stats.results_df.copy()
res.index.name = "ENSG"
res.to_csv("deseq2_results.tsv", sep="\t")

mapping = pd.read_csv(mapping_path, sep="\t", dtype=str)
if not {"ENSG", "gene_name"}.issubset(mapping.columns):
    raise ValueError("Mapping file must contain ENSG and gene_name")
mapping = mapping.dropna(subset=["ENSG", "gene_name"])
mapping = mapping.loc[mapping["gene_name"].str.strip().ne("")]
mapping = mapping.drop_duplicates(subset="ENSG", keep="first").set_index("ENSG")["gene_name"]

sig_mask = (
    res["padj"].notna()
    & (res["padj"] <= 0.05)
    & (res["log2FoldChange"].abs() >= 0.5)
    & (res["baseMean"] >= 10)
)
foreground = pd.Index(res.index[sig_mask]).map(mapping).dropna()
foreground = pd.Index(pd.unique(foreground.astype(str)))
background = pd.Index(counts_filtered.index).map(mapping).dropna()
background = pd.Index(pd.unique(background.astype(str)))
if len(foreground) == 0:
    raise ValueError("No mapped significant genes after requested thresholds")

pd.Series(foreground).to_csv("foreground_genes.txt", index=False, header=False)
pd.Series(background).to_csv("background_genes.txt", index=False, header=False)
report = {
    "pydeseq2_version": __import__("pydeseq2").__version__,
    "all_samples_for_prefilter": int(counts_all.shape[1]),
    "genes_before_prefilter": int(counts_all.shape[0]),
    "genes_after_prefilter": int(counts_filtered.shape[0]),
    "model_samples": int(counts_model.shape[0]),
    "model_group_counts": {str(k): int(v) for k, v in meta["Group"].value_counts(sort=False).items()},
    "design": "~Group",
    "contrast": ["Group", comparison, control],
    "alpha": 0.05,
    "thresholds": {"padj_lte": 0.05, "abs_log2FoldChange_gte": 0.5, "baseMean_gte": 10},
    "significant_ensembl_genes": int(sig_mask.sum()),
    "mapped_unique_foreground_genes": int(len(foreground)),
    "mapped_unique_background_genes": int(len(background)),
}
with open("analysis_report.json", "w") as handle:
    json.dump(report, handle, indent=2)
