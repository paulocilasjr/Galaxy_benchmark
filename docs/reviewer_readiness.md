# Reviewer Readiness Checklist

This document captures the review gaps Galaxy Benchmark v0.3 is intended to close.

## Questions The Benchmark Must Answer

### 1. Is the benchmark scientifically meaningful?

Expected evidence:

- real biomedical tasks
- explicit final artifact contracts
- allowance for scientifically valid alternatives where appropriate
- explicit treatment of non-unique acceptable solutions
- task-level rationale for preprocessing and parameter choices

### 2. Does the benchmark separate model quality from harness quality?

Expected evidence:

- environment comparisons (`open` vs `galaxy`)
- explicit harness-aware reporting
- trace capture that shows what the harness executed

### 3. Is Galaxy itself being evaluated?

Expected evidence:

- Galaxy-specific operational metrics
- history, job, invocation, and dataset trace artifacts
- scoring for tool choice, workflow coherence, parameterization, and retries

### 4. Is robustness to user phrasing measured?

Expected evidence:

- semantically equivalent prompt variants
- prompt-style metadata
- robustness and output-agreement reporting
- iterative stability under prompt variation

### 5. Is confidence evaluated rather than assumed?

Expected evidence:

- confidence query policy in task design
- confidence records in run artifacts
- confidence-calibration metric in reporting

### 6. Is iterative improvement evaluated rather than hidden inside retry behavior?

Expected evidence:

- explicit `single_run` and `multi_run` settings
- first-run versus best-of-N reporting
- improvement trajectory metrics
- attempt manifests and workflow differences across runs

### 7. Can failures be audited after the fact?

Expected evidence:

- append-only activity log
- structured error envelope
- retry chain
- attempt-specific artifacts
- Galaxy failure evidence snapshots

### 8. Does the benchmark support human-informed scientific acceptability?

Expected evidence:

- structured scientific acceptability policy
- explicit acceptable solution classes
- hybrid or human-informed review when deterministic checks are insufficient

### 9. Is the benchmark reproducible?

Expected evidence:

- immutable run layout
- artifact manifests
- evaluation manifests
- reproduction scripts
- clear separation of public versus hidden assets
