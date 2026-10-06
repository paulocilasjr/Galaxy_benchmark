"""Fig. 5: Galaxy increases analysis inspectability at higher token cost.

The panels answer the questions of Results section 4 of the outline:
a, how many more input tokens does Galaxy use, and is token use related to model capability (accuracy against median
   input tokens per run, one point per replicate, model and condition);
b, does Galaxy use more tokens because of failed attempts (incorrect runs use no more tokens than correct runs of the
   same task);
c, or because of something else (input tokens against actions per correct run);
d, what fills the Galaxy context (interface requests and returned text by what they were for);
The record the extra tokens buy (tool, version, parameters and linked outputs of every Galaxy job) is described in the
text; its counts are written to the source data as panel 'text'.

Input tokens include cached context. Actions are tool calls by the agent (shell commands, Galaxy interface calls, web
searches or fetches, file reads, writes and edits), as in On-demand Fig. 6. A run is correct when accepted or, for IWC,
at >= 0.99 output agreement (as in Figs 2b and 3). Ratios are geometric means over paired cells, with 95% percentile
cluster-bootstrap intervals (clusters are BixBench source capsules, otherwise tasks) and paired cluster sign-flip
randomization tests (200,000 draws), Holm-adjusted per panel.
Writes figures/fig5.{svg,pdf,png}, figures/fig5_source_data.csv and prints the statistics.
"""
import glob
import io
import json
import os
import re
import sys

import numpy as np
import openpyxl
import pandas as pd

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
ACTIONS = os.path.join(ROOT, 'manuscript_material', 'on_demand', 'Source_Data_OD_Fig6.xlsx')
OUT = os.path.join(ROOT, 'figures')
B, SEED, B_PERM, B_MEDIAN = 20000, 20261002, 200000, 2000
W, MM = 180.0, 1 / 25.4
CFG = style.CONFIGS
ENVS = style.ENVS                                    # custom code first, always
CODE, GAL = ENVS
BIN = ['BixBench50', 'CompBio']                      # binary endpoints, as in Fig. 2a
TICK = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6\nSol', 'GPT-5.6 Luna': 'GPT-5.6\nLuna',
        'DeepSeek V4 Pro': 'DeepSeek\nV4 Pro'}
# Model identity (Paul Tol muted green, purple, sand and indigo). Every pair differs by >= 25 (OKLab x 100) in normal
# vision and >= 13 under simulated deuteranopia, protanopia and tritanopia (Machado et al. 2009); the earlier olive and
# wine fell to 13.4 (purple-wine) and 9.0 (green-wine, deuteranopia). Figs 2 and 3 still use olive and wine.
MODEL_COLOR = dict(zip(CFG, ['#117733', '#AA4499', '#DDCC77', '#332288']))
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
KEY = ['benchmark', 'task', 'cfg', 'env', 'replicate']
TRACE_MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
               'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
               'codex_deepseek_v4_pro': 'DeepSeek V4 Pro'}
# Galaxy interface operations, grouped; discovery is highlighted because it is the largest avoidable cost.
OPS = [('Finding tools (search, read tool descriptions)', ('search_galaxy_tools', 'inspect_galaxy_tool')),
       ('Running installed tools', ('run_galaxy_tool_and_wait',)),
       ('Running agent-written code (UDTs)', ('run_galaxy_udt_and_wait',)),
       ('Reading results (history, datasets)', ('inspect_galaxy_history', 'peek_galaxy_dataset',
                                                 'inspect_archive_inventory')),
       ('Waiting for jobs, uploading files', ('wait_for_galaxy_jobs', 'stage_workspace_file'))]
