"""Shared data access, statistics and figure helpers for the two narrative manuscripts.

Both `user-oriented/scripts/make_figures.py` and `galaxy-oriented/scripts/make_figures.py` import this module.
It reads only archived evidence already in this repository; it runs no agent code, contacts no Galaxy server and
opens nothing under `ground_truth/`.

Inputs
  BixBench50_CompBio_analysis/analysis.json                 per-run records (score, tokens, cluster), per-job records
  manuscript_material/source_data/derived/run_summaries.jsonl.gz   per-run trace summaries (interface calls, failures)
  manuscript_material/source_data/figure_data.json          panel data assembled by manuscript_material/scripts/build_data.py
  manuscript_material/on_demand/Source_Data_OD_Fig*.xlsx    per-run grades, errors, actions and UDT trajectories
  analysis_reports/galaxy_improvement_20260924/v2_trace_friction/ledger.json   failure ledger (root causes)

CompBioBench per-run grades come from Source_Data_OD_Fig4.xlsx (`ab_replicate_sets`). They were produced by
manuscript_material/scripts/fig_on_demand.py against the reference key of the lab results repository, and that script
stops unless the grades reproduce all 24 official paired replicate scores. Two replicate scores are one point above the
archived reported benchmark scores (see manuscript_material/on_demand/README.md).

Statistics: 95% percentile cluster-bootstrap intervals, 20,000 resamples. Clusters are source capsules for
BixBench-Verified-50 and tasks for CompBioBench and IWC, as in the main manuscript materials.
"""
import functools
import gzip
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
NARR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
import style  # noqa: E402  (shared Nature Portfolio figure style; sets rcParams on import)
from style import plt  # noqa: E402,F401

B_SEED = 20261002
N_BOOT = 20000
FIG_W = 180 * style.MM  # Nature Methods maximum figure width (submission guidelines, checked October 2026)

CFG = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
       'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
       'codex_deepseek_v4_pro': 'DeepSeek V4 Pro',
       'deepseek_v4_pro_via_claude_code_superseded': style.SUPERSEDED, 'codex_gpt_6_astra': 'GPT-6 Astra'}
OD_CFG = {'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro'}  # on-demand workbooks spell the Codex DeepSeek label out
OD_BENCH = {'BixBench-Verified-50': 'BixBench50', 'CompBioBench': 'CompBio', 'IWC': 'IWC'}
OD_ENV = {'Galaxy condition': 'galaxy', 'Open-ended code condition': 'open_ended_code'}
CODEX4 = style.CONFIGS  # the four Codex model configurations: the primary paired population
IWC_NINE_EXCLUDED = 'wf_003_host_contamination_removal'  # unscored routes and score conflicts (main manuscript, I6)


def path(*p):
    return os.path.join(ROOT, *p)


# ---------------------------------------------------------------------------------------------------- loaders
@functools.lru_cache(None)
def analysis():
    return json.load(open(path('BixBench50_CompBio_analysis', 'analysis.json')))


@functools.lru_cache(None)
def runs():
    """One row per archived run: benchmark, task, cluster, cfg, env, replicate, score, tokens."""
    keep = ['benchmark', 'task', 'cluster', 'model', 'condition', 'replicate', 'score', 'answer', 'input_tokens',
            'output_tokens', 'jobs', 'errors', 'udt_requested', 'prompt_words']
    df = pd.DataFrame([{k: r.get(k) for k in keep} for r in analysis()['runs']])
    df['cfg'] = df['model'].map(CFG)
    df = df.rename(columns={'condition': 'env'})
    df.loc[df.benchmark != 'BixBench50', 'cluster'] = df.loc[df.benchmark != 'BixBench50', 'task']
    return df


