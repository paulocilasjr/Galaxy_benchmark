"""Fig. 3: Galaxy records trace most failures beyond the workbench.

a, replicate sets with one, two or three incorrect runs, by condition and model;
b, runs ending correct by the number of execution errors in the run (error recovery), by condition;
c, causes of incorrect BixBench-Verified-50 runs, by how many runs of the set were incorrect;
d, accuracy when all three runs must be correct and with a majority (consensus) vote, by model and condition.

A replicate set is one task x model x condition (three runs). A run is incorrect when it is not accepted
(BixBench-Verified-50, CompBioBench) or its IWC output agreement is below 0.99, as in Fig. 2b.
Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules,
otherwise tasks). P values come from paired cluster randomization tests (200,000 draws).
Writes figures/fig3.{svg,pdf,png}, figures/fig3_source_data.csv and prints the statistics.
"""
import io
import json
import os
import sys

import numpy as np
import openpyxl
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
import style  # noqa: E402  (sets rcParams on import)
from style import plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})

AN = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis')
ERRORS = os.path.join(ROOT, 'manuscript_material', 'on_demand', 'Source_Data_OD_Fig5.xlsx')
LEDGER = os.path.join(ROOT, 'analysis_reports', 'galaxy_improvement_20260924', 'v2_trace_friction', 'ledger.json')
OUT = os.path.join(ROOT, 'figures')
B, SEED, B_PERM = 20000, 20261002, 200000
W, MM = 180.0, 1 / 25.4
CFG = style.CONFIGS
ENVS = style.ENVS                                    # open-ended code first, always
CODE, GAL = ENVS
MODEL_COLOR = dict(zip(CFG, ['#117733', '#AA4499', '#999933', '#882255']))   # as in Fig. 2
TICK = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6\nSol', 'GPT-5.6 Luna': 'GPT-5.6\nLuna',
        'DeepSeek V4 Pro': 'DeepSeek\nV4 Pro'}
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}       # as in Fig. 2b
ERROR_BINS = [(0, 0, '0'), (1, 2, '1–2'), (3, 5, '3–5'), (6, 10, '6–10'), (11, 10 ** 9, '>10')]   # bins of the recovery test
# Display bins for panel b: exact counts while runs are plentiful, wider bins in the sparse tail.
FINE_BINS = [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 7), (8, 10), (11, 15), (16, 25), (26, 10 ** 6)]
B_CURVE = 2000           # cluster-bootstrap resamples for the fitted-curve bands
# Panel c: every scored-incorrect BixBench-Verified-50 run has one primary cause in the run-level failure ledger.
# Each ledger code maps to exactly one category; the first three are the categories proposed for the analysis.
CAUSE_OF = {'RIGOR': 'No answer validation', 'KNOWLEDGE': 'Lacking biological knowledge',
            'PLATFORM': 'Not able to use Galaxy', 'HARNESS': 'No answer submitted',
            'SPEC': 'Benchmark specification or scoring', 'EVALUATOR': 'Benchmark specification or scoring',
            'CONTRACT': 'Benchmark specification or scoring'}
CAUSES = ['No answer validation', 'Lacking biological knowledge', 'Not able to use Galaxy', 'No answer submitted',
          'Benchmark specification or scoring']
# Cause colours follow the failure-cause palette of the paper (agent analysis dark grey, domain knowledge yellow,
# Galaxy platform purple, benchmark green, other light grey); they avoid the condition colours.
CAUSE_COLOR = dict(zip(CAUSES, [style.NEUTRAL_DARK, style.OI_YELLOW, style.OI_PURPLE, style.NEUTRAL_LIGHT,
                                style.OI_GREEN]))
