# BioAgent Task 2 Attempt 4 Plan

## Why attempt 3 failed

- The scientific recovery path was still correct, but the first `Prokka` submission used the wrong parameter key for the tool's conditional `kingdom` selector.
- Galaxy rejected the payload with `Invalid value 'Bacteria' submitted for conditional parameter 'kingdom'.`

## Attempt 4 workflow

1. Keep the same uploaded-FASTA plus `Prokka -> Roary -> FastTree` analysis design.
2. Relaunch on a fresh Galaxy history.
3. Submit `Prokka` with the correct conditional selector key: `kingdom|kingdom_select=Bacteria`.
4. Continue with the same GFF-collection, Roary, FastTree, download, and evaluation steps if Prokka succeeds.
