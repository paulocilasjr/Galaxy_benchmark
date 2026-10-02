"""Main and Extended Data figures, Source Data and text numbers for the user-oriented Analysis.

Run from the repository root with Python 3.12 and manuscript_narrative/requirements.txt:
    python manuscript_narrative/user-oriented/scripts/make_figures.py [1 2 3 4 5 6 ed]

Question: when does executing a biomedical AI agent through Galaxy, rather than through open-ended code, change the
reliability and reviewability of its analyses, and at what cost? The primary paired population is the four Codex model
configurations; the superseded Claude Code harness and the unpaired GPT-6 Astra runs are reported separately.
Every number quoted in manuscript.md as {{key}} is written to numbers.json by this script.
"""
import json
import os
import sys
import textwrap

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(PAPER))
import narrative_common as nc  # noqa: E402
from narrative_common import FIG_W, fmt, plt, style  # noqa: E402
from style import (CODE, CONFIGS, ENV_COLOR, ENV_LABEL, ENV_MARKER, ENV_TINT, ENVS, GALAXY, GRID, INK, INK2, LIGHT,  # noqa: E402
                   MM, NEUTRAL_DARK, NEUTRAL_LIGHT, NEUTRAL_MID, OI_GREEN, OI_ORANGE, OI_PURPLE, OI_SKY, SUPERSEDED,
                   env_handles, grid_x, panel_label, panel_title)

TITLES = {
    'Fig1': 'Comparison design, analysed populations and primary endpoints',
    'Fig2': 'Benchmark accuracy by execution condition, with reference and evaluator sensitivity',
    'Fig3': 'Outcome repeatability across replicate runs',
    'Fig4': 'Implementation and version differences behind divergent and stable results',
    'Fig5': 'What each condition leaves for review, and what the audit found',
    'Fig6': 'Observed resource use and retrospective answer-voting strategies',
    'ED_Fig1': 'Summary of condition contrasts across user-facing measures',
    'ED_Fig2': 'Task-level accuracy and replicate answer agreement',
    'ED_Fig3': 'Execution errors by type and condition',
    'ED_Fig4': 'Majority-vote rules compared with the scored-correct oracle',
}
CFG_SHORT = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6 Sol', 'GPT-5.6 Luna': 'GPT-5.6 Luna',
             'DeepSeek V4 Pro': 'DeepSeek V4 Pro (Codex)', SUPERSEDED: 'DeepSeek V4 Pro\n(Claude Code, superseded)'}
BL = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
NUM = {}
TOK_IN = {}


FIG_OF = {'fig1': 'Fig. 1', 'fig2': 'Fig. 2', 'fig3': 'Fig. 3', 'fig4': 'Fig. 4', 'fig5': 'Fig. 5', 'fig6': 'Fig. 6', 'figed': 'Extended Data'}
SRC = {}


def put(key, value):
    """Record a number quoted in manuscript.md as {{key}}, with the figure function that computed it."""
    import inspect
    NUM[key] = value
    for fr in inspect.stack()[1:]:
        if fr.function in FIG_OF or fr.function in ('design_numbers', 'readiness_measures'):
            SRC[key] = FIG_OF.get(fr.function, fr.function)
            break


def save_numbers(fresh=False):
    for name, data in [('numbers.json', NUM), ('numbers_provenance.json', SRC)]:
        p = os.path.join(PAPER, name)
        old = json.load(open(p)) if os.path.exists(p) and not fresh else {}
        old.update(data)
        json.dump(dict(sorted(old.items())), open(p, 'w'), indent=1, ensure_ascii=False)


def new_fig(h_mm):
    return plt.figure(figsize=(FIG_W, h_mm * MM))


def ci(d, nd=1):
    return f'{fmt(d[0], nd, True)} ({fmt(d[1], nd)} to {fmt(d[2], nd)})'


# ---------------------------------------------------------------------------------------------------- drawing helpers
def box(ax, x, y, w, h, text, fc='white', ec=INK2, lw=0.6, fs=5.5, weight='normal', ha='center', ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.012', fc=fc, ec=ec, lw=lw, ls=ls,
                                transform=ax.transAxes, clip_on=False))
    tx = x + w / 2 if ha == 'center' else x + 0.012
    ax.text(tx, y + h / 2, text, ha=ha, va='center', fontsize=fs, fontweight=weight, transform=ax.transAxes, linespacing=1.22)


def arrow(ax, x0, y0, x1, y1, color=INK2, lw=0.7):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=6, lw=lw, color=color,
                                 transform=ax.transAxes, shrinkA=0, shrinkB=0, clip_on=False))


def dot(ax, x, y, env, filled=True, ms=3.4, z=3):
    ax.plot(x, y, ENV_MARKER[env], ms=ms, mfc=ENV_COLOR[env] if filled else 'white',
            mec='white' if filled else ENV_COLOR[env], mew=0.4 if filled else 0.8, zorder=z, ls='', clip_on=False)


def plain_log(ax, ticks, axis='x'):
    from matplotlib.ticker import FixedLocator, NullFormatter
    a = ax.xaxis if axis == 'x' else ax.yaxis
    a.set_major_locator(FixedLocator(ticks))
    (ax.set_xticklabels if axis == 'x' else ax.set_yticklabels)([f'{t:g}' for t in ticks])
    a.set_minor_formatter(NullFormatter())


def cluster_map():
    r = nc.runs()
    return dict(zip(zip(r.benchmark, r.task), r.cluster))


def cell_ratio(df, value, bench, cfgs=CONFIGS, complete=True):
    """Median over task x model-configuration cells of median(Galaxy)/median(open-ended code), cluster bootstrap.
    complete=True keeps only cells with all six runs' values present (the canonical eligibility rule)."""
    cmap = cluster_map()
    x = df[(df.benchmark == bench) & df.cfg.isin(cfgs)]
    n_ok = x.groupby(['task', 'cfg', 'env'])[value].apply(lambda v: v.notna().sum()).unstack('env')
    med = x.groupby(['task', 'cfg', 'env'])[value].median().unstack('env')
    eligible = len(med)
    if complete:
        med = med[(n_ok.open_ended_code == 3) & (n_ok.galaxy == 3)]
    med = med.dropna()
    med = med[med.open_ended_code > 0]
    med['ratio'] = med.galaxy / med.open_ended_code
    med = med.reset_index()
    med['cluster'] = [cmap[(bench, t)] for t in med.task]
    est = nc.boot_median_ratio([g.ratio.values for _, g in med.groupby('cluster')])
    return est, len(med), eligible, med


def text_table(ax, cols, xs, rows, y0=0.86, dy=0.15, fs=5.3, header_fs=5.4):
    for x, c in zip(xs, cols):
        ax.text(x, 0.99, c, fontsize=header_fs, fontweight='bold', va='top', transform=ax.transAxes, linespacing=1.15)
    ax.plot([0, 1], [y0 + 0.04, y0 + 0.04], color=INK2, lw=0.5, transform=ax.transAxes, clip_on=False)
    for i, row in enumerate(rows):
        for x, t in zip(xs, row):
            ax.text(x, y0 - i * dy, t, fontsize=fs, va='top', transform=ax.transAxes, linespacing=1.15)


# ---------------------------------------------------------------------------------------------------- Figure 1
def primary_endpoints():
    """Benchmark-specific primary endpoints (four Codex configurations), with the condition difference and interval."""
    g = nc.graded_runs()
    fd = nc.fd()
    rows = []
    bix = [r for r in fd['fig2a'] if r['config'] == 'Four Codex configurations'][0]
    rows.append(dict(benchmark='BixBench50', endpoint='Accepted by the original evaluator (% of runs)',
                     reference='Benchmark reference answer and its original evaluator', code=100 * bix['code'][0] / bix['code'][1],
                     galaxy=100 * bix['galaxy'][0] / bix['galaxy'][1], diff=bix['diff'], unit='points', n='600 / 600 runs'))
    x = g[(g.benchmark == 'CompBio') & g.cfg.isin(CONFIGS)]
    arr = nc.paired_cluster_arrays(x, 'score')
    rows.append(dict(benchmark='CompBio', endpoint='Agreement with the reconstructed reference key (% of runs)',
                     reference='Key reconstructed from leaderboard totals (54 items score-inferred, 46 score-predicted)',
                     code=100 * arr[0].sum() / arr[1].sum(), galaxy=100 * arr[2].sum() / arr[3].sum(),
                     diff=nc.boot_diff(*arr, scale=100), unit='points', n='1,200 / 1,200 runs'))
    iwc = [r for r in fd['fig2c'] if r['config'] == 'All four'][0]
    rows.append(dict(benchmark='IWC', endpoint='Mean output agreement with the workflow output (0-1), nine matched tasks',
                     reference='Published workflow output; some route references calibrated from agent runs',
                     code=iwc['code_mean'], galaxy=iwc['galaxy_mean'], diff=iwc['diff'], unit='agreement', n='108 / 108 runs'))
    return rows


