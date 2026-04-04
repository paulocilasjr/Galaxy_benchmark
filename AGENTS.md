# Galaxy Benchmark Codex Guide

This is the startup guide for Codex sessions in this repository. Read this file first.

Then use:
- [README.md](/Users/4475918/Projects/Galaxy_benchmark/README.md) for the full benchmark protocol and reporting standard
- [SKILL.md](/Users/4475918/Projects/Galaxy_benchmark/SKILL.md) when the task is to execute benchmark experiments

## Project Intent

Galaxy Benchmark evaluates whether an AI agent can infer, plan, execute, adapt, and report real biomedical analyses in Galaxy.

The benchmark is intended to answer two top-level questions:

- Scientist-help question:
  What level of scientist can the agent meaningfully help, from more junior task support to more advanced biomedical workflow assistance?
- Galaxy-competence question:
  How well can the agent actually work inside the Galaxy environment, including dataset upload, history navigation, tool and workflow choice, parameterization, multistep execution, failure recovery, and adaptation toward better valid results?

The benchmark should produce a trust signal for biomedical work in Galaxy, not just a one-shot task score.

Core structural choices:

- realistic end-to-end tasks
- three prompt tiers for the same underlying task
- Galaxy-only execution after planning
- concrete output artifacts
- hidden evaluation plus post-run comparison to ground truth
- separate assessment of scientific usefulness and Galaxy operational competence
- explicit reporting of `scientific_solution_score`, `standard_analysis_score`, and `galaxy_execution_score`

## Core Benchmark Principles

Use these principles when creating, revising, or evaluating tasks:

1. Measure scientific usefulness and Galaxy competence separately.
- The benchmark should not collapse everything into one brittle field match.
- Each task should support three distinct judgments:
  - `scientific_solution_score`: the quality of the biomedical answer
  - `standard_analysis_score`: adherence to the requested or benchmark-standard analysis path
  - `galaxy_execution_score`: the quality of Galaxy manipulation and access behavior

2. Judge what the agent can help with, not only whether it copied a reference pipeline.
- A fair benchmark should reveal whether the agent behaves like a junior, intermediate, or advanced scientific assistant for that task class.
- This is why each task should carry a scientist-help label and a Galaxy-complexity label.

3. Favor valid biomedical outcomes over exact hidden pipeline imitation unless the task explicitly requires exact adherence.
- `high_context` tasks may require a specific Galaxy tool or workflow.
- `low_context` and most `medium_context` tasks should allow equivalent valid solutions unless the benchmark goal is exact instruction following.
- This means `standard_analysis_score` should become strict only when the prompt actually defines a standard path.

4. Keep scoring fair under real Galaxy conditions.
- Do not require broad parameter sweeps or architecture searches just to satisfy the benchmark.
- Do not punish an agent for getting a better valid metric than the reference threshold.
- Do not over-penalize harmless naming differences, minor workflow-version drift, or equivalent artifact formats.

5. Test real Galaxy operations directly.
- Good tasks should expose whether the agent can:
  - upload local files and fetch remote data
  - organize and inspect Galaxy histories
  - choose tools and workflows appropriately
  - set or infer parameters
  - monitor jobs and workflows correctly
  - recover from execution failures without blind retries
  - revise the plan when Galaxy behavior or tool constraints require adaptation
- These behaviors should feed `galaxy_execution_score`, not be mixed into scientific-method correctness unless the task explicitly requires that linkage.

6. Keep the three-score model explicit.
- `scientific_solution_score` concerns whether the user got a scientifically useful solution.
- `standard_analysis_score` concerns whether the agent followed the requested standard analysis.
- `galaxy_execution_score` concerns whether the agent worked competently inside Galaxy as an environment.
- Do not silently substitute one of these scores for another in task design or reporting.

7. Preserve auditability.
- Trust in biomedical settings requires inspectable run records.
- If a decision, retry, failure analysis, or adaptation is not recorded, it should not contribute to benchmark credit.

## Papers Guiding This Benchmark

This repository is intentionally shaped by the following papers:

