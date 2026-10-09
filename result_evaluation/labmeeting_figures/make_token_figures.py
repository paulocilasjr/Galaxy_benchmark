#!/usr/bin/env python3
"""Fig. 4 (lab meeting): token use with custom code and with Galaxy.

- fig4_token_usage: tokens per run (input including cached context, plus output) by benchmark and model, and the
  Galaxy / custom-code ratio: the geometric mean over tasks of the paired ratio (each task's mean over its replicates),
  with a 95% cluster-bootstrap interval and a paired cluster sign-flip test (clusters: BixBench source capsules,
  otherwise tasks), as in Fig. 5a of the manuscript.
- fig4_token_accuracy: a, accuracy against median tokens per run for each model and condition; b, within the same task,
  model and condition, how many more tokens the incorrect runs used than the correct ones (geometric mean over the
  replicate sets that have both, with a cluster-bootstrap interval).
- fig4_token_phases: where the input tokens go, by phase of the run (start-up, analysis, error correction, output
  preparation), estimated from each run's sequence of calls (token_phases.py) and scaled to its recorded input tokens.
- fig4_token_reduction: the token-reduction experiments in token_improvment/ (BixBench-Verified-50, complete 50-task
  runs): Galaxy tokens before and after each round of interface changes, against custom code, with accuracy; and the
  change for each task. The stage values are those of the manuscript's Fig. 5c (figures/make_fig5.py, token_rounds).

Scores: figures/scored_runs.csv. Tokens: manuscript_narrative/original_layout/analysis/token_run_observations.csv
(the run's final usage record). A run is correct when accepted or, for IWC, at >= 0.99 output agreement.
Usage: python result_evaluation/labmeeting_figures/make_token_figures.py
"""
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_labmeeting_figures as lm  # noqa: E402
import token_phases as tp  # noqa: E402

f2, plt = lm.f2, lm.plt
sys.path.insert(0, os.path.join(ROOT, 'figures'))
with plt.rc_context():                            # make_fig5 sets the manuscript's style; keep the lab-meeting one
    import make_fig5 as f5  # noqa: E402  (token_rounds: the reduction experiments as in Fig. 5c)
from multiprocessing import Pool  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

CODE, GAL = lm.CODE, lm.GAL
INK, INK2, GRID, SURFACE = lm.INK, lm.INK2, lm.GRID, lm.SURFACE
CFG = list(lm.CFG)
BENCH = lm.BENCH
KEY = ['benchmark', 'task', 'cfg', 'env', 'replicate']
TOKENS = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis', 'token_run_observations.csv')
DIRS = {'BixBench50': 'BixBench_50', 'CompBio': 'CompBio', 'IWC': 'IWC'}
MARKER = dict(zip(CFG, ['o', 's', '^', 'D']))
ALL = 'all four'
MIN_SETS = 3                                      # replicate sets with both outcomes needed for an estimate
B = 20000
rng = np.random.default_rng(20261008)
# grid for the context model of token_phases: overhead per request (tokens), context cap (tokens), tokens per character
GRID_P = [5e3, 10e3, 15e3, 20e3, 25e3, 30e3]
GRID_W = [100e3, 125e3, 150e3, 175e3, 200e3, 250e3]
GRID_C = [0.2, 0.25, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7]


# ---------------------------------------------------------------- data
def load():
    r = f2.load_runs()
    t = pd.read_csv(TOKENS)
    t = t[t.model_primary]
    r = r.merge(t[KEY + ['input_tokens', 'cached', 'output_tokens']], on=KEY, how='left')
    r['tokens'] = r.input_tokens + r.output_tokens
    return r


def cluster_boot_mean(values, clusters):
    """Mean over cells with a percentile cluster bootstrap (clusters resampled with their cells)."""
    d = pd.DataFrame({'v': values, 'c': clusters}).groupby('c').v.agg(['sum', 'count'])
    w = rng.multinomial(len(d), np.full(len(d), 1 / len(d)), size=B)
    draws = (w @ d['sum'].values) / (w @ d['count'].values)
    return d['sum'].sum() / d['count'].sum(), np.percentile(draws, 2.5), np.percentile(draws, 97.5)


def paired_ratio(r, bm, cfg=None):
    """Geometric mean over tasks (and models, if pooled) of Galaxy / custom-code tokens, with CI and sign-flip P."""
    d = r[(r.benchmark == bm) & r.tokens.notna()]
    if cfg is not None:
        d = d[d.cfg == cfg]
    cell = d.groupby(['cluster', 'task', 'cfg', 'env']).tokens.mean().unstack('env').dropna()
    lr = np.log(cell[GAL] / cell[CODE])
    est, lo, hi = cluster_boot_mean(lr.values, lr.index.get_level_values('cluster'))
    p = f2.signflip_p(lr.groupby(level='cluster').sum().values)
    return dict(ratio=np.exp(est), lo=np.exp(lo), hi=np.exp(hi), p=p, cells=len(lr))


