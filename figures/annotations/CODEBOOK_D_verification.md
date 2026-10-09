# Coding protocol D: verification steps in agent runs

You are coding what an AI agent did to check its own analysis. Each transcript is one run of an agent answering a bioinformatics benchmark question (custom code or Galaxy). You do **not** know, and must not try to infer, whether the run's final answer was graded correct. Code behaviour only.

Read each assigned transcript completely (they are plain text; use the Read tool in chunks for long files). Do not open any other file in the repository, do not use the internet, and do not look for grades, references or answer keys.

## Codes (present / absent, with evidence)

A check counts only when the agent explicitly tests something its answer depends on. Routine actions (listing files, printing the head of a file once to see its format, installing software, retrying after a crash) are **not** checks unless the agent uses them to test an assumption it states.

- **V1 Count or denominator check**: the agent verifies counts (rows, samples, genes, sequences, reads, groups) or a denominator, for example asserting an expected number, comparing counts before and after a filter or join, or checking that no records were lost.
- **V2 Independent recomputation**: the same final or intermediate quantity is computed a second time by a different method, tool, library or code path, and the two are compared.
- **V3 Sensitivity analysis**: the agent varies a parameter, threshold, filter, statistical test, version or definition and compares the results.
- **V4 Assumption check on the inputs**: the agent inspects the inputs specifically to confirm an assumption the answer depends on (group labels, identifier mapping, units, strand, genome build, file content matches the question), beyond routine format inspection.
- **V5 Plausibility check**: the agent compares the result with an expected range, known biology, published values or a sanity criterion (for example, a proportion within 0–1, a P value consistent with the effect).
- **V6 Domain diagnostic**: the agent runs a recognised quality-control or diagnostic analysis for the method (mapping rate, read-position or strand bias, model convergence, residuals, duplicate rate).

Also code:
- **changed_conclusion**: `yes` if a check led the agent to change its method or its answer (cite the step), `no` if checks were done but nothing changed, `none` if no check was done, `unclear` otherwise.
- **hedged_answer**: `yes` if the agent states uncertainty or alternatives in its final answer or final message, otherwise `no`.

## Output

For each transcript, produce one JSON object:

```json
{"code": "D001",
 "V1": {"present": true, "steps": [12, 30], "evidence": "≤25-word quote or paraphrase"},
 "V2": {"present": false, "steps": [], "evidence": ""},
 "V3": {...}, "V4": {...}, "V5": {...}, "V6": {...},
 "changed_conclusion": "yes|no|none|unclear", "changed_steps": [31],
 "hedged_answer": "yes|no",
 "notes": "≤30 words"}
```

Step numbers are the `[n]` markers in the transcript. Write all objects as a JSON list to the output file named in your assignment, and return a one-line summary.
