"""Extended Data Figs 6 and 7: independent checks of the annotations, benchmark integrity, verification and recovery.

Extended Data Fig. 6 (checks of the audits and of benchmark integrity):
a, runs that reached a source of benchmark answers during the run, by exposure tier (make_answer_exposure.py);
b, the Galaxy - custom code accuracy difference with all runs, without runs with verified or probable exposure, and
   without any run that searched for the benchmark;
c, an independent AI-assisted second rater against the original failure-cause audit (45 BixBench-Verified-50 runs);
d, an independent AI-assisted second rater against the rule-based failure classes of failed Galaxy requests (150).

Extended Data Fig. 7 (verification and recovery):
a, verification checks coded in 80 runs (coder blind to the grade), by outcome and by condition;
b, failure episodes: failed steps later re-run without error in the same run, and final correctness;
c, a worked parameter check (bix-43-q4): a request blocked before the job, then corrected;
d, a selected case (variant-status-q1): outcomes of all 24 runs and the runs that ran a read-position diagnostic.

Scores come from figures/scored_runs.csv (make_scored_runs.py): every run as the public results site shows it
(https://goeckslab.github.io/galaxy-agent-benchmark/), the IWC host-read removal task included.
Writes figures/ed_fig6.{svg,pdf,png}, ed_fig7.{svg,pdf,png}, ed_fig6_source_data.csv and ed_fig7_source_data.csv.
CompBioBench answers are never written.
"""
import glob
import gzip
import io
import json
import os
import re
import sys

import numpy as np
import panel_io  # noqa: E402  (figures/panel_io.py)
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
import style  # noqa: E402
from style import plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})
style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}
OUT = os.path.join(ROOT, 'figures')
SCORED = os.path.join(OUT, 'scored_runs.csv')      # per-run scores as the results site shows them (make_scored_runs.py)
ANN = os.path.join(OUT, 'annotations')
AN = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis')
SUMMARIES = os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz')
W, MM, B, SEED = 180.0, 1 / 25.4, 20000, 20261002
ENVS = style.ENVS
CODE, GAL = ENVS
CFG = style.CONFIGS
BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
TIERS = [('verified', 'Answers seen in the trace', '#882255'), ('probable', 'Opened a page with answers', '#CC6677'),
         ('attempted', 'Searched for the benchmark', '#DDCC77'), ('none', 'No benchmark search', '#E8E8E8')]
GROUP = {'RIGOR': 'Validation', 'SPEC': 'Benchmark', 'EVALUATOR': 'Benchmark', 'CONTRACT': 'Benchmark',
         'KNOWLEDGE': 'Knowledge', 'PLATFORM': 'Galaxy', 'HARNESS': 'No answer'}
GROUPS = ['Validation', 'Benchmark', 'Knowledge', 'Galaxy', 'No answer']
FIX = {'A1': 'API design', 'A3': 'API design', 'A5': 'API design', 'B2': 'Error diagnostics',
       'A4': 'Tool and parameter descriptions', 'A2': 'Tool and parameter descriptions', 'A7': 'Datatypes and uploads',
       'B4': 'Datatypes and uploads', 'A6': 'UDT support', 'B1': 'UDT support', 'A8': 'Server capacity',
       'B5': 'Server capacity', 'B3': None, 'X': None, 'Z': None}
CHECKS = [('V1', 'Count or denominator'), ('V2', 'Independent recomputation'), ('V3', 'Sensitivity analysis'),
          ('V4', 'Assumption check on inputs'), ('V5', 'Plausibility'), ('V6', 'Domain diagnostic'),
          ('any', 'Any check')]
CHANNELS = [('Galaxy installed-tool jobs', GAL), ('Galaxy UDT jobs', GAL), ('shell (Galaxy runs)', GAL),
            ('shell (custom code runs)', CODE)]
rng = np.random.default_rng(SEED + 7)


# ---------------------------------------------------------------- helpers
def axes_mm(fig, x, y, w, h, H):
    return fig.add_axes([x / W, 1 - (y + h) / H, w / W, h / H])


