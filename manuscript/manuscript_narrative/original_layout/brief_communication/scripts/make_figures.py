#!/usr/bin/env python3
"""Figures 1 and 2 of the Brief Communication, to Nature Methods specifications (180 mm wide, 5-7 pt Arial, 600 dpi).

Fig. 1: a, design; b-d, Galaxy - custom code by model and pooled (archive figures/fig2_source_data.csv, panel b).
Fig. 2: a, causes of incorrect BixBench-Verified-50 runs by sibling-replicate agreement
(data/bixbench_causes_by_agreement.csv); b, what each condition's record retains per analysis step
(data/inspectability_counts.csv); c, tokens per 50-task run at each interface round (archive figures/fig5_source_data.csv,
panel c). Writes figures/Fig1.{pdf,png,svg}, figures/Fig2.{pdf,png,svg} and the source data workbooks
figures/Source_Data_Fig1.xlsx and figures/Source_Data_Fig2.xlsx.
Usage: python scripts/make_figures.py
"""
import json
import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BC = os.path.dirname(HERE)
ARCHIVE = os.path.abspath(os.path.join(BC, '..', '..', '..', '..'))
FIG, DATA, OUT = os.path.join(ARCHIVE, 'figures'), os.path.join(BC, 'data'), os.path.join(BC, 'figures')
MM = 1 / 25.4
GAL, CODE, INK, INK2, GRID = '#0072B2', '#D55E00', '#1a1a1a', '#5a5a5a', '#e4e4e4'
GAL_T, CODE_T = '#e3eff7', '#fbebe0'
MODELS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro']
plt.rcParams.update({'font.family': 'Arial', 'font.size': 6, 'axes.linewidth': 0.5, 'xtick.major.width': 0.5,
                     'ytick.major.width': 0.5, 'xtick.major.size': 2, 'ytick.major.size': 2, 'axes.edgecolor': INK2,
                     'xtick.color': INK2, 'ytick.color': INK2, 'axes.labelcolor': INK, 'svg.fonttype': 'none',
                     'pdf.fonttype': 42, 'legend.frameon': False})


def letter(fig, x, y, s):
    fig.text(x, y, s, fontsize=8, fontweight='bold', color=INK, va='top', ha='left')


def clean(ax, grid='x'):
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, lw=0.4, zorder=0)
        ax.set_axisbelow(True)


def rbox(ax, x, y, w, h, fc, ec=None, lw=0.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.012', fc=fc,
                                ec=ec or fc, lw=lw, transform=ax.transAxes, clip_on=False))


def arrow(ax, x1, y1, x2, y2, color=INK2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), xycoords='axes fraction',
                arrowprops=dict(arrowstyle='-|>', color=color, lw=0.6, mutation_scale=6, shrinkA=0, shrinkB=0))


def save(fig, name):
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(os.path.join(OUT, f'{name}.{ext}'), dpi=600, facecolor='white')
    plt.close(fig)
    print('wrote', name)


