**Fig. 5 \| Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks.**
**a**, Token use in Galaxy relative to custom code, per benchmark: input (including cached context), uncached input and output tokens.
Diamonds (primary) give the typical paired task: the geometric mean, over task–model cells, of the ratio of median tokens per run. Circles give aggregate consumption: the ratio of total tokens over the same cells.
On IWC, Galaxy did not use clearly more input (1.7×, 95% interval 0.8–3.5; aggregate 0.90×).
Below, input tokens of incorrect relative to correct runs of the same task and model (models pooled); the intervals do not exclude sizeable differences.
Models price tokens differently, so ratios are not monetary costs.
**b**, Left, Galaxy relative to custom code in actions (the agent's tool calls) and input tokens per action, over all runs (correct runs only in Source Data).
Right, characters that Galaxy returned to the agent, by what the request was for (1,908 traced Galaxy runs).
Returned characters are not tokens: a reply enters the context once and is then reread from the prompt cache.
**c**, What the retained record holds for each analysis step (Galaxy jobs, and custom-code shell commands labelled as analysis), by level of record:
- structured: a field in the Galaxy job record or, for exit codes, in the agent trace;
- free text: recoverable from commands or printed output in the retained trace (for software, a version printed anywhere in the run);
- partial: an environment image recorded for the run, or history metadata only;
- not retained: evidence the benchmark did not keep, such as custom-code output files and workspaces. This is unknown, not absent.

The whole-analysis row counts runs with a retrieved Galaxy history; no analysis was rerun.
**d**, One analysis step recorded in both conditions, from the retained evidence.
A run is correct when accepted or, for IWC, at ≥ 0.99 output agreement.
Intervals are 95% percentile cluster-bootstrap intervals (clusters are BixBench source capsules, otherwise tasks). *P* values (Source Data) come from paired cluster sign-flip tests (200,000 draws; exact for IWC).
