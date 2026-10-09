#!/usr/bin/env python3
"""Lab-meeting versions of the Figure 2 accuracy comparison: three bar charts, one per way of computing accuracy.

Accuracy of each model in each condition (custom code, Galaxy), one panel per benchmark. The scores are the archive's
figures/scored_runs.csv: every run as the public results site shows it. A run is correct when accepted
(BixBench-Verified-50, CompBioBench) or, for IWC, at >= 0.99 output agreement (the rule used throughout the figures).

- fig2_raw_numbers: correct runs / all runs, pooled over tasks and replicates (e.g. 137/150).
- fig2_replicate_numbers: accuracy of each replicate (one run of every task), then the mean of the three, with each
  replicate shown and the standard deviation across replicates. Every replicate covers every task, so the mean equals
  the pooled accuracy; what this figure adds is the replicate-to-replicate spread.
- fig2_statistical_numbers: accuracy with 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are
  BixBench source capsules, otherwise tasks), and the Galaxy minus custom-code difference for each model tested with a
  paired cluster sign-flip randomization test (200,000 draws; exact enumeration with 16 or fewer clusters, i.e. IWC),
  Holm-adjusted over the 12 model comparisons. These are the estimators of Figure 2b (figures/make_fig2.py).

- fig2_statistical_unanimous: as fig2_statistical_numbers, with the task as the unit: a model solves a task in a
  condition when at least 2 of its 3 runs are correct (majority), and accuracy is tasks solved / tasks. The intervals,
  paired test and Holm adjustment are the same, applied to the per-task solved / not solved outcome.
- fig2_statistical_unanimous3: the same with the strict rule: a task counts as solved only when all 3 runs are correct.
- fig2_statistical_compilation: the three accuracies side by side (per run, task solved with >= 2 of 3 runs, task
  solved with all 3), for each condition, model and benchmark, with each rule's test in a table under each panel.
- fig2_task_similarity: for each benchmark and model, a Venn diagram of the tasks each condition does not solve: tasks
  that only custom code fails, that both fail, and that only Galaxy fails, so that the errors exclusive to a condition
  sit in its own circle. A condition solves a task when at least 2 of its 3 runs are correct (majority); the tasks on
  each side are named. fig2_task_similarity_counts.csv also gives the counts for "any run correct" and
  "all three runs correct".
- fig2_task_consistency: the same tasks as a 4 x 4 matrix per benchmark and model: how many of a task's 3 runs were
  correct with custom code (x) against with Galaxy (y). The two conditions are paired by task; their replicate numbers
  are independent runs and are not matched to each other.

Each figure is written as PNG (300 dpi), PDF and SVG, with a CSV of the plotted values.
Usage: python result_evaluation/labmeeting_figures/make_labmeeting_figures.py
"""
import os
import re
import sys
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'figures'))
sys.dont_write_bytecode = True
import make_fig2 as f2  # noqa: E402  (scored runs, cluster bootstrap, sign-flip test, Holm)

plt = f2.plt
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.colors import to_rgb  # noqa: E402
from matplotlib.patches import Circle, Patch, PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path  # noqa: E402

CFG = f2.CFG                                   # GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, DeepSeek V4 Pro
CODE, GAL = f2.ENVS
COLOR = {CODE: '#D55E00', GAL: '#0072B2'}      # the manuscript's condition colours (validated, CVD-safe)
LABEL = {CODE: 'Custom code', GAL: 'Galaxy'}
INK, INK2, GRID, SURFACE = '#1a1a1a', '#555555', '#e6e6e6', '#ffffff'
BENCH = [('BixBench50', 'BixBench-Verified-50', '50 tasks'), ('CompBio', 'CompBioBench', '100 tasks'),
         ('IWC', 'IWC', '10 tasks; correct at ≥ 0.99 agreement')]
TICK = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6\nSol', 'GPT-5.6 Luna': 'GPT-5.6\nLuna',
        'DeepSeek V4 Pro': 'DeepSeek\nV4 Pro'}
W, GAP = 0.30, 0.02                            # bar width and the surface gap between the two bars of a model (data units)

plt.rcParams.update({'font.family': 'Arial', 'font.size': 11, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'xtick.labelsize': 10.5, 'ytick.labelsize': 10, 'axes.edgecolor': INK2, 'axes.linewidth': 0.8,
                     'xtick.color': INK2, 'ytick.color': INK2, 'svg.fonttype': 'none', 'pdf.fonttype': 42})


# ---------------------------------------------------------------- numbers
def runs():
    r = f2.load_runs()                         # adds cluster and ok (correct) columns
    return r


def raw(r):
    t = r.groupby(['benchmark', 'cfg', 'env']).ok.agg(correct='sum', runs='size').reset_index()
    t['accuracy'] = 100 * t.correct / t.runs
    return t


def replicates(r):
    per = r.groupby(['benchmark', 'cfg', 'env', 'replicate']).ok.agg(correct='sum', runs='size').reset_index()
    per['accuracy'] = 100 * per.correct / per.runs
    t = per.groupby(['benchmark', 'cfg', 'env']).accuracy.agg(mean='mean', sd='std', lo='min', hi='max').reset_index()
    for k in (1, 2, 3):
        t[f'replicate_{k}'] = per[per.replicate == k].set_index(['benchmark', 'cfg', 'env']).accuracy.reindex(
            pd.MultiIndex.from_frame(t[['benchmark', 'cfg', 'env']])).values
    return t, per