# ---------------------------------------------------------------- Fig. 1
def design(ax):
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    t = dict(transform=ax.transAxes, color=INK, va='top')
    # tasks
    rbox(ax, 0.0, 0.06, 0.17, 0.86, '#f3f4f5')
    ax.text(0.012, 0.88, 'Task', fontsize=6.5, fontweight='bold', **t)
    ax.text(0.012, 0.77, '160 tasks', fontsize=6, **t)
    for i, (n, k) in enumerate([('BixBench-Verified-50', '50'), ('CompBioBench', '100'), ('IWC-derived', '10')]):
        ax.text(0.012, 0.64 - i * 0.13, n, fontsize=5.5, **t)
        ax.text(0.158, 0.64 - i * 0.13, k, fontsize=5.5, ha='right', transform=ax.transAxes, color=INK, va='top')
    ax.text(0.012, 0.22, 'Question and\ninput data', fontsize=5.5, color=INK2, transform=ax.transAxes, va='top',
            linespacing=1.15)
    arrow(ax, 0.175, 0.49, 0.205, 0.49)
    # models
    rbox(ax, 0.21, 0.06, 0.15, 0.86, '#f3f4f5')
    ax.text(0.222, 0.88, 'Same model', fontsize=6.5, fontweight='bold', **t)
    ax.text(0.222, 0.77, 'Codex agent harness', fontsize=5.5, color=INK2, transform=ax.transAxes, va='top')
    for i, m in enumerate(MODELS):
        ax.text(0.222, 0.64 - i * 0.12, m, fontsize=5.5, **t)
    arrow(ax, 0.365, 0.62, 0.395, 0.74)
    arrow(ax, 0.365, 0.36, 0.395, 0.24)
    # Galaxy lane
    rbox(ax, 0.40, 0.52, 0.43, 0.40, GAL_T, GAL)
    ax.text(0.412, 0.885, 'Galaxy', fontsize=6.5, fontweight='bold', color=GAL, transform=ax.transAxes, va='top')
    ax.text(0.465, 0.885, 'analysis runs as Galaxy jobs on usegalaxy.org', fontsize=5.5, color=INK,
            transform=ax.transAxes, va='top')
    chips = ['Tool search', 'Parameter\ndescriptions', 'History\ninspection', 'Job submission\nand monitoring',
             'User-defined\ntools (UDTs)']
    ax.text(0.412, 0.80, 'Galaxy MCP server', fontsize=5.5, color=INK2, transform=ax.transAxes, va='top')
    w = 0.077
    for i, c in enumerate(chips):
        x = 0.412 + i * (w + 0.006)
        rbox(ax, x, 0.555, w, 0.17, 'white', GAL, lw=0.5)
        ax.text(x + w / 2, 0.64, c, fontsize=5, ha='center', va='center', color=INK, transform=ax.transAxes,
                linespacing=1.1)
    # custom-code lane
    rbox(ax, 0.40, 0.06, 0.43, 0.40, CODE_T, CODE)
    ax.text(0.412, 0.425, 'Custom code', fontsize=6.5, fontweight='bold', color=CODE, transform=ax.transAxes,
            va='top')
    ax.text(0.503, 0.42, '(baseline)', fontsize=5.5, color=INK2, transform=ax.transAxes, va='top')
    ax.text(0.412, 0.30, 'The agent installs software and writes\nand runs its own code in an isolated workspace',
            fontsize=5.5, color=INK, transform=ax.transAxes, va='top', linespacing=1.2)
    arrow(ax, 0.835, 0.72, 0.865, 0.6)
    arrow(ax, 0.835, 0.26, 0.865, 0.38)
    # outputs
    rbox(ax, 0.87, 0.06, 0.13, 0.86, '#f3f4f5')
    ax.text(0.882, 0.88, '3 replicates', fontsize=6.5, fontweight='bold', **t)
    ax.text(0.882, 0.78, 'per task and\ncondition', fontsize=5.5, color=INK2, transform=ax.transAxes, va='top',
            linespacing=1.15)
    ax.text(0.882, 0.58, '3,840 runs', fontsize=6.5, fontweight='bold', **t)
    ax.text(0.882, 0.46, 'Answer scored by\neach benchmark\'s\nown rule', fontsize=5.5, color=INK2,
            transform=ax.transAxes, va='top', linespacing=1.15)
    ax.text(0.882, 0.27, 'Galaxy history:\ntools, versions,\nparameters, data', fontsize=5.5, color=GAL,
            transform=ax.transAxes, va='top', linespacing=1.15)


