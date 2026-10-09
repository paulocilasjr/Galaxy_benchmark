"""Fig. 3: Galaxy provides a structured environment for agent analyses.

Panels:
a, correct runs by task domain, Galaxy against custom code (a run is correct when accepted, not merely completed);
b, how each traced Galaxy run used Galaxy and how it ended: the kinds of job that completed (installed tools, user-defined
   tools (UDTs), both), runs whose jobs all failed and runs that submitted no job, with the share of runs correct and the
   exact number of runs per row;
c, how often each kind of execution step failed: the share of installed-tool jobs, UDT jobs and shell commands that
   failed, and all execution errors per run; right, the main error types in each channel (the seven-type breakdown is in
   Extended Data);
d, final correctness among runs with execution errors, by the number of errors, with the unadjusted and the
   error-bin-adjusted (exploratory) Galaxy - custom code differences;
e, what the interface's parameter check found for installed-tool requests: matched; a value Galaxy would set or set
   differently (blocked before the job, or after it ran); a requested value with no recorded counterpart; no comparison;
f, failed Galaxy requests by failure class, grouped into candidate infrastructure improvements (an unvalidated codebook,
   written to figures/fig3_failure_class_codebook.csv), with the runs each group affected.

Extended Data Fig. 3: a, the status of every task (correct runs of three per model and condition); b, the full seven-type
error breakdown by channel; c, final correctness by error bin for each benchmark.

A run is correct when accepted (BixBench-Verified-50, CompBioBench) or at >= 0.99 IWC output agreement. Intervals are
95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks).
P values come from paired cluster randomization tests (200,000 draws), Holm-adjusted within each panel.
Writes figures/fig3.{svg,pdf,png}, fig3_source_data.csv, fig3_failure_class_codebook.csv, ed_fig3.{svg,pdf,png} and
ed_fig3_source_data.csv, and prints the statistics.
"""
# result_evaluation copy of figures/make_fig3.py: scores come from scored_runs.csv (make_scored_runs.py; every run matched to
# the public results site, IWC host-read removal included) and every output is written next to this script. The
# manuscript figure set in figures/ is not touched. Changes from the original are marked "result_evaluation:".
import io
import itertools
import json
import os
import sys

import numpy as np
import panel_io  # noqa: E402  (figures/panel_io.py)
import openpyxl
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))   # result_evaluation: two levels up
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
sys.path.insert(0, os.path.join(ROOT, 'manuscript_narrative'))
import style  # noqa: E402  (sets rcParams on import)
from style import plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})
style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition

AN = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis')
GC = os.path.join(ROOT, 'manuscript_narrative', 'derived', 'galaxy_calls')
ERRORS = os.path.join(ROOT, 'manuscript_material', 'on_demand', 'Source_Data_OD_Fig5.xlsx')
ACTIONS = os.path.join(ROOT, 'manuscript_material', 'on_demand', 'Source_Data_OD_Fig6.xlsx')
COMPBIO_AUDIT = os.path.join(ROOT, 'CompBio', 'compBio_overview_audit.json')
OUT = os.path.dirname(os.path.abspath(__file__))   # result_evaluation: write here, not to figures/
FIGS = os.path.join(ROOT, 'figures')               # result_evaluation: unchanged inputs from the manuscript figure set
SCORED = os.path.join(OUT, 'scored_runs.csv')      # result_evaluation: per-run scores matched to the results site
B, SEED, B_PERM = 20000, 20261002, 200000
W, MM = 180.0, 1 / 25.4
CFG = style.CONFIGS
ENVS = style.ENVS                                    # custom code first, always
CODE, GAL = ENVS
BENCH = style.BENCH
BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}       # as in Fig. 2
TRACE_MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
               'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
               'codex_deepseek_v4_pro': 'DeepSeek V4 Pro'}     # the superseded Claude Code harness is excluded
KEY = ['benchmark', 'task', 'cfg', 'env', 'replicate']
# Panel a: CompBioBench task domains as labelled by the benchmark; two small domains are merged.
DOMAIN = {'Population Genetics': 'Population genetics', 'Machine Learning': 'Machine learning',
          'Spatial': 'Spatial and structure', 'Structure': 'Spatial and structure'}
# Panel b: what each traced Galaxy run did through the agent interface, from the states of its jobs.
ROUTES = [('I', 'Installed tools only', style.GALAXY), ('IU', 'Installed tools and UDTs', '#56B4E9'),
          ('U', 'UDTs only', '#CFE3F1'), ('F', 'Jobs submitted, none completed', '#999999'),
          ('', 'No job submitted', style.NEUTRAL_LIGHT)]
# Panel c: error types as classified for On-demand Fig. 5 (error text, exit code and command of every error); the
# figure collapses the seven types into four, and Extended Data shows all seven.
ETYPES = [('Code, parameter or syntax error', '#44BB99'), ('Missing software, package or container', '#BBCC33'),
          ('File, path or input format', '#EEDD88'), ('Time or memory limit', '#FFAABB'),
          ('Network or download', '#99DDFF'), ('Galaxy job never started', '#AAAA00'),
          ('No or unclassified message', style.NEUTRAL_LIGHT)]
EGROUPS = [('Code, parameter or syntax', ('Code, parameter or syntax error',), '#44BB99'),
           ('Missing software or package', ('Missing software, package or container',), '#BBCC33'),
           ('Galaxy job never started', ('Galaxy job never started',), '#AAAA00'),
           ('Other or unclassified', ('File, path or input format', 'Time or memory limit', 'Network or download',
                                      'No or unclassified message'), style.NEUTRAL_LIGHT)]
CHANNELS = [('galaxy_tool', 'Installed-tool jobs', GAL), ('galaxy_udt', 'UDT jobs', GAL),
            ('galaxy_shell', 'Shell commands', GAL), ('code_shell', 'Shell commands', CODE)]
# Panel d: final correctness by the number of execution errors; the adjusted comparison weights these bins.
ERROR_BINS = [(0, 0, '0'), (1, 2, '1–2'), (3, 5, '3–5'), (6, 10, '6–10'), (11, 10 ** 9, '>10')]
B_CURVE = 2000           # cluster-bootstrap resamples for the logistic slopes (Source Data; not drawn)
# Panel e: the interface's comparison of requested parameters with those Galaxy validated or recorded.
CHECKS = [('matched', 'Matched', style.NEUTRAL_DARK),
          ('diff_blocked', 'Different value, blocked before the job', style.OI_GREEN),
          ('diff_ran', 'Different value, job ran', style.OI_PURPLE),
          ('unrecorded', 'Requested value not recorded (default or format)', '#BBBBBB'),
          ('none', 'No comparison (no parameters or no result)', '#E8E8E8')]
# Panel f: classes of failed Galaxy requests (the archive's ordered rules, four primary configurations), grouped by
# the change most likely to prevent them. The grouping is ours and has not been validated against a sample.
FIXES = [('API design', ('A1', 'A3', 'A5'),
          'tool forms that need history context; nested parameter keys; dataset and job IDs'),
         ('Error diagnostics', ('B2',), 'jobs that failed without any diagnostic message'),
         ('Tool and parameter descriptions', ('A4', 'A2'), 'invalid parameter values or datatypes; tool IDs not found'),
         ('Datatypes and uploads', ('A7', 'B4'), 'upload or datatype registry; input format, compression or index'),
         ('UDT support', ('A6', 'B1'), 'UDT definition schema; missing dependency in the UDT container'),
         ('Server capacity', ('A8', 'B5'), 'server, transport or rate limits; job memory or resources'),
         ('Tool runtime error (not attributable)', ('B3',), 'tool wrote an error; agent input or tool, not attributable'),
         ('Other or unclassified', ('X', 'Z'), 'other transport or tool exceptions; unclassified')]
