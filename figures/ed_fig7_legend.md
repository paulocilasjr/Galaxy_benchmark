**Extended Data Fig. 7 \| Verification, recovery and selected cases.**
**a**, Verification checks in 80 runs sampled at 10 per benchmark (BixBench-Verified-50, CompBioBench) × condition × outcome, coded by AI coders blind to the grade (the condition is visible in a transcript).
A check counts when the agent explicitly tested something its answer depended on: counts or denominators; recomputation by a second method; sensitivity to a parameter or definition; an input assumption; plausibility; or a domain diagnostic.
Right, runs in which a check changed the method or the answer.
Intervals, 95% Wilson intervals.
**b**, Failed steps later re-run without error in the same run.
A Galaxy job in the error state counts as resolved when a later job of the same tool (or a later UDT job) completed. A failed shell command counts as resolved when a later command of the same analysis program or script exited 0; inline code, file inspection and downloads are excluded.
Right, the share of runs that ended correct, for resolved and unresolved failures.
Resolution means the step later ran without error, not that the error was understood or the result was right.
Intervals are 95% cluster-bootstrap intervals over tasks.
**c**, A parameter check from the agent interface. The first request nested the gene-set library name, which Galaxy would have bound to an empty value; the job was not submitted, and the agent resubmitted with flat keys.
**d**, A selected CompBioBench case in which read-end artefacts mimic an alternate allele: the outcome of each of the 24 runs, and the runs that ran a read-position diagnostic (a UDT in Galaxy, or a command in custom code).
Answers are not shown.
