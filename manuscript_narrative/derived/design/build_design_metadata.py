"""Build design_metadata.json / design_metadata.md from the extracted per-run tables (read-only on the repo)."""
import json, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
WORK = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
USER_RE = re.compile(r'alexch')  # public Galaxy username in seed-history URLs / IWC run roots; redacted in outputs


ACCOUNT_TOKENS = {'jqsde': '[account-A]', 'jqwm': '[account-B]'}  # tokens the archive itself redacts as [REDACTED ACCOUNT]


def red(x):
    if not isinstance(x, str):
        return x
    x = USER_RE.sub('[galaxy-user]', x)
    for k, v in ACCOUNT_TOKENS.items():
        x = x.replace(k, v)
    return x


df = pd.read_csv(WORK / 'per_run_design_metadata.csv', low_memory=False)
ph = pd.read_csv(WORK / 'prompt_phrases.csv')
hist = pd.read_csv(WORK / 'galaxy_history_snapshots.csv')
df = df.merge(ph, on=['benchmark', 'task', 'run_id'], how='left')
assert len(df) == 4240
KEYS = ['benchmark', 'model', 'condition']
ORDER = {'BixBench50': 0, 'CompBio': 1, 'IWC': 2}


def nn(v):
    if v is None:
        return None
    if isinstance(v, float) and np.isnan(v):
        return None
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return red(v)


def records(frame):
    return [{k: nn(v) for k, v in r.items()} for r in frame.to_dict('records')]


def rng(s):
    s = s.dropna().astype(str)
    return (s.min(), s.max(), int(len(s))) if len(s) else (None, None, 0)


def sort_cfg(frame):
    return frame.assign(_o=frame.benchmark.map(ORDER)).sort_values(['_o', 'model', 'condition']).drop(columns='_o')


out = {
    'title': 'Design differences between the open_ended_code and galaxy arms (archived Galaxy_benchmark runs)',
    'generated_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    'scope': '4,240 archived runs: BixBench50 1,500; CompBio 2,500; IWC 240. Read-only extraction; ground_truth/, '
             'evaluation.json and result.json contents, .env and credentials were not read; no agent code run; no server contacted.',
    'conventions': {
        'run_key': 'benchmark + task + run_id (run_id is unique only within a task)',
        'condition': "'galaxy' or 'open_ended_code' as labelled in history_analysis_evidence.json runs[].condition",
        'model': 'model key as in BixBench50_CompBio_analysis/analysis.json runs[].model',
        'redaction': "The public Galaxy username that appears in BixBench seed-history records and one IWC run-root name is replaced by '[galaxy-user]'.",
        'not_recorded': "'not recorded' means no field carrying the value was found in the archive; it is never imputed.",
    },
    'source_files': {
        'analysis_json': 'BixBench50_CompBio_analysis/analysis.json (runs[]: model_metadata, prompt_sha256, prompt_words, galaxy_helpers_exposed, interface_calls)',
        'task_evidence': '<benchmark dir>/analysis/<task>/history_analysis_evidence.json (runs[]: prompt_variant, prompt_sha256, iteration_setting, original_condition_label, model, timestamps, budgets, environment, source_ids; sources[]: location, retrieval_time_utc; audit.timestamp_utc)',
        'run_snapshots': '<benchmark dir>/analysis/<task>/source_snapshots/huggingface_traces/files/<run_id>/ : prompt.txt, attempt.json, run_record.json, task.json, seed_history.json, usage.json, completion.json, inputs_manifest.json; run_trace/ or agent_workspace/run_trace/: docker_invocation.json, conda_invocation.json, skill_inventory.json, provider_config.json, effective_prompt.txt, history_routing_tags*.json, identity_isolation_preflight.json, codex_invocation.json, docker_isolation.json, docker_postrun.json, condition.json',
        'galaxy_history_snapshots': '<benchmark dir>/analysis/<task>/source_snapshots/galaxy/<history_id>/history.json (create_time, update_time)',
        'iwc_audit': 'IWC/iwc_scientific_audit.json runs[] (wall_timeout_seconds, started_at_utc, runtime, prompt_sha256, skills_revision)',
        'compbio_campaigns': 'CompBio/compBio_overview_audit.json score_vectors[].source_campaigns; CompBio/source_snapshots/aggregate_metadata/paper_site_runs.json models[].conditions[].replicates[].roots; CompBio/source_snapshots/aggregate_metadata/compbiobench/replicates.tsv and replicates/<campaign>/provenance.tsv (source_run_id column)',
        'docs': 'IWC/result_section_iwc.md Table 1; IWC/iwc_overview.md; CompBio/compBio_recovery_summary.md; Result_table.md',
    },
}

# ---------------------------------------------------------------- Q1 harness / container
q1 = df.assign(
    image=df.docker_image.fillna(df.ev_env_docker_image),
    image_id=df.docker_image_id.fillna(df.iso_image_id),
    execution_backend=df.task_execution_backend.fillna(df.conda_execution_backend)
        .fillna(pd.Series(np.where(df.iso_image_id.notna(), 'docker (docker_isolation.json)',
                                   np.where(df.docker_image.notna(), 'docker (docker_invocation.json)', None)), index=df.index)),
    agent_runtime=df.attempt_agent_runtime.fillna(df.docker_agent_runtime).fillna(df.conda_codex_executable),
).groupby(KEYS + ['mm_harness', 'image', 'image_id', 'execution_backend', 'agent_runtime'], dropna=False).size().reset_index(name='n_runs')
out['q1_harness_container'] = {
    'source': 'analysis.json runs[].model_metadata.harness (mm_harness); docker image from run_trace/docker_invocation.json image (fallback evidence runs[].environment.docker_image); image_id from docker_invocation.json image_id or IWC docker_isolation.json image_id; execution_backend from CompBio task.json execution_backend / conda_invocation.json execution_backend, or presence of a docker invocation/isolation record; agent_runtime from attempt.json agent_runtime / docker_invocation.json agent_runtime / conda_invocation.json codex_executable',
    'rows': records(sort_cfg(q1)),
    'note': 'Null image/image_id means no invocation record was archived for that run (CompBio open-ended GPT-5.5/Sol/Luna runs, 56 CompBio Galaxy GPT-5.5 runs and 30 CompBio Galaxy Sol runs). The IWC image is recorded only as a content digest (no tag).',
}

