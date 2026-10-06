"""Fig. 2: Agents show similar observed benchmark performance in Galaxy and custom code.

Panels:
a, score of each model in each condition, one facet per benchmark and its own scoring contract: evaluator acceptance
   (BixBench-Verified-50), agreement with a reconstructed answer key (CompBioBench) and agreement with curated workflow
   outputs on a 0-1 scale (IWC); paired points with 95% intervals, and each replicate as a small dot;
b, the paired estimates: Galaxy minus custom code for each model and for the four models pooled, as two aligned groups
   that are never mixed in one row: the mean score (the primary endpoint of each benchmark) and the share of replicate
   sets with all three runs correct (reliability; IWC at >= 0.99 agreement);
c, correct runs of three for each task and model, custom code against Galaxy, one matrix per benchmark;
d, why the conditions disagree on BixBench-Verified-50: the AI-assisted audit's primary cause of each incorrect run,
   split by whether the task-model pair was discordant (one condition had more correct runs) or had the same count, with
   one traced discordant case (bix-45-q1, a tool-version difference).

Extended Data Fig. 2 (written by the same script): a, the full census of causes by the number of incorrect runs in the
set (the first version's panel d); b, sensitivity of the condition difference to the IWC correctness threshold and to
the archive's population sensitivities.

A run is correct when accepted or at >= 0.99 IWC output agreement. Intervals are 95% percentile cluster-bootstrap
intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). P values come from paired cluster
sign-flip randomization tests (200,000 draws, or exact enumeration with at most 16 clusters), Holm-adjusted within each
family. No test here is an equivalence test: the figure reports estimates and intervals.
Writes figures/fig2.{svg,pdf,png}, figures/fig2_source_data.csv, figures/ed_fig2.{svg,pdf,png} and
figures/ed_fig2_source_data.csv, and prints the statistics.
"""
import io
import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
import style  # noqa: E402  (sets rcParams on import)
from style import plt  # noqa: E402
from matplotlib.colors import LogNorm  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})
style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition

AN = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis')
LEDGER = os.path.join(ROOT, 'analysis_reports', 'galaxy_improvement_20260924', 'v2_trace_friction', 'ledger.json')
OUT = os.path.join(ROOT, 'figures')
B, SEED = 20000, 20261002
B_PERM = 200000          # randomization draws; Monte Carlo error on a Holm-adjusted P near 0.05 is below 0.003
W, MM = 180.0, 1 / 25.4
CFG = style.CONFIGS
ENVS = style.ENVS                                    # custom code first, always
CODE, GAL = ENVS
BENCH = style.BENCH
TICK = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6\nSol', 'GPT-5.6 Luna': 'GPT-5.6\nLuna',
        'DeepSeek V4 Pro': 'DeepSeek\nV4 Pro'}
BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
CONTRACT = {'BixBench50': 'evaluator acceptance', 'CompBio': 'reconstructed-key agreement',
            'IWC': 'workflow-output agreement (0–1)'}
# A run is correct when accepted; an IWC run when it reaches >= 0.99 output agreement (172 of 216 IWC runs), the rule
# used for replicate sets in every figure.
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
IWC_THRESHOLDS = [0.95, 0.99, 1.0]                   # Extended Data: sensitivity of the secondary IWC conversion
# Panel d: every scored-incorrect BixBench-Verified-50 run has one primary cause in the run-level failure ledger, an
# audit made with AI assistance.
CAUSE_OF = {'RIGOR': 'No answer validation', 'KNOWLEDGE': 'Lacking biological knowledge',
            'PLATFORM': 'Not able to use Galaxy', 'HARNESS': 'No answer submitted',
            'SPEC': 'Benchmark specification or scoring', 'EVALUATOR': 'Benchmark specification or scoring',
            'CONTRACT': 'Benchmark specification or scoring'}
CAUSES = ['No answer validation', 'Benchmark specification or scoring', 'Lacking biological knowledge',
          'Not able to use Galaxy', 'No answer submitted']
CAUSE_COLOR = dict(zip(CAUSES, [style.NEUTRAL_DARK, style.OI_GREEN, style.OI_YELLOW, style.OI_PURPLE,
                                style.NEUTRAL_LIGHT]))
OVERLAP = {('RIGOR', 'SPEC'), ('SPEC', 'RIGOR')}     # validation and specification both implicated (primary, secondary)
LEDGER_MODEL = {'GPT-5.5': 'GPT-5.5', 'Sol': 'GPT-5.6 Sol', 'Luna': 'GPT-5.6 Luna', 'DS-Codex': 'DeepSeek V4 Pro'}
EXAMPLE = 'bix-45-q1'                                 # traced discordant case: PhyKIT version
PAIR_TYPES = [('galaxy_higher', CODE, 'Galaxy higher'), ('code_higher', GAL, 'Custom code higher'),
              ('equal', CODE, 'Same count'), ('equal', GAL, None)]
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- statistics
def holm(p):
    p = np.asarray(p, float)
    order, adj, run = np.argsort(p), np.empty(len(p)), 0.0
    for i, k in enumerate(order):
        run = max(run, (len(p) - i) * p[k])
        adj[k] = min(1.0, run)
    return adj