def statistics(r, col='ok'):
    """Accuracy with cluster-bootstrap intervals and the paired sign-flip test, per benchmark and model; `col` is the
    0/1 outcome of each row (a run, or a task under the majority rule)."""
    rows, pooled = [], []
    for bm, _, _ in BENCH:
        d = r[r.benchmark == bm]
        est, draws = f2.boot_means(d, ['cfg', 'env'], value=col)
        lo, hi = f2.ci(draws)
        acc = pd.DataFrame({'accuracy': 100 * est, 'ci95_low': 100 * lo, 'ci95_high': 100 * hi})
        k = d.groupby(['cfg', 'env'])[col].agg(['sum', 'size'])
        for v in f2.paired_difference(d, col, group='cfg'):
            rows.append(dict(benchmark=bm, cfg=v['cfg'],
                             custom_code_correct=int(k.loc[(v['cfg'], CODE), 'sum']),
                             galaxy_correct=int(k.loc[(v['cfg'], GAL), 'sum']), n=int(k.loc[(v['cfg'], GAL), 'size']),
                             custom_code=acc.loc[(v['cfg'], CODE), 'accuracy'],
                             custom_code_low=acc.loc[(v['cfg'], CODE), 'ci95_low'],
                             custom_code_high=acc.loc[(v['cfg'], CODE), 'ci95_high'],
                             galaxy=acc.loc[(v['cfg'], GAL), 'accuracy'],
                             galaxy_low=acc.loc[(v['cfg'], GAL), 'ci95_low'],
                             galaxy_high=acc.loc[(v['cfg'], GAL), 'ci95_high'],
                             difference=v['diff'], difference_low=v['lo'], difference_high=v['hi'],
                             p=v['p'], clusters=v['clusters']))
        v = f2.paired_difference(d, col)[0]
        pooled.append(dict(benchmark=bm, difference=v['diff'], difference_low=v['lo'], difference_high=v['hi'],
                           p=v['p'], clusters=v['clusters']))
    t, pooled = pd.DataFrame(rows), pd.DataFrame(pooled)
    t['p_holm'] = f2.holm(t.p.values)                 # 12 model comparisons
    pooled['p_holm'] = f2.holm(pooled.p.values)       # 3 pooled comparisons
    return t, pooled


def majority_tasks(r, at=None):
    """One row per benchmark, task, model and condition: solved when at least `at` of its 3 runs are correct
    (default SOLVED_AT, the majority; 3 for all three)."""
    t = r.groupby(['benchmark', 'task', 'cluster', 'cfg', 'env']).ok.agg(runs_correct='sum', runs='size').reset_index()
    assert (t.runs == 3).all()
    t['solved'] = (t.runs_correct >= (SOLVED_AT if at is None else at)).astype(int)
    return t


# ---------------------------------------------------------------- drawing
def rounded_bar(ax, x0, width, height, color, radius_px=4.0, edge=None):
    """A column with a rounded data end (radius in display pixels) and a square baseline."""
    if height <= 0:
        return
    fig = ax.figure
    fig.canvas.draw_idle()
    bb = ax.get_window_extent()
    (xmin, xmax), (ymin, ymax) = ax.get_xlim(), ax.get_ylim()
    rx = radius_px * (xmax - xmin) / bb.width
    ry = min(radius_px * (ymax - ymin) / bb.height, height)
    x1 = x0 + width
    verts = [(x0, 0), (x0, height - ry), (x0, height), (x0 + rx, height), (x1 - rx, height), (x1, height),
             (x1, height - ry), (x1, 0), (x0, 0)]
    codes = [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO,
             Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), facecolor=color, edgecolor=edge or 'none', lw=0.8 if edge else 0,
                           zorder=2))


def frame(title, subtitle, top=100, keys=(), height=5.9, bottom=0.14, head=1.42, legend=None, ncol=None,
          legend_at=None):
    fig, axes = plt.subplots(1, 3, figsize=(13.33, height), sharey=True)
    fig.subplots_adjust(left=0.06, right=0.99, top=1 - head / height, bottom=bottom, wspace=0.08)
    fig.text(0.06, 1 - 0.2 / height, title, fontsize=17, fontweight='bold', color=INK, va='top')
    fig.text(0.06, 1 - 0.56 / height, subtitle, fontsize=10.5, color=INK2, va='top', linespacing=1.35)
    handles = legend if legend is not None else [Patch(facecolor=COLOR[e], label=LABEL[e]) for e in (CODE, GAL)] + list(keys)
    loc, anchor = legend_at or ('upper right', (0.99, 1 - 0.15 / height))
    fig.legend(handles=handles, loc=loc, bbox_to_anchor=anchor, ncol=ncol or len(handles), frameon=False, fontsize=11 if legend is None else 10, handlelength=1.2,
               columnspacing=1.4)
    for ax, (bm, name, note) in zip(axes, BENCH):
        ax.set_xlim(-0.55, len(CFG) - 0.45)
        ax.set_ylim(0, top)
        ax.set_yticks([0, 25, 50, 75, 100])
        ax.grid(axis='y', color=GRID, linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
        ax.spines['left'].set_bounds(0, 100)
        ax.set_xticks(range(len(CFG)), [TICK[c] for c in CFG])
        ax.tick_params(axis='x', length=0, pad=6)
        ax.set_title(f'{name}', loc='left', fontweight='bold', color=INK, pad=22)
        ax.text(0, 1.02, note, transform=ax.transAxes, fontsize=9.5, color=INK2, va='bottom')
    axes[0].set_ylabel('Accuracy (%)', color=INK)
    return fig, axes


def whisker(label):
    return Line2D([], [], color=INK, lw=1.2, label=label)


def fixed(x, digits=1):
    """Half-up rounding (0.125 -> 0.13, -1.75 -> -1.8), after removing floating-point noise (-1.7499999... is -1.75);
    Python's own formatting rounds exact halves to even and would print 0.12 and +2.2."""
    d = Decimal(repr(round(float(x), 9))).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)
    return d if d != 0 else abs(d)