# ---------------------------------------------------------------- Q2 runtime model / reasoning
inv_model = df.docker_model.fillna(df.conda_model).fillna(df.iwc_runtime_model)
inv_reason = df.docker_reasoning_effort.fillna(df.docker_effort).fillna(df.conda_reasoning_effort).fillna(df.iwc_runtime_model_reasoning_effort)
inv_tier = df.docker_service_tier.fillna(df.conda_service_tier).fillna(df.iwc_runtime_service_tier)
inv_provider = df.docker_model_provider.fillna(df.docker_provider).fillna(df.conda_model_provider).fillna(df.iwc_runtime_model_provider)
q2 = df.assign(invocation_model=inv_model, invocation_reasoning=inv_reason, invocation_service_tier=inv_tier.replace('', '(empty)'),
               invocation_provider=inv_provider).groupby(
    KEYS + ['mm_supplied_label', 'mm_verified_runtime_id', 'mm_reasoning', 'mm_verification_status', 'invocation_model',
            'invocation_reasoning', 'invocation_service_tier', 'invocation_provider'], dropna=False).size().reset_index(name='n_runs')
ver = df.assign(has_invocation_model=inv_model.notna()).groupby(['benchmark', 'condition', 'mm_verification_status', 'has_invocation_model']).size().reset_index(name='n_runs')
out['q2_model_runtime'] = {
    'source': 'analysis.json runs[].model_metadata (supplied_label, verified_runtime_id, reasoning_setting, verification_status; IWC verified_runtime_id/reasoning are filled by analysis.json from IWC/iwc_scientific_audit.json runtime); invocation_* columns re-read from docker_invocation.json (model, reasoning_effort|effort, service_tier, model_provider|provider), conda_invocation.json, IWC codex_invocation.json runtime',
    'rows': records(sort_cfg(q2)),
    'verification_counts': records(ver.assign(_o=ver.benchmark.map(ORDER)).sort_values(['_o', 'condition']).drop(columns='_o')),
    'note': "IWC task evidence labels all 240 runs 'user_supplied_only', but each IWC run has codex_invocation.json runtime.model and model_reasoning_effort (the IWC README treats these as verification). "
            "GPT runs record no model-provider override (default provider). CompBio has no runtime model record for 900 open-ended GPT-5.5/Sol/Luna runs, 56 Galaxy GPT-5.5 runs and 30 Galaxy Sol runs. The campaign registry gives only descriptive settings ('high reasoning / fast processing' for GPT-5.5, Sol and Luna; Luna Galaxy campaign names contain 'luna_max_fast'). service_tier is 'fast' for GPT runs and empty for DeepSeek via Codex. The superseded BixBench DeepSeek harness ran Claude Code with deepseek_anthropic_compat and subagent/haiku model deepseek-v4-flash (provider_config.json).",
}

# ---------------------------------------------------------------- Q3 prompts
p_task_cond = df.groupby(['benchmark', 'task', 'condition']).prompt_file_sha256.nunique().reset_index(name='distinct')
q3a = p_task_cond.groupby(['benchmark', 'condition']).distinct.agg(['min', 'median', 'max']).reset_index()
_d = {k: {str(a): b for a, b in sorted(Counter(map(int, g.distinct)).items())} for k, g in p_task_cond.groupby(['benchmark', 'condition'])}
q3a['tasks_by_distinct_count'] = [_d[(b, c)] for b, c in zip(q3a.benchmark, q3a.condition)]
p_tcm = df.groupby(['benchmark', 'task', 'condition', 'model']).prompt_file_sha256.nunique().reset_index(name='distinct')
q3b = pd.DataFrame([{'benchmark': k[0], 'model': k[1], 'condition': k[2],
                     'tasks_by_distinct_hashes_within_model': {str(a): b for a, b in sorted(Counter(map(int, g.distinct)).items())}}
                    for k, g in p_tcm.groupby(KEYS)])
# galaxy vs code identical pairs
pv = df.pivot_table(index=['benchmark', 'task', 'model', 'replicate'], columns='condition', values='prompt_file_sha256', aggfunc='first').dropna()
pairs = pv.reset_index()
pairs['identical'] = pairs.galaxy == pairs.open_ended_code
q3c = pairs.groupby('benchmark').identical.agg(pairs_compared='size', identical_hash_pairs='sum').reset_index()
# share of hashes across conditions at task level
cross = []
for (b, t), g in df.groupby(['benchmark', 'task']):
    gs, cs = set(g[g.condition == 'galaxy'].prompt_file_sha256), set(g[g.condition == 'open_ended_code'].prompt_file_sha256)
    cross.append({'benchmark': b, 'task': t, 'shared': len(gs & cs)})
q3c = q3c.merge(pd.DataFrame(cross).groupby('benchmark').shared.apply(lambda s: int((s > 0).sum())).reset_index(name='tasks_with_any_hash_shared_across_conditions'))
# words
wq = lambda s: {'median': float(s.median()), 'q1': float(s.quantile(.25)), 'q3': float(s.quantile(.75)), 'min': int(s.min()), 'max': int(s.max())}
q3d = df.groupby(['benchmark', 'condition']).agg(n_runs=('run_id', 'size'),
                                               prompt_file_words_median=('prompt_file_words', 'median'),
                                               prompt_file_words_q1=('prompt_file_words', lambda s: s.quantile(.25)),
                                               prompt_file_words_q3=('prompt_file_words', lambda s: s.quantile(.75)),
                                               analysis_json_prompt_words_median=('an_prompt_words', 'median')).reset_index()
q3e = df.groupby(KEYS).agg(n_runs=('run_id', 'size'), prompt_file_words_median=('prompt_file_words', 'median'),
                           prompt_file_words_min=('prompt_file_words', 'min'), prompt_file_words_max=('prompt_file_words', 'max'),
                           analysis_json_prompt_words_median=('an_prompt_words', 'median')).reset_index()