def label(fig, x, y, letter, title, H, note=None):
    fig.text(x / W, 1 - y / H, letter, fontsize=8, fontweight='bold', va='top', ha='left')
    fig.text((x + 4.4) / W, 1 - (y + 0.5) / H, title, fontsize=6.5, fontweight='bold', va='top', ha='left')
    if note:
        fig.text((x + 4.4) / W, 1 - (y + 4.4) / H, note, fontsize=5, color=style.INK2, va='top', ha='left',
                 linespacing=1.2)


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    d = 1 + z ** 2 / n
    c = (p + z ** 2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / d
    return c - h, c + h


def kappa(a, b):
    a, b = np.asarray(a), np.asarray(b)
    po = np.mean(a == b)
    pe = sum(np.mean(a == c) * np.mean(b == c) for c in set(a) | set(b))
    return (po - pe) / (1 - pe)


def cluster_diff(d):
    """Galaxy - custom code share correct (points), with a cluster-bootstrap interval (clusters within benchmark)."""
    g = d.groupby(['cluster', 'env']).ok.agg(['sum', 'count']).unstack('env', fill_value=0)
    w = rng.multinomial(len(g), np.full(len(g), 1 / len(g)), size=B)
    sG, nG = w @ g[('sum', GAL)].values, w @ g[('count', GAL)].values
    sC, nC = w @ g[('sum', CODE)].values, w @ g[('count', CODE)].values
    draws = 100 * (sG / nG - sC / nC)
    est = 100 * (g[('sum', GAL)].sum() / g[('count', GAL)].sum() - g[('sum', CODE)].sum() / g[('count', CODE)].sum())
    return est, np.percentile(draws, 2.5), np.percentile(draws, 97.5)


def load_runs():
    r = pd.read_csv(SCORED)
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    return r


# ---------------------------------------------------------------- statistics
def exposure(r):
    t = pd.read_csv(os.path.join(OUT, 'answer_exposure_tiers.csv'))
    m = r.merge(t[['benchmark', 'task', 'cfg', 'env', 'replicate', 'tier']],
                on=['benchmark', 'task', 'cfg', 'env', 'replicate'], how='left')
    m['tier'] = m.tier.fillna('none')                    # 12 untraced CompBioBench runs: no record, counted as none
    counts = m.groupby(['benchmark', 'env', 'tier']).size().unstack('tier', fill_value=0).reindex(
        columns=[x for x, _, _ in TIERS], fill_value=0)
    sens = []
    for bm in ['BixBench50', 'CompBio']:
        d = m[m.benchmark == bm]
        for name, keep in (('All runs', d), ('Without verified or probable exposure',
                                             d[~d.tier.isin(['verified', 'probable'])]),
                           ('Without any benchmark search', d[d.tier == 'none'])):
            est, lo, hi = cluster_diff(keep)
            sens.append(dict(benchmark=bm, population=name, diff=est, lo=lo, hi=hi, runs=len(keep)))
    acc = m.groupby(['benchmark', 'tier']).ok.agg(['mean', 'size']).reset_index()
    return counts, pd.DataFrame(sens), acc


def second_rater_causes():
    a2 = pd.DataFrame([o for f in sorted(glob.glob(os.path.join(ANN, 'coded', 'A2_batch*.json'))) for o in json.load(open(f))])
    m = a2.merge(pd.read_csv(os.path.join(ANN, 'A2_key.csv')), on='code')
    m['orig'], m['new'] = m.p.map(GROUP), m.primary.map(GROUP)
    m['orig2'], m['new2'] = m.s.map(GROUP), m.secondary.map(GROUP)
    tab = pd.crosstab(m.orig, m.new).reindex(index=GROUPS, columns=GROUPS, fill_value=0)
    either = ((m.orig == m.new) | (m.orig == m.new2) | (m.orig2 == m.new)).mean()
    return tab, dict(items=len(m), agree=(m.orig == m.new).mean(), kappa=kappa(m.orig, m.new), either=either)


def second_rater_classes():
    a1 = pd.DataFrame(json.load(open(os.path.join(ANN, 'coded', 'A1_part1.json'))) +
                      json.load(open(os.path.join(ANN, 'coded', 'A1_part2.json'))))
    m = a1.merge(pd.read_csv(os.path.join(ANN, 'A1_key.csv')), on='code')
    m['rule'] = m.rule_class.str.split(' ').str[0]
    m['same'] = m['class'] == m.rule
    m['fix'] = m.rule.map(FIX)
    m['fix_in'] = [f in p if isinstance(f, str) else np.nan for f, p in zip(m.fix, m.prevent)]   # was `if f`, true for NaN
    m['agent_only'] = [p == ['Agent error only'] for p in m.prevent]
    m['multiple'] = [len([x for x in p if x not in ('Agent error only', 'Cannot tell')]) > 1 for p in m.prevent]
    per = m.groupby('rule').same.agg(['sum', 'size'])
    classified = m[~m.rule.isin(['X', 'Z'])]
    info = dict(items=len(m), agree_all=m.same.mean(), agree_classified=classified.same.mean(),
                kappa_classified=kappa(classified.rule, classified['class']),
                fix_supported=m.fix_in.dropna().mean(), agent_only=m.agent_only.mean(), multiple=m.multiple.mean())
    return per, info


def verification(r):
    D = pd.DataFrame([o for f in sorted(glob.glob(os.path.join(ANN, 'coded', 'D_batch*.json'))) for o in json.load(open(f))])
    rows = []
    for o in D.itertuples():
        row = dict(code=o.code, changed=o.changed_conclusion)
        for k, _ in CHECKS[:-1]:
            row[k] = bool(getattr(o, k)['present'])
        rows.append(row)
    d = pd.DataFrame(rows)
    d.loc[d.code == 'D043', 'V5'] = False          # an answer-file download, not a plausibility check (see README)
    d['any'] = d[[k for k, _ in CHECKS[:-1]]].any(axis=1)
    d = d.merge(pd.read_csv(os.path.join(ANN, 'D_key.csv')), on='code')
    # outcome from the site-matched grades, not the grade at sampling time (D079, bix-53-q2, was
    # sampled as incorrect and is correct on the results site)
    cur = r.assign(ok_now=(r.score >= 1 - 1e-9).astype(int)).set_index(['benchmark', 'task', 'cfg', 'env', 'replicate']).ok_now
    d['ok_sampled'] = d.ok
    d['ok'] = cur.reindex(pd.MultiIndex.from_frame(d[['benchmark', 'task', 'cfg', 'env', 'replicate']])).values
    assert d.ok.notna().all()
    out = []
    for by in ('ok', 'env'):
        for val, g in d.groupby(by):
            for k, _ in CHECKS:
                lo, hi = wilson(int(g[k].sum()), len(g))
                out.append(dict(by=by, group=val, check=k, value=100 * g[k].mean(), lo=100 * lo, hi=100 * hi,
                                n=len(g)))
    changed = pd.crosstab(d.ok, d.changed)
    return pd.DataFrame(out), changed, d


def episodes():
    e = pd.read_csv(os.path.join(OUT, 'failure_episodes.csv'))
    rows = []
    for ch, env in CHANNELS:
        g = e[e.channel == ch]
        per = g.groupby('cluster').resolved.agg(['sum', 'count'])
        w = rng.multinomial(len(per), np.full(len(per), 1 / len(per)), size=B)
        draws = 100 * (w @ per['sum'].values) / (w @ per['count'].values)
        rows.append(dict(channel=ch, env=env, episodes=len(g), resolved=100 * g.resolved.mean(),
                         lo=np.percentile(draws, 2.5), hi=np.percentile(draws, 97.5),
                         correct_resolved=100 * g[g.resolved].run_correct.mean(),
                         correct_unresolved=100 * g[~g.resolved].run_correct.mean()))
    return pd.DataFrame(rows)


def trace_of(run_id, task):
    for raw in gzip.open(SUMMARIES, 'rt'):
        s = json.loads(raw)
        if s['run_id'] == run_id and s['task'] == task:
            p = s['trace']
            return p if os.path.exists(p) else p + '.gz'


def parameter_example():
    """bix-43-q4, GPT-5.5 Galaxy replicate 1: the request blocked before the job and the corrected request."""
    path = trace_of('galaxy_codex_gpt_5_5_r1', 'bix-43-q4')
    op = gzip.open if path.endswith('.gz') else open
    calls = []
    with op(path, 'rt', newline='\n') as f:
        for i, line in enumerate(f, 1):
            if '"run_galaxy_tool_and_wait"' in line and '"item.completed"' in line and 'gseapy_enrichr' in line:
                it = json.loads(line)['item']
                res = it.get('result') or {}
                body = res.get('structured_content') or (json.loads(res['content'][0]['text'])
                                                         if res.get('content') else {})
                mism = body.get('mismatches') or (body.get('parameter_provenance') or {}).get('mismatches')
                calls.append(dict(line=i, inputs=it['arguments'].get('tool_inputs'), status=body.get('status'),
                                  mismatches=mism))
    first = next(c for c in calls if c['status'] == 'validation_parameter_mismatch' and c['mismatches'])
    fixed = next(c for c in calls if c['line'] > first['line'] and c['status'] == 'ok')
    mm = first['mismatches'][0]
    return dict(tool='gseapy_enrichr 0.1.0+galaxy2', path=mm['path'], requested=mm['expected'],
                resolved=mm['resolved'] or '(empty)', first_line=first['line'], fixed_line=fixed['line'],
                first_form='nested: gene_sets = {source, library_name, organism}',
                fixed_form='flat: gene_sets|library_name = ' + str(fixed['inputs'].get('gene_sets|library_name')))


def variant_case(r):
    """Outcome of every run on variant-status-q1 and whether it ran a read-position diagnostic as a UDT or command."""
    v = r[r.task == 'variant-status-q1'][['cfg', 'env', 'replicate', 'ok']].copy()
    pat = re.compile(r'read[-_ ]?(position|cycle|end)|position in (the )?read|query_position|distance from (the )?'
                     r'(read )?end|end of (the )?read', re.I)
    diag = {}
    for raw in gzip.open(SUMMARIES, 'rt'):
        s = json.loads(raw)
        if s['task'] != 'variant-status-q1':
            continue
        cfg = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
               'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro'}.get(s['model'])
        if not cfg or not s.get('trace'):
            continue
        p = s['trace'] if os.path.exists(s['trace']) else s['trace'] + '.gz'
        op = gzip.open if p.endswith('.gz') else open
        ran = False
        with op(p, 'rt', newline='\n') as f:
            for line in f:
                if '"item.completed"' in line and pat.search(line):
                    it = json.loads(line)['item']
                    if it.get('tool') == 'run_galaxy_udt_and_wait':     # the UDT definition or its result
                        ran = True
                    elif it.get('type') == 'command_execution' and pat.search(str(it.get('command'))):
                        ran = True
                    if ran:
                        break
        diag[(cfg, s['condition'], int(s['replicate']))] = ran
    v['diagnostic'] = [diag.get((c, e, rep), False) for c, e, rep in zip(v.cfg, v.env, v.replicate)]
    return v