def fig1():
    fig = new_fig(150)
    sd = {}
    # ---------------- a: design
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'Paired execution conditions (assigned arms)')
    ax = fig.add_axes([0.0, 0.66, 0.60, 0.28])
    ax.axis('off')
    box(ax, 0.0, 0.36, 0.14, 0.30, 'Task prompt\nand input data', fc=LIGHT)
    box(ax, 0.18, 0.36, 0.15, 0.30, 'Agent:\nmodel\nconfiguration\n+ harness', fc=LIGHT, weight='bold')
    arrow(ax, 0.14, 0.51, 0.18, 0.51)
    box(ax, 0.39, 0.60, 0.33, 0.34, 'Open-ended code condition\nunrestricted shell; the agent installs\nsoftware and writes its own code',
        fc=ENV_TINT['open_ended_code'], ec=CODE)
    box(ax, 0.39, 0.02, 0.33, 0.46, 'Galaxy condition\nGalaxy interface to usegalaxy.org;\ninstalled, versioned tool wrappers;\n'
        'agent code as a Galaxy job;\nlocal shell for staging', fc=ENV_TINT['galaxy'], ec=GALAXY)
    arrow(ax, 0.33, 0.56, 0.39, 0.77, color=CODE)
    arrow(ax, 0.33, 0.46, 0.39, 0.25, color=GALAXY)
    box(ax, 0.76, 0.60, 0.24, 0.34, 'Answer\n+ execution trace', ec=CODE)
    box(ax, 0.76, 0.02, 0.24, 0.46, 'Answer\n+ execution trace\n+ analysis history\n(tools, versions,\nparameters, jobs)', ec=GALAXY)
    arrow(ax, 0.72, 0.77, 0.76, 0.77, color=CODE)
    arrow(ax, 0.72, 0.25, 0.76, 0.25, color=GALAXY)
    # ---------------- b: populations
    panel_label(fig, 0.625, 0.995, 'b')
    panel_title(fig, 0.625, 0.995, 'Analysed populations')
    axb = fig.add_axes([0.63, 0.60, 0.365, 0.34])
    axb.axis('off')
    r = nc.runs()
    total = len(r)
    sup = int((r.cfg == SUPERSEDED).sum())
    astra = int((r.cfg == 'GPT-6 Astra').sum())
    prim = r[r.cfg.isin(CONFIGS)]
    per = {b: int((prim.benchmark == b).sum()) for b in style.BENCH}
    iwc_nine = int(((prim.benchmark == 'IWC') & (prim.task != nc.IWC_NINE_EXCLUDED)).sum())
    box(axb, 0.0, 0.80, 0.42, 0.17, f'{total:,} archived runs\n160 tasks, 3 benchmarks', fc=LIGHT, fs=5.4)
    box(axb, 0.55, 0.80, 0.45, 0.17, f'Reported separately: {sup} runs,\nsuperseded Claude Code harness', fs=5.1, ls=(0, (3, 2)))
    box(axb, 0.55, 0.58, 0.45, 0.17, f'Excluded from pairing: {astra} runs,\nGPT-6 Astra (code only)', fs=5.1, ls=(0, (3, 2)))
    arrow(axb, 0.42, 0.885, 0.55, 0.885)
    arrow(axb, 0.42, 0.85, 0.55, 0.67)
    box(axb, 0.0, 0.40, 0.48, 0.30, f'{len(prim):,} paired runs\nfour Codex model configurations\n× 2 conditions × 3 replicate runs',
        fc=LIGHT, fs=5.3, weight='bold')
    arrow(axb, 0.21, 0.80, 0.21, 0.70)
    bx = [('BixBench-Verified-50', f'{per["BixBench50"]:,} runs'), ('CompBioBench', f'{per["CompBio"]:,} runs'),
          ('IWC', f'{per["IWC"]:,} runs; {iwc_nine} in\nnine matched tasks')]
    for i, (b, t) in enumerate(bx):
        box(axb, 0.0 + i * 0.345, 0.0, 0.31, 0.27, f'{b}\n{t}', fs=5.0)
        arrow(axb, 0.24, 0.40, 0.155 + i * 0.345, 0.27)
    put('n_total_runs', f'{total:,}')
    put('n_superseded_runs', f'{sup}')
    put('n_astra_runs', f'{astra}')
    put('n_primary_runs', f'{len(prim):,}')
    put('n_primary_runs_iwc_nine', f'{len(prim) - per["IWC"] + iwc_nine:,}')
    sd['b_populations'] = pd.DataFrame([dict(population='archived', runs=total), dict(population='superseded Claude Code harness', runs=sup),
                                        dict(population='GPT-6 Astra (unpaired)', runs=astra), dict(population='primary paired', runs=len(prim))]
                                       + [dict(population=f'primary {BL[b]}', runs=v) for b, v in per.items()]
                                       + [dict(population='primary IWC nine matched tasks', runs=iwc_nine)])
    # ---------------- c: primary endpoints
    panel_label(fig, 0.005, 0.52, 'c')
    panel_title(fig, 0.005, 0.52, 'Benchmark-specific primary endpoints (four Codex model configurations)')
    axc = fig.add_axes([0.02, 0.02, 0.96, 0.43])
    axc.axis('off')
    ep = primary_endpoints()
    sets = nc.replicate_sets()
    rows, srows = [], []
    for e in ep:
        b = e['benchmark']
        nd = 3 if b == 'IWC' else 1
        d = e['diff']
        s = sets[(sets.benchmark == b) & sets.cfg.isin(CONFIGS)]
        disc = {env: int(((s.env == env) & (s.cat == 'split')).sum()) for env in ENVS}
        nsets = {env: int((s.env == env).sum()) for env in ENVS}
        rows.append([BL[b], e['endpoint'], e['reference'], fmt(e['code'], nd), fmt(e['galaxy'], nd), ci(d, nd),
                     f'{disc["open_ended_code"]} of {nsets["open_ended_code"]} vs {disc["galaxy"]} of {nsets["galaxy"]}'])
        srows.append(dict(benchmark=BL[b], endpoint=e['endpoint'], reference_provenance=e['reference'], open_ended_code=e['code'],
                          galaxy=e['galaxy'], difference=d[0], ci95_low=d[1], ci95_high=d[2], unit=e['unit'], runs=e['n'],
                          discordant_sets_code=disc['open_ended_code'], sets_code=nsets['open_ended_code'],
                          discordant_sets_galaxy=disc['galaxy'], sets_galaxy=nsets['galaxy']))
        key = {'BixBench50': 'bix', 'CompBio': 'cb', 'IWC': 'iwc'}[b]
        put(f'{key}_code', fmt(e['code'], nd))
        put(f'{key}_galaxy', fmt(e['galaxy'], nd))
        put(f'{key}_diff', fmt(d[0], nd, True))
        put(f'{key}_diff_ci', f'{fmt(d[1], nd)} to {fmt(d[2], nd)}')
        put(f'{key}_disc_code', f'{disc["open_ended_code"]} of {nsets["open_ended_code"]}')
        put(f'{key}_disc_galaxy', f'{disc["galaxy"]} of {nsets["galaxy"]}')
    wrap = lambda t, w: '\n'.join(textwrap.wrap(t, w))  # noqa: E731
    rows = [[r_[0].replace('-50', '-\n50') if 'Bix' in r_[0] else r_[0], wrap(r_[1], 30), wrap(r_[2], 34)] + r_[3:6]
            + [r_[6].replace(' vs ', '\nvs ')] for r_ in rows]
    text_table(axc, ['Benchmark', 'Endpoint', 'Reference provenance', 'Open-ended\ncode', 'Galaxy', 'Galaxy − open-ended\ncode (95% CI)',
                     'Discordant replicate\nsets, code vs Galaxy'],
               [0.0, 0.11, 0.33, 0.57, 0.66, 0.73, 0.88], rows, y0=0.74, dy=0.25, fs=5.3)
    axc.text(0.0, 0.0, 'BixBench-Verified-50 and IWC intervals are the archived 95% cluster-bootstrap intervals; the CompBioBench interval is from\n'
             'this analysis (20,000 resamples). IWC discordant sets: three output-agreement values spanning more than 0.05.',
             fontsize=5, color=INK2, transform=axc.transAxes, va='bottom')
    sd['c_primary_endpoints'] = pd.DataFrame(srows)
    nc.save_figure(fig, PAPER, 'Fig1', TITLES['Fig1'])
    nc.source_data(PAPER, 'Fig1', sd, TITLES['Fig1'])


# ---------------------------------------------------------------------------------------------------- Figure 2
def forest(fig, rect_l, rect_r, rows, xlim, dlim, xlabel, dlabel, nd):
    """Rows: dicts with label, kind ('config', 'pooled', 'sensitivity', 'separate'), optional reps/means and diff."""
    axl, axr = fig.add_axes(rect_l), fig.add_axes(rect_r)
    n = len(rows)
    for ax in (axl, axr):
        ax.set_ylim(n - 0.4, -0.6)
        ax.set_yticks(range(n))
        for i, r in enumerate(rows):
            if r['kind'] == 'pooled':
                ax.axhspan(i - 0.5, i + 0.5, color=LIGHT, zorder=0, lw=0)
        for i in range(1, n):
            if rows[i]['kind'] != rows[i - 1]['kind'] and rows[i]['kind'] in ('sensitivity', 'separate'):
                ax.axhline(i - 0.5, color=NEUTRAL_MID, lw=0.4, ls=(0, (1, 1)))
    axl.set_yticklabels([r['label'] for r in rows], fontsize=5.2, linespacing=1.08)
    for t, r in zip(axl.get_yticklabels(), rows):
        if r['kind'] == 'sensitivity':
            t.set_color(INK2)
    axr.set_yticklabels([])
    for i, r in enumerate(rows):
        if r.get('reps'):
            for e, dy in zip(ENVS, (-0.17, 0.17)):
                v = r['reps'][e]
                jit = np.linspace(-0.05, 0.05, len(v)) if len(v) > 3 else np.zeros(len(v))
                axl.plot(v, i + dy + jit, ENV_MARKER[e], ms=2.4, mfc=ENV_COLOR[e], mec='white', mew=0.3, ls='', zorder=3)
                axl.plot([r['means'][e]] * 2, [i + dy - 0.16, i + dy + 0.16], color=INK, lw=0.9, zorder=4)
        elif r.get('means'):
            axl.text(np.mean(xlim), i, f'{fmt(r["means"]["open_ended_code"], nd)} vs {fmt(r["means"]["galaxy"], nd)}',
                     ha='center', va='center', fontsize=5, color=INK2)
        est, lo, hi = r['diff']
        sens = r['kind'] == 'sensitivity'
        axr.plot([lo, hi], [i, i], color=INK2 if sens else INK, lw=0.8)
        axr.plot(est, i, 'D' if sens else 'o', ms=2.8, mfc='white' if sens else INK, mec=INK2 if sens else INK, mew=0.8)
        axr.text(1.05, i, f'{fmt(est, nd, True)}\n({fmt(lo, nd)} to {fmt(hi, nd)})', transform=axr.get_yaxis_transform(), fontsize=5.0,
                 va='center', linespacing=1.05, color=INK2 if sens else INK)
    axl.set_xlim(*xlim)
    axr.set_xlim(*dlim)
    axr.axvline(0, color=INK2, lw=0.6, ls=(0, (2, 2)))
    grid_x(axl), grid_x(axr)
    axl.set_xlabel(xlabel)
    axr.set_xlabel(dlabel)
    axl.set_title('Replicate means and arm mean', fontsize=5.5, loc='left')
    axr.set_title('Galaxy − code', fontsize=5.5, loc='left')
    return axl, axr


def config_rows(bench, scale):
    g = nc.graded_runs()
    x = g[g.benchmark == bench]
    out = []
    for c in CONFIGS + ['Pooled', SUPERSEDED]:
        y = x[x.cfg.isin(CONFIGS if c == 'Pooled' else [c])]
        if y.empty:
            continue
        reps = {e: list(y[y.env == e].groupby(['cfg', 'replicate']).score.mean() * scale) for e in ENVS}
        means = {e: float(y[y.env == e].score.mean() * scale) for e in ENVS}
        out.append(dict(cfg=c, label=CFG_SHORT.get(c, 'Four Codex model\nconfigurations, pooled'),
                        kind='separate' if c == SUPERSEDED else ('pooled' if c == 'Pooled' else 'config'), reps=reps, means=means,
                        data=y))
    return out


def forest_source(rows, interval_source):
    return pd.DataFrame([dict(row=r['label'].replace('\n', ' '), kind=r['kind'], open_ended_code=r['means']['open_ended_code'],
                              galaxy=r['means']['galaxy'], difference=r['diff'][0], ci95_low=r['diff'][1], ci95_high=r['diff'][2],
                              interval_source=interval_source if r['kind'] != 'sensitivity' else 'this analysis (seed 20261002)')
                         for r in rows])


def replicate_mean_source(rows):
    """The observed means behind every coloured point, including its number of task runs."""
    out = []
    for row in rows:
        if 'data' not in row:
            continue
        for (cfg, env, replicate), x in row['data'].groupby(['cfg', 'env', 'replicate']):
            out.append(dict(row=row['label'].replace('\n', ' '), benchmark=x.benchmark.iloc[0], cfg=cfg,
                            env=env, replicate=replicate, mean_score=float(x.score.mean()), runs=len(x)))
    return pd.DataFrame(out)


def design_metadata():
    p = os.path.join(nc.NARR, 'derived', 'design', 'design_metadata.json')
    return json.load(open(p))


def iwc_budget_pairs():
    """One row per IWC task x configuration x replicate: whether both arms had the same wall-clock budget."""
    d = pd.DataFrame(design_metadata()['q4_budgets']['iwc_per_run']['rows'])
    d['cfg'] = d.model.map(nc.CFG)
    w = d.pivot_table(index=['task', 'cfg', 'replicate'], columns='condition', values='budget_h').reset_index()
    w['budget_matched'] = w['galaxy'] == w['open_ended_code']
    return w[['task', 'cfg', 'replicate', 'budget_matched']]


def design_numbers():
    d = design_metadata()
    pm = d['q4_budgets']['iwc_pair_matching']
    put('iwc_budget_matched', f'{pm["matched_budget_pairs"]} of {pm["pairs"]}')
    ident = d['q3_prompts']['galaxy_vs_code_prompt_identity']['rows']
    put('prompt_pairs_identical', f'{sum(r["identical_hash_pairs"] for r in ident):,} of {sum(r["pairs_compared"] for r in ident):,}')
    wc = {(r['benchmark'], r['condition']): r['prompt_file_words_median'] for r in d['q3_prompts']['word_counts_by_condition']['rows']}
    for b in ['BixBench50', 'CompBio', 'IWC']:
        put(f'prompt_words_{b}', f'{wc[(b, "galaxy")]:,.0f} versus {wc[(b, "open_ended_code")]:,.0f}')


