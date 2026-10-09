#!/usr/bin/env python3
"""Fig. 3 (lab meeting): do the three replicates of a task follow the same trajectory?

The frame is the set of task x model pairs that only Galaxy fails: custom code solves the task (at least 2 of its 3
runs correct) and Galaxy does not (0 or 1 of 3), the right-hand side of fig2_task_similarity. For each pair three groups
of replicates are compared:
- Galaxy, task failed: the three Galaxy runs of the frame pair;
- custom code, task solved: the three custom-code runs of the same pair (same task and model, other condition);
- Galaxy, task solved 3/3: the three Galaxy runs of a matched control pair: same benchmark and model, a task Galaxy
  solved in all three runs, with the closest median number of Galaxy steps (tasks in the frame are never controls).

Each run is reduced to the sequence of analysis steps it executed (trajectory_steps.py), and the three replicates of
a group are compared two by two (3 pairs):
- approach similarity: Jaccard overlap of the sets of step labels (same tools and scripts, whatever the order);
- path similarity: 1 - normalised edit distance between the step sequences, consecutive repeats collapsed (same
  steps in the same order).
A group's value is the mean over its three replicate pairs. Galaxy failed vs custom code is paired by task and model,
Galaxy failed vs Galaxy 3/3 by the matching; both are tested with the paired cluster sign-flip test of Fig. 2
(clusters: frame tasks, since some tasks are in the frame for several models).

Outputs, next to this script:
- fig3_trajectory_similarity.{png,pdf,svg};
- fig3_frame_tasks.csv: the frame pairs with their matched controls and every group's similarity and step counts;
- fig3_frame_runs.csv: every run of the frame and control pairs: score, submitted answer, steps and the step sequence;
- fig3_trajectory_tests.csv: the paired comparisons.
Usage: python result_evaluation/labmeeting_figures/make_trajectory_figures.py
"""
import itertools
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_labmeeting_figures as lm  # noqa: E402  (style, scored runs, sign-flip test via make_fig2)
from trajectory_steps import steps  # noqa: E402

f2, plt = lm.f2, lm.plt
from matplotlib.lines import Line2D  # noqa: E402

BENCH_DIR = {'BixBench50': 'BixBench_50', 'CompBio': 'CompBio', 'IWC': 'IWC'}
CODE, GAL = lm.CODE, lm.GAL
GROUPS = [('code', 'Custom code\ntask solved'), ('fail', 'Galaxy\ntask failed'), ('ctrl', 'Galaxy, matched task\nsolved 3/3')]
GCOLOR = {'code': lm.COLOR[CODE], 'fail': lm.COLOR[GAL], 'ctrl': lm.tint(lm.COLOR[GAL], 0.45)}
GEDGE = {'code': lm.COLOR[CODE], 'fail': lm.COLOR[GAL], 'ctrl': lm.COLOR[GAL]}
MARKER = {'BixBench50': 'o', 'CompBio': 's'}


def ledger(r):
    return os.path.join(ROOT, BENCH_DIR[r.benchmark], 'analysis', r.task, 'job_ledgers', r.env, f'{r.run_id}.json')


def answer(r):
    """The submitted answer: codex_output/answer.txt, else any answer.txt in the run's archived workspace."""
    base = os.path.join(ROOT, BENCH_DIR[r.benchmark], 'analysis', r.task, 'source_snapshots', 'huggingface_traces',
                        'files', r.run_id)
    p = os.path.join(base, 'agent_workspace', 'codex_output', 'answer.txt')
    if not os.path.exists(p):
        found = sorted(os.path.join(d, f) for d, _, fs in os.walk(base) for f in fs if f == 'answer.txt')
        if not found:
            return '(no answer file)'
        p = found[0]
    return ' '.join(open(p, errors='replace').read().split())[:300]


def p_text(p):
    return 'P < 0.001' if p < 0.001 else f'P = {lm.fixed(p, 3):.3f}' if p < 0.01 else f'P = {lm.fixed(p, 2):.2f}'


def collapse(seq):
    return [s for i, s in enumerate(seq) if i == 0 or s != seq[i - 1]]


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def approach(a, b):
    A, B = set(a), set(b)
    return np.nan if not A and not B else len(A & B) / len(A | B)


def path(a, b):
    a, b = collapse(a), collapse(b)
    return np.nan if not a and not b else 1 - edit_distance(a, b) / max(len(a), len(b))


