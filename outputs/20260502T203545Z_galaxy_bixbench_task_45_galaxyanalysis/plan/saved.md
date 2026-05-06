# BixBench task 45

Objective: In the Control Children cohort, what percentage of Clonal Hematopoiesis of Indeterminate Potential (CHIP) variants have a Variant Allele Frequency (VAF) between 0.3 and 0.7?

Galaxy plan: upload task input as tabular/text and execute the scientific calculation with Galaxy Text reformatting with awk. The awk output is the fixed submitted answer.

Parameter selection: Galaxy awk filters CHIP rows by cohort, zygosity, in_CHIP and VAF interval, then computes requested proportion.

Ground truth access deferred until result.json is written.