def fig2():
    fig = new_fig(170)
    sd = {}
    fd = nc.fd()
    cats = nc.audit_categories()
    # ---------------- a BixBench
    rows = config_rows('BixBench50', 100)
    arch = {}
    for r in fd['fig2a']:
        k = {'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro', 'Four Codex configurations': 'Pooled',
             'DeepSeek V4 Pro (Claude Code, superseded)': SUPERSEDED}.get(r['config'], r['config'])
        arch[k] = tuple(r['diff'])
    for r in rows:
        r['diff'] = arch[r['cfg']]
    pooled = [r for r in rows if r['cfg'] == 'Pooled'][0]['data']
    bench_side = {t for (b, t), c in cats.items() if b == 'BixBench50' and c in ('C1', 'C2', 'C3', 'C6')}
    y = pooled[~pooled.task.isin(bench_side)]
    d = nc.boot_diff(*nc.paired_cluster_arrays(y, 'score'), scale=100)
    rows.insert(5, dict(label=f'Pooled, without {len(bench_side)} tasks\n(C1, C2, C3 or C6)', kind='sensitivity', diff=d,
                        means={e: 100 * y[y.env == e].score.mean() for e in ENVS}))
    put('bix_sens_bench_side_n', str(len(bench_side)))
    put('bix_sens_bench_side_diff', ci(d))
    sup = [r for r in rows if r.get('cfg') == SUPERSEDED][0]
    put('bix_superseded_diff', ci(sup['diff']))
    put('bix_superseded_code', fmt(sup['means']['open_ended_code']))
    put('bix_superseded_galaxy', fmt(sup['means']['galaxy']))
    cfg_d = [r['diff'][0] for r in rows if r['kind'] == 'config']
    put('bix_cfg_diff_range', f'{fmt(min(cfg_d), 1, True)} to {fmt(max(cfg_d), 1, True)}')
    for r in rows:
        if r['kind'] == 'config':
            put(f'bix_diff_{r["cfg"].replace(" ", "_").replace(".", "")}', fmt(r['diff'][0], 1, True))
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'BixBench-Verified-50: original evaluator acceptance')
    forest(fig, [0.165, 0.66, 0.145, 0.28], [0.335, 0.66, 0.055, 0.28], rows, (55, 100), (-12, 24), 'Accepted runs (%)',
           'Difference\n(points)', 1)
    sd['a_bixbench'] = forest_source(rows, 'archived (manuscript_material Supplementary Table 2)')
    sd['a_replicate_means'] = replicate_mean_source(rows)
    # ---------------- b CompBio with key variants
    rows = config_rows('CompBio', 100)
    for r in rows:
        r['diff'] = nc.boot_diff(*nc.paired_cluster_arrays(r['data'], 'score'), scale=100)
        if r['kind'] == 'config':
            put(f'cb_diff_{r["cfg"].replace(" ", "_").replace(".", "")}', fmt(r['diff'][0], 1, True))
    var = nc.compbio_variants()
    labels = {'alt_genome_D': 'Pooled, genome-coords-q1\nscored against key D',
              'no_predicted': 'Pooled, without the two\naudited predicted-key tasks',
              'informative': 'Pooled, 53 tasks with a run\ndeviating from the key'}
    bad, n_bad = nc.compbio_outcome_named_cells()
    prim = var['primary'].merge(bad.assign(_f=1), on=['task', 'cfg'], how='left')
    var['no_outcome_campaigns'] = prim[prim._f.isna()].drop(columns='_f')
    labels['no_outcome_campaigns'] = f'Pooled, without {len(bad)} cells with\na run from an outcome-named campaign'
    put('cb_outcome_named_runs', str(n_bad))
    put('cb_outcome_named_cells', str(len(bad)))
    for k, lab in labels.items():
        y = var[k]
        d = nc.boot_diff(*nc.paired_cluster_arrays(y, 'score'), scale=100)
        rows.append(dict(label=lab, kind='sensitivity', diff=d, means={e: 100 * y[y.env == e].score.mean() for e in ENVS}))
        put(f'cb_sens_{k}', ci(d))
    panel_label(fig, 0.505, 0.995, 'b')
    panel_title(fig, 0.505, 0.995, 'CompBioBench: agreement with the reconstructed key')
    forest(fig, [0.665, 0.66, 0.145, 0.28], [0.835, 0.66, 0.055, 0.28], rows, (75, 100), (-8, 8), 'Runs agreeing with key (%)',
           'Difference\n(points)', 1)
    sd['b_compbiobench'] = forest_source(rows, 'this analysis (seed 20261002)')
    sd['b_replicate_means'] = replicate_mean_source(rows)
    # ---------------- c IWC nine tasks with sensitivity
    rows = config_rows('IWC', 1)
    arch = {({'All four': 'Pooled'}.get(r['config'], r['config'])): tuple(r['diff']) for r in fd['fig2c']}
    for r in rows:
        r['diff'] = arch[r['cfg']]
    pooled = [r for r in rows if r['cfg'] == 'Pooled'][0]['data']

    def iwc_diff(y):
        return nc.boot_diff(*nc.paired_cluster_arrays(y.assign(cluster=y.task), 'score'))
    comp = nc.iwc_components()
    circular = 'wf_006_atacseq_chromatin_accessibility'
    zero_tasks = {t for t, z in pooled.groupby('task') if (z.score == 0).any()}
    bud = iwc_budget_pairs()
    pk = pooled.merge(bud, on=['task', 'cfg', 'replicate'], how='left')
    matched = pk[pk.budget_matched == True]  # noqa: E712
    n_matched_pairs = matched.groupby(['task', 'cfg', 'replicate']).env.nunique().eq(2).sum()
    for lab, y in [('Without ATAC-seq (route\nreferences from agent runs)', pooled[pooled.task != circular]),
                   (f'Without the {len(zero_tasks)} tasks with\na zero-scored run', pooled[~pooled.task.isin(zero_tasks)]),
                   (f'Only the {n_matched_pairs} replicate pairs\nwith equal time budgets', matched[pooled.columns])]:
        rows.append(dict(label=lab, kind='sensitivity', diff=iwc_diff(y), means={e: y[y.env == e].score.mean() for e in ENVS}))
    put('iwc_sens_no_atac', ci(rows[-3]['diff'], 3))
    put('iwc_sens_no_zero', ci(rows[-2]['diff'], 3))
    put('iwc_sens_budget_matched', ci(rows[-1]['diff'], 3))
    put('iwc_budget_matched_pairs_nine', str(n_matched_pairs))
    put('iwc_budget_pairs_nine', str(pooled.groupby(['task', 'cfg', 'replicate']).ngroups))
    put('iwc_zero_tasks_n', str(len(zero_tasks)))
    for r in rows:
        if r['kind'] == 'config':
            put(f'iwc_diff_{r["cfg"].replace(" ", "_").replace(".", "")}', ci(r['diff'], 3))
    n_cal = {e: int(comp[(comp.task == circular) & (comp.env == e)].route_reference_from_agent_run.sum()) for e in ENVS}
    put('iwc_atac_agent_calibrated_code', str(n_cal['open_ended_code']))
    put('iwc_atac_agent_calibrated_galaxy', str(n_cal['galaxy']))
    panel_label(fig, 0.005, 0.585, 'c')
    panel_title(fig, 0.005, 0.585, 'IWC: output agreement, nine matched tasks')
    forest(fig, [0.165, 0.305, 0.145, 0.22], [0.335, 0.305, 0.055, 0.22], rows, (0.75, 1.0), (-0.12, 0.26),
           'Mean output agreement (0-1)', 'Difference', 3)
    sd['c_iwc'] = forest_source(rows, 'archived (manuscript_material Supplementary Table 7)')
    sd['c_replicate_means'] = replicate_mean_source(rows)
    # No benchmark answer is disclosed: only grades, identities and sensitivity eligibility.
    obs = nc.graded_runs().copy()
    obs['primary_configuration'] = obs.cfg.isin(CONFIGS)
    obs['bix_benchmark_side_task'] = obs.benchmark.eq('BixBench50') & obs.task.isin(bench_side)
    obs['compbio_outcome_named_cell'] = [b == 'CompBio' and (t, c) in set(zip(bad.task, bad.cfg))
                                         for b, t, c in zip(obs.benchmark, obs.task, obs.cfg)]
    obs['iwc_zero_task'] = obs.benchmark.eq('IWC') & obs.task.isin(zero_tasks)
    obs['iwc_atac_task'] = obs.benchmark.eq('IWC') & obs.task.eq(circular)
    obs = obs.merge(bud, on=['task', 'cfg', 'replicate'], how='left')
    sd['abc_run_scores_eligibility'] = obs
    # ---------------- d IWC task-level differences with leave-one-task-out
    panel_label(fig, 0.505, 0.585, 'd')
    panel_title(fig, 0.505, 0.585, 'IWC: task-level differences')
    tm = pooled.groupby(['task', 'env']).score.mean().unstack()
    tm['d'] = tm.galaxy - tm.open_ended_code
    tm = tm.sort_values('d')
    label = {r['task']: r['task_label'] for r in fd['fig2d']}
    ax = fig.add_axes([0.70, 0.305, 0.19, 0.22])
    for i, (t, r_) in enumerate(tm.iterrows()):
        ax.plot([0, r_.d], [i, i], color=NEUTRAL_MID, lw=0.8)
        ax.plot(r_.d, i, 'o', ms=3, color=GALAXY if r_.d > 0 else CODE)
        ax.text(max(r_.d, 0) + 0.012, i, fmt(r_.d, 3, True), fontsize=5.0, va='center')
    loto = []
    for t in tm.index:
        y = pooled[pooled.task != t]
        loto.append(y[y.env == 'galaxy'].groupby('task').score.mean().mean() - y[y.env == 'open_ended_code'].groupby('task').score.mean().mean())
    ax.set_yticks(range(len(tm)))
    ax.set_yticklabels([label[t] + (' *' if t == circular else '') for t in tm.index], fontsize=5.1)
    ax.axvline(0, color=INK2, lw=0.6, ls=(0, (2, 2)))
    ax.set_xlim(-0.08, 0.36)
    ax.set_ylim(len(tm) - 0.4, -0.6)
    ax.set_xlabel('Galaxy − code, task mean (0-1)')
    grid_x(ax)
    ax.text(-0.55, -0.36, f'Leave-one-task-out pooled difference: {fmt(min(loto), 3, True)} to {fmt(max(loto), 3, True)}.\n'
            f'* Route references for {n_cal["open_ended_code"]} of 12 code and {n_cal["galaxy"]} of 12 Galaxy\nruns were calibrated from agent runs.',
            transform=ax.transAxes, fontsize=5.0, color=INK2, va='top')
    put('iwc_loto', f'{fmt(min(loto), 3, True)} to {fmt(max(loto), 3, True)}')
    sd['d_iwc_tasks'] = tm.reset_index().assign(task_label=lambda z: z.task.map(label))
    sd['d_iwc_loto'] = pd.DataFrame(dict(task_left_out=list(tm.index), pooled_difference=loto))
    # ---------------- e IWC components
    panel_label(fig, 0.005, 0.185, 'e')
    panel_title(fig, 0.005, 0.185, 'IWC: biological components alongside the headline score')
    comps = [('wf_002_rnaseq_de_visualization', 'significant_jaccard', 'RNA-seq differential expression:\nsignificant-gene Jaccard with the reference'),
             ('wf_009_clinicalmp_peptide_verification', 'precision', 'Peptide verification:\npeptide-accession precision'),
             ('wf_007_vgp_mitogenome_assembly', 'f1', 'Mitochondrial genome assembly:\n31-mer F1 with the reference')]
    rows = []
    for j, (t, col, lab) in enumerate(comps):
        ax = fig.add_axes([0.07 + j * 0.33, 0.035, 0.24, 0.085])
        for i, e in enumerate(ENVS):
            z = comp[(comp.task == t) & (comp.env == e)]
            v = z[col].dropna().values
            jit = np.linspace(-0.18, 0.18, len(v))
            ax.plot(v, i + jit, ENV_MARKER[e], ms=2.6, mfc=ENV_COLOR[e], mec='white', mew=0.3, ls='')
            rows += [dict(task=t, component=col, env=e, run_id=rid, value=float(x)) for rid, x in zip(z.dropna(subset=[col]).run_id, v)]
        ax.set_yticks([0, 1])
        ax.set_yticklabels(['Code', 'Galaxy'], fontsize=5.2)
        ax.set_ylim(1.5, -0.5)
        ax.set_xlim(-0.03, 1.03)
        ax.set_title(lab, fontsize=5.2, loc='left', linespacing=1.1)
        grid_x(ax)
    sig = comp[(comp.task == comps[0][0]) & comp.significant_candidate.notna()]
    big = sig[sig.significant_candidate > 20].iloc[0]
    put('iwc_rnaseq_edger_genes', f'{int(big.significant_candidate)}')
    put('iwc_rnaseq_edger_score', fmt(big.score, 3))
    put('iwc_rnaseq_ref_genes', f'{int(big.significant_reference)}')
    put('iwc_rnaseq_pydeseq_runs', str(int(((sig.significant_candidate == 12)).sum())))
    sd['e_iwc_components'] = pd.DataFrame(rows)
    fig.legend(handles=env_handles(ms=3.2) + [Line2D([], [], marker='D', ls='', mfc='white', mec=INK2, ms=3, label='Sensitivity analysis')],
               loc='upper right', bbox_to_anchor=(0.995, 0.19), ncol=3, fontsize=5.2)
    nc.save_figure(fig, PAPER, 'Fig2', TITLES['Fig2'])
    nc.source_data(PAPER, 'Fig2', sd, TITLES['Fig2'])