@functools.lru_cache(None)
def summaries():
    rows = []
    for line in gzip.open(path('manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt'):
        s = json.loads(line)
        cc, ch = s.get('class_calls') or {}, s.get('class_chars') or {}
        rows.append(dict(benchmark=s['benchmark'], task=s['task'], cfg=CFG[s['model']], env=s['condition'],
                         replicate=s['replicate'], score=s['score'], input_tokens=s['input_tokens'],
                         output_tokens=s['output_tokens'], has_trace='n_mcp' in s,
                         n_mcp=s.get('n_mcp'), n_mcp_fail=s.get('n_mcp_fail'), n_shell=s.get('n_shell'),
                         n_shell_nonzero=s.get('n_shell_nonzero'), n_web=s.get('n_web'),
                         disc_calls=cc.get('discovery', 0), insp_calls=cc.get('inspection', 0),
                         exe_calls=cc.get('execution', 0), other_calls=cc.get('other', 0),
                         disc_chars=ch.get('discovery', 0), insp_chars=ch.get('inspection', 0),
                         exe_chars=ch.get('execution', 0), other_chars=ch.get('other', 0), shell_chars=ch.get('shell', 0),
                         udt_calls=(s.get('mcp_by') or {}).get('run_galaxy_udt_and_wait', 0),
                         cached=(s.get('usage') or {}).get('cached_input_tokens')))
    return pd.DataFrame(rows)


@functools.lru_cache(None)
def fd():
    return json.load(open(path('manuscript_material', 'source_data', 'figure_data.json')))


@functools.lru_cache(None)
def od(n, sheet):
    df = pd.read_excel(path('manuscript_material', 'on_demand', f'Source_Data_OD_Fig{n}.xlsx'), sheet_name=sheet)
    for c, m in [('benchmark', OD_BENCH), ('execution_condition', OD_ENV)]:
        if c in df:
            df[c] = df[c].map(lambda v: m.get(v, v))
    if 'model_configuration' in df:
        df['model_configuration'] = df['model_configuration'].map(lambda v: OD_CFG.get(v, v))
    return df.rename(columns={'execution_condition': 'env', 'model_configuration': 'cfg'})


@functools.lru_cache(None)
def ledger():
    return json.load(open(path('analysis_reports', 'galaxy_improvement_20260924', 'v2_trace_friction', 'ledger.json')))


@functools.lru_cache(None)
def graded_runs():
    """Per-run correctness for all three benchmarks, one row per replicate run.

    BixBench-Verified-50: archived binary evaluator score. CompBioBench: reference-key grade (see module docstring).
    IWC: continuous output agreement. Built from the replicate sets of Source_Data_OD_Fig4 so every benchmark uses the
    same set definition; BixBench scores are checked against the archive.
    """
    sets = od(4, 'ab_replicate_sets')
    out = []
    for r in sets.itertuples():
        for i, v in enumerate(str(r.replicate_scores).split(';'), start=1):
            out.append(dict(benchmark=r.benchmark, task=r.task, cfg=r.cfg, env=r.env, replicate=i, score=float(v)))
    g = pd.DataFrame(out)
    rr = runs()
    bix = rr[rr.benchmark == 'BixBench50'].groupby(['task', 'cfg', 'env']).score.sum()
    chk = g[g.benchmark == 'BixBench50'].groupby(['task', 'cfg', 'env']).score.sum()
    assert (bix.reindex(chk.index) == chk).all(), 'BixBench grades disagree with the archive'
    cl = rr.drop_duplicates(['benchmark', 'task'])[['benchmark', 'task', 'cluster']]
    return g.merge(cl, on=['benchmark', 'task'], how='left')


def set_category(scores, benchmark):
    """Replicate-set outcome: '3/3', 'split' or '0/3' (IWC: 'within' or 'split' on a 0.05 range)."""
    if benchmark == 'IWC':
        return 'split' if max(scores) - min(scores) > 0.05 else 'within'
    k = sum(1 for v in scores if v == 1)
    return '3/3' if k == len(scores) else ('0/3' if k == 0 else 'split')


@functools.lru_cache(None)
def replicate_sets():
    g = graded_runs()
    rows = []
    for (b, t, c, e), x in g.groupby(['benchmark', 'task', 'cfg', 'env']):
        sc = list(x.sort_values('replicate').score)
        rows.append(dict(benchmark=b, task=t, cfg=c, env=e, cluster=x.cluster.iloc[0], scores=sc,
                         n=len(sc), mean=float(np.mean(sc)), cat=set_category(sc, b)))
    return pd.DataFrame(rows)


@functools.lru_cache(None)
def iwc_sets_all_ten():
    """IWC replicate sets over all ten tasks (the on-demand sets use the nine matched tasks)."""
    rr = runs()
    iw = rr[(rr.benchmark == 'IWC')]
    rows = []
    for (t, c, e), x in iw.groupby(['task', 'cfg', 'env']):
        sc = [v for v in x.sort_values('replicate').score if v is not None and not pd.isna(v)]
        rows.append(dict(task=t, cfg=c, env=e, scored=len(sc) == 3,
                         cat=set_category(sc, 'IWC') if len(sc) == 3 else 'not scored',
                         rng=(max(sc) - min(sc)) if len(sc) == 3 else np.nan))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------------- statistics
def _weights(k, seed, n_boot=N_BOOT):
    rng = np.random.default_rng(seed)
    return rng.multinomial(k, np.full(k, 1.0 / k), size=n_boot).astype(float)


def boot_ratio_of_sums(num, den, seed=B_SEED, n_boot=N_BOOT):
    """Point estimate and 95% percentile interval of sum(num)/sum(den) with clusters resampled (arrays per cluster)."""
    num, den = np.asarray(num, float), np.asarray(den, float)
    w = _weights(len(num), seed, n_boot)
    est = num.sum() / den.sum()
    bs = (w @ num) / (w @ den)
    return est, float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))