# per-task galaxy minus code median words (same model)
tm = df.groupby(['benchmark', 'task', 'model', 'condition']).prompt_file_words.median().unstack('condition').dropna()
tm['diff'] = tm.galaxy - tm.open_ended_code
q3f = tm.reset_index().groupby('benchmark')['diff'].agg(['median', 'min', 'max', 'size']).reset_index().rename(columns={'size': 'task_model_cells'})
# model-sharing patterns
pat = Counter()
for (b, t, c), g in df.groupby(['benchmark', 'task', 'condition']):
    groups = []
    for h, gg in g.groupby('prompt_file_sha256'):
        groups.append(' + '.join(sorted(f"{m}[r{''.join(map(str, sorted(set(x.replicate))))}]" for m, x in gg.groupby('model'))))
    pat[(b, c, ' | '.join(sorted(groups)))] += 1
q3g = pd.DataFrame([{'benchmark': b, 'condition': c, 'hash_groups (models[replicates] sharing one prompt file per task)': p, 'n_tasks': n}
                    for (b, c, p), n in pat.items()])
q3g = q3g.assign(_o=q3g.benchmark.map(ORDER)).sort_values(['_o', 'condition', 'n_tasks'], ascending=[True, True, False]).drop(columns='_o')
flags = ['galaxy_not_required', 'no_local_inputs_staged', 'mentions_skills', 'udt_mentioned', 'start_timeout_300',
         'compbio_galaxy_promptv2_marker', 'compbio_galaxy_old_marker', 'no_wallclock_limit_instruction',
         'iwc_analysis_steps_jsonl', 'iwc_concise_log', 'mentions_internet']
q3h = df.groupby(KEYS)[flags].sum().astype(int).reset_index()
q3h['n_runs'] = df.groupby(KEYS).size().values
q3h['stated_minutes_in_prompt'] = [{('none' if np.isnan(k) else str(int(k))): int(v) for k, v in g.stated_minutes.value_counts(dropna=False).items()}
                                   for _, g in df.groupby(KEYS)]
out['q3_prompts'] = {
    'source': 'prompt.txt in each run snapshot (sha256 recomputed from bytes; equals evidence runs[].prompt_sha256 and analysis.json prompt_sha256 for 4,240/4,240 runs); word counts use the generator regex \\b\\w+\\b; analysis.json prompt_words counts the task-level question for BixBench/CompBio (evidence task.prompt) and the archived prompt.txt for IWC',
    'distinct_hashes_per_task_and_condition': records(q3a),
    'distinct_hashes_per_task_condition_model': records(sort_cfg(q3b)),
    'galaxy_vs_code_prompt_identity': records(q3c),
    'word_counts_by_condition': records(q3d),
    'word_counts_by_configuration': records(sort_cfg(q3e)),
    'galaxy_minus_code_words_per_task_model_cell': records(q3f),
    'model_sharing_patterns': records(q3g),
    'prompt_content_flags': {'rows': records(sort_cfg(q3h)),
                             'definitions': {
                                 'galaxy_not_required': "contains 'Galaxy is not required'",
                                 'no_local_inputs_staged': "contains 'No local input files were staged'",
                                 'mentions_skills': "contains 'skill' (case-insensitive)",
                                 'udt_mentioned': "contains the word UDT(s) or 'user-defined tool'",
                                 'start_timeout_300': "contains 'start_timeout_seconds=300'",
                                 'compbio_galaxy_promptv2_marker': "contains 'Your objective is to solve the scientific problem correctly'",
                                 'compbio_galaxy_old_marker': "contains 'Galaxy is the execution environment for this task, not the scientific method'",
                                 'no_wallclock_limit_instruction': "contains 'do not set a wall-clock time limit'",
                                 'iwc_analysis_steps_jsonl': "requires run_trace/analysis_steps.jsonl execution-trace records",
                                 'iwc_concise_log': "contains 'concise execution log'",
                                 'mentions_internet': "contains 'internet'",
                                 'stated_minutes_in_prompt': "value N from 'You have N minutes'"}},
}

# ---------------------------------------------------------------- Q4 budgets
iwc = df[df.benchmark == 'IWC'].copy()
assert (iwc.iwc_wall_clock_timeout_seconds == iwc.iwc_audit_wall_timeout_seconds).all()
iwc['budget_h'] = iwc.iwc_wall_clock_timeout_seconds / 3600
iwc_runs = iwc[['task', 'model', 'condition', 'replicate', 'run_id', 'iwc_wall_clock_timeout_seconds', 'budget_h', 'iwc_started_at_utc',
                'iwc_run_root', 'iwc_analysis_steps_jsonl']].sort_values(['task', 'model', 'condition', 'replicate'])
iwc_runs = iwc_runs.rename(columns={'iwc_wall_clock_timeout_seconds': 'wall_clock_timeout_seconds', 'iwc_started_at_utc': 'started_at_utc',
                                    'iwc_run_root': 'run_root', 'iwc_analysis_steps_jsonl': 'prompt_requires_analysis_steps_jsonl'})