LEDGER_MODEL = {'GPT-5.5': 'GPT-5.5', 'Sol': 'GPT-5.6 Sol', 'Luna': 'GPT-5.6 Luna', 'DS-Codex': 'DeepSeek V4 Pro'}
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
    """Two-sided paired randomization test: flip the sign of each cluster's summed difference."""
    d = np.asarray(cluster_diffs, float)
    hits = 0
    for _ in range(B_PERM // 20000):
        null = rng.choice([-1.0, 1.0], size=(20000, len(d))) @ d
        hits += np.sum(np.abs(null) >= abs(d.sum()) - 1e-12)
    return (1 + hits) / (B_PERM + 1)


def boot_means(frames, group_cols, value='score'):
    """Pooled means per group with cluster-bootstrap draws; clusters resampled within each benchmark."""
    point, num, den = None, 0.0, 0.0
    for _, d in frames.groupby('benchmark'):
        s = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='sum').fillna(0)
        n = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='count').fillna(0)
        wts = rng.multinomial(len(s), np.full(len(s), 1 / len(s)), size=B)
        num, den = num + wts @ s.values, den + wts @ n.values
        point = (s.sum(), n.sum()) if point is None else (point[0].add(s.sum(), fill_value=0),
                                                         point[1].add(n.sum(), fill_value=0))
    est = point[0] / point[1]
    return est, pd.DataFrame(num / den, columns=est.index)


# ---------------------------------------------------------------- data
def load_runs():
    r = pd.read_csv(os.path.join(AN, 'accuracy_primary_runs.csv'))
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    return r


def replicate_sets(r):
    s = r.groupby(['benchmark', 'cluster', 'task', 'cfg', 'env']).ok.sum().rename('n_correct').reset_index()
    s['n_wrong'] = 3 - s.n_correct
    return s


def load_errors(r):
    """Execution errors per run (failed shell commands + Galaxy jobs in the error state), from On-demand Fig. 5."""
    ws = openpyxl.load_workbook(ERRORS, read_only=True)['abc_runs']
    rows = list(ws.iter_rows(values_only=True))
    e = pd.DataFrame(rows[1:], columns=rows[0])
    e = e[e.model_configuration != 'DeepSeek V4 Pro (Claude Code, superseded)']
    e = e.assign(benchmark=e.benchmark.map({'BixBench-Verified-50': 'BixBench50', 'CompBioBench': 'CompBio',
                                            'IWC': 'IWC'}),
                 cfg=e.model_configuration.replace({'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro'}),
                 env=e.execution_condition.map({'Galaxy condition': GAL, 'Open-ended code condition': CODE}),
                 errors=e.failed_shell_commands.fillna(0) + e.galaxy_jobs_in_error_state.fillna(0))
    m = r.merge(e[['benchmark', 'cfg', 'env', 'task', 'replicate', 'errors']],
                on=['benchmark', 'cfg', 'env', 'task', 'replicate'], how='inner')
    m['bin'] = pd.cut(m.errors, [b[0] - 0.5 for b in ERROR_BINS] + [1e12], labels=[b[2] for b in ERROR_BINS])
    return m


def load_ledger(r):
    led = pd.DataFrame(json.load(open(LEDGER)))
    led = led[(led.b == 'BixBench') & ~led.run.str.contains('ClaudeCode')].copy()
    led['cfg'] = led.run.str.extract(r'^[CG] (.+) r\d$')[0].map(LEDGER_MODEL)
    led['replicate'] = led.run.str.extract(r'r(\d)$')[0].astype(int)
    led['env'] = led.cond
    led['cause'] = led.p.map(CAUSE_OF)
    wrong = r[(r.benchmark == 'BixBench50') & (r.ok == 0)]
    key = ['task', 'cfg', 'env', 'replicate']
    j = wrong.merge(led[key + ['p', 's', 'cause', 'd']], on=key, how='outer', indicator=True)
    assert (j._merge == 'both').all() and not led.duplicated(key).any(), 'ledger must label every incorrect run once'
    return j.drop(columns='_merge')


# ---------------------------------------------------------------- panels
def panel_a(sets):
    w = sets[sets.n_wrong > 0]
    counts = w.groupby(['n_wrong', 'env', 'cfg']).size().unstack('cfg', fill_value=0)[CFG]
    tests = []
    for k in (1, 2, 3):
        x = sets.assign(hit=(sets.n_wrong == k).astype(int)).pivot_table(
            index=['cluster', 'task', 'cfg'], columns='env', values='hit')
        diff = (x[GAL] - x[CODE]).groupby(level='cluster').sum()
        tests.append(dict(n_wrong=k, code=int(x[CODE].sum()), galaxy=int(x[GAL].sum()), p=signflip_p(diff.values)))
    tests = pd.DataFrame(tests)
    tests['p_holm'] = holm(tests.p)
    n_sets = sets.groupby('env').size()
    return counts, tests, n_sets


