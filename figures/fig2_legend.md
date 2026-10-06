**Fig. 2 \| Agents show similar observed benchmark performance in Galaxy and custom code.**
**a**, Score of each model in the custom-code (squares) and Galaxy (circles) conditions, under each benchmark's scoring contract: acceptance by the original evaluator (BixBench-Verified-50; 150 runs per point), agreement with a reconstructed answer key (CompBioBench; 300 runs) and mean agreement with curated workflow outputs on a 0–1 scale (IWC; 27 runs).
Small dots, replicates (one run per task).
**b**, Galaxy minus custom code for each model and for the four models pooled (diamonds), for two estimands kept apart: the mean score (IWC agreement × 100) and the share of replicate sets (one task × model × condition, three runs) with all three runs correct (IWC, agreement ≥ 0.99).
No difference was significant after Holm adjustment (smallest adjusted *P* = 0.38, GPT-5.5 on IWC); this does not establish equivalence, and no equivalence margin was prespecified.
With nine IWC tasks, bootstrap intervals are too narrow: the pooled IWC agreement difference, +4.0 points (0.7 to 7.8), has an exact *P* of 0.06.
**c**, Correct runs of three for each task–model pair in custom code (columns) and Galaxy (rows), per benchmark; outlined cells have equal counts.
Equal counts mean equal replicate success, not identical answers or methods.
**d**, Primary cause of incorrect BixBench-Verified-50 runs, from an AI-assisted run-level audit. The runs are grouped by pair type: pairs in which Galaxy had more correct runs (the custom-code runs that failed), pairs in which custom code had more (the Galaxy runs that failed), and pairs with the same count.
Hatching marks runs for which the audit named answer validation and the benchmark specification as primary and secondary causes.
The six incorrect runs of the better condition in discordant pairs are in Source Data.
Right, a traced discordant case.
A run is correct when accepted or, for IWC, at ≥ 0.99 agreement.
Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). *P* values come from paired cluster sign-flip tests (200,000 draws; exact for IWC).
Extended Data Fig. 2 gives the full census of causes and the sensitivity analyses.
