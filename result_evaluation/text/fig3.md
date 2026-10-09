# Figure 3 | Galaxy provides a structured environment for agent analyses

This figure asks what running analyses through Galaxy changed in how agents worked, beyond final correctness: whether correctness held in every task domain, how agents used Galaxy's jobs, how often steps failed and were fixed, and what Galaxy's job and parameter records reveal about failures. It matters because the study evaluates Galaxy as an execution environment. Its records should therefore show where agents used it, where it caught or caused problems, and which infrastructure changes might help.

## Fig. 3a | Does running in Galaxy change the share of runs correct in any task domain?
panel: fig3a

### Rationale
- **Data.** All 3,840 scored primary runs (160 tasks × four model configurations × three replicates × two conditions). BixBench-Verified-50 grades are those displayed on the results site (the original evaluator's, with documented regrades of bix-53-q2 and bix-43-q2), and IWC includes host-read removal. CompBioBench tasks are grouped by the benchmark's own domain labels (spatial and structure merged); BixBench-Verified-50 (50 tasks) and IWC (10 tasks) are shown whole. The unit is the run.
- **Variables.** x is the share of runs correct. A run counts as correct when the BixBench-Verified-50 or CompBioBench evaluator accepts it, or when IWC output agreement is at least 0.99; completing without error is not enough. Rows are domains, with CompBioBench domains sorted by the Galaxy estimate and task counts in parentheses.
- **Analysis.** The share correct per domain and condition, with 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Each domain's Galaxy minus custom-code difference is tested by a paired cluster randomization test (200,000 draws, or exact enumeration with 16 or fewer clusters), Holm-adjusted across the nine domains.
- **Reading the plot.** Orange squares, custom code; blue circles, Galaxy; horizontal lines, 95% intervals. The grey rule separates the CompBioBench domains from the other two benchmarks.

### Conclusion
No domain showed a detectable difference between conditions (Holm-adjusted *P* ≥ 0.56 for all nine). Point differences ranged from −1.5 points (Transcriptomics) to +8.3 points (Machine learning: Galaxy 100%, custom code 92%, 95% interval 87–96%; unadjusted *P* = 0.06). For BixBench-Verified-50, 87.7% (79.2–94.1%) of Galaxy runs and 87.2% (79.0–93.6%) of custom-code runs were correct. Intervals are wide for small domains (Spatial and structure, 3 tasks; IWC, 10 tasks). There, the panel cannot rule out moderate differences.

## Fig. 3b | Which Galaxy routes did agents use in each run, and how often were those runs correct?
panel: fig3b

### Rationale
- **Data.** 1,908 traced Galaxy-condition runs of the four model configurations (600 BixBench-Verified-50, 1,188 CompBioBench, 120 IWC); twelve CompBioBench runs have no trace. Job submissions and job states come from the agent-interface call records extracted from the traces. Correctness comes from the grades of Fig. 3a (BixBench-Verified-50 as displayed on the results site; IWC including host-read removal, so every traced IWC run is scored). The unit is the run.
- **Variables.** Each run gets one route from the jobs it submitted through the interface's two job-running calls: completed installed-tool jobs only, both installed-tool and UDT jobs, UDT jobs only, jobs submitted but none completed, or no job. Bars give the share of each configuration's runs on each route. The right-hand columns give traced runs and the share of them correct.
- **Analysis.** Descriptive only. Correctness by route (pooled over models, in Source Data) is descriptive, because the agent chose the route.
- **Reading the plot.** One 100% bar per model configuration, grouped by benchmark; numbers are percentages of runs, with small segments labelled above the bar. Dark blue, installed tools only; mid blue, both; pale blue, UDTs only; dark grey, all jobs failed; light grey, no job (UDTs were not offered for IWC).

### Conclusion
Routes varied more between model configurations than correctness did. On BixBench-Verified-50, GPT-5.6 Sol used installed tools only in 65% of runs, GPT-5.5 used UDTs only in 45%, and DeepSeek V4 Pro submitted no job in 38%. Yet the share correct ranged only from 82% to 91%. On CompBioBench, GPT-5.5 used UDTs only in 52% of runs. On IWC, 73–97% of runs used installed tools only. Pooled over models, BixBench-Verified-50 runs with no job were correct in 70% (57 runs), against 88–93% on routes with a completed job; this association is descriptive. The panel does not show where the analysis ran when no interface job completed.

## Fig. 3c | How often did each kind of execution step fail, what kinds of error occurred, and were failed steps fixed later?
panel: fig3c

### Rationale
- **Data.** 3,791 scored runs with execution records (1,871 Galaxy, 1,920 custom code); shell commands come from the agent traces and the left-hand job shares from the agent-interface call records. Error types and errors per run come from the archive's per-error table, which takes Galaxy jobs in the error state from the archived job records, so its job-error counts differ from the left-hand failures. Errors of the 24 IWC host-read removal runs were added, extracted with the archive's own rules.
- **Variables.** Left: the share of steps that failed in each channel, with step counts in parentheses (a silent exit code 1 is not a failed shell command). "Fixed later" is the share of failed steps re-run without error later in the same run: a job of the same tool, a later UDT job, or the same named analysis program. Right, error types in four groups; below, all execution errors per run.
- **Analysis.** Shares and errors per run are ratios of sums with 95% percentile cluster-bootstrap intervals (20,000 resamples; BixBench source capsules, otherwise tasks, resampled within each benchmark). Descriptive only; no test.
- **Reading the plot.** Circles, Galaxy runs; squares, custom-code runs; lines, 95% intervals. Each stacked bar gives the percentage of that channel's errors in each type group.

### Conclusion
UDT jobs failed most often: 41% (95% interval 36.8–45.0%), against 9.3% (7.9–10.8%) for installed-tool jobs. More than half of UDT errors (56%) were jobs that never started. Shell commands failed less often in Galaxy runs (4.9%, 4.6–5.1%) than in custom-code runs (8.6%, 7.9–9.3%). Even so, Galaxy runs had more errors per run (3.5, 3.1–4.0, against 2.7, 2.4–3.1); the intervals barely separate (Galaxy lower bound 3.14, custom-code upper bound 3.13), and no test was run. In every channel, 54–62% of failed steps were later re-run without error. A successful re-run does not show that the error was understood or that the result was right.

## Fig. 3d | Were runs with execution errors more often correct in Galaxy than in custom code?
panel: fig3d

### Rationale
- **Data.** The same 3,791 scored runs with execution records as in Fig. 3c (1,920 custom code, 1,871 Galaxy), with the grades of Fig. 3a. Of these, 2,875 runs had at least one execution error. The unit is the run.
- **Variables.** x is the number of execution errors in the run (failed shell commands plus Galaxy jobs in the error state), in five bins: 0, 1–2, 3–5, 6–10 and more than 10. y is the share of runs correct. Run counts per bin and condition are printed below the axis.
- **Analysis.** Per-bin shares have 95% percentile cluster-bootstrap intervals (20,000 resamples). The primary estimate is the unadjusted Galaxy minus custom-code difference among runs with errors; an exploratory estimate averages it over the four error bins, weighted by pooled bin size, with bins chosen after inspection. Both *P* values come from paired cluster randomization tests that swap condition labels within clusters (200,000 draws).
- **Reading the plot.** Orange squares and line, custom code; blue circles and line, Galaxy; vertical lines, 95% intervals. The lines join the bin estimates only to guide the eye.

### Conclusion
The primary comparison detected no difference. Among runs with errors, Galaxy runs were correct 1.6 points more often than custom-code runs (*P* = 0.18). The exploratory error-bin-adjusted difference was +2.8 points (*P* = 0.02). In both conditions, correctness fell as errors increased. The fall was larger in custom code (92.1% with no errors to 62.0% with more than 10) than in Galaxy (89.6% to 74.8%). Error counts are themselves outcomes of the run. The panel therefore shows an association, not recovery from individual failures.

## Fig. 3e | When agents requested installed tools, did Galaxy's record match the parameters they asked for?
panel: fig3e

### Rationale
- **Data.** 16,757 installed-tool requests from traced Galaxy runs of the four model configurations (4,414 BixBench-Verified-50, 11,175 CompBioBench, 1,168 IWC), taken from the agent-interface call records. For each request, the interface compares the requested parameters with those Galaxy validated before the job or recorded after it. The unit is the request.
- **Variables.** Each request has one of five outcomes: matched; different value, blocked before the job; different value, job ran (Galaxy recorded a different value); requested value not recorded (no counterpart in Galaxy's record, as with defaults or reformatting); or no comparison (no parameters or no result). A follow-up measure records whether the run later completed a job of the same tool after a blocked request.
- **Analysis.** Descriptive only: counts and shares, with no intervals or tests.
- **Reading the plot.** One 100% bar per benchmark and one for all requests. Numbers are percentages, and small segments are labelled above the bar. The note below the bars gives the follow-up after blocked requests.

### Conclusion
Galaxy's record matched the requested parameters for 57% of requests. A different value was caught before the job in 10% (1,700 requests) and recorded after the job ran in 3%. For 15%, Galaxy recorded no counterpart to the requested value, and 16% could not be compared. IWC had the largest share of jobs that ran with a different value (11%). After a blocked request, the run later completed a job of the same tool in 71% of the 1,700 cases, with matching parameters in 52%. A match shows that Galaxy ran what was asked, not that the settings were scientifically appropriate.

## Fig. 3f | Which infrastructure changes could prevent the most failed Galaxy requests?
panel: fig3f

### Rationale
- **Data.** 7,141 failed calls to the Galaxy agent interface, from the agent traces of the four model configurations; 1,339 Galaxy runs had at least one. Each failure has one of 15 classes from the archive's ordered, rule-based classifier. The unit is the failed request; runs are also counted per group.
- **Variables.** Classes are grouped by the change most likely to prevent them (codebook in Source Data): six attributable groups (API design, error diagnostics, tool and parameter descriptions, datatypes and uploads, server capacity, UDT support) and two that cannot be attributed (tool runtime errors; other or unclassified). Bars give each group's requests and share of all failed requests; the right-hand column gives the runs with at least one failure in the group.
- **Analysis.** Descriptive only, with an unvalidated codebook. An independent AI rater, blind to the rule, recoded 150 requests (10 per class; Extended Data Fig. 6d), which is an AI second rating, not human validation.
- **Reading the plot.** Blue bars, attributable groups sorted by size. Grey bars below the rule, groups that cannot be attributed. Labels give each group's count and percentage.

### Conclusion
API design was the largest attributable group (1,580 requests, 22%, in 651 runs). Error diagnostics came next (1,340, 19%; jobs that failed with no diagnostic message), then tool and parameter descriptions (1,154, 16%). Datatypes and uploads, server capacity and UDT support each accounted for 3–4%. About a third of failures (32%) could not be attributed: tool runtime errors (1,474, 21%) and other or unclassified (833, 12%). The AI rater gave the same class to 92% of sampled requests in rule-defined classes. For 89% (107 of 120) of the sampled requests whose class has an improvement group, that group was among those the rater chose; this is the share the subtitle reports. The panel ranks candidate changes; it does not show that any change would prevent these failures.

# Extended Data Fig. 3 | Task status, execution errors and final correctness

This figure gives the detail behind Fig. 3a, c and d: correctness for every task, model configuration and condition; all seven error types in each channel; and the error-bin analysis of Fig. 3d within each benchmark. It shows whether the pooled results depend on a few tasks or on one benchmark.

## Extended Data Fig. 3a | Are failures spread across tasks, or concentrated in a few tasks that fail in both conditions?
panel: ed3a

### Rationale
- **Data.** All 3,840 scored primary runs on 160 tasks (50 BixBench-Verified-50, 100 CompBioBench, 10 IWC), graded as in Fig. 3a (BixBench-Verified-50 as displayed on the results site; IWC including host-read removal). The unit is a cell of three replicate runs for one task, model configuration and condition: 1,280 cells.
- **Variables.** Columns are tasks, grouped as BixBench-Verified-50, then the CompBioBench domains, then IWC, and sorted within each group by mean correct runs across cells. Rows are the four model configurations, each in custom code and in Galaxy. The shade of a cell gives its correct runs of three, with correctness defined as in Fig. 3a.
- **Analysis.** Descriptive only.
- **Reading the plot.** Black, 3 of 3; dark grey, 2 of 3; light grey, 1 of 3; near-white, 0 of 3. Each model's custom-code row sits directly above its Galaxy row, so the two conditions can be compared on the same task.

### Conclusion
Most cells were fully correct (1,016 of 1,280 at 3 of 3), and 80 of 160 tasks were correct in all 24 runs. Failures clustered in a minority of tasks and were usually shared by both conditions. Of the 15 tasks with at most half of their Galaxy runs correct, 13 also had at most half of their custom-code runs correct. Two tasks were never correct. A few tasks differed sharply between conditions in either direction: bix-45-q1 was correct in 8 of 12 custom-code runs and 0 of 12 Galaxy runs, and bix-30-q3 in 4 of 12 and 12 of 12. The panel shows where failures fall, not why.

## Extended Data Fig. 3b | Which kinds of execution error occurred in each channel?
panel: ed3b

### Rationale
- **Data.** All 11,878 execution errors in the 3,791 scored runs with execution records (1,871 Galaxy, 1,920 custom code): the archive's per-error table plus 71 errors in the 24 IWC host-read removal runs, extracted with the archive's own rules. Failed shell commands come from the agent traces, and Galaxy jobs in the error state come from the archived job records. A job error counts as a UDT error when its tool matches a UDT identifier in the interface calls.
- **Variables.** Ordered rules assign each error one of seven types from its message, exit code and command; "Galaxy job never started" is a job with neither a command line nor an output, and Fig. 3c merges the seven types into four. The right-hand column gives each channel's errors and errors per run (errors divided by the condition's runs).
- **Analysis.** Descriptive only: counts and shares.
- **Reading the plot.** One 100% bar per channel. Numbers are percentages of that channel's errors. Small segments are labelled above the bar, with "<1" for shares below 0.5%.

### Conclusion
Error types differed by channel. Installed-tool job errors were mostly code, parameter or syntax errors (64%), whereas UDT job errors were mostly jobs that never started (56%). Shell commands in custom-code runs had more missing-software errors (27% against 19%) and more time or memory limits (15% against 11%) than shell commands in Galaxy runs. Galaxy-run shell commands had more network or download errors (12% against 5%). Per run, Galaxy runs had 0.8 installed-tool, 1.1 UDT and 1.7 shell errors; custom-code runs had 2.7 shell errors. The types come from error text, so they describe the reported symptom, not the root cause.

## Extended Data Fig. 3c | Does the relation between execution errors and correctness in Fig. 3d hold within each benchmark?
panel: ed3c

### Rationale
- **Data.** The same 3,791 scored runs with execution records as in Fig. 3d, split by benchmark. Runs with errors number 858 for BixBench-Verified-50, 1,795 for CompBioBench and 222 for IWC (including host-read removal). The unit is the run.
- **Variables.** x is the number of execution errors in the run, binned as in Fig. 3d. y is the share of runs correct in each bin and condition. Each facet title gives the unadjusted Galaxy minus custom-code difference among runs with errors.
- **Analysis.** Per-bin shares with 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Bins with fewer than five runs would be omitted, but none had so few. *P* values come from paired cluster randomization tests (200,000 draws) and are not adjusted across the three benchmarks.
- **Reading the plot.** Orange squares, custom code; blue circles, Galaxy; vertical lines, 95% intervals. Each benchmark has its own facet on a 0–100% axis.

### Conclusion
No benchmark showed a detectable difference among runs with errors: +0.1 points for BixBench-Verified-50 (*P* = 0.98), +1.8 for CompBioBench (*P* = 0.19) and +6.9 for IWC (*P* = 0.052). In CompBioBench, correctness fell with more errors in both conditions, as in the pooled panel. In BixBench-Verified-50, Galaxy runs stayed 87–89% correct up to 10 errors, while custom-code runs fell from 92% (1–2 errors) to 78% (6–10); both were lowest above 10 errors. IWC bins hold 5–42 runs, so their intervals are wide (0–100% for custom code above 10 errors). The pooled result in Fig. 3d is weighted toward CompBioBench, which contributes 1,795 of the 2,875 runs with errors.
