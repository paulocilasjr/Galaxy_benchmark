# Benchmark Design

## Benchmark Focus

GalaxyAgentBench evaluates whether an agent can complete realistic Galaxy work with the right workflow or tool choice, the right parameter decisions, and a reproducible final report.

## Paper-Inspired Prompt Shape

The prompt scaffold is deliberately short and sectioned.

- `Task`: one explicit objective
- `Attachments`: the files or datasets available to the agent
- `Suggested Galaxy Resources`: at most a few focused hints, not a long reference dump
- `Requirements`: atomic constraints that the agent must satisfy
- `Return`: the exact fields that must be reported

This combines three ideas from the papers:

- AgentIF-OneDay frames tasks around concrete user objectives, available files, and tangible deliverables.
- AGENTIF shows that instruction-following is easier to evaluate when constraints are explicit and separable.
- SkillsBench shows that focused guidance is better than overwhelming the agent with broad documentation.

## Prompt Levels

- `novice`: same task, but with more explicit operational guidance
- `intermediate`: same task, with only the key decision points called out
- `expert`: same task, but concise and assumption-heavy

The structure stays fixed across tiers so the benchmark changes explicitness, not task semantics.

## Flat Asset Layout

- `benchmark/tasks/`: canonical task definitions
- `benchmark/ground_truth/`: canonical ground truths
- `benchmark/datasets/local/`: local benchmark inputs named by task id
- `benchmark/prompts/`: one template plus tiered prompt outputs
- `benchmark/suites.json`: suite definitions

This keeps the benchmark easy to scan without changing the underlying benchmark model.