UNRESOLVED = ('Tool runtime error (not attributable)', 'Other or unclassified')
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- statistics
def holm(p):
    p = np.asarray(p, float)
    order, adj, run = np.argsort(p), np.empty(len(p)), 0.0
    for i, k in enumerate(order):
        run = max(run, (len(p) - i) * p[k])
        adj[k] = min(1.0, run)
    return adj


def signflip_p(cluster_diffs):
    d = np.asarray(cluster_diffs, float)
    if len(d) <= 16:  # enumerate every sign vector exactly
        signs = np.array(list(itertools.product([-1.0, 1.0], repeat=len(d))))
        return float(np.mean(np.abs(signs @ d) >= abs(d.sum()) - 1e-12))
    hits = 0
    for _ in range(B_PERM // 20000):
        null = rng.choice([-1.0, 1.0], size=(20000, len(d))) @ d
        hits += np.sum(np.abs(null) >= abs(d.sum()) - 1e-12)
    return (1 + hits) / (B_PERM + 1)


def boot_means(frames, group_cols, value='score'):
    point, num, den = None, 0.0, 0.0
    for _, d in frames.groupby('benchmark'):
        s = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='sum').fillna(0)
        n = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='count').fillna(0)
        wts = rng.multinomial(len(s), np.full(len(s), 1 / len(s)), size=B)
        num = num + wts @ s.values
        den = den + wts @ n.values
        point = (s.sum(), n.sum()) if point is None else (point[0] + s.sum(), point[1] + n.sum())
    est = point[0] / point[1]
    return est, pd.DataFrame(num / den, columns=est.index)


def boot_ratio(frame, num_col, den_col):
    """Ratio of sums with cluster-bootstrap interval; clusters resampled within each benchmark."""
    num, den, pn, pd_ = 0.0, 0.0, 0.0, 0.0
    for _, d in frame.groupby('benchmark'):
        g = d.groupby('cluster')[[num_col, den_col]].sum()
        wts = rng.multinomial(len(g), np.full(len(g), 1 / len(g)), size=B)
        num, den = num + wts @ g[num_col].values, den + wts @ g[den_col].values
        pn, pd_ = pn + g[num_col].sum(), pd_ + g[den_col].sum()
    draws = num / den
    return pn / pd_, np.percentile(draws, 2.5), np.percentile(draws, 97.5)


# ---------------------------------------------------------------- data
def load_runs():
    r = pd.read_csv(SCORED)
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    return r


def load_calls():
    c = pd.read_csv(os.path.join(GC, 'calls.csv.gz'), low_memory=False,
                    usecols=['benchmark', 'task', 'model', 'replicate', 'run_id', 'line', 'tool', 'galaxy_server',
                             'n_jobs', 'job_states', 'prov_status', 'prov_stage', 'n_substituted', 'tool_id_base',
                             'tool_id_full'])
    c = c[c.model.isin(TRACE_MODEL) & c.galaxy_server].assign(cfg=lambda x: x.model.map(TRACE_MODEL))
    cov = pd.read_csv(os.path.join(GC, 'run_coverage.csv'))
    cov = cov[cov.model.isin(TRACE_MODEL)].assign(cfg=lambda x: x.model.map(TRACE_MODEL))
    return c, cov[['benchmark', 'task', 'cfg', 'replicate']].drop_duplicates()


def read_sheet(path, name):
    ws = openpyxl.load_workbook(path, read_only=True)[name]
    rows = list(ws.iter_rows(values_only=True))
    e = pd.DataFrame(rows[1:], columns=rows[0])
    extra = os.path.join(OUT, f'wf003_{name}.csv')       # result_evaluation: host-read removal runs (make_wf003_errors.py)
    if name in ('abc_runs', 'abc_every_error') and os.path.exists(extra):
        e = pd.concat([e, pd.read_csv(extra)], ignore_index=True)
    e = e[e.model_configuration != 'DeepSeek V4 Pro (Claude Code, superseded)']
    return e.assign(benchmark=e.benchmark.map({'BixBench-Verified-50': 'BixBench50', 'BixBench50': 'BixBench50',
                                               'CompBioBench': 'CompBio', 'IWC': 'IWC'}),
                    cfg=e.model_configuration.replace({'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro'}),
                    env=e.execution_condition.map({'Galaxy condition': GAL, 'Open-ended code condition': CODE}))


def load_errors(r):
    """Execution errors per run (failed shell commands, not counting a silent exit code 1, + Galaxy jobs in the error
    state), from On-demand Fig. 5, and the run's shell commands, from On-demand Fig. 6."""
    e = read_sheet(ERRORS, 'abc_runs')
    e = e.assign(errors=e.failed_shell_commands.fillna(0) + e.galaxy_jobs_in_error_state.fillna(0))
    a = read_sheet(ACTIONS, 'abf_runs')[KEY + ['shell_commands']]
    m = r.merge(e[KEY + ['errors', 'failed_shell_commands', 'galaxy_jobs_in_error_state']], on=KEY, how='inner')
    m = m.merge(a, on=KEY, how='left')
    m['bin'] = pd.cut(m.errors, [b[0] - 0.5 for b in ERROR_BINS] + [1e12], labels=[b[2] for b in ERROR_BINS])
    return m


# ---------------------------------------------------------------- panels: statistics
def panel_a(r):
    """Runs correct by task domain and condition: CompBioBench domains, BixBench-Verified-50 and IWC."""
    dom = {t['task']: DOMAIN.get(t['domain'], t['domain']) for t in json.load(open(COMPBIO_AUDIT))['tasks']}
    d = r.assign(domain=np.where(r.benchmark == 'CompBio', r.task.map(dom), r.benchmark.map(BENCH_NAME)))
    assert d.domain.notna().all(), 'every CompBioBench task needs a domain'
    rows, tests = [], []
    for name, g in d.groupby('domain'):                 # each domain lies within one benchmark
        est, draws = boot_means(g, ['env'], value='ok')
        for env in ENVS:
            rows.append(dict(domain=name, env=env, value=est[env] * 100, lo=np.percentile(draws[env], 2.5) * 100,
                             hi=np.percentile(draws[env], 97.5) * 100, tasks=g.task.nunique()))
        cell = g.groupby(['cluster', 'task', 'cfg', 'env']).ok.mean().unstack('env')
        diff = (cell[GAL] - cell[CODE]).groupby(level='cluster').sum()
        tests.append(dict(domain=name, diff=100 * (g[g.env == GAL].ok.mean() - g[g.env == CODE].ok.mean()),
                          p=signflip_p(diff.values)))
    tests = pd.DataFrame(tests)
    tests['p_holm'] = holm(tests.p)
    return pd.DataFrame(rows), tests, d[['benchmark', 'task', 'domain']].drop_duplicates()


def run_jobs(calls):
    """Per traced run: interface-submitted jobs and jobs in the error state, for installed tools and for UDTs."""
    k = ['benchmark', 'task', 'cfg', 'replicate']
    j = calls[calls.tool.isin(['run_galaxy_tool_and_wait', 'run_galaxy_udt_and_wait'])].copy()
    states = j.job_states.fillna('')
    j['jobs'] = j.n_jobs.fillna(0)
    j['ok_jobs'] = states.str.count(r'(?:^|;)ok(?=;|$)')
    j['err_jobs'] = states.str.count(r'(?:^|;)error(?=;|$)')
    j['kind'] = np.where(j.tool == 'run_galaxy_tool_and_wait', 'tool', 'udt')
    out = j.groupby(k + ['kind'])[['jobs', 'ok_jobs', 'err_jobs']].sum().unstack('kind', fill_value=0)
    out.columns = [f'{a}_{b}' for a, b in out.columns]
    return out


