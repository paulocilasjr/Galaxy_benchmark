# Supplementary Note 1: Protocol for prospective validation

This note specifies the prospective steps that the retrospective archive cannot replace. No part of this protocol has been run. It addresses five gaps. The two arms differed in more than the execution environment. Repeatability was measured only within an arm. No history or transcript was replayed. No domain expert judged scientific validity blind to the arm. The trace audit was AI-assisted.

## 1. Matched-arm rerun

**Arms.** Flexible code, pinned code with retained scripts and provenance, and Galaxy. The pinned-code arm distinguishes benefits of version control and artifacts from the complete workbench intervention. All arms receive the same scientific prompt and information access, with a separate, versioned execution-policy block. Freeze policy text, hashes and lengths before any run. The archive had no identical Galaxy/code prompt pair ({{prompt_pairs_identical}}); differing policies remain part of the intervention even when scientific wording is identical.

**Budgets.** All arms get the same wall-clock, token and scientific-compute budgets per run, recorded identically. Queue time and cached tokens are reported separately. In the archive, IWC limits matched in only {{iwc_budget_matched}} replicate pairs, and CompBioBench stated a limit only in the code arm.

**Runtime.** All agent clients run in the same isolated container image, identified by digest. Pinned code and Galaxy use independently prepared, scientifically equivalent tool environments; flexible code may install dependencies. The Galaxy catalogue, code dependencies and reference datasets are frozen and hashed.

**Campaigns and reruns.** Every run belongs to one campaign per configuration × arm, declared before the first run. A run is repeated only for an infrastructure failure, under a rule declared in advance and applied without access to answers or scores. Every attempt is archived and reported. In the archive, {{cb_outcome_named_runs}} CompBioBench Galaxy runs came from campaigns whose names refer to wrong answers or target scores; this rule prevents that.

**Order and replicates.** Randomize and interleave task × configuration × arm × replicate blocks. Determine task and replicate counts by the power procedure below; five repeats are a planning candidate, not a justified sample size. Record seeds where supported; replicate labels are not assumed to supply paired model randomness.

**Contamination controls.** Web access to benchmark sources, such as dataset viewers and answer repositories, is blocked by a published deny-list, and every web fetch is logged. Each run uses its own Galaxy account and history namespace, so runs cannot read each other's outputs. In the archive, agents retrieved or tried to retrieve benchmark answers in {{retrieval_tasks}} task cases, and {{cross_run}} answers were copied between runs through the shared account.

**Tasks.** All tasks from the three archived benchmarks, plus held-out tasks that are not public, so that contamination can be estimated.

## 2. Endpoints and references

The primary user endpoint is independent replay success per assigned attempt; scientifically acceptable completion is the principal scientific endpoint. Benchmark acceptance and scored-outcome discordance are secondary, reported separately by benchmark. Independently adjudicate all 100 CompBioBench references: 46 predicted and 54 inferred items. Aggregate score agreement alone is insufficient. IWC references are prepared without agent outputs used in evaluation, and scores include biological components such as significant-gene agreement. Freeze input/reference hashes, method versions and allowable alternative solutions before enrollment.

## 3. Independent replay

**Galaxy arm.** Each analysis history is extracted as a workflow, with tool identifiers, versions and parameters taken from the job records. It is then re-run on a second Galaxy deployment with the same frozen catalogue. Each final output is compared with the original, exactly for text and within a declared tolerance for numbers. Replay success is the share of runs whose outputs are reproduced, and replay agreement is the share of runs whose submitted answer is unchanged.

**Code arms.** Preserved scripts and commands are re-executed in the recorded image using frozen dependency artifacts and reference data. A changed package resolution cannot silently substitute a newer version. The same artifact and answer-agreement measures are computed.

**Report.** First replay in a clean instance of the original environment, then on a second Galaxy deployment or code host; distinguish reproduction from transportability. Preserve actual scripts, resolved parameters, frozen dependencies and reference datasets. Use a frozen procedure to regenerate submitted answers. Retain unreconstructable and failed attempts in the assigned-attempt denominator, with common reconstruction time/intervention limits. Record missing scripts, nondeterminism, unavailable tools and changed references.

## 4. Blinded expert review

**Sample.** All discordant sets and a stratified probability sample of concordant sets. Record inclusion probabilities; use inverse-probability weights for population estimates and report enriched-sample estimates separately.

**Blinding.** Standardize output summaries and remove arm labels while retaining scientific information. Record reviewers' arm guesses. Trace review is partially blinded because provenance structure can reveal the arm. A separate usability assessment uses authentic records; it cannot be fully blinded.

**Packets.** `user-oriented/review/make_review_packets.py` in the code release generates blinded packets for the archived runs. It covers all discordant sets plus up to five concordant sets per benchmark × arm × stratum (660 runs in 95 tasks), with inclusion probabilities, a 20-run arm-guess pilot and 30 audit-verification cases. Because packets reveal benchmark references, they are written outside the repository. No review has been performed.

**Rubric.** Each run is rated as scientifically valid, defensible but different from the reference, or invalid. Reviewers also rate whether the analysis followed the request and whether each step can be checked from the record, and they record the time taken to check it.

**Reviewers.** Two domain experts per task review independently. Agreement is reported as Cohen's kappa, and a third expert resolves disagreements.

**Audit verification.** Human reviewers re-assess a random 20% of the archived audit's task cases and every case attributed to the Galaxy platform, blind to the AI-assisted assignment, and report agreement with the original assignments.

## 5. Analysis plan

Report task/source-capsule-clustered contrasts for Galaxy versus each code arm, separately by benchmark. Before execution, simulate clustered outcomes using archived rates and a range of task/configuration effects. Choose sample sizes for at least 90% power at familywise alpha 0.05 for a prespecified practically useful effect. Freeze endpoint families and use cluster-aware tests with Holm-adjusted P values or simultaneous bootstrap intervals; pointwise intervals are not described as multiplicity-adjusted.

Accuracy non-inferiority requires a domain-justified margin registered before enrollment. Planning simulations may examine 1, 2 and 5 percentage points, but the margin cannot be chosen after seeing results. Preserve biological component guardrails. Analyze assigned arms first; post hoc compliance exclusions cannot remove confounding.

## 6. Reporting

Every run, rerun and deviation from this protocol is reported, together with the prompt hashes, invocation records, catalogue list and deny-list. The prompts, policy blocks, summary format, rubric and analysis code are deposited before the first run.

**Execution gate.** Freeze exact model snapshots, reasoning settings, harness commits, container/dependency/reference hashes, held-out task counts, power results, practical-effect targets, any non-inferiority margin, budgets, retry/selection rules, review inclusion probabilities and statistical code. Record an immutable registration identifier. These author and experimental decisions remain pending; this protocol does not supply prospective results.
