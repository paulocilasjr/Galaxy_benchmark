"""Wrap every table in design_metadata.json as {"source": ..., "rows": [...]} so each table carries its own source."""
import json, sys
from pathlib import Path

OUT = Path(sys.argv[1])
d = json.load(open(OUT / 'design_metadata.json'))
SPECIFIC = {
    ('q2_model_runtime', 'verification_counts'): 'analysis.json runs[].model_metadata.verification_status x presence of a model ID in docker_invocation.json / conda_invocation.json / IWC codex_invocation.json runtime.model',
    ('q3_prompts', 'distinct_hashes_per_task_and_condition'): 'sha256 of each run prompt.txt; distinct values per (benchmark, task, condition)',
    ('q3_prompts', 'distinct_hashes_per_task_condition_model'): 'sha256 of each run prompt.txt; distinct values per (benchmark, task, condition, model)',
    ('q3_prompts', 'galaxy_vs_code_prompt_identity'): 'prompt.txt sha256 compared between galaxy and open_ended_code for the same (benchmark, task, model, replicate)',
    ('q3_prompts', 'word_counts_by_condition'): "prompt.txt word count (regex \\b\\w+\\b); analysis.json runs[].prompt_words",
    ('q3_prompts', 'word_counts_by_configuration'): "prompt.txt word count (regex \\b\\w+\\b); analysis.json runs[].prompt_words",
    ('q3_prompts', 'galaxy_minus_code_words_per_task_model_cell'): 'median prompt.txt words per (task, model, condition); Galaxy minus code',
    ('q3_prompts', 'model_sharing_patterns'): 'prompt.txt sha256 grouped per (benchmark, task, condition); models[replicates] sharing each hash',
    ('q4_budgets', 'summary'): 'see q4_budgets.source',
    ('q4_budgets', 'compbio_budget_rows'): 'CompBio task.json timeout_minutes; conda_invocation.json timeout_seconds; prompt.txt "You have N minutes"',
    ('q4_budgets', 'iwc_by_configuration'): 'IWC codex_invocation.json wall_clock_timeout_seconds',
    ('q4_budgets', 'iwc_budget_by_start_time'): 'IWC codex_invocation.json wall_clock_timeout_seconds and started_at_utc',
    ('q4_budgets', 'iwc_open_ended_prompt_variant_by_budget'): 'IWC prompt.txt (analysis_steps.jsonl requirement) x codex_invocation.json wall_clock_timeout_seconds',
    ('q4_budgets', 'iwc_per_run'): 'IWC codex_invocation.json wall_clock_timeout_seconds, started_at_utc, run_root; prompt.txt',
    ('q5_dates', 'galaxy_history_times_by_configuration'): 'source_snapshots/galaxy/<history_id>/history.json create_time, update_time; run linkage via evidence runs[].source_ids',
    ('q5_dates', 'galaxy_history_times_by_benchmark'): 'source_snapshots/galaxy/<history_id>/history.json create_time, update_time',
    ('q5_dates', 'evidence_collection_by_benchmark'): 'history_analysis_evidence.json sources[].retrieval_time_utc and audit.timestamp_utc',
    ('q5_dates', 'histories_linked_to_more_than_one_run'): 'history_analysis_evidence.json runs[].source_ids (src_galaxy_<history_id>)',
    ('q7_campaign_selection', 'compbio_vectors'): 'run_record.json agent_workspace campaign directory; CompBio/compBio_overview_audit.json score_vectors[] (campaign_id, score_type, hash_matches, source_campaigns)',
    ('q7_campaign_selection', 'compbio_totals_by_condition'): 'sum of q7_campaign_selection.compbio_vectors',
    ('q7_campaign_selection', 'compbio_campaign_run_counts'): 'run_record.json agent_workspace campaign directory per archived CompBio run',
    ('q7_campaign_selection', 'compbio_provenance_tsv_summary'): 'CompBio/source_snapshots/aggregate_metadata/compbiobench/replicates/<campaign_id>/provenance.tsv source_run_id, source_type (answer column not read)',
    ('q7_campaign_selection', 'compbio_archive_vs_registry_differences'): 'run_record.json campaign vs compBio_overview_audit.json score_vectors[].source_campaigns',
    ('q7_campaign_selection', 'bixbench_iteration_settings'): 'history_analysis_evidence.json runs[].iteration_setting; attempt.json experiment',
    ('q7_campaign_selection', 'iwc_run_roots'): 'IWC codex_invocation.json run_root',
    ('q8_other_differences', 'skills'): 'run_trace/skill_inventory.json copied_skills|skills, skipped_skills, exclude_regex; IWC codex_invocation.json skills_bundle',
    ('q8_other_differences', 'local_inputs'): 'inputs_manifest.json inputs[]',
    ('q8_other_differences', 'network'): 'docker_invocation.json blocked_hosts; conda_invocation.json blocked_host_suffixes, network_filter_mode; IWC docker_isolation.json network.mode; prompt.txt',
    ('q8_other_differences', 'iwc_isolation'): 'IWC run_trace/docker_isolation.json resources, mounts, environment_variable_names; codex_invocation.json solution_mode, skills_bundle.revision',
    ('q8_other_differences', 'compbio_routing'): 'CompBio run_trace/history_routing_tags.json tags_after; presence of history_routing_tags_disabled.json',
    ('q8_other_differences', 'items'): 'per-item source field',
}
for sec, body in d.items():
    if not (sec.startswith('q') and isinstance(body, dict)):
        continue
    src = body.get('source')
    for k, val in list(body.items()):
        if isinstance(val, list) and val and isinstance(val[0], dict):
            body[k] = {'source': SPECIFIC.get((sec, k), src), 'rows': val}
        elif k == 'prompt_content_flags':
            body[k] = {'source': 'prompt.txt phrase matching (definitions below)', 'rows': val['rows'], 'definitions': val['definitions']}
        elif k == 'iwc_pair_matching':
            val['source'] = 'IWC codex_invocation.json wall_clock_timeout_seconds (= iwc_scientific_audit.json runs[].wall_timeout_seconds), paired on task, model, replicate'
            for kk in ('by_model', 'by_task', 'pairs_detail'):
                val[kk] = {'source': val['source'], 'rows': val[kk]}
        elif k == 'rows' and isinstance(val, list):
            pass  # already a sourced table (section-level source)
d['unknowns_not_recorded'] = {'source': 'absence of any field carrying the value across the files listed in source_files', 'rows': [{'item': u} for u in d['unknowns_not_recorded']]}
(OUT / 'design_metadata.json').write_text(json.dumps(d, indent=1))
print('wrapped')