def signed(x):
    return f'{fixed(x):+.1f}'.replace('-', '\u2212')


def plain(x):
    return f'{fixed(x):.1f}'.replace('-', '\u2212')


def bar_x(i, env):
    return i - W - GAP / 2 if env == CODE else i + GAP / 2


def inside_label(ax, x, text, height):
    """A label set vertically inside the column, from near the baseline, in white."""
    if height < 22:
        return
    ax.text(x + W / 2, 3, text, rotation=90, ha='center', va='bottom', fontsize=9, color='white', fontweight='bold',
            zorder=4)


def save(fig, name):
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(os.path.join(HERE, f'{name}.{ext}'), dpi=300 if ext == 'png' else None, facecolor=SURFACE)
    plt.close(fig)
    print(f'wrote {name}.png/.pdf/.svg')


def draw_raw(t):
    fig, axes = frame('Accuracy by model: raw counts',
                      'Correct runs out of all runs of each model and condition, pooled over tasks and the three '
                      'replicates (BixBench-Verified-50: 150 runs; CompBioBench: 300; IWC: 30).\nScores as shown on the '
                      'project results site; IWC runs count as correct at ≥ 0.99 output agreement.')
    fig.canvas.draw()
    for ax, (bm, _, _) in zip(axes, BENCH):
        for i, c in enumerate(CFG):
            for e in (CODE, GAL):
                row = t[(t.benchmark == bm) & (t.cfg == c) & (t.env == e)].iloc[0]
                x = bar_x(i, e)
                rounded_bar(ax, x, W, row.accuracy, COLOR[e])
                inside_label(ax, x, f'{int(row.correct)}/{int(row.runs)} · {row.accuracy:.1f}%', row.accuracy)
    save(fig, 'fig2_raw_numbers')


def draw_replicates(t):
    fig, axes = frame('Accuracy by model: mean of the three replicates',
                      'Each replicate is one run of every task; bars give the mean of the three replicate accuracies '
                      '(equal to the pooled accuracy, because every replicate covers every task),\ndots each replicate, '
                      'and whiskers ± 1 standard deviation across replicates. IWC runs count as correct at ≥ 0.99 '
                      'output agreement.',
                      keys=[Line2D([], [], marker='o', ls='', color=INK, markeredgecolor=SURFACE, markersize=6,
                                   label='Replicate'), whisker('± 1 SD')])
    fig.canvas.draw()
    for ax, (bm, _, _) in zip(axes, BENCH):
        for i, c in enumerate(CFG):
            for e in (CODE, GAL):
                row = t[(t.benchmark == bm) & (t.cfg == c) & (t.env == e)].iloc[0]
                x = bar_x(i, e)
                rounded_bar(ax, x, W, row['mean'], COLOR[e])
                xc = x + W / 2
                ax.plot([xc, xc], [row['mean'] - row.sd, row['mean'] + row.sd], color=INK, lw=1.2, zorder=5,
                        solid_capstyle='butt')
                vals = [row[f'replicate_{k}'] for k in (1, 2, 3)]
                ax.scatter([xc - 0.07, xc, xc + 0.07], vals, s=26, color=INK, edgecolor=SURFACE, linewidth=1.2,
                           zorder=6)
                inside_label(ax, x, f'{row["mean"]:.1f}% (SD {row.sd:.1f})', row['mean'])
    save(fig, 'fig2_replicate_numbers')


def p_text(p):
    return 'P < 0.001' if p < 0.001 else f'P = {fixed(p, 2):.2f}'


def stars(p):
    return '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else 'ns'


def below(ax, x, offset_pt, text, **kw):
    """Text under the panel, placed in points below the x-axis so it does not depend on the panel height."""
    kw = {'va': 'top', 'fontsize': 9.5, 'color': INK2, **kw}
    ax.annotate(text, xy=(x, 0), xycoords='axes fraction', xytext=(0, -offset_pt), textcoords='offset points',
                annotation_clip=False, **kw)


STAT_SUBTITLE = ('Bars: accuracy with 95% cluster-bootstrap intervals (20,000 resamples; clusters are BixBench '
                 'source capsules, otherwise tasks). Brackets: Galaxy vs custom code for each model, paired cluster\n'
                 'sign-flip test (200,000 draws; exact for IWC), Holm-adjusted over the 12 model comparisons: '
                 '* adj. P < 0.05, ** < 0.01, *** < 0.001, ns not significant. IWC runs count as correct at ≥ 0.99.')
TASK_SUBTITLE = (
    'Accuracy = tasks solved ÷ tasks (BixBench-Verified-50: 50; CompBioBench: 100; IWC: 10); a model solves a task when '
    '{rule} (IWC runs: ≥ 0.99 agreement).\nBars: 95% cluster-bootstrap intervals (20,000 '
    'resamples; clusters are BixBench source capsules, otherwise tasks). Brackets: Galaxy vs custom code for each model,\n'
    'paired cluster sign-flip test on tasks solved (200,000 draws; exact for IWC), Holm-adjusted over the 12 model '
    'comparisons: * adj. P < 0.05, ** < 0.01, *** < 0.001, ns not significant.')


