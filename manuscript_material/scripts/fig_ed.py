"""Extended Data figures 1-5 and their Source Data workbooks.

Run from the repository root after build_data.py:  python manuscript_material/scripts/fig_ed.py [1 2 3 4 5]
Outputs: extended_data/ED_FigN.tif (300 dpi, RGB, LZW) and .eps, as required for Extended Data.
Design rules as in style.py: open-ended code first; vermillion squares = open-ended code, blue circles = Galaxy;
no abbreviations; panel titles state the finding.
"""
import collections
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
from style import (BENCH, BENCH_2L, BENCH_LABEL, CONFIGS, ENV_COLOR, ENV_LABEL, ENV_MARKER, ENVS, GALAXY, GRID,  # noqa: E402
                   INK, INK2, LIGHT, MM, NEUTRAL_DARK, NEUTRAL_LIGHT, NEUTRAL_MID, OI_BLACK, OI_ORANGE, OI_PURPLE, SUPERSEDED,
                   W_ED, env_handles, grid_x, grid_y, panel_label, panel_title, plt, save_ed)
from fig_main import dot, rnd, signed, source_data  # noqa: E402

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


def env_rows(ax, key_fn, cfgs=CFG5):
    """Per configuration: open-ended code row above, Galaxy row below. Returns y centre per configuration."""
    for i, cfg in enumerate(cfgs):
        for env, off in (('open_ended_code', -0.19), ('galaxy', 0.19)):
            yield i, cfg, env, i + off


# =====================================================================================================
def ed1():
    fig = plt.figure(figsize=(W_ED, 140 * MM))
    inv = D['inventory']
    sd = {}
    # ---- a: evidence inventory
    ax = fig.add_axes([0.0, 0.52, 0.53, 0.40]); ax.axis('off')
    panel_label(fig, 0.005, 0.995, 'a'); panel_title(fig, 0.005, 0.995, 'The archive analysed')
    led = json.load(open(os.path.join(ROOT, 'analysis_reports', 'galaxy_improvement_20260924', 'v2_trace_friction', 'ledger.json')))
    adj = {'BixBench50': sum(1 for x in led if x['b'] == 'BixBench'), 'CompBio': 'proxy (panel c)', 'IWC': sum(1 for x in led if x['b'] == 'IWC')}
    rows = [('Tasks', [inv[b]['tasks'] for b in BENCH]),
            ('Archived runs', [inv[b]['runs'] for b in BENCH]),
            ('Execution traces (one event log per run)', [inv[b]['traces'] for b in BENCH]),
            ('Galaxy-condition runs with a detailed analysis-history snapshot', [f"{inv[b]['detailed_histories'][0]:,} of {inv[b]['detailed_histories'][1]:,}" for b in BENCH]),
            ('Galaxy analysis jobs (excluding data uploads)', [inv[b]['nonfetch_jobs'] for b in BENCH]),
            ('   of which Galaxy job errors', [inv[b]['error_jobs'] for b in BENCH]),
            ('Galaxy interface calls', [inv[b]['mcp_calls'] for b in BENCH]),
            ('   of which returned a failure status', [inv[b]['mcp_failed'] for b in BENCH]),
            ('Runs adjudicated trace by trace', [adj[b] for b in BENCH])]
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
    ax.text(0.01, -0.02, 'CompBioBench keeps no per-question grades, so its probable failures come from the consensus proxy\n'
            'validated in c. Jobs are counted once per server and job identifier.', fontsize=5.0, color=INK2, transform=ax.transAxes, va='top')
    sd['a_archive'] = pd.DataFrame([dict(measure=lab.strip(), **{BENCH_LABEL[b]: v for b, v in zip(BENCH, vals)}) for lab, vals in rows])
    # ---- b: audit pipeline
    ax = fig.add_axes([0.575, 0.50, 0.425, 0.44]); ax.axis('off')
    panel_label(fig, 0.56, 0.995, 'b'); panel_title(fig, 0.56, 0.995, 'Trace-level audit pipeline')
    steps = [('Execution\ntraces', f"{sum(inv[b]['traces'] for b in BENCH):,} event logs, one per run"),
             ('Call extraction', f"{sum(inv[b]['mcp_calls'] for b in BENCH):,} Galaxy interface calls and all shell\ncommands, with status and parameter records"),
             ('Call classification', '7,389 failed Galaxy interface calls sorted into\n13 causes; 4,352 tool-run calls with parameter\nsubstitution'),
             ('Failure\nadjudication', '246 scored-incorrect BixBench-Verified-50 runs\nand 8 IWC runs with output agreement below 0.5:\nprimary and secondary cause, adjudication confidence'),
             ('Replicate-set\ncomparison', '81 scored-incorrect replicate runs in split\nreplicate sets (45 open-ended code, 36 Galaxy):\ndivergence mechanism versus scored-correct siblings')]
    for k, (t, d) in enumerate(steps):
        y = 0.83 - k * 0.19
        box(ax, 0.0, y, 0.27, 0.14, t, fc=LIGHT, ec=INK2, weight='bold', fs=5.4)
        ax.text(0.30, y + 0.07, d, fontsize=5.1, va='center', transform=ax.transAxes, linespacing=1.15)
        if k < len(steps) - 1:
            arrow(ax, 0.135, y, 0.135, y - 0.05)
    ax.text(0.30, 0.0, 'Also used: evaluator records, analysis-history\nsnapshots and independent checks (public reference\ngenomes, recomputed statistics)',
            fontsize=5.0, color=INK2, transform=ax.transAxes, va='top')
    # ---- c: consensus proxy validation
    ax = fig.add_axes([0.085, 0.075, 0.27, 0.315])
    panel_label(fig, 0.005, 0.44, 'c'); panel_title(fig, 0.005, 0.44, 'The consensus proxy reproduces the reported\nCompBioBench benchmark scores')
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
    ax.text(96.5, 97.8, 'Identity', fontsize=5.0, color=INK2, rotation=45, ha='center', va='bottom')
    mae = st.mean(abs(p['proxy_score'] - p['reported_benchmark_score']) for p in pts)
    bias = st.mean(p['proxy_score'] - p['reported_benchmark_score'] for p in pts)
    ax.text(0.03, 0.97, f'{len(pts)} reported benchmark scores with retained answers\nMean absolute error {mae:.1f}; mean bias +{bias:.1f}',
            transform=ax.transAxes, va='top', fontsize=5.2)
    ax.set_xlim(78, 99); ax.set_ylim(78, 99); ax.set_xticks(range(80, 100, 5)); ax.set_yticks(range(80, 100, 5))
    ax.set_xlabel('Reported benchmark score (answers credited, of 100)')
    ax.set_ylabel('Answers matching the consensus\nanswer of 25 runs (of 100)')
    grid_x(ax); grid_y(ax)
    ax.legend(handles=env_handles(ms=3.6) + [Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, mew=0.8, ms=3.6,
                                                    label='Open symbol: score labelled\npredicted in the archive')],
              loc='lower right', fontsize=5.0)
    sd['c_consensus_proxy'] = pd.DataFrame([dict(p, execution_condition=ENV_LABEL[p['execution_condition']]) for e in ENVS for p in pts if p['execution_condition'] == e])
    # ---- d: consensus strength
    ax = fig.add_axes([0.51, 0.075, 0.45, 0.315])
    panel_label(fig, 0.44, 0.44, 'd'); panel_title(fig, 0.44, 0.44, '82 of 100 CompBioBench tasks have a strong consensus answer')
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
    sd['d_consensus_support'] = pd.DataFrame([dict(task=t, runs_with_most_common_answer=modal[t][1]) for t in tasks])
    save_ed(fig, 'ED_Fig1', OUTDIR)
    source_data('ED_Fig1', sd)


