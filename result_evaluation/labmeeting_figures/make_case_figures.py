#!/usr/bin/env python3
"""Fig. 3 case studies (lab meeting): why the same model reached the correct answer with custom code but not in Galaxy.

Each case is one task x model pair from the frame of fig3_trajectory_similarity (custom code solves the task, Galaxy
does not). The model demonstrably can solve the task, so the cases are read as lapses of rigor in the Galaxy runs:
a check, or a closer reading of the question, that would have put the run back on the path the same model took in
custom code. Every statement in a figure is traced to the run's agent trace (codex_events.jsonl line numbers) or to
its job ledger, and the answers and scores are those of figures/scored_runs.csv.

Each figure has
- a, the six runs of the model (three Galaxy, three custom code) as step timelines, the submitted answer and its grade;
- b, a case-specific panel that puts every submitted answer against the quantity the question asks for;
- c, what happened in Galaxy, the check that was missing, and what the custom-code runs did.

Outputs: fig3_case<k>_<task>.{png,pdf,svg} and fig3_cases.csv (the runs shown, with answers and step sequences).
Usage: python result_evaluation/labmeeting_figures/make_case_figures.py   (after make_trajectory_figures.py)
"""
import os
import sys
import textwrap

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import make_labmeeting_figures as lm  # noqa: E402

plt = lm.plt
plt.rcParams['font.family'] = ['Arial', 'DejaVu Sans']        # DejaVu Sans supplies ✓ and ✗
from matplotlib.ticker import MaxNLocator  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch, Rectangle  # noqa: E402

CODE, GAL = lm.CODE, lm.GAL
INK, INK2, SURFACE, GRID = lm.INK, lm.INK2, lm.SURFACE, lm.GRID
UTILITIES = {'Cut1', 'Filter1', 'Grep1', 'Grouping1', 'join1', 'sort1', 'cat1', 'Count1', 'wc_gnu', 'mergeCols1',
             'Paste1', 'Summary_Statistics1', 'table_compute', 'filter_tabular', 'datamash_ops', 'column_maker',
             'Add_a_column1', 'awk', 'sed', 'grep', 'sort', 'cut', 'uniq', 'tr', 'jq', 'datamash', 'join', 'paste', 'rg',
             'perl', 'bc', 'Remove beginning1', 'Show beginning1', 'Convert characters1'}
KINDS = [('tool', 'Named tool', 1.0), ('script', 'Script or UDT', 0.55), ('utility', 'Table or text utility', 0.25)]
KIND_NAME = {GAL: {'tool': 'named tool', 'script': 'UDT', 'utility': 'table or text utility'},
             CODE: {'tool': 'named tool', 'script': 'script', 'utility': 'table or text utility'}}
SHORT = {'Filter1': 'Filter', 'wc_gnu': 'wc', 'table_compute': 'Compute', 'filter_tabular': 'FilterTab',
         'datamash_ops': 'Datamash', 'Cut1': 'Cut', 'sed': 'sed', 'awk': 'awk'}


def used_kinds(pairs):
    """(env, kind) present among (env, sequence) pairs."""
    out = set()
    for env, seq in pairs:
        for lab in (seq.split(' > ') if isinstance(seq, str) and seq else []):
            out.add((env, kind(lab)))
    return out


def kind(label):
    if label.startswith(('UDT', 'py', 'R:')) or label in ('R', 'python', 'bash'):
        return 'script'
    if label.split(' ')[0] in UTILITIES or label.startswith('tp_'):
        return 'utility'
    return 'tool'


def wrap(text, width):
    return '\n'.join('\n'.join(textwrap.wrap(p, width)) if p else '' for p in text.split('\n'))


# ---------------------------------------------------------------- shared drawing
def lanes(ax, runs, marks):
    """One lane per run: its steps as blocks (colour = condition, shade = kind), then its answer and grade."""
    order = [(GAL, k) for k in (1, 2, 3)] + [(CODE, k) for k in (1, 2, 3)]
    n_max = max(1, max(len(str(s).split(' > ')) if isinstance(s, str) else 0 for s in runs.sequence))
    ax.set_xlim(-0.3, n_max * 1.45 + 3)                       # room right of the steps for the callouts
    ax.set_ylim(len(order) - 0.4, -0.9)
    for y, (env, rep) in enumerate(order):
        r = runs[(runs.env == env) & (runs.replicate == rep)].iloc[0]
        seq = r.sequence.split(' > ') if isinstance(r.sequence, str) and r.sequence else []
        for i, lab in enumerate(seq):
            a = dict((k, s) for k, _, s in KINDS)[kind(lab)]
            ax.add_patch(Rectangle((i + 0.06, y - 0.32), 0.88, 0.64, facecolor=lm.tint(lm.COLOR[env], a),
                                   edgecolor=lm.COLOR[env] if a < 1 else 'none', lw=0.6, zorder=2))
        if not seq:
            ax.text(0.1, y, 'no Galaxy job: answer submitted without running an analysis step', va='center',
                    fontsize=8.5, color=INK2, style='italic')
        name = f'{"Galaxy" if env == GAL else "Custom code"} r{rep}'
        ax.text(-0.9, y, name, ha='right', va='center', fontsize=9.5, color=INK)
        ok = r.ok == 1
        ax.annotate(f'{"✓" if ok else "✗"}  {r.answer_short}', xy=(1.0, y), xycoords=('axes fraction', 'data'),
                    xytext=(8, 0), textcoords='offset points', va='center', fontsize=9.5,
                    color=INK, fontweight='bold' if not ok else 'normal', annotation_clip=False)
        for (e, k, step, text) in marks:
            if e == env and k == rep:
                x = len(seq) if step == 'end' else step
                ax.text(x + 0.25, y, '◀ ' + text, va='center', fontsize=8.5, color=INK, style='italic', zorder=6)
    ax.axhline(2.5, color=GRID, lw=1.0)
    ax.set_yticks([])
    ax.set_xlabel('Analysis step (Galaxy job or command), in execution order', fontsize=9, color=INK2)
    ticks = [t for t in MaxNLocator(nbins=6, integer=True, min_n_ticks=2).tick_values(1, n_max) if 1 <= t <= n_max]
    ax.set_xticks([t - 0.5 for t in ticks], [str(int(t)) for t in ticks])
    ax.spines['bottom'].set_bounds(0, n_max)
    ax.tick_params(axis='x', labelsize=8.5, colors=INK2)
    for s in ('top', 'right', 'left'):
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_color(INK2)


def notes(fig, box, columns):
    """Panel c: three text columns, each with a heading."""
    x0, y0, w, h = box
    cw = w / len(columns)
    for i, (head, body) in enumerate(columns):
        fig.add_artist(FancyBboxPatch((x0 + i * cw + 0.004, y0), cw - 0.012, h, boxstyle='round,pad=0,rounding_size=0.008',
                                      transform=fig.transFigure, facecolor='#f5f5f5', edgecolor='none', zorder=0))
        fig.text(x0 + i * cw + 0.014, y0 + h - 0.018, head, fontsize=10.5, fontweight='bold', color=INK, va='top')
        fig.text(x0 + i * cw + 0.014, y0 + h - 0.055, body, fontsize=9, color=INK, va='top', linespacing=1.35)