def draw_statistics(t, pooled, name='fig2_statistical_numbers',
                    title='Accuracy by model, with statistical tests of the condition difference',
                    subtitle=STAT_SUBTITLE, head=1.42, counts=False):
    # an interval that excludes zero while the exact test does not reject: few clusters make the percentile bootstrap
    # too narrow, and significance rests on the test; such lines are marked and explained in a footnote
    dagger = ((pooled.difference_low > 1e-9) | (pooled.difference_high < -1e-9)) & (pooled.p >= 0.05)
    note = 0.3 if dagger.any() else 0.0
    height = 7.4 + head - 1.42 + note
    fig, axes = frame(title, subtitle, top=112, keys=[whisker('95% CI')], height=height,
                      bottom=(2.3 + note) / height, head=head)
    if note:
        fig.text(0.06, 0.12 / height, '† The 95% interval excludes zero but the test does not reject. With few clusters '
                 'that differ between the conditions, the percentile bootstrap is too narrow; significance rests on '
                 'the exact sign-flip test.', fontsize=9.5, color=INK2, va='bottom')
    fig.canvas.draw()
    for ax, (bm, _, _) in zip(axes, BENCH):
        for i, c in enumerate(CFG):
            row = t[(t.benchmark == bm) & (t.cfg == c)].iloc[0]
            tops = []
            for e, key in ((CODE, 'custom_code'), (GAL, 'galaxy')):
                x = bar_x(i, e)
                acc, lo, hi = row[key], row[f'{key}_low'], row[f'{key}_high']
                rounded_bar(ax, x, W, acc, COLOR[e])
                xc = x + W / 2
                ax.plot([xc, xc], [lo, hi], color=INK, lw=1.2, zorder=5, solid_capstyle='butt')
                text = f'{acc:.1f}%'
                if counts:
                    text = f'{row[key + "_correct"]}/{row.n} · {text}'
                inside_label(ax, x, text, acc)
                tops.append(hi)
            y = max(tops) + 3
            xa, xb = bar_x(i, CODE) + W / 2, bar_x(i, GAL) + W / 2
            ax.plot([xa, xa, xb, xb], [y - 1.5, y, y, y - 1.5], color=INK2, lw=0.9, zorder=5)
            mark = stars(row.p_holm)
            ax.text(i, y + (0.4 if mark != 'ns' else 1.0), mark, ha='center', va='bottom', color=INK,
                    fontsize=12 if mark != 'ns' else 9.5, fontweight='bold' if mark != 'ns' else 'normal')
        # the numbers behind the brackets, under the panel
        pr = pooled[pooled.benchmark == bm].iloc[0]
        mark = '†' if dagger[pooled.benchmark == bm].any() else ''
        below(ax, 0, 46, f'All four models: Galaxy − custom code {signed(pr.difference)} pts\n(95% CI '
                         f'{plain(pr.difference_low)} to {plain(pr.difference_high)}{mark}; {p_text(pr.p)}, '
                         f'adj. over 3 benchmarks {p_text(pr.p_holm)})', linespacing=1.3)
        cols = [(0.0, 'left', 'Galaxy − custom code'), (0.56, 'right', 'Δ (pts)'), (0.76, 'right', 'P'),
                (0.96, 'right', 'adj. P')]
        top_pt, step = 84, 13.5
        for x, ha, head in cols:
            below(ax, x, top_pt, head, ha=ha, fontweight='bold')
        for k, c in enumerate(CFG):
            row = t[(t.benchmark == bm) & (t.cfg == c)].iloc[0]
            vals = [c, signed(row.difference), f'{fixed(row.p, 2):.2f}', f'{fixed(row.p_holm, 2):.2f}']
            for (x, ha, _), v in zip(cols, vals):
                below(ax, x, top_pt + step * (k + 1), v, ha=ha)
    save(fig, name)


# ---------------------------------------------------------------- the three rules side by side
RULE_VIEWS = [('per run', 'Per run', 1.0), ('2of3', '≥ 2 of 3', 0.6), ('3of3', 'All 3', 0.3)]   # key, label, tint


