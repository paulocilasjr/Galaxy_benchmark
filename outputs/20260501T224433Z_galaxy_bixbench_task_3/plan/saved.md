# Initial plan: BixBench task 3

Objective: What is the odds ratio of higher COVID-19 severity (encoded in the column AESEV) associated with BCG vaccination in a multivariable ordinal logistic regression model that includes patient interaction frequency variables as covariates?

Inputs: public task datasets listed in experiments/BixBench/task_3.json.

Intended Galaxy path: inspect public schemas locally, prepare a tabular answer-evidence file, upload source/evidence files to usegalaxy.org, run Galaxy query_tabular to extract the fixed answer, download the Galaxy output, record submit_answer, then open ground truth for evaluation.

Expected result: one fixed submitted answer traceable to a preserved Galaxy query output.

Risks: BixBench final-answer tasks may require task-specific interpretation; submitted answer will not be changed after ground-truth access.