- [SkillsBench](https://arxiv.org/abs/2602.12670): use focused, portable, file-based procedural guidance; avoid bloated instructions; prefer concise operational docs that help across a class of tasks rather than leaking solutions.
- [AGENTIF](https://arxiv.org/abs/2505.16944): treat instruction following as a core benchmark target; prompts and evaluators should make tool, condition, output, and reporting constraints explicit and auditable.
- [AgentIF-OneDay](https://arxiv.org/abs/2601.20613): benchmark tasks should feel like real user requests, consume attached files, and require tangible file-based deliverables rather than chat-only answers.
- [BioAgent Bench](https://arxiv.org/abs/2601.21800): prefer curated end-to-end bioinformatics tasks with concrete output artifacts and support robustness testing through controlled perturbations when appropriate.

## Priority Rules For Codex

When working in this repo:

1. Preserve the benchmark design:
- the same task should exist across `low_context`, `medium_context`, and `high_context`
- prompt specificity changes across tiers, but the underlying task, inputs, and target result contract do not

2. Respect public vs hidden benchmark assets:
- `experiments/` and `dataset/` are public benchmark inputs
- `evaluators/` and `ground_truth/` are hidden benchmark assets
- do not leak hidden evaluator or ground-truth information into public task files

3. Distinguish benchmark authoring from benchmark execution:
- when authoring the benchmark, editing `dataset/`, `experiments/`, `evaluators/`, `ground_truth/`, `docs/`, and root docs is allowed
- when executing a benchmark run, follow [SKILL.md](/Users/4475918/Projects/Galaxy_benchmark/SKILL.md) and write only inside `outputs/`

4. Keep instructions focused:
- prefer short, operational guidance over long narrative documents
- if adding more guidance, keep it modular and reusable rather than task-instance-specific

## Repository Structure

```text
.
|-- AGENTS.md
|-- README.md
|-- SKILL.md
|-- dataset/
|-- docs/
|-- evaluators/
|-- experiments/
|   |-- low_context/
|   |-- medium_context/
|   `-- high_context/
|-- ground_truth/
`-- outputs/
```

Directory roles:

- `dataset/experiment_N/`: files attached to a benchmark task
- `experiments/<level>/experiment_N.json`: public task definitions for each prompt tier
- `evaluators/experiment_N.json`: hidden evaluator metadata, success criteria, and rubric
- `ground_truth/experiment_N.json`: hidden reference answer used only after result generation
- `outputs/<timestamp>_<level>_<experiment>/`: run artifacts for one benchmark execution
- `docs/`: extended design notes or benchmark-authoring documentation

## Benchmark Design Principles

Every benchmark task should satisfy these design goals:

- Use a real Galaxy-solvable biomedical task, not a toy puzzle.
- Require end-to-end reasoning: task interpretation, tool or workflow selection, execution, and result extraction.
- Depend on attached files in `dataset/` so the task is grounded in actual inputs.
- Ask for concrete, machine-comparable result fields whenever possible.
- Separate public prompt content from hidden evaluation logic.
- Make traceability part of the task, not optional bookkeeping.

In addition, every task should be designed so that scoring can answer both:

- What is the level of scientific help the agent provided?
- How competently did the agent operate inside Galaxy?

For that reason, task design should prefer:

- scientific-answer fields that reflect the biomedical outcome or interpretation
- Galaxy-execution fields that reflect operational competence, such as tool/workflow choice, upload mode, history handling, and adaptation behavior

Prefer tasks that naturally test one or more of:

- open workflow execution
- latent instruction extraction from datasets or attachments
- iterative refinement after an initial attempt
- constraint following for tools, parameters, outputs, or report fields

## Prompt-Tier Contract

Each experiment must have three task files:

- `experiments/low_context/experiment_N.json`
- `experiments/medium_context/experiment_N.json`
- `experiments/high_context/experiment_N.json`

Across these three files:

- keep `task_id`, `task_group_id`, `task_family`, `execution_environment`, and `inputs` aligned
- change `level` and `user_prompt`
- keep the expected final result fields aligned across tiers
- if the task target, datasets, or required outcome changes materially, create a new experiment instead of a new tier

Tier definitions:

- `low_context`: minimally specified user request; the agent must infer the task structure, method, and sometimes the target from the datasets
- `medium_context`: clearer task framing, expected metric or deliverable, and some methodological hints, while still leaving meaningful choices open
- `high_context`: explicit tool, workflow, parameter, target-column, or reporting instructions; this tier measures compliance with detailed constraints

Practical rule:

- low-context measures inference
- medium-context measures informed planning
- high-context measures instruction adherence

## Galaxy Execution Contract

All task packages should encode Galaxy as the execution environment:

```json
{
  "execution_environment": {
    "platform": "Galaxy",
    "galaxy_instance": "https://usegalaxy.org/",
    "execution_rule": "After you form a plan for the analysis, execute that plan in Galaxy."
  }
}
```

Galaxy-specific benchmark rules:

- planning can consult Galaxy-native resources such as GTN, IWC, and Galaxy tool help
- once the plan is formed, execution should happen in Galaxy, not via substitute local pipelines
- prompts should request concrete Galaxy outputs, report fields, workflow properties, or artifact types
- evaluators should explicitly test whether Galaxy execution was respected
- benchmark runs must capture enough IDs and artifact paths to audit what happened in Galaxy

## Public Task File Schema

Each public task file should follow the current repository schema:

```json
{
  "format_version": "galaxy_benchmark_task_input_v2",
  "task_id": "experiment_N",
  "task_group_id": "experiment_N_<slug>_prompt_tiers",
  "level": "low_context",
  "task_family": "<family>",
  "benchmark_axes": {
    "scientist_level_band": "junior|intermediate|advanced",
    "galaxy_complexity_band": "basic|intermediate|advanced",
    "focus_capabilities": ["..."]
  },
  "required_result_format": {
    "format_name": "galaxy_benchmark_result_v2",
    "scientific_answer": {
      "required_fields": ["..."]
    },
    "galaxy_execution": {
      "required_fields": [
        "final_entity_type",
        "final_entity_name",
        "history_input_mode",
        "adaptation_summary"
      ]
    }
  },
  "execution_environment": {
    "platform": "Galaxy",
    "galaxy_instance": "https://usegalaxy.org/",
    "execution_rule": "After you form a plan for the analysis, execute that plan in Galaxy."
  },
  "inputs": {
    "datasets": [
      {
        "name": "<file>",
        "path": "dataset/experiment_N/<file>"
      }
    ]
  },
  "user_prompt": "..."
}
```

Authoring rules for `user_prompt`:

- write it like a real user request, not like evaluator instructions
- mention the attached data naturally
- ask for final outputs that can be checked against `ground_truth/`
- use the high-context tier for exact tool or workflow constraints
- do not mention hidden answers, rubric logic, or evaluator-only criteria
- do not encode unfair compute expectations such as arbitrary large parameter sweeps
- request outputs that reveal both scientific usefulness and Galaxy execution quality when possible

Result-format rules:

- `scientific_answer` should contain the task-specific biomedical result
- `galaxy_execution` should contain the task-specific Galaxy-operation summary
- the benchmark should be able to derive `scientific_solution_score`, `standard_analysis_score`, and `galaxy_execution_score` from the hidden evaluation assets
- do not invent one-off ad hoc result schemas when the shared `galaxy_benchmark_result_v2` structure is sufficient

## Hidden Evaluator Requirements

Each `evaluators/experiment_N.json` should define, at minimum:

- `source_task_files`
- `benchmark_metadata`
- `resource_discovery_targets`
- `canonical_task_interpretation`
- `hidden_dataset_profile`
- `expected_result_fields`
- `score_model`
- `variant_success_criteria`
- `deterministic_checks`
- `evaluation_rubric`
- `reference_answers_source`
- `benchmark_gaps_covered`

Evaluator design rules:

- encode the same task across prompt tiers, with tier-specific success criteria
- list the expected result fields under `scientific_answer` and `galaxy_execution`
- define deterministic checks whenever possible
- use rubric dimensions to separate context extraction, planning, execution, and reporting quality
- reserve hidden evaluator details for scoring, not for public prompt leakage

Fairness rules for evaluators:

- use exact matching only when exact matching is scientifically justified
- use alias matching for equivalent labels when appropriate
- use threshold scoring for metrics where higher is better
- use tolerances when live Galaxy workflow versions can change harmless structural details
- use overlap-based comparison for outputs such as gene sets when exact identity is too brittle
- score scientific validity and Galaxy competence separately before any aggregate score
- make the mapping to `scientific_solution_score`, `standard_analysis_score`, and `galaxy_execution_score` explicit in the evaluator logic
- keep `galaxy_execution_score` restricted to Galaxy interaction, monitoring, recovery, and provenance rather than analytical correctness alone

Evaluator intent:

- `scientific_answer` should support `scientific_solution_score`
- explicit standard-path constraints should support `standard_analysis_score`
- `galaxy_execution` should support `galaxy_execution_score`

Score-model rule:

- `scientific_solution_score`: scientific usefulness of the solution
- `standard_analysis_score`: adherence to the requested or benchmark-standard method
- `galaxy_execution_score`: competence in manipulating and accessing Galaxy

See [docs/formal_score_model.md](/Users/4475918/Projects/Galaxy_benchmark/docs/formal_score_model.md) for the benchmark-wide formal definition.

## Ground Truth Rules

`ground_truth/experiment_N.json` should follow `galaxy_benchmark_ground_truth_v2` and support fair comparison.

Each ground-truth file should also expose, under `fair_scoring`, a `score_model_support` mapping that makes the three-score split explicit and set `preserve_three_score_vector` to keep the score vector intact.

Prefer:

- stable strings when exact values are truly required
- threshold metrics when better performance should still pass
- alias lists for equivalent names
- tolerances for workflow-step counts or other live-environment structural values
- small structured objects
- final values extracted from the intended Galaxy output
- explicit separation between `scientific_answer` expectations and `galaxy_execution` expectations

Avoid:

- long free-text explanations
- ambiguous summaries
- fields that depend on hidden chain-of-thought
- overly brittle exact-match rules that penalize scientifically valid equivalent answers

Ground truth should help the benchmark answer both benchmark questions fairly:

- the scientific-help question
- the Galaxy-competence question

Ground truth should also preserve the three-score split:

- base scientific criteria should support `scientific_solution_score`
- tier-specific exact or standard-path criteria should support `standard_analysis_score`
- Galaxy-operation expectations should support `galaxy_execution_score`

## Adding A New Benchmark Experiment

When creating `experiment_N`:

1. Choose one Galaxy-native biomedical task family.
2. Put all public input files under `dataset/experiment_N/`.
3. Create the three public task files under `experiments/low_context/`, `experiments/medium_context/`, and `experiments/high_context/`.
4. Assign `scientist_level_band` and `galaxy_complexity_band` deliberately.
5. Keep the task constant across tiers and vary only prompt specificity.
6. Define a `required_result_format` that separates `scientific_answer` from `galaxy_execution`.
7. Create `evaluators/experiment_N.json` with hidden expectations, checks, and rubric logic.
8. Create `ground_truth/experiment_N.json` with fair-scoring comparison rules.
9. Verify that evaluator `expected_result_fields` align with the new nested result schema.
10. Verify that the high-context prompt is executable as written in Galaxy.
11. Verify that low-context and medium-context prompts remain realistic and do not accidentally leak the solution path.
12. Check that the task can answer:
    - what level of scientist the agent can help on this task
    - how well the agent can operate inside Galaxy on this task
13. Check that the hidden evaluator can distinguish:
    - `scientific_solution_score`
    - `standard_analysis_score`
    - `galaxy_execution_score`

## Optional Robustness Track

BioAgent Bench motivates controlled perturbations. If robustness variants are added, keep them clearly separated from the base benchmark and document them explicitly.

Examples:

- prompt bloat
- decoy files or decoy reference material
- mildly corrupted or malformed inputs

Do not contaminate the vanilla benchmark with perturbations unless the experiment is explicitly defined as a robustness case.

## Execution Outputs

For benchmark runs, the expected artifact pattern is:

```text
outputs/<timestamp>_<level>_<experiment>/
|-- plan/
|-- reasoning/
|-- errors/
`-- results/
```

Use [README.md](/Users/4475918/Projects/Galaxy_benchmark/README.md) and [SKILL.md](/Users/4475918/Projects/Galaxy_benchmark/SKILL.md) for the exact filenames, logging expectations, error envelope, and comparison-report requirements.

## Guardrails

- Do not overwrite previous benchmark outputs.
- Do not read `ground_truth/` during a blind execution run before result generation is complete.
- Do not replace Galaxy execution with local scripts after planning unless the benchmark authoring task explicitly changes the benchmark design.
- Do not change the meaning of an existing experiment tier without updating its paired evaluator and ground-truth files.
- Keep filenames aligned across `experiments/`, `evaluators/`, and `ground_truth/`.

If a future Codex session needs to run experiments, follow [SKILL.md](/Users/4475918/Projects/Galaxy_benchmark/SKILL.md). If it needs to extend the benchmark, follow this file first and then check the matching evaluator and task files already in the repository.