def fig1():
    f2 = pd.read_csv(os.path.join(FIG, 'fig2_source_data.csv'))
    b = f2[(f2.panel == 'b') & f2.measure.str.contains('mean_score_difference')]
    runs = pd.read_csv(os.path.join(FIG, 'scored_runs.csv'))
    fig = plt.figure(figsize=(180 * MM, 118 * MM))
    ax = fig.add_axes([0.035, 0.635, 0.955, 0.33])
    design(ax)
    letter(fig, 0.0, 0.985, 'a')
    bench = [('BixBench50', 'BixBench-Verified-50', 'accepted runs', 'Galaxy − custom code (percentage points)'),
             ('CompBio', 'CompBioBench', 'agreement with the answer key', 'Galaxy − custom code (percentage points)'),
             ('IWC', 'IWC-derived tasks', 'mean output agreement (0–1)', 'Galaxy − custom code (agreement)')]
    rows = MODELS + ['All four models']
    src = []
    for j, (bm, name, unit, xl) in enumerate(bench):
        ax = fig.add_axes([0.13 + j * 0.295, 0.085, 0.235, 0.34])
        g = b[b.benchmark == bm].copy()
        r = runs[runs.benchmark == bm]
        iwc = bm == 'IWC'
        if iwc:
            g[['value', 'ci95_low', 'ci95_high']] /= 100
            m = r.groupby('env').score.mean()
            vals = (f'{m.open_ended_code:.2f}', f'{m.galaxy:.2f}')
            lo, hi, nd = -0.06, 0.27, 3
        else:
            m = 100 * r.assign(ok=(r.score >= 1 - 1e-9)).groupby('env').ok.mean()
            vals = (f'{m.open_ended_code:.1f}%', f'{m.galaxy:.1f}%')
            lo, hi, nd = -10, 10, 1
            ax.axvspan(-5, 5, color='#ededed', zorder=0, lw=0)
        ax.axvline(0, color=INK2, lw=0.6, zorder=1)
        for i, mname in enumerate(rows):
            row = g[g.model == ('all four' if mname == 'All four models' else mname)].iloc[0]
            pooled = mname == 'All four models'
            y = i + (0.3 if pooled else 0)
            ax.plot([row.ci95_low, row.ci95_high], [y, y], color=INK, lw=1.3 if pooled else 0.8, zorder=2,
                    solid_capstyle='butt')
            ax.scatter(row.value, y, marker='D' if pooled else 'o', s=16 if pooled else 9,
                       facecolor=INK if pooled else 'white', edgecolor=INK, linewidth=0.7, zorder=3)
            src.append(dict(panel='bcd'[j], benchmark=name, model=mname, difference=row.value,
                            ci95_low=row.ci95_low, ci95_high=row.ci95_high, p=row.p, p_holm=row.p_holm))
            if pooled:
                s = f'{row.value:+.{nd}f} ({row.ci95_low:.{nd}f} to {row.ci95_high:.{nd}f})'.replace('-', '−')
                ax.text(hi, y - 0.42, s, ha='right', va='bottom', fontsize=5.5, color=INK, fontweight='bold')
        ax.set_ylim(len(rows) - 0.25, -0.65)
        ax.set_yticks([0, 1, 2, 3, 4.3], rows if j == 0 else [''] * 5, fontsize=6)
        if j == 0:
            ax.get_yticklabels()[-1].set_fontweight('bold')
        ax.tick_params(axis='y', length=0)
        ax.set_xlim(lo, hi)
        if not iwc:
            ax.set_xticks([-10, -5, 0, 5, 10])
        clean(ax)
        ax.set_xlabel(xl, fontsize=6)
        ax.text(0, 1.205, name, transform=ax.transAxes, fontsize=6.5, fontweight='bold', color=INK, va='bottom')
        ax.text(0, 1.115, unit, transform=ax.transAxes, fontsize=5.5, color=INK2, va='bottom')
        ax.scatter([0.01], [1.045], transform=ax.transAxes, marker='s', s=7, color=CODE, clip_on=False)
        ax.text(0.04, 1.045, f'Custom code {vals[0]}', transform=ax.transAxes, fontsize=5.5, va='center')
        ax.scatter([0.53], [1.045], transform=ax.transAxes, marker='o', s=7, color=GAL, clip_on=False)
        ax.text(0.56, 1.045, f'Galaxy {vals[1]}', transform=ax.transAxes, fontsize=5.5, va='center')
        letter(fig, 0.0 if j == 0 else 0.13 + j * 0.295 - 0.03, 0.535, 'bcd'[j])
    save(fig, 'Fig1')
    with pd.ExcelWriter(os.path.join(OUT, 'Source_Data_Fig1.xlsx')) as w:
        pd.DataFrame(src).to_excel(w, sheet_name='Fig1b-d', index=False)
        cond = runs.assign(correct=lambda x: x.score >= x.benchmark.map({'BixBench50': 1.0, 'CompBio': 1.0,
                                                                          'IWC': 0.99}) - 1e-9)
        cond.groupby(['benchmark', 'cfg', 'env']).agg(runs=('score', 'size'), mean_score=('score', 'mean'),
                                                      runs_correct=('correct', 'sum')).reset_index().to_excel(
            w, sheet_name='condition values', index=False)


# ---------------------------------------------------------------- Fig. 2
CAUSES = [('SPEC', 'Under-specified task\nor reference answer', 'Benchmark'),
          ('EVALUATOR', 'Scorer rejected a\nvalid answer', 'Benchmark'),
          ('RIGOR', 'No validation of\nthe answer', 'Agent'),
          ('KNOWLEDGE', 'Wrong biological or\nstatistical knowledge', 'Agent'),
          ('PLATFORM', 'Galaxy itself', 'Galaxy'),
          ('HARNESS', 'No answer submitted', 'Other')]
