#!/usr/bin/env python3
"""Figures for the Brief Communication talk (10 slides), one message per figure, in the outline's terms.

- deck_result1_accuracy: Galaxy - custom code per benchmark, by model and pooled, with 95% intervals (archive
  figures/fig2_source_data.csv, the values of PR #12).
- deck_result2_errors: incorrect BixBench-Verified-50 runs by primary cause, split by how many of the other two
  replicates were correct (replicate_consensus.py: bixbench_causes_by_agreement.csv).
- deck_result3_consensus: single run, majority of 3, at least 1 of 3 correct and majority of 12 runs, per benchmark and
  condition (replicate_consensus.csv).
- deck_result4_tokens: Galaxy / custom-code tokens at each optimization stage on BixBench-Verified-50
  (token_optimization_ratios.csv, PR #14).

Inputs are read from --tables (the outputs of the manuscript's analysis/replicate_consensus.py rerun on PR #12's data, and
PR #14's token tables) and from the archive's figures/fig2_source_data.csv.
Usage: python make_deck_figures.py --tables DIR
"""
import argparse
import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CODE, GAL = '#D55E00', '#0072B2'          # custom code, Galaxy (validated, CVD-safe)
INK, INK2, GRID = '#1a1a1a', '#555555', '#e3e3e3'
plt.rcParams.update({'font.family': 'Arial', 'font.size': 13, 'axes.edgecolor': INK2, 'axes.labelcolor': INK,
                     'xtick.color': INK2, 'ytick.color': INK2, 'svg.fonttype': 'none', 'pdf.fonttype': 42})
MODELS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro']


def clean(ax, grid='x'):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.9, zorder=0)
        ax.set_axisbelow(True)


def save(fig, name):
    for ext in ('png', 'svg'):
        fig.savefig(os.path.join(HERE, f'{name}.{ext}'), dpi=300, facecolor='white', transparent=False)
    plt.close(fig)
    print('wrote', name)


def signed(v, nd=1):
    return f'{v:+.{nd}f}'.replace('-', '−')


def num(v, nd=1):
    return f'{v:.{nd}f}'.replace('-', '−')


