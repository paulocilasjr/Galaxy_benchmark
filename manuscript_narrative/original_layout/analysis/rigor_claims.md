# Evidence for the failure-analysis section (Results 3)

Prepared from the archive without new benchmark execution, hidden ground-truth access or private key access. Produced by `scripts/rigor_analysis.py` (`rigor_results.json`, `rigor_task_cases.csv`, `rigor_census_categories.csv`, `rigor_persistence.csv`, `rigor_tag_overlap.csv`, `rigor_cases.csv`, `rigor_evidence.csv`) and `scripts/accuracy_analysis.py` (`accuracy_cross_arm_error_transitions.csv`, `accuracy_persistent_failure_overlap.csv`). Labels are AI-assisted; blinded expert adjudication is pending.

## The audit is a census of failing tasks

The 93 audited tasks are every BixBench task with a rejected run in any archived configuration (33), every CompBioBench task with a run deviating from the reconstructed key (53) and seven IWC workflows (six with a low-agreement run, one whose near-perfect agreement concealed a changed significant-gene set). `rigor_analysis.py` asserts that every BixBench and CompBioBench task with a rejected primary run is audited (22 and 51 tasks) and that the BixBench audit equals the set of tasks with any rejected run. Census analyses use these 73 binary-benchmark tasks. An earlier description of this audit as "targeted" understated its coverage: the selection rule is "at least one failure", applied exhaustively.

## Claims and evidence

**"When agents got an answer wrong, it was often gaps in rigor/validation, not biological or Galaxy knowledge."** Supported at task level. Among the 73 failing tasks: agent analysis is the primary cause in 42 (57.5%); benchmark reference, scoring or provenance in 23 (31.5%); Galaxy platform or wrapper in 7 (9.6%); other in 1. Insufficient verification is tagged in 42 tasks (57.5%) and in 34 of 42 agent-analysis tasks (81.0%). Domain knowledge is tagged in 21 tasks, 17 of them together with insufficient verification; domain knowledge alone accounts for 4 (5.5%). Weighted by rejected primary runs (485), benchmark-side tasks contribute 51.8%, because they tend to fail every attempt. Limits: labels are task-level and AI-assisted, and tags are not knowledge tests.

**"Agents often are not checking their work."** Supported by the tag counts and by five cases with positive recorded evidence (`rigor_cases.csv`, 16 hashed trace lines): a filter that dropped valid identifiers and an accepted reduced denominator (bix-52-q2); read-end artifacts read as alleles, contrasted with a read-position audit (variant-status-q1); in-sample fitting and scoring, contrasted with grouped hold-out (exogenous-mix-reads-q1); circularity and self-mapping taken as identity (IWC mitogenome); and a negative overlap check that did not change the conclusion (histone-chip-q1). Missing reasoning is never coded as absent validation.

**"Replicates show the error pattern — 3, 2 and 1 errors per task."** A replicate set is one task × configuration × arm with three attempts. One or two rejected attempts (sporadic) mean the same agent can succeed or fail on the same task; three (persistent) mean the failure repeats. Persistent sets recur across arms: 17 BixBench task–configuration pairs were rejected 3/3 in both arms (of 22 code and 20 Galaxy sets) and 15 on CompBioBench (of 25 in each arm). The arm difference in repeatability lies in mixed sets (19 versus 15 on BixBench; 66 versus 53 on CompBioBench).

**"Trajectory explains 1–2 errors; task specification or validation rigor explains 3."** Partly supported. Of 25 tasks with a persistent set, 12 have a benchmark, reference or provenance cause and 12 agent analysis (11 of these verification-tagged); of 48 tasks with only sporadic failures, 11 are benchmark-side, 30 agent analysis and 6 Galaxy platform. Persistent failures are therefore enriched for task-specification and reference problems, and Galaxy platform problems are almost always sporadic (6 of 7). Insufficient verification occurs in both groups (13 of 25; 29 of 48), so it does not distinguish them.

**"Galaxy errors are more recoverable than shell errors."** Not testable in this archive: no matched comparison of equivalent Galaxy and shell failure episodes exists. The run-level acceptance proxy in `rigor_recovery_proxy.csv` (an error event belongs to a run that later passed) is retained as an archival observation only. The nearest supported statement is that Galaxy platform failures were overcome in other attempts of the same task.

## Figure 4

a, primary cause groups for all 73 failing tasks and by benchmark; b, tag combinations for all failing tasks and agent-analysis tasks; c, cause groups for persistent and sporadic tasks; d, cross-arm transitions of rejected attempts for the same task × configuration; e, the five recorded cases.

## Required next step

Blinded expert review should freeze task- and run-level codebooks, separate biological knowledge, Galaxy operation, statistical rigor and evidence quality, allow overlapping causes, report inter-rater agreement and include a probability sample of successful runs.