def draw_compilation(results):
    """results: {rule key: (per-model table, pooled table)} from statistics()."""
    BW, IG, CG = 0.115, 0.012, 0.05            # bar width, gap inside a condition's three bars, gap between conditions
    T = 3 * BW + 2 * IG
    GW = 2 * T + CG
    legend = [Patch(facecolor=tint(COLOR[e], a), edgecolor=COLOR[e], lw=0.8, label=f'{LABEL[e]}, {label.lower()}')
              for e in (CODE, GAL) for _, label, a in RULE_VIEWS]
    height, head = 8.5, 2.3
    fig, axes = frame('Accuracy under three counting rules',
                      'For each model, three bars per condition: accuracy per run (correct runs ÷ runs), then per task '
                      'with a task solved when ≥ 2 of its 3 runs are correct, then only when all 3 are.\n'
                      'Table: accuracy (%) under each rule, and Δ = Galaxy − custom code for all four models. IWC runs '
                      'count as correct at ≥ 0.99 output agreement.\nPaired cluster sign-flip test of Galaxy vs custom '
                      'code, Holm-adjusted over each rule\'s 12 model comparisons: * adj. P < 0.05, ** < 0.01, '
                      '*** < 0.001; no mark or ns: not significant.\nIntervals and exact P values: '
                      'fig2_statistical_numbers, fig2_statistical_unanimous and fig2_statistical_unanimous3.',
                      height=height, bottom=2.45 / height, head=head, legend=legend, ncol=6,
                      legend_at=('upper left', (0.06 - 0.006, 1 - 1.44 / height)))
    fig.canvas.draw()
    for ax, (bm, _, _) in zip(axes, BENCH):
        for i, c in enumerate(CFG):
            for j, e in enumerate((CODE, GAL)):
                key_e = 'custom_code' if e == CODE else 'galaxy'
                for k, (rk, _, a) in enumerate(RULE_VIEWS):
                    t = results[rk][0]
                    acc = t[(t.benchmark == bm) & (t.cfg == c)].iloc[0][key_e]
                    x = i - GW / 2 + j * (T + CG) + k * (BW + IG)
                    rounded_bar(ax, x, BW, acc, tint(COLOR[e], a), edge=COLOR[e] if a < 1 else None)
        # table: one pair of right-aligned columns (custom code, Galaxy) per rule
        pairs = [(0.36, 0.48), (0.62, 0.74), (0.88, 1.0)]
        top_pt, step = 46, 13
        below(ax, 0, top_pt + step, 'Accuracy (%)', fontweight='bold', fontsize=9)
        for (xc, xg), (_, label, _) in zip(pairs, RULE_VIEWS):
            below(ax, (xc + xg) / 2 - 0.03, top_pt, label, ha='center', fontweight='bold', fontsize=9)
            below(ax, xc, top_pt + step, 'Code', ha='right', fontsize=9)
            below(ax, xg, top_pt + step, 'Galaxy', ha='right', fontsize=9)
        for r_i, c in enumerate(CFG):
            y = top_pt + step * (r_i + 2) + 2
            below(ax, 0, y, c, color=INK, fontsize=9)
            for (xc, xg), (rk, _, _) in zip(pairs, RULE_VIEWS):
                row = results[rk][0]
                row = row[(row.benchmark == bm) & (row.cfg == c)].iloc[0]
                mark = stars(row.p_holm)
                below(ax, xc, y, f'{fixed(row.custom_code):.1f}', ha='right', color=INK, fontsize=9)
                below(ax, xg, y, f'{fixed(row.galaxy):.1f}' + ('' if mark == 'ns' else mark), ha='right', color=INK,
                      fontsize=9)
        y = top_pt + step * (len(CFG) + 2) + 6
        below(ax, 0, y, 'All four, Δ (pts)', color=INK, fontsize=9, fontweight='bold')
        for (xc, xg), (rk, _, _) in zip(pairs, RULE_VIEWS):
            pr = results[rk][1]
            pr = pr[pr.benchmark == bm].iloc[0]
            below(ax, xg, y, f'{signed(pr.difference)} ({stars(pr.p_holm)})', ha='right', color=INK, fontsize=9,
                  fontweight='bold')
    save(fig, 'fig2_statistical_compilation')


# ---------------------------------------------------------------- task overlap (Venn)
SOLVED_AT = 2                                  # a condition solves a task with >= 2 of its 3 runs correct (majority)
RULES = {'any': 1, 'majority': 2, 'all': 3}
MAX_NAMES = 8                                  # list the tasks of a side when there are this many or fewer
# the same four regions seen from the failures: a task solved only with Galaxy is one that only custom code fails
FAILURE_OF = {'galaxy_only': 'custom_code_fails_only', 'neither': 'both_fail', 'custom_code_only': 'galaxy_fails_only',
              'both': 'neither_fails'}


def task_label(bm, task):
    return f'IWC_{task[3:6]}' if bm == 'IWC' else task         # wf_003_host_contamination_removal -> IWC_003


def natural(s):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]


def similarity(r):
    k = r.groupby(['benchmark', 'cfg', 'task', 'env']).ok.agg(['sum', 'size']).unstack('env')
    assert (k['size'] == 3).all().all(), 'every task has three runs per condition'
    t = pd.DataFrame({'custom_code_correct': k['sum'][CODE], 'galaxy_correct': k['sum'][GAL]}).reset_index()
    t.insert(3, 'label', [task_label(b, x) for b, x in zip(t.benchmark, t.task)])
    a, b = t.custom_code_correct >= SOLVED_AT, t.galaxy_correct >= SOLVED_AT
    t['custom_code_solved'], t['galaxy_solved'] = a, b
    t['region'] = np.select([a & b, a & ~b, ~a & b], ['both', 'custom_code_only', 'galaxy_only'], 'neither')
    t['failure_region'] = t.region.map(FAILURE_OF)
    counts = []
    for rule, th in RULES.items():
        a, b = t.custom_code_correct >= th, t.galaxy_correct >= th
        g = pd.DataFrame({'benchmark': t.benchmark, 'cfg': t.cfg, 'custom_code_only': a & ~b, 'both': a & b,
                          'galaxy_only': ~a & b, 'neither': ~a & ~b}).groupby(['benchmark', 'cfg']).sum()
        for solved, failed in FAILURE_OF.items():
            g[failed] = g[solved]
        counts.append(g.reset_index().assign(rule=rule, runs_correct_needed=th))
    counts = pd.concat(counts)[['rule', 'runs_correct_needed', 'benchmark', 'cfg', 'custom_code_only', 'both',
                                'galaxy_only', 'neither'] + list(FAILURE_OF.values())]
    return t, counts