def panel_b(calls, traced, r):
    """Route of each traced Galaxy run, from its completed jobs, with the share of runs correct per row."""
    k = ['benchmark', 'task', 'cfg', 'replicate']
    jobs = run_jobs(calls)
    m = traced.join(jobs, on=k).fillna(0)
    it, ut = m.ok_jobs_tool > 0, m.ok_jobs_udt > 0
    any_job = (m.jobs_tool + m.jobs_udt) > 0
    m['route'] = np.select([it & ut, it, ut, any_job], ['IU', 'I', 'U', 'F'], '')
    m = m[k + ['route']].copy()
    m = m.merge(r[r.env == GAL][k + ['ok']], on=k, how='left')         # unscored IWC task: no grade
    tab = m.groupby(['benchmark', 'cfg', 'route']).size().unstack('route', fill_value=0)
    tab = tab.reindex(columns=[c for c, _, _ in ROUTES], fill_value=0)
    acc = m.groupby(['benchmark', 'cfg']).ok.agg(['mean', 'count'])
    by_route = m.groupby(['benchmark', 'route']).ok.agg(['mean', 'count'])
    return tab, acc, by_route


def panel_c(calls, m):
    """How often each kind of execution step failed (share of steps, ratio of sums with cluster-bootstrap intervals),
    all execution errors per run, and the error types per channel."""
    jobs = run_jobs(calls)
    k = ['benchmark', 'task', 'cfg', 'replicate']
    g = m[m.env == GAL][k + ['cluster', 'shell_commands', 'failed_shell_commands']].join(jobs, on=k).fillna(0)
    c_ = m[m.env == CODE][k + ['cluster', 'shell_commands', 'failed_shell_commands']].fillna(0)
    rates = []
    for code, frame, num, den in (('galaxy_tool', g, 'err_jobs_tool', 'jobs_tool'),
                                  ('galaxy_udt', g, 'err_jobs_udt', 'jobs_udt'),
                                  ('galaxy_shell', g, 'failed_shell_commands', 'shell_commands'),
                                  ('code_shell', c_, 'failed_shell_commands', 'shell_commands')):
        est, lo, hi = boot_ratio(frame, num, den)
        rates.append(dict(channel=code, value=100 * est, lo=100 * lo, hi=100 * hi, failed=int(frame[num].sum()),
                          steps=int(frame[den].sum())))
    burden = []
    for env in ENVS:
        e = m[m.env == env].assign(one=1)
        est, lo, hi = boot_ratio(e, 'errors', 'one')
        burden.append(dict(env=env, value=est, lo=lo, hi=hi, errors=int(e.errors.sum()), runs=len(e)))
    e = read_sheet(ERRORS, 'abc_every_error')
    udt_ids = set(calls[calls.tool == 'run_galaxy_udt_and_wait'].tool_id_base.dropna()) | \
        set(calls[calls.tool == 'run_galaxy_udt_and_wait'].tool_id_full.dropna())
    is_job = e.channel == 'Galaxy job'
    e['where'] = np.select([is_job & e.tool.isin(udt_ids), is_job, e.env == GAL],
                           ['galaxy_udt', 'galaxy_tool', 'galaxy_shell'], 'code_shell')
    tab = e.groupby(['where', 'error_type']).size().unstack('error_type', fill_value=0)
    tab = tab.reindex(index=[c for c, _, _ in CHANNELS], columns=[t for t, _ in ETYPES], fill_value=0)
    return pd.DataFrame(rates), pd.DataFrame(burden), tab


def stratified_difference(sG, nG, sC, nC, weights):
    return np.sum(weights * (sG / nG - sC / nC), axis=-1)


def recovery_test(e, bins):
    """Weighted Galaxy - custom code difference over error bins, with a cluster condition-swap randomization test."""
    agg = e.groupby(['cluster', 'env', 'bin'], observed=True).ok.agg(['sum', 'count']).unstack(['env', 'bin'])
    agg = agg.reindex(columns=pd.MultiIndex.from_product([['sum', 'count'], ENVS, bins]), fill_value=0).fillna(0)
    sG, nG = agg['sum'][GAL].values, agg['count'][GAL].values
    sC, nC = agg['sum'][CODE].values, agg['count'][CODE].values
    wts = (nG.sum(0) + nC.sum(0)) / (nG.sum() + nC.sum())
    observed = stratified_difference(sG.sum(0), nG.sum(0), sC.sum(0), nC.sum(0), wts)
    hits = 0
    for _ in range(B_PERM // 20000):
        f = rng.integers(0, 2, size=(20000, len(agg)))[:, :, None]
        g_s, g_n = ((1 - f) * sG + f * sC).sum(1), ((1 - f) * nG + f * nC).sum(1)
        c_s, c_n = (f * sG + (1 - f) * sC).sum(1), (f * nG + (1 - f) * nC).sum(1)
        hits += np.sum(np.abs(stratified_difference(g_s, g_n, c_s, c_n, wts)) >= abs(observed) - 1e-12)
    return observed, (1 + hits) / (B_PERM + 1)


def logistic_fit(x, succ, n, iters=30):
    """Binomial logistic regression of P(correct) on x by iteratively reweighted least squares."""
    X = np.column_stack([np.ones_like(x), x])
    beta = np.array([np.log((succ.sum() + 0.5) / (n.sum() - succ.sum() + 0.5)), 0.0])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ beta)))
        w = n * p * (1 - p)
        z = X @ beta + np.divide(succ - n * p, w, out=np.zeros_like(w), where=w > 0)
        step = np.linalg.solve(X.T @ (X * w[:, None]) + 1e-9 * np.eye(2), X.T @ (w * z))
        if np.allclose(step, beta, atol=1e-10):
            break
        beta = step
    return beta


def recovery_slopes(m):
    """Logistic slope of runs ending correct on ln(1 + errors), per condition, with cluster-bootstrap intervals."""
    agg = m.groupby(['benchmark', 'cluster', 'env', 'errors']).ok.agg(['sum', 'count']).reset_index()
    coef = {}
    for env in ENVS:
        d = agg[agg.env == env]
        x, succ, n = np.log1p(d.errors.values.astype(float)), d['sum'].values.astype(float), d['count'].values.astype(float)
        beta = logistic_fit(x, succ, n)
        clusters = d.cluster.values
        weights = np.ones((B_CURVE, len(d)))
        for bm in d.benchmark.unique():
            names = np.unique(clusters[d.benchmark.values == bm])
            draw = rng.multinomial(len(names), np.full(len(names), 1 / len(names)), size=B_CURVE)
            col = {c: i for i, c in enumerate(names)}
            idx = np.array([col[c] for c in clusters[d.benchmark.values == bm]])
            weights[:, d.benchmark.values == bm] = draw[:, idx]
        betas = np.array([logistic_fit(x, succ * weights[k], n * weights[k]) for k in range(B_CURVE)])
        coef[env] = dict(intercept=beta[0], slope=beta[1], slope_lo=np.percentile(betas[:, 1], 2.5),
                         slope_hi=np.percentile(betas[:, 1], 97.5), runs=int(n.sum()))
    return coef


def panel_d(m):
    """Galaxy - custom code among runs with errors: unadjusted, and averaged over error bins (chosen after inspecting
    the bins, so exploratory); per benchmark as well."""
    e = m[m.errors > 0]
    adjusted = recovery_test(e, [b[2] for b in ERROR_BINS[1:]])
    unadjusted = recovery_test(e.assign(bin='any'), ['any'])
    rec = dict(difference=adjusted[0] * 100, p=adjusted[1], unadjusted=unadjusted[0] * 100, p_unadjusted=unadjusted[1],
               runs_with_errors=int(len(e)))
    coef = recovery_slopes(m)
    return rec, coef