# ---------------------------------------------------------------------------------------------------- Figure 3
STATES = [('3/3', 'All three\ncorrect'), ('split', 'Discordant'), ('0/3', 'None\ncorrect')]


def fig3():
    fig = new_fig(150)
    sd = {}
    sets = nc.replicate_sets()
    # ---------------- a: paired transitions
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'Paired replicate-set outcomes, open-ended code to Galaxy')
    rows = []
    for j, b in enumerate(['BixBench50', 'CompBio']):
        s = sets[(sets.benchmark == b) & sets.cfg.isin(CONFIGS)]
        p = s.pivot_table(index=['task', 'cfg'], columns='env', values='cat', aggfunc='first')
        m = pd.crosstab(p.open_ended_code, p.galaxy).reindex(index=[k for k, _ in STATES], columns=[k for k, _ in STATES], fill_value=0)
        ax = fig.add_axes([0.10 + j * 0.24, 0.62, 0.13, 0.27])
        vmax = m.values.max()
        for i, (ki, _) in enumerate(STATES):
            for k, (kj, _) in enumerate(STATES):
                v = int(m.loc[ki, kj])
                ax.add_patch(plt.Rectangle((k, i), 1, 1, fc=NEUTRAL_DARK if i == k else GALAXY if k < i else CODE,
                                           alpha=0.12 + 0.6 * (v / vmax) ** 0.5 if v else 0.04, ec='white', lw=1))
                ax.text(k + 0.5, i + 0.5, str(v), ha='center', va='center', fontsize=5.6, fontweight='bold' if i == k else 'normal')
                rows.append(dict(benchmark=BL[b], open_ended_code_state=ki, galaxy_state=kj, task_configuration_pairs=v))
        ax.set_xlim(0, 3), ax.set_ylim(3, 0)
        ax.set_xticks([0.5, 1.5, 2.5]), ax.set_yticks([0.5, 1.5, 2.5])
        ax.set_xticklabels(['3/3\ncorrect', 'Discordant', '0/3\ncorrect'], fontsize=5)
        ax.set_yticklabels([l for _, l in STATES] if j == 0 else [], fontsize=5)
        ax.tick_params(length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
        ax.set_title(f'{BL[b]} ({len(p)} task ×\nmodel configuration pairs)', fontsize=5.4, loc='left', linespacing=1.1)
        ax.set_xlabel('Galaxy', fontsize=5.6)
        if j == 0:
            ax.set_ylabel('Open-ended code', fontsize=5.6)
        better = int(sum(m.iloc[i, k] for i in range(3) for k in range(3) if k < i))
        worse = int(sum(m.iloc[i, k] for i in range(3) for k in range(3) if k > i))
        ax.text(0, 3.75, f'Better in Galaxy (blue): {better}; worse\n(vermillion): {worse}; same (grey): {len(p) - better - worse}',
                fontsize=5, color=INK2, va='top')
        key = 'bix' if b == 'BixBench50' else 'cb'
        put(f'{key}_trans_better', str(better))
        put(f'{key}_trans_worse', str(worse))
        put(f'{key}_trans_pairs', str(len(p)))
    sd['a_transitions'] = pd.DataFrame(rows)
    # ---------------- b: discordant sets per configuration
    panel_label(fig, 0.53, 0.995, 'b')
    panel_title(fig, 0.53, 0.995, 'Discordant replicate sets per model configuration')
    rows = []
    for j, b in enumerate(['BixBench50', 'CompBio']):
        ax = fig.add_axes([0.665 + j * 0.17, 0.62, 0.12, 0.27])
        for i, c in enumerate(CONFIGS):
            q = sets[(sets.benchmark == b) & (sets.cfg == c)]
            v = {e: int(((q.env == e) & (q.cat == 'split')).sum()) for e in ENVS}
            ax.plot([v['open_ended_code'], v['galaxy']], [i, i], color=NEUTRAL_MID, lw=0.8, zorder=1)
            for e in ENVS:
                dot(ax, v[e], i, e)
            rows.append(dict(benchmark=BL[b], cfg=c, discordant_code=v['open_ended_code'], discordant_galaxy=v['galaxy'],
                             sets_per_condition=int((q.env == 'galaxy').sum())))
        q = sets[(sets.benchmark == b) & sets.cfg.isin(CONFIGS)].assign(split=lambda d: (d.cat == 'split').astype(int))
        est = nc.boot_rel(*nc.paired_cluster_arrays(q, 'split'))
        ax.set_ylim(3.6, -0.6)
        ax.set_yticks(range(4))
        ax.set_yticklabels([CFG_SHORT[c] for c in CONFIGS] if j == 0 else [], fontsize=5.2)
        ax.set_xlim(-1, {'BixBench50': 10, 'CompBio': 25}[b])
        ax.set_title(f'{BL[b]}\nratio {fmt(est[0], 2)} ({fmt(est[1], 2)} to {fmt(est[2], 2)})', fontsize=5.3, loc='left', linespacing=1.1)
        ax.set_xlabel('Discordant sets')
        grid_x(ax)
        put(f'{"bix" if b == "BixBench50" else "cb"}_disc_ratio', f'{fmt(est[0], 2)} ({fmt(est[1], 2)} to {fmt(est[2], 2)})')
    sd['b_discordant_by_configuration'] = pd.DataFrame(rows)
    fig.legend(handles=env_handles(ms=3.2), loc='upper left', bbox_to_anchor=(0.665, 0.535), ncol=2, fontsize=5.2)
    # ---------------- c: IWC within-set ranges, nine matched tasks
    panel_label(fig, 0.005, 0.44, 'c')
    panel_title(fig, 0.005, 0.44, 'IWC: spread of output agreement within replicate sets')
    iw = sets[sets.benchmark == 'IWC'].copy()
    iw['range'] = iw.scores.apply(lambda v: max(v) - min(v))
    ax = fig.add_axes([0.10, 0.10, 0.32, 0.25])
    rows = []
    for i, e in enumerate(ENVS):
        v = iw[iw.env == e]['range'].values
        jit = np.random.default_rng(1).uniform(-0.2, 0.2, len(v))
        ax.plot(np.maximum(v, 1e-4), i + jit, ENV_MARKER[e], ms=2.8, mfc=ENV_COLOR[e], mec='white', mew=0.3, ls='', alpha=0.9)
        n_split = int((v > 0.05).sum())
        ax.text(1.04, i, f'{n_split} of {len(v)} above 0.05', transform=ax.get_yaxis_transform(), fontsize=5.2, va='center')
        rows += [dict(env=e, task=t, cfg=c, within_set_range=float(x)) for t, c, x in zip(iw[iw.env == e].task, iw[iw.env == e].cfg, v)]
    ax.axvline(0.05, color=INK2, lw=0.6, ls=(0, (2, 2)))
    ax.set_xscale('log')
    ax.set_xlim(8e-5, 1.5)
    plain_log(ax, [0.0001, 0.001, 0.01, 0.05, 0.1, 1])
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Open-ended code', 'Galaxy'], fontsize=5.3)
    ax.set_ylim(1.6, -0.6)
    ax.set_xlabel('Within-set range of output agreement (log; 0 shown at 0.0001)')
    grid_x(ax)
    iw10 = nc.iwc_sets_all_ten()
    s10 = {e: (int(((iw10.env == e) & (iw10.cat == 'split')).sum()), int(((iw10.env == e) & iw10.scored).sum())) for e in ENVS}
    ax.text(0.0, -0.42, f'Nine matched tasks (36 sets per condition). Ten tasks, sensitivity: {s10["open_ended_code"][0]} of '
            f'{s10["open_ended_code"][1]} scored code sets vs {s10["galaxy"][0]} of {s10["galaxy"][1]} Galaxy sets.',
            transform=ax.transAxes, fontsize=5.0, color=INK2, va='top')
    put('iwc_disc_ten', f'{s10["open_ended_code"][0]} of {s10["open_ended_code"][1]} vs {s10["galaxy"][0]} of {s10["galaxy"][1]}')
    sd['c_iwc_ranges'] = pd.DataFrame(rows)
    # ---------------- d: unanimous accuracy
    panel_label(fig, 0.53, 0.44, 'd')
    panel_title(fig, 0.53, 0.44, 'Tasks solved by all three replicate runs')
    rows = []
    for j, b in enumerate(['BixBench50', 'CompBio']):
        ax = fig.add_axes([0.665 + j * 0.17, 0.10, 0.12, 0.25])
        labs = CONFIGS + ['Pooled']
        for i, c in enumerate(labs):
            q = sets[(sets.benchmark == b) & sets.cfg.isin(CONFIGS if c == 'Pooled' else [c])].assign(u=lambda d: (d.cat == '3/3').astype(int))
            est, lo, hi = nc.boot_diff(*nc.paired_cluster_arrays(q, 'u'), scale=100)
            v = {e: 100 * q[q.env == e].u.mean() for e in ENVS}
            ax.plot([v['open_ended_code'], v['galaxy']], [i, i], color=NEUTRAL_MID, lw=0.8, zorder=1)
            for e in ENVS:
                dot(ax, v[e], i, e)
            rows.append(dict(benchmark=BL[b], cfg=c, unanimous_code=v['open_ended_code'], unanimous_galaxy=v['galaxy'],
                             difference=est, ci95_low=lo, ci95_high=hi))
            if c == 'Pooled':
                key = 'bix' if b == 'BixBench50' else 'cb'
                put(f'{key}_unan_code', fmt(v['open_ended_code']))
                put(f'{key}_unan_galaxy', fmt(v['galaxy']))
                put(f'{key}_unan_diff', ci((est, lo, hi)))
        ax.axhline(3.5, color=NEUTRAL_MID, lw=0.4, ls=(0, (1, 1)))
        ax.set_ylim(4.6, -0.6)
        ax.set_yticks(range(5))
        ax.set_yticklabels([CFG_SHORT.get(c, 'Pooled') for c in labs] if j == 0 else [], fontsize=5.2)
        ax.set_xlim(65, 95)
        ax.set_title(BL[b], fontsize=5.4, loc='left')
        ax.set_xlabel('Tasks with 3 of 3\nruns correct (%)')
        grid_x(ax)
    d = pd.DataFrame(rows)
    pos = int((d[d.cfg != 'Pooled'].difference > 0).sum())
    put('unan_pairs_positive', f'{pos} of {int((d.cfg != "Pooled").sum())}')
    put('unan_range', f'{fmt(d[d.cfg != "Pooled"].difference.min(), 0)} to {fmt(d[d.cfg != "Pooled"].difference.max(), 0)}')
    sd['d_unanimous'] = d
    nc.save_figure(fig, PAPER, 'Fig3', TITLES['Fig3'])
    nc.source_data(PAPER, 'Fig3', sd, TITLES['Fig3'])


# ---------------------------------------------------------------------------------------------------- Figure 4
DIVERGENCE = [('Hand-written method or different\nsoftware version', ['V5', 'V3'], OI_ORANGE),
              ('Domain convention applied\ndifferently', ['V4'], OI_SKY),
              ('Error in the final step', ['V6'], OI_GREEN),
              ('Galaxy interface trap', ['V1'], NEUTRAL_DARK),
              ('No answer, or benchmark\nsource files read', ['V7', 'V8'], NEUTRAL_LIGHT)]


def case_panel(ax, title, groups, note_x=2.35):
    """groups: list of (label, {env: n_runs}, correct, note)."""
    for i, (lab, counts, ok, note) in enumerate(groups):
        for col, e in enumerate(ENVS):
            for m in range(counts.get(e, 0)):
                ax.plot(col * 1.15 + (m % 6) * 0.17, i + (m // 6) * 0.3 - 0.15, ENV_MARKER[e], ms=2.6,
                        mfc=ENV_COLOR[e] if ok else 'white', mec=ENV_COLOR[e], mew=0.6, clip_on=False)
        ax.text(note_x, i, note, fontsize=5.0, va='center', linespacing=1.12, color=INK if ok else INK2)
    ax.set_yticks(range(len(groups)))
    ax.set_yticklabels([g[0] for g in groups], fontsize=5.2)
    ax.set_ylim(len(groups) - 0.35, -0.75)
    ax.set_xlim(-0.15, 2.1)
    ax.set_xticks([0.42, 1.57])
    ax.set_xticklabels(['Code', 'Galaxy'], fontsize=5.2)
    ax.tick_params(axis='x', length=0)
    ax.spines['bottom'].set_visible(False)
    ax.set_title(title, fontsize=5.3, loc='left', linespacing=1.12)


def fig4():
    fig = new_fig(155)
    sd = {}
    fd = nc.fd()
    # ---------------- a: divergence mechanisms by harness
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'How scored-incorrect runs differed from their correct siblings (BixBench-Verified-50)')
    dbc = fd['divergence_by_config']
    groups = [('Four Codex\nconfigurations', CONFIGS), ('Superseded\nClaude Code harness', [SUPERSEDED])]
    ax = fig.add_axes([0.13, 0.70, 0.40, 0.22])
    rows, y, yt, yl = [], 0, [], []
    for gname, cfgs in groups:
        for e in ENVS:
            cnt = {lab: sum(dbc.get(f'{e}|{c}', {}).get(k, 0) for c in cfgs for k in codes) for lab, codes, _ in DIVERGENCE}
            tot = sum(cnt.values())
            left = 0
            for lab, codes, col in DIVERGENCE:
                v = cnt[lab]
                if v:
                    ax.barh(y, v, left=left, color=col, edgecolor='white', lw=0.5, height=0.62)
                    if v >= 2:
                        ax.text(left + v / 2, y, str(v), ha='center', va='center', fontsize=5.1, color='white' if col == NEUTRAL_DARK else INK)
                    left += v
                rows.append(dict(harness=gname.replace('\n', ' '), env=e, mechanism=lab.replace('\n', ' '), runs=v, total=tot))
            ax.text(left + 0.5, y, f'{tot} runs', va='center', fontsize=5, color=INK2)
            yt.append(y)
            yl.append(f'{gname.split(chr(10))[0]}: {ENV_LABEL[e].lower()}' if False else ENV_LABEL[e])
            y += 1
        y += 0.6
    ax.set_yticks(yt)
    ax.set_yticklabels(yl, fontsize=5.3)
    for yy, (gname, _) in zip([-0.75, 1.85], groups):
        ax.text(0, yy, gname.replace('\n', ' '), fontsize=5.4, fontweight='bold', va='center')
    ax.set_ylim(y - 0.4, -1.2)
    ax.set_xlim(0, 30)
    ax.set_xlabel('Scored-incorrect runs in discordant replicate sets')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=c, label=l) for l, _, c in DIVERGENCE], loc='upper left', bbox_to_anchor=(1.02, 1.05), fontsize=5,
              labelspacing=0.7)
    d = pd.DataFrame(rows)
    cx = d[(d.harness == 'Four Codex configurations')]
    hw = cx[cx.mechanism.str.startswith('Hand-written')].set_index('env').runs
    tot = cx.groupby('env').runs.sum()
    put('div_codex_hw_code', f'{int(hw["open_ended_code"])} of {int(tot["open_ended_code"])}')
    put('div_codex_hw_galaxy', f'{int(hw["galaxy"])} of {int(tot["galaxy"])}')
    trap = cx[cx.mechanism == 'Galaxy interface trap'].set_index('env').runs
    put('div_codex_trap_galaxy', f'{int(trap["galaxy"])} of {int(tot["galaxy"])}')
    sx = d[d.harness != 'Four Codex configurations']
    hws = sx[sx.mechanism.str.startswith('Hand-written')].set_index('env').runs
    tots = sx.groupby('env').runs.sum()
    put('div_sup_hw_code', f'{int(hws["open_ended_code"])} of {int(tots["open_ended_code"])}')
    put('div_sup_hw_galaxy', f'{int(hws["galaxy"])} of {int(tots["galaxy"])}')
    sd['a_divergence'] = d
    # ---------------- b-d: three traced cases, four Codex configurations (12 runs per condition)
    cases = [
        ('b', 'bix-55-q1: complete BUSCO genes\n(supplied BUSCO 5.8.0 outputs)', [
            ('101', {'open_ended_code': 10, 'galaxy': 12}, True, 'reference'),
            ('100', {'open_ended_code': 2}, False, 'BUSCO 5.7.1 installed\nby the agent')]),
        ('c', 'bix-45-q1: Mann-Whitney P of relative\ncomposition variability (PhyKIT)', [
            ('7.70e-54', {'open_ended_code': 8}, True, 'reference: PhyKIT 2.0.3\ndefinition, reconstructed'),
            ('1.52e-56', {'open_ended_code': 4, 'galaxy': 12}, False, 'current PhyKIT definition;\nscientifically defensible,\n'
             'rejected (Galaxy: 10 wrapper,\n2 user-defined-tool runs)')]),
        ('d', 'encode-atac-pipeline-q1: IDR N_opt\n(ENCODE ATAC-seq pipeline)', [
            ('Reference-\nmatching', {'galaxy': 2}, True, 'official container,\nas a Galaxy job'),
            ('Nearby,\nnonmatching', {'open_ended_code': 11}, False, 'outside its container;\nhost-library differences\nuntested'),
            ('Trimming-\ndisabled', {'galaxy': 8}, False, 'staged names disabled\ntrimming (1 run copied\nanother run\'s answer)'),
            ('Local\nfallback', {'galaxy': 2}, False, 'computed locally after\nGalaxy jobs failed'),
            ('Local port', {'open_ended_code': 1}, False, 'local port; unchecked')]),
    ]
    r = nc.runs()
    chk = {('bix-55-q1', 'open_ended_code'): 12, ('bix-55-q1', 'galaxy'): 12, ('bix-45-q1', 'galaxy'): 12,
           ('encode-atac-pipeline-q1', 'galaxy'): 12, ('encode-atac-pipeline-q1', 'open_ended_code'): 12}
    rows = []
    for k, (letter, title, groups_) in enumerate(cases):
        task = title.split(':')[0]
        for e in ENVS:
            n = sum(g[1].get(e, 0) for g in groups_)
            assert n == int(((r.task == task) & (r.env == e) & r.cfg.isin(CONFIGS)).sum()) == chk.get((task, e), n), (task, e, n)
        x0 = 0.035 + k * 0.32
        panel_label(fig, x0 - 0.03, 0.585, letter)
        ax = fig.add_axes([x0 + 0.06, 0.30, 0.10, 0.23])
        case_panel(ax, title, groups_)
        rows += [dict(task=task, answer=g[0].replace('\n', ' '), runs_code=g[1].get('open_ended_code', 0), runs_galaxy=g[1].get('galaxy', 0),
                      matches_reference=g[2], interpretation=g[3].replace('\n', ' ')) for g in groups_]
    fig.text(0.005, 0.585 - 0.0, '', fontsize=1)
    sd['bcd_cases'] = pd.DataFrame(rows)
    # verify the case counts against the archive
    bix55 = r[(r.task == 'bix-55-q1') & r.cfg.isin(CONFIGS)]
    assert int(((bix55.env == 'open_ended_code') & (bix55.answer.str.strip() == '100')).sum()) == 2
    # ---------------- e: IWC runs below 0.5
    panel_label(fig, 0.005, 0.18, 'e')
    panel_title(fig, 0.005, 0.18, 'Every IWC run with output agreement below 0.5, by traced cause')
    causes = [('Hand-written multiple-testing correction', 1, 0, 'Galaxy wrappers compute adjusted P values with library code'),
              ('Sample identifiers lowercased from folder names', 2, 0, 'Galaxy collections carry sample identifiers'),
              ('Wrong contig submitted as the mitochondrial genome', 2, 1, 'No identity check in either condition'),
              ('Score conflict: correct output scored against another route', 0, 2, 'Evaluator artifact')]
    ax = fig.add_axes([0.30, 0.02, 0.10, 0.13])
    rows = []
    for i, (lab, c_, g_, note) in enumerate(causes):
        for e, v, dy in [('open_ended_code', c_, -0.17), ('galaxy', g_, 0.17)]:
            ax.barh(i + dy, v, height=0.32, color=ENV_COLOR[e])
            ax.text(v + 0.08, i + dy, str(v), va='center', fontsize=5)
        ax.text(1.12, i, note, transform=ax.get_yaxis_transform(), fontsize=5, va='center', color=INK2)
        rows.append(dict(cause=lab, runs_code=c_, runs_galaxy=g_, interpretation=note))
    ax.set_yticks(range(4))
    ax.set_yticklabels([c[0] for c in causes], fontsize=5.2)
    ax.set_ylim(3.6, -0.6)
    ax.set_xlim(0, 2.6)
    ax.set_xticks([0, 1, 2])
    ax.set_xlabel('Runs')
    grid_x(ax)
    fig.legend(handles=[Patch(fc=CODE, label='Open-ended code (5 of 117 scored runs)'), Patch(fc=GALAXY, label='Galaxy (3 of 120)')],
               loc='upper right', bbox_to_anchor=(0.995, 0.185), ncol=1, fontsize=5)
    sd['e_iwc_below_half'] = pd.DataFrame(rows)
    nc.save_figure(fig, PAPER, 'Fig4', TITLES['Fig4'])
    nc.source_data(PAPER, 'Fig4', sd, TITLES['Fig4'])