# ---------------------------------------------------------------- drawing: Extended Data Fig. 6
def ed6(counts, sens, acc, tab, cinfo, per, ainfo):
    H = 112.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    label(fig, 0, 0, 'a', 'Runs that reached benchmark answers during the run', H,
          'Highest tier per run, from the traces (web pages themselves are not logged)')
    ax = axes_mm(fig, 40.0, 14.0, 44.0, 20.0, H)
    rows = [(bm, env) for bm in ('BixBench50', 'CompBio', 'IWC') for env in ENVS]
    ypos = [0, 1, 2.4, 3.4, 4.8, 5.8]
    for (bm, env), y in zip(rows, ypos):
        t = counts.loc[(bm, env)] if (bm, env) in counts.index else pd.Series(0, index=[x for x, _, _ in TIERS])
        n, left = t.sum(), 0
        for code, _, col in TIERS:
            v = 100 * t[code] / n
            ax.barh(y, v, left=left, height=0.7, color=col, ec='white', lw=0.3, zorder=3)
            left += v
        exposed = int(t['verified'] + t['probable'])
        ax.text(101.5, y, f'{exposed} / {int(n):,}', ha='left', va='center', fontsize=5)
        ax.text(-1.5, y, style.ENV_LABEL[env], ha='right', va='center', fontsize=5)
    for bm, y in (('BixBench50', 0.5), ('CompBio', 2.9), ('IWC', 5.3)):
        ax.text(-0.42, y, BENCH_NAME[bm].replace('-Verified-50', '-\nVerified-50'),
                transform=blended_transform_factory(ax.transAxes, ax.transData), ha='right', va='center', fontsize=5,
                fontweight='bold', linespacing=1.1)
    ax.text(101.5, -1.0, 'Exposed / runs', ha='left', va='center', fontsize=5, color=style.INK2)
    ax.set_ylim(6.4, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Runs (%)', labelpad=1.5)
    ax.legend(handles=[Patch(fc=c, ec=style.NEUTRAL_MID if c == '#E8E8E8' else c, lw=0.3, label=l) for _, l, c in TIERS],
              loc='upper left', bbox_to_anchor=(-0.85, -0.32), ncol=2, fontsize=5, handlelength=0.9,
              columnspacing=0.8, labelspacing=0.25, borderaxespad=0)

    label(fig, 100.0, 0, 'b', 'Galaxy minus custom code without exposed runs', H)
    bx = axes_mm(fig, 146.0, 12.0, 32.0, 26.0, H)
    y = 0
    for bm in ('BixBench50', 'CompBio'):
        bx.text(-1.38, y, BENCH_NAME[bm], transform=blended_transform_factory(bx.transAxes, bx.transData), ha='left',
                va='center', fontsize=5, fontweight='bold')
        y += 0.9
        for t in sens[sens.benchmark == bm].itertuples():
            bx.plot([t.lo, t.hi], [y, y], color=style.INK, lw=0.7)
            bx.plot(t.diff, y, ls='', marker='D' if t.population == 'All runs' else 'o', ms=2.6,
                    mfc=style.INK if t.population == 'All runs' else 'white', mec=style.INK, mew=0.6)
            bx.text(-0.04, y, f'{t.population} ({t.runs:,})', transform=blended_transform_factory(bx.transAxes,
                    bx.transData), ha='right', va='center', fontsize=5)
            y += 0.9
        y += 0.4
    bx.axvline(0, color=style.INK2, lw=0.6)
    bx.set_ylim(y - 0.4, -0.6)
    bx.set_yticks([])
    bx.spines['left'].set_visible(False)
    bx.set_xlim(-8, 8)
    style.grid_x(bx)
    bx.set_xlabel('Runs correct, percentage points', labelpad=1.5)

    label(fig, 0, 54.0, 'c', 'Second rater for the failure-cause audit (BixBench-Verified-50)', H,
          f'{cinfo["items"]} incorrect runs; agreement {100 * cinfo["agree"]:.0f}%, Cohen\'s κ = {cinfo["kappa"]:.2f}; '
          f'{100 * cinfo["either"]:.0f}% counting secondary causes')
    cx = axes_mm(fig, 30.0, 66.0, 32.0, 32.0, H)
    m = tab.values.astype(float)
    cx.imshow(m, cmap='Greys', vmin=0, vmax=m.max() * 1.3)
    for i in range(len(GROUPS)):
        for j in range(len(GROUPS)):
            cx.text(j, i, f'{int(m[i, j])}', ha='center', va='center', fontsize=5,
                    color='white' if m[i, j] > m.max() * 0.6 else style.INK, fontweight='bold' if i == j else 'normal')
    cx.set_xticks(range(len(GROUPS)), GROUPS, fontsize=5, rotation=45, ha='right')
    cx.set_yticks(range(len(GROUPS)), GROUPS, fontsize=5)
    cx.tick_params(length=0, pad=1.5)
    for s in cx.spines.values():
        s.set_visible(False)
    cx.set_xlabel('Second rater', labelpad=1.5)
    cx.set_ylabel('Original audit', labelpad=1.5)

    label(fig, 100.0, 54.0, 'd', 'Second rater for the failure classes of failed requests', H,
          f'{ainfo["items"]} requests, 10 per class; agreement {100 * ainfo["agree_classified"]:.0f}% for classified '
          f'requests\n(κ = {ainfo["kappa_classified"]:.2f}); the rule\'s improvement group was among the rater\'s in '
          f'{100 * ainfo["fix_supported"]:.0f}%')
    dx = axes_mm(fig, 108.0, 70.0, 70.0, 22.0, H)
    order = [c for c in ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'B1', 'B2', 'B3', 'B4', 'B5', 'X', 'Z']
             if c in per.index]
    vals = [100 * per.loc[c, 'sum'] / per.loc[c, 'size'] for c in order]
    dx.bar(range(len(order)), vals, width=0.7, color=style.NEUTRAL_DARK, zorder=3)
    dx.set_xticks(range(len(order)), order, fontsize=5)
    dx.tick_params(axis='x', length=0)
    dx.set_ylim(0, 100)
    dx.set_yticks([0, 50, 100])
    style.grid_y(dx)
    dx.set_ylabel('Same class (%)')
    dx.text(1.0, -0.22, f'Rater judged the failure an agent error only in {100 * ainfo["agent_only"]:.0f}%; more than '
            f'one improvement plausible in {100 * ainfo["multiple"]:.0f}%', transform=dx.transAxes, ha='right',
            va='top', fontsize=5, color=style.INK2)
    save(fig, 'ed_fig6', 'Extended Data Fig. 6 | Independent checks of the audits and of benchmark integrity')


