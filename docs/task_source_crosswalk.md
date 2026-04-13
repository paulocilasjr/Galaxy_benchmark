# Task Source Crosswalk

This document records how benchmark tasks in this repository were reconciled against:

- `paulocilasjr/Galaxy_benchmark` `main`
- `paulocilasjr/Galaxy_benchmark` `benchmark_v0.2`
- `paulocilasjr/agent_galaxy_experiment` `main`

It also records one unresolved source reference:

- `goeckslab/galaxy-workflow-benchmark` branch `issue3/workflow`

On April 8, 2026, a direct GitHub API repository search for `goeckslab/galaxy-workflow-benchmark` returned no public repository result. No task assets from that source could be incorporated because the referenced repository could not be resolved.

## Direct Carry-Forward Coverage

The current benchmark already covers the public task inventory from `paulocilasjr/Galaxy_benchmark` `benchmark_v0.2`.

| Current experiment | Legacy source coverage |
|---|---|
| `experiment_1` | `Galaxy_benchmark` experiment 1; `agent_galaxy_experiment/exp_immunotherapy_chowell_tabular_learner` |
| `experiment_2` | `Galaxy_benchmark` experiment 2; `agent_galaxy_experiment/exp_skin_lesion_classification__ds_ham10000__tool_image_learner` |
| `experiment_3` | `Galaxy_benchmark` experiment 3; `agent_galaxy_experiment/exp_multimodal_dataset__ds_hancock_tma__tool_multimodal` and `exp_claude_multimodal_dataset` |
| `experiment_4` | `Galaxy_benchmark` experiment 4; `agent_galaxy_experiment/IWC_ATAC-seq_Workflow` |
| `experiment_5` | `Galaxy_benchmark` experiment 5 |
| `experiment_6` | `Galaxy_benchmark` experiment 6 |
| `experiment_7` | `Galaxy_benchmark` experiment 7 |
| `experiment_8` | `Galaxy_benchmark` experiment 8 |

## Newly Added Coverage

The following source experiments introduced distinct Galaxy-native task families not already represented here:

| New experiment | Source project task | Reason added |
|---|---|---|
| `experiment_9` | `agent_galaxy_experiment/Built_ML_workflow` | Adds workflow construction plus external-cohort validation rather than single-tool tabular classification |
| `experiment_10` | `agent_galaxy_experiment/IWC_ChIP-seq Analysis` | Adds workflow replay and output-equivalence comparison against a baseline workflow |
| `experiment_11` | `agent_galaxy_experiment/RNA-seq_From_Paper` | Adds literature-faithful RNA-seq paper reproduction with published-result validation |

## Explicit Non-Additions

These source experiments were not copied into new benchmark IDs because they were either duplicates of existing benchmark tasks or not Galaxy-native benchmark targets:

| Source experiment | Disposition |
|---|---|
| `exp_library_model_tabular` | Excluded: local sklearn baseline, not a Galaxy execution task; overlaps `experiment_1` scientifically |
| `exp_library_model_multimodal` | Excluded: local Python multimodal baseline, not a Galaxy execution task; overlaps `experiment_3` scientifically |
| `exp_claude_multimodal_dataset` | Excluded as a duplicate multimodal Galaxy task family already covered by `experiment_3` |

## Result

After deduplication, the repository benchmark inventory expands from 8 task groups to 11 task groups while preserving the prompt-tier contract under `experiments/low_context`, `experiments/medium_context`, and `experiments/high_context`.