def draw_similarity(t):
    FW, COLW, ROWH, HEAD, BOT, LM = 13.33, 4.2, 2.7, 1.65, 0.1, 0.25
    GAPX = (FW - 2 * LM - 3 * COLW) / 2
    FH = HEAD + len(CFG) * ROWH + BOT
    R, CX = 0.6, 0.38                          # circle radius and centre offset (inches; one data unit = one inch)
    fig = plt.figure(figsize=(FW, FH))
    fig.patch.set_facecolor(SURFACE)
    fig.text(LM / FW, 1 - 0.2 / FH, 'Which tasks each condition does not solve', fontsize=17, fontweight='bold',
             color=INK, va='top')
    fig.text(LM / FW, 1 - 0.56 / FH,
             'For each model, each circle holds the tasks a condition does not solve: tasks only custom code fails '
             '(left), tasks both conditions fail (centre) and tasks only Galaxy fails (right);\nthe tasks on each side '
             'are named below it. A condition solves a task when at least 2 of its 3 runs are correct (IWC: ≥ 0.99 '
             'output agreement). Circles are not drawn to scale;\ntasks solved by both conditions are counted at the '
             'top right.',
             fontsize=10.5, color=INK2, va='top', linespacing=1.35)
    fig.legend(handles=[Patch(facecolor=COLOR[e], alpha=0.35, edgecolor=COLOR[e], lw=1.5,
                              label=f'Not solved with {LABEL[e].lower() if e == CODE else LABEL[e]}')
                        for e in (CODE, GAL)], loc='upper right', bbox_to_anchor=(1 - LM / FW, 1 - 0.15 / FH),
               ncol=2, frameon=False, fontsize=11, handlelength=1.2, columnspacing=1.4)
    for j, (bm, name, note) in enumerate(BENCH):
        x0 = LM + j * (COLW + GAPX)
        n_tasks = t[t.benchmark == bm].task.nunique()
        fig.text(x0 / FW, (FH - HEAD + 0.22) / FH, name, fontsize=13, fontweight='bold', color=INK, va='bottom')
        fig.text((x0 + COLW) / FW, (FH - HEAD + 0.22) / FH, note, fontsize=9.5, color=INK2, va='bottom', ha='right')
        fig.add_artist(Line2D([x0 / FW, (x0 + COLW) / FW], [(FH - HEAD + 0.15) / FH] * 2, color=INK2, lw=0.8))
        for i, c in enumerate(CFG):
            y0 = FH - HEAD - (i + 1) * ROWH
            ax = fig.add_axes([x0 / FW, y0 / FH, COLW / FW, ROWH / FH])
            ax.set_xlim(-COLW / 2, COLW / 2)
            ax.set_ylim(-1.75, ROWH - 1.75)
            ax.axis('off')
            d = t[(t.benchmark == bm) & (t.cfg == c)]
            sides = {reg: sorted(d[d.failure_region == reg].label, key=natural)
                     for reg in ('custom_code_fails_only', 'galaxy_fails_only')}
            both_fail, neither_fails = (d.failure_region == 'both_fail').sum(), (d.failure_region == 'neither_fails').sum()
            for e, cx in ((CODE, -CX), (GAL, CX)):
                ax.add_patch(Circle((cx, 0), R, facecolor=COLOR[e], alpha=0.16, edgecolor='none', zorder=1))
                ax.add_patch(Circle((cx, 0), R, facecolor='none', edgecolor=COLOR[e], lw=1.6, zorder=2))
            ax.text(-COLW / 2 + 0.05, 0.75, c, fontsize=11, fontweight='bold', color=INK, va='center')
            ax.text(COLW / 2 - 0.05, 0.75, f'solved by both: {neither_fails} of {n_tasks}', fontsize=9, color=INK2,
                    va='center', ha='right')
            ax.text(0, 0, str(both_fail), fontsize=16, fontweight='bold', color=INK, ha='center', va='center', zorder=3)
            for reg, sx in (('custom_code_fails_only', -1), ('galaxy_fails_only', 1)):
                names = sides[reg]
                ax.text(sx * R, 0,                   # middle of the side region, between -CX-R and CX-R
                        str(len(names)), fontsize=13, fontweight='bold', color=INK if names else INK2, ha='center',
                        va='center', zorder=3)
                if not names:
                    continue
                text = '\n'.join(names) if len(names) <= MAX_NAMES else f'{len(names)} tasks\n(listed in the CSV)'
                ax.text(sx * 0.1, -R - 0.12, text, fontsize=7.5, color=INK, ha='right' if sx < 0 else 'left',
                        va='top', linespacing=1.25)
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(os.path.join(HERE, f'fig2_task_similarity.{ext}'), dpi=300 if ext == 'png' else None,
                    facecolor=SURFACE)
    plt.close(fig)
    print('wrote fig2_task_similarity.png/.pdf/.svg')


# ---------------------------------------------------------------- runs correct per task (confusion-style matrix)
DIAG = '#4d4d4d'                               # neutral for the diagonal (same number correct in both conditions)


def consistency(sim):
    rows = []
    for bm, _, _ in BENCH:
        for c in CFG:
            d = sim[(sim.benchmark == bm) & (sim.cfg == c)]
            for x in range(4):
                for y in range(4):
                    sel = d[(d.custom_code_correct == x) & (d.galaxy_correct == y)]
                    rows.append(dict(benchmark=bm, cfg=c, custom_code_correct=x, galaxy_correct=y, tasks=len(sel),
                                     task_labels='; '.join(sorted(sel.label, key=natural))))
            m = pd.DataFrame(rows[-16:])
            a, b = m.custom_code_correct >= SOLVED_AT, m.galaxy_correct >= SOLVED_AT
            for mask, reg in ((a & b, 'both'), (a & ~b, 'custom_code_only'), (~a & b, 'galaxy_only'),
                              (~a & ~b, 'neither')):
                assert m[mask].tasks.sum() == (d.region == reg).sum(), (bm, c, reg)   # the blocks are the Venn regions
    return pd.DataFrame(rows)


