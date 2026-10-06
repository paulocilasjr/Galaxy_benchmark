"""Fig. 5: Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks.

Panels:
a, Galaxy / custom-code token ratios for each benchmark (including IWC, where Galaxy did not use more input): total
   input (including cached context), uncached input and output tokens. Primary estimate, the geometric mean of paired
   task-model ratios (typical paired-task demand); secondary, the ratio of total tokens over the same cells (aggregate
   consumption). Below, input tokens of incorrect relative to correct runs of the same task and model;
b, where the extra input comes from: Galaxy / custom-code ratios of actions and of input tokens per action, by
   benchmark; right, the characters Galaxy returned to the agent, by what the request was for;
c, what the retained record holds for each analysis step in each condition, separating structured records from free
   text in the retained trace, records of the environment only, and evidence that was not retained or not recorded
   (unknown, not absent);
d, one analysis step recorded both ways: PhyKIT relative composition variability on bix-45-q1 (GPT-5.6 Sol, replicate
   1), the tool-version case of Fig. 2d.

Extended Data Fig. 5: a, accuracy against median input tokens per model and condition, by benchmark; b, input tokens of
correct and incorrect runs (the first version's panel b); c, input tokens against actions (the first version's panel c).

Input tokens include cached context unless stated. Actions are the agent's tool calls (shell commands, Galaxy interface
calls, web searches or fetches, file reads, writes and edits), as in On-demand Fig. 6. Tokens differ between models in
price, so ratios are not monetary costs. A run is correct when accepted or, for IWC, at >= 0.99 output agreement.
Intervals are 95% percentile cluster-bootstrap intervals (clusters are BixBench source capsules, otherwise tasks); P values
come from paired cluster sign-flip randomization tests (200,000 draws; exact with at most 16 clusters).
Writes figures/fig5.{svg,pdf,png}, fig5_source_data.csv, ed_fig5.{svg,pdf,png} and ed_fig5_source_data.csv.
"""
import glob
import io
import itertools
import json
import os
import re
import sys
import textwrap

import numpy as np
import openpyxl
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
import style  # noqa: E402  (sets rcParams on import)
from style import plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch, Rectangle  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402
from PIL import Image  # noqa: E402

plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic',  # italic P
                     'mathtext.cal': 'Arial', 'mathtext.bf': 'Arial:bold', 'mathtext.sf': 'Arial'})
style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition

AN = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis')
GC = os.path.join(ROOT, 'manuscript_narrative', 'derived', 'galaxy_calls')
DESIGN = os.path.join(ROOT, 'manuscript_narrative', 'derived', 'design', 'per_run_design_metadata.csv')
ACTIONS = os.path.join(ROOT, 'manuscript_material', 'on_demand', 'Source_Data_OD_Fig6.xlsx')
OUT = os.path.join(ROOT, 'figures')
B, SEED, B_PERM, B_MEDIAN = 20000, 20261002, 200000, 2000
W, MM = 180.0, 1 / 25.4
CFG = style.CONFIGS
ENVS = style.ENVS                                    # custom code first, always
CODE, GAL = ENVS
BENCH = style.BENCH
BENCH_NAME = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
TICK = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6\nSol', 'GPT-5.6 Luna': 'GPT-5.6\nLuna',
        'DeepSeek V4 Pro': 'DeepSeek\nV4 Pro'}
MODEL_COLOR = dict(zip(CFG, ['#117733', '#AA4499', '#DDCC77', '#332288']))
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
KEY = ['benchmark', 'task', 'cfg', 'env', 'replicate']
TRACE_MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
               'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
               'codex_deepseek_v4_pro': 'DeepSeek V4 Pro'}
TOKEN_KINDS = [('input_tokens', 'Input, incl. cached'), ('uncached', 'Uncached input'), ('output_tokens', 'Output')]
# Galaxy interface operations, grouped; tool discovery is highlighted.
OPS = [('Finding tools (search, tool descriptions)', ('search_galaxy_tools', 'inspect_galaxy_tool')),
       ('Running installed tools', ('run_galaxy_tool_and_wait',)),
       ('Running agent-written code (UDTs)', ('run_galaxy_udt_and_wait',)),
       ('Reading results (history, datasets)', ('inspect_galaxy_history', 'peek_galaxy_dataset',
                                                 'inspect_archive_inventory')),
       ('Waiting for jobs, uploading files', ('wait_for_galaxy_jobs', 'stage_workspace_file'))]
OP_COLOR = [style.GALAXY, style.NEUTRAL_DARK, '#8a8a8a', '#bdbdbd', '#e3e3e3']
# Panel c: what the retained record holds for each analysis step. Galaxy steps are Galaxy jobs; custom-code steps are
# the agent's shell commands that the run-level evidence labels as analysis.
EVIDENCE = [os.path.join(ROOT, b, 'analysis', '*', 'history_analysis_evidence.json') for b in ('BixBench_50', 'CompBio', 'IWC')]
NOT_PRIMARY = {'deepseek_v4_pro_via_claude_code_superseded', 'codex_gpt_6_astra'}
VERSION_CMD = re.compile(r'--version|__version__|packageVersion|pip (show|list|freeze)|conda (list|env export)|'
                         r'sessionInfo|importlib\.metadata|\bversion\(\)', re.I)
ELEMENTS = [('software', 'Software and version'), ('parameters', 'Parameters'), ('inputs', 'Input data'),
            ('outputs', 'Output data'), ('status', 'Execution status'), ('command', 'Command or code'),
            ('analysis', 'Whole analysis (per run)')]
LEVELS = [('S', 'Structured record', '#3A3A3A'), ('T', 'Free text in the retained trace', '#9A9A9A'),
          ('P', 'Partial: environment image or metadata only', '#D6D6D6'),
          ('N', 'Not retained or not recorded (unknown)', 'white')]
