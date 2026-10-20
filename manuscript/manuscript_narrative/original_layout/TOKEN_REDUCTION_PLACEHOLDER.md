# Token-reduction intervention — RESULTS PLACEHOLDER

**Status: PLACEHOLDER — RESULTS PENDING. This file, the final paragraph of Results section 4 and Fig. 6f must remain marked as placeholders until the intervention results are confirmed and finalized.** No intervention result is reported in this package, and no provisional percentage is plotted. No new agent runs were performed.

## The loop the manuscript will close

Benchmarks show where agents spend tokens in Galaxy (X, Y, Z) → the Galaxy API and MCP server are changed to address X, Y and Z → a benchmark rerun shows by how much token use falls while accuracy and provenance are preserved. This is feasible: the archive already supplies the baseline and the measured targets, and BixBench-Verified-50 is small and fast enough for a controlled rerun.

## What the archive now establishes

- **The archived runs are the post-change baseline.** The GPT-5.5 BixBench Galaxy/code ratio of total input tokens is **2.82 (95% CI 2.12–3.81)**, over 50 tasks × 3 replicates per arm. This reproduces the "2.8×" reported for the comparison after the second development round, and confirms its definition: total (equivalently mean per run) input tokens including cached context, Galaxy divided by code. The archived interface already includes combined submission and waiting (`run_galaxy_tool_and_wait`, `run_galaxy_udt_and_wait`) and parameter checks.
- **The earlier states are not in the archive.** No archived campaign corresponds to the reported 13× or 5.5× ratios. The four GPT-5.5 BixBench Galaxy image tags (`no-static-udt-resolver`, `adaptive-search`, `mcp-hardening`, `full-blocking`) were assigned by task, not run as within-task variants, and their median inputs are similar (about 1.15 million tokens), so they cannot recover the before/after effect.
- **The manuscript's headline ratios use the same definition.** Pooled over the four configurations, the ratio of totals is 4.25 on BixBench, 2.70 on CompBioBench and 0.90 on IWC. The higher values previously reported in this package (5.17 and 4.42) were medians of within-task ratios, a different aggregation; they are now a secondary measure.

## X, Y and Z measured in the archive (four primary configurations)

| Target | Archive evidence | Interface change to test | Guardrail |
|---|---|---|---|
| X. Tool discovery | Search plus inspection are 47%, 44% and 54% of calls and 69%, 44% and 51% of returned text (BixBench, CompBioBench, IWC); 45–53% of tools inspected in a run are never run; 417 calls used a nonexistent tool ID | Relevance-ranked search with operation and datatype filters; reusable tool inventories; ID validation before submission | Correct tool retrieval; tool versions retained |
| Y. Request construction | 3,155 of 7,354 failed calls were rejected before a job ran: 1,119 because the tool schema needed history context, 769 for parameter values, 253 for foreign or wrong IDs, 215 for nested-parameter structure | History-scoped schemas that return only the parameters relevant to a request; structured validation errors | Requested versus resolved parameters compared; dataset bindings checked |
| Z. Failures without diagnostics | 1,601 job errors returned no diagnostic text; 64.6% of failed UDT jobs failed before execution without diagnostics; after such failures, 50% of next calls were identical resubmissions and 78% of these failed again; 43.5% of CompBioBench Galaxy runs contain probe or preflight UDTs | UDT dependency and dispatch preflight; actionable failure payloads; resumable waits | First-attempt completion; diagnostics reported for every failure |
| Returned text | Full histories, logs and schemas returned to the model | Full records saved with hashes; bounded summaries returned; targeted retrieval | Details retrievable on demand; no hidden failures |

Per-run Galaxy input tracks the number of interface calls plus shell commands (Spearman ρ = 0.89, 0.86 and 0.83), so removing interaction rounds should reduce tokens.

## The development history (to be documented, not inferred)

Junhao Qiu described two rounds of changes. Round 1 (prompt and skills): shortened repetitive skill explanations and examples, and guidance to save full API responses in run records while showing compact summaries, reuse saved tool inventories, inspect only relevant parameters and avoid reprinting full histories and logs. Round 2 (MCP and execution): combined submission and waiting, automated record keeping and parameter checks, and compact results. He reported that in a later GPT-5.5 comparison (50 tasks, three replicates) Galaxy token use fell by 55.2%, from 5.5× to 2.8× open-ended code.

Answers to the open questions in the discussion:

- **Can we infer 13× → 5.5× from round 1 and 5.5× → 2.8× from round 2?** Only if each pair of ratios comes from the same tasks, model, budgets, token definition and code reference. The 13× value has no recorded cohort or definition. Request the run identifiers or campaign roots behind each ratio.
- **Arithmetic check.** With an unchanged code denominator, 5.5× → 2.8× is a 49.1% fall in the ratio. A 55.2% fall in Galaxy tokens is consistent with those ratios only if code-arm tokens also fell by about 12% between the two comparisons, for example because a new code baseline was run. Confirm which.
- **How does saving full responses reduce tokens?** Saving a file does not reduce tokens by itself. Tokens fall when the full payload is kept out of what the model sees and rereads on later turns, and only a bounded summary with identifiers, status and a record locator is returned.
- **Examples of shortened skills and automated records** (illustrative, not verified version diffs): one short discovery instruction referenced by several skills instead of repeated worked examples; on submission, a receipt with history, job and dataset IDs, then after completion an automatic comparison of requested and resolved parameters, with only a compact status returned.

## Prospective comparison

Freeze the model snapshot and reasoning setting, task and input hashes, budgets, container catalogue, prompts, skills, interface commits and answer extraction. On BixBench-Verified-50, compare a 2 × 2 design—current baseline, prompt/skill changes only, MCP changes only, and both—with a contemporaneous frozen code arm. Randomize order within task × configuration × replicate blocks and isolate accounts, histories and workspaces. Choose replicate numbers from a registered clustered power simulation; three repeats is a starting point. Confirm on CompBioBench before claiming generality; IWC is a poor primary test because Galaxy did not use more total input there.

Report input tokens per assigned attempt, including failures and timeouts, as (i) reduction relative to the baseline, `100 × (1 − total optimized Galaxy input / total baseline Galaxy input)`, and (ii) Galaxy/code ratio of totals, with task- or capsule-clustered intervals. Also report uncached input, output tokens, interface calls, returned text, wall time and cost where pricing and cache accounting are available. Accuracy, appropriate methods, parameter and dataset fidelity, complete receipts and diagnostics are guardrails; refusal, early stopping or hidden failures do not count as savings. Justify any non-inferiority margin before outcomes are observed.

## Required to replace this placeholder

1. Run identifiers, interface versions and token definitions for the 13×, 5.5× and 2.8× ratios.
2. Exact diffs for each intervention.
3. All assigned run outcomes, tokens and missing-data flags for the prospective comparison, with the contemporaneous code arm.
4. Measured reductions with intervals and the accuracy and fidelity guardrails.

Then replace the `[Authors: insert measured reductions …]` field in the manuscript and Fig. 6f, and remove the RESULTS PENDING labels. Until then, the manuscript must not report an achieved reduction.
