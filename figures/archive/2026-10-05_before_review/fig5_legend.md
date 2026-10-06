**Fig. 5 \| Galaxy increases analysis inspectability at higher token cost.**
**a**, Accuracy against median input tokens per run, including cached context, for each replicate of each model and condition (one run per BixBench-Verified-50 and CompBioBench task; 146–150 runs with token counts per point); colour, model; squares, custom code; circles, Galaxy.
Numbers give how many times more input tokens Galaxy used on the same task and, for all four models, counting only uncached input (150 task cells per model; all *P* < 0.001); accuracy differences are not significant (Fig. 2a).
**b**, Input tokens of correct (light) and incorrect (solid) runs.
Numbers compare incorrect with correct runs of the same task and model, in replicate sets with both outcomes (93 custom-code and 70 Galaxy sets); headers pool the four models.
**c**, Input tokens against actions (agent tool calls) for correct runs; lines join medians within bins of actions (bins with at least ten runs).
On the same task, Galaxy runs took 2.5 times more actions and used 1.9 times more input tokens per action.
**d**, Share of requests to Galaxy (left) and of the text Galaxy sent back, in characters (right), by what the request was for (1,908 traced Galaxy runs).
Notes give the share of tools read about but never run in the same run (range over benchmarks) and the median share of input reread from the prompt cache.
A run is correct when accepted or, for IWC, at ≥ 0.99 output agreement.
Boxes, middle 50% and median; whiskers, 1.5 times the interquartile range.
Ratios are geometric means over paired cells; *P* values come from two-sided paired cluster sign-flip tests (200,000 draws), Holm-adjusted within each panel; intervals are in Source Data.
