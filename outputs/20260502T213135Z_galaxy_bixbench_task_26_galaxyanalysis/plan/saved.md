# BixBench task 26

Objective: In the BLM mutation carrier cohort, what fraction of variants with a variant allele frequency (VAF) below 0.3 are annotated as synonymous?

Galaxy plan: upload prepared tabular representation of the public task data and execute the scalar analysis using Galaxy Text reformatting with awk.

Parameter selection: Galaxy awk filters combined CHIP table by cohort, VAF, zygosity, annotation, and in_CHIP to compute requested CHIP scalar.

Ground truth access deferred until result.json is written.
