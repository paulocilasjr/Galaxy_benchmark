"""Extended Data figures 1-8 and their Source Data workbooks.

Run from the repository root after build_data.py:  python manuscript_material/scripts/fig_ed.py [1 2 ... 8]
Outputs: extended_data/ED_FigN.tif (300 dpi, RGB, LZW) and .eps, as required for Extended Data.
Design rules as in style.py: open-ended code first; vermillion squares = open-ended code, blue circles = Galaxy;
no abbreviations; panel titles state the finding.

Figure order follows the call-outs in the Results:
  1 archive and audit pipeline            5 divergence mechanisms by model configuration; IWC split replicate sets
  2 CompBioBench consensus proxy          6 input-token usage versus performance
  3 IWC sensitivity of the condition diff 7 bix-35-q1: every PhyKIT job of every Galaxy-condition run
  4 domain skills and interface scripting 8 integrity: answer retrieval, local computation, cross-run copying
"""
import collections
import textwrap
import gzip
import json
import math
import os
import statistics as st
import sys

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch, Rectangle

sys.path.insert(0, os.path.dirname(__file__))
from style import (BENCH, BENCH_2L, BENCH_LABEL, CFG_LABEL, CONFIGS, ENV_COLOR, ENV_LABEL, ENV_LABEL_LONG, ENV_MARKER, ENV_TINT,  # noqa: E402
                   ENVS, GALAXY, GRID, INK, INK2, LIGHT, MM, NEUTRAL_DARK, NEUTRAL_LIGHT, NEUTRAL_MID, OI_BLACK, OI_GREEN,
                   OI_ORANGE, OI_PURPLE, OI_SKY, SUPERSEDED, W_ED, env_handles, grid_x, grid_y, panel_label, panel_title, plt, save_ed)
from fig_main import MECH, HATCH, DARK_FILL, dot, rnd, signed, source_data  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUTDIR = os.path.join(ROOT, 'manuscript_material')
D = json.load(open(os.path.join(OUTDIR, 'source_data', 'figure_data.json')))
A = json.load(open(os.path.join(ROOT, 'BixBench50_CompBio_analysis', 'analysis.json')))
CFG5 = CONFIGS + [SUPERSEDED]
CFG_ROW = {c: c for c in CONFIGS}
CFG_ROW['DeepSeek V4 Pro'] = 'DeepSeek V4 Pro (Codex)'
CFG_ROW[SUPERSEDED] = 'DeepSeek V4 Pro (Claude\nCode, superseded)'


def box(ax, x, y, w, h, text, fc='white', ec=INK2, lw=0.6, fs=5.5, weight='normal'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.012', fc=fc, ec=ec, lw=lw,
                                transform=ax.transAxes))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, fontweight=weight, transform=ax.transAxes,
            linespacing=1.2)


def arrow(ax, x0, y0, x1, y1):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=6, lw=0.7, color=INK2,
                                 transform=ax.transAxes, shrinkA=0, shrinkB=0))


# =====================================================================================================
def ed1():
    fig = plt.figure(figsize=(W_ED, 88 * MM))
    inv = D['inventory']
    sd = {}
    ax = fig.add_axes([0.0, 0.10, 0.53, 0.76]); ax.axis('off')
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'The archive analysed')
    cases = collections.Counter(c['benchmark'] for c in D['task_cases'])
    rows = [('Tasks', [inv[b]['tasks'] for b in BENCH]),
            ('Archived runs', [inv[b]['runs'] for b in BENCH]),
            ('Execution traces (one event log per run)', [inv[b]['traces'] for b in BENCH]),
            ('Galaxy-condition runs with a detailed analysis-history snapshot', [f"{inv[b]['detailed_histories'][0]:,} of {inv[b]['detailed_histories'][1]:,}" for b in BENCH]),
            ('Galaxy analysis jobs (excluding data uploads)', [inv[b]['nonfetch_jobs'] for b in BENCH]),
            ('   of which Galaxy job errors', [inv[b]['error_jobs'] for b in BENCH]),
            ('Galaxy interface calls', [inv[b]['mcp_calls'] for b in BENCH]),
            ('   of which returned a failure status', [inv[b]['mcp_failed'] for b in BENCH]),
            ('Task cases audited trace by trace (Fig. 5a)', [cases[b] for b in BENCH])]
    xs = [0.01, 0.56, 0.72, 0.87]
    for k, b in enumerate(BENCH):
        ax.text(xs[k + 1] + 0.065, 1.0, BENCH_2L[b], ha='center', va='bottom', fontsize=5.6, fontweight='bold', transform=ax.transAxes)
        ax.plot([xs[k + 1] + 0.0, xs[k + 1] + 0.13], [0.985, 0.985], color=INK, lw=0.6, transform=ax.transAxes)
    for i, (lab, vals) in enumerate(rows):
        y = 0.92 - i * 0.1
        if i % 2 == 0:
            ax.add_patch(Rectangle((0.0, y - 0.05), 1.0, 0.1, fc='#f5f4f1', ec='none', transform=ax.transAxes))
        ax.text(xs[0], y, lab, fontsize=5.4, va='center', transform=ax.transAxes)
        for x, v in zip(xs[1:], vals):
            ax.text(x + 0.065, y, f'{v:,}' if isinstance(v, int) else str(v), fontsize=5.4, va='center', ha='center', transform=ax.transAxes)
    ax.text(0.01, -0.02, 'Jobs are counted once per server and job identifier. Totals: 4,240 runs, 4,228 execution traces,\n'
            '23,080 Galaxy analysis jobs and 69,812 Galaxy interface calls.', fontsize=5.0, color=INK2, transform=ax.transAxes, va='top')
    sd['a_archive'] = pd.DataFrame([dict(measure=lab.strip(), **{BENCH_LABEL[b]: v for b, v in zip(BENCH, vals)}) for lab, vals in rows])
    ax = fig.add_axes([0.575, 0.04, 0.425, 0.84]); ax.axis('off')
    panel_label(fig, 0.56, 0.99, 'b'); panel_title(fig, 0.56, 0.99, 'Trace-level audit pipeline')
    steps = [('Execution\ntraces', f"{sum(inv[b]['traces'] for b in BENCH):,} event logs, one per run"),
             ('Call extraction', f"{sum(inv[b]['mcp_calls'] for b in BENCH):,} Galaxy interface calls and all shell\ncommands, with status and parameter records"),
             ('Outcome\ncomparison', 'Evaluator verdicts (BixBench-Verified-50), output\nagreement (IWC), reported benchmark scores and\nthe consensus proxy (CompBioBench)'),
             ('Replicate-set\ncomparison', '81 scored-incorrect replicate runs in split\nBixBench-Verified-50 replicate sets: divergence\nmechanism versus scored-correct siblings'),
             ('Task-level\naudit', '93 task cases with at least one wrong, scored-\nincorrect or low-scoring run: one primary cause,\nsecondary causes and integrity flags')]
    for k, (t, d) in enumerate(steps):
        y = 0.83 - k * 0.19
        box(ax, 0.0, y, 0.27, 0.14, t, fc=LIGHT, ec=INK2, weight='bold', fs=5.4)
        ax.text(0.30, y + 0.07, d, fontsize=5.1, va='center', transform=ax.transAxes, linespacing=1.15)
        if k < len(steps) - 1:
            arrow(ax, 0.135, y, 0.135, y - 0.05)
    ax.text(0.30, 0.07, 'Also used: analysis-history snapshots, evaluator records\nand independent checks (public reference genomes,\nrecomputed statistics)',
            fontsize=5.0, color=INK2, transform=ax.transAxes, va='top')
    save_ed(fig, 'ED_Fig1', OUTDIR)
    source_data('ED_Fig1', sd)


