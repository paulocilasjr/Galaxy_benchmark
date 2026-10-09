**Extended Data Fig. 2 \| Failure causes and sensitivity of the accuracy comparison.**
**a**, Primary cause of each of the 170 incorrect BixBench-Verified-50 runs, by how many runs of its replicate set were incorrect (the census shown in the first version of Fig. 2d).
Causes come from an AI-assisted run-level audit; under-specified runs often also lacked answer validation (secondary cause).
**b**, Galaxy minus custom code under alternative definitions.
Primary estimates (diamonds) are the mean score of each benchmark; IWC agreement is × 100.
IWC runs and replicate sets are also shown as correct at three agreement thresholds (≥ 0.95, ≥ 0.99, the threshold used elsewhere, and = 1).
The last five rows are the archive's own population sensitivities (`accuracy_sensitivities.csv`):
- BixBench-Verified-50 without the tasks whose failures the audit attributes to the benchmark;
- CompBioBench without runs from campaigns whose names reference target scores or wrong answers;
- IWC without tasks that had a zero-scored run;
- IWC without the agent-calibrated ATAC routes;
- IWC restricted to replicate pairs with matching time budgets.

Intervals are 95% percentile cluster-bootstrap intervals (clusters are BixBench source capsules, otherwise tasks). With nine or fewer IWC clusters these intervals are too narrow, so the exact sign-flip *P* values in Source Data should be preferred.
