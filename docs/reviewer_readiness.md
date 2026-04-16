# Reviewer Readiness Checklist

This document captures the review gaps Galaxy Benchmark v0.3 is intended to close.

## Questions The Benchmark Must Answer

### 1. Is the benchmark scientifically meaningful?

Expected evidence:

- real biomedical tasks
- explicit final artifact contracts
- allowance for scientifically valid alternatives where appropriate
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

### 5. Is confidence evaluated rather than assumed?

Expected evidence:

- confidence query policy in task design
- confidence records in run artifacts
- confidence-calibration metric in reporting

### 6. Can failures be audited after the fact?

Expected evidence:

- append-only activity log
- structured error envelope
- retry chain
- attempt-specific artifacts
- Galaxy failure evidence snapshots

### 7. Is the benchmark reproducible?

Expected evidence:

- immutable run layout
- artifact manifests
- evaluation manifests
- reproduction scripts
- clear separation of public versus hidden assets