# =====================================================================================================
def ed2():
    fig = plt.figure(figsize=(W_ED, 72 * MM))
    sd = {}
    ax = fig.add_axes([0.085, 0.16, 0.27, 0.64])
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'The consensus proxy reproduces the reported\nCompBioBench benchmark scores')
    runs = [r for r in A['runs'] if r['benchmark'] == 'CompBio']
    norm = lambda a: (a or '').strip().lower().replace(' ', '')
    tasks = sorted({r['task'] for r in runs})
    modal = {t: collections.Counter(norm(r['answer']) for r in runs if r['task'] == t).most_common(1)[0] for t in tasks}
    by = collections.defaultdict(dict)
    for r in runs:
        by[(r['model'], r['condition'], r['replicate'])][r['task']] = norm(r['answer'])
    cb = json.load(open(os.path.join(ROOT, 'CompBio', 'compBio_overview_audit.json')))['score_vectors']
    pts = []
    for v in cb:
        if v.get('answers_compared'):
            key = (v['model'], v['condition'], int(v['replicate'][1:]))
            pts.append(dict(model_configuration=v['model'], execution_condition=v['condition'], replicate_run=v['replicate'], reported_benchmark_score=v['score'],
                            proxy_score=sum(1 for t, a in by[key].items() if a == modal[t][0]), official=v['score_type'].startswith('official')))
    for env in ENVS:
        for p in pts:
            if p['execution_condition'] == env:
                dot(ax, p['reported_benchmark_score'], p['proxy_score'], env, filled=p['official'], ms=3.8)
    ax.plot([78, 100], [78, 100], color=INK2, lw=0.5, ls=(0, (2, 2)))
    mae = st.mean(abs(p['proxy_score'] - p['reported_benchmark_score']) for p in pts)
    bias = st.mean(p['proxy_score'] - p['reported_benchmark_score'] for p in pts)
    ax.text(0.03, 0.97, f'{len(pts)} reported benchmark scores with retained answers\nMean absolute error {mae:.1f}; mean bias +{bias:.1f}\nDashed line: identity',
            transform=ax.transAxes, va='top', fontsize=5.2)
    ax.set_xlim(78, 99); ax.set_ylim(78, 99); ax.set_xticks(range(80, 100, 5)); ax.set_yticks(range(80, 100, 5))
    ax.set_xlabel('Reported benchmark score (answers credited, of 100)')
    ax.set_ylabel('Answers matching the consensus\nanswer of 25 runs (of 100)')
    grid_x(ax); grid_y(ax)
    ax.legend(handles=env_handles(ms=3.6) + [Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, mew=0.8, ms=3.6,
                                                    label='Open symbol: score labelled\npredicted in the archive')], loc='lower right', fontsize=5.0)
    sd['a_consensus_proxy'] = pd.DataFrame([dict(p, execution_condition=ENV_LABEL[p['execution_condition']]) for e in ENVS for p in pts if p['execution_condition'] == e])
    ax = fig.add_axes([0.51, 0.16, 0.45, 0.64])
    panel_label(fig, 0.44, 0.99, 'b'); panel_title(fig, 0.44, 0.99, '82 of 100 CompBioBench tasks have a strong consensus answer')
    sup = [modal[t][1] for t in tasks]
    cnt = collections.Counter(sup)
    xs_ = list(range(min(sup), 26))
    ax.bar(xs_, [cnt.get(x, 0) for x in xs_], color=[NEUTRAL_MID if x < 20 else NEUTRAL_DARK for x in xs_], width=0.8)
    ax.axvline(19.5, color=INK2, lw=0.5, ls=(0, (2, 2)))
    top = max(cnt.values())
    ax.text(5.3, top * 0.97, f'Dark bars, strong consensus (20 or more of 25 runs agree):\n{sum(1 for s in sup if s >= 20)} tasks, used to identify probable failures\n'
            'and split replicate sets', fontsize=5.1, va='top')
    ax.text(5.3, top * 0.66, f'Light bars, contested (fewer than 20 agree):\n{sum(1 for s in sup if s < 20)} tasks, not used', fontsize=5.1, va='top')
    ax.set_xticks(range(5, 26, 5)); ax.set_xlabel('Runs giving the most common answer (of 25)'); ax.set_ylabel('Tasks'); grid_y(ax)
    sd['b_consensus_support'] = pd.DataFrame([dict(task=t, runs_with_most_common_answer=modal[t][1]) for t in tasks])
    save_ed(fig, 'ED_Fig2', OUTDIR)
    source_data('ED_Fig2', sd)