def boot_diff(num_a, den_a, num_b, den_b, seed=B_SEED, n_boot=N_BOOT, scale=1.0):
    """Difference b - a of two ratio-of-sums sharing the same clusters (arrays aligned by cluster)."""
    a = [np.asarray(v, float) for v in (num_a, den_a, num_b, den_b)]
    w = _weights(len(a[0]), seed, n_boot)
    est = (a[2].sum() / a[3].sum() - a[0].sum() / a[1].sum()) * scale
    bs = ((w @ a[2]) / (w @ a[3]) - (w @ a[0]) / (w @ a[1])) * scale
    return est, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def boot_rel(num_a, den_a, num_b, den_b, seed=B_SEED, n_boot=N_BOOT):
    """Ratio (b / a) of two ratio-of-sums sharing the same clusters."""
    a = [np.asarray(v, float) for v in (num_a, den_a, num_b, den_b)]
    w = _weights(len(a[0]), seed, n_boot)
    est = (a[2].sum() / a[3].sum()) / (a[0].sum() / a[1].sum())
    with np.errstate(divide='ignore', invalid='ignore'):
        bs = ((w @ a[2]) / (w @ a[3])) / ((w @ a[0]) / (w @ a[1]))
    bs = bs[np.isfinite(bs)]
    return est, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def boot_median_ratio(values_by_cluster, seed=B_SEED, n_boot=N_BOOT):
    """Median of per-cell ratios, clusters resampled. values_by_cluster: list of arrays of per-cell ratios."""
    groups = [np.asarray(v, float) for v in values_by_cluster if len(v)]
    rng = np.random.default_rng(seed)
    est = float(np.median(np.concatenate(groups)))
    k = len(groups)
    bs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, k, k)
        bs[i] = np.median(np.concatenate([groups[j] for j in idx]))
    return est, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def paired_cluster_arrays(df, value, env_col='env', cluster_col='cluster', den=None):
    """Per-cluster sums of `value` (and of `den`, default counts) for open-ended code and Galaxy, aligned by cluster."""
    agg = {'num': (value, 'sum'), 'den': (den, 'sum') if den else (value, 'size')}
    g = df.groupby([cluster_col, env_col]).agg(**agg).unstack(env_col).fillna(0)
    return (g[('num', 'open_ended_code')].values, g[('den', 'open_ended_code')].values,
            g[('num', 'galaxy')].values, g[('den', 'galaxy')].values)


# ---------------------------------------------------------------------------------------------------- figure helpers
def outdirs(paper_dir):
    for sub in ['figures', os.path.join('figures', 'previews'), 'source_data']:
        os.makedirs(os.path.join(paper_dir, sub), exist_ok=True)


def save_figure(fig, paper_dir, name, title):
    """Vector PDF (editable TrueType text) plus a 300-dpi PNG preview; the title is stored as PDF metadata."""
    style.enforce_min_font(fig)
    fig.savefig(os.path.join(paper_dir, 'figures', f'{name}.pdf'), metadata={'Title': f"{name.replace('Fig', 'Fig. ')} | {title}"})
    fig.savefig(os.path.join(paper_dir, 'figures', 'previews', f'{name}.png'), dpi=300)
    plt.close(fig)