# ---------------------------------------------------------------- drawing: Extended Data Fig. 7
def ed7(ver, changed, eps, ex, case):
    H = 150.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    label(fig, 0, 0, 'a', 'Verification checks in 80 coded runs (coder blind to the grade)', H,
          '10 runs per benchmark × condition × outcome; 95% Wilson intervals')
    for j, (by, groups, title) in enumerate((('ok', [(1, 'Correct', style.INK), (0, 'Incorrect', '#999999')],
                                               'By outcome'),
                                              ('env', [(CODE, 'Custom code', style.CODE), (GAL, 'Galaxy', style.GALAXY)],
                                               'By condition'))):
        ax = axes_mm(fig, 40.0 + j * 50.0, 14.0, 40.0, 32.0, H)
        for k, (val, lab, col) in enumerate(groups):
            d = ver[(ver.by == by) & (ver.group == val)].set_index('check').reindex([c for c, _ in CHECKS])
            y = np.arange(len(CHECKS)) + (k - 0.5) * 0.3
            ax.errorbar(d.value, y, xerr=[d.value - d.lo, d.hi - d.value], fmt='o' if k == 0 else 's', ms=2.8,
                        color=col, mfc=col, mec='white', mew=0.3, elinewidth=0.7, capsize=0, label=lab)
        ax.set_yticks(range(len(CHECKS)), [l for _, l in CHECKS] if j == 0 else [''] * len(CHECKS), fontsize=5)
        ax.set_ylim(len(CHECKS) - 0.4, -0.6)
        ax.set_xlim(0, 100)
        style.grid_x(ax)
        ax.tick_params(axis='y', length=0)
        ax.set_xlabel('Runs with the check (%)', labelpad=1.5)
        ax.set_title(title, fontsize=5.5, fontweight='bold', pad=3, loc='left')
        ax.legend(loc='lower right', bbox_to_anchor=(1.0, 1.0), ncol=2, fontsize=5, borderaxespad=0.2,
                  handletextpad=0.2, columnspacing=0.8)
    yes = changed.get('yes', pd.Series(0, index=changed.index))
    fig.text(142.0 / W, 1 - 16.0 / H, 'A check changed the method\nor answer in\n'
             f'{int(yes.get(1, 0))} of {int(changed.loc[1].sum())} correct runs\n'
             f'{int(yes.get(0, 0))} of {int(changed.loc[0].sum())} incorrect runs', fontsize=5, va='top',
             linespacing=1.3)

    label(fig, 0, 56.0, 'b', 'Failed steps later re-run without error in the same run', H,
          'Galaxy jobs by tool; shell commands by the analysis program or script they ran (inline code excluded)')
    bx = axes_mm(fig, 40.0, 70.0, 50.0, 20.0, H)
    for i, t in enumerate(eps.itertuples()):
        bx.barh(i, t.resolved, height=0.6, color=style.ENV_COLOR[t.env], zorder=3, alpha=0.85)
        bx.plot([t.lo, t.hi], [i, i], color=style.INK, lw=0.7, zorder=4)
        bx.text(-1.5, i, f'{t.channel.replace("shell", "Shell commands").replace("custom code", "custom-code")} ({t.episodes:,})', ha='right', va='center',
                fontsize=5)
        bx.text(101.5, i, f'{t.correct_resolved:.0f}% / {t.correct_unresolved:.0f}%', ha='left', va='center',
                fontsize=5)
    bx.text(101.5, -1.0, 'Runs correct: re-run / not', ha='left', va='center', fontsize=5, color=style.INK2)
    bx.set_ylim(len(eps) - 0.4, -0.6)
    bx.set_yticks([])
    bx.spines['left'].set_visible(False)
    bx.set_xlim(0, 100)
    style.grid_x(bx)
    bx.set_xlabel('Failed steps later re-run without error (%)', labelpad=1.5)

    label(fig, 0, 100.0, 'c', 'A parameter check that stopped a job', H)
    cx = axes_mm(fig, 4.0, 108.0, 84.0, 36.0, H)
    cx.set_axis_off()
    cx.set_xlim(0, 84)
    cx.set_ylim(36, 0)
    cx.add_patch(Rectangle((0, 0), 84, 36, fc=style.LIGHT, ec='none'))
    lines = [('Task', 'bix-43-q4, GPT-5.5, Galaxy, replicate 1 (Reactome enrichment)'),
             ('Tool', ex['tool']),
             ('First request', ex['first_form']),
             ('Interface check', f'{ex["path"]}: requested {ex["requested"]},\nGalaxy would bind {ex["resolved"]}; '
                                 'the job was not submitted'),
             ('Agent response', 'Resubmitted with flat parameter keys'),
             ('Second request', ex['fixed_form'] + '; parameters matched; job ran')]
    y = 2.5
    for k, v in lines:
        cx.text(1.5, y, k, fontsize=5, fontweight='bold', va='top')
        cx.text(20.0, y, v, fontsize=5, va='top', linespacing=1.2)
        y += 4.6 + 2.2 * v.count('\n')

    label(fig, 92.0, 100.0, 'd', 'A selected case: variant-status-q1 (CompBioBench)', H,
          'Read-end artefacts mimic an alternate allele; answers are not shown')
    dx = axes_mm(fig, 96.0, 112.0, 84.0, 32.0, H)
    dx.set_axis_off()
    dx.set_xlim(0, 84)
    dx.set_ylim(32, 0)
    xs = {CODE: 36.0, GAL: 58.0}
    for env in ENVS:
        dx.text(xs[env] + 2.6, 1.0, style.ENV_LABEL[env], fontsize=5, ha='center', va='top', fontweight='bold')
    for i, c in enumerate(CFG):
        y = 6.5 + i * 3.4
        dx.text(1.0, y, c, fontsize=5, va='center')
        for env in ENVS:
            for rep in (1, 2, 3):
                row = case[(case.cfg == c) & (case.env == env) & (case.replicate == rep)]
                ok = bool(row.ok.iloc[0]) if len(row) else False
                dg = bool(row.diagnostic.iloc[0]) if len(row) else False
                x = xs[env] + (rep - 1) * 2.6
                dx.plot(x, y, ls='', marker='o', ms=2.8, mfc=style.INK if ok else 'white', mec=style.INK, mew=0.5)
                if dg:
                    dx.add_patch(Rectangle((x - 1.1, y - 1.1), 2.2, 2.2, fill=False, ec=style.OI_VERMILLION
                                           if env == CODE else style.GALAXY, lw=0.6))
    n_ok = int(case.ok.sum())
    n_dg = int(case.diagnostic.sum())
    cc = case[(case.env == CODE) & case.diagnostic]
    dx.text(1.0, 22.0, f'● accepted   ○ rejected   □ ran a read-position diagnostic ({n_dg} runs)\n'
            f'{n_ok} of {len(case)} runs accepted. GPT-5.6 Sol in Galaxy ran the diagnostic as a UDT in\n'
            f'replicates 2 and 3, and both were accepted; {len(cc)} custom-code runs also ran it '
            f'({int(cc.ok.sum())} accepted).', fontsize=5, va='top', linespacing=1.3)
    save(fig, 'ed_fig7', 'Extended Data Fig. 7 | Verification, recovery and selected cases')


