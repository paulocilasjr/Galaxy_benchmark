"""Fig. 4: Task solution variability is model-dependent.

The panels answer the questions of Results section 3 of the outline:
a, which tools did each model use (the 15 installed Galaxy tools used in the most Galaxy runs, per model);
b, does variability differ by model and by benchmark, and is it a property of Galaxy (share of replicate sets whose
   three runs gave the same answer, by model, benchmark and condition; per-model trajectory similarity goes to the
   source data for the text);
c, is solution consistency related to task difficulty (trajectory similarity of each task against the share of its runs
   that were correct);
   whether path diversity is good, bad or neutral is answered in panel c's note (models compared on the same task);
d, do agents show less analytical rigor than they could, especially on harder tasks (in replicate sets with a wrong
   answer, whether the error was random, with answers differing between replicates, or systematic, with the same wrong
   answer in all three, by task difficulty).

A run trajectory is the set of analysis steps of a Galaxy run: the installed tools it ran (Tool Shed identifiers
without version) plus one step for any user-defined tool (UDT), whose names are chosen anew by the agent in each run.
Trajectory similarity is the mean pairwise Jaccard index of the three replicate trajectories of one task and model.
Trajectories come from
the jobs submitted through the agent interface, so they are measured in the Galaxy condition only; custom-code commands
are free text and have no comparable record. A run is correct when accepted or, for IWC, at >= 0.99 output agreement.
Intervals are 95% percentile cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules,
otherwise tasks). Writes figures/fig4.{svg,pdf,png}, figures/fig4_source_data.csv and prints the statistics.
"""
import glob
import io
import itertools
import json
import os
import re
import sys

import numpy as np
import pandas as pd
from scipy.stats import rankdata

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
import style  # noqa: E402  (sets rcParams on import)
from style import plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})
style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition

AN = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis')
GC = os.path.join(ROOT, 'manuscript_narrative', 'derived', 'galaxy_calls')
EVIDENCE = [os.path.join(ROOT, 'BixBench_50', 'analysis', '*', 'history_analysis_evidence.json'),
            os.path.join(ROOT, 'CompBio', 'analysis', '*', 'history_analysis_evidence.json')]
OUT = os.path.join(ROOT, 'figures')
B, SEED, B_PERM = 20000, 20261002, 20000
W, MM = 180.0, 1 / 25.4
CFG = style.CONFIGS
ENVS = style.ENVS                                    # custom code first, always
CODE, GAL = ENVS
BENCH = style.BENCH
BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
# Okabe-Ito orange and sky blue; IWC in light pink (Paul Tol), outlined so its nine tasks stay visible
BENCH_MARK = {'BixBench50': ('^', '#E69F00'), 'CompBio': ('D', '#56B4E9'), 'IWC': ('v', '#FFAABB')}
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
# Model identity, as in Fig. 5 (Paul Tol muted green, purple, sand and indigo); every pair differs by >= 25 (OKLab x 100)
# in normal vision and >= 13 under simulated colour-vision deficiencies.
MODEL_COLOR = dict(zip(CFG, ['#117733', '#AA4499', '#DDCC77', '#332288']))
TRACE_MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
               'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
               'codex_deepseek_v4_pro': 'DeepSeek V4 Pro'}     # the superseded Claude Code harness is excluded