def bin_estimates(m, by_benchmark=False):
    """Runs ending correct per error bin and condition, with cluster-bootstrap intervals."""
    rows = []
    groups = [('all', m)] + ([(bm, m[m.benchmark == bm]) for bm in BENCH] if by_benchmark else [])
    for scope, d in groups:
        for env in ENVS:
            for lo_, hi_, lab in ERROR_BINS:
                g = d[(d.env == env) & (d.errors >= lo_) & (d.errors <= hi_)]
                if len(g) < 5:
                    continue
                est, draws = boot_means(g.assign(env_bin='x'), ['env_bin'], value='ok')
                rows.append(dict(scope=scope, env=env, bin=lab, value=100 * est['x'],
                                 lo=100 * np.percentile(draws['x'], 2.5), hi=100 * np.percentile(draws['x'], 97.5),
                                 n=len(g), tasks=g.task.nunique()))
    return pd.DataFrame(rows)


def recovery_by_benchmark(m):
    rows = []
    for bm in BENCH:
        e = m[(m.benchmark == bm) & (m.errors > 0)]
        un = recovery_test(e.assign(bin='any'), ['any'])
        rows.append(dict(benchmark=bm, unadjusted=100 * un[0], p_unadjusted=un[1], runs=len(e)))
    return pd.DataFrame(rows)


def panel_e(calls):
    """Parameter checks on installed-tool requests, by benchmark, and what followed a blocked request."""
    r = calls[calls.tool == 'run_galaxy_tool_and_wait'].copy()
    sub = r.n_substituted.fillna(0) > 0
    mism = r.prov_status == 'mismatch'
    r['check'] = np.select([r.prov_status == 'matched', mism & sub & (r.prov_stage == 'validation'), mism & sub,
                            mism], ['matched', 'diff_blocked', 'diff_ran', 'unrecorded'], 'none')
    tab = pd.crosstab(r.benchmark, r.check).reindex(index=BENCH, columns=[c for c, _, _ in CHECKS], fill_value=0)
    tab.loc['all'] = tab.sum()
    # after a request blocked before the job: did the run later complete a job of the same tool?
    r = r.sort_values(['run_id', 'task', 'line'])
    r['okjob'] = r.job_states.fillna('').str.contains(r'(?:^|;)ok(?=;|$)')
    rows = []
    for _, g in r.groupby(['run_id', 'task'], sort=False):
        g = g.reset_index(drop=True)
        for i in np.flatnonzero((g.prov_status == 'mismatch') & (g.prov_stage == 'validation')):
            later = g.iloc[i + 1:]
            later = later[later.tool_id_base == g.tool_id_base[i]]
            rows.append(dict(kind='diff_blocked' if g.n_substituted.fillna(0)[i] > 0 else 'unrecorded',
                             retried=len(later) > 0, completed=bool(later.okjob.any()),
                             matched=bool((later.okjob & (later.prov_status == 'matched')).any())))
    follow = pd.DataFrame(rows).groupby('kind').agg(requests=('retried', 'size'), retried=('retried', 'mean'),
                                                     completed=('completed', 'mean'), matched=('matched', 'mean'))
    return tab, follow


def panel_f():
    """Failed Galaxy requests and the runs they affected, by candidate improvement (archive classifier)."""
    import narrative_common as nc
    f = nc.galaxy_failures()
    f = f[f.cfg.isin(CFG)].assign(code=lambda x: x.failure_class.str.split(' ').str[0],
                                  run=lambda x: x.run_id + '|' + x.task)
    # 6,904 in runs that were not rerun plus 237 in the 53 reviewed reruns (the replaced runs had 450; total was 7,354)
    assert len(f) == 7141, 'failed requests of the four primary configurations'
    rows, book = [], []
    for name, codes, desc in FIXES:
        g = f[f.code.isin(codes)]
        rows.append(dict(fix=name, classes='+'.join(codes), description=desc, requests=len(g), runs=g.run.nunique()))
        for code in codes:
            cls = f[f.code == code].failure_class.iloc[0]
            book.append(dict(failure_class=cls, candidate_improvement=name, requests=int((f.code == code).sum()),
                             runs=f[f.code == code].run.nunique(), validated='no'))
    tab = pd.DataFrame(rows)
    assert tab.requests.sum() == len(f), 'every failure class must map to one improvement'
    tab['pct'] = 100 * tab.requests / tab.requests.sum()
    comparable = tab[~tab.fix.isin(UNRESOLVED)].sort_values('requests', ascending=False)
    tab = pd.concat([comparable, tab[tab.fix.isin(UNRESOLVED)]], ignore_index=True)
    return tab, pd.DataFrame(book), f.run.nunique()


def task_status(r, domains):
    """Extended Data: correct runs of three for every task, model and condition."""
    s = r.groupby(['benchmark', 'task', 'cfg', 'env']).ok.sum().unstack(['cfg', 'env'])
    s = s.reindex(columns=pd.MultiIndex.from_product([CFG, ENVS]))
    s.columns = [f'{c}|{e}' for c, e in s.columns]
    cells = list(s.columns)
    s = s.join(domains.set_index(['benchmark', 'task']).domain)
    s['mean'] = s[cells].mean(axis=1)
    order = {'BixBench-Verified-50': 0, 'IWC': 99}
    s['dom_order'] = s.domain.map(lambda d: order.get(d, 1))
    s = s.reset_index().sort_values(['dom_order', 'domain', 'mean'], ascending=[True, True, False])
    return s


# ---------------------------------------------------------------- drawing helpers
def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


def fmt_p(p):
    if p < 0.001:
        return r'$\mathit{P}$ < 0.001'
    return rf'$\mathit{{P}}$ = {p:.2f}' if p >= 0.01 else rf'$\mathit{{P}}$ = {p:.3f}'


def pct_text(v):
    return '<1' if 0 < v < 0.5 else f'{v:.0f}'


def stacked_rows(ax, ypos, shares, colors, width_mm, bar_h=0.72, dark=(), last_right=False, lead=0.42):
    """Horizontal 100% bars with every share printed: inside its segment when it fits; otherwise above the bar with a
    short leader (or, for the last segment when last_right is set, just right of the bar)."""
    for y, row in zip(ypos, shares):
        left, out = 0.0, []
        last = max(i for i, v in enumerate(row) if v > 0)
        for i, (v, c) in enumerate(zip(row, colors)):
            if v <= 0:
                continue
            ax.barh(y, v, left=left, height=bar_h, color=c, ec='white', lw=0.4, zorder=3)
            txt = pct_text(v)
            if v / 100 * width_mm >= 1.25 * len(txt) + 0.6:          # fits inside at 5 pt
                ax.text(left + v / 2, y, txt, ha='center', va='center', fontsize=5,
                        color='white' if c in dark else style.INK, zorder=4)
            elif i == last and last_right:
                ax.text(101.2, y, txt, ha='left', va='center', fontsize=5, color=style.INK, zorder=4, clip_on=False)
            else:
                out.append([left + v / 2, txt, left + v / 2])
            left += v
        for a_, b_ in zip(out, out[1:]):                    # neighbouring outside labels at least 5 points apart
            if b_[0] - a_[0] < 5.0:
                b_[0] = a_[0] + 5.0
        for xc, txt, seg in out:
            edge, tip = y - bar_h / 2, y - bar_h / 2 - lead     # y axis inverted: smaller y is higher
            ax.plot([seg, xc], [edge, tip], color=style.INK2, lw=0.4, zorder=4, clip_on=False)
            ax.text(xc, tip - 0.04, txt, ha='center', va='bottom', fontsize=5, color=style.INK, zorder=4,
                    clip_on=False)


def cond_marker(ax, x, y, env, ms=3.0, **kw):
    ax.plot(x, y, ls='', marker=style.ENV_MARKER[env], ms=ms, mfc=style.ENV_COLOR[env], mec='white', mew=0.35, **kw)


