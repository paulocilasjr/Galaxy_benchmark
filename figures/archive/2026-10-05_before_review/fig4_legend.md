**Fig. 4 \| Task solution variability is model-dependent.**
**a**, The 15 installed Galaxy tools used in the most Galaxy runs, ranked by overall share, with each model's share of its own traced Galaxy runs (470–480 per model; one count per run, successful or not).
Labels give the share of runs that called a user-defined tool (UDT), agent-written code run as a Galaxy job.
**b**, Share of replicate sets (one task × model × condition) whose three runs gave the same answer, by model and condition (squares, custom code; circles, Galaxy), for each benchmark and both pooled (50, 100 and 150 sets per model and condition).
*P* values test whether models differ within each condition, permuting model labels within tasks (20,000 permutations).
**c**, Similarity of the run trajectories (the Galaxy tools used) of the three replicate runs, averaged over models for each task, against the task's accuracy, the share of its 24 runs (both conditions, all models) that were correct.
Similarity is the mean pairwise Jaccard index of the runs' tool sets, with UDT jobs counted as one step because agents name each UDT anew; Spearman correlations use permutation tests, within benchmarks across tasks and within tasks when models on the same task are compared.
**d**, Replicate sets with at least one wrong answer (245 of 1,200 BixBench-Verified-50 and CompBioBench sets), by task difficulty, the share of the task's runs that were wrong: random errors, in which the answers differed between replicates, and systematic errors, in which all three replicates gave the same wrong answer; numbers above bars are sets.
Answers were compared as text after trimming and lower-casing, with numbers rounded to three significant digits.
A run is correct when accepted or, for IWC, at ≥ 0.99 output agreement.
Error bars, 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks).
