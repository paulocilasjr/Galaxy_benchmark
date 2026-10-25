# DADA2 paired-end 16S V4 denoising execution log

## Scope
- Galaxy history: bbd44e69cb8906b5458d3b823dfd8f0f
- Input collection: Paired input data (list:paired, 17 samples)
- Deliverable: final_answer/asv_abundance.tsv

## Steps
1. Created one paired collection per sample from the supplied forward/reverse HDAs so the individual DADA2 filterAndTrim tool could consume each sample.
2. Ran `dada2: filterAndTrim` for all 17 samples:
   - forward truncLen = 240, maxEE = 2, truncQ = 2
   - reverse truncLen = 160, maxEE = 2, truncQ = 2
   - minLen = 20, maxN = 0, rmPhiX = TRUE
3. Ran `dada2: learnErrors` separately on the 17 forward and 17 reverse filtered FASTQ files (default loessErrfun, nbases = 1e8).
4. Ran `dada2: dada` separately for forward and reverse reads with the learned error rates (pooling = FALSE).
5. Ran `dada2: mergePairs` per sample:
   - minOverlap = 12
   - maxMismatch = 0
   - justConcatenate = FALSE
   - trimOverhang = FALSE
6. Ran `dada2: makeSequenceTable` on the 17 merged sample outputs (orderBy = abundance).
7. Ran `dada2: removeBimeraDenovo` with method = consensus.
8. Downloaded the resulting stable sequence table, renamed the sample columns to the supplied sample identifiers, named the sequence column `sequence`, uppercase-checked all ASV sequences, and wrote the raw-count TSV.

## Output
- final_answer/asv_abundance.tsv
- 315 unique ASVs, 17 sample columns, raw integer counts.
