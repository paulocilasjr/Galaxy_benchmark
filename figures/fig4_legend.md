**Fig. 4 \| Answer agreement and tool use vary across model configurations.**
**a**, Share of each model's traced Galaxy runs with at least one completed job in each method family, by benchmark.
Families group 397 installed tools (codebook in Source Data). User-defined tools (UDTs; agent-written code run as Galaxy jobs) form one row; their methods are in Extended Data Fig. 4e.
**b**, Share of replicate sets whose three submitted answers agreed (a replicate set is three runs of one task by one model in one condition; squares, custom code; circles, Galaxy; 50 or 100 sets per point).
Numbers agree within the benchmark verifier's tolerance (otherwise 0.1%), lists are compared as sets, and case and spacing are ignored.
A missing submission does not agree; agreement is not correctness.
The primary tests (bold) pool both benchmarks within each condition and permute model labels within tasks (20,000 permutations; Holm over two); the per-benchmark tests are secondary (Holm over four).
**c**, Tool-set similarity of each task against the share of its 24 runs that were correct.
Similarity is the mean pairwise Jaccard index of the three replicate runs' sets of installed tools, plus one item for any UDT, over task–model cells in which all three Galaxy runs completed a job.
It ignores order, versions and parameters (sensitivity analyses in Extended Data Fig. 4b); correlations are descriptive.
**d**, Verification checks in 80 runs (10 per benchmark × condition × outcome) coded by AI coders blind to the grade; 95% Wilson intervals (by condition, Extended Data Fig. 7a).
**e**, Outcome of every BixBench-Verified-50 and CompBioBench replicate set (both conditions) by held-out difficulty, the number of incorrect runs among the task's other 21 runs.
Error bars, 95% intervals for the share with the same rejected answer in all three runs.
A repeated rejection can reflect an agent's error, an ambiguous reference or the scorer, so on its own it does not measure rigor.
A run is correct when accepted or, for IWC, at ≥ 0.99 output agreement.
Other intervals, 95% percentile cluster-bootstrap (20,000 resamples; clusters are BixBench source capsules, otherwise tasks); Spearman *P* values from permutation tests.
