"""Concrete, sheet-aware Source Data definitions for the integrated narrative.

No fallback descriptions are generated. Unknown columns cause the build to fail.
Null/blank spreadsheet cells represent unavailable/not-applicable observations,
not zeros; eligibility fields identify exclusions from the plotted estimand.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import narrative_common as nc


DOC = dict(nc.COLUMN_DOC)
DOC.update({
    'benchmark': 'Archived benchmark identifier: BixBench50 (BixBench-Verified-50), CompBio (CompBioBench), or IWC.',
    'cfg': 'Archived model configuration; the four primary configurations are GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro via Codex. Pooled/All labels denote aggregation.',
    'env': 'Assigned execution arm: open_ended_code or galaxy; this label does not verify the location of every computation.',
    'replicate': 'Repeated-attempt label 1–3; labels do not identify matched random seeds.',
    'cluster': 'Resampling unit: source capsule on BixBench; task identifier on CompBioBench and IWC.',
    'clusters': 'Number of distinct source-capsule/task resampling units represented in this estimate.',
    'endpoint': 'Benchmark-specific scored quantity: original evaluator acceptance (BixBench), reconstructed-key agreement (CompBio), or continuous workflow-output agreement (IWC).',
    'endpoint_type': 'Binary benchmark acceptance for BixBench/CompBio; continuous output agreement for IWC. These endpoints are not pooled.',
    'scale': 'Multiplier applied to the endpoint: 100 for percentage-point binary summaries and 1 for IWC agreement on the 0–1 scale.',
    'score': 'Per-run archived evaluator grade on BixBench; reconstructed-key grade on CompBio; continuous output agreement on IWC. Acceptance is not independent scientific adjudication.',
    'endpoint_score': 'Primary scored quantity for this archived run: binary BixBench/CompBio acceptance or continuous IWC output agreement. Missing for excluded/unscored endpoint populations.',
    'difference': 'Galaxy minus code point estimate for the stated endpoint/measure; binary percentages are percentage points, IWC performance is agreement units.',
    'ci95_low': 'Lower 2.5th percentile of the source-capsule/task cluster-bootstrap estimate (20,000 resamples); units match the reported estimate.',
    'ci95_high': 'Upper 97.5th percentile of the source-capsule/task cluster-bootstrap estimate (20,000 resamples); units match the reported estimate.',
    'galaxy_ci95_low': 'Lower 95% cluster-bootstrap bound for the Galaxy-arm quantity in this row.',
    'galaxy_ci95_high': 'Upper 95% cluster-bootstrap bound for the Galaxy-arm quantity in this row.',
    'open_ended_code_ci95_low': 'Lower 95% cluster-bootstrap bound for the code-arm quantity in this row.',
    'open_ended_code_ci95_high': 'Upper 95% cluster-bootstrap bound for the code-arm quantity in this row.',
    'galaxy_n': 'Number of Galaxy-arm units contributing to the estimate: runs for performance; replicate sets for repeatability.',
    'open_ended_code_n': 'Number of code-arm units contributing to the estimate: runs for performance; replicate sets for repeatability.',
    'ratio_ci95_low': 'Lower 95% cluster-bootstrap bound for the Galaxy/code replicate-set proportion ratio.',
    'ratio_ci95_high': 'Upper 95% cluster-bootstrap bound for the Galaxy/code replicate-set proportion ratio.',
    'primary_tasks': 'Number of primary scored tasks: 50 BixBench, 100 CompBioBench, nine of ten archived IWC tasks.',
    'runs_per_arm': 'Assigned runs contributing to the primary endpoint per arm: tasks × four configurations × three repeated attempts.',
    'run_id': 'Archived run identifier, unique within a benchmark/task; combines assigned arm, configuration and replicate.',
    'bix_benchmark_side_task': 'Task has a primary C1/C2/C3/C6 audit category; removed in the 15-task BixBench benchmark-side sensitivity.',
    'compbio_outcome_named_cell': 'Task × configuration cell contains at least one Galaxy run from a campaign whose name refers to an outcome/target score. The whole paired cell is removed in the sensitivity.',
    'iwc_zero_task': 'IWC task contains at least one zero-scored run in either primary arm; all attempts on that task are excluded in the corresponding sensitivity.',
    'iwc_atac_task': 'IWC ATAC-seq task; its references include calibration from agent runs. Flag does not mean every route/run was calibrated.',
    'budget_matched': 'Recorded Galaxy and code time limits are equal for this task × configuration × replicate pair; missing means unavailable, not unequal.',
    'population': 'Named subset/configuration population used for the estimate. Its eligibility rule is retained with the row; paired sensitivities and interface populations differ.',
    'tasks': 'Number of distinct benchmark tasks retained by this population, unless a textual task listing is supplied.',
    'runs': 'Number of run attempts contributing to the stated row/population; this is not a number of tool calls or independent tasks.',
    'n': 'Number of scored repeated attempts in this task × configuration × arm set; expected primary sets contain three.',
    'scores': 'Ordered scored values for the replicate set, retaining its three repeated-attempt outcomes. IWC values remain continuous.',
    'mean': 'Arithmetic mean of scored repeated attempts within this task × configuration × arm set.',
    'cat': 'Replicate-set category: 3/3 (all accepted), split (mixed outcomes) or 0/3 (all rejected) on binary benchmarks; within/split on the IWC >0.05 range rule.',
    'n_correct': 'Number of binary benchmark-accepted runs among the three repeated attempts; not applicable to continuous IWC agreement.',
    'n_errors': 'Number of rejected binary-scored runs among three repeated attempts. Error count does not identify its cause.',
    'all_three_correct': 'True if all three binary-scored repeated attempts were accepted; not a causal stability measure and not applicable to IWC.',
    'discordant': 'True for a binary set containing both accepted and rejected attempts; IWC uses maximum–minimum agreement >0.05.',
    'within_set_range': 'Maximum minus minimum scored outcome within the replicate set; IWC uses >0.05 to define discordance.',
    'within_set_sd': 'Sample standard deviation of the three scored repeated outcomes, using ddof=1.',
    'measure': 'Reported repeatability statistic, such as all_three_correct or discordant; IWC discordance uses the continuous range rule.',
    'sets': 'Number of task × configuration × arm replicate sets with the stated binary rejection count.',
    'denominator': 'Total replicate sets or other explicitly named eligible units for the stated proportion; does not imply statistical independence.',
    'percent': '100 × numerator/denominator for the stated eligible units; category counts may be task cases, not runs.',
    'udt_requested_archive': 'Archived run-level flag indicating a requested user-defined tool; separate from requests observed in the complete call table.',
    'traces': 'Assigned runs with a parsed primary execution trace; absence cannot be treated as evidence of no UDT use.',
    'archived_requesting_runs': 'Assigned Galaxy runs flagged in archived records as requesting a UDT, independent of complete-call-table observations.',
    'observed_attempting_runs': 'Assigned Galaxy runs with at least one observed run_galaxy_udt_and_wait call in the complete interface table.',
    'observed_submitted_runs': 'Assigned Galaxy runs with at least one UDT call whose returned submission flag records submission; missing flags are not negative evidence.',
    'observed_job_record_runs': 'Assigned Galaxy runs with at least one returned UDT job record, irrespective of final job state or usable outputs.',
    'observed_completed_ok_runs': 'Assigned Galaxy runs with at least one UDT job recorded in state ok. This can include a call whose returned status reports a dataset/output error.',
    'observed_returned_ok_runs': 'Assigned Galaxy runs with at least one UDT call returning status ok. This is distinct from a job being recorded in state ok.',
    'udt_calls': 'Observed run_galaxy_udt_and_wait interface calls; repeated attempts and freshly named tools count separately, not as independent runs.',
    'submitted_calls': 'UDT calls with a returned submitted=true flag; lack of this flag does not prove no submission.',
    'job_record_calls': 'UDT calls returning one or more job records, regardless of state or output usability.',
    'completed_ok_job_calls': 'UDT calls returning at least one job in state ok; a completed job is not necessarily a usable scientific output.',
    'returned_ok_calls': 'UDT calls whose structured result status is ok; distinguishes usable call receipts from recorded completed jobs.',
    'trajectory': 'Observed run-level UDT group based on presence of attempts and completed-ok job records. Groups are selected observationally, not randomized.',
    'score_mean': 'Mean final benchmark acceptance score among runs in the observed UDT trajectory group; not the UDT call-success rate.',
    'correct_runs': 'Number of final binary benchmark-accepted run answers in the observed UDT trajectory group; not applicable to continuous IWC agreement.',
    'interpretation': 'Explanation of the observational grouping or evidence limitation; does not certify a causal effect.',
    'case_id': 'Stable illustrative audit-case identifier used to link task descriptions to preserved trace locators.',
    'mechanism': 'Specific recorded decision/process proposed to explain this illustrative case; attribution remains retrospective.',
    'recorded_evidence': 'Trace/audit observation supporting the illustrative case, with the source locator retained separately.',
    'validation_opportunity': 'Concrete check that could have challenged the recorded answer or analysis; it was not an experimentally tested intervention.',
    'contrasting_run': 'Archived run or route offering a contrasting decision in the case; it is not a randomized control.',
    'observed_mechanism_runs': 'Number of reviewed runs in which the stated mechanism was observed, under the explicit count_definition.',
    'task_primary_runs': 'Number of assigned primary runs for this task/population. This denominator does not imply every run received independent case review.',
    'count_definition': 'Exact reviewed population and counting rule for observed_mechanism_runs; preserves the limit of the case evidence.',
    'caveat': 'Specific evidentiary limitation of this case, such as incomplete observations or an alternative explanation.',
    'audit_task': 'Task identifier as written in the original audit source, retained for exact heading/locator matching.',
    'audit_source': 'Repository-relative audit document containing the task-level classification or description.',
    'audit_heading_locator': 'Task-only heading prefix used with audit_heading_line to locate the case. Full audit headings are not reproduced because they can contain private reference-answer values.',
    'audit_heading_line': 'One-based line of the audit heading in the retained source text.',
    'category': 'Primary retrospective audit category C1–C8: equivalent answer, score artifact, unstated reference, platform/wrapper, agent analysis, answer exposure/provenance, changed result, or incomplete answer.',
    'insufficient_verification_tag': 'Non-exclusive retrospective task tag for inadequate checking/validation. False denotes no such tag, not proof the agent checked every run.',
    'domain_knowledge_tag': 'Non-exclusive retrospective task tag involving domain knowledge. Absence is not an independently measured knowledge score.',
    'primary_category': 'Original audit primary C1–C8 task-case category; one primary category is assigned even when several tags coexist.',
    'primary_category_label': 'Readable description of the primary C1–C8 category for this audited task case.',
    'tags': 'Non-exclusive retrospective task-case labels; their counts overlap and are not mutually exclusive error prevalences.',
    'purpose': 'Reason the preserved trace/document line is linked to an illustrative audit case.',
    'source_file': 'Repository-relative source file containing the evidence line. Compressed files use decompressed physical line numbering.',
    'decompressed_line': 'One-based physical line number in the decompressed retained source file; permits exact evidence retrieval.',
    'line_sha256': 'SHA-256 digest of the preserved source line used to verify exact evidence identity.',
    'expected_evidence_found': 'True when the predefined evidence string/check was found at the cited retained line; this checks the locator, not scientific truth.',
    'evidence_role': 'Type of support supplied by the locator, distinguishing a trace observation from an audit interpretation.',
    'input_tokens': 'Recorded cumulative input tokens for this run, including cached input/context rereads; does not include necessarily complete campaign/subagent/compute cost.',
    'cached': 'Recorded cached input tokens included within input_tokens; missing is unavailable rather than zero.',
    'uncached_input_tokens': 'input_tokens minus cached input; missing when either operand is unavailable or the subtraction is invalid.',
    'output_tokens': 'Recorded cumulative generated/output tokens for the run; excludes unrecorded campaign/subagent usage.',
    'has_trace': 'True when a primary trace summary contains parsed interface-action information; missing trace is not evidence of zero calls.',
    'model_primary': 'True for one of the four shared Codex configurations; false for unpaired Astra or superseded Claude Code configurations.',
    'primary_endpoint': 'True if the run belongs to a primary configuration and has a primary scored endpoint; the host-removal IWC task is excluded.',
    'n_mcp': 'All MCP calls in the original trace summary, including non-Galaxy servers; use the complete Galaxy-only table for manuscript interface counts.',
    'n_mcp_fail': 'Legacy MCP failure count in the original summary; excludes some later-reconciled transport/tool exceptions and is not the manuscript failure numerator.',
    'n_shell': 'Parsed local shell commands in the primary agent trace; may include staging or direct Galaxy API calls.',
    'n_shell_nonzero': 'Shell commands with nonzero recorded exit status; this unvalidated screen is not directly comparable with Galaxy failure/recovery classifications.',
    'n_web': 'Parsed web/search actions in the original run summary.',
    'disc_calls': 'Original summary calls classed as discovery (tool search/inspection); reconciled manuscript counts come from Galaxy-only operations.',
    'insp_calls': 'Original summary history/dataset inspection calls; retained as archive observations.',
    'exe_calls': 'Original summary execution-related calls (run/wait); retained as archive observations.',
    'other_calls': 'Original summary interface calls outside discovery/inspection/execution; retained as archive observations.',
    'disc_chars': 'Characters returned by original-summary discovery calls; a proxy for response context rather than token-level attribution.',
    'insp_chars': 'Characters returned by original-summary history/dataset inspection calls.',
    'exe_chars': 'Characters returned by original-summary execution-related calls.',
    'other_chars': 'Characters returned by original-summary other interface calls.',
    'shell_chars': 'Characters returned by parsed shell commands; does not prove whether the command performed scientific computation.',
    'token_kind': 'Recorded resource quantity: input_tokens (including cache), uncached_input_tokens (input minus cache), or output_tokens.',
    'task_scope': 'archive_token_tasks includes all ten IWC tasks for token-only sensitivity; primary_endpoint includes nine scored IWC tasks. BixBench/CompBio task lists coincide.',
    'n_galaxy': 'Number of non-missing token records in the three Galaxy repeated attempts for this task × configuration cell.',
    'n_open_ended_code': 'Number of non-missing token records in the three code repeated attempts for this task × configuration cell.',
    'eligible': 'True if each arm has all three token records and the code median is positive. False cells retain observed medians but have no plotted ratio.',
    'complete_cells': 'Eligible task × configuration cells with three token records in each arm and a positive code median for the stated quantity.',
    'candidate_cells': 'All task × configuration cells considered before complete-record/positive-denominator eligibility restrictions.',
    'median_ratio': 'Median across eligible task × configuration cells of Galaxy-arm median tokens divided by code-arm median tokens; not a ratio of pooled medians.',
    'greater_than_one_point': 'True when the point median Galaxy/code token ratio exceeds one; this does not establish statistical significance.',
    'ci_excludes_one': 'True when the exploratory 95% cluster-bootstrap ratio interval lies wholly above or below one.',
    'mean_endpoint': 'Arithmetic mean endpoint on the same tasks used for the model/resource comparison; binary endpoints are proportions, IWC remains 0–1 agreement.',
    'endpoint_ci95_low': 'Lower 95% source-capsule/task cluster-bootstrap bound for mean_endpoint on the common complete task population.',
    'endpoint_ci95_high': 'Upper 95% source-capsule/task cluster-bootstrap bound for mean_endpoint on the common complete task population.',
    'median_tokens': 'Median single-run token usage for this model/arm on the common complete task population; not the median arm-ratio estimand.',
    'token_ci95_low': 'Lower 95% source-capsule/task cluster-bootstrap bound for median single-run token usage.',
    'token_ci95_high': 'Upper 95% source-capsule/task cluster-bootstrap bound for median single-run token usage.',
    'common_tasks': 'Tasks with three input and score records in all eight primary configuration × arm groups: 50 BixBench, 86 CompBio, nine IWC. Model comparisons share this population.',
    'common_runs': 'Runs for this model/arm on common_tasks, normally three per common task; uncached records may be missing separately.',
    'common_clusters': 'Distinct source capsules/tasks represented in the common complete model/resource population.',
    'all_primary_mean_endpoint': 'Mean endpoint on all primary scored tasks for this model/arm, before common-task token restrictions; CompBio includes 100 tasks rather than 86.',
    'all_primary_scored_runs': 'Number of all-primary scored runs for this model/arm, before common-task token restrictions.',
    'all_primary_median_tokens': 'Median available single-run token usage across all primary endpoint tasks for this model/arm; task mix may differ through missing token records.',
    'all_primary_token_records': 'Number of non-missing token records across all primary endpoint tasks for this model/arm, before common-task restrictions.',
    'point_pareto_efficient': 'True if no other primary configuration in the same benchmark/arm has at least as high mean endpoint and at most as high median tokens, with one strict improvement. Point classification is not a validated ranking.',
    'dominated_by': 'Semicolon-separated model configurations with point estimates weakly better on both performance and tokens and strictly better on one. Blank means no point dominator, not missing data.',
    'median_rejected_over_accepted_tokens': 'Median incorrect/correct median-input ratio across discordant task × configuration × arm replicate sets with all three usages; comparison is conditional on observing both outcomes.',
    'split_sets': 'Discordant binary replicate sets with both accepted and rejected attempts and complete token records used for the sibling comparison.',
    'wilcoxon_p_unadjusted': 'Exploratory unadjusted Wilcoxon signed-rank P value for log sibling ratios, treating sets as observations. It does not account for capsule/task dependence or multiplicity; cluster intervals provide the stated uncertainty.',
    'inference': 'Specific interpretive limits of the descriptive/exploratory estimate, including absence of equivalence or causal evidence.',
    'operation': 'Galaxy-interface MCP operation name, such as search_galaxy_tools or run_galaxy_udt_and_wait; not a shell operation.',
    'calls': 'Number of observed Galaxy-interface operation calls in this benchmark/model population; repeat calls count separately.',
    'failed_calls': 'Calls meeting legacy failure rules or transport call_status=failed, restricted to Galaxy-interface servers/operations. Parameter mismatches are not uniformly in this union.',
    'failed_percent': '100 × failed_calls/calls under the reconciled Galaxy failure union, independent of scientific answer acceptance.',
    'returned_ok': 'Calls returning structured result_status=ok. Operations returning no status can succeed, so zero here is not a failure classification.',
    'returned_ok_percent': '100 × calls with result_status=ok / all calls to this operation; statusless read operations are not necessarily unsuccessful.',
    'returned_characters': 'Total characters of text returned to the agent by this Galaxy-interface operation. Characters are a context-volume proxy, not attributable input tokens.',
    'character_share_percent': '100 × operation returned characters / all Galaxy-interface returned characters in the same benchmark/model population.',
    'call_share_percent': '100 × operation calls / all Galaxy-interface calls in the same benchmark/model population.',
    'discovery_call_share_percent': 'Combined search_galaxy_tools plus inspect_galaxy_tool share of primary Galaxy-interface calls for this benchmark.',
    'discovery_character_share_percent': 'Combined tool-search plus tool-inspection share of primary Galaxy-interface returned characters for this benchmark.',
    'cost_mechanism': 'Archive-observed context/action burden motivating a prospective interface change; causal token savings have not been measured.',
    'intervention_to_test': 'Proposed versioned interface/instruction change to evaluate in matched runs; it is not an achieved reduction result.',
    'quality_guardrail': 'Scientific fidelity, evidence-retention or diagnostic requirement that must hold when testing lower context/API usage.',
    'status': 'Evidence state of the proposed intervention; reduction result remains pending in this package.',
    # Audit census and replicate persistence.
    'label': 'Readable label for the primary audit category of an audited task.',
    'task_cases': 'Number of audited task cases with this category/tag combination; one task case is the counting unit.',
    'denominator_cases': 'Number of audited task cases in the population represented by the row, not all benchmark tasks or failed runs.',
    'unit': 'Explicit counting/measurement unit of the row, such as an audited task or a task with at least one rejected primary run.',
    'scope': 'Named audit population for the tag counts: all 93 audited cases, their agent-analysis subset, or the census of 73 binary-benchmark tasks with a rejected primary run and its agent-analysis subset.',
    'selection': 'Rule by which the task entered the audit: every BixBench task with a rejected run, every CompBioBench task with a key-deviating run (any archived configuration), or an IWC low-agreement/concealed-change workflow.',
    'tag_combination': 'Exclusive combination of the two non-exclusive tags: verification only, verification and domain, domain only, or neither tag.',
    'cause_group': 'Grouping of primary audit categories: agent analysis (C5); benchmark, reference or provenance (C1, C2, C3, C6); Galaxy platform or wrapper (C4); other (C7, C8).',
    'denominator_tasks': 'Number of tasks with at least one rejected primary run in the stated benchmark or persistence group.',
    'rejected_primary_runs': 'Rejected runs of the four primary configurations (both arms) on the task or tasks in this row.',
    'denominator_runs': 'All rejected primary runs on census tasks in the stated benchmark scope.',
    'verification_tagged_tasks': 'Tasks in this row carrying the non-exclusive insufficient-verification tag.',
    'primary_failing_task': 'True if at least one primary-configuration run on this binary-benchmark task was rejected; the census population.',
    'max_rejected_in_primary_set': 'Largest number of rejected attempts (of three) in any primary task × configuration × arm set; blank for IWC.',
    'persistence': 'Persistent if any primary replicate set was rejected 3/3; sporadic if sets had at most one or two rejected attempts. IWC is continuous and not classified.',
    'code_rejected': 'Rejected attempts (of three) in the open-ended code set for this task × configuration.',
    'galaxy_rejected': 'Rejected attempts (of three) in the Galaxy set for the same task × configuration.',
    'paired_sets': 'Task × configuration pairs with three scored attempts in each arm.',
    'three_rejected_sets_code': 'Code sets with all three attempts rejected.',
    'three_rejected_sets_galaxy': 'Galaxy sets with all three attempts rejected.',
    'three_rejected_sets_both': 'Task × configuration pairs rejected 3/3 in both arms.',
    'three_rejected_tasks_code': 'Distinct tasks with at least one code set rejected 3/3.',
    'three_rejected_tasks_galaxy': 'Distinct tasks with at least one Galaxy set rejected 3/3.',
    'three_rejected_tasks_both': 'Distinct tasks with a 3/3-rejected set in both arms (not necessarily the same configuration).',
    'mixed_sets_code': 'Code sets with one or two rejected attempts.',
    'mixed_sets_galaxy': 'Galaxy sets with one or two rejected attempts.',
    # Prompt design.
    'prompt_pairs': 'Primary Galaxy/code prompt-file pairs matched by task, configuration and replicate.',
    'identical_prompt_pairs': 'Matched pairs whose prompt files have identical SHA-256 digests.',
    'median_prompt_words_code': 'Median word count of open-ended code prompt files in the primary configurations.',
    'median_prompt_words_galaxy': 'Median word count of Galaxy prompt files in the primary configurations; Galaxy prompts add execution policy.',
    # Aggregate token ratios and IWC task inputs.
    'ratio_of_totals': 'Total Galaxy tokens divided by total code tokens over the eligible task × configuration cells (three runs per arm); the primary arm comparison.',
    'galaxy_total_tokens': 'Sum of the token quantity over Galaxy runs in the eligible cells.',
    'code_total_tokens': 'Sum of the token quantity over code runs in the eligible cells.',
    'galaxy_mean_per_run': 'Mean token quantity per Galaxy run in the eligible cells.',
    'code_mean_per_run': 'Mean token quantity per code run in the eligible cells.',
    'mean_tokens': 'Mean single-run input tokens for this model/arm on the common complete task population; used for the frontier sensitivity.',
    'point_pareto_efficient_mean_tokens': 'Frontier classification using mean rather than median single-run input tokens; a sensitivity analysis.',
    'primary_endpoint_task': 'True for the nine IWC tasks with comparable arm scores; the host-removal task is token-only.',
    'mean_input_tokens': 'Mean recorded input tokens per run (including cache) for the task and arm, primary configurations.',
    'median_input_tokens': 'Median recorded input tokens per run for the task and arm, primary configurations.',
    'max_input_tokens': 'Largest recorded input tokens in one run for the task and arm.',
    'total_input_tokens': 'Sum of recorded input tokens over runs for the task and arm.',
    # Interface failures and friction.
    'failure_stage': 'Request rejected before a job ran (A classes), job failed during execution (B classes), or other exception (X, Z).',
    'call_outcome': 'Mutually exclusive UDT call outcome: returned ok; job error with diagnostic text (stderr, stdout or traceback); job error without diagnostic text; other non-ok return.',
    'inspected_never_run_percent': 'Percentage of distinct tools inspected within a traced Galaxy run that were never run in that run.',
    'count': 'Numerator of the friction measure, or the median for the searches-per-run row.',
})


def describe(col, sheet):
    """Return a concrete column definition in its Source Data table context."""
    if col not in DOC:
        raise ValueError(f'Missing concrete Source Data definition: {sheet}.{col}')
    if col in ('galaxy', 'open_ended_code'):
        arm = 'Galaxy' if col == 'galaxy' else 'code'
        if sheet == 'Token_cells':
            return f'Median available {arm}-arm token usage among the three attempts for this task × configuration; retained for ineligible cells, whose ratio is blank.'
        if sheet == 'F3_repeatability':
            return f'{arm}-arm mean replicate-set measure: percentage for discordant/all_three_correct, raw agreement units for IWC within_set_range/within_set_sd. This is not per-run accuracy.'
        if sheet in ('F2_scores', 'F2_sensitivity'):
            return f'{arm}-arm mean scored endpoint in the stated population: binary percentage on BixBench/CompBio; agreement units on IWC.'
        raise ValueError(f'Missing arm-value context: {sheet}.{col}')
    if col == 'ratio':
        if sheet == 'Token_cells':
            return 'Galaxy median / code median for this task × configuration × token quantity; blank when complete-record or positive-code eligibility fails. Blank is not zero.'
        if sheet == 'F3_repeatability':
            return 'Galaxy/code ratio of replicate-set proportions satisfying the stated repeatability measure; not a token or per-run accuracy ratio.'
    if col == 'difference' and sheet == 'F3_repeatability':
        return 'Galaxy minus code replicate-set mean: percentage points for discordant/all_three_correct; agreement units for IWC within-set range/SD.'
    if col in ('ci95_low', 'ci95_high'):
        bound = 'Lower' if col.endswith('low') else 'Upper'
        if sheet == 'F5_arm_totals':
            return f'{bound} 95% cluster-bootstrap bound for the Galaxy/code ratio of total tokens; source-capsule/task clusters, 20,000 resamples.'
        if sheet == 'F5_arm_ratios':
            return f'{bound} 95% cluster-bootstrap bound for median within-cell Galaxy/code token ratio; source-capsule/task clusters, 20,000 resamples.'
        if sheet == 'F5_outcome':
            return f'{bound} 95% cluster-bootstrap bound for median incorrect/correct sibling input ratio; discordant task × configuration × arm sets, 20,000 resamples.'
    if col == 'population' and sheet == 'F6_operations':
        return 'Interface population is four_primary_configurations: 66,316 Galaxy calls in 1,908 traced/1,920 assigned runs, covering all ten IWC tasks. This differs from the nine-task performance endpoint.'
    if col == 'percent' and sheet in ('F4_census', 'F4_persistence'):
        return '100 × tasks/denominator_tasks among tasks with at least one rejected primary run; a task-level, not run-level, share.'
    if col == 'percent' and sheet == 'F6_udt_outcomes':
        return '100 × calls/denominator: share of primary UDT calls with this exclusive outcome.'
    if col == 'percent' and sheet == 'F6_friction':
        return '100 × count/denominator; blank for the median searches-per-run row.'
    if col == 'denominator' and sheet == 'F6_friction':
        return 'Denominator of the friction measure, in the stated unit (traced runs, inspected tools, failed UDT jobs or follow-up calls).'
    if col == 'denominator' and sheet == 'F6_udt_outcomes':
        return 'All primary UDT calls on the benchmark.'
    if col == 'denominator' and sheet == 'F4_transitions':
        return 'Task × configuration pairs with three scored attempts in each arm.'
    if col == 'sets' and sheet == 'F4_transitions':
        return 'Task × configuration pairs with the stated numbers of rejected code and Galaxy attempts.'
    if col == 'measure' and sheet == 'F6_friction':
        return 'Trace-level friction measure from the archive scan of the primary Galaxy traces.'
    if col == 'tasks' and sheet in ('F4_census', 'F4_persistence'):
        return 'Tasks with at least one rejected primary run assigned to this category or cause group.'
    if col == 'population' and sheet == 'F6_failure_classes':
        return 'Interface population: four_primary_configurations (shown in Fig. 6c) or all_archived_configurations.'
    if col == 'runs_per_arm' and sheet == 'F5_arm_totals':
        return 'Galaxy runs contributing to the totals; equal to the number of code runs (three per eligible cell).'
    if col == 'greater_than_one_point' and sheet == 'F5_arm_totals':
        return 'True when the point ratio of totals exceeds one; this does not establish statistical significance.'
    if col == 'runs' and sheet == 'F5_IWC_tasks':
        return 'Runs with a recorded input-token count for this IWC task and arm (four primary configurations × three replicates).'
    return DOC[col]
