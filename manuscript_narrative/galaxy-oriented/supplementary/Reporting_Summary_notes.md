# Reporting Summary: answers for the Nature Portfolio form

These notes are the authors' draft answers to the Nature Portfolio Reporting Summary for *Measuring agent readiness in scientific workbenches through Galaxy*. Copy them into the official form; numbers refer to `numbers.json` and the Source Data.

## Statistics

- **Sample sizes.** Exact n is given for every proportion in the figure legends and Source Data: runs, interface calls, jobs, failure episodes and tools.
- **Repeated measurements.** Interface calls are nested within runs, and runs within tasks. Proportions are descriptive. Token ratios use task × configuration cells, with intervals resampling tasks or source capsules.
- **Tests.** Two-sided Wilcoxon signed-rank tests for token use of incorrect versus correct sibling runs; Spearman correlations between tokens and actions. All other results are descriptive proportions, and token ratios carry 95% percentile cluster-bootstrap intervals (20,000 resamples; seed 20261002).
- **Covariates and multiplicity.** No covariate adjustment and no multiplicity adjustment; all intervals are pointwise and exploratory.
- **Assumptions.** The bootstrap assumes exchangeable clusters.
- **Effect sizes.** Proportions with numerators and denominators, and ratios with intervals.
- **Bayesian analyses, hierarchical designs.** None.

## Software and code

- **Data collection.** None; the archive was generated earlier. Calls were extracted from archived traces with `manuscript_narrative/derived/galaxy_calls/extract_calls.py`.
- **Data analysis.** Python 3.12 with matplotlib 3.11.2, numpy 2.5.3, pandas 3.0.6, openpyxl 3.1.5 and scipy 1.18.1 (`manuscript_narrative/requirements.txt`). Documents are built with Node.js and docx 9.6.1. The single entry point is `manuscript_narrative/build_all.sh` [Authors: release DOI].

## Data

See the Data availability statement.

## Field-specific reporting

Life sciences.

## Study design

- **Sample size.** No sample-size calculation was performed. The analysis covers all 2,070 archived Galaxy-arm runs (2,058 with parsed traces; 69,505 Galaxy-interface calls; 23,080 jobs).
- **Data exclusions.** 307 calls to non-Galaxy tool servers were excluded from interface measures. Twelve runs without a parsed trace contribute only run-level measures. Supplementary Table 1 reconciles the counts.
- **Replication.** Archived adapter deployments on one public server; interface-commit coverage is incomplete. Replication on a second deployment is specified in Supplementary Note 1.
- **Randomization.** None; the study is observational.
- **Blinding.** None. The targeted trace audit was AI-assisted [Authors: describe the human review].