pp = iwc.pivot_table(index=['task', 'model', 'replicate'], columns='condition', values='budget_h', aggfunc='first').reset_index()
pp['matched'] = pp.galaxy == pp.open_ended_code
pp['combination'] = pp.galaxy.astype(int).astype(str) + 'h Galaxy / ' + pp.open_ended_code.astype(int).astype(str) + 'h code'
assert len(pp) == 120
iwc_by_cfg = iwc.groupby(['model', 'condition', 'budget_h']).size().unstack('budget_h', fill_value=0).reset_index()
iwc_by_cfg.columns = ['model', 'condition', 'runs_6h', 'runs_12h']
pair_by_model = pp.groupby('model').agg(pairs=('matched', 'size'), matched=('matched', 'sum')).reset_index()
pair_by_model = pair_by_model.merge(pp.groupby(['model', 'combination']).size().unstack(fill_value=0).reset_index())
pair_by_task = pp.groupby('task').agg(pairs=('matched', 'size'), matched=('matched', 'sum')).reset_index()
start_split = iwc.groupby('budget_h').iwc_started_at_utc.agg(['min', 'max', 'size']).reset_index()
steps_x_budget = iwc[iwc.condition == 'open_ended_code'].groupby(['iwc_analysis_steps_jsonl', 'budget_h']).size().reset_index(name='n_runs')
cb = df[df.benchmark == 'CompBio']
cb_budget = cb.groupby(['model', 'condition', 'task_timeout_minutes', 'conda_timeout_seconds', 'stated_minutes'], dropna=False).size().reset_index(name='n_runs')
out['q4_budgets'] = {
    'source': 'IWC: agent_workspace/run_trace/codex_invocation.json wall_clock_timeout_seconds (identical to IWC/iwc_scientific_audit.json runs[].wall_timeout_seconds for 240/240); CompBio: evidence runs[].budgets.time (timeout_minutes/timeout_seconds) <- task.json timeout_minutes, conda_invocation.json timeout_seconds, and prompt text \'You have N minutes\'; BixBench50: evidence runs[].budgets {time,tokens,retry_policy} all null and no run-level timeout field found in docker_invocation.json, attempt.json, run_record.json or runner.log',
    'summary': [
        {'benchmark': 'BixBench50', 'condition': 'both', 'run_time_budget': 'not recorded (1,500/1,500 evidence budgets null)',
         'note': 'Galaxy prompts instruct a per-job blocking-call timeout (normally 5400 s); this is a Galaxy job wait, not a run budget. Open-ended prompts say only "within the active runtime limits".'},
        {'benchmark': 'CompBio', 'condition': 'open_ended_code',
         'run_time_budget': '120 min for 1,294/1,300 runs; 240 min for 3; 480 min for 3 (prompt "You have N minutes" = task.json timeout_minutes for all 1,300; conda_invocation timeout_seconds 7,200/14,400/28,800 also recorded for the 400 DeepSeek and Astra runs)',
         'note': 'The longer budgets belong to single-item recovery campaigns (campaign names contain encode_retry_240m, timeout240, t480, recovery480, timeout480).'},
        {'benchmark': 'CompBio', 'condition': 'galaxy', 'run_time_budget': 'not recorded (task.json timeout_minutes null for 1,200/1,200; prompts state no minutes)',
         'note': '81 Sol and 79 GPT-5.5 Galaxy prompts (older prompt version) say "do not set a wall-clock time limit" on blocking Galaxy calls.'},
        {'benchmark': 'IWC', 'condition': 'both', 'run_time_budget': '21,600 s (6 h) or 43,200 s (12 h) per run',
         'note': 'All runs started up to 2026-08-28T13:44:15Z had 6 h; all runs started from 2026-08-28T13:49:53Z had 12 h. Token and retry budgets: not recorded.'},
    ],
    'compbio_budget_rows': records(cb_budget),
    'iwc_by_configuration': records(iwc_by_cfg),
    'iwc_budget_by_start_time': records(start_split),
    'iwc_open_ended_prompt_variant_by_budget': records(steps_x_budget),
    'iwc_pair_matching': {
        'definition': 'pair = same IWC task, model configuration and replicate label (1-3) in galaxy and open_ended_code; replicate labels are not matched seeds',
        'pairs': int(len(pp)), 'matched_budget_pairs': int(pp.matched.sum()), 'mismatched_budget_pairs': int((~pp.matched).sum()),
        'by_combination': {k: int(v) for k, v in pp.combination.value_counts().items()},
        'by_model': records(pair_by_model), 'by_task': records(pair_by_task),
        'pairs_detail': records(pp.rename(columns={'galaxy': 'galaxy_budget_h', 'open_ended_code': 'code_budget_h'})),
    },
    'iwc_per_run': records(iwc_runs),
}

# ---------------------------------------------------------------- Q5 dates
def camp_ts(name):
    if not isinstance(name, str):
        return None
    m = re.search(r'(\d{8})T(\d{4})(\d{2})?(Z|ET)', name)
    if not m:
        return None
    t = datetime.strptime(m.group(1) + m.group(2), '%Y%m%d%H%M')
    if m.group(4) == 'ET':
        t = t + pd.Timedelta(hours=4)  # US Eastern daylight time (UTC-4) in Jul-Sep 2026
    return t.strftime('%Y-%m-%dT%H:%MZ')


df['campaign_name_time'] = df.rr_campaign.apply(camp_ts)
date_rows = []
for (b, m, c), g in df.groupby(KEYS):
    row = {'benchmark': b, 'model': m, 'condition': c, 'n_runs': len(g)}
    for col, label in [('rr_prepared_at_utc', 'run_record_prepared_at_utc'), ('task_created_at', 'compbio_task_json_created_at'),
                       ('campaign_name_time', 'compbio_campaign_name_timestamp'),
                       ('completion_started_at', 'completion_json_started_at'), ('completion_finished_at', 'completion_json_finished_at'),
                       ('usage_written_at_utc', 'usage_json_written_at_utc'), ('iwc_started_at_utc', 'iwc_codex_invocation_started_at_utc'),
                       ('postrun_started_at', 'iwc_docker_postrun_started_at'), ('postrun_finished_at', 'iwc_docker_postrun_finished_at'),
                       ('ev_ts_history_create', 'evidence_history_create_time')]:
        lo, hi, n = rng(g[col])
        row[label] = None if n == 0 else {'min': lo[:19], 'max': hi[:19], 'n': n}
    date_rows.append(row)
hrows = []
for (b, m, c), g in hist.groupby(KEYS):
    hrows.append({'benchmark': b, 'model': m, 'condition': c, 'history_links': len(g), 'unique_histories': g.history_id.nunique(),
                  'history_json_present': int(g.history_json_present.sum()),
                  'create_time_min': nn(g.create_time.min()), 'create_time_max': nn(g.create_time.max()),
                  'update_time_min': nn(g.update_time.min()), 'update_time_max': nn(g.update_time.max())})
hb = hist.groupby('benchmark').agg(unique_histories=('history_id', 'nunique'), create_time_min=('create_time', 'min'), create_time_max=('create_time', 'max'),
                                   update_time_min=('update_time', 'min'), update_time_max=('update_time', 'max')).reset_index()
coll = df.groupby('benchmark').agg(source_retrieval_min=('source_retrieval_min', 'min'), source_retrieval_max=('source_retrieval_max', 'max'),
                                   evidence_audit_timestamp_min=('evidence_audit_timestamp', 'min'), evidence_audit_timestamp_max=('evidence_audit_timestamp', 'max')).reset_index()