SHADE = {0: '#33414c', 1: '#8796a2', 2: '#cdd5db'}


def panel_causes(ax):
    c = pd.read_csv(os.path.join(DATA, 'bixbench_causes_by_agreement.csv'))
    t = c.groupby(['primary_cause', 'correct_replicates_in_group']).incorrect_runs.sum().unstack(fill_value=0)
    rows = []
    for i, (code, label, group) in enumerate(CAUSES):
        left = 0
        for k in (0, 1, 2):
            v = int(t.loc[code, k]) if code in t.index and k in t.columns else 0
            rows.append(dict(cause=label.replace('\n', ' '), group=group, other_replicates_correct=k, incorrect_runs=v))
            if v:
                ax.barh(i, v, left=left, height=0.62, color=SHADE[k], edgecolor='white', linewidth=0.5, zorder=2)
                if v >= 6:
                    ax.text(left + v / 2, i, str(v), ha='center', va='center', fontsize=5.5,
                            color='white' if k < 2 else INK, zorder=3)
            left += v
        ax.text(left + 1.5, i, str(left), va='center', fontsize=5.5, color=INK, fontweight='bold')
    ax.set_yticks(range(len(CAUSES)), [lab for _, lab, _ in CAUSES], fontsize=5.5, linespacing=1.05)
    ax.tick_params(axis='y', length=0)
    ax.set_ylim(len(CAUSES) - 0.5, -0.6)
    ax.set_xlim(0, 105)
    clean(ax)
    ax.set_xlabel('Incorrect runs (n = 151)', fontsize=6)
    ax.legend(handles=[Patch(facecolor=SHADE[k], label=s) for k, s in ((0, '0'), (1, '1'), (2, '2'))],
              title='Sibling replicates correct', title_fontsize=5.5, fontsize=5.5, ncol=3, loc='lower right',
              bbox_to_anchor=(1.0, 0.02), handlelength=0.9, columnspacing=0.8, handletextpad=0.4)
    return rows


def panel_record(ax):
    ins = pd.read_csv(os.path.join(DATA, 'inspectability_counts.csv'))
    els = [('command', 'Command'), ('tool_version', 'Tool and version'), ('parameters', 'Parameters'),
           ('outputs', 'Output datasets')]
    rows = []
    for i, (el, lab) in enumerate(els):
        for k, (tr, col) in enumerate((('custom code', CODE), ('Galaxy', GAL))):
            x = ins[(ins.track == tr) & (ins.element == el)].iloc[0]
            pct = 100 * x.with_record / x.total
            y = i + (0.19 if k else -0.19)
            ax.barh(y, pct, height=0.34, color=col, zorder=2)
            ax.text(pct + 2 if pct < 80 else pct - 2, y, f'{pct:.0f}%', va='center', fontsize=5.5,
                    ha='left' if pct < 80 else 'right', color=INK if pct < 80 else 'white')
            rows.append(dict(element=lab, condition=tr, steps_with_record=int(x.with_record), steps=int(x.total),
                             percent=pct))
    ax.set_yticks(range(len(els)), [lab for _, lab in els], fontsize=5.5)
    ax.tick_params(axis='y', length=0)
    ax.set_ylim(len(els) - 0.45, -0.55)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 50, 100])
    clean(ax)
    ax.set_xlabel('Analysis steps with a record (%)', fontsize=6)
    ax.legend(handles=[Patch(facecolor=CODE, label='Custom code'), Patch(facecolor=GAL, label='Galaxy')],
              fontsize=5.5, loc='lower left', bbox_to_anchor=(-0.02, 1.01), ncol=2, handlelength=0.9,
              columnspacing=0.8, handletextpad=0.4)
    return rows


