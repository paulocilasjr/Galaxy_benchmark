#!/usr/bin/env python3
"""When Galaxy was the problem (lab meeting): tasks that custom code solved in 11 or 12 of 12 runs, where the
task-level trace audit attributes the Galaxy misses to Galaxy itself.

a, every task by runs correct with custom code (x) and in Galaxy (y), out of 12 each; the tasks of b are marked.
b, one row per task: the 24 runs (4 models x Galaxy and custom code x 3 replicates) as correct or wrong, the number
   of failed Galaxy jobs in each Galaxy run, and what went wrong in the wrong Galaxy runs.

The explanations come from docs/reports/individual_error_analysis.md (trace line numbers there); grades from
figures/scored_runs.csv; failed Galaxy jobs per run from the run execution-error table copied from the manuscript
repository (brief_communication/data/run_execution_errors.csv).
Outputs: galaxy_failures.{png,pdf,svg} and galaxy_failures.csv.
Usage: python manuscript/result_evaluation/labmeeting_figures/make_galaxy_failures.py
"""
import os
import textwrap

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
ERRORS = os.path.join(ROOT, 'manuscript', 'manuscript_narrative', 'original_layout', 'brief_communication', 'data',
                      'run_execution_errors.csv')
plt.rcParams.update({'font.family': ['Arial', 'DejaVu Sans'], 'svg.fonttype': 'none', 'pdf.fonttype': 42})
GAL_C, CODE_C, INK, INK2 = '#1f64c8', '#c8531f', '#1a1a1a', '#555555'
OK_C, BAD_C, CARD, DOT = '#2e9e5b', '#d62728', '#f2f3f5', '#9aa3ad'
MODELS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro']
SHORT = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'Sol', 'GPT-5.6 Luna': 'Luna', 'DeepSeek V4 Pro': 'DeepSeek'}
COLS = [('galaxy', k) for k in (1, 2, 3)] + [('open_ended_code', k) for k in (1, 2, 3)]
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
BENCH = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC-derived'}

GROUPS = [
    ('Galaxy execution failed, and the agent switched to a route that gave a different answer', [
        dict(task='bix-31-q2', what='Shrunken log2 fold change of FAM138A with PyDESeq2',
             why='DeepSeek r2, r3: the PyDESeq2 UDT jobs never ran (r2) or wrote empty outputs (r3). Both fell back to '
                 'Galaxy\'s R DESeq2, giving −0.081 and −0.083 (accepted −0.07 to −0.05). The 10 correct Galaxy runs got '
                 'a PyDESeq2 UDT to run, some after one to four failed versions.'),
        dict(task='spatial-sim-q2', what='Cell types biased toward tumour-core spots',
             why='Sol r2: every UDT failed to start ("custom project image is not schedulable"). It rebuilt the analysis '
                 'from about 75 stock-tool jobs and used an adjacency test, which found one of the two cell types. Luna '
                 'r2 also had 14 failed jobs and recovered.'),
        dict(task='gtf-5-utr-median-len-q1', what='Median 5′ UTR, CDS and 3′ UTR lengths of MANE transcripts',
             why='DeepSeek r3: its UDT probes failed, so it rebuilt the task with stock interval tools. The join ignored '
                 'transcript identity and added 6 bp to two of the three medians.'),
    ]),
    ('A Galaxy tool returned a misleading value, and the agent did not check it', [
        dict(task='bix-28-q3', what='Median PhyKIT long-branch score of a gene tree',
             why='Sol r1: the PhyKIT wrapper\'s single non-verbose value is the variance (146.30), not the median '
                 '(−30.46), and the run submitted it. Two DeepSeek runs saw the same value and rejected it.'),
        dict(task='bix-52-q7', what='Rows removed by a methylation filter',
             why='Luna r2, Sol r3: Galaxy\'s filtered table keeps its header line, and the line count included it '
                 '(19,160 instead of 19,159). Luna r3 reported the rows kept instead of removed, an agent error.'),
    ]),
]


def load():
    r = pd.read_csv(os.path.join(ROOT, 'figures', 'scored_runs.csv'))
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    e = pd.read_csv(ERRORS)
    e = e.assign(env=e.track.map({'Galaxy': 'galaxy', 'custom code': 'open_ended_code'}))
    e = e.rename(columns={'task_id': 'task', 'model': 'cfg'})[['task', 'cfg', 'env', 'replicate',
                                                                 'galaxy_jobs_in_error_state']]
    return r.merge(e, on=['task', 'cfg', 'env', 'replicate'], how='left')


