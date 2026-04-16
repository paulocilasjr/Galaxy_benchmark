# Agent Adapter Spec

Every benchmarked system should be wrapped behind a consistent adapter.

Suggested API:

- `prepare(task, prompt, environment)`
- `execute()`
- `collect_outputs()`
- `get_trace()`
- `get_confidence_record()`

Required metadata:

- `agent_id`
- `agent_version`
- `model_name`
- `supports_galaxy`
- `supports_skills`
- `harness_name`
- `harness_version`

Adapters should preserve enough trace information to separate model behavior from harness behavior in later analysis.