# ---------------------------------------------------------------------------------------------------- Figure 5
CAUSE_CATS = [('C1', 'Equivalent answer,\nother notation', OI_SKY), ('C2', 'Scoring or\nevaluator artifact', OI_GREEN),
              ('C3', 'Reference depends on\nan unstated choice', '#F0E442'), ('C4', 'Galaxy platform,\nwrapper or server', NEUTRAL_DARK),
              ('C5', 'Agent analysis error', OI_ORANGE), ('C6+', 'Other', NEUTRAL_LIGHT)]


def coverage_table():
    A = nc.analysis()
    rows = []
    for r in A['runs']:
        c = r.get('coverage') or {}
        rows.append(dict(benchmark=r['benchmark'], env=r['condition'], cfg=nc.CFG[r['model']], trace=c.get('agent_transcript') == 'retrieved',
                         history=c.get('public_history_contents'), tool_ids=r.get('galaxy_full_tool_ids') or [],
                         indicators=r.get('software_command_indicators') or []))
    return pd.DataFrame(rows)


def fig5():
    fig = new_fig(140)
    sd = {}
    cov = coverage_table()
    prim = cov[cov.cfg.isin(CONFIGS)]
    calls = nc.galaxy_calls()
    # ---------------- a: evidence recorded per run
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'Recorded evidence and parameter-check coverage')
    ev = []
    for e in ENVS:
        x = prim[prim.env == e]
        ev.append(('Execution trace retrieved', e, int(x.trace.sum()), len(x)))
    g = prim[prim.env == 'galaxy']
    ev.append(('Detailed analysis history\n(tools, parameters, job states)', 'galaxy', int((g.history == 'retrieved').sum()), len(g)))
    if calls is not None:
        tr = calls[(calls.tool == 'run_galaxy_tool_and_wait') & calls.cfg.isin(CONFIGS)]
        ev.append(('Tool-run calls with a requested-\nversus-resolved parameter check', 'galaxy',
                   int((tr.prov_status.isin(['matched', 'mismatch']) &
                        tr.checked_parameter_count.fillna(0).gt(0)).sum()), len(tr)))
    jobs = nc.analysis()['jobs']
    ev.append(('Galaxy jobs whose tool identifier includes\nthe wrapper version (all archived jobs)', 'galaxy',
               sum(1 for j in jobs if '/' in j['tool']), len(jobs)))
    ax = fig.add_axes([0.22, 0.62, 0.26, 0.29])
    labels = list(dict.fromkeys(e[0] for e in ev))
    rows = []
    for lab, e, n, d in ev:
        i = labels.index(lab)
        dy = -0.17 if e == 'open_ended_code' else (0.17 if lab == labels[0] else 0)
        ax.barh(i + dy, 100 * n / d, height=0.3, color=ENV_COLOR[e])
        ax.text(100 * n / d + 1.5, i + dy, f'{fmt(100 * n / d)}% ({n:,} of {d:,})', va='center', fontsize=5.0)
        rows.append(dict(evidence=lab.replace('\n', ' '), env=e, numerator=n, denominator=d, percent=100 * n / d))
    for i, lab in enumerate(labels[1:], start=1):
        ax.text(1.5, i - 0.3, 'open-ended code: not applicable', fontsize=5.0, color=INK2, va='center')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=5.2, linespacing=1.1)
    ax.set_ylim(len(labels) - 0.4, -0.6)
    ax.set_xlim(0, 135)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Runs, calls or jobs (%)')
    grid_x(ax)
    sd['a_evidence'] = pd.DataFrame(rows)
    if calls is not None:
        sd['a_parameter_check_calls'] = tr[['benchmark', 'task', 'run_id', 'cfg', 'replicate', 'line', 'result_line',
                                           'prov_status', 'checked_parameter_count', 'n_mismatches',
                                           'dataset_prov_status']].copy()
    hist = [r for r in rows if r['evidence'].startswith('Detailed')][0]
    for r in rows:
        if r['evidence'].startswith('Execution trace'):
            put(f'trace_{"code" if r["env"] == "open_ended_code" else "galaxy"}_primary', f'{r["numerator"]:,} of {r["denominator"]:,}')
    put('hist_primary', f'{hist["numerator"]:,} of {hist["denominator"]:,}')
    hist_all = cov[cov.env == 'galaxy']
    put('hist_all', f'{int((hist_all.history == "retrieved").sum()):,} of {len(hist_all):,}')
    put('trace_galaxy_all', f'{int(hist_all.trace.sum()):,} of {len(hist_all):,}')
    if calls is not None:
        chk = [r for r in rows if r['evidence'].startswith('Tool-run calls')][0]
        put('check_coverage_primary', f'{fmt(chk["percent"])}% ({chk["numerator"]:,} of {chk["denominator"]:,})')
    # ---------------- b: targeted audit attribution
    panel_label(fig, 0.53, 0.995, 'b')
    panel_title(fig, 0.53, 0.995, 'Primary cause in the targeted trace audit (93 task cases)')
    tc = pd.DataFrame(nc.fd()['task_cases'])
    tc['cat'] = tc.category.where(tc.category.isin(['C1', 'C2', 'C3', 'C4', 'C5']), 'C6+')
    ax = fig.add_axes([0.64, 0.66, 0.20, 0.24])
    rows = []
    for i, b in enumerate(['All', 'BixBench50', 'CompBio', 'IWC']):
        x = tc if b == 'All' else tc[tc.benchmark == b]
        left = 0
        for k, lab, col in CAUSE_CATS:
            v = int((x.cat == k).sum())
            rows.append(dict(benchmark=b, primary_cause=lab.replace('\n', ' '), task_cases=v))
            if v:
                ax.barh(i, v, left=left, color=col, edgecolor='white', lw=0.4, height=0.64)
                if v >= 4:
                    ax.text(left + v / 2, i, str(v), ha='center', va='center', fontsize=5, color='white' if col == NEUTRAL_DARK else INK)
                left += v
        ax.text(left + 1, i, str(len(x)), va='center', fontsize=5, color=INK2)
    ax.set_yticks(range(4))
    ax.set_yticklabels(['All three', 'BixBench-\nVerified-50', 'CompBioBench', 'IWC'], fontsize=5.2, linespacing=1.1)
    ax.set_ylim(3.6, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Task cases')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=c, label=l) for _, l, c in CAUSE_CATS], loc='upper left', bbox_to_anchor=(1.01, 1.08), fontsize=5.0,
              labelspacing=0.45)
    ax.text(0, -0.40, 'Outcome-selected task cases plus one near-perfect IWC\ncase (AI-assisted trace review). Not an exhaustive audit\n'
            'of all runs; causes are not split by condition.', transform=ax.transAxes, fontsize=5.0,
            color=INK2, va='top')
    sd['b_audit'] = pd.DataFrame(rows)
    allc = {r['primary_cause']: r['task_cases'] for r in rows if r['benchmark'] == 'All'}
    put('audit_cases', str(len(tc)))
    for k, lab, _ in CAUSE_CATS:
        put(f'audit_{k.replace("+", "plus")}', str(allc[lab.replace(chr(10), ' ')]))
    # ---------------- c: execution location
    panel_label(fig, 0.005, 0.44, 'c')
    panel_title(fig, 0.005, 0.44, 'Execution location in Galaxy-condition runs: an all-run screen and confirmed cases')
    ax = fig.add_axes([0.22, 0.09, 0.26, 0.27])
    rows = []
    for i, b in enumerate(style.BENCH):
        x = prim[(prim.env == 'galaxy') & (prim.benchmark == b)]
        n = int(x.indicators.apply(len).gt(0).sum())
        ax.barh(i, 100 * n / len(x), color=ENV_TINT['galaxy'], edgecolor=GALAXY, lw=0.5, height=0.6)
        ax.text(100 * n / len(x) + 1.5, i, f'{fmt(100 * n / len(x))}% ({n:,} of {len(x):,})', va='center', fontsize=5)
        rows.append(dict(benchmark=BL[b], galaxy_runs=len(x), runs_with_analysis_software_named_in_shell=n))
        put(f'screen_{b}', f'{fmt(100 * n / len(x))}%')
    ax.set_yticks(range(3))
    ax.set_yticklabels([BL[b] for b in style.BENCH], fontsize=5.3)
    ax.set_ylim(2.5, -0.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Galaxy-condition runs whose shell commands named\nan analysis program (unvalidated screen; not verified execution)')
    grid_x(ax)
    sd['c_screen'] = pd.DataFrame(rows)
    integ = nc.fd()['integrity']
    n_ret = len({t for v in integ['retrieval'].values() for t in v})
    conf = [(f"{len(integ['local_fallback_correct']) + len(integ['local_fallback_incorrect'])} CompBioBench Galaxy-condition answers were computed\n"
             f"in the local shell after user-defined-tool execution became unavailable\n({len(integ['local_fallback_correct'])} scored correct)"),
            f"{len(integ['cross_run'])} Galaxy-condition answers were copied from other runs\nthrough the shared Galaxy account",
            f"{n_ret} task cases in which agents retrieved, or tried to retrieve,\nbenchmark answers online (both conditions)"]
    axn = fig.add_axes([0.55, 0.09, 0.44, 0.27])
    axn.axis('off')
    axn.text(0, 1.0, 'Confirmed in the targeted audit (observed cases, not prevalence):', fontsize=5.4, fontweight='bold', va='top',
             transform=axn.transAxes)
    for i, t in enumerate(conf):
        axn.text(0.02, 0.82 - i * 0.28, '•  ' + t.replace('\n', '\n    '), fontsize=5.2, va='top', transform=axn.transAxes, linespacing=1.2)
    put('local_answers', str(len(integ['local_fallback_correct']) + len(integ['local_fallback_incorrect'])))
    put('local_answers_correct', str(len(integ['local_fallback_correct'])))
    put('cross_run', str(len(integ['cross_run'])))
    put('retrieval_tasks', str(n_ret))
    sd['c_confirmed'] = pd.DataFrame(dict(finding=[t.replace('\n', ' ') for t in conf]))
    nc.save_figure(fig, PAPER, 'Fig5', TITLES['Fig5'])
    nc.source_data(PAPER, 'Fig5', sd, TITLES['Fig5'])


# ---------------------------------------------------------------------------------------------------- Figure 6
GALAXY_RISKS = [
    ('Underlying software version not shown\n(current definition; reference used a retired one)', 'bix-45-q1', 15, 15),
    ('Staged file names without extensions\nswitched off adapter trimming', 'encode-atac-pipeline-q1', 7, 12),
    ('Wrapper output semantics (variance under\nthe metric name; header line counted)', 'bix-28-q3, bix-52-q7', 3, 30),
    ('Conditional parameter rebound to its\ndefault without a flag', 'bix-35-q1', 1, 15),
    ('Reference database job did not complete;\nfallback database lacked the organism', 'contaminated-rna-q1', 3, 12),
    ('User-defined tool never dispatched;\nagent substituted another method', 'bix-31-q2', 2, 15),
]


def fig6():
    fig = new_fig(150)
    sd = {}
    S = nc.summaries()
    S = S.assign(uncached=S.input_tokens - S.cached)
    # ---------------- a: token decomposition, complete cells
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'Token use, Galaxy ÷ open-ended code (complete cells)')
    ax = fig.add_axes([0.16, 0.62, 0.28, 0.28])
    kinds = [('input_tokens', 'All input (incl. cached)', 'o'), ('uncached', 'Uncached input', 'D'), ('output_tokens', 'Output', 's')]
    rows = []
    cell_observations = []
    for i, b in enumerate(style.BENCH):
        for k, (col, lab, mk) in enumerate(kinds):
            (est, lo, hi), n, elig, observations = cell_ratio(S, col, b)
            cell_observations.append(observations.assign(benchmark=BL[b], token_kind=lab))
            yy = i * 1.3 + (k - 1) * 0.3
            ax.plot([lo, hi], [yy, yy], color=GALAXY, lw=0.8)
            ax.plot(est, yy, mk, ms=3.1, mfc=GALAXY if k == 0 else 'white', mec=GALAXY, mew=0.8)
            ax.text(1.02, yy, f'{fmt(est)}', transform=ax.get_yaxis_transform(), fontsize=5.0, va='center')
            rows.append(dict(benchmark=BL[b], token_kind=lab, median_ratio=est, ci95_low=lo, ci95_high=hi, complete_cells=n, eligible_cells=elig))
            key = {'BixBench50': 'bix', 'CompBio': 'cb', 'IWC': 'iwc'}[b]
            put(f'{key}_tok_{col}', f'{fmt(est)} ({fmt(lo)} to {fmt(hi)})')
            put(f'{key}_tok_cells', f'{n} of {elig}')
            if k == 0:
                TOK_IN[b] = est
    put('tok_input_range', f'{fmt(min(TOK_IN.values()))} to {fmt(max(TOK_IN.values()))}')
    ax.axvline(1, color=INK2, lw=0.6, ls=(0, (2, 2)))
    ax.set_xscale('log')
    ax.set_xlim(0.5, 10)
    plain_log(ax, [0.5, 1, 2, 5, 10])
    ax.set_yticks([0, 1.3, 2.6])
    ax.set_yticklabels([BL[b].replace('-50', '-\n50') for b in style.BENCH], fontsize=5.2, linespacing=1.1)
    ax.set_ylim(3.05, -0.45)
    ax.set_xlabel('Median within task × configuration (log; 95% CI)')
    grid_x(ax)
    ax.legend(handles=[Line2D([], [], marker=m, ls='', mfc=GALAXY if k == 0 else 'white', mec=GALAXY, ms=3.2, label=l)
                       for k, (_, l, m) in enumerate(kinds)], loc='upper left', bbox_to_anchor=(-0.45, -0.24), ncol=3, fontsize=5)
    sd['a_tokens'] = pd.DataFrame(rows)
    sd['a_complete_cell_observations'] = pd.concat(cell_observations, ignore_index=True)
    # ---------------- b: retrospective strategies at observed token use
    panel_label(fig, 0.53, 0.995, 'b')
    panel_title(fig, 0.53, 0.995, 'Accuracy against observed tokens for four strategies')
    v = nc.vote_sets()
    v = v[v.cfg.isin(CONFIGS)]
    r = nc.runs()
    sd['b_single_run_tokens'] = r[r.benchmark.isin(['BixBench50', 'CompBio']) & r.cfg.isin(CONFIGS)][
        ['benchmark', 'task', 'cfg', 'env', 'replicate', 'input_tokens']].copy()
    rows = []
    for j, b in enumerate(['BixBench50', 'CompBio']):
        ax = fig.add_axes([0.62 + j * 0.19, 0.62, 0.15, 0.28])
        for e in ENVS:
            x = v[(v.benchmark == b) & (v.env == e)]
            one_tok = r[(r.benchmark == b) & (r.env == e) & r.cfg.isin(CONFIGS)].input_tokens.median() / 1e6
            three_tok = x.input_tokens_three_runs.median() / 1e6
            one_acc, vote_acc = 100 * x.single.mean(), 100 * x.vote_A.mean()
            ax.plot([one_tok, three_tok], [one_acc, vote_acc], color=ENV_COLOR[e], lw=0.8)
            dot(ax, one_tok, one_acc, e, filled=False, ms=3.6)
            dot(ax, three_tok, vote_acc, e, ms=3.6)
            rows.append(dict(benchmark=BL[b], env=e, strategy='one run', median_input_tokens_million=one_tok, accuracy=one_acc))
            rows.append(dict(benchmark=BL[b], env=e, strategy='three runs, outcome-blind majority vote (rule A)',
                             median_input_tokens_million=three_tok, accuracy=vote_acc))
            key = ('bix' if b == 'BixBench50' else 'cb') + ('_code' if e == 'open_ended_code' else '_gal')
            put(f'{key}_vote', fmt(vote_acc))
            put(f'{key}_vote_B', fmt(100 * x.vote_B.mean()))
            put(f'{key}_vote_oracle', fmt(100 * x.oracle.mean()))
            put(f'{key}_one_tok', fmt(one_tok, 2))
            put(f'{key}_three_tok', fmt(three_tok, 2))
            put(f'{key}_single', fmt(one_acc))
        ax.set_xscale('log')
        ax.set_xlim(0.3, 20)
        plain_log(ax, [0.3, 1, 3, 10])
        ax.set_ylim(78, 92)
        ax.set_title(BL[b], fontsize=5.4, loc='left')
        ax.set_xlabel('Median input tokens per task\n(millions, log)')
        if j == 0:
            ax.set_ylabel('Accuracy (%)')
        grid_x(ax)
        ax.yaxis.grid(True, color=GRID, lw=0.4)
    h = env_handles(ms=3.2) + [Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, ms=3.4, label='One run'),
                               Line2D([], [], marker='o', ls='', mfc=INK2, mec='white', ms=3.4, label='Three runs + vote')]
    fig.legend(handles=h, loc='upper left', bbox_to_anchor=(0.60, 0.50), ncol=2, fontsize=5)
    sd['b_strategies'] = pd.DataFrame(rows)
    sd['b_voting_sets'] = v.copy()
    # ---------------- c: actions
    panel_label(fig, 0.005, 0.44, 'c')
    panel_title(fig, 0.005, 0.44, 'Actions per run, Galaxy ÷ open-ended code')
    act = nc.od(6, 'a_ratio_galaxy_over_code')
    rows = []
    for j, b in enumerate(style.BENCH):
        ax = fig.add_axes([0.16 + j * 0.10, 0.10, 0.075, 0.25])
        for i, c in enumerate(CONFIGS):
            q = act[(act.benchmark == b) & (act.cfg == c)].iloc[0]
            sig = q.p_holm < 0.05
            ax.plot([q.ratio_ci95_low, q.ratio_ci95_high], [i, i], color=INK, lw=0.8)
            ax.plot(q.median_ratio_galaxy_over_code, i, 'D', ms=2.8, mfc=INK if sig else 'white', mec=INK, mew=0.7)
            rows.append(dict(benchmark=BL[b], cfg=c, median_ratio=q.median_ratio_galaxy_over_code, ci95_low=q.ratio_ci95_low,
                             ci95_high=q.ratio_ci95_high, p_holm=q.p_holm))
        ax.axvline(1, color=INK2, lw=0.6, ls=(0, (2, 2)))
        ax.set_xscale('log')
        ax.set_xlim(0.6, 5)
        plain_log(ax, [1, 2, 4])
        ax.set_ylim(3.6, -0.6)
        ax.set_yticks(range(4))
        ax.set_yticklabels([CFG_SHORT[c] for c in CONFIGS] if j == 0 else [], fontsize=5.1)
        ax.set_title(BL[b].replace('-50', '-\n50'), fontsize=5.1, loc='left', linespacing=1.05)
        grid_x(ax)
        if j == 1:
            ax.set_xlabel('Median ratio (filled: Holm-adjusted P < 0.05)')
    sd['c_actions'] = pd.DataFrame(rows)
    ra = pd.DataFrame(rows)
    for b, k in [('BixBench-Verified-50', 'bix'), ('CompBioBench', 'cb'), ('IWC', 'iwc')]:
        x = ra[ra.benchmark == b]
        put(f'{k}_actions_range', f'{fmt(x.median_ratio.min())} to {fmt(x.median_ratio.max())}')
        put(f'{k}_actions_sig', f'{int((x.p_holm < 0.05).sum())} of {len(x)}')
    # ---------------- d: Galaxy-specific failure modes
    panel_label(fig, 0.53, 0.44, 'd')
    panel_title(fig, 0.53, 0.44, 'Galaxy-specific mechanisms behind scored-incorrect runs')
    ax = fig.add_axes([0.80, 0.10, 0.12, 0.27])
    rows = []
    for i, (lab, task, n, of) in enumerate(GALAXY_RISKS):
        ax.barh(i, n, color=GALAXY, height=0.6)
        ax.text(n + 0.3, i, f'{n} of {of}', va='center', fontsize=5)
        rows.append(dict(mechanism=lab.replace('\n', ' '), tasks=task, scored_incorrect_galaxy_runs=n, galaxy_runs_of_task=of,
                         source='individual_error_analysis.md (targeted audit)'))
    ax.axhline(3.5, color=INK2, lw=0.5, ls=(0, (2, 2)))
    ax.set_yticks(range(len(GALAXY_RISKS)))
    ax.set_yticklabels([f'{x[0]}\n({x[1]})' for x in GALAXY_RISKS], fontsize=5.0, linespacing=1.05)
    ax.set_ylim(len(GALAXY_RISKS) - 0.4, -0.6)
    ax.set_xlim(0, 19)
    ax.set_xlabel('Galaxy runs (all\nfive configurations)')
    grid_x(ax)
    ax.text(1.0, 3.35, 'no job error', ha='right', va='bottom', fontsize=5.0, color=INK2, transform=ax.get_yaxis_transform())
    ax.text(1.0, 3.65, 'job failed', ha='right', va='top', fontsize=5.0, color=INK2, transform=ax.get_yaxis_transform())
    sd['d_galaxy_mechanisms'] = pd.DataFrame(rows)
    put('galaxy_specific_runs', str(sum(r['scored_incorrect_galaxy_runs'] for r in rows)))
    put('galaxy_specific_mechanisms', str(len(rows)))
    nc.save_figure(fig, PAPER, 'Fig6', TITLES['Fig6'])
    nc.source_data(PAPER, 'Fig6', sd, TITLES['Fig6'])


