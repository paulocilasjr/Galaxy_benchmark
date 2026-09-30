"""Main figures 1-5 and their Source Data workbooks.

Run from the repository root after build_data.py:  python manuscript_material/scripts/fig_main.py [1 2 3 4 5]

Design rules (see style.py): open-ended code is the reference condition and is always shown first; vermillion squares
are open-ended code and blue circles are Galaxy; no abbreviations; every panel title states its finding.
"""
import json
import os
import statistics as st
import sys
import textwrap

import numpy as np
import pandas as pd
from matplotlib.legend_handler import HandlerTuple
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch, Rectangle

sys.path.insert(0, os.path.dirname(__file__))
from style import (BENCH, BENCH_2L, BENCH_LABEL, CFG_LABEL, CODE, CONFIGS, ENV_COLOR, ENV_LABEL, ENV_LABEL_LONG, ENV_MARKER,  # noqa: E402
                   ENV_TINT, ENVS, GALAXY, GRID, INK, INK2, LIGHT, MM, NEUTRAL_DARK, NEUTRAL_LIGHT, NEUTRAL_MID, OI_BLACK,
                   OI_GREEN, OI_ORANGE, OI_PURPLE, OI_SKY, SUPERSEDED, W_DOUBLE, env_handles, env_patches, grid_x, grid_y,
                   panel_label, panel_title, plt, save_main)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUTDIR = os.path.join(ROOT, 'manuscript_material')
D = json.load(open(os.path.join(OUTDIR, 'source_data', 'figure_data.json')))

# Root-cause categories: Okabe-Ito colours, ordered so that no two neighbours fall below Delta E 8 under simulated
# colour-vision deficiency; every segment also carries its count, and the legend names each category.
CAUSES = [('SPEC', 'Task under-specified or\nreference ambiguous', OI_GREEN),
          ('RIGOR', 'Statistical or reasoning error', OI_ORANGE),
          ('EVALUATOR', 'Evaluator rejected a\ncorrect answer', OI_SKY),
          ('KNOWLEDGE', 'Missing domain knowledge', OI_PURPLE),
          ('HARNESS', 'No answer submitted', NEUTRAL_LIGHT),
          ('PLATFORM', 'Platform or tool defect\n(Galaxy or local software)', OI_BLACK),
          ('CONTRACT', 'Output format violated', NEUTRAL_MID)]
DARK_FILL = {OI_BLACK, OI_PURPLE, OI_GREEN, NEUTRAL_DARK}


def source_data(name, sheets):
    path = os.path.join(OUTDIR, 'source_data', f'Source_Data_{name}.xlsx')
    with pd.ExcelWriter(path, engine='openpyxl') as xw:
        for sheet, df in sheets.items():
            df.to_excel(xw, sheet_name=sheet[:31], index=False)
    return path


def box(ax, x, y, w, h, text, fc='white', ec=INK2, lw=0.6, fs=5.6, weight='normal'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.012', fc=fc, ec=ec, lw=lw,
                                transform=ax.transAxes))
    ax.text(x + w / 2, y + h / 2, text, ha='center', va='center', fontsize=fs, fontweight=weight, transform=ax.transAxes,
            linespacing=1.2)


def arrow(ax, x0, y0, x1, y1, style='-|>'):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=6, lw=0.7, color=INK2,
                                 transform=ax.transAxes, shrinkA=0, shrinkB=0))


def dot(ax, x, y, env, filled=True, ms=3.6, z=3, clip=True):
    ax.plot(x, y, ENV_MARKER[env], ms=ms, mfc=ENV_COLOR[env] if filled else 'white', mec=ENV_COLOR[env] if not filled else 'white',
            mew=0.8 if not filled else 0.4, zorder=z, ls='', clip_on=clip)


def direction_hint(ax, y, left='Open-ended\ncode higher', right='Galaxy\nhigher'):
    ax.text(0.02, y, '← ' + left.split('\n')[0] + ('\n' + left.split('\n')[1] if '\n' in left else ''), transform=ax.get_yaxis_transform(),
            fontsize=5, color=INK2, ha='left', va='center')
    ax.text(0.98, y, right.split('\n')[0] + ' →' + ('\n' + right.split('\n')[1] if '\n' in right else ''), transform=ax.get_yaxis_transform(),
            fontsize=5, color=INK2, ha='right', va='center')