# ---------------------------------------------------------------- panels: drawing
def draw_a(fig, H, tab, tests):
    label(fig, 0, 0, 'a', 'Correct runs by domain', H)
    ax = axes_mm(fig, 33.0, 12.0, 22.0, 41.0, H)
    gal = tab[tab.env == GAL].set_index('domain')
    comp = [d for d in gal.value.sort_values(ascending=False).index if d not in BENCH_NAME.values()]
    order = comp + ['BixBench-Verified-50', 'IWC']
    ys = {d: i + (0.6 if d in ('BixBench-Verified-50', 'IWC') else 0) for i, d in enumerate(order)}
    for k, env in enumerate(ENVS):
        t = tab[tab.env == env].set_index('domain')
        for d in order:
            y = ys[d] + (k - 0.5) * 0.34
            ax.plot([t.loc[d, 'lo'], t.loc[d, 'hi']], [y, y], color=style.ENV_COLOR[env], lw=0.7, zorder=3,
                    clip_on=False)
            cond_marker(ax, t.loc[d, 'value'], y, env, ms=2.9, zorder=4, clip_on=False)
    ax.set_ylim(max(ys.values()) + 0.6, -0.6)
    ax.set_yticks([ys[d] for d in order], [f'{d} ({int(gal.loc[d, "tasks"])})' for d in order], fontsize=5.5)
    ax.tick_params(axis='y', length=0)
    ax.axhline(len(comp) - 0.2, color=style.NEUTRAL_MID, lw=0.5, zorder=1)
    ax.set_xlim(25, 104)                                 # room past 100% so markers are not clipped
    ax.set_xticks([25, 50, 75, 100])
    ax.spines['bottom'].set_bounds(25, 100)
    style.grid_x(ax)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Runs correct (%)')
    ax.text(-0.04, -0.75, 'CompBioBench domains (tasks)', transform=blended_transform_factory(ax.transAxes, ax.transData),
            ha='right', va='center', fontsize=5.5, fontweight='bold')
    hand = [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=2.9, mfc=style.ENV_COLOR[e], mec='white', mew=0.35,
                   label=style.ENV_LABEL[e]) for e in ENVS]
    ax.legend(handles=hand, loc='lower left', bbox_to_anchor=(-1.35, 1.07), ncol=2, fontsize=5.3, handletextpad=0.2,
              columnspacing=0.8, borderaxespad=0)
    worst = tests.p_holm.min()
    ax.text(1.0, 1.02, f'no domain differs\n(Holm-adjusted {fmt_p(worst).replace("= ", "≥ ")})',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=5, color=style.INK2, linespacing=1.15)


def draw_b(fig, H, tab, acc):
    label(fig, 62.0, 0, 'b', 'How each Galaxy run used Galaxy, and how it ended', H)
    ax = axes_mm(fig, 92.0, 13.0, 62.0, 40.0, H)
    rows = [(bm, c) for bm in BENCH for c in CFG]
    ypos = [i + 0.45 * BENCH.index(bm) for i, (bm, c) in enumerate(rows)]
    shares = [100 * tab.loc[(bm, c)].values / tab.loc[(bm, c)].sum() for bm, c in rows]
    stacked_rows(ax, ypos, shares, [col for _, _, col in ROUTES], 62.0, dark=(style.GALAXY, '#999999'))
    ax.set_ylim(max(ypos) + 0.6, -0.6)
    ax.set_yticks(ypos, [c for _, c in rows], fontsize=5)
    ax.tick_params(axis='y', length=0)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Galaxy runs (%)')
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    for bm in BENCH:
        ys = [y for y, (b, _) in zip(ypos, rows) if b == bm]
        ax.text(-0.485, np.mean(ys), BENCH_NAME[bm].replace('-Verified-50', '-\nVerified-50'), transform=tr,
                ha='left', va='center', fontsize=5, fontweight='bold', linespacing=1.1)
    ax.text(1.12, -1.05, 'Runs', transform=tr, ha='right', va='center', fontsize=5, color=style.INK2)
    ax.text(1.28, -1.05, 'Correct', transform=tr, ha='right', va='center', fontsize=5, color=style.INK2)
    for y, (bm, c) in zip(ypos, rows):
        n = int(tab.loc[(bm, c)].sum())
        ax.text(1.12, y, f'{n}', transform=tr, ha='right', va='center', fontsize=5)
        a = acc.loc[(bm, c)]
        ax.text(1.28, y, f'{100 * a["mean"]:.0f}%', transform=tr, ha='right', va='center', fontsize=5)
    ax.text(-0.485, np.mean(ypos[-4:]) + 0.9, '(UDTs not\noffered)', transform=tr, ha='left', va='top',
            fontsize=5, color=style.INK2, linespacing=1.1)
    ax.legend(handles=[Patch(fc=col, ec=style.NEUTRAL_MID if col == '#CFE3F1' else col, lw=0.3, label=lab)
                       for _, lab, col in ROUTES], loc='lower left', bbox_to_anchor=(-0.485, 1.015), ncol=3,
              fontsize=5.0, handlelength=0.9, handletextpad=0.3, columnspacing=0.8, labelspacing=0.2, borderaxespad=0)


EPISODE_CHANNEL = {'galaxy_tool': 'Galaxy installed-tool jobs', 'galaxy_udt': 'Galaxy UDT jobs',
                   'galaxy_shell': 'shell (Galaxy runs)', 'code_shell': 'shell (custom code runs)'}


def fixed_later():
    """Share of failed steps later re-run without error in the same run (make_failure_episodes.py)."""
    e = pd.read_csv(os.path.join(OUT, 'failure_episodes.csv'))
    return e.groupby('channel').resolved.agg(['mean', 'size'])


def draw_c(fig, H, y0, rates, burden, tab, fixed=None):
    label(fig, 0, y0, 'c', 'How often execution steps failed, and were fixed later', H)
    ax = axes_mm(fig, 33.0, y0 + 10.0, 26.0, 20.0, H)
    rr = rates.set_index('channel')
    ypos = [0, 1.3, 2.6, 4.1]
    for y, (code, name, env) in zip(ypos, CHANNELS):
        t = rr.loc[code]
        ax.plot([t.lo, t.hi], [y, y], color=style.ENV_COLOR[env], lw=0.8, zorder=3)
        cond_marker(ax, t.value, y, env, ms=3.2, zorder=4)
        ax.text(-0.04, y, f'{name}\n({int(t.steps):,})', transform=blended_transform_factory(ax.transAxes,
                ax.transData), ha='right', va='center', fontsize=5.5, linespacing=1.1)
        ax.text(t.hi + 1.5, y, f'{t.value:.0f}%' if t.value >= 10 else f'{t.value:.1f}%', ha='left', va='center',
                fontsize=5, color=style.INK2)
        if fixed is not None:
            f = fixed.loc[EPISODE_CHANNEL[code]]
            ax.text((62.5 - 33.0) / 26.0 * 60, y, f'{100 * f["mean"]:.0f}%', ha='center', va='center',
                    fontsize=5.5, clip_on=False)
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    ax.text(-1.25, 1.3, 'Galaxy\nruns', transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold',
            linespacing=1.1)
    ax.text(-1.25, 4.1, 'Custom-\ncode runs', transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold',
            linespacing=1.1)
    ax.set_ylim(4.7, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 60)
    ax.set_xticks([0, 20, 40, 60])
    style.grid_x(ax)
    ax.set_xlabel('Steps that failed (%)', labelpad=1.5)
    if fixed is not None:
        ax.text((62.5 - 33.0) / 26.0 * 60, -1.15, 'Fixed\nlater', ha='center', va='center', fontsize=5,
                color=style.INK2, linespacing=1.05, clip_on=False)
    # all execution errors per run
    bx = axes_mm(fig, 33.0, y0 + 38.0, 26.0, 6.0, H)
    bb = burden.set_index('env')
    for y, env in enumerate([GAL, CODE]):
        t = bb.loc[env]
        bx.plot([t.lo, t.hi], [y, y], color=style.ENV_COLOR[env], lw=0.8, zorder=3)
        cond_marker(bx, t.value, y, env, ms=3.2, zorder=4)
        bx.text(-0.04, y, f'{style.ENV_LABEL[env].replace("Custom code", "Custom-code")} runs', transform=blended_transform_factory(bx.transAxes, bx.transData),
                ha='right', va='center', fontsize=5.5)
        bx.text(t.hi + 0.12, y, f'{t.value:.1f}', ha='left', va='center', fontsize=5, color=style.INK2)
    bx.set_ylim(1.6, -0.6)
    bx.set_yticks([])
    bx.spines['left'].set_visible(False)
    bx.set_xlim(0, 5)
    bx.set_xticks([0, 1, 2, 3, 4, 5])
    style.grid_x(bx)
    bx.set_xlabel('All execution errors per run', labelpad=1.5)
    # error types per channel, four groups
    cx = axes_mm(fig, 66.0, y0 + 10.0, 31.0, 20.0, H)
    shares = []
    for code, _, _ in CHANNELS:
        row = tab.loc[code]
        shares.append([100 * row[list(types)].sum() / row.sum() for _, types, _ in EGROUPS])
    stacked_rows(cx, ypos, shares, [c for _, _, c in EGROUPS], 31.0, bar_h=0.66, lead=0.30)
    cx.set_ylim(4.7, -0.6)
    cx.set_yticks([])
    cx.spines['left'].set_visible(False)
    cx.set_xlim(0, 100)
    cx.set_xticks([0, 50, 100])
    cx.set_xlabel('Error types (%)', labelpad=1.5)
    cx.legend(handles=[Patch(fc=c, label=n) for n, _, c in EGROUPS], loc='upper left', bbox_to_anchor=(0.0, -0.40),
              ncol=1, fontsize=5, handlelength=0.9, handletextpad=0.3, labelspacing=0.2, borderaxespad=0)


