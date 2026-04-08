# Agent Adapter Spec

Every agent must be wrapped behind a consistent adapter.

Suggested adapter API:
- `prepare(task, prompt, environment)`
- `execute()`
- `collect_outputs()`
- `get_trace()`

Required metadata:
- `agent_id`
- `agent_version`
- `model_name`
- `supports_galaxy`
- `supports_skills`

Adapters should avoid embedding benchmark-specific assumptions.