shared = hist[hist.duplicated('history_id', keep=False)].sort_values('history_id')[['benchmark', 'task', 'run_id', 'history_id']]
out['q5_dates'] = {
    'source': 'run_record.json prepared_at_utc (workspace preparation, not execution start); CompBio task.json created_at and campaign-directory timestamp in run_record.json agent_workspace path; completion.json started_at/finished_at (BixBench DeepSeek runs); usage.json written_at_utc (end-of-run usage write); IWC codex_invocation.json started_at_utc and docker_postrun.json started_at/finished_at; evidence runs[].timestamps.history_create_time; Galaxy history.json create_time/update_time; evidence sources[].retrieval_time_utc and audit.timestamp_utc for collection dates',
    'run_dates_by_configuration': [{k: nn(v) if not isinstance(v, dict) else v for k, v in r.items()} for r in
                                   sorted(date_rows, key=lambda r: (ORDER[r['benchmark']], r['model'], r['condition']))],
    'galaxy_history_times_by_configuration': sorted(hrows, key=lambda r: (ORDER[r['benchmark']], r['model'])),
    'galaxy_history_times_by_benchmark': records(hb),
    'evidence_collection_by_benchmark': records(coll),
    'histories_linked_to_more_than_one_run': records(shared),
    'note': 'Galaxy update_time reflects the last server-side change (for example publication or later tagging), not run end. Galaxy job create_time values in evidence include jobs inherited from copied seed histories and are not used as run dates. Open-ended BixBench GPT-5.6 and DeepSeek-via-Codex runs, and all CompBio open-ended runs, have no recorded execution start; only preparation/creation or usage-write times.',
}

# ---------------------------------------------------------------- Q6 tools
tool_rows = []
for (b, m, c), g in df.groupby(KEYS):
    runs = Counter()
    for x in g.interface_calls:
        for k in json.loads(x):
            runs[k] += 1
    tool_rows.append({'benchmark': b, 'model': m, 'condition': c, 'n_runs': len(g),
                      'galaxy_server (evidence environment.galaxy_server)': ', '.join(sorted(set(g.ev_env_galaxy_server.dropna()))) or None,
                      'docker galaxy_execute_mcp_enabled': {str(k): int(v) for k, v in g.docker_galaxy_execute_mcp_enabled.fillna('not recorded').value_counts().items()},
                      'docker galaxy_wait_mcp_enabled': {str(k): int(v) for k, v in g.docker_galaxy_wait_mcp_enabled.fillna('not recorded').value_counts().items()},
                      'mcp_config_mode (Claude Code)': {str(k): int(v) for k, v in g.docker_mcp_config_mode.dropna().value_counts().items()} or None,
                      'galaxy_api_key_mode': {str(k): int(v) for k, v in g.docker_galaxy_api_key_mode.fillna(g.ev_env_api_key_mode).fillna('not recorded').value_counts().items()},
                      'iwc_galaxy_api_key_mounted': int(g.iso_galaxy_key_mounted.fillna(False).astype(bool).sum()) if g.iso_galaxy_key_mounted.notna().any() else None,
                      'recorded_galaxy_mcp_tool_list (IWC codex_invocation runtime.galaxy_mcp_tools)': sorted(set(g.iwc_galaxy_mcp_tools.dropna())),
                      'udt_helper_in_recorded_list': None if g.iwc_galaxy_mcp_tools.isna().all() else int(g.iwc_galaxy_mcp_tools.fillna('').str.contains('run_galaxy_udt_and_wait').sum()),
                      'prompt_mentions_UDT': int(g.udt_mentioned.sum()),
                      'prompt_names_run_galaxy_udt_and_wait': int(g.prompt_tool_names.fillna('').str.contains('run_galaxy_udt_and_wait').sum()),
                      'runs_calling_run_galaxy_udt_and_wait': runs.get('run_galaxy_udt_and_wait', 0),
                      'runs_calling_each_interface': dict(sorted(runs.items(), key=lambda kv: (-kv[1], kv[0])))})
out['q6_tools'] = {
    'source': 'analysis.json runs[].galaxy_helpers_exposed (non-null only for IWC; copied from IWC codex_invocation.json runtime.galaxy_mcp_tools); docker_invocation.json galaxy_execute_mcp_enabled / galaxy_wait_mcp_enabled / galaxy_api_key_mode / mcp_config_mode; prompt.txt tool names; analysis.json runs[].interface_calls (tools actually called, from traces); evidence runs[].environment.galaxy_server',
    'rows': sorted(tool_rows, key=lambda r: (ORDER[r['benchmark']], r['model'], r['condition'])),
    'note': 'A recorded list of exposed Galaxy MCP tools exists only for IWC (7 tools: stage_workspace_file, search_galaxy_tools, inspect_galaxy_history, inspect_archive_inventory, inspect_galaxy_tool, run_galaxy_tool_and_wait, wait_for_galaxy_jobs); it omits run_galaxy_udt_and_wait and no IWC run called it. BixBench and CompBio exposure lists are not recorded; Galaxy-arm prompts name run_galaxy_udt_and_wait (BixBench) or permit UDTs (CompBio), and Galaxy-arm traces call it. CompBio Galaxy traces also call peek_galaxy_dataset, which is absent from the IWC list. Galaxy server in every Galaxy-arm run with a recorded server: https://usegalaxy.org (IWC containers also receive IWC_GALAXY_URL, value not recorded).',
}