# =====================================================================================================
def ed2():
    fig = plt.figure(figsize=(W_ED, 158 * MM))
    sd = {}
    # ---- a: cross-benchmark tool-set similarity (X3), open-ended code first
    ax = fig.add_axes([0.20, 0.655, 0.25, 0.235])
    panel_label(fig, 0.005, 0.995, 'a'); panel_title(fig, 0.005, 0.995, 'Tool-set similarity is highest on IWC tasks\nin both execution conditions')
    rows = []
    recs = {r['instrument']: r for r in D['ed2a']}
    groups = [('open_ended_code', 'Open-ended code', 'Open-ended code condition: command names'),
              ('galaxy', 'Galaxy', 'Galaxy condition: installed Galaxy tools')]
    ticks, labs = [], []
    for g, (env, inst, head) in enumerate(groups):
        base = g * 4.3
        ax.text(-0.70, base + 0.2, head, fontsize=5.3, fontweight='bold', va='center', ha='left', transform=ax.get_yaxis_transform())
        r = recs[inst]
        for k, b in enumerate(BENCH):
            y = base + 1 + k
            e, lo, hi = r['values'][k]
            ax.plot([lo, hi], [y, y], color=ENV_COLOR[env], lw=0.9)
            dot(ax, e, y, env)
            ticks.append(y); labs.append(f"{BENCH_LABEL[b]} ({r['n'][k]} replicate sets)")
            rows.append(dict(execution_condition=ENV_LABEL[env], benchmark=BENCH_LABEL[b], replicate_sets=r['n'][k], tool_set_similarity=e, ci_low=lo, ci_high=hi))
    ax.set_yticks(ticks); ax.set_yticklabels(labs, fontsize=5.1); ax.set_ylim(ticks[-1] + 0.6, -0.3); ax.set_xlim(0, 0.8)
    ax.set_xlabel('Tool-set similarity within replicate sets\n(mean pairwise Jaccard similarity; 95% confidence interval)'); grid_x(ax)
    fig.text(0.023, 0.935, 'Three GPT model configurations shared by all benchmarks. Tool-set fingerprints are measured differently in the two\n'
             'execution conditions, so compare benchmarks within a condition, not the conditions with each other.', fontsize=5.0, color=INK2, va='top')
    sd['a_tool_set_similarity'] = pd.DataFrame(rows)
    # ---- b: bix-45-q1
    ax = fig.add_axes([0.62, 0.655, 0.35, 0.255])
    panel_label(fig, 0.50, 0.995, 'b'); panel_title(fig, 0.50, 0.995, 'bix-45-q1: every Galaxy run returned the value of the\ncurrent PhyKIT release and was scored incorrect')
    ref = [r for r in D['ed2b'] if r['expected']][0]['expected']
    cur = 1.5197572608715265e-56
    for i, cfg in enumerate(CFG5):
        for env, off in (('open_ended_code', -0.2), ('galaxy', 0.2)):
            rr = sorted([r for r in D['ed2b'] if r['config'] == cfg and r['condition'] == env], key=lambda r: r['replicate'])
            for k, r in enumerate(rr):
                if r['value'] is not None:
                    dot(ax, -math.log10(r['value']), i + off + (k - 1) * 0.07, env, filled=r['accepted'], ms=3.4)
    ax.axvline(-math.log10(ref), color=INK, lw=0.6, ls=(0, (3, 2))); ax.axvline(-math.log10(cur), color=INK2, lw=0.5, ls=(0, (1, 1.5)))
    ax.text(-math.log10(ref) + 0.07, -0.72, 'Accepted reference, 7.70 × $10^{-54}$\n(reproduced by PhyKIT 2.0.3)', fontsize=5.0, va='center')
    ax.text(-math.log10(cur) + 0.07, -0.72, 'Current PhyKIT\nrelease and the\nGalaxy tool,\n1.52 × $10^{-56}$', fontsize=5.0, va='center', ha='left')
    ax.set_yticks(range(len(CFG5))); ax.set_yticklabels([CFG_ROW[c] for c in CFG5], fontsize=5.1); ax.set_ylim(len(CFG5) - 0.5, -1.35)
    ax.set_xlim(52.5, 57.4); ax.set_xlabel('Submitted P value, $-\\log_{10}$ (Mann–Whitney test of relative composition\nvariability, animals versus fungi)')
    grid_x(ax)
    ax.legend(handles=env_handles(ms=3.4) + [Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, mew=0.8, ms=3.4, label='Open symbol: scored incorrect')],
              loc='center', bbox_to_anchor=(0.43, 0.47), ncol=1, fontsize=5.0)
    sd['b_bix45q1'] = pd.DataFrame([dict(execution_condition=ENV_LABEL[r['condition']], model_configuration=r['config'], replicate_run=r['replicate'],
                                         submitted_p=r['value'], scored_correct=r['accepted']) for e in ENVS for r in D['ed2b'] if r['condition'] == e])
    # ---- c: bix-43-q2
    ax = fig.add_axes([0.20, 0.08, 0.25, 0.36])
    panel_label(fig, 0.005, 0.56, 'c'); panel_title(fig, 0.005, 0.56, 'bix-43-q2: the same value was scored correct or incorrect\ndepending on the verifier mode')
    rr = [r for r in D['ed2c'] if r['value'] is not None]
    exp = float([r for r in D['ed2c'] if r['expected']][0]['expected'])
    tol = [r['tolerance'] for r in D['ed2c'] if r['tolerance']][0]
    rounded = {c for c in CFG5 if any(r['mode'] == 'str_verifier_rounded_numeric' for r in rr if r['config'] == c)}
    for i, cfg in enumerate(CFG5):
        if cfg in rounded:
            ax.axhspan(i - 0.48, i + 0.48, color='#efeee9', lw=0, zorder=0)
    ax.axvspan(exp - tol, exp + tol, color='#d9e6ef', lw=0, zorder=0.5)
    ax.axvline(exp, color=INK, lw=0.6, ls=(0, (3, 2)))
    for i, cfg in enumerate(CFG5):
        for env, off in (('open_ended_code', -0.2), ('galaxy', 0.2)):
            pts = sorted([r for r in rr if r['config'] == cfg and r['condition'] == env], key=lambda r: r['replicate'])
            for k, r in enumerate(pts):
                dot(ax, r['value'], i + off + (k - 1) * 0.07, env, filled=r['accepted'], ms=3.4)
    ax.set_yticks(range(len(CFG5))); ax.set_yticklabels([CFG_ROW[c] for c in CFG5], fontsize=5.1); ax.set_ylim(len(CFG5) - 0.5, -0.6)
    ax.set_xlim(5.6, 6.2); ax.set_xticks([5.6, 5.8, 6.0, 6.2]); grid_x(ax)
    ax.set_xlabel('Submitted odds ratio (one value of 7.17 lies off scale)')
    for i, cfg in enumerate(CFG5):
        ax.text(1.02, i, 'Rounded-numeric\nverifier' if cfg in rounded else 'Tolerance\nverifier', transform=ax.get_yaxis_transform(),
                fontsize=5.0, va='center', color=INK2)
    ax.annotate('The value 5.831005…\nwas scored correct\nunder the tolerance\nverifier (filled) and\nincorrect under the\nrounded-numeric\nverifier (open)',
                xy=(5.8335, 3.2), xytext=(5.895, 2.5), fontsize=5.0, va='center', arrowprops=dict(arrowstyle='-', lw=0.5, color=INK2))
    ax.legend(handles=env_handles(ms=3.4) + [Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, mew=0.8, ms=3.4, label='Open symbol: scored incorrect'),
                                              Patch(fc='#d9e6ef', label=f'Range scored correct, {exp} ± {tol:.3f}'),
                                              Patch(fc='#efeee9', label='Grey rows: rounded-numeric verifier')],
              loc='lower left', bbox_to_anchor=(-0.02, 1.01), ncol=2, fontsize=5.0)
    sd['c_bix43q2'] = pd.DataFrame([dict(execution_condition=ENV_LABEL[r['condition']], model_configuration=r['config'], replicate_run=r['replicate'],
                                         submitted_value=r['value'], scored_correct=r['accepted'], verifier_mode=r['mode']) for e in ENVS for r in rr
                                    if r['condition'] == e])
    # ---- d: IWC low scores
    panel_label(fig, 0.58, 0.56, 'd'); panel_title(fig, 0.58, 0.56, 'Low IWC output agreement re-examined\nagainst independent references')
    ax = fig.add_axes([0.66, 0.08, 0.095, 0.34])
    mito = D['ed2d_mito']
    for env, x0 in (('open_ended_code', 0), ('galaxy', 1)):
        v = [m['f1'] for m in mito if m['condition'] == env]
        ax.scatter(x0 + np.linspace(-0.22, 0.22, len(v)), v, s=9, marker=ENV_MARKER[env], color=ENV_COLOR[env], ec='white', lw=0.3, zorder=3)
    ax.set_xticks([0, 1]); ax.set_xticklabels(['Open-\nended code', 'Galaxy']); ax.set_xlim(-0.5, 1.5); ax.set_ylim(-0.05, 1.05)
    ax.set_ylabel('Overlap with reference genome OZ203683.1\n(F1 score of shared 31-base sequences)'); grid_y(ax)
    fig.text(0.60, 0.44, f'Mitochondrial genome\ncontigs (n = {len(mito)})', fontsize=5.4, fontweight='bold', va='bottom')
    ax.text(0.5, 0.22, '3 wrong contigs\nshare no 31-base\nsequences with\nthe reference', ha='center', va='center', fontsize=5.0, color=INK2)
    ax2 = fig.add_axes([0.885, 0.08, 0.095, 0.34])
    host = D['ed2d_host']
    luna, sol, bt = host['galaxy_gpt_5_6_luna_r1'], host['galaxy_gpt_5_6_sol_r1'], host['galaxy_gpt_5_6_luna_r2']
    bars = [('Galaxy output,\nGPT-5.6 Luna replicate\nrun 1 (BWA-MEM)', luna['candidate_retained'], GALAXY),
            ('Reference output,\nBWA-MEM route', sol['reference_retained'], NEUTRAL_DARK),
            ('Reference output,\nBowtie2 route\n(used for scoring)', bt['reference_retained'], NEUTRAL_MID)]
    ax2.barh(range(3), [b[1] for b in bars], color=[b[2] for b in bars], height=0.6)
    for i, b in enumerate(bars):
        ax2.text(b[1] + 2000, i, f'{int(b[1]):,}', va='center', fontsize=5.0)
    ax2.set_yticks(range(3)); ax2.set_yticklabels([b[0] for b in bars], fontsize=5.0); ax2.set_ylim(2.5, -0.5)
    ax2.set_xlim(0, 105000); ax2.set_xticks([0, 50000, 100000]); ax2.set_xticklabels(['0', '50,000', '100,000'])
    ax2.set_xlabel('Read pairs kept after\nhost-read removal'); grid_x(ax2)
    fig.text(0.80, 0.44, 'Host-read removal: score conflict\n(evaluator 0.273, run record 0.9999)', fontsize=5.4, fontweight='bold', va='bottom')
    sd['d_mitochondrial_contigs'] = pd.DataFrame([dict(execution_condition=ENV_LABEL[m['condition']], run=m['run'], f1=m['f1'], length=m['length'])
                                                  for e in ENVS for m in mito if m['condition'] == e])
    sd['d_host_removal'] = pd.DataFrame([dict(item=b[0].replace('\n', ' '), read_pairs_kept=b[1]) for b in bars])
    save_ed(fig, 'ED_Fig2', OUTDIR)
    source_data('ED_Fig2', sd)


