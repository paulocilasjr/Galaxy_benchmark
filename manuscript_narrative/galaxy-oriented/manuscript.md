# Measuring agent readiness in scientific workbenches through Galaxy

[Authors: author list, affiliations and corresponding author]

Analysis

## Abstract

Scientific workbenches are being connected to AI agents, but it is unclear what a workbench must expose for an agent's intended analysis to be executed faithfully, its failures diagnosed and its results attributed. We audited {{n_galaxy_runs}} archived agent runs that performed three biomedical benchmarks on usegalaxy.org through one Model Context Protocol interface, comprising {{n_interface_calls}} interface calls and {{n_jobs}} Galaxy jobs. Of these calls, {{fail_rate}}% met an exception or job-failure rule; error categories did not uniquely identify phase, and failed-job excerpts frequently lacked diagnostics. Requested and resolved parameters were compared and matched in {{fid_ok_checked}} of installed-tool run calls. Tool discovery accounted for {{disc_chars_CompBio}} to {{disc_chars_BixBench50}} of the text the interface returned. A third or more of shell commands in Galaxy-arm runs called the Galaxy API directly, outside the interface's checks. We report eight baseline measures and six requirements, each to be tested prospectively.

## [Introduction]

AI agents are increasingly expected to carry out biomedical analyses end to end[@gao2024;@biomni2026;@cellvoyager2026;@paper2agent2026]. Most agent benchmarks score the final answer[@bixbench2025;@compbiobench;@swebench2024], so they say little about the software the agent works through. Scientific workbenches such as Galaxy[@goecks2010;@galaxy2024] were built to make analyses reproducible and auditable[@nekrutenko2012;@sandve2013;@gruning2018cs]. They provide installed, versioned tools[@toolshed2014;@bioconda2018], typed datasets and analysis histories that record each job, much as workflow systems such as Nextflow, nf-core, Snakemake and the Common Workflow Language do for pipelines[@wratten2021;@nextflow2017;@nfcore2020;@snakemake2021;@cwl2022]. These guarantees were designed for human users. An agent instead discovers tools from text, fills parameters from schemas, interprets job states and decides when to retry. Where that interaction fails, the workbench's guarantees may not reach the analysis that is actually run. Studies of agent failures in general software settings point to the same interface between the model and its tools[@cemri2025;@react2023;@toolformer2023].

Here we treat Galaxy as the system under test and ask what a workbench must expose so that an agent's intended analysis is faithfully executed, diagnosably recoverable and attributable. We analysed every Galaxy-arm run in a paired benchmark archive, interface call by interface call and job by job. Runs from the archive's open-ended code arm provide descriptive token comparisons; the observational design does not isolate a causal workbench effect. A companion manuscript uses the same archive to compare accuracy and repeatability between execution arms from a user's perspective [Authors: companion manuscript citation]. The two papers share some descriptive measures, such as token use, but answer different questions, and neither depends on the other's conclusions. All measurements describe the archived Galaxy interface deployments and one public server in July to September 2026. They are baselines for prospective intervention studies, not estimates for other deployments.

## Results

### System layers, the provenance boundary and the evidence analysed