EXAMPLE = ('bix-45-q1', 'galaxy_codex_gpt_5_6_sol_r1', 'open_ended_code_codex_gpt_5_6_sol_r1')
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- data
def load_runs():
    r = pd.read_csv(os.path.join(AN, 'accuracy_primary_runs.csv'))
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = r.score >= r.benchmark.map(CORRECT_AT) - 1e-9
    t = pd.read_csv(os.path.join(AN, 'token_run_observations.csv'))
    t = t[t.model_primary]
    r = r.merge(t[KEY + ['input_tokens', 'cached', 'output_tokens']], on=KEY, how='left')
    ws = openpyxl.load_workbook(ACTIONS, read_only=True)['abf_runs']
    rows = list(ws.iter_rows(values_only=True))
    a = pd.DataFrame(rows[1:], columns=rows[0])
    a = a[a.model_configuration != 'DeepSeek V4 Pro (Claude Code, superseded)']
    a = a.assign(benchmark=a.benchmark.map({'BixBench-Verified-50': 'BixBench50', 'CompBioBench': 'CompBio',
                                            'IWC': 'IWC'}),
                 cfg=a.model_configuration.replace({'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro'}),
                 env=a.execution_condition.map({'Galaxy condition': GAL, 'Open-ended code condition': CODE}))
    r = r.merge(a[KEY + ['actions']], on=KEY, how='left')
    r['tokens_per_action'] = r.input_tokens / r.actions.where(r.actions > 0)
    r['uncached'] = r.input_tokens - r.cached
    return r


def load_calls():
    c = pd.read_csv(os.path.join(GC, 'calls.csv.gz'), low_memory=False,
                    usecols=['benchmark', 'task', 'model', 'replicate', 'tool', 'galaxy_server', 'chars_returned',
                             'tool_id_full'])
    return c[c.model.isin(TRACE_MODEL) & c.galaxy_server].assign(cfg=lambda x: x.model.map(TRACE_MODEL))


# ---------------------------------------------------------------- statistics
def holm(p):
    p = np.asarray(p, float)
    order, adj, run = np.argsort(p), np.empty(len(p)), 0.0
    for i, k in enumerate(order):
        run = max(run, (len(p) - i) * p[k])
        adj[k] = min(1.0, run)
    return adj