OP_COLOR = [style.GALAXY, style.NEUTRAL_DARK, '#8a8a8a', '#bdbdbd', '#e3e3e3']
# Text (no panel): what each analysis step leaves for inspection. Galaxy steps are Galaxy jobs; custom-code steps are the
# agent's shell commands that the run-level evidence labels as analysis.
EVIDENCE = [os.path.join(ROOT, b, 'analysis', '*', 'history_analysis_evidence.json') for b in ('BixBench_50', 'CompBio', 'IWC')]
NOT_PRIMARY = {'deepseek_v4_pro_via_claude_code_superseded', 'codex_gpt_6_astra'}
INSPECT = [('command', 'Command recorded'), ('tool_version', 'Tool and version identified'),
           ('params', 'Parameters stored as fields'), ('outputs', 'Outputs kept and linked to the step'),
           ('history', 'Browsable history to rerun without an agent')]
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- data
def load_runs():
    r = pd.read_csv(os.path.join(AN, 'accuracy_primary_runs.csv'))
    r['cluster'] = r.benchmark + ':' + r.cluster.astype(str)
    r['ok'] = r.score >= r.benchmark.map(CORRECT_AT) - 1e-9
    t = pd.read_csv(os.path.join(AN, 'token_run_observations.csv'))
    t = t[t.model_primary]
    r = r.merge(t[KEY + ['input_tokens', 'cached']], on=KEY, how='left')
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
                    usecols=['benchmark', 'task', 'model', 'replicate', 'tool', 'galaxy_server', 'chars_returned'])
    return c[c.model.isin(TRACE_MODEL) & c.galaxy_server].assign(cfg=lambda x: x.model.map(TRACE_MODEL))


# ---------------------------------------------------------------- statistics
def holm(p):
    p = np.asarray(p, float)
    order, adj, run = np.argsort(p), np.empty(len(p)), 0.0
    for i, k in enumerate(order):
        run = max(run, (len(p) - i) * p[k])
        adj[k] = min(1.0, run)
    return adj