# ---------------------------------------------------------------- Q7 CompBio campaign selection
audit = json.load(open(ROOT / 'CompBio/compBio_overview_audit.json'))
OUTCOME = re.compile(r'wrong|target\d+|near\d+')
SELECTIVE = re.compile(r'consensus|top10')
cbr = cb.copy()
cbr['campaign'] = cbr.rr_campaign
vec_rows, item_check, mismatches = [], Counter(), []
camp_runs = []
for s in audit['score_vectors']:
    model, cond, rep = s['model'], s['condition'], int(s['replicate'][1:])
    g = cbr[(cbr.model == model) & (cbr.condition == cond) & (cbr.replicate == rep)]
    src = {}
    for sc in s.get('source_campaigns') or []:
        for it in sc['items']:
            src[it] = sc['path'].removeprefix('runs/')
    acct = Counter()
    for r in g.itertuples():
        if src:
            reg = src.get(r.task)
            pat = '^' + re.escape(r.campaign).replace(re.escape('[REDACTED ACCOUNT]'), '([A-Za-z0-9]+)') + '$'
            if reg == r.campaign:
                item_check['archived campaign equals registry source campaign'] += 1
            elif reg and re.match(pat, reg):
                item_check['equal after archive account redaction'] += 1
            else:
                item_check['different'] += 1
                mismatches.append({'vector': s.get('campaign_id'), 'task': r.task, 'archived_campaign': red(r.campaign), 'registry_campaign': red(reg)})
            for k, v in ACCOUNT_TOKENS.items():
                if reg and k in reg:
                    acct[v] += 1
    cnt = Counter(g.campaign)
    largest, nlargest = cnt.most_common(1)[0]
    rep_tok = g.campaign.str.extract(r'_r(\d)(?:_|$)')[0]
    cross = int(((rep_tok.notna()) & (rep_tok.astype(float) != rep)).sum()) if not (model == 'codex_gpt_5_5' and cond == 'open_ended_code') else None
    vec_rows.append({'model': model, 'condition': cond, 'replicate': rep, 'campaign_id': s.get('campaign_id', 'codex_gpt_6_astra'),
                     'score_type': s.get('score_type'), 'vector_hash_matches': s.get('hash_matches'),
                     'n_source_campaigns': len(cnt), 'largest_campaign': red(largest), 'runs_from_largest_campaign': nlargest,
                     'runs_from_other_campaigns': len(g) - nlargest,
                     'runs_from_outcome_named_campaigns': int(g.campaign.str.contains(OUTCOME).sum()),
                     'runs_from_consensus_or_top10_campaigns': int(g.campaign.str.contains(SELECTIVE).sum()),
                     'runs_by_registry_account_label': dict(acct) or None,
                     'runs_from_campaigns_labelled_other_replicate': cross,
                     'runs_with_promptv2_in_campaign_name': int(g.campaign.str.contains('promptv2').sum()) if cond == 'galaxy' else None,
                     'runs_agents_noagents_waitagents': {k: int(g.campaign.str.contains(p).sum()) for k, p in
                                                         [('agents', r'_agents_'), ('noagents', r'noagents'), ('waitagents', r'waitagents')]} if cond == 'galaxy' else None})
    for name, n in cnt.items():
        camp_runs.append({'model': model, 'condition': cond, 'replicate': rep, 'campaign': red(name), 'n_runs': n,
                          'campaign_name_time': camp_ts(name), 'outcome_named': bool(OUTCOME.search(name)),
                          'consensus_or_top10': bool(SELECTIVE.search(name))})
astra = cbr[cbr.model == 'codex_gpt_6_astra']
for name, n in Counter(astra.campaign).items():
    camp_runs.append({'model': 'codex_gpt_6_astra', 'condition': 'open_ended_code', 'replicate': 1, 'campaign': name, 'n_runs': n,
                      'campaign_name_time': camp_ts(name), 'outcome_named': bool(OUTCOME.search(name))})
vr = pd.DataFrame(vec_rows)
tot = vr.groupby('condition')[['runs_from_largest_campaign', 'runs_from_other_campaigns', 'runs_from_outcome_named_campaigns',
                                'runs_from_consensus_or_top10_campaigns']].sum().reset_index()
prov = []
for d in sorted((ROOT / 'CompBio/source_snapshots/aggregate_metadata/compbiobench/replicates').iterdir()):
    p = d / 'provenance.tsv'
    if p.exists():
        t = pd.read_csv(p, sep='\t', usecols=['question_id', 'source_run_id', 'source_type'])
        c = t.source_run_id.value_counts()
        prov.append({'campaign_id': d.name, 'items': len(t), 'distinct_source_run_ids': int(len(c)),
                     'largest_source_run_id': red(c.index[0]), 'items_from_largest': int(c.iloc[0]),
                     'source_run_id_counts': {red(k): int(v) for k, v in c.items()},
                     'source_type_counts': {k: int(v) for k, v in t.source_type.value_counts().items()}})
bix_iter = df[df.benchmark == 'BixBench50'].groupby(['model', 'condition', 'ev_iteration_setting', 'attempt_experiment'], dropna=False).size().reset_index(name='n_runs')
iwc_roots = iwc.groupby(['model', 'condition', 'iwc_run_root']).size().reset_index(name='n_runs')
iwc_roots['primary_root'] = iwc_roots.iwc_run_root.str.endswith('-formal') | (iwc_roots.iwc_run_root.str.contains('deepseek-galaxy-') & ~iwc_roots.iwc_run_root.str.contains('rerun'))
out['q7_campaign_selection'] = {
    'source': 'Per-run campaign = runs/<campaign>/ directory in run_record.json agent_workspace (CompBio); cross-checked against CompBio/compBio_overview_audit.json score_vectors[].source_campaigns (from paper_site_runs.json roots) and replicates/<campaign>/provenance.tsv source_run_id; BixBench: evidence runs[].iteration_setting and attempt.json experiment/attempt; IWC: codex_invocation.json run_root',
    'compbio_archive_vs_registry_item_check': dict(item_check),
    'compbio_archive_vs_registry_differences': mismatches,
    'compbio_vectors': records(vr),
    'compbio_totals_by_condition': records(tot),
    'compbio_campaign_run_counts': camp_runs,
    'compbio_provenance_tsv_summary': prov,
    'outcome_named_token_regex': OUTCOME.pattern,
    'consensus_or_top10_token_regex': SELECTIVE.pattern,
    'bixbench_iteration_settings': records(bix_iter),
    'iwc_run_roots': records(iwc_roots),
    'note': "CompBio final vectors are composites. 'Largest campaign' is the campaign contributing most items to a vector; other campaigns include recoveries, continuations, completions, retries, repeats and fresh-history reruns. Campaign names containing 'wrong', 'wrongset', 'fastwrong', 'target84' or 'near84' (outcome_named) suggest item selection informed by earlier answers or scores; names containing 'consensus' or 'top10' indicate other selective reruns whose criterion is not stated. The selection rules are not recorded in the archive. Registry campaign names carry two account-like tokens that the archive redacts as [REDACTED ACCOUNT]; they are shown here as [account-A]/[account-B]. Cross-replicate counts compare the _rN token in the campaign name with the archived replicate label and are not computed for open-ended GPT-5.5, whose registry labels are offset (gpt55-anycode-jul30 = R1, gpt55-anycode-r1 = R2, gpt55-anycode-r2 = R3).",
}

