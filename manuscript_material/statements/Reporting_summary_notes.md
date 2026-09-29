# Notes for the Nature Portfolio Reporting Summary

These notes pre-fill the answers that the archive supports. The Reporting Summary form itself must be completed on the journal's current template at submission.

## Statistics

- **Sample size.** No sample-size calculation was performed; the study analyses a complete, pre-existing archive of 4,240 runs.
  - BixBench-Verified-50: 50 tasks; 5 model configurations × 2 execution conditions × 3 replicate runs.
  - CompBioBench: 100 tasks; 4 paired model configurations × 2 × 3, plus 100 unpaired open-ended code condition runs.
  - IWC: 10 tasks; 4 × 2 × 3.
- **Unit of analysis.** Runs are nested in tasks. Clusters are source capsules for BixBench (up to 33) and tasks for CompBioBench and IWC.
- **Replicate runs.** Three per task × model configuration × execution condition (one replicate set). Replicate labels are not matched random seeds; CompBioBench replicate runs are final campaign selections and may include continuations.
- **Tests and intervals.**
  - No hypothesis tests are reported.
  - Intervals are exploratory 95% percentile cluster-bootstrap intervals: 20,000 resamples, seed 20260922; 5,000 resamples for the Spearman correlations.
  - Intervals are pointwise and not adjusted for multiplicity.
  - No confirmatory, equivalence, non-inferiority or causal claim is made.
- **Central tendency and dispersion.** These are defined in each figure legend: medians with 95% confidence intervals; boxes span the interquartile range, with whiskers at 1.5 times the interquartile range.

## Data exclusions

- **No run was excluded or regraded.**
  - All 4,240 runs are retained, including runs without an answer, which count as scored incorrect.
  - Twelve CompBioBench runs have no execution trace. They are counted in the reported benchmark scores but not in the trace-level analyses.
- **Interface-level statistics use Codex execution traces only (1,908 Galaxy-condition runs).** These are parameter substitution, user-defined-tool status and direct Galaxy API calls. The superseded Claude Code agent harness records tool results in a different structure.
- **CompBioBench consensus-proxy analyses (probable failures, split replicate sets) use the 82 strong-consensus tasks.** The consensus proxy is explained in Supplementary Note 7. The task-level audit instead uses the answer key inferred from the official leaderboard scores (Supplementary Note 6).
- **The IWC condition difference uses the nine tasks scored in both execution conditions.** Host removal is excluded because of null scores and score conflicts (Supplementary Table 7).

## Randomization and blinding

- **Randomization.** Not applicable. Execution conditions were assigned by design, and every model configuration ran every task of its benchmarks in both execution conditions (GPT-6 Astra ran CompBioBench in the open-ended code condition only).
- **Blinding.** Adjudication was not blinded to execution condition, because execution traces reveal it. Adjudicators read BixBench reference values only from the evaluator records of completed runs, and assigned an adjudication confidence to limit over-interpretation (Supplementary Note 6). The task-level audit read every run of each task case, in both execution conditions, and opened no file of the benchmark ground truth.

## Software

- **Statistics:** Python 3.12.13 with NumPy 2.4.1.
- **Figures and supplement:** Python with matplotlib, pandas, openpyxl, reportlab and python-docx (`manuscript_material/scripts/requirements.txt`).

## Life-science specifics

- **Human participants, animals, clinical data and new sequencing:** none. The study analyses computational agent runs on public benchmark data.
- **Public datasets:** the benchmarks use public datasets; see the task sources.
- **Dual-use research of concern:** none identified.