# =====================================================================================================
def ed3():
    fig = plt.figure(figsize=(W_ED, 85 * MM))
    sd = {}
    sens = {r['config']: r for r in D['iwc_sensitivity']}
    order = CONFIGS + ['All four']
    lab = {**{c: CFG_ROW[c] for c in CONFIGS}, 'All four': 'Four Codex model\nconfigurations, pooled'}
    ax = fig.add_axes([0.16, 0.14, 0.33, 0.66])
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'The IWC condition difference rests on a few\nzero-scored open-ended code runs')
    rows = []
    for i, c in enumerate(order):
        r = sens[c]
        y = i * 1.3
        ax.plot([r['loto_low'], r['loto_high']], [y - 0.28, y - 0.28], color='#AAAAAA', lw=2.2, solid_capstyle='butt')
        ax.plot(r['nine'], y - 0.28, 'o', ms=3.6, mfc=INK, mec='white', mew=0.4)
        ax.plot(r['no_zero'], y + 0.05, 'D', ms=3.2, mfc=OI_ORANGE, mec='white', mew=0.4)
        ax.plot(r['with_host'], y + 0.35, '^', ms=3.4, mfc=NEUTRAL_MID, mec='white', mew=0.4)
        ax.text(1.02, y, f"{signed(r['nine'], 3)} → {signed(r['no_zero'], 3)}", transform=ax.get_yaxis_transform(), fontsize=5.0, va='center')
        rows.append(dict(model_configuration=lab[c].replace('\n', ' '), nine_task_difference=r['nine'], leave_one_task_out_low=r['loto_low'],
                         leave_one_task_out_high=r['loto_high'], sign_stable_under_leave_one_task_out=r['sign_stable'],
                         difference_excluding_tasks_with_a_zero_scored_run=r['no_zero'], tasks_removed=r['no_zero_removed'], difference_retaining_host_removal=r['with_host']))
    ax.axvline(0, color=INK2, lw=0.5, ls=(0, (2, 2)))
    ax.set_yticks([i * 1.3 for i in range(len(order))]); ax.set_yticklabels([lab[c] for c in order], fontsize=5.1)
    ax.set_ylim(len(order) * 1.3 - 0.6, -0.8); ax.set_xlim(-0.06, 0.11); grid_x(ax)
    ax.set_xlabel('Condition difference in mean output agreement, Galaxy − open-ended code')
    ax.text(1.02, -0.65, 'Nine tasks →\nno zero tasks', transform=ax.get_yaxis_transform(), fontsize=5.0, fontweight='bold', va='center')
    ax.legend(handles=[Line2D([], [], marker='o', ls='', mfc=INK, mec='white', ms=3.6, label='Nine matched tasks'),
                       Line2D([], [], color='#AAAAAA', lw=2.2, label='Range when leaving one task out'),
                       Line2D([], [], marker='D', ls='', mfc=OI_ORANGE, mec='white', ms=3.2, label='Tasks with a zero-scored run removed'),
                       Line2D([], [], marker='^', ls='', mfc=NEUTRAL_MID, mec='white', ms=3.4, label='Host-read removal retained where scored')],
              loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, fontsize=5.0)
    sd['a_sensitivity'] = pd.DataFrame(rows)
    # ---- b: the zero-scored and conflicting runs behind the difference
    axb = fig.add_axes([0.60, 0.06, 0.39, 0.80]); axb.axis('off')
    panel_label(fig, 0.56, 0.99, 'b'); panel_title(fig, 0.56, 0.99, 'Every IWC run below 0.5 and its traced cause')
    low = sorted([p for p in D['fig2d'] if p['score'] is not None and p['score'] < 0.5], key=lambda p: (ENVS.index(p['condition']), p['task'], p['config']))
    cause = {'Pseudobulk DE': 'Hand-written multiple-testing correction was wrong', 'Amplicon denoising': 'Sample names lost capital letters',
             'Mitogenome assembly': 'Wrong contig submitted (no mitochondrial identity check)',
             'Host-read removal': 'Score conflict: correct BWA-MEM output scored against the Bowtie2 reference'}
    rowsb = []
    for k, p in enumerate(low):
        y = 0.95 - k * 0.112
        task = p['task_label'].replace(' DE', ' differential expression').replace('Mitogenome', 'Mitochondrial genome')
        cfg = CFG_ROW[p['config']].replace(chr(10), ' ')
        axb.plot([0.008], [y - 0.012], ENV_MARKER[p['condition']], ms=3.4, mfc=ENV_COLOR[p['condition']], mec='white', mew=0.4, transform=axb.transAxes, clip_on=False)
        axb.text(0.03, y, f"{task} · output agreement {p['score']:.3f}", fontsize=5.0, fontweight='bold', va='top', transform=axb.transAxes)
        axb.text(0.03, y - 0.034, f"{cfg}, replicate run {p['replicate']}", fontsize=5.0, va='top', transform=axb.transAxes)
        axb.text(0.03, y - 0.068, cause[p['task_label']], fontsize=5.0, va='top', transform=axb.transAxes)
        rowsb.append(dict(execution_condition=ENV_LABEL_LONG[p['condition']], task=task, model_configuration=cfg, replicate_run=p['replicate'],
                          output_agreement=p['score'], traced_cause=cause[p['task_label']]))
    axb.legend(handles=env_handles(ms=3.2), loc='lower left', bbox_to_anchor=(0.0, 0.98), ncol=2, fontsize=5.0)
    axb.text(0.0, 0.95 - len(low) * 0.112 - 0.005, 'Removing the three open-ended code tasks with a zero-scored run reduces the pooled\ncondition difference from 0.040 to 0.004 (Supplementary Tables 12 and 18).',
             fontsize=5.0, color=INK2, va='top', transform=axb.transAxes)
    sd['b_runs_below_0_5'] = pd.DataFrame(rowsb)
    save_ed(fig, 'ED_Fig3', OUTDIR)
    source_data('ED_Fig3', sd)


