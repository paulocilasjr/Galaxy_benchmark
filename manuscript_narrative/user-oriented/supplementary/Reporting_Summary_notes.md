# Reporting Summary: answers for the Nature Portfolio form

These notes are the authors' draft answers to the Nature Portfolio Reporting Summary for *Execution environments shape the reliability of biomedical AI agents*. Copy them into the official form; numbers refer to `numbers.json` and the Source Data.

## Statistics

- **Sample sizes.** Exact n is given for every estimate in the figure legends and Source Data: runs, replicate sets, task × configuration cells, tasks and clusters.
- **Repeated measurements.** Three replicate runs per task × model configuration × arm, analysed as replicate sets. Arms are paired within task and configuration, and intervals resample clusters (33 BixBench-Verified-50 source capsules; 100 CompBioBench tasks; nine IWC tasks).
- **Tests.** Two-sided Wilcoxon signed-rank tests on per-task medians for actions, with Holm adjustment. All other comparisons are estimates with 95% percentile cluster-bootstrap intervals (20,000 resamples; seeds 20260922 for archived intervals and 20261002 for new ones).
- **Covariates and multiplicity.** No covariate adjustment. Intervals are pointwise; multiplicity is addressed only for actions (Holm).
- **Assumptions.** The bootstrap assumes exchangeable clusters; Wilcoxon tests assume symmetric paired differences.
- **Effect sizes.** Differences in percentage points or agreement units, and ratios, each with an interval.
- **Bayesian analyses, hierarchical designs, correlation coefficients.** None.

## Software and code

- **Data collection.** None; the archive was generated earlier by the benchmark harnesses. No agent code was run for this analysis.
- **Data analysis.** Python 3.12 with matplotlib 3.11.2, numpy 2.5.3, pandas 3.0.6, openpyxl 3.1.5 and scipy 1.18.1 (`manuscript_narrative/requirements.txt`). Documents are built with Node.js and docx 9.6.1. The single entry point is `manuscript_narrative/build_all.sh` [Authors: release DOI].

## Data

See the Data availability statement. The CompBioBench reference key is private; Source Data contain grades but no CompBioBench answers.

## Field-specific reporting

Life sciences.

## Study design

- **Sample size.** No sample-size calculation was performed. The analysis covers every archived run of the four primary model configurations (3,840 runs; 3,816 in the endpoint analyses). The superseded harness (300 runs) is reported separately, and 100 unpaired runs are excluded.
- **Data exclusions.** The IWC host-read-removal task was excluded from IWC endpoints, as in the archived analyses: three code runs followed unsupported routes and two Galaxy runs had conflicting scores. Token ratios use only cells with records in both arms. Each exclusion is listed in Supplementary Table 2.
- **Replication.** Three replicate runs per task, configuration and arm. Replicate labels are not matched random seeds. No independent replay was performed; a protocol is in Supplementary Note 1.
- **Randomization.** None. Arms were assigned by design, not randomized, and run order was not randomized. Run dates, prompts, budgets and campaigns differed between arms (Supplementary Table 1).
- **Blinding.** None. The targeted trace audit was AI-assisted and not blinded to arm [Authors: describe the human review]. Blinded expert review is specified in Supplementary Note 1.