def token_usage_table(r):
    rows = []
    for bm, _, _ in BENCH:
        for cfg in CFG + [None]:
            d = r[(r.benchmark == bm) & (r.cfg == cfg if cfg else True) & r.tokens.notna()]
            st = paired_ratio(r, bm, cfg)
            row = dict(benchmark=bm, cfg=cfg or ALL, **st)
            for e in (CODE, GAL):
                x = d[d.env == e]
                row[f'{e}_median_m'] = x.tokens.median() / 1e6
                row[f'{e}_q1_m'] = x.tokens.quantile(0.25) / 1e6
                row[f'{e}_q3_m'] = x.tokens.quantile(0.75) / 1e6
                row[f'{e}_mean_m'] = x.tokens.mean() / 1e6
                row[f'{e}_cached_share'] = x.cached.sum() / x.input_tokens.sum()
                row[f'{e}_runs'] = len(x)
            rows.append(row)
    t = pd.DataFrame(rows)
    t['p_holm'] = np.nan
    per_model = t.cfg != ALL
    t.loc[per_model, 'p_holm'] = f2.holm(t.loc[per_model, 'p'].values)
    t.loc[~per_model, 'p_holm'] = f2.holm(t.loc[~per_model, 'p'].values)
    return t


def accuracy_table(r):
    rows = []
    for (bm, cfg, env), g in r.groupby(['benchmark', 'cfg', 'env']):         # accuracy over all runs, as in Fig. 2
        rows.append(dict(benchmark=bm, cfg=cfg, env=env, accuracy=100 * g.ok.mean(), median_tokens_m=g.tokens.median() / 1e6,
                         runs=len(g), runs_with_tokens=int(g.tokens.notna().sum())))
    return pd.DataFrame(rows)


def outcome_table(r):
    """Incorrect / correct tokens within replicate sets (task x model x condition) that have both outcomes, per model
    and for the four models together."""
    rows = []
    d = r[r.tokens.notna()]
    for (bm, env), g in d.groupby(['benchmark', 'env']):
        for cfg in CFG + [ALL]:
            s_ = g if cfg == ALL else g[g.cfg == cfg]
            lr, cl = [], []
            for (c, task, _), s in s_.groupby(['cluster', 'task', 'cfg']):
                if s.ok.any() and not s.ok.all():
                    lr.append(np.log(s[s.ok == 0].tokens.mean() / s[s.ok == 1].tokens.mean()))
                    cl.append(c)
            row = dict(benchmark=bm, cfg=cfg, env=env, ratio=np.nan, lo=np.nan, hi=np.nan, sets=len(lr),
                       incorrect_more=int(np.sum(np.array(lr) > 0)))
            if len(lr) >= MIN_SETS:
                est, lo, hi = cluster_boot_mean(np.array(lr), np.array(cl))
                row.update(ratio=np.exp(est), lo=np.exp(lo), hi=np.exp(hi))
            rows.append(row)
    return pd.DataFrame(rows)


def _requests(job):
    path, env = job
    req = tp.requests(path, env)
    return [c for c, _ in req], [q for _, q in req]


def run_requests(r):
    """Each run's model requests (characters of conversation before the request, phase), from its agent trace."""
    d = r[r.input_tokens.notna()].copy()
    d['trace'] = [tp.trace_path(os.path.join(ROOT, DIRS[b], 'analysis', t, 'source_snapshots', 'huggingface_traces',
                                             'files', i)) for b, t, i in zip(d.benchmark, d.task, d.run_id)]
    d = d[d.trace.notna()]
    with Pool(min(8, os.cpu_count() or 1)) as pool:
        out = pool.map(_requests, list(zip(d.trace, d.env)), chunksize=8)
    d['chars'] = [np.array(c, float) for c, _ in out]
    d['phases'] = [np.array(q) for _, q in out]
    return d[d.chars.map(len) > 0].drop(columns='trace')


def estimate(chars, P, W, c):
    return np.minimum(P + c * chars, W)


def fit_context(d):
    """Grid search, per condition, for the parameters that best reproduce the recorded input tokens of each run
    (smallest median absolute log error)."""
    rows = []
    for env, g in d.groupby('env'):
        actual = np.log(g.input_tokens.values)
        for P in GRID_P:
            for W in GRID_W:
                for c in GRID_C:
                    est = np.log([estimate(x, P, W, c).sum() for x in g.chars])
                    err = est - actual
                    rows.append(dict(env=env, overhead=P, cap=W, tokens_per_char=c, median_abs_log_error=np.median(np.abs(err)),
                                     r2_log=1 - np.sum(err ** 2) / np.sum((actual - actual.mean()) ** 2)))
    grid = pd.DataFrame(rows).sort_values(['env', 'median_abs_log_error']).reset_index(drop=True)
    grid['rank'] = grid.groupby('env').cumcount() + 1
    return grid


def phase_runs(d, grid):
    """Estimated input tokens per phase for every run (best fit), and the shares under the next-best fits."""
    rows = []
    best = {e: g.iloc[:3] for e, g in grid.groupby('env')}
    for x in d.itertuples():
        b = best[x.env].iloc[0]
        w = estimate(x.chars, b.overhead, b.cap, b.tokens_per_char)
        row = dict(benchmark=x.benchmark, task=x.task, cfg=x.cfg, env=x.env, replicate=x.replicate, ok=x.ok,
                   input_tokens=x.input_tokens, estimated_input=w.sum(), requests=len(w))
        for p in tp.PHASES:
            row[f'tokens_{p}'] = w[x.phases == p].sum() / w.sum() * x.input_tokens
            row[f'requests_{p}'] = int((x.phases == p).sum())
        for k in (1, 2):                                   # sensitivity: the second and third best parameter sets
            alt = best[x.env].iloc[k]
            wa = estimate(x.chars, alt.overhead, alt.cap, alt.tokens_per_char)
            for p in tp.PHASES:
                row[f'alt{k}_tokens_{p}'] = wa[x.phases == p].sum() / wa.sum() * x.input_tokens
        rows.append(row)
    return pd.DataFrame(rows)


