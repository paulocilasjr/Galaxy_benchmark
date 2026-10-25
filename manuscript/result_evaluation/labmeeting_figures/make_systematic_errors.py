#!/usr/bin/env python3
"""Systematic errors (lab meeting): the BixBench-Verified-50 tasks that the fewest runs solved, across both conditions.

For each task, a grid of all 24 primary runs (4 models x Galaxy and custom code x 3 replicates) shows the submitted
answer, coloured by answer, with the accepted runs in green. When every model in both conditions gives the same
answer, or the answer follows the analysis route rather than the model, the error lies in the task, not the agent or
the platform. The explanations come from the task-level trace audit (docs/reports/individual_error_analysis.md, with
trace line numbers) and the integrity audit (analysis/integrity_audit/); grades are those of figures/scored_runs.csv.

Tasks: bix-61-q5 (0 of 24 correct), bix-26-q5 (1 of 24) and bix-54-q7 (2 of 24), the three lowest on BixBench-Verified-50.
Outputs: systematic_errors.{png,pdf,svg} and systematic_errors.csv (every run shown, with its answer and group).
Usage: python manuscript/result_evaluation/labmeeting_figures/make_systematic_errors.py
"""
import os
import sys
import textwrap

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_trajectory_figures as mt  # noqa: E402

from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

plt.rcParams.update({'font.family': ['Arial', 'DejaVu Sans'], 'svg.fonttype': 'none', 'pdf.fonttype': 42})
GAL_C, CODE_C, INK, INK2 = '#1f64c8', '#c8531f', '#1a1a1a', '#555555'
OK_C, CARD = '#2e9e5b', '#f2f3f5'
WRONG = ['#7d8a99', '#d8c39d']                                # first and second wrong answer
MODELS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro']
COLS = [('galaxy', k) for k in (1, 2, 3)] + [('open_ended_code', k) for k in (1, 2, 3)]


def num(fmt):
    def f(a):
        try:
            return fmt.format(float(a))
        except (TypeError, ValueError):
            return None
    return f


TASKS = [
    dict(task='bix-61-q5', what='Ts/Tv ratio of the MDR sample (2 decimals)', reference='2.68',
         label=num('{:.2f}'),
         why=['All 24 runs computed Ts/Tv on the variant file supplied with the task: 48,234 transitions / 18,865 '
              'transversions = 2.56.',
              'The reference (2.68) re-calls variants from the untrimmed reads, a step the question never mentions.',
              'Every model in both conditions agrees, so the task, not the agent or the platform, sets the answer.'],
         key=set()),
    dict(task='bix-26-q5', what='KEGG pathways enriched under iron depletion only', reference='3',
         label=num('{:.0f}'),
         why=['The count follows the analysis route: {g2} of 12 Galaxy runs got 2 with the defaults of Galaxy\'s '
              'enrichment tool, and {c1} of 12 custom-code runs got 1 with their own enrichment code.',
              'The reference depends on enrichment settings the question does not state (gene-set size limits, the '
              'family of tests corrected together).',
              'The one accepted run read the benchmark\'s answer key before answering (†).'],
         key={('DeepSeek V4 Pro', 'galaxy', 3)}),
    dict(task='bix-54-q7', what='Maximum colony area at the optimal strain frequency', reference='184,000–185,000',
         label=num('{:,.0f}'),
         why=['Runs split between two defensible row filters: mixtures only (180,771; {n180} runs) or both pure '
              'strains included (178,984; {n178} runs).',
              'The reference drops one pure strain but keeps the other, a choice the question does not state.',
              'Both accepted runs copied that filter from benchmark sources: the answer key and notebook, or a '
              'BixBench-tuned repository (†).'],
         key={('DeepSeek V4 Pro', 'galaxy', 1), ('DeepSeek V4 Pro', 'open_ended_code', 2)}),
]


def runs_of(task, r):
    d = r[(r.benchmark == 'BixBench50') & (r.task == task)].copy()
    assert len(d) == 24, (task, len(d))
    d['answer'] = [mt.answer(x) for x in d.itertuples()]
    return d


