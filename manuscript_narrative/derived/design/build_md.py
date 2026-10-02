"""Render design_metadata.md from design_metadata.json."""
import json, sys
from pathlib import Path

OUT = Path(sys.argv[1])
d = json.load(open(OUT / 'design_metadata.json'))
L = []
w = L.append

LABEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
         'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro (Codex)', 'deepseek_v4_pro_via_claude_code_superseded': 'DeepSeek V4 Pro (Claude Code, superseded)',
         'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro 0813 (Codex)', 'codex_deepseek_v4_pro': 'DeepSeek V4 Pro (Codex)', 'codex_gpt_6_astra': 'GPT-6 Astra'}
COND = {'galaxy': 'Galaxy', 'open_ended_code': 'Code'}
lab = lambda m: LABEL.get(m, m)


def v(x, nr='not recorded'):
    if x is None or x == '' or x == [] or x == {}:
        return nr
    if isinstance(x, float) and x.is_integer():
        return f'{int(x):,}'
    if isinstance(x, dict):
        return '; '.join(f'{k}: {v(val)}' for k, val in x.items())
    if isinstance(x, list):
        return ', '.join(map(str, x))
    if isinstance(x, int) and not isinstance(x, bool):
        return f'{x:,}'
    return str(x).replace('|', '\\|')


def table(headers, rows):
    w('| ' + ' | '.join(headers) + ' |')
    w('|' + '|'.join('---' for _ in headers) + '|')
    for r in rows:
        w('| ' + ' | '.join(v(c) for c in r) + ' |')
    w('')


q4 = d['q4_budgets']; pm = q4['iwc_pair_matching']; q7 = d['q7_campaign_selection']
tot = {r['condition']: r for r in q7['compbio_totals_by_condition']}
bix_nonprimary = sum(r['n_runs'] for r in q7['bixbench_iteration_settings'] if r['ev_iteration_setting'] not in ('primary', None))
iwc_nonprimary = [r for r in q7['iwc_run_roots'] if not r['primary_root']]
iwc_np = {c: sum(r['n_runs'] for r in iwc_nonprimary if r['condition'] == c) for c in ('galaxy', 'open_ended_code')}

w('# Design differences between the open-ended-code and Galaxy arms')
w('')
w(f"Compiled {d['generated_utc'][:10]} from the archived Galaxy_benchmark repository. {d['scope']} "
  "Machine-readable tables, with the exact source fields, are in `design_metadata.json`; `per_run_design_metadata.csv` lists one row per run. "
  "'Not recorded' means no field holding the value was found; nothing is imputed. One public Galaxy username and two account tokens are redacted, as the archive itself does elsewhere.")