def signflip_p(cluster_diffs):
    """Two-sided paired randomization test: flip the sign of each cluster's summed difference."""
    d = np.asarray(cluster_diffs, float)
    if len(d) <= 16:  # enumerate every sign vector exactly
        signs = np.array(list(itertools.product([-1.0, 1.0], repeat=len(d))))
        return float(np.mean(np.abs(signs @ d) >= abs(d.sum()) - 1e-12))
    hits = 0
    for _ in range(B_PERM // 20000):
        null = rng.choice([-1.0, 1.0], size=(20000, len(d))) @ d
        hits += np.sum(np.abs(null) >= abs(d.sum()) - 1e-12)
    return (1 + hits) / (B_PERM + 1)


def boot_means(frames, group_cols, value='score'):
    """Pooled means per group with cluster-bootstrap draws; clusters resampled within each benchmark."""
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


def ci(draws):
    return np.percentile(draws, 2.5, axis=0), np.percentile(draws, 97.5, axis=0)


def paired_difference(d, col, group=None):
    """Galaxy minus custom code (x 100) for one benchmark, overall or per model, with interval and sign-flip P."""
    est, draws = boot_means(d, ['env'] if group is None else [group, 'env'], value=col)
    cell = d.groupby(['cluster', 'task', 'cfg', 'env'])[col].mean().unstack('env')
    out = []
    keys = [None] if group is None else CFG
    for k in keys:
        g, c = (GAL, CODE) if k is None else ((k, GAL), (k, CODE))
        dd = (draws[g] - draws[c]) * 100
        sub = cell if k is None else cell.xs(k, level='cfg', drop_level=False)
        diff = (sub[GAL] - sub[CODE]).groupby(level='cluster').sum()
        out.append(dict(cfg=k or 'all four', code=est[c] * 100, galaxy=est[g] * 100, diff=(est[g] - est[c]) * 100,
                        lo=np.percentile(dd, 2.5), hi=np.percentile(dd, 97.5), p=signflip_p(diff.values),
                        clusters=len(diff)))
    return out


# ---------------------------------------------------------------- data
def load_runs():
    r = pd.read_csv(os.path.join(AN, 'accuracy_primary_runs.csv'))
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    return r


def replicate_sets(r):
    """One row per task x model x condition: correct runs of three."""
    return r.groupby(['benchmark', 'cluster', 'task', 'cfg', 'env']).ok.sum().rename('n_correct').reset_index()


def load_ledger(r):
    led = pd.DataFrame(json.load(open(LEDGER)))
    led = led[(led.b == 'BixBench') & ~led.run.str.contains('ClaudeCode')].copy()
    led['cfg'] = led.run.str.extract(r'^[CG] (.+) r\d$')[0].map(LEDGER_MODEL)
    led['replicate'] = led.run.str.extract(r'r(\d)$')[0].astype(int)
    led['env'] = led.cond
    led['cause'] = led.p.map(CAUSE_OF)
    wrong = r[(r.benchmark == 'BixBench50') & (r.ok == 0)]
    key = ['task', 'cfg', 'env', 'replicate']
    j = wrong.merge(led[key + ['p', 's', 'cause', 'd']], on=key, how='outer', indicator=True)
    assert (j._merge == 'both').all() and not led.duplicated(key).any(), 'ledger must label every incorrect run once'
    return j.drop(columns='_merge')


# ---------------------------------------------------------------- panels: statistics
def panel_a(r):
    """Mean score per benchmark, model and condition (IWC: output agreement), with each replicate's mean, and the
    Galaxy - custom code difference per model (12 comparisons, Holm-adjusted)."""
    rows, tests = [], []
    for bm in BENCH:
        d = r[r.benchmark == bm]
        est, draws = boot_means(d, ['cfg', 'env'])
        lo, hi = ci(draws)
        for (c, env), v, a, b in zip(est.index, est.values, lo, hi):
            rows.append(dict(benchmark=bm, cfg=c, env=env, value=v * 100, lo=a * 100, hi=b * 100,
                             n=int(((d.cfg == c) & (d.env == env)).sum()), tasks=d.task.nunique()))
        task = d.groupby(['cluster', 'task', 'cfg', 'env']).score.mean().unstack('env')
        for c in CFG:
            t = task.xs(c, level='cfg')
            diff = (t[GAL] - t[CODE]).groupby(level='cluster').sum()
            dd = (draws[(c, GAL)] - draws[(c, CODE)]) * 100
            tests.append(dict(benchmark=bm, cfg=c, diff=(est[(c, GAL)] - est[(c, CODE)]) * 100,
                              lo=np.percentile(dd, 2.5), hi=np.percentile(dd, 97.5), p=signflip_p(diff.values)))
    tests = pd.DataFrame(tests)
    tests['p_holm'] = holm(tests.p)      # 12 comparisons: 4 models in each of 3 benchmarks
    reps = r.groupby(['benchmark', 'cfg', 'env', 'replicate']).score.agg(['mean', 'size']).reset_index()
    reps = reps.rename(columns={'mean': 'value', 'size': 'n'}).assign(value=lambda x: x.value * 100)
    return pd.DataFrame(rows), tests, reps


def panel_b(r, sets):
    """Galaxy minus custom code by benchmark, models pooled: runs correct, and replicate sets with 3/3 correct."""
    s = sets.assign(solved=(sets.n_correct == 3).astype(int))
    out = []
    for measure, frame, col in (('runs_correct', r, 'ok'), ('sets_all_three_correct', s, 'solved')):
        for bm in BENCH:
            d = frame[frame.benchmark == bm]
            est, draws = boot_means(d, ['env'], value=col)
            dd = (draws[GAL] - draws[CODE]) * 100
            cell = d.groupby(['cluster', 'task', 'cfg', 'env'])[col].mean().unstack('env')
            diff = (cell[GAL] - cell[CODE]).groupby(level='cluster').sum()
            out.append(dict(measure=measure, benchmark=bm, code=est[CODE] * 100, galaxy=est[GAL] * 100,
                            diff=(est[GAL] - est[CODE]) * 100, lo=np.percentile(dd, 2.5), hi=np.percentile(dd, 97.5),
                            p=signflip_p(diff.values), clusters=len(diff)))
    out = pd.DataFrame(out)
    out['p_holm'] = holm(out.p)          # 6 comparisons: 2 measures in each of 3 benchmarks
    return out


def forest(r, sets, a_tests, b_tab):
    """Rows of panel b. Mean score: per model from panel a; pooled from panel b for the binary benchmarks, and the
    pooled mean IWC agreement (new). All three runs correct: per model (new) and pooled from panel b."""
    s = sets.assign(solved=(sets.n_correct == 3).astype(int))
    rows = []
    for t in a_tests.itertuples():
        rows.append(dict(group='mean_score', benchmark=t.benchmark, cfg=t.cfg, diff=t.diff, lo=t.lo, hi=t.hi, p=t.p,
                         p_holm=t.p_holm, family='panel a: 12 model comparisons'))
    for t in b_tab[b_tab.measure == 'runs_correct'].itertuples():
        if t.benchmark != 'IWC':      # accepted runs are the mean score of a binary benchmark
            rows.append(dict(group='mean_score', benchmark=t.benchmark, cfg='all four', diff=t.diff, lo=t.lo, hi=t.hi,
                             p=t.p, p_holm=t.p_holm, family='pooled: 6 comparisons'))
    for t in b_tab[b_tab.measure == 'sets_all_three_correct'].itertuples():
        rows.append(dict(group='all_three', benchmark=t.benchmark, cfg='all four', diff=t.diff, lo=t.lo, hi=t.hi,
                         p=t.p, p_holm=t.p_holm, family='pooled: 6 comparisons'))
    iwc = paired_difference(r[r.benchmark == 'IWC'], 'score')[0]
    rows.append(dict(group='mean_score', benchmark='IWC', cfg='all four', diff=iwc['diff'], lo=iwc['lo'], hi=iwc['hi'],
                     p=iwc['p'], p_holm=np.nan, family='pooled IWC agreement (added)'))
    per = []
    for bm in BENCH:
        for x in paired_difference(s[s.benchmark == bm], 'solved', group='cfg'):
            per.append(dict(group='all_three', benchmark=bm, **{k: x[k] for k in ('cfg', 'diff', 'lo', 'hi', 'p')},
                            family='all three correct per model: 12 comparisons'))
    per = pd.DataFrame(per)
    per['p_holm'] = holm(per.p)
    return pd.concat([pd.DataFrame(rows), per], ignore_index=True)


def panel_c(sets):
    """Correct runs of three in custom code against Galaxy, one count per task x model, per benchmark."""
    pair = sets.pivot_table(index=['benchmark', 'task', 'cfg'], columns='env', values='n_correct').dropna().astype(int)
    grids, summ = {}, {}
    for bm in BENCH:
        p = pair.loc[bm]
        grids[bm] = pd.crosstab(p[GAL], p[CODE]).reindex(index=range(4), columns=range(4), fill_value=0)
        summ[bm] = dict(pairs=len(p), equal=int((p[GAL] == p[CODE]).sum()), galaxy_higher=int((p[GAL] > p[CODE]).sum()),
                        code_higher=int((p[GAL] < p[CODE]).sum()), tasks=p.index.get_level_values('task').nunique())
    return grids, summ, pair


def panel_d(ledger, sets):
    """Incorrect BixBench-Verified-50 runs by pair type (discordant either way, or the same count) and cause."""
    pair = sets[sets.benchmark == 'BixBench50'].pivot_table(index=['task', 'cfg'], columns='env', values='n_correct')
    gap = pair[GAL] - pair[CODE]
    pair['type'] = np.select([gap > 0, gap < 0], ['galaxy_higher', 'code_higher'], 'equal')
    lg = ledger.join(pair['type'], on=['task', 'cfg'])
    lg['overlap'] = [(p, s) in OVERLAP for p, s in zip(lg.p, lg.s)]
    lg['capsule'] = lg.cluster
    tab = lg.groupby(['type', 'env', 'cause']).size().unstack('cause', fill_value=0).reindex(columns=CAUSES,
                                                                                            fill_value=0)
    over = lg[lg.overlap].groupby(['type', 'env', 'cause']).size()
    cover = lg.groupby(['type', 'env']).agg(runs=('task', 'size'), tasks=('task', 'nunique'), capsules=('capsule', 'nunique'))
    pairs = pair.type.value_counts()
    return tab, over, cover, pairs, lg


def census(ledger):
    """Extended Data: primary cause by how many runs of the set were incorrect (the first version's panel d)."""
    lg = ledger.assign(n_wrong=ledger.groupby(['task', 'cfg', 'env']).replicate.transform('size'))
    tab = lg.groupby(['n_wrong', 'env', 'cause']).size().unstack('cause', fill_value=0).reindex(columns=CAUSES,
                                                                                               fill_value=0)
    secondary = lg[(lg.p == 'SPEC') & (lg.s == 'RIGOR')].shape[0], lg[lg.p == 'SPEC'].shape[0]
    return tab, secondary


def iwc_threshold(r):
    """Extended Data: IWC runs correct and sets with all three correct at three agreement thresholds."""
    d = r[r.benchmark == 'IWC']
    rows = []
    for th in IWC_THRESHOLDS:
        x = d.assign(okt=(d.score >= th - 1e-9).astype(int))
        sets = x.groupby(['benchmark', 'cluster', 'task', 'cfg', 'env']).okt.sum().rename('n').reset_index()
        sets['solved'] = (sets.n == 3).astype(int)
        for measure, frame, col in (('runs_correct', x, 'okt'), ('sets_all_three_correct', sets, 'solved')):
            v = paired_difference(frame, col)[0]
            rows.append(dict(threshold=th, measure=measure, **v))
    return pd.DataFrame(rows)


def archive_sensitivities():
    s = pd.read_csv(os.path.join(AN, 'accuracy_sensitivities.csv'))
    scale = np.where(s.benchmark == 'IWC', 100.0, 1.0)            # IWC rows are agreement on a 0-1 scale
    return s.assign(diff=s.difference * scale, lo=s.ci95_low * scale, hi=s.ci95_high * scale)


# ---------------------------------------------------------------- drawing helpers
def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


def fmt_p(p):
    if p < 0.001:
        return r'$\mathit{P}$ < 0.001'
    return rf'$\mathit{{P}}$ = {p:.2f}' if p >= 0.01 else rf'$\mathit{{P}}$ = {p:.3f}'


def signed(text):
    return text.replace('-', '\u2212')


def cond_marker(ax, x, y, env, ms=3.4, **kw):
    ax.plot(x, y, ls='', marker=style.ENV_MARKER[env], ms=ms, mfc=style.ENV_COLOR[env], mec='white', mew=0.4, **kw)


# ---------------------------------------------------------------- panels: drawing
def draw_a(fig, H, tab, reps):
    label(fig, 0, 0, 'a', 'Scores by benchmark, model and condition', H)
    specs = [('BixBench50', 12.0), ('CompBio', 66.0), ('IWC', 128.0)]
    for bm, x0 in specs:
        ax = axes_mm(fig, x0, 14.0, 48.0, 28.0, H)
        iwc = bm == 'IWC'
        k = 0.01 if iwc else 1.0                      # IWC on its own agreement scale, 0-1
        for i, c in enumerate(CFG):
            pts = {}
            for j, env in enumerate(ENVS):
                t = tab[(tab.benchmark == bm) & (tab.cfg == c) & (tab.env == env)].iloc[0]
                x = i + (j - 0.5) * 0.36
                ax.plot([x, x], [t.lo * k, t.hi * k], color=style.ENV_COLOR[env], lw=0.8, zorder=3,
                        solid_capstyle='butt')
                cond_marker(ax, x, t.value * k, env, zorder=5)
                pts[env] = (x, t.value * k)
                v = reps[(reps.benchmark == bm) & (reps.cfg == c) & (reps.env == env)].value.values * k
                ax.plot(np.full(len(v), x + (j - 0.5) * 0.30), v, ls='', marker='o', ms=1.4, mfc='white',
                        mec=style.INK2, mew=0.4, zorder=4)
            ax.plot([pts[CODE][0], pts[GAL][0]], [pts[CODE][1], pts[GAL][1]], color=style.NEUTRAL_MID, lw=0.5,
                    zorder=2)
        if iwc:
            ax.set_ylim(0.6, 1.02)
            ax.set_yticks([0.6, 0.7, 0.8, 0.9, 1.0], ['0.6', '0.7', '0.8', '0.9', '1.0'])
            ax.set_ylabel('Mean output agreement')
        else:
            ax.set_ylim(60, 102)
            ax.set_yticks([60, 70, 80, 90, 100])
            if bm == 'BixBench50':
                ax.set_ylabel('Runs accepted (%)')
            else:
                ax.set_yticklabels([])
        style.grid_y(ax)
        ax.set_xlim(-0.6, len(CFG) - 0.4)
        ax.set_xticks(range(len(CFG)), [TICK[c] for c in CFG])
        ax.tick_params(axis='x', length=0, pad=2, labelsize=5.5)
        ntask = int(tab[tab.benchmark == bm].tasks.iloc[0])
        ax.text(0.0, 1 + 5.6 / 28.0, f'{BENCH_NAME[bm]} · {ntask} tasks', transform=ax.transAxes, ha='left',
                va='bottom', fontsize=6, fontweight='bold')
        ax.text(0.0, 1 + 1.6 / 28.0, CONTRACT[bm], transform=ax.transAxes, ha='left', va='bottom', fontsize=5,
                color=style.INK2)
    hand = [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.4, mfc=style.ENV_COLOR[e], mec='white', mew=0.4,
                   label=style.ENV_LABEL[e]) for e in ENVS]
    hand.append(Line2D([], [], ls='', marker='o', ms=1.4, mfc='white', mec=style.INK2, mew=0.4,
                       label='Replicate (one run per task)'))
    fig.legend(handles=hand, ncol=3, loc='upper right', bbox_to_anchor=(1.0, 1 - 0.6 / H), fontsize=5.3,
               handletextpad=0.3, columnspacing=1.0, borderaxespad=0, frameon=False)