TOOL_LABEL = {
    'toolshed.g2.bx.psu.edu/repos/iuc/filter_tabular/filter_tabular': 'Filter tabular',
    'Cut1': 'Cut columns',
    'toolshed.g2.bx.psu.edu/repos/iuc/datamash_ops/datamash_ops': 'Datamash',
    'toolshed.g2.bx.psu.edu/repos/devteam/column_maker/Add_a_column1': 'Compute column',
    'toolshed.g2.bx.psu.edu/repos/ufz/xlsx2tsv/xlsx2tsv': 'XLSX to TSV',
    'Filter1': 'Filter rows',
    'csv_to_tabular': 'CSV to tabular',
    'Grep1': 'Select lines',
    'toolshed.g2.bx.psu.edu/repos/devteam/bwa/bwa_mem': 'BWA-MEM',
    'toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_grep_tool': 'Search text (grep)',
    'toolshed.g2.bx.psu.edu/repos/goeckslab/phykit_metrics/phykit_metrics': 'PhyKIT metrics',
    'toolshed.g2.bx.psu.edu/repos/bgruening/text_processing/tp_sort_header_tool': 'Sort with header',
    'toolshed.g2.bx.psu.edu/repos/iuc/anndata_inspect/anndata_inspect': 'Inspect AnnData',
    'Grouping1': 'Group',
    'join1': 'Join datasets',
}
N_TOOLS = 15
SIM_BINS = [(0.0, 1 / 3, 'Low\n(< 0.33)'), (1 / 3, 2 / 3, 'Medium\n(0.33–0.67)'), (2 / 3, 1.01, 'High\n(≥ 0.67)')]
DIFF_BINS = [(0.0001, 0.25, '1–25'), (0.25, 0.50, '26–50'), (0.50, 0.75, '51–75'), (0.75, 1.0, '76–100')]
AGREE = [('differ', 'Random error: answers\ndiffer between replicates', '#009E73'),
         ('same_wrong', 'Systematic error: the\nsame wrong answer in all\nthree replicates', '#CC79A7'),
         ('mixed_grade', 'Same answer, graded\ndifferently', '#E8E8E8')]
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- statistics
def boot_means(frames, group_cols, value):
    point, num, den = None, 0.0, 0.0
    for _, d in frames.groupby('benchmark'):
        s = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='sum').fillna(0)
        n = d.pivot_table(index='cluster', columns=group_cols, values=value, aggfunc='count').fillna(0)
        wts = rng.multinomial(len(s), np.full(len(s), 1 / len(s)), size=B)
        num = num + wts @ s.values
        den = den + wts @ n.values
        point = (s.sum(), n.sum()) if point is None else (point[0] + s.sum(), point[1] + n.sum())
    est = point[0] / point[1]
    return est, pd.DataFrame(num / den, columns=est.index)


def model_effect_p(cells):
    """Permutation test of a model effect on trajectory similarity: model labels permuted within each task."""
    groups = [g for _, g in cells.groupby('task')]
    vals = [g.sim.values for g in groups]
    labs = [np.array([CFG.index(c) for c in g.cfg]) for g in groups]

    def stat(lab_list):
        s, n = np.zeros(len(CFG)), np.zeros(len(CFG))
        for v, l in zip(vals, lab_list):
            np.add.at(s, l, v)
            np.add.at(n, l, 1)
        m, grand = s / np.maximum(n, 1), sum(v.sum() for v in vals) / sum(len(v) for v in vals)
        return float(np.sum(n * (m - grand) ** 2))
    observed = stat(labs)
    hits = sum(stat([rng.permutation(l) for l in labs]) >= observed - 1e-12 for _ in range(B_PERM))
    return observed, (1 + hits) / (B_PERM + 1)


def spearman_perm(x, y, strata):
    """Spearman correlation with a permutation P value, y permuted within strata."""
    x, y, strata = np.asarray(x), np.asarray(y), np.asarray(strata)
    rx = rankdata(x)

    def rho(yy):
        return np.corrcoef(rx, rankdata(yy))[0, 1]
    observed = rho(y)
    idx = [np.where(strata == s)[0] for s in np.unique(strata)]
    hits = 0
    for _ in range(B_PERM):
        yy = y.copy()
        for i in idx:
            yy[i] = y[rng.permutation(i)]
        hits += abs(rho(yy)) >= abs(observed) - 1e-12
    return observed, (1 + hits) / (B_PERM + 1)


# ---------------------------------------------------------------- data
def load_runs():
    r = pd.read_csv(os.path.join(AN, 'accuracy_primary_runs.csv'))
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    return r


def load_calls():
    c = pd.read_csv(os.path.join(GC, 'calls.csv.gz'), low_memory=False,
                    usecols=['benchmark', 'task', 'model', 'replicate', 'tool', 'galaxy_server', 'n_jobs',
                             'tool_id_base'])
    c = c[c.model.isin(TRACE_MODEL) & c.galaxy_server].assign(cfg=lambda x: x.model.map(TRACE_MODEL))
    cov = pd.read_csv(os.path.join(GC, 'run_coverage.csv'))
    cov = cov[cov.model.isin(TRACE_MODEL)].assign(cfg=lambda x: x.model.map(TRACE_MODEL))
    return c, cov


