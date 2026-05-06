# BixBench task 28

Objective: After filtering out reference variant calls and variants located in intronic, intergenic, or UTR regions how many non-reference exonic variants remain in clonal hematopoiesis (CHIP) genes from the 86 samples analyzed?

Galaxy plan: upload prepared tabular representation of the public task data and execute the scalar analysis using Galaxy Text reformatting with awk.

Parameter selection: Galaxy awk filters combined CHIP table by cohort, VAF, zygosity, annotation, and in_CHIP to compute requested CHIP scalar.

Ground truth access deferred until result.json is written.