# ---------------------------------------------------------------- Q8 other differences
skills = df.groupby(KEYS + ['skills_copied', 'skills_skipped', 'skills_exclude_regex', 'skills_bundle_revision'], dropna=False).size().reset_index(name='n_runs')
local_inputs = df.groupby(KEYS).agg(n_runs=('run_id', 'size'), inputs_manifest_present=('local_input_count', lambda s: int(s.notna().sum())),
                                    runs_with_local_inputs=('local_input_count', lambda s: int((s > 0).sum()))).reset_index()
net = df.assign(blocked_hf=df.docker_blocked_hosts.fillna('').str.contains('huggingface') | df.conda_blocked_host_suffixes.fillna('').str.contains('huggingface')) \
    .groupby(KEYS).agg(n_runs=('run_id', 'size'), runs_blocking_huggingface=('blocked_hf', 'sum'),
                       conda_network_filter=('conda_network_filter_mode', lambda s: int(s.notna().sum())),
                       iwc_network_mode=('iso_network_mode', lambda s: ','.join(sorted(set(s.dropna())))),
                       prompt_mentions_internet=('mentions_internet', 'sum')).reset_index()
iso = iwc.groupby(['condition']).agg(n=('run_id', 'size'), memory_bytes=('iso_memory_bytes', lambda s: sorted(set(s.dropna().astype(int)))),
                                     nano_cpus=('iso_nano_cpus', lambda s: sorted(set(s.dropna().astype(int)))),
                                     galaxy_key_mounted=('iso_galaxy_key_mounted', 'sum'), galaxy_url_env=('iso_env_has_galaxy_url', 'sum'),
                                     solution_mode=('iwc_solution_mode', lambda s: sorted(set(s.dropna()))),
                                     skills_revision=('skills_bundle_revision', lambda s: sorted(set(s.dropna())))).reset_index()
routing = df[(df.benchmark == 'CompBio') & (df.condition == 'galaxy')].groupby('model').agg(
    n_runs=('run_id', 'size'), training_tag_applied=('routing_tags_after', lambda s: int((s == 'training').sum())),
    training_tag_disabled_record=('routing_tags_disabled_file', 'sum')).reset_index()
other = [
    {'item': 'Execution substrate (CompBio)', 'galaxy': 'Docker image galaxy-eval-agent:latest (image_id sha256:57082a89...; docker_cp workspace transport)',
     'open_ended_code': 'host_conda_clone (macOS host conda env compbio-benchmark; no container)', 'counts': '1,200 Galaxy runs docker per task.json; 1,300 open-ended runs host_conda_clone', 'source': 'task.json execution_backend; docker_invocation.json; conda_invocation.json'},
    {'item': 'Execution substrate (IWC)', 'galaxy': 'Docker, same image digest as open-ended; 8 GiB memory, 4 CPUs, pids 512, bridge network; Galaxy key mounted at /run/secrets; IWC_GALAXY_URL set',
     'open_ended_code': 'Docker, same digest and resource limits; no Galaxy key or Galaxy URL', 'counts': '120 / 120', 'source': 'run_trace/docker_isolation.json'},
    {'item': 'Execution substrate (BixBench50)', 'galaxy': 'Docker images per harness (table Q1)', 'open_ended_code': 'Same image family; GPT-5.5 open-ended mostly no-static-udt-resolver-20260714 vs Galaxy mostly full-blocking-20260715', 'counts': 'see Q1', 'source': 'docker_invocation.json image'},
    {'item': 'Skills bundled', 'galaxy': 'BixBench: 8 skills incl. galaxy-tool-submission, galaxy-udt-authoring; CompBio: only galaxy-tool-submission, galaxy-udt-authoring (where inventory recorded); IWC: 5 domain skills, rev 03e9f1b9, result_verification excluded',
     'open_ended_code': "BixBench: same 6 domain skills, '^galaxy-' excluded; CompBio: no skill inventory recorded (prompts of 1,200/1,300 runs allow installed skill instructions; GPT-5.5 replicate-1 campaign named no_project_skills); IWC: identical 5 skills", 'counts': 'table q8.skills', 'source': 'skill_inventory.json; IWC codex_invocation.json skills_bundle'},
    {'item': 'Local input files (BixBench50 DeepSeek)', 'galaxy': 'No local input files staged for both DeepSeek harnesses (inputs only in Galaxy seed history); GPT Galaxy runs had local inputs',
     'open_ended_code': 'Local inputs staged for all runs', 'counts': '300/300 DeepSeek Galaxy runs with empty inputs_manifest and prompt "No local input files were staged"', 'source': 'inputs_manifest.json; prompt.txt'},
    {'item': 'Galaxy credentials in open-ended arm', 'galaxy': 'API key as read-only secret file / container temp secret', 'open_ended_code': "BixBench DeepSeek-via-Codex open-ended runs record galaxy_api_key_mode 'read_only_secret_file' (MCP disabled); other open-ended runs 'not_set' or no record",
     'counts': '150 BixBench DeepSeek-via-Codex open-ended runs', 'source': 'docker_invocation.json galaxy_api_key_mode'},
    {'item': 'Network', 'galaxy': 'Unrestricted in BixBench/IWC records; CompBio Galaxy containers list blocked Hugging Face hosts in 291/1,200 runs',
     'open_ended_code': 'BixBench prompts explicitly allow internet access; CompBio DeepSeek/Astra conda runs record an HTTP CONNECT proxy filter blocking Hugging Face in 102 runs; IWC bridge network', 'counts': 'table q8.network', 'source': 'docker_invocation.json blocked_hosts; conda_invocation.json blocked_host_suffixes/network_filter_mode; prompt.txt'},
    {'item': 'Prompt-required logging (IWC)', 'galaxy': "All 120 prompts: 'Keep a concise execution log in run_trace/'", 'open_ended_code': '55 prompts require structured run_trace/analysis_steps.jsonl records (exactly the 55 runs with 12 h budgets); 65 have the concise-log line', 'counts': '55 / 65', 'source': 'prompt.txt'},
    {'item': 'Galaxy history routing tag (CompBio)', 'galaxy': "history_routing_tags.json applied tag 'training' to some Galaxy histories (verified 2026-08-21..25); purpose not documented", 'open_ended_code': 'n/a', 'counts': 'table q8.routing', 'source': 'run_trace/history_routing_tags.json, history_routing_tags_disabled.json'},
    {'item': 'Extra MCP connectors (CompBio Galaxy)', 'galaxy': '3 GPT-5.5 and 2 Luna CompBio Galaxy runs called github.* or hugging_face.* MCP tools (connectors present in those runtimes)', 'open_ended_code': 'No such calls in any benchmark', 'counts': '5 runs', 'source': 'analysis.json interface_calls'},
    {'item': 'Internet in prompt text (BixBench50)', 'galaxy': 'Galaxy prompts do not mention internet access', 'open_ended_code': 'All 750 code prompts state that internet access may be used', 'counts': '0 / 750', 'source': 'prompt.txt'},
    {'item': 'Agent harness for superseded DeepSeek (BixBench)', 'galaxy': "Claude Code, provider deepseek_anthropic_compat, mcp_config_mode 'strict'", 'open_ended_code': "Claude Code, mcp_config_mode 'none'", 'counts': '150 / 150', 'source': 'docker_invocation.json; provider_config.json'},
    {'item': 'Interrupted/resumed or relabelled runs', 'galaxy': '-', 'open_ended_code': 'CompBio Astra: 2 runs resumed after host interruption (resume_invocation.json); CompBio DeepSeek: 2 false-positive wall-clock timeouts documented (TIMEOUT_FALSE_POSITIVE.md)', 'counts': '2 + 2', 'source': 'run_trace/resume_invocation.json; run_trace/TIMEOUT_FALSE_POSITIVE.md'},
    {'item': 'Shared Galaxy histories', 'galaxy': '3 BixBench history IDs are each linked to two runs (Sol bix-11-q1 r2/r3; DeepSeek-Claude bix-16-q3 r2/r3 and bix-61-q5 r1/r3)', 'open_ended_code': 'n/a', 'counts': '3', 'source': 'evidence runs[].source_ids'},
    {'item': 'Galaxy account identity', 'galaxy': 'Not recorded (history user/username redacted; CompBio seed owners and several campaign names redacted as [REDACTED ACCOUNT]); BixBench seed histories owned by one public Galaxy user; one IWC DeepSeek Galaxy run root is named after that user', 'open_ended_code': 'n/a', 'counts': '-', 'source': 'history.json; seed_history.json; run_record.json; codex_invocation.json run_root'},
    {'item': 'Authentication (IWC)', 'galaxy': "auth_mode 'chatgpt' for all runs incl. DeepSeek (model_provider deepseek)", 'open_ended_code': 'same', 'counts': '240', 'source': 'codex_invocation.json auth_mode, runtime.model_provider'},
]
out['q8_other_differences'] = {
    'source': 'see per-item source',
    'items': other,
    'skills': records(sort_cfg(skills)),
    'local_inputs': records(sort_cfg(local_inputs)),
    'network': records(sort_cfg(net)),
    'iwc_isolation': records(iso),
    'compbio_routing': records(routing),
}

