# Galaxy Agent Benchmark – PROJECT_SPEC

## 1. Overview

This project implements a benchmark to evaluate AI agents in biomedical workflows using the Galaxy environment.

The benchmark evaluates:
- Task-solving capability
- Sensitivity to prompt specificity
- Effect of execution environment (Open vs Galaxy vs Galaxy+Skills)
- Usability across user expertise levels

The benchmark is structured around:

**Task × Prompt × Environment**

## 2. Core Concepts

### Task
A biomedical objective with:
- dataset(s)
- ground truth or acceptable solution(s)
- complexity label

### Prompt Specificity
Three variants per task:
- vague (novice)
- specific (intermediate)
- very specific (expert)

### Environment
Each run occurs in:
- open
- Galaxy
- Galaxy + Skills

## 3. Benchmark Matrix

For each task:

**3 prompts × 3 environments = 9 runs**

## 4. Task Specification

Each task must include:
- task_id
- description
- domain
- datasets
- ground_truth
- acceptable_solutions
- complexity (simple, complex, very_complex)
- evaluation_spec
- requires_iteration (bool)
- iteration_budget (optional)

## 5. Prompt Generation

Each task must generate:
- vague_prompt
- specific_prompt
- very_specific_prompt

All prompts must represent the same task.

## 6. Environments

Implement wrappers for:
- Open environment
- Galaxy environment
- Galaxy + Skills environment

Each environment must expose a common execution interface.

## 7. Run Execution

Each run must store:
- run_id
- task_id
- prompt_level
- environment
- agent_id
- input_prompt
- outputs
- trace/logs
- status
- performance_score
- component_scores

## 8. Scoring

### 8.1 Performance
Perf(t,p,e) ∈ [0,1]

Based on:
- correctness
- execution success
- scientific validity
- reproducibility
- interpretation (if applicable)

Aggregate:
Perf(t,e) = Σ w_p Perf(t,p,e)

### 8.2 Robustness
Measures stability across prompts:
Robust(t,e) = mean(Perf(t,p,e)) - variance(Perf(t,p,e))

### 8.3 Adaptability
Galaxy effect:
Adapt_G(t,p) = Perf(t,p,Galaxy) - Perf(t,p,Open)

Skills effect:
Adapt_S(t,p) = Perf(t,p,Galaxy+Skills) - Perf(t,p,Galaxy)

Aggregate across prompts.

## 9. User-Level Confidence

Derived from prompt specificity:
- vague → novice
- specific → intermediate
- very specific → expert

ULC(p,e) = fraction of tasks where Perf(t,p,e) ≥ threshold

## 10. Iterative Tasks

For tasks requiring iteration:
- run initial analysis
- evaluate output
- adjust parameters
- rerun
- track improvement

Store iteration traces.

## 11. Project Structure

```text
tasks/
prompts/
environments/
agents/
skills/
evaluation/
reports/
schemas/
examples/
```

## 12. Evaluation Pipeline

1. Load tasks
2. Generate prompts
3. Run all combinations (task × prompt × environment)
4. Compute run-level scores
5. Aggregate:
   - per task
   - per environment
   - per agent
6. Compute:
   - Performance
   - Robustness
   - Adaptability
   - User-level confidence

## 13. Outputs

Per agent:
- overall performance
- robustness
- adaptability
- user-level support

Per task:
- prompt breakdown
- environment comparison

## 14. Key Goal

Measure:
- What tasks agents can solve
- How much prompt detail they require
- Whether Galaxy improves reliability
- Whether Skills improve usability
- Which users can trust the agent

## 15. Summary

This benchmark evaluates agents as scientific assistants by combining:
- Task complexity
- Prompt specificity
- Execution environment

to produce:
- Performance
- Robustness
- Adaptability
- User-level confidence