w('')
w('## Key differences')
w('')
w(f"- **IWC time budgets differ within matched replicate pairs.** Each IWC run had a 6 h (21,600 s) or 12 h (43,200 s) wall-clock ceiling (`codex_invocation.json` `wall_clock_timeout_seconds`, identical to `iwc_scientific_audit.json` `wall_timeout_seconds` for 240/240). The budget depends only on start time: all runs started up to 2026-08-28 13:44 UTC had 6 h, and all runs started from 13:49 UTC had 12 h. Of {pm['pairs']} same-task, same-model, same-replicate Galaxy/code pairs, **{pm['matched_budget_pairs']} have matching budgets** and {pm['mismatched_budget_pairs']} do not ({pm['by_combination'].get('12h Galaxy / 6h code', 0)} with 12 h Galaxy and 6 h code; {pm['by_combination'].get('6h Galaxy / 12h code', 0)} with 6 h Galaxy and 12 h code).")
w("- **Run budgets elsewhere are asymmetric or absent.** CompBio code prompts state \"You have 120 minutes\" for 1,294/1,300 runs (240 or 480 min for 6 single-item recovery runs). No budget is recorded for CompBio Galaxy runs or for any BixBench50 run.")
w(f"- **Prompts always differ between arms.** No task/model/replicate pair shares a prompt file ({sum(r['identical_hash_pairs'] for r in d['q3_prompts']['galaxy_vs_code_prompt_identity'])} identical of {sum(r['pairs_compared'] for r in d['q3_prompts']['galaxy_vs_code_prompt_identity']):,} compared). BixBench and CompBio Galaxy prompts add execution policy: compute on Galaxy only, copy or use the assigned history, banned tools, a local-code allowlist, route selection and UDT rules, MCP tool names and blocking-call timeouts. By median they are longer: 702 vs 368 words in BixBench50 and 938 vs 227 in CompBio. IWC prompts differ in only two lines plus the logging instruction: 55 code prompts (the 12 h code runs) require structured `analysis_steps.jsonl` records, and all Galaxy prompts ask for a concise log. Prompt versions also vary within arms: BixBench uses two versions per arm (Galaxy: GPT models vs DeepSeek; code: GPT-5.5 and DeepSeek vs GPT-5.6), and CompBio Galaxy uses an older and a newer (`promptv2`) version.")
w("- **Harnesses and containers are not constant within configurations.** BixBench GPT-5.5 Galaxy runs used 4 image tags, mostly `full-blocking-20260715`, while its code runs mostly used `no-static-udt-resolver-20260714`. CompBio Galaxy runs ran in Docker (`galaxy-eval-agent:latest`), while CompBio code runs ran in a host conda clone with no container. IWC used one image digest for both arms, the same digest as the CompBio Galaxy image.")
w(f"- **CompBio vectors are composite campaigns, mostly in the Galaxy arm.** {tot['galaxy']['runs_from_other_campaigns']}/1,200 Galaxy runs and {tot['open_ended_code']['runs_from_other_campaigns']}/1,300 code runs come from a campaign other than the largest one in their replicate vector. {tot['galaxy']['runs_from_outcome_named_campaigns']} Galaxy runs and 0 code runs come from campaigns whose names reference wrong answers or target scores (`wrong19`, `wrongset`, `fastwrong`, `target84`, `near84`). Of the 2,400 archived paired runs, 2,399 match the registry's source campaign for that item.")
w(f"- **Reruns and replacements exist in all benchmarks.** BixBench50 has {bix_nonprimary} non-primary iteration settings, and IWC has {iwc_np['galaxy']} Galaxy and {iwc_np['open_ended_code']} code runs from rerun roots, both detailed under Q7.")
w("- **Other arm-specific conditions.** BixBench DeepSeek Galaxy runs (both harnesses, 300) had no local input files, while GPT Galaxy runs and all code runs did. Galaxy-only skills (`galaxy-tool-submission`, `galaxy-udt-authoring`) were removed from code runs. BixBench DeepSeek-via-Codex code runs still mounted a Galaxy API key. Some CompBio Galaxy histories were tagged `training`. Galaxy-arm registry campaigns carry two redacted account labels.")
w('')

# Q1
w('## Q1. Agent harness and container')
w('')
w(f"Source: {d['q1_harness_container']['source']}.")
w('')
table(['Benchmark', 'Model', 'Arm', 'analysis.json harness', 'Docker image', 'Image ID', 'Backend', 'Agent runtime', 'Runs'],
      [[r['benchmark'], lab(r['model']), COND[r['condition']], r['mm_harness'], r['image'], (r['image_id'] or '')[:19] + ('...' if r['image_id'] else ''),
        r['execution_backend'], r['agent_runtime'], r['n_runs']] for r in d['q1_harness_container']['rows']])
w(d['q1_harness_container']['note'])
w('')

# Q2
w('## Q2. Runtime model IDs and reasoning settings')
w('')
w(f"Source: {d['q2_model_runtime']['source']}.")
w('')
table(['Benchmark', 'Model', 'Arm', 'Verified runtime ID', 'Reasoning', 'Status', 'Invocation model', 'Invocation reasoning', 'Service tier', 'Provider', 'Runs'],
      [[r['benchmark'], lab(r['model']), COND[r['condition']], r['mm_verified_runtime_id'], r['mm_reasoning'], r['mm_verification_status'],
        r['invocation_model'], r['invocation_reasoning'], r['invocation_service_tier'], r['invocation_provider'], r['n_runs']] for r in d['q2_model_runtime']['rows']])
w('Verification counts (status from task evidence; "invocation record" means a model ID was re-read from an invocation file):')
w('')
table(['Benchmark', 'Arm', 'Evidence status', 'Invocation record', 'Runs'],
      [[r['benchmark'], COND[r['condition']], r['mm_verification_status'], 'yes' if r['has_invocation_model'] else 'no', r['n_runs']] for r in d['q2_model_runtime']['verification_counts']])
