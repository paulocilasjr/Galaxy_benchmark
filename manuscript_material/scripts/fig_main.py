"""Main figures 1-5 and their Source Data workbooks.

Run from the repository root after build_data.py:  python manuscript_material/scripts/fig_main.py [1 2 3 4 5]

Design rules (see style.py): open-ended code is the reference condition and is always shown first; vermillion squares
are open-ended code and blue circles are Galaxy; no abbreviations; every panel title states its finding.
"""
import json
import os
import statistics as st
import sys

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch, Rectangle

sys.path.insert(0, os.path.dirname(__file__))
from style import (BENCH, BENCH_2L, BENCH_LABEL, CFG_LABEL, CODE, CONFIGS, ENV_COLOR, ENV_LABEL, ENV_MARKER,  # noqa: E402
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


def dot(ax, x, y, env, filled=True, ms=3.6, z=3):
    ax.plot(x, y, ENV_MARKER[env], ms=ms, mfc=ENV_COLOR[env] if filled else 'white', mec=ENV_COLOR[env] if not filled else 'white',
            mew=0.8 if not filled else 0.4, zorder=z, ls='')


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
    ax.text(0.045, 0.97, 'Open-ended code (reference condition)', fontsize=6.5, fontweight='bold', va='top')
    box(ax, 0.03, 0.40, 0.27, 0.30, 'Language-model\nagent\n(same model and\nagent harness)', fc=LIGHT, weight='bold')
    box(ax, 0.37, 0.40, 0.25, 0.30, 'Unrestricted\nshell', fc=ENV_TINT['open_ended_code'], ec=CODE, lw=0.9, weight='bold')
    box(ax, 0.69, 0.40, 0.29, 0.30, 'Installs and runs\nany software on\nlocal files', fc=LIGHT, ec=GRID)
    arrow(ax, 0.30, 0.55, 0.37, 0.55); arrow(ax, 0.62, 0.55, 0.69, 0.55)
    ax.text(0.50, 0.19, 'Recorded: commands, scripts, command output\nand final files; no record of individual analysis jobs',
            ha='center', va='center', fontsize=5.3, color=INK2, style='italic')
    # ---- b: Galaxy-mediated condition
    ax = fig.add_axes([0.42, 0.47, 0.58, 0.50]); ax.axis('off')
    panel_label(fig, 0.415, 0.985, 'b')
    ax.text(0.035, 0.97, 'Galaxy-mediated condition', fontsize=6.5, fontweight='bold', va='top')
    box(ax, 0.01, 0.40, 0.17, 0.30, 'Language-model\nagent\n(Codex agent\nharness)', fc=LIGHT, weight='bold')
    ax.add_patch(FancyBboxPatch((0.235, 0.10), 0.27, 0.80, boxstyle='round,pad=0,rounding_size=0.012', fc='white', ec=GALAXY,
                                lw=0.9, transform=ax.transAxes))
    ax.text(0.37, 0.845, 'Galaxy interface\n(Model Context Protocol)', ha='center', va='center', fontsize=5.8, fontweight='bold')
    ops = ['Tool search', 'Tool parameter descriptions', 'History inspection', 'Job submission\nand monitoring',
           'User-defined tools\n(agent-written code)']
    for i, op in enumerate(ops):
        y = 0.70 - i * 0.13
        box(ax, 0.25, y - 0.05, 0.24, 0.10, op, fc=ENV_TINT['galaxy'], ec=GALAXY, lw=0.5, fs=5.3)
    ax.add_patch(FancyBboxPatch((0.565, 0.12), 0.425, 0.78, boxstyle='round,pad=0,rounding_size=0.012', fc='white', ec=INK2,
                                lw=0.8, transform=ax.transAxes))
    ax.text(0.7775, 0.845, 'Galaxy server (usegalaxy.org)', ha='center', va='center', fontsize=5.8, fontweight='bold')
    for i, t in enumerate(['Installed tools (Galaxy Tool Shed)', 'Histories and datasets',
                           'Jobs: state, parameters, error messages', 'Agent-written tools run as Galaxy jobs']):
        box(ax, 0.585, 0.66 - i * 0.145, 0.385, 0.10, t, fc=LIGHT, ec=GRID, lw=0.4, fs=5.3)
    ax.text(0.7775, 0.05, 'Recorded: tool identities and versions,\nrequested and resolved parameters, datasets,\njob states and error messages',
            ha='center', va='center', fontsize=5.3, color=INK2, style='italic')
    arrow(ax, 0.18, 0.55, 0.235, 0.55); arrow(ax, 0.505, 0.55, 0.565, 0.55, style='<|-|>')
    ax.text(0.095, 0.30, 'Local shell used\nonly to stage files\nand extract the\nanswer', ha='center', va='top', fontsize=5.1, color=INK2)
    # ---- c: design matrix
    ax = fig.add_axes([0.205, 0.03, 0.465, 0.30])
    panel_label(fig, 0.005, 0.445, 'c')
    fig.text(0.023, 0.444, 'Three benchmarks, five agent configurations, three replicates of every task', fontsize=6.5, fontweight='bold', va='top')
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
            table.append(dict(benchmark=BENCH_LABEL[b], environment=ENV_LABEL[env], configuration=cfg, runs=n or 0))
    ax.set_xlim(-0.02, 6); ax.set_ylim(len(rowsl) + 1.2, -0.1)
    ax.set_yticks([i + 0.45 for i in range(len(rowsl))])
    ax.set_yticklabels(['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro',
                        'DeepSeek V4 Pro, Claude Code harness\n(superseded; reported separately)',
                        'GPT-6 Astra (open-ended code only;\nnot paired)'], fontsize=5.4)
    ax.set_xticks([]); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    for j, (b, env) in enumerate(cols):
        ax.text(j + 0.48, -0.2, 'Open-ended\ncode' if env == 'open_ended_code' else 'Galaxy', ha='center', va='bottom', fontsize=5.3)
    for k, b in enumerate(BENCH):
        ax.text(2 * k + 0.98, -1.25, BENCH_LABEL[b], ha='center', va='bottom', fontsize=5.8, fontweight='bold')
        ax.plot([2 * k + 0.05, 2 * k + 1.9], [-1.15, -1.15], color=INK, lw=0.6, clip_on=False)
    ax.text(3.0, len(rowsl) + 0.55, 'Numbers are archived runs: tasks × 3 replicates, per configuration and environment',
            ha='center', va='center', fontsize=5.2, color=INK2)
    # ---- c (right): benchmark descriptions
    ax2 = fig.add_axes([0.70, 0.02, 0.30, 0.40]); ax2.axis('off')
    cards = [('BixBench-Verified-50', '50 tasks; platform-neutral questions', 'Endpoint: answer accepted or rejected\nby the original evaluator'),
             ('CompBioBench', '100 tasks; platform-neutral questions', 'Endpoint: aggregate score\n(answers credited, of 100)'),
             ('IWC (Intergalactic Workflow Commission)', '10 tasks derived from published Galaxy workflows',
              "Endpoint: agreement with the workflow's\nreference output (0 to 1)")]
    for k, (name, l1, l2) in enumerate(cards):
        y = 0.97 - k * 0.245
        ax2.add_patch(Rectangle((0.0, y - 0.20), 0.012, 0.20, fc=INK, ec='none', transform=ax2.transAxes))
        ax2.text(0.035, y, name, fontsize=5.8, fontweight='bold', va='top', transform=ax2.transAxes)
        ax2.text(0.035, y - 0.058, l1, fontsize=5.3, va='top', transform=ax2.transAxes)
        ax2.text(0.035, y - 0.105, l2, fontsize=5.3, va='top', color=INK2, transform=ax2.transAxes, linespacing=1.15)
    tot = {k: sum(v[k] for v in inv.values()) for k in ('runs', 'traces', 'nonfetch_jobs', 'mcp_calls')}
    ax2.text(0.0, 0.0, f"Archive: {tot['runs']:,} runs · {tot['traces']:,} agent traces\n{tot['nonfetch_jobs']:,} Galaxy analysis jobs "
             f"· {tot['mcp_calls']:,} Galaxy interface calls", fontsize=5.5, fontweight='bold', va='bottom', transform=ax2.transAxes,
             linespacing=1.3)
    save_main(fig, 'Fig1', OUTDIR)
    source_data('Fig1', {'c_design_runs': pd.DataFrame(table), 'c_archive_totals': pd.DataFrame(
        [dict(benchmark=BENCH_LABEL[b], tasks=inv[b]['tasks'], runs=inv[b]['runs'], agent_traces=inv[b]['traces'],
              galaxy_analysis_jobs=inv[b]['nonfetch_jobs'], galaxy_interface_calls=inv[b]['mcp_calls']) for b in BENCH])})


# =====================================================================================================
IWC_TASK = {'Short-read QC': 'Short-read quality control', 'RNA-seq DE': 'RNA-seq differential expression',
            'ATAC-seq peaks': 'ATAC-seq chromatin accessibility', 'AMR detection': 'Antimicrobial-resistance genes',
            'Pseudobulk DE': 'Pseudobulk differential expression', 'BioProject retrieval': 'BioProject metadata retrieval',
            'Peptide verification': 'Peptide verification', 'Amplicon denoising': 'Amplicon denoising',
            'Mitogenome assembly': 'Mitochondrial genome assembly', 'Host-read removal': 'Host-read removal'}


def fig2():
    import collections
    import gzip
    fig = plt.figure(figsize=(W_DOUBLE, 170 * MM))
    sd = {}
    # ================= a-c: one representation for all three benchmarks =================
    # Rows are the same configurations in the same order in every panel (labels written once, on the left).
    # Left half of each panel: the benchmark's own score; open-ended code on the upper sub-row, Galaxy on the lower
    # sub-row, one symbol per replicate and a tick for their mean. Right half: Galaxy minus open-ended code with its
    # 95% confidence interval.
    ROWS = [('GPT-5.5', 'GPT-5.5'), ('GPT-5.6 Sol', 'GPT-5.6 Sol'), ('GPT-5.6 Luna', 'GPT-5.6 Luna'), ('DeepSeek V4 Pro', 'DeepSeek V4 Pro'),
            ('pooled', 'Four configurations,\npooled (Codex harness)'), (SUPERSEDED, 'DeepSeek V4 Pro, Claude Code\nharness (superseded)')]
    YROW = [0, 1, 2, 3, 4.3, 5.75]
    OFF = {'open_ended_code': -0.21, 'galaxy': 0.21}
    MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
             'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'deepseek_v4_pro_via_claude_code_superseded': SUPERSEDED}
    reps = {b: collections.defaultdict(list) for b in BENCH}      # (row, env) -> [(value, filled)]
    diffs = {b: {} for b in BENCH}                               # row -> (estimate, low, high) ; low/high None = no interval
    # BixBench-Verified-50: replicate acceptance (% of 50 tasks), from the per-run evaluator scores
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
    for c, rr in list(fa.items()):  # archive check: replicate totals reproduce the evaluator counts
        pass
    # CompBioBench: archived aggregate score vectors (answers credited, of 100); open symbol = labelled predicted
    for p in D['fig2b']:
        if p['config'] != 'GPT-6 Astra':
            reps['CompBio'][(p['config'], p['condition'])].append((p['score'], p['official']))
    # IWC: replicate mean agreement over the nine tasks scored in both environments (host removal excluded)
    iw = collections.defaultdict(list)
    for p in D['fig2d']:
        if p['task_label'] != 'Host-read removal' and p['score'] is not None:
            iw[(p['config'], p['condition'], p['replicate'])].append(p['score'])
    for (cfg, env, r), v in sorted(iw.items()):
        reps['IWC'][(cfg, env)].append((st.mean(v), True))
    fc = {r['config']: r for r in D['fig2c']}
    for key in CONFIGS:
        diffs['IWC'][key] = tuple(fc[key]['diff'])
    diffs['IWC']['pooled'] = tuple(fc['All four']['diff'])
    for b in BENCH:  # pooled row: all replicates of the four Codex configurations
        for env in ENVS:
            reps[b][('pooled', env)] = [x for c in CONFIGS for x in reps[b][(c, env)]]
    for key in CONFIGS + ['pooled']:  # CompBioBench: difference of means only (the archive computes no interval)
        m = {e: st.mean(v for v, _ in reps['CompBio'][(key, e)]) for e in ENVS}
        diffs['CompBio'][key] = (m['galaxy'] - m['open_ended_code'], None, None)
    # consistency with the archived tables
    assert abs(st.mean(v for v, _ in reps['BixBench50'][('pooled', 'galaxy')]) - 86.5) < 0.01
    for key in CONFIGS:
        assert abs(st.mean(v for v, _ in reps['IWC'][(key, 'galaxy')]) - fc[key]['galaxy_mean']) < 1e-3

    pooled = {b: {e: st.mean(v for v, _ in reps[b][('pooled', e)]) for e in ENVS} for b in BENCH}
    spec = {
        'BixBench50': dict(x0=0.165, title='BixBench-Verified-50: similar acceptance',
                           sub=f"Pooled: open-ended code {pooled['BixBench50']['open_ended_code']:.1f}%, Galaxy {pooled['BixBench50']['galaxy']:.1f}% accepted",
                           dlab='Difference in accepted answers\n(percentage points)', dlim=(-10, 23), dt=[-10, 0, 10, 20], nd=1),
        'CompBio': dict(x0=0.45, title='CompBioBench: similar aggregate scores',
                        sub=f"Pooled mean: open-ended code {pooled['CompBio']['open_ended_code']:.1f}, Galaxy {pooled['CompBio']['galaxy']:.1f} of 100",
                        dlab='Difference in aggregate score (answers of 100;\nopen points: the archive allows no interval)', dlim=(-4, 4), dt=[-4, -2, 0, 2, 4], nd=1),
        'IWC': dict(x0=0.735, title='IWC: equal or higher agreement with Galaxy',
                    sub=f"Pooled mean: open-ended code {pooled['IWC']['open_ended_code']:.3f}, Galaxy {pooled['IWC']['galaxy']:.3f}",
                    dlab='Difference in mean agreement\n(0 to 1 scale; nine tasks)', dlim=(-0.03, 0.26), dt=[0, 0.1, 0.2], nd=3)}
    rows_sd = []
    for k, b in enumerate(BENCH):
        sp = spec[b]
        axd = fig.add_axes([sp['x0'], 0.745, 0.15, 0.18])
        lx = 0.005 if k == 0 else sp['x0'] - 0.03
        panel_label(fig, lx, 0.995, 'abc'[k]); panel_title(fig, lx, 0.995, sp['title'])
        fig.text(lx + 0.018, 0.972, sp['sub'], fontsize=5.4, color=INK2, va='top')
        for j, y in enumerate(YROW):
            if j % 2 == 0:
                axd.axhspan(y - 0.47, y + 0.47, color='#f5f4f1', lw=0, zorder=0)
        axd.axhline(3.65, color=GRID, lw=0.5); axd.axhline(5.03, color=INK2, lw=0.4, ls=(0, (1, 1.5)))
        axd.set_ylim(6.3, -1.2); axd.set_yticks(YROW)
        for (key, name), y in zip(ROWS, YROW):
            if key not in diffs[b]:
                zx = (0 - sp['dlim'][0]) / (sp['dlim'][1] - sp['dlim'][0])
                axd.text(zx + 0.03, y, 'Not run with this harness', transform=axd.get_yaxis_transform(), fontsize=5.0, color=INK2,
                         ha='left', va='center', clip_on=False)
                continue
            e_, lo, hi = diffs[b][key]
            if lo is not None:
                axd.plot([lo, hi], [y, y], color=INK, lw=1.0, zorder=3)
                axd.plot(e_, y, 'o', ms=3.6, mfc=INK, mec='white', mew=0.4, zorder=4)
                txt = fmt_ci(e_, lo, hi, nd=sp['nd']).replace(' (', '\n(')
            else:
                axd.plot(e_, y, 'o', ms=3.6, mfc='white', mec=INK, mew=0.9, zorder=4)
                txt = signed(e_, sp['nd']) + '\n(no interval)'
            axd.text(1.04, y, txt, transform=axd.get_yaxis_transform(), fontsize=5.0, ha='left', va='center', linespacing=1.05)
            means = {e: st.mean(v for v, _ in reps[b][(key, e)]) for e in ENVS}
            rows_sd.append(dict(benchmark=BENCH_LABEL[b], configuration=name.replace('\n', ' '),
                                open_ended_code_mean=round(means['open_ended_code'], 4), galaxy_mean=round(means['galaxy'], 4),
                                difference_galaxy_minus_code=round(e_, 4), ci_low=lo, ci_high=hi,
                                replicates_open_ended_code='; '.join(f'{v:.4g}' for v, _ in reps[b][(key, 'open_ended_code')]),
                                replicates_galaxy='; '.join(f'{v:.4g}' for v, _ in reps[b][(key, 'galaxy')])))
        axd.axvline(0, color=INK2, lw=0.6, ls=(0, (2, 2)))
        axd.set_xlim(*sp['dlim']); axd.set_xticks(sp['dt']); axd.set_xlabel(sp['dlab']); grid_x(axd)
        if b == 'IWC':
            axd.set_xticklabels(['0', '0.1', '0.2'])
        axd.set_yticklabels([n for _, n in ROWS] if k == 0 else [], fontsize=5.3)
        axd.set_title('Galaxy minus open-ended code\n(95% confidence interval)', fontsize=5.3, fontweight='bold', loc='left', pad=2, linespacing=1.05)
        axd.text(sp['dlim'][1] * 0.03, -0.8, 'Galaxy higher →', fontsize=5.0, color=INK2, va='center', ha='left')
    sd['a-c_differences'] = pd.DataFrame(rows_sd)
    # ---- d: IWC per task, broken axis
    pts = D['fig2d']
    tasks = list(IWC_TASK)
    axl = fig.add_axes([0.215, 0.415, 0.055, 0.215]); axr = fig.add_axes([0.28, 0.415, 0.36, 0.215])
    panel_label(fig, 0.005, 0.675, 'd'); panel_title(fig, 0.005, 0.675, 'IWC: most tasks reach near-perfect agreement, and every score below 0.5 has an identified cause')
    rng = np.random.default_rng(20260925)
    for ax_ in (axl, axr):
        for i, t in enumerate(tasks):
            for env, off in [('open_ended_code', -0.19), ('galaxy', 0.19)]:
                vals = [p['score'] for p in pts if p['task_label'] == t and p['condition'] == env and p['score'] is not None]
                jit = rng.uniform(-0.07, 0.07, len(vals))
                ax_.scatter(vals, np.full(len(vals), i + off) + jit, s=5, marker=ENV_MARKER[env], color=ENV_COLOR[env], lw=0.25,
                            ec='white', zorder=3)
                if vals:
                    m = st.mean(vals)
                    ax_.plot([m, m], [i + off - 0.16, i + off + 0.16], color=INK, lw=0.8, zorder=4)
        ax_.set_ylim(len(tasks) - 0.5, -0.6)
        for i in range(len(tasks)):
            if i % 2 == 0:
                ax_.axhspan(i - 0.5, i + 0.5, color='#f5f4f1', zorder=0, lw=0)
    axl.set_xlim(-0.03, 0.45); axl.set_xticks([0, 0.2]); axl.set_xticklabels(['0', '0.2'])
    axr.set_xlim(0.80, 1.005); axr.set_xticks([0.8, 0.85, 0.9, 0.95, 1.0]); axr.set_xticklabels(['0.80', '0.85', '0.90', '0.95', '1'])
    axl.set_yticks(range(len(tasks))); axl.set_yticklabels([IWC_TASK[t] for t in tasks], fontsize=5.3); axr.set_yticks([])
    axl.spines['right'].set_visible(False); axr.spines['left'].set_visible(False)
    for ax_, xs_ in [(axl, 1), (axr, 0)]:
        ax_.plot([xs_ - 0.03, xs_ + 0.03], [-0.03, 0.03], transform=ax_.transAxes, color=INK2, lw=0.5, clip_on=False)
    axr.set_xlabel('Agreement with the workflow reference output (0 to 1; axis broken between 0.45 and 0.80)', x=0.4)
    marks = [('Pseudobulk DE', 'open_ended_code', 0.0, '1'), ('Amplicon denoising', 'open_ended_code', 0.0, '2'),
             ('Mitogenome assembly', 'open_ended_code', 0.0, '3'), ('Mitogenome assembly', 'galaxy', 0.0, '3'),
             ('Host-read removal', 'galaxy', 0.273, '4')]
    for t, env, x, lab in marks:
        i = tasks.index(t) + (-0.19 if env == 'open_ended_code' else 0.19)
        axl.text(x + 0.035, i, lab, fontsize=5.2, fontweight='bold', va='center', ha='left', zorder=5)
    key = ('Why scores fell below 0.5\n'
           '1  Open-ended code, DeepSeek V4 Pro, replicate 3: hand-written\n    multiple-testing correction was wrong\n'
           '2  Open-ended code, GPT-5.5, replicates 1 and 3: sample names\n    lost their capital letters\n'
           '3  Wrong contig submitted: GPT-5.5 replicate 1 in both\n    environments; DeepSeek V4 Pro replicate 2 in open-ended code\n'
           '4  Galaxy, GPT-5.6 Luna, replicates 1 and 3: correct BWA-MEM\n    output scored against the Bowtie2 reference (scoring artefact)')
    fig.text(0.665, 0.63, key, fontsize=5.1, va='top', ha='left', linespacing=1.22)
    axr.legend(handles=env_handles(ms=3.4) + [Line2D([], [], color=INK, lw=0.8, label='Mean of 12 replicates')], loc='lower left', ncol=3,
               fontsize=5.0, bbox_to_anchor=(0.0, 1.0))
    sd['d_IWC_runs'] = pd.DataFrame([dict(task=IWC_TASK[p['task_label']], environment=ENV_LABEL[p['condition']], configuration=p['config'],
                                          replicate=p['replicate'], agreement=p['score'])
                                     for e in ENVS for p in pts if p['condition'] == e])
    # ---- e: root causes
    ax = fig.add_axes([0.13, 0.045, 0.555, 0.225])
    panel_label(fig, 0.005, 0.33, 'e'); panel_title(fig, 0.005, 0.33, 'Most rejected BixBench-Verified-50 answers were not caused by Galaxy (246 rejected runs, each examined call by call)')
    e = D['fig2e']
    bars = [('Open-ended code:\nprimary cause', e['open_ended_code']['primary'], e['open_ended_code']['n']),
            ('Galaxy:\nprimary cause', e['galaxy']['primary'], e['galaxy']['n']),
            ('Open-ended code:\nsecondary cause', e['open_ended_code']['secondary'], sum(e['open_ended_code']['secondary'].values())),
            ('Galaxy:\nsecondary cause', e['galaxy']['secondary'], sum(e['galaxy']['secondary'].values()))]
    ypos = [0, 1, 2.4, 3.4]
    rowse = []
    for y, (lab, cnt, n) in zip(ypos, bars):
        left = 0
        for c, name, col in CAUSES:
            k = cnt.get(c, 0)
            if not k:
                continue
            ax.barh(y, k, left=left, height=0.72, color=col, ec='white', lw=0.6)
            if k >= 4:
                ax.text(left + k / 2, y, str(k), ha='center', va='center', fontsize=5.2, color='white' if col in DARK_FILL else INK)
            left += k
            rowse.append(dict(bar=lab.replace('\n', ' '), cause=name.replace('\n', ' '), runs=k))
        ax.text(left + 1.5, y, f'{n} runs', va='center', fontsize=5.2, color=INK2)
    ax.set_yticks(ypos); ax.set_yticklabels([b[0] for b in bars], fontsize=5.3); ax.set_ylim(3.95, -0.55)
    ax.set_xlim(0, 150); ax.set_xlabel('Rejected runs'); grid_x(ax)
    ax.text(104, 2.9, f"Galaxy was the primary or secondary\ncause in {e['galaxy']['platform_any']} of {e['galaxy']['n']} Galaxy rejections "
            f"({100 * e['galaxy']['platform_any'] / e['galaxy']['n']:.0f}%)", fontsize=5.3, va='center', fontweight='bold')
    axl2 = fig.add_axes([0.72, 0.045, 0.27, 0.235]); axl2.axis('off')
    for k, (c, name, col) in enumerate(CAUSES):
        yk = 0.93 - k * 0.118
        axl2.add_patch(Rectangle((0.0, yk - 0.035), 0.06, 0.07, fc=col, ec=INK2 if col == NEUTRAL_LIGHT else 'none', lw=0.3,
                                 transform=axl2.transAxes))
        axl2.text(0.09, yk, name.replace('\n', ' ') if len(name) < 38 else name, fontsize=5.1, va='center', transform=axl2.transAxes,
                  linespacing=1.1)
    conf = D['fig2e_confidence']
    axl2.text(0.0, 0.0, f"Adjudication confidence: {conf['high']} high, {conf['moderate']} moderate,\n{conf['mixed']} mixed, "
              f"{conf['unresolved']} unresolved", fontsize=5.0, color=INK2, transform=axl2.transAxes, va='bottom')
    sd['e_root_causes'] = pd.DataFrame(rowse)
    save_main(fig, 'Fig2', OUTDIR)
    source_data('Fig2', sd)


# =====================================================================================================
DIAG = {
    'Empty background after pathway intersection': 'KEGG enrichment: empty background after pathway matching',
    'Mapping table has too few columns': 'KEGG enrichment: mapping table has too few columns',
    'Empty foreground after intersection': 'KEGG enrichment: empty gene list after matching',
    'Missing factor-list element': 'DESeq2: experimental factor missing',
    'Duplicate row names or factor levels': 'DESeq2: duplicated row names or factor levels',
    'Invalid gzip magic': 'Decompression: file is not valid gzip',
    'Unrecognized or unindexable input': 'bcftools norm: input format not recognized',
    'DataFrame construction failure': 'AnnData export: table could not be built',
    'No residual degrees of freedom': 'DESeq2: no residual degrees of freedom',
    'No retained stdout/stderr': 'fastp: no error message retained',
    'Contrast names a missing factor level': 'edgeR: contrast names a missing group',
    'Count-matrix header/column mismatch': 'edgeR: count-table header mismatch',
    'Empty NCBI Entrez query': 'MitoHiFi: empty NCBI sequence query',
    'Mismatched dereplication and denoising objects': 'DADA2: mismatched intermediate objects',
    'Unset numeric filter threshold': 'decoupler: numeric filter threshold not set',
    'Protein FM-index mapping exception': 'PepQuery2: protein index error',
}
TOOL_NAME = {'xlsx2tsv': 'Spreadsheet to table', 'Cut1': 'Select columns', 'Filter1': 'Filter rows', 'kegg_ora': 'KEGG enrichment',
             'phykit_metrics': 'PhyKIT tree metrics', 'csv_to_tabular': 'CSV to table', 'filter_tabular': 'Filter table',
             'anndata_inspect': 'AnnData inspection', 'datamash_ops': 'Datamash summaries', 'upload1': 'Upload file',
             'bedtools_intersectbed': 'bedtools intersect', 'tp_awk_tool': 'Text processing (awk)', 'fastp': 'fastp read trimming',
             'dada2_mergePairs': 'DADA2 merge read pairs', 'dada2_filterAndTrim': 'DADA2 filter and trim',
             'pepquery2': 'PepQuery2 peptide search', 'pysradb_search': 'pysradb metadata search'}
UTILITY = {'xlsx2tsv', 'Cut1', 'Filter1', 'csv_to_tabular', 'filter_tabular', 'datamash_ops', 'upload1', 'tp_awk_tool'}
GALAXY_LIGHT = '#9DC3E0'
SUBST = [('ok', 'Ran as requested', NEUTRAL_LIGHT),
         ('blocked', "Values would have changed; the benchmark's check blocked submission", OI_ORANGE),
         ('executed', 'Ran with changed or dropped values', OI_PURPLE),
         ('other', 'Other failure', NEUTRAL_MID)]


def fig3():
    fig = plt.figure(figsize=(W_DOUBLE, 170 * MM))
    sd = {}
    # ---- a: operations exercised (X14), one small multiple per benchmark
    panel_label(fig, 0.005, 0.995, 'a'); panel_title(fig, 0.005, 0.995, 'Agents used every core workbench operation')
    ops = D['fig3a']
    names = {'Tool discovery': 'Tool search', 'Parameter/schema inspection': 'Tool parameter inspection',
             'History inspection': 'History inspection', 'Ordinary-tool submission requests': 'Installed-tool job submission',
             'User-defined-tool submission requests': 'User-defined-tool submission',
             'Explicit waiting/status requests': 'Explicit job-status check'}
    rowsa = []
    for k, b in enumerate(BENCH):
        ax = fig.add_axes([0.165 + k * 0.108, 0.705, 0.08, 0.215])
        vals = [100 * o['values'][k][0] / o['values'][k][1] for o in ops]
        ax.barh(range(len(ops)), vals, color=GALAXY, height=0.62)
        for i, v in enumerate(vals):
            ax.text(v + 3, i, f'{v:.0f}', va='center', fontsize=5.0)
        ax.set_ylim(len(ops) - 0.5, -0.5); ax.set_xlim(0, 100); ax.set_xticks([0, 50, 100]); grid_x(ax)
        ax.set_yticks(range(len(ops))); ax.set_yticklabels([names[o['operation']] for o in ops] if k == 0 else [])
        ax.set_title(f"{BENCH_2L[b]}\n({ops[0]['values'][k][1]:,} runs)", fontsize=5.4, fontweight='bold', loc='center')
        if k == 1:
            ax.set_xlabel('Galaxy runs using the operation (%)')
        for i, o in enumerate(ops):
            rowsa.append(dict(benchmark=BENCH_LABEL[b], operation=names[o['operation']], runs=o['values'][k][0],
                              galaxy_runs=o['values'][k][1], percent=round(vals[i], 1)))
    sd['a_operations'] = pd.DataFrame(rowsa)
    # ---- b: tool mixture
    panel_label(fig, 0.50, 0.995, 'b'); panel_title(fig, 0.50, 0.995, 'Workflow-derived tasks relied more on\ndomain-analysis tools')
    ts = D['fig3b_toolshed']
    vals = [100 * ts[b][0] / ts[b][1] for b in BENCH]
    top = D['fig3b_top']
    ax2 = fig.add_axes([0.735, 0.705, 0.25, 0.215])
    ylab, yv, ye, yc, y = [], [], [], [], []
    pos = 0
    for b in BENCH:
        for t in top[b]:
            tid = t['tool'].split('/')[0]
            ylab.append(TOOL_NAME.get(tid, tid)); yv.append(t['jobs']); ye.append(t['errors'])
            yc.append(GALAXY_LIGHT if tid in UTILITY else GALAXY); y.append(pos); pos += 1
        pos += 1.5
    ax2.barh(y, yv, color=yc, height=0.75)
    ax2.barh(y, ye, color='white', height=0.75, hatch='//////', ec=INK2, lw=0.3)
    ax2.set_yticks(y); ax2.set_yticklabels(ylab, fontsize=5.0); ax2.set_ylim(pos - 1.2, -1.5)
    ax2.set_xlabel('Galaxy jobs with each of the six most frequent tools'); grid_x(ax2); ax2.set_xticks([0, 200, 400, 600])
    for k, (b, v_) in enumerate(zip(BENCH, vals)):
        ax2.text(-0.42, y[6 * k] - 1.1, f'{BENCH_LABEL[b]}: {v_:.0f}% of all jobs used domain-analysis tools', transform=ax2.get_yaxis_transform(),
                 fontsize=5.2, fontweight='bold', va='center', ha='left')
    ax2.legend(handles=[Patch(fc=GALAXY, label='Domain-analysis tool'), Patch(fc=GALAXY_LIGHT, label='File or table utility'),
                        Patch(fc='white', ec=INK2, hatch='//////', label='Jobs ending in error')],
               loc='lower right', fontsize=5.0, bbox_to_anchor=(1.02, 0.0))
    sd['b_domain_tool_share'] = pd.DataFrame([dict(benchmark=BENCH_LABEL[b], domain_analysis_jobs=ts[b][0], galaxy_analysis_jobs=ts[b][1],
                                                   percent=round(v, 1)) for b, v in zip(BENCH, vals)])
    sd['b_top_tools'] = pd.DataFrame([dict(benchmark=BENCH_LABEL[b], tool=TOOL_NAME.get(t['tool'].split('/')[0], t['tool']), galaxy_tool_id=t['tool'],
                                           tool_class='file or table utility' if t['tool'].split('/')[0] in UTILITY else 'domain analysis',
                                           jobs=t['jobs'], jobs_in_error=t['errors']) for b in BENCH for t in top[b]])
    # ---- c: UDT use by configuration (X12)
    ax = fig.add_axes([0.20, 0.385, 0.25, 0.205])
    panel_label(fig, 0.005, 0.665, 'c'); panel_title(fig, 0.005, 0.665, 'Use of user-defined tools depends on the model')
    rows_ = [r for r in D['fig3c'] if r['benchmark'] in ('BixBench50', 'CompBio') and r['config'] != 'All configurations']
    labels, req, ok, yy, rowsc = [], [], [], [], []
    pos = 0
    for b in ['BixBench50', 'CompBio']:
        for r in [r for r in rows_ if r['benchmark'] == b]:
            n, d = r['requesting']
            cfg = r['config'].replace(' 0813 (Codex)', '').replace(' (Codex)', '')
            labels.append(CFG_LABEL.get(cfg, cfg).replace('\nClaude Code harness\n', ' Claude\nCode harness ') if cfg == SUPERSEDED else cfg)
            req.append(100 * n / d); ok.append(100 * (r['linked_success'] or 0) / d); yy.append(pos); pos += 1
            rowsc.append(dict(benchmark=BENCH_LABEL[b], configuration=cfg, runs_requesting=n, runs_with_transcripts=d,
                              runs_with_linked_job=r['linked'][0], runs_with_successful_job=r['linked_success']))
        pos += 0.9
    ax.barh(yy, req, color=GALAXY_LIGHT, height=0.72, label='Runs that requested a user-defined tool (agent-written code run as a Galaxy tool)')
    ax.barh(yy, ok, color=GALAXY, height=0.38, label='Runs with at least one successful user-defined-tool job')
    for y_, v in zip(yy, req):
        ax.text(v + 1.5, y_, f'{v:.0f}%', va='center', fontsize=5.0)
    ax.set_yticks(yy); ax.set_yticklabels(labels, fontsize=5.1); ax.set_xlim(0, 100)
    ax.set_xlabel('Galaxy runs (%)'); grid_x(ax)
    for b, i0, i1 in [('BixBench-Verified-50', yy[0], yy[4]), ('CompBioBench', yy[5], yy[8])]:
        ax.plot([-0.62, -0.62], [i0 - 0.3, i1 + 0.3], transform=ax.get_yaxis_transform(), color=INK2, lw=0.6, clip_on=False)
        ax.text(-0.66, (i0 + i1) / 2, b, transform=ax.get_yaxis_transform(), rotation=90, va='center', ha='center', fontsize=5.2,
                fontweight='bold')
    ax.legend(loc='lower left', fontsize=5.0, bbox_to_anchor=(-0.75, 1.0), ncol=1)
    ax.text(0.99, yy[4] + 0.95, 'IWC: facility not offered (0 of 120 runs)', transform=ax.get_yaxis_transform(), fontsize=5,
            color=INK2, ha='right', va='center')
    ax.set_ylim(yy[-1] + 0.6, -0.7)
    sd['c_user_defined_tools'] = pd.DataFrame(rowsc)
    # ---- d: recurring diagnostics (X18)
    ax = fig.add_axes([0.80, 0.385, 0.125, 0.215])
    panel_label(fig, 0.50, 0.665, 'd'); panel_title(fig, 0.50, 0.665, 'Recorded errors point to inputs and parameters,\nnot to missing software')
    dd = sorted(D['fig3d'], key=lambda r: (BENCH.index(r['benchmark']), -r['n'][0]))
    labs = [DIAG.get(r['diagnostic'], r['family'] + ': ' + r['diagnostic']) for r in dd]
    pct = [100 * r['n'][0] / r['n'][1] for r in dd]
    yd = np.arange(len(dd))
    ax.barh(yd, pct, color=GALAXY, height=0.66)
    for i, r in enumerate(dd):
        ax.text(pct[i] + 2, i, f"{r['n'][0]}/{r['n'][1]}", va='center', fontsize=5.0)
    ax.set_yticks(yd); ax.set_yticklabels(labs, fontsize=5.0); ax.set_ylim(len(dd) - 0.5, -0.5)
    ax.set_xlim(0, 130); ax.set_xticks([0, 50, 100])
    ax.set_xlabel("Share of the tool's error jobs (%)"); grid_x(ax)
    for b in BENCH:
        idx = [i for i, r in enumerate(dd) if r['benchmark'] == b]
        ax.plot([1.04, 1.04], [idx[0] - 0.35, idx[-1] + 0.35], transform=ax.get_yaxis_transform(), color=INK2, lw=0.6, clip_on=False)
        ax.text(1.07, (idx[0] + idx[-1]) / 2, {'BixBench50': 'BixBench-\nVerified-50', 'CompBio': 'CompBio-\nBench', 'IWC': 'IWC'}[b],
                transform=ax.get_yaxis_transform(), va='center', ha='left', fontsize=5.0, fontweight='bold')
    fig.text(0.52, 0.605, 'Numbers: error jobs with this message / all error jobs of that tool', fontsize=5.0, color=INK2, va='bottom')
    sd['d_diagnostics'] = pd.DataFrame([dict(benchmark=BENCH_LABEL[r['benchmark']], tool_family=r['family'], diagnostic=DIAG.get(r['diagnostic'], r['diagnostic']),
                                             matching_error_jobs=r['n'][0], tool_error_jobs=r['n'][1]) for r in dd])
    # ---- e: silent parameter substitution
    ax = fig.add_axes([0.155, 0.05, 0.385, 0.15])
    panel_label(fig, 0.005, 0.325, 'e'); panel_title(fig, 0.005, 0.325, 'Galaxy silently changed requested parameter values in 16–30% of tool runs')
    scan = D['scan']
    rowse = []
    for i, b in enumerate(BENCH):
        stt = scan['runtool_status'][b]
        tot = sum(stt.values())
        vals = dict(ok=stt.get('ok', 0), blocked=stt.get('validation_parameter_mismatch', 0), executed=stt.get('parameter_mismatch', 0))
        vals['other'] = tot - sum(vals.values())
        left = 0
        for key, lab, col in SUBST:
            v = 100 * vals[key] / tot
            ax.barh(i, v, left=left, color=col, height=0.66, ec='white', lw=0.6)
            if key in ('blocked', 'executed') and v >= 4:
                ax.text(left + v / 2, i, f'{vals[key]:,}', ha='center', va='center', fontsize=5.0, color=INK if key == 'blocked' else 'white')
            left += v
            rowse.append(dict(benchmark=BENCH_LABEL[b], outcome=lab, calls=vals[key], tool_run_calls=tot, percent=round(v, 1)))
        mis = vals['blocked'] + vals['executed']
        ax.text(101.5, i, f'{100 * mis / tot:.0f}% changed\n({mis:,} of {tot:,})', va='center', fontsize=5.0)
    ax.set_yticks(range(3)); ax.set_yticklabels([BENCH_LABEL[b] for b in BENCH]); ax.set_ylim(2.5, -0.5)
    ax.set_xlim(0, 100); ax.set_xlabel('Tool-run calls to the Galaxy interface (%)'); grid_x(ax)
    ax.legend(handles=[Patch(fc=c, label=l) for _, l, c in SUBST], loc='lower left', bbox_to_anchor=(-0.02, 1.02), ncol=1, fontsize=5.0)
    sd['e_substitution'] = pd.DataFrame(rowse)
    axt = fig.add_axes([0.635, 0.04, 0.355, 0.245]); axt.axis('off')
    ex = [('Datamash', 'operation', 'max', 'count'), ('Datamash', 'column number', '6', '1'),
          ('PhyKIT metrics', 'metric', 'treeness', 'total tree length'), ('STAR-Fusion', 'genome', 'human (hg38)', 'honey bee (apiMel4)'),
          ('STAR-Fusion', 'read layout', 'paired-end', 'single-end'), ('Unzip', 'files to extract', 'matching pattern', 'all files'),
          ('DESeq2', 'factor level', 'DMSO', 'FactorLevel')]
    axt.text(0.0, 1.0, 'Examples: value requested by the agent\nand value Galaxy actually used', fontsize=5.5, fontweight='bold', va='top',
             transform=axt.transAxes)
    hdr = ['Tool', 'Parameter', 'Requested', 'Used by Galaxy']
    xs = [0.0, 0.235, 0.465, 0.695]
    for x, h in zip(xs, hdr):
        axt.text(x, 0.84, h, fontsize=5.1, color=INK2, va='top', transform=axt.transAxes, fontweight='bold')
    axt.plot([0, 1], [0.79, 0.79], color=INK2, lw=0.4, transform=axt.transAxes)
    for k, row in enumerate(ex):
        yk = 0.745 - k * 0.105
        for x, val in zip(xs, row):
            axt.text(x, yk, val, fontsize=5.0, va='top', transform=axt.transAxes)
    axt.plot([0, 1], [0.0, 0.0], color=INK2, lw=0.4, transform=axt.transAxes)
    sd['e_examples'] = pd.DataFrame(ex, columns=hdr)
    sd['e_all_detected_substitutions'] = pd.DataFrame(scan['mismatch_examples'], columns=['benchmark', 'task', 'tool', 'parameter',
                                                                                           'requested', 'resolved'])
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


def fig4():
    fig = plt.figure(figsize=(W_DOUBLE, 170 * MM))
    sd = {}
    # ---- a: software families heatmap (X9), open-ended code first
    ax = fig.add_axes([0.12, 0.60, 0.345, 0.30])
    panel_label(fig, 0.005, 0.995, 'a'); panel_title(fig, 0.005, 0.995, 'Open-ended-code runs spread across more command-line\nsoftware than Galaxy runs')
    fam = D['fig4a_families']
    order_idx = [1, 0, 3, 2, 5, 4]  # archive order is Galaxy, code per benchmark; show code first
    mat = np.array([[100 * f['values'][j][0] / f['values'][j][1] for j in order_idx] for f in fam])
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list('greys_n', ['#f7f6f3', '#bdbcb6', '#6f6e69', '#262624'])
    ax.imshow(mat, cmap=cmap, vmin=0, vmax=45, aspect='auto')
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            ax.text(j, i, f'{v:.0f}' if v >= 0.5 else '·', ha='center', va='center', fontsize=5.0, color='white' if v > 22 else INK)
    fname = {'DESeq2 / PyDESeq2': 'DESeq2 or PyDESeq2', 'MACS2 / MACS3': 'MACS2 or MACS3'}
    ax.set_yticks(range(len(fam))); ax.set_yticklabels([fname.get(f['family'], f['family']) for f in fam], fontsize=5.3)
    ax.set_xticks(range(6)); ax.set_xticklabels(['Open-ended\ncode', 'Galaxy'] * 3, fontsize=5.0); ax.tick_params(length=0)
    ax.xaxis.tick_top()
    for s in ax.spines.values():
        s.set_visible(False)
    for k, b in enumerate(BENCH):
        ax.text(2 * k + 0.5, -2.05, BENCH_LABEL[b], ha='center', fontsize=5.5, fontweight='bold')
        ax.plot([2 * k - 0.4, 2 * k + 1.4], [-1.85, -1.85], color=INK, lw=0.6, clip_on=False)
    for x in (1.5, 3.5):
        ax.axvline(x, color='white', lw=1.5)
    ax.text(0.5, -0.02, 'Cell value: % of runs using the software (three GPT configurations shared by all benchmarks).\n'
            'Open-ended code: software named in shell commands. Galaxy: installed tools in job records.',
            transform=ax.transAxes, ha='center', fontsize=5.0, color=INK2, va='top')
    cols = [f'{BENCH_LABEL[b]}, {ENV_LABEL[e]}' for b in BENCH for e in ENVS]
    sd['a_software_families'] = pd.DataFrame([dict(software=f['family'], **{c: f"{f['values'][j][0]}/{f['values'][j][1]}"
                                                                           for c, j in zip(cols, order_idx)}) for f in fam])
    # ---- b: Jaccard by configuration and benchmark
    ax = fig.add_axes([0.60, 0.625, 0.24, 0.28])
    panel_label(fig, 0.51, 0.995, 'b'); panel_title(fig, 0.51, 0.995, 'Replicate tool sets in Galaxy agree most on\nworkflow-derived tasks')
    jb = D['fig4b']
    markers = ['o', 's', '^', 'D']
    rowsb = []
    endy = {}
    for m_, cfg in zip(markers, CONFIGS):
        ys = [[r['jaccard'] for r in jb[b] if r['config'] == cfg][0] for b in BENCH]
        for b, v_ in zip(BENCH, ys):
            rowsb.append(dict(benchmark=BENCH_LABEL[b], configuration=cfg, mean_pairwise_jaccard=v_))
        ax.plot(range(3), ys, color=INK2, lw=0.6, zorder=1)
        ax.scatter(range(3), ys, marker=m_, s=16, color=INK, ec='white', lw=0.4, zorder=3)
        endy[cfg] = ys[2]
    lab_y = {'GPT-5.5': 0.72, 'DeepSeek V4 Pro': 0.645, 'GPT-5.6 Luna': 0.585, 'GPT-5.6 Sol': 0.535}
    for m_, cfg in zip(markers, CONFIGS):
        ax.plot([2.06, 2.14], [endy[cfg], lab_y[cfg]], color=GRID, lw=0.5)
        ax.scatter([2.2], [lab_y[cfg]], marker=m_, s=10, color=INK, zorder=3)
        ax.text(2.28, lab_y[cfg], cfg, va='center', fontsize=5.2)
    ax.set_xticks(range(3)); ax.set_xticklabels([BENCH_2L[b] for b in BENCH]); ax.set_xlim(-0.3, 2.3)
    ax.set_ylim(0, 0.8); ax.set_ylabel('Similarity of tool sets between replicates\n(mean pairwise Jaccard index; 1 = identical)'); grid_y(ax)
    for sp in ('right',):
        ax.spines[sp].set_visible(False)
    sd['b_jaccard'] = pd.DataFrame(rowsb)
    # ---- c: mixed cells
    panel_label(fig, 0.005, 0.525, 'c'); panel_title(fig, 0.005, 0.525, 'Galaxy produced fewer non-unanimous triplicates than open-ended code in every benchmark')
    mc = D['fig4c']
    denom = {'BixBench50': 50, 'CompBio': D['compbio_strong_tasks'], 'IWC': 10}
    rowsc = []
    for k, b in enumerate(BENCH):
        ax = fig.add_axes([0.135 + k * 0.335, 0.30, 0.17, 0.14])
        cl = CONFIGS + ([SUPERSEDED] if b == 'BixBench50' else [])
        y = np.arange(len(cl))
        cc = [mc[f'{b}|open_ended_code'].get(c, 0) for c in cl]; g = [mc[f'{b}|galaxy'].get(c, 0) for c in cl]
        ax.barh(y - 0.2, cc, height=0.38, color=CODE)
        ax.barh(y + 0.2, g, height=0.38, color=GALAXY)
        for yi, cv, gv in zip(y, cc, g):
            ax.text(cv + 0.25, yi - 0.2, str(cv), va='center', fontsize=5.0)
            ax.text(gv + 0.25, yi + 0.2, str(gv), va='center', fontsize=5.0)
        ax.set_yticks(y); ax.set_yticklabels(['DeepSeek V4 Pro, Claude\nCode harness (superseded)' if c == SUPERSEDED else c for c in cl],
                                             fontsize=5.1)
        ax.set_ylim(len(cl) - 0.5, -0.6); ax.set_xlim(0, max(g + cc) * 1.22 + 1); grid_x(ax)
        ax.set_title(f'{BENCH_LABEL[b]}: open-ended code {sum(cc)}, Galaxy {sum(g)}', fontsize=5.6, loc='left', x=-0.05)
        ax.set_xlabel(f'Non-unanimous triplicates\n(of {denom[b]} tasks per configuration)', fontsize=5.3)
        for c, cv, gv in zip(cl, cc, g):
            rowsc.append(dict(benchmark=BENCH_LABEL[b], configuration=c, open_ended_code=cv, galaxy=gv, tasks_per_configuration=denom[b]))
    fig.legend(handles=env_patches(), loc='upper right', bbox_to_anchor=(0.99, 0.527), ncol=2, fontsize=5.2)
    fig.text(0.023, 0.505, 'A triplicate is one task run three times with one configuration in one environment; it is non-unanimous when 1 or 2 of '
             'the 3 replicates succeeded (BixBench-Verified-50: accepted by the evaluator;\nCompBioBench: matched the answer given by at least 20 '
             'of 25 runs, 82 tasks; IWC: replicate scores differed by more than 0.05).', fontsize=5.0, color=INK2, va='top')
    sd['c_non_unanimous_triplicates'] = pd.DataFrame(rowsc)
    # ---- d: divergence mechanisms
    ax = fig.add_axes([0.135, 0.04, 0.52, 0.09])
    panel_label(fig, 0.005, 0.215, 'd'); panel_title(fig, 0.005, 0.215, 'Replicates diverged for different reasons in each environment (BixBench-Verified-50)')
    md = D['fig4d']
    rowsd = []
    share = {}
    for i, env in enumerate(ENVS):
        tot = sum(md[env].values()); left = 0
        for key, name, col in MECH:
            v = md[env].get(key, 0)
            if not v:
                continue
            w = 100 * v / tot
            ax.barh(i, w, left=left, color=col, height=0.66, ec=INK2 if key in HATCH else 'white', lw=0.6, hatch=HATCH.get(key))
            if w >= 5:
                ax.text(left + w / 2, i, str(v), ha='center', va='center', fontsize=5.0, color='white' if col in DARK_FILL else INK,
                        bbox=dict(boxstyle='round,pad=0.1', fc=col, ec='none') if key in HATCH else None)
            left += w
            rowsd.append(dict(environment=ENV_LABEL[env], mechanism=name.replace('\n', ' '), rejected_replicates=v, total=tot, percent=round(w, 1)))
        share[env] = 100 * (md[env].get('V5', 0) + md[env].get('V3', 0)) / tot
        ax.text(101, i, f'{tot} rejected\nreplicates', va='center', fontsize=5.0, color=INK2)
    ax.set_yticks([0, 1]); ax.set_yticklabels([ENV_LABEL[e] for e in ENVS]); ax.set_ylim(1.5, -0.5); ax.set_xlim(0, 100)
    ax.set_xlabel('Rejected replicates in non-unanimous triplicates (%)'); grid_x(ax)
    trap = 100 * md['galaxy'].get('V1', 0) / sum(md['galaxy'].values())
    fig.text(0.023, 0.19, f"Hand-written methods and software-version differences: {share['open_ended_code']:.0f}% of open-ended-code divergences, "
             f"{share['galaxy']:.0f}% of Galaxy divergences. Galaxy interface traps: {trap:.0f}% of Galaxy divergences, none in open-ended code.",
             fontsize=5.3)
    axl = fig.add_axes([0.745, 0.02, 0.25, 0.15]); axl.axis('off')
    for k, (key, name, col) in enumerate(MECH):
        yk = 0.95 - k * 0.14
        axl.add_patch(Rectangle((0.0, yk - 0.045), 0.06, 0.09, fc=col, ec=INK2 if key in HATCH or col == NEUTRAL_LIGHT else 'none',
                                lw=0.3, hatch=HATCH.get(key), transform=axl.transAxes))
        axl.text(0.085, yk, name, fontsize=5.0, va='center', transform=axl.transAxes, linespacing=1.05)
    sd['d_divergence_mechanisms'] = pd.DataFrame(rowsd)
    save_main(fig, 'Fig4', OUTDIR)
    source_data('Fig4', sd)


# =====================================================================================================
LABPOS = {  # (environment, configuration): (x factor, y offset, ha) for direct labels in Fig. 5c
    ('galaxy', 'GPT-5.6 Sol'): (1.05, 1.2, 'left'), ('open_ended_code', 'GPT-5.6 Sol'): (0.99, -1.7, 'left'),
    ('galaxy', 'GPT-5.6 Luna'): (1.05, 1.3, 'left'), ('open_ended_code', 'GPT-5.6 Luna'): (1.05, 1.3, 'left'),
    ('galaxy', 'DeepSeek V4 Pro (Codex)'): (0.97, -1.6, 'right'), ('open_ended_code', 'DeepSeek V4 Pro (Codex)'): (1.05, -1.7, 'left'),
    ('galaxy', SUPERSEDED): (0.95, -1.9, 'right'), ('open_ended_code', SUPERSEDED): (1.06, -1.8, 'left')}


def fig5():
    fig = plt.figure(figsize=(W_DOUBLE, 155 * MM))
    sd = {}
    # ---- a: token ratios
    ax = fig.add_axes([0.10, 0.575, 0.36, 0.33])
    panel_label(fig, 0.005, 0.995, 'a'); panel_title(fig, 0.005, 0.995, 'Galaxy used 4–5 times more input tokens on platform-\nneutral tasks, and 1.9 times more on IWC tasks')
    rng = np.random.default_rng(7)
    rowsa = []
    for k, b in enumerate(BENCH):
        r = [p['ratio'] for p in D['fig5a'] if p['benchmark'] == b]
        ax.scatter(k + rng.uniform(-0.18, 0.18, len(r)), r, s=4, color=NEUTRAL_MID, lw=0.2, ec='white', zorder=2)
        med, lo, hi = D['fig5a_summary'][b]
        ax.plot([k + 0.29, k + 0.29], [lo, hi], color=INK, lw=0.9, zorder=3)
        ax.plot(k + 0.29, med, 'o', ms=3.5, mfc=INK, mec='white', mew=0.5, zorder=4)
        above = sum(v > 1 for v in r)
        ax.text(k, 1500, f'Median {med:.2f}\n({lo:.2f} to {hi:.2f})\nGalaxy higher in\n{above} of {len(r)} pairs', ha='center', fontsize=5.0,
                va='top')
        rowsa += [dict(benchmark=BENCH_LABEL[b], configuration=p['config'], galaxy_over_code_ratio=p['ratio'])
                  for p in D['fig5a'] if p['benchmark'] == b]
    ax.axhline(1, color=INK2, lw=0.5, ls=(0, (2, 2)))
    ax.text(-0.47, 0.9, 'Equal use', fontsize=5.0, color=INK2, ha='left', va='top')
    ax.set_yscale('log'); ax.set_ylim(0.08, 2000); ax.spines['left'].set_bounds(0.08, 150)
    ax.set_yticks([0.1, 1, 10, 100]); ax.set_yticklabels(['0.1', '1', '10', '100'])
    ax.set_yticks([m * 10 ** e for e in (-1, 0, 1) for m in range(2, 10)] + [0.09], minor=True)
    ax.set_xticks(range(3)); ax.set_xticklabels([BENCH_2L[b] for b in BENCH]); ax.set_xlim(-0.5, 2.65)
    ax.set_ylabel('Input tokens, Galaxy ÷ open-ended code\n(same task and configuration; log scale)'); grid_y(ax)
    ax.legend(handles=[Line2D([], [], marker='o', ls='', mfc=NEUTRAL_MID, mec='white', ms=3, label='One task and configuration'),
                       Line2D([], [], marker='o', ls='-', color=INK, mfc=INK, mec='white', ms=3.5, lw=0.9,
                              label='Median with 95% confidence interval')], loc='lower left', bbox_to_anchor=(0.0, 1.0),
              ncol=2, fontsize=5.0)
    sd['a_token_ratios'] = pd.DataFrame(rowsa)
    # ---- b: discovery share
    ax = fig.add_axes([0.58, 0.62, 0.40, 0.285])
    panel_label(fig, 0.51, 0.995, 'b'); panel_title(fig, 0.51, 0.995, 'Finding and inspecting tools took about half of the\nGalaxy interface activity')
    rowsb = []
    for k, b in enumerate(BENCH):
        for j, (key, lab) in enumerate([('calls', 'Share of Galaxy interface calls'), ('chars', 'Share of text returned to the agent')]):
            v = np.array(D['fig5b'][b][key]) * 100
            pos = k * 2.6 + j
            bp = ax.boxplot(v, positions=[pos], widths=0.6, patch_artist=True, showfliers=False,
                            medianprops=dict(color=INK, lw=0.9), whiskerprops=dict(lw=0.5, color=INK2),
                            capprops=dict(lw=0.5, color=INK2), boxprops=dict(lw=0.5, ec=INK2))
            bp['boxes'][0].set_facecolor(GALAXY if j == 0 else 'white')
            if j == 1:
                bp['boxes'][0].set_hatch('//////'); bp['boxes'][0].set_edgecolor(GALAXY)
            ax.text(pos, 103, f'{np.median(v):.0f}%', ha='center', fontsize=5.0)
            rowsb.append(dict(benchmark=BENCH_LABEL[b], measure=lab, median_percent=round(float(np.median(v)), 1),
                              q1=round(float(np.percentile(v, 25)), 1), q3=round(float(np.percentile(v, 75)), 1), runs=len(v)))
        insp = D['scan']['inspected'][b]; never = D['scan']['inspected_never_run'][b]
        ax.text(k * 2.6 + 0.5, -20, f'{never:,} of {insp:,} inspected\ntools were never run', ha='center', fontsize=5.0, va='top', color=INK2)
    ax.set_xticks([k * 2.6 + 0.5 for k in range(3)]); ax.set_xticklabels([BENCH_LABEL[b] for b in BENCH])
    ax.set_ylim(0, 110); ax.set_ylabel('Share spent on tool search and\ninspection (% per Galaxy run)'); grid_y(ax)
    ax.legend(handles=[Patch(fc=GALAXY, ec=INK2, label='Share of Galaxy interface calls'),
                       Patch(fc='white', ec=GALAXY, hatch='//////', label='Share of text returned to the agent')],
              loc='lower left', bbox_to_anchor=(0.0, 1.03), ncol=1, fontsize=5.0)
    ax.text(1.0, 1.04, 'Box: middle 50% of runs; line: median;\nwhiskers: 1.5 × interquartile range', transform=ax.transAxes,
            fontsize=5.0, color=INK2, ha='right', va='bottom')
    sd['b_tool_search_share'] = pd.DataFrame(rowsb)
    # ---- c: token ratio and acceptance relative to GPT-5.5 (B15), as two aligned forest plots
    panel_label(fig, 0.005, 0.49, 'c'); panel_title(fig, 0.005, 0.49, 'Configurations that used more input tokens were not\nmore accurate (BixBench-Verified-50, relative to GPT-5.5)')
    axt = fig.add_axes([0.17, 0.10, 0.12, 0.305]); axa = fig.add_axes([0.345, 0.10, 0.12, 0.305])
    recs = {(('galaxy' if r['env'] == 'Galaxy' else 'open_ended_code'), r['config']): r for r in D['fig5c']}
    cfgs = ['GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro (Codex)', SUPERSEDED]
    ylab = {'GPT-5.6 Sol': 'GPT-5.6 Sol', 'GPT-5.6 Luna': 'GPT-5.6 Luna', 'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro',
            SUPERSEDED: 'DeepSeek V4 Pro, Claude\nCode harness (superseded)'}
    ys, labels, rowsc = [], [], []
    y = 0
    for env in ENVS:
        axt.text(-0.02, y, ENV_LABEL[env], transform=axt.get_yaxis_transform(), ha='right', va='center', fontsize=5.4, fontweight='bold')
        y += 1
        for cfg in cfgs:
            r = recs[(env, cfg)]
            (a_, al, ah), (t, tl, th) = r['acc_diff'], r['token_ratio']
            for ax_, (e_, lo_, hi_) in ((axt, (t, tl, th)), (axa, (a_, al, ah))):
                ax_.plot([lo_, hi_], [y, y], color=ENV_COLOR[env], lw=0.9)
                dot(ax_, e_, y, env, ms=3.6)
            axt.text(1.02, y, f'{t:.2f}', transform=axt.get_yaxis_transform(), fontsize=5.0, va='center')
            axa.text(1.02, y, signed(a_, 1), transform=axa.get_yaxis_transform(), fontsize=5.0, va='center')
            ys.append(y); labels.append(ylab[cfg])
            rowsc.append(dict(environment=ENV_LABEL[env], configuration=cfg, input_token_ratio=t, token_ci_low=tl, token_ci_high=th,
                              acceptance_difference_pp=a_, acc_ci_low=al, acc_ci_high=ah))
            y += 1
        y += 0.4
    for ax_ in (axt, axa):
        ax_.set_ylim(y - 0.6, -0.7); grid_x(ax_)
    axt.set_yticks(ys); axt.set_yticklabels(labels, fontsize=5.1); axa.set_yticks(ys); axa.set_yticklabels([])
    axt.axvline(1, color=INK2, lw=0.5, ls=(0, (2, 2))); axa.axvline(0, color=INK2, lw=0.5, ls=(0, (2, 2)))
    axt.set_xscale('log'); axt.set_xlim(0.8, 7); axt.set_xticks([1, 2, 4]); axt.set_xticklabels(['1', '2', '4'])
    axt.xaxis.set_minor_locator(plt.NullLocator())
    axa.set_xlim(-31, 7); axa.set_xticks([-30, -20, -10, 0])
    axt.set_xlabel('Input tokens relative to\nGPT-5.5 (ratio; log scale)')
    axa.set_xlabel('Accepted answers relative\nto GPT-5.5 (percentage points)')
    axt.set_title('More tokens →', fontsize=5.2, loc='right', fontweight='normal', color=INK2)
    axa.set_title('← Less accurate', fontsize=5.2, loc='left', fontweight='normal', color=INK2)
    fig.text(0.17, 0.006, 'Lines: 95% confidence intervals. Dashed lines: GPT-5.5 in the same environment.', fontsize=5.0, color=INK2)
    sd['c_tokens_vs_accuracy'] = pd.DataFrame(rowsc)
    # ---- d: what the record made recoverable
    axd = fig.add_axes([0.52, 0.06, 0.35, 0.385]); axd.axis('off')
    panel_label(fig, 0.51, 0.49, 'd'); panel_title(fig, 0.51, 0.49, 'What the Galaxy record made recoverable')
    items = [('Tool version', 'A version-dependent reference (bix-45-q1):\ncurrent PhyKIT reproduces the Galaxy value;\nPhyKIT 2.0.3 the accepted value'),
             ('Resolved\nparameters', '916 jobs ran with changed or dropped values;\n3,436 more were blocked before submission'),
             ('Tool output', 'A tool returned a sample variance where the\nagent expected a median (bix-28-q3)'),
             ('Scoring route', 'Correct BWA-MEM output (20,899 read pairs)\nscored against the Bowtie2 reference\n(72,867 read pairs)'),
             ('Per-replicate\ntrace', 'Why each rejected replicate diverged\n(45 open-ended code, 36 Galaxy)'),
             ('Server state', 'Missing tool scripts (15 jobs), a silent empty\nconversion, rate-limit messages returned\nas web pages')]
    for k, (tag, txt) in enumerate(items):
        y = 0.99 - k * 0.165
        axd.add_patch(FancyBboxPatch((0.0, y - 0.125), 0.25, 0.125, boxstyle='round,pad=0,rounding_size=0.01', fc=ENV_TINT['galaxy'],
                                     ec=GALAXY, lw=0.5, transform=axd.transAxes))
        axd.text(0.125, y - 0.0625, tag, ha='center', va='center', fontsize=5.1, fontweight='bold', transform=axd.transAxes, linespacing=1.1)
        axd.text(0.28, y - 0.0625, txt, va='center', fontsize=5.0, transform=axd.transAxes, linespacing=1.15)
    axb = fig.add_axes([0.915, 0.12, 0.075, 0.26])
    md = D['fig4d']
    c = 100 * (md['open_ended_code'].get('V5', 0) + md['open_ended_code'].get('V3', 0)) / sum(md['open_ended_code'].values())
    g = 100 * (md['galaxy'].get('V5', 0) + md['galaxy'].get('V3', 0)) / sum(md['galaxy'].values())
    axb.bar([0, 1], [c, g], color=[CODE, GALAXY], width=0.65)
    for i, v in enumerate([c, g]):
        axb.text(i, v + 2, f'{v:.0f}%', ha='center', fontsize=5.2)
    axb.set_xticks([0, 1]); axb.set_xticklabels(['Open-\nended\ncode', 'Galaxy'], fontsize=5.0); axb.set_ylim(0, 85)
    axb.set_ylabel('Divergent rejected replicates caused by\nhand-written methods or software-version\ndifferences (%)', fontsize=5.0)
    grid_y(axb)
    sd['d_recoverable_findings'] = pd.DataFrame([dict(record_element=t.replace('\n', ' '), finding=x.replace('\n', ' ')) for t, x in items] +
                                                [dict(record_element='Divergence source', finding=f'open-ended code {c:.1f}%; Galaxy {g:.1f}%')])
    save_main(fig, 'Fig5', OUTDIR)
    source_data('Fig5', sd)


if __name__ == '__main__':
    which = sys.argv[1:] or ['1', '2', '3', '4', '5']
    for w in which:
        globals()[f'fig{w}']()
        print('done Fig', w)