def tint(color, a):
    return tuple(1 - a + a * v for v in to_rgb(color))


def text_on(rgb):
    """White or ink text, whichever contrasts more with the cell (WCAG relative luminance)."""
    lum = sum(w * (v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4) for w, v in zip((0.2126, 0.7152, 0.0722), rgb))
    ink = sum(w * (v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4)
              for w, v in zip((0.2126, 0.7152, 0.0722), to_rgb(INK)))
    return 'white' if 1.05 / (lum + 0.05) > (lum + 0.05) / (ink + 0.05) else INK


def draw_consistency(m):
    FW, COLW, ROWH, HEAD, BOT, LM = 13.33, 4.2, 2.75, 1.6, 0.1, 0.25
    GAPX = (FW - 2 * LM - 3 * COLW) / 2
    FH = HEAD + len(CFG) * ROWH + BOT
    MS, ML, MB, G = 1.9, 0.62, 0.5, 0.025      # matrix side, its left and bottom offsets (inches); cell gap (data units)
    fig = plt.figure(figsize=(FW, FH))
    fig.patch.set_facecolor(SURFACE)
    fig.text(LM / FW, 1 - 0.2 / FH, 'Runs correct per task: custom code against Galaxy', fontsize=17,
             fontweight='bold', color=INK, va='top')
    fig.text(LM / FW, 1 - 0.56 / FH,
             'Each cell counts the tasks of one model by how many of their 3 runs were correct with custom code (x) and '
             'with Galaxy (y); the conditions are paired by task. Diagonal: the same number\ncorrect in both; above it, '
             'Galaxy got more runs right; below it, custom code did. Shade: number of tasks (log scale). Dashed lines: '
             'the ≥ 2-of-3 rule of fig2_task_similarity\n(bottom left: both fail; top left: only custom code fails; '
             'bottom right: only Galaxy fails; top right: neither fails). IWC runs count as correct at ≥ 0.99 output '
             'agreement.',
             fontsize=10.5, color=INK2, va='top', linespacing=1.35)
    fig.legend(handles=[Patch(facecolor=tint(DIAG, 0.7), label='Same number correct'),
                        Patch(facecolor=tint(COLOR[GAL], 0.7), label='Galaxy more correct'),
                        Patch(facecolor=tint(COLOR[CODE], 0.7), label='Custom code more correct')],
               loc='upper right', bbox_to_anchor=(1 - LM / FW, 1 - 0.15 / FH), ncol=3, frameon=False, fontsize=11,
               handlelength=1.2, columnspacing=1.4)
    for j, (bm, name, note) in enumerate(BENCH):
        x0 = LM + j * (COLW + GAPX)
        fig.text(x0 / FW, (FH - HEAD + 0.22) / FH, name, fontsize=13, fontweight='bold', color=INK, va='bottom')
        fig.text((x0 + COLW) / FW, (FH - HEAD + 0.22) / FH, note, fontsize=9.5, color=INK2, va='bottom', ha='right')
        fig.add_artist(Line2D([x0 / FW, (x0 + COLW) / FW], [(FH - HEAD + 0.15) / FH] * 2, color=INK2, lw=0.8))
        for i, c in enumerate(CFG):
            y0 = FH - HEAD - (i + 1) * ROWH
            d = m[(m.benchmark == bm) & (m.cfg == c)]
            n_tasks = d.tasks.sum()
            fig.text((x0 + 0.05) / FW, (y0 + ROWH - 0.12) / FH, c, fontsize=11, fontweight='bold', color=INK,
                     va='top')
            ax = fig.add_axes([(x0 + ML) / FW, (y0 + MB) / FH, MS / FW, MS / FH])
            ax.set_xlim(-0.5, 3.5)
            ax.set_ylim(-0.5, 3.5)
            for row in d.itertuples():
                x, y, n = row.custom_code_correct, row.galaxy_correct, row.tasks
                base = DIAG if x == y else COLOR[GAL] if y > x else COLOR[CODE]
                a = 0.12 + 0.88 * np.log1p(n) / np.log1p(n_tasks) if n else 0
                fc = tint(base, a) if n else to_rgb('#f3f3f3')
                ax.add_patch(Rectangle((x - 0.5 + G, y - 0.5 + G), 1 - 2 * G, 1 - 2 * G, edgecolor='none',
                                       facecolor=fc, zorder=1))
                if n:
                    ax.text(x, y, str(n), ha='center', va='center', fontsize=10, fontweight='bold',
                            color=text_on(fc), zorder=3)
            for v in (ax.axvline, ax.axhline):
                v(1.5, color=INK2, lw=0.9, ls=(0, (3, 2)), zorder=2)
            ax.set_xticks(range(4))
            ax.set_yticks(range(4))
            ax.tick_params(length=0, labelsize=9, pad=3)
            for sp in ax.spines.values():
                sp.set_visible(False)
            ax.set_xlabel('Custom code: runs correct', fontsize=8.5, color=INK2, labelpad=3)
            ax.set_ylabel('Galaxy: runs correct', fontsize=8.5, color=INK2, labelpad=3)
            same = d[d.custom_code_correct == d.galaxy_correct].tasks.sum()
            gal = d[d.galaxy_correct > d.custom_code_correct].tasks.sum()
            code = d[d.custom_code_correct > d.galaxy_correct].tasks.sum()
            xs, yc = x0 + ML + MS + 0.3, y0 + MB + MS / 2
            for k, (col, text) in enumerate(((DIAG, f'Same: {same} of {n_tasks} ({100 * same / n_tasks:.0f}%)'),
                                             (COLOR[GAL], f'Galaxy more: {gal}'), (COLOR[CODE], f'Custom code more: {code}'))):
                yy = yc + (1 - k) * 0.3
                fig.add_artist(Rectangle(((xs) / FW, (yy - 0.06) / FH), 0.12 / FW, 0.12 / FH,
                                         transform=fig.transFigure, facecolor=tint(col, 0.7), edgecolor='none'))
                fig.text((xs + 0.2) / FW, yy / FH, text, fontsize=9.5, color=INK, va='center')
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(os.path.join(HERE, f'fig2_task_consistency.{ext}'), dpi=300 if ext == 'png' else None,
                    facecolor=SURFACE)
    plt.close(fig)
    print('wrote fig2_task_consistency.png/.pdf/.svg')


