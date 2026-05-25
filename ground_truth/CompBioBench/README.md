# CompBioBench Ground Truth

No task-level CompBioBench answer key was imported.

The public source dataset (https://huggingface.co/datasets/Genentech/compbiobench-data-v1) contains task prompts, metadata, and input files. The public leaderboard code validates submissions with `question_id` and `answer` columns and reports exact-string-match accuracy, but the answer key is not exposed in the public dataset or leaderboard files.

`ground_truth_manifest.json` records all 100 task IDs with `ground_truth_available: false`. Add task-level ground-truth JSON files here only if an official public or evaluator-approved answer source becomes available.
