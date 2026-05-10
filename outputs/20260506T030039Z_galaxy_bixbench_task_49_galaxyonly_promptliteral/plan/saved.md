# BixBench/task_49 Initial Plan

Objective: In samples with 'Mother' or 'Father' status, what proportion (between 0-1) of somatic CHIP variants (VAF < 0.3) can be classified as benign - after filtering out intronic, intergenic, UTR regions, and reference (non-variant) calls?

Plan: upload prepared text/tabular input to usegalaxy.org; run Galaxy Text reformatting awk for all scientific filtering and scalar calculation; download Galaxy output; write result.json before ground-truth access.

Parameters: CHIP filter: VAF < 0.3, non-reference, In_CHIP true, exclude only intron/intergenic/UTR annotations, benign numerator includes Benign and Likely Benign.