def paired_ratio(cells):
    """cells: benchmark, cluster and d = log ratio per paired cell -> geometric-mean ratio, 95% CI, sign-flip P, n."""
    est = np.exp(cells.d.mean())
    num, den = 0.0, 0.0
    for _, g in cells.groupby('benchmark'):
        per = g.groupby('cluster').d.agg(['sum', 'count'])
        w = rng.multinomial(len(per), np.full(len(per), 1 / len(per)), size=B)
        num, den = num + w @ per['sum'].values, den + w @ per['count'].values
    lo, hi = np.exp(np.percentile(num / den, [2.5, 97.5]))
    d = cells.groupby('cluster').d.sum().values
    hits = 0
    for _ in range(B_PERM // 20000):
        null = rng.choice([-1.0, 1.0], size=(20000, len(d))) @ d
        hits += np.sum(np.abs(null) >= abs(d.sum()) - 1e-12)
    return est, lo, hi, (1 + hits) / (B_PERM + 1), len(cells)


def paired_cells(r, value):
    cell = r.dropna(subset=[value]).groupby(['benchmark', 'cluster', 'task', 'cfg', 'env'])[value].median()
    cell = cell.unstack('env').dropna()
    cell = cell[(cell[GAL] > 0) & (cell[CODE] > 0)]
    return cell.assign(d=np.log(cell[GAL] / cell[CODE])).reset_index()


def condition_ratios(r, value):
    """Galaxy / custom code per task x model cell (medians over runs), per model and pooled over models."""
    cell = paired_cells(r, value)
    rows = []
    for c in CFG + ['all four']:
        est, lo, hi, p, n = paired_ratio(cell if c == 'all four' else cell[cell.cfg == c])
        rows.append(dict(cfg=c, ratio=est, lo=lo, hi=hi, p=p, cells=n))
    out = pd.DataFrame(rows)
    out['p_holm'] = np.r_[holm(out.p[:len(CFG)]), out.p.iloc[-1]]
    return out


def outcome_ratios(r):
    """Incorrect / correct input tokens within replicate sets that have both, per condition and model."""
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


def trade(r):
    """Accuracy (mean, cluster-bootstrap CI) and median input tokens (cluster-bootstrap CI) per model and condition,
    BixBench-Verified-50 and CompBioBench runs pooled."""
    d = r[r.benchmark.isin(BIN)].dropna(subset=['input_tokens'])
    rows = []
    pooled_rng = np.random.default_rng(SEED + 1)    # separate stream, so the other panels' draws are unchanged
    groups = [(k, g, rng) for k, g in d.groupby(['cfg', 'env'])] + \
             [(('all four', env), d[d.env == env], pooled_rng) for env in ENVS]
    for (c, env), g, gen in groups:
        clusters = g.cluster.values
        acc_draw, med_draw = np.zeros(B_MEDIAN), np.zeros(B_MEDIAN)
        # one weight per run from cluster multiplicities, resampled within benchmark
        wts = np.zeros((B_MEDIAN, len(g)))
        for bm in g.benchmark.unique():
            sel = g.benchmark.values == bm
            names, inv = np.unique(clusters[sel], return_inverse=True)
            draw = gen.multinomial(len(names), np.full(len(names), 1 / len(names)), size=B_MEDIAN)
            wts[:, sel] = draw[:, inv]
        acc_draw = (wts @ g.score.values) / wts.sum(1)
        order = np.argsort(g.input_tokens.values)
        cum = np.cumsum(wts[:, order], axis=1)
        med_draw = g.input_tokens.values[order][np.argmax(cum >= cum[:, -1:] / 2, axis=1)]
        rows.append(dict(cfg=c, env=env, accuracy=100 * g.score.mean(),
                         acc_lo=100 * np.percentile(acc_draw, 2.5), acc_hi=100 * np.percentile(acc_draw, 97.5),
                         tokens=g.input_tokens.median(), tok_lo=np.percentile(med_draw, 2.5),
                         tok_hi=np.percentile(med_draw, 97.5), runs=len(g)))
    return pd.DataFrame(rows), condition_ratios(d, 'input_tokens')


def replicate_points(r):
    """Accuracy and median input tokens of each replicate (one run per task) per model and condition: the points of
    panel a. Same runs as trade(): BixBench-Verified-50 and CompBioBench runs with a token count."""
    d = r[r.benchmark.isin(BIN)].dropna(subset=['input_tokens'])
    rep = d.groupby(['cfg', 'env', 'replicate']).agg(accuracy=('score', 'mean'), tokens=('input_tokens', 'median'),
                                                     runs=('score', 'size')).reset_index()
    rep['accuracy'] *= 100
    return rep


def interaction(r):
    ok = r[r.ok].dropna(subset=['input_tokens', 'actions'])
    ok = ok[ok.actions > 0]
    fits, rho = {}, {}
    for env in ENVS:
        e = ok[ok.env == env]
        x, y = np.log10(e.actions.values), np.log10(e.input_tokens.values)
        fits[env] = np.polyfit(x, y, 1)
        rho[env] = pd.Series(x).rank().corr(pd.Series(y).rank())
    return ok, fits, rho, condition_ratios(r[r.ok], 'actions'), condition_ratios(r[r.ok], 'tokens_per_action')


def context(calls, r):
    rows = []
    total_calls, total_chars = len(calls), calls.chars_returned.sum()
    for name, tools in OPS:
        s = calls[calls.tool.isin(tools)]
        rows.append(dict(operation=name, calls=len(s), call_pct=100 * len(s) / total_calls,
                         chars=int(s.chars_returned.sum()), char_pct=100 * s.chars_returned.sum() / total_chars))
    fr = pd.read_csv(os.path.join(AN, 'token_interface_friction.csv'))
    never = fr[fr.measure == 'Inspected tools never run in the same run'][['benchmark', 'percent', 'count',
                                                                          'denominator']]
    cached = (r.dropna(subset=['input_tokens']).assign(share=lambda x: x.cached / x.input_tokens)
              .groupby('env').share.median() * 100)
    return pd.DataFrame(rows), never, cached


def _ids(v):
    if isinstance(v, list):
        return len(v)
    return len(re.findall(r"'([^']+)'", v)) if isinstance(v, str) else 0


def inspectability():
    """Share of analysis steps (and of runs, for the history) carrying each element of an inspectable record."""
    steps, runs = [], []
    for path in sorted(p for pattern in EVIDENCE for p in glob.glob(pattern)):
        for run in json.load(open(path))['runs']:
            model = re.sub(r'_r\d+$', '', re.sub(r'^(galaxy|open_ended_code)_', '', run['run_id']))
            if model in NOT_PRIMARY:
                continue
            env = GAL if run['condition'] == 'galaxy' else CODE
            runs.append(dict(env=env, history=run['evidence_completeness'].get('public_history_contents') == 'retrieved'))
            for e in run['events']:
                galaxy_step = env == GAL and e['execution_location'] == 'galaxy_job'
                code_step = env == CODE and e['execution_location'] == 'agent_runtime' and e.get('event_type') == 'analysis'
                if not (galaxy_step or code_step):
                    continue
                tool = str(e.get('tool') or '')
                # Tool Shed identifiers end in the tool version; built-in tools take the recorded Galaxy release (26.1)
                versioned = galaxy_step and (e.get('tool_version') not in (None, '', 'None') or
                                             tool.startswith('toolshed') and len(tool.split('/')) >= 6 or
                                             not tool.startswith('toolshed'))
                steps.append(dict(env=env, command=bool(e.get('command')), tool_version=bool(versioned),
                                  params=galaxy_step and e.get('parameters') not in (None, '', 'None', '{}'),
                                  outputs=galaxy_step and _ids(e.get('output_artifact_ids')) > 0))
    s, r = pd.DataFrame(steps), pd.DataFrame(runs)
    tab = s.groupby('env')[['command', 'tool_version', 'params', 'outputs']].mean() * 100
    tab['history'] = r.groupby('env').history.mean() * 100
    counts = dict(steps=s.groupby('env').size().to_dict(), runs=r.groupby('env').size().to_dict(),
                  histories=int(r[r.env == GAL].history.sum()))
    return tab.reindex(ENVS), counts


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


def box(ax, x, values, color, tint, solid, width=0.34, dots=True):
    """Box (middle 50%, median), whiskers to 1.5 x IQR, and every run as a dot."""
    v = np.asarray(values, float)
    v = v[np.isfinite(v) & (v > 0)]
    lv = np.log10(v)
    q1, med, q3 = np.percentile(lv, [25, 50, 75])
    lo_w, hi_w = lv[lv >= q1 - 1.5 * (q3 - q1)].min(), lv[lv <= q3 + 1.5 * (q3 - q1)].max()
    if dots:
        ax.scatter(x + rng.uniform(-width * 0.38, width * 0.38, len(v)), v, s=0.6, color=style.INK, alpha=0.22,
                   lw=0, zorder=2, rasterized=True)
    ax.add_patch(plt.Rectangle((x - width / 2, 10 ** q1), width, 10 ** q3 - 10 ** q1, fc=color if solid else tint,
                               ec=color, lw=0.6, alpha=0.85, zorder=3))
    ax.plot([x - width / 2, x + width / 2], [10 ** med] * 2, color='white' if solid else style.INK, lw=0.9, zorder=4,
            solid_capstyle='butt')
    for a_, b_ in ((10 ** lo_w, 10 ** q1), (10 ** q3, 10 ** hi_w)):
        ax.plot([x, x], [a_, b_], color=color, lw=0.6, zorder=3)
    for cap in (10 ** lo_w, 10 ** hi_w):
        ax.plot([x - width / 5, x + width / 5], [cap, cap], color=color, lw=0.6, zorder=3)


def ratio_label(ax, x, y_top, ratio, p):
    bold = p < 0.05
    tr = blended_transform_factory(ax.transData, ax.transAxes)
    col = style.INK if bold else style.INK2
    ax.text(x, y_top, f'{ratio:.2f}×', ha='center', va='bottom', fontsize=5, color=col,
            fontweight='bold' if bold else 'normal', transform=tr)
    ax.text(x, y_top - 0.045, fmt_p(p), ha='center', va='bottom', fontsize=5, color=col, transform=tr)


def log_axis(ax, lo, hi, ticks, labels, ylabel):
    ax.set_yscale('log')
    ax.set_ylim(lo, hi)
    ax.set_yticks(ticks, labels)
    ax.minorticks_off()
    style.grid_y(ax)
    ax.set_ylabel(ylabel)


def env_handles(ms=3.4):
    return [Line2D([], [], marker=style.ENV_MARKER[e], ls='', ms=ms, mfc=style.ENV_COLOR[e], mec='white', mew=0.4,
                   label=style.ENV_LABEL[e]) for e in ENVS]


# ---------------------------------------------------------------- panels
def point_style(c, env):
    """Colour gives the model and shape the condition (square, custom code; circle, Galaxy). Markers are filled,
    with a thin dark outline that keeps the pale sand visible on white."""
    return dict(marker=style.ENV_MARKER[env], mfc=MODEL_COLOR[c], mec=style.INK, mew=0.35)


def draw_a(fig, H, reps, ratios, uncached=None):
    label(fig, 0, 0, 'a', 'The trade: same accuracy, more input tokens', H,
          'BixBench-Verified-50 and CompBioBench; each point is one replicate (one run per task)\n'
          'Numbers: times more input tokens in Galaxy on the same task')
    ax = axes_mm(fig, 11.0, 15.0, 36.0, 37.0, H)
    for c in CFG:
        for env in ENVS:
            t = reps[(reps.cfg == c) & (reps.env == env)]
            ax.plot(t.accuracy, t.tokens / 1e6, ls='', ms=3.6, zorder=3, **point_style(c, env))
    ax.set_yscale('log')
    ax.set_ylim(0.25, 15)
    ax.set_yticks([0.3, 1, 3, 10], ['0.3', '1', '3', '10'])
    ax.minorticks_off()
    ax.set_xlim(78, 94)
    ax.set_xticks([80, 85, 90])
    style.grid_x(ax)
    style.grid_y(ax)
    ax.set_xlabel('Accuracy of the replicate (%)')
    ax.set_ylabel('Median input tokens per run (millions)')
    # key, in mm: conditions by marker, then models by colour with the Galaxy token ratio on the same task
    key = axes_mm(fig, 50.0, 15.0, 25.0, 37.0, H)
    key.set_axis_off()
    key.set_xlim(0, 25.0)
    key.set_ylim(37.0, 0)
    for k, env in enumerate(ENVS):
        y = 1.0 + k * 3.0
        key.plot(0.9, y, ls='', ms=3.6, **dict(point_style(CFG[0], env), mfc=style.NEUTRAL_MID))
        key.text(2.6, y, style.ENV_LABEL[env], va='center', ha='left', fontsize=5.5)
    rr = ratios.set_index('cfg')
    for k, c in enumerate(CFG + ['all four']):
        y = 9.6 + k * 3.0 + (0.8 if c == 'all four' else 0.0)
        if c != 'all four':
            key.add_patch(plt.Rectangle((0.2, y - 0.75), 1.4, 1.5, fc=MODEL_COLOR[c], ec='none'))
        bold = 'bold' if c == 'all four' else 'normal'
        key.text(2.6, y, 'All four models' if c == 'all four' else c, va='center', ha='left', fontsize=5.5,
                 fontweight=bold)
        key.text(25.0, y, f'{rr.loc[c, "ratio"]:.1f}\u00d7', va='center', ha='right', fontsize=5.5, fontweight=bold)
    if uncached is not None:
        y = 9.6 + 5 * 3.0 + 1.6
        key.text(2.6, y, 'Uncached input only', va='center', ha='left', fontsize=5.5, color=style.INK2)
        key.text(25.0, y, f'{uncached:.1f}\u00d7', va='center', ha='right', fontsize=5.5, color=style.INK2)


def draw_b(fig, H, r, per, pooled):
    label(fig, 76.0, 0, 'b', 'Incorrect runs cost no more than correct runs of the same task', H,
          'Numbers: input tokens of incorrect runs relative to correct runs of the same task and model')
    for j, env in enumerate(ENVS):
        ax = axes_mm(fig, 87.0 + j * 47.0, 17.0, 45.0, 35.0, H)
        log_axis(ax, 0.01, 10 ** 4, [0.01, 0.1, 1, 10, 100], ['0.01', '0.1', '1', '10', '100'],
                 'Input tokens per run (millions)' if j == 0 else '')
        if j:
            ax.set_yticklabels([])
        for i, c in enumerate(CFG):
            d = r[(r.cfg == c) & (r.env == env)]
            box(ax, i - 0.21, d[d.ok].input_tokens / 1e6, style.ENV_COLOR[env], style.ENV_TINT[env], solid=False)
            box(ax, i + 0.21, d[~d.ok].input_tokens / 1e6, style.ENV_COLOR[env], style.ENV_TINT[env], solid=True)
            t = per[(per.env == env) & (per.cfg == c)].iloc[0]
            ratio_label(ax, i, 0.92, t.ratio, t.p_holm)
        ax.set_xticks(range(len(CFG)), [TICK[c] for c in CFG])
        ax.tick_params(axis='x', length=0, pad=2, labelsize=5)
        ax.set_xlim(-0.6, len(CFG) - 0.4)
        pool = pooled.set_index('env').loc[env]
        ax.set_title(f'{style.ENV_LABEL[env]}, all models: {pool.ratio:.2f}×, {fmt_p(pool.p_holm)} '
                     f'({int(pool.sets)} sets)', fontsize=5, fontweight='bold', loc='left', pad=2.5, color=style.INK)
    handles = []
    for env in ENVS:
        handles += [Patch(fc=style.ENV_TINT[env], ec=style.ENV_COLOR[env], lw=0.6,
                          label=f'{style.ENV_LABEL[env]}, correct'),
                    Patch(fc=style.ENV_COLOR[env], ec=style.ENV_COLOR[env], lw=0.6,
                          label=f'{style.ENV_LABEL[env]}, incorrect')]
    fig.legend(handles=handles, ncol=4, loc='upper left', bbox_to_anchor=((76.0 + 4.4) / W, 1 - 8.0 / H),
               fontsize=5, handlelength=1.0, columnspacing=0.8, handletextpad=0.3, borderaxespad=0, frameon=False)


def draw_c(fig, H, y0, ok, fits, rho, act, tpa):
    label(fig, 0, y0, 'c', 'Cost follows interaction', H, 'Correct runs; lines join median input tokens in bins of actions')
    ax = axes_mm(fig, 11.0, y0 + 14.0, 76.0, 39.0, H)
    for env in ENVS:
        e = ok[ok.env == env]
        ax.scatter(e.actions, e.input_tokens / 1e6, s=1.2, marker=style.ENV_MARKER[env], color=style.ENV_COLOR[env],
                   alpha=0.25, lw=0, zorder=2, rasterized=True)
    edges = np.unique(np.round(np.logspace(0, 3.3, 15)))
    for env in ENVS:
        e = ok[ok.env == env]
        b = pd.cut(e.actions, np.r_[edges, 1e9], right=False)
        g = e.groupby(b, observed=True).agg(x=('actions', 'median'), y=('input_tokens', 'median'),
                                             n=('actions', 'size'))
        g = g[g.n >= 10]
        ax.plot(g.x, g.y / 1e6, color=style.ENV_COLOR[env], lw=0.9, zorder=3, marker=style.ENV_MARKER[env], ms=2.6,
                mfc=style.ENV_COLOR[env], mec='white', mew=0.3)
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1, 2000)
    ax.set_ylim(0.005, 300)
    ax.set_xticks([1, 10, 100, 1000], ['1', '10', '100', '1,000'])
    ax.set_yticks([0.01, 0.1, 1, 10, 100], ['0.01', '0.1', '1', '10', '100'])
    ax.minorticks_off()
    style.grid_y(ax)
    style.grid_x(ax)
    ax.set_xlabel('Actions per run (log scale)')
    ax.set_ylabel('Input tokens per run (millions)')
    a_, t_ = act.set_index('cfg').loc['all four'], tpa.set_index('cfg').loc['all four']
    ax.text(0.03, 0.97, f'Galaxy, same task:\n{a_.ratio:.1f}× actions\n{t_.ratio:.1f}× tokens per action',
            transform=ax.transAxes, ha='left', va='top', fontsize=5, linespacing=1.25)
    ax.text(0.97, 0.03, f'Spearman ρ = {rho[CODE]:.2f} (custom code)\n{rho[GAL]:.2f} (Galaxy)',
            transform=ax.transAxes, ha='right', va='bottom', fontsize=5, color=style.INK2, linespacing=1.25)
    ax.legend(handles=env_handles(), ncol=2, loc='lower left', bbox_to_anchor=(0.0, 1.01), fontsize=5.5,
              handletextpad=0.3, columnspacing=1.0, borderaxespad=0)