def stratified_difference(sG, nG, sC, nC, weights):
    return np.sum(weights * (sG / nG - sC / nC), axis=-1)


def recovery_test(e, bins):
    """Weighted Galaxy - open-ended code difference over error bins, with a cluster condition-swap randomization test."""
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


def recovery_curves(m, grid):
    """Logistic fit of runs ending correct on log(1 + errors), per condition, with cluster-bootstrap bands."""
    agg = m.groupby(['benchmark', 'cluster', 'env', 'errors']).ok.agg(['sum', 'count']).reset_index()
    out, coef = {}, {}
    for env in ENVS:
        d = agg[agg.env == env]
        x, succ, n = np.log1p(d.errors.values.astype(float)), d['sum'].values.astype(float), d['count'].values.astype(float)
        beta = logistic_fit(x, succ, n)
        # resample clusters within each benchmark; the same draws serve both conditions only through the seed
        clusters = d.cluster.values
        weights = np.ones((B_CURVE, len(d)))
        for bm in d.benchmark.unique():
            names = np.unique(clusters[d.benchmark.values == bm])
            draw = rng.multinomial(len(names), np.full(len(names), 1 / len(names)), size=B_CURVE)
            col = {c: i for i, c in enumerate(names)}
            idx = np.array([col[c] for c in clusters[d.benchmark.values == bm]])
            weights[:, d.benchmark.values == bm] = draw[:, idx]
        curves = np.empty((B_CURVE, len(grid)))
        betas = np.empty((B_CURVE, 2))
        for k in range(B_CURVE):
            bk = logistic_fit(x, succ * weights[k], n * weights[k])
            betas[k] = bk
            curves[k] = 1 / (1 + np.exp(-(bk[0] + bk[1] * np.log1p(grid))))
        out[env] = (100 / (1 + np.exp(-(beta[0] + beta[1] * np.log1p(grid)))),
                    100 * np.percentile(curves, 2.5, axis=0), 100 * np.percentile(curves, 97.5, axis=0))
        coef[env] = dict(intercept=beta[0], slope=beta[1], slope_lo=np.percentile(betas[:, 1], 2.5),
                         slope_hi=np.percentile(betas[:, 1], 97.5), runs=int(n.sum()))
    return out, coef


def fine_bins(m):
    rows = []
    for env in ENVS:
        d = m[m.env == env]
        for lo, hi in FINE_BINS:
            g = d[(d.errors >= lo) & (d.errors <= hi)]
            if len(g):
                lab = f'{lo}' if lo == hi else (f'>{lo - 1}' if hi > 10 ** 5 else f'{lo}\u2013{hi}')
                rows.append(dict(env=env, bin=lab, mean_errors=g.errors.mean(), value=100 * g.ok.mean(), n=len(g)))
    return pd.DataFrame(rows)


def panel_b(m):
    est, draws = boot_means(m, ['env', 'bin'], value='ok')
    lo, hi = np.percentile(draws, 2.5, axis=0), np.percentile(draws, 97.5, axis=0)
    tab = pd.DataFrame({'value': est * 100, 'lo': lo * 100, 'hi': hi * 100}, index=est.index)
    tab['n'] = m.groupby(['env', 'bin'], observed=True).size()
    # Error-adjusted recovery: Galaxy - open-ended code difference in runs ending correct among runs with >= 1
    # execution error, averaged over the four error bins with weights equal to each bin's share of those runs.
    # Null: the condition labels of all runs in a cluster are swapped at random (paired by cluster).
    # The adjustment was chosen after an exploratory look at the binned data; the unadjusted test is reported too.
    e = m[m.errors > 0]
    adjusted = recovery_test(e, [b[2] for b in ERROR_BINS[1:]])
    unadjusted = recovery_test(e.assign(bin='any'), ['any'])
    rec = dict(difference=adjusted[0] * 100, p=adjusted[1], unadjusted=unadjusted[0] * 100, p_unadjusted=unadjusted[1],
               runs_with_errors=int(len(e)), galaxy_any=e[e.env == GAL].ok.mean() * 100,
               code_any=e[e.env == CODE].ok.mean() * 100)
    grid = np.linspace(0, 40, 161)
    curves, coef = recovery_curves(m, grid)
    return tab, rec, fine_bins(m), grid, curves, coef


