**Fig. 3 \| Galaxy provides a structured environment for agent analyses.**
**a**, Runs correct (accepted, not merely completed) by task domain (squares, custom code; circles, Galaxy): the CompBioBench domains, with spatial and structure merged, plus BixBench-Verified-50 and IWC; tasks are in parentheses.
No domain differs after Holm adjustment.
**b**, How each traced Galaxy run used Galaxy, from the jobs it submitted through the agent interface: completed jobs of installed tools, of user-defined tools (UDTs; agent-written code run as a Galaxy job) or of both; jobs that all failed; or no job.
Right, traced runs and the share of scored runs correct.
Agents chose their route, so its association with correctness is descriptive; twelve CompBioBench runs have no trace.
**c**, Share of execution steps that failed: Galaxy jobs of installed tools and of UDTs, and shell commands (a silent exit code 1 is not counted) in each condition, with the number of steps in parentheses.
Below, execution errors per run; right, error types classified from message, exit code and command (seven types in Extended Data Fig. 3b).
**d**, Runs correct by the number of execution errors in the run (failed shell commands plus Galaxy jobs in the error state; 3,767 runs with records).
Final correctness is not episode-level recovery, and error counts are themselves outcomes of the run.
The unadjusted difference among runs with errors is the primary estimate; the error-bin adjustment was chosen after inspecting the bins and is exploratory.
**e**, Parameter checks on 17,180 installed-tool requests, comparing the requested parameters with those Galaxy validated before the job or recorded after it.
A value not recorded has no counterpart in Galaxy's record, as with defaults or reformatting.
**f**, Failed Galaxy requests (four model configurations) by failure class from the request and job records, grouped by the change most likely to prevent them (an unvalidated codebook, in Source Data). Right, runs with at least one such failure; grey groups cannot be attributed from the records.
Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). *P* values come from paired cluster randomization tests (200,000 draws).