def frame(case, used=None, height=8.4):
    fig = plt.figure(figsize=(13.33, height))
    fig.patch.set_facecolor(SURFACE)
    inch = 1 / height                                          # figure fraction of one inch
    fig.text(0.04, 1 - 0.21 * inch, f'Case {case["number"]} · {case["task"]} ({case["bench_name"]}), {case["model"]}',
             fontsize=11, color=INK2, va='top')
    fig.text(0.04, 1 - 0.44 * inch, case['title'], fontsize=17, fontweight='bold', color=INK, va='top')
    fig.text(0.04, 1 - 0.80 * inch, wrap('Question: ' + case['question'], 190), fontsize=10, color=INK2, va='top',
             linespacing=1.35, style='italic')
    handles = [Patch(facecolor=lm.tint(lm.COLOR[e], a), edgecolor=lm.COLOR[e], lw=0.6,
                     label=f'{"Galaxy" if e == GAL else "Custom code"}: {KIND_NAME[e][k]}')
               for e in (GAL, CODE) for k, _, a in KINDS if used is None or (e, k) in used]
    fig.legend(handles=handles, loc='upper left', bbox_to_anchor=(0.04, 1 - 1.30 * inch), ncol=len(handles),
               frameon=False, fontsize=9, handlelength=1.0, columnspacing=1.2)
    return fig


def save(fig, case):
    name = f'fig3_case{case["number"]}_{case["task"]}'
    for ext in ('png', 'pdf', 'svg'):
        fig.savefig(os.path.join(HERE, f'{name}.{ext}'), dpi=300 if ext == 'png' else None, facecolor=SURFACE)
    plt.close(fig)
    print(f'wrote {name}.png/.pdf/.svg')


def panel_label(fig, x, y, letter, text):
    fig.text(x, y, letter, fontsize=13, fontweight='bold', color=INK, va='bottom')
    fig.text(x + 0.018, y, text, fontsize=11, fontweight='bold', color=INK, va='bottom')


# ---------------------------------------------------------------- case 1: bix-52-q7, GPT-5.6 Luna
def panel_bix52(ax, runs):
    """What each submitted number counts, on the 19,698 data rows of the Zebra Finch table."""
    rows = [('Rows removed\n(10% ≤ value ≤ 90%)', 19159, True),
            ('Rows removed\n+ the header line', 19160, False),
            ('Rows kept\n(> 90% or < 10%)', 539, False)]
    who = {19159: 'custom code r1–r3, Galaxy r1', 19160: 'Galaxy r2', 539: 'Galaxy r3'}
    for i, (lab, v, right) in enumerate(rows):
        ax.barh(i, v, height=0.55, color='#bdbdbd' if not right else '#6f6f6f', edgecolor='none', zorder=2)
        ax.text(v + 300, i, f'{v:,}', va='center', fontsize=10, color=INK, fontweight='bold')
        if v > 5000:                                          # who submitted it: inside a long bar, else beside it
            ax.text(400, i, who[v], va='center', fontsize=8.5, color='white' if right else INK)
        else:
            ax.text(v + 2700, i, who[v], va='center', fontsize=8.5, color=INK2)
    ax.set_yticks(range(3), [r[0] for r in rows], fontsize=9.5)
    ax.invert_yaxis()
    ax.set_xlim(0, 24000)
    ax.set_xticks([0, 5000, 10000, 15000, 20000], ['0', '5,000', '10,000', '15,000', '20,000'])
    ax.tick_params(axis='x', labelsize=8.5, colors=INK2)
    ax.tick_params(axis='y', length=0, colors=INK)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.grid(axis='x', color=GRID, lw=0.8, zorder=0)
    ax.set_xlabel('Rows (19,698 data rows + 1 header line)', fontsize=9, color=INK2)
    return ('Dark bar: the quantity the question asks for. Kept rows: 268 above 90% and 271 below 10%; the 8 rows '
            'at exactly 10% and the 13 at 90% are removed (the thresholds are strict).')


CASE1 = dict(
    number=1, task='bix-52-q7', benchmark='BixBench50', bench_name='BixBench-Verified-50', model='GPT-5.6 Luna',
    title='Rows removed or rows kept? The arithmetic was right; the check of what was counted was missing',
    question='How many individual methylation measurements (rows) are removed when filtering out measurements that '
             'do not show >90% or <10% methylation in the Zebra Finch dataset?',
    answers={19159: '19,159', 19160: '19,160', 539: '539'},
    marks=[(GAL, 2, 'end', 'line count includes the header'), (GAL, 3, 'end', 'subtracted: reported the rows kept')],
    panel=panel_bix52, panel_title='What each submitted number counts',
    simple=True,
    groups=[('GPT-5.6 Luna', 'GPT-5.6 Luna', (CODE, GAL), 'all'),
            ('GPT-5.5', 'GPT-5.5', (CODE, GAL), 'all'),
            ('GPT-5.6 Sol', 'GPT-5.6 Sol', (CODE, GAL), 'all'),
            ('DeepSeek V4 Pro', 'DeepSeek V4 Pro', (CODE, GAL), 'all')],
    callouts={('GPT-5.6 Luna', GAL, 1): 'subtracted the header: 19,698 − 268 − 271',
              ('GPT-5.6 Luna', GAL, 2): 'line count includes the header',
              ('GPT-5.6 Luna', GAL, 3): 'reported the rows kept (539), not removed',
              ('GPT-5.6 Luna', CODE, 1): 'counted kept and removed rows together',
              ('GPT-5.5', GAL, 1): 'UDT reads the table by its header',
              ('GPT-5.5', GAL, 2): 'UDT reads the table by its header',
              ('GPT-5.5', GAL, 3): 'output keeps the header: 19,160 − 1',
              ('GPT-5.6 Sol', GAL, 1): 'checked whether the header was kept',
              ('GPT-5.6 Sol', GAL, 2): '19,160 − header; checked 19,698 − 539',
              ('GPT-5.6 Sol', GAL, 3): 'line count includes the header',
              ('DeepSeek V4 Pro', GAL, 1): 'counted rows kept (539): 19,698 − 539',
              ('DeepSeek V4 Pro', GAL, 2): 'counted rows kept (539): 19,698 − 539',
              ('DeepSeek V4 Pro', GAL, 3): 'counted rows kept (539): 19,698 − 539'},
    notes=[('What happened in Galaxy',
            'Galaxy r2 filtered the right rows (10–90%) and counted them with Galaxy\'s line-count tool, which also '
            'counts the header line: 19,160. It had noted the header itself ("a header plus 19,698 measurement rows", '
            'trace L23) but submitted the count as read.\n\nGalaxy r3 framed the 10–90% rows as the ones kept '
            '(L29), then subtracted them from the total: "the requested removed count is therefore 539" (L167). '
            'Earlier it caught a Galaxy converter reading the wrong dataset (L96): its checks went to the tool, not '
            'to the question.'),
           ('The check that was missing',
            'Reconcile the counts: kept + removed must equal the 19,698 data rows.\n\n• r2: 19,160 + 539 = 19,699, '
            'one more than the data rows: the header line.\n\n• r3: re-read the question. Measurements that "do not '
            'show >90% or <10%" are the ones filtered out, so the removed rows are the 10–90% rows, 19,159, not '
            'the 539 in the tails.'),
           ('What custom code did',
            'All three custom-code runs counted both sides in one script ("kept_extreme_rows 539, removed_rows '
            '19159"), together with the rows exactly at 10% and 90%, so each number checked the other (r1, L7–L8).'
            '\n\nGalaxy r1 made the same reconciliation and was correct: "19,699 total lines (header plus 19,698 '
            'measurements) … 19698 − 268 − 271 = 19159" (L121).')],
    takeaway='Same model, same data, same arithmetic: the two Galaxy failures are one unreconciled count and one '
             'unchecked reading of the question, not a missing capability.')