def normalize_answer(x):
    """Answers compared as text after trimming and lower-casing; numbers to three significant digits."""
    if x is None:
        return None
    s = re.sub(r'\s+', ' ', str(x).strip().strip('"\'').lower())
    try:
        return f'{float(s):.3g}'
    except ValueError:
        return s.replace(' ', '')


def load_answers():
    """Submitted answer of every BixBench-Verified-50 and CompBioBench run (compared here, never written out)."""
    rows = []
    for path in sorted(p for pattern in EVIDENCE for p in glob.glob(pattern)):
        d = json.load(open(path))
        bm = 'BixBench50' if os.sep + 'BixBench_50' + os.sep in path else 'CompBio'
        for run in d['runs']:
            model = re.sub(r'_r\d+$', '', re.sub(r'^(galaxy|open_ended_code)_', '', run['run_id']))
            if model in TRACE_MODEL:
                rows.append(dict(benchmark=bm, task=d['task']['task_id'], cfg=TRACE_MODEL[model], env=run['condition'],
                                 replicate=run['replicate_id'],
                                 answer=normalize_answer((run.get('outcome') or {}).get('submitted_answer'))))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- panels: statistics
def panel_a(calls, cov):
    runs = cov.groupby('cfg').size()
    key = ['benchmark', 'task', 'model', 'replicate', 'cfg']
    used = calls[calls.tool == 'run_galaxy_tool_and_wait'].dropna(subset=['tool_id_base'])[key + ['tool_id_base']]
    used = used.drop_duplicates()
    overall = used.groupby('tool_id_base').size().sort_values(ascending=False) / runs.sum() * 100
    top = overall.head(N_TOOLS)
    missing = set(top.index) - set(TOOL_LABEL)
    assert not missing, f'add display names for {missing}'
    per = (used.groupby(['tool_id_base', 'cfg']).size().unstack(fill_value=0) / runs * 100).loc[top.index, CFG]
    udt = calls[calls.tool == 'run_galaxy_udt_and_wait'][key].drop_duplicates().groupby('cfg').size() / runs * 100
    return top, per, udt.reindex(CFG), runs.reindex(CFG)


def route_cells(calls, r):
    """Trajectory similarity of each task x model in the Galaxy condition (three runs, each with at least one job)."""
    ran = calls[calls.n_jobs.fillna(0) > 0]
    inst = ran[ran.tool == 'run_galaxy_tool_and_wait'].dropna(subset=['tool_id_base']).assign(step=lambda x: x.tool_id_base)
    udt = ran[ran.tool == 'run_galaxy_udt_and_wait'].assign(step='UDT')
    fp = pd.concat([inst, udt]).groupby(['benchmark', 'task', 'cfg', 'replicate']).step.agg(frozenset).reset_index()
    rows = []
    for (bm, task, c), g in fp.groupby(['benchmark', 'task', 'cfg']):
        if len(g) == 3:
            f = list(g.step)
            sims = [len(a & b) / len(a | b) for a, b in itertools.combinations(f, 2)]
            rows.append(dict(benchmark=bm, task=task, cfg=c, sim=float(np.mean(sims)), identical=len(set(f)) == 1,
                             steps=float(np.mean([len(x) for x in f]))))
    cells = pd.DataFrame(rows)
    acc = r[r.env == GAL].groupby(['benchmark', 'task', 'cfg']).agg(cluster=('cluster', 'first'), ok=('ok', 'mean'))
    cells = cells.join(acc, on=['benchmark', 'task', 'cfg'])
    return cells[cells.cluster.notna()].reset_index(drop=True)      # scored tasks only (IWC host removal is not)


