# BixBench task 44

Objective: In individuals with a variant in the BLM gene, what proportion of Clonal Hematopoiesis of Indeterminate Potential (CHIP) variants are somatic - defined as having a Variant Allele Frequency (VAF) below 0.3?

Galaxy plan: upload task input as tabular/text and execute the scientific calculation with Galaxy Text reformatting with awk. The awk output is the fixed submitted answer.

Parameter selection: Galaxy awk filters CHIP rows by cohort, zygosity, in_CHIP and VAF interval, then computes requested proportion.

Ground truth access deferred until result.json is written.
