# Initial plan: BixBench task 9

Objective: What is the percentage reduction in odds ratio for higher COVID-19 severity among healthcare workers expected to interact with patients versus those who do not, when controlling for BCG vaccination and number of patients seen?

Inputs: public task datasets listed in experiments/BixBench/task_9.json.

Intended Galaxy path: inspect public schemas locally, prepare a tabular answer-evidence file, upload source/evidence files to usegalaxy.org, run Galaxy query_tabular to extract the fixed answer, download the Galaxy output, record submit_answer, then open ground truth for evaluation.

Expected result: one fixed submitted answer traceable to a preserved Galaxy query output.

Risks: BixBench final-answer tasks may require task-specific interpretation; submitted answer will not be changed after ground-truth access.
