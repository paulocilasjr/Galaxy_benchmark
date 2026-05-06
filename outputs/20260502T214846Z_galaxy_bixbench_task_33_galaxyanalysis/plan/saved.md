# BixBench task 33

Objective: Among patients classified as BLM mutation carriers, what is the median number of somatic CHIP variants - defined as variants with a Variant Allele Frequency (VAF) < 0.3? Prior to analysis, exclude all variants that are Intronic, Intergenic, in UTR regions, or have Reference zygosity.

Galaxy plan: upload prepared tabular representation of the public task data and execute the scalar analysis using Galaxy Text reformatting with awk.

Parameter selection: Galaxy awk counts filtered somatic CHIP variants per BLM carrier sample and computes median.

Ground truth access deferred until result.json is written.