def replicate_similarity(seqs):
    """Mean approach and path similarity over the three replicate pairs."""
    pairs = list(itertools.combinations(seqs, 2))
    return (float(np.nanmean([approach(a, b) for a, b in pairs])), float(np.nanmean([path(a, b) for a, b in pairs])))


# ---------------------------------------------------------------- data
def build():
    runs = f2.load_runs()
    sim = pd.read_csv(os.path.join(HERE, 'fig2_task_similarity.csv'))
    frame = sim[sim.failure_region == 'galaxy_fails_only'].copy()
    frame_tasks = set(frame.task)
    # steps of every Galaxy run of the benchmarks in the frame, and of the custom-code runs used below
    benches = sorted(frame.benchmark.unique())
    gal = runs[(runs.env == GAL) & runs.benchmark.isin(benches)].copy()
    gal['steps'] = [steps(ledger(r), r.env) for r in gal.itertuples()]
    gal['n_steps'] = gal.steps.map(len)
    med = gal.groupby(['benchmark', 'cfg', 'task']).n_steps.median()
    # matched controls: Galaxy 3/3, same benchmark and model, closest median steps (log scale), without replacement
    pool = sim[(sim.galaxy_correct == 3) & ~sim.task.isin(frame_tasks)]
    frame['galaxy_median_steps'] = [med[(r.benchmark, r.cfg, r.task)] for r in frame.itertuples()]
    used, ctrl = set(), {}
    for r in frame.sort_values('galaxy_median_steps', ascending=False).itertuples():
        cands = pool[(pool.benchmark == r.benchmark) & (pool.cfg == r.cfg)]
        cands = cands[[(r.benchmark, r.cfg, t) not in used for t in cands.task]]
        dist = [(abs(np.log1p(med[(r.benchmark, r.cfg, t)]) - np.log1p(r.galaxy_median_steps)), lm.natural(t), t)
                for t in cands.task]
        _, _, best = min(dist)
        used.add((r.benchmark, r.cfg, best))
        ctrl[(r.benchmark, r.cfg, r.task)] = best
    frame['control_task'] = [ctrl[(r.benchmark, r.cfg, r.task)] for r in frame.itertuples()]
    frame['control_median_steps'] = [med[(r.benchmark, r.cfg, r.control_task)] for r in frame.itertuples()]
    # the runs of each group
    keys = {(r.benchmark, r.cfg, r.task): 'fail' for r in frame.itertuples()}
    keys.update({(r.benchmark, r.cfg, r.control_task): 'ctrl' for r in frame.itertuples()})
    pick = runs[[(b, c, t) in keys for b, c, t in zip(runs.benchmark, runs.cfg, runs.task)]].copy()
    pick['role'] = [keys[(b, c, t)] for b, c, t in zip(pick.benchmark, pick.cfg, pick.task)]
    pick['group'] = np.where(pick.env == GAL, pick.role, np.where(pick.role == 'fail', 'code', 'ctrl_code'))
    pick['steps'] = [steps(ledger(r), r.env) for r in pick.itertuples()]
    pick['n_steps'] = pick.steps.map(len)
    pick['n_distinct'] = pick.steps.map(lambda s: len(set(s)))
    pick['sequence'] = pick.steps.map(' > '.join)
    pick['answer'] = [answer(r) for r in pick.itertuples()]
    # similarity per group
    sims = {}
    for (b, c, t, g), d in pick.groupby(['benchmark', 'cfg', 'task', 'group']):
        d = d.sort_values('replicate')
        sims[(b, c, t, g)] = replicate_similarity(list(d.steps)) + (float(d.n_steps.median()),)
    for g in ('fail', 'code', 'ctrl', 'ctrl_code'):
        task_col = 'control_task' if g.startswith('ctrl') else 'task'
        vals = [sims[(r.benchmark, r.cfg, getattr(r, task_col), g)] for r in frame.itertuples()]
        frame[f'{g}_approach'] = [v[0] for v in vals]
        frame[f'{g}_path'] = [v[1] for v in vals]
        frame[f'{g}_median_steps'] = [v[2] for v in vals]
    frame['label'] = [lm.task_label(b, t) for b, t in zip(frame.benchmark, frame.task)]
    order = {b: i for i, (b, _, _) in enumerate(lm.BENCH)}
    idx = sorted(range(len(frame)), key=lambda i: (order[frame.benchmark.iloc[i]], list(lm.CFG).index(frame.cfg.iloc[i]),
                                                  lm.natural(frame.task.iloc[i])))
    frame = frame.iloc[idx].reset_index(drop=True)
    return frame, pick