def phase_table(pr):
    rows = []
    for (bm, env), g in pr.groupby(['benchmark', 'env']):
        tot = g.input_tokens.sum()
        for p in tp.PHASES:
            rows.append(dict(benchmark=bm, env=env, phase=p, mean_tokens_m=g[f'tokens_{p}'].mean() / 1e6,
                             share=g[f'tokens_{p}'].sum() / tot, share_alt1=g[f'alt1_tokens_{p}'].sum() / tot,
                             share_alt2=g[f'alt2_tokens_{p}'].sum() / tot, mean_requests=g[f'requests_{p}'].mean(),
                             runs_with_phase=(g[f'requests_{p}'] > 0).mean(), runs=len(g)))
    return pd.DataFrame(rows)


def reduction_runs():
    """Per-task Galaxy tokens of the reduction experiments (the runs make_fig5.token_rounds() sums)."""
    rows = []
    for p in glob.glob(os.path.join(ROOT, 'token_improvment', 'earlier_rounds', 'run_traces_july6_codex', '*', '*',
                                    'replicate_*', 'usage.json')):
        task_dir, cond, rep = p.split(os.sep)[-4:-1]
        if cond != 'galaxy_strict_skills':
            continue
        u = json.load(open(p))['totals']
        rows.append(dict(source='july6', task=task_dir.replace('_', '-'), tokens=u['input_tokens'] + u['output_tokens']))
    inv = pd.read_csv(os.path.join(ROOT, 'token_improvment', 'run_inventory.csv'))
    inv['tokens'] = inv.input_tokens + inv.output_tokens
    for model, src in (('Codex GPT-5.5', 'archive GPT-5.5'), ('Codex GPT-5.6 Sol', 'archive GPT-5.6 Sol')):
        g = inv[inv.group.str.startswith('archive_') & (inv.model == model) & (inv.condition == GAL)]
        rows += [dict(source=src, task=t.task, tokens=t.tokens) for t in g.itertuples()]
    g = inv[inv.group == 'token_optimization_oct2026']
    rows += [dict(source='token optimization', task=t.task, tokens=t.tokens) for t in g.itertuples()]
    d = pd.DataFrame(rows).groupby(['source', 'task']).tokens.sum().unstack('source')
    return pd.DataFrame({'July': d['archive GPT-5.5'] / d['july6'],
                         'October': d['token optimization'] / d['archive GPT-5.6 Sol']}).dropna()


def october_phase_runs(req, grid):
    """Input tokens by phase in the October experiment (GPT-5.6 Sol, BixBench-Verified-50): the archived runs (Galaxy with
    round 2 in place, and custom code) and the 150 Galaxy runs after round 3 plus longer waits (token_improvment/analysis)."""
    t = pd.read_csv(os.path.join(ROOT, 'token_improvment', 'token_optimization_runs.csv'),
                    usecols=['item_id', 'replicate', 'passed', 'input_tokens', 'output_tokens'])
    t = t.rename(columns={'item_id': 'task'})
    t['benchmark'], t['cfg'], t['env'], t['ok'] = 'BixBench50', 'GPT-5.6 Sol', GAL, t.passed.astype(int)
    t['trace'] = [tp.trace_path(os.path.join(ROOT, 'token_improvment', 'analysis', x.task, 'source_snapshots',
                                             'huggingface_traces', 'files',
                                             f'galaxy_codex_gpt_5_6_sol_token_optimization_oct_2026_r{x.replicate}'))
                  for x in t.itertuples()]
    assert t.trace.notna().all() and len(t) == 150
    with Pool(min(8, os.cpu_count() or 1)) as pool:
        out = pool.map(_requests, list(zip(t.trace, t.env)), chunksize=4)
    t['chars'] = [np.array(c, float) for c, _ in out]
    t['phases'] = [np.array(q) for _, q in out]
    old = req[(req.benchmark == 'BixBench50') & (req.cfg == 'GPT-5.6 Sol')]
    pr = pd.concat([phase_runs(old, grid).assign(stage=lambda x: np.where(x.env == GAL, 'before', 'code')),
                    phase_runs(t, grid).assign(stage='after')], ignore_index=True)
    return pr



# ---------------------------------------------------------------- drawing helpers
def header(fig, height, title, subtitle, legend=None, ncol=None):
    """Title, subtitle and (under them) the legend; returns where the header ends, in inches from the top."""
    fig.text(0.05, 1 - 0.2 / height, title, fontsize=17, fontweight='bold', color=INK, va='top')
    fig.text(0.05, 1 - 0.56 / height, subtitle, fontsize=10.5, color=INK2, va='top', linespacing=1.35)
    y = 0.56 + 0.2 * (subtitle.count('\n') + 1) + 0.1
    if legend:
        fig.legend(handles=legend, loc='upper left', bbox_to_anchor=(0.045, 1 - y / height), ncol=ncol or len(legend),
                   frameon=False, fontsize=10.5, handlelength=1.2, columnspacing=1.6, borderaxespad=0)
        y += 0.3
    return y


