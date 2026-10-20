# DADA2 ASV workflow execution log

Assigned history: `bbd44e69cb8906b5ee1171e94c720212`
Input list:paired collection: `bc691189a1eab94e`

## Workflow

1. Built one paired collection per sample from the supplied raw forward/reverse
   HDAs because the installed `dada2_filterAndTrim` 1.38.0+galaxy1 wrapper could
   not be submitted directly with the nested `list:paired` input collection.
2. Ran `dada2: filterAndTrim` in paired mode independently for each sample with:
   forward truncLen 240, reverse truncLen 160, truncQ 2, maxEE 2, minLen 20,
   maxN 0, minQ 0, rmPhiX true, low-complexity kmer threshold 0.
3. Learned error rates from all paired-filtered forward and reverse reads with
   `dada2: learnErrors` (`nbases=8`, loess error function).
4. Ran `dada2: dada` separately for each sample/direction using those error
   models.
5. Merged paired reads with `dada2: mergePairs`
   (`minOverlap=12`, `maxMismatch=0`, no concatenation fallback, no overhang
   trimming).
6. Built a sequence table from the 17 merged samples with
   `dada2: makeSequenceTable` (ASVs ordered by abundance, no length filter).
7. Removed chimeras de novo with `dada2: removeBimeraDenovo` using
   `method=consensus`.
8. Downloaded the final sequence table as tabular text and wrote
   `final_answer/asv_abundance.tsv` with the first column named `sequence`.

## Final Galaxy outputs

- Paired-filtered read map: `/tmp/dada2/paired_filter_map.tsv`
- DADA output map: `/tmp/dada2/dada_paired_map.tsv`
- Merge output map: `/tmp/dada2/merge_paired_map.tsv`
- Final non-chimeric sequence table HDA:
  `f9cad7b01a4721357553daba3fb1272c`

## Final deliverable validation

- File: `final_answer/asv_abundance.tsv`
- Rows: 315 ASVs
- Columns: 18 (`sequence` + 17 supplied samples)
- Sequence strings are uppercase and contain only A/C/G/T.
- Counts are nonnegative integers.
- Sample order matches the supplied input collection.
