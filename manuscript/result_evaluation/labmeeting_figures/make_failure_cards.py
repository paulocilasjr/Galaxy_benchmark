#!/usr/bin/env python3
"""Failure cards (lab meeting): one BixBench-Verified-50 task, its accepted answer, and each wrong Galaxy run with its
answer and the reason it went wrong.

Every reason is traced to the run's agent trace (codex_events.jsonl line numbers, listed in CARDS and in the CSV);
grades are those of figures/scored_runs.csv. The accepted answer is the answer of the runs graded correct.

Outputs: card_<task>.{png,pdf,svg} and failure_cards.csv (the runs shown, with their evidence).
Usage: python manuscript/result_evaluation/labmeeting_figures/make_failure_cards.py
"""
import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
TRACES = os.path.join(ROOT, 'runs', 'BixBench_50', 'analysis', '{task}', 'source_snapshots', 'huggingface_traces',
                      'files', '{run}', 'agent_workspace', 'run_trace')
GAL, INK, INK2, WRONG, RIGHT = '#1f64c8', '#1a1a1a', '#555555', '#d62728', '#1a7f3c'
CARD, ROW = '#f2f3f5', '#ffffff'
plt.rcParams.update({'font.family': ['Arial', 'DejaVu Sans'], 'svg.fonttype': 'none', 'pdf.fonttype': 42})

CARDS = [dict(
    task='bix-16-q1', bench='BixBench-Verified-50',
    what='Gene whose expression is most negatively correlated with essentiality.',
    correct='CDKN1A',
    runs=[  # model, replicate, run folder, answer, reason, evidence (trace lines)
        ('DeepSeek V4 Pro', 1, 'galaxy_deepseek_v4_pro_via_codex_r1', 'COX17',
         'SciPy missing in the UDT; its own correlation (ρ = −0.24) accepted',
         "L114 UDT job fails: No module named 'scipy'; L119–120 hand-written correlation ranks COX17 first "
         "(rho -0.238) and is submitted. Correct runs find CDKN1A at rho -0.523 (Luna r1, L58)."),
        ('DeepSeek V4 Pro', 3, 'galaxy_deepseek_v4_pro_via_codex_r3', 'CCND1',
         'correlated with raw gene effect; essentiality not negated',
         "L92–93 correlation tool run with transform_b 'none' on CRISPRGeneEffect; L99 CCND1 most negative "
         "(rho -0.629) on the raw scale. Luna r1, correct, set transform_b 'negate' (L44, L46)."),
        ('GPT-5.6 Luna', 2, 'galaxy_codex_gpt_5_6_luna_r2', 'USP54',
         'text sort read ρ = −9.4×10⁻⁵ as −9.4',
         "L58 sort -k3,3n over the Galaxy correlation table puts USP54 (rho -9.41e-05, p = 0.998) first; L65 "
         "submits it as the minimum."),
    ],
    highlight=2,
)]


def check(card):
    """Grades and run folders must match the archive."""
    r = pd.read_csv(os.path.join(ROOT, 'figures', 'scored_runs.csv'))
    t = r[(r.benchmark == 'BixBench50') & (r.task == card['task']) & (r.env == 'galaxy')]
    wrong = t[t.score < 1]
    assert len(t) == 12, len(t)
    shown = {(m, k) for m, k, *_ in card['runs']}
    assert shown == set(zip(wrong.cfg, wrong.replicate)), (shown, wrong[['cfg', 'replicate']])
    for _, _, run, *_ in card['runs']:
        d = TRACES.format(task=card['task'], run=run)
        assert any(f.startswith('codex_events') for f in os.listdir(d)), d
    return len(wrong), len(t)


def draw(card):
    n_wrong, n_runs = check(card)
    rows = card['runs']
    W, row_h, head_h, pad = 8.0, 0.36, 0.46, 0.12           # W grows to fit the longest line
    H = head_h + row_h * len(rows) + 2 * pad
    fig = plt.figure(figsize=(W, H), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])                         # data units are inches
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis('off')
    renderer = fig.canvas.get_renderer()

    def right(t):                                             # right edge of a text, in data units
        return t.get_window_extent(renderer=renderer).transformed(ax.transData.inverted()).x1

    y = pad + head_h / 2
    t = ax.text(0.22, y, f"{card['task']} ({card['bench']}). {card['what']}", va='center', fontsize=10.5, color=INK2)
    t = ax.text(right(t) + 0.22, y, 'Correct: ', va='center', fontsize=10.5, color=INK2)
    t = ax.text(right(t), y, f"✓ {card['correct']}", va='center', fontsize=10.5, color=RIGHT, fontweight='bold')
    t = ax.text(right(t), y, f'  ·  wrong in {n_wrong} of {n_runs} Galaxy runs', va='center', fontsize=10.5,
                color=INK2)
    ends = [right(t)]
    y0 = pad + head_h
    for i, (model, rep, _, answer, reason, _) in enumerate(rows):
        yc = y0 + row_h * (i + 0.5)
        ax.add_patch(plt.Rectangle((0.22, yc - 0.075), 0.15, 0.15, fc=GAL, ec='none'))
        ax.text(0.5, yc, f'{model} r{rep}', va='center', fontsize=11, color=INK)
        ax.text(2.55, yc, '✗', va='center', fontsize=12, color=WRONG)
        ta = ax.text(2.78, yc, answer, va='center', fontsize=11, color=INK, fontweight='bold')
        ends.append(right(ax.text(max(right(ta) + 0.2, 3.75), yc, reason, va='center', fontsize=11, color=INK)))
    W = max(W, max(ends) + 0.3)                               # widen the card to the longest line
    fig.set_size_inches(W, H)
    ax.set_xlim(0, W)
    ax.add_patch(FancyBboxPatch((0.04, 0.04), W - 0.08, H - 0.08, boxstyle='round,pad=0,rounding_size=0.08',
                                fc=CARD, ec='#d9dbe0', lw=0.8, zorder=0))
    if card.get('highlight') is not None:
        yc = y0 + row_h * (card['highlight'] + 0.5)
        ax.add_patch(FancyBboxPatch((0.14, yc - row_h / 2 + 0.03), W - 0.28, row_h - 0.06,
                                    boxstyle='round,pad=0,rounding_size=0.04', fc=ROW, ec='none', zorder=0.5))
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(os.path.join(HERE, f"card_{card['task']}.{ext}"), dpi=300, facecolor='white')
    plt.close(fig)


def main():
    out = []
    for card in CARDS:
        draw(card)
        for model, rep, run, answer, reason, evidence in card['runs']:
            out.append(dict(task=card['task'], model=model, condition='galaxy', replicate=rep, run=run,
                            answer=answer, correct_answer=card['correct'], reason=reason, evidence=evidence))
        print('wrote', f"card_{card['task']}.{{png,pdf,svg}}")
    pd.DataFrame(out).to_csv(os.path.join(HERE, 'failure_cards.csv'), index=False)


if __name__ == '__main__':
    main()