# =====================================================================================================
def ed4():
    fig = plt.figure(figsize=(W_ED, 80 * MM))
    sd = {}
    up = D['skill_uptake']
    ax = fig.add_axes([0.20, 0.15, 0.27, 0.58])
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'In the Galaxy condition, DeepSeek V4 Pro opened the bundled\ndomain skill least often (BixBench-Verified-50)')
    rows = []
    for i, c in enumerate(CFG5):
        for env, off in (('open_ended_code', -0.19), ('galaxy', 0.19)):
            k, n = up[f'{c}|{env}']
            v = 100 * k / n
            ax.barh(i + off, v, height=0.36, color=ENV_COLOR[env])
            ax.text(v + 1.5, i + off, f'{v:.0f}%', va='center', fontsize=5.0)
            rows.append(dict(model_configuration=CFG_ROW[c].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[env], runs_opening_the_relevant_skill=k,
                             runs_on_skill_relevant_tasks=n, percent=round(v, 1)))
    ax.set_yticks(range(len(CFG5))); ax.set_yticklabels([CFG_ROW[c] for c in CFG5], fontsize=5.1); ax.set_ylim(len(CFG5) - 0.5, -0.6)
    ax.set_xlim(0, 100); ax.set_xlabel(f"Runs that opened the relevant domain skill (%; {D['skill_relevant_tasks']} tasks\nwith a relevant skill, {up['GPT-5.5|galaxy'][1]} runs per bar)"); grid_x(ax)
    ax.legend(handles=[Patch(fc=ENV_COLOR[e], label=ENV_LABEL_LONG[e]) for e in ENVS], loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, fontsize=5.0)
    sd['a_domain_skill_uptake'] = pd.DataFrame(rows)
    ax = fig.add_axes([0.70, 0.15, 0.27, 0.58])
    panel_label(fig, 0.51, 0.99, 'b'); panel_title(fig, 0.51, 0.99, 'DeepSeek V4 Pro (Codex) alone scripted the Galaxy\ninterface library from the shell')
    ca = D['core_library_accuracy']
    rowsb = []
    for i, c in enumerate(CONFIGS):
        r = ca[c]
        ax.barh(i, 100 * r['scripted'] / r['runs'], height=0.6, color=GALAXY)
        ax.barh(i, 100 * r['read_only'] / r['runs'], left=100 * r['scripted'] / r['runs'], height=0.6, color='#9DC3E0')
        txt = (f"{r['scripted']} scripted, {r['read_only']} read only\n(of {r['runs']} runs)" if r['read_only'] else f"{r['scripted']} of {r['runs']}")
        ax.text(100 * (r['scripted'] + r['read_only']) / r['runs'] + 1.5, i, txt, va='center', fontsize=5.0)
        rowsb.append(dict(model_configuration=CFG_ROW[c], galaxy_condition_runs=r['runs'], runs_importing_the_interface_library_in_shell_code=r['scripted'],
                          runs_only_reading_its_source=r['read_only'], scored_correct_when_scripted=r['scripted_correct'],
                          scored_correct_otherwise=r['other_correct']))
    ds = ca['DeepSeek V4 Pro']
    ax.set_yticks(range(len(CONFIGS))); ax.set_yticklabels([CFG_ROW[c] for c in CONFIGS], fontsize=5.1); ax.set_ylim(len(CONFIGS) - 0.5, -0.6)
    ax.set_xlim(0, 60); ax.set_xlabel('BixBench-Verified-50 Galaxy-condition runs (%)'); grid_x(ax)
    ax.legend(handles=[Patch(fc=GALAXY, label='Imported into a shell script'), Patch(fc='#9DC3E0', label='Read its source only')],
              loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, fontsize=5.0)
    fig.text(0.53, 0.015, f"Scored correct: {ds['scripted_correct']} of {ds['scripted']} scripted runs and {ds['other_correct']} of {ds['runs'] - ds['scripted']} other\n"
             "DeepSeek V4 Pro (Codex) runs. Codex execution traces.", fontsize=5.0, color=INK2, linespacing=1.2)
    sd['b_interface_library_scripting'] = pd.DataFrame(rowsb)
    save_ed(fig, 'ED_Fig4', OUTDIR)
    source_data('ED_Fig4', sd)