def signflip_p(d):
    d = np.asarray(d, float)
    if len(d) <= 16:
        signs = np.array(list(itertools.product([-1.0, 1.0], repeat=len(d))))
        return float(np.mean(np.abs(signs @ d) >= abs(d.sum()) - 1e-12))
    hits = 0
    for _ in range(B_PERM // 20000):
        null = rng.choice([-1.0, 1.0], size=(20000, len(d))) @ d
        hits += np.sum(np.abs(null) >= abs(d.sum()) - 1e-12)
    return (1 + hits) / (B_PERM + 1)


def paired_ratio(cells):
    """cells: benchmark, cluster and d = log ratio per paired cell -> geometric-mean ratio, 95% CI, sign-flip P, n."""
    est = np.exp(cells.d.mean())
    num, den = 0.0, 0.0
    for _, g in cells.groupby('benchmark'):
        per = g.groupby('cluster').d.agg(['sum', 'count'])
        w = rng.multinomial(len(per), np.full(len(per), 1 / len(per)), size=B)
        num, den = num + w @ per['sum'].values, den + w @ per['count'].values
    lo, hi = np.exp(np.percentile(num / den, [2.5, 97.5]))
    return est, lo, hi, signflip_p(cells.groupby('cluster').d.sum().values), len(cells)


def paired_cells(r, value):
    cell = r.dropna(subset=[value]).groupby(['benchmark', 'cluster', 'task', 'cfg', 'env'])[value].median()
    cell = cell.unstack('env').dropna()
    cell = cell[(cell[GAL] > 0) & (cell[CODE] > 0)]
    return cell.assign(d=np.log(cell[GAL] / cell[CODE])).reset_index()


def ratio_of_totals(r, value, cells):
    """Total Galaxy / total custom-code tokens over the runs of the matched cells, with a cluster-bootstrap interval."""
    keep = cells[['benchmark', 'task', 'cfg']].drop_duplicates()
    d = r.merge(keep, on=['benchmark', 'task', 'cfg']).dropna(subset=[value])
    g = d.pivot_table(index='cluster', columns='env', values=value, aggfunc='sum').fillna(0)
    w = rng.multinomial(len(g), np.full(len(g), 1 / len(g)), size=B)
    draws = (w @ g[GAL].values) / (w @ g[CODE].values)
    return g[GAL].sum() / g[CODE].sum(), np.percentile(draws, 2.5), np.percentile(draws, 97.5)


def benchmark_ratios(r, kinds):
    rows = []
    for bm in BENCH:
        d = r[r.benchmark == bm]
        for value, lab in kinds:
            cells = paired_cells(d, value)
            est, lo, hi, p, n = paired_ratio(cells)
            tot, tlo, thi = ratio_of_totals(d, value, cells)
            rows.append(dict(benchmark=bm, kind=value, label=lab, ratio=est, lo=lo, hi=hi, p=p, cells=n,
                             total_ratio=tot, total_lo=tlo, total_hi=thi))
    out = pd.DataFrame(rows)
    out['p_holm'] = holm(out.p)
    return out


def outcome_ratios(r):
    """Incorrect / correct input tokens within replicate sets that have both, per condition (models pooled) and per
    condition and model."""
    d = r.dropna(subset=['input_tokens'])
    rows = []
    for key, s in d.groupby(['benchmark', 'cluster', 'task', 'cfg', 'env']):
        if s.ok.any() and (~s.ok).any():
            rows.append(dict(zip(['benchmark', 'cluster', 'task', 'cfg', 'env'], key),
                             d=np.log(s[~s.ok].input_tokens.median() / s[s.ok].input_tokens.median())))
    sets = pd.DataFrame(rows)
    per, pooled = [], []
    for env in ENVS:
        e = sets[sets.env == env]
        est, lo, hi, p, n = paired_ratio(e)
        pooled.append(dict(env=env, ratio=est, lo=lo, hi=hi, p=p, sets=n))
        for c in CFG:
            est, lo, hi, p, n = paired_ratio(e[e.cfg == c])
            per.append(dict(env=env, cfg=c, ratio=est, lo=lo, hi=hi, p=p, sets=n))
    per, pooled = pd.DataFrame(per), pd.DataFrame(pooled)
    per['p_holm'] = holm(per.p)
    pooled['p_holm'] = holm(pooled.p)
    return per, pooled


def replies(calls, r):
    """Characters Galaxy returned to the agent, by request type and benchmark; inspected-but-not-run tools; cached
    share of input."""
    rows = []
    for bm, c in calls.groupby('benchmark'):
        total = c.chars_returned.sum()
        for name, tools in OPS:
            s = c[c.tool.isin(tools)]
            rows.append(dict(benchmark=bm, operation=name, calls=len(s), chars=int(s.chars_returned.sum()),
                             char_pct=100 * s.chars_returned.sum() / total))
    fr = pd.read_csv(os.path.join(AN, 'token_interface_friction.csv'))
    never = fr[fr.measure == 'Inspected tools never run in the same run'].set_index('benchmark')
    cached = (r.dropna(subset=['input_tokens']).assign(share=lambda x: x.cached / x.input_tokens)
              .groupby(['benchmark', 'env']).share.median() * 100)
    return pd.DataFrame(rows), never, cached


def evidence(calls):
    """Share of analysis steps (runs, for the whole analysis) whose retained record holds each element, by level."""
    udt_ids = set(calls[calls.tool == 'run_galaxy_udt_and_wait'].tool_id_full.dropna())
    design = pd.read_csv(DESIGN, low_memory=False)
    image = (design.docker_image.notna() | design.docker_image_id.notna() | design.iso_image_id.notna())
    image = dict(zip(zip(design.benchmark, design.task, design.run_id), image))
    steps, runs = [], []
    for path in sorted(p for pattern in EVIDENCE for p in glob.glob(pattern)):
        d = json.load(open(path))
        for run in d['runs']:
            model = re.sub(r'_r\d+$', '', re.sub(r'^(galaxy|open_ended_code)_', '', run['run_id']))
            if model in NOT_PRIMARY:
                continue
            env = GAL if run['condition'] == 'galaxy' else CODE
            bm = {'bixbench': 'BixBench50', 'compbio': 'CompBio', 'iwc': 'IWC'}[run.get('benchmark') or
                                                                             d['task'].get('benchmark')]
            ev = run['events']
            printed = env == CODE and any(VERSION_CMD.search(str(e.get('command') or '')) for e in ev)
            img = image.get((bm, d['task']['task_id'], run['run_id']), False)
            hist = run['evidence_completeness'].get('public_history_contents')
            runs.append(dict(env=env, analysis={'retrieved': 'S', 'history_metadata_only': 'P'}.get(hist, 'N')
                             if env == GAL else 'N'))
            for e in ev:
                if env == GAL and not (e['execution_location'] == 'galaxy_job' and e['event_type'] == 'analysis'):
                    continue
                if env == CODE and not (e['execution_location'] == 'agent_runtime' and e['event_type'] == 'analysis'):
                    continue
                if env == GAL:
                    tool = str(e.get('tool') or '')
                    has = lambda k: str(e.get(k)) not in ('[]', 'None', '', 'nan')   # noqa: E731
                    steps.append(dict(env=env, software='T' if tool in udt_ids else 'S',
                                      parameters='S' if e.get('parameters') not in (None, '', 'None', '{}') else 'N',
                                      inputs='S' if has('input_artifact_ids') or has('native_input_hda_ids') else 'N',
                                      outputs='S' if has('output_artifact_ids') else 'N',
                                      status='S' if e.get('status') not in (None, '', 'None') else 'N',
                                      command='S' if e.get('command') else 'N', udt=tool in udt_ids))
                else:
                    steps.append(dict(env=env, software='T' if printed else ('P' if img else 'N'), parameters='T',
                                      inputs='T', outputs='N',
                                      status='S' if str(e.get('exit_code')) not in ('None', '', 'nan') else 'N',
                                      command='T' if e.get('command') else 'N', udt=False))
    s, rr = pd.DataFrame(steps), pd.DataFrame(runs)
    rows = []
    for env in ENVS:
        for code, _ in ELEMENTS:
            col = rr[rr.env == env].analysis if code == 'analysis' else s[s.env == env][code]
            share = col.value_counts(normalize=True) * 100
            for lev, _, _ in LEVELS:
                rows.append(dict(env=env, element=code, level=lev, pct=float(share.get(lev, 0.0)), n=len(col)))
    counts = dict(steps=s.groupby('env').size().to_dict(), runs=rr.groupby('env').size().to_dict(),
                  udt_steps=int(s.udt.sum()))
    return pd.DataFrame(rows), counts


def example_record(r):
    """The matched step of panel d, read from the retained evidence of bix-45-q1."""
    task, gal_id, code_id = EXAMPLE
    d = json.load(open(os.path.join(ROOT, 'BixBench_50', 'analysis', task, 'history_analysis_evidence.json')))
    runs = {x['run_id']: x for x in d['runs']}
    g = [e for e in runs[gal_id]['events'] if 'phykit' in str(e.get('tool') or '').lower()][0]
    c = [e for e in runs[code_id]['events'] if e['event_type'] == 'analysis']
    cmds = ' '.join(str(e.get('command') or '') for e in c)
    tool = g['tool']
    ptxt = (g['parameters'] if isinstance(g['parameters'], str) else json.dumps(g['parameters'])).replace('\\"', '"')
    ids = lambda v: len(v) if isinstance(v, list) else len(re.findall(r"'([^']+)'", str(v)))   # noqa: E731
    rec = dict(tool=tool.split('/repos/')[-1], wrapper_version=tool.rsplit('/', 1)[-1],
               metric=re.findall(r'"selector": "([a-z_]+)"', ptxt)[-1],
               suffix=re.search(r'"filter_suffix": "([^"]+)"', ptxt).group(1),
               mode=re.search(r'"selector": "(zip_archive)"', ptxt).group(1),
               n_in=ids(g['input_artifact_ids']), n_out=ids(g['output_artifact_ids']), state=g['status'],
               exit=g['exit_code'], installed='phykit==2.4.1' in cmds, pinned='phykit==2.0.3' in cmds,
               pythonpath='PYTHONPATH' in cmds and 'phykit203' in cmds,
               code_outputs=sum(ids(e.get('output_artifact_ids')) > 0 for e in c),
               code_exit=sorted({str(e.get('exit_code')) for e in c}))
    assert rec['pinned'] and rec['pythonpath'] and rec['code_outputs'] == 0, 'example record changed'
    rep = int(gal_id[-1])
    out = r[(r.task == task) & (r.cfg == 'GPT-5.6 Sol') & (r.replicate == rep)].set_index('env').ok
    rec['code_ok'], rec['gal_ok'] = bool(out[CODE]), bool(out[GAL])
    return rec


def trade(r):
    """Extended Data: score and median input tokens per model and condition, by benchmark."""
    rows = []
    gen = np.random.default_rng(SEED + 1)
    for (bm, c, env), g in r.dropna(subset=['input_tokens']).groupby(['benchmark', 'cfg', 'env']):
        names, inv = np.unique(g.cluster.values, return_inverse=True)
        wts = gen.multinomial(len(names), np.full(len(names), 1 / len(names)), size=B_MEDIAN)[:, inv]
        acc = (wts @ g.score.values) / wts.sum(1)
        order = np.argsort(g.input_tokens.values)
        cum = np.cumsum(wts[:, order], axis=1)
        med = g.input_tokens.values[order][np.argmax(cum >= cum[:, -1:] / 2, axis=1)]
        rows.append(dict(benchmark=bm, cfg=c, env=env, score=100 * g.score.mean(), s_lo=100 * np.percentile(acc, 2.5),
                         s_hi=100 * np.percentile(acc, 97.5), tokens=g.input_tokens.median(),
                         t_lo=np.percentile(med, 2.5), t_hi=np.percentile(med, 97.5), runs=len(g)))
    return pd.DataFrame(rows)


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


def log_ratio_axis(ax, lo=0.2, hi=12.0, ticks=(0.25, 0.5, 1, 2, 4, 8)):
    ax.set_xscale('log')
    ax.set_xlim(lo, hi)
    ax.set_xticks(list(ticks), [f'{t:g}' for t in ticks])
    ax.minorticks_off()
    style.grid_x(ax)
    ax.axvline(1, color=style.INK2, lw=0.6, zorder=2)


def forest_point(ax, y, est, lo, hi, primary=True, color=style.INK):
    ax.plot([lo, hi], [y, y], color=color, lw=0.8 if primary else 0.6, zorder=3, solid_capstyle='butt')
    ax.plot(est, y, ls='', marker='D' if primary else 'o', ms=2.8 if primary else 2.4,
            mfc=color if primary else 'white', mec=color, mew=0.6, zorder=4)


# ---------------------------------------------------------------- panels: drawing
def draw_a(fig, H, tok, pooled):
    label(fig, 0, 0, 'a', 'Token use, Galaxy relative to custom code', H,
          'Diamonds, typical paired task (geometric mean of task–model ratios; primary);\n'
          'circles, all tokens summed over the same tasks (aggregate)')
    ax = axes_mm(fig, 33.0, 15.0, 42.0, 34.0, H)
    rows, y = [], 0.0
    for bm in BENCH:
        rows.append(('head', bm, y))
        y += 0.95
        for value, lab in TOKEN_KINDS:
            rows.append(('row', (bm, value, lab), y))
            y += 0.95
        y += 0.35
    t = tok.set_index(['benchmark', 'kind'])
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    for kind, key, yy in rows:
        if kind == 'head':
            ax.text(-0.76, yy, BENCH_NAME[key], transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold')
            continue
        bm, value, lab = key
        x = t.loc[(bm, value)]
        forest_point(ax, yy - 0.17, x.ratio, x.lo, x.hi, primary=True)
        forest_point(ax, yy + 0.17, x.total_ratio, x.total_lo, x.total_hi, primary=False, color=style.INK2)
        ax.text(-0.04, yy, lab, transform=tr, ha='right', va='center', fontsize=5)
        ax.text(1.02, yy, f'{x.ratio:.1f}×', transform=tr, ha='left', va='center', fontsize=5,
                fontweight='bold' if value == 'input_tokens' else 'normal')
    log_ratio_axis(ax)
    ax.set_ylim(y - 0.35 + 0.1, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Galaxy / custom code (log scale)', labelpad=1.5)
    # incorrect relative to correct runs of the same task and model
    bx = axes_mm(fig, 33.0, 61.0, 42.0, 5.5, H)
    pp = pooled.set_index('env')
    for i, env in enumerate(ENVS):
        x = pp.loc[env]
        forest_point(bx, i, x.ratio, x.lo, x.hi, color=style.ENV_COLOR[env])
        bx.text(-0.04, i, f'{style.ENV_LABEL[env]} ({int(x.sets)} sets)', transform=blended_transform_factory(
            bx.transAxes, bx.transData), ha='right', va='center', fontsize=5)
        bx.text(1.02, i, f'{x.ratio:.2f}×', transform=blended_transform_factory(bx.transAxes, bx.transData),
                ha='left', va='center', fontsize=5)
    log_ratio_axis(bx)
    bx.set_ylim(1.6, -0.6)
    bx.set_yticks([])
    bx.spines['left'].set_visible(False)
    bx.set_xlabel('Incorrect / correct runs of the same task and model', labelpad=1.5)
    fig.text(4.4 / W, 1 - 56.5 / H, 'No clear input-token difference between correct and incorrect siblings',
             fontsize=5.5, fontweight='bold', va='top')


def draw_b(fig, H, act, rep, never, cached):
    label(fig, 92.0, 0, 'b', 'Where the extra input comes from', H,
          'Left, Galaxy / custom code, typical paired task (all runs); right, the text\nGalaxy returned to the agent, '
          'by what the request was for')
    ax = axes_mm(fig, 120.0, 15.0, 22.0, 34.0, H)
    rows, y = [], 0.0
    for bm in BENCH:
        rows.append(('head', bm, y))
        y += 0.95
        for value, lab in (('actions', 'Actions'), ('tokens_per_action', 'Tokens per action')):
            rows.append(('row', (bm, value, lab), y))
            y += 0.95
        y += 0.35
    t = act.set_index(['benchmark', 'kind'])
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    for kind, key, yy in rows:
        if kind == 'head':
            ax.text(-1.05, yy, BENCH_NAME[key], transform=tr, ha='left', va='center', fontsize=5.5, fontweight='bold')
            continue
        bm, value, lab = key
        x = t.loc[(bm, value)]
        forest_point(ax, yy, x.ratio, x.lo, x.hi)
        ax.text(-0.06, yy, lab, transform=tr, ha='right', va='center', fontsize=5)
        ax.text(1.03, yy, f'{x.ratio:.1f}×', transform=tr, ha='left', va='center', fontsize=5)
    log_ratio_axis(ax, 0.25, 8.0, (0.5, 1, 2, 4))
    ax.set_ylim(y - 0.25, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlabel('Galaxy / custom code', labelpad=1.5)
    # returned characters by request type, per benchmark
    cx = axes_mm(fig, 155.0, 15.0, 24.0, 34.0, H)
    for i, bm in enumerate(BENCH):
        d = rep[rep.benchmark == bm].set_index('operation')
        bottom = 0.0
        for (name, _), col in zip(OPS, OP_COLOR):
            v = d.loc[name, 'char_pct']
            cx.bar(i, v, bottom=bottom, width=0.72, color=col, ec='white', lw=0.3, zorder=3)
            if v >= 9:
                cx.text(i, bottom + v / 2, f'{v:.0f}', ha='center', va='center', fontsize=5,
                        color='white' if col in (style.GALAXY, style.NEUTRAL_DARK, '#8a8a8a') else style.INK)
            bottom += v
    cx.set_xticks(range(3), ['BixB.', 'CompBio', 'IWC'], fontsize=5, rotation=0)
    cx.tick_params(axis='x', length=0, pad=1.5)
    cx.set_ylim(0, 100)
    cx.set_yticks([0, 50, 100])
    cx.set_ylabel('Returned characters (%)', labelpad=1.0)
    cx.legend(handles=[Patch(fc=c, ec=style.NEUTRAL_MID if c == '#e3e3e3' else c, lw=0.3, label=n)
                       for (n, _), c in zip(OPS, OP_COLOR)], loc='upper left', bbox_to_anchor=(-2.42, -0.21), ncol=2,
              fontsize=5, handlelength=0.9, handletextpad=0.3, columnspacing=0.8, labelspacing=0.2, borderaxespad=0)
    nv = never.percent
    rng_txt = lambda s_: (f'{s_.min():.0f}%' if round(s_.min()) == round(s_.max())   # noqa: E731
                          else f'{s_.min():.0f}–{s_.max():.0f}%')
    fig.text(96.4 / W, 1 - 66.0 / H,
             f'Tools inspected but not executed in the same run: {rng_txt(nv)} by benchmark.\n'
             f'Median share of input that was cached (earlier context reread): Galaxy '
             f'{rng_txt(cached.xs(GAL, level="env"))}, custom code {rng_txt(cached.xs(CODE, level="env"))}.',
             fontsize=5, color=style.INK2, va='top', linespacing=1.25)


def draw_c(fig, H, y0, ev, counts):
    label(fig, 0, y0, 'c', 'What the retained record holds for each analysis step', H,
          f'{counts["steps"][CODE]:,} custom-code steps (shell commands labelled analysis) and '
          f'{counts["steps"][GAL]:,} Galaxy jobs;\nwhole analysis per run ({counts["runs"][GAL]:,} runs per condition)')
    ax = axes_mm(fig, 40.0, y0 + 12.0, 46.0, 46.0, H)
    ypos, y = [], 0.0
    for k, (code, name) in enumerate(ELEMENTS):
        for env in ENVS:
            ypos.append((code, env, y))
            y += 0.78
        y += 0.5
    tr = blended_transform_factory(ax.transAxes, ax.transData)
    for code, env, yy in ypos:
        d = ev[(ev.env == env) & (ev.element == code)].set_index('level').pct
        left = 0.0
        for lev, _, col in LEVELS:
            v = d.get(lev, 0.0)
            if v <= 0:
                continue
            ax.barh(yy, v, left=left, height=0.62, color=col, ec=style.NEUTRAL_MID if lev == 'N' else 'white',
                    lw=0.4, hatch='/////' if lev == 'N' else None, zorder=3)
            if v >= 12:
                ax.text(left + v / 2, yy, f'{v:.0f}', ha='center', va='center', fontsize=5, zorder=4,
                        color='white' if lev == 'S' else style.INK,
                        bbox=dict(boxstyle='square,pad=0.1', fc='white', ec='none') if lev == 'N' else None)
            left += v
        ax.text(-0.02, yy, style.ENV_LABEL[env], transform=tr, ha='right', va='center', fontsize=5)
    for code, name in ELEMENTS:
        ys = [yy for c, _, yy in ypos if c == code]
        ax.text(-13.0 / 46.0, np.mean(ys), name, transform=tr, ha='right', va='center', fontsize=5.5,
                fontweight='bold')
    ax.set_ylim(y - 0.5 + 0.1, -0.6)
    ax.set_yticks([])
    ax.spines['left'].set_visible(False)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Steps (or runs) (%)', labelpad=1.5)
    ax.legend(handles=[Patch(fc=col, ec=style.NEUTRAL_MID, lw=0.4, hatch='/////' if lev == 'N' else None, label=lab)
                       for lev, lab, col in LEVELS], loc='upper left', bbox_to_anchor=(-0.78, -0.12), ncol=2,
              fontsize=5, handlelength=1.1, handletextpad=0.3, columnspacing=0.8, labelspacing=0.25, borderaxespad=0)


def draw_d(fig, H, y0, rec):
    label(fig, 92.0, y0, 'd', 'One analysis step, recorded both ways', H,
          f'{EXAMPLE[0]}, PhyKIT relative composition variability; GPT-5.6 Sol, replicate 1 (the case in Fig. 2d)')
    x0, w, top, hgt = 96.0, 84.0, y0 + 11.5, 54.0
    ax = axes_mm(fig, x0, top, w, hgt, H)
    ax.set_axis_off()
    ax.set_xlim(0, w)
    ax.set_ylim(hgt, 0)
    c1, c2, cw = 18.5, 51.5, 32.0
    ax.text(c1, 1.2, 'Custom code: retained trace', fontsize=5.5, fontweight='bold', va='top')
    ax.text(c2, 1.2, 'Galaxy: job record', fontsize=5.5, fontweight='bold', va='top')
    rows = [
        ('Software and\nversion', f'PhyKIT 2.4.1 installed, then 2.0.3\ndownloaded and loaded through\n'
                                  f'PYTHONPATH (in command text only)',
         f'{rec["tool"].split("/")[1]} wrapper {rec["wrapper_version"]}\n(Tool Shed ID); library version\n'
         f'not in the job record'),
        ('Parameters', 'In the Python code of the command\n(file suffix, rounding)',
         f'Fields: metric = {rec["metric"].replace("composition_", "composition_" + chr(10))};\n'
         f'mode = {rec["mode"]}; suffix = {rec["suffix"]}'),
        ('Inputs and\noutputs', 'Input archives named in the\ncommand; output files not retained',
         f'{rec["n_in"]} input and {rec["n_out"]} output datasets,\nlinked by ID in the history'),
        ('Status', f'Exit code {", ".join(rec["code_exit"])} for every command', f'Job state "{rec["state"]}", exit code '
                                                                                f'{rec["exit"]}'),
        ('Answer', 'Accepted' if rec['code_ok'] else 'Rejected', ('Accepted' if rec['gal_ok'] else 'Rejected') +
         ': the reference encodes the\nolder PhyKIT value'),
    ]
    y = 6.2
    for name, a, b in rows:
        n = max(a.count('\n'), b.count('\n'), name.count('\n')) + 1
        ax.text(0.5, y, name, fontsize=5, fontweight='bold', va='top', linespacing=1.2)
        ax.text(c1, y, a, fontsize=5, va='top', linespacing=1.2)
        ax.text(c2, y, b, fontsize=5, va='top', linespacing=1.2)
        y += n * 2.25 + 2.0
        ax.plot([0.5, w], [y - 1.1, y - 1.1], color=style.GRID, lw=0.4)
    ax.add_patch(Rectangle((c1 - 1.0, 0), cw, y - 1.1, fc=style.ENV_TINT[CODE], ec='none', zorder=0))
    ax.add_patch(Rectangle((c2 - 1.0, 0), cw, y - 1.1, fc=style.ENV_TINT[GAL], ec='none', zorder=0))
    ax.text(0.5, y + 1.0, 'The Galaxy record keeps fields a reviewer can query; the custom-code trace keeps the code,\n'
            'so the same facts must be read from it. Neither record was rerun to test reproducibility.',
            fontsize=5, color=style.INK2, va='top', linespacing=1.25)


# ---------------------------------------------------------------- Extended Data
def ed_trade(fig, H, tt):
    label(fig, 0, 0, 'a', 'Score and input tokens per model and condition', H,
          'Points, mean score (IWC, output agreement) and median input tokens per run, with 95% intervals')
    for j, bm in enumerate(BENCH):
        ax = axes_mm(fig, 12.0 + j * 57.0, 13.0, 48.0, 32.0, H)
        d = tt[tt.benchmark == bm]
        for t in d.itertuples():
            ax.plot([t.t_lo / 1e6, t.t_hi / 1e6], [t.score, t.score], color=MODEL_COLOR[t.cfg], lw=0.6, zorder=2)
            ax.plot([t.tokens / 1e6] * 2, [t.s_lo, t.s_hi], color=MODEL_COLOR[t.cfg], lw=0.6, zorder=2)
            ax.plot(t.tokens / 1e6, t.score, ls='', marker=style.ENV_MARKER[t.env], ms=3.4, mfc=MODEL_COLOR[t.cfg],
                    mec=style.INK, mew=0.35, zorder=3)
        ax.set_xscale('log')
        ax.set_xlim(0.1, 40)
        ax.set_xticks([0.1, 1, 10], ['0.1', '1', '10'])
        ax.minorticks_off()
        ax.set_ylim(60, 101)
        style.grid_y(ax)
        ax.set_xlabel('Median input tokens per run (millions)')
        if j == 0:
            ax.set_ylabel('Score (%)')
        ax.set_title(BENCH_NAME[bm] + (' (agreement × 100)' if bm == 'IWC' else ''), fontsize=5.5, fontweight='bold',
                     loc='left', pad=3)
    hand = [Line2D([], [], ls='', marker='o', ms=3.2, mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35, label=c) for c in CFG]
    hand += [Line2D([], [], ls='', marker=style.ENV_MARKER[e], ms=3.2, mfc=style.NEUTRAL_MID, mec=style.INK, mew=0.35,
                    label=style.ENV_LABEL[e]) for e in ENVS]
    fig.legend(handles=hand, ncol=6, loc='upper right', bbox_to_anchor=(1.0, 1 - 0.6 / H), fontsize=5,
               handletextpad=0.2, columnspacing=0.8, borderaxespad=0, frameon=False)


def box(ax, x, values, color, tint, solid, width=0.34):
    """Box (middle 50%, median), whiskers to 1.5 x IQR, and every run as a dot."""
    v = np.asarray(values, float)
    v = v[np.isfinite(v) & (v > 0)]
    lv = np.log10(v)
    q1, med, q3 = np.percentile(lv, [25, 50, 75])
    lo_w, hi_w = lv[lv >= q1 - 1.5 * (q3 - q1)].min(), lv[lv <= q3 + 1.5 * (q3 - q1)].max()
    ax.scatter(x + rng.uniform(-width * 0.38, width * 0.38, len(v)), v, s=0.6, color=style.INK, alpha=0.22, lw=0,
               zorder=2, rasterized=True)
    ax.add_patch(plt.Rectangle((x - width / 2, 10 ** q1), width, 10 ** q3 - 10 ** q1, fc=color if solid else tint,
                               ec=color, lw=0.6, alpha=0.85, zorder=3))
    ax.plot([x - width / 2, x + width / 2], [10 ** med] * 2, color='white' if solid else style.INK, lw=0.9, zorder=4,
            solid_capstyle='butt')
    for a_, b_ in ((10 ** lo_w, 10 ** q1), (10 ** q3, 10 ** hi_w)):
        ax.plot([x, x], [a_, b_], color=color, lw=0.6, zorder=3)


def ed_siblings(fig, H, y0, r, per):
    label(fig, 0, y0, 'b', 'Input tokens of correct (light) and incorrect (solid) runs', H)
    for j, env in enumerate(ENVS):
        ax = axes_mm(fig, 12.0 + j * 46.0, y0 + 9.0, 42.0, 28.0, H)
        ax.set_yscale('log')
        ax.set_ylim(0.01, 1000)
        ax.set_yticks([0.01, 0.1, 1, 10, 100], ['0.01', '0.1', '1', '10', '100'] if j == 0 else [''] * 5)
        ax.minorticks_off()
        style.grid_y(ax)
        if j == 0:
            ax.set_ylabel('Input tokens per run (millions)')
        for i, c in enumerate(CFG):
            d = r[(r.cfg == c) & (r.env == env)]
            box(ax, i - 0.21, d[d.ok].input_tokens / 1e6, style.ENV_COLOR[env], style.ENV_TINT[env], solid=False)
            box(ax, i + 0.21, d[~d.ok].input_tokens / 1e6, style.ENV_COLOR[env], style.ENV_TINT[env], solid=True)
            t = per[(per.env == env) & (per.cfg == c)].iloc[0]
            ax.text(i, 400, f'{t.ratio:.2f}×', ha='center', va='center', fontsize=5, color=style.INK2)
        ax.set_xticks(range(len(CFG)), [TICK[c] for c in CFG], fontsize=5)
        ax.tick_params(axis='x', length=0, pad=2)
        ax.set_xlim(-0.6, len(CFG) - 0.4)
        ax.set_title(style.ENV_LABEL[env], fontsize=5.5, fontweight='bold', loc='left', pad=3)


def ed_actions(fig, H, y0, r):
    label(fig, 96.0, y0, 'c', 'Input tokens against actions (all runs)', H)
    ax = axes_mm(fig, 108.0, y0 + 9.0, 70.0, 28.0, H)
    d = r.dropna(subset=['input_tokens', 'actions'])
    d = d[d.actions > 0]
    for env in ENVS:
        e = d[d.env == env]
        ax.scatter(e.actions, e.input_tokens / 1e6, s=1.0, marker=style.ENV_MARKER[env], color=style.ENV_COLOR[env],
                   alpha=0.25, lw=0, zorder=2, rasterized=True, label=style.ENV_LABEL[env])
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1, 2000)
    ax.set_ylim(0.005, 300)
    ax.set_xticks([1, 10, 100, 1000], ['1', '10', '100', '1,000'])
    ax.set_yticks([0.01, 0.1, 1, 10, 100], ['0.01', '0.1', '1', '10', '100'])
    ax.minorticks_off()
    style.grid_y(ax)
    style.grid_x(ax)
    ax.set_xlabel('Actions per run')
    ax.set_ylabel('Input tokens (millions)')
    ax.legend(markerscale=4, loc='upper left', fontsize=5, borderaxespad=0.3)


# ---------------------------------------------------------------- source data and assembly
def source_data(tok, pooled, per, act, act_ok, rep, never, cached, ev, counts, rec):
    rows = []
    for t in tok.itertuples():
        rows.append(dict(panel='a', benchmark=t.benchmark, condition='galaxy / custom_code', group=t.label,
                         measure='geometric_mean_paired_cell_ratio (primary)', value=t.ratio, ci95_low=t.lo,
                         ci95_high=t.hi, n=t.cells, p=t.p, p_holm=t.p_holm))
        rows.append(dict(panel='a', benchmark=t.benchmark, condition='galaxy / custom_code', group=t.label,
                         measure='ratio_of_totals_same_cells (aggregate)', value=t.total_ratio, ci95_low=t.total_lo,
                         ci95_high=t.total_hi, n=t.cells))
    for t in pooled.itertuples():
        rows.append(dict(panel='a', benchmark='all', condition=t.env, group='all four models',
                         measure='input_tokens_ratio_incorrect_over_correct', value=t.ratio, ci95_low=t.lo,
                         ci95_high=t.hi, n=t.sets, p=t.p, p_holm=t.p_holm))
    for t in per.itertuples():
        rows.append(dict(panel='a (ED b)', benchmark='all', condition=t.env, group=t.cfg,
                         measure='input_tokens_ratio_incorrect_over_correct', value=t.ratio, ci95_low=t.lo,
                         ci95_high=t.hi, n=t.sets, p=t.p, p_holm=t.p_holm))
    for frame, scope in ((act, 'all runs'), (act_ok, 'correct runs (sensitivity)')):
        for t in frame.itertuples():
            rows.append(dict(panel='b', benchmark=t.benchmark, condition='galaxy / custom_code', group=scope,
                             measure=f'{t.kind}_ratio (geometric mean of paired cells)', value=t.ratio,
                             ci95_low=t.lo, ci95_high=t.hi, n=t.cells, p=t.p, p_holm=t.p_holm))
    for t in rep.itertuples():
        rows.append(dict(panel='b', benchmark=t.benchmark, condition='galaxy', group=t.operation,
                         measure='pct_returned_characters', value=t.char_pct, n=t.chars))
    for bm, t in never.iterrows():
        rows.append(dict(panel='b', benchmark=bm, condition='galaxy', group='inspected tools',
                         measure='pct_inspected_but_not_executed_in_run', value=t.percent, n=int(t.denominator)))
    for (bm, env), v in cached.items():
        rows.append(dict(panel='b', benchmark=bm, condition=env, group='runs', measure='median_cached_share_of_input_pct',
                         value=v))
    for t in ev.itertuples():
        rows.append(dict(panel='c', benchmark='all', condition=t.env, group=t.element,
                         measure=f'pct_{"runs" if t.element == "analysis" else "steps"}: '
                                 f'{dict((l, n) for l, n, _ in LEVELS)[t.level]}', value=t.pct, n=t.n))
    for k, v in rec.items():
        rows.append(dict(panel='d', benchmark='BixBench50', condition='both', group=EXAMPLE[0], measure=k, value=str(v)))
    cols = ['panel', 'benchmark', 'condition', 'group', 'measure', 'value', 'ci95_low', 'ci95_high', 'n', 'p', 'p_holm']
    out = pd.DataFrame(rows).reindex(columns=cols)
    out['condition'] = out.condition.str.replace('open_ended_code', 'custom_code')
    out.to_csv(os.path.join(OUT, 'fig5_source_data.csv'), index=False, float_format='%.4f')


def ed_source_data(tt):
    out = tt.rename(columns={'cfg': 'model', 'env': 'condition'})
    out['condition'] = out.condition.str.replace('open_ended_code', 'custom_code')
    out.round(4).to_csv(os.path.join(OUT, 'ed_fig5_source_data.csv'), index=False)


def save(fig, name, title):
    style.enforce_min_font(fig)
    fig.savefig(os.path.join(OUT, f'{name}.svg'), metadata={'Title': title}, dpi=600)
    fig.savefig(os.path.join(OUT, f'{name}.pdf'), metadata={'Title': title}, dpi=600)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, f'{name}.png'), dpi=(600, 600))
    plt.close(fig)


def main():
    global rng
    r = load_runs()
    calls = load_calls()
    per, pooled = outcome_ratios(r)                 # first, as in the approved build
    rng = np.random.default_rng(SEED + 1)
    tok = benchmark_ratios(r, TOKEN_KINDS)
    act = benchmark_ratios(r, [('actions', 'Actions'), ('tokens_per_action', 'Tokens per action')])
    act_ok = benchmark_ratios(r[r.ok], [('actions', 'Actions'), ('tokens_per_action', 'Tokens per action')])
    rep, never, cached = replies(calls, r)
    ev, counts = evidence(calls)
    rec = example_record(r)
    tt = trade(r)
    for name, t in (('a: token ratios', tok), ('a: siblings pooled', pooled), ('b: actions', act),
                    ('b: actions, correct runs', act_ok), ('b: replies', rep), ('c: evidence', ev)):
        print(name)
        print(t.round(3).to_string())
    print('never', never.percent.to_dict(), '| cached', cached.round(1).to_dict(), '| counts', counts, '| rec', rec)

    H = 150.0
    rng = np.random.default_rng(SEED + 5)           # box jitter only
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, tok, pooled)
    draw_b(fig, H, act, rep, never, cached)
    draw_c(fig, H, 78.0, ev, counts)
    draw_d(fig, H, 78.0, rec)
    save(fig, 'fig5', 'Fig. 5 | Galaxy records analyses as structured provenance and uses more input tokens on '
                      'question-answering tasks')
    source_data(tok, pooled, per, act, act_ok, rep, never, cached, ev, counts, rec)

    He = 100.0
    fig = plt.figure(figsize=(W * MM, He * MM))
    ed_trade(fig, He, tt)
    ed_siblings(fig, He, 56.0, r, per)
    ed_actions(fig, He, 56.0, r)
    save(fig, 'ed_fig5', 'Extended Data Fig. 5 | Token use by model, outcome and action count')
    ed_source_data(tt)


if __name__ == '__main__':
    main()
