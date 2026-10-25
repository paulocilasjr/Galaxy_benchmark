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
    fig.savefig(os.path.join(OUT, f'{name}_300dpi.png'), dpi=300, facecolor='white')   # embedded in the .docx
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
    ax.text(0.412, 0.80, 'Galaxy MCP servers', fontsize=5.5, color=INK2, transform=ax.transAxes, va='top')
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
        left, above = 0, []
        for k in (0, 1, 2):
            v = int(t.loc[code, k]) if code in t.index and k in t.columns else 0
            rows.append(dict(cause=label.replace('\n', ' '), group=group, other_replicates_correct=k, incorrect_runs=v))
            if v:
                ax.barh(i, v, left=left, height=0.62, color=SHADE[k], edgecolor='white', linewidth=0.5, zorder=2)
                if v >= (5 if v < 10 else 7):                     # the number fits inside the segment
                    ax.text(left + v / 2, i, str(v), ha='center', va='center', fontsize=5.5,
                            color='white' if k < 2 else INK, zorder=3)
                else:
                    above.append((left + v / 2, v))
            left += v
        x_prev = 1.8 - 3.6                                        # keep the first label clear of the axis line
        for xc, v in above:                                       # small segments: number above the bar,
            x = max(xc, x_prev + 3.6)                             # spread so neighbours do not overlap
            ax.plot([xc, xc, x], [i - 0.31, i - 0.38, i - 0.42], color=INK2, lw=0.4, zorder=3,
                    solid_capstyle='butt')
            ax.text(x, i - 0.4, str(v), ha='center', va='bottom', fontsize=5, color=INK, zorder=3)
            x_prev = x
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


def panel_consensus(ax):
    """Accuracy of a single run, majority of 3, majority of 12 and at least 1 of 3 correct, per benchmark and
    condition (four models pooled; data/replicate_consensus.csv)."""
    q = pd.read_csv(os.path.join(DATA, 'replicate_consensus.csv'))
    names = {'BixBench-Verified-50': 'BixBench-Verified-50', 'CompBioBench': 'CompBioBench', 'IWC': 'IWC-derived'}
    marks = [('single_run_accuracy', 'Single run', 'o', True), ('majority_of_3_accuracy', 'Majority of 3', '^', False),
             ('majority_of_12_accuracy', 'Majority of 12', 'D', False),
             ('any_of_3_accuracy', 'At least 1 of 3 correct', 's', False)]
    rows, ticks, labels, y = [], [], [], 0.0
    for bm in ('BixBench-Verified-50', 'CompBioBench', 'IWC'):
        ax.text(-0.03, y - 0.62, names[bm], fontsize=5.8, fontweight='bold', va='center', ha='right', color=INK,
                transform=ax.get_yaxis_transform(), clip_on=False)
        for track, col, lab in (('Galaxy', GAL, 'Galaxy'), ('custom code', CODE, 'Custom code')):
            x = q[(q.benchmark == bm) & (q.track == track)].iloc[0]
            v = [100 * x[k] for k, *_ in marks]
            ax.plot([min(v), max(v)], [y, y], color=col, lw=0.7, alpha=0.45, zorder=1)
            for (k, _, m, filled), val in zip(marks, v):          # single run last and smaller, so ties stay visible
                ax.scatter(val, y, marker=m, s=7 if filled else (17 if m != 'D' else 13),
                           facecolor=col if filled else 'white', edgecolor=col, linewidth=0.7, zorder=4 if filled else 3)
            rows.append(dict(benchmark=bm, condition=track, **{lab_: 100 * x[k] for k, lab_, *_ in marks},
                             answer_vote_of_3=100 * x.answer_majority_of_3_accuracy, replicate_groups=x.replicate_groups))
            ticks.append(y)
            labels.append(lab)
            y += 1.0
        y += 0.75
    ax.set_yticks(ticks, labels, fontsize=5.5)
    ax.tick_params(axis='y', length=0)
    ax.set_ylim(y - 0.6, -1.15)
    ax.set_xlim(66, 100)
    ax.set_xticks([70, 80, 90, 100])
    clean(ax)
    ax.set_xlabel('Accuracy (%)', fontsize=6)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker=m, ls='', ms=3.6, mfc=INK2 if f else 'white', mec=INK2, mew=0.7,
                              label=lab) for _, lab, m, f in marks],
              fontsize=5.3, loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, handletextpad=0.2,
              columnspacing=1.0, borderaxespad=0.2)
    return rows