def clean(ax, grid='y'):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.spines['left'].set_color(INK2)
    ax.spines['bottom'].set_color(INK2)
    ax.tick_params(colors=INK2, labelsize=9.5)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)


def p_text(p):
    return 'P < 0.001' if p < 0.001 else f'P = {lm.fixed(p, 3):.3f}' if p < 0.01 else f'P = {lm.fixed(p, 2):.2f}'


def save(fig, name):
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(os.path.join(HERE, f'{name}.{ext}'), dpi=300 if ext == 'png' else None, facecolor=SURFACE)
    plt.close(fig)
    print(f'wrote {name}.png/.pdf/.svg')


def condition_legend():
    return [Patch(facecolor=lm.COLOR[e], label=lm.LABEL[e]) for e in (CODE, GAL)]


# ---------------------------------------------------------------- figures
def draw_usage(t):
    height = 6.6
    fig, axes = plt.subplots(1, 3, figsize=(13.33, height))
    y = header(fig, height, 'Galaxy runs use 3–9× the tokens of custom code on BixBench and CompBioBench',
               'Bars: median tokens per run (input including cached context, plus output); whiskers: interquartile range. '
               'Above each pair: Galaxy ÷ custom code, the geometric\nmean over tasks of the ratio of their mean tokens '
               '(replicates averaged), with the paired cluster sign-flip test, Holm-adjusted over the 12 model '
               'comparisons:\n* adj. P < 0.05, ** < 0.01, *** < 0.001, ns not significant. Under each panel: the same '
               'ratio for the four models together, and the share of input tokens read from the cache.',
               legend=condition_legend())
    fig.subplots_adjust(left=0.06, right=0.99, top=1 - (y + 0.45) / height, bottom=1.15 / height, wspace=0.2)
    W, G = 0.34, 0.02
    for ax, (bm, name, note) in zip(axes, BENCH):
        d = t[(t.benchmark == bm) & (t.cfg != ALL)].set_index('cfg').reindex(CFG)
        top = max(d[f'{CODE}_q3_m'].max(), d[f'{GAL}_q3_m'].max()) * 1.15
        ax.set_xlim(-0.6, len(CFG) - 0.4)
        ax.set_ylim(0, top)
        clean(ax)
        for i, c in enumerate(CFG):
            row = d.loc[c]
            for e, x0 in ((CODE, i - W - G / 2), (GAL, i + G / 2)):
                lm.rounded_bar(ax, x0, W, row[f'{e}_median_m'], lm.COLOR[e])
                ax.plot([x0 + W / 2] * 2, [row[f'{e}_q1_m'], row[f'{e}_q3_m']], color=INK, lw=1.1, zorder=5,
                        solid_capstyle='butt')
            yy = max(row[f'{CODE}_q3_m'], row[f'{GAL}_q3_m']) + top * 0.02
            ax.text(i, yy, f'×{lm.fixed(row.ratio, 1):.1f} {lm.stars(row.p_holm)}', ha='center', va='bottom',
                    fontsize=9.5, color=INK, fontweight='bold')
        ax.set_xticks(range(len(CFG)), [lm.TICK[c] for c in CFG], fontsize=9.5)
        ax.tick_params(axis='x', length=0)
        ax.set_title(name, loc='left', fontweight='bold', color=INK, fontsize=12, pad=8)
        a = t[(t.benchmark == bm) & (t.cfg == ALL)].iloc[0]
        ax.annotate(f'All four models: ×{lm.fixed(a.ratio, 1):.1f} (95% CI {lm.fixed(a.lo, 1):.1f} to '
                    f'{lm.fixed(a.hi, 1):.1f}), {p_text(a.p)}\nCached share of input: custom code '
                    f'{100 * a[f"{CODE}_cached_share"]:.0f}%, Galaxy {100 * a[f"{GAL}_cached_share"]:.0f}%',
                    xy=(0, 0), xycoords='axes fraction', xytext=(0, -38), textcoords='offset points', va='top',
                    fontsize=9, color=INK2, linespacing=1.35)
    axes[0].set_ylabel('Tokens per run (millions)', color=INK)
    save(fig, 'fig4_token_usage')