# =====================================================================================================
TAX = [('A1', 'Tool description needs an analysis history'), ('A2', 'Tool identifier not found'), ('A3', 'Conditional option structure'),
       ('A4', 'Parameter value or data type'), ('A5', 'Dataset or analysis-history identifier'), ('A6', 'User-defined tool definition'),
       ('A7', 'Upload or file type'), ('A8', 'Server, connection or rate limit'), ('B1', 'User-defined tool: software missing'),
       ('B2', 'Job failed, no error message'), ('B3', 'Job failed with error message'), ('B4', 'File format, compression or index'),
       ('B5', 'Memory or compute limit')]
MISMATCH_NAME = {'filter_tabular': 'Filter table', 'datamash_ops': 'Datamash summaries', 'Add_a_column1': 'Add column',
                 'Grouping1': 'Group rows', 'tp_sort_header_tool': 'Sort table', 'phykit_metrics': 'PhyKIT tree metrics', 'deseq2': 'DESeq2',
                 'anndata_inspect': 'AnnData inspection', 'upload1': 'Upload file', 'Count1': 'Count occurrences', 'bwa_mem': 'BWA-MEM alignment',
                 'unzip': 'Unzip', 'fastp': 'fastp read trimming', 'regexColumn1': 'Column text replacement'}


