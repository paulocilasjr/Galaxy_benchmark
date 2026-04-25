# BioAgent Task 2 Attempt 5 Plan

## Why attempt 4 failed

- Attempt 4 corrected the `kingdom` selector shape, but `Prokka` still rejected the payload because the optional `gffver` select parameter was submitted as a numeric value rather than the exact expected selector format.

## Attempt 5 workflow

1. Keep the same uploaded-FASTA plus `Prokka -> Roary -> FastTree` recovery path.
2. Launch on a fresh Galaxy history.
3. Submit `Prokka` with only the minimal validated inputs:
   - `input`
   - `locustag`
   - `kingdom|kingdom_select=Bacteria`
4. Rely on Prokka defaults for optional parameters to avoid further local payload-shape errors.