def draw_b(fig, H, y0, fr):
    label(fig, 0, y0, 'b', 'Paired differences: Galaxy minus custom code', H)
    rows, y = [], 0.0
    for bm in BENCH:
        rows.append((bm, None, y))
        y += 1.0
        for c in CFG + ['all four']:
            rows.append((bm, c, y))
            y += 1.0
        y += 0.45
    ymax = y - 0.45
    h = 43.0
    cols = [('mean_score', 'Mean score', 34.0, (-15, 25), [-10, 0, 10, 20]),
            ('all_three', 'All three runs correct', 67.0, (-45, 70), [-40, 0, 40])]
    for k, (grp, title, x0, xlim, ticks) in enumerate(cols):
        ax = axes_mm(fig, x0, y0 + 12.0, 29.0, h, H)
        g = fr[fr.group == grp].set_index(['benchmark', 'cfg'])
        for bm, c, yy in rows:
            if c is None:
                continue
            t = g.loc[(bm, c)]
            pooled = c == 'all four'
            lo, hi = max(t.lo, xlim[0]), min(t.hi, xlim[1])
            ax.plot([lo, hi], [yy, yy], color=style.INK, lw=0.9 if pooled else 0.6, zorder=3, solid_capstyle='butt')
            for edge, lim, sgn in ((t.lo, xlim[0], -1), (t.hi, xlim[1], 1)):
                if (edge < lim) if sgn < 0 else (edge > lim):     # interval runs past the axis
                    ax.plot(lim, yy, ls='', marker='<' if sgn < 0 else '>', ms=2.2, color=style.INK, zorder=3,
                            clip_on=False)
            ax.plot(t['diff'], yy, ls='', marker='D' if pooled else 'o', ms=3.0 if pooled else 2.3,
                    mfc=style.INK if pooled else 'white', mec=style.INK, mew=0.6, zorder=4)
        ax.axvline(0, color=style.INK2, lw=0.6, zorder=2)
        ax.set_ylim(ymax - 0.4, -0.6)
        ax.set_yticks([])
        ax.spines['left'].set_visible(False)
        ax.set_xlim(*xlim)
        ax.set_xticks(ticks)
        style.grid_x(ax)
        ax.set_title(title, fontsize=5.5, fontweight='bold', pad=3)
        ax.set_xlabel('Percentage points', labelpad=1.5)
        if k == 0:
            tr = blended_transform_factory(ax.transAxes, ax.transData)
            for bm, c, yy in rows:
                if c is None:
                    ax.text(-(x0 - 1.0) / 29.0, yy, BENCH_NAME[bm] + (' (agreement × 100)' if bm == 'IWC' else ''),
                            transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold')
                else:
                    ax.text(-0.05, yy, 'All four models' if c == 'all four' else c, transform=tr, ha='right',
                            va='center', fontsize=5.5, fontweight='bold' if c == 'all four' else 'normal')
    fig.text((0 + 4.4) / W, 1 - (y0 + 4.6) / H, '← custom code higher · Galaxy higher →  (95% intervals)', fontsize=5,
             color=style.INK2, va='top')


def draw_c(fig, H, y0, grids, summ):
    label(fig, 100.0, y0, 'c', 'Correct runs of three, same task and model', H)
    vmax = max(g.values.max() for g in grids.values())
    norm = LogNorm(vmin=1, vmax=vmax * 1.6)
    side, xs = 20.0, (112.0, 135.5, 159.0)
    for k, (bm, x0) in enumerate(zip(BENCH, xs)):
        ax = axes_mm(fig, x0, y0 + 14.0, side, side, H)
        m = grids[bm].values.astype(float)
        im = ax.imshow(np.where(m > 0, m, np.nan), origin='lower', cmap='Greys', norm=norm,
                       extent=(-0.5, 3.5, -0.5, 3.5), zorder=1)
        for gg in range(4):
            for cc in range(4):
                v = int(m[gg, cc])
                ax.text(cc, gg, f'{v}', ha='center', va='center', fontsize=5,
                        color='white' if v >= 0.18 * vmax else style.INK, fontweight='bold' if gg == cc else 'normal',
                        zorder=3)
                if gg == cc:
                    ax.add_patch(Rectangle((cc - 0.5, gg - 0.5), 1, 1, fill=False, ec=style.INK, lw=0.7, zorder=2))
        ax.set_xticks(range(4))
        ax.set_yticks(range(4), [str(i) for i in range(4)] if k == 0 else [''] * 4)
        ax.tick_params(length=0, pad=1.5, labelsize=5)
        for s in ax.spines.values():
            s.set_visible(False)
        name = {'BixBench50': 'BixBench-V-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC (≥ 0.99)'}[bm]
        ax.set_title(name, fontsize=5, fontweight='bold', pad=2.5)
        s = summ[bm]
        ax.text(0.5, -0.30, f'{s["pairs"]} pairs\nSame count {s["equal"]}\nGalaxy higher {s["galaxy_higher"]}\n'
                f'Custom code higher {s["code_higher"]}', transform=ax.transAxes, ha='center', va='top', fontsize=5,
                linespacing=1.2)
        if k == 0:
            ax.set_ylabel('Galaxy', labelpad=1.5)
        if k == 1:
            ax.set_xlabel('Custom code', labelpad=1.5)
    fig.text(104.4 / W, 1 - (y0 + 4.6) / H, 'Outlined diagonal, same count; above it, Galaxy had more correct runs;\n'
             'below it, custom code had more', fontsize=5, color=style.INK2, va='top', linespacing=1.2)
    cax = axes_mm(fig, 112.0, y0 + 50.5, 20.0, 1.4, H)
    cb = fig.colorbar(im, cax=cax, orientation='horizontal', ticks=[1, 10, 100])
    cb.ax.set_xticklabels(['1', '10', '100'])
    cb.ax.minorticks_off()
    cb.ax.tick_params(labelsize=5, length=1.5, pad=1)
    cb.outline.set_linewidth(0.4)
    fig.text(134.0 / W, 1 - (y0 + 50.1) / H, 'Task–model pairs per cell (log scale)', fontsize=5, color=style.INK2,
             va='top')


def stacked_causes(ax, yy, counts, over, width_mm, bar_h=0.66, outside=False, below=False):
    n = int(counts.sum())
    left, out = 0.0, []
    for cause in CAUSES:
        v = 100 * counts[cause] / n if n else 0
        if not v:
            continue
        ax.barh(yy, v, left=left, height=bar_h, color=CAUSE_COLOR[cause], ec='white', lw=0.4, zorder=3)
        o = over.get(cause, 0)
        if o:
            ax.barh(yy, 100 * o / n, left=left, height=bar_h, fill=False, hatch='////', ec='white', lw=0, zorder=4)
        txt = f'{int(counts[cause])}'
        if v / 100 * width_mm >= 1.25 * len(txt) + 0.8:
            ax.text(left + v / 2, yy, txt, ha='center', va='center', fontsize=5, zorder=5,
                    color='white' if cause in ('No answer validation', 'Benchmark specification or scoring',
                                               'Not able to use Galaxy') else style.INK,
                    bbox=dict(boxstyle='square,pad=0.08', fc=CAUSE_COLOR[cause], ec='none') if o else None)
        elif outside:
            out.append([left + v / 2, txt])
        left += v
    for a_, b_ in zip(out, out[1:]):                    # neighbouring outside counts at least 4 points apart
        if b_[0] - a_[0] < 4.0:
            b_[0] = a_[0] + 4.0
    for xc, txt in out:                                 # narrow segments: count just above (or below) the bar
        ax.text(xc, yy + (bar_h / 2 + 0.05) * (1 if below else -1), txt, ha='center', va='top' if below else 'bottom',
                fontsize=5, color=style.INK, zorder=5)
    return n


def draw_d(fig, H, y0, tab, over, cover, pairs, sets, r):
    label(fig, 0, y0, 'd', 'Why the conditions disagree (BixBench-Verified-50)', H,
          'Incorrect runs by primary cause (AI-assisted audit), for task–model pairs whose conditions differ or agree')
    ax = axes_mm(fig, 43.0, y0 + 12.0, 54.0, 19.0, H)
    ypos = [0.0, 1.45, 3.05, 4.1]
    for (ptype, env, lab), yy in zip(PAIR_TYPES, ypos):
        counts = tab.loc[(ptype, env)] if (ptype, env) in tab.index else pd.Series(0, index=CAUSES)
        o = {c: int(over.get((ptype, env, c), 0)) for c in CAUSES}
        n = stacked_causes(ax, yy, counts, o, 54.0, outside=True, below=yy == ypos[-1])
        cv = cover.loc[(ptype, env)]
        ax.text(101.5, yy, f'{n} runs · {int(cv.tasks)} tasks', ha='left', va='center', fontsize=5, color=style.INK2)
        ax.text(-1.0, yy, f'{style.ENV_LABEL[env]} runs', ha='right', va='center', fontsize=5)
        if lab:
            npairs = int(pairs.get(ptype, 0)) if ptype != 'equal' else int(
                (sets[sets.benchmark == 'BixBench50'].pivot_table(index=['task', 'cfg'], columns='env',
                                                                  values='n_correct').min(axis=1) < 3).sum() -
                pairs.get('galaxy_higher', 0) - pairs.get('code_higher', 0))
            mid = yy if ptype != 'equal' else (ypos[2] + ypos[3]) / 2
            ax.text(-0.335, mid, f'{lab}\n({npairs} pairs)', transform=blended_transform_factory(ax.transAxes, ax.transData),
                    ha='right', va='center', fontsize=5, fontweight='bold', linespacing=1.1)
    ax.set_ylim(ypos[-1] + 0.95, -0.95)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Incorrect runs (%)', labelpad=1.5)
    style.grid_x(ax)
    handles = [Patch(fc=CAUSE_COLOR[c], label=c) for c in CAUSES]
    handles.append(Patch(fc=style.NEUTRAL_MID, hatch='////', ec='white', lw=0, label='Validation and specification\n'
                         'both implicated'))
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(-0.77, -0.50), ncol=3, fontsize=5, handlelength=1.0,
              handletextpad=0.3, columnspacing=0.8, labelspacing=0.3, borderaxespad=0)
    draw_example(fig, H, y0, r)