def panel_tokens(ax):
    f5 = pd.read_csv(os.path.join(FIG, 'fig5_source_data.csv'))
    c5 = f5[f5.panel == 'c'].copy()
    c5['value'] = pd.to_numeric(c5.value, errors='coerce')
    stages = [('July: Round 1 in place: shorter skills, prompt guidance', 'Round 1'),
              ('July: Round 2: submit, wait and check in one MCP call', 'Round 2'),
              ('October: Archived runs (round 2 in place)', 'Round 2'),
              ('October: Round 3: compact replies, templates (1 replicate)', 'Round 3\n(1 replicate)'),
              ('October: Round 3 plus longer waits between requests', 'Round 3 +\nlonger waits')]
    xs = [0, 1.1, 2.7, 3.85, 5.0]
    rows, top = [], 185
    for x, (grp, lab) in zip(xs, stages):
        g = c5[c5.group == grp].set_index(c5[c5.group == grp].measure.str.split(' \\(').str[0])
        gal, code = g.value['galaxy_tokens_m'], g.value['code_tokens_m']
        ratio = g.value['ratio_of_tokens_per_50_task_run']
        acc = g.value.get('galaxy_correct', np.nan)
        ax.bar(x - 0.19, code, width=0.36, color=CODE, zorder=2)
        ax.bar(x + 0.19, gal, width=0.36, color=GAL, zorder=2)
        ax.text(x, max(gal, code) + 4, f'{ratio:.2f}×', ha='center', va='bottom', fontsize=5.5, color=INK,
                fontweight='bold')
        if not np.isnan(acc):
            ax.text(x + 0.19, 3, f'{acc:.1f}% correct', ha='center', va='bottom', fontsize=4.8, color='white',
                    rotation=90)
        rows.append(dict(stage=grp, galaxy_tokens_millions=gal, custom_code_tokens_millions=code,
                         galaxy_over_custom_code=ratio, galaxy_runs_correct_pct=acc))
    ax.set_xticks(xs, [lab for _, lab in stages], fontsize=5.5, linespacing=1.05)
    ax.tick_params(axis='x', length=0, pad=3)
    ax.set_xlim(-0.55, 5.55)
    ax.set_ylim(0, top)
    clean(ax, grid='y')
    ax.set_ylabel('Tokens per 50-task run (millions)', fontsize=6)
    ax.text(0.55, top * 1.01, 'GPT-5.5 (July)', ha='center', va='bottom', fontsize=5.5, color=INK2)
    ax.text(3.85, top * 1.01, 'GPT-5.6 Sol (October)', ha='center', va='bottom', fontsize=5.5, color=INK2)
    ax.axvline(1.9, color=GRID, lw=0.6)
    ch = c5[c5.measure.str.contains('pct_change')].set_index('group')
    for (a, b_), key, yb in (((0, 1.1), 'July', 168), ((2.7, 5.0), 'October', 143)):
        ax.plot([a + 0.19, a + 0.19, b_ + 0.19, b_ + 0.19], [yb - 4, yb, yb, yb - 4], color=INK2, lw=0.5)
        r = ch.loc[key]
        ax.text((a + b_) / 2 + 0.19, yb + 1.5, f'{float(r.value):.1f}% ({r.ci95_low:.1f} to {r.ci95_high:.1f})'
                .replace('-', '−'), ha='center', va='bottom', fontsize=5, color=INK)
    return rows


def fig2():
    fig = plt.figure(figsize=(180 * MM, 72 * MM))
    a = fig.add_axes([0.118, 0.17, 0.20, 0.70])
    b = fig.add_axes([0.425, 0.17, 0.145, 0.62])
    c = fig.add_axes([0.655, 0.20, 0.335, 0.60])
    ra, rb, rc = panel_causes(a), panel_record(b), panel_tokens(c)
    fig.text(0.03, 0.965, 'Causes of incorrect BixBench-Verified-50 runs', fontsize=6.5, fontweight='bold', va='top')
    fig.text(0.355, 0.965, 'What each analysis step records', fontsize=6.5, fontweight='bold', va='top')
    fig.text(0.60, 0.965, 'Galaxy token use before and after interface changes', fontsize=6.5, fontweight='bold',
             va='top')
    letter(fig, 0.005, 0.985, 'a')
    letter(fig, 0.33, 0.985, 'b')
    letter(fig, 0.575, 0.985, 'c')
    save(fig, 'Fig2')
    with pd.ExcelWriter(os.path.join(OUT, 'Source_Data_Fig2.xlsx')) as w:
        pd.DataFrame(ra).to_excel(w, sheet_name='Fig2a', index=False)
        pd.DataFrame(rb).to_excel(w, sheet_name='Fig2b', index=False)
        pd.DataFrame(rc).to_excel(w, sheet_name='Fig2c', index=False)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig1()
    fig2()