def draw_accuracy(acc, oc):
    height = 10.2
    fig = plt.figure(figsize=(13.33, height))
    pooled = oc[oc.cfg == ALL].set_index(['benchmark', 'env'])
    y = header(fig, height, 'More tokens do not buy accuracy',
               'a, accuracy against median tokens per run for each model and condition; a grey line joins a model\'s two '
               'conditions. Galaxy always costs more tokens, and its accuracy is\nhigher for some models and lower for '
               'others. b, the same task, model and condition: tokens of the incorrect runs relative to the correct ones, '
               'the geometric mean over\nthe replicate sets that had both outcomes (n sets; at least 3 needed), with a '
               '95% cluster-bootstrap interval. Above 1, failing runs used more tokens. IWC: correct at ≥ 0.99.',
               legend=condition_legend() + [Line2D([], [], marker=MARKER[c], ls='', color=INK2, markersize=7, label=c)
                                            for c in CFG], ncol=6)
    top_a = 1 - (y + 0.55) / height
    h_a, h_b = 3.0 / height, 3.25 / height
    W_ = 0.28
    for j, (bm, name, note) in enumerate(BENCH):
        ax = fig.add_axes([0.06 + j * 0.322, top_a - h_a, W_, h_a])
        d = acc[acc.benchmark == bm]
        for c in CFG:
            a, g = d[(d.cfg == c) & (d.env == CODE)].iloc[0], d[(d.cfg == c) & (d.env == GAL)].iloc[0]
            ax.plot([a.median_tokens_m, g.median_tokens_m], [a.accuracy, g.accuracy], color='#c8c8c8', lw=1.2, zorder=1)
            for row, e in ((a, CODE), (g, GAL)):
                ax.scatter(row.median_tokens_m, row.accuracy, marker=MARKER[c], s=70, color=lm.COLOR[e],
                           edgecolor=SURFACE, linewidth=1.2, zorder=3)
        ax.set_xscale('log')
        lo_x, hi_x = d.median_tokens_m.min() / 1.6, d.median_tokens_m.max() * 1.6
        ax.set_xlim(lo_x, hi_x)
        ticks = [v for v in (0.25, 0.5, 1, 2, 4, 8, 16) if lo_x <= v <= hi_x]
        ax.set_xticks(ticks, [f'{v:g}' for v in ticks])
        ax.xaxis.set_minor_locator(plt.NullLocator())
        ax.set_ylim(60 if bm == 'IWC' else 75, 101)
        clean(ax, grid='both')
        ax.set_xlabel('Median tokens per run (millions, log scale)', fontsize=9.5, color=INK2)
        ax.set_title(name, loc='left', fontweight='bold', color=INK, fontsize=12, pad=8)
        if j == 0:
            ax.set_ylabel('Accuracy (%)', color=INK)
            fig.text(0.03, top_a + 0.3 / height, 'a', fontsize=15, fontweight='bold', color=INK, va='bottom')
        # b: incorrect / correct within replicate sets
        top_b = top_a - h_a - 1.05 / height
        bx = fig.add_axes([0.06 + j * 0.322 + 0.075, top_b - h_b, W_ - 0.075, h_b])
        o = oc[oc.benchmark == bm]
        rows = CFG + [ALL]
        for i, c in enumerate(rows):
            for e in (CODE, GAL):
                row = o[(o.cfg == c) & (o.env == e)].iloc[0]
                yy = i + (-0.17 if e == CODE else 0.17)
                if np.isnan(row.ratio):
                    bx.text(0.27, yy, f'{lm.LABEL[e]}: {row.sets} set{"s" if row.sets != 1 else ""}, too few',
                            fontsize=8, color=INK2, va='center', ha='left', zorder=4,
                            bbox=dict(facecolor=SURFACE, edgecolor='none', pad=1.0))
                    continue
                bx.plot([row.lo, row.hi], [yy, yy], color=lm.COLOR[e], lw=1.6, zorder=2, solid_capstyle='butt')
                bx.scatter(row.ratio, yy, color=lm.COLOR[e], s=34 if c != ALL else 52, edgecolor=SURFACE, linewidth=1.0,
                           zorder=3, marker='o' if c != ALL else 'D')
                bx.text(min(row.hi, 7) * 1.07, yy, f'n {row.sets}', fontsize=7.5, color=INK2, va='center')
        bx.axhline(len(CFG) - 0.5, color=GRID, lw=1.0)
        bx.axvline(1, color=INK2, lw=0.9, ls=(0, (3, 2)), zorder=1)
        bx.set_xscale('log')
        bx.set_xlim(0.25, 8)
        bx.set_xticks([0.25, 0.5, 1, 2, 4, 8], ['0.25', '0.5', '1', '2', '4', '8'])
        bx.xaxis.set_minor_locator(plt.NullLocator())
        bx.set_ylim(len(rows) - 0.5, -0.5)
        bx.set_yticks(range(len(rows)), CFG + ['All four models'], fontsize=9.5)
        bx.get_yticklabels()[-1].set_fontweight('bold')
        bx.tick_params(axis='y', length=0)
        clean(bx, grid='x')
        bx.set_xlabel('Tokens, incorrect ÷ correct runs (log scale)', fontsize=9.5, color=INK2)
        bx.set_title(name, loc='left', fontweight='bold', color=INK, fontsize=12, pad=8)
        if j == 0:
            fig.text(0.03, top_b + 0.3 / height, 'b', fontsize=15, fontweight='bold', color=INK, va='bottom')
    save(fig, 'fig4_token_accuracy')


PHASE_LABEL = {'start-up': 'Start-up', 'analysis': 'Analysis', 'error correction': 'Error\ncorrection',
               'output preparation': 'Output\npreparation'}


def phase_bars(ax, groups, colors, width, values, labels=None, top=None):
    """Grouped rounded bars by phase: one bar per group, separated by a surface gap."""
    n, G = len(groups), 0.025
    for i, p in enumerate(tp.PHASES):
        for k, gname in enumerate(groups):
            x0 = i - (n * width + (n - 1) * G) / 2 + k * (width + G)
            v = values[gname][p]
            lm.rounded_bar(ax, x0, width, v, colors[k])
            if labels is not None:
                ax.text(x0 + width / 2, v + top * 0.012, labels[gname][p], ha='center', va='bottom', fontsize=8.5,
                        color=INK)