def panel_c(ledger):
    sets_wrong = ledger.groupby(['task', 'cfg', 'env']).replicate.transform('size')   # incorrect runs in the set
    lg = ledger.assign(n_wrong=sets_wrong)
    tab = lg.groupby(['n_wrong', 'env', 'cause']).size().unstack('cause', fill_value=0).reindex(columns=CAUSES,
                                                                                               fill_value=0)
    secondary = lg[(lg.p == 'SPEC') & (lg.s == 'RIGOR')].shape[0], lg[lg.p == 'SPEC'].shape[0]
    return tab, secondary


def panel_d(sets):
    s = sets.assign(strict=(sets.n_wrong == 0).astype(int), majority=(sets.n_wrong <= 1).astype(int))
    tab = s.groupby(['cfg', 'env'])[['strict', 'majority']].mean() * 100
    tab['n'] = s.groupby(['cfg', 'env']).size()
    tests = []
    for c in CFG:
        x = s[s.cfg == c].pivot_table(index=['cluster', 'task'], columns='env', values='majority')
        diff = (x[GAL] - x[CODE]).groupby(level='cluster').sum()
        tests.append(dict(cfg=c, diff=(x[GAL].mean() - x[CODE].mean()) * 100, p=signflip_p(diff.values)))
    tests = pd.DataFrame(tests)
    tests['p_holm'] = holm(tests.p)
    pooled = s.groupby('env')[['strict', 'majority']].mean() * 100
    return tab, tests, pooled


# ---------------------------------------------------------------- drawing helpers
def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')


def bracket(ax, x0, x1, y, text, h, pad):
    ax.plot([x0, x0, x1, x1], [y, y + h, y + h, y], color=style.INK, lw=0.5, zorder=4, clip_on=False)
    ax.text((x0 + x1) / 2, y + h + pad, text, ha='center', va='bottom', fontsize=5, color=style.INK, clip_on=False)


def fmt_p(p):
    if p < 0.001:
        return r'$\mathit{P}$ < 0.001'
    return rf'$\mathit{{P}}$ = {p:.2f}' if p >= 0.01 else rf'$\mathit{{P}}$ = {p:.3f}'


def env_handles():
    return [Line2D([], [], marker=style.ENV_MARKER[e], ls='', ms=3.6, mfc=style.ENV_COLOR[e], mec='white', mew=0.4,
                   label=style.ENV_LABEL[e]) for e in ENVS]


# ---------------------------------------------------------------- panels: drawing
def draw_a(fig, H, counts, tests, n_sets):
    label(fig, 0, 0, 'a', 'Replicate sets with incorrect runs', H)
    ax = axes_mm(fig, 10.0, 12.0, 76.0, 31.0, H)
    wd, gap = 0.34, 0.06
    top = counts.sum(axis=1).max()
    xticks = []
    for i, k in enumerate((1, 2, 3)):
        for j, env in enumerate(ENVS):
            x = i + (j - 0.5) * (wd + gap)
            base = 0
            for c in CFG:
                v = counts.loc[(k, env), c]
                ax.bar(x, v, bottom=base, width=wd, color=MODEL_COLOR[c], ec='white', lw=0.4, zorder=3)
                base += v
            ax.text(x, base + top * 0.02, f'{base}', ha='center', va='bottom', fontsize=5)
            xticks.append(x)
        t = tests.set_index('n_wrong').loc[k]
        y = counts.xs(k, level='n_wrong').sum(axis=1).max() + top * 0.12
        bracket(ax, i - (wd + gap) / 2, i + (wd + gap) / 2, y, fmt_p(t.p_holm), top * 0.03, top * 0.015)
    ax.set_ylim(0, top * 1.32)
    ax.spines['left'].set_bounds(0, np.ceil(top / 20) * 20)
    ax.set_yticks(np.arange(0, np.ceil(top / 20) * 20 + 1, 20))
    style.grid_y(ax)
    # condition names under each bar, then a line spanning each pair with its group label below
    ax.set_xticks(xticks, [{CODE: 'Open-ended', GAL: 'Galaxy'}[e] for _ in range(3) for e in ENVS], rotation=40,
                  ha='right', rotation_mode='anchor', fontsize=5.5)
    ax.tick_params(axis='x', length=0, pad=1.5)
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for i, k in enumerate((1, 2, 3)):
        x0, x1 = i - (wd + gap) / 2 - wd / 2, i + (wd + gap) / 2 + wd / 2
        ax.plot([x0, x1], [-0.31, -0.31], transform=tr, color=style.INK2, lw=0.6, clip_on=False)
        ax.text(i, -0.345, f'{k} of 3', transform=tr, ha='center', va='top', fontsize=5.5)
    ax.text(0.5, -0.47, 'Incorrect runs in the replicate set', transform=ax.transAxes, ha='center', va='top',
            fontsize=6)
    ax.set_ylabel('Replicate sets')
    ax.set_xlim(-0.55, 2.55)
    models = ax.legend(handles=[Patch(fc=MODEL_COLOR[c], label=c) for c in CFG], ncol=4, loc='lower left',
                       bbox_to_anchor=(0.0, 1.02), fontsize=5.5, handlelength=1.0, columnspacing=0.9,
                       borderaxespad=0)
    ax.text(0.0, 1.0, f'{int(n_sets.iloc[0])} sets per condition', transform=ax.transAxes, ha='left', va='top',
            fontsize=5, color=style.INK2)