def tests(frame):
    rows = []
    for metric in ('approach', 'path', 'median_steps'):
        for other, name in (('code', 'Galaxy failed - custom code (same task)'),
                            ('ctrl', 'Galaxy failed - Galaxy 3/3 (matched task)')):
            d = frame[f'fail_{metric}'] - frame[f'{other}_{metric}']
            ok = d.notna()
            clusters = d[ok].groupby(frame.task[ok]).sum()
            rows.append(dict(metric=metric, comparison=name, pairs=int(ok.sum()), clusters=len(clusters),
                             mean_difference=float(d[ok].mean()), median_galaxy_failed=float(frame[f'fail_{metric}'].median()),
                             median_other=float(frame[f'{other}_{metric}'].median()),
                             p=f2.signflip_p(clusters.values)))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- drawing
def draw(frame, t):
    fig, axes = plt.subplots(1, 3, figsize=(13.33, 6.6))
    fig.subplots_adjust(left=0.06, right=0.99, top=0.70, bottom=0.17, wspace=0.28)
    fig.text(0.06, 0.965, 'Do the three replicates of a task follow the same trajectory?', fontsize=17,
             fontweight='bold', color=lm.INK, va='top')
    fig.text(0.06, 0.905,
             f'The {len(frame)} task × model pairs that only Galaxy fails (custom code solves ≥ 2 of 3 runs, Galaxy '
             '0 or 1 of 3), compared with the custom-code runs of the same pairs and with Galaxy runs\non matched tasks '
             'Galaxy solved 3/3 (same benchmark and model, closest median number of Galaxy steps). A step is one '
             'executed Galaxy job or command, labelled by tool or by script\nlibraries. Each dot is one pair: the mean '
             'over its three replicate pairs. Lines join the same pair. P: paired cluster sign-flip test (clusters: '
             'tasks); black bars: medians.',
             fontsize=10.5, color=lm.INK2, va='top', linespacing=1.35)
    handles = [Line2D([], [], marker=MARKER[b], ls='', color=lm.INK2, markersize=7, label=n)
               for b, n in (('BixBench50', 'BixBench-Verified-50'), ('CompBio', 'CompBioBench'))]
    fig.legend(handles=handles, loc='upper right', bbox_to_anchor=(0.99, 0.975), ncol=2, frameon=False, fontsize=10.5)
    panels = [('approach', 'Approach similarity', 'Same tools and scripts\n(Jaccard overlap of step labels)', (0, 1)),
              ('path', 'Path similarity', 'Same steps in the same order\n(1 − normalised edit distance)', (0, 1)),
              ('median_steps', 'Steps per run', 'Median over the three replicates\n(log scale)', None)]
    rng = np.random.default_rng(7)
    jitter = rng.uniform(-0.09, 0.09, len(frame))
    for ax, (metric, title, sub, lim) in zip(axes, panels):
        for i, r in frame.iterrows():
            ys = [r[f'{g}_{metric}'] for g, _ in GROUPS]
            ax.plot([k + jitter[i] for k in range(3)], ys, color='#c8c8c8', lw=0.8, zorder=1)
        for k, (g, _) in enumerate(GROUPS):
            for b in MARKER:
                d = frame[frame.benchmark == b]
                ax.scatter(k + jitter[d.index], d[f'{g}_{metric}'], s=46, marker=MARKER[b], facecolor=GCOLOR[g],
                           edgecolor=lm.SURFACE if g != 'ctrl' else GEDGE[g], linewidth=1.2 if g != 'ctrl' else 1.0,
                           zorder=3)
            m = frame[f'{g}_{metric}'].median()
            ax.plot([k - 0.24, k + 0.24], [m, m], color=lm.INK, lw=2.2, zorder=4, solid_capstyle='butt')
            ax.text(k + 0.27, m, f'{m:.2f}' if metric != 'median_steps' else f'{m:.0f}', va='center', fontsize=9,
                    color=lm.INK, zorder=5)
        ax.set_xticks(range(3), [n for _, n in GROUPS], fontsize=9.5)
        ax.tick_params(axis='x', length=0, pad=6)
        for s in ('top', 'right'):
            ax.spines[s].set_visible(False)
        ax.grid(axis='y', color=lm.GRID, lw=0.8, zorder=0)
        ax.set_axisbelow(True)
        ax.set_xlim(-0.5, 2.75)
        if lim:
            ax.set_ylim(-0.02, 1.22)
            ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
            ax.spines['left'].set_bounds(0, 1)
            top = 1.04
        else:
            ax.set_yscale('log')
            lo, hi = frame[[f'{g}_median_steps' for g, _ in GROUPS]].min().min(), frame[
                [f'{g}_median_steps' for g, _ in GROUPS]].max().max()
            ax.set_ylim(max(lo / 1.6, 0.8), hi * 3.2)
            ax.set_yticks([1, 10, 100], ['1', '10', '100'])
            ax.yaxis.set_minor_locator(plt.NullLocator())
            ax.spines['left'].set_bounds(max(lo / 1.6, 0.8), hi * 1.1)
            top = hi * 1.35
        ax.set_title(title, loc='left', fontweight='bold', color=lm.INK, pad=30, fontsize=12)
        ax.text(0, 1.015, sub, transform=ax.transAxes, fontsize=9.5, color=lm.INK2, va='bottom')
        # brackets: Galaxy failed vs custom code (left), vs Galaxy 3/3 (right)
        for (xa, xb), other, level in (((0, 1), 'code', 0), ((1, 2), 'ctrl', 1)):
            row = t[(t.metric == metric) & (t.comparison.str.contains('custom' if other == 'code' else 'matched'))].iloc[0]
            y = top * (1 + 0.09 * level) if not lim else top + 0.085 * level
            dy = (y * 0.03) if not lim else 0.02
            ax.plot([xa, xa, xb, xb], [y - dy, y, y, y - dy], color=lm.INK2, lw=0.9)
            ax.text((xa + xb) / 2, y + dy * 0.4, p_text(row.p), ha='center', va='bottom', fontsize=9,
                    color=lm.INK)
    axes[0].set_ylabel('Similarity between replicates', color=lm.INK)
    axes[2].set_ylabel('Steps', color=lm.INK)
    fig.text(0.06, 0.03, 'Steps: Galaxy jobs (uploads, fetches and converters excluded) or shell commands (downloads, '
             'installs and file inspection excluded). Custom scripts are labelled by language and imported\nlibraries, '
             'Galaxy user-defined tools by container. The matched controls make the Galaxy comparison fair in length; '
             'custom-code runs take more, finer steps, so their similarity is on a different scale.',
             fontsize=9, color=lm.INK2, va='bottom', linespacing=1.35)
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(os.path.join(HERE, f'fig3_trajectory_similarity.{ext}'), dpi=300 if ext == 'png' else None,
                    facecolor=lm.SURFACE)
    plt.close(fig)
    print('wrote fig3_trajectory_similarity.png/.pdf/.svg')