# ---------------------------------------------------------------- result 1: accuracy
def result1():
    d = pd.read_csv(os.path.join(ROOT, 'figures', 'fig2_source_data.csv'))
    a = d[d.panel == 'a']
    b = d[(d.panel == 'b') & d.measure.str.contains('mean_score_difference')]
    runs = pd.read_csv(os.path.join(ROOT, 'figures', 'scored_runs.csv'))
    bench = [('BixBench50', 'BixBench-Verified-50', '50 tasks · acceptance', 'percentage points'),
             ('CompBio', 'CompBioBench', '100 tasks · agreement with the key', 'percentage points'),
             ('IWC', 'IWC', '10 tasks · output agreement (0–1)', 'agreement')]
    fig, axes = plt.subplots(1, 3, figsize=(12.3, 4.75))
    fig.subplots_adjust(left=0.13, right=0.985, top=0.64, bottom=0.14, wspace=0.40)
    rows = MODELS + ['All four models']
    for ax, (bm, name, sub, unit) in zip(axes, bench):
        g = b[b.benchmark == bm].copy()
        nd = 1
        if bm == 'IWC':                                  # agreement on its own 0-1 scale, as in the text
            g[['value', 'ci95_low', 'ci95_high']] /= 100
            nd = 3
        r = runs[runs.benchmark == bm]
        if bm == 'IWC':
            vals = r.groupby('env').score.mean()
            code_txt, gal_txt = f'{vals.open_ended_code:.2f}', f'{vals.galaxy:.2f}'
        else:
            vals = 100 * r.groupby('env').score.mean()
            code_txt, gal_txt = f'{vals.open_ended_code:.1f}%', f'{vals.galaxy:.1f}%'
        pad = 0.01 if bm == 'IWC' else 1
        lo = min(g.ci95_low.min(), -4 * pad) - pad
        hi = max(g.ci95_high.max(), 5 * pad) + pad
        ax.axvline(0, color=INK2, lw=1.1, zorder=1)
        for i, m in enumerate(rows):
            row = g[g.model == ('all four' if m == 'All four models' else m)].iloc[0]
            pooled = m == 'All four models'
            y = i + (0.35 if pooled else 0)
            ax.plot([row.ci95_low, row.ci95_high], [y, y], color=INK, lw=2.6 if pooled else 1.6, zorder=2,
                    solid_capstyle='butt')
            ax.scatter(row.value, y, marker='D' if pooled else 'o', s=95 if pooled else 46, color=INK if pooled else 'white',
                       edgecolor=INK, linewidth=1.6, zorder=3)
            if pooled:
                ax.text(hi, y - 0.38, f'{signed(row.value, nd)} ({num(row.ci95_low, nd)} to {num(row.ci95_high, nd)})',
                        ha='right', va='bottom', fontsize=12.5, color=INK, fontweight='bold')
        ax.set_ylim(len(rows) - 0.2, -0.7)
        ax.set_yticks([0, 1, 2, 3, 4.35], rows if ax is axes[0] else [''] * 5, fontsize=12.5)
        if ax is axes[0]:
            ax.get_yticklabels()[-1].set_fontweight('bold')
        ax.tick_params(axis='y', length=0)
        ax.set_xlim(lo, hi)
        clean(ax)
        ax.set_xlabel(f'Galaxy − custom code ({unit})', fontsize=12, color=INK2)
        ax.text(0, 1.47, name, transform=ax.transAxes, fontsize=15.5, fontweight='bold', color=INK, va='bottom')
        ax.text(0, 1.37, sub, transform=ax.transAxes, fontsize=11.5, color=INK2, va='bottom')
        # the two condition values, with a colour key beside the text
        ax.scatter([0.015], [1.21], transform=ax.transAxes, marker='s', s=70, color=CODE, clip_on=False)
        ax.text(0.05, 1.21, f'Custom code  {code_txt}', transform=ax.transAxes, fontsize=13, color=INK, va='center')
        ax.scatter([0.015], [1.09], transform=ax.transAxes, marker='o', s=70, color=GAL, clip_on=False)
        ax.text(0.05, 1.09, f'Galaxy  {gal_txt}', transform=ax.transAxes, fontsize=13, color=INK, va='center')
    save(fig, 'deck_result1_accuracy')


# ---------------------------------------------------------------- result 2: two kinds of errors
CAUSES = [('SPEC', 'Under-specified task or reference answer', 'Benchmark'),
          ('EVALUATOR', 'Scorer rejected a valid answer', 'Benchmark'),
          ('RIGOR', 'No validation of the answer', 'Agent'),
          ('KNOWLEDGE', 'Wrong biological or statistical knowledge', 'Agent'),
          ('PLATFORM', 'Galaxy itself', 'Galaxy'),
          ('HARNESS', 'No answer submitted', '')]
SHADE = {0: '#33414c', 1: '#8796a2', 2: '#cdd5db'}     # one hue, dark to light: 0, 1, 2 other replicates correct


