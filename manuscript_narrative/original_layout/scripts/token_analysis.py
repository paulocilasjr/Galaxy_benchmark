"""Archive-only context-cost analysis for the original-layout narrative.

No benchmark agents, live services, private reference keys or ground_truth files are opened.
IWC agreement remains continuous; model labels identify archived configurations.
Primary model comparisons exclude Astra and the superseded Claude Code configuration.
"""
from pathlib import Path
import json
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon

PAPER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAPER.parent))
import narrative_common as nc

OUT = PAPER / 'analysis'
OUT.mkdir(exist_ok=True)
BOOT = 20000
SEED = 20261002
PRIMARY = list(nc.CODEX4)
BENCHES = ['BixBench50', 'CompBio', 'IWC']
ENVS = ['open_ended_code', 'galaxy']
KEYS = ['benchmark', 'task', 'cfg', 'env', 'replicate']
OPS = {'search_galaxy_tools': 'Discovery', 'inspect_galaxy_tool': 'Discovery',
       'inspect_galaxy_history': 'History/dataset inspection', 'peek_galaxy_dataset': 'History/dataset inspection',
       'inspect_archive_inventory': 'History/dataset inspection', 'run_galaxy_tool_and_wait': 'Execution',
       'run_galaxy_udt_and_wait': 'Execution', 'wait_for_galaxy_jobs': 'Execution', 'stage_workspace_file': 'Staging/other'}


def records(df):
    return json.loads(df.to_json(orient='records'))


def write(df, name):
    df.to_csv(OUT / ('token_' + name + '.csv'), index=False)


def ci(values, clusters):
    """Median of observations with source capsules/tasks resampled, not individual runs."""
    z = pd.DataFrame({'v': values, 'cluster': clusters}).dropna()
    if z.empty:
        return (None, None, None)
    return nc.boot_median_ratio([x.v.values for _, x in z.groupby('cluster')], n_boot=BOOT)


def cell_table(s, kind, scope, cfg=None):
    x = s[s.cfg.isin(PRIMARY)]
    if scope == 'primary_endpoint':
        x = x[x.primary_endpoint]
    if cfg:
        x = x[x.cfg == cfg]
    med = x.groupby(['benchmark', 'task', 'cfg', 'env'])[kind].median().unstack('env')
    n = x.groupby(['benchmark', 'task', 'cfg', 'env'])[kind].count().unstack('env').fillna(0)
    tab = med.join(n.add_prefix('n_')).reset_index()
    tab['token_kind'] = kind
    tab['task_scope'] = scope
    tab['eligible'] = ((tab.n_galaxy == 3) & (tab.n_open_ended_code == 3) &
                       tab.open_ended_code.gt(0) & tab.galaxy.notna())
    tab['ratio'] = (tab.galaxy / tab.open_ended_code).where(tab.eligible)
    clusters = s.drop_duplicates(['benchmark', 'task'])[['benchmark', 'task', 'cluster']]
    return tab.merge(clusters, on=['benchmark', 'task'], how='left')


def performance_ci(x):
    q = x.groupby('cluster').score.agg(['sum', 'count'])
    w = nc._weights(len(q), SEED, BOOT)
    vals = (w @ q['sum'].values) / (w @ q['count'].values)
    return x.score.mean(), *np.percentile(vals, [2.5, 97.5])