EXAMPLE_TASK, EXAMPLE_RUNS = 'bix-16-q1', ('galaxy_codex_gpt_5_6_luna_r1', 'open_ended_code_codex_gpt_5_6_luna_r1')


def example_record():
    """One analysis step as each condition retains it: bix-16-q1, GPT-5.6 Luna, replicate 1 (both runs correct).
    Every field shown is read from the run evidence (runs/BixBench_50/analysis/<task>/history_analysis_evidence.json)."""
    d = json.load(open(os.path.join(ARCHIVE, 'runs', 'BixBench_50', 'analysis', EXAMPLE_TASK,
                                    'history_analysis_evidence.json')))
    runs = {x['run_id']: x for x in d['runs']}

    def job(run_id):
        e = [e for e in runs[run_id]['events'] if 'featurewise_correlation' in str(e.get('tool'))]
        return e[-1] if e else None

    def params(e):
        p = e['parameters'] if isinstance(e['parameters'], dict) else json.loads(e['parameters'])
        return {k: str(v).strip('"') for k, v in p.items()}

    g = job(EXAMPLE_RUNS[0])
    p = params(g)
    ids = lambda v: len(v) if isinstance(v, list) else str(v).count("'") // 2       # noqa: E731
    code = [e for e in runs[EXAMPLE_RUNS[1]]['events'] if e['event_type'] == 'analysis']
    cmds = ' '.join(str(e.get('command')) for e in code)
    rec = dict(tool=g['tool'].split('/repos/')[-1].split('/')[1], version=g['tool'].rsplit('/', 1)[-1],
               method=p['method'], transform_b=p['transform_b'], min_pairs=p['min_pairs'],
               n_in=ids(g['input_artifact_ids']), n_out=ids(g['output_artifact_ids']), state=g['status'],
               exit=g['exit_code'], code_steps=len(code), code_failed=sum(e['status'] == 'failed' for e in code))
    assert rec['transform_b'] == 'negate' and rec['method'] == 'spearman', rec
    assert 'pip install --disable-pip-version-check --no-input numpy scipy pandas' in cmds
    assert not any(f'{m}==' in cmds for m in ('numpy', 'scipy', 'pandas')), 'packages were not pinned'
    assert "'ess',format(-x[0]" in cmds, 'custom code takes essentiality as -rho'
    ds = params(job('galaxy_deepseek_v4_pro_via_codex_r3'))
    assert ds['transform_b'] == 'none', ds
    r = pd.read_csv(os.path.join(FIG, 'scored_runs.csv'))
    t = r[(r.task == EXAMPLE_TASK)].set_index(['cfg', 'env', 'replicate']).score
    assert t[('GPT-5.6 Luna', 'galaxy', 1)] == 1 and t[('GPT-5.6 Luna', 'open_ended_code', 1)] == 1
    assert t[('DeepSeek V4 Pro', 'galaxy', 3)] == 0
    return rec


