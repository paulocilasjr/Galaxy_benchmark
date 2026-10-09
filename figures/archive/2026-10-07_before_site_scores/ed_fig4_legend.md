**Extended Data Fig. 4 \| Tool inventory, route similarity, answer matching, difficulty and UDT methods.**
**a**, The 15 installed Galaxy tools with completed jobs in the most Galaxy runs, with each model's share of its traced Galaxy runs.
**b**, Mean tool-set similarity by model and benchmark, with *P* values for a model effect (model labels permuted within tasks, 20,000 permutations).
The table gives the Fig. 4c correlation under alternative route definitions:
- UDT items dropped;
- cells whose runs used only installed tools, or any UDT;
- ordered steps, as one minus the normalised edit distance between job sequences;
- tools distinguished by version;
- tools with identical non-dataset parameters.

Correlations that account for order or versions stay negative on BixBench-Verified-50; once parameters are included, the BixBench-Verified-50 correlation is close to zero.
**c**, Share of replicate sets with the same answer in all three runs under four answer-matching rules (600 sets per condition).
Rounding to three significant digits merged distinct numeric answers in three sets; the primary task-aware rule does not.
**d**, Share of replicate sets with the same rejected answer in all three runs, by held-out difficulty computed in two ways: from the task's other 21 runs (as in Fig. 4e) and from the other three models' 18 runs.
**e**, Method classes of completed UDT jobs (figures in parentheses are jobs per column).
Classes come from deterministic rules applied to the UDT definition (`udt_methods.csv`). The rules use the code where the definition contains it, otherwise a container named after a specific tool.
Many CompBioBench UDTs ran a script supplied as a separate dataset. Their method is kept in the Galaxy history but not in the request, so they are not classified.
Intervals are 95% percentile cluster-bootstrap intervals.