def panel_b(cells):
    rows, tests = [], []
    for bm in BENCH:
        d = cells[cells.benchmark == bm]
        est, draws = boot_means(d, ['cfg'], 'sim')
        for c in CFG:
            rows.append(dict(benchmark=bm, cfg=c, value=est[c], lo=np.nanpercentile(draws[c], 2.5),
                             hi=np.nanpercentile(draws[c], 97.5), n=int((d.cfg == c).sum())))
        stat, p = model_effect_p(d)
        tests.append(dict(benchmark=bm, statistic=stat, p=p, cells=len(d), tasks=d.task.nunique()))
    return pd.DataFrame(rows), pd.DataFrame(tests)


def panel_c(cells, r):
    task = cells.groupby(['benchmark', 'task']).sim.mean().rename('sim').reset_index()
    acc = r.groupby(['benchmark', 'task']).ok.mean().rename('task_ok').reset_index()
    task = task.merge(acc, on=['benchmark', 'task'])
    task['correct'] = 100 * task.task_ok
    rho, p = spearman_perm(task.correct, task.sim, task.benchmark)
    per = {bm: spearman_perm(g.correct, g.sim, np.zeros(len(g)))[0] for bm, g in task.groupby('benchmark')}
    return task, dict(rho=rho, p=p, tasks=len(task), per_benchmark=per)


def panel_d(cells):
    c = cells.copy()
    c['bin'] = pd.cut(c.sim, [b[0] for b in SIM_BINS] + [SIM_BINS[-1][1]], right=False,
                      labels=[b[2] for b in SIM_BINS])
    est, draws = boot_means(c, ['bin'], 'ok')
    rows = [dict(bin=b, value=100 * est[b], lo=100 * np.nanpercentile(draws[b], 2.5), hi=100 * np.nanpercentile(draws[b], 97.5),
                 n=int((c.bin == b).sum())) for b in [x[2] for x in SIM_BINS]]
    # within-task association: models compared with each other on the same task
    within = c.assign(s_dm=c.sim - c.groupby('task').sim.transform('mean'), a_dm=c.ok - c.groupby('task').ok.transform('mean'))
    within = within[c.groupby('task').sim.transform('size') > 1]
    rho, p = spearman_perm(within.s_dm, within.a_dm, within.task)
    return pd.DataFrame(rows), dict(rho=rho, p=p, cells=len(within))


def panel_e(r, answers):
    d = r[r.benchmark != 'IWC'].merge(answers, on=['benchmark', 'task', 'cfg', 'env', 'replicate'], how='left')
    sets = d.groupby(['benchmark', 'task', 'cfg', 'env']).agg(
        n_ok=('ok', 'sum'), n_answers=('answer', lambda s: s.fillna('<no answer>').nunique())).reset_index()
    task_ok = r.groupby(['benchmark', 'task']).ok.mean().rename('task_ok')
    sets = sets.join(task_ok, on=['benchmark', 'task'])
    sets['incorrect'] = 1 - sets.task_ok
    err = sets[sets.n_ok < 3].copy()
    err['agree'] = np.select([err.n_answers > 1, err.n_ok == 0], ['differ', 'same_wrong'], 'mixed_grade')
    err['bin'] = pd.cut(err.incorrect, [DIFF_BINS[0][0]] + [b[1] for b in DIFF_BINS], include_lowest=True,
                        labels=[b[2] for b in DIFF_BINS])
    tab = pd.crosstab(err.bin, err.agree).reindex(index=[b[2] for b in DIFF_BINS], columns=[a[0] for a in AGREE],
                                                  fill_value=0)
    correct_differ = int(((sets.n_ok == 3) & (sets.n_answers > 1)).sum())
    return tab, dict(sets=len(sets), error_sets=len(err), correct_but_differ=correct_differ,
                     missing_answers=int(d.answer.isna().sum()))