w(d['q2_model_runtime']['note'])
w('')

# Q3
q3 = d['q3_prompts']
w('## Q3. Prompts')
w('')
w(f"Source: {q3['source']}.")
w('')
w('Distinct prompt-file hashes per task and arm, across all models and replicates:')
w('')
table(['Benchmark', 'Arm', 'Min', 'Median', 'Max', 'Tasks by number of distinct hashes'],
      [[r['benchmark'], COND[r['condition']], r['min'], r['median'], r['max'], r['tasks_by_distinct_count']] for r in q3['distinct_hashes_per_task_and_condition']])
w('Galaxy and code prompt identity:')
w('')
table(['Benchmark', 'Pairs compared (task, model, replicate)', 'Identical prompt hash', 'Tasks sharing any hash across arms'],
      [[r['benchmark'], r['pairs_compared'], r['identical_hash_pairs'], r['tasks_with_any_hash_shared_across_conditions']] for r in q3['galaxy_vs_code_prompt_identity']])
w('Prompt length (words in the archived `prompt.txt`). `analysis.json` `prompt_words` counts only the task question for BixBench and CompBio, so it is the same in both arms:')
w('')
table(['Benchmark', 'Arm', 'Runs', 'Median words (prompt.txt)', 'IQR', 'Median analysis.json prompt_words'],
      [[r['benchmark'], COND[r['condition']], r['n_runs'], r['prompt_file_words_median'], f"{r['prompt_file_words_q1']:.0f}-{r['prompt_file_words_q3']:.0f}", r['analysis_json_prompt_words_median']] for r in q3['word_counts_by_condition']])
table(['Benchmark', 'Model', 'Arm', 'Median words', 'Range'],
      [[r['benchmark'], lab(r['model']), COND[r['condition']], r['prompt_file_words_median'], f"{r['prompt_file_words_min']}-{r['prompt_file_words_max']}"] for r in q3['word_counts_by_configuration']])
w('Per task and model, the median Galaxy prompt length minus the median code prompt length:')
w('')
table(['Benchmark', 'Median difference (words)', 'Min', 'Max', 'Task-model cells'],
      [[r['benchmark'], r['median'], r['min'], r['max'], r['task_model_cells']] for r in q3['galaxy_minus_code_words_per_task_model_cell']])
w('Prompt content flags (runs whose prompt contains the phrase; definitions in JSON):')
w('')
fl = ['galaxy_not_required', 'no_local_inputs_staged', 'mentions_skills', 'udt_mentioned', 'start_timeout_300', 'compbio_galaxy_old_marker', 'compbio_galaxy_promptv2_marker',
      'no_wallclock_limit_instruction', 'iwc_analysis_steps_jsonl', 'iwc_concise_log', 'mentions_internet']
table(['Benchmark', 'Model', 'Arm', 'Runs', '"Galaxy is not required"', 'No local inputs', 'Skills', 'UDT', 'start_timeout 300', 'CompBio old Galaxy prompt', 'CompBio promptv2',
       'No wall-clock limit on calls', 'IWC analysis_steps.jsonl', 'IWC concise log', 'Internet', 'Stated minutes'],
      [[r['benchmark'], lab(r['model']), COND[r['condition']], r['n_runs']] + [r[f] for f in fl] + [r['stated_minutes_in_prompt']] for r in q3['prompt_content_flags']['rows']])
w('Prompt versions (models that share one prompt file for a task):')
w('')
w('- BixBench50: each arm has two versions for all 50 tasks. Galaxy: the GPT family shares one version, and both DeepSeek harnesses share the other (no local inputs, different blocking-call text). Code: GPT-5.5 and both DeepSeek harnesses share one version, which includes "Galaxy is not required"; GPT-5.6 Sol and Luna use a version without that sentence.')
w('- CompBio: in 62/100 tasks, GPT-5.5 r1 and Sol r1 share an older Galaxy prompt, and all other Galaxy runs share `promptv2`. Galaxy prompt versions follow campaign names exactly: `promptv2` appears in the campaign name of every run with the new text. In code, GPT-5.5 r1 (campaign `no_project_skills`) differs from all other runs in 98/100 tasks.')
w('- IWC: all 12 Galaxy runs per task share one prompt (10/10 tasks). Code prompts take 2-3 versions per task, mainly the `analysis_steps.jsonl` requirement, which tracks start date and budget.')
w('')

