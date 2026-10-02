# Codebook: where did the error happen in a scored-incorrect Galaxy run that used a user-defined tool (UDT)?

## Context
In the Galaxy condition, an agent reaches usegalaxy.org through an interface (MCP server). Besides installed Galaxy wrapper tools, it can submit a **user-defined tool (UDT)**: agent-written code (a shell command, often running a Python/R script) that Galaxy runs as a job in a container (`run_galaxy_udt_and_wait`). Every run you audit was **scored incorrect** and **requested at least one UDT**. The question is whether the UDT was the reason the answer was wrong, or whether the error happened before or after the UDT, or elsewhere, so that it is unrelated to UDT use.

## Evidence you have for each run
- `timelines/<benchmark>__<task>__<run_id>.txt`: a header (submitted answer, reference, UDT counts, failure-ledger adjudication for BixBench) and an ordered, truncated timeline. `L<n>` is the line number in the decompressed full trace (`FULL TRACE:` path; `.gz` files: use `gzip -cd <path> | sed -n '<n>p'`). Events:
  - `UDT RUN`: UDT id, container, status, job states, failure phase, shell command and inline output previews.
  - `GALAXY TOOL RUN`: an installed Galaxy wrapper.
  - `GALAXY INTERFACE`: search, inspect or wait calls.
  - `SHELL`: a local shell command, with its exit code and output tail.
  - `WEB`, `FILE`, `AGENT` (the agent's messages).
- `tasks/<task>.md`: the task-level audit entry (question, reference, per-run explanations of the wrong answers). **Read it first**: it often already names the mechanism for your run.
- For BixBench, the header's `FAILURE LEDGER` line is an earlier run-level adjudication of the decisive error. Use it as the starting point and check it against the trace.
- Timelines can be long. Search them (for example `grep -n "UDT RUN\|GALAXY TOOL RUN\|AGENT:" file | tail -60`) and read the region around the final answer and each UDT, rather than reading everything. Open the full trace at specific lines when the preview is not enough (for example to read a UDT's script or output).

## Categories (exactly one per run)
Apply them in this order and take the first that fits.

1. **REFERENCE_OR_EVALUATOR**: the submitted answer is equivalent to the reference or scientifically defensible, according to the task entry or the ledger (EVALUATOR, CONTRACT, or SPEC where the entry says the reference encodes an unstated choice and the run's reading is defensible). There is no execution error to locate. Use this only when the task entry or ledger supports it for this answer.
2. **NOT_ON_PATH**: the UDT(s) did not contribute to the submitted answer. They were used only for side tasks (runtime probes, smoke tests, file format conversion, inspection) or their output was abandoned for reasons unrelated to UDT failure. The wrong value came from other steps: a Galaxy wrapper tool, local shell computation, web lookup or the model's own knowledge. If the agent abandoned the UDT *because it failed* and the fallback produced the wrong answer, use UDT_EXECUTION instead.
3. **UDT_EXECUTION**: a UDT did not run as intended, and that failure is what made the final answer wrong or missing. Examples:
   - the job was never dispatched ("no execution destination", routing);
   - the command failed to render or bind;
   - the container lacked a package;
   - a resource or time limit was hit;
   - the UDT kept failing and the budget ran out.

   This includes a forced fallback, such as local computation, a different Galaxy wrapper or a different method, whose result differs from the reference because of the fallback route. The UDT mechanism is the main problem.
4. **UDT_CODE**: the UDT ran and its output is, or directly yields, the submitted answer, and the error is in what the agent's UDT code computed: wrong method, statistic, filter, definition, identifier mapping, or a bug. The UDT step is where the error lives, although the mistake is the agent's analysis, not the UDT mechanism.
5. **BEFORE_UDT**: the UDT computed appropriately on what it was given, but its inputs were already wrong. Examples:
   - the wrong file or subset was staged;
   - an earlier Galaxy tool produced a wrong intermediate;
   - earlier preprocessing or a wrong parameter was passed in.

   The decisive error precedes the UDT step.
6. **AFTER_UDT**: the UDT's output was correct, or contained the correct value, but a later step introduced the error. Examples:
   - misreading or selecting the wrong row or field;
   - later arithmetic, rounding, unit or format changes;
   - a subsequent non-UDT analysis that overrode the UDT result.

If the evidence is truly insufficient, choose the most likely category and set confidence to `low`.

## Output
Write one JSON object per line (JSONL) to your assigned output file, one line per run, with these keys:
- `benchmark`, `task`, `run_id`: copied from the header.
- `category`: one of the six codes above.
- `udt_role`: one of `answer_producing` (a UDT output is, or directly yields, the answer), `intermediate` (a UDT produced an intermediate used downstream), `side_task` (probe, conversion or inspection only), or `failed_only` (every UDT attempt failed; none produced usable output).
- `answer_source`: one of `udt`, `galaxy_wrapper`, `local_shell`, `web_or_knowledge`, `no_answer`, `unclear`.
- `decisive_error_lines`: a list of trace line numbers (integers) where the decisive error is visible. Use an empty list only for REFERENCE_OR_EVALUATOR.
- `udt_lines`: a list of line numbers of the relevant UDT calls.
- `confidence`: `high`, `moderate` or `low`.
- `rationale`: at most 40 words, factual, naming the step and what went wrong.

## Rules
- Read-only. Do not modify any file in the repository, do not run any agent code, do not contact Galaxy or the internet, and do not open anything under `ground_truth/`. Write only your assigned output file.
- Judge each run on its own trace. Runs of the same task often share a mechanism, but verify each.
- Be consistent with the task entry unless the trace clearly contradicts it; if it does, say so in the rationale.

## Amendment 1 (added after batches 1–5 returned, before the final categories were fixed)
Several reviewers independently met the same case: every UDT failed, and a fallback route then made the *same* scientific choice or error that the UDT's own script or inputs already contained. The original rule 3 did not separate this from a failure that changed the answer. The rule is now as follows, applied to every run in which a UDT failed.

- **UDT_EXECUTION** only if the failure *changed the answer*: the fallback route gave a different result from what the agent's own UDT would have computed, because of the route. Examples: tool defaults, a missing package, a forced different wrapper, a local environment, a copied answer, or the budget running out.
- **UDT_FAILED_NOT_DECISIVE** (new): the failed UDT was meant to produce the answer or an input to it, but the fallback applied the same method, choice or error that was already in the UDT's script or inputs, or that was fixed before the UDT. The UDT failure therefore did not decide the wrong answer. This counts as *not related to UDT use*.
- **NOT_ON_PATH** is kept for UDTs that were only side tasks (probes, smoke tests, conversion, inspection, a side screen), whether or not they failed.

Decision order: 1 REFERENCE_OR_EVALUATOR, 2 NOT_ON_PATH, 2b UDT_FAILED_NOT_DECISIVE, 3 UDT_EXECUTION, 4 UDT_CODE, 5 BEFORE_UDT, 6 AFTER_UDT.
