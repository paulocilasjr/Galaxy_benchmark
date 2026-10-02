"""Read-only extraction of per-run design metadata from the Galaxy_benchmark archive.

Reads task evidence JSON and small per-run metadata files under
<benchmark>/analysis/<task>/source_snapshots/. Never opens ground_truth/,
never reads evaluation.json/result.json contents, and never contacts a server.
"""
import gzip, hashlib, json, re, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1])
FOLDERS = {'BixBench50': 'BixBench_50', 'CompBio': 'CompBio', 'IWC': 'IWC'}
WORD = re.compile(r'\b\w+\b')
TOOL_NAMES = ['stage_workspace_file', 'search_galaxy_tools', 'inspect_galaxy_history', 'inspect_archive_inventory',
              'inspect_galaxy_tool', 'run_galaxy_tool_and_wait', 'wait_for_galaxy_jobs', 'run_galaxy_udt_and_wait']

analysis = json.load(open(ROOT / 'BixBench50_CompBio_analysis/analysis.json'))
amap = {(r['benchmark'], r['task'], r['run_id']): r for r in analysis['runs']}
iwc_audit = {(r['task'], r['run_id']): r for r in json.load(open(ROOT / 'IWC/iwc_scientific_audit.json'))['runs']}


def jload(p):
    try:
        return json.loads(p.read_text())
    except Exception:
        return None


def find(base, rel):
    for cand in (base / rel, base / 'agent_workspace' / rel):
        if cand.exists():
            return cand
    return None


def text_stats(p):
    if p is None:
        return None, None, None
    b = p.read_bytes()
    t = b.decode('utf-8', 'replace')
    return hashlib.sha256(b).hexdigest(), len(WORD.findall(t)), t


def campaign_from_path(path):
    if not path:
        return None
    m = re.search(r'/runs/([^/]+)/', path)
    if m and m.group(1) != '.agent_runtime':
        return m.group(1)
    m = re.search(r'/local/([^/]+)/', path)  # BixBench experiment root
    if m:
        return m.group(1)
    m = re.search(r'iwc-bench-runs-[^/]+/[^/]+', path)
    return m.group(0) if m else None


