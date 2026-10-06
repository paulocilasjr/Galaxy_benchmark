**Fig. 2 \| Galaxy matches agent performance with open-ended code.**
**a**, Accuracy of each model configuration in the open-ended code (vermillion) and Galaxy (blue) conditions, pooling all BixBench-Verified-50 and CompBioBench runs (450 runs per bar: 150 tasks × 3 replicate runs).
n.s., Holm-adjusted *P* ≥ 0.05 for the Galaxy − open-ended code difference (all four adjusted *P* = 1.0; differences 0 to +1.3 percentage points).
IWC (continuous endpoint) is not pooled.
**b**, Share of replicate sets (one task × one model, three runs) in which all three runs were correct, summed over the four models; numbers above bars are set counts (200, 400 and 36 sets per condition).
An IWC run counts as correct at ≥ 0.99 agreement with the curated workflow output (172 of 216 IWC runs); at 0.95 and 1.0, counts are 24 versus 30 and 13 versus 17 sets.
*P* values are Holm-adjusted across benchmarks.
**c**, Accuracy by benchmark and model in the Galaxy condition (150, 300 and 27 runs per bar).
IWC bars show mean output agreement (× 100).
Dots, accuracy of each replicate (50, 100 and 9 runs; their mean is the bar height), showing rerun variation on the same tasks; error bars show uncertainty over tasks.
No model pair differs after Holm adjustment across 18 comparisons (six pairs in each benchmark; adjusted *P* ≥ 0.20), and model rankings do not differ detectably between benchmarks (*P* = 0.07; BixBench-Verified-50 versus CompBioBench, *P* = 0.61; permutation test of within-task model ranks).
**d**, The 15 installed Galaxy tools used in the most Galaxy-condition runs, ranked by overall share, with each model's share of its own Galaxy runs (470–480 traced runs per model; one count per run, successful or not).
Labels above each model give the share of its runs that called a user-defined tool (UDT), agent-written code run as a Galaxy job.
Error bars, 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks).
*P* values come from two-sided paired randomization tests that flip the sign of cluster-level differences (200,000 draws; exact for IWC); the ranking test permutes clusters between benchmarks (100,000 permutations).
