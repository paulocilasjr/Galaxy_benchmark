# Benchmark definition

What an agent is given when a benchmark task is run. [SKILL.md](../SKILL.md) is the execution contract that uses these files; new runs are written to `outputs/` at the repository root.

| Folder | Contents |
|---|---|
| [experiments/](experiments/) | Task prompts and allowed inputs. `low_context/`, `medium_context/` and `high_context/` are prompt variants of the same GalaxyBench tasks; `BioAgent/`, `BixBench/` and `CompBioBench/` hold those benchmarks' tasks. |
| [ground_truth/](ground_truth/) | Evaluator references. Controlled access: open them only when the evaluation procedure in SKILL.md allows it. BixBench ground truth stays closed until the submitted answer is fixed. CompBioBench has no public answer key (`ground_truth/CompBioBench/ground_truth_manifest.json`). |
| [dataset/](dataset/) | Local inputs of the GalaxyBench-style tasks. Inputs that task files list under `benchmark/dataset/compbiobench_inputs/` or `benchmark/dataset/bioagent_inputs/` are downloaded on demand and are not tracked. |

The archived runs analysed for the manuscript (BixBench-Verified-50, CompBioBench, IWC) were run by the lab's own harness, not from these files; their prompts are preserved with each run under [runs/](../runs/).
