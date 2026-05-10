# BixBench task 27

Objective: When examining variants with a VAF < 0.3, what is the difference in missense variant frequency between the parental control group and the patients with a BLM mutation status marked as 'Affected', which is also referred to as the 'BSyn Probands' group?

Galaxy plan: upload prepared tabular representation of the public task data and execute the scalar analysis using Galaxy Text reformatting with awk.

Parameter selection: Galaxy awk filters combined CHIP table by cohort, VAF, zygosity, annotation, and in_CHIP to compute requested CHIP scalar.

Ground truth access deferred until result.json is written.