def draw_d(fig, H, y0, rec, bins_):
    label(fig, 103.0, y0, 'd', 'Final correctness among runs with execution errors', H)
    ax = axes_mm(fig, 113.0, y0 + 10.0, 66.0, 22.0, H)
    labs = [b[2] for b in ERROR_BINS]
    for k, env in enumerate(ENVS):
        t = bins_[(bins_.scope == 'all') & (bins_.env == env)].set_index('bin').reindex(labs)
        x = np.arange(len(labs)) + (k - 0.5) * 0.22
        ax.plot(x, t.value, color=style.ENV_COLOR[env], lw=0.5, zorder=2, alpha=0.6)
        for xi, (_, row) in zip(x, t.iterrows()):
            ax.plot([xi, xi], [row.lo, row.hi], color=style.ENV_COLOR[env], lw=0.8, zorder=3)
            cond_marker(ax, xi, row.value, env, ms=3.2, zorder=4)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for i, lab in enumerate(labs):
        n = bins_[(bins_.scope == 'all') & (bins_.bin == lab)].set_index('env').n
        ax.text(i, -0.42, f'{int(n[CODE]):,}\n{int(n[GAL]):,}', transform=tr, ha='center', va='top', fontsize=5,
                color=style.INK2, linespacing=1.15)
    ax.text(-0.75, -0.42, 'Runs, custom code\nGalaxy', transform=tr, ha='right', va='top', fontsize=5,
            color=style.INK2, linespacing=1.15)
    ax.set_xticks(range(len(labs)), labs)
    ax.tick_params(axis='x', length=0, pad=1.5)
    ax.set_xlim(-0.6, len(labs) - 0.4)
    ax.set_ylim(40, 100)
    ax.set_yticks([40, 60, 80, 100])
    style.grid_y(ax)
    ax.set_xlabel('Execution errors in the run', labelpad=1.5)
    ax.set_ylabel('Runs correct (%)')
    hand = [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.2, mfc=style.ENV_COLOR[e], mec='white', mew=0.35,
                   label=style.ENV_LABEL[e]) for e in ENVS]
    ax.legend(handles=hand, ncol=2, loc='lower right', bbox_to_anchor=(1.0, 1.02), fontsize=5.3, handletextpad=0.2,
              columnspacing=0.8, borderaxespad=0)
    ax.text(0.02, 0.05, f'Runs with errors, Galaxy − custom code:\n'
            f'unadjusted {rec["unadjusted"]:+.1f} points ({fmt_p(rec["p_unadjusted"])})\n'
            f'adjusted for error bin, exploratory {rec["difference"]:+.1f} ({fmt_p(rec["p"])})',
            transform=ax.transAxes, ha='left', va='bottom', fontsize=5, linespacing=1.25)


def draw_e(fig, H, y0, tab, follow):
    label(fig, 0, y0, 'e', 'Parameter checks on installed-tool requests', H,
          'The interface compares the requested parameters with those Galaxy validated or recorded')
    ax = axes_mm(fig, 20.0, y0 + 12.0, 60.0, 19.0, H)
    rows = BENCH + ['all']
    ypos = [0, 1.3, 2.6, 4.0]
    shares = [100 * tab.loc[b].values / tab.loc[b].sum() for b in rows]
    stacked_rows(ax, ypos, shares, [col for _, _, col in CHECKS], 60.0, last_right=True,
                 dark=(style.NEUTRAL_DARK, style.OI_GREEN, style.OI_PURPLE))
    ax.set_ylim(4.55, -0.75)
    ax.set_yticks(ypos, ['BixBench-\nVerified-50', 'CompBioBench', 'IWC', 'All'], fontsize=5)
    ax.get_yticklabels()[-1].set_fontweight('bold')
    ax.tick_params(axis='y', length=0)
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Installed-tool requests (%)', labelpad=1.5)
    ax.text(1.0, 1.04, f'{int(tab.loc["all"].sum()):,} requests', transform=ax.transAxes, ha='right', va='bottom',
            fontsize=5, color=style.INK2)
    ax.legend(handles=[Patch(fc=col, ec=style.NEUTRAL_MID if col == '#E8E8E8' else col, lw=0.3, label=lab)
                       for _, lab, col in CHECKS], loc='upper left', bbox_to_anchor=(-0.28, -0.42), ncol=2,
              fontsize=5.0, handlelength=0.9, handletextpad=0.3, columnspacing=0.8, labelspacing=0.25, borderaxespad=0)
    f = follow.loc['diff_blocked']
    fig.text(4.4 / W, 1 - (y0 + 49.5) / H, f'After a request was blocked for a different value, the run later completed '
             f'a job of the same tool in {100 * f.completed:.0f}% of {int(f.requests):,} cases\n(with matching '
             f'parameters in {100 * f.matched:.0f}%). Matching parameters do not show that the settings were '
             f'scientifically appropriate.', fontsize=5, color=style.INK2, va='top', linespacing=1.25)


def draw_f(fig, H, y0, tab, runs_any, ainfo):
    label(fig, 90.0, y0, 'f', 'Failed requests and candidate infrastructure improvements', H,
          'Failure classes grouped by the change most likely to help (codebook in Source Data); an independent rater\n'
          f'reproduced {100 * ainfo["agree_classified"]:.0f}% of the classes and named the same improvement for '
          f'{100 * ainfo["fix_supported"]:.0f}% of requests')
    ax = axes_mm(fig, 133.0, y0 + 12.5, 28.0, 33.0, H)
    n = len(tab)
    ypos = [i + (0.4 if t.fix in UNRESOLVED else 0) for i, t in enumerate(tab.itertuples())]
    for y, t in zip(ypos, tab.itertuples()):
        grey = t.fix in UNRESOLVED
        ax.barh(y, t.requests, height=0.68, color=style.NEUTRAL_LIGHT if grey else style.GALAXY, zorder=3)
        ax.text(t.requests + 40, y, f'{t.requests:,} ({t.pct:.0f}%)', ha='left', va='center', fontsize=5)
        ax.text(1.62, y, f'{t.runs:,}', transform=blended_transform_factory(ax.transAxes, ax.transData), ha='right',
                va='center', fontsize=5)
    ax.text(1.62, -1.1, 'Runs', transform=blended_transform_factory(ax.transAxes, ax.transData), ha='right',
            va='center', fontsize=5, color=style.INK2)
    ax.set_ylim(max(ypos) + 0.6, -0.6)
    ax.set_yticks(ypos, tab.fix, fontsize=5.5)
    ax.tick_params(axis='y', length=0)
    ax.axhline(ypos[n - 3] + 0.7, color=style.NEUTRAL_MID, lw=0.5, zorder=1)
    ax.set_xlim(0, tab.requests.max() * 1.45)
    ax.set_xticks([0, 500, 1000, 1500])
    style.grid_x(ax)
    ax.spines['left'].set_visible(False)
    ax.set_xlabel(f'Failed requests (of {int(tab.requests.sum()):,}; {runs_any:,} runs)', labelpad=1.5)