COLUMN_DOC = {
    # identifiers and populations
    'benchmark': 'Benchmark: BixBench-Verified-50, CompBioBench or IWC.',
    'task': 'Benchmark task identifier.', 'task_label': 'Short task name used in the figure.',
    'task_left_out': 'Task removed in this leave-one-task-out estimate.',
    'cfg': 'Model configuration (four Codex configurations are primary; the Claude Code harness is superseded).',
    'model': 'Model key as recorded in the archive (maps to cfg).', 'harness': 'Agent harness group.',
    'env': 'Execution arm: open_ended_code or galaxy (assigned arm, not verified execution location).',
    'run_id': 'Archived run identifier (unique within a task).', 'replicate': 'Replicate label 1-3 (not a matched random seed).',
    'row': 'Row label in the figure (model configuration, pooled estimate or sensitivity analysis).',
    'kind': 'Row type (config, pooled, sensitivity, superseded) or, for shell-side API use, whether the operation is permitted or a bypass.',
    'population': 'Analysed population.', 'group': 'Measure group.', 'unit': 'Unit of analysis or of the estimate.',
    'source': 'Evidence source for the row.', 'interval_source': 'Origin of the interval (archived analysis seed 20260922, or this analysis seed 20261002).',
    # counts
    'runs': 'Number of runs (eligible units for this row).', 'total': 'Denominator: all eligible units in this group.',
    'numerator': 'Numerator of the proportion.', 'denominator': 'Denominator of the proportion.',
    'calls': 'Number of interface calls.', 'tasks': 'Task(s) concerned.', 'task_cases': 'Number of audited task cases.',
    'episodes': 'Failure episodes (first failed run of a tool in a run plus later calls of that tool).',
    'errors': 'Number of execution errors.', 'failed_calls': 'Number of failed interface calls.',
    'failed_job_calls': 'Interface calls that returned a failed job.', 'with_error_text': 'Failed-job calls that returned standard error or output.',
    'without_error_text': 'Failed-job calls that returned only a job-state summary.',
    'returned_ok': 'Calls whose returned status was ok.', 'udt_calls': 'User-defined tool calls.',
    'requesting_runs': 'Runs that requested at least one user-defined tool.', 'galaxy_runs': 'Galaxy-arm runs.',
    'galaxy_runs_of_task': 'Galaxy-arm runs of the task(s), all five configurations.',
    'scored_incorrect_galaxy_runs': 'Galaxy-arm runs scored incorrect whose decisive cause was this mechanism.',
    'codex_galaxy_runs': 'Galaxy-arm runs with Codex traces (denominator for shell-side API use).',
    'traces': 'Runs with a parsed execution trace.', 'detailed_histories': 'Runs with a retrieved detailed analysis history.',
    'galaxy_interface_calls': 'Calls to the Galaxy interface namespaces.', 'galaxy_interface_call': 'True if the tool belongs to a Galaxy interface namespace.',
    'other_tool_server_calls': 'Calls to client built-ins and external connectors (excluded from interface measures).',
    'analysis_jobs': 'Galaxy analysis jobs (data-fetch jobs excluded).', 'history_dates': 'Range of Galaxy history creation dates.',
    'harness_variants': 'Distinct harness or image labels.', 'legacy_failed_calls': 'Failed calls counted by the archived trace-friction ledger.',
    'runs_code': 'Open-ended code runs.', 'runs_galaxy': 'Galaxy-arm runs.', 'sets_code': 'Replicate sets, open-ended code.',
    'sets_galaxy': 'Replicate sets, Galaxy.', 'sets_per_condition': 'Replicate sets per arm.',
    'discordant_code': 'Discordant replicate sets, open-ended code.', 'discordant_galaxy': 'Discordant replicate sets, Galaxy.',
    'discordant_sets_code': 'Discordant replicate sets, open-ended code.', 'discordant_sets_galaxy': 'Discordant replicate sets, Galaxy.',
    'split_replicate_sets': 'Discordant replicate sets contributing to the comparison.',
    'task_configuration_pairs': 'Task x model configuration pairs.', 'correct_code': 'Runs scored correct, open-ended code (of 12).',
    'correct_galaxy': 'Runs scored correct, Galaxy (of 12).', 'complete_cells': 'Task x configuration cells with all three required replicate observations in each arm for the stated measure.',
    'eligible_cells': 'Task x configuration cells eligible for the comparison.',
    'runs_with_analysis_software_named_in_shell': 'Galaxy-arm runs whose shell commands named an analysis program (unvalidated screen; neither a lower nor an upper bound on local computation).',
    'tools_inspected': 'Distinct tools inspected.', 'inspected_not_run': 'Distinct inspected tools never run.',
    'median_searches': 'Median tool searches per run.', 'max_searches': 'Maximum tool searches in one run.',
    'identifiers_not_found': 'Tool identifiers that could not be resolved.', 'mism': 'Run calls with a parameter mismatch.',
    'actions': 'Interface calls plus shell commands in the run.', 'input_tokens': 'Input tokens in the run, including cached input.',
    'galaxy_primary': 'Units with Galaxy platform, wrapper or server as primary cause.',
    'galaxy_contributing_only': 'Units with Galaxy as contributing cause only.', 'union': 'Primary plus contributing-only units.',
    # values
    'percent': 'Numerator / denominator x 100.', 'percent_ok': 'Calls returning ok (%).', 'percent_correct': 'Runs scored correct (%).',
    'rate': 'Proportion (0-1).', 'value': 'Component value (0-1).', 'accuracy': 'Runs or sets scored correct (%).',
    'open_ended_code': 'Value in the open-ended code arm.', 'galaxy': 'Value in the Galaxy arm.', 'code': 'Value in the open-ended code arm, or failure-class code.',
    'difference': 'Galaxy minus open-ended code.', 'd': 'Galaxy minus open-ended code, task mean.', 'pooled_difference': 'Pooled Galaxy minus code difference.',
    'ratio': 'Galaxy / open-ended code.', 'median_ratio': 'Median of within-cell Galaxy / code ratios (or incorrect / correct sibling ratio).',
    'ci95_low': 'Lower bound, 95% percentile cluster-bootstrap interval (20,000 resamples).',
    'ci95_high': 'Upper bound, 95% percentile cluster-bootstrap interval (20,000 resamples).',
    'p_holm': 'Holm-adjusted P value, two-sided Wilcoxon signed-rank test.', 'p_two_sided': 'Two-sided P value, Wilcoxon signed-rank test.',
    'spearman_rho': 'Spearman correlation over runs.', 'errors_per_run': 'Mean execution errors per run.',
    'unanimous_code': 'Tasks with all three runs correct, open-ended code (%).', 'unanimous_galaxy': 'Tasks with all three runs correct, Galaxy (%).',
    'within_set_range': 'Maximum minus minimum output agreement within the replicate set.',
    'median_input_tokens_million': 'Strategy token coordinate, millions: median per run for one run; median three-run sum per task x configuration for a vote.',
    'consensus_rate_A': 'Replicate sets with a majority answer under rule A (%).', 'consensus_rate_B': 'Replicate sets with a majority answer under rule B (%).',
    'grade': 'Run score: binary for BixBench-Verified-50 and CompBioBench, output agreement 0-1 for IWC.',
    'run_correct': 'Run scored correct (IWC: output agreement >= 0.95).', 'later_ok': 'The same tool later returned ok in the run.',
    'matches_reference': 'Answer matches the benchmark reference.',
    # categories and text
    'measure': 'Measure name.', 'category': 'Category.', 'status': 'Returned status.', 'status_label': 'Plain-language status.',
    'primary_cause': 'Primary cause assigned in the targeted audit.', 'cause': 'Traced cause.', 'mechanism': 'Mechanism.',
    'failure_class': 'Failure class from the ordered rules (Methods).', 'fidelity_class': 'Semantic-fidelity class (Methods).',
    'error_type': 'Execution-error type.', 'phase': 'Job-failure phase.', 'attempt': 'First attempt at the tool in the run, or retry.',
    'tool': 'Interface operation.', 'tool_id': 'Galaxy tool identifier.', 'tool_id_base': 'Galaxy tool identifier without version.',
    'tool_kind': 'Installed tool or user-defined tool.', 'user_defined_tool': 'True for user-defined-tool calls.',
    'call_class': 'Interface call class (discovery, inspection, execution, staging).', 'operation': 'Shell-side Galaxy API operation.',
    'trajectory': 'User-defined-tool trajectory of the run.', 'strategy': 'User strategy (one run, or three runs and a vote).',
    'token_kind': 'Token measure.', 'component': 'IWC score component.', 'endpoint': 'Benchmark-specific endpoint.',
    'reference_provenance': 'How the reference was obtained.', 'evidence': 'Evidence item.', 'finding': 'Confirmed audit finding (observed case).',
    'answer': 'Submitted BixBench-Verified-50 answer; CompBioBench answer values are withheld in the manuscript package pending release authorization.',
    'interpretation': 'Traced explanation.', 'what_happened': 'Requested versus executed analysis.', 'consequence': 'Observed consequence.',
    'open_ended_code_state': 'Replicate-set outcome, open-ended code.', 'galaxy_state': 'Replicate-set outcome, Galaxy.',
    'better': 'Direction of improvement.', 'baseline_measure': 'Baseline measure (Fig. 6a).', 'requirement': 'Requirement.',
    'intervention': 'Intervention needed to test the requirement (not tested here).',
    'mean_score': 'Mean archived score over the eligible task runs in a configuration x replicate (0-1; multiplied by 100 only for percentage displays).',
    'primary_configuration': 'True for one of the four shared Codex configurations.',
    'bix_benchmark_side_task': 'True for a task removed by the stated retrospective BixBench audit-category sensitivity.',
    'compbio_outcome_named_cell': 'True for a task x configuration cell containing an outcome-named campaign run.',
    'iwc_zero_task': 'True for an IWC task containing at least one zero-scored run.',
    'iwc_atac_task': 'True for the IWC ATAC-seq task whose route references include calibration from agent runs.',
    'budget_matched': 'True when the recorded Galaxy and code time limits match for this task x configuration x replicate pair.',
    'selected_replicate_A': 'Earliest replicate in the majority identity group under rule A; absent when no consensus exists.',
    'selected_replicate_B': 'Earliest replicate in the majority identity group under rule B; absent when no consensus exists.',
    'member_grades_disagree_A': 'True when the rule A majority identity group contains differing archived grades.',
    'member_grades_disagree_B': 'True when the rule B majority identity group contains differing archived grades.',
    'checked_parameter_count': 'Adapter-reported count of compared non-dataset parameters; a positive count alone does not establish matching.',
    'prov_status': 'Adapter-reported parameter provenance status; not_comparable is not a match.',
    'dataset_prov_status': 'Adapter-reported dataset/input provenance status, evaluated separately from parameter matching.',
    'cluster': 'Bootstrap resampling unit: BixBench source capsule, otherwise task identifier.',
    'single': 'Mean archived grade across the three replicate runs in this set (0-1).',
    'oracle': 'One if at least two replicate grades are correct; uses evaluator information and is not a user strategy.',
    'input_tokens_three_runs': 'Sum of input tokens for all three runs; missing if any usage record is incomplete.',
    'vote_A': 'Archived grade of the earliest-replicate submitted answer in the rule A majority group; zero when no consensus exists.',
    'vote_B': 'Archived grade of the earliest-replicate submitted answer in the rule B majority group; zero when no consensus exists.',
    'consensus_A': 'True if at least two finite, nonempty answers share rule A identity.',
    'consensus_B': 'True if at least two finite, nonempty answers share rule B identity.',
    'score': 'Archived binary evaluator grade or reconstructed-reference grade; IWC is continuous output agreement (0-1).',
    'line': 'Line number of the interface call or event in the archived trace.',
    'result_line': 'Line number of the returned result in the archived trace.',
    'n_mismatches': 'Count of parameter mismatches recorded by the adapter.',
    'Galaxy-interface calls per run (median)': 'Median calls to Galaxy-interface namespaces per traced run in this configuration.',
    'Failed Galaxy-interface calls (%)': 'Error-coded Galaxy-interface calls divided by all Galaxy-interface calls, percent.',
    'Input tokens per run (median, millions)': 'Median recorded input tokens per run divided by one million.',
    'User-defined tool requested (% runs)': 'Percent of traced runs requesting at least one user-defined tool.',
    'Relevant skill opened (% of 114 runs)': 'Percent opening a relevant skill among the 114 configuration runs whose tasks provided one.',
    'Interface library scripted (runs)': 'Count of runs invoking the interface library from a script.',
    'tool_id_full': 'Requested or reported Galaxy tool identifier, including version when available.',
    'result_status': 'Status reported by the structured or parsed interface result.',
    'prov_stage': 'Recorded provenance-check stage: validation (before submission) or post_run (after execution), where available.',
    'fid': 'Exclusive result/provenance class; independent mismatch flags may overlap these classes.',
    'parameter_mismatch': 'True when the adapter parameter provenance status is mismatch, including failed-result calls.',
    'input_mismatch': 'True when the adapter dataset/input provenance status is mismatch.',
    'a1_subclass': 'Missing versus unusable history context subclass; populated only for A1 calls.',
    'n_jobs': 'Count of job records returned by this call; missing or zero does not prove that no job existed.',
    'job_ids': 'Job identifiers returned in the interface result.',
    'job_states': 'States of job records returned in the interface result.',
    'any_job_error': 'True if any returned job state is error or failed.',
    'job_failure_phases': 'Failure phases reported by job diagnostics; may contain multiple phases.',
    'call_status': 'Client transport/item status, separate from the structured result status.',
    'returned_job_evidence': 'Category: Job record returned or Job metadata absent; absent metadata does not prove that no job existed.',
    'first_non_ok_line': 'Trace line of the first non-ok result for this run and version-stripped tool family.',
    'first_non_ok_status': 'Returned status of that first non-ok result; includes caught mismatches and timeouts.',
    'all_episodes': 'All observed non-ok run x tool-family episodes before grade availability filtering.',
    'scored_episodes': 'Episodes with an available benchmark grade for the run.',
    'shell_commands': 'Count of shell commands in the traced run.',
}