# Q4
w('## Q4. Time and resource budgets')
w('')
w(f"Source: {q4['source']}.")
w('')
table(['Benchmark', 'Arm', 'Run budget', 'Note'], [[r['benchmark'], r['condition'], r['run_time_budget'], r['note']] for r in q4['summary']])
w('IWC budgets by configuration (runs; matches IWC/result_section_iwc.md Table 1):')
w('')
table(['Model', 'Arm', '6 h', '12 h'], [[lab(r['model']), COND[r['condition']], r['runs_6h'], r['runs_12h']] for r in q4['iwc_by_configuration']])
w('IWC budget by start time (`codex_invocation.json` `started_at_utc`):')
w('')
table(['Budget (h)', 'First start', 'Last start', 'Runs'], [[r['budget_h'], r['min'], r['max'], r['size']] for r in q4['iwc_budget_by_start_time']])
w(f"IWC matched-budget pairs ({pm['definition']}): **{pm['matched_budget_pairs']}/{pm['pairs']} matched**.")
w('')
combos = sorted(pm['by_combination'])
table(['Model', 'Pairs', 'Matched'] + combos, [[lab(r['model']), r['pairs'], r['matched']] + [r.get(c, 0) for c in combos] for r in pm['by_model']])
table(['Task', 'Pairs', 'Matched'], [[r['task'], r['pairs'], r['matched']] for r in pm['by_task']])
w('IWC code-arm prompt variant against budget:')
w('')
table(['Prompt requires analysis_steps.jsonl', 'Budget (h)', 'Runs'], [[r['iwc_analysis_steps_jsonl'], r['budget_h'], r['n_runs']] for r in q4['iwc_open_ended_prompt_variant_by_budget']])
w('CompBio budget fields:')
w('')
table(['Model', 'Arm', 'task.json timeout_minutes', 'conda timeout_seconds', 'Prompt minutes', 'Runs'],
      [[lab(r['model']), COND[r['condition']], r['task_timeout_minutes'], r['conda_timeout_seconds'], r['stated_minutes'], r['n_runs']] for r in q4['compbio_budget_rows']])
w('Recorded resource limits: IWC containers only (both arms identical): 8 GiB memory, 4 CPUs, pids limit 512, bridge network (`docker_isolation.json`). No CPU or memory limits are recorded for BixBench or CompBio. Token and retry budgets are not recorded in any benchmark.')
w('')

# Q5
q5 = d['q5_dates']
w('## Q5. Dates')
w('')
w(f"Source: {q5['source']}.")
w('')


def rr(x):
    return 'not recorded' if not x else f"{x['min'][:16].replace('T', ' ')} to {x['max'][:16].replace('T', ' ')}"


table(['Benchmark', 'Model', 'Arm', 'Workspace prepared (run_record)', 'Recorded run start', 'Recorded run end', 'Galaxy history created (evidence)', 'CompBio campaign-name timestamps'],
      [[r['benchmark'], lab(r['model']), COND[r['condition']], rr(r['run_record_prepared_at_utc']),
        rr(r['iwc_codex_invocation_started_at_utc'] or r['completion_json_started_at']),
        rr(r['iwc_docker_postrun_finished_at'] or r['completion_json_finished_at'] or r['usage_json_written_at_utc']),
        rr(r['evidence_history_create_time']), rr(r['compbio_campaign_name_timestamp'])] for r in q5['run_dates_by_configuration']])
w('Run start: IWC `codex_invocation.json` started_at_utc, or BixBench DeepSeek `completion.json` started_at. Run end: IWC `docker_postrun.json` finished_at, BixBench DeepSeek `completion.json` finished_at, or `usage.json` written_at_utc (BixBench GPT and Claude runs). CompBio campaign timestamps are parsed from campaign directory names and converted to UTC (names ending in ET are taken as US Eastern daylight time, UTC-4).')
w('')
w('Galaxy history snapshot times (`history.json`):')
w('')
table(['Benchmark', 'Unique histories', 'create_time range', 'update_time range'],
      [[r['benchmark'], r['unique_histories'], f"{r['create_time_min'][:16]} to {r['create_time_max'][:16]}", f"{r['update_time_min'][:16]} to {r['update_time_max'][:16]}"] for r in q5['galaxy_history_times_by_benchmark']])
