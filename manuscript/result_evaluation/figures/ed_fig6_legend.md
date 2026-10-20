**Extended Data Fig. 6 \| Independent checks of the audits and of benchmark integrity.**
**a**, Runs that reached a source of benchmark answers during the run, from their traces, by highest tier:
- answers seen: a command or connector output contained the task's reference answer, or other agents' recorded answers;
- page with answers: the run opened the public BixBench dataset or a published archive of other agents' traces (the page content is not logged);
- search: the run searched the web for the benchmark or the task;
- none.

Numbers are runs with answers seen or a page with answers, over all scored runs.
Most exposure came from DeepSeek V4 Pro and GPT-5.6 Luna runs, in both conditions.
**b**, Galaxy minus custom code in runs correct with all runs, without runs in the two exposure tiers, and without any run that searched for the benchmark, with 95% cluster-bootstrap intervals.
**c**, Primary cause of 45 BixBench-Verified-50 runs graded incorrect at the time of the audit (stratified by the original cause and condition) from the original audit and from an independent second rater. The second rater, an AI coder blind to the audit, saw the run's transcript, submitted answer and reference answer.
Causes are grouped as in Fig. 2d.
Seven of the 45 runs (six on bix-53-q2, one on bix-43-q2) are graded correct after the regrades of those tasks; both raters attributed all seven to the benchmark.
**d**, The same check for the failure classes of 150 failed Galaxy requests (10 per class). The coder assigned a class and the changes that would plausibly have prevented the failure, without seeing the rule-based class.
The share of requests whose rule-linked improvement group was among the coder's choices is computed over the 120 requests in classes that have a group (B3, X and Z have none).
X (other exceptions) and Z (unclassified) have no rule definition to reproduce.
Both checks are AI-assisted second ratings, not human validation; codebooks and coded data are in `figures/annotations/`.