def draw_phases(pr, fit, sens):
    height = 7.3
    fig, axes = plt.subplots(1, 3, figsize=(13.33, height))
    y = header(fig, height, 'Galaxy\'s extra input tokens go to start-up and error correction',
               'Mean input tokens per run (millions) by phase; above each bar, its share of the condition\'s input. '
               'Start-up: before the first analysis step (a Galaxy job, or a command\nthat runs an analysis program or '
               'script). Error correction: after a failed call, until the next successful analysis step. Output '
               'preparation: after the last successful\nanalysis step. Estimated from each run\'s sequence of calls '
               '(each model request re-reads the conversation so far, up to a context cap) and scaled to the run\'s '
               'recorded\ninput tokens. Under the phase names: model requests per run.',
               legend=condition_legend())
    fig.subplots_adjust(left=0.06, right=0.99, top=1 - (y + 0.5) / height, bottom=1.8 / height, wspace=0.2)
    PH = tp.PHASES
    for ax, (bm, name, note) in zip(axes, BENCH):
        d = pr[pr.benchmark == bm]
        means = {e: {p: d[d.env == e][f'tokens_{p}'].mean() / 1e6 for p in PH} for e in (CODE, GAL)}
        totals = {e: d[d.env == e].input_tokens.mean() / 1e6 for e in (CODE, GAL)}
        top = max(max(means[e].values()) for e in (CODE, GAL)) * 1.16
        ax.set_xlim(-0.6, len(PH) - 0.4)
        ax.set_ylim(0, top)
        clean(ax)
        labels = {e: {p: f'{100 * means[e][p] / totals[e]:.0f}%' for p in PH} for e in (CODE, GAL)}
        phase_bars(ax, (CODE, GAL), (lm.COLOR[CODE], lm.COLOR[GAL]), 0.36, means, labels, top)
        req = {e: d[d.env == e][[f'requests_{p}' for p in PH]].mean() for e in (CODE, GAL)}
        ax.set_xticks(range(len(PH)), [f'{PHASE_LABEL[p]}' for p in PH], fontsize=9.5)
        for i, p in enumerate(PH):
            ax.annotate(f'{req[CODE][f"requests_{p}"]:.0f} · {req[GAL][f"requests_{p}"]:.0f}', xy=(i, 0),
                        xycoords=('data', 'axes fraction'), xytext=(0, -38), textcoords='offset points', ha='center',
                        va='top', fontsize=9, color=INK2)
        ax.annotate('model requests per run, custom code · Galaxy', xy=(0.5, 0), xycoords='axes fraction', xytext=(0, -53),
                    textcoords='offset points', ha='center', va='top', fontsize=8.5, color=INK2, style='italic')
        ax.tick_params(axis='x', length=0)
        ax.set_title(name, loc='left', fontweight='bold', color=INK, fontsize=12, pad=8)
        ax.text(0.98, 0.98, f'Input per run:\ncustom code {totals[CODE]:.1f}M\nGalaxy {totals[GAL]:.1f}M',
                transform=ax.transAxes, ha='right', va='top', fontsize=9, color=INK2, linespacing=1.35)
    axes[0].set_ylabel('Input tokens per run (millions)', color=INK)
    fig.text(0.05, 0.025, f'Context model fitted to each run\'s recorded input tokens (rank correlation: custom code '
             f'{fit[CODE]:.2f}, Galaxy {fit[GAL]:.2f}); with the next two best parameter sets no phase share moves by more '
             f'than {lm.fixed(sens, 1):.1f} percentage points.\nCustom code starts a script almost at once, and any script counts as an '
             'analysis step, so its start-up is near zero by definition. In Galaxy, start-up covers finding and '
             'inspecting\ntools, reading the history and staging data before the first job. A failed call is a non-zero '
             'exit, a failed Galaxy job, or a rejected submission.',
             fontsize=8.5, color=INK2, va='bottom', linespacing=1.4)
    save(fig, 'fig4_token_phases')


STAGE_LABEL = {('July', 'before'): 'Round 1: shorter\nskills, prompt\nguidance',
               ('July', 'after'): 'Round 2: submit,\nwait and check\nin one call',
               ('October', 'before'): 'Archived runs\n(round 2)',
               ('October', 'interface'): 'Round 3: compact\nreplies, templates\n(1 replicate)',
               ('October', 'after'): 'Round 3 plus\nlonger waits'}


