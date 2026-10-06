**Fig. 4 \| Galaxy trades input tokens for analysis provenance.**
**a**, Accuracy against median input tokens per run, including cached context, for each replicate of each model and condition (one run per BixBench-Verified-50 and CompBioBench task; 146–150 runs with token counts per point); colour, model; squares, open-ended code; circles, Galaxy.
Numbers give how many times more input tokens Galaxy used on the same task (150 task cells per model; all *P* < 0.001); accuracy differences are not significant (Fig. 2a).
**b**, Input tokens of correct (light) and incorrect (solid) runs.
Numbers compare incorrect with correct runs of the same task and model, in replicate sets with both outcomes (93 open-ended code and 70 Galaxy sets); headers pool the four models.
**c**, Input tokens against actions for correct runs; lines join medians within bins of actions (bins with at least ten runs).
Actions are agent tool calls: shell commands, Galaxy interface calls, web searches or fetches, and file operations.
On the same task, Galaxy runs took 2.5 times more actions and used 1.9 times more input tokens per action.
**d**, Each Galaxy interaction is a request from the agent and a text reply from Galaxy; bars give, for all traced Galaxy runs (1,908), the share of requests (left) and of reply text, in characters (right), by what the request was for.
Replies stay in the model's context and are reread at every later step, so reply text drives input tokens.
Notes give the share of tools an agent read about that the same run never ran (range over benchmarks) and the median share of input tokens reread from the prompt cache.
A run is correct when accepted or, for IWC, at ≥ 0.99 output agreement.
Boxes, middle 50% and median; whiskers, 1.5 times the interquartile range.
Ratios are geometric means over paired cells; *P* values come from two-sided paired cluster sign-flip tests (200,000 draws), Holm-adjusted within each panel; intervals are in Source Data.
