# Coding protocol A2: why a benchmark answer was graded incorrect

Each transcript is one run of an AI agent answering a BixBench-Verified-50 question, either with custom code or through Galaxy. The run was graded **incorrect**. The header gives the submitted answer, the reference answer and the evaluator mode. Your job is to assign the most likely cause of the incorrect grade from the transcript, independently. You have not seen any earlier audit; do not look for one.

Read each assigned transcript completely (use the Read tool in chunks for long files). Do not open any other file in the repository and do not use the internet.

## Causes

Assign one **primary** cause and, optionally, one **secondary** cause:

- **RIGOR (no answer validation)**: the agent made an error that a check of its own result would have exposed. Examples: wrong subset or filter, off-by-one, inverted contrast, unit or scale error, a calculation mistake, an unverified assumption about the data.
- **KNOWLEDGE (lacking biological or statistical knowledge)**: the agent used a wrong biological or statistical concept, method or definition.
- **PLATFORM (not able to use Galaxy)**: a Galaxy tool, wrapper or job gave a wrong result, failed, or blocked the route that would have produced the reference. Use only for Galaxy runs.
- **HARNESS (no answer submitted)**: the run ended without a usable answer (time-out, crash, empty or malformed submission).
- **SPEC (benchmark specification)**: the question or reference is under-specified or ambiguous, so a defensible analysis gives a different value. Examples: unstated software version, normalisation, test family, or inclusion rule that the reference silently assumes.
- **EVALUATOR (scoring)**: the submitted answer matches the reference within the intended tolerance or meaning, but the scorer rejected it, for example because of formatting.

When the transcript supports two causes, choose the one without which the run would most likely have been accepted as primary, and give the other as secondary.

## Output

For each transcript, one JSON object:

```json
{"code": "C001", "primary": "RIGOR|KNOWLEDGE|PLATFORM|HARNESS|SPEC|EVALUATOR", "secondary": "…|none",
 "confidence": "high|moderate|low", "rationale": "≤40 words citing step numbers [n]"}
```

Write all objects as a JSON list to the output file named in your assignment, and return a one-line summary.