def ed3():
    fig = plt.figure(figsize=(W_ED, 165 * MM))
    sd = {}
    scan = D['scan']
    # ---- a: user-defined tool reliability
    panel_label(fig, 0.005, 0.995, 'a'); panel_title(fig, 0.005, 0.995, 'User-defined tools often failed, usually without an error message')
    ax = fig.add_axes([0.07, 0.83, 0.40, 0.075])
    us = scan['udt_status']
    cats = [('ok', 'Succeeded', NEUTRAL_LIGHT), ('failed', 'Job failed', OI_BLACK), ('udt_creation_failed', 'Tool could not be created', OI_ORANGE),
            ('None', 'No status returned', NEUTRAL_MID), ('other', 'Other failure', OI_PURPLE)]
    other = sum(v for k, v in us.items() if k not in ('ok', 'failed', 'udt_creation_failed', 'None'))
    tot = sum(us.values()); left = 0; rows = []; handles = []
    for key, lab, col in cats:
        v = other if key == 'other' else us.get(key, 0)
        ax.barh(0, v, left=left, color=col, height=0.6, ec='white', lw=0.6)
        if v / tot > 0.08:
            ax.text(left + v / 2, 0, f'{lab}\n{v:,}', ha='center', va='center', fontsize=5.1, color='white' if col == OI_BLACK else INK)
        else:
            handles.append(Patch(fc=col, label=f'{lab} ({v:,})'))
        left += v; rows.append(dict(status=lab, calls=v))
    ax.legend(handles=handles, loc='lower right', bbox_to_anchor=(1.0, 1.02), ncol=3, fontsize=5.0)
    ax.set_xlim(0, tot); ax.set_yticks([]); ax.spines['left'].set_visible(False)
    ax.set_xlabel(f'Calls that ran a user-defined tool (n = {tot:,}); {100 * us.get("ok", 0) / tot:.0f}% succeeded')
    sd['a_user_defined_tool_status'] = pd.DataFrame(rows)
    ax = fig.add_axes([0.20, 0.575, 0.12, 0.15])
    fp = scan['failed_phase']
    ph = [('User-defined tool, failed\nbefore running, no message', fp.get('udt|pre_execution_or_command_rendering|no_text', 0), OI_BLACK),
          ('User-defined tool, failed\nwhile running, with message', fp.get('udt|command_runtime|stderr', 0), NEUTRAL_MID),
          ('Installed tool, failed\nwhile running, with message', fp.get('tool|command_runtime|stderr', 0), NEUTRAL_MID),
          ('Installed tool, failed\nbefore running, no message', fp.get('tool|pre_execution_or_command_rendering|no_text', 0), OI_BLACK)]
    ax.barh(range(4), [p[1] for p in ph], color=[p[2] for p in ph], height=0.62)
    for i, p in enumerate(ph):
        ax.text(p[1] + 25, i, f'{p[1]:,}', va='center', fontsize=5.0)
    ax.set_yticks(range(4)); ax.set_yticklabels([p[0] for p in ph], fontsize=5.0); ax.set_ylim(3.5, -0.5); ax.set_xlim(0, 1650)
    ax.set_xlabel('Galaxy job errors'); grid_x(ax)
    ax.set_title('Where Galaxy job errors occurred (black: no error message)', fontsize=5.3, loc='right', fontweight='bold', x=1.0)
    sd['a_failure_phase'] = pd.DataFrame([dict(phase=p[0].replace('\n', ' '), galaxy_job_errors=p[1]) for p in ph])
    ax = fig.add_axes([0.39, 0.575, 0.08, 0.15])
    an = scan['after_notext']
    nx = [('Same\nrequest', an.get('identical|failed', 0), an.get('identical|other', 0)),
          ('Changed\nrequest', an.get('modified|failed', 0), an.get('modified|other', 0))]
    for i, (lab, f, o) in enumerate(nx):
        ax.bar(i, f, color=OI_BLACK, width=0.62); ax.bar(i, o, bottom=f, color=NEUTRAL_LIGHT, width=0.62)
        ax.text(i, f / 2, f'{f}', ha='center', va='center', fontsize=5.0, color='white')
        ax.text(i, f + o + 25, f'{f + o}', ha='center', fontsize=5.0)
    ax.set_xticks([0, 1]); ax.set_xticklabels([n[0] for n in nx], fontsize=5.0); ax.set_ylim(0, 1150); grid_y(ax)
    ax.set_ylabel('Next call after a failure\nwith no error message')
    ax.legend(handles=[Patch(fc=OI_BLACK, label='Failed again'), Patch(fc=NEUTRAL_LIGHT, label='Other outcome')], fontsize=5.0, loc='upper left')
    pr = scan['probe']
    fig.text(0.023, 0.515, f"Agents also wrote {pr.get('CompBio|calls', 0):,} throwaway probe tools in {pr.get('CompBio|runs', 0)} of the 808 CompBioBench runs "
             f"that used user-defined tools\n(and {pr.get('BixBench50|calls', 0)} in {pr.get('BixBench50|runs', 0)} BixBench-Verified-50 runs) "
             "to find out why jobs failed, because Galaxy offers no trial run.", fontsize=5.0, color=INK2)
    sd['a_after_no_message'] = pd.DataFrame([dict(next_call=n[0].replace('\n', ' '), failed_again=n[1], other_outcome=n[2]) for n in nx])
    # ---- b: failed calls by cause, one small multiple per benchmark
    panel_label(fig, 0.53, 0.995, 'b'); panel_title(fig, 0.53, 0.995, 'Failed Galaxy interface calls by cause\n(per 1,000 calls)')
    tx, inv = D['ed3b'], D['inventory']
    ylab = [n for _, n in TAX]
    ypos = [i + (1.2 if c.startswith('B') else 0) for i, (c, _) in enumerate(TAX)]
    rows = []
    for k, b in enumerate(BENCH):
        ax = fig.add_axes([0.745 + k * 0.085, 0.555, 0.07, 0.37])
        vals = []
        for code, name in TAX:
            n = sum(v for kk, v in tx[b].items() if kk.split()[0] == code)
            vals.append(1000 * n / inv[b]['mcp_calls'])
            rows.append(dict(cause=name, stage='no job created' if code.startswith('A') else 'job created, then failed', benchmark=BENCH_LABEL[b],
                             failed_calls=n, interface_calls=inv[b]['mcp_calls'], per_1000=round(vals[-1], 2)))
        ax.barh(ypos, vals, color=GALAXY, height=0.66)
        for yv, v in zip(ypos, vals):
            if v >= 0.5:
                ax.text(v + 1, yv, f'{v:.0f}', va='center', fontsize=5.0)
        ax.set_ylim(ypos[-1] + 0.6, -1.4); ax.set_xlim(0, 48); ax.set_xticks([0, 20, 40]); grid_x(ax)
        ax.set_yticks(ypos); ax.set_yticklabels(ylab if k == 0 else [], fontsize=5.0)
        ax.set_title(BENCH_2L[b], fontsize=5.3, fontweight='bold')
        ax.axhline(8.1, color=INK2, lw=0.4)
        if k == 0:
            ax.text(-2.95, -1.0, 'No job was created:', transform=ax.get_yaxis_transform(), fontsize=5.1, fontweight='bold', va='center')
            ax.text(-2.95, 8.1, 'A job was created and failed:', transform=ax.get_yaxis_transform(), fontsize=5.1, fontweight='bold', va='center')
        if k == 1:
            ax.set_xlabel('Failed calls per 1,000 calls')
    fig.text(0.535, 0.515, '258 calls matched no cause and are not shown.', fontsize=5.0, color=INK2)
    sd['b_failed_calls_by_cause'] = pd.DataFrame(rows)
    # ---- c: tools with most parameter changes
    ax = fig.add_axes([0.16, 0.055, 0.30, 0.38])
    panel_label(fig, 0.005, 0.48, 'c'); panel_title(fig, 0.005, 0.48, 'Tools with the most parameter substitution')
    mt = scan['mismatch_tools']
    top = sorted(mt.items(), key=lambda kv: -sum(kv[1].values()))[:14]
    rows = []
    for i, (tool, v) in enumerate(top):
        b_, e_ = v.get('validation_parameter_mismatch', 0), v.get('parameter_mismatch', 0)
        ax.barh(i, b_, color=OI_ORANGE, height=0.66, ec='white', lw=0.5); ax.barh(i, e_, left=b_, color=OI_PURPLE, height=0.66, ec='white', lw=0.5)
        rows.append(dict(tool=MISMATCH_NAME.get(tool, tool), galaxy_tool_id=tool, blocked_before_submission=b_, executed_with_substitution=e_))
    ax.set_yticks(range(len(top))); ax.set_yticklabels([MISMATCH_NAME.get(t, t) for t, _ in top], fontsize=5.1); ax.set_ylim(len(top) - 0.5, -0.6)
    ax.set_xlabel('Tool-run calls with parameter substitution'); grid_x(ax)
    ax.legend(handles=[Patch(fc=OI_ORANGE, label="Blocked by the benchmark's check"), Patch(fc=OI_PURPLE, label='Executed with substituted values')],
              loc='lower right', fontsize=5.0)
    sd['c_parameter_substitution_by_tool'] = pd.DataFrame(rows)
    # ---- d: engineering targets
    axt = fig.add_axes([0.51, 0.02, 0.48, 0.44]); axt.axis('off')
    panel_label(fig, 0.50, 0.48, 'd'); panel_title(fig, 0.50, 0.48, 'Engineering targets derived from the traces')
    tbl = [('Validate tool settings strictly and report\nrequested-versus-used differences', '4,352 parameter substitutions;\n916 executed', 'Executed parameter\nsubstitutions = 0'),
           ('Select conditional options by value,\nnot by position', '220 option-structure errors;\none decisive failure (bix-35-q1)', 'One submission per\nconfigured tool'),
           ('Serve tool descriptions without\nrequiring an analysis history', '1,340 failures', 'No failures of this kind'),
           ('Return an error message for every\nGalaxy job error', '1,829 failures without a\nmessage; 784 identical retries', 'Failures without a\nmessage = 0; no probe\ntools needed'),
           ('Check user-defined tools before they\nrun (trial run, software, dispatch)', 'Half of user-defined-tool\ncalls failed; 79 missing software', 'First-attempt success\nrate'),
           ('Show software versions and what each\noutput statistic means', 'bix-45-q1 (0 of 15 scored correct);\nbix-28-q3 (a variance read\nas a median)', 'Version visible in\nsearch and inspection')]
    xs = [0.0, 0.42, 0.74]
    for x, h in zip(xs, ['Change to Galaxy or the Galaxy interface', 'Evidence in the execution traces', 'Measure of success']):
        axt.text(x, 0.97, h, fontsize=5.3, fontweight='bold', va='top', transform=axt.transAxes)
    axt.plot([0, 1], [0.925, 0.925], color=INK, lw=0.5, transform=axt.transAxes)
    for k, row in enumerate(tbl):
        y = 0.895 - k * 0.148
        for x, v in zip(xs, row):
            axt.text(x, y, v, fontsize=5.0, va='top', transform=axt.transAxes, linespacing=1.15)
        axt.plot([0, 1], [y - 0.125, y - 0.125], color=GRID, lw=0.4, transform=axt.transAxes)
    sd['d_engineering_targets'] = pd.DataFrame([dict(change=a.replace('\n', ' '), evidence=b.replace('\n', ' '), measure=c.replace('\n', ' '))
                                                for a, b, c in tbl])
    save_ed(fig, 'ED_Fig3', OUTDIR)
    source_data('ED_Fig3', sd)


