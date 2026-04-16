# Reporting Requirements

The reporting layer should support both scientific publication and engineering auditability.

## Per-Run Outputs

- run record JSON
- artifact manifest
- evaluation manifest
- field comparisons
- score vector
- operational metrics
- confidence record
- execution context
- trace references
- failure modes

## Per-Task Outputs

- prompt-level performance table
- environment comparison
- robustness summary
- output agreement summary
- failure analysis
- preprocessing and parameterization findings

## Per-Agent Outputs

- overall performance by environment
- mean score-vector components
- robustness by environment
- Galaxy effect
- Skills effect if used
- confidence calibration
- performance by scientist-help band
- performance by Galaxy-complexity band

## Benchmark-Level Outputs

- aggregate completion rate
- aggregate operational metrics
- aggregate score-vector summaries
- uncertainty estimates
- failure taxonomy
- dataset governance references
- publication eligibility filters
