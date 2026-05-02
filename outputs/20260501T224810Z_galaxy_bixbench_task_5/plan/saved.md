# Initial plan: BixBench task 5

Objective: In which patient volume group (number of patients seen) do healthcare workers show statistically significant differences (p<0.05) in COVID-19 severity between BCG vaccination and placebo groups based on chi-square analysis?

Inputs: public task datasets listed in experiments/BixBench/task_5.json.

Intended Galaxy path: inspect public schemas locally, prepare a tabular answer-evidence file, upload source/evidence files to usegalaxy.org, run Galaxy query_tabular to extract the fixed answer, download the Galaxy output, record submit_answer, then open ground truth for evaluation.

Expected result: one fixed submitted answer traceable to a preserved Galaxy query output.

Risks: BixBench final-answer tasks may require task-specific interpretation; submitted answer will not be changed after ground-truth access.