# =====================================================================================================
def ed5():
    fig = plt.figure(figsize=(W_ED, 110 * MM))
    sd = {}
    dv = D['divergence_by_config']
    ax = fig.add_axes([0.17, 0.10, 0.30, 0.66])
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'Divergence mechanisms by model configuration\n(BixBench-Verified-50, split replicate sets)')
    ynames = {'DeepSeek V4 Pro': 'DeepSeek V4 Pro (Codex)'}
    rows, ys, labels = [], [], []
    y = 0
    for c in CFG5:
        name = ynames.get(c, c)
        ax.text(-0.03, y, CFG_ROW[c], transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=5.2, fontweight='bold', linespacing=1.05)
        y += 1
        for env in ENVS:
            cnt = dv.get(f'{env}|{c}', {})
            left = 0
            for key, nm, col in MECH:
                v = cnt.get(key, 0)
                if v:
                    ax.barh(y, v, left=left, color=col, height=0.72, ec=INK2 if key in HATCH else 'white', lw=0.5, hatch=HATCH.get(key))
                    if v >= 2:
                        ax.text(left + v / 2, y, str(v), ha='center', va='center', fontsize=5.0, color='white' if col in DARK_FILL else INK)
                    left += v
                    rows.append(dict(model_configuration=CFG_ROW[c].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[env], divergence_mechanism=nm.replace('\n', ' '),
                                     scored_incorrect_replicate_runs=v))
            ax.text(left + 0.4, y, str(left), va='center', fontsize=5.0, color=INK2)
            labels.append(ENV_LABEL[env]); ys.append(y); y += 1
        y += 0.35
    ax.set_yticks(ys); ax.set_yticklabels(labels, fontsize=5.0); ax.set_ylim(y + 0.1, -1.3); ax.set_xlim(0, 25)
    ax.set_xlabel('Scored-incorrect replicate runs in split replicate sets'); grid_x(ax)
    axl = fig.add_axes([0.52, 0.52, 0.18, 0.30]); axl.axis('off')
    for k, (key, nm, col) in enumerate(MECH):
        yk = 0.97 - k * 0.14
        axl.add_patch(Rectangle((0.0, yk - 0.045), 0.07, 0.09, fc=col, ec=INK2 if key in HATCH or col == NEUTRAL_LIGHT else 'none', lw=0.3,
                                hatch=HATCH.get(key), transform=axl.transAxes))
        axl.text(0.1, yk, nm.replace('\n', ' '), fontsize=5.0, va='center', transform=axl.transAxes)
    sd['a_divergence_by_model_configuration'] = pd.DataFrame(rows)
    # ---- b: IWC within-set range and split Galaxy-condition replicate sets
    lev = collections.defaultdict(list)
    for p in D['fig2d']:
        lev[(p['condition'], p['config'], p['task_label'])].append(p['score'])
    axb = fig.add_axes([0.52, 0.06, 0.47, 0.36]); axb.axis('off')
    panel_label(fig, 0.505, 0.47, 'b'); panel_title(fig, 0.505, 0.47, 'IWC: the five split Galaxy-condition replicate sets')
    why = {('GPT-5.5', 'Peptide verification'): 'Replicate run 2 used the older PepQuery 1.6.2 wrapper (0.908); runs 1 and 3 used PepQuery2 2.0.2.',
           ('GPT-5.6 Sol', 'Peptide verification'): 'Replicate run 3 used the older PepQuery 1.6.2 wrapper (0.908).',
           ('GPT-5.6 Luna', 'Peptide verification'): 'Run 2 used PepQuery 1.6.2 (0.868); run 3 used PepQuery2, but its unrestricted-\nmodification step searched no protein sequences (0.900).',
           ('GPT-5.5', 'Mitogenome assembly'): 'Replicate run 1 submitted a nuclear contig without checking mitochondrial identity (0.000).',
           ('GPT-5.6 Luna', 'Host-read removal'): 'Score conflict in runs 1 and 3: correct BWA-MEM output scored against the Bowtie2\nreference (0.273; run record 0.9999 and 1.0).'}
    split = [(k, v) for k, v in sorted(lev.items()) if k[0] == 'galaxy' and None not in v and max(v) - min(v) > 0.05]
    rowsb = []
    for i, ((env, c, t), v) in enumerate(split):
        yk = 0.97 - i * 0.19
        axb.text(0.0, yk, f"{CFG_ROW[c]} · {t.replace('Mitogenome', 'Mitochondrial genome')} · output agreement {', '.join(f'{x:.3f}' for x in v)}",
                 fontsize=5.1, fontweight='bold', va='top', transform=axb.transAxes)
        axb.text(0.0, yk - 0.06, why[(c, t)], fontsize=5.0, va='top', transform=axb.transAxes, linespacing=1.15)
        rowsb.append(dict(model_configuration=CFG_ROW[c], task=t, replicate_runs='; '.join(f'{x:.3f}' for x in v), within_set_range=round(max(v) - min(v), 3),
                          cause=why[(c, t)].replace('\n', ' ')))
    sd['b_iwc_split_galaxy_sets'] = pd.DataFrame(rowsb)
    fig.text(0.52, 0.03, 'Amplicon denoising split only in the open-ended code condition (three model configurations).', fontsize=5.0, color=INK2)
    save_ed(fig, 'ED_Fig5', OUTDIR)
    source_data('ED_Fig5', sd)


