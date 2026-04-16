# Benchmark Card

## Name

Galaxy Benchmark v0.3

## Primary Question

How much does Galaxy Workbench improve the combined performance of an agent and its harness on biomedical tasks, and how competently does that system operate within Galaxy itself?

## Core Per-Run Scores

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

## Core Benchmark Endpoints

- `pipeline_completion_rate`
- `tool_selection_accuracy`
- `workflow_coherence`
- `parameterization_accuracy`
- `preprocessing_accuracy`
- `result_quality`
- `output_agreement`
- `confidence_calibration`

## Primary Environments

- `open`
- `galaxy`

Optional diagnostic environment:

- `galaxy_skills`

## Prompt Variants

- `low_context`
- `medium_context`
- `high_context`

## Intended Use

Use this benchmark to evaluate:

- whether Galaxy improves agent execution reliability
- whether the agent can work coherently inside Galaxy
- whether the agent remains robust to prompt variation
- whether preprocessing and parameter configuration are handled correctly
- whether confidence is calibrated to outcome

## Misuse To Avoid

- reducing the benchmark to a single aggregate score
- claiming scientific validity from Galaxy execution quality alone
- claiming Galaxy competence from final artifact correctness alone
- using hidden assets during blind execution
- ignoring provenance and retry evidence
