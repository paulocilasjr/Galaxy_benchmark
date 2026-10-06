**Fig. 2 \| Agents maintain bioinformatics accuracy when operating through Galaxy.**
**a**, Accuracy of each model in the custom-code (vermillion) and Galaxy (blue) conditions on each benchmark (150, 300 and 27 runs per bar for BixBench-Verified-50, CompBioBench and IWC); IWC bars show mean agreement with curated workflow outputs (× 100).
Dots, accuracy of each replicate (one run per task).
n.s., Holm-adjusted *P* ≥ 0.05 across the 12 comparisons (smallest adjusted *P* = 0.38).
**b**, Galaxy minus custom code by benchmark, models pooled, for the share of runs correct (circles) and of replicate sets (one task × model × condition, three runs) with all three runs correct (diamonds).
IWC tasks derive from Galaxy workflows; BixBench-Verified-50 and CompBioBench are platform-neutral.
*P* values are Holm-adjusted across the six comparisons.
**c**, For each task and model (636 pairs), the number of correct runs of three in custom code (columns) and in Galaxy (rows); shading is logarithmic in the count, and outlined cells have equal counts.
**d**, Primary cause of each incorrect BixBench-Verified-50 run (170 runs), by how many runs of its set were incorrect.
Causes come from the run-level failure audit: no answer validation (an error that checking the result would have exposed); lacking biological knowledge (a wrong biological or statistical concept); not able to use Galaxy (a Galaxy tool, wrapper or job gave the wrong result); no answer submitted; and benchmark specification or scoring (an under-specified task or reference, or a scorer rejecting a valid answer).
CompBioBench and IWC have task-level audits only.
A run is correct when accepted or, for IWC, at ≥ 0.99 output agreement (172 of 216 IWC runs).
Error bars, 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks).
*P* values come from two-sided paired randomization tests that flip the sign of cluster-level differences (200,000 draws; exact for IWC).
