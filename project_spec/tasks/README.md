# Task Authoring Guide

Each task represents one biomedical objective and must be authored independently of prompt specificity and environment.

Required fields:
- `task_id`
- `title`
- `domain`
- `description`
- `complexity`
- `datasets`
- `ground_truth`
- `acceptable_solutions`
- `requires_iteration`
- `iteration_budget`
- `evaluation_spec`

Complexity labels:
- `simple`
- `complex`
- `very_complex`

Complexity should reflect:
- number of steps
- number of important parameters
- number of decision points
- amount of intermediate interpretation required
- need for retries/optimization

Authoring rule:
A task must be stable across the three prompt variants.
