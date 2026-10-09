import sys
import numpy as np
import pandas as pd
import pydeseq2
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

counts_path, metadata_path, slots_text = sys.argv[1:4]
n_cpus = max(1, int(slots_text))
gene_by_sample = pd.read_csv(counts_path, index_col=0)
metadata = pd.read_csv(metadata_path, index_col=0)
gene_by_sample.columns = gene_by_sample.columns.astype(str)
metadata.index = metadata.index.astype(str)

if gene_by_sample.index.has_duplicates:
    raise ValueError("Duplicate gene identifiers in count matrix")
if metadata.index.has_duplicates:
    raise ValueError("Duplicate sample identifiers in metadata")
if set(gene_by_sample.columns) != set(metadata.index):
    raise ValueError("Count-matrix samples and metadata samples do not match")
if "batch" not in metadata.columns or "sex" not in metadata.columns:
    raise ValueError("Metadata must contain batch and sex columns")
if set(metadata["sex"].astype(str)) != {"F", "M"}:
    raise ValueError("Sex levels must be exactly F and M")
if "FAM138A" not in gene_by_sample.index:
    raise ValueError("FAM138A is absent from the count matrix")

gene_by_sample = gene_by_sample.loc[:, metadata.index]
counts = gene_by_sample.T
values = counts.to_numpy()
if not np.isfinite(values).all():
    raise ValueError("Counts contain non-finite values")
if (values < 0).any():
    raise ValueError("Counts contain negative values")
if not np.equal(values, np.floor(values)).all():
    raise ValueError("Counts are not integer-valued")
counts = counts.astype(np.int64)

metadata = metadata.copy()
metadata["batch"] = pd.Categorical(
    metadata["batch"].astype(str),
    categories=sorted(metadata["batch"].astype(str).unique().tolist())
)
metadata["sex"] = pd.Categorical(metadata["sex"].astype(str), categories=["F", "M"])

dds = DeseqDataSet(
    counts=counts,
    metadata=metadata,
    design="~ batch + sex",
    refit_cooks=True,
    n_cpus=n_cpus,
)
dds.deseq2()
stats = DeseqStats(dds, contrast=["sex", "M", "F"], n_cpus=n_cpus)
stats.summary()

coef_columns = [str(x) for x in dds.varm["LFC"].columns]
if "sex[T.M]" in coef_columns:
    coefficient = "sex[T.M]"
else:
    candidates = [x for x in coef_columns if "sex" in x and "M" in x]
    if len(candidates) != 1:
        raise ValueError(f"Could not uniquely identify M-vs-F coefficient from {coef_columns}")
    coefficient = candidates[0]

stats.lfc_shrink(coeff=coefficient)
results = stats.results_df.copy()
target = results.loc[["FAM138A"]].copy()
target.index.name = "gene"
target["passes_abs_lfc_gt_0.5"] = target["log2FoldChange"].abs() > 0.5
target["passes_baseMean_gt_10"] = target["baseMean"] > 10
target["passes_requested_thresholds"] = (
    target["passes_abs_lfc_gt_0.5"] & target["passes_baseMean_gt_10"]
)
target.to_csv("fam138a.tsv", sep="\t")

with open("diagnostics.txt", "w") as out:
    out.write(f"pydeseq2_version={pydeseq2.__version__}\n")
    out.write("input=BatchCorrectedReadCounts_Zenodo.csv\n")
    out.write("design=~ batch + sex\n")
    out.write("batch_type=categorical\n")
    out.write("contrast=sex,M,F\n")
    out.write(f"shrink_coefficient={coefficient}\n")
    out.write("shrinkage_call=lfc_shrink(coeff=coefficient)\n")
    out.write(f"n_samples={counts.shape[0]}\n")
    out.write(f"n_genes={counts.shape[1]}\n")
    out.write(f"n_F={(metadata['sex'].astype(str) == 'F').sum()}\n")
    out.write(f"n_M={(metadata['sex'].astype(str) == 'M').sum()}\n")
    out.write("thresholds=abs(log2FoldChange)>0.5;baseMean>10\n")