# ---------------------------------------------------------------- Supplementary Fig. 4: consensus by model
def supp_consensus():
    """Single run, majority of 3 and at least 1 of 3 correct, per benchmark, model (and all four) and condition."""
    r = pd.read_csv(os.path.join(FIG, 'scored_runs.csv'))
    r['ok'] = (r.score >= r.benchmark.map({'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}) - 1e-9).astype(int)
    g = r.groupby(['benchmark', 'cfg', 'env', 'task']).ok.sum().rename('k').reset_index()
    rows = []
    for (bm, env), d in g.groupby(['benchmark', 'env']):
        for cfg, s in list(d.groupby('cfg')) + [('All four models', d)]:
            rows.append(dict(benchmark=bm, model=cfg, condition=env, single_run=100 * s.k.sum() / (3 * len(s)),
                             majority_of_3=100 * (s.k >= 2).mean(), at_least_1_of_3=100 * (s.k >= 1).mean(),
                             replicate_groups=len(s)))
    t = pd.DataFrame(rows)
    bench = [('BixBench50', 'BixBench-Verified-50', (72, 101.5), range(75, 101, 5)),
             ('CompBio', 'CompBioBench', (72, 101.5), range(75, 101, 5)),
             ('IWC', 'IWC-derived tasks', (52, 104), range(60, 101, 10))]
    order = ['All four models'] + MODELS
    ys = {}
    y = 0.0
    for m in order:
        ys[(m, 'galaxy')], ys[(m, 'open_ended_code')] = y, y + 0.36
        y += 1.15 if m != 'All four models' else 1.45
    fig, axes = plt.subplots(1, 3, figsize=(180 * MM, 82 * MM), sharey=True)
    fig.subplots_adjust(left=0.135, right=0.985, top=0.83, bottom=0.12, wspace=0.08)
    for ax, (bm, name, (lo, hi), ticks) in zip(axes, bench):
        d = t[t.benchmark == bm].set_index(['model', 'condition'])
        for (m, env), yy in ys.items():
            row = d.loc[(m, env)]
            col, fill = (GAL, GAL_T) if env == 'galaxy' else (CODE, CODE_T)
            s, v, c = row.single_run, row.majority_of_3, row.at_least_1_of_3
            ax.fill_betweenx([yy - 0.11, yy + 0.11], min(s, v), c, color=fill, lw=0, zorder=1)
            ax.scatter(c, yy, marker='s', s=11, facecolor='white', edgecolor=col, linewidth=0.7, zorder=3)
            ax.scatter(v, yy, marker='^', s=13, facecolor='white', edgecolor=col, linewidth=0.7, zorder=4)
            ax.scatter(s, yy, marker='o', s=5, color=col, edgecolor='none', zorder=5)
            ax.text(c + (hi - lo) * 0.02, yy, f'{c:.0f}', va='center', fontsize=5, color=INK)
        ax.set_xlim(lo, hi)
        ax.set_xticks(list(ticks))
        clean(ax)
        ax.spines['left'].set_visible(False)
        ax.tick_params(axis='y', length=0)
        ax.set_title(name, loc='left', fontsize=6.5, fontweight='bold', color=INK, pad=4)
    axes[0].set_ylim(y - 0.6, -0.4)
    axes[0].set_yticks([ys[(m, 'galaxy')] + 0.18 for m in order], order, fontsize=6)
    axes[0].get_yticklabels()[0].set_fontweight('bold')
    axes[1].set_xlabel('Accuracy (%; IWC-derived tasks: correct at output agreement ≥ 0.99)', fontsize=6)
    from matplotlib.lines import Line2D
    fig.legend(handles=[Line2D([], [], marker='o', ls='', color=INK2, markersize=3, label='Single run'),
                        Line2D([], [], marker='^', ls='', markerfacecolor='white', markeredgecolor=INK2,
                               markeredgewidth=0.7, markersize=4.5, label='Majority of 3'),
                        Line2D([], [], marker='s', ls='', markerfacecolor='white', markeredgecolor=INK2,
                               markeredgewidth=0.7, markersize=4, label='At least 1 of 3 correct'),
                        Patch(facecolor=GAL, label='Galaxy (upper row)'),
                        Patch(facecolor=CODE, label='Custom code (lower row)')],
               loc='upper center', bbox_to_anchor=(0.56, 0.995), ncol=5, fontsize=5.5, handlelength=1.0,
               columnspacing=1.2, handletextpad=0.4)
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(OUT, 'supplementary', f'SuppFig4_consensus_by_model.{ext}'), dpi=300,
                    facecolor='white')
    plt.close(fig)
    t.round(2).to_csv(os.path.join(OUT, 'supplementary', 'SuppFig4_consensus_by_model.csv'), index=False)
    print('wrote SuppFig4')


if __name__ == '__main__':
    supp_consensus()