def answer_agreement(r, answers):
    """Share of replicate sets whose three runs gave the same answer, by model and condition, for both benchmarks pooled
    and for BixBench-Verified-50 and CompBioBench apart, with a test of a model effect within each condition (model
    labels permuted within tasks)."""
    d = r[r.benchmark != 'IWC'].merge(answers, on=['benchmark', 'task', 'cfg', 'env', 'replicate'], how='left')
    sets = (d.groupby(['benchmark', 'cluster', 'task', 'cfg', 'env']).answer
            .agg(lambda s: int(s.fillna('<no answer>').nunique() == 1)).rename('same').reset_index())
    rows, tests = [], []
    for scope in ('both', 'BixBench50', 'CompBio'):          # pooled first, so its draws match the earlier build
        sub = sets if scope == 'both' else sets[sets.benchmark == scope]
        est, draws = boot_means(sub, ['cfg', 'env'], 'same')
        rows += [dict(scope=scope, cfg=c, env=e, value=100 * est[(c, e)], lo=100 * np.percentile(draws[(c, e)], 2.5),
                      hi=100 * np.percentile(draws[(c, e)], 97.5), n=int(((sub.cfg == c) & (sub.env == e)).sum()))
                 for c in CFG for e in ENVS]
        for env in ENVS:
            stat, p = model_effect_p(sub[sub.env == env].rename(columns={'same': 'sim'}))
            tests.append(dict(scope=scope, env=env, statistic=stat, p=p, sets=int((sub.env == env).sum())))
    return pd.DataFrame(rows), pd.DataFrame(tests)


# ---------------------------------------------------------------- drawing helpers
def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')


def fmt_p(p):
    if p < 0.001:
        return r'$\mathit{P}$ < 0.001'
    return rf'$\mathit{{P}}$ = {p:.2f}' if p >= 0.01 else rf'$\mathit{{P}}$ = {p:.3f}'


# ---------------------------------------------------------------- panels: drawing
def draw_a(fig, H, top, per, udt, runs):
    label(fig, 0, 0, 'a', f'Installed tools each model used ({N_TOOLS} most used)', H)
    x_lab, x0, pw, gap = 0.0, 27.0, 16.0, 1.8
    ytop, h = 15.0, 41.0
    labels = [TOOL_LABEL[t] for t in top.index]
    for j, c in enumerate(CFG):
        ax = axes_mm(fig, x0 + j * (pw + gap), ytop, pw, h, H)
        ax.barh(range(N_TOOLS), per[c].values, height=0.68, color=MODEL_COLOR[c], ec=style.INK if c == 'GPT-5.6 Luna'
                else 'none', lw=0.3, zorder=3)
        ax.set_ylim(N_TOOLS - 0.5, -0.5)
        ax.set_xlim(0, 25)
        ax.set_xticks([0, 10, 20])
        style.grid_x(ax)
        ax.tick_params(axis='y', length=0)
        if j == 0:
            ax.set_yticks(range(N_TOOLS), labels, fontsize=5)
            rank_x = -(x0 - x_lab - 1.2) / pw
            tr = blended_transform_factory(ax.transAxes, ax.transData)
            ax.text(rank_x, -1.25, 'Rank', transform=tr, ha='left', va='center', fontsize=5, color=style.INK2)
            for i in range(N_TOOLS):
                ax.text(rank_x + 0.08, i, f'{i + 1}', transform=tr, ha='center', va='center', fontsize=5,
                        color=style.INK2)
        else:
            ax.set_yticks(range(N_TOOLS), [''] * N_TOOLS)
            ax.spines['left'].set_visible(False)
        ax.set_title(c, fontsize=5.5, fontweight='bold', pad=8.0, loc='left')
        ax.text(0, 1.018, f'UDTs: {udt[c]:.0f}% of runs', transform=ax.transAxes, ha='left', va='bottom', fontsize=5,
                color=style.INK2)
        if j == 1:
            ax.text(1 + gap / pw / 2, -0.10, 'Galaxy runs using the tool (%)', transform=ax.transAxes,
                    ha='center', va='top', fontsize=5.5)
    fig.text(4.4 / W, 1 - 4.6 / H, f'Galaxy condition; {int(runs.min())}–{int(runs.max())} runs per model',
             fontsize=5, color=style.INK2, va='top')