def draw_b(fig, H, rec, fine, grid, curves, runs, max_errors):
    label(fig, 96.0, 0, 'b', 'Recovery from execution errors', H)
    ax = axes_mm(fig, 106.0, 12.0, 73.0, 38.0, H)
    gx = np.log1p(grid)
    for k, env in enumerate(ENVS):
        fit, lo, hi = curves[env]
        keep = grid <= max_errors[env]                  # no extrapolation beyond the condition's observed runs
        ax.fill_between(gx[keep], lo[keep], hi[keep], color=style.ENV_COLOR[env], alpha=0.15, lw=0, zorder=2)
        ax.plot(gx[keep], fit[keep], color=style.ENV_COLOR[env], lw=0.8, zorder=3)
        f = fine[fine.env == env]
        dodge = (k - 0.5) * 0.07                         # open-ended code a little left, Galaxy a little right
        ax.scatter(np.log1p(f.mean_errors) + dodge, f.value, s=np.maximum(f.n * 0.11, 3.0),
                   marker=style.ENV_MARKER[env], facecolor=style.ENV_COLOR[env], edgecolor='white', lw=0.4,
                   alpha=0.9, zorder=4)
    ticks = [0, 1, 2, 5, 10, 20, 40]
    ax.set_xticks(np.log1p(ticks), [str(t) for t in ticks])
    ax.set_xlim(-0.15, np.log1p(42))
    ax.set_ylim(20, 100)
    ax.set_yticks(range(20, 101, 20))
    style.grid_y(ax)
    ax.set_xlabel('Execution errors in the run (log scale)')
    ax.set_ylabel('Runs ending correct (%)')
    cond = [Line2D([], [], color=style.ENV_COLOR[e], lw=0.8, marker=style.ENV_MARKER[e], ms=3.6,
                   mfc=style.ENV_COLOR[e], mec='white', mew=0.4, label=f'{style.ENV_LABEL[e]} ({runs[e]:,} runs)')
            for e in ENVS]
    leg = ax.legend(handles=cond, ncol=1, loc='lower left', bbox_to_anchor=(0.0, 1.01), fontsize=5.5,
                    handlelength=1.6, handletextpad=0.4, labelspacing=0.25, borderaxespad=0)
    ax.add_artist(leg)
    sizes = [Line2D([], [], ls='', marker='o', ms=np.sqrt(max(n * 0.11, 3.0)), mfc='none', mec=style.INK2, mew=0.5,
                    label=f'{n}') for n in (25, 100, 400)]
    ax.legend(handles=sizes, ncol=3, loc='lower right', bbox_to_anchor=(1.0, 1.01), fontsize=5, handletextpad=0.6,
              columnspacing=1.0, handlelength=1.2, borderaxespad=0, title='Runs per point', title_fontsize=5)
    ax.text(0.02, 0.04, f'At equal error counts, Galaxy runs with errors ended\ncorrect {rec["difference"]:.1f} '
            f'percentage points more often ({fmt_p(rec["p"])})', transform=ax.transAxes, ha='left', va='bottom',
            fontsize=5, color=style.INK, linespacing=1.25)


