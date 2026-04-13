# Outputs

`outputs/` is the writable run-artifact target during benchmark execution.

Repository policy:

- keep this directory itself tracked so benchmark runners have a stable destination
- do not commit benchmark run artifacts here
- the public blind release package must include only this placeholder directory, not scored runs

For a benchmark execution, create a new timestamped subdirectory under `outputs/`.