def result2(tables):
    c = pd.read_csv(os.path.join(tables, 'bixbench_causes_by_agreement.csv'))
    t = c.groupby(['primary_cause', 'correct_replicates_in_group']).incorrect_runs.sum().unstack(fill_value=0)
    fig, ax = plt.subplots(figsize=(8.1, 4.7))
    fig.subplots_adjust(left=0.44, right=0.97, top=0.86, bottom=0.14)
    for i, (code, label, group) in enumerate(CAUSES):
        left = 0
        for k in (0, 1, 2):
            v = int(t.loc[code, k]) if code in t.index and k in t.columns else 0
            if v:
                ax.barh(i, v, left=left, height=0.62, color=SHADE[k], edgecolor='white', linewidth=1.5, zorder=2)
                if v >= 5:
                    ax.text(left + v / 2, i, str(v), ha='center', va='center', fontsize=11.5,
                            color='white' if k < 2 else INK, fontweight='bold', zorder=3)
            left += v
        ax.text(left + 1.2, i, str(left), va='center', fontsize=12.5, color=INK, fontweight='bold')
    ax.set_yticks(range(len(CAUSES)), [lab for _, lab, _ in CAUSES], fontsize=12.5)
    ax.tick_params(axis='y', length=0)
    for i, (_, _, group) in enumerate(CAUSES):
        if group and (i == 0 or CAUSES[i - 1][2] != group):
            ax.text(-0.82, i - 0.43, group.upper(), transform=ax.get_yaxis_transform(), fontsize=10.5, color=INK2,
                    fontweight='bold', va='center')
    ax.set_ylim(len(CAUSES) - 0.5, -0.75)
    ax.set_xlim(0, 104)
    clean(ax)
    ax.set_xlabel('Incorrect runs (BixBench-Verified-50, 151 runs, both conditions)', fontsize=12, color=INK2)
    ax.legend(handles=[Patch(facecolor=SHADE[k], label=lab) for k, lab in
                       ((0, 'None: all three wrong'), (1, 'One'), (2, 'Both'))],
              title='Other two replicates correct', title_fontsize=11.5, fontsize=11.5, frameon=False, ncol=3,
              loc='lower left', bbox_to_anchor=(-0.02, 1.0), handlelength=1.2, columnspacing=1.2, alignment='left')
    save(fig, 'deck_result2_errors')


# ---------------------------------------------------------------- result 3: consensus
def result3(tables):
    c = pd.read_csv(os.path.join(tables, 'replicate_consensus.csv'))
    order = [('BixBench-Verified-50', 'Galaxy'), ('BixBench-Verified-50', 'custom code'), ('CompBioBench', 'Galaxy'),
             ('CompBioBench', 'custom code'), ('IWC', 'Galaxy'), ('IWC', 'custom code')]
    fig, ax = plt.subplots(figsize=(8.3, 4.85))
    fig.subplots_adjust(left=0.30, right=0.97, top=0.83, bottom=0.13)
    ys = []
    for i, (bm, tr) in enumerate(order):
        y = i + (0.45 if i >= 2 else 0) + (0.45 if i >= 4 else 0)
        ys.append(y)
        r = c[(c.benchmark == bm) & (c.track == tr)].iloc[0]
        col = GAL if tr == 'Galaxy' else CODE
        single, vote, ceil, twelve = (100 * r[k] for k in ('single_run_accuracy', 'majority_of_3_accuracy',
                                                           'any_of_3_accuracy', 'majority_of_12_accuracy'))
        ax.plot([min(single, vote), ceil], [y, y], color=col, lw=1.2, alpha=0.45, zorder=1)
        ax.fill_betweenx([y - 0.16, y + 0.16], max(single, vote), ceil, color=col, alpha=0.13, lw=0, zorder=1)
        ax.scatter(vote, y, marker='o', s=230, facecolor='white', edgecolor=col, linewidth=2.2, zorder=4)
        ax.scatter(single, y, marker='o', s=70, color=col, edgecolor='none', zorder=5)
        ax.scatter(ceil, y, marker='|', s=420, color=col, linewidth=3.0, zorder=3)
        ax.scatter(twelve, y + 0.3, marker='s', s=45, facecolor='white', edgecolor=INK2, linewidth=1.4, zorder=3)
        ax.text(ceil + 0.55, y - 0.02, f'{ceil:.1f}', va='center', fontsize=11.5, color=INK, fontweight='bold')
    ax.set_yticks(ys, [f'{bm.replace("-Verified-50", "")}  ·  {tr}' for bm, tr in order], fontsize=12.5)
    ax.tick_params(axis='y', length=0)
    ax.set_ylim(ys[-1] + 0.75, -0.6)
    ax.set_xlim(68, 99)
    clean(ax)
    ax.set_xlabel('Accuracy (%; IWC: correct at output agreement ≥ 0.99)', fontsize=12, color=INK2)
    ax.legend(handles=[Line2D([], [], marker='o', ls='', color=INK2, markersize=8.5, label='Single run'),
                       Line2D([], [], marker='o', ls='', markerfacecolor='white', markeredgecolor=INK2,
                              markeredgewidth=2, markersize=13, label='Majority of 3'),
                       Line2D([], [], marker='|', ls='', color=INK2, markersize=16, markeredgewidth=3,
                              label='At least 1 of 3 correct'),
                       Line2D([], [], marker='s', ls='', markerfacecolor='white', markeredgecolor=INK2,
                              markeredgewidth=1.5, markersize=7.5, label='Majority of 12 runs')],
              fontsize=11.5, frameon=False, ncol=4, loc='lower left', bbox_to_anchor=(-0.38, 1.0),
              handlelength=1.0, columnspacing=1.1)
    save(fig, 'deck_result3_consensus')