def draw_reduction(rounds, change, per_task, opr):
    height = 11.6
    fig = plt.figure(figsize=(13.33, height))
    GAL_BEFORE, GAL_MID = lm.tint(lm.COLOR[GAL], 0.45), lm.tint(lm.COLOR[GAL], 0.72)
    shade = {'before': GAL_BEFORE, 'interface': GAL_MID, 'after': lm.COLOR[GAL]}
    y = header(fig, height, 'Interface changes cut Galaxy tokens by more than half, with accuracy unchanged',
               'BixBench-Verified-50. a, b, tokens per complete 50-task run (input including cached context, plus '
               'output; mean of 3 runs per task), Galaxy and custom code side by side at each stage;\nabove each pair: '
               'Galaxy ÷ custom code; in the bars: accuracy. c, each task\'s Galaxy tokens after the changes relative to '
               'before (3 runs each, summed); the bar is the median.\nd, where the October savings came from: mean input '
               'tokens per run by phase (estimated as in the phase figure). Intervals: 95% cluster bootstrap over source '
               'capsules.', legend=[Patch(facecolor=lm.COLOR[CODE], label='Custom code'),
                                      Patch(facecolor=GAL_BEFORE, label='Galaxy before the changes'),
                                      Patch(facecolor=GAL_MID, label='Galaxy, intermediate round'),
                                      Patch(facecolor=lm.COLOR[GAL], label='Galaxy after the changes')])
    top = 1 - (y + 0.5) / height
    h = 3.6 / height
    boxes = {'July': [0.06, top - h, 0.25, h], 'October': [0.37, top - h, 0.37, h]}
    heads = {'July': 'a  July 2026 · GPT-5.5', 'October': 'b  October 2026 · GPT-5.6 Sol'}
    W, G = 0.36, 0.025
    for comp, box in boxes.items():
        ax = fig.add_axes(box)
        d = rounds[rounds.comparison == comp].reset_index(drop=True)
        n = len(d)
        ymax = max(d.galaxy_tokens_m.max(), d.code_tokens_m.max()) * 1.3
        ax.set_xlim(-0.6, n - 0.4)
        ax.set_ylim(0, ymax)
        clean(ax)
        for i, row in d.iterrows():
            gcol = shade[row.stage]
            for x0, v, col, accv in ((i + G / 2, row.galaxy_tokens_m, gcol, row.galaxy_correct),
                                     (i - W - G / 2, row.code_tokens_m, lm.COLOR[CODE], row.code_correct)):
                lm.rounded_bar(ax, x0, W, v, col)
                ax.text(x0 + W / 2, v + ymax * 0.012, f'{v:.0f}M', ha='center', va='bottom', fontsize=8.5, color=INK)
                if not np.isnan(accv):
                    ax.text(x0 + W / 2, ymax * 0.02, f'{accv:.1f}%', ha='center', va='bottom', fontsize=8,
                            color=lm.text_on(lm.to_rgb(col)), fontweight='bold')
            ax.text(i, max(row.galaxy_tokens_m, row.code_tokens_m) + ymax * 0.075, f'×{lm.fixed(row.ratio, 1):.1f}',
                    ha='center', va='bottom', fontsize=10, color=INK, fontweight='bold')
        ax.set_xticks(range(n), [STAGE_LABEL[(comp, s)] for s in d.stage], fontsize=8.5)
        ax.tick_params(axis='x', length=0)
        ax.set_title(heads[comp], loc='left', fontweight='bold', color=INK, fontsize=12, pad=8)
        ch = change[comp]
        ax.text(0.98, 0.97, f'Galaxy, first to last stage:\n{lm.signed(lm.fixed(ch["pct"], 1))}% (95% CI '
                f'{lm.plain(lm.fixed(ch["lo"], 1))} to {lm.plain(lm.fixed(ch["hi"], 1))}%)', transform=ax.transAxes,
                ha='right', va='top', fontsize=9.5, color=INK, fontweight='bold', linespacing=1.3)
        if comp == 'July':
            ax.set_ylabel('Tokens per 50-task run (millions)', color=INK)
        else:
            ax.annotate('Round 3 (1 replicate): accuracy not reported. Custom code: the same archived runs at each stage.',
                        xy=(0, 0), xycoords='axes fraction', xytext=(0, -52), textcoords='offset points', va='top',
                        fontsize=8.5, color=INK2)
    # c: per-task change
    cx = fig.add_axes([0.8, top - h, 0.18, h])
    for k, comp in enumerate(('July', 'October')):
        v = per_task[comp]
        jit = np.random.default_rng(3 + k).uniform(-0.16, 0.16, len(v))
        cx.scatter(k + jit, v, s=16, color=lm.COLOR[GAL], alpha=0.75, edgecolor=SURFACE, linewidth=0.5, zorder=3)
        m = v.median()
        cx.plot([k - 0.26, k + 0.26], [m, m], color=INK, lw=2.2, zorder=4, solid_capstyle='butt')
        cx.text(k + 0.3, m, f'{lm.fixed(m, 2):.2f}', va='center', fontsize=9, color=INK)
        cx.text(k, 3.3, f'{(v < 1).sum()} of {len(v)}\ntasks lower', ha='center', va='top', fontsize=8.5, color=INK2)
    cx.axhline(1, color=INK2, lw=0.9, ls=(0, (3, 2)))
    cx.set_yscale('log')
    cx.set_ylim(0.08, 3.5)
    cx.set_yticks([0.1, 0.25, 0.5, 1, 2], ['0.1', '0.25', '0.5', '1', '2'])
    cx.yaxis.set_minor_locator(plt.NullLocator())
    cx.set_xlim(-0.5, 1.6)
    cx.set_xticks([0, 1], ['July', 'October'])
    cx.tick_params(axis='x', length=0)
    clean(cx)
    cx.set_ylabel('Galaxy tokens, after ÷ before (log)', color=INK, fontsize=9.5)
    cx.set_title('c  Change for each task', loc='left', fontweight='bold', color=INK, fontsize=12, pad=8)
    # d: October by phase
    top_d = top - h - 1.75 / height
    h_d = 3.3 / height
    dx = fig.add_axes([0.06, top_d - h_d, 0.62, h_d])
    groups = ('before', 'after', 'code')
    cols = (GAL_BEFORE, lm.COLOR[GAL], lm.COLOR[CODE])
    means = {s: {p: opr[opr.stage == s][f'tokens_{p}'].mean() / 1e6 for p in tp.PHASES} for s in groups}
    req = {s: {p: opr[opr.stage == s][f'requests_{p}'].mean() for p in tp.PHASES} for s in groups}
    ymax = max(max(v.values()) for v in means.values()) * 1.3
    dx.set_xlim(-0.6, len(tp.PHASES) - 0.4)
    dx.set_ylim(0, ymax)
    clean(dx)
    labels = {s: {p: f'{means[s][p]:.2f}' for p in tp.PHASES} for s in groups}
    phase_bars(dx, groups, cols, 0.25, means, labels, ymax)
    for i, p in enumerate(tp.PHASES):
        b, a = means['before'][p], means['after'][p]
        dx.text(i, max(b, a, means['code'][p]) + ymax * 0.1, 'Galaxy ' + f'{lm.fixed(100 * (a / b - 1), 0):+.0f}%'.replace('-', '−'),
                ha='center', va='bottom', fontsize=9.5, color=INK, fontweight='bold')
        dx.annotate(f'Galaxy {req["before"][p]:.0f} → {req["after"][p]:.0f} requests\ncustom code {req["code"][p]:.0f}',
                    xy=(i, 0), xycoords=('data', 'axes fraction'), xytext=(0, -38), textcoords='offset points',
                    ha='center', va='top', fontsize=8.5, color=INK2, linespacing=1.3)
    dx.set_xticks(range(len(tp.PHASES)), [PHASE_LABEL[p] for p in tp.PHASES], fontsize=9.5)
    dx.tick_params(axis='x', length=0)
    dx.set_ylabel('Input tokens per run (millions)', color=INK)
    dx.set_title('d  Where the October savings came from', loc='left', fontweight='bold', color=INK, fontsize=12, pad=8)
    tot = {s: opr[opr.stage == s].input_tokens.mean() / 1e6 for s in groups}
    dx.legend(handles=[Patch(facecolor=GAL_BEFORE, label=f'Galaxy, archived runs (round 2): {tot["before"]:.2f}M per run'),
                       Patch(facecolor=lm.COLOR[GAL], label=f'Galaxy, round 3 plus longer waits: {tot["after"]:.2f}M'),
                       Patch(facecolor=lm.COLOR[CODE], label=f'Custom code, archived runs: {tot["code"]:.2f}M')],
              loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=False, fontsize=9.5, handlelength=1.2,
              title='Mean input tokens per run', title_fontproperties={'weight': 'bold', 'size': 9.5})
    saved = {p: means['before'][p] - means['after'][p] for p in tp.PHASES}
    total = sum(saved.values())
    dx.annotate('Share of the Galaxy saving:\n' + '\n'.join(
        f'{PHASE_LABEL[p].replace(chr(10), " ").lower()} {100 * saved[p] / total:.0f}%' for p in tp.PHASES),
                xy=(1.02, 0.6), xycoords='axes fraction', va='top', fontsize=9.5, color=INK, linespacing=1.45)
    save(fig, 'fig4_token_reduction')