Agents reached usegalaxy.org through a Galaxy interface adapter built on the Model Context Protocol (https://modelcontextprotocol.io; Fig. 1a). The adapter exposed tool search and inspection, history and dataset inspection, runs of installed tools, runs of user-defined tools and waits for jobs. User-defined tools are agent-written code that Galaxy runs as a job in a declared container. Before submitting a run, the adapter validated the request against the tool state that Galaxy would build; after the job, it compared the requested parameters with those Galaxy had recorded. Galaxy's job records and analysis histories form a provenance boundary: computation inside it is recorded with tool identity, version, parameters and datasets. The agent also had a local shell for staging and answer extraction. Everything done there, including any direct call to the Galaxy API, bypassed the adapter's checks. Extended Data Fig. 1 shows how often runs used each capability.

The evidence comprises {{n_galaxy_runs}} Galaxy-arm runs on BixBench-Verified-50, CompBioBench and IWC, of which {{n_traces}} have parsed execution traces and {{n_histories}} have detailed analysis histories (Fig. 1b; Supplementary Table 1). The parsed calls comprise {{n_interface_calls}} Galaxy-interface calls and {{n_jobs}} analysis jobs. We excluded {{n_other_calls}} calls to client built-ins and external connectors from all interface measures. Runs took place from {{dates_BixBench50}} for BixBench-Verified-50, {{dates_CompBio}} for CompBioBench and {{dates_IWC}} for IWC, and BixBench-Verified-50 runs used {{harness_BixBench50}} harness or image labels. Tool versions and the server's catalogue were those current at run time, and we could not freeze them retrospectively.

### Failed interactions, diagnostic content and operational recovery

Of {{n_interface_calls}} Galaxy-interface calls, {{fail_total}} ({{fail_rate}}%) failed: {{fail_BixBench50}} on BixBench-Verified-50, {{fail_CompBio}} on CompBioBench and {{fail_IWC}} on IWC (Fig. 2a). The ordered taxonomy assigned {{fail_pre}} to interface, input or transport classes (A). These categories do not establish phase: {{a_calls_with_job_records}} A-class calls returned job records. A further {{fail_adapter}} were transport or tool exceptions omitted by the earlier failure rule; these include adapter validation and exceptions from Galaxy HTTP responses, so their origin is not uniformly pre-server. Another {{fail_post}} entered job/tool classes (B), and {{fail_unclassified}} remained unclassified. Failure rates and interaction styles differed between model configurations (Extended Data Fig. 2). The archived failure ledger counted {{legacy_total}} failures, including {{legacy_unclassified}} unclassified. It also included {{legacy_nongalaxy}} calls to non-Galaxy tool servers, {{legacy_nongalaxy_unclassified}} of them unclassified, which we excluded (Supplementary Table 2).

The largest single class was missing or unusable history context ({{a1_total}} calls). In {{a1_no_history}} of these calls, a tool schema was requested without any history, and in {{a1_unusable}} the history supplied could not be used. Galaxy builds a tool's parameter schema in the context of a history, so a request for a tool's interface without a usable history fails although nothing about the tool has changed. Other interface/input classes included parameter values or datatypes that Galaxy rejected, guessed tool identifiers, misused dataset or history identifiers and nested parameter structures that did not match the schema.

About half of tool-run calls returned ok, and retries were not consistently more successful than first attempts (Fig. 2b); {{first_attempt_share}} of run calls were first attempts at that tool in the run.

Returned excerpts often lacked diagnostic indicators when a job failed (Fig. 2c). Of failed user-defined-tool calls classified before execution, {{pre_udt_notext}} lacked a diagnostic indicator in the extracted excerpt, as did nearly all equivalent installed-tool calls. For runtime failures, {{runtime_notext}} lacked such an indicator. This excerpt screen is a proxy for diagnostic visibility, not verification of complete result contents. The largest post-job class was a failed job with no diagnostic text ({{b2_total}} calls). Server-side causes were also hidden. On CompBioBench, {{outage_udt_in_runs}} failed user-defined-tool calls occurred in the {{outage_runs}} runs whose traces show that Galaxy had no execution destination available. The interface never relayed that message; agents saw it only through the shell (Extended Data Fig. 3).

We followed non-ok tool-call episodes: the first non-ok call and subsequent calls of that tool family within a run, treating all user-defined tools as one family (Fig. 2d). This includes caught mismatches, timeouts and failed jobs. A later call returned ok in {{recover_BixBench50}}, {{recover_CompBio}} and {{recover_IWC}} of scored episodes. Final benchmark acceptance was assessed separately. Neither later ok nor acceptance establishes repair of the failed step or retention of the same scientific goal; episodes without grades are reported separately in Source Data.

### Semantic fidelity: from requested to executed analysis

A job that finishes in the ok state need not have run the analysis that the agent requested. We classified each of {{tool_run_calls}} installed-tool run calls by whether, and how, its requested parameters were checked against what Galaxy resolved (Fig. 3a). Checks cover explicit requested parameters, not all scientific intent, defaults or output semantics. Across benchmarks, {{fid_ok_checked}} of calls returned ok with a positive count of non-dataset parameters compared and matched. In {{fid_ok_dataset_only}} of calls ({{ok_dataset_only}} calls), ok accompanied no explicit non-dataset parameter to compare; another {{ok_unverified}} ok calls had non-comparable parameter provenance. These are mostly format-conversion tools with no other parameters, but the class also contains resubmissions that addressed a conditional parameter in a way the comparison could not see. The absence of a parameter check is therefore neither automatic noncompliance nor evidence of full fidelity. A further {{fid_mismatch_before}} returned a pre-submission mismatch status, {{fid_mismatch_after}} returned a parameter or input mismatch status after execution, and {{fid_failed}} had other non-ok outcomes. These exclusive status groups do not exhaust overlapping mismatch flags.

Parameter-provenance flags identified {{mismatch_calls}} calls with mismatches: {{mismatch_before_share}} before submission ({{mismatch_before}}) and {{mismatch_after}} after execution, including {{mismatch_with_failed_status}} with failed status. Separately, {{input_mismatch_calls}} calls had input-dataset mismatches; the parameter-or-input union was {{any_mismatch_calls}}. Mismatch rates varied strongly between tools (Fig. 3b). Among {{n_tools_40}} tools with at least 40 run calls, the ten highest had mismatches in {{top10_mismatch_range}} of calls, and {{tools_zero_mismatch}} had none. These descriptive rates pool versions, tasks and models; they do not isolate wrapper effects.

Five audited mechanisms show how execution or interpretation departed from the request (Fig. 3c). On bix-35-q1, a conditional parameter was silently rebound to its default: the agent requested the metric "evolutionary rate", and Galaxy ran "total tree length" with job state ok. The adapter flagged the mismatch, and six of seven affected runs resubmitted. One resubmission addressed the branch by index, sent no comparable parameter and passed unchecked; that answer was wrong. On bix-28-q3, the output was a variance under the requested metric name; the suspected wrapper parsing mechanism is inferred because its source was not archived. On bix-45-q1, the wrapper did not show which PhyKIT version it ran[@phykit2021]. Thirteen runs used the wrapper and two used user-defined tools. All 15 returned the current-definition value, judged scientifically defensible in the targeted audit, yet were scored incorrect against a retired-definition reference. On encode-atac-pipeline-q1, inputs staged without file extensions switched off adapter trimming without any error. On the IWC peptide-verification task, runs that used a legacy PepQuery wrapper scored lower than runs that used only the current version. This is an association: the order in which agents found the two versions was not controlled.

The targeted audit assigned Galaxy-related causes at three different units (Fig. 3d). In the targeted audit, Galaxy was a cause in {{attr_cases}} task cases. It was also a cause in {{attr_runs}} scored-incorrect BixBench-Verified-50 Galaxy runs, and it explained {{attr_div}} replicate divergences.

### Context consumption

Galaxy-arm runs used a median {{tok_BixBench50_input_tokens}}, {{tok_CompBio_input_tokens}} and {{tok_IWC_input_tokens}} times the input tokens of code-arm runs of the same task and configuration (Fig. 4a). The ratios were {{tok_BixBench50_uncached}}, {{tok_CompBio_uncached}} and {{tok_IWC_uncached}} for uncached input and {{tok_BixBench50_output_tokens}}, {{tok_CompBio_output_tokens}} and {{tok_IWC_output_tokens}} for output. Much of the difference was cached context re-read on each turn. The composition of returned text showed where the context went (Fig. 4b). Tool discovery, meaning search and inspection, made up {{disc_calls_BixBench50}}, {{disc_calls_CompBio}} and {{disc_calls_IWC}} of interface calls but {{disc_chars_BixBench50}}, {{disc_chars_CompBio}} and {{disc_chars_IWC}} of returned characters.

Input tokens rose with the number of actions in a run (Spearman correlations {{rho_BixBench50}}, {{rho_CompBio}} and {{rho_IWC}}; Fig. 4c), and many actions explored tools that were never used: of distinct tools that agents inspected, {{inspect_not_run_BixBench50}}, {{inspect_not_run_CompBio}} and {{inspect_not_run_IWC}} were never run (Fig. 4d). The sibling-run token comparison did not detect an outcome difference (Fig. 4e). Within discordant BixBench-Verified-50 replicate sets, incorrect runs used as many input tokens as their correct siblings: the median ratio was {{sib_tok_galaxy}} in the Galaxy arm and {{sib_tok_open_ended_code}} in the code arm. These associations motivate testing compact discovery while retaining scientific quality; they do not exclude task difficulty or establish that interface changes reduce tokens. Tokens measure recorded context consumption, not complete monetary or computational cost.

### Execution attribution

The Galaxy-arm label records an assignment; it does not show that every operation ran inside Galaxy. In Codex traces, {{api_shell_BixBench50}}, {{api_shell_CompBio}} and {{api_shell_IWC}} of Galaxy-arm shell commands called the Galaxy API directly (Fig. 5a). Most of these calls downloaded full datasets, copied the seed history, fetched tool schemas or polled job state, indicating lifecycle operations to assess prospectively. In {{raw_post_runs}} runs, agents also submitted jobs by raw API request, which skips the adapter's parameter check while the job itself is still recorded by Galaxy. Jobs submitted through the API still have Galaxy provenance, while request validation bypasses the adapter. API reads do not establish where scientific computation occurred. We distinguish it from guard bypass, local computation and cross-run reuse, which differ in what the record can show.

Run-level evidence could not fully establish where computation happened (Fig. 5b). Runs with a detailed history and no analysis program named in the shell made up {{attest_BixBench50}}, {{attest_CompBio}} and {{attest_IWC}} of Galaxy runs. In most of the rest, the shell named an analysis program, which leaves the location of computation uncertain; a few runs had no detailed history. The targeted audit confirmed cases outside the boundary. In {{local_answers}} CompBioBench runs, answers were computed locally after Galaxy execution of user-defined tools became unavailable, and in {{cross_run}} runs answers were copied from other runs through the shared account. These are observed cases, not prevalence estimates.

User-defined tools brought agent-written code inside the boundary (Fig. 5c,d). The four Codex configurations requested them in {{udt_req_BixBench50}} of Galaxy runs on BixBench-Verified-50 and {{udt_req_CompBio}} on CompBioBench. Of these calls, {{udt_ok_BixBench50}} and {{udt_ok_CompBio}} returned ok. Final accepted outcomes in runs with a successful user-defined-tool job and runs without a request were, respectively, {{udt_traj_BixBench50_1}} versus {{udt_traj_BixBench50_0}} on BixBench-Verified-50 and {{udt_traj_CompBio_1}} versus {{udt_traj_CompBio_0}} on CompBioBench. Runs in which every such job failed had accepted outcomes in {{udt_traj_CompBio_2}} on CompBioBench. These comparisons are associations across tasks and configurations.

### Baseline agent-readiness measures and the requirements they motivate

We summarized the audit as eight baseline measures, each a proportion with a stated direction of improvement and a numerator and denominator in Supplementary Table 4 (Fig. 6a). By benchmark, the measures were as follows: run calls compared and matched, {{base_checked_matched}}; run calls with a recorded parameter mismatch, {{base_unbound}}; failed interface calls, {{base_failed_calls}}; failed-job excerpts with no diagnostic indicator, {{base_notext}}; returned text spent on discovery, {{base_discovery_text}}; shell commands calling the Galaxy API directly, {{base_shell_api}}; runs with a detailed analysis history, {{base_history}}; and user-defined-tool calls returning ok, {{base_udt_ok}}.

Each measure motivates a requirement on the workbench and an intervention that could test it (Fig. 6b). The interface should bind parameters strictly and return what will run, explain every failure in a structured form, and expose software versions and output semantics as tool metadata. It should also make discovery compact and independent of a history, cover the analysis life cycle so that agents need not script the API, and attest where computation ran with per-run isolation. None of these interventions was tested here. Supplementary Note 1 specifies, for each, a conformance test, the held-out tasks, the measure that should move and the replication on a second Galaxy deployment.

## Discussion

Connecting an agent to a workbench does not by itself transfer the workbench's guarantees to the agent's analysis. In this archive, the guarantees broke down at four points. Agents could not always obtain a tool's interface; failed jobs often returned only a job-state summary; a job could run with parameters other than those requested; and agents moved work into the shell when the interface did not support an operation. The retained evidence supports baseline measures; prospective validation must determine whether changes resolve the failures.

Semantic fidelity is the property most specific to agents. A human user sees a tool form with its defaults and resolved conditionals; an agent sees a schema and a returned status. The adapter's requested-versus-resolved check caught most non-binding parameters before submission, but in {{fid_ok_dataset_only}} of installed-tool calls no explicit non-dataset parameter was compared. The bix-35-q1 resubmission also showed that a check comparing only what was sent can be bypassed without the comparator detecting it. A workbench that wants agents to use it correctly needs to return the resolved state before execution and treat unbound keys as errors.

Missing diagnostics and repeated interactions can increase context consumption, but this archive does not establish that causal chain. Discovery accounted for the largest share of returned text in two of three benchmarks, and about half of the inspected tools were never run. Compact, ranked tool cards and schemas that do not need a history would address both problems.

These lessons are likely relevant to other workbenches and tool platforms that expose tools to agents, including workflow systems, notebook services and laboratory information systems[@wratten2021;@knime2008;@jupyter2016;@fair2016]. Any system that compiles a typed request into an executed job faces the same questions. Did the request bind? What did the job run? Why did it fail? Where did the computation happen? We do not claim that the rates measured here transfer. They depend on Galaxy's tool catalogue, on this adapter and on the models that used it.

The study has limitations. It is retrospective and observational. We analysed archived adapter deployments on one public server over July to September with a shared account. Interface commits and runtime model metadata are incomplete, and catalogue and tool versions changed. Failure classes come from ordered rules applied to returned text, so classes with uninformative messages are undercounted. Recovery is defined at the level of tools and runs, not as a linked repair. The trace audit was AI-assisted, and its attribution counts cover targeted cases, not all runs. The requirements are hypotheses: each needs an intervention, a conformance test and replication on a second deployment, as specified in Supplementary Note 1, before it can be called validated.

Galaxy records substantial audit evidence, although history coverage is incomplete. The audited interface did not consistently expose that evidence while an analysis could still be corrected. The baseline measures in this study give developers of Galaxy and other workbenches a way to test whether such an interface works.

## References

[[REFERENCES]]

\newpage

## Figure legends

**Fig. 1 | System layers, provenance boundary and analysed evidence.** **a**, Components between a model configuration and an executed Galaxy job. The Galaxy interface adapter validates requests and compares requested with resolved parameters. Galaxy job records and analysis histories form the provenance boundary (dashed blue box). The vermillion dashed arrow marks direct Galaxy API calls from the local shell, which stay inside the boundary but outside the adapter's checks. Local computation and cross-run reuse fall outside the boundary. **b**, Analysed Galaxy-arm evidence per benchmark: runs, parsed traces, detailed histories, Galaxy-interface calls, other tool-server calls (excluded from interface measures), analysis jobs, run dates and the number of harness or image labels.

**Fig. 2 | Failed interactions, diagnostic indicators and later tool outcomes.** **a**, Error-coded Galaxy-interface calls by taxonomy and benchmark: interface/input/transport classes (sky blue), additional transport/tool exceptions with unknown phase (purple), job/tool classes (orange) and unclassified (grey). Mismatch-only statuses are measured separately. **b**, Calls returning ok, for first attempts at a tool identifier in a run (filled) and later calls (open); n, calls. Later calls need not be retries of the same scientific goal. **c**, Failed-job calls by phase and tool kind, split by diagnostic indicators in the extracted 240-character error excerpt; absence is a proxy. Two calls containing both pre-execution and runtime phases are assigned to pre-execution. **d**, Scored non-ok episodes (run × version-stripped tool family; all user-defined tools are one family), by later ok status and final evaluator acceptance. n at right gives scored episodes; Source Data gives missing grades. No linked repair or independent scientific recovery is established.

**Fig. 3 | Semantic fidelity: from requested to executed analysis.** **a**, Exclusive installed-tool call classes: ok with positive, matched parameter checks (light grey); ok with dataset inputs only (mid grey); ok with non-comparable/unverified parameter provenance (dark grey); pre-submission mismatch status (sky blue); post-execution parameter/input mismatch status (purple); other non-ok outcome (orange). n at right, calls. Parameter checks concern the explicit requested subset, not full scientific intent, defaults or output interpretation. Independent parameter/input mismatch flags, overlaps and call-level checks are in Source Data. **b**, Parameter-provenance mismatch rates, including failed calls, for the ten highest and three lowest tools among {{n_tools_40}} with at least 40 calls; versions are pooled. **c**, Five audited mechanisms by which execution or interpretation departed from the request, with their observed consequences. **d**, Share of audited task cases, scored-incorrect BixBench-Verified-50 Galaxy runs and Galaxy replicate divergences attributed to the Galaxy platform, a wrapper or the server, as primary cause (dark grey) or as contributing cause only (light grey).

**Fig. 4 | Context consumption.** **a**, Galaxy ÷ open-ended code ratio of input tokens (filled circles), uncached input (open diamonds) and output tokens (open squares): the median, over task × model configuration cells with all three usage records in each arm, of the within-cell ratio of medians, with 95% cluster-bootstrap intervals (20,000 resamples). **b**, Share of Galaxy-interface calls and of returned characters by call class. **c**, Input tokens against actions (Galaxy-interface calls plus shell commands) per Galaxy run (log–log), with Spearman correlations. **d**, Distinct inspected tools that were later run (dark blue) or never run (light blue), with the number of distinct tools, searches per run and unresolved identifiers. **e**, Ratio of input tokens of scored-incorrect to scored-correct sibling runs in discordant BixBench-Verified-50 replicate sets (median; two-sided Wilcoxon signed-rank test; n, replicate sets).

**Fig. 5 | Execution attribution.** **a**, Share of Galaxy-arm runs (Codex traces) whose shell commands called the Galaxy API for each operation; orange marks raw job submissions that skip the adapter's parameter check. The header gives the share of all shell commands that called the API. **b**, Galaxy-arm runs by the evidence on where computation happened: a detailed history with no analysis program named in the shell, a detailed history with an analysis program named (location uncertain), or no detailed history. **c**, Galaxy-arm runs requesting a user-defined tool, per model configuration (filled circles, BixBench-Verified-50; open triangles, CompBioBench). **d**, User-defined-tool calls returning ok (top) and the share of runs scored correct by user-defined-tool trajectory (bottom; groups with fewer than five runs are not shown).

**Fig. 6 | Baseline agent-readiness measures and the requirements they motivate.** **a**, Eight descriptive baseline measures for the Galaxy arm (circles, BixBench-Verified-50; triangles, CompBioBench; squares, IWC); dashed arrows give the direction of improvement, and values at right are in benchmark order. **b**, Requirements, their baseline or supporting evidence and interventions to test on held-out tasks. Version-metadata coverage has no systematic baseline; computation-location screening is not an attestation. No intervention was tested in this study.

## Methods

### Archive

We analysed the Galaxy-arm runs of an archive of 4,240 agent runs on three benchmarks: BixBench-Verified-50 (50 tasks; 750 Galaxy-arm runs)[@bixbench2025], CompBioBench (100 tasks; 1,200)[@compbiobench] and IWC (10 workflow-derived tasks; 120; https://github.com/galaxyproject/iwc). Four model configurations ran under the Codex agent harness (GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro), with three replicate runs per task. On BixBench-Verified-50, DeepSeek V4 Pro also ran under a superseded Claude Code harness. Open-ended code runs were used only for the token comparison (Fig. 4a) and the sibling-run comparison (Fig. 4e). No agent code was re-run, no Galaxy job was submitted and no file in the repository's ground-truth directory was opened for this analysis.

### Galaxy interface

The adapter was a Model Context Protocol server exposing nine operations: search tools, inspect a tool, inspect a history, peek at a dataset, inspect the archive inventory, run an installed tool and wait, run a user-defined tool and wait, wait for jobs, and stage a workspace file. Benchmark-specific deployments used separate tool-server namespaces. Before submission, the adapter built the tool state Galaxy would use and rejected requests whose keys would not bind. After submission, it compared the requested non-dataset parameters with those recorded in the job. User-defined tools were offered on BixBench-Verified-50 and CompBioBench but not on IWC.

### Call extraction

Every primary execution trace was parsed: Codex event logs, and Claude Code logs for the superseded harness. For each call we recorded the tool server, operation, arguments, returned status, error text, validation errors, the parameter-provenance record and the number of characters returned. Per-run counts of parsed calls and failed calls were checked against the archived run summaries and agreed for every run. Previously omitted transport failures were added. Four calls recovered from corrupted lines are retained separately, four truncated completions were unrecoverable, and sixteen client-rejected stderr attempts were not logged as MCP call items; these are excluded from main call counts. Calls to tool servers outside the Galaxy namespaces, such as client built-ins and external connectors, were flagged and excluded from all interface measures. The call table and its reconciliation report are released with the code (`derived/galaxy_calls/`).

### Failure taxonomy

Failed calls were classified by ordered rules applied to returned text. Classes A1–A8 describe interface, input and transport errors rather than verified failure phases: missing or unusable history context (A1), tool identifier not found (A2), nested parameter structure (A3), parameter value or datatype (A4), dataset or history identifier handling (A5), user-defined-tool schema (A6), upload datatype (A7) and server, transport or rate limit (A8). Classes B1–B5 describe job/tool errors: missing container dependency (B1), no diagnostic text (B2), runtime error with standard error (B3), input format, compression or index (B4) and memory or resource limit (B5). Class X covers additional transport or tool exceptions omitted by the legacy rule, including server-response exceptions; class Z covers unclassified failures. The failure endpoint excludes mismatch-only statuses, which are measured separately. A1 was split by whether any history was supplied. The rules are those of the archived failure ledger, extended with class X. Supplementary Table 2 gives them with a reconciliation against the ledger's counts.

### Diagnostics and recovery

A failed-job call was counted as having a diagnostic indicator when its extracted 240-character error excerpt matched non-empty standard error/output or a traceback. This proxy may miss later or differently formatted diagnostics. Phase (before execution or at run time) was read from the adapter's job-failure record. A non-ok episode begins with the first non-ok call within a run and includes later calls of the version-stripped installed-tool family; all user-defined tools count as one family. Later ok is an operational status proxy. Final acceptance means the original evaluator decision for BixBench-Verified-50, agreement with the reconstructed key for CompBioBench and output agreement of at least 0.95 for IWC, using nine matched tasks. CompBioBench grades are reconstructed-reference agreement; some IWC references are calibrated from archived runs. Neither endpoint establishes independent scientific validity.

### Semantic-fidelity classes

Each installed-tool run call was assigned one class. A call is "compared and matched" when it returned ok, parameter-provenance status was matched and checked_parameter_count was positive. It is "dataset inputs only" when ok accompanies no_explicit_non_dataset_parameters and a zero count. Other ok calls are unverified. It is "mismatch before submission" when validation found parameters that would not bind, and "mismatch after the job" when the job ran and the adapter reported a parameter or provenance mismatch. All other calls have other non-ok statuses. Independently, parameter and input mismatch flags are counted with overlap; tool-level parameter-mismatch rates use provenance status mismatch, including failed calls. Rates were computed for tools with at least 40 run calls, identified by their identifier without version.

### Context and shell-side API use

Interface calls were grouped into discovery (search and inspect tool), history and dataset inspection, execution (tool runs, user-defined-tool runs and waits) and staging or other operations. Distinct inspected tools that were never run were counted per benchmark from tool identifiers. Shell commands in Galaxy-arm Codex traces were scanned for BioBlend[@bioblend2013] and REST calls to the Galaxy API. They were classed as dataset download, history copy, schema fetch, job polling or raw job submission. Input tokens include cached input, and uncached input is input minus cached input. Token ratios use the four shared Codex configurations and require all three usage records in each arm. They are medians of within-cell ratios. Actions in Fig. 4c exclude non-Galaxy MCP calls. Recorded usage does not include complete campaign, subagent or compute costs.

### Execution attribution and audit

Run-level coverage combined history retrieval with a screen of shell commands for named analysis programs. The screen is an indicator, with false positives and false negatives; it neither confirms local computation nor bounds its prevalence. The targeted audit reviewed the traces of every task with at least one wrong, scored-incorrect or low-scoring run (93 task cases; `individual_error_analysis.md`). It assigned one primary cause per case and recorded whether the Galaxy platform, a wrapper or the server contributed, which gives primary, contributing-only and union counts. It also recorded flags for local computation, cross-run reuse and answer retrieval. The audit was performed with an AI assistant, and every assignment cites trace lines that a reader can check [Authors: describe the human review of the AI-assisted audit]. The run-level failure ledger assigned a primary and an optional secondary cause to every scored-incorrect BixBench-Verified-50 run.

### Readiness measures

Each measure in Fig. 6a is a descriptive proportion computed from Galaxy-arm traces and job records, not a validated readiness threshold. Directions are hypotheses subject to retained scientific quality; lower discovery/API use need not be beneficial by itself. Supplementary Table 4 gives its numerator, denominator, eligible units and direction of improvement.

### Statistics

Intervals are 95% percentile cluster-bootstrap intervals with 20,000 resamples[@davison1997], resampling tasks or source capsules (seed 20261002). Sibling-run token comparisons used two-sided Wilcoxon signed-rank tests, and correlations are Spearman coefficients over runs. All intervals are pointwise and exploratory. Values are rounded half away from zero.

### Use of AI tools

An AI assistant helped perform the targeted trace audit, write analysis and figure code and draft text. Documented independent human verification remains pending [Authors: name the assistants, versions and dates, document human verification and confirm responsibility for the content].

### Figures and reporting

Panels showing only Galaxy-arm runs use Galaxy blue. Where open-ended code appears, it is shown first, in vermillion squares, from the Okabe–Ito palette[@wong2011]. Every figure, Source Data workbook and number in the text is generated by `scripts/make_figures.py`, which writes the numbers to `numbers.json`. Each Source Data workbook includes a data dictionary sheet. Further information on research design is available in the Nature Portfolio Reporting Summary linked to this article.

## Data availability

The run archive, execution traces, Galaxy analysis-history snapshots and derived call tables are available at [Authors: archive DOI and Hugging Face dataset identifier]. Source Data are provided with this paper.

## Code availability

Analysis and figure code is in `manuscript_narrative/` of the project repository [Authors: repository URL and release DOI]. `manuscript_narrative/build_all.sh` rebuilds figures, workbooks and documents from frozen archived summaries and per-call tables using the pinned environment. CompBioBench per-item grades are reused from archived workbooks; independent regeneration requires authorized access to the private reconstructed key. Input and artifact hashes are recorded in `release_manifest.json`.

## Methods references

[[METHODS_REFERENCES]]

## Extended Data figure legends

**Extended Data Fig. 1 | Galaxy capabilities used by agents.** Share of Galaxy-arm runs that made at least one call of each kind, per benchmark; user-defined tools were not offered on IWC.

**Extended Data Fig. 2 | Interaction styles of the model configurations.** Per model configuration (Galaxy arm, BixBench-Verified-50): median interface calls per run, failed interface calls, median input tokens per run, runs requesting a user-defined tool, runs that opened a relevant skill (of the 114 runs whose task had one) and runs that scripted the interface library; shading is scaled within each column.

**Extended Data Fig. 3 | User-defined tool outcomes.** User-defined-tool calls by returned status on BixBench-Verified-50 and CompBioBench. The note gives the CompBioBench failed user-defined-tool calls that occurred in runs whose traces contain the server message that no execution destination was available, and those linked to it by job or dataset identifier.

## Supplementary information

Supplementary Tables 1–5 (`supplementary/Supplementary_Tables.xlsx`): 1, evidence inventory, run dates and harness labels; 2, failure-taxonomy rules and reconciliation with the archived ledger; 3, semantic-fidelity class definitions and per-tool mismatch rates; 4, readiness-measure definitions with numerators and denominators; 5, the number provenance of every value quoted in the text. Supplementary Note 1 (`supplementary/Supplementary_Note_1_interventions_and_conformance.md`): protocol for interventions, conformance tests and replication on a second deployment.

## Acknowledgements

[Authors: funding and acknowledgements]

## Author contributions

[Authors: contributions]

## Competing interests

[Authors: competing interests]

\newpage

## Figures

[[FIGURES]]

[[ED_FIGURES]]
