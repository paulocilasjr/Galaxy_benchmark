**Fig. 2 \| Agents show similar observed benchmark performance in Galaxy and custom code.**
**a**, Score of each model in the custom-code (squares) and Galaxy (circles) conditions, under each benchmark's scoring contract: acceptance as graded on the results site, that is, by the original evaluator with bix-53-q2 and bix-43-q2 regraded (BixBench-Verified-50; 150 runs per point), agreement with a reconstructed answer key (CompBioBench; 300 runs) and mean agreement with curated workflow outputs on a 0–1 scale (IWC, 10 tasks including host-read removal; 30 runs).
Dots, replicates.
**b**, Galaxy minus custom code for each model and for the four models pooled (diamonds), for two estimands kept apart: the mean score (IWC agreement × 100) and the share of replicate sets (one task × model × condition, three runs) with all three runs correct (IWC, agreement ≥ 0.99).
No difference was significant after Holm adjustment (smallest adjusted *P* = 0.19, GPT-5.5 on IWC); this does not establish equivalence, and no equivalence margin was prespecified.
With ten IWC tasks, bootstrap intervals are too narrow: the pooled IWC agreement difference, +3.6 points (0.6 to 7.4), has an exact *P* of 0.055.
**c**, Correct runs of three for each task–model pair in custom code (columns) and Galaxy (rows), per benchmark; outlined cells have equal counts.
Equal counts mean equal replicate success, not identical answers or methods.
**d**, Primary cause of incorrect BixBench-Verified-50 runs, from an AI-assisted run-level audit. The runs are grouped by pair type: pairs in which Galaxy had more correct runs (the custom-code runs that failed), pairs in which custom code had more (the Galaxy runs that failed), and pairs with the same count.
Four bix-43-q2 runs graded incorrect only by the site's regrade take the task-level audit's cause (benchmark specification or scoring).
Hatching marks runs for which the audit named answer validation and the benchmark specification as primary and secondary causes.
The seven incorrect runs of the better condition in discordant pairs are in Source Data.
Right, a traced discordant case.
A run is correct when accepted or, for IWC, at ≥ 0.99 agreement.
Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). *P* values come from paired cluster sign-flip tests (200,000 draws; exact for IWC).
Extended Data Figs 2 and 6: cause census, sensitivity analyses (including answer exposure) and a second audit.
