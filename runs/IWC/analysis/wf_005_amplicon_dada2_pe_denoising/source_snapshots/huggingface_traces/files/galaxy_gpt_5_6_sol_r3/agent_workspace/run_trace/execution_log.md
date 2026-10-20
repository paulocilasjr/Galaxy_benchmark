# Galaxy execution log

- Assigned history only: `bbd44e69cb8906b5bf7138af8581bb34` (`run-fd7f1ed856a6487098edfa37c12d6c7e`).
- Input: one `list:paired` collection with 17 primer-free paired-end samples (250,607 read pairs).
- Quality assessment: DADA2 `plotQualityProfile` 1.38.0+galaxy1, joint across the run.
- Filtering: DADA2 `filterAndTrim` 1.38.0+galaxy1; forward `truncLen=240`, reverse `truncLen=220`, both `maxEE=2`, `maxN=0`, `truncQ=2`, `trimLeft=0`; PhiX removal enabled. Retained 231,360/250,607 pairs (92.32%).
- Error models: DADA2 `learnErrors` 1.38.0+galaxy1, separate forward/reverse models learned jointly from all 17 samples (`loessErrfun`, `nbases=10^8`).
- Denoising: DADA2 `dada` 1.38.0+galaxy1, samples processed individually (`pool=FALSE`) with the corresponding run-wide directional error model.
- Pair reconstruction: DADA2 `mergePairs` 1.38.0+galaxy1; `minOverlap=12`, `maxMismatch=0`, no concatenation. All 17 corrected, identifier-aligned jobs succeeded.
- Sequence table: DADA2 `makeSequenceTable` 1.38.0+galaxy1, no length filter. Before chimera removal: 511 variants and 223,840 reads.
- Chimera removal: DADA2 `removeBimeraDenovo` 1.38.0+galaxy1, de novo `consensus` method. Final: 334 ASVs and 214,614 reads; sequence lengths 252-254 nt.
- Discarded attempts: parameter-encoding tests that failed before computation, plus one batch merge with mismatched collection order. None of their outputs were used. Filtered-read collections were rebuilt in the same lexicographic identifier order as DADA outputs before the accepted merge.
- Deliverable transformation: the chimera-free Galaxy sequence table was copied unchanged except that its blank row-name header was replaced with `sequence`.
- Validation: exact 17-sample identifier set; 334 unique uppercase A/C/G/T sequences; exactly 18 columns on every row; all counts nonnegative integers; SHA-256 `ab7bf5522bee2c24c3c96fdfb1d470101e93d9f3bd3143e6ce7a43ee93434cbf`.