def draw_d(fig, H, y0, ops, never, cached):
    label(fig, 96.0, y0, 'd', 'Finding tools is half of what Galaxy sends back', H,
          'Each Galaxy interaction is a request from the agent and a text reply from Galaxy;\n'
          'the model reads every reply and rereads it at each later step (all Galaxy runs)')
    ax = axes_mm(fig, 107.0, y0 + 15.5, 27.0, 37.5, H)
    for i, col in enumerate(('call_pct', 'char_pct')):
        bottom = 0.0
        for (_, row), color in zip(ops.iterrows(), OP_COLOR):
            v = row[col]
            ax.bar(i, v, bottom=bottom, width=0.72, color=color, ec='white', lw=0.4, zorder=3)
            if v >= 6:
                ax.text(i, bottom + v / 2, f'{v:.0f}%', ha='center', va='center', fontsize=5,
                        color='white' if color in (style.GALAXY, style.NEUTRAL_DARK, '#8a8a8a') else style.INK)
            bottom += v
    ax.set_xticks([0, 1], ['Requests\nto Galaxy', 'Text sent\nback'])
    ax.tick_params(axis='x', length=0, pad=2)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_ylabel('Share of all requests or of all reply text (%)')
    ax.set_xlim(-0.5, 1.5)
    ax.legend(handles=[Patch(fc=c, label=n) for (n, _), c in zip(OPS, OP_COLOR)][::-1], loc='upper left',
              bbox_to_anchor=(1.06, 1.0), fontsize=5.5, handlelength=1.0, labelspacing=0.45, borderaxespad=0,
              title='What the request was for', title_fontsize=5.5, alignment='left')
    lo, hi = never.percent.min(), never.percent.max()
    ax.text(1.09, 0.36, f'Much of the lookup is unused: {lo:.0f}\u2013{hi:.0f}%\nof the tools an agent read about\n'
            f'were never run in that run\n\nReplies accumulate: {cached[GAL]:.0f}% of Galaxy\n'
            f'input tokens are earlier context\nreread at each step (custom\ncode {cached[CODE]:.0f}%)',
            transform=ax.transAxes, ha='left', va='top', fontsize=5, linespacing=1.25)


