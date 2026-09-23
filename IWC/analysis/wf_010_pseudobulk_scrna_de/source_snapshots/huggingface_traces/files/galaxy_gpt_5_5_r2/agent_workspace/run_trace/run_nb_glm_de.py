#!/usr/bin/env python
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import NegativeBinomial


ROOT = Path("/workspace")
TRACE = ROOT / "run_trace"
FINAL = ROOT / "final_answer"


def bh_adjust(p_values):
    p = np.asarray(p_values, dtype=float)
    n = p.size
    order = np.argsort(p)
    ranked = p[order]
    adjusted_ranked = ranked * n / np.arange(1, n + 1)
    adjusted_ranked = np.minimum.accumulate(adjusted_ranked[::-1])[::-1]
    adjusted = np.empty_like(adjusted_ranked)
    adjusted[order] = np.clip(adjusted_ranked, 0.0, 1.0)
    return adjusted


def fallback_nb_glm(y, x, offset):
    poisson = sm.GLM(y, x, family=sm.families.Poisson(), offset=offset).fit(maxiter=100)
    mu = np.asarray(poisson.fittedvalues, dtype=float)
    numerator = np.sum((y - mu) ** 2 - mu)
    denominator = np.sum(mu ** 2)
    alpha = max(float(numerator / denominator), 1e-8) if denominator > 0 else 1e-8
    model = sm.GLM(
        y,
        x,
        family=sm.families.NegativeBinomial(alpha=alpha),
        offset=offset,
    )
    return model.fit(maxiter=100)


def fit_gene(y, x, offset):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            result = NegativeBinomial(
                y, x, loglike_method="nb2", offset=offset
            ).fit(disp=0, maxiter=200, method="bfgs")
            beta = float(result.params[1])
            se = float(result.bse[1])
            converged = bool(result.mle_retvals.get("converged", False))
            if converged and np.isfinite(beta) and np.isfinite(se) and se > 0:
                return beta, float(2 * stats.norm.sf(abs(beta / se))), "discrete_nb"
        except Exception:
            pass

        result = fallback_nb_glm(y, x, offset)
        beta = float(result.params[1])
        se = float(result.bse[1])
        if not (np.isfinite(beta) and np.isfinite(se) and se > 0):
            return 0.0, 1.0, "failed_set_neutral"
        return beta, float(2 * stats.norm.sf(abs(beta / se))), "glm_nb_fallback"


def main():
    counts = pd.read_csv(FINAL / "pseudobulk_counts.tsv", sep="\t")
    factors = pd.read_csv(TRACE / "edger_factors.tsv", sep="\t")

    sample_columns = list(counts.columns[1:])
    if sample_columns != list(factors["Sample"]):
        raise ValueError("Count matrix columns do not match factor-file samples")

    disease_normal = factors["disease"].eq("normal").astype(float).to_numpy()
    cell_type_terms = pd.get_dummies(factors["cell_type"], drop_first=True, dtype=float)
    design = np.column_stack(
        [np.ones(len(factors), dtype=float), disease_normal, cell_type_terms.to_numpy()]
    )

    count_values = counts.iloc[:, 1:].to_numpy(dtype=float)
    library_sizes = count_values.sum(axis=0)
    if np.any(library_sizes <= 0):
        raise ValueError("All pseudobulk samples must have positive library sizes")
    offset = np.log(library_sizes)

    rows = []
    method_counts = {}
    for i, gene in enumerate(counts["gene"]):
        beta, p_value, method = fit_gene(count_values[i, :], design, offset)
        if not np.isfinite(beta):
            beta = 0.0
        if not np.isfinite(p_value):
            p_value = 1.0
        p_value = float(np.clip(p_value, 0.0, 1.0))
        rows.append((gene, beta / np.log(2.0), p_value))
        method_counts[method] = method_counts.get(method, 0) + 1
        if (i + 1) % 100 == 0:
            print(f"fit {i + 1} genes", flush=True)

    result = pd.DataFrame(rows, columns=["gene", "log2_fold_change", "p_value"])
    result["fdr"] = bh_adjust(result["p_value"].to_numpy())
    result = result[["gene", "log2_fold_change", "p_value", "fdr"]]

    if len(result) != len(counts):
        raise ValueError("DE result row count does not match pseudobulk matrix")
    if not np.isfinite(result["log2_fold_change"]).all():
        raise ValueError("Non-finite log2 fold change found")
    for column in ["p_value", "fdr"]:
        values = result[column].to_numpy()
        if not (np.isfinite(values).all() and np.all((values >= 0) & (values <= 1))):
            raise ValueError(f"Invalid {column} values found")

    result.to_csv(FINAL / "differential_expression.tsv", sep="\t", index=False)
    (TRACE / "nb_glm_de_summary.json").write_text(
        json.dumps(
            {
                "method": "negative binomial GLM",
                "genes_tested": int(len(result)),
                "design_columns": ["intercept", "disease_normal_minus_COVID_19"]
                + list(cell_type_terms.columns),
                "offset": "log pseudobulk library size",
                "fit_method_counts": method_counts,
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps(method_counts, indent=2))


if __name__ == "__main__":
    main()