# ---------------------------------------------------------------- case 2: ml-model-track-overlap-q1, GPT-5.5
def panel_mltrack(ax, runs):
    """The overlap each matching rule gives, and the runs that submitted it (rounded to the nearest 100)."""
    rows = [('Exact identifiers only', 109, 100, 'Galaxy r3'),
            ('+ ENCODE replicate suffix\nstripped (ENCSR…_1 → ENCSR…)', 1264, 1300, 'Galaxy r1, r2'),
            ('+ ENCODE → GEO cross-\nreferences only (dbxrefs)', 2418, 2400, 'custom code r2'),
            ('Both: suffix stripped\nand cross-references', 3573, 3600, 'custom code r1, r3')]
    for i, (lab, v, rounded, who) in enumerate(rows):
        right = rounded == 3600
        ax.barh(i, v, height=0.55, color='#6f6f6f' if right else '#bdbdbd', edgecolor='none', zorder=2)
        ax.text(v + 60, i, f'{v:,} → {rounded:,}', va='center', fontsize=10, color=INK, fontweight='bold')
        if v > 1000:
            ax.text(60, i, who, va='center', fontsize=8.5, color='white' if right else INK)
        else:
            ax.text(v + 1500, i, who, va='center', fontsize=8.5, color=INK2)
    ax.set_yticks(range(len(rows)), [r[0] for r in rows], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlim(0, 5000)
    ax.set_xticks([0, 1000, 2000, 3000, 4000], ['0', '1,000', '2,000', '3,000', '4,000'])
    ax.tick_params(axis='x', labelsize=8.5, colors=INK2)
    ax.tick_params(axis='y', length=0, colors=INK)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    ax.grid(axis='x', color=GRID, lw=0.8, zorder=0)
    ax.set_xlabel('Sei tracks sharing provenance with Borzoi (→ rounded)', fontsize=9, color=INK2)
    return ('Counts as computed in the runs\' own traces: 109 (Galaxy r3, L201), 1,264 (Galaxy r1, L97; custom code '
            'r1, L145), 2,418 (custom code r2, L140), 3,573 (custom code r1, L184). Dark bar: the accepted answer, 3600.')


CASE2 = dict(
    number=2, task='ml-model-track-overlap-q1', benchmark='CompBio', bench_name='CompBioBench', model='GPT-5.5',
    title='Both runs reached 1,264; only the custom-code run asked why ENCODE tracks barely matched',
    question='Borzoi and Sei are both DNA sequence models trained to predict genomic assay outputs. Out of the Sei '
             'tracks that are linked to a specific Cistrome ID, how many tracks share provenance with any of the '
             'tracks in Borzoi? Round your answer to the nearest 100.',
    answers={1300: '1300', 100: '100', 3600: '3600', 2400: '2400'},
    marks=[(GAL, 1, 'end', 'stopped at 1,264'), (GAL, 2, 'end', 'answered after its check job failed'),
           (GAL, 3, 'end', 'accepted a 109-row join'), (CODE, 2, 'end', 'cross-references, but suffixes kept')],
    panel=panel_mltrack, panel_title='The overlap each matching rule gives',
    simple=True,
    groups=[('GPT-5.5', 'GPT-5.5', (CODE, GAL), 'all'),
            ('GPT-5.6 Sol', 'GPT-5.6 Sol', (CODE, GAL), 'all'),
            ('GPT-5.6 Luna', 'GPT-5.6 Luna', (CODE, GAL), 'all'),
            ('DeepSeek V4 Pro', 'DeepSeek V4 Pro', (CODE, GAL), 'all')],
    callouts={('GPT-5.5', GAL, 1): 'stopped at 1,264; never queried ENCODE',
              ('GPT-5.5', GAL, 2): 'answered right after its check job failed',
              ('GPT-5.5', GAL, 3): 'accepted a 109-row join',
              ('GPT-5.5', CODE, 1): '1,264, then hidden aliases: ENCODE → GEO, 3,573',
              ('GPT-5.5', CODE, 2): 'cross-references added, replicate suffixes kept',
              ('GPT-5.5', CODE, 3): 'translated ENCODE accessions to GEO from the start',
              ('GPT-5.6 Sol', CODE, 1): 'suffixes stripped, no cross-references: 1,264',
              ('GPT-5.6 Sol', CODE, 2): 'stopped at 1,264 (102 GEO + 1,162 ENCODE)',
              ('GPT-5.6 Sol', CODE, 3): 'linked ENCODE experiments to GEO samples',
              ('GPT-5.6 Luna', CODE, 1): 'never queried ENCODE',
              ('GPT-5.6 Luna', CODE, 2): 'never queried ENCODE',
              ('GPT-5.6 Luna', CODE, 3): 'never queried ENCODE',
              ('DeepSeek V4 Pro', CODE, 1): '2,404 + 1,020 = 3,424; also searched the web for the answer',
              ('DeepSeek V4 Pro', CODE, 2): 'stopped at 1,264; also searched the web for the answer',
              ('DeepSeek V4 Pro', CODE, 3): '2,404 + 1,162 = 3,566; also searched the web for the answer',
              ('GPT-5.6 Sol', GAL, 1): 'ENCODE cross-references; 2,404 matches',
              ('GPT-5.6 Sol', GAL, 2): 'exact joins through ENCODE cross-references',
              ('GPT-5.6 Sol', GAL, 3): 'added direct ENCODE matches; still 2,400',
              ('GPT-5.6 Luna', GAL, 1): 'never queried ENCODE',
              ('GPT-5.6 Luna', GAL, 2): 'exact join, 102 matches; never queried ENCODE',
              ('GPT-5.6 Luna', GAL, 3): 'exact join on file IDs; never queried ENCODE',
              ('DeepSeek V4 Pro', GAL, 1): 'never queried ENCODE',
              ('DeepSeek V4 Pro', GAL, 2): 'queried ENCODE; reached the 2,400 level',
              ('DeepSeek V4 Pro', GAL, 3): 'resolved ENCODE → GEO cross-references in a UDT'},
    notes=[('What happened in Galaxy',
            'Galaxy r1\'s user-defined tool found 1,264 matching tracks. The agent called its "exact accession '
            'match and the broader series diagnostic" in agreement (L98), but the diagnostic had no Borzoi series to '
            'match (borzoi_unique_gse 0, L97), so it could not have disagreed. It answered 1300 after one look at '
            'the table (L101).\n\nr2 got 62, then 1,263 (a 20-fold jump), and answered 1300 right after its '
            'validation job failed (L187–L188). r3 rebuilt the match from ordinary tools and accepted 109 (L201). '
            'None of the three ever queried the ENCODE portal.'),
           ('The check that was missing',
            'Ask why so few Borzoi tracks match: Borzoi labels its ENCODE tracks with ENCODE accessions (5,267 '
            'ENCSR experiments, L201), while Cistrome records most samples by GEO ID. Each ENCODE experiment lists '
            'its GEO sample in dbxrefs (ENCSR000EIJ → GEO:GSM1008583).\n\nThe check was possible in Galaxy: '
            'Galaxy jobs reached external APIs in these runs, and DeepSeek V4 Pro\'s Galaxy r3 resolved the ENCODE '
            'cross-references in a user-defined tool and answered 3600.'),
           ('What custom code did',
            'Custom-code r1 reached the same 1,264 (L145), then went on: "I\'m checking one more possible source of '
            'hidden aliases" (L163). It found the dbxrefs (L165), recounted 3,573, and audited the jump by accession '
            'prefix before answering 3600 (L184–L200).\n\nr3 reasoned up front that Borzoi\'s ENCODE tracks '
            'use ENCODE accessions (L86) and answered 3600. r2 added the cross-references but kept the replicate '
            'suffixes, and answered 2400.')],
    takeaway='Galaxy r1 and custom-code r1 reached the same 1,264; one more question about the identifiers separated '
             '1300 from 3600, and nothing in Galaxy prevented asking it.')


# ---------------------------------------------------------------- case 3: overexpress-tf-q1, GPT-5.6 Luna
# odds ratio of motif presence, gained regions vs background (10,000 regions each, JASPAR score >= 0.8), from GPT-5.6
# Luna custom-code r2: background not matched (trace L122) and GC-matched (L156); REST had no hits and is not shown
OVEREXPRESS_OR = {'KLF4': (0.605, 1.640), 'ASCL1': (0.545, 1.121), 'TCF7': (1.685, 1.047), 'TFAP2A': (0.492, 1.035),
                  'GATA3': (1.364, 0.968), 'PAX7': (1.534, 0.911), 'FOXA1': (1.434, 0.819), 'RUNX1': (1.030, 0.793),
                  'SPI1': (0.665, 0.772)}


def spread(ys, gap):
    """Label positions (log10 units) at least `gap` apart, kept as close as possible to the data."""
    order = np.argsort(ys)
    pos = np.array(ys, float)[order]
    for _ in range(200):
        moved = False
        for i in range(1, len(pos)):
            if pos[i] - pos[i - 1] < gap:
                d = (gap - (pos[i] - pos[i - 1])) / 2
                pos[i - 1] -= d
                pos[i] += d
                moved = True
        if not moved:
            break
    out = np.empty(len(ys))
    out[order] = pos
    return out


def panel_overexpress(fig, runs):
    # GC content of the two region sets, as measured in Galaxy r2 (Fasta Statistics base counts)
    gx = fig.add_axes([0.745, 0.705, 0.235, 0.06])
    for i, (lab, v) in enumerate((('Gained regions', 39.11), ('Reference regions', 53.38))):
        gx.barh(i, v, height=0.62, color='#8c8c8c' if i == 0 else '#bdbdbd', edgecolor='none')
        gx.text(v + 1, i, f'{v:.1f}% GC', va='center', fontsize=9, color=INK, fontweight='bold')
    gx.set_yticks([0, 1], ['Gained regions', 'Reference regions'], fontsize=9)
    gx.invert_yaxis()
    gx.set_xlim(0, 75)
    gx.set_xticks([])
    for sp in ('top', 'right', 'bottom'):
        gx.spines[sp].set_visible(False)
    gx.tick_params(axis='y', length=0, colors=INK)
    gx.set_title('Measured in Galaxy r2 (Fasta Statistics, L445 and L447)', fontsize=8.5, color=INK2, loc='left',
                 pad=3, fontweight='normal')
    # motif enrichment before and after matching the background on GC
    ax = fig.add_axes([0.745, 0.475, 0.2, 0.185])
    ax.set_yscale('log')
    ax.set_ylim(0.42, 2.0)
    ax.set_xlim(-0.75, 1.75)
    ax.plot([-0.04, 1.04], [1, 1], color=INK2, lw=0.8, ls=(0, (3, 2)), zorder=1)
    names = list(OVEREXPRESS_OR)
    before = [OVEREXPRESS_OR[n][0] for n in names]
    after = [OVEREXPRESS_OR[n][1] for n in names]
    for n, b, a in zip(names, before, after):
        style = (dict(color=INK, lw=2.2, zorder=4) if n == 'KLF4' else
                 dict(color=lm.COLOR[GAL], lw=1.8, zorder=3) if n == 'PAX7' else dict(color='#c8c8c8', lw=1.0, zorder=2))
        ax.plot([0, 1], [b, a], marker='o', ms=4.5, mec=SURFACE, mew=0.8, **style)
    ly = 10 ** spread(np.log10(before), 0.05)
    for n, b, y in zip(names, before, ly):
        ax.text(-0.08, y, f'{n} {b:.2f}', ha='right', va='center', fontsize=8,
                color=INK, fontweight='bold' if n in ('KLF4', 'PAX7') else 'normal')
    for n in ('KLF4', 'PAX7'):
        a = OVEREXPRESS_OR[n][1]
        ax.text(1.08, a, f'{n} {a:.2f}', ha='left', va='center', fontsize=8.5, color=INK, fontweight='bold')
    ax.set_xticks([0, 1], ['Background\nnot matched', 'GC-matched\nbackground'], fontsize=8.5)
    ax.set_yticks([0.5, 1, 2], ['0.5', '1', '2'])
    ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.tick_params(axis='y', labelsize=8.5, colors=INK2, length=0)
    ax.tick_params(axis='x', length=0, colors=INK)
    for sp in ('top', 'right', 'left', 'bottom'):
        ax.spines[sp].set_visible(False)
    ax.yaxis.tick_right()
    return ('Odds ratio of motif presence, gained regions vs background (log scale), custom-code r2 (L122, L156; 10,000 '
            'regions per set). Black: KLF4, accepted. Blue: PAX7, the Galaxy answer. REST (no hits) not shown.')


CASE3 = dict(
    number=3, task='overexpress-tf-q1', benchmark='CompBio', bench_name='CompBioBench', model='GPT-5.6 Luna',
    title='The confounder was measured and then ignored: AT-rich regions make AT-rich motifs look enriched',
    question='We perturbed a primary cell culture with a cocktail of transcription factors (TFs). ATAC-seq is '
             'performed on the initial sample and 48 hours after perturbation. Exactly one of the TFs in the '
             'following list is part of the cocktail: FOXA1, ASCL1, TFAP2A, RUNX1, KLF4, PAX7, TCF7, REST, SPI1, '
             'GATA3. Identify which one.',
    answers={},
    marks=[(GAL, 2, 'end', 'GC measured, answer from raw hit rates'), (GAL, 3, 'end', 'checked peak length, not GC'),
           (CODE, 3, 'end', 'overrode its own GC-matched table')],
    panel=panel_overexpress, panel_fig=True, panel_title='Matching the background on GC flips the ranking',
    simple=True,
    groups=[('GPT-5.6 Luna', 'GPT-5.6 Luna', (CODE, GAL), 'all'),
            ('GPT-5.5', 'GPT-5.5', (CODE, GAL), 'all'),
            ('GPT-5.6 Sol', 'GPT-5.6 Sol', (CODE, GAL), 'all'),
            ('DeepSeek V4 Pro', 'DeepSeek V4 Pro', (CODE, GAL), 'all')],
    callouts={('GPT-5.6 Luna', GAL, 1): 'MEME-ChIP with reference peaks as control',
              ('GPT-5.5', CODE, 1): 'inferred KLF4 from OCT/SOX co-motifs, no GC control',
              ('GPT-5.5', CODE, 2): 'checked motif names, not GC',
              ('GPT-5.5', CODE, 3): 'GC-matched motif scan',
              ('GPT-5.6 Sol', CODE, 1): 'controlled for the GC shift: about 4-fold for KLF4',
              ('GPT-5.6 Sol', CODE, 2): 'PAX7 led first; GC- and accessibility-matched rerun',
              ('GPT-5.6 Sol', CODE, 3): 'PAX7 led first; GC-matched control',
              ('DeepSeek V4 Pro', CODE, 1): 'motif-rate differences between peak sets',
              ('DeepSeek V4 Pro', CODE, 2): 'motif-score AUC against a background: KLF4 0.68',
              ('DeepSeek V4 Pro', CODE, 3): 'GC-adjusted regression: KLF4 OR 1.37',
              ('GPT-5.6 Luna', GAL, 2): 'GC measured (39% vs 53%); answer from raw hit rates',
              ('GPT-5.6 Luna', GAL, 3): 'checked peak length, not GC',
              ('GPT-5.6 Luna', CODE, 1): 'GC-matched background: KLF4 22.7% vs 7.5%',
              ('GPT-5.6 Luna', CODE, 2): 'GC check flipped the ranking',
              ('GPT-5.6 Luna', CODE, 3): 'overrode its own GC-matched table',
              ('GPT-5.5', GAL, 1): 'GC matching moved the top hit TCF7 → FOXA1; answered at once',
              ('GPT-5.5', GAL, 2): 'tested SPI1 alone: 51,933 vs 64,006 fragments',
              ('GPT-5.5', GAL, 3): 'de novo motifs, then a check against GC-rich effects',
              ('GPT-5.6 Sol', GAL, 1): 'de novo GGGTGKR; checked it was not a GC artifact',
              ('GPT-5.6 Sol', GAL, 2): 'composition-controlled test (shuffled controls)',
              ('GPT-5.6 Sol', GAL, 3): 'PAX7 led a first count; a full PWM test gave KLF4',
              ('DeepSeek V4 Pro', GAL, 1): 'MEME-ChIP with a control set',
              ('DeepSeek V4 Pro', GAL, 2): 'MEME-ChIP with a control set',
              ('DeepSeek V4 Pro', GAL, 3): 'set MEME-ChIP aside; FIMO hit enrichment gave PAX7'},
    notes=[('What happened in Galaxy',
            'Galaxy r2 called gained and reference peaks (MACS2) and scanned the ten motifs with FIMO against a '
            'uniform 25% base background (L331). It measured 39.1% GC in gained regions and 53.4% in reference regions '
            '(L445, L447), then answered from raw hit rates three events later: PAX7 in 4.6% vs 1.9% of sequences, '
            'KLF4 in 20.1% vs 24.1% (L455) → PAX7.\n\nr3 used the same design and checked "two possible '
            'confounders", peak lengths and JASPAR versions, but not GC (L290) → PAX7.'),
           ('The check that was missing',
            'Control for base composition. Gained regions are AT-rich, so AT-rich motifs (PAX7, TCF7, FOXA1, GATA3) '
            'occur there more often by chance and the GC-rich KLF4 motif less: compare against a GC-matched '
            'background, or let the background model come from the sequences.\n\nThe Galaxy tools were there: '
            'Galaxy r1 ran MEME-ChIP "with the gained sequences as primary and all reference-peak sequences as '
            'control" (L136) and answered KLF4.'),
           ('What custom code did',
            'r1 measured GC (gained 0.395, stable 0.568; L104), drew a GC-matched background (0.403 vs 0.403; L108) '
            'and found the KLF4 motif in 22.7% against 7.5% of regions (p = 1.8e-42; L110) → KLF4.\n\nr2 saw TCF7 '
            'and PAX7 lead the raw ranking (L122), then "a GC check changed the apparent ranking" (L219): after '
            'matching, KLF4 led (L156) → KLF4. r3 built a matched table with KLF4 on top but overrode it (L142) → '
            'TCF7.')],
    takeaway='Galaxy r2 measured the confounder and answered without using it; the same model, controlling for it in '
             'custom code and in Galaxy r1, found KLF4.')


# ---------------------------------------------------------------- simplified layout (case 1): step timelines only
def all_runs(task):
    """Every run of a task, with its steps and submitted answer, from the ledgers (any model)."""
    import make_trajectory_figures as mt
    from trajectory_steps import steps
    r = mt.f2.load_runs()
    r = r[r.task == task].copy()
    r['sequence'] = [' > '.join(steps(mt.ledger(x), x.env)) for x in r.itertuples()]
    r['answer'] = [mt.answer(x) for x in r.itertuples()]
    return r


def draw_simple(case):
    runs = all_runs(case['task'])
    groups = []                                               # (heading, [(lane label, row, callout)])
    for heading, cfg, envs, keep in case['groups']:
        lanes_ = []
        for env in envs:
            for rep in (1, 2, 3):
                row = runs[(runs.cfg == cfg) & (runs.env == env) & (runs.replicate == rep)].iloc[0]
                if keep == 'correct' and row.ok != 1:
                    continue
                name = f'{"Galaxy" if env == GAL else "Custom code"} r{rep}'
                lanes_.append((name, row, case['callouts'].get((cfg, env, rep), '')))
        groups.append((heading, lanes_))
    n_lanes = sum(len(g) for _, g in groups)
    rows = n_lanes + len(groups)                              # one heading row per group
    bottom = 0.95 if case.get('footnote') else 0.85           # inches below the lanes (axis labels, notes)
    height = 1.75 + 0.36 * rows + bottom
    used = used_kinds((row.env, row.sequence) for _, g in groups for _, row, _ in g)
    fig = frame(case, used, height=height)
    AX_W = 0.62                                               # axes width, figure fraction
    ax = fig.add_axes([0.155, bottom / height, AX_W, (0.36 * rows) / height])
    length = lambda row: len(row.sequence.split(' > ')) if row.sequence else 0
    # very long runs are cut so that the others stay readable: the cap is 80 steps, or the longest run of the model
    # in focus; a cut run ends with its total number of steps
    cap = max(80, max(length(row) for _, row, _ in groups[0][1]))
    shown = lambda row: min(length(row), cap)
    n_max = max(shown(row) for _, g in groups for _, row, _ in g)
    truncated = any(length(row) > cap for _, g in groups for _, row, _ in g)
    width_in = AX_W * 13.33
    # the x range that leaves room after each run for its callout (italic 9 pt, about 4.6 pt per character)
    right = max(n / max(0.2, 1 - (len(c) * 4.6 / 72 + 0.45 + (0.75 if cut else 0)) / width_in) for n, c, cut in
                ((shown(row), '◀ ' + c if c else '', length(row) > cap) for _, g in groups for _, row, c in g))
    right = max(right, n_max + 1)
    ax.set_xlim(-0.2, right)
    box_pt = width_in * 72 / (right + 0.2) * 0.9              # width of one step box, points
    ax.set_ylim(rows - 0.5, -0.5)
    y = 0
    for gi, (heading, lanes_) in enumerate(groups):
        if gi:
            ax.axhline(y - 0.5, color=GRID, lw=1.0, xmin=0, xmax=1)
        ax.text(-0.2, y, heading, fontsize=10, fontweight='bold', color=INK, va='center', ha='left')
        y += 1
        for name, row, callout in lanes_:
            seq = row.sequence.split(' > ') if row.sequence else []
            n_all, end = len(seq), shown(row)
            if n_all > cap:
                seq = seq[:cap]
            for i, lab in enumerate(seq):
                a = dict((k, s) for k, _, s in KINDS)[kind(lab)]
                fc = lm.tint(lm.COLOR[row.env], a)
                ax.add_patch(Rectangle((i + 0.05, y - 0.33), 0.9, 0.66, facecolor=fc,
                                       edgecolor=lm.COLOR[row.env] if a < 1 else 'none', lw=0.6, zorder=2))
                short = SHORT.get(lab, 'UDT' if lab.startswith('UDT') else lab.split(':')[0].split(' ')[0])
                if len(short) * 3.7 + 2 <= box_pt:                # only where the name fits inside the box
                    ax.text(i + 0.5, y, short, ha='center', va='center', fontsize=6.8, color=lm.text_on(fc),
                            zorder=3)
            ax.text(-0.35, y, name, ha='right', va='center', fontsize=9.5, color=INK)
            after = ''
            if n_all > cap:                                   # cut lane: its total length, then the callout
                after = f'⋯ {n_all} steps  '
            if callout or after:
                ax.text(end + 0.25, y, after + ('◀ ' + callout if callout else ''), va='center', fontsize=9,
                        color=INK, style='italic')
            ok = row.ok == 1
            if case.get('show_score'):                        # IWC: the output-agreement score, not an answer
                shown_answer = f'{"✓" if ok else "✗"}  {float(row.score):.3f}'
            elif str(row.answer).replace('.', '').isdigit():
                shown_answer = f'{"✓" if ok else "✗"}  {int(float(row.answer)):,}'
            else:
                shown_answer = f'{"✓" if ok else "✗"}  {row.answer}'
            ax.annotate(shown_answer, xy=(1.0, y), xycoords=('axes fraction', 'data'),
                        xytext=(10, 0), textcoords='offset points', va='center', fontsize=10, color=INK,
                        fontweight='normal' if ok else 'bold', annotation_clip=False)
            y += 1
    ax.set_yticks([])
    ticks = list(range(1, n_max + 1)) if n_max <= 12 else [
        t for t in MaxNLocator(nbins=8, integer=True).tick_values(1, n_max) if 1 <= t <= n_max]
    ax.set_xticks([t - 0.5 for t in ticks], [str(int(t)) for t in ticks])
    ax.tick_params(axis='x', labelsize=8.5, colors=INK2, length=0)
    ax.annotate('Analysis step (Galaxy job or command), in execution order', xy=(n_max / 2, 0),
                xycoords=('data', 'axes fraction'), xytext=(0, -22), textcoords='offset points', ha='center',
                va='top', fontsize=9, color=INK2, annotation_clip=False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    fig.text(0.155 + AX_W, 1 - 1.62 / height, 'Score (✓ ≥ 0.99)' if case.get('show_score') else 'Answer', fontsize=9,
             color=INK2, ha='left', va='bottom',
             transform=fig.transFigure)
    if truncated:
        ax.annotate(f'Runs longer than {cap} steps are cut at {cap}; their total is shown after the cut.',
                    xy=(n_max / 2, 0), xycoords=('data', 'axes fraction'), xytext=(0, -36), textcoords='offset points',
                    ha='center', va='top', fontsize=8.5, color=INK2, annotation_clip=False)
    if case.get('footnote'):
        fig.text(0.04, 0.1 / height, case['footnote'], fontsize=9, color=INK2, va='bottom')
    save(fig, case)
    return pd.concat([row.to_frame().T.assign(group=h) for h, g in groups for _, row, _ in g]).assign(
        case=case['number'])


# ---------------------------------------------------------------- case 4 (Galaxy solved, custom code did not):
# contaminated-rna-q3, GPT-5.6 Luna. What Galaxy provided: the default, prebuilt Kraken2 core_nt database on CVMFS
# (2024-09-04 build), which includes ape genomes, so the chimpanzee reads are classified as Pan.
CASE4 = dict(
    number=4, task='contaminated-rna-q3', benchmark='CompBio', bench_name='CompBioBench', model='GPT-5.6 Luna',
    title="Galaxy's default Kraken2 database includes ape genomes, so the chimpanzee reads stood out",
    question='You are given a single-end RNA-seq FASTQ file. The sample is expected to be human, but it may contain '
             'reads from another organism. Determine the genus of the most likely non-human organism present, if any '
             '(lowercase scientific genus name, or "none").',
    simple=True,
    groups=[('GPT-5.6 Luna', 'GPT-5.6 Luna', (CODE, GAL), 'all'),
            ('GPT-5.5', 'GPT-5.5', (CODE, GAL), 'all'),
            ('GPT-5.6 Sol', 'GPT-5.6 Sol', (CODE, GAL), 'all'),
            ('DeepSeek V4 Pro', 'DeepSeek V4 Pro', (CODE, GAL), 'all')],
    callouts={('GPT-5.6 Luna', CODE, 1): 'primate hits set aside as host; 118 reads M. hyorhinis',
              ('GPT-5.6 Luna', CODE, 2): '9,486 chimp-best reads set aside; also searched web for answer',
              ('GPT-5.6 Luna', CODE, 3): 'primates filtered as host; also searched web for answer',
              ('GPT-5.6 Luna', GAL, 1): 'Kraken2 core_nt genus tally: Pan 6,271 vs Meso 26',
              ('GPT-5.6 Luna', GAL, 2): 'Kraken2 core_nt genus count: Pan 6,271 vs Meso 26',
              ('GPT-5.6 Luna', GAL, 3): 'Kraken2 core_nt genus count: Pan 6,271, Pongo 371',
              ('GPT-5.5', CODE, 1): 'primate cDNA race: Pan 4,723 vs gorilla 440',
              ('GPT-5.5', CODE, 2): 'bonobo cDNA: 1,508 reads beat human',
              ('GPT-5.5', CODE, 3): 'exact mtDNA matches: 487 bonobo-only reads',
              ('GPT-5.5', GAL, 1): 'Kraken2 core_nt: top non-human genus Pan, 5,665',
              ('GPT-5.5', GAL, 2): 'Kraken2 core_nt on a 50k-read sample: Pan 1,332',
              ('GPT-5.5', GAL, 3): 'Kraken2 core_nt: Pan 6,271; BLAST nt confirms',
              ('GPT-5.6 Sol', CODE, 1): 'microbial-only sourmash database: M. hyorhinis',
              ('GPT-5.6 Sol', CODE, 2): 'bonobo/chimp cDNA: 7,638 reads best to bonobo',
              ('GPT-5.6 Sol', CODE, 3): 'ape genome race: Pan-unique 9,318 vs macaque 2,667',
              ('GPT-5.6 Sol', GAL, 1): 'Kraken2 core_nt: Pan 6,271; rerun at confidence 0.2',
              ('GPT-5.6 Sol', GAL, 2): 'core_nt job orphaned; Bowtie2: rat 1,001 > mouse 960',
              ('GPT-5.6 Sol', GAL, 3): 'Kraken2 core_nt: Pan 5,665 vs Pongo 288',
              ('DeepSeek V4 Pro', CODE, 1): 'BLAST: Pan ~1,500 vs Meso 98, chose Meso; searched web for answer',
              ('DeepSeek V4 Pro', CODE, 2): 'Pan mtDNA-only 626 reads; searched web for answer',
              ('DeepSeek V4 Pro', CODE, 3): 'k2_pluspf_16gb has no Pan; searched web for answer',
              ('DeepSeek V4 Pro', GAL, 1): 'Kraken2 core_nt: Pan 6,271; 5,121 at confidence 0.1',
              ('DeepSeek V4 Pro', GAL, 2): 'core_nt never returned; k2_pluspf_2021: Mycoplasma 75',
              ('DeepSeek V4 Pro', GAL, 3): 'Kraken2 core_nt (confidence 0.5): Pan 1,554'})


# ---------------------------------------------------------------- case 5 (Galaxy solved, custom code did not):
# wf_007_vgp_mitogenome_assembly, GPT-5.5. What Galaxy provided: MitoHiFi 3.2.3 (read filtering, hifiasm, a related
# reference found on NCBI, annotation and rotation) running on server compute; locally hifiasm ran out of memory.
CASE5 = dict(
    number=5, task='wf_007_vgp_mitogenome_assembly', benchmark='IWC', bench_name='IWC', model='GPT-5.5',
    title='Galaxy ran a complete mitogenome pipeline (MitoHiFi) on server compute; locally, hifiasm ran out of memory',
    question='Assemble the complete mitochondrial genome of Agrius convolvuli from the provided PacBio HiFi reads, as '
             'one FASTA record. Scored by output agreement with the reference workflow (31-mer F1); correct at '
             '≥ 0.99.',
    simple=True, show_score=True,
    groups=[('GPT-5.5', 'GPT-5.5', (CODE, GAL), 'all'),
            ('GPT-5.6 Sol', 'GPT-5.6 Sol', (CODE, GAL), 'all'),
            ('GPT-5.6 Luna', 'GPT-5.6 Luna', (CODE, GAL), 'all'),
            ('DeepSeek V4 Pro', 'DeepSeek V4 Pro', (CODE, GAL), 'all')],
    callouts={('GPT-5.5', CODE, 1): 'nuclear-repeat circle (16,279 bp) kept despite low support',
              ('GPT-5.5', CODE, 2): 'hifiasm out of memory 3×; unpolished Flye unit',
              ('GPT-5.5', CODE, 3): 'Flye on a low-GC subset + samtools consensus',
              ('GPT-5.5', GAL, 1): 'skipped MitoHiFi; hifiasm contig picked by depth',
              ('GPT-5.5', GAL, 2): 'Galaxy MitoHiFi (genetic code 5): 37 genes, circular',
              ('GPT-5.5', GAL, 3): 'rejected a hifiasm circle; then Galaxy MitoHiFi',
              ('GPT-5.6 Sol', CODE, 1): 'k-mer enrichment, 15,448-bp consensus',
              ('GPT-5.6 Sol', CODE, 2): 'COI-seeded read pool + hifiasm',
              ('GPT-5.6 Sol', CODE, 3): 'local assembly, rotated 15,448-bp consensus',
              ('GPT-5.6 Sol', GAL, 1): 'MitoHiFi errored; Galaxy minimap2 → Flye contig',
              ('GPT-5.6 Sol', GAL, 2): 'Galaxy MitoHiFi',
              ('GPT-5.6 Sol', GAL, 3): 'Galaxy MitoHiFi',
              ('GPT-5.6 Luna', CODE, 1): 'hifiasm on low-GC reads + samtools consensus',
              ('GPT-5.6 Luna', CODE, 2): 'read enrichment, Flye seed, consensus',
              ('GPT-5.6 Luna', CODE, 3): 'COX1-motif reads, Flye, polished unit',
              ('GPT-5.6 Luna', GAL, 1): 'Galaxy MitoHiFi',
              ('GPT-5.6 Luna', GAL, 2): 'Galaxy MitoHiFi',
              ('GPT-5.6 Luna', GAL, 3): 'Galaxy MitoHiFi',
              ('DeepSeek V4 Pro', CODE, 1): 'fetched the published mitogenome as bait; de novo unitig',
              ('DeepSeek V4 Pro', CODE, 2): '18x-depth nuclear contig taken as mitochondrial',
              ('DeepSeek V4 Pro', CODE, 3): 'fetched the published mitogenome, edited to match it',
              ('DeepSeek V4 Pro', GAL, 1): 'Galaxy MitoHiFi',
              ('DeepSeek V4 Pro', GAL, 2): 'Galaxy MitoHiFi',
              ('DeepSeek V4 Pro', GAL, 3): 'MitoHiFi failed; consensus on the related reference'})


# ---------------------------------------------------------------- case 6 (Galaxy solved, custom code did not):
# contaminated-rna-q2, DeepSeek V4 Pro. What Galaxy provided: a catalogue of prebuilt genome indexes on CVMFS that
# includes pig (susScr3 for BWA, HISAT2 and Bowtie2), next to the default Kraken2 core_nt database.
CASE6 = dict(
    number=6, task='contaminated-rna-q2', benchmark='CompBio', bench_name='CompBioBench', model='DeepSeek V4 Pro',
    title="Galaxy's prebuilt genome indexes put pig on the panel; the failing custom-code runs never tested it",
    question='You are given a single-end RNA-seq FASTQ file that contains mostly human reads and a small fraction of '
             'contaminant reads. Identify the contaminant species (lowercase scientific name, for example "mus '
             'musculus").',
    simple=True,
    groups=[('DeepSeek V4 Pro', 'DeepSeek V4 Pro', (CODE, GAL), 'all'),
            ('GPT-5.5', 'GPT-5.5', (CODE, GAL), 'all'),
            ('GPT-5.6 Sol', 'GPT-5.6 Sol', (CODE, GAL), 'all'),
            ('GPT-5.6 Luna', 'GPT-5.6 Luna', (CODE, GAL), 'all')],
    callouts={('DeepSeek V4 Pro', CODE, 1): 'Kraken2 8 GB database (no pig): EBV on top; searched web',
              ('DeepSeek V4 Pro', CODE, 2): "copied an earlier agent's downloaded answer (rattus)",
              ('DeepSeek V4 Pro', CODE, 3): "copied an earlier agent's downloaded answer (rattus)",
              ('DeepSeek V4 Pro', GAL, 1): 'prebuilt pig index 18.4% > cow, rat; saw earlier answers',
              ('DeepSeek V4 Pro', GAL, 2): 'HISAT2 prebuilt susScr3 6.9% vs mouse 0.4%, rat 0.7%',
              ('DeepSeek V4 Pro', GAL, 3): 'BWA prebuilt panel: susScr3 19% vs cow 4%',
              ('GPT-5.5', CODE, 1): 'rodent-only reference panels; pig never tested',
              ('GPT-5.5', CODE, 2): 'remote BLAST: 17/200 pig; searched web for answer',
              ('GPT-5.5', CODE, 3): '6-species cDNA panel without pig: rat rRNA',
              ('GPT-5.5', GAL, 1): 'core_nt + HISAT2 on prebuilt susScr3: 7.5%',
              ('GPT-5.5', GAL, 2): 'core_nt: chose the EBV clade',
              ('GPT-5.5', GAL, 3): 'mitochondrial k-mer panel: pig; searched web for answer',
              ('GPT-5.6 Sol', CODE, 1): 'UCSC mRNA panel: pig on top; searched web for answer',
              ('GPT-5.6 Sol', CODE, 2): 'remote BLAST: pig, 1,216 reads; searched web for answer',
              ('GPT-5.6 Sol', CODE, 3): 'RefSeq mitochondrial BLAST: Sus scrofa',
              ('GPT-5.6 Sol', GAL, 1): 'core_nt: Sus 238 direct reads, 1,299 minimizers',
              ('GPT-5.6 Sol', GAL, 2): 'core_nt ranked by clade reads: EBV 523 > pig',
              ('GPT-5.6 Sol', GAL, 3): 'core_nt ranked by direct reads; BLAST confirms',
              ('GPT-5.6 Luna', CODE, 1): 'saw pig (151 reads), EBV cluster larger; searched web',
              ('GPT-5.6 Luna', CODE, 2): 'EBV genome 589 reads; pig not pursued',
              ('GPT-5.6 Luna', CODE, 3): 'NCBI BLAST: Sus scrofa in 50/55 residual reads',
              ('GPT-5.6 Luna', GAL, 1): 'prebuilt Bowtie2 panel: susScr3 18.6% vs ≤ 4.9%',
              ('GPT-5.6 Luna', GAL, 2): 'core_nt: took only the viral branch (EBV)',
              ('GPT-5.6 Luna', GAL, 3): 'core_nt stalled; PlusPF (no pig): EBV 574'})


# ---------------------------------------------------------------- assembly
def case_runs(case):
    r = pd.read_csv(os.path.join(HERE, 'fig3_frame_runs.csv'))
    r = r[(r.task == case['task']) & (r.cfg == case['model']) & r.group.isin(
        ['Galaxy, task failed', 'custom code, task solved'])].copy()
    assert len(r) == 6, (case['task'], len(r))

    def short(a):
        try:
            v = float(a)
            for k, s in case.get('answers', {}).items():
                if abs(v - k) <= 1e-9 * max(1, abs(k)):
                    return s
            return f'{v:.4g}'
        except ValueError:
            return a if len(a) <= 22 else a[:20] + '…'
    r['answer_short'] = r.answer.astype(str).map(short)
    return r


def draw_case(case):
    if case.get('simple'):
        return draw_simple(case)
    runs = case_runs(case)
    fig = frame(case, used_kinds(zip(runs.env, runs.sequence)))
    panel_label(fig, 0.04, 0.785, 'a', 'Six runs of the same model: steps, answer and grade (✓ correct, ✗ incorrect)')
    ax = fig.add_axes([0.115, 0.43, 0.40, 0.33])
    lanes(ax, runs, case['marks'])
    panel_label(fig, 0.635, 0.785, 'b', case['panel_title'])
    if case.get('panel_fig'):
        note = case['panel'](fig, runs)
    else:
        note = case['panel'](fig.add_axes([0.745, 0.49, 0.235, 0.27]), runs)
    if note:
        fig.text(0.635, 0.405 if case.get('panel_fig') else 0.415, wrap(note, 80), fontsize=8.5, color=INK2, va='top',
                 linespacing=1.3)
    panel_label(fig, 0.04, 0.355, 'c', 'Why Galaxy missed it, and the check that would have caught it')
    notes(fig, (0.04, 0.075, 0.94, 0.27), [(h, wrap(b, 62)) for h, b in case['notes']])
    fig.text(0.04, 0.03, case['takeaway'], fontsize=10.5, fontweight='bold', color=INK, va='bottom')
    save(fig, case)
    return runs.assign(case=case['number'])


def main():
    out = [draw_case(c) for c in CASES]
    keep = ['case', 'task', 'cfg', 'env', 'replicate', 'run_id', 'score', 'answer', 'sequence']
    pd.concat(out)[keep].to_csv(os.path.join(HERE, 'fig3_cases.csv'), index=False)


CASES = [CASE1, CASE2, CASE3, CASE4, CASE5, CASE6]

if __name__ == '__main__':
    main()