def draw_example(fig, H, y0, r):
    """Traced discordant case: run outcome of every model and replicate on bix-45-q1, in both conditions."""
    x0, w = 122.0, 58.0
    ax = axes_mm(fig, x0, y0 + 1.0, w, 40.0, H)
    ax.set_axis_off()
    ax.set_xlim(0, w)
    ax.set_ylim(40.0, 0)
    ax.add_patch(Rectangle((0, 0), w, 40.0, fc=style.LIGHT, ec='none', zorder=0))
    ax.text(1.5, 1.6, f'Traced case: {EXAMPLE} (relative composition variability)', fontsize=5.5, fontweight='bold',
            va='top')
    d = r[r.task == EXAMPLE]
    gx = {CODE: 25.0, GAL: 44.0}
    for env in ENVS:
        ax.text(gx[env] + 2.4, 6.0, style.ENV_LABEL[env], fontsize=5, ha='center', va='top', fontweight='bold')
    for i, c in enumerate(CFG):
        yy = 10.4 + i * 2.6
        ax.text(1.5, yy, c, fontsize=5, va='center')
        for env in ENVS:
            v = d[(d.cfg == c) & (d.env == env)].sort_values('replicate').ok.values
            for j, ok in enumerate(v):
                ax.plot(gx[env] + j * 2.4, yy, ls='', marker='o', ms=2.6, mfc=style.INK if ok else 'white',
                        mec=style.INK, mew=0.5, zorder=3)
    for env in ENVS:
        n = int(d[d.env == env].ok.sum())
        ax.text(gx[env] + 2.4, 21.4, f'{n} of {len(d[d.env == env])} correct', fontsize=5, ha='center', va='center',
                color=style.INK2)
    ax.plot([], [], ls='', marker='o', ms=2.6, mfc=style.INK, mec=style.INK, mew=0.5)
    ax.text(1.5, 24.6, 'Successful custom-code runs matched the PhyKIT version to the\n'
            'date of the input archive. The Galaxy PhyKIT wrapper, like current\n'
            'PhyKIT, returned a different value, and the wrapper version was not\n'
            'shown to the agent; the reference encodes the older value.',
            fontsize=5, va='top', linespacing=1.25)
    ax.text(1.5, 37.6, '●  correct    ○  incorrect (one run each)', fontsize=5, va='center', color=style.INK2)


