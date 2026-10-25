# Supplementary Note 1: Protocol for interventions, conformance tests and a second deployment

The six requirements in Fig. 6b are hypotheses derived from one adapter, one public server and one period. This note specifies how each should be tested. No part of this protocol has been run.

## 1. Design shared by all interventions

**Comparison.** The baseline adapter (the archived version) is compared with the adapter carrying one intervention, and then with all six interventions together. Each comparison uses the same model configurations, prompts, budgets and container image, and runs are interleaved in a random order.

**Tasks.** Held-out tasks that no archived run has seen, drawn from the same three benchmark families, plus a fixed conformance suite (section 3).

**Deployments.** The primary deployment is a Galaxy instance with a tool catalogue frozen for the study. Replication uses a second, independently administered Galaxy deployment with its own catalogue, to show whether an effect depends on one server's tools.

**Accounts.** Each run gets its own account and history namespace.

**Measures.** The baseline measures of Fig. 6a, with exclusive result-status classes kept separate from independent parameter/input mismatch flags. Diagnostic availability is assessed from full returned payloads; the archive's 240-character excerpt screen is only a proxy. Report same-goal operational recovery and scientific validity separately. Show refusal and completion rates together so rejecting every request cannot improve apparent fidelity.

**Success criterion.** Before execution, specify a practically useful target effect and biological guardrails. Size held-out task and replicate samples using clustered simulations at 90% power and familywise alpha 0.05. Freeze intervention-to-endpoint mappings and use multiplicity-adjusted tests or simultaneous intervals. Any accuracy non-inferiority margin requires independent domain justification and preregistration; a point estimate or directional change is insufficient.

## 2. Interventions

**R1. Bind parameters strictly and return what will run.** The adapter rejects any key that does not bind to the tool state Galaxy would build. It returns the resolved state, including conditional branches and defaults, before submission, and it offers a dry-run that returns this state without creating a job. Target measures: run calls compared and matched (baseline {{base_checked_matched}}) rises; mismatches reported after the job ({{fid_mismatch_after}} of run calls) fall to zero; and the dataset-only class contains no conditional resubmissions of the kind seen on bix-35-q1.

**R2. Explain every failure in a structured form.** Return phase, exit code when available, tool messages and explicit diagnostic-availability states. Pre-dispatch failures may legitimately lack standard error. The archived {{base_notext}} measure screens truncated excerpts; new measurements inspect full payloads and link the failed step, repair, successful execution and scientific output.

**R3. Expose versions and output semantics as tool metadata.** Search and inspection return underlying software versions, reference snapshots and output definitions, checked against executed containers and output fixtures. Assess detection of reference-version disagreement and scientifically defensible alternatives. Bix-45-q1 illustrates reference-version disagreement; its current-definition output is not established scientific invalidity.

**R4. Make discovery compact and independent of a history.** Search returns ranked tool cards of bounded size, and tool schemas can be requested without a history. Target measures: returned text spent on discovery (baseline {{base_discovery_text}}) falls; failures from missing or unusable history context (baseline {{a1_total}} calls) fall to zero; input tokens per run fall.

**R5. Cover the analysis life cycle in the agent interface.** The interface supports history copy, full dataset download and waits that can be resumed. Target measures: shell commands calling the Galaxy API directly (baseline {{base_shell_api}}) fall, and raw job submissions ({{raw_post_runs}} runs at baseline) fall to zero.

**R6. Attest where computation ran and isolate runs.** Each run gets its own account. Log staging, answer extraction and scientific computation separately, and record the location and input/output identities of each evidence-bearing step. The archived history-plus-shell-screen proportions ({{attest_BixBench50}}, {{attest_CompBio}} and {{attest_IWC}}) are unvalidated proxies. Measure receipt coverage, sensitivity and specificity against known execution-location fixtures; confirm that cross-run reads are refused.

## 3. Conformance suite

The suite is a fixed set of requests that tests the adapter and server, not the model, so it can run on any deployment and on other workbenches that expose tools to agents:

- Binding: requests that address conditional branches by name and by index, flat and nested keys, repeat elements and unknown keys. Each must be rejected or echoed exactly as resolved.
- Failure payloads: jobs designed to fail through a missing dependency, an unreadable input format, a memory limit or a non-zero exit code. Each must return a structured explanation.
- Metadata: for a sample of catalogue tools, the version and output definitions returned by inspection must match the wrapper's declarations.
- Discovery: schema requests without a history must succeed, and response sizes must stay within a stated limit.
- Life cycle: copying a history, downloading a dataset in full and resuming an interrupted wait must work through the interface.
- Isolation: attempts to read another run's history must be refused and logged.

The suite, its expected results and its scoring script are to be published with the intervention study. A first version is in `galaxy-oriented/conformance/` of the code release: 33 fixtures across R1–R6, five of them reproducing request shapes from archived bix-35-q1 job ledgers, with a scorer and a self-test in which reference responses pass and ten injected defects are each detected. It has not been run against any deployment, and its tool versions, images and output descriptions are frozen only at registration.

Every fixture includes input hashes, expected resolved state, allowed defaults, output identity and expected failure phase. Add legitimate positive controls, dataset-only tools and calls whose comparison is unsupported. Include deliberate mutations that remove parameter checks, truncate receipts or permit cross-account reads; the suite must detect them before intervention results are interpreted. Some pre-dispatch failures legitimately have no stderr, so check availability states rather than requiring stderr in every phase.

## 4. Reporting

Results are reported for each intervention, each deployment and each benchmark, together with the adapter versions, the frozen catalogues and every deviation from this protocol.

**Execution gate.** Freeze exact model/harness/interface commits, container and reference hashes, task counts, power calculations, budgets, retry rules, endpoint families and any non-inferiority margin in a dated registration. If the archived interface cannot be reconstructed, document the baseline departure. Count full campaigns and subagents, queue time and scientific compute. A second Galaxy deployment tests installation robustness; cross-platform transfer requires implementing the abstract contract on another workbench and testing equivalent positive, negative and mutation fixtures. No such validation is reported here.