rows = []
histories = []
for bench, folder in FOLDERS.items():
    for ev_path in sorted((ROOT / folder / 'analysis').glob('*/history_analysis_evidence.json')):
        tdir = ev_path.parent
        ev = json.load(open(ev_path))
        task = ev['task']['task_id']
        src_by_id = {s['source_id']: s for s in ev['sources']}
        audit_ts = ev['audit'].get('timestamp_utc')
        for r in ev['runs']:
            a = amap[(bench, task, r['run_id'])]
            snap = tdir / 'source_snapshots/huggingface_traces/files' / r['run_id']
            row = {
                'benchmark': bench, 'task': task, 'run_id': r['run_id'], 'condition': r['condition'],
                'model': a['model'], 'replicate': r['replicate_id'],
                'ev_prompt_variant': r.get('prompt_variant'), 'ev_prompt_sha256': r.get('prompt_sha256'),
                'ev_iteration_setting': r.get('iteration_setting'), 'ev_original_condition_label': r.get('original_condition_label'),
                'ev_status': r.get('status'),
                'mm_harness': a['model_metadata'].get('harness'), 'mm_verified_runtime_id': a['model_metadata'].get('verified_runtime_id'),
                'mm_reasoning': a['model_metadata'].get('reasoning_setting'), 'mm_verification_status': a['model_metadata'].get('verification_status'),
                'mm_supplied_label': a['model_metadata'].get('supplied_label'), 'mm_version': a['model_metadata'].get('version'),
                'mm_verification_source': a['model_metadata'].get('verification_source'),
                'an_prompt_sha256': a.get('prompt_sha256'), 'an_prompt_words': a.get('prompt_words'),
                'ev_ts_submission': r['timestamps'].get('submission'), 'ev_ts_history_create': r['timestamps'].get('history_create_time'),
                'ev_budget_time': r['budgets'].get('time'), 'ev_budget_tokens': r['budgets'].get('tokens'),
                'ev_budget_retry': r['budgets'].get('retry_policy'),
                'ev_env_galaxy_server': r['environment'].get('galaxy_server'), 'ev_env_docker_image': r['environment'].get('docker_image'),
                'ev_env_api_key_mode': r['environment'].get('galaxy_api_key_mode'),
                'ev_env_other_keys': ','.join(sorted(set(r['environment']) - {'galaxy_server', 'docker_image', 'galaxy_api_key_mode'})),
                'evidence_audit_timestamp': audit_ts,
                'udt_requested': a.get('udt_requested'), 'udt_request_count': a.get('udt_request_count'),
                'interface_calls': json.dumps(a.get('interface_calls') or {}, sort_keys=True),
                'snapshot_dir_exists': snap.exists(),
            }
            # sources
            trace_srcs = [src_by_id[s] for s in r['source_ids'] if s in src_by_id and 'huggingface' in (src_by_id[s].get('location') or '')]
            row['trace_url'] = trace_srcs[0]['location'] if trace_srcs else None
            m = re.search(r'galaxy-agent-benchmark-run-traces/tree/main/([^/]+)/([^/]+)/', row['trace_url'] or '')
            row['trace_collection'] = f'{m.group(1)}/{m.group(2)}' if m else None
            m = re.search(r'/(galaxy_strict_skills|anycode_nongalaxy_skills|[a-z_]+)/replicate_\d+', row['trace_url'] or '')
            row['trace_condition_folder'] = m.group(1) if m else None
            rts = [src_by_id[s].get('retrieval_time_utc') for s in r['source_ids'] if s in src_by_id and src_by_id[s].get('retrieval_time_utc')]
            row['source_retrieval_min'] = min(rts) if rts else None
            row['source_retrieval_max'] = max(rts) if rts else None
            gal_ids = [s.removeprefix('src_galaxy_') for s in r['source_ids'] if s.startswith('src_galaxy_')]
            row['galaxy_history_ids'] = ','.join(gal_ids)
            for hid in gal_ids:
                h = jload(tdir / 'source_snapshots/galaxy' / hid / 'history.json')
                s = src_by_id.get('src_galaxy_' + hid, {})
                histories.append({'benchmark': bench, 'task': task, 'run_id': r['run_id'], 'model': a['model'], 'condition': r['condition'],
                                  'history_id': hid, 'create_time': (h or {}).get('create_time'), 'update_time': (h or {}).get('update_time'),
                                  'history_json_present': h is not None, 'retrieval_time_utc': s.get('retrieval_time_utc'),
                                  'access_status': s.get('access_status'), 'location': s.get('location')})
            # galaxy job create times from evidence (includes inherited/copied jobs)
            jt = sorted(e['timestamp'] for e in r['events'] if e['execution_location'] == 'galaxy_job' and e.get('timestamp'))
            row['galaxy_job_create_min'] = jt[0] if jt else None
            row['galaxy_job_create_max'] = jt[-1] if jt else None

            # prompt files
            p = find(snap, 'prompt.txt')
            row['prompt_file_sha256'], row['prompt_file_words'], ptxt = text_stats(p)
            row['prompt_file_chars'] = len(ptxt) if ptxt else None
            if ptxt:
                low = ptxt.lower()
                row['prompt_mentions_galaxy'] = 'galaxy' in low
                row['prompt_tool_names'] = ','.join(t for t in TOOL_NAMES if t in ptxt)
                row['prompt_mentions_udt'] = ('udt' in low) or ('user-defined tool' in low) or ('user defined tool' in low)
            ep = find(snap, 'run_trace/effective_prompt.txt')
            row['effective_prompt_sha256'], row['effective_prompt_words'], _ = text_stats(ep)

            im = jload(find(snap, 'inputs_manifest.json') or Path('/nonexistent'))
            if isinstance(im, dict):
                ins = im.get('inputs') if isinstance(im.get('inputs'), list) else None
                row['local_input_count'] = len(ins) if ins is not None else None
                row['local_input_bytes'] = sum((x.get('size_bytes') or 0) for x in ins) if ins else (0 if ins is not None else None)
            elif isinstance(im, list):
                row['local_input_count'] = len(im)
            # invocation metadata
            di = jload(find(snap, 'run_trace/docker_invocation.json') or Path('/nonexistent'))
            if di:
                for k in ['image', 'image_id', 'galaxy_api_key_mode', 'galaxy_execute_mcp_enabled', 'galaxy_wait_mcp_enabled',
                          'model', 'reasoning_effort', 'service_tier', 'skill_exclude_regex', 'model_provider', 'model_provider_base_url',
                          'agent_runtime', 'mcp_config_mode', 'galaxy_strict', 'galaxy_url', 'science_first_mode', 'blocked_hosts',
                          'workspace_transport', 'extra_ca_bundle_mode', 'host_ca_bundle_mounted', 'plugins', 'remote_plugin', 'provider', 'effort',
                          'private_dir_mounted', 'source_jsonl_mounted', 'source_tsv_mounted']:
                    if k in di:
                        row['docker_' + k] = json.dumps(di[k]) if isinstance(di[k], (list, dict)) else di[k]
                row['docker_invocation_keys'] = ','.join(sorted(di))
                row['docker_campaign'] = campaign_from_path(di.get('workspace_mount'))
            ci = jload(find(snap, 'run_trace/conda_invocation.json') or Path('/nonexistent'))
            if ci:
                for k in ['execution_backend', 'timeout_seconds', 'network_filter_mode', 'model', 'reasoning_effort', 'service_tier',
                          'model_provider', 'model_provider_base_url', 'base_environment']:
                    if k in ci:
                        row['conda_' + k] = ci[k]
                row['conda_blocked_host_suffixes'] = json.dumps(ci.get('blocked_host_suffixes'))
                row['conda_codex_executable'] = re.sub(r'.*/(codex_cli_[^/]+|ChatGPT\.app)/.*', r'\1', ci.get('codex_executable') or '') or None
                row['conda_campaign'] = campaign_from_path(ci.get('skills_snapshot'))
            si = jload(find(snap, 'run_trace/skill_inventory.json') or Path('/nonexistent'))
            if si:
                row['skills_copied'] = ','.join(si.get('copied_skills') or si.get('skills') or [])
                row['skills_skipped'] = ','.join(si.get('skipped_skills') or [])
                row['skills_exclude_regex'] = si.get('exclude_regex')
            at = jload(snap / 'attempt.json')
            if at:
                for k in ['experiment', 'condition', 'attempt', 'agent_runtime', 'provider', 'canonical_preparation_source']:
                    row['attempt_' + k] = at.get(k)
            rr = jload(snap / 'run_record.json')
            if rr:
                row['rr_prepared_at_utc'] = rr.get('prepared_at_utc')
                row['rr_condition'] = rr.get('condition') or rr.get('run_condition')
                row['rr_campaign'] = campaign_from_path(rr.get('agent_workspace'))
                row['rr_status'] = rr.get('status')
                row['rr_model'] = rr.get('model')
                sh = rr.get('seed_history') or {}
                row['rr_seed_owner'] = sh.get('seed_owner_username')
            tj = jload(find(snap, 'task.json') or Path('/nonexistent'))
            if tj:
                row['task_timeout_minutes'] = tj.get('timeout_minutes')
                row['task_execution_backend'] = tj.get('execution_backend')
                row['task_created_at'] = tj.get('created_at')
                row['task_condition'] = tj.get('condition')
                md = tj.get('metadata') if isinstance(tj.get('metadata'), dict) else {}
                row['task_internet_required'] = md.get('internet_required')
                row['task_placed_input_count'] = len(tj['placed_inputs']) if isinstance(tj.get('placed_inputs'), list) else None
                sh = tj.get('seed_history') or {}
                row['task_seed_owner'] = sh.get('seed_history_owner')
            sd = jload(find(snap, 'seed_history.json') or Path('/nonexistent'))
            if sd:
                row['seed_owner'] = sd.get('seed_history_owner') or sd.get('seed_owner_username')
            comp = jload(snap / 'completion.json')
            if comp:
                row['completion_started_at'] = comp.get('started_at')
                row['completion_finished_at'] = comp.get('finished_at')
            us = jload(snap / 'usage.json')
            if isinstance(us, dict):
                row['usage_written_at_utc'] = us.get('written_at_utc')
            pc = jload(find(snap, 'run_trace/provider_config.json') or Path('/nonexistent'))
            if pc:
                row['provider_base_url'] = pc.get('base_url')
                row['provider_subagent_model'] = pc.get('subagent_model')
                row['provider_default_haiku_model'] = pc.get('default_haiku_model')
            ht = jload(find(snap, 'run_trace/history_routing_tags.json') or Path('/nonexistent'))
            if ht:
                row['routing_tags_after'] = ','.join(ht.get('tags_after') or [])
                row['routing_verified_at'] = ht.get('verified_at_utc')
            row['routing_tags_disabled_file'] = find(snap, 'run_trace/history_routing_tags_disabled.json') is not None
            ip = jload(find(snap, 'run_trace/identity_isolation_preflight.json') or Path('/nonexistent'))
            if ip:
                row['identity_preflight_status'] = ip.get('status')
            # IWC
            cx = jload(find(snap, 'run_trace/codex_invocation.json') or Path('/nonexistent'))
            if cx:
                row['iwc_started_at_utc'] = cx.get('started_at_utc')
                row['iwc_wall_clock_timeout_seconds'] = cx.get('wall_clock_timeout_seconds')
                row['iwc_skill_mode'] = cx.get('skill_mode')
                row['iwc_solution_mode'] = cx.get('solution_mode')
                row['iwc_auth_mode'] = cx.get('auth_mode')
                row['iwc_prompt_with_condition_sha256'] = cx.get('prompt_sha256')
                row['iwc_run_root'] = re.sub(r'^.*iwc-bench-runs-', 'iwc-bench-runs-', cx.get('run_root') or '')
                sb = cx.get('skills_bundle') or {}
                row['skills_bundle_revision'] = sb.get('revision')
                row['skills_bundle_sha256'] = sb.get('sha256')
                row['skills_copied'] = ','.join(s['name'] for s in sb.get('skills') or [])
                row['skills_skipped'] = ','.join(sb.get('excluded') or [])
                rt = cx.get('runtime') or {}
                row['iwc_galaxy_mcp_tools'] = ','.join(rt.get('galaxy_mcp_tools') or [])
                for k in ['model', 'model_reasoning_effort', 'service_tier', 'model_provider', 'fast_mode', 'agents_enabled',
                          'plugins_enabled', 'apps_enabled', 'hooks_enabled', 'solution_mode']:
                    row['iwc_runtime_' + k] = rt.get(k)
                row['iwc_system_skills'] = ','.join((cx.get('expected_runtime_system_skills') or {}).get('entries') or [])
                row['iwc_reference_cache_roots'] = json.dumps(cx.get('reference_cache_roots'))
            dz = jload(find(snap, 'run_trace/docker_isolation.json') or Path('/nonexistent'))
            if dz:
                row['iso_image_id'] = dz.get('image_id')
                row['iso_network_mode'] = (dz.get('network') or {}).get('mode')
                res = dz.get('resources') or {}
                row['iso_memory_bytes'] = res.get('memory_bytes')
                row['iso_nano_cpus'] = res.get('nano_cpus')
                row['iso_pids_limit'] = res.get('pids_limit')
                row['iso_env_has_galaxy_url'] = 'IWC_GALAXY_URL' in (dz.get('environment_variable_names') or [])
                row['iso_galaxy_key_mounted'] = any('galaxy_api_key' in (m.get('destination') or '') for m in dz.get('mounts') or [])
            dp = jload(find(snap, 'run_trace/docker_postrun.json') or Path('/nonexistent'))
            if dp:
                row['postrun_started_at'] = dp.get('started_at')
                row['postrun_finished_at'] = dp.get('finished_at')
                row['postrun_exit_code'] = dp.get('exit_code')
                row['postrun_oom_killed'] = dp.get('oom_killed')
            cond = jload(find(snap, 'run_trace/condition.json') or Path('/nonexistent'))
            if cond:
                row['iwc_condition_json'] = cond.get('solution_mode')
            if bench == 'IWC':
                au = iwc_audit[(task, r['run_id'])]
                row['iwc_audit_wall_timeout_seconds'] = au.get('wall_timeout_seconds')
                row['iwc_audit_started_at_utc'] = au.get('started_at_utc')
                row['iwc_audit_prompt_sha256'] = au.get('prompt_sha256')
                row['iwc_audit_harness_status'] = au.get('harness_status')
                row['iwc_audit_skills_revision'] = au.get('skills_revision')
                row['iwc_audit_model_label'] = au.get('model')
                row['iwc_audit_original_condition'] = au.get('original_condition')
            # list of metadata files present (excluding outputs)
            rows.append(row)

df = pd.DataFrame(rows)
hdf = pd.DataFrame(histories)
assert len(df) == 4240, len(df)
df.to_csv(OUT / 'per_run_design_metadata.csv', index=False)
hdf.to_csv(OUT / 'galaxy_history_snapshots.csv', index=False)
print(df.shape, hdf.shape)