def draw_b(fig, H, agree, agree_t):
    label(fig, 102.0, 0, 'b', 'Same answer in all three runs, by model', H)
    fig.text((102.0 + 4.4) / W, 1 - 4.6 / H, 'Share of replicate sets (one task, one model) whose three runs gave the '
             'same answer', fontsize=5, color=style.INK2, va='top')
    ax = axes_mm(fig, 113.0, 18.0, 65.0, 33.0, H)
    groups = [('BixBench50', 'BixBench-Verified-50'), ('CompBio', 'CompBioBench'), ('both', 'Both benchmarks')]
    a = agree.set_index(['scope', 'cfg', 'env'])
    for g, (scope, _) in enumerate(groups):
        for j, c in enumerate(CFG):
            for k, env in enumerate(ENVS):
                t = a.loc[(scope, c, env)]
                x = g * 1.15 + (j - 1.5) * 0.25 + (k - 0.5) * 0.10
                ax.errorbar(x, t.value, yerr=[[t.value - t.lo], [t.hi - t.value]], fmt=style.ENV_MARKER[env], ms=3.0,
                            mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, elinewidth=0.8, capsize=0, zorder=3,
                            ecolor=MODEL_COLOR[c] if c != 'GPT-5.6 Luna' else '#A8994A')
        if g:
            ax.axvline(g * 1.15 - 0.575, color=style.GRID if g == 1 else style.NEUTRAL_MID, lw=0.6, zorder=1)
    ax.set_ylim(55, 100)
    ax.set_yticks([60, 70, 80, 90, 100])
    style.grid_y(ax)
    ax.set_xticks([g * 1.15 for g in range(len(groups))], [name for _, name in groups], fontsize=5.5)
    ax.get_xticklabels()[-1].set_fontweight('bold')
    ax.tick_params(axis='x', length=0, pad=2)
    ax.set_xlim(-0.55, (len(groups) - 1) * 1.15 + 0.55)
    ax.set_ylabel('Same answer in all three runs (%)')
    at = agree_t.set_index(['scope', 'env'])
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    for g, (scope, _) in enumerate(groups):
        ax.text(g * 1.15, -0.13, f'custom code {fmt_p(at.loc[(scope, CODE), "p"])}\nGalaxy {fmt_p(at.loc[(scope, GAL), "p"])}',
                transform=tr, ha='center', va='top', fontsize=5, color=style.INK2, linespacing=1.2)
    ax.text(-0.55, -0.13, 'Models\ndiffer:', transform=tr, ha='right', va='top', fontsize=5, color=style.INK2,
            linespacing=1.2)
    models = [Line2D([], [], ls='', marker='o', ms=3.2, mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, label=c)
              for c in CFG]
    shapes = [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.0, mfc=style.NEUTRAL_MID, mec=style.INK, mew=0.35,
                     label=style.ENV_LABEL[e]) for e in ENVS]
    ax.add_artist(ax.legend(handles=models, ncol=4, loc='lower left', bbox_to_anchor=(0.0, 1.10), fontsize=5.3,
                            handletextpad=0.2, columnspacing=0.8, borderaxespad=0))
    ax.legend(handles=shapes, ncol=2, loc='lower left', bbox_to_anchor=(0.0, 1.02), fontsize=5.3, handletextpad=0.2,
              columnspacing=0.8, borderaxespad=0)


def draw_c(fig, H, y0, task, res, within):
    label(fig, 0, y0, 'c', 'Same trajectory and task accuracy', H)
    ax = axes_mm(fig, 11.0, y0 + 16.5, 64.0, 32.0, H)
    for bm in BENCH:
        t = task[task.benchmark == bm]
        m, col = BENCH_MARK[bm]
        jitter = rng.uniform(-1.2, 1.2, len(t))
        iwc = bm == 'IWC'
        ax.scatter(t.correct + jitter, t.sim, s=9 if iwc else 6, marker=m, facecolor=col,
                   edgecolor=style.INK2 if iwc else 'white', lw=0.3, alpha=1.0 if iwc else 0.85,
                   zorder=4 if iwc else 3, label=BENCH_NAME[bm])
    ax.set_xlim(-4, 104)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    style.grid_y(ax)
    ax.set_xlabel('Task accuracy: correct runs on the task (%)')
    ax.set_ylabel('Trajectory similarity (task mean)')
    rho = f'{res["rho"]:.2f}'.replace('-', '\u2212')
    fig.text(4.4 / W, 1 - (y0 + 4.6) / H, f'Galaxy; 1 = the same tools in all three runs (a UDT is one step)\n'
             f'Across tasks: Spearman ρ = {rho}, {fmt_p(res["p"])}; {res["tasks"]} tasks\n'
             f'Models on the same task, trajectory similarity against accuracy: ρ = {within["rho"]:.2f}, '
             f'{fmt_p(within["p"])}', fontsize=5, color=style.INK2, va='top', linespacing=1.25)
    ax.legend(loc='lower left', bbox_to_anchor=(0.0, 1.02), ncol=3, fontsize=5.0, handletextpad=0.1,
              columnspacing=0.5, borderaxespad=0, markerscale=1.2)


