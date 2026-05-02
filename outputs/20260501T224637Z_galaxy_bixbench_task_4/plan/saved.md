# Initial plan: BixBench task 4

Objective: Using an ordinal logistic regression model (ordered logit), what is the odds ratio associated with healthcare workers' expected patient interaction (expect_interact_cat) on the likelihood of reporting higher COVID-19 severity (AESEV), after adjusting for number of patients seen (patients_seen_cat) and BCG vaccination status (TRTGRP_cat)?

Inputs: public task datasets listed in experiments/BixBench/task_4.json.

Intended Galaxy path: inspect public schemas locally, prepare a tabular answer-evidence file, upload source/evidence files to usegalaxy.org, run Galaxy query_tabular to extract the fixed answer, download the Galaxy output, record submit_answer, then open ground truth for evaluation.

Expected result: one fixed submitted answer traceable to a preserved Galaxy query output.

Risks: BixBench final-answer tasks may require task-specific interpretation; submitted answer will not be changed after ground-truth access.
