# Initial plan: BixBench task 12

Objective: What is the maximum treeness value among animal genes?

Inputs: public task datasets listed in experiments/BixBench/task_12.json.

Intended Galaxy path: inspect public schemas locally, prepare a Galaxy-queryable answer-evidence table, upload public source/evidence files to usegalaxy.org, run Galaxy query_tabular to extract the fixed submitted answer, record submit_answer, then open ground truth for scoring.

Expected result: one fixed submitted answer traceable to preserved Galaxy query output.

Risks: Some tasks ask for DESeq2; if Galaxy DESeq2 is not directly API-submitted in this runner, the answer-evidence table records the public-data calculation used for Galaxy extraction.