def draw_e(fig, H, y0, tab, info):
    label(fig, 86.0, y0, 'd', 'Wrong answers: random or systematic?', H)
    fig.text((86.0 + 4.4) / W, 1 - (y0 + 4.6) / H, 'Replicate sets (three runs of one task by one model) with at least '
             'one wrong answer;\nBixBench-Verified-50 and CompBioBench, both environments', fontsize=5, color=style.INK2,
             va='top', linespacing=1.25)
    ax = axes_mm(fig, 98.0, y0 + 16.5, 50.0, 32.0, H)
    xs = np.arange(len(tab))
    bottom = np.zeros(len(tab))
    totals = tab.sum(axis=1).values
    for code, lab, col in AGREE:
        v = 100 * tab[code].values / totals
        ax.bar(xs, v, bottom=bottom, width=0.7, color=col, ec='white', lw=0.4, zorder=3, label=lab)
        for x, b_, vv, n in zip(xs, bottom, v, tab[code].values):
            if vv >= 9:
                ax.text(x, b_ + vv / 2, f'{n}', ha='center', va='center', fontsize=5,
                        color='white' if col == '#009E73' else style.INK, zorder=4)
        bottom += v
    for x, n in zip(xs, totals):
        ax.text(x, 101.5, f'{n}', ha='center', va='bottom', fontsize=5, color=style.INK2)
    ticks = [f'{t}%' for t in tab.index]
    ticks[0], ticks[-1] = ticks[0] + '\n(easier)', ticks[-1] + '\n(harder)'
    ax.set_xticks(xs, ticks, fontsize=5)
    ax.tick_params(axis='x', length=0, pad=2)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Task difficulty: wrong runs on the task')
    ax.set_ylabel('Replicate sets with a wrong answer (%)')
    ax.text(1.0, 1.065, 'Sets', transform=ax.transAxes, ha='right', va='bottom', fontsize=5, color=style.INK2)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], loc='upper left', bbox_to_anchor=(1.04, 1.0), ncol=1, fontsize=5.0,
              handlelength=0.9, handletextpad=0.4, labelspacing=0.7, borderaxespad=0)