# =====================================================================================================
def ed6():
    fig = plt.figure(figsize=(W_ED, 110 * MM))
    sd = {}
    tm, bx = D['input_tokens'], D['bix_accuracy']
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'On no benchmark was the lowest-input model configuration the least accurate (Galaxy condition)')
    perf = {'IWC': {c: D['iwc_levels'][f'{c}|galaxy']['ten_mean'] for c in CONFIGS},
            'BixBench50': {c: bx[f'{c}|galaxy']['run_level'] for c in CFG5},
            'CompBio': {c: D['compbio_scores'][f'{c}|galaxy']['mean'] for c in CONFIGS}}
    ylab = {'IWC': 'Mean output agreement\n(all ten tasks)', 'BixBench50': 'Accuracy (%)', 'CompBio': 'Reported benchmark\nscore (of 100)'}
    markers = {'GPT-5.5': 'o', 'GPT-5.6 Sol': 's', 'GPT-5.6 Luna': '^', 'DeepSeek V4 Pro': 'D', SUPERSEDED: 'v'}
    rows = []
    for k, b in enumerate(['IWC', 'BixBench50', 'CompBio']):
        ax = fig.add_axes([0.07 + k * 0.33, 0.58, 0.24, 0.30])
        for c, v in perf[b].items():
            x = tm[f'{b}|{c}|galaxy']['median'] / 1e6
            ax.scatter([x], [v], marker=markers[c], s=18, color=GALAXY, ec='white', lw=0.4, zorder=3)
            right = x > 5
            ax.annotate(CFG_ROW[c].replace('\n', ' ').replace(' (Claude Code, superseded)', ' (Claude Code)'), (x, v), xytext=(-4 if right else 4, 3),
                        textcoords='offset points', fontsize=5.0, ha='right' if right else 'left')
            rows.append(dict(benchmark=BENCH_LABEL[b], model_configuration=CFG_ROW[c].replace('\n', ' '), median_input_tokens_millions=round(x, 3), galaxy_condition_performance=round(v, 4)))
        ax.set_xscale('log'); ax.set_xlim(0.8, 20); ax.set_xticks([1, 2, 5, 10]); ax.set_xticklabels(['1', '2', '5', '10'])
        ax.xaxis.set_minor_locator(plt.NullLocator())
        ax.set_xlabel('Median input-token usage per run\n(millions; log scale)'); ax.set_ylabel(ylab[b]); grid_x(ax); grid_y(ax)
        ax.set_title(BENCH_LABEL[b], fontsize=5.6, fontweight='bold', loc='left')
    sd['a_tokens_versus_performance'] = pd.DataFrame(rows)
    # ---- b: model differences relative to GPT-5.5 (B15)
    panel_label(fig, 0.005, 0.43, 'b'); panel_title(fig, 0.005, 0.43, 'BixBench-Verified-50: more input tokens did not buy accuracy (each model configuration versus GPT-5.5)')
    axt = fig.add_axes([0.20, 0.08, 0.14, 0.27]); axa = fig.add_axes([0.42, 0.08, 0.14, 0.27])
    recs = {(('galaxy' if r['env'] == 'Galaxy' else 'open_ended_code'), r['config']): r for r in D['fig5c']}
    cfgs = ['GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro (Codex)', SUPERSEDED]
    yl = {'GPT-5.6 Sol': 'GPT-5.6 Sol', 'GPT-5.6 Luna': 'GPT-5.6 Luna', 'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro (Codex)', SUPERSEDED: 'DeepSeek V4 Pro (Claude Code)'}
    ys, labels, rowsc = [], [], []
    y = 0
    for env in ENVS:
        axt.text(-0.02, y, ENV_LABEL_LONG[env], transform=axt.get_yaxis_transform(), ha='right', va='center', fontsize=5.3, fontweight='bold')
        y += 1
        for cfg in cfgs:
            r = recs[(env, cfg)]
            (a_, al, ah), (t, tl, th) = r['acc_diff'], r['token_ratio']
            for ax_, (e_, lo_, hi_) in ((axt, (t, tl, th)), (axa, (a_, al, ah))):
                ax_.plot([lo_, hi_], [y, y], color=ENV_COLOR[env], lw=0.9)
                dot(ax_, e_, y, env, ms=3.4)
            axt.text(1.02, y, f'{t:.2f}', transform=axt.get_yaxis_transform(), fontsize=5.0, va='center')
            axa.text(1.02, y, signed(a_, 1), transform=axa.get_yaxis_transform(), fontsize=5.0, va='center')
            ys.append(y); labels.append(yl[cfg])
            rowsc.append(dict(execution_condition=ENV_LABEL_LONG[env], model_configuration=cfg, input_token_ratio_vs_gpt55=t, token_ci_low=tl, token_ci_high=th,
                              model_difference_accuracy_pp=a_, acc_ci_low=al, acc_ci_high=ah))
            y += 1
        y += 0.4
    for ax_ in (axt, axa):
        ax_.set_ylim(y - 0.6, -0.7); grid_x(ax_)
    axt.set_yticks(ys); axt.set_yticklabels(labels, fontsize=5.0); axa.set_yticks(ys); axa.set_yticklabels([])
    axt.axvline(1, color=INK2, lw=0.5, ls=(0, (2, 2))); axa.axvline(0, color=INK2, lw=0.5, ls=(0, (2, 2)))
    axt.set_xscale('log'); axt.set_xlim(0.8, 7); axt.set_xticks([1, 2, 4]); axt.set_xticklabels(['1', '2', '4']); axt.xaxis.set_minor_locator(plt.NullLocator())
    axa.set_xlim(-31, 7); axa.set_xticks([-30, -20, -10, 0])
    axt.set_xlabel('Input-token usage relative\nto GPT-5.5 (ratio; log scale)'); axa.set_xlabel('Model difference in accuracy\nversus GPT-5.5 (percentage points)')
    fig.text(0.62, 0.30, 'Lines: 95% confidence intervals.\nDashed lines: GPT-5.5 in the same execution condition\n(Supplementary Table 54).', fontsize=5.0, color=INK2, va='top')
    sd['b_model_differences'] = pd.DataFrame(rowsc)
    save_ed(fig, 'ED_Fig6', OUTDIR)
    source_data('ED_Fig6', sd)


