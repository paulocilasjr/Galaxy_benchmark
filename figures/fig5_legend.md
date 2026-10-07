**Fig. 5 \| Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks.**
**a**, Galaxy relative to custom code in input (including cached context), uncached input and output tokens, per benchmark.
Diamonds (primary), the geometric mean over task–model cells of the ratio of median tokens per run; circles, the ratio of total tokens over the same cells.
On IWC, Galaxy did not use clearly more input (1.8×, 95% interval 0.9–3.4; aggregate 0.89×).
Below, incorrect relative to correct runs of the same task and model.
Ratios are not monetary costs.
**b**, Left, Galaxy relative to custom code in actions (tool calls) and input tokens per action.
Right, characters Galaxy returned to the agent, by request type (1,908 traced runs); a reply enters the context once, then is reread from cache.
**c**, Galaxy / custom-code tokens per complete 50-task BixBench-Verified-50 run, before and after rounds of interface changes, in two separate comparisons.
July (GPT-5.5; round 1, shorter skills and prompt guidance, in place): round 2 moved submission, waiting and parameter checks into one call that returns compact results; both conditions were rerun.
October (GPT-5.6 Sol; archived custom-code runs): round 3 shortened and deduplicated replies and added submission templates, then longer waits between model requests.
Batch comparisons, not effects of single changes; the agent CLI version also changed.
**d**, What the retained record holds for each analysis step (Galaxy jobs; custom-code shell commands labelled as analysis): structured, a field in the Galaxy job record (for UDTs, a versioned container) or, for exit codes, the agent trace; free text, commands or printed output in the trace; partial, an environment image or history metadata only; not retained, evidence the benchmark did not keep, such as custom-code output files (unknown, not absent).
The whole-analysis row counts runs with a retrieved Galaxy history; nothing was rerun.
**e**, One analysis step recorded in both conditions.
A run is correct when accepted on the results site or, for IWC, at ≥ 0.99 output agreement.
Intervals, 95% percentile cluster-bootstrap (clusters are BixBench source capsules, otherwise tasks). *P* values (Source Data) come from paired cluster sign-flip tests (200,000 draws; exact for IWC).