def rnd(x, nd=1):
    """Round half away from zero, as in the text (e.g. 0.0095 -> 0.010)."""
    from decimal import ROUND_HALF_UP, Decimal
    return str(Decimal(str(x)).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def signed(x, nd=1):
    v = rnd(x, nd)
    if float(v) == 0:
        return rnd(0, nd)
    return ('+' + v if not v.startswith('-') else v).replace('-', '−')


def fmt_ci(e, lo, hi, nd=1, sign=True):
    return f"{signed(e, nd) if sign else rnd(e, nd)} ({rnd(lo, nd).replace('-', '−')} to {rnd(hi, nd).replace('-', '−')})"


# =====================================================================================================
def fig1():
    fig = plt.figure(figsize=(W_DOUBLE, 112 * MM))
    inv = D['inventory']
    # ---- a: open-ended code, the reference condition
    ax = fig.add_axes([0.0, 0.47, 0.40, 0.50]); ax.axis('off')
    panel_label(fig, 0.005, 0.985, 'a')
    ax.text(0.045, 0.97, 'Open-ended code condition (reference)', fontsize=6.5, fontweight='bold', va='top')
    box(ax, 0.03, 0.40, 0.27, 0.30, 'Language-model\nagent\n(model\nconfiguration and\nagent harness)', fc=LIGHT, weight='bold')
    box(ax, 0.37, 0.40, 0.25, 0.30, 'Unrestricted\nshell', fc=ENV_TINT['open_ended_code'], ec=CODE, lw=0.9, weight='bold')
    box(ax, 0.69, 0.40, 0.29, 0.30, 'Installs and runs\nany software on\nlocal files', fc=LIGHT, ec=GRID)
    arrow(ax, 0.30, 0.55, 0.37, 0.55); arrow(ax, 0.62, 0.55, 0.69, 0.55)
    ax.text(0.50, 0.19, 'Execution trace: commands, scripts, command output\nand final files; no record of individual analysis jobs',
            ha='center', va='center', fontsize=5.3, color=INK2, style='italic')
    # ---- b: Galaxy-mediated condition
    ax = fig.add_axes([0.42, 0.47, 0.58, 0.50]); ax.axis('off')
    panel_label(fig, 0.415, 0.985, 'b')
    ax.text(0.035, 0.97, 'Galaxy condition (Galaxy-mediated execution)', fontsize=6.5, fontweight='bold', va='top')
    box(ax, 0.01, 0.40, 0.17, 0.30, 'Language-model\nagent\n(same model\nconfiguration and\nagent harness)', fc=LIGHT, weight='bold')
    ax.add_patch(FancyBboxPatch((0.235, 0.10), 0.27, 0.80, boxstyle='round,pad=0,rounding_size=0.012', fc='white', ec=GALAXY,
                                lw=0.9, transform=ax.transAxes))
    ax.text(0.37, 0.845, 'Galaxy interface\n(Model Context Protocol)', ha='center', va='center', fontsize=5.8, fontweight='bold')
    ops = ['Tool search', 'Tool parameter descriptions', 'Analysis-history inspection', 'Job submission\nand monitoring',
           'User-defined tools\n(agent-written code)']
    for i, op in enumerate(ops):
        y = 0.70 - i * 0.13
        box(ax, 0.25, y - 0.05, 0.24, 0.10, op, fc=ENV_TINT['galaxy'], ec=GALAXY, lw=0.5, fs=5.3)
    ax.add_patch(FancyBboxPatch((0.565, 0.12), 0.425, 0.78, boxstyle='round,pad=0,rounding_size=0.012', fc='white', ec=INK2,
                                lw=0.8, transform=ax.transAxes))
    ax.text(0.7775, 0.845, 'Galaxy server (usegalaxy.org)', ha='center', va='center', fontsize=5.8, fontweight='bold')
    for i, t in enumerate(['Installed Galaxy tools (Tool Shed)', 'Analysis histories and datasets',
                           'Jobs: state, parameters, error messages', 'User-defined tools run as Galaxy jobs']):
        box(ax, 0.585, 0.66 - i * 0.145, 0.385, 0.10, t, fc=LIGHT, ec=GRID, lw=0.4, fs=5.3)
    ax.text(0.7775, 0.05, 'Execution trace and analysis history: tool identities\nand versions, requested and resolved parameters,\ndatasets, job states and error messages',
            ha='center', va='center', fontsize=5.3, color=INK2, style='italic')
    arrow(ax, 0.18, 0.55, 0.235, 0.55); arrow(ax, 0.505, 0.55, 0.565, 0.55, style='<|-|>')
    ax.text(0.095, 0.30, 'Local shell meant\nonly for staging\nfiles and extracting\nthe answer', ha='center', va='top', fontsize=5.1, color=INK2)
    # ---- c: design matrix
    ax = fig.add_axes([0.205, 0.03, 0.465, 0.30])
    panel_label(fig, 0.005, 0.445, 'c')
    fig.text(0.023, 0.444, 'Three benchmarks, five model configurations, three replicate runs of every task', fontsize=6.5, fontweight='bold', va='top')
    cols = [(b, e) for b in BENCH for e in ENVS]
    rowsl = CONFIGS + [SUPERSEDED, 'GPT-6 Astra']
    runs = {('BixBench50', c): 150 for c in CONFIGS + [SUPERSEDED]}
    runs.update({('CompBio', c): 300 for c in CONFIGS})
    runs.update({('IWC', c): 30 for c in CONFIGS})
    table = []
    for j, (b, env) in enumerate(cols):
        for i, cfg in enumerate(rowsl):
            n = runs.get((b, cfg))
            if cfg == 'GPT-6 Astra':
                n = 100 if (b == 'CompBio' and env == 'open_ended_code') else None
            ax.add_patch(Rectangle((j, i), 0.96, 0.9, fc=ENV_TINT[env] if n else 'white', ec=GRID if n else 'white', lw=0.4))
            ax.text(j + 0.48, i + 0.45, f'{n:,}' if n else '–', ha='center', va='center', fontsize=5.5, color=INK if n else INK2)
            table.append(dict(benchmark=BENCH_LABEL[b], execution_condition=ENV_LABEL_LONG[env], model_configuration=cfg, runs=n or 0))
    ax.set_xlim(-0.02, 6); ax.set_ylim(len(rowsl) + 1.2, -0.1)
    ax.set_yticks([i + 0.45 for i in range(len(rowsl))])
    ax.set_yticklabels(['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro (Codex)',
                        'DeepSeek V4 Pro (Claude Code,\nsuperseded; reported separately)',
                        'GPT-6 Astra (open-ended code\ncondition only; not paired)'], fontsize=5.4)
    ax.set_xticks([]); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    for j, (b, env) in enumerate(cols):
        ax.text(j + 0.48, -0.2, 'Open-ended\ncode' if env == 'open_ended_code' else 'Galaxy', ha='center', va='bottom', fontsize=5.3)
    ax.text(-0.08, -0.2, 'Execution condition', ha='right', va='bottom', fontsize=5.3, color=INK2)
    ax.text(-0.08, -1.25, 'Benchmark', ha='right', va='bottom', fontsize=5.3, color=INK2)
    for k, b in enumerate(BENCH):
        ax.text(2 * k + 0.98, -1.25, BENCH_LABEL[b], ha='center', va='bottom', fontsize=5.8, fontweight='bold')
        ax.plot([2 * k + 0.05, 2 * k + 1.9], [-1.15, -1.15], color=INK, lw=0.6, clip_on=False)
    ax.text(3.0, len(rowsl) + 0.55, 'Numbers are runs: tasks × 3 replicate runs, per model configuration and execution condition',
            ha='center', va='center', fontsize=5.2, color=INK2)
    # ---- c (right): benchmark descriptions
    ax2 = fig.add_axes([0.70, 0.02, 0.30, 0.40]); ax2.axis('off')
    cards = [('BixBench-Verified-50', '50 tasks; platform-neutral benchmark', 'Endpoint: accuracy (share of runs scored\ncorrect by the benchmark evaluator)'),
             ('CompBioBench', '100 tasks; platform-neutral benchmark', 'Endpoint: reported benchmark score\n(answers credited, of 100)'),
             ('IWC (Intergalactic Workflow Commission)', '10 tasks; workflow-derived benchmark',
              "Endpoint: output agreement with the\nworkflow's reference output (0 to 1)")]
    for k, (name, l1, l2) in enumerate(cards):
        y = 0.97 - k * 0.245
        ax2.add_patch(Rectangle((0.0, y - 0.20), 0.012, 0.20, fc=INK, ec='none', transform=ax2.transAxes))
        ax2.text(0.035, y, name, fontsize=5.8, fontweight='bold', va='top', transform=ax2.transAxes)
        ax2.text(0.035, y - 0.058, l1, fontsize=5.3, va='top', transform=ax2.transAxes)
        ax2.text(0.035, y - 0.105, l2, fontsize=5.3, va='top', color=INK2, transform=ax2.transAxes, linespacing=1.15)
    tot = {k: sum(v[k] for v in inv.values()) for k in ('runs', 'traces', 'nonfetch_jobs', 'mcp_calls')}
    ax2.text(0.0, 0.0, f"Archive: {tot['runs']:,} runs · {tot['traces']:,} execution traces\n{tot['nonfetch_jobs']:,} Galaxy analysis jobs "
             f"· {tot['mcp_calls']:,} Galaxy interface calls", fontsize=5.5, fontweight='bold', va='bottom', transform=ax2.transAxes,
             linespacing=1.3)
    save_main(fig, 'Fig1', OUTDIR)
    source_data('Fig1', {'c_design_runs': pd.DataFrame(table), 'c_archive_totals': pd.DataFrame(
        [dict(benchmark=BENCH_LABEL[b], tasks=inv[b]['tasks'], runs=inv[b]['runs'], execution_traces=inv[b]['traces'],
              galaxy_analysis_jobs=inv[b]['nonfetch_jobs'], galaxy_interface_calls=inv[b]['mcp_calls']) for b in BENCH])})


# =====================================================================================================
IWC_TASK = {'Short-read QC': 'Short-read quality control', 'RNA-seq DE': 'RNA-seq differential expression',
            'ATAC-seq peaks': 'ATAC-seq chromatin accessibility', 'AMR detection': 'Antimicrobial-resistance genes',
            'Pseudobulk DE': 'Pseudobulk differential expression', 'BioProject retrieval': 'BioProject metadata retrieval',
            'Peptide verification': 'Peptide verification', 'Amplicon denoising': 'Amplicon denoising',
            'Mitogenome assembly': 'Mitochondrial genome assembly', 'Host-read removal': 'Host-read removal'}
ROWS = [('GPT-5.5', 'GPT-5.5'), ('GPT-5.6 Sol', 'GPT-5.6 Sol'), ('GPT-5.6 Luna', 'GPT-5.6 Luna'), ('DeepSeek V4 Pro', 'DeepSeek V4 Pro (Codex)'),
        ('pooled', 'Four Codex model\nconfigurations, pooled'), (SUPERSEDED, 'DeepSeek V4 Pro\n(Claude Code, superseded)')]
YROW = [0, 1, 2, 3, 4.3, 5.75]
OFF = {'open_ended_code': -0.21, 'galaxy': 0.21}
MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
         'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'deepseek_v4_pro_via_claude_code_superseded': SUPERSEDED}


def condition_levels():
    """Replicate-level scores per (row, condition) and condition differences per row, for all three benchmarks."""
    import collections
    import gzip
    reps = {b: collections.defaultdict(list) for b in BENCH}      # (row, env) -> [(value, filled)]
    diffs = {b: {} for b in BENCH}                               # row -> (estimate, low, high); low/high None = no interval
    acc = collections.defaultdict(list)
    for s in (json.loads(l) for l in gzip.open(os.path.join(OUTDIR, 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt')):
        if s['benchmark'] == 'BixBench50':
            acc[(MODEL[s['model']], s['condition'], s['replicate'])].append(1 if s['score'] == 1 else 0)
    for (cfg, env, r), v in sorted(acc.items()):
        reps['BixBench50'][(cfg, env)].append((100 * sum(v) / len(v), True))
    fa = {r['config']: r for r in D['fig2a']}
    for key, name in [('GPT-5.5', 'GPT-5.5'), ('GPT-5.6 Sol', 'GPT-5.6 Sol'), ('GPT-5.6 Luna', 'GPT-5.6 Luna'),
                      ('DeepSeek V4 Pro', 'DeepSeek V4 Pro (Codex)'), ('pooled', 'Four Codex configurations'), (SUPERSEDED, SUPERSEDED)]:
        diffs['BixBench50'][key] = tuple(fa[name]['diff'])
    for p in D['fig2b']:  # CompBioBench: archived reported benchmark scores; open symbol = labelled predicted
        if p['config'] != 'GPT-6 Astra':
            reps['CompBio'][(p['config'], p['condition'])].append((p['score'], p['official']))
    iw = collections.defaultdict(list)  # IWC: replicate mean over the nine tasks scored in both conditions
    for p in D['fig2d']:
        if p['task_label'] != 'Host-read removal' and p['score'] is not None:
            iw[(p['config'], p['condition'], p['replicate'])].append(p['score'])
    for (cfg, env, r), v in sorted(iw.items()):
        reps['IWC'][(cfg, env)].append((st.mean(v), True))
    fc = {r['config']: r for r in D['fig2c']}
    for key in CONFIGS:
        diffs['IWC'][key] = tuple(fc[key]['diff'])
    diffs['IWC']['pooled'] = tuple(fc['All four']['diff'])
    for b in BENCH:
        for env in ENVS:
            reps[b][('pooled', env)] = [x for c in CONFIGS for x in reps[b][(c, env)]]
    for key in CONFIGS + ['pooled']:
        m = {e: st.mean(v for v, _ in reps['CompBio'][(key, e)]) for e in ENVS}
        diffs['CompBio'][key] = (m['galaxy'] - m['open_ended_code'], None, None)
    assert abs(st.mean(v for v, _ in reps['BixBench50'][('pooled', 'galaxy')]) - 86.5) < 0.01
    for key in CONFIGS:
        assert abs(st.mean(v for v, _ in reps['IWC'][(key, 'galaxy')]) - fc[key]['galaxy_mean']) < 1e-3
    return reps, diffs


def level_and_difference(fig, b, reps, diffs, x_lev, x_dif, y0, h, spec, show_labels=True, medians=None):
    """Left: replicate-level scores per model configuration (open-ended code upper sub-row, Galaxy lower; mean tick).
    Right: Galaxy minus open-ended code with its 95% confidence interval (open point: no interval available)."""
    axl = fig.add_axes([x_lev, y0, spec['wlev'], h]); axd = fig.add_axes([x_dif, y0, spec['wdif'], h])
    rows_sd = []
    for ax in (axl, axd):
        for j, y in enumerate(YROW):
            if j % 2 == 0:
                ax.axhspan(y - 0.47, y + 0.47, color='#f5f4f1', lw=0, zorder=0)
        ax.axhline(3.65, color=GRID, lw=0.5); ax.axhline(5.03, color=INK2, lw=0.4, ls=(0, (1, 1.5)))
        ax.set_ylim(6.3, -0.75); ax.set_yticks(YROW)
    for (key, name), y in zip(ROWS, YROW):
        if key not in diffs[b]:
            if not spec.get('legend_in_empty_row'):
                axl.text(0.03, y, 'Not run', transform=axl.get_yaxis_transform(), fontsize=5.0, color=INK2, ha='left', va='center')
            continue
        means = {}
        for env in ENVS:
            vals = reps[b][(key, env)]
            yy = y + OFF[env]
            for k, (v, filled) in enumerate(vals):
                dot(axl, v, yy, env, filled=filled, ms=2.6 if key == 'pooled' else 3.2)
            means[env] = st.mean(v for v, _ in vals)
            axl.plot([means[env]] * 2, [yy - 0.17, yy + 0.17], color=INK, lw=0.9, zorder=5)
        e_, lo, hi = diffs[b][key]
        if lo is not None:
            axd.plot([lo, hi], [y, y], color=INK, lw=1.0, zorder=3)
            axd.plot(e_, y, 'o', ms=3.6, mfc=INK, mec='white', mew=0.4, zorder=4)
            txt = fmt_ci(e_, lo, hi, nd=spec['nd']).replace(' (', '\n(')
        else:
            axd.plot(e_, y, 'o', ms=3.6, mfc='white', mec=INK, mew=0.9, zorder=4)
            txt = signed(e_, spec['nd']) + '\n(no interval)'
        axd.text(1.04, y, txt, transform=axd.get_yaxis_transform(), fontsize=5.0, ha='left', va='center', linespacing=1.05)
        row = dict(benchmark=BENCH_LABEL[b], model_configuration=name.replace('\n', ' '), open_ended_code_mean=round(means['open_ended_code'], 4),
                   galaxy_mean=round(means['galaxy'], 4), condition_difference_galaxy_minus_open_ended_code=round(e_, 4), ci_low=lo, ci_high=hi,
                   replicate_runs_open_ended_code='; '.join(f'{v:.4g}' for v, _ in reps[b][(key, 'open_ended_code')]),
                   replicate_runs_galaxy='; '.join(f'{v:.4g}' for v, _ in reps[b][(key, 'galaxy')]))
        if medians is not None and key in medians:
            row.update(medians[key])
        rows_sd.append(row)
    axl.set_xlim(*spec['llim']); axl.set_xticks(spec['lt']); axl.set_xlabel(spec['llab']); grid_x(axl)
    if 'ltl' in spec:
        axl.set_xticklabels(spec['ltl'])
    axl.set_yticklabels([n for _, n in ROWS] if show_labels else [], fontsize=5.3)
    axl.set_title('Replicate runs and mean', fontsize=5.3, fontweight='bold', loc='left', pad=2)
    axd.axvline(0, color=INK2, lw=0.6, ls=(0, (2, 2)))
    axd.set_xlim(*spec['dlim']); axd.set_xticks(spec['dt']); axd.set_xlabel(spec['dlab']); grid_x(axd)
    if 'dtl' in spec:
        axd.set_xticklabels(spec['dtl'])
    axd.set_yticklabels([])
    axd.set_title('Galaxy − open-ended code', fontsize=5.3, fontweight='bold', loc='left', pad=2)
    return axl, axd, rows_sd


def fig2():
    fig = plt.figure(figsize=(W_DOUBLE, 170 * MM))
    sd = {}
    reps, diffs = condition_levels()
    pooled = {b: {e: st.mean(v for v, _ in reps[b][('pooled', e)]) for e in ENVS} for b in BENCH}
    lev = D['iwc_levels']
    med = {c: dict(open_ended_code_median_nine_tasks=lev[f'{c}|open_ended_code']['nine_median'], galaxy_median_nine_tasks=lev[f'{c}|galaxy']['nine_median'])
           for c in CONFIGS}
    TOP, BOT, HT, HB = 0.655, 0.065, 0.255, 0.275
    XL, XD, XL2, XD2 = 0.155, 0.325, 0.655, 0.825
    # ---- a: IWC
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'IWC: mean output agreement was higher in the\nGalaxy condition on the workflow-derived benchmark')
    fig.text(0.023, 0.951, f"Nine tasks scored in both conditions. Pooled mean: open-ended code {pooled['IWC']['open_ended_code']:.3f}, "
             f"Galaxy {pooled['IWC']['galaxy']:.3f}.\nGrey text: median output agreement, open-ended code / Galaxy.", fontsize=5.2, color=INK2, va='top', linespacing=1.2)
    spec = dict(wlev=0.12, wdif=0.09, llim=(0.76, 1.005), lt=[0.8, 0.9, 1.0], ltl=['0.8', '0.9', '1'], llab='Mean output agreement,\nnine tasks (0 to 1)',
                dlim=(-0.03, 0.26), dt=[0, 0.1, 0.2], dtl=['0', '0.1', '0.2'], dlab='Difference in mean\noutput agreement', nd=3, legend_in_empty_row=True)
    axl, axd, rows_a = level_and_difference(fig, 'IWC', reps, diffs, XL, XD, TOP, HT, spec, medians=med)
    for c, y in zip(CONFIGS, YROW):
        m = med[c]
        axl.text(-0.02, y + 0.43, f"median {rnd(m['open_ended_code_median_nine_tasks'], 3)} / {rnd(m['galaxy_median_nine_tasks'], 3)}",
                 transform=axl.get_yaxis_transform(), fontsize=5.0, color=INK2, ha='right', va='center')
    axl.legend(handles=env_handles(ms=3.2), loc='center left', bbox_to_anchor=(-0.02, 0.07), fontsize=5.0, ncol=1)
    sd['a_IWC_levels_differences'] = pd.DataFrame(rows_a)
    # ---- b: IWC per task, broken axis
    pts = D['fig2d']
    tasks = list(IWC_TASK)
    axl = fig.add_axes([0.655, TOP, 0.05, HT]); axr = fig.add_axes([0.715, TOP, 0.275, HT])
    panel_label(fig, 0.50, 0.995, 'b')
    panel_title(fig, 0.50, 0.995, 'IWC: six of ten tasks reached near-perfect Galaxy-condition\nmean output agreement; every run below 0.5 has a traced cause')
    rng = np.random.default_rng(20260925)
    for ax_ in (axl, axr):
        for i, t in enumerate(tasks):
            for env, off in [('open_ended_code', -0.19), ('galaxy', 0.19)]:
                vals = [p['score'] for p in pts if p['task_label'] == t and p['condition'] == env and p['score'] is not None]
                jit = rng.uniform(-0.07, 0.07, len(vals))
                ax_.scatter(vals, np.full(len(vals), i + off) + jit, s=5, marker=ENV_MARKER[env], color=ENV_COLOR[env], lw=0.25, ec='white', zorder=3)
                if vals:
                    m = st.mean(vals)
                    ax_.plot([m, m], [i + off - 0.16, i + off + 0.16], color=INK, lw=0.8, zorder=4)
        ax_.set_ylim(len(tasks) - 0.5, -0.6)
        for i in range(len(tasks)):
            if i % 2 == 0:
                ax_.axhspan(i - 0.5, i + 0.5, color='#f5f4f1', zorder=0, lw=0)
    axl.set_xlim(-0.03, 0.45); axl.set_xticks([0, 0.2]); axl.set_xticklabels(['0', '0.2'])
    axr.set_xlim(0.80, 1.005); axr.set_xticks([0.8, 0.85, 0.9, 0.95, 1.0]); axr.set_xticklabels(['0.80', '0.85', '0.90', '0.95', '1'])
    axl.set_yticks(range(len(tasks))); axl.set_yticklabels([IWC_TASK[t] for t in tasks], fontsize=5.2); axr.set_yticks([])
    axl.spines['right'].set_visible(False); axr.spines['left'].set_visible(False)
    for ax_, xs_ in [(axl, 1), (axr, 0)]:
        ax_.plot([xs_ - 0.03, xs_ + 0.03], [-0.03, 0.03], transform=ax_.transAxes, color=INK2, lw=0.5, clip_on=False)
    axr.set_xlabel('Output agreement with the workflow reference output\n(0 to 1; axis broken between 0.45 and 0.80)', x=0.35)
    gm = D['fig2d_means']
    marks = [('Pseudobulk DE', 'open_ended_code', 0.0, '1'), ('Amplicon denoising', 'open_ended_code', 0.0, '2'),
             ('Mitogenome assembly', 'open_ended_code', 0.0, '3'), ('Mitogenome assembly', 'galaxy', 0.0, '3'),
             ('Host-read removal', 'galaxy', 0.273, '4')]
    for t, env, x, lab in marks:
        i = tasks.index(t) + (-0.19 if env == 'open_ended_code' else 0.19)
        axl.text(x + 0.035, i, lab, fontsize=5.2, fontweight='bold', va='center', ha='left', zorder=5)
    axr.legend(handles=env_handles(ms=3.4) + [Line2D([], [], color=INK, lw=0.8, label='Mean of 12 replicate runs')], loc='lower left', ncol=3,
               fontsize=5.0, bbox_to_anchor=(-0.62, 1.0))
    fig.text(0.52, 0.585, 'Runs with output agreement below 0.5 (numbers on the plot)', fontsize=5.1, fontweight='bold', va='top')
    k1 = ('1  Open-ended code only: hand-written multiple-\n    testing correction was wrong (DeepSeek V4 Pro\n    (Codex), replicate run 3); installed Galaxy tools\n'
          '    return library-computed adjusted P values\n'
          '2  Open-ended code only: sample names lost capital\n    letters when read from directory names (GPT-5.5,\n    replicate runs 1 and 3); Galaxy collections keep them')
    k2 = ('3  Wrong contig submitted: GPT-5.5 replicate run 1\n    in both conditions; DeepSeek V4 Pro (Codex)\n    replicate run 2, open-ended code condition\n'
          '4  Galaxy condition, GPT-5.6 Luna, replicate runs\n    1 and 3: score conflict; correct BWA-MEM output\n    scored against the Bowtie2 reference')
    fig.text(0.52, 0.565, k1, fontsize=5.0, va='top', ha='left', linespacing=1.18)
    fig.text(0.775, 0.565, k2, fontsize=5.0, va='top', ha='left', linespacing=1.18)
    sd['b_IWC_runs'] = pd.DataFrame([dict(task=IWC_TASK[p['task_label']], execution_condition=ENV_LABEL_LONG[p['condition']], model_configuration=p['config'],
                                          replicate_run=p['replicate'], output_agreement=p['score']) for e in ENVS for p in pts if p['condition'] == e])
    sd['b_IWC_task_means'] = pd.DataFrame([dict(task=k, open_ended_code_mean=v['code'], galaxy_mean=v['galaxy']) for k, v in gm.items()])
    # ---- c: BixBench
    panel_label(fig, 0.005, 0.455, 'c')
    panel_title(fig, 0.005, 0.455, 'BixBench-Verified-50: similar accuracy\nin both execution conditions')
    fig.text(0.023, 0.411, f"Pooled accuracy, four Codex model configurations: open-ended\ncode {pooled['BixBench50']['open_ended_code']:.1f}%, "
             f"Galaxy {pooled['BixBench50']['galaxy']:.1f}%.", fontsize=5.2, color=INK2, va='top', linespacing=1.2)
    spec = dict(wlev=0.12, wdif=0.09, llim=(60, 100), lt=[60, 80, 100], llab='Accuracy per replicate\nrun (% of 50 tasks)',
                dlim=(-10, 23), dt=[-10, 0, 10, 20], dlab='Difference in accuracy\n(percentage points)', nd=1)
    _, _, rows_c = level_and_difference(fig, 'BixBench50', reps, diffs, XL, XD, BOT, HB, spec)
    sd['c_BixBench_levels_differences'] = pd.DataFrame(rows_c)
    # ---- d: CompBio
    panel_label(fig, 0.50, 0.455, 'd')
    panel_title(fig, 0.50, 0.455, 'CompBioBench: similar reported benchmark\nscores in both execution conditions')
    fig.text(0.518, 0.411, f"Mean of replicate runs, four Codex model configurations: open-ended\ncode {pooled['CompBio']['open_ended_code']:.1f}, "
             f"Galaxy {pooled['CompBio']['galaxy']:.1f} of 100. No interval: the archive keeps no per-run grades.", fontsize=5.2, color=INK2, va='top', linespacing=1.2)
    spec = dict(wlev=0.12, wdif=0.09, llim=(78, 97), lt=[80, 85, 90, 95], llab='Reported benchmark\nscore (of 100)',
                dlim=(-4, 4), dt=[-4, -2, 0, 2, 4], dlab='Difference in reported\nscore (of 100)', nd=1, legend_in_empty_row=True)
    axl_d, _, rows_d = level_and_difference(fig, 'CompBio', reps, diffs, XL2, XD2, BOT, HB, spec)
    axl_d.legend(handles=env_handles(ms=3.2) + [Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, mew=0.8, ms=3.2, label='Open symbol: score labelled\npredicted in the archive')],
                 loc='center left', bbox_to_anchor=(-0.02, 0.08), fontsize=5.0)
    sd['d_CompBio_levels_differences'] = pd.DataFrame(rows_d)
    save_main(fig, 'Fig2', OUTDIR)
    source_data('Fig2', sd)


# =====================================================================================================
GALAXY_LIGHT = '#9DC3E0'


def fig3():
    fig = plt.figure(figsize=(W_DOUBLE, 150 * MM))
    sd = {}
    # ---- a: performance by model configuration within the Galaxy condition, one small multiple per benchmark
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'No model configuration led on every benchmark: Galaxy-condition performance by model configuration')
    cfg5 = CONFIGS + [SUPERSEDED]
    lab5 = {c: CFG_LABEL[c] for c in cfg5}
    bx = D['bix_accuracy']
    rep_iwc = D['iwc_replicate_means_ten']
    import collections
    bxrep = collections.defaultdict(list)
    import gzip
    for s in (json.loads(l) for l in gzip.open(os.path.join(OUTDIR, 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt')):
        if s['benchmark'] == 'BixBench50' and s['condition'] == 'galaxy':
            bxrep[(MODEL[s['model']], s['replicate'])].append(1 if s['score'] == 1 else 0)
    # One percentage axis, 70 to 100, for all three benchmarks; IWC output agreement (0 to 1) is shown x 100.
    panels = [('IWC', 'Mean output agreement over all ten tasks (%)',
               {c: [100 * rep_iwc[f'{c}|galaxy|{r}'] for r in (1, 2, 3)] for c in CONFIGS}, {c: 100 * D['iwc_levels'][f'{c}|galaxy']['ten_mean'] for c in CONFIGS}),
              ('BixBench50', 'Accuracy (% of runs scored correct)',
               {c: [100 * sum(bxrep[(c, r)]) / len(bxrep[(c, r)]) for r in (1, 2, 3)] for c in cfg5}, {c: bx[f'{c}|galaxy']['run_level'] for c in cfg5}),
              ('CompBio', 'Reported benchmark score (% of answers credited)',
               {c: D['compbio_scores'][f'{c}|galaxy']['replicates'] for c in CONFIGS}, {c: D['compbio_scores'][f'{c}|galaxy']['mean'] for c in CONFIGS})]
    xlim, xt = (70, 100), [70, 80, 90, 100]
    filled = {('CompBio', c): [p['official'] for p in D['fig2b'] if p['config'] == c and p['condition'] == 'galaxy'] for c in CONFIGS}
    rows_a = []
    for k, (b, xl, vals, means) in enumerate(panels):
        ax = fig.add_axes([0.165 + k * 0.285, 0.70, 0.19, 0.215])
        for i, c in enumerate(cfg5):
            if i % 2 == 0:
                ax.axhspan(i - 0.5, i + 0.5, color='#f5f4f1', lw=0, zorder=0)
            if c not in vals:
                ax.text(np.mean(xlim), i, 'Not run with this agent harness', fontsize=5.0, color=INK2, ha='center', va='center')
                continue
            for j_, v in enumerate(vals[c]):
                dot(ax, v, i, 'galaxy', ms=3.2, filled=filled.get((b, c), [True] * 3)[j_], clip=False)
            ax.plot([means[c]] * 2, [i - 0.28, i + 0.28], color=INK, lw=0.9, zorder=5)
            ax.text(1.04, i, rnd(means[c], 1), transform=ax.get_yaxis_transform(), fontsize=5.0, va='center')
            rows_a.append(dict(benchmark=BENCH_LABEL[b], model_configuration=CFG_LABEL[c], galaxy_condition_mean_percent=round(means[c], 2),
                               replicate_runs='; '.join(f'{v:.4g}' for v in vals[c])))
        ax.set_ylim(len(cfg5) - 0.5, -0.6); ax.set_yticks(range(len(cfg5)))
        ax.set_yticklabels([lab5[c] for c in cfg5] if k == 0 else [], fontsize=5.2)
        ax.set_xlim(*xlim); ax.set_xticks(xt); grid_x(ax)
        ax.set_xlabel(xl); ax.set_title(BENCH_LABEL[b], fontsize=5.6, fontweight='bold', loc='left')
    fig.text(0.165, 0.625, 'Symbols: replicate runs; tick and number: mean. IWC output agreement uses all ten tasks. CompBioBench: archived reported benchmark scores; open symbols are labelled predicted.',
             fontsize=5.0, color=INK2)
    sd['a_performance_by_model_configuration'] = pd.DataFrame(rows_a)
    # ---- b: user-defined-tool requests by model configuration
    ax = fig.add_axes([0.20, 0.09, 0.24, 0.42])
    panel_label(fig, 0.005, 0.585, 'b'); panel_title(fig, 0.005, 0.585, 'Model configurations differed most in whether\nthey wrote user-defined tools')
    # Benchmarks in the order of panel a. IWC runs were not offered user-defined tools, so their bars are 0 by design.
    order3 = ['IWC', 'BixBench50', 'CompBio']
    rows_ = [r for r in D['fig3c'] if r['config'] != 'All configurations']
    labels, req, yy, rowsb, groups = [], [], [], [], []
    pos = 0
    for b in order3:
        y0 = pos
        for r in [r for r in rows_ if r['benchmark'] == b]:
            n, d = r['requesting']
            cfg = r['config'].replace(' (Codex, IWC)', '').replace(' 0813 (Codex)', '').replace(' (Codex)', '')
            labels.append(CFG_LABEL.get(cfg, cfg).replace('\n', ' ') if cfg != SUPERSEDED else 'DeepSeek V4 Pro (Claude\nCode, superseded)')
            req.append(100 * n / d); yy.append(pos); pos += 1
            rowsb.append(dict(benchmark=BENCH_LABEL[b], model_configuration=cfg, user_defined_tools_offered='no' if b == 'IWC' else 'yes',
                              runs_requesting_a_user_defined_tool=n, galaxy_condition_runs_with_traces=d, percent=round(100 * n / d, 1)))
        groups.append((b, y0, pos - 1)); pos += 0.9
    ax.barh(yy, req, color=GALAXY, height=0.66)
    for y_, v in zip(yy, req):
        ax.text(v + 1.5, y_, f'{v:.0f}%', va='center', fontsize=5.0)
    ax.set_yticks(yy); ax.set_yticklabels(labels, fontsize=5.1); ax.set_xlim(0, 100)
    ax.set_xlabel('Galaxy-condition runs that requested a\nuser-defined tool (agent-written code run as a Galaxy job, %)'); grid_x(ax)
    for b, i0, i1 in groups:
        ax.plot([-0.66, -0.66], [i0 - 0.3, i1 + 0.3], transform=ax.get_yaxis_transform(), color=INK2, lw=0.6, clip_on=False)
        ax.text(-0.70, (i0 + i1) / 2, BENCH_LABEL[b], transform=ax.get_yaxis_transform(), rotation=90, va='center', ha='center', fontsize=5.2, fontweight='bold')
    b, i0, i1 = groups[0]
    ax.text(12, (i0 + i1) / 2, 'User-defined tools not offered\nfor IWC tasks (0 of 120 runs)', fontsize=5.0, color=INK2, ha='left', va='center')
    ax.set_ylim(yy[-1] + 0.7, -0.7)
    sd['b_user_defined_tool_requests'] = pd.DataFrame(rowsb)
    # ---- c: input-token usage per Galaxy-condition run, by model configuration and benchmark
    panel_label(fig, 0.50, 0.585, 'c'); panel_title(fig, 0.50, 0.585, 'Input-token usage differed several-fold between model\nconfigurations and did not track performance')
    tr, tm = D['input_tokens_runs'], D['input_tokens']
    rowsc = []
    for k, b in enumerate(order3):
        ax = fig.add_axes([0.66, 0.405 - k * 0.155, 0.27, 0.11])
        cl = CONFIGS + ([SUPERSEDED] if b == 'BixBench50' else [])
        for i, c in enumerate(cl):
            v = np.array(tr[f'{b}|{c}|galaxy']) / 1e6
            bp = ax.boxplot(v, positions=[i], orientation='horizontal', widths=0.6, patch_artist=True, showfliers=False,
                            medianprops=dict(color=INK, lw=0.9), whiskerprops=dict(lw=0.5, color=INK2), capprops=dict(lw=0.5, color=INK2),
                            boxprops=dict(lw=0.5, ec=GALAXY, fc='#CFE3F1'))
            m = tm[f'{b}|{c}|galaxy']['median'] / 1e6
            ax.text(1.01, i, f'{m:.2f}' if m < 10 else f'{m:.1f}', transform=ax.get_yaxis_transform(), fontsize=5.0, va='center')
            rowsc.append(dict(benchmark=BENCH_LABEL[b], model_configuration=CFG_LABEL[c].replace('\n', ' '), galaxy_condition_runs=len(v),
                              median_input_tokens_millions=round(m, 3), q1=round(float(np.percentile(v, 25)), 3), q3=round(float(np.percentile(v, 75)), 3),
                              open_ended_code_median_millions=round(tm[f'{b}|{c}|open_ended_code']['median'] / 1e6, 3)))
        ax.set_xscale('log'); ax.set_xlim(0.1, 80); ax.set_xticks([0.1, 1, 10]); ax.set_xticklabels(['0.1', '1', '10'])
        ax.xaxis.set_minor_locator(plt.NullLocator())
        ax.set_yticks(range(len(cl))); ax.set_yticklabels([CFG_LABEL[c].replace('\n', ' ') if c != SUPERSEDED else 'DeepSeek V4 Pro (Claude Code)' for c in cl], fontsize=5.0)
        ax.set_ylim(len(cl) - 0.5, -0.6); grid_x(ax)
        ax.set_title(BENCH_LABEL[b], fontsize=5.4, fontweight='bold', loc='left', pad=1)
        ax.text(1.01, -0.95, 'Median', transform=ax.get_yaxis_transform(), fontsize=5.0, fontweight='bold', va='center')
        if k == 2:
            ax.set_xlabel('Input-token usage per Galaxy-condition run (millions; log scale)')
    fig.text(0.66, 0.012, 'Box: middle 50% of runs; line: median; whiskers: 1.5 × interquartile range.', fontsize=5.0, color=INK2)
    sd['c_input_token_usage'] = pd.DataFrame(rowsc)
    save_main(fig, 'Fig3', OUTDIR)
    source_data('Fig3', sd)


# =====================================================================================================
MECH = [('V4', 'Domain convention or definition applied differently', OI_SKY),
        ('V6', 'Error in the final step (sorting, counting, units)', OI_GREEN),
        ('V5', 'Hand-written method instead of the library method', OI_ORANGE),
        ('V3', 'Different software version installed', OI_ORANGE),
        ('V7', 'No answer submitted', NEUTRAL_LIGHT),
        ('V1', 'Galaxy interface trap (silent default, output\nsemantics or job not dispatched)', OI_BLACK),
        ('V8', 'Answer retrieved from benchmark source files', OI_PURPLE)]
HATCH = {'V3': '//////'}
CFG5 = CONFIGS + [SUPERSEDED]
ROW5 = {c: CFG_LABEL[c].replace('\n', ' ') for c in CFG5}
ROW5[SUPERSEDED] = 'DeepSeek V4 Pro (Claude\nCode, superseded)'


def fig4():
    fig = plt.figure(figsize=(W_DOUBLE, 165 * MM))
    sd = {}
    bx = D['bix_accuracy']
    # ---- a-c: replicate agreement, one small multiple per benchmark on shared rows, in the order of Fig. 3a
    ys, head = [], {}
    y = 0
    for cfg in CFG5:
        head[cfg] = y; y += 1
        for env in ENVS:
            ys.append((cfg, env, y)); y += 1
        y += 0.35
    y_end = y
    # Every panel orders its segments all runs succeed, split, no run succeeds; split is coloured by execution condition.
    split2 = lambda lab: ((Patch(fc=ENV_COLOR['open_ended_code']), Patch(fc=ENV_COLOR['galaxy'])), lab)
    cells4, split_iwc = D['fig4c_cells'], D['fig4c']
    tot = {e: {k: sum(bx[f'{c}|{e}'][k] for c in CFG5) for k in ('all', 'split', 'none')} for e in ENVS}
    iwc_n = {e: sum(cells4[f'IWC|{e}|{c}']['cells'] for c in CONFIGS) for e in ENVS}
    iwc_s = {e: sum(split_iwc[f'IWC|{e}'].values()) for e in ENVS}
    cb = {e: {k: sum(cells4[f'CompBio|{e}|{c}'].get(k, 0) for c in CONFIGS) for k in ('cells', 'all', 'mixed', 'none')} for e in ENVS}

    def segs(b, cfg, env):
        if b == 'IWC':
            n, s = cells4[f'IWC|{env}|{cfg}']['cells'], split_iwc[f'IWC|{env}'].get(cfg, 0)
            return [('within', 'Range 0.05 or less', NEUTRAL_LIGHT, n - s), ('split', 'Split (range above 0.05)', ENV_COLOR[env], s),
                    ('unscored', 'Not scored', 'white', 10 - n)]
        if b == 'BixBench50':
            c = bx[f'{cfg}|{env}']
            return [('all', '3/3 scored correct', NEUTRAL_LIGHT, c['all']), ('split', 'Split (1–2/3)', ENV_COLOR[env], c['split']),
                    ('none', '0/3 scored correct', NEUTRAL_DARK, c['none'])]
        c = cells4[f'CompBio|{env}|{cfg}']
        return [('all', '3/3 matched the consensus answer', NEUTRAL_LIGHT, c.get('all', 0)), ('split', 'Split (1–2/3)', ENV_COLOR[env], c.get('mixed', 0)),
                ('none', '0/3 matched the consensus answer', NEUTRAL_DARK, c.get('none', 0))]

    top = [('IWC', 'IWC: fewer replicate sets split in\nthe Galaxy condition', CONFIGS, 'of 10 tasks', 10, range(0, 11, 2), 1,
            [(Patch(fc=NEUTRAL_LIGHT), 'Range 0.05 or less'), split2('Split (range above 0.05)'), (Patch(fc='white', ec=INK2, lw=0.4), 'Not scored')],
            f"Split: the three output-agreement values ranged by more than 0.05; 3/3 and 0/3 are not defined for a continuous endpoint. "
            f"Split sets: open-ended code {iwc_s['open_ended_code']} of {iwc_n['open_ended_code']}, Galaxy {iwc_s['galaxy']} of {iwc_n['galaxy']}.",
            'a_iwc_split_replicate_sets'),
           ('BixBench50', 'BixBench-Verified-50: the Galaxy\ncondition had more unanimous and\nfewer split replicate sets', CFG5, 'of 50 tasks', 50,
            range(0, 51, 10), 3,
            [(Patch(fc=NEUTRAL_LIGHT), '3/3 scored correct'), split2('Split (1–2/3)'), (Patch(fc=NEUTRAL_DARK), '0/3 scored correct')],
            f"All five model configurations, 250 replicate sets per condition: open-ended code {tot['open_ended_code']['all']} at 3/3, "
            f"{tot['open_ended_code']['split']} split, {tot['open_ended_code']['none']} at 0/3; Galaxy {tot['galaxy']['all']}, {tot['galaxy']['split']} and "
            f"{tot['galaxy']['none']} (0/3: 5 of 50 for every model configuration).", 'b_repeatability_categories'),
           ('CompBio', 'CompBioBench: fewer Galaxy-condition\nreplicate sets split on the\nconsensus answer', CONFIGS, f"of {cb['galaxy']['cells'] // 4} tasks", 82,
            range(0, 81, 20), 4,
            [(Patch(fc=NEUTRAL_LIGHT), '3/3 matched consensus'), split2('Split (1–2/3)'), (Patch(fc=NEUTRAL_DARK), '0/3 matched consensus')],
            f"Success: the consensus answer, given by at least 20 of the 25 runs of a task ({cb['galaxy']['cells'] // 4} of 100 tasks). "
            f"Open-ended code {cb['open_ended_code']['all']} at 3/3, {cb['open_ended_code']['mixed']} split, {cb['open_ended_code']['none']} at 0/3; "
            f"Galaxy {cb['galaxy']['all']}, {cb['galaxy']['mixed']} and {cb['galaxy']['none']}.",
            'c_consensus_repeatability')]
    for k, (b, title, cfgs, per, xmax, xt, min_lab, handles, note, sheet) in enumerate(top):
        x0 = 0.155 + k * 0.29
        ax = fig.add_axes([x0, 0.55, 0.235, 0.355])
        panel_label(fig, 0.005 if k == 0 else x0 - 0.035, 0.995, 'abc'[k]); panel_title(fig, 0.005 if k == 0 else x0 - 0.035, 0.995, title)
        rows = []
        for cfg, env, yy_ in ys:
            if cfg not in cfgs:
                continue
            left = 0
            for key, lab, col, v in segs(b, cfg, env):
                if v:
                    ax.barh(yy_, v, left=left, color=col, height=0.72, ec=INK2 if key == 'unscored' else 'white', lw=0.4 if key == 'unscored' else 0.5)
                if v >= min_lab and key != 'unscored':
                    ax.text(left + v / 2, yy_, str(v), ha='center', va='center', fontsize=5.0, color=INK if col == NEUTRAL_LIGHT else 'white')
                left += v
                rows.append(dict(benchmark=BENCH_LABEL[b], model_configuration=ROW5[cfg].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[env],
                                 category=lab, replicate_sets=v))
        for cfg in CFG5:
            if k == 0:
                ax.text(-0.03, head[cfg], ROW5[cfg], transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=5.2, fontweight='bold',
                        linespacing=1.05)
            if cfg not in cfgs:
                ax.text(0.5, head[cfg] + 1.5, 'Not run with this agent harness', transform=ax.get_yaxis_transform(), ha='center', va='center',
                        fontsize=5.0, color=INK2)
        ax.set_yticks([v for *_, v in ys]); ax.set_yticklabels([ENV_LABEL[e] for _, e, _ in ys] if k == 0 else [], fontsize=5.0)
        ax.set_ylim(y_end + 0.1, -1.3); ax.set_xlim(0, xmax); ax.set_xticks(xt)
        ax.set_xlabel(f'Replicate sets\n({per} per model configuration)'); grid_x(ax)
        handles = [handles[0], handles[2], handles[1]]  # two columns filled downwards: row 1 all succeed | split, row 2 none succeed
        ax.legend(handles=[h for h, _ in handles], labels=[l for _, l in handles], handler_map={tuple: HandlerTuple(ndivide=None, pad=0)},
                  handlelength=1.8, loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, fontsize=5.0)
        fig.text(x0, 0.487, textwrap.fill(note, 52), fontsize=5.0, color=INK2, va='top', linespacing=1.2)
        sd[sheet] = pd.DataFrame(rows)
    # ---- d: divergence mechanisms
    ax = fig.add_axes([0.155, 0.065, 0.33, 0.10])
    panel_label(fig, 0.005, 0.425, 'd'); panel_title(fig, 0.005, 0.425, 'Replicate runs diverged for different reasons in the\ntwo conditions (BixBench-Verified-50)')
    md = D['fig4d']
    rowsd, share = [], {}
    for i, env in enumerate(ENVS):
        tot_ = sum(md[env].values()); left = 0
        for key, name, col in MECH:
            v = md[env].get(key, 0)
            if not v:
                continue
            w = 100 * v / tot_
            ax.barh(i, w, left=left, color=col, height=0.66, ec=INK2 if key in HATCH else 'white', lw=0.6, hatch=HATCH.get(key))
            if w >= 5:
                ax.text(left + w / 2, i, str(v), ha='center', va='center', fontsize=5.0, color='white' if col in DARK_FILL else INK,
                        bbox=dict(boxstyle='round,pad=0.1', fc=col, ec='none') if key in HATCH else None)
            left += w
            rowsd.append(dict(execution_condition=ENV_LABEL_LONG[env], divergence_mechanism=name.replace('\n', ' '), scored_incorrect_replicate_runs=v, total=tot_,
                              percent=round(w, 1)))
        share[env] = (md[env].get('V5', 0) + md[env].get('V3', 0), tot_)
        ax.text(101, i, f'{tot_} runs', va='center', fontsize=5.0, color=INK2)
    ax.set_yticks([0, 1]); ax.set_yticklabels([ENV_LABEL[e] for e in ENVS]); ax.set_ylim(1.5, -0.5); ax.set_xlim(0, 100)
    ax.set_xlabel('Scored-incorrect replicate runs in split replicate sets (%)'); grid_x(ax)
    axl = fig.add_axes([0.155, 0.19, 0.33, 0.155]); axl.axis('off')
    for k, (key, name, col) in enumerate(MECH):
        xk, yk = 0.0, 0.96 - k * 0.145
        axl.add_patch(Rectangle((xk, yk - 0.055), 0.03, 0.11, fc=col, ec=INK2 if key in HATCH or col == NEUTRAL_LIGHT else 'none', lw=0.3,
                                hatch=HATCH.get(key), transform=axl.transAxes))
        axl.text(xk + 0.045, yk, name.replace('\n', ' '), fontsize=5.0, va='center', transform=axl.transAxes, linespacing=1.05)
    fig.text(0.023, 0.382, f"Hand-written method or software-version difference: {share['open_ended_code'][0]} of {share['open_ended_code'][1]} open-ended code runs,\n"
             f"{share['galaxy'][0]} of {share['galaxy'][1]} Galaxy runs;\nGalaxy interface trap: {md['galaxy'].get('V1', 0)} of {share['galaxy'][1]} Galaxy runs.",
             fontsize=5.0, va='top', fontweight='bold', linespacing=1.2)
    sd['d_divergence_mechanisms'] = pd.DataFrame(rowsd)
    # ---- e: run-level versus unanimous accuracy
    ax = fig.add_axes([0.70, 0.065, 0.22, 0.255])
    panel_label(fig, 0.50, 0.425, 'e'); panel_title(fig, 0.50, 0.425, 'Requiring all three replicate runs to succeed widened\ndifferences between model configurations')
    rowse, ys, labs = [], [], []
    y = 0
    for cfg in CFG5:
        for env in ENVS:
            c = bx[f'{cfg}|{env}']
            yy_ = y + (-0.17 if env == 'open_ended_code' else 0.17)
            ax.plot([c['unanimous'], c['run_level']], [yy_, yy_], color=ENV_COLOR[env], lw=0.9, zorder=2)
            ax.plot(c['run_level'], yy_, ENV_MARKER[env], ms=3.4, mfc='white', mec=ENV_COLOR[env], mew=0.9, zorder=3)
            ax.plot(c['unanimous'], yy_, ENV_MARKER[env], ms=3.4, mfc=ENV_COLOR[env], mec='white', mew=0.4, zorder=4)
            rowse.append(dict(model_configuration=ROW5[cfg].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[env], run_level_accuracy=round(c['run_level'], 2),
                              unanimous_accuracy=round(c['unanimous'], 2), difference_pp=round(c['unanimous'] - c['run_level'], 2)))
        ax.text(1.02, y, f"{signed(bx[f'{cfg}|galaxy']['unanimous'] - bx[f'{cfg}|galaxy']['run_level'], 1)}", transform=ax.get_yaxis_transform(),
                fontsize=5.0, va='center')
        ys.append(y); labs.append(ROW5[cfg]); y += 1
    ax.set_yticks(ys); ax.set_yticklabels(labs, fontsize=5.1); ax.set_ylim(y - 0.4, -0.7); ax.set_xlim(50, 95); grid_x(ax)
    ax.set_xlabel('Accuracy (%): open symbol, run-level;\nfilled symbol, unanimous (3/3 replicate runs)')
    ax.text(1.02, -0.62, 'Galaxy:\nunanimous −\nrun-level', transform=ax.get_yaxis_transform(), fontsize=5.0, fontweight='bold', va='bottom')
    four = {e: (sum(bx[f'{c}|{e}']['all'] for c in CONFIGS) / 2, sum(bx[f'{c}|{e}']['correct'] for c in CONFIGS) / 6) for e in ENVS}
    five = {e: (sum(bx[f'{c}|{e}']['all'] for c in CFG5) / 2.5, sum(bx[f'{c}|{e}']['correct'] for c in CFG5) / 7.5) for e in ENVS}
    fig.text(0.518, 0.382, f"Condition difference, Galaxy − open-ended code (percentage points):\nfour Codex model configurations, run-level {signed(four['galaxy'][1] - four['open_ended_code'][1], 1)}, "
             f"unanimous {signed(four['galaxy'][0] - four['open_ended_code'][0], 1)};\nall five model configurations, run-level "
             f"{signed(five['galaxy'][1] - five['open_ended_code'][1], 1)}, unanimous {signed(five['galaxy'][0] - five['open_ended_code'][0], 1)}.",
             fontsize=5.0, va='top', color=INK2, linespacing=1.2)
    ax.legend(handles=env_handles(ms=3.2), loc='upper left', fontsize=5.0)
    sd['e_run_level_versus_unanimous'] = pd.DataFrame(rowse)
    save_main(fig, 'Fig4', OUTDIR)
    source_data('Fig4', sd)


# =====================================================================================================
CATCOL = {'C1': OI_SKY, 'C2': OI_GREEN, 'C3': '#F0E442', 'C4': OI_BLACK, 'C5': OI_ORANGE, 'C6': OI_PURPLE,
          'C7': NEUTRAL_MID, 'C8': NEUTRAL_LIGHT}
CATSHORT = {'C1': 'Equivalent answer in another notation', 'C2': 'Scoring or evaluator artifact', 'C3': 'Reference depends on an unstated choice',
            'C4': 'Galaxy platform, wrapper or server', 'C5': 'Agent analysis error', 'C6': 'Answer provenance (benchmark sources read)',
            'C7': 'Near-perfect score concealed a changed result', 'C8': 'Completion failure (no answer)'}


def fig5():
    import collections
    fig = plt.figure(figsize=(W_DOUBLE, 165 * MM))
    sd = {}
    cases = D['task_cases']
    # ---- a: primary cause of every audited task case
    ax = fig.add_axes([0.17, 0.72, 0.50, 0.19])
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'In 30 of 93 audited task cases the primary cause was the reference or evaluator, not the agent or Galaxy')
    groups = [('All three benchmarks', None), ('BixBench-Verified-50', 'BixBench50'), ('CompBioBench', 'CompBio'), ('IWC', 'IWC')]
    rowsa = []
    for i, (lab, b) in enumerate(groups):
        cnt = collections.Counter(c['category'] for c in cases if b is None or c['benchmark'] == b)
        left = 0
        for k in ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']:
            v = cnt.get(k, 0)
            if not v:
                continue
            ax.barh(i, v, left=left, color=CATCOL[k], height=0.66, ec='white', lw=0.6)
            if v >= 3 or (b == 'IWC' and v >= 1):
                ax.text(left + v / 2, i, str(v), ha='center', va='center', fontsize=5.0, color='white' if CATCOL[k] in (OI_BLACK, OI_PURPLE) else INK)
            left += v
            rowsa.append(dict(benchmark=lab, primary_cause=CATSHORT[k], category_code=k, task_cases=v))
        ax.text(left + 1, i, f'{left} task cases', va='center', fontsize=5.0, color=INK2)
    ax.set_yticks(range(len(groups))); ax.set_yticklabels([g[0] for g in groups], fontsize=5.3); ax.set_ylim(len(groups) - 0.5, -0.5)
    ax.set_xlim(0, 105); ax.set_xlabel('Task cases (tasks with at least one wrong, scored-incorrect or low-scoring run), by primary cause'); grid_x(ax)
    ax.plot([0, 30], [-0.55, -0.55], color=INK, lw=0.8, clip_on=False)
    ax.text(15, -0.62, 'Reference or evaluator: 30', ha='center', va='bottom', fontsize=5.0, fontweight='bold')
    axk = fig.add_axes([0.70, 0.705, 0.29, 0.22]); axk.axis('off')
    for k_, key in enumerate(['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8']):
        yk = 0.97 - k_ * 0.105
        axk.add_patch(Rectangle((0.0, yk - 0.035), 0.05, 0.07, fc=CATCOL[key], ec=INK2 if key == 'C8' else 'none', lw=0.3, transform=axk.transAxes))
        axk.text(0.07, yk, CATSHORT[key], fontsize=5.0, va='center', transform=axk.transAxes)
    nf = {f: sum(1 for c in cases if f in c['tags']) for f in ('galaxy-platform-defect', 'benchmark-answer-retrieval', 'local-fallback-in-galaxy', 'cross-run-output-reuse')}
    txt = (f"Recorded in addition to the primary cause: Galaxy contributed as primary or secondary cause in {nf['galaxy-platform-defect']} task cases; benchmark answers were "
           f"retrieved, or retrieval was attempted, in {nf['benchmark-answer-retrieval']};\na Galaxy-condition answer was computed in the local shell in "
           f"{nf['local-fallback-in-galaxy']} (15 correct CompBioBench answers); an answer was copied from another run through the shared Galaxy account in "
           f"{nf['cross-run-output-reuse']} (Extended Data Fig. 8).")
    fig.text(0.023, 0.655, txt, fontsize=5.0, color=INK2, va='top', linespacing=1.2)
    sd['a_primary_cause'] = pd.DataFrame(rowsa)
    sd['a_task_cases'] = pd.DataFrame([dict(benchmark=BENCH_LABEL[c['benchmark']], task=c['task'], primary_cause=CATSHORT[c['category']], category_code=c['category'],
                                            galaxy_correct=c['galaxy'], open_ended_code_correct=c['code'], finding=c['finding'], tags='; '.join(c['tags'])) for c in cases])
    # ---- b: bix-35-q1
    axb = fig.add_axes([0.0, 0.03, 0.50, 0.56]); axb.axis('off')
    panel_label(fig, 0.005, 0.60, 'b'); panel_title(fig, 0.005, 0.60, 'bix-35-q1: an interface-binding failure that\nreturned a successful job')
    b35 = D['bix35']
    n_sub = sum(1 for r in b35 if any(j['metric'] == 'total_tree_length' for j in r['jobs']))
    fail = [r for r in b35 if not r['correct']][0]
    axb.text(0.045, 0.915, 'Task: PhyKIT evolutionary rate of one BUSCO gene tree; reference 0.0471.\nScored correct: open-ended code 15 of 15, Galaxy 14 of 15 runs.',
             fontsize=5.3, va='top', transform=axb.transAxes, linespacing=1.25)
    box(axb, 0.045, 0.72, 0.36, 0.12, 'Agent requests metric\n"evolutionary rate"', fc=ENV_TINT['galaxy'], ec=GALAXY, fs=5.3)
    box(axb, 0.52, 0.72, 0.44, 0.12, 'Galaxy binds the nested conditional\nand silently runs the default metric,\n"total tree length"; job state: ok', fc=LIGHT, ec=INK2, fs=5.3)
    arrow(axb, 0.405, 0.78, 0.52, 0.78)
    axb.text(0.74, 0.69, f'{n_sub} of 15 Galaxy histories contain such a job', ha='center', va='top', fontsize=5.2, fontweight='bold', transform=axb.transAxes)
    box(axb, 0.045, 0.40, 0.42, 0.17, 'Six runs: the Galaxy interface compared\nrequested with resolved parameters, flagged\nthe mismatch, and the agent resubmitted;\n'
        'the answer 0.0471 was scored correct', fc='white', ec=GALAXY, fs=5.1)
    box(axb, 0.54, 0.40, 0.42, 0.17, 'One run (DeepSeek V4 Pro, Claude Code):\nthe selector key was removed from the\npayload, so nothing was compared and\n'
        f'no mismatch was flagged; answer {fail["answer"]}', fc='white', ec=OI_BLACK, lw=0.9, fs=5.1)
    arrow(axb, 0.60, 0.645, 0.30, 0.575); arrow(axb, 0.80, 0.645, 0.75, 0.575)
    box(axb, 0.54, 0.10, 0.42, 0.20, 'The agent had divided 0.188376 by four\ntaxa (0.04709) and noted that the output\nwas the total tree length, then trusted\nthe tool output', fc=LIGHT, ec=GRID, fs=5.1)
    arrow(axb, 0.75, 0.40, 0.75, 0.30)
    axb.text(0.045, 0.28, 'Fix: validate tool state strictly and return\nevery difference between requested and\nresolved parameters to the agent\n(Extended Data Fig. 7)',
             fontsize=5.1, va='top', transform=axb.transAxes, color=INK2, linespacing=1.2)
    sd['b_bix35q1_runs'] = pd.DataFrame([dict(model_configuration=r['config'], replicate_run=r['replicate'], answer=r['answer'], scored_correct=r['correct'],
                                              phykit_jobs_in_order='; '.join(j['metric'] or 'unknown' for j in r['jobs']),
                                              any_default_metric_job=any(j['metric'] == 'total_tree_length' for j in r['jobs'])) for r in b35])
    # ---- c: contaminated-rna-q1
    axc = fig.add_axes([0.50, 0.03, 0.50, 0.56]); axc.axis('off')
    panel_label(fig, 0.505, 0.60, 'c'); panel_title(fig, 0.505, 0.60, 'contaminated-rna-q1: a reference database the\nworkbench did not reliably provide')
    cr = D['contaminated_rna_q1']
    ok = {e: (sum(1 for r in cr['runs'] if r['condition'] == e and r['correct'] and r['config'] != 'GPT-6 Astra'),
              sum(1 for r in cr['runs'] if r['condition'] == e and r['config'] != 'GPT-6 Astra')) for e in ENVS}
    okc = (sum(1 for r in cr['runs'] if r['condition'] == 'open_ended_code' and r['correct']), sum(1 for r in cr['runs'] if r['condition'] == 'open_ended_code'))
    axc.text(0.045, 0.915, f"Task: name the contaminant species in a mostly human RNA-seq file\n({cr['total_reads']:,} reads); reference answer $\\it{{Hydra\\ vulgaris}}$.\n"
             f"Scored correct: open-ended code {okc[0]} of {okc[1]} (GPT-6 Astra included), Galaxy {ok['galaxy'][0]} of {ok['galaxy'][1]} runs.",
             fontsize=5.3, va='top', transform=axc.transAxes, linespacing=1.25)
    box(axc, 0.28, 0.70, 0.44, 0.11, 'Kraken2 with core_nt, the only installed\ndatabase that contains cnidarians', fc=ENV_TINT['galaxy'], ec=GALAXY, fs=5.3)
    box(axc, 0.04, 0.47, 0.42, 0.16, f"Completed (9 runs): coherent Cnidaria\nto $\\it{{Hydra}}$ lineage, {cr['hydra_reads']:,} reads; confirmed\nby read extraction and BLAST in Galaxy",
        fc='white', ec=GALAXY, fs=5.1)
    box(axc, 0.54, 0.47, 0.42, 0.16, 'Did not complete (3 runs): empty\nclassification datasets; hours on one\nthread, then cancelled; four-hour\nwall-time limit', fc='white', ec=OI_BLACK, lw=0.9, fs=5.1)
    arrow(axc, 0.42, 0.70, 0.28, 0.63); arrow(axc, 0.58, 0.70, 0.72, 0.63)
    box(axc, 0.54, 0.14, 0.42, 0.22, 'Fallback: standard-16 database (human,\nbacteria, viruses, plasmids; no cnidarians)\nor mitochondrion-only BLAST. Answers:\n'
        f"Epstein–Barr virus ({cr['ebv_reads']} reads, 0.2%)\nor $\\it{{Artemia}}$", fc=LIGHT, ec=GRID, fs=5.1)
    arrow(axc, 0.75, 0.47, 0.75, 0.36)
    axc.text(0.045, 0.34, 'Open-ended code: agents installed their own\ndatabases; the one scored-incorrect run built a\ncustom database of human, mouse, rat and\n'
             'Epstein–Barr virus only, and reported rat.\n\nFix: database coverage, job reliability and\nexplicit statements of what a reference\ndatabase can contain',
             fontsize=5.1, va='top', transform=axc.transAxes, color=INK2, linespacing=1.2)
    sd['c_contaminated_rna_q1_runs'] = pd.DataFrame([dict(model_configuration=r['config'], execution_condition=ENV_LABEL_LONG[r['condition']], replicate_run=r['replicate'],
                                                          answer=r['answer'], scored_correct_against_reference=r['correct'],
                                                          galaxy_failure_mode=cr['failures'].get(f"{r['config']}|{r['replicate']}", '') if r['condition'] == 'galaxy' else '')
                                                     for e in ENVS for r in cr['runs'] if r['condition'] == e])
    save_main(fig, 'Fig5', OUTDIR)
    source_data('Fig5', sd)


if __name__ == '__main__':
    which = sys.argv[1:] or ['1', '2', '3', '4', '5']
    for w in which:
        globals()[f'fig{w}']()
        print('done Fig', w)