# =====================================================================================================
def ed7():
    fig = plt.figure(figsize=(W_ED, 100 * MM))
    sd = {}
    b35 = D['bix35']
    ax = fig.add_axes([0.20, 0.10, 0.36, 0.72])
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'bix-35-q1: the metric each PhyKIT job actually ran,\nfor every Galaxy-condition run')
    col = {'evolutionary_rate': GALAXY, 'total_tree_length': OI_BLACK}
    rows = []
    for i, r in enumerate(b35):
        for j, jb in enumerate(r['jobs']):
            ax.add_patch(Rectangle((j + 0.08, i - 0.34), 0.84, 0.68, fc=col.get(jb['metric'], NEUTRAL_MID), ec='white', lw=0.5))
            rows.append(dict(model_configuration=r['config'], replicate_run=r['replicate'], job_order=j + 1, galaxy_job=jb['job'], job_state=jb['state'], metric_executed=jb['metric']))
        if not r['jobs']:
            ax.text(0.1, i, 'no PhyKIT wrapper job (user-defined tool)', fontsize=5.0, color=INK2, va='center')
        ax.text(5.4, i, r['answer'], fontsize=5.0, va='center', color=INK, fontweight='normal' if r['correct'] else 'bold')
    ax.set_xlim(0, 6.2); ax.set_ylim(len(b35) - 0.5, -0.8)
    ax.set_yticks(range(len(b35))); ax.set_yticklabels([f"{CFG_ROW.get(r['config'], r['config']).replace(chr(10), ' ').replace(' (Claude Code, superseded)', ' (Claude Code)')}, run {r['replicate']}" for r in b35], fontsize=5.0)
    ax.set_xticks([0.5, 1.5, 2.5, 3.5, 4.5]); ax.set_xticklabels(['1', '2', '3', '4', '5'])
    ax.set_xlabel('PhyKIT metrics jobs in the analysis history, in order of creation')
    ax.text(5.4, -0.65, 'Answer', fontsize=5.0, fontweight='bold', va='center')
    for s_ in ('left', 'bottom'):
        ax.spines[s_].set_visible(True)
    ax.legend(handles=[Patch(fc=GALAXY, label='Ran "evolutionary rate" (requested)'), Patch(fc=OI_BLACK, label='Ran "total tree length" (default metric)')],
              loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, fontsize=5.0)
    sd['a_phykit_jobs'] = pd.DataFrame(rows)
    axt = fig.add_axes([0.62, 0.08, 0.37, 0.78]); axt.axis('off')
    panel_label(fig, 0.60, 0.99, 'b'); panel_title(fig, 0.60, 0.99, 'Which request shapes bound the metric')
    tbl = [('Request shape (tool-state format)', 'Metric executed'),
           ('Flat keys, 21.01 format\n(operation|selector)', 'Default: total tree length'),
           ('Nested conditional with selector,\n21.01 format', 'Default: total tree length'),
           ('Nested conditional with\n__current_case__, 21.01 format', 'Default: total tree length'),
           ('Flat keys, legacy format', 'Requested: evolutionary rate')]
    for k, (a, b) in enumerate(tbl):
        y = 0.94 - k * 0.12
        axt.text(0.0, y, a, fontsize=5.1 if k else 5.2, fontweight='bold' if k == 0 else 'normal', va='top', transform=axt.transAxes, linespacing=1.15)
        axt.text(0.60, y, b, fontsize=5.1 if k else 5.2, fontweight='bold' if k == 0 else 'normal', va='top', transform=axt.transAxes)
        if k == 0:
            axt.plot([0, 1], [y - 0.05, y - 0.05], color=INK, lw=0.5, transform=axt.transAxes)
    axt.text(0.0, 0.30, 'Every job returned the state "ok". The Galaxy interface compared requested\nwith resolved parameters and flagged a mismatch whenever the request named\n'
             'the metric; six runs resubmitted and were scored correct. The failing run\nremoved the selector key, so there was nothing to compare and no flag\nwas raised.\n\n'
             'Source: command lines of the archived Galaxy job records (--metric);\nrequest shapes from the execution traces (individual_error_analysis.md,\nbix-35-q1).',
             fontsize=5.0, va='top', transform=axt.transAxes, color=INK2, linespacing=1.2)
    sd['b_request_shapes'] = pd.DataFrame(tbl[1:], columns=list(tbl[0]))
    save_ed(fig, 'ED_Fig7', OUTDIR)
    source_data('ED_Fig7', sd)