def overview(ax, r, shown):
    t = r.groupby(['benchmark', 'task']).apply(
        lambda d: pd.Series({'code': d[d.env != 'galaxy'].ok.sum(), 'galaxy': d[d.env == 'galaxy'].ok.sum()}),
        include_groups=False).reset_index()
    n = t.groupby(['code', 'galaxy']).size().rename('n').reset_index()
    ax.plot([0, 12], [0, 12], color='#c9ced4', lw=1, zorder=1)
    ax.scatter(n.code, n.galaxy, s=n.n * 7 + 8, color=DOT, alpha=0.6, edgecolor='white', lw=0.6, zorder=2)
    for _, x in n[n.n >= 10].iterrows():
        ax.text(x.code, x.galaxy, int(x.n), ha='center', va='center', fontsize=7.5, color=INK, zorder=3)
    hi = t[t.task.isin(shown)].groupby(['code', 'galaxy']).task.apply(list).reset_index()
    ax.scatter(hi.code, hi.galaxy, s=40, facecolor='none', edgecolor=GAL_C, lw=1.6, zorder=4)
    for x in hi.itertuples():                                 # the task numbers of panel b, left of the circle
        keys = ' '.join(str(shown.index(k) + 1) for k in sorted(x.task, key=shown.index))
        ax.text(x.code - 0.38, x.galaxy, keys, ha='right', va='center', fontsize=8.5, color=GAL_C,
                fontweight='bold', zorder=5, bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.85))
    ax.text(3.6, 5.6, 'Galaxy better', fontsize=8, color=INK2, rotation=45, ha='center', va='center')
    ax.text(5.6, 3.6, 'custom code better', fontsize=8, color=INK2, rotation=45, ha='center', va='center')
    ax.set_xlim(-0.6, 12.8)
    ax.set_ylim(-0.6, 12.8)
    ax.set_xticks(range(0, 13, 2))
    ax.set_yticks(range(0, 13, 2))
    ax.set_xlabel('Custom-code runs correct (of 12)', fontsize=9.5, color=INK)
    ax.set_ylabel('Galaxy runs correct (of 12)', fontsize=9.5, color=INK)
    ax.tick_params(labelsize=8.5, colors=INK2)
    for sp in ('top', 'right'):
        ax.spines[sp].set_visible(False)
    ax.set_aspect('equal')
    return t


def task_row(ax, x0, y0, spec, d, bench, number):
    """One row: header block | 4 x 6 grid of runs (failed Galaxy jobs in Galaxy cells) | what went wrong."""
    ng, nc = int(d[d.env == 'galaxy'].ok.sum()), int(d[d.env != 'galaxy'].ok.sum())
    ax.text(x0, y0, str(number), fontsize=9, fontweight='bold', color='white', va='top',
            bbox=dict(boxstyle='circle,pad=0.18', fc=GAL_C, ec='none'))
    ax.text(x0 + 0.28, y0, spec['task'], fontsize=11, fontweight='bold', color=INK, va='top')
    ax.text(x0, y0 + 0.25, textwrap.fill(f"{BENCH[bench]}. {spec['what']}", 40), fontsize=8.3, color=INK2,
            va='top', linespacing=1.25)
    ax.text(x0, y0 + 0.78, f'Custom code {nc}/12', fontsize=9, color=CODE_C, fontweight='bold', va='top')
    ax.text(x0 + 1.32, y0 + 0.78, f'Galaxy {ng}/12', fontsize=9, color=GAL_C, fontweight='bold', va='top')
    cw, ch, gap, lab = 0.29, 0.22, 0.12, 0.62
    gx, top = x0 + 2.65 + lab, y0 + 0.24
    for env, name, c, j0 in (('galaxy', 'Galaxy', GAL_C, 0), ('open_ended_code', 'Custom code', CODE_C, 3)):
        x = gx + j0 * cw + (gap if j0 else 0)
        ax.text(x + 1.5 * cw, top - 0.1, name, ha='center', va='bottom', fontsize=7.5, color=c, fontweight='bold')
        ax.add_patch(Rectangle((x + 0.02, top - 0.08), 3 * cw - 0.04, 0.03, fc=c, ec='none'))
    for i, m in enumerate(MODELS):
        y = top + i * ch
        ax.text(gx - 0.06, y + ch / 2, SHORT[m], ha='right', va='center', fontsize=7.3, color=INK)
        for env, rep in COLS:
            j = COLS.index((env, rep))
            x = gx + j * cw + (gap if env != 'galaxy' else 0)
            row = d[(d.cfg == m) & (d.env == env) & (d.replicate == rep)].iloc[0]
            ax.add_patch(FancyBboxPatch((x + 0.02, y + 0.02), cw - 0.04, ch - 0.04,
                                        boxstyle='round,pad=0,rounding_size=0.025',
                                        fc=OK_C if row.ok else BAD_C, ec='none'))
            jobs = row.galaxy_jobs_in_error_state
            if env == 'galaxy' and pd.notna(jobs) and jobs > 0:
                ax.text(x + cw / 2, y + ch / 2, int(jobs), ha='center', va='center', fontsize=6.6, color='white')
    tx = gx + 6 * cw + gap + 0.3
    ax.text(tx, y0 + 0.02, textwrap.fill(spec['why'], 66), fontsize=8.6, color=INK, va='top', linespacing=1.35)


