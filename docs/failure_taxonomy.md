# Failure Taxonomy

## Purpose

Failure analysis should explain why a run failed, whether recovery was possible, and which execution decision or access condition caused the failure.

## Primary Categories

- `task_understanding`
- `workflow_discovery`
- `tool_discovery`
- `input_mapping`
- `parameter_grounding`
- `execution_control`
- `polling_or_waiting`
- `output_interpretation`
- `provenance_failure`
- `knowledge_retrieval_failure`
- `knowledge_adaptation_failure`
- `unnecessary_autonomy`
- `unsafe_defaulting`
- `unsupported_capability`
- `hallucinated_action`
- `incomplete_recovery`

## Secondary Attributes

- recoverable vs terminal
- first-attempt vs repeated
- prompt-induced vs environment-induced
- UI-only vs API-only vs MCP-specific

## Recovery Expectations

- read concrete failure evidence before retrying
- record a normalized signature
- justify the fix strategy before rerun
- treat repeated identical signatures as invalid fixes
