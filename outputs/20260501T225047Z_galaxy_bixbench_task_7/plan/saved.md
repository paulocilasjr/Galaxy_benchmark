# Initial plan: BixBench task 7

Objective: For healthcare workers seeing over 100 patients, what is the statistical significance (p-value) of the association between vaccination status and disease severity?

Inputs: public task datasets listed in experiments/BixBench/task_7.json.

Intended Galaxy path: inspect public schemas locally, prepare a tabular answer-evidence file, upload source/evidence files to usegalaxy.org, run Galaxy query_tabular to extract the fixed answer, download the Galaxy output, record submit_answer, then open ground truth for evaluation.

Expected result: one fixed submitted answer traceable to a preserved Galaxy query output.

Risks: BixBench final-answer tasks may require task-specific interpretation; submitted answer will not be changed after ground-truth access.
