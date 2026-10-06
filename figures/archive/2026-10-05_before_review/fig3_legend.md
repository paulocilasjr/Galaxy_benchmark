**Fig. 3 \| Galaxy provides a structured environment for agent analyses.**
**a**, Runs correct by task domain (squares, custom code; circles, Galaxy): CompBioBench domains as labelled by the benchmark (spatial and structure merged), BixBench-Verified-50 and IWC; tasks in parentheses.
No domain differs after Holm adjustment (smallest adjusted *P* = 0.56).
**b**, How each traced Galaxy run used Galaxy, from the jobs it submitted through the agent interface: installed tools only, installed tools and user-defined tools (UDTs; agent-written code run as a Galaxy job), UDTs only, or neither.
Numbers are percentages of runs; UDTs were not offered on IWC.
**c**, Execution errors by type and by where they occurred: Galaxy jobs of installed tools or of UDTs, and failed shell commands (a silent exit code 1 is not counted) in Galaxy and custom-code runs.
Types follow each error's message, exit code and command; right, errors and errors per run (1,859 Galaxy and 1,908 custom-code runs with records).
**d**, Runs ending correct by the number of execution errors in the run.
Circles group runs with the same number of errors (area proportional to runs); lines are logistic fits on ln(1 + errors) with 95% cluster-bootstrap bands.
The annotated comparison averages the Galaxy minus custom-code difference over four error bins (1–2, 3–5, 6–10, >10), weighted by their share of runs with errors; it was chosen after inspecting the bins (unadjusted, +2.3 points, *P* = 0.07).
**e**, Parameter checks on 17,180 installed-tool requests: the interface compares the parameters the agent requested with those Galaxy validated before the job or recorded after it.
**f**, Failed Galaxy requests (7,354) grouped by the change that would most likely prevent them; the failure classes come from the request and job records, and their grouping is ours (classes in Source Data).
Tool runtime errors cannot be attributed to the agent or the tool from the records alone.
A run is correct when accepted or, for IWC, at ≥ 0.99 output agreement.
Error bars, 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks).
*P* values come from paired cluster randomization tests (200,000 draws).
