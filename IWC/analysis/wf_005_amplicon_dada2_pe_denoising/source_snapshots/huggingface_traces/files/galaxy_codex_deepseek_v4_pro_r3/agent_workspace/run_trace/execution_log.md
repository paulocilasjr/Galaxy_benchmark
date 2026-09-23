# Execution log

## Goal
- Denoise 17 paired-end 16S V4 samples into ASVs with DADA2 in the assigned Galaxy history.
- Remove chimeras de novo and export a raw-count sequence table.

## Parameters
- filterAndTrim: paired, forward truncLen=240, reverse truncLen=160, truncQ=2, maxN=0, maxEE=2, minLen=20, rmPhiX=true.
- learnErrors: nbases=8, default loess error model; run separately for forward and reverse.
- dada: one sample/direction per job, individual sample inference, advanced options off.
- mergePairs: minOverlap=12, maxMismatch=0, justConcatenate=false, trimOverhang=false.
- makeSequenceTable: orderBy=abundance, no length filter.
- removeBimeraDenovo: method=consensus.

## Key Galaxy outputs
- Final stable sequence table: f9cad7b01a472135a3b95cf5b0c01d44
- Exported final table: final_answer/asv_abundance.tsv

## Job tracking
- filterAndTrim job map: run_trace/filter_jobs.tsv
- filtered read map: run_trace/filter_output_map.tsv
- learnErrors jobs: bbd44e69cb8906b562157f4bb5945525 (forward), bbd44e69cb8906b57a5530597eac7f5e (reverse)
- dada job map: run_trace/dada_jobs.tsv
- mergePairs job map: run_trace/merge_jobs.tsv
- makeSequenceTable job: bbd44e69cb8906b579535b9d194069be
- removeBimeraDenovo job: bbd44e69cb8906b50624706ce129a5de
