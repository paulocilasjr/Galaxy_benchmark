# Benchmark Card

## Name

Galaxy-Bench v0.3

## Primary Question

How much do Galaxy-mediated execution and iterative refinement improve the combined performance of an agent and its harness on biomedical tasks, and how scientifically valid are the resulting analyses?

## Core Per-Run Scores

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

## Core Benchmark Endpoints

- `pipeline_completion_rate`
- `first_run_completion_rate`
- `best_of_n_completion_rate`
- `improvement_trajectory`
- `tool_selection_accuracy`
- `workflow_coherence`
- `parameterization_accuracy`
- `preprocessing_accuracy`
- `result_quality`
- `scientific_acceptability`
- `output_agreement`
- `confidence_calibration`

## Primary Environments

- `open`
- `galaxy`

Optional diagnostic environment:

- `galaxy_skills`

## Iteration Settings

- `single_run`
- `multi_run`

## Prompt Variants

- `low_context`
- `medium_context`
- `high_context`

## Intended Use

Use this benchmark to evaluate:

- whether Galaxy improves agent execution reliability
- whether iteration improves performance beyond the first attempt
- whether the agent can work coherently inside Galaxy
- whether the agent remains robust to prompt variation
- whether preprocessing and parameter configuration are handled correctly
- whether multiple acceptable solutions are recognized fairly
- whether confidence is calibrated to outcome

## Misuse To Avoid

- reducing the benchmark to a single aggregate score
- reporting only best-of-N success without first-run performance
- claiming scientific validity from Galaxy execution quality alone
- claiming Galaxy competence from final artifact correctness alone
- using hidden assets during blind execution
- ignoring provenance and retry evidence