# =====================================================================================================
def ed8():
    fig = plt.figure(figsize=(W_ED, 120 * MM))
    sd = {}
    it = D['integrity']
    bench_of = {c['task']: c['benchmark'] for c in D['task_cases']}
    # ---- a: benchmark-answer retrieval
    ax = fig.add_axes([0.20, 0.64, 0.30, 0.22])
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'Agents retrieved, or tried to retrieve, benchmark answers\nonline in 26 of the 93 audited task cases')
    cls = list(it['retrieval'])
    rows = []
    for i, k in enumerate(cls):
        left = 0
        for b, colr in zip(BENCH, [NEUTRAL_DARK, NEUTRAL_MID, NEUTRAL_LIGHT]):
            v = sum(1 for t in it['retrieval'][k] if bench_of[t] == b)
            if v:
                ax.barh(i, v, left=left, color=colr, height=0.6, ec='white', lw=0.5)
                ax.text(left + v / 2, i, str(v), ha='center', va='center', fontsize=5.0, color='white' if colr == NEUTRAL_DARK else INK)
            left += v
        for t in it['retrieval'][k]:
            rows.append(dict(retrieval_class=k, benchmark=BENCH_LABEL[bench_of[t]], task=t))
    ax.set_yticks(range(len(cls))); ax.set_yticklabels(['Benchmark answer, key or\nanother agent\'s answer obtained', 'Source paper, dataset or\nworkflow settings that fix the answer',
                                                         'Attempted; nothing\nusable obtained'], fontsize=5.1)
    ax.set_ylim(len(cls) - 0.5, -0.5); ax.set_xlim(0, 12); ax.set_xlabel('Task cases'); grid_x(ax)
    ax.legend(handles=[Patch(fc=c, label=BENCH_LABEL[b]) for b, c in zip(BENCH, [NEUTRAL_DARK, NEUTRAL_MID, NEUTRAL_LIGHT])],
              loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=3, fontsize=5.0)
    fig.text(0.56, 0.87, 'Tasks where an answer was obtained:\n' + textwrap.fill(', '.join(it['retrieval'][cls[0]]), 90, break_on_hyphens=False), fontsize=5.0, va='top', linespacing=1.2)
    fig.text(0.56, 0.76, 'Sources included one public dataset of another group\'s agent traces, the BixBench\nrows on Hugging Face (with the "ideal" answer), source papers and the lab\'s own\n'
             'results page. Retrieval was concentrated in the DeepSeek V4 Pro configurations.', fontsize=5.0, va='top', color=INK2, linespacing=1.2)
    sd['a_answer_retrieval'] = pd.DataFrame(rows)
    # ---- b: local computation in the Galaxy condition
    ax = fig.add_axes([0.16, 0.10, 0.22, 0.33])
    panel_label(fig, 0.005, 0.54, 'b'); panel_title(fig, 0.005, 0.54, 'Galaxy-condition CompBioBench answers computed in the\nlocal shell after user-defined-tool execution failed')
    ok = collections.Counter(c for _, c, _ in it['local_fallback_correct'])
    bad = collections.Counter(c for _, c, _ in it['local_fallback_incorrect'])
    rowsb = []
    for i, c in enumerate(CONFIGS):
        ax.barh(i, ok.get(c, 0), color=GALAXY, height=0.6)
        ax.barh(i, bad.get(c, 0), left=ok.get(c, 0), color='white', ec=GALAXY, hatch='//////', height=0.6, lw=0.6)
        ax.text(ok.get(c, 0) + bad.get(c, 0) + 0.3, i, f"{ok.get(c, 0)} correct" + (f", {bad.get(c, 0)} incorrect" if bad.get(c, 0) else ''), va='center', fontsize=5.0)
    for t, c, r in it['local_fallback_correct'] + it['local_fallback_incorrect']:
        rowsb.append(dict(task=t, model_configuration=CFG_ROW[c], replicate_run=r, answer_scored_against_reference='correct' if (t, c, r) in it['local_fallback_correct'] else 'incorrect'))
    ax.set_yticks(range(len(CONFIGS))); ax.set_yticklabels([CFG_ROW[c] for c in CONFIGS], fontsize=5.1); ax.set_ylim(len(CONFIGS) - 0.5, -0.6)
    ax.set_xlim(0, 17); ax.set_xlabel('Galaxy-condition runs (CompBioBench)'); grid_x(ax)
    ax.legend(handles=[Patch(fc=GALAXY, label='Scored correct'), Patch(fc='white', ec=GALAXY, hatch='//////', label='Scored incorrect')],
              loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, fontsize=5.0)
    tasks = collections.Counter(t for t, _, _ in it['local_fallback_correct'])
    fig.text(0.49, 0.46, 'Correct answers computed locally, by task:\n' + '\n'.join(f'{t}: {n}' for t, n in tasks.most_common()), fontsize=5.0, va='top', linespacing=1.2)
    sd['b_local_computation'] = pd.DataFrame(rowsb)
    # ---- c: cross-run copying
    panel_label(fig, 0.73, 0.54, 'c'); panel_title(fig, 0.73, 0.54, 'Answers copied between runs\nthrough the shared Galaxy account')
    for k, (t, c, r, what) in enumerate(it['cross_run']):
        fig.text(0.75, 0.44 - k * 0.14, f'{t}\n{CFG_ROW[c]}, Galaxy condition,\nreplicate run {r}: ' + textwrap.fill(what, 42, initial_indent=' ' * 18).lstrip(),
                 fontsize=5.0, va='top', linespacing=1.2)
    fig.text(0.75, 0.13, 'Both runs could read histories and job\noutputs left by other runs on the same\naccount. Replicate runs should use\nisolated Galaxy accounts.', fontsize=5.0, va='top', color=INK2, linespacing=1.2)
    sd['c_cross_run_copying'] = pd.DataFrame([dict(task=t, model_configuration=CFG_ROW[c], replicate_run=r, what_happened=w) for t, c, r, w in it['cross_run']])
    save_ed(fig, 'ED_Fig8', OUTDIR)
    source_data('ED_Fig8', sd)


if __name__ == '__main__':
    which = sys.argv[1:] or [str(i) for i in range(1, 9)]
    for w in which:
        globals()[f'ed{w}']()
        print('done ED Fig', w)