def draw_c(fig, H, y0, tab, secondary):
    label(fig, 0, y0, 'c', 'Causes of incorrect runs (BixBench-Verified-50)', H)
    ax = axes_mm(fig, 30.0, y0 + 17.0, 59.0, 37.0, H)
    rows = [(k, env) for k in (1, 2, 3) for env in ENVS]
    ypos = []
    y = 0.0
    for i, (k, env) in enumerate(rows):
        ypos.append(y)
        y += 1.0 if env == CODE else 2.05      # room between groups for counts placed outside narrow segments
    bar_h, width_mm = 0.72, 59.0
    dark = ('No answer validation', 'Benchmark specification or scoring', 'Not able to use Galaxy')
    for (k, env), yy in zip(rows, ypos):
        t = tab.loc[(k, env)] if (k, env) in tab.index else pd.Series(0, index=CAUSES)
        n = int(t.sum())
        left, outside = 0.0, []
        for cause in CAUSES:
            v = 100 * t[cause] / n if n else 0
            if v:
                ax.barh(yy, v, left=left, height=bar_h, color=CAUSE_COLOR[cause], ec='white', lw=0.4, zorder=3)
                txt = f'{int(t[cause])}'
                if v / 100 * width_mm >= 1.25 * len(txt) + 1.0:     # count fits inside the segment
                    ax.text(left + v / 2, yy, txt, ha='center', va='center', fontsize=5,
                            color='white' if cause in dark else style.INK, zorder=4)
                else:
                    outside.append([left + v / 2, txt, left + v / 2])   # label x, count, segment centre
            left += v
        # narrow segments: count outside the bar with a leader line (above open-ended code, below Galaxy)
        for a_, b_ in zip(outside, outside[1:]):          # keep neighbouring labels at least 4 points apart
            if b_[0] - a_[0] < 4.0:
                b_[0] = a_[0] + 4.0
        sign = -1 if env == CODE else 1
        for xc, txt, seg in outside:
            edge, tip = yy + sign * bar_h / 2, yy + sign * (bar_h / 2 + 0.32)
            xc = xc + 2.5                           # angled leader, so the count is not read as an axis label
            ax.plot([seg, xc], [edge, tip], color=style.INK2, lw=0.4, zorder=4, clip_on=False)
            ax.text(xc, tip + sign * 0.05, txt, ha='center', va='bottom' if sign < 0 else 'top', fontsize=5,
                    color=style.INK, zorder=4, clip_on=False)
        ax.text(101.5, yy, f'{n}', ha='left', va='center', fontsize=5, color=style.INK2)
        ax.text(-1.2, yy, style.ENV_LABEL[env], ha='right', va='center', fontsize=5, color=style.INK)
    ax.set_ylim(ypos[-1] + 1.25, -0.6)        # bottom margin keeps outside counts clear of the axis
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Incorrect runs (%)')
    style.grid_x(ax)
    for k in (1, 2, 3):
        mid = (ypos[rows.index((k, CODE))] + ypos[rows.index((k, GAL))]) / 2
        ax.text(-0.27, mid, f'{k} of 3\nincorrect', transform=blended_transform_factory(ax.transAxes, ax.transData),
                ha='right', va='center', fontsize=5.5, fontweight='bold', linespacing=1.1)
    ax.text(101.5, -0.95, 'Runs', ha='left', va='center', fontsize=5, color=style.INK2)
    ax.legend(handles=[Patch(fc=CAUSE_COLOR[c], label=c) for c in CAUSES], ncol=2, loc='lower left',
              bbox_to_anchor=(-0.43, 1.03), fontsize=5.3, handlelength=1.0, columnspacing=0.9, labelspacing=0.3,
              borderaxespad=0)