def main():
    os.makedirs(HERE, exist_ok=True)
    r = runs()
    assert len(r) == 3840, len(r)
    t_raw = raw(r)
    t_rep, per = replicates(r)
    assert np.allclose(t_rep['mean'].values, t_raw.set_index(['benchmark', 'cfg', 'env']).accuracy
                       .reindex(pd.MultiIndex.from_frame(t_rep[['benchmark', 'cfg', 'env']])).values)
    t_stat, pooled = statistics(r)
    t_raw.round(4).to_csv(os.path.join(HERE, 'fig2_raw_numbers.csv'), index=False)
    t_rep.round(4).to_csv(os.path.join(HERE, 'fig2_replicate_numbers.csv'), index=False)
    t_stat.round(4).to_csv(os.path.join(HERE, 'fig2_statistical_numbers.csv'), index=False)
    pooled.round(4).to_csv(os.path.join(HERE, 'fig2_statistical_numbers_pooled.csv'), index=False)
    draw_raw(t_raw)
    draw_replicates(t_rep)
    draw_statistics(t_stat, pooled)
    sim, counts = similarity(r)
    sim.to_csv(os.path.join(HERE, 'fig2_task_similarity.csv'), index=False)
    counts.to_csv(os.path.join(HERE, 'fig2_task_similarity_counts.csv'), index=False)
    draw_similarity(sim)
    cons = consistency(sim)
    cons.to_csv(os.path.join(HERE, 'fig2_task_consistency.csv'), index=False)
    draw_consistency(cons)
    # last, so that the earlier figures keep their bootstrap and permutation draws
    t_maj, pooled_maj = statistics(majority_tasks(r), col='solved')
    t_maj.round(4).to_csv(os.path.join(HERE, 'fig2_statistical_unanimous.csv'), index=False)
    pooled_maj.round(4).to_csv(os.path.join(HERE, 'fig2_statistical_unanimous_pooled.csv'), index=False)
    draw_statistics(t_maj, pooled_maj, name='fig2_statistical_unanimous',
                    title='Task accuracy by model (task solved when ≥ 2 of 3 runs are correct)',
                    subtitle=TASK_SUBTITLE.format(rule='at least 2 of its 3 runs are correct'), head=1.62,
                    counts=True)
    t_all, pooled_all = statistics(majority_tasks(r, at=3), col='solved')
    t_all.round(4).to_csv(os.path.join(HERE, 'fig2_statistical_unanimous3.csv'), index=False)
    pooled_all.round(4).to_csv(os.path.join(HERE, 'fig2_statistical_unanimous3_pooled.csv'), index=False)
    draw_statistics(t_all, pooled_all, name='fig2_statistical_unanimous3',
                    title='Task accuracy by model (task solved only when all 3 runs are correct)',
                    subtitle=TASK_SUBTITLE.format(rule='all 3 of its runs are correct'), head=1.62, counts=True)
    draw_compilation({'per run': (t_stat, pooled), '2of3': (t_maj, pooled_maj), '3of3': (t_all, pooled_all)})
    allc = counts[counts.rule == 'all'].set_index(['benchmark', 'cfg'])            # agrees with the Venn counts
    for row in t_all.itertuples():
        assert row.custom_code_correct == allc.loc[(row.benchmark, row.cfg), ['custom_code_only', 'both']].sum()
        assert row.galaxy_correct == allc.loc[(row.benchmark, row.cfg), ['galaxy_only', 'both']].sum()
    print(t_stat[['benchmark', 'cfg', 'custom_code', 'galaxy', 'difference', 'p', 'p_holm']].round(3).to_string(index=False))
    print(pooled.round(3).to_string(index=False))
    print(t_maj[['benchmark', 'cfg', 'custom_code_correct', 'galaxy_correct', 'n', 'custom_code', 'galaxy', 'difference',
                 'difference_low', 'difference_high', 'p', 'p_holm']].round(3).to_string(index=False))
    print(pooled_maj.round(3).to_string(index=False))
    print(t_all[['benchmark', 'cfg', 'custom_code_correct', 'galaxy_correct', 'n', 'difference', 'difference_low',
                 'difference_high', 'p', 'p_holm']].round(3).to_string(index=False))
    print(pooled_all.round(3).to_string(index=False))


if __name__ == '__main__':
    main()