def save(fig, name, title):
    style.enforce_min_font(fig)
    fig.savefig(os.path.join(OUT, f'{name}.svg'), metadata={'Title': title})
    fig.savefig(os.path.join(OUT, f'{name}.pdf'), metadata={'Title': title})
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, f'{name}.png'), dpi=(600, 600))
    plt.close(fig)


def main():
    panel_io.record(globals(), 'ed_validation', ['ed6', 'ed7', 'save'])   # figures/panel_data/ed_validation.json
    r = load_runs()
    counts, sens, acc = exposure(r)
    tab, cinfo = second_rater_causes()
    per, ainfo = second_rater_classes()
    ver, changed, dcoded = verification(r)
    eps = episodes()
    ex = parameter_example()
    case = variant_case(r)
    for name, t in (('exposure', counts), ('sensitivity', sens), ('accuracy by tier', acc), ('causes', tab),
                    ('classes', per), ('verification', ver), ('changed', changed), ('episodes', eps)):
        print(name)
        print(t.round(3).to_string())
    print(cinfo, ainfo, ex)
    ed6(counts, sens, acc, tab, cinfo, per, ainfo)
    ed7(ver, changed, eps, ex, case)
    rows = []
    for (bm, env), t in counts.iterrows():
        for tier in t.index:
            rows.append(dict(panel='a', benchmark=bm, condition=env, measure=f'runs: {tier}', value=int(t[tier])))
    for t in sens.itertuples():
        rows.append(dict(panel='b', benchmark=t.benchmark, condition='galaxy-custom_code', group=t.population,
                         measure='runs_correct_difference_points', value=t.diff, ci95_low=t.lo, ci95_high=t.hi,
                         n=t.runs))
    for t in acc.itertuples():
        rows.append(dict(panel='b', benchmark=t.benchmark, group=t.tier, measure='runs_correct_share',
                         value=getattr(t, 'mean'), n=getattr(t, 'size')))
    for o in GROUPS:
        for n_ in GROUPS:
            rows.append(dict(panel='c', group=f'original {o} | second rater {n_}', measure='runs', value=int(tab.loc[o, n_])))
    for k, v in cinfo.items():
        rows.append(dict(panel='c', measure=k, value=v))
    for c, t in per.iterrows():
        rows.append(dict(panel='d', group=c, measure='items_same_class', value=int(t['sum']), n=int(t['size'])))
    for k, v in ainfo.items():
        rows.append(dict(panel='d', measure=k, value=v))
    out = pd.DataFrame(rows).reindex(columns=['panel', 'benchmark', 'condition', 'group', 'measure', 'value',
                                              'ci95_low', 'ci95_high', 'n'])
    out['condition'] = out.condition.str.replace('open_ended_code', 'custom_code')
    out.to_csv(os.path.join(OUT, 'ed_fig6_source_data.csv'), index=False, float_format='%.4f')
    rows = []
    for t in ver.itertuples():
        rows.append(dict(panel='a', group=f'{t.by}={t.group}', measure=f'pct_runs_with: {dict(CHECKS)[t.check]}',
                         value=t.value, ci95_low=t.lo, ci95_high=t.hi, n=t.n))
    for ok_, t in changed.iterrows():
        for k, v in t.items():
            rows.append(dict(panel='a', group=f'ok={ok_}', measure=f'changed_conclusion: {k}', value=int(v)))
    for t in eps.itertuples():
        rows.append(dict(panel='b', group=t.channel, measure='pct_failed_steps_later_rerun_ok', value=t.resolved,
                         ci95_low=t.lo, ci95_high=t.hi, n=t.episodes))
        rows.append(dict(panel='b', group=t.channel, measure='pct_runs_correct_if_rerun', value=t.correct_resolved))
        rows.append(dict(panel='b', group=t.channel, measure='pct_runs_correct_if_not', value=t.correct_unresolved))
    for k, v in ex.items():
        rows.append(dict(panel='c', measure=k, value=str(v)))
    for t in case.itertuples():
        rows.append(dict(panel='d', group=f'{t.cfg} | {t.env} | r{t.replicate}', measure='accepted; diagnostic',
                         value=f'{int(t.ok)}; {int(t.diagnostic)}'))
    out = pd.DataFrame(rows).reindex(columns=['panel', 'group', 'measure', 'value', 'ci95_low', 'ci95_high', 'n'])
    out['group'] = out.group.str.replace('open_ended_code', 'custom_code')
    out.to_csv(os.path.join(OUT, 'ed_fig7_source_data.csv'), index=False, float_format='%.4f')


if __name__ == '__main__':
    main()