def panel_provenance(ax):
    rec = example_record()
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(1, 0)
    c0, c1, c2 = 0.0, 0.215, 0.61
    ax.add_patch(plt.Rectangle((c1 - 0.012, 0.0), 0.385, 0.86, fc='#e3eff7', ec='none', zorder=0))
    ax.add_patch(plt.Rectangle((c2 - 0.012, 0.0), 0.402, 0.86, fc='#fbebe0', ec='none', zorder=0))
    ax.text(c1, 0.035, 'Galaxy job record', fontsize=5.8, fontweight='bold', color=GAL, va='top')
    ax.text(c2, 0.035, 'Custom-code trace', fontsize=5.8, fontweight='bold', color=CODE, va='top')
    rows = [('Tool and version', f'{rec["tool"]}\n{rec["version"]} (Tool Shed identifier)',
             'Inline Python script; pandas, NumPy\nand SciPy installed with unpinned pip'),
            ('Parameters', f'Fields: method = {rec["method"]};\ntransform_b = {rec["transform_b"]}; '
                           f'min_pairs = {rec["min_pairs"]}',
             'Written in the code; essentiality\ntaken as −ρ when ranking'),
            ('Inputs and\noutputs', f'{rec["n_in"]} input and {rec["n_out"]} output datasets,\nlinked by identifier '
                                   f'in the history', 'Inputs named in the code; results\nprinted to the log only'),
            ('Status', f'Job state "{rec["state"]}", exit code {rec["exit"]}',
             f'Exit code per command ({rec["code_failed"]} of\n{rec["code_steps"]} analysis commands failed)'),
            ('Answer', 'CDKN1A (accepted)', 'CDKN1A (accepted)')]
    y = 0.135
    for name, a, b in rows:
        n = max(a.count('\n'), b.count('\n')) + 1
        ax.text(c0, y, name, fontsize=5.3, fontweight='bold', va='top', color=INK)
        ax.text(c1, y, a, fontsize=5.0, va='top', color=INK, linespacing=1.2)
        ax.text(c2, y, b, fontsize=5.0, va='top', color=INK, linespacing=1.2)
        y += 0.062 * n + 0.045
        ax.plot([0, 1.0], [y - 0.028, y - 0.028], color=GRID, lw=0.5)
    ax.text(c0, 0.9, 'The decisive choice is a stored field: DeepSeek V4 Pro r3 left transform_b = none and answered '
                     'CCND1.', fontsize=5.3, color=INK2, va='top')
    return [dict(element=n_, galaxy=a.replace('\n', ' '), custom_code=b.replace('\n', ' ')) for n_, a, b in rows]