# ---------------------------------------------------------------- Extended Data
def ed_status(fig, H, y0, status):
    label(fig, 0, y0, 'a', 'Correct runs of three for every task, model and condition', H)
    cols = [(c, e) for c in CFG for e in ENVS]
    m = status[[f'{c}|{e}' for c, e in cols]].values.T.astype(float)   # rows: model x condition; columns: tasks
    ax = axes_mm(fig, 33.0, y0 + 8.0, 146.0, 17.0, H)
    cmap = plt.matplotlib.colors.ListedColormap(['#F2F1EE', '#C9C8C3', '#8A8A8A', '#1A1A1A'])
    ax.imshow(m, aspect='auto', cmap=cmap, vmin=-0.5, vmax=3.5, interpolation='nearest')
    ax.set_yticks(range(len(cols)), [f'{c} · {style.ENV_LABEL[e]}' for c, e in cols], fontsize=5)
    ax.tick_params(length=0, pad=1.5)
    ax.set_xticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    for y in np.arange(1.5, len(cols) - 1, 2):
        ax.axhline(y, color='white', lw=0.8)
    groups = status.domain.values
    start = 0
    for i in range(1, len(groups) + 1):
        if i == len(groups) or groups[i] != groups[start]:
            name = groups[start]
            ax.axvline(i - 0.5, color='white', lw=0.8) if i < len(groups) else None
            ax.plot([start - 0.3, i - 0.7], [len(cols) - 0.2] * 2, color=style.INK2, lw=0.5, clip_on=False)
            short = {'BixBench-Verified-50': 'BixBench-Verified-50', 'Population genetics': 'Pop. gen.',
                     'Machine learning': 'ML', 'Spatial and structure': 'Sp.', 'Transcriptomics': 'Transcript.',
                     'Epigenomics': 'Epigenomics', 'Single-cell': 'Single-cell', 'Genomics': 'Genomics', 'IWC': 'IWC'}
            ax.text((start + i - 1) / 2, len(cols) + 0.4, short.get(name, name), ha='center', va='top', fontsize=5,
                    rotation=0)
            start = i
    ax.text(0.5, len(cols) + 2.2, 'CompBioBench domains between BixBench-Verified-50 and IWC; tasks sorted by '
            'correct runs within each group', transform=blended_transform_factory(ax.transAxes, ax.transData),
            ha='center', va='top', fontsize=5, color=style.INK2)
    ax.legend(handles=[Patch(fc=cmap(k), ec=style.NEUTRAL_MID, lw=0.3, label=f'{k} of 3') for k in range(4)],
              loc='lower right', bbox_to_anchor=(1.0, 1.02), ncol=4, fontsize=5, handlelength=0.9, borderaxespad=0,
              title='Correct runs', title_fontsize=5)


def ed_types(fig, H, y0, tab, runs):
    label(fig, 0, y0, 'b', 'Execution errors by type and channel (all seven types)', H)
    ax = axes_mm(fig, 30.0, y0 + 9.0, 70.0, 22.0, H)
    shares = [100 * tab.loc[c].values / tab.loc[c].sum() for c, _, _ in CHANNELS]
    ypos = [0, 1.6, 3.2, 5.0]
    stacked_rows(ax, ypos, shares, [col for _, col in ETYPES], 70.0, bar_h=0.78)
    ax.set_ylim(5.6, -1.2)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Errors (%)')
    for y, (c, name, env) in zip(ypos, CHANNELS):
        ax.text(-1.5, y, f'{name} ({"Galaxy" if env == GAL else "custom-code"} runs)', ha='right', va='center', fontsize=5)
        n = int(tab.loc[c].sum())
        ax.text(101.5, y, f'{n:,} ({n / runs[env]:.1f}/run)', ha='left', va='center', fontsize=5, color=style.INK2)
    ax.legend(handles=[Patch(fc=col, label=lab) for lab, col in ETYPES], loc='upper left', bbox_to_anchor=(1.25, 1.0),
              ncol=1, fontsize=5.0, handlelength=0.9, handletextpad=0.3, labelspacing=0.25, borderaxespad=0)


def ed_recovery(fig, H, y0, bins_, by_bm):
    label(fig, 0, y0, 'c', 'Final correctness by execution errors, per benchmark', H)
    labs = [b[2] for b in ERROR_BINS]
    for j, bm in enumerate(BENCH):
        ax = axes_mm(fig, 14.0 + j * 56.0, y0 + 10.0, 48.0, 24.0, H)
        for k, env in enumerate(ENVS):
            t = bins_[(bins_.scope == bm) & (bins_.env == env)].set_index('bin').reindex(labs)
            x = np.arange(len(labs)) + (k - 0.5) * 0.22
            for xi, (_, row) in zip(x, t.iterrows()):
                if np.isnan(row.value):
                    continue
                ax.plot([xi, xi], [row.lo, row.hi], color=style.ENV_COLOR[env], lw=0.8, zorder=3)
                cond_marker(ax, xi, row.value, env, ms=3.0, zorder=4)
        ax.set_xticks(range(len(labs)), labs)
        ax.tick_params(axis='x', length=0, pad=1.5)
        ax.set_xlim(-0.6, len(labs) - 0.4)
        ax.set_ylim(0, 104)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.spines['left'].set_bounds(0, 100)
        style.grid_y(ax)
        ax.set_xlabel('Execution errors in the run')
        if j == 0:
            ax.set_ylabel('Runs correct (%)')
        t = by_bm.set_index('benchmark').loc[bm]
        ax.set_title(f'{BENCH_NAME[bm]}: {t.unadjusted:+.1f} points, unadjusted ({fmt_p(t.p_unadjusted)})', fontsize=5.5,
                     fontweight='bold', loc='left', pad=3)


