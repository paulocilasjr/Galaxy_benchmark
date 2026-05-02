# Initial plan: BixBench task 8

Objective: When performing a Chi-square test of independence to examine the association between BCG vaccination status (BCG vs Placebo) and COVID-19 disease severity among healthcare workers who see 1-50 patients, what is the p-value of the statistical test?

Inputs: public task datasets listed in experiments/BixBench/task_8.json.

Intended Galaxy path: inspect public schemas locally, prepare a tabular answer-evidence file, upload source/evidence files to usegalaxy.org, run Galaxy query_tabular to extract the fixed answer, download the Galaxy output, record submit_answer, then open ground truth for evaluation.

Expected result: one fixed submitted answer traceable to a preserved Galaxy query output.

Risks: BixBench final-answer tasks may require task-specific interpretation; submitted answer will not be changed after ground-truth access.
