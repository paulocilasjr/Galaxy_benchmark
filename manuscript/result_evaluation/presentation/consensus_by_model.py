#!/usr/bin/env python3
"""Consensus by model: single run, majority of 3 and at least 1 of 3 correct, per benchmark, model and condition.

The per-model version of the poster's consensus figure. A replicate group is the 3 replicates of one task, model and
condition; a run is correct when accepted (BixBench-Verified-50, CompBioBench) or at output agreement >= 0.99
(IWC-WorkflowBench). Single run: share of runs correct. Majority of 3: share of groups with at least 2 correct runs.
At least 1 of 3 correct: share of groups with a correct run (the ceiling for a validation step that picks it).
Pooled over models these reproduce data/replicate_consensus.csv. Scores: figures/scored_runs.csv (site-matched).
Writes consensus_by_model.{png,svg,pdf} and consensus_by_model.csv next to this script.
"""
import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def find(rel):
    d = HERE
    while d != os.path.dirname(d):
        if os.path.exists(os.path.join(d, rel)):
            return os.path.join(d, rel)
        d = os.path.dirname(d)
    raise FileNotFoundError(rel)


GAL, GAL_FILL = '#1f64c8', '#d6e4f7'            # Galaxy: marker, band (the poster's colours)
CODE, CODE_FILL, CODE_KEY = '#b9772f', '#f2e3d0', '#dcb98f'   # custom code: marker, band, legend swatch
NAVY, INK, INK2, GRID = '#12296b', '#1a1a1a', '#555555', '#e6e6e6'
BENCH = [('BixBench50', 'BixBench-Verified-50', (74, 101.5), range(75, 101, 5)),
         ('CompBio', 'CompBioBench', (74, 101.5), range(75, 101, 5)),
         ('IWC', 'IWC-WorkflowBench', (55, 105), range(60, 101, 10))]
MODELS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro']
CONDS = [('galaxy', 'Galaxy', GAL, GAL_FILL), ('open_ended_code', 'Custom code', CODE, CODE_FILL)]
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
plt.rcParams.update({'font.family': 'Arial', 'font.size': 11, 'svg.fonttype': 'none', 'pdf.fonttype': 42,
                     'axes.edgecolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2})


def table():
    r = pd.read_csv(find(os.path.join('figures', 'scored_runs.csv')))
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    g = r.groupby(['benchmark', 'cfg', 'env', 'task']).ok.agg(['sum', 'size']).reset_index()
    assert (g['size'] == 3).all(), 'every replicate group needs 3 runs'
    return g.groupby(['benchmark', 'cfg', 'env']).agg(
        single_run=('sum', lambda s: 100 * s.sum() / (3 * len(s))),
        majority_of_3=('sum', lambda s: 100 * (s >= 2).mean()),
        at_least_1_of_3=('sum', lambda s: 100 * (s >= 1).mean()),
        tasks=('sum', 'size')).reset_index()


def draw(t):
    # rows: per model, Galaxy then custom code; a gap between models
    ys, labels = {}, []
    y = 0.0
    for m in MODELS:
        for k, (env, *_rest) in enumerate(CONDS):
            ys[(m, env)] = y + 0.42 * k
        labels.append((m, y + 0.21))
        y += 1.25
    fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.7), sharey=True)
    fig.subplots_adjust(left=0.135, right=0.99, top=0.80, bottom=0.13, wspace=0.10)
    for ax, (bm, name, (lo, hi), ticks) in zip(axes, BENCH):
        d = t[t.benchmark == bm].set_index(['cfg', 'env'])
        for m in MODELS:
            for env, _, col, fill in CONDS:
                row, yy = d.loc[(m, env)], ys[(m, env)]
                s, v, c = row.single_run, row.majority_of_3, row.at_least_1_of_3
                ax.fill_betweenx([yy - 0.13, yy + 0.13], min(s, v), c, color=fill, lw=0, zorder=1)
                ax.scatter(c, yy, marker='s', s=78, facecolor='white', edgecolor=col, linewidth=1.6, zorder=3)
                ax.scatter(v, yy, marker='^', s=92, facecolor='white', edgecolor=col, linewidth=1.6, zorder=4)
                ax.scatter(s, yy, marker='o', s=30, color=col, edgecolor='none', zorder=5)
                ax.text(c + (hi - lo) * 0.025, yy, f'{c:.0f}', va='center', fontsize=9.5, color=INK,
                        fontweight='bold')
        ax.set_xlim(lo, hi)
        ax.set_xticks(list(ticks))
        ax.tick_params(axis='x', labelsize=10)
        ax.grid(axis='x', color=GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        for sp in ('top', 'right', 'left'):
            ax.spines[sp].set_visible(False)
        ax.tick_params(axis='y', length=0)
        ax.set_title(name, loc='left', fontsize=13, fontweight='bold', color=NAVY, pad=8)
    axes[0].set_ylim(y - 1.25 + 0.42 + 0.35, -0.35)
    axes[0].set_yticks([p for _, p in labels], [m for m, _ in labels], fontsize=11.5, color=INK)
    for lab in axes[0].get_yticklabels():
        lab.set_fontweight('bold')
    axes[0].tick_params(axis='y', pad=26)
    for (m, env), yy in ys.items():                         # condition swatch beside each row
        col = GAL if env == 'galaxy' else CODE_KEY
        axes[0].plot([-0.045], [yy], marker='s', markersize=7, color=col, transform=axes[0].get_yaxis_transform(),
                     clip_on=False, zorder=6)
    axes[1].set_xlabel('Accuracy (%; IWC-WorkflowBench: correct at output agreement ≥ 0.99)', fontsize=10.5,
                       color=INK2)
    fig.legend(handles=[Line2D([], [], marker='o', ls='', color=INK2, markersize=6.5, label='Single run'),
                        Line2D([], [], marker='^', ls='', markerfacecolor='white', markeredgecolor=INK2,
                               markeredgewidth=1.5, markersize=10, label='Majority of 3'),
                        Line2D([], [], marker='s', ls='', markerfacecolor='white', markeredgecolor=INK2,
                               markeredgewidth=1.5, markersize=9, label='At least 1 of 3 correct'),
                        Line2D([], [], marker='s', ls='', color=GAL, markersize=9, label='Galaxy'),
                        Line2D([], [], marker='s', ls='', color=CODE_KEY, markersize=9, label='Custom code')],
               loc='upper center', bbox_to_anchor=(0.56, 1.0), ncol=5, frameon=False, fontsize=11,
               handletextpad=0.4, columnspacing=1.6)
    for ext in ('png', 'svg', 'pdf'):
        fig.savefig(os.path.join(HERE, f'consensus_by_model.{ext}'), dpi=300, facecolor='white')
    plt.close(fig)


def main():
    t = table()
    t.round(2).to_csv(os.path.join(HERE, 'consensus_by_model.csv'), index=False)
    draw(t)
    print('wrote consensus_by_model.{png,svg,pdf,csv}')


if __name__ == '__main__':
    main()
