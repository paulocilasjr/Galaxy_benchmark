# BioAgent Task 2 Attempt 3 Plan

## Why attempt 2 failed

- The intended Prokka-based recovery path was correct, but the local runner aborted immediately after the first genome upload because it assumed Galaxy would name the upload output `output`.
- Galaxy returned the uploaded dataset under `output0`, so the failure was in local response parsing rather than Galaxy execution.

## Attempt 3 workflow

1. Reuse the same corrected scientific path as attempt 2.
2. Extract the four target FASTAs from the task dataset archive.
3. Upload all four FASTAs into a fresh Galaxy history, this time accepting Galaxy's actual upload response shape.
4. Run `Prokka` on each genome.
5. Build a GFF list collection from the four Prokka outputs.
6. Run `Roary`, then `FastTree`, then finalize the result artifacts and evaluations.
