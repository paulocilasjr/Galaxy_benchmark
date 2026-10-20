**Extended Data Fig. 2 \| Failure causes and sensitivity of the accuracy comparison.**
**a**, Primary cause of each of the 151 incorrect BixBench-Verified-50 runs, graded as on the results site, by how many runs of its replicate set were incorrect (the census shown in the first version of Fig. 2d).
Causes come from an AI-assisted run-level audit; under-specified runs often also lacked answer validation (secondary cause). Four bix-43-q2 runs graded incorrect only by the site's regrade take the task-level audit's cause (benchmark specification or scoring).
**b**, Galaxy minus custom code under alternative definitions.
Primary estimates (diamonds) are the mean score of each benchmark; IWC agreement is × 100.
IWC runs and replicate sets (10 tasks, including host-read removal) are also shown as correct at three agreement thresholds (≥ 0.95, ≥ 0.99, the threshold used elsewhere, and = 1).
The last five rows are the archive's population sensitivities, recomputed on these scores with the primary estimator (the archive's `accuracy_sensitivities.csv` used its own grades and nine IWC tasks):
- BixBench-Verified-50 without the tasks whose failures the audit attributes to the benchmark;
- CompBioBench without runs from campaigns whose names reference target scores or wrong answers;
- IWC without tasks that had a zero-scored run;
- IWC without the agent-calibrated ATAC routes;
- IWC restricted to replicate pairs with matching time budgets.

Intervals are 95% percentile cluster-bootstrap intervals (clusters are BixBench source capsules, otherwise tasks). With ten or fewer IWC clusters these intervals are too narrow, so the sign-flip *P* values in Source Data (exact for IWC) should be preferred.
