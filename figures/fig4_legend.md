**Fig. 4 \| Answer agreement and tool use vary across model configurations.**
**a**, Share of each model's traced Galaxy runs with at least one completed job in each method family, by benchmark.
Families group 422 installed tools by our codebook (Source Data) and separate data handling from scientific methods. User-defined tools (UDTs; agent-written code run as a Galaxy job) form one row because their methods were not annotated.
**b**, Share of replicate sets whose three submitted answers were the same (a replicate set is three runs of one task by one model in one condition; squares, custom code; circles, Galaxy; 50 or 100 sets per point).
Answers were compared after trimming and lower-casing, with numbers rounded to three significant digits.
A set with a missing submission does not agree, and agreement is not correctness.
The primary tests (bold) pool both benchmarks within each condition; the per-benchmark tests are secondary.
Model labels were permuted within tasks (20,000 permutations), with Holm adjustment within each family of tests.
**c**, Tool-set similarity of each task against the share of its 24 runs that were correct.
Similarity is the mean pairwise Jaccard index of the three replicate runs' sets of installed tools, plus one item for any UDT, over task–model cells in which all three Galaxy runs completed a job.
It ignores order, repetition, versions, parameters and UDT methods, so it does not describe analytical routes; the correlations are descriptive.
**d**, Outcome of every BixBench-Verified-50 and CompBioBench replicate set (both conditions) by held-out difficulty, the number of incorrect runs among the task's other 21 runs.
Error bars, 95% intervals for the share with the same rejected answer in all three runs.
A repeated rejection can reflect an agent's error, an ambiguous reference or the scorer, so on its own it does not measure analytical rigor.
A run is correct when accepted or, for IWC, at ≥ 0.99 output agreement.
Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks); Spearman *P* values come from permutation tests.
Extended Data Fig. 4 gives the tool inventory, similarity by model and answer-matching sensitivity.
