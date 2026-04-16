# Reporting Requirements

The reporting layer should support both scientific publication and engineering auditability.

## Per-Run Outputs

- run record JSON
- attempt manifest
- artifact manifest
- evaluation manifest
- field comparisons
- score vector
- operational metrics
- first-run vs best-of-N summary
- improvement trajectory summary
- scientific acceptability review
- confidence record
- execution context
- trace references
- failure modes

## Per-Task Outputs

- prompt-level performance table
- environment comparison
- single-run vs multi-run comparison
- robustness summary
- output agreement summary
- failure analysis
- preprocessing and parameterization findings
- iterative improvement findings
- acceptable-solution-class distribution

## Per-Agent Outputs

- overall performance by environment
- overall performance by iteration setting
- mean score-vector components
- robustness by environment
- Galaxy effect
- iteration benefit
- Skills effect if used
- confidence calibration
- performance by scientist-help band
- performance by Galaxy-complexity band

## Benchmark-Level Outputs

- aggregate completion rate
- aggregate first-run and best-of-N completion
- aggregate improvement trajectory
- aggregate operational metrics
- aggregate score-vector summaries
- aggregate scientific acceptability distribution
- uncertainty estimates
- failure taxonomy
- dataset governance references
- publication eligibility filters