# ---------------------------------------------------------------- source data and assembly
def source_data(trade_tab, trade_ratio, reps, per, pooled, act, tpa, rho, ops, never, cached, uncached, insp, counts):
    rows = []
    for x in reps.itertuples():                       # the plotted points of panel a
        rows.append(dict(panel='a', model=x.cfg, condition=x.env, replicate=x.replicate, measure='accuracy_pct',
                         value=x.accuracy, n=x.runs))
        rows.append(dict(panel='a', model=x.cfg, condition=x.env, replicate=x.replicate,
                         measure='median_input_tokens', value=x.tokens, n=x.runs))
    # all replicates pooled, with 95% cluster-bootstrap intervals (not plotted; for the text)
    for x in trade_tab.itertuples():
        rows.append(dict(panel='a', model=x.cfg, condition=x.env, measure='accuracy_pct', value=x.accuracy,
                         ci95_low=x.acc_lo, ci95_high=x.acc_hi, n=x.runs))
        rows.append(dict(panel='a', model=x.cfg, condition=x.env, measure='median_input_tokens', value=x.tokens,
                         ci95_low=x.tok_lo, ci95_high=x.tok_hi, n=x.runs))
    for panel, measure, t in (('a', 'input_tokens_ratio_galaxy_over_code', trade_ratio),
                              ('c', 'actions_ratio_galaxy_over_code', act),
                              ('c', 'tokens_per_action_ratio_galaxy_over_code', tpa)):
        for x in t.itertuples():
            rows.append(dict(panel=panel, model=x.cfg, condition='galaxy / open_ended_code', measure=measure,
                             value=x.ratio, ci95_low=x.lo, ci95_high=x.hi, n=x.cells, p=x.p, p_holm=x.p_holm))
    for x in per.itertuples():
        rows.append(dict(panel='b', model=x.cfg, condition=x.env, measure='input_tokens_ratio_incorrect_over_correct',
                         value=x.ratio, ci95_low=x.lo, ci95_high=x.hi, n=x.sets, p=x.p, p_holm=x.p_holm))
    for x in pooled.itertuples():
        rows.append(dict(panel='b', model='all four', condition=x.env,
                         measure='input_tokens_ratio_incorrect_over_correct', value=x.ratio, ci95_low=x.lo,
                         ci95_high=x.hi, n=x.sets, p=x.p, p_holm=x.p_holm))
    for env, v in rho.items():
        rows.append(dict(panel='c', model='all four', condition=env, measure='spearman_rho_tokens_actions', value=v))
    for x in ops.itertuples():
        rows.append(dict(panel='d', model='all four', condition='galaxy', measure=f'calls_pct: {x.operation}',
                         value=x.call_pct, n=x.calls))
        rows.append(dict(panel='d', model='all four', condition='galaxy', measure=f'returned_text_pct: {x.operation}',
                         value=x.char_pct, n=x.chars))
    for x in never.itertuples():
        rows.append(dict(panel='d', model='all four', condition='galaxy', measure=f'inspected_never_run_pct: '
                         f'{x.benchmark}', value=x.percent, n=x.denominator))
    for env, v in cached.items():
        rows.append(dict(panel='d', model='all four', condition=env, measure='cached_share_of_input_pct_median', value=v))
    for x in uncached.itertuples():
        rows.append(dict(panel='a', model=x.cfg, condition='galaxy / custom_code', measure='uncached_input_tokens_ratio',
                         value=x.ratio, ci95_low=x.lo, ci95_high=x.hi, n=x.cells, p=x.p, p_holm=x.p_holm))
    for env, t in insp.iterrows():
        for code, lab in INSPECT:
            unit = 'runs' if code == 'history' else 'steps'
            rows.append(dict(panel='text', model='all four', condition=env, measure=f'pct_{unit}: {lab}', value=t[code],
                             n=counts[unit][env]))
    cols = ['panel', 'model', 'condition', 'replicate', 'measure', 'value', 'ci95_low', 'ci95_high', 'n', 'p', 'p_holm']
    out = pd.DataFrame(rows).reindex(columns=cols)
    out['condition'] = out.condition.str.replace('open_ended_code', 'custom_code')
    out.round(4).to_csv(os.path.join(OUT, 'fig5_source_data.csv'), index=False)