def draw_d(fig, H, y0, tab, tests):
    label(fig, 104.0, y0, 'd', 'Accuracy with a majority vote', H)
    ax = axes_mm(fig, 114.0, y0 + 12.0, 65.0, 42.0, H)
    wd = 0.36
    for k, env in enumerate(ENVS):
        xs = np.arange(len(CFG)) + (k - 0.5) * (wd + 0.04)
        t = tab.xs(env, level='env').loc[CFG]
        ax.bar(xs, t.strict, width=wd, color=style.ENV_COLOR[env], zorder=3)
        ax.bar(xs, t.majority - t.strict, bottom=t.strict, width=wd, color=style.ENV_TINT[env],
               ec=style.ENV_COLOR[env], lw=0.5, zorder=3)
        for x, s_, m_ in zip(xs, t.strict, t.majority):
            ax.text(x, m_ + 1.2, f'{m_:.0f}', ha='center', va='bottom', fontsize=5)
    ax.set_ylim(0, 116)
    ax.set_yticks(range(0, 101, 25))
    ax.spines['left'].set_bounds(0, 100)
    style.grid_y(ax)
    ax.set_xticks(range(len(CFG)), [TICK[c] for c in CFG])
    ax.tick_params(axis='x', length=0, pad=2)
    ax.set_xlim(-0.6, len(CFG) - 0.4)
    ax.set_ylabel('Accuracy (%)')
    for i, c in enumerate(CFG):
        p = tests.set_index('cfg').loc[c, 'p_holm']
        y = tab.loc[c].majority.max() + 6.5
        bracket(ax, i - 0.2, i + 0.2, y, 'n.s.' if p >= 0.05 else fmt_p(p), 1.6, 0.8)
    # key: one row per condition, one column per segment, so every bar colour is defined
    key = fig.add_axes([116.0 / W, 1 - (y0 + 11.0) / H, 62.0 / W, 7.0 / H])
    key.set_xlim(0, 62)
    key.set_ylim(7, 0)
    key.axis('off')
    cols = {'strict': (20.5, 'All 3 runs correct'), 'majority': (41.0, '+ 2 of 3 correct (majority)')}
    for kind, (cx, head) in cols.items():
        key.text(cx, 1.1, head, ha='center', va='center', fontsize=5, color=style.INK2)
    for row, env in enumerate(ENVS):
        yy = 3.4 + row * 2.6
        key.text(0, yy, style.ENV_LABEL[env], ha='left', va='center', fontsize=5.5)
        for kind, (cx, _) in cols.items():
            solid = kind == 'strict'
            key.add_patch(plt.Rectangle((cx - 2.0, yy - 0.8), 4.0, 1.6, lw=0.5, ec=style.ENV_COLOR[env],
                                        fc=style.ENV_COLOR[env] if solid else style.ENV_TINT[env]))
    key.text(62, 4.7, 'Number above bar:\nmajority-vote accuracy', ha='right', va='center', fontsize=5,
             color=style.INK2, linespacing=1.15)