# ---------------------------------------------------------------- Extended Data
def ed_census(fig, H, y0, tab, secondary):
    label(fig, 0, y0, 'a', 'Primary cause of every incorrect run, by incorrect runs in its set (BixBench-Verified-50)', H)
    ax = axes_mm(fig, 30.0, y0 + 9.0, 78.0, 34.0, H)
    rows = [(k, env) for k in (1, 2, 3) for env in ENVS]
    ypos, y = [], 0.0
    for k, env in rows:
        ypos.append(y)
        y += 1.0 if env == CODE else 2.05
    for (k, env), yy in zip(rows, ypos):
        t = tab.loc[(k, env)] if (k, env) in tab.index else pd.Series(0, index=CAUSES)
        n = stacked_causes(ax, yy, t, {}, 78.0, bar_h=0.72)
        ax.text(101.5, yy, f'{n}', ha='left', va='center', fontsize=5, color=style.INK2)
        ax.text(-1.2, yy, style.ENV_LABEL[env], ha='right', va='center', fontsize=5)
    ax.set_ylim(ypos[-1] + 1.25, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Incorrect runs (%)')
    style.grid_x(ax)
    for k in (1, 2, 3):
        mid = (ypos[rows.index((k, CODE))] + ypos[rows.index((k, GAL))]) / 2
        ax.text(-0.235, mid, f'{k} of 3\nincorrect', transform=blended_transform_factory(ax.transAxes, ax.transData),
                ha='right', va='center', fontsize=5.5, fontweight='bold', linespacing=1.1)
    ax.text(101.5, -0.95, 'Runs', ha='left', va='center', fontsize=5, color=style.INK2)
    ax.legend(handles=[Patch(fc=CAUSE_COLOR[c], label=c) for c in CAUSES], loc='upper left',
              bbox_to_anchor=(1.10, 1.0), fontsize=5.3, handlelength=1.0, labelspacing=0.45, borderaxespad=0,
              title='Primary cause (AI-assisted audit)', title_fontsize=5.3, alignment='left')
    k, n = secondary
    ax.text(1.10, 0.30, f'Under-specified runs often also lacked\nanswer validation ({k} of {n}, secondary cause)',
            transform=ax.transAxes, ha='left', va='top', fontsize=5, color=style.INK2, linespacing=1.2)


def ed_sensitivity(fig, H, y0, th, sens, main):
    label(fig, 0, y0, 'b', 'Sensitivity of the condition difference', H)
    rows = []
    for t in main.itertuples():
        rows.append((f'{BENCH_NAME[t.benchmark]}, primary', t.diff, t.lo, t.hi, True))
    rows.append(None)
    for t in th.itertuples():
        what = 'runs' if t.measure == 'runs_correct' else 'sets 3/3'
        rel = '=' if t.threshold == 1.0 else '≥'
        rows.append((f'IWC {what} correct, agreement {rel} {t.threshold:g}', t.diff, t.lo, t.hi, t.threshold == 0.99))
    rows.append(None)
    names = {'BixBench_exclude_benchmark_side_C1_C2_C3_C6': 'BixBench-V-50 without benchmark-side tasks',
             'CompBio_exclude_outcome_named_cells': 'CompBioBench without outcome-named campaigns',
             'IWC_exclude_tasks_with_zero_run': 'IWC agreement without tasks with a zero-scored run',
             'IWC_exclude_ATAC_agent_calibrated_routes': 'IWC agreement without ATAC calibrated routes',
             'IWC_budget_matched_pairs': 'IWC agreement, budget-matched pairs only'}
    for t in sens.itertuples():
        rows.append((names.get(t.population, t.population), t.diff, t.lo, t.hi, False))
    ax = axes_mm(fig, 62.0, y0 + 8.0, 70.0, 52.0, H)
    y = 0
    ys = []
    for row in rows:
        if row is None:
            y += 0.6
            continue
        name, d, lo, hi, bold = row
        ax.plot([lo, hi], [y, y], color=style.INK, lw=0.7, zorder=3)
        ax.plot(d, y, ls='', marker='D' if bold else 'o', ms=2.6, mfc=style.INK if bold else 'white', mec=style.INK,
                mew=0.6, zorder=4)
        ax.text(-0.03, y, name, transform=blended_transform_factory(ax.transAxes, ax.transData), ha='right',
                va='center', fontsize=5, fontweight='bold' if bold else 'normal')
        ax.text(1.02, y, signed(f'{d:+.1f} ({lo:+.1f} to {hi:+.1f})'), transform=blended_transform_factory(ax.transAxes,
                ax.transData), ha='left', va='center', fontsize=5, color=style.INK2)
        ys.append(y)
        y += 1
    ax.axvline(0, color=style.INK2, lw=0.6, zorder=2)
    ax.set_ylim(y - 0.4, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(-15, 35)
    style.grid_x(ax)
    ax.set_xlabel('Galaxy minus custom code (percentage points; IWC agreement × 100)')
    ax.text(0.0, 1.02, 'Primary estimates (diamonds, bold) and alternatives; archive sensitivities from '
            'accuracy_sensitivities.csv', transform=ax.transAxes, ha='left', va='bottom', fontsize=5, color=style.INK2)


# ---------------------------------------------------------------- source data and assembly
def source_data(a_tab, a_reps, fr, b_tab, grids, summ, d_tab, d_over, d_cover, d_pairs):
    rows = []
    endpoint = {'IWC': 'output_agreement_x100'}
    for r in a_tab.itertuples():
        rows.append(dict(panel='a', benchmark=r.benchmark, model=r.cfg, condition=r.env,
                         measure=endpoint.get(r.benchmark, 'accuracy_pct'), value=r.value, ci95_low=r.lo,
                         ci95_high=r.hi, n=r.n))
    for r in a_reps.itertuples():
        rows.append(dict(panel='a', benchmark=r.benchmark, model=r.cfg, condition=r.env, replicate=r.replicate,
                         measure=endpoint.get(r.benchmark, 'accuracy_pct') + '_replicate', value=r.value, n=r.n))
    for r in fr.itertuples():
        m = {'mean_score': 'mean_score', 'all_three': 'sets_all_three_correct'}[r.group]
        rows.append(dict(panel='b', benchmark=r.benchmark, model=r.cfg, condition='galaxy-custom_code',
                         measure=f'{m}_difference_points', value=r.diff, ci95_low=r.lo, ci95_high=r.hi, p=r.p,
                         p_holm=r.p_holm, group=r.family))
    for r in b_tab.itertuples():
        for env, v in ((CODE, r.code), (GAL, r.galaxy)):
            rows.append(dict(panel='b', benchmark=r.benchmark, model='all four', condition=env,
                             measure=f'{r.measure}_pct', value=v))
    for bm, g in grids.items():
        for gg in range(4):
            for cc in range(4):
                rows.append(dict(panel='c', benchmark=bm, model='all four', condition='galaxy x custom_code',
                                 measure=f'pairs_galaxy_{gg}_custom_code_{cc}_correct_of_3', value=int(g.loc[gg, cc])))
        for k, v in summ[bm].items():
            rows.append(dict(panel='c', benchmark=bm, model='all four', condition='galaxy x custom_code',
                             measure=f'pairs_{k}', value=v))
    for (ptype, env), t in d_tab.iterrows():
        for cause in CAUSES:
            rows.append(dict(panel='d', benchmark='BixBench50', model='all four', condition=env,
                             group=f'pairs_{ptype}', measure=f'incorrect_runs: {cause}', value=int(t[cause]),
                             n=int(d_over.get((ptype, env, cause), 0))))
        cv = d_cover.loc[(ptype, env)]
        rows.append(dict(panel='d', benchmark='BixBench50', model='all four', condition=env, group=f'pairs_{ptype}',
                         measure='coverage_runs_tasks_capsules', value=int(cv.runs), n=f'{int(cv.tasks)} tasks; '
                         f'{int(cv.capsules)} capsules'))
    for ptype, n in d_pairs.items():
        rows.append(dict(panel='d', benchmark='BixBench50', model='all four', condition='both', group=f'pairs_{ptype}',
                         measure='task_model_pairs', value=int(n)))
    cols = ['panel', 'benchmark', 'model', 'condition', 'replicate', 'group', 'measure', 'value', 'ci95_low',
            'ci95_high', 'n', 'p', 'p_holm']
    out = pd.DataFrame(rows).reindex(columns=cols)
    out['condition'] = out.condition.str.replace('open_ended_code', 'custom_code')
    out.round(4).to_csv(os.path.join(OUT, 'fig2_source_data.csv'), index=False)


def ed_source_data(cen, secondary, th, sens):
    rows = []
    for (k, env), t in cen.iterrows():
        for cause in CAUSES:
            rows.append(dict(panel='a', condition=env, group=f'sets_with_{k}_of_3_incorrect',
                             measure=f'incorrect_runs: {cause}', value=int(t[cause])))
    rows.append(dict(panel='a', condition='both', group='SPEC primary', measure='with RIGOR secondary',
                     value=secondary[0], n=secondary[1]))
    for t in th.itertuples():
        rows.append(dict(panel='b', condition='galaxy-custom_code', group=f'IWC threshold {t.threshold:g}',
                         measure=f'{t.measure}_difference_points', value=t.diff, ci95_low=t.lo, ci95_high=t.hi,
                         p=t.p, n=t.clusters))
    for t in sens.itertuples():
        rows.append(dict(panel='b', condition='galaxy-custom_code', group=t.population,
                         measure='difference_points (archive accuracy_sensitivities.csv)', value=t.diff,
                         ci95_low=t.lo, ci95_high=t.hi, n=t.clusters))
    out = pd.DataFrame(rows).reindex(columns=['panel', 'condition', 'group', 'measure', 'value', 'ci95_low',
                                              'ci95_high', 'n', 'p'])
    out['condition'] = out.condition.str.replace('open_ended_code', 'custom_code')
    out.round(4).to_csv(os.path.join(OUT, 'ed_fig2_source_data.csv'), index=False)


def save(fig, name, title):
    style.enforce_min_font(fig)
    fig.savefig(os.path.join(OUT, f'{name}.svg'), metadata={'Title': title})
    fig.savefig(os.path.join(OUT, f'{name}.pdf'), metadata={'Title': title})
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, f'{name}.png'), dpi=(600, 600))
    plt.close(fig)


