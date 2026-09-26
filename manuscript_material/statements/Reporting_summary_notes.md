# Notes for the Nature Portfolio Reporting Summary

These notes pre-fill the answers that the archive supports. The Reporting Summary form itself must be completed on the journal's current template at submission.

## Statistics

- **Sample size.** No sample-size calculation was performed; the study analyses a complete, pre-existing archive of 4,240 runs.
  - BixBench-Verified-50: 50 tasks; 5 configurations × 2 environments × 3 replicates.
  - CompBioBench: 100 tasks; 4 paired configurations × 2 × 3, plus 100 unpaired code runs.
  - IWC: 10 tasks; 4 × 2 × 3.
- **Unit of analysis.** Runs are nested in tasks. Clusters are source capsules for BixBench (up to 33) and tasks for CompBioBench and IWC.
- **Replicates.** Three per task, configuration and environment. The replicates are not seed-matched.
- **Tests and intervals.**
  - No hypothesis tests are reported.
  - Intervals are exploratory 95% percentile cluster-bootstrap intervals: 20,000 resamples, seed 20260922; 5,000 resamples for the Spearman correlations.
  - Intervals are pointwise and not adjusted for multiplicity.
  - No confirmatory, equivalence, non-inferiority or causal claim is made.
- **Central tendency and dispersion.** These are defined in each figure legend: medians with 95% CI; boxes as interquartile range with whiskers at 1.5× IQR.

## Data exclusions

- **No run was excluded or regraded.**
  - All 4,240 runs are retained, including scored missing answers.
  - Twelve CompBioBench runs have no primary trace. They are counted in the accuracy data but not in the trace-level analyses.
- **Interface-level statistics use Codex-harness traces only (1,908 Galaxy runs).** These are parameter substitution, UDT status and BioBlend/REST use. The superseded Claude Code harness returns tool results in a different structure.
- **CompBioBench task-level analyses use the 82 strong-consensus tasks.** The consensus proxy is explained in Supplementary Note 7.
- **The IWC environment contrast uses the nine tasks scored in both environments.** Host removal is excluded because of null and conflicted route scores (Supplementary Table 7).

## Randomization and blinding

- **Randomization.** Not applicable. Environments were assigned by design, and every configuration ran every task in both environments.
- **Blinding.** Trace adjudication was not blinded to environment, because the traces reveal it. Adjudicators read BixBench reference values only from the evaluator records of completed runs, and assigned confidence levels to limit over-interpretation (Supplementary Note 6).

## Software

- **Statistics:** Python 3.12.13 with NumPy 2.4.1.
- **Figures and supplement:** Python with matplotlib, pandas, openpyxl, reportlab and python-docx (`manuscript_material/scripts/requirements.txt`).

## Life-science specifics

- **Human participants, animals, clinical data and new sequencing:** none. The study analyses computational agent runs on public benchmark data.
- **Public datasets:** the benchmarks use public datasets; see the task sources.
- **Dual-use research of concern:** none identified.