def _describe(col):
    if col in COLUMN_DOC:
        return COLUMN_DOC[col]
    return 'Value shown in the figure for this column (see the panel legend).'


def source_data(paper_dir, name, sheets, title=None):
    """Write one Source Data workbook: a README sheet, one sheet per panel and a column dictionary."""
    p = os.path.join(paper_dir, 'source_data', f'Source_Data_{name}.xlsx')
    paper = os.path.basename(os.path.normpath(paper_dir))
    label = name.replace('ED_Fig', 'Extended Data Fig. ').replace('Fig', 'Fig. ')
    readme = pd.DataFrame({'field': ['item', 'title', 'paper', 'generated by', 'intervals', 'rounding', 'sheets'],
                           'value': [label, title or '', paper, f'manuscript_narrative/{paper}/scripts/make_figures.py',
                                     '95% percentile cluster bootstrap, 20,000 resamples; clusters are source capsules '
                                     '(BixBench-Verified-50) or tasks; seed 20261002 unless a row says archived (seed 20260922)',
                                     'Values are unrounded here; text and figures round half away from zero',
                                     '; '.join(k[:31] for k in sheets)]})
    dic = [dict(sheet=sheet[:31], column=str(c), description=_describe(str(c))) for sheet, df in sheets.items() for c in df.columns]
    with pd.ExcelWriter(p, engine='openpyxl') as xw:
        readme.to_excel(xw, sheet_name='README', index=False)
        for sheet, df in sheets.items():
            df.to_excel(xw, sheet_name=sheet[:31], index=False)
        pd.DataFrame(dic).to_excel(xw, sheet_name='dictionary', index=False)
    return p