# ---------------------------------------------------------------- source data and assembly
def source_data(a_tab, a_t, b_tab, b_acc, b_route, rates, burden, c_tab, rec, coef, bins_, e_tab, follow, f_tab):
    rows = []
    for t in a_tab.itertuples():
        rows.append(dict(panel='a', group=t.domain, condition=t.env, measure='runs_correct_pct', value=t.value,
                         ci95_low=t.lo, ci95_high=t.hi, n=t.tasks))
    for t in a_t.itertuples():
        rows.append(dict(panel='a', group=t.domain, condition='galaxy-custom_code', measure='difference_points',
                         value=t.diff, p=t.p, p_holm=t.p_holm))
    for (bm, c), t in b_tab.iterrows():
        for code, lab, _ in ROUTES:
            rows.append(dict(panel='b', benchmark=bm, model=c, condition='galaxy', group=lab, measure='traced_runs',
                             value=int(t[code]), n=int(t.sum())))
        a = b_acc.loc[(bm, c)]
        rows.append(dict(panel='b', benchmark=bm, model=c, condition='galaxy', group='all routes',
                         measure='runs_correct_pct', value=100 * a['mean'], n=int(a['count'])))
    for (bm, route), t in b_route.iterrows():
        lab = {c: l for c, l, _ in ROUTES}[route]
        rows.append(dict(panel='b', benchmark=bm, model='all four', condition='galaxy', group=lab,
                         measure='runs_correct_pct (descriptive; route chosen by the agent)', value=100 * t['mean'],
                         n=int(t['count'])))
    for t in rates.itertuples():
        env = CODE if t.channel == 'code_shell' else GAL
        rows.append(dict(panel='c', condition=env, group=t.channel, measure='pct_steps_failed', value=t.value,
                         ci95_low=t.lo, ci95_high=t.hi, n=t.steps))
    for t in burden.itertuples():
        rows.append(dict(panel='c', condition=t.env, group='all channels', measure='execution_errors_per_run',
                         value=t.value, ci95_low=t.lo, ci95_high=t.hi, n=t.runs))
    for code, name, env in CHANNELS:
        for et, _ in ETYPES:
            rows.append(dict(panel='c', group=f'{name} ({env})', condition=env, measure=f'errors: {et}',
                             value=int(c_tab.loc[code, et])))
    for t in bins_.itertuples():
        rows.append(dict(panel='d' if t.scope == 'all' else 'ED c', benchmark=t.scope, group=f'errors_{t.bin}',
                         condition=t.env, measure='runs_correct_pct', value=t.value, ci95_low=t.lo, ci95_high=t.hi,
                         n=t.n))
    rows.append(dict(panel='d', group='runs with errors', condition='galaxy-custom_code',
                     measure='difference_points_unadjusted', value=rec['unadjusted'], p=rec['p_unadjusted'],
                     n=rec['runs_with_errors']))
    rows.append(dict(panel='d', group='runs with errors', condition='galaxy-custom_code',
                     measure='difference_points_adjusted_for_error_bins_exploratory', value=rec['difference'],
                     p=rec['p'], n=rec['runs_with_errors']))
    for env, c in coef.items():
        rows.append(dict(panel='d', group='logistic fit on ln(1 + errors), not drawn', condition=env, measure='slope',
                         value=c['slope'], ci95_low=c['slope_lo'], ci95_high=c['slope_hi'], n=c['runs']))
    for bm, t in e_tab.iterrows():
        for code, lab, _ in CHECKS:
            rows.append(dict(panel='e', benchmark=bm, condition='galaxy', group=lab,
                             measure='installed_tool_requests', value=int(t[code]), n=int(t.sum())))
    for kind, t in follow.iterrows():
        for col in ('retried', 'completed', 'matched'):
            rows.append(dict(panel='e', benchmark='all', condition='galaxy', group=f'blocked before the job: {kind}',
                             measure=f'pct_later_same_tool_{col}', value=100 * t[col], n=int(t.requests)))
    for t in f_tab.itertuples():
        rows.append(dict(panel='f', condition='galaxy', group=t.fix, measure=f'failed_requests ({t.classes})',
                         value=t.requests, n=int(f_tab.requests.sum())))
        rows.append(dict(panel='f', condition='galaxy', group=t.fix, measure='runs_with_a_failed_request_in_group',
                         value=t.runs))
    cols = ['panel', 'benchmark', 'model', 'condition', 'group', 'measure', 'value', 'ci95_low', 'ci95_high', 'n', 'p',
            'p_holm']
    out = pd.DataFrame(rows).reindex(columns=cols)
    out['condition'] = out.condition.str.replace('open_ended_code', 'custom_code')
    out.round(4).to_csv(os.path.join(OUT, 'fig3_source_data.csv'), index=False)


def ed_source_data(status, by_bm):
    rows = []
    cols = [(c, e) for c in CFG for e in ENVS]
    for _, t in status.iterrows():
        for c, e in cols:
            rows.append(dict(panel='a', benchmark=t['benchmark'], task=t['task'], group=t['domain'], model=c,
                             condition=e, measure='correct_runs_of_3', value=t[f'{c}|{e}']))
    for t in by_bm.itertuples():
        rows.append(dict(panel='c', benchmark=t.benchmark, condition='galaxy-custom_code',
                         measure='difference_points_unadjusted_runs_with_errors', value=t.unadjusted, p=t.p_unadjusted,
                         n=t.runs))
    out = pd.DataFrame(rows).reindex(columns=['panel', 'benchmark', 'task', 'group', 'model', 'condition', 'measure',
                                              'value', 'n', 'p'])
    out['condition'] = out.condition.str.replace('open_ended_code', 'custom_code')
    out.round(4).to_csv(os.path.join(OUT, 'ed_fig3_source_data.csv'), index=False)


def save(fig, name, title):
    style.enforce_min_font(fig)
    fig.savefig(os.path.join(OUT, f'{name}.svg'), metadata={'Title': title})
    fig.savefig(os.path.join(OUT, f'{name}.pdf'), metadata={'Title': title})
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, f'{name}.png'), dpi=(600, 600))
    plt.close(fig)


def main():
    panel_io.record(globals(), 'fig3')   # with PANEL_DATA set, also write figures/panel_data/fig3.json
    global rng
    r = load_runs()
    calls, traced = load_calls()
    m = load_errors(r)
    rec, coef = panel_d(m)                   # same draw order as the approved build: recovery, slopes, domains
    a_tab, a_t, domains = panel_a(r)
    rng = np.random.default_rng(SEED + 1)     # new estimates draw from their own stream
    b_tab, b_acc, b_route = panel_b(calls, traced, r)
    rates, burden, c_tab = panel_c(calls, m)
    bins_ = bin_estimates(m, by_benchmark=True)
    by_bm = recovery_by_benchmark(m)
    e_tab, follow = panel_e(calls)
    f_tab, codebook, runs_any = panel_f()
    status = task_status(r, domains)
    codebook.to_csv(os.path.join(OUT, 'fig3_failure_class_codebook.csv'), index=False)
    for name, t in (('a: domains', a_tab), ('a: tests', a_t), ('b: routes', b_tab), ('b: correct', b_acc),
                    ('b: correct by route', b_route), ('c: rates', rates), ('c: burden', burden),
                    ('c: errors', c_tab), ('d: bins', bins_[bins_.scope == 'all']), ('d: by benchmark', by_bm),
                    ('e: parameter checks', e_tab), ('e: after a blocked request', follow), ('f: fixes', f_tab)):
        print(name)
        print(t.round(3).to_string())
    print('d:', {k: round(float(v), 4) for k, v in rec.items()})

    H = 170.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, a_tab, a_t)
    draw_b(fig, H, b_tab, b_acc)
    y2 = 63.0
    draw_c(fig, H, y2, rates, burden, c_tab, fixed_later())
    draw_d(fig, H, y2, rec, bins_)
    y3 = 113.0
    draw_e(fig, H, y3, e_tab, follow)
    import make_ed_validation as validation          # same statistics as Extended Data Fig. 6d
    _, ainfo = validation.second_rater_classes()
    draw_f(fig, H, y3, f_tab, runs_any, ainfo)
    save(fig, 'fig3', 'Fig. 3 | Galaxy provides a structured environment for agent analyses')
    source_data(a_tab, a_t, b_tab, b_acc, b_route, rates, burden, c_tab, rec, coef, bins_, e_tab, follow, f_tab)

    He = 120.0
    fig = plt.figure(figsize=(W * MM, He * MM))
    ed_status(fig, He, 0, status)
    ed_types(fig, He, 40.0, c_tab, m.groupby('env').size())
    ed_recovery(fig, He, 78.0, bins_, by_bm)
    save(fig, 'ed_fig3', 'Extended Data Fig. 3 | Task status, execution errors and final correctness')
    ed_source_data(status, by_bm)


if __name__ == '__main__':
    main()