def main():
    s = nc.summaries().drop(columns='score').merge(nc.graded_runs().rename(columns={'score': 'endpoint_score'}), on=KEYS, how='left')
    # Primary IWC endpoint has nine tasks. For token-only comparisons we also show all ten archived tasks.
    s['primary_endpoint'] = s.cfg.isin(PRIMARY) & s.endpoint_score.notna()
    cl = nc.runs().drop_duplicates(['benchmark', 'task'])[['benchmark', 'task', 'cluster']]
    s = s.drop(columns='cluster').merge(cl, on=['benchmark', 'task'], how='left')
    s['uncached_input_tokens'] = s.input_tokens - s.cached
    s['uncached_input_tokens'] = s.uncached_input_tokens.where(s.uncached_input_tokens.ge(0))
    s['endpoint_type'] = np.where(s.benchmark == 'IWC', 'continuous output agreement', 'binary benchmark acceptance')
    s['model_primary'] = s.cfg.isin(PRIMARY)
    write(s, 'run_observations')

    cells, ratios, totals = [], [], []
    for scope in ['archive_token_tasks', 'primary_endpoint']:
        for kind in ['input_tokens', 'uncached_input_tokens', 'output_tokens']:
            tab = cell_table(s, kind, scope)
            cells.append(tab)
            runs = s[s.cfg.isin(PRIMARY)]
            if scope == 'primary_endpoint':
                runs = runs[runs.primary_endpoint]
            runs = runs.merge(tab[tab.eligible][['benchmark', 'task', 'cfg']], on=['benchmark', 'task', 'cfg'])
            for b in BENCHES:
                for cfg in ['All four primary configurations'] + PRIMARY:
                    allx = tab[tab.benchmark == b]
                    q = runs[runs.benchmark == b]
                    if cfg in PRIMARY:
                        allx = allx[allx.cfg == cfg]
                        q = q[q.cfg == cfg]
                    x = allx[allx.eligible]
                    est, low, high = ci(x.ratio, x.cluster)
                    ratios.append(dict(benchmark=b, cfg=cfg, token_kind=kind, task_scope=scope,
                                       median_ratio=est, ci95_low=low, ci95_high=high,
                                       complete_cells=len(x), candidate_cells=len(allx), clusters=x.cluster.nunique(),
                                       greater_than_one_point=bool(est > 1) if est is not None else None,
                                       ci_excludes_one=bool(low > 1 or high < 1) if low is not None else None))
                    if kind == 'output_tokens':
                        continue
                    # Aggregate consumption: total Galaxy tokens over total code tokens on the same eligible cells.
                    by = q.groupby(['cluster', 'env'])[kind].sum().unstack('env').fillna(0)
                    tot, tlo, thi = nc.boot_ratio_of_sums(by.galaxy.values, by.open_ended_code.values, seed=SEED, n_boot=BOOT)
                    totals.append(dict(benchmark=b, cfg=cfg, token_kind=kind, task_scope=scope,
                                       ratio_of_totals=tot, ci95_low=tlo, ci95_high=thi,
                                       galaxy_total_tokens=float(by.galaxy.sum()), code_total_tokens=float(by.open_ended_code.sum()),
                                       galaxy_mean_per_run=float(q[q.env == 'galaxy'][kind].mean()),
                                       code_mean_per_run=float(q[q.env == 'open_ended_code'][kind].mean()),
                                       runs_per_arm=int((q.env == 'galaxy').sum()), complete_cells=len(x), clusters=int(q.cluster.nunique()),
                                       greater_than_one_point=bool(tot > 1), ci_excludes_one=bool(tlo > 1 or thi < 1)))
    cell_obs = pd.concat(cells, ignore_index=True)
    ratio_df = pd.DataFrame(ratios)
    total_df = pd.DataFrame(totals)
    write(cell_obs, 'cell_eligibility_and_ratios')
    write(ratio_df, 'paired_arm_ratios')
    write(total_df, 'arm_total_ratios')

    # Code-arm runs with very large inputs on a few IWC workflows drive the aggregate IWC comparison.
    iwc_rows = []
    for (task, e), q in s[(s.benchmark == 'IWC') & s.model_primary].groupby(['task', 'env']):
        iwc_rows.append(dict(task=task, env=e, primary_endpoint_task=task != nc.IWC_NINE_EXCLUDED, runs=int(q.input_tokens.count()),
                             mean_input_tokens=q.input_tokens.mean(), median_input_tokens=q.input_tokens.median(),
                             max_input_tokens=q.input_tokens.max(), total_input_tokens=q.input_tokens.sum()))
    write(pd.DataFrame(iwc_rows), 'iwc_task_inputs')

    # A common task population across all eight arm × configuration groups avoids changing the model's task mix.
    models, sol = [], []
    for b in BENCHES:
        x = s[(s.benchmark == b) & s.primary_endpoint].copy()
        complete = x.groupby(['task', 'cfg', 'env']).agg(n=('input_tokens', 'count'), score_n=('endpoint_score', 'count'))
        eligible = complete[(complete.n == 3) & (complete.score_n == 3)].reset_index().groupby('task').size()
        tasks = eligible[eligible == len(PRIMARY) * 2].index
        common = x[x.task.isin(tasks)]
        for e in ENVS:
            for kind in ['input_tokens', 'uncached_input_tokens']:
                rr = []
                for cfg in PRIMARY:
                    q = common[(common.env == e) & (common.cfg == cfg)]
                    score, lo, hi = performance_ci(q.rename(columns={'endpoint_score': 'score'}))
                    tok, tlo, thi = ci(q[kind], q.cluster)
                    qq = x[(x.env == e) & (x.cfg == cfg)]
                    rr.append(dict(benchmark=b, env=e, cfg=cfg, token_kind=kind,
                                   mean_endpoint=score, endpoint_ci95_low=lo, endpoint_ci95_high=hi,
                                   median_tokens=tok, token_ci95_low=tlo, token_ci95_high=thi, mean_tokens=q[kind].mean(),
                                   common_tasks=len(tasks), common_runs=len(q), common_clusters=q.cluster.nunique(),
                                   all_primary_mean_endpoint=qq.endpoint_score.mean(), all_primary_scored_runs=len(qq),
                                   all_primary_median_tokens=qq[kind].median(), all_primary_token_records=qq[kind].count()))
                for r in rr:
                    r['point_pareto_efficient'] = not any(
                        (p['mean_endpoint'] >= r['mean_endpoint'] and p['median_tokens'] <= r['median_tokens'] and
                         (p['mean_endpoint'] > r['mean_endpoint'] or p['median_tokens'] < r['median_tokens'])) for p in rr)
                    r['dominated_by'] = ';'.join(p['cfg'] for p in rr if
                        p['mean_endpoint'] >= r['mean_endpoint'] and p['median_tokens'] <= r['median_tokens'] and
                        (p['mean_endpoint'] > r['mean_endpoint'] or p['median_tokens'] < r['median_tokens']))
                    # Sensitivity: the same rule with mean rather than median single-run tokens.
                    r['point_pareto_efficient_mean_tokens'] = not any(
                        (p['mean_endpoint'] >= r['mean_endpoint'] and p['mean_tokens'] <= r['mean_tokens'] and
                         (p['mean_endpoint'] > r['mean_endpoint'] or p['mean_tokens'] < r['mean_tokens'])) for p in rr)
                models.extend(rr)
                target = common[(common.env == e) & (common.cfg == 'GPT-5.6 Sol')]
                for cfg in PRIMARY:
                    if cfg == 'GPT-5.6 Sol':
                        continue
                    competitor = common[(common.env == e) & (common.cfg == cfg)]
                    pair = target.merge(competitor, on=['task', 'replicate', 'cluster'], suffixes=('_sol', '_other'))
                    p = pair.groupby('cluster').agg(s=('endpoint_score_sol', 'sum'), o=('endpoint_score_other', 'sum'), n=('task', 'size'))
                    diff, dlo, dhi = nc.boot_diff(p.o, p.n, p.s, p.n, n_boot=BOOT)
                    pos = pair[kind + '_other'].gt(0) & pair[kind + '_sol'].notna()
                    tr, trlo, trhi = ci(pair.loc[pos, kind + '_sol'] / pair.loc[pos, kind + '_other'], pair.loc[pos, 'cluster'])
                    sol.append(dict(benchmark=b, env=e, token_kind=kind, competitor=cfg,
                                    sol_minus_other_endpoint=diff, endpoint_ci95_low=dlo, endpoint_ci95_high=dhi,
                                    median_sol_over_other_tokens=tr, token_ci95_low=trlo, token_ci95_high=trhi,
                                    paired_runs=len(pair), tasks=len(tasks), clusters=len(p),
                                    inference='exploratory unadjusted 95% intervals; not simultaneous model-ranking proof'))
    model_df = pd.DataFrame(models)
    sol_df = pd.DataFrame(sol)
    write(model_df, 'model_pareto_common_tasks')
    write(sol_df, 'sol_pairwise_common_tasks')

    # Correctness is compared within the SAME task × configuration × arm replicate set, so task/model mix is fixed.
    outcome_obs, outcome_summary = [], []
    for b in ['BixBench50', 'CompBio']:
        x = s[(s.benchmark == b) & s.primary_endpoint]
        for (task, cfg, e), q in x.groupby(['task', 'cfg', 'env']):
            if len(q) != 3 or q.endpoint_score.nunique() != 2 or q.input_tokens.count() != 3:
                continue
            good = q[q.endpoint_score == 1].input_tokens.median()
            bad = q[q.endpoint_score == 0].input_tokens.median()
            if good > 0:
                outcome_obs.append(dict(benchmark=b, task=task, cfg=cfg, env=e, cluster=q.cluster.iloc[0],
                                        median_accepted_tokens=good, median_rejected_tokens=bad, ratio=bad / good,
                                        accepted_runs=int((q.endpoint_score == 1).sum()), rejected_runs=int((q.endpoint_score == 0).sum())))
        obs = pd.DataFrame(outcome_obs)
        for e in ENVS:
            for cfg in ['All four primary configurations'] + PRIMARY:
                q = obs[(obs.benchmark == b) & (obs.env == e)]
                if cfg in PRIMARY:
                    q = q[q.cfg == cfg]
                est, lo, hi = ci(q.ratio, q.cluster)
                logs = np.log(q.ratio.values)
                pv = wilcoxon(logs).pvalue if len(logs) and np.any(logs != 0) else None
                outcome_summary.append(dict(benchmark=b, env=e, cfg=cfg, median_rejected_over_accepted_tokens=est,
                                            ci95_low=lo, ci95_high=hi, split_sets=len(q), clusters=q.cluster.nunique(),
                                            wilcoxon_p_unadjusted=pv,
                                            inference='interval crossing one or nonsignificance does not establish equal token use'))
    write(pd.DataFrame(outcome_obs), 'outcome_sibling_observations')
    write(pd.DataFrame(outcome_summary), 'outcome_sibling_summary')

    iwc = []
    for (cfg, e), q in s[(s.benchmark == 'IWC') & s.primary_endpoint].groupby(['cfg', 'env']):
        z = q.dropna(subset=['input_tokens', 'endpoint_score'])
        rho = spearmanr(z.input_tokens, z.endpoint_score).statistic
        iwc.append(dict(cfg=cfg, env=e, runs=len(z), spearman_rho_tokens_agreement=rho,
                        inference='descriptive continuous endpoint; repeated tasks and confounding prevent causal interpretation'))
    write(pd.DataFrame(iwc), 'iwc_continuous_outcome')

    c = nc.galaxy_calls()
    c = c[c.galaxy_server == True].copy()
    c['failed_union'] = c.extract_fail | c.call_status.eq('failed')
    c['returned_ok'] = c.result_status.eq('ok')
    c['operation_class'] = c.tool.map(OPS).fillna('Staging/other')
    c['primary_configuration'] = c.cfg.isin(PRIMARY)
    operations = []
    for pop in ['all_archived_configurations', 'four_primary_configurations']:
        q = c if pop.startswith('all') else c[c.primary_configuration]
        for b in BENCHES + ['All benchmarks']:
            x = q if b == 'All benchmarks' else q[q.benchmark == b]
            chars = x.chars_returned.sum()
            for op, z in x.groupby('tool'):
                operations.append(dict(population=pop, benchmark=b, operation=op, calls=len(z),
                                       failed_calls=int(z.failed_union.sum()), failed_percent=100 * z.failed_union.mean(),
                                       returned_ok=int(z.returned_ok.sum()), returned_ok_percent=100 * z.returned_ok.mean(),
                                       returned_characters=int(z.chars_returned.sum()), character_share_percent=100 * z.chars_returned.sum() / chars,
                                       call_share_percent=100 * len(z) / len(x)))
    opdf = pd.DataFrame(operations)
    write(opdf, 'operation_volume')
    c[['benchmark', 'task', 'run_id', 'cfg', 'replicate', 'line', 'tool', 'tool_id_full', 'result_status', 'call_status',
       'failed_union', 'returned_ok', 'chars_returned', 'operation_class', 'primary_configuration', 'job_failure_phases',
       'outage_sig_linked', 'n_jobs', 'has_error_text']].to_csv(OUT / 'token_call_observations.csv.gz', index=False)
    udt = c[c.tool == 'run_galaxy_udt_and_wait'].copy()
    first_udt = udt.sort_values('call_index_in_run').groupby(['benchmark', 'task', 'run_id']).head(1).index
    udt['first_udt_call_in_run'] = udt.index.isin(first_udt)
    udt['probe_id_indicator'] = udt.tool_id_full.fillna('').str.contains(r'probe|preflight', case=False, regex=True)
    diagrx = r'(?:tool_)?std(?:err|out): *[^|\s]|Traceback'
    udt['diagnostic_indicator_excerpt'] = udt.error_excerpt.fillna('').str.contains(diagrx, regex=True)
    udt['preexecution_phase_recorded'] = udt.job_failure_phases.fillna('').str.contains('pre_execution_or_command_rendering')
    udt_rows = []
    for pop in ['all_archived_configurations', 'four_primary_configurations']:
        qq = udt if pop.startswith('all') else udt[udt.primary_configuration]
        for b in ['BixBench50', 'CompBio']:
            for cfg in ['All configurations in population'] + list(qq.cfg.unique()):
                z = qq[qq.benchmark == b]
                if cfg != 'All configurations in population':
                    z = z[z.cfg == cfg]
                if z.empty:
                    continue
                f = z[z.any_job_error == True]
                udt_rows.append(dict(population=pop, benchmark=b, cfg=cfg, calls=len(z), ok_calls=int(z.returned_ok.sum()),
                                     percent_ok=100 * z.returned_ok.mean(), failed_union=int(z.failed_union.sum()),
                                     calls_recording_job_error=len(f), job_error_no_diagnostic_indicator_excerpt=int((~f.diagnostic_indicator_excerpt).sum()),
                                     preexecution_phase_calls=int(z.preexecution_phase_recorded.sum()), probe_id_calls=int(z.probe_id_indicator.sum()),
                                     probe_id_runs=z[z.probe_id_indicator].groupby(['task', 'run_id']).ngroups,
                                     first_udt_call_in_run=int(z.first_udt_call_in_run.sum()),
                                     first_udt_call_in_run_ok=int(z[z.first_udt_call_in_run].returned_ok.sum()),
                                     first_use_of_tool_id_calls=int((z.prior_same_tool_calls_base == 0).sum()),
                                     first_use_of_tool_id_ok=int(z[z.prior_same_tool_calls_base == 0].returned_ok.sum()),
                                     linked_outage_signature_calls=int(z.outage_sig_linked.sum())))
    write(pd.DataFrame(udt_rows), 'udt_outcomes')
    write(udt.groupby(['benchmark', 'cfg', 'result_status'], dropna=False).size().rename('calls').reset_index(), 'udt_status_distribution')
    # Mutually exclusive call outcomes for the primary configurations.
    err = udt.any_job_error.eq(True)
    udt['call_outcome'] = np.select([udt.returned_ok, err & udt.diagnostic_indicator_excerpt, err],
                                    ['Returned ok', 'Job error with diagnostic text', 'Job error without diagnostic text'],
                                    default='Other non-ok return')
    breakdown = udt[udt.primary_configuration].groupby(['benchmark', 'call_outcome']).size().rename('calls').reset_index()
    breakdown['denominator'] = breakdown.groupby('benchmark').calls.transform('sum')
    breakdown['percent'] = 100 * breakdown.calls / breakdown.denominator
    write(breakdown, 'udt_call_breakdown')
    trajectory = nc.od(7, 'b_accuracy_by_udt_trajectory')
    write(trajectory, 'udt_trajectory_acceptance_archived')
    request_rows = nc.fd()['fig3c']
    write(pd.DataFrame([dict(benchmark=r['benchmark'], cfg=r['config'], requesting_runs=r['requesting'][0],
                             galaxy_runs=r['requesting'][1], percent_requesting=100 * r['requesting'][0] / r['requesting'][1])
                        for r in request_rows if r['benchmark'] in ['BixBench50', 'CompBio']]), 'udt_requests')

    f = nc.galaxy_failures()
    f['primary_configuration'] = f.cfg.isin(PRIMARY)
    fc = []
    for pop in ['all_archived_configurations', 'four_primary_configurations']:
        q = f if pop.startswith('all') else f[f.primary_configuration]
        fc.append(q.groupby(['benchmark', 'failure_class', 'a1_subclass'], dropna=False).size().rename('calls').reset_index().assign(population=pop))
    fail_df = pd.concat(fc, ignore_index=True)
    fail_df['failure_stage'] = fail_df.failure_class.str[0].map(
        {'A': 'Request rejected before a job ran', 'B': 'Job failed during execution'}).fillna('Other exception')
    fail_df = fail_df[['population', 'benchmark', 'failure_stage', 'failure_class', 'a1_subclass', 'calls']]
    write(fail_df, 'failure_classes')

    # Trace-level friction recorded by the archive scan of the primary Galaxy traces (manuscript_material build_data.py).
    scan = nc.fd()['scan']
    friction = []
    for b in BENCHES:
        friction.append(dict(benchmark=b, measure='Inspected tools never run in the same run', count=scan['inspected_never_run'][b],
                             denominator=scan['inspected'][b], unit='distinct tool inspected within a traced Galaxy run'))
        friction.append(dict(benchmark=b, measure='Median tool searches per run', count=scan['searches'][b]['median'],
                             denominator=scan['codex_galaxy_runs'][b], unit='traced Galaxy run'))
    for b in ['BixBench50', 'CompBio']:
        friction.append(dict(benchmark=b, measure='Runs with probe or preflight-named calls', count=scan['probe'][f'{b}|runs'],
                             denominator=scan['codex_galaxy_runs'][b], unit='traced Galaxy run'))
    udt_phase = {k: v for k, v in scan['failed_phase'].items() if k.startswith('udt|')}
    friction.append(dict(benchmark='All benchmarks', measure='UDT job failures before execution without diagnostic text',
                         count=udt_phase.get('udt|pre_execution_or_command_rendering|no_text', 0), denominator=sum(udt_phase.values()),
                         unit='failed UDT job'))
    after = scan['after_notext']
    identical = after['identical|failed'] + after['identical|other']
    friction.append(dict(benchmark='All benchmarks', measure='Identical resubmission after a failed job without diagnostic text',
                         count=identical, denominator=sum(after.values()), unit='next call after a failed job without diagnostic text'))
    friction.append(dict(benchmark='All benchmarks', measure='Identical resubmissions that failed again',
                         count=after['identical|failed'], denominator=identical, unit='identical resubmission'))
    friction = pd.DataFrame(friction)
    friction['percent'] = 100 * friction['count'] / friction.denominator
    friction.loc[friction.measure.eq('Median tool searches per run'), 'percent'] = np.nan
    write(friction, 'interface_friction')
    actions = c[c.primary_configuration].groupby(['benchmark', 'task', 'cfg', 'replicate']).size().rename('galaxy_interface_calls').reset_index()
    action_runs = s[(s.env == 'galaxy') & s.model_primary & s.has_trace].merge(actions, on=['benchmark', 'task', 'cfg', 'replicate'], how='left')
    action_runs['actions'] = action_runs.galaxy_interface_calls + action_runs.n_shell
    write(action_runs, 'actions_by_run')
    associations = []
    for b, x in action_runs.groupby('benchmark'):
        z = x.dropna(subset=['actions', 'input_tokens'])
        associations.append(dict(benchmark=b, runs=len(z), rho=spearmanr(z.actions, z.input_tokens).statistic,
                                 median_actions=z.actions.median(),
                                 inference='association; tokens are not attributable to individual API calls'))
    write(pd.DataFrame(associations), 'actions_association')

    result = dict(
        scope=dict(primary_configurations=PRIMARY, astra_excluded=True, superseded_harness_excluded_from_primary=True,
                   iwc_primary_tasks=9, iwc_archive_token_tasks=10, bootstrap_resamples=BOOT, seed=SEED,
                   token_definition='Recorded cumulative input includes cached context rereads; uncached=input-cached; not total cost.',
                   primary_arm_measure='Ratio of total Galaxy to total code tokens over eligible paired cells (aggregate consumption); '
                                       'the median of within-cell ratios (typical task) is a secondary measure.',
                   cluster_definition='BixBench source capsule; CompBio and IWC task',
                   pareto_definition='On common complete tasks: no other configuration has >=mean endpoint and <=median single-run input, with one strict improvement.',
                   caveat='Exploratory retrospective comparisons; unequal prompts, budgets and host/container policy; incomplete campaign/subagent usage.'),
        arm_total_ratios=records(total_df), paired_arm_ratios=records(ratio_df), model_pareto=records(model_df), sol_pairwise=records(sol_df),
        failure_classes=records(fail_df), interface_friction=records(friction), udt_call_breakdown=records(breakdown),
        outcome_sibling=outcome_summary, actions_association=associations,
        operations=records(opdf), udt_outcomes=udt_rows,
        discovery_archive=nc.fd()['scan'].get('inspected', {}),
        discovery_never_run_archive=nc.fd()['scan'].get('inspected_never_run', {}),
        search_counts_archive=nc.fd()['scan'].get('searches', {}),
        archive_call_count=len(c), archive_failed_union_count=int(c.failed_union.sum()),
        qualification='No intervention was tested; no personal attribution or before/after improvement established by this archive.')
    (OUT / 'token_results.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'primary_total_ratios': records(total_df[(total_df.task_scope == 'primary_endpoint') &
                                                               (total_df.token_kind == 'input_tokens')]),
                      'primary_ratios': records(ratio_df[(ratio_df.cfg == 'All four primary configurations') &
                                                        (ratio_df.task_scope == 'primary_endpoint')]),
                      'common_task_model_points': records(model_df[model_df.token_kind == 'input_tokens']),
                      'calls': len(c), 'failures': int(c.failed_union.sum())}, indent=2))


if __name__ == '__main__':
    main()
