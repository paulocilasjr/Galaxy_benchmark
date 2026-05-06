# BixBench task 39

Objective: Using the NeuN count data, calculate the effect size (Cohen's d) for the difference between KD and CTRL conditions (using pooled standard deviation), then perform a power analysis for a two-sample t-test to determine how many samples per group would be required to detect a statistically significant difference with 80% power at α = 0.05. Return the number of samples per group as your final answer.

Galaxy plan: upload task input as tabular/text and execute the scientific calculation with Galaxy Text reformatting with awk. The awk output is the fixed submitted answer.

Parameter selection: Galaxy awk computes NeuN pooled-SD effect size, power sample size approximation, Shapiro W, or two-way interaction F from uploaded NeuN table.

Ground truth access deferred until result.json is written.