def panel(ax, x0, y0, t, d, x_right):
    """One task: header, a 4 x 6 grid of answers and the explanation, drawn in inch coordinates from (x0, y0)."""
    d = d.assign(shown=[t['label'](a) for a in d.answer])
    wrong = d[d.ok == 0].shown.dropna().value_counts()
    colour = {a: WRONG[min(i, 1)] for i, a in enumerate(wrong.index)}
    n_ok = int(d.ok.sum())
    ax.text(x0, y0, t['task'], fontsize=12.5, fontweight='bold', color=INK, va='top')
    ax.text(x0 + 1.05, y0, f"{t['what']}.   Reference: {t['reference']}", fontsize=10.5, color=INK2, va='top')
    ax.text(x_right, y0, f'correct in {n_ok} of 24 runs', fontsize=10.5, color=OK_C if n_ok else '#b02a2a',
            fontweight='bold', va='top', ha='right')
    cw, ch, gap, lab_w = 0.78, 0.36, 0.22, 1.45
    gx = x0 + lab_w
    top = y0 + 0.95                                           # header, then condition labels, then replicates
    for j, (env, rep) in enumerate(COLS):
        x = gx + j * cw + (gap if env != 'galaxy' else 0)
        ax.text(x + cw / 2, top - 0.06, f'r{rep}', ha='center', va='bottom', fontsize=8.5, color=INK2)
    for env, name, c, j0 in (('galaxy', 'Galaxy', GAL_C, 0), ('open_ended_code', 'Custom code', CODE_C, 3)):
        x = gx + j0 * cw + (gap if j0 else 0)
        ax.add_patch(Rectangle((x + 0.03, top - 0.33), 3 * cw - 0.06, 0.05, fc=c, ec='none'))
        ax.text(x + 1.5 * cw, top - 0.37, name, ha='center', va='bottom', fontsize=10, color=c, fontweight='bold')
    for i, m in enumerate(MODELS):
        y = top + i * ch
        ax.text(gx - 0.1, y + ch / 2, m, ha='right', va='center', fontsize=9.5, color=INK)
        for j, (env, rep) in enumerate(COLS):
            x = gx + j * cw + (gap if env != 'galaxy' else 0)
            row = d[(d.cfg == m) & (d.env == env) & (d.replicate == rep)].iloc[0]
            if row.ok:
                fc, tc, txt = OK_C, 'white', f'✓ {row.shown}'
            elif pd.isna(row.shown):
                fc, tc, txt = 'white', INK2, 'none'
            else:
                fc, tc, txt = colour[row.shown], 'white' if colour[row.shown] == WRONG[0] else INK, row.shown
            ax.add_patch(FancyBboxPatch((x + 0.03, y + 0.03), cw - 0.06, ch - 0.06,
                                        boxstyle='round,pad=0,rounding_size=0.04', fc=fc,
                                        ec='#9aa0a6' if fc == 'white' else 'none', lw=0.6,
                                        ls='--' if fc == 'white' else '-'))
            if (m, env, rep) in t['key']:
                txt += ' †'
            ax.text(x + cw / 2, y + ch / 2, txt, ha='center', va='center', fontsize=8.6 if len(txt) > 8 else 9.5,
                    color=tc, fontweight='bold' if row.ok else 'normal')
    # explanation, to the right of the grid
    counts = dict(g2=int(((d.env == 'galaxy') & (d.shown == '2')).sum()),
                  c1=int(((d.env != 'galaxy') & (d.shown == '1')).sum()),
                  n180=int((d.shown == '180,771').sum()), n178=int((d.shown == '178,984').sum()))
    tx = gx + 6 * cw + gap + 0.35
    ty = top - 0.3
    for line in t['why']:
        wrapped = textwrap.fill(line.format(**counts), 62)
        ax.text(tx + 0.14, ty, wrapped, fontsize=9.3, color=INK, va='top', linespacing=1.3)
        ax.text(tx, ty, '•', fontsize=9.3, color=INK2, va='top')
        ty += 0.19 * (wrapped.count('\n') + 1) + 0.12
    return d.assign(task=t['task'], correct=d.ok.astype(bool), key_read=[(m, e, k) in t['key'] for m, e, k in
                                                                        zip(d.cfg, d.env, d.replicate)])


def main():
    r = mt.f2.load_runs()
    W, Hp, H0 = 12.2, 2.85, 0.85
    H = H0 + Hp * len(TASKS) + 0.45
    fig = plt.figure(figsize=(W, H), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis('off')
    ax.text(0.3, 0.28, 'Systematic errors: the same wrong answer across models and both conditions', fontsize=15,
            fontweight='bold', color=INK, va='top')
    ax.text(0.3, 0.62, 'The three BixBench-Verified-50 tasks solved by the fewest of their 24 runs (4 models × 2 '
            'conditions × 3 replicates). Cells show each run\'s submitted answer; colour marks identical answers.',
            fontsize=10, color=INK2, va='top')
    out = []
    for k, t in enumerate(TASKS):
        y = H0 + k * Hp
        ax.add_patch(FancyBboxPatch((0.2, y + 0.05), W - 0.4, Hp - 0.18, boxstyle='round,pad=0,rounding_size=0.08',
                                    fc=CARD, ec='#d9dbe0', lw=0.8, zorder=0))
        out.append(panel(ax, 0.4, y + 0.22, t, runs_of(t['task'], r), W - 0.45))
    ax.text(0.3, H - 0.2, '✓ accepted by the benchmark   ·   † the run read the benchmark\'s answer key or source before '
            'answering   ·   Sources: task-level trace audit (docs/reports/individual_error_analysis.md) and the '
            'integrity audit', fontsize=8.5, color=INK2, va='center')
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(os.path.join(HERE, f'systematic_errors.{ext}'), dpi=300, facecolor='white')
    plt.close(fig)
    cols = ['task', 'cfg', 'env', 'replicate', 'score', 'correct', 'answer', 'shown', 'key_read']
    pd.concat(out)[cols].rename(columns={'cfg': 'model', 'env': 'condition', 'shown': 'answer_shown'}).to_csv(
        os.path.join(HERE, 'systematic_errors.csv'), index=False)
    print('wrote systematic_errors.{png,pdf,svg,csv}')


if __name__ == '__main__':
    main()