def main():
    global rng
    r = load_runs()
    sets = replicate_sets(r)
    a_tab, a_t, a_reps = panel_a(r)
    b_tab = panel_b(r, sets)
    rng = np.random.default_rng(SEED + 1)        # new estimates draw from their own stream; a and b are unchanged
    fr = forest(r, sets, a_t, b_tab)
    grids, summ, _ = panel_c(sets)
    ledger = load_ledger(r)
    d_tab, d_over, d_cover, d_pairs, _ = panel_d(ledger, sets)
    cen, secondary = census(ledger)
    rng = np.random.default_rng(SEED + 2)
    th = iwc_threshold(r)
    sens = archive_sensitivities()
    for name, t in (('a: Galaxy - custom code by benchmark and model', a_t), ('b: pooled', b_tab),
                    ('b: forest', fr), ('d: causes by pair type', d_tab), ('d: coverage', d_cover),
                    ('ED: IWC thresholds', th), ('ED: census', cen)):
        print(name)
        print(t.round(4).to_string())
    print('c:', summ, '| pairs:', d_pairs.to_dict())

    H = 168.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, a_tab, a_reps)
    y2 = 54.0
    draw_b(fig, H, y2, fr)
    draw_c(fig, H, y2, grids, summ)
    draw_d(fig, H, 119.0, d_tab, d_over, d_cover, d_pairs, sets, r)
    save(fig, 'fig2', 'Fig. 2 | Agents show similar observed benchmark performance in Galaxy and custom code')
    source_data(a_tab, a_reps, fr, b_tab, grids, summ, d_tab, d_over, d_cover, d_pairs)

    main_rows = fr[(fr.group == 'mean_score') & (fr.cfg == 'all four')].set_index('benchmark').loc[BENCH].reset_index()
    He = 132.0
    fig = plt.figure(figsize=(W * MM, He * MM))
    ed_census(fig, He, 0, cen, secondary)
    ed_sensitivity(fig, He, 58.0, th, sens, main_rows)
    save(fig, 'ed_fig2', 'Extended Data Fig. 2 | Failure causes and sensitivity of the accuracy comparison')
    ed_source_data(cen, secondary, th, sens)


if __name__ == '__main__':
    main()