# ---------------------------------------------------------------- source data and assembly
def source_data(counts, a_t, n_sets, b_tab, b_fine, coef, rec, c_tab, secondary, d_tab, d_t, d_pool):
    rows = []
    for (k, env), r in counts.iterrows():
        for c in CFG:
            rows.append(dict(panel='a', benchmark='all', model=c, condition=env, group=f'{k}_of_3_incorrect',
                             measure='replicate_sets', value=r[c], n=int(n_sets[env]) // len(CFG)))
    for r in a_t.itertuples():
        rows.append(dict(panel='a', benchmark='all', model='all four', condition='galaxy-open_ended_code',
                         group=f'{r.n_wrong}_of_3_incorrect', measure='difference_sets', value=r.galaxy - r.code,
                         p=r.p, p_holm=r.p_holm))
    for (env, b), r in b_tab.iterrows():   # the four bins of the recovery test, plus zero errors
        rows.append(dict(panel='b (test bins)', benchmark='all', model='all four', condition=env, group=f'errors_{b}',
                         measure='runs_ending_correct_pct', value=r.value, ci95_low=r.lo, ci95_high=r.hi, n=r.n))
    for r in b_fine.itertuples():           # the plotted points
        rows.append(dict(panel='b', benchmark='all', model='all four', condition=r.env, group=f'errors_{r.bin}',
                         measure='runs_ending_correct_pct', value=r.value, n=r.n))
        rows.append(dict(panel='b', benchmark='all', model='all four', condition=r.env, group=f'errors_{r.bin}',
                         measure='mean_errors_per_run', value=r.mean_errors, n=r.n))
    for env, c in coef.items():             # fitted curves: logit P(correct) = intercept + slope * ln(1 + errors)
        rows.append(dict(panel='b', benchmark='all', model='all four', condition=env, group='logistic_fit',
                         measure='slope_per_ln(1+errors)', value=c['slope'], ci95_low=c['slope_lo'],
                         ci95_high=c['slope_hi'], n=c['runs']))
        rows.append(dict(panel='b', benchmark='all', model='all four', condition=env, group='logistic_fit',
                         measure='intercept', value=c['intercept'], n=c['runs']))
    rows.append(dict(panel='b', benchmark='all', model='all four', condition='galaxy-open_ended_code',
                     group='runs_with_errors', measure='error_adjusted_difference_points', value=rec['difference'],
                     n=rec['runs_with_errors'], p=rec['p']))
    rows.append(dict(panel='b', benchmark='all', model='all four', condition='galaxy-open_ended_code',
                     group='runs_with_errors', measure='unadjusted_difference_points', value=rec['unadjusted'],
                     n=rec['runs_with_errors'], p=rec['p_unadjusted']))
    for env, key in ((CODE, 'code_any'), (GAL, 'galaxy_any')):
        rows.append(dict(panel='b', benchmark='all', model='all four', condition=env, group='runs_with_errors',
                         measure='runs_ending_correct_pct', value=rec[key]))
    for (k, env), r in c_tab.iterrows():
        for cause in CAUSES:
            rows.append(dict(panel='c', benchmark='BixBench50', model='all four', condition=env,
                             group=f'{k}_of_3_incorrect', measure=cause, value=r[cause], n=int(r.sum())))
    rows.append(dict(panel='c', benchmark='BixBench50', model='all four', condition='both',
                     group='benchmark_specification_with_rigor_secondary', measure='runs', value=secondary[0],
                     n=secondary[1]))
    for (c, env), r in d_tab.iterrows():
        for m in ('strict', 'majority'):
            rows.append(dict(panel='d', benchmark='all', model=c, condition=env, group=m, measure='accuracy_pct',
                             value=r[m], n=int(r.n)))
    for r in d_t.itertuples():
        rows.append(dict(panel='d', benchmark='all', model=r.cfg, condition='galaxy-open_ended_code', group='majority',
                         measure='difference_pct_points', value=r.diff, p=r.p, p_holm=r.p_holm))
    for env, r in d_pool.iterrows():
        for m in ('strict', 'majority'):
            rows.append(dict(panel='d', benchmark='all', model='all four', condition=env, group=m,
                             measure='accuracy_pct', value=r[m]))
    cols = ['panel', 'benchmark', 'model', 'condition', 'group', 'measure', 'value', 'ci95_low', 'ci95_high', 'n',
            'p', 'p_holm']
    pd.DataFrame(rows).reindex(columns=cols).round(4).to_csv(os.path.join(OUT, 'fig3_source_data.csv'), index=False)


def main():
    r = load_runs()
    sets = replicate_sets(r)
    counts, a_t, n_sets = panel_a(sets)
    m = load_errors(r)
    b_tab, rec, b_fine, grid, curves, coef = panel_b(m)
    c_tab, secondary = panel_c(load_ledger(r))
    d_tab, d_t, d_pool = panel_d(sets)
    print('a: sets by incorrect runs'); print(counts.assign(total=counts.sum(axis=1)).to_string())
    print(a_t.round(4).to_string(index=False))
    print(f'b: runs with error data {len(m)} of {len(r)}'); print(b_fine.round(1).to_string()); print(rec); print(coef)
    print('c: causes'); print(c_tab.to_string()); print('SPEC runs with RIGOR secondary', secondary)
    print('d: strict vs majority'); print(d_tab.round(1).to_string()); print(d_t.round(4).to_string(index=False))
    print(d_pool.round(1))

    H = 128.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, counts, a_t, n_sets)
    draw_b(fig, H, rec, b_fine, grid, curves, {e: c['runs'] for e, c in coef.items()},
           m.groupby('env').errors.max().to_dict())
    y2 = 66.0
    draw_c(fig, H, y2, c_tab, secondary)
    draw_d(fig, H, y2, d_tab, d_t)
    style.enforce_min_font(fig)
    title = 'Fig. 3 | Galaxy records trace most failures beyond the workbench'
    fig.savefig(os.path.join(OUT, 'fig3.svg'), metadata={'Title': title})
    fig.savefig(os.path.join(OUT, 'fig3.pdf'), metadata={'Title': title})
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, 'fig3.png'), dpi=(600, 600))
    source_data(counts, a_t, n_sets, b_tab, b_fine, coef, rec, c_tab, secondary, d_tab, d_t, d_pool)


if __name__ == '__main__':
    main()