# ---------------------------------------------------------------------------------------------------- Extended Data
def save_ed(fig, name, sheets):
    nc.save_figure(fig, PAPER, name, TITLES[name])
    nc.source_data(PAPER, name, sheets, TITLES[name])


def scorecard_rows():
    g = nc.graded_runs()
    sets = nc.replicate_sets()
    rows = []
    for b, lab in [('BixBench50', 'BixBench-Verified-50 accuracy'), ('CompBio', 'CompBioBench reconstructed-key agreement')]:
        arr = nc.paired_cluster_arrays(g[(g.benchmark == b) & g.cfg.isin(CONFIGS)], 'score')
        rows.append(('Accuracy', lab, 'higher', f'{fmt(100 * arr[0].sum() / arr[1].sum())}%', f'{fmt(100 * arr[2].sum() / arr[3].sum())}%',
                     *nc.boot_rel(*arr)))
    arr = nc.paired_cluster_arrays(g[g.benchmark == 'IWC'].assign(cluster=lambda d: d.task), 'score')
    rows.append(('Accuracy', 'IWC mean output agreement (nine tasks)', 'higher', fmt(arr[0].sum() / arr[1].sum(), 3),
                 fmt(arr[2].sum() / arr[3].sum(), 3), *nc.boot_rel(*arr)))
    for b, lab in [('BixBench50', 'BixBench-Verified-50'), ('CompBio', 'CompBioBench'), ('IWC', 'IWC (nine tasks)')]:
        q = sets[(sets.benchmark == b) & sets.cfg.isin(CONFIGS)].assign(split=lambda d: (d.cat == 'split').astype(int))
        if b == 'IWC':
            q = q.assign(cluster=q.task)
        arr = nc.paired_cluster_arrays(q, 'split')
        rows.append(('Repeatability', f'Discordant replicate sets, {lab}', 'lower', f'{int(arr[0].sum())} of {int(arr[1].sum())}',
                     f'{int(arr[2].sum())} of {int(arr[3].sum())}', *nc.boot_rel(*arr)))
        if b == 'IWC':
            put('iwc_disc_ratio', f'{fmt(rows[-1][5], 2)} ({fmt(rows[-1][6], 2)} to {fmt(rows[-1][7], 2)})')
    for b, lab in [('BixBench50', 'BixBench-Verified-50'), ('CompBio', 'CompBioBench')]:
        q = sets[(sets.benchmark == b) & sets.cfg.isin(CONFIGS)].assign(u=lambda d: (d.cat == '3/3').astype(int))
        arr = nc.paired_cluster_arrays(q, 'u')
        rows.append(('Repeatability', f'Tasks with all three runs correct, {lab}', 'higher', f'{fmt(100 * arr[0].sum() / arr[1].sum())}%',
                     f'{fmt(100 * arr[2].sum() / arr[3].sum())}%', *nc.boot_rel(*arr)))
    err = nc.od(5, 'abc_every_error')
    cmap = cluster_map()
    err['cluster'] = [cmap[(b, t)] for b, t in zip(err.benchmark, err.task)]
    err = err[err.cfg.isin(CONFIGS)].assign(rec=lambda d: d.run_ended_correct.astype(int))
    for b in style.BENCH:
        arr = nc.paired_cluster_arrays(err[err.benchmark == b], 'rec')
        rows.append(('Error/outcome association', f'Errors occurring in runs that ended correct, {BL[b]}', 'descriptive', f'{fmt(100 * arr[0].sum() / arr[1].sum(), 0)}%',
                     f'{fmt(100 * arr[2].sum() / arr[3].sum(), 0)}%', *nc.boot_rel(*arr)))
    S = nc.summaries()
    for b in style.BENCH:
        (est, lo, hi), n, elig, _ = cell_ratio(S.assign(uncached=S.input_tokens - S.cached), 'uncached', b)
        rows.append(('Cost', f'Uncached input tokens per run, {BL[b]}', 'lower', '', '', est, lo, hi))
    return pd.DataFrame(rows, columns=['group', 'measure', 'better', 'open_ended_code', 'galaxy', 'ratio', 'ci95_low', 'ci95_high'])