# ---------------------------------------------------------------- result 4: token cost
def result4(tables):
    t = pd.read_csv(os.path.join(tables, 'token_optimization_ratios.csv')).sort_values('order')
    labels = ['Baseline', 'Round 1:\nprompt\nand skills', 'Round 1,\nrerun with\nreplicates', 'Round 2:\nMCP and\nexecution',
              'Round 2,\nnewer\nmodel', 'Round 3a:\ninterface', 'Round 3b:\nlonger\nwaits']
    x = np.arange(len(t))
    fig, ax = plt.subplots(figsize=(7.7, 4.85))
    fig.subplots_adjust(left=0.10, right=0.98, top=0.93, bottom=0.25)
    ax.axvspan(3.5, 6.5, color='#f2f2f2', zorder=0, lw=0)
    ax.text(1.5, 31, 'GPT-5.5', ha='center', fontsize=11.5, color=INK2)
    ax.text(5.0, 31, 'GPT-5.6 Sol', ha='center', fontsize=11.5, color=INK2)
    ax.axhline(1, color=CODE, lw=1.6, ls=(0, (4, 3)), zorder=1)
    ax.text(-0.42, 1.07, 'custom code = 1×', ha='left', va='bottom', fontsize=11, color=INK2)
    ax.text(-0.42, 0.66, 'Galaxy runs correct:', ha='left', va='center', fontsize=10.5, color=INK2)
    ax.plot(x, t.ratio, color=GAL, lw=2.0, zorder=2, drawstyle='steps-mid', alpha=0.35)
    for xi, r in zip(x, t.itertuples()):
        approx = bool(r.approximate)
        ax.scatter(xi, r.ratio, s=110, marker='o', facecolor='white' if approx else GAL, edgecolor=GAL, linewidth=2.2,
                   zorder=4)
        txt = f'~{r.ratio:.0f}×' if approx else f'{r.ratio:.2f}×'
        ax.text(xi, r.ratio * 1.16, txt, ha='center', va='bottom', fontsize=13, color=INK, fontweight='bold')
        if not np.isnan(r.galaxy_correct):
            ax.text(xi, 0.66, f'{int(r.galaxy_correct)}/{int(r.galaxy_runs)}', ha='center', va='center',
                    fontsize=11, color=INK, fontweight='bold')
    ax.set_yscale('log')
    ax.set_ylim(0.58, 42)
    ax.set_yticks([1, 2, 5, 10, 20], ['1×', '2×', '5×', '10×', '20×'])
    ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.set_xlim(-0.5, len(t) - 0.5)
    ax.set_xticks(x, labels, fontsize=11)
    ax.tick_params(axis='x', length=0)
    clean(ax, grid='y')
    ax.set_ylabel('Galaxy ÷ custom code, total tokens', fontsize=12, color=INK)
    save(fig, 'deck_result4_tokens')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--tables', required=True)
    a = p.parse_args()
    result1()
    result2(a.tables)
    result3(a.tables)
    result4(a.tables)


if __name__ == '__main__':
    main()