table(['Benchmark', 'Model', 'Links', 'Unique', 'history.json present', 'create_time range', 'update_time range'],
      [[r['benchmark'], lab(r['model']), r['history_links'], r['unique_histories'], r['history_json_present'], f"{(r['create_time_min'] or '')[:16]} to {(r['create_time_max'] or '')[:16]}",
        f"{(r['update_time_min'] or '')[:16]} to {(r['update_time_max'] or '')[:16]}"] for r in q5['galaxy_history_times_by_configuration']])
w('Evidence collection (retrospective audit):')
w('')
table(['Benchmark', 'Source retrieval (sources[].retrieval_time_utc)', 'Evidence audit timestamp'],
      [[r['benchmark'], f"{r['source_retrieval_min'][:16]} to {r['source_retrieval_max'][:16]} UTC", f"{r['evidence_audit_timestamp_min'][:16]} to {r['evidence_audit_timestamp_max'][:16]} UTC"] for r in q5['evidence_collection_by_benchmark']])
w(q5['note'] + ' CompBio aggregate registry files were retrieved 2026-09-22; the IWC scientific audit was generated 2026-09-23.')
w('')

# Q6
q6 = d['q6_tools']
w('## Q6. Tools offered')
w('')
w(f"Source: {q6['source']}.")
w('')
table(['Benchmark', 'Model', 'Arm', 'Galaxy server', 'Execute MCP enabled', 'Claude MCP config', 'API key mode', 'IWC key mounted', 'Recorded MCP list', 'UDT helper in list', 'Prompt names run_galaxy_udt_and_wait', 'Runs calling it'],
      [[r['benchmark'], lab(r['model']), COND[r['condition']], r['galaxy_server (evidence environment.galaxy_server)'] or '-', r['docker galaxy_execute_mcp_enabled'],
        r['mcp_config_mode (Claude Code)'] or '-', r['galaxy_api_key_mode'], r['iwc_galaxy_api_key_mounted'] if r['iwc_galaxy_api_key_mounted'] is not None else '-', 'yes (7 tools)' if r['recorded_galaxy_mcp_tool_list (IWC codex_invocation runtime.galaxy_mcp_tools)'] else 'not recorded',
        r['udt_helper_in_recorded_list'] if r['udt_helper_in_recorded_list'] is not None else 'n/a', r['prompt_names_run_galaxy_udt_and_wait'], r['runs_calling_run_galaxy_udt_and_wait']] for r in q6['rows']])
w(q6['note'] + ' `analysis.json` `galaxy_helpers_exposed` is non-null only for the 240 IWC runs (120 Galaxy lists with 7 tools; 120 empty code lists). Per-configuration counts of runs calling each interface are in the JSON (`q6_tools.rows[].runs_calling_each_interface`).')
w('')

# Q7
w('## Q7. CompBio campaign selection, and BixBench/IWC reruns')
w('')
w(f"Source: {q7['source']}.")
w('')
chk = q7['compbio_archive_vs_registry_item_check']
w(f"Archive-to-registry check over the 2,400 paired runs: {chk.get('archived campaign equals registry source campaign', 0):,} identical campaign names and {chk.get('equal after archive account redaction', 0)} identical after the archive's account redaction. {chk.get('different', 0)} differs: DeepSeek Galaxy r3 `finding-geo-q1`, where the vector uses an `operator_na` final-disposition campaign and the archived trace comes from `finding_geo_strict_retry2`.")
w('')
table(['Model', 'Arm', 'Rep', 'Vector (campaign_id)', 'Score type', 'Campaigns', 'Runs from largest', 'From other campaigns', 'Outcome-named', 'Consensus/top10', 'Other-replicate-labelled', 'Account labels (registry)'],
      [[lab(r['model']), COND[r['condition']], r['replicate'], r['campaign_id'], r['score_type'], r['n_source_campaigns'], r['runs_from_largest_campaign'], r['runs_from_other_campaigns'],
        r['runs_from_outcome_named_campaigns'], r['runs_from_consensus_or_top10_campaigns'], r['runs_from_campaigns_labelled_other_replicate'] if r['runs_from_campaigns_labelled_other_replicate'] is not None else 'n/a',
        r['runs_by_registry_account_label'] or '-'] for r in q7['compbio_vectors']])