def figed():
    # ---------------- ED Fig. 1: scorecard
    sc = scorecard_rows()
    fig = new_fig(110)
    panel_title(fig, -0.013, 0.995, 'Galaxy ÷ open-ended code for user-facing measures (four Codex model configurations)')
    ax = fig.add_axes([0.40, 0.08, 0.25, 0.82])
    groups = list(dict.fromkeys(sc.group))
    y, ypos, gy = 0, [], {}
    for gname in groups:
        gy[gname] = y
        y += 0.9
        for _ in range((sc.group == gname).sum()):
            ypos.append(y)
            y += 1
        y += 0.3
    sc['y'] = ypos
    ax.set_xscale('log')
    ax.set_xlim(0.1, 12)
    ax.set_ylim(y - 0.2, -0.3)
    ax.axvline(1, color=INK2, lw=0.6, ls=(0, (2, 2)))
    grid_x(ax)
    for r in sc.itertuples():
        if r.better == 'descriptive':
            ax.plot([max(r.ci95_low, 0.1), min(r.ci95_high, 12)], [r.y, r.y], color=INK2, lw=0.9)
            ax.plot(r.ratio, r.y, 'o', ms=3.6, mfc=INK2, mec='white', mew=0.4)
            continue
        fav = (r.ratio > 1) == (r.better == 'higher')
        e = 'galaxy' if fav else 'open_ended_code'
        excl = (r.ci95_low > 1) or (r.ci95_high < 1)
        ax.plot([max(r.ci95_low, 0.1), min(r.ci95_high, 12)], [r.y, r.y], color=ENV_COLOR[e], lw=0.9)
        dot(ax, r.ratio, r.y, e, filled=excl, ms=3.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    plain_log(ax, [0.1, 0.2, 0.5, 1, 2, 5, 10])
    ax.set_xlabel('Galaxy ÷ open-ended code (log; 95% CI)')
    tr = ax.get_yaxis_transform()
    for gname in groups:
        ax.text(-1.55, gy[gname] + 0.35, gname, transform=tr, fontsize=5.8, fontweight='bold', va='center')
    for r in sc.itertuples():
        ax.text(-1.55, r.y, r.measure, transform=tr, fontsize=5.2, va='center')
        direction = 'descriptive only' if r.better == 'descriptive' else f'{r.better} better'
        ax.text(-0.03, r.y, direction, transform=tr, fontsize=5.0, va='center', ha='right', color=INK2)
        ax.text(1.04, r.y, r.open_ended_code, transform=tr, fontsize=5.2, va='center')
        ax.text(1.30, r.y, r.galaxy, transform=tr, fontsize=5.2, va='center')
        ax.text(1.52, r.y, f'{fmt(r.ratio, 2)} ({fmt(r.ci95_low, 2)} to {fmt(r.ci95_high, 2)})', transform=tr, fontsize=5.2, va='center')
    for x, t in [(1.04, 'Code'), (1.30, 'Galaxy'), (1.52, 'Ratio (95% CI)')]:
        ax.text(x, -0.6, t, transform=tr, fontsize=5.4, fontweight='bold', va='bottom')
    fig.legend(handles=[Line2D([], [], marker='o', ls='', mfc=GALAXY, mec='white', ms=4, label='Point estimate favours Galaxy'),
                        Line2D([], [], marker='s', ls='', mfc=CODE, mec='white', ms=4, label='Favours open-ended code'),
                        Line2D([], [], marker='o', ls='', mfc='white', mec=INK2, ms=4, label='Open: interval includes 1'),
                        Line2D([], [], marker='o', ls='', mfc=INK2, mec='white', ms=4, label='Grey: descriptive association')],
               loc='lower left', bbox_to_anchor=(0.0, 0.0), ncol=4, fontsize=5)
    save_ed(fig, 'ED_Fig1', {'scorecard': sc.drop(columns='y')})
    # ---------------- ED Fig. 2: task scatter and answer agreement
    fig = new_fig(80)
    g = nc.graded_runs()
    rows = []
    for j, b in enumerate(['BixBench50', 'CompBio']):
        ax = fig.add_axes([0.06 + j * 0.30, 0.16, 0.22, 0.68])
        x = g[(g.benchmark == b) & g.cfg.isin(CONFIGS)].groupby(['task', 'env']).score.sum().unstack()
        cnt = x.groupby(['open_ended_code', 'galaxy']).size().reset_index(name='k')
        ax.plot([0, 12], [0, 12], color=INK2, lw=0.5, ls=(0, (2, 2)))
        for r in cnt.itertuples():
            env = 'galaxy' if r.galaxy > r.open_ended_code else ('open_ended_code' if r.galaxy < r.open_ended_code else None)
            ax.scatter(r.open_ended_code, r.galaxy, s=5 + 9 * np.sqrt(r.k), marker=ENV_MARKER[env] if env else 'o',
                       c=ENV_COLOR[env] if env else NEUTRAL_MID, edgecolors='white', linewidths=0.3)
        d = x.galaxy - x.open_ended_code
        ax.set_title(f'{BL[b]} ({len(x)} tasks): Galaxy higher {int((d > 0).sum())},\ncode higher {int((d < 0).sum())}, tied {int((d == 0).sum())}',
                     fontsize=5.3, loc='left', linespacing=1.1)
        ax.set_xlim(-0.6, 12.6), ax.set_ylim(-0.6, 12.6)
        ax.set_xticks(range(0, 13, 3)), ax.set_yticks(range(0, 13, 3))
        ax.set_xlabel('Code: runs correct (of 12)')
        ax.set_ylabel('Galaxy: runs correct (of 12)')
        rows += [dict(benchmark=BL[b], task=t, correct_code=int(a), correct_galaxy=int(c_)) for t, a, c_ in zip(x.index, x.open_ended_code, x.galaxy)]
    sd2 = {'a_tasks': pd.DataFrame(rows)}
    ag = answer_pair_agreement()
    ax = fig.add_axes([0.76, 0.22, 0.16, 0.55])
    rows = []
    for i, b in enumerate(['BixBench50', 'CompBio']):
        q = ag[ag.benchmark == b]
        est, lo, hi = nc.boot_diff(*nc.paired_cluster_arrays(q, 'agree', den='pairs'), scale=100)
        v = {e: 100 * q[q.env == e].agree.sum() / q[q.env == e].pairs.sum() for e in ENVS}
        ax.plot([v['open_ended_code'], v['galaxy']], [i, i], color=NEUTRAL_MID, lw=0.8)
        for e in ENVS:
            dot(ax, v[e], i, e)
        ax.text(1.03, i, f'{fmt(est, 1, True)}\n({fmt(lo)} to {fmt(hi)})', transform=ax.get_yaxis_transform(), fontsize=5.0, va='center')
        rows.append(dict(benchmark=BL[b], open_ended_code=v['open_ended_code'], galaxy=v['galaxy'], difference=est, ci95_low=lo, ci95_high=hi))
        key = 'bix' if b == 'BixBench50' else 'cb'
        put(f'{key}_answer_agree', f'{fmt(v["galaxy"])}% versus {fmt(v["open_ended_code"])}%')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['BixBench-\nVerified-50', 'CompBioBench'], fontsize=5.2)
    ax.set_ylim(1.6, -0.6)
    ax.set_xlim(80, 95)
    ax.set_xlabel('Replicate-run pairs with the\nsame answer (%)')
    ax.set_title('Answer agreement', fontsize=5.3, loc='left')
    grid_x(ax)
    sd2['b_answer_agreement'] = pd.DataFrame(rows)
    panel_label(fig, 0.005, 0.99, 'a')
    panel_label(fig, 0.69, 0.99, 'b')
    save_ed(fig, 'ED_Fig2', sd2)
    # ---------------- ED Fig. 3: execution errors by type
    ERR = [('Code, parameter or syntax error', 'Code, parameter or syntax', OI_ORANGE),
           ('Missing software, package or container', 'Missing software, package or container', OI_SKY),
           ('File, path or input format', 'File, path or input format', OI_GREEN), ('Time or memory limit', 'Time or memory limit', OI_PURPLE),
           ('Galaxy job never started', 'Galaxy job never started', NEUTRAL_DARK), ('Other', 'Network, or no or unclassified message', NEUTRAL_LIGHT)]
    err = nc.od(5, 'abc_every_error')
    runs5 = nc.od(5, 'abc_runs')
    err = err[err.cfg.isin(CONFIGS)].copy()
    runs5 = runs5[runs5.cfg.isin(CONFIGS)]
    err['etype'] = err.error_type.where(err.error_type.isin([t for t, _, _ in ERR[:-1]]), 'Other')
    fig = new_fig(62)
    ax = fig.add_axes([0.25, 0.20, 0.52, 0.74])
    rows, y, yt, yl = [], 0, [], []
    for b in style.BENCH:
        for e in ENVS:
            n_runs = int(((runs5.benchmark == b) & (runs5.env == e)).sum())
            x = err[(err.benchmark == b) & (err.env == e)]
            left = 0
            for t, lab, col in ERR:
                v = (x.etype == t).sum() / n_runs
                ax.barh(y, v, left=left, color=col, edgecolor='white', lw=0.4, height=0.7)
                if v > 0.25:
                    ax.text(left + v / 2, y, fmt(v), ha='center', va='center', fontsize=5.0, color='white' if col == NEUTRAL_DARK else INK)
                left += v
                rows.append(dict(benchmark=BL[b], env=e, error_type=lab, errors=int((x.etype == t).sum()), runs=n_runs, errors_per_run=v))
            ax.text(left + 0.05, y, fmt(left, 2), va='center', fontsize=5, color=INK2)
            yt.append(y)
            yl.append(f'{BL[b]}, {"open-ended code" if e == "open_ended_code" else "Galaxy"}')
            y += 1
        y += 0.5
    ax.set_yticks(yt)
    ax.set_yticklabels(yl, fontsize=5.2)
    ax.set_ylim(y - 0.4, -0.6)
    ax.set_xlim(0, 5.2)
    ax.set_xlabel('Execution errors per run (mean)')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=c, label=l) for _, l, c in ERR], loc='upper left', bbox_to_anchor=(1.01, 1.0), fontsize=5)
    save_ed(fig, 'ED_Fig3', {'errors_per_run': pd.DataFrame(rows)})
    # ---------------- ED Fig. 4: voting rules
    v = nc.vote_sets()
    fig = new_fig(85)
    rows = []
    labs = CONFIGS + [SUPERSEDED]
    measures = [('single', 'One run', 'o', 'white'), ('oracle', 'At least 2 of 3\nscored correct (oracle)', 's', NEUTRAL_MID),
                ('vote_A', 'Answer vote, rule A\n(10 significant digits)', 'D', INK), ('vote_B', 'Answer vote, rule B\n(3 significant digits)', '^', INK2)]
    for j, b in enumerate(['BixBench50', 'CompBio']):
        for k, e in enumerate(ENVS):
            ax = fig.add_axes([0.16 + (2 * j + k) * 0.20, 0.20, 0.15, 0.66])
            for i, c in enumerate(labs):
                x = v[(v.benchmark == b) & (v.env == e) & (v.cfg == c)]
                if x.empty:
                    continue
                for m, lab, mk, fc in measures:
                    val = 100 * x[m].mean()
                    ax.plot(val, i, mk, ms=3.2, mfc=fc, mec=INK, mew=0.6)
                    rows.append(dict(benchmark=BL[b], env=e, cfg=c, measure=lab.replace('\n', ' '), accuracy=val,
                                     consensus_rate_A=100 * x.consensus_A.mean(), consensus_rate_B=100 * x.consensus_B.mean()))
            ax.set_ylim(len(labs) - 0.4, -0.6)
            ax.set_yticks(range(len(labs)))
            ax.set_yticklabels([CFG_SHORT[c] for c in labs] if (j, k) == (0, 0) else [], fontsize=5)
            ax.set_xlim(60, 100)
            ax.set_title(f'{BL[b]}\n{ENV_LABEL[e]}', fontsize=5.2, loc='left', linespacing=1.1)
            ax.set_xlabel('Accuracy (%)')
            grid_x(ax)
    fig.legend(handles=[Line2D([], [], marker=mk, ls='', mfc=fc, mec=INK, ms=3.4, label=lab.replace('\n', ' ')) for _, lab, mk, fc in measures],
               loc='lower left', bbox_to_anchor=(0.16, 0.0), ncol=4, fontsize=5)
    save_ed(fig, 'ED_Fig4', {'voting': pd.DataFrame(rows), 'replicate_sets': v.copy()})