def main():
    r = load()
    usage = token_usage_table(r)
    usage.round(4).to_csv(os.path.join(HERE, 'fig4_token_usage.csv'), index=False)
    draw_usage(usage)
    acc, oc = accuracy_table(r), outcome_table(r)
    acc.round(4).to_csv(os.path.join(HERE, 'fig4_token_accuracy.csv'), index=False)
    oc.round(4).to_csv(os.path.join(HERE, 'fig4_token_accuracy_outcomes.csv'), index=False)
    draw_accuracy(acc, oc)
    req = run_requests(r)
    grid = fit_context(req)
    grid.round(4).to_csv(os.path.join(HERE, 'fig4_token_phases_fit.csv'), index=False)
    pr = phase_runs(req, grid)
    from scipy.stats import spearmanr
    fit = {e: spearmanr(g.estimated_input, g.input_tokens)[0] for e, g in pr.groupby('env')}
    pt = phase_table(pr)
    sens = 100 * np.max(np.abs(np.r_[pt.share - pt.share_alt1, pt.share - pt.share_alt2]))
    pr.drop(columns=[c for c in pr if c.startswith('alt')]).round(1).to_csv(
        os.path.join(HERE, 'fig4_token_phases_runs.csv'), index=False)
    pt.round(4).to_csv(os.path.join(HERE, 'fig4_token_phases.csv'), index=False)
    draw_phases(pr, fit, sens)
    rounds, change = f5.token_rounds()
    per_task = reduction_runs()
    opr = october_phase_runs(req, grid)
    rounds.round(4).to_csv(os.path.join(HERE, 'fig4_token_reduction.csv'), index=False)
    per_task.round(4).to_csv(os.path.join(HERE, 'fig4_token_reduction_per_task.csv'))
    opt = opr.groupby('stage')[[f'tokens_{p}' for p in tp.PHASES] + [f'requests_{p}' for p in tp.PHASES] +
                               ['input_tokens', 'requests']].mean()
    opt.round(1).to_csv(os.path.join(HERE, 'fig4_token_reduction_phases.csv'))
    draw_reduction(rounds, change, per_task, opr)
    print(grid[grid['rank'] <= 3].round(3).to_string(index=False))
    print(usage[['benchmark', 'cfg', 'ratio', 'lo', 'hi', 'p', 'p_holm']].round(3).to_string(index=False))
    print(oc.round(2).to_string(index=False))
    print(pt.round(3).to_string(index=False))
    print(opt.T.round(0).to_string())
    print({k: round(v, 3) for k, v in fit.items()}, 'sensitivity', round(sens, 2))


if __name__ == '__main__':
    main()