# =====================================================================================================
def ed4():
    fig = plt.figure(figsize=(W_ED, 115 * MM))
    sd = {}
    ax = fig.add_axes([0.16, 0.10, 0.28, 0.76])
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'Repeatability categories by model configuration\n(BixBench-Verified-50)')
    cells = D['fig4c_cells']
    rows, ys, labels = [], [], []
    y = 0
    for cfg in CFG5:
        ax.text(-0.03, y, CFG_ROW[cfg].replace('\n', ' ') if cfg != SUPERSEDED else 'DeepSeek V4 Pro (Claude\nCode, superseded)',
                transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=5.2, fontweight='bold', linespacing=1.05)
        y += 1
        for env in ENVS:
            c = cells.get(f'BixBench50|{env}|{cfg}', {})
            left = 0
            for key, lab, col in [('all', '3/3 scored correct', NEUTRAL_LIGHT), ('mixed', 'Split (1–2/3)', ENV_COLOR[env]), ('none', '0/3 scored correct', NEUTRAL_DARK)]:
                v = c.get(key, 0)
                ax.barh(y, v, left=left, color=col, height=0.72, ec='white', lw=0.5)
                if v >= 3:
                    ax.text(left + v / 2, y, str(v), ha='center', va='center', fontsize=5.0, color=INK if key == 'all' else 'white')
                left += v
                rows.append(dict(model_configuration=cfg, execution_condition=ENV_LABEL[env], repeatability_category=lab, replicate_sets=v))
            ax.text(54, y, str(c.get('mixed', 0)), ha='center', va='center', fontsize=5.4, fontweight='bold')
            labels.append(ENV_LABEL[env])
            ys.append(y); y += 1
        y += 0.35
    ax.text(54, -1.1, 'Split\nsets', ha='center', va='center', fontsize=5.1, fontweight='bold')
    tot = {e: sum(cells.get(f'BixBench50|{e}|{c}', {}).get('mixed', 0) for c in CFG5) for e in ENVS}
    ax.text(57, y - 0.3, f"Total split replicate sets: open-ended code {tot['open_ended_code']}, Galaxy {tot['galaxy']}", ha='right', va='center', fontsize=5.1)
    ax.set_yticks(ys); ax.set_yticklabels(labels, fontsize=5.0); ax.set_ylim(y + 0.2, -1.7); ax.set_xlim(0, 57); ax.set_xticks(range(0, 51, 10))
    ax.spines['bottom'].set_bounds(0, 50); ax.set_xlabel('Replicate sets (of 50 tasks)'); grid_x(ax)
    ax.legend(handles=[Patch(fc=NEUTRAL_LIGHT, label='3/3 replicate runs scored correct'), Patch(fc=ENV_COLOR['open_ended_code'], label='Split (1–2/3), open-ended code condition'),
                       Patch(fc=ENV_COLOR['galaxy'], label='Split (1–2/3), Galaxy condition'), Patch(fc=NEUTRAL_DARK, label='0/3 replicate runs scored correct')],
              loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, fontsize=5.0)
    sd['a_triplicate_outcomes'] = pd.DataFrame(rows)
    ax = fig.add_axes([0.80, 0.10, 0.18, 0.76])
    panel_label(fig, 0.49, 0.99, 'b'); panel_title(fig, 0.49, 0.99, 'Neither prompt length nor workload consistently\npredicted operational errors')
    rr = D['ed4b']
    name = {('Open-ended code', 'Prompt word count'): ('open_ended_code', 'Open-ended code condition: prompt length\nversus runs with a nonzero shell exit'),
            ('Galaxy', 'Prompt word count'): ('galaxy', 'Galaxy condition: prompt length versus\nruns with a Galaxy job error'),
            ('Galaxy', 'Median recorded non-fetch jobs/run'): ('galaxy', 'Galaxy condition: analysis jobs per run\nversus share of Galaxy job errors')}
    order = [('Open-ended code', 'Prompt word count'), ('Galaxy', 'Prompt word count'), ('Galaxy', 'Median recorded non-fetch jobs/run')]
    ax.axvline(0, color=INK2, lw=0.5, ls=(0, (2, 2)))
    ticks, labs, rows = [], [], []
    y = 0
    for b in BENCH:
        ax.text(-0.03, y, BENCH_LABEL[b], fontsize=5.4, fontweight='bold', va='center', ha='right', transform=ax.get_yaxis_transform())
        y += 1
        for key in order:
            r = [r for r in rr if r['benchmark'] == b and (r['env'], r['exposure']) == key][0]
            env, lab = name[key]
            e, lo, hi = r['rho']
            ax.plot([lo, hi], [y, y], color=ENV_COLOR[env], lw=0.9)
            dot(ax, e, y, env, ms=3.4)
            ticks.append(y); labs.append(f"{lab} ({r['n']} tasks)")
            rows.append(dict(benchmark=BENCH_LABEL[b], execution_condition=ENV_LABEL[env], comparison=lab.replace('\n', ' '), tasks=r['n'],
                             spearman_rho=e, ci_low=lo, ci_high=hi))
            y += 1.25
        y += 0.3
    ax.set_yticks(ticks); ax.set_yticklabels(labs, fontsize=5.0); ax.set_ylim(y - 0.8, -0.7); ax.set_xlim(-1, 1)
    ax.set_xticks([-1, -0.5, 0, 0.5, 1]); ax.set_xlabel('Spearman correlation across tasks\n(ρ; 95% confidence interval)'); grid_x(ax)
    sd['b_correlations'] = pd.DataFrame(rows)
    save_ed(fig, 'ED_Fig4', OUTDIR)
    source_data('ED_Fig4', sd)