def answer_pair_agreement(rel=1e-4):
    """Per replicate set: number of the three replicate pairs whose submitted answers agree (decimals within rel, integers exact)."""
    import itertools
    r = nc.runs()
    r = r[r.benchmark.isin(['BixBench50', 'CompBio']) & r.cfg.isin(CONFIGS)]

    def num(a):
        try:
            return float(str(a).strip().replace(',', '').rstrip('%'))
        except (TypeError, ValueError):
            return None

    def same(a, b):
        if not isinstance(a, str) or not isinstance(b, str):
            return False
        x, y = num(a), num(b)
        if x is not None and y is not None:
            if all(str(v).strip().lstrip('-').isdigit() for v in (a, b)):
                return x == y
            return abs(x - y) <= rel * max(abs(x), abs(y), 1e-300)
        return a.strip().lower().replace(' ', '') == b.strip().lower().replace(' ', '')
    rows = []
    for (b, t, c, e, cl), x in r.groupby(['benchmark', 'task', 'cfg', 'env', 'cluster']):
        a = list(x.sort_values('replicate').answer)
        if len(a) == 3:
            rows.append(dict(benchmark=b, task=t, cfg=c, env=e, cluster=cl, pairs=3,
                             agree=sum(same(a[i], a[j]) for i, j in itertools.combinations(range(3), 2))))
    return pd.DataFrame(rows)


if __name__ == '__main__':
    nc.outdirs(PAPER)
    design_numbers()
    which = sys.argv[1:] or ['1', '2', '3', '4', '5', '6', 'ed']
    for w in which:
        globals()[f'fig{w}']()
        print('Fig', w, 'done')
    save_numbers(fresh=not sys.argv[1:])
