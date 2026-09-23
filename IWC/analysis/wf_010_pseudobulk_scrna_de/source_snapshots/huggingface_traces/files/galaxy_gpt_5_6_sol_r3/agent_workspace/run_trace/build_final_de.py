import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path("/workspace")
TRACE = ROOT / "run_trace"
FINAL = ROOT / "final_answer"

counts = pd.read_csv(TRACE / "edger_counts.tsv", sep="\t", index_col=0)
var = pd.read_csv(TRACE / "source_var.tsv", sep="\t").set_index("ensembl_gene_id")
result = pd.read_csv(TRACE / "edger_result.tsv", sep="\t").set_index("GeneID")

assert result.index.is_unique
assert counts.index.is_unique
assert set(result.index) == set(counts.index)
result = result.loc[counts.index]

logfc = result["logFC"].to_numpy(dtype=float)
pvals = result["PValue"].to_numpy(dtype=float)
assert np.isfinite(logfc).all()
assert np.isfinite(pvals).all()
assert ((0 <= pvals) & (pvals <= 1)).all()

# Benjamini-Hochberg adjustment computed directly across all reported genes.
m = len(pvals)
order = np.argsort(pvals, kind="mergesort")
ranked = pvals[order]
adjusted_ranked = ranked * m / np.arange(1, m + 1)
adjusted_ranked = np.minimum.accumulate(adjusted_ranked[::-1])[::-1]
adjusted_ranked = np.minimum(adjusted_ranked, 1.0)
fdr = np.empty(m, dtype=float)
fdr[order] = adjusted_ranked
assert np.isfinite(fdr).all()
assert ((0 <= fdr) & (fdr <= 1)).all()

symbols = var.loc[counts.index, "gene_symbol"].to_numpy()
de = pd.DataFrame(
    {
        "gene": symbols,
        "log2_fold_change": logfc,
        "p_value": pvals,
        "fdr": fdr,
    }
)
de.to_csv(FINAL / "differential_expression.tsv", sep="\t", index=False)
(FINAL / "method.json").write_text(json.dumps({"method": "edgeR"}) + "\n")

# Final identity checks against the required count matrix.
final_counts = pd.read_csv(FINAL / "pseudobulk_counts.tsv", sep="\t")
assert list(de["gene"]) == list(final_counts["gene"])
assert len(de) == len(final_counts) == 1429
print(f"wrote {len(de)} complete edgeR rows")