# =====================================================================================================
def ed5():
    fig = plt.figure(figsize=(W_ED, 100 * MM))
    sd = {}
    ax = fig.add_axes([0.16, 0.13, 0.26, 0.72])
    panel_label(fig, 0.005, 0.99, 'a'); panel_title(fig, 0.005, 0.99, 'The input-token ratio is lowest on the workflow-derived\nbenchmark for every model configuration')
    ax.axvline(1, color=INK2, lw=0.5, ls=(0, (2, 2)))
    rows, ticks, labs = [], [], []
    y = 0
    for r in D['ed5a']:
        head = 'Three model configurations, pooled' if r['config'].startswith('All three') else r['config']
        ax.text(-0.03, y, head, fontsize=5.4, fontweight='bold', va='center', ha='right', transform=ax.get_yaxis_transform())
        y += 1
        for k, b in enumerate(BENCH):
            e, lo, hi = r['values'][k]
            ax.plot([lo, hi], [y, y], color=INK, lw=0.9)
            ax.plot(e, y, 'o', ms=3.4, mfc=INK, mec='white', mew=0.4, zorder=3)
            ax.text(1.03, y, f'{e:.2f}', transform=ax.get_yaxis_transform(), fontsize=5.0, va='center')
            ticks.append(y); labs.append(BENCH_LABEL[b])
            rows.append(dict(model_configuration=r['config'], benchmark=BENCH_LABEL[b], median_input_token_ratio=e, ci_low=lo, ci_high=hi))
            y += 1
        y += 0.3
    ax.text(1.03, -0.3, 'Median', transform=ax.get_yaxis_transform(), fontsize=5.0, fontweight='bold', va='center')
    ax.text(0.97, -0.3, 'equal use', fontsize=5.0, color=INK2, ha='right', va='center')
    ax.set_yticks(ticks); ax.set_yticklabels(labs, fontsize=5.1); ax.set_ylim(y - 0.5, -0.6)
    ax.set_xscale('log'); ax.set_xlim(0.4, 16.5); ax.set_xticks([0.5, 1, 2, 4, 8, 16]); ax.set_xticklabels(['0.5', '1', '2', '4', '8', '16'])
    ax.xaxis.set_minor_locator(plt.NullLocator())
    ax.set_xlabel('Input-token ratio, Galaxy ÷ open-ended code\n(median of task pairs; 95% confidence interval)'); grid_x(ax)
    sd['a_input_token_ratio'] = pd.DataFrame(rows)
    # ---- b: direct use of Galaxy's programming interface
    panel_label(fig, 0.53, 0.99, 'b'); panel_title(fig, 0.53, 0.99, 'Agents made direct Galaxy API calls for operations\nthe Galaxy interface lacked')
    bp, nr, sh = D['scan']['bypass'], D['scan']['codex_galaxy_runs'], D['scan']
    ops = [('copy_history', 'Copy the provided\nanalysis history'), ('download', 'Download output files'), ('tool_schema', "Read a tool's\nparameter description"),
           ('job_polling', 'Check job status'), ('raw_submission', 'Submit a job directly,\nbypassing checks')]
    rows = []
    for k, b in enumerate(BENCH):
        ax = fig.add_axes([0.66 + k * 0.11, 0.15, 0.085, 0.64])
        for i, (key, lab) in enumerate(ops):
            if key == 'copy_history' and b != 'BixBench50':
                ax.text(2, i, 'not applicable', va='center', fontsize=5.0, color=INK2)
                continue
            v = 100 * bp.get(b, {}).get(key, 0) / nr[b]
            ax.barh(i, v, color=GALAXY, height=0.62)
            ax.text(v + 3, i, f'{v:.0f}', va='center', fontsize=5.0)
            rows.append(dict(operation=lab.replace('\n', ' '), benchmark=BENCH_LABEL[b], runs=bp.get(b, {}).get(key, 0), galaxy_condition_runs=nr[b], percent=round(v, 1)))
        ax.set_yticks(range(len(ops))); ax.set_yticklabels([o[1] for o in ops] if k == 0 else [], fontsize=5.0); ax.set_ylim(len(ops) - 0.5, -0.5)
        ax.set_xlim(0, 100); ax.set_xticks([0, 50, 100]); grid_x(ax)
        ax.set_title(f'{BENCH_2L[b]}\n({nr[b]:,} runs)', fontsize=5.2, fontweight='bold')
        if k == 1:
            ax.set_xlabel('Galaxy-condition runs using the operation (%)')
    fig.text(0.53, 0.012, 'Direct Galaxy API calls as a share of shell commands in Galaxy-condition runs:\n' + ', '.join(
        f"{BENCH_LABEL[b]} {100 * sh['api_shell_core'][b] / sh['all_shell'][b]:.0f}%" for b in BENCH) + '.', fontsize=5.0, color=INK2)
    sd['b_direct_galaxy_api_calls'] = pd.DataFrame(rows)
    save_ed(fig, 'ED_Fig5', OUTDIR)
    source_data('ED_Fig5', sd)


if __name__ == '__main__':
    which = sys.argv[1:] or ['1', '2', '3', '4', '5']
    for w in which:
        globals()[f'ed{w}']()
        print('done ED Fig', w)
