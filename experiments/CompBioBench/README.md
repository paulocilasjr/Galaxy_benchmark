# CompBioBench Experiments

This directory contains a faithful import of the public CompBioBench v1 task set into the Galaxy Benchmark repository as a separate benchmark group.

Source article: Agentic systems are adept at solving well-scoped, verifiable problems in computational biology (10.64898/2026.04.06.716850)

Source dataset: https://huggingface.co/datasets/Genentech/compbiobench-data-v1

## Import Structure

- `task_1.json` through `task_100.json` contain one task each.
- `experiments.json` is the aggregate manifest keyed by CompBioBench `question_id`.
- `source_compbiobench.v1.tsv` is the public source TSV used for the import.
- Referenced input files are not downloaded here; each task lists both the intended local path under `dataset/compbiobench_inputs/` and the official Hugging Face `source_url`.

## Prompt Handling

Each task preserves the original CompBioBench prompt in `original_prompt_task`. The `prompt_task` field appends a Galaxy Benchmark execution/provenance sentence so imported tasks fit this repository's execution model while leaving the source prompt auditable.

## Ground Truth

The public CompBioBench data repository exposes questions, metadata, and input files, but not answer strings. The leaderboard evaluates answers by exact string match against a non-public key. Ground-truth status is documented in `../../ground_truth/CompBioBench/`.