# ---------------------------------------------------------------- source data and assembly
def source_data(top, per, udt, runs, b_tab, b_t, task, c_res, d_tab, d_res, e_tab, e_info, agree, agree_t):
    rows = []
    for t in agree.itertuples():
        rows.append(dict(panel='b', benchmark={'both': 'BixBench50+CompBio'}.get(t.scope, t.scope), model=t.cfg, group=t.env,
                         measure='pct_sets_same_answer_all_three_runs', value=t.value, ci95_low=t.lo, ci95_high=t.hi,
                         n=t.n))
    for t in agree_t.itertuples():
        rows.append(dict(panel='b', benchmark={'both': 'BixBench50+CompBio'}.get(t.scope, t.scope), model='all four', group=t.env,
                         measure='model_effect_permutation', value=t.statistic, n=t.sets, p=t.p))
    for rank, t in enumerate(top.index, 1):
        for c in CFG:
            rows.append(dict(panel='a', benchmark='all', model=c, group=f'{rank}: {TOOL_LABEL[t]} ({t})',
                             measure='pct_galaxy_runs_using_tool', value=per.loc[t, c], n=int(runs[c])))
    for c in CFG:
        rows.append(dict(panel='a', benchmark='all', model=c, group='UDT', measure='pct_galaxy_runs_with_udt_call',
                         value=udt[c], n=int(runs[c])))
    for t in b_tab.itertuples():
        rows.append(dict(panel='text', benchmark=t.benchmark, model=t.cfg, measure='mean_trajectory_similarity', value=t.value,
                         ci95_low=t.lo, ci95_high=t.hi, n=t.n))
    for t in b_t.itertuples():
        rows.append(dict(panel='text', benchmark=t.benchmark, model='all four', measure='model_effect_permutation',
                         value=t.statistic, n=t.cells, p=t.p))
    for t in task.itertuples():
        rows.append(dict(panel='c', benchmark=t.benchmark, model='all four', group=t.task,
                         measure='task_trajectory_similarity', value=t.sim))
        rows.append(dict(panel='c', benchmark=t.benchmark, model='all four', group=t.task,
                         measure='task_pct_runs_correct', value=t.correct))
    rows.append(dict(panel='c', benchmark='all', model='all four', measure='spearman_rho', value=c_res['rho'],
                     n=c_res['tasks'], p=c_res['p']))
    for bm, rho in c_res['per_benchmark'].items():
        rows.append(dict(panel='c', benchmark=bm, model='all four', measure='spearman_rho', value=rho))
    for t in d_tab.itertuples():
        rows.append(dict(panel='text', benchmark='all', model='all four', group=t.bin.replace('\n', ' '),
                         measure='galaxy_runs_correct_pct', value=t.value, ci95_low=t.lo, ci95_high=t.hi, n=t.n))
    rows.append(dict(panel='c', benchmark='all', model='all four', group='within task',
                     measure='spearman_rho_similarity_accuracy', value=d_res['rho'], n=d_res['cells'], p=d_res['p']))
    for b_, t in e_tab.iterrows():
        for code, lab, _ in AGREE:
            rows.append(dict(panel='d', benchmark='BixBench50+CompBio', model='all four', group=f'{b_}% incorrect',
                             measure='sets_with_incorrect_run: ' + lab.replace('\n', ' '), value=int(t[code]),
                             n=int(t.sum())))
    for k, v in e_info.items():
        rows.append(dict(panel='d', benchmark='BixBench50+CompBio', model='all four', measure=k, value=v))
    cols = ['panel', 'benchmark', 'model', 'group', 'measure', 'value', 'ci95_low', 'ci95_high', 'n', 'p']
    pd.DataFrame(rows).reindex(columns=cols).round(4).to_csv(os.path.join(OUT, 'fig4_source_data.csv'), index=False)


def main():
    r = load_runs()
    calls, cov = load_calls()
    top, per, udt, runs = panel_a(calls, cov)
    cells = route_cells(calls, r)
    b_tab, b_t = panel_b(cells)
    task, c_res = panel_c(cells, r)
    d_tab, d_res = panel_d(cells)
    answers = load_answers()
    e_tab, e_info = panel_e(r, answers)
    global rng                              # separate random stream, so the draws of the other panels are unchanged
    main_rng, rng = rng, np.random.default_rng(SEED + 3)
    agree, agree_t = answer_agreement(r, answers)
    rng = main_rng
    print('b (right): answer agreement'); print(agree.round(2).to_string()); print(agree_t.round(4).to_string())
    for name, t in (('b: trajectory similarity', b_tab), ('b: model effect', b_t), ('d: accuracy by similarity', d_tab),
                    ('e: answer agreement in sets with an error', e_tab)):
        print(name)
        print(t.round(3).to_string())
    print('c:', {k: (round(v, 3) if isinstance(v, float) else v) for k, v in c_res.items()})
    print('d:', d_res, '| e:', e_info, '| cells:', len(cells))

    H = 131.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, top, per, udt, runs)
    draw_b(fig, H, agree, agree_t)
    y2 = 70.0
    draw_c(fig, H, y2, task, c_res, d_res)
    draw_e(fig, H, y2, e_tab, e_info)
    style.enforce_min_font(fig)
    title = 'Fig. 4 | Task solution variability is model-dependent'
    fig.savefig(os.path.join(OUT, 'fig4.svg'), metadata={'Title': title})
    fig.savefig(os.path.join(OUT, 'fig4.pdf'), metadata={'Title': title})
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, 'fig4.png'), dpi=(600, 600))
    source_data(top, per, udt, runs, b_tab, b_t, task, c_res, d_tab, d_res, e_tab, e_info, agree, agree_t)


if __name__ == '__main__':
    main()
