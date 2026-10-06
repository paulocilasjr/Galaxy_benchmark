**Fig. 3 \| Galaxy records trace most failures beyond the workbench.**
**a**, Replicate sets (one task × model × condition, three runs) with one, two or three incorrect runs, pooled over benchmarks (636 sets per condition) and stacked by model.
A run is incorrect when not accepted or, for IWC, below 0.99 output agreement (Fig. 2b).
*P* values compare set counts between conditions (Holm-adjusted across groups).
**b**, Runs ending correct by the number of execution errors in the run (failed shell commands, excluding a silent exit code 1, plus Galaxy jobs in error; 3,767 of 3,816 runs have records).
Points group runs by error count (area proportional to runs); lines are logistic fits with 95% cluster-bootstrap bands.
The annotated comparison averages the Galaxy − open-ended code difference over four error bins (1–2, 3–5, 6–10, >10), weighted by their share of runs with errors; it was chosen after inspecting the bins (unadjusted, +2.3 points, *P* = 0.07).
**c**, Primary cause of each incorrect BixBench-Verified-50 run (170 runs), by how many runs of its set were incorrect.
Each run's primary cause in the run-level failure audit maps to one category: no answer validation (an error that checking the result would have exposed); lacking biological knowledge (a wrong biological or statistical concept); not able to use Galaxy (a Galaxy tool, wrapper or job gave the wrong result); no answer submitted; and benchmark specification or scoring (an under-specified task or reference, or a scorer rejecting a valid answer).
In 79 of the 99 under-specified runs, missing validation was the secondary cause.
CompBioBench and IWC have task-level audits only.
**d**, Accuracy when all three runs must be correct (solid; vermillion, open-ended code; blue, Galaxy) and with a majority vote, in which a set is correct when two or more runs are (light segment adds sets with two of three correct; number above bar); 159 sets per bar.
n.s., Holm-adjusted *P* ≥ 0.05 (Galaxy − open-ended code).
Error bars, 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks).
*P* values come from two-sided paired randomization tests within clusters (200,000 draws).