table(['Arm', 'Runs from largest campaign', 'From other campaigns', 'Outcome-named', 'Consensus/top10'],
      [[COND[r['condition']], r['runs_from_largest_campaign'], r['runs_from_other_campaigns'], r['runs_from_outcome_named_campaigns'], r['runs_from_consensus_or_top10_campaigns']] for r in q7['compbio_totals_by_condition']])
w(q7['note'])
w('')
w('Galaxy-arm prompt and harness tokens in CompBio campaign names: older prompt (no `promptv2`) for 79 GPT-5.5 and 81 Sol Galaxy runs. The names also carry `_agents_` (21 GPT-5.5 r2, 24 Sol r2), `noagents`, or `waitagents` (8 GPT-5.5 r3, 1 DeepSeek r3, 44 Luna). These tokens presumably encode the Codex agents/subagent setting, which is not otherwise recorded for CompBio. Per-vector counts are in `q7_campaign_selection.compbio_vectors.rows[].runs_agents_noagents_waitagents`. Code campaign names carry no prompt-version tokens.')
w('')
w('BixBench50 iteration settings (evidence `iteration_setting`, `attempt.json` experiment):')
w('')
table(['Model', 'Arm', 'iteration_setting', 'experiment', 'Runs'],
      [[lab(r['model']), COND[r['condition']], r['ev_iteration_setting'], r['attempt_experiment'], r['n_runs']] for r in q7['bixbench_iteration_settings']])
w('IWC run roots (`codex_invocation.json` run_root); "primary" means a `*-formal` root or the DeepSeek Galaxy main root:')
w('')
table(['Model', 'Arm', 'Run root', 'Primary', 'Runs'],
      [[lab(r['model']), COND[r['condition']], r['iwc_run_root'].replace('iwc-bench-runs-20260827/', ''), r['primary_root'], r['n_runs']] for r in q7['iwc_run_roots']])

# Q8
q8 = d['q8_other_differences']
w('## Q8. Other differences between arms')
w('')
table(['Item', 'Galaxy arm', 'Open-ended-code arm', 'Counts', 'Source'], [[i['item'], i['galaxy'], i['open_ended_code'], i['counts'], i['source']] for i in q8['items']])
w('Local inputs staged (`inputs_manifest.json`; IWC mounts data read-only at /workspace/data instead and has no manifest):')
w('')
table(['Benchmark', 'Model', 'Arm', 'Runs', 'Manifest present', 'Runs with local inputs'],
      [[r['benchmark'], lab(r['model']), COND[r['condition']], r['n_runs'], r['inputs_manifest_present'], r['runs_with_local_inputs']] for r in q8['local_inputs']])
w('CompBio Galaxy history routing tag (`history_routing_tags.json`):')
w('')
table(['Model', 'Galaxy runs', "Tag 'training' applied", 'Tag-disabled record'], [[lab(r['model']), r['n_runs'], r['training_tag_applied'], r['training_tag_disabled_record']] for r in q8['compbio_routing']])
w('Network-related records:')
w('')
table(['Benchmark', 'Model', 'Arm', 'Runs', 'Hugging Face blocked', 'Conda network filter', 'IWC network', 'Prompt mentions internet'],
      [[r['benchmark'], lab(r['model']), COND[r['condition']], r['n_runs'], r['runs_blocking_huggingface'], r['conda_network_filter'], r['iwc_network_mode'] or '-', r['prompt_mentions_internet']] for r in q8['network']])

w('## Not recorded')
w('')
for u in d['unknowns_not_recorded']:
    w(f'- {u}')
w('')
w('## Files')
w('')
w('- `design_metadata.json`: all tables above, plus IWC per-run budgets (`q4_budgets.iwc_per_run.rows`), the 120 pair details (`q4_budgets.iwc_pair_matching.pairs_detail.rows`), per-campaign CompBio run counts, provenance.tsv summaries and the interface-call counts.')
w('- `per_run_design_metadata.csv`: 4,240 runs with the extracted fields, redacted as described.')
(OUT / 'design_metadata.md').write_text('\n'.join(L) + '\n')
print('md lines', len(L))