def panel_token_steps(ax):
    """Galaxy / custom-code tokens per 50-task BixBench-Verified-50 run at each interface stage (numbers.json)."""
    st = json.load(open(os.path.join(BC, 'numbers.json')))['token_stages']['value']
    labels = ['Round 1', 'Round 2', 'Round 2\n(main runs)', 'Round 3\n(1 replicate)', 'Round 3 +\nlonger waits']
    xs = [0, 1, 2.45, 3.45, 4.45]
    rows = []
    for seg, col in (((0, 1), INK), ((2, 3, 4), INK)):
        x = [xs[i] for i in seg]
        y = [float(st[i]['ratio_of_tokens_per_50_task_run']) for i in seg]
        ax.step(x, y, where='mid', color=GAL, lw=1.0, zorder=2)
    for i, (x, s_) in enumerate(zip(xs, st)):
        r = float(s_['ratio_of_tokens_per_50_task_run'])
        lo, hi = s_.get('ratio_lo'), s_.get('ratio_hi')
        has_ci = lo is not None and not (isinstance(lo, float) and np.isnan(lo))
        if has_ci:
            ax.plot([x, x], [lo, hi], color=GAL, lw=0.8, zorder=3)
        ax.scatter(x, r, s=16, marker='o', facecolor=GAL if has_ci else 'white', edgecolor=GAL, lw=0.8, zorder=4)
        ax.text(x + 0.12, r, f'{r:.2f}×', fontsize=5.5, va='bottom', ha='left', color=INK, fontweight='bold')
        acc = s_.get('galaxy_correct')
        ax.text(x, 13.2, f'{float(acc):.1f}' if acc is not None else 'n.a.', ha='center', va='center', fontsize=5.3,
                color=INK if acc is not None else INK2)
        rows.append(dict(stage=labels[i].replace('\n', ' '), galaxy_over_custom_code=r,
                         ci95_low=lo if has_ci else None, ci95_high=hi if has_ci else None,
                         galaxy_runs_correct_pct=float(acc) if acc is not None else None,
                         galaxy_tokens_millions=float(s_['galaxy_tokens_m']),
                         custom_code_tokens_millions=float(s_['code_tokens_m'])))
    ax.text(-0.55, 13.2, 'Galaxy\ncorrect (%)', ha='right', va='center', fontsize=5.3, color=INK2, linespacing=1.0)
    ax.axhline(1, color=INK2, lw=0.6, ls=(0, (3, 2)), zorder=1)
    ax.text(-0.4, 1.04, 'parity', fontsize=5, color=INK2, ha='left', va='bottom')
    ax.axvline(1.72, color=GRID, lw=0.6)
    ax.text(0.5, 9.4, 'GPT-5.5, July 2026', ha='center', fontsize=5.5, color=INK2)
    ax.text(3.45, 9.4, 'GPT-5.6 Sol, October 2026', ha='center', fontsize=5.5, color=INK2)
    ax.set_yscale('log')
    ax.set_ylim(0.7, 16)
    ax.set_yticks([1, 2, 4, 8], ['1×', '2×', '4×', '8×'])
    ax.minorticks_off()
    ax.set_xticks(xs, labels, fontsize=5.3, linespacing=1.0)
    ax.tick_params(axis='x', length=0, pad=2.5)
    ax.set_xlim(-0.45, 5.0)
    clean(ax, grid='y')
    ax.spines['top'].set_visible(False)
    ax.set_ylabel('Galaxy ÷ custom-code tokens', fontsize=6)
    return rows


def fig2():
    fig = plt.figure(figsize=(180 * MM, 128 * MM))
    a = fig.add_axes([0.135, 0.585, 0.30, 0.355])
    b = fig.add_axes([0.665, 0.585, 0.25, 0.30])
    c = fig.add_axes([0.03, 0.035, 0.44, 0.40])
    d = fig.add_axes([0.62, 0.11, 0.355, 0.33])
    ra, rb, rc, rd = panel_causes(a), panel_consensus(b), panel_provenance(c), panel_token_steps(d)
    fig.text(0.03, 0.975, 'Causes of incorrect BixBench-Verified-50 runs', fontsize=6.5, fontweight='bold', va='top')
    fig.text(0.52, 0.975, 'Accuracy of one run and of consensus across replicates', fontsize=6.5, fontweight='bold',
             va='top')
    fig.text(0.03, 0.485, 'One analysis step as each condition records it', fontsize=6.5, fontweight='bold', va='top')
    fig.text(0.03, 0.458, 'bix-16-q1, GPT-5.6 Luna, replicate 1', fontsize=5.5, color=INK2, va='top')
    fig.text(0.52, 0.485, 'Galaxy token use relative to custom code', fontsize=6.5, fontweight='bold', va='top')
    letter(fig, 0.005, 0.99, 'a')
    letter(fig, 0.497, 0.99, 'b')
    letter(fig, 0.005, 0.50, 'c')
    letter(fig, 0.497, 0.50, 'd')
    save(fig, 'Fig2')
    with pd.ExcelWriter(os.path.join(OUT, 'Source_Data_Fig2.xlsx')) as w:
        pd.DataFrame(ra).to_excel(w, sheet_name='Fig2a', index=False)
        pd.DataFrame(rb).to_excel(w, sheet_name='Fig2b', index=False)
        pd.DataFrame(rc).to_excel(w, sheet_name='Fig2c', index=False)
        pd.DataFrame(rd).to_excel(w, sheet_name='Fig2d', index=False)


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