unknowns = [
    'BixBench50: per-run time, token and retry budgets (evidence budgets null; no timeout field in invocation records).',
    'CompBio Galaxy arm: per-run wall-clock budget (task.json timeout_minutes null; prompts state none).',
    'All benchmarks: token budgets, retry policies and random seeds (seed null in all evidence records).',
    'Execution start/end for BixBench GPT runs (only workspace-preparation time, Galaxy history creation and usage-write time) and for all CompBio runs (only task creation/preparation and campaign-directory timestamps).',
    'Runtime model ID and reasoning for 900 CompBio open-ended GPT-5.5/Sol/Luna runs and 86 CompBio Galaxy runs (56 GPT-5.5, 30 Sol): no invocation record.',
    'Recorded list of exposed Galaxy MCP tools for BixBench50 and CompBio (only IWC records one).',
    'Codex CLI version for GPT runs outside the codex-0.146.0 image tag / codex_cli_0146 paths; IWC image tag (digest only).',
    'CompBio open-ended skill inventory (no skill_inventory.json in conda runs).',
    "Galaxy account(s) used to execute runs (redacted), and the purpose of the CompBio 'training' history routing tag.",
    'The rule used to select items for CompBio recovery/continuation/retry campaigns (only campaign names are recorded).',
    'Value of IWC_GALAXY_URL inside IWC containers (variable name recorded; evidence lists https://usegalaxy.org as the Galaxy server).',
]
out['unknowns_not_recorded'] = unknowns
(OUT / 'design_metadata.json').write_text(json.dumps(out, indent=1, default=nn))

# per-run supplementary CSV (selected columns, redacted)
cols = ['benchmark', 'task', 'run_id', 'condition', 'model', 'replicate', 'mm_supplied_label', 'mm_harness', 'mm_verified_runtime_id', 'mm_reasoning',
        'mm_verification_status', 'ev_iteration_setting', 'ev_prompt_variant', 'prompt_file_sha256', 'prompt_file_words', 'docker_image', 'docker_image_id',
        'iso_image_id', 'task_execution_backend', 'conda_execution_backend', 'docker_model', 'conda_model', 'iwc_runtime_model',
        'docker_reasoning_effort', 'conda_reasoning_effort', 'iwc_runtime_model_reasoning_effort', 'iwc_wall_clock_timeout_seconds', 'task_timeout_minutes',
        'conda_timeout_seconds', 'stated_minutes', 'rr_campaign', 'attempt_experiment', 'attempt_attempt', 'iwc_run_root', 'rr_prepared_at_utc',
        'task_created_at', 'completion_started_at', 'completion_finished_at', 'usage_written_at_utc', 'iwc_started_at_utc', 'postrun_finished_at',
        'ev_ts_history_create', 'galaxy_history_ids', 'ev_env_galaxy_server', 'docker_galaxy_execute_mcp_enabled', 'docker_galaxy_api_key_mode',
        'iwc_galaxy_mcp_tools', 'skills_copied', 'skills_skipped', 'local_input_count', 'trace_url', 'source_retrieval_min', 'source_retrieval_max']
df[cols].map(red).to_csv(OUT / 'per_run_design_metadata.csv', index=False)
print('ok')
