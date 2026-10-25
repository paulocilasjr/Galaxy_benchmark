import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path("/workspace")
TRACE = ROOT / "run_trace"
FINAL = ROOT / "final_answer"


def r_make_name(value: str) -> str:
    value = re.sub(r"[^0-9A-Za-z_.]", ".", value)
    if not re.match(r"^[A-Za-z]|^\.[^0-9]", value):
        value = "X" + value
    return value


FINAL.mkdir(exist_ok=True)

obs = pd.read_csv(TRACE / "source_obs.tsv", sep="\t", index_col=0)
var = pd.read_csv(TRACE / "source_var.tsv", sep="\t")
pb = pd.read_csv(TRACE / "galaxy_pseudobulk_all.tsv", sep="\t", index_col=0)
meta = pd.read_csv(TRACE / "galaxy_pseudobulk_metadata.tsv", sep="\t", index_col=0)

assert list(meta.columns) == ["orig.ident", "individual", "cell_type"]
assert len(pb.columns) == len(meta) == 39
assert [r_make_name(x) for x in meta.index] == list(pb.columns)
assert (pb.to_numpy() >= 0).all()
assert np.equal(pb.to_numpy(), np.floor(pb.to_numpy())).all()
pb = pb.astype(np.int64)

cell_counts = (
    obs.groupby(["individual", "cell_type"], observed=True)
    .size()
    .rename("n_cells")
)
meta["n_cells"] = [cell_counts.loc[(r.individual, r.cell_type)] for r in meta.itertuples()]

ind_disease = obs.groupby("individual", observed=True)["disease"].agg(lambda x: sorted(set(x)))
assert ind_disease.map(len).eq(1).all()
ind_disease = ind_disease.map(lambda x: x[0])
assert set(ind_disease) == {"normal", "COVID-19"}
meta["disease"] = meta["individual"].map(ind_disease)

keep_samples = meta["n_cells"].ge(10)
retained_meta = meta.loc[keep_samples].copy()
retained = pb.loc[:, keep_samples.to_numpy()].copy()

n_samples = retained.shape[1]
totals = retained.sum(axis=0)
assert totals.gt(0).all()
median_total = float(np.median(totals.to_numpy(dtype=float)))
required_samples = int(math.ceil(10 + 0.7 * (n_samples - 10)))
cpm_threshold = 10.0 / median_total * 1_000_000.0
cpm = retained.div(totals, axis=1) * 1_000_000.0
keep_genes = cpm.ge(cpm_threshold).sum(axis=1).ge(required_samples) & retained.sum(axis=1).ge(1000)
filtered = retained.loc[keep_genes].copy()

symbol_map = var.set_index("ensembl_gene_id")["gene_symbol"]
assert filtered.index.isin(symbol_map.index).all()
gene_symbols = symbol_map.loc[filtered.index]

def output_sample_name(row):
    return (f"{row.individual}_{row.cell_type}").replace(" ", "_").replace("-", "_")

output_columns = [output_sample_name(row) for row in retained_meta.itertuples()]
assert len(output_columns) == len(set(output_columns))

final_counts = filtered.copy()
final_counts.index = gene_symbols.to_numpy()
final_counts.index.name = "gene"
final_counts.columns = output_columns
final_counts.to_csv(FINAL / "pseudobulk_counts.tsv", sep="\t")

edger_counts = filtered.copy()
edger_counts.index.name = "gene"
edger_counts.to_csv(TRACE / "edger_counts.tsv", sep="\t")

retained_meta["matrix_column"] = list(filtered.columns)
retained_meta["output_column"] = output_columns
retained_meta["edger_disease"] = retained_meta["disease"].replace({"COVID-19": "COVID_19"})
retained_meta["edger_cell_type"] = retained_meta["cell_type"].str.replace(r"[^A-Za-z0-9_]", "_", regex=True)
retained_meta.to_csv(TRACE / "edger_sample_metadata.tsv", sep="\t", index_label="aggregate_id")

summary = {
    "all_aggregate_samples": int(len(meta)),
    "retained_samples_N": int(n_samples),
    "median_total_count_M": median_total,
    "required_samples_S": required_samples,
    "cpm_threshold": cpm_threshold,
    "retained_genes": int(filtered.shape[0]),
    "disease_groups": retained_meta["disease"].value_counts().sort_index().to_dict(),
    "cell_types": retained_meta["cell_type"].value_counts().sort_index().to_dict(),
}
(TRACE / "filter_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