def main():
    frame, pick = build()
    t = tests(frame)
    cols = ['benchmark', 'cfg', 'task', 'label', 'custom_code_correct', 'galaxy_correct', 'control_task']
    cols += [f'{g}_{m}' for g in ('fail', 'code', 'ctrl', 'ctrl_code') for m in ('approach', 'path', 'median_steps')]
    frame[cols].round(4).to_csv(os.path.join(HERE, 'fig3_frame_tasks.csv'), index=False)
    out = pick.drop(columns=['steps', 'cluster'], errors='ignore')
    out['group'] = out.group.map({'fail': 'Galaxy, task failed', 'code': 'custom code, task solved',
                                  'ctrl': 'Galaxy, matched task solved 3/3', 'ctrl_code': 'custom code, matched task'})
    keep = ['group', 'benchmark', 'cfg', 'task', 'env', 'replicate', 'run_id', 'score', 'ok', 'answer', 'n_steps',
            'n_distinct', 'sequence']
    out[keep].sort_values(['benchmark', 'cfg', 'task', 'env', 'replicate']).to_csv(
        os.path.join(HERE, 'fig3_frame_runs.csv'), index=False)
    t.round(4).to_csv(os.path.join(HERE, 'fig3_trajectory_tests.csv'), index=False)
    draw(frame, t)
    print(frame[['benchmark', 'cfg', 'task', 'control_task', 'fail_median_steps', 'ctrl_median_steps',
                 'code_median_steps', 'fail_approach', 'code_approach', 'ctrl_approach', 'fail_path', 'code_path',
                 'ctrl_path']].round(2).to_string(index=False))
    print(t.round(3).to_string(index=False))


if __name__ == '__main__':
    main()