def fmt_ci(est, lo, hi, nd=1, signed=True, unit=''):
    f = (lambda v: f'{v:+.{nd}f}') if signed else (lambda v: f'{v:.{nd}f}')
    g = lambda v: f'{v:.{nd}f}'.replace('-', '−')  # noqa: E731
    return f"{f(est).replace('-', '−')}{unit} ({g(lo)} to {g(hi)})"


# ---------------------------------------------------------------------------------------------------- revision analyses
def fmt(x, nd=1, signed=False):
    """Round half away from zero (21.15 -> 21.2) so that text, figures and Source Data agree."""
    from decimal import ROUND_HALF_UP, Decimal
    q = Decimal(str(round(float(x), 12))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    if q == 0:
        q = abs(q)  # no negative zero
    out = f'{q:f}'
    if signed and q > 0:
        out = '+' + out
    return out.replace('-', '−')


def answer_id(a, rule='A'):
    """Outcome-blind answer identity used for retrospective voting sensitivity.

    Rule A (primary, as documented for the majority-vote analysis): trim, lowercase, remove spaces; a numeric answer
    is compared to 10 significant digits. A trailing percent sign is retained as a unit; no unit conversion is performed.
    Rule B (sensitivity): as A, but numbers compared to 3 significant digits.
    Missing or empty answers have no identity and cannot form a majority.
    """
    if not isinstance(a, str) or not a.strip():
        return None
    a = ''.join(a.strip().lower().split())
    percent = a.endswith('%')
    numeric = a[:-1] if percent else a
    try:
        v = float(numeric)
        if not np.isfinite(v):
            return None
        if v == 0:
            v = 0.0  # signed zero has the same numeric identity
        identity = f'{v:.10g}' if rule == 'A' else f'{v:.3g}'
        return identity + ('%' if percent else '')
    except ValueError:
        return a


@functools.lru_cache(None)
def vote_sets():
    """Per replicate set (BixBench-Verified-50, CompBioBench): single-run accuracy, the at-least-two-correct oracle and
    outcome-blind majority votes under rules A and B. A vote selects the answer identity given by at least two runs;
    without such a majority the set has no consensus answer and is scored incorrect. The selected answer is then scored
    using the archived grade of the earliest-replicate member of that group. Selection of both the group and its
    representative is independent of grades. This reuses a submitted answer's grade; it is not independent regrading
    of the normalized identity. Conflicting member grades are counted explicitly."""
    import collections
    r = runs()
    g = graded_runs()[['benchmark', 'task', 'cfg', 'env', 'replicate', 'score']].rename(columns={'score': 'grade'})
    x = r.merge(g, on=['benchmark', 'task', 'cfg', 'env', 'replicate'])
    x = x[x.benchmark.isin(['BixBench50', 'CompBio'])]
    rows = []
    for (b, t, c, e, cl), y in x.groupby(['benchmark', 'task', 'cfg', 'env', 'cluster']):
        y = y.sort_values('replicate')
        grades = list(y.grade)
        row = dict(benchmark=b, task=t, cfg=c, env=e, cluster=cl, single=float(np.mean(grades)), oracle=float(sum(grades) >= 2),
                   input_tokens_three_runs=float(y.input_tokens.sum()) if y.input_tokens.notna().all() else np.nan)
        for rule in ('A', 'B'):
            ids = [answer_id(a, rule) for a in y.answer]
            cnt = collections.Counter(i for i in ids if i)
            top = cnt.most_common(1)[0] if cnt else (None, 0)
            if top[1] >= 2:
                member_indices = [j for j, identity in enumerate(ids) if identity == top[0]]
                member = [grades[j] for j in member_indices]
                selected = member_indices[0]
                row[f'vote_{rule}'] = float(grades[selected])
                row[f'selected_replicate_{rule}'] = int(y.replicate.iloc[selected])
                row[f'consensus_{rule}'] = True
                row[f'member_grades_disagree_{rule}'] = len(set(member)) > 1
            else:
                row[f'vote_{rule}'] = 0.0
                row[f'selected_replicate_{rule}'] = None
                row[f'consensus_{rule}'] = False
                row[f'member_grades_disagree_{rule}'] = False
        rows.append(row)
    return pd.DataFrame(rows)


AUDIT_KEY_LAYER = {'genome-coords-q1': 'predicted (audit corrected to E)', 'extract-rna-secondary-structure-q1': 'predicted'}


def compbio_variants():
    """CompBioBench per-run grades under reference-key variants (per-run grades from the reconstructed key).

    primary: reconstructed key as used throughout; alt_genome_D: genome-coords-q1 scored against the published
    predicted answer D instead of the audit's E; no_predicted: excluding the two audited tasks whose key is score-predicted;
    informative: only the 53 audited tasks (every task with at least one run that deviates from the key)."""
    g = graded_runs()
    g = g[(g.benchmark == 'CompBio') & g.cfg.isin(CODEX4)].copy()
    r = runs()
    ans = r[r.benchmark == 'CompBio'][['task', 'cfg', 'env', 'replicate', 'answer']]
    g = g.merge(ans, on=['task', 'cfg', 'env', 'replicate'], how='left')
    audited = {t['task'] for t in fd()['task_cases'] if t['benchmark'] == 'CompBio'}
    alt = g.copy()
    m = alt.task == 'genome-coords-q1'
    alt.loc[m, 'score'] = (alt.loc[m, 'answer'].str.strip().str.upper() == 'D').astype(float)
    return {'primary': g, 'alt_genome_D': alt, 'no_predicted': g[~g.task.isin(AUDIT_KEY_LAYER)],
            'informative': g[g.task.isin(audited)]}


def audit_categories():
    """Task -> primary audit category (C1-C8) from the targeted task-level audit (individual_error_analysis.md)."""
    return {(t['benchmark'], t['task']): t['category'] for t in fd()['task_cases']}


@functools.lru_cache(None)
def iwc_components():
    """Per IWC run: archived score, evaluator route, whether the route reference was calibrated from an agent execution
    record, and the task's scientifically interpretable components (from each run's evaluation.json)."""
    import glob
    rr = {(x['task'], x['run_id']): x for x in analysis()['runs'] if x['benchmark'] == 'IWC'}
    rows = []
    for f in glob.glob(path('IWC', 'analysis', '*', 'source_snapshots', 'huggingface_traces', 'files', '*', 'evaluation.json')):
        task, run = f.split(os.sep)[-6], f.split(os.sep)[-2]
        meta = rr.get((task, run))
        if meta is None:
            continue
        e = json.load(open(f))
        rt = e.get('route') or {}
        prov = (rt.get('provenance') or '').lower()
        det = e.get('details') or {}
        vs = rt.get('reference_variant_scores') or {}
        rows.append(dict(task=task, run_id=run, cfg=CFG[meta['model']], env=meta['condition'], replicate=meta['replicate'],
                         score=meta['score'], run_record_score=meta.get('run_record_score'), route=rt.get('route_id'),
                         route_reference_from_agent_run=('calibrated from' in prov and 'execution' in prov and 'protocols are calibrated' not in prov),
                         significant_jaccard=det.get('significant_jaccard'), significant_candidate=det.get('significant_candidate'),
                         significant_reference=det.get('significant_reference'), precision=det.get('precision'), recall=det.get('recall'),
                         f1=det.get('f1'), workflow_variant_score=vs.get('iwc-summit-split')))
    return pd.DataFrame(rows)


@functools.lru_cache(None)
def galaxy_calls():
    """Per-call table of interface activity in Galaxy-condition runs (derived/galaxy_calls/, built by extract_calls.py)."""
    p = os.path.join(NARR, 'derived', 'galaxy_calls', 'calls.csv.gz')
    if not os.path.exists(p):
        return None
    c = pd.read_csv(p, low_memory=False)
    c['cfg'] = c['model'].map(CFG)
    return c


# Failure classes for failed Galaxy-interface calls. Rules copied verbatim from
# analysis_reports/galaxy_improvement_20260924/v2_trace_friction/taxonomy.py so that counts stay comparable.
FAIL_RULES = [
    ('A1 tool-schema needs history context', r'History unavailable\. Please specify a valid history id'),
    ('A5 ID handling (wrong/foreign/truncated IDs)', r'Wrong\s+id|invalid dataset id|History is not owned|unable to decode|not owned by user'),
    ('A2 tool ID not found / guessed', r'Tool not found|Could not find tool with id'),
    ('A6 UDT representation schema', r"\('body', 'representation'|from_work_dir|String should match pattern|Extra inputs are not permitted|discriminator|udt_creation|representation"),
    ('A3 nested-parameter key structure', r'invalid key structure|received conflicting value|must be set for non optional|submitted for conditional parameter'),
    ('A7 upload / datatype registry', r'Requested extension .* unknown|create file url|upload_failed|cannot upload|No data was entered in the upload'),
    ('A8 server / transport / rate-limit', r'<!DOCTYPE HTML|<html|Uncaught exception|Too Many Requests|Transport closed|timed out|Cannot execute tool \[__DATA_FETCH__\]|Required parameter\(s\) kwd'),
    ('A4 parameter value / datatype validation', r'VALIDATION|ParameterValueError|No value provided|invalid option|required format|collection supplied|at least \d+ datasets|Field requires a value|cannot use dataset collection|Parameter validation error|Cannot split collection'),
    ('B1 UDT container missing dependency', r'there is no package called|ModuleNotFoundError|No module named|externally-managed|command not found|: not found|ImportError|cannot open shared object'),
    ('B4 input format / compression / index', r'gzip|magic|Could not parse|unrecognized|unindexable|index|not a valid|EOF|truncated file|UnicodeDecodeError'),
    ('B5 memory / resource', r'MemoryError|Killed|out of memory|OOM|oom|Cannot allocate'),
    ('B2 job error with no diagnostic', r'NO_DIAGNOSTIC|^[0-9a-f]{32}=error(?! \()'),
    ('B3 tool runtime error (stderr)', r'tool_stderr|stderr|Traceback|recent call last|line \d+|Error in|Exception|exit_code|Error:|error:'),
]


def _classify_failure(err, status, tool):
    import re
    txt = (err or '') + ' ' + (status or '')
    if tool == 'run_galaxy_udt_and_wait' and status == 'udt_creation_failed':
        return 'A6 UDT representation schema'
    for name, rx in FAIL_RULES:
        if re.search(rx, txt):
            return name
    if status in ('validation_failed',):
        return 'A4 parameter value / datatype validation'
    if status in ('timeout', 'start_timeout'):
        return 'A8 server / transport / rate-limit'
    if not (err or '').strip():
        return 'B2 job error with no diagnostic'
    return 'Z unclassified'


@functools.lru_cache(None)
def galaxy_failures():
    """One row per failed call of the Galaxy interface: the original rule (taxonomy.py classes; non-Galaxy namespaces
    removed) plus transport or tool exceptions that the original rule counted as successes (class X)."""
    calls = galaxy_calls()
    gal = calls[calls.galaxy_server == True]  # noqa: E712
    key = set(zip(gal.run_id, gal.task, gal.line))
    rows = []
    for line in gzip.open(path('manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt'):
        s = json.loads(line)
        if s['condition'] != 'galaxy' or not s.get('trace'):
            continue
        for er in s.get('errors') or []:
            if (s['run_id'], s['task'], er['line']) not in key:
                continue  # not a Galaxy-interface call
            c = _classify_failure(er.get('err'), er.get('status'), er['tool'])
            sub = None
            if c.startswith('A1'):
                sub = 'history not owned by the user' if 'not owned' in (er.get('err') or '') else (
                    'history given but unusable' if '"history_id"' in (er.get('args') or '') else 'no history given')
            rows.append(dict(benchmark=s['benchmark'], task=s['task'], run_id=s['run_id'], cfg=CFG[s['model']], line=er['line'],
                             tool=er['tool'], failure_class=c, a1_subclass=sub))
    extra = gal[(gal.call_status == 'failed') & (gal.extract_fail == False)]  # noqa: E712
    for r in extra.itertuples():
        rows.append(dict(benchmark=r.benchmark, task=r.task, run_id=r.run_id, cfg=CFG[r.model], line=r.line, tool=r.tool,
                         failure_class='X additional transport or tool exceptions (previously uncounted)', a1_subclass=None))
    return pd.DataFrame(rows)


OUTCOME_NAMED = r'wrong|target\d+|near\d+'


@functools.lru_cache(None)
def design_runs():
    p = os.path.join(NARR, 'derived', 'design', 'per_run_design_metadata.csv')
    d = pd.read_csv(p, low_memory=False)
    d['cfg'] = d.model.map(CFG)
    return d


def compbio_outcome_named_cells():
    """CompBioBench task x model-configuration cells containing a run selected from a campaign whose name refers to
    wrong answers or target scores (derived/design; the selection rule for these campaigns is not recorded)."""
    d = design_runs()
    cb = d[(d.benchmark == 'CompBio')]
    flag = cb.rr_campaign.fillna('').str.contains(OUTCOME_NAMED, regex=True)
    return cb[flag][['task', 'cfg']].drop_duplicates(), int(flag.sum())