def main():
    r = load()
    shown = [s['task'] for _, specs in GROUPS for s in specs]
    W, H, row_h = 15.4, 9.3, 1.3
    fig = plt.figure(figsize=(W, H), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis('off')
    ax.text(0.3, 0.25, 'When Galaxy was the problem: custom code solved the task, and Galaxy execution or a Galaxy '
            'tool caused the misses', fontsize=14.5, fontweight='bold', color=INK, va='top')
    ax.text(0.3, 0.6, 'The tasks where the trace audit attributes the Galaxy misses to Galaxy itself. Custom code '
            'solved each in 11 or 12 of 12 runs; Galaxy lost one to three runs per task.', fontsize=10, color=INK2,
            va='top')
    ax.text(0.3, 1.05, 'a', fontsize=13, fontweight='bold', color=INK, va='top')
    ax.text(0.55, 1.07, 'Every task: runs correct in each condition', fontsize=10.5, color=INK, va='top')
    ax_w = 3.9
    ov = fig.add_axes([0.55 / W, 1 - (1.5 + ax_w) / H, ax_w / W, ax_w / H])
    t = overview(ov, r, shown)
    below, above = int((t.galaxy < t.code).sum()), int((t.galaxy > t.code).sum())
    ax.text(0.3, 1.5 + ax_w + 0.55, textwrap.fill(
        f'{len(t)} tasks: Galaxy solved fewer runs than custom code on {below}, the same number on '
        f'{len(t) - below - above} and more on {above}. Bubble area: number of tasks; circled and numbered: the '
        f'tasks in b.', 62),
        fontsize=8.6, color=INK2, va='top', linespacing=1.35)
    x0 = 4.95
    ax.text(x0 - 0.15, 1.05, 'b', fontsize=13, fontweight='bold', color=INK, va='top')
    ax.text(x0 + 0.1, 1.07, 'The 24 runs of each task: green correct, red wrong; numbers are failed Galaxy jobs in '
            'the run', fontsize=10.5, color=INK, va='top')
    y = 1.5
    out = []
    for title, specs in GROUPS:
        ax.text(x0 - 0.1, y, title, fontsize=10, color=GAL_C, fontweight='bold', va='top')
        y += 0.32
        for spec in specs:
            d = r[r.task == spec['task']]
            assert len(d) == 24, spec['task']
            ax.add_patch(FancyBboxPatch((x0 - 0.1, y - 0.06), W - x0 - 0.15, row_h - 0.1,
                                        boxstyle='round,pad=0,rounding_size=0.06', fc=CARD, ec='#d9dbe0', lw=0.7,
                                        zorder=0))
            task_row(ax, x0 + 0.05, y + 0.04, spec, d, d.benchmark.iloc[0], shown.index(spec['task']) + 1)
            out.append(d.assign(group=title))
            y += row_h
        y += 0.1
    ax.text(0.3, H - 0.2, 'Sources: task-level trace audit (docs/reports/individual_error_analysis.md); grades as on the '
            'results site; failed Galaxy jobs from the run execution-error table (no record for DeepSeek r2 on '
            'bix-31-q2, whose jobs never left the queue).', fontsize=8, color=INK2, va='center')
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(os.path.join(HERE, f'galaxy_failures.{ext}'), dpi=300, facecolor='white')
    plt.close(fig)
    cols = ['group', 'benchmark', 'task', 'cfg', 'env', 'replicate', 'score', 'ok', 'galaxy_jobs_in_error_state']
    pd.concat(out)[cols].rename(columns={'cfg': 'model', 'env': 'condition', 'ok': 'correct'}).to_csv(
        os.path.join(HERE, 'galaxy_failures.csv'), index=False)
    t.to_csv(os.path.join(HERE, 'galaxy_failures_tasks.csv'), index=False)
    print('wrote galaxy_failures.{png,pdf,svg,csv} and galaxy_failures_tasks.csv')


if __name__ == '__main__':
    main()
