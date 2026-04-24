# BixBench task 1 attempt 1

Attempt 1 follows the initial plan without modification.

- Strategy: use Galaxy `DESeq2` with sample-sheet contrasts
- Full analysis: `KL1`, `KL2`, `KL3` versus `WL1`, `WL2`, `WL3`
- Reduced analysis: `KL1`, `KL2` versus `WL1`, `WL2`
- Post-processing: count DEGs from Galaxy output tables using the prompt thresholds and compare the direction to the ground truth `ideal` field