def main():
    r = load_runs()
    calls = load_calls()
    trade_tab, trade_ratio = trade(r)
    reps = replicate_points(r)
    per, pooled = outcome_ratios(r)
    ok, fits, rho, act, tpa = interaction(r)
    ops, never, cached = context(calls, r)
    global rng                              # separate random stream, so the draws of panels b-d are unchanged
    main_rng, rng = rng, np.random.default_rng(SEED + 2)
    uncached = condition_ratios(r[r.benchmark.isin(BIN)].dropna(subset=['uncached']), 'uncached')
    rng = main_rng
    insp, counts = inspectability()
    print('uncached ratio'); print(uncached.round(3).to_string(index=False))
    print('inspectability'); print(insp.round(1).to_string(), counts)
    for name, t in (('a: trade', trade_tab), ('a: replicates', reps), ('a: token ratio', trade_ratio), ('b: pooled', pooled),
                    ('c: actions', act), ('c: tokens per action', tpa), ('d: operations', ops), ('d: never run', never)):
        print(name)
        print(t.round(3).to_string(index=False))
    print('rho', rho, '| cached', cached.round(1).to_dict())

    H = 128.0
    fig = plt.figure(figsize=(W * MM, H * MM))
    draw_a(fig, H, reps, trade_ratio, uncached.set_index('cfg').loc['all four', 'ratio'])
    draw_b(fig, H, r, per, pooled)
    y2 = 66.0
    draw_c(fig, H, y2, ok, fits, rho, act, tpa)
    draw_d(fig, H, y2, ops, never, cached)
    style.enforce_min_font(fig)
    title = 'Fig. 5 | Galaxy increases analysis inspectability at higher token cost'
    fig.savefig(os.path.join(OUT, 'fig5.svg'), metadata={'Title': title}, dpi=600)
    fig.savefig(os.path.join(OUT, 'fig5.pdf'), metadata={'Title': title}, dpi=600)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    Image.open(buf).convert('RGB').save(os.path.join(OUT, 'fig5.png'), dpi=(600, 600))
    source_data(trade_tab, trade_ratio, reps, per, pooled, act, tpa, rho, ops, never, cached, uncached, insp, counts)


if __name__ == '__main__':
    main()
