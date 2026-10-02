"""Main and Extended Data figures, Source Data and text numbers for the Galaxy-oriented Analysis.

Run from the repository root with Python 3.12 and manuscript_narrative/requirements.txt:
    python manuscript_narrative/galaxy-oriented/scripts/make_figures.py [1 2 3 4 5 6 ed]

Question: what information and guarantees must a scientific workbench expose so that an agent's intended analysis is
faithfully executed, diagnosably recoverable and attributable? Galaxy (usegalaxy.org, reached through one Galaxy
interface adapter, July to September 2026) is the system studied. Open-ended code supplies observational resource
comparisons. Interface measures come from derived/galaxy_calls/calls.csv.gz (one row per interface call).
Every number quoted in manuscript.md as {{key}} is written to numbers.json by this script.
"""
import json
import os
import sys

import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER = os.path.dirname(HERE)
sys.path.insert(0, os.path.dirname(PAPER))
import narrative_common as nc  # noqa: E402
from narrative_common import FIG_W, fmt, plt, style  # noqa: E402
from style import (CODE, CONFIGS, ENV_COLOR, ENV_LABEL, ENV_MARKER, ENV_TINT, ENVS, GALAXY, GRID, INK, INK2, LIGHT,  # noqa: E402
                   MM, NEUTRAL_DARK, NEUTRAL_LIGHT, NEUTRAL_MID, OI_GREEN, OI_ORANGE, OI_PURPLE, OI_SKY, SUPERSEDED,
                   env_handles, grid_x, panel_label, panel_title)

TITLES = {
    'Fig1': 'System layers, provenance boundary and analysed evidence',
    'Fig2': 'Failed interactions, diagnostic indicators and later tool outcomes',
    'Fig3': 'Semantic fidelity: from requested to executed analysis',
    'Fig4': 'Context consumption in agent-driven Galaxy runs',
    'Fig5': 'Execution attribution: what the workbench record does and does not establish',
    'Fig6': 'Baseline agent-readiness measures and the requirements they motivate',
    'ED_Fig1': 'Galaxy capabilities used by agents',
    'ED_Fig2': 'Interaction styles of the model configurations',
    'ED_Fig3': 'User-defined tool outcomes',
}
BENCHES = style.BENCH
BL = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
BL2 = {'BixBench50': 'BixBench-\nVerified-50', 'CompBio': 'CompBio-\nBench', 'IWC': 'IWC'}
CFG_SHORT = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6 Sol', 'GPT-5.6 Luna': 'GPT-5.6 Luna',
             'DeepSeek V4 Pro': 'DeepSeek V4 Pro (Codex)', SUPERSEDED: 'DeepSeek V4 Pro\n(Claude Code, superseded)'}
PRE, POST, ADAPT = OI_SKY, OI_ORANGE, OI_PURPLE
DIAG_RX = r'(?:tool_)?std(?:err|out): *[^|\s]|Traceback'
CALL_CLASS = {'search_galaxy_tools': 'discovery', 'inspect_galaxy_tool': 'discovery', 'inspect_galaxy_history': 'inspection',
              'peek_galaxy_dataset': 'inspection', 'inspect_archive_inventory': 'inspection', 'run_galaxy_tool_and_wait': 'execution',
              'run_galaxy_udt_and_wait': 'execution', 'wait_for_galaxy_jobs': 'execution', 'stage_workspace_file': 'staging'}
NUM = {}
UDT_REQ = {}


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


def save_numbers(partial=False):
    for name, data in [('numbers.json', NUM), ('numbers_provenance.json', SRC)]:
        p = os.path.join(PAPER, name)
        old = json.load(open(p)) if partial and os.path.exists(p) else {}
        old.update(data)
        json.dump(dict(sorted(old.items())), open(p, 'w'), indent=1, ensure_ascii=False)


def new_fig(h_mm):
    return plt.figure(figsize=(FIG_W, h_mm * MM))


def pct(n, d, nd=1):
    return fmt(100 * n / d, nd)


def box(ax, x, y, w, h, text, fc='white', ec=INK2, lw=0.6, fs=5.4, weight='normal', ha='center', ls='-'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0,rounding_size=0.012', fc=fc, ec=ec, lw=lw, ls=ls,
                                transform=ax.transAxes, clip_on=False))
    tx = x + w / 2 if ha == 'center' else x + 0.012
    ax.text(tx, y + h / 2, text, ha=ha, va='center', fontsize=fs, fontweight=weight, transform=ax.transAxes, linespacing=1.2)


def arrow(ax, x0, y0, x1, y1, color=INK2, lw=0.7, ls='-', both=False):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle='<|-|>' if both else '-|>', mutation_scale=6, lw=lw,
                                 color=color, ls=ls, transform=ax.transAxes, shrinkA=0, shrinkB=0, clip_on=False))


def dot(ax, x, y, env, filled=True, ms=3.4, z=3):
    ax.plot(x, y, ENV_MARKER[env], ms=ms, mfc=ENV_COLOR[env] if filled else 'white',
            mec='white' if filled else ENV_COLOR[env], mew=0.4 if filled else 0.8, zorder=z, ls='', clip_on=False)


def plain_log(ax, ticks, axis='x'):
    from matplotlib.ticker import FixedLocator, NullFormatter
    a = ax.xaxis if axis == 'x' else ax.yaxis
    a.set_major_locator(FixedLocator(ticks))
    (ax.set_xticklabels if axis == 'x' else ax.set_yticklabels)([f'{t:g}' for t in ticks])
    a.set_minor_formatter(NullFormatter())


def gcalls():
    c = nc.galaxy_calls()
    return c[c.galaxy_server == True].copy()  # noqa: E712


def fidelity_class(r):
    s, prov = r.result_status, r.prov_status
    if s == 'ok' and prov == 'matched' and r.checked_parameter_count > 0:
        return 'ok_checked'
    if s == 'ok' and prov == 'no_explicit_non_dataset_parameters' and r.checked_parameter_count == 0:
        return 'ok_dataset_only'
    if s == 'ok':
        return 'ok_unverified'
    if s == 'validation_parameter_mismatch':
        return 'mismatch_before'
    if s in ('parameter_mismatch', 'provenance_mismatch'):
        return 'mismatch_after'
    return 'failed'


FIDELITY = [('ok_checked', 'Ran; requested and resolved\nparameters compared and matched', NEUTRAL_LIGHT),
            ('ok_dataset_only', 'Ran; dataset inputs only,\nno other parameter compared', '#BBBBBB'),
            ('ok_unverified', 'Ran; parameter provenance\nnot comparable or unverified', NEUTRAL_DARK),
            ('mismatch_before', 'Mismatch caught before\nsubmission', OI_SKY),
            ('mismatch_after', 'Job ran; parameter/input\nmismatch status returned', OI_PURPLE),
            ('failed', 'Other non-ok status\n(including failed jobs)', OI_ORANGE)]


# ---------------------------------------------------------------------------------------------------- Figure 1
def design_metadata():
    p = os.path.join(nc.NARR, 'derived', 'design_metadata.json')
    return json.load(open(p)) if os.path.exists(p) else None


def fig1():
    fig = new_fig(128)
    sd = {}
    calls = nc.galaxy_calls()
    g = calls[calls.galaxy_server == True]  # noqa: E712
    fd = nc.fd()
    inv = fd['inventory']
    # ---------------- a: layers
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'System layers and the provenance boundary')
    ax = fig.add_axes([0.01, 0.50, 0.98, 0.44])
    ax.axis('off')
    box(ax, 0.0, 0.55, 0.13, 0.36, 'Model\nconfiguration\n+ agent harness\n(Codex; Claude\nCode superseded)', fc=LIGHT, weight='bold')
    box(ax, 0.18, 0.55, 0.19, 0.36, 'Galaxy interface adapter\n(Model Context Protocol)\nsearch · inspect · run · wait\nuser-defined tools\n'
        'requested-vs-resolved\nparameter check', fc=ENV_TINT['galaxy'], ec=GALAXY)
    ax.add_patch(FancyBboxPatch((0.42, 0.50), 0.42, 0.47, boxstyle='round,pad=0,rounding_size=0.012', fc='none', ec=GALAXY, lw=0.9,
                                ls=(0, (4, 2)), transform=ax.transAxes))
    ax.text(0.43, 0.955, 'Provenance boundary: recorded in Galaxy job records and analysis histories', fontsize=5.1, color=GALAXY,
            transform=ax.transAxes, va='top')
    box(ax, 0.44, 0.56, 0.18, 0.32, 'Galaxy API and job system\n(usegalaxy.org)\ntool state, datatypes,\nhistories, job handlers', fc='white', ec=GALAXY)
    box(ax, 0.645, 0.56, 0.18, 0.32, 'Tool wrappers, containers\nand reference data\n(Tool Shed versions;\nagent-written tools)', fc='white', ec=GALAXY)
    box(ax, 0.87, 0.55, 0.13, 0.36, 'Benchmark\nreference and\nevaluator\n(outside the\nworkbench)', fc=LIGHT, ls=(0, (2, 2)))
    arrow(ax, 0.13, 0.73, 0.18, 0.73, both=True)
    arrow(ax, 0.37, 0.73, 0.44, 0.73, color=GALAXY, both=True)
    arrow(ax, 0.62, 0.73, 0.645, 0.73, color=GALAXY, both=True)
    box(ax, 0.18, 0.04, 0.19, 0.26, 'Local shell\nstaging, answer extraction;\nany local computation or\ncross-run reuse happens here,\noutside the boundary', fc='white', ls=(0, (3, 2)))
    arrow(ax, 0.07, 0.55, 0.18, 0.17, ls=(0, (3, 2)))
    arrow(ax, 0.37, 0.24, 0.50, 0.50, color=CODE, ls=(0, (3, 2)))
    ax.plot([0.37, 0.935], [0.08, 0.08], color=INK2, lw=0.7, ls=(0, (2, 2)), transform=ax.transAxes, clip_on=False)
    arrow(ax, 0.935, 0.08, 0.935, 0.55, ls=(0, (2, 2)))
    ax.text(0.66, 0.10, 'submitted answer', fontsize=5, transform=ax.transAxes, color=INK2, va='bottom')
    ax.plot([0.52, 0.56], [0.33, 0.33], color=CODE, lw=0.7, ls=(0, (3, 2)), transform=ax.transAxes)
    ax.text(0.57, 0.33, 'Direct Galaxy API calls from the shell: inside the boundary,\nbut outside the adapter and its parameter check', fontsize=5,
            transform=ax.transAxes, va='center', color=INK)
    # ---------------- b: evidence
    panel_label(fig, 0.005, 0.45, 'b')
    panel_title(fig, 0.005, 0.45, 'Analysed evidence (Galaxy-condition runs)')
    axb = fig.add_axes([0.02, 0.02, 0.96, 0.37])
    axb.axis('off')
    meta = design_metadata()
    hdr = ['', 'Galaxy runs', 'Traces parsed', 'Detailed\nhistory', 'Galaxy-interface\ncalls', 'Other tool-\nserver calls',
           'Analysis jobs', 'Run dates (histories)', 'Harness or\nimage labels']
    xs = [0.0, 0.13, 0.22, 0.31, 0.40, 0.51, 0.61, 0.70, 0.86]
    for x, h in zip(xs, hdr):
        axb.text(x, 0.98, h, fontsize=5.3, fontweight='bold', va='top', transform=axb.transAxes, linespacing=1.12)
    axb.plot([0, 1], [0.80, 0.80], color=INK2, lw=0.5, transform=axb.transAxes, clip_on=False)
    cov = nc.analysis()['runs']
    rows = []
    for i, b in enumerate(BENCHES):
        gr = [r for r in cov if r['benchmark'] == b and r['condition'] == 'galaxy']
        hist = sum(1 for r in gr if (r.get('coverage') or {}).get('public_history_contents') == 'retrieved')
        tr = sum(1 for r in gr if (r.get('coverage') or {}).get('agent_transcript') == 'retrieved')
        ncalls = int((g.benchmark == b).sum())
        other = int(((calls.benchmark == b) & (calls.galaxy_server != True)).sum())  # noqa: E712
        dm = nc.design_runs()
        dm = dm[(dm.benchmark == b) & (dm.condition == 'galaxy')]
        ts = pd.to_datetime(dm.ev_ts_history_create, errors='coerce', format='mixed').dropna()
        dates = f'{ts.min():%d %b} to\n{ts.max():%d %b %Y}' if len(ts) else 'not recorded'
        lab_ = dm[['mm_harness', 'docker_image', 'iso_image_id']].bfill(axis=1).iloc[:, 0]
        variants = f'{lab_.nunique()}'
        put(f'dates_{b}', f'{ts.min().day} {ts.min():%B} to {ts.max().day} {ts.max():%B %Y}' if len(ts) else 'not recorded')
        put(f'harness_{b}', str(lab_.nunique()))
        cells = [BL2[b], f'{len(gr):,}', f'{tr:,}', f'{hist:,}', f'{ncalls:,}', f'{other:,}', f'{inv[b]["nonfetch_jobs"]:,}', str(dates), str(variants)]
        y = 0.72 - i * 0.20
        for x, t in zip(xs, cells):
            axb.text(x, y, t, fontsize=5.3, va='top', transform=axb.transAxes, linespacing=1.12, fontweight='bold' if x == 0 else 'normal')
        rows.append(dict(benchmark=BL[b], galaxy_runs=len(gr), traces=tr, detailed_histories=hist, galaxy_interface_calls=ncalls,
                         other_tool_server_calls=other, analysis_jobs=inv[b]['nonfetch_jobs'], history_dates=dates, harness_variants=variants))
    axb.text(0.0, 0.0, 'Other tool-server calls: client built-ins and external connectors logged in Galaxy-condition runs; excluded from interface '
             'measures. usegalaxy.org only; adapter commit coverage is incomplete;\nsoftware and catalog versions are those current at run time and are not '
             'frozen (Methods).', fontsize=4.9, color=INK2, transform=axb.transAxes, va='bottom')
    sd['b_evidence'] = pd.DataFrame(rows)
    tot = sum(r['galaxy_interface_calls'] for r in rows)
    put('n_galaxy_runs', f'{sum(r["galaxy_runs"] for r in rows):,}')
    put('n_traces', f'{sum(r["traces"] for r in rows):,}')
    put('n_histories', f'{sum(r["detailed_histories"] for r in rows):,}')
    put('n_interface_calls', f'{tot:,}')
    put('n_other_calls', f'{sum(r["other_tool_server_calls"] for r in rows):,}')
    put('n_jobs', f'{sum(inv[b]["nonfetch_jobs"] for b in BENCHES):,}')
    nc.save_figure(fig, PAPER, 'Fig1', TITLES['Fig1'])
    nc.source_data(PAPER, 'Fig1', sd, TITLES['Fig1'])


# ---------------------------------------------------------------------------------------------------- Figure 2
FAIL_LABEL = [
    ('A1 tool-schema needs history context', 'Schema requested without a usable history', PRE),
    ('A4 parameter value / datatype validation', 'Parameter value or datatype rejected', PRE),
    ('A2 tool ID not found / guessed', 'Tool identifier not found', PRE),
    ('A5 ID handling (wrong/foreign/truncated IDs)', 'Dataset or history identifier misused', PRE),
    ('A3 nested-parameter key structure', 'Nested parameter structure rejected', PRE),
    ('A8 server / transport / rate-limit', 'Server, transport or rate limit', PRE),
    ('A6 UDT representation schema', 'User-defined tool schema rejected', PRE),
    ('A7 upload / datatype registry', 'Upload datatype unknown', PRE),
    ('X additional transport or tool exceptions (previously uncounted)', 'Additional transport/tool exceptions\n(previously uncounted)', ADAPT),
    ('B2 job error with no diagnostic', 'Job failed, no diagnostic text', POST),
    ('B3 tool runtime error (stderr)', 'Runtime error with stderr', POST),
    ('B4 input format / compression / index', 'Input format, compression or index', POST),
    ('B1 UDT container missing dependency', 'Container lacked a dependency', POST),
    ('B5 memory / resource', 'Memory or resource limit', POST),
    ('Z unclassified', 'Unclassified', NEUTRAL_MID),
]


def fig2():
    fig = new_fig(160)
    sd = {}
    f = nc.galaxy_failures()
    g = gcalls()
    # ---------------- a: failure classes
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'Failed Galaxy-interface calls by class')
    rows = []
    for j, b in enumerate(BENCHES):
        ax = fig.add_axes([0.225 + j * 0.095, 0.53, 0.075, 0.40])
        for i, (k, lab, col) in enumerate(FAIL_LABEL):
            v = int(((f.benchmark == b) & f.failure_class.str.split().str[0].eq(k.split()[0])).sum())
            ax.barh(i, v, color=col, height=0.7)
            ax.text(v + 12, i, f'{v:,}', va='center', fontsize=4.7)
            rows.append(dict(benchmark=BL[b], failure_class=lab.replace('\n', ' '), code=k.split(' ')[0], failed_calls=v))
        ax.set_ylim(len(FAIL_LABEL) - 0.4, -0.6)
        ax.set_yticks(range(len(FAIL_LABEL)))
        ax.set_yticklabels([x[1] for x in FAIL_LABEL] if j == 0 else [], fontsize=5, linespacing=1.05)
        ax.set_xlim(0, {'BixBench50': 900, 'CompBio': 2000, 'IWC': 160}[b])
        n_calls = int((g.benchmark == b).sum())
        n_fail = int((f.benchmark == b).sum())
        ax.set_title(f'{BL2[b]}\n{n_fail:,} of {n_calls:,}', fontsize=5.2, loc='left', linespacing=1.08)
        for yy in (7.5, 8.5, 13.5):
            ax.axhline(yy, color=INK2, lw=0.4, ls=(0, (2, 2)))
        grid_x(ax)
        ax.tick_params(axis='x', labelsize=4.8)
        if j == 1:
            ax.set_xlabel('Failed calls')
        put(f'fail_{b}', f'{n_fail:,} of {n_calls:,} ({pct(n_fail, n_calls)}%)')
    pre = int(f.failure_class.str[0].eq('A').sum())
    xad = int(f.failure_class.str[0].eq('X').sum())
    post = int(f.failure_class.str[0].eq('B').sum())
    unc = int(f.failure_class.str[0].eq('Z').sum())
    tot = len(f)
    put('fail_total', f'{tot:,}')
    put('fail_rate', pct(tot, len(g)))
    put('fail_legacy', f'{tot - xad:,}')
    put('fail_adapter', f'{xad:,}')
    put('fail_pre', f'{pre:,} ({pct(pre, tot)}%)')
    put('fail_post', f'{post:,} ({pct(post, tot)}%)')
    put('fail_unclassified', f'{unc:,}')
    # reconciliation with the archived trace-friction ledger, which also counted calls to non-Galaxy tool servers
    leg = json.load(open(os.path.join(nc.ROOT, 'analysis_reports', 'galaxy_improvement_20260924', 'v2_trace_friction', 'cat_tool.json')))
    leg_n = {k: (v if isinstance(v, int) else sum(v.values()) if isinstance(v, dict) else len(v)) for k, v in leg.items()}
    leg_nong = {k: v for k, v in leg_n.items() if k.split('|')[1] not in CALL_CLASS}
    put('legacy_total', f'{sum(leg_n.values()):,}')
    put('legacy_unclassified', f'{sum(v for k, v in leg_n.items() if k.startswith("Z")):,}')
    put('legacy_nongalaxy', f'{sum(leg_nong.values()):,}')
    put('legacy_nongalaxy_unclassified', f'{sum(v for k, v in leg_nong.items() if k.startswith("Z")):,}')
    sd['a_legacy_reconciliation'] = pd.DataFrame([dict(category=k.split('|')[0], tool=k.split('|')[1], legacy_failed_calls=v,
                                                       galaxy_interface_call=k.split('|')[1] in CALL_CLASS) for k, v in leg_n.items()])
    a1 = f[f.failure_class.str.startswith('A1')].a1_subclass.value_counts()
    put('a1_total', f'{int(a1.sum()):,}')
    put('a1_no_history', f'{int(a1.get("no history given", 0)):,}')
    put('a1_unusable', f'{int(a1.get("history given but unusable", 0)):,}')
    put('b2_total', f'{int((f.failure_class.str.startswith("B2")).sum()):,}')
    fig.legend(handles=[Patch(fc=PRE, label='Interface/input/transport classes'), Patch(fc=ADAPT, label='Additional exceptions (phase unknown)'),
                        Patch(fc=POST, label='Job/tool classes'), Patch(fc=NEUTRAL_MID, label='Unclassified')],
               loc='upper left', bbox_to_anchor=(0.01, 0.48), ncol=4, fontsize=5)
    sd['a_failure_classes'] = pd.DataFrame(rows)
    phase = f.merge(g[['benchmark', 'task', 'run_id', 'line', 'n_jobs', 'job_ids', 'job_states', 'any_job_error',
                       'job_failure_phases', 'result_status', 'call_status']],
                    on=['benchmark', 'task', 'run_id', 'line'], how='left', validate='one_to_one')
    phase['returned_job_evidence'] = np.where(phase.n_jobs.fillna(0) > 0, 'Job record returned',
                                             np.where(phase.n_jobs.notna(), 'No job record returned', 'Job metadata absent'))
    sd['a_call_job_evidence'] = phase
    sd['a_class_job_evidence'] = phase.groupby(['benchmark', 'failure_class', 'returned_job_evidence']).size().rename('calls').reset_index()
    put('a_calls_with_job_records', str(int((phase.failure_class.str.startswith('A') & phase.n_jobs.fillna(0).gt(0)).sum())))
    # ---------------- b: first attempts versus retries
    panel_label(fig, 0.53, 0.995, 'b')
    panel_title(fig, 0.53, 0.995, 'Outcome of tool-run calls: first attempts and retries')
    runs_ = g[g.tool.isin(['run_galaxy_tool_and_wait', 'run_galaxy_udt_and_wait'])].copy()
    runs_['attempt'] = np.where(runs_.prior_same_tool_calls.fillna(0) > 0, 'retry', 'first')
    runs_['ok'] = runs_.result_status.eq('ok')
    ax = fig.add_axes([0.66, 0.66, 0.24, 0.27])
    rows = []
    for i, b in enumerate(BENCHES):
        for k, (tool, tl) in enumerate([('run_galaxy_tool_and_wait', 'installed tool'), ('run_galaxy_udt_and_wait', 'user-defined tool')]):
            if b == 'IWC' and tool == 'run_galaxy_udt_and_wait':
                ax.text(2, i * 2.4 + k, 'not offered', fontsize=4.8, va='center', color=INK2)
            for a, dy in [('first', -0.13), ('retry', 0.13)]:
                x = runs_[(runs_.benchmark == b) & (runs_.tool == tool) & (runs_.attempt == a)]
                if len(x) < 20:
                    continue
                yy = i * 2.4 + k * 1.0 + dy
                v = 100 * x.ok.mean()
                ax.barh(yy, v, height=0.24, color=GALAXY if a == 'first' else ENV_TINT['galaxy'], edgecolor=GALAXY, lw=0.4)
                ax.text(v + 1, yy, f'{fmt(v, 0)}% (n = {len(x):,})', va='center', fontsize=4.6)
                rows.append(dict(benchmark=BL[b], tool_kind=tl, attempt=a, calls=len(x), returned_ok=int(x.ok.sum()), percent_ok=v))
    yt = [i * 2.4 + k for i in range(3) for k in range(2)]
    ax.set_yticks(yt)
    ax.set_yticklabels([f'{BL[b]}, {tl}' for b in BENCHES for tl in ('installed tool', 'user-defined tool')], fontsize=4.9)
    ax.set_ylim(6.3, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Calls returning "ok" (%)')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=GALAXY, label='First attempt for that tool in the run'), Patch(fc=ENV_TINT['galaxy'], ec=GALAXY, lw=0.4, label='Retry')],
              loc='lower right', fontsize=4.8)
    sd['b_attempts'] = pd.DataFrame(rows)
    first = runs_[runs_.attempt == 'first']
    put('first_attempt_share', f'{pct(len(first), len(runs_), 0)}%')
    # ---------------- c: diagnostics
    panel_label(fig, 0.005, 0.40, 'c')
    panel_title(fig, 0.005, 0.40, 'Failed jobs: phase and diagnostic indicators in returned excerpts')
    jf = g[g.any_job_error == True].copy()  # noqa: E712
    jf['phase'] = np.where(jf.job_failure_phases.fillna('').str.contains('pre_execution'), 'Before execution', 'At run time')
    ax = fig.add_axes([0.20, 0.07, 0.26, 0.22])
    rows = []
    for i, (ph, udt) in enumerate([('Before execution', True), ('Before execution', False), ('At run time', True), ('At run time', False)]):
        x = jf[(jf.phase == ph) & (jf.udt == udt)]
        if not len(x):
            continue
        txt = int(x.error_excerpt.fillna('').str.contains(DIAG_RX, regex=True).sum())
        ax.barh(i, txt, color=NEUTRAL_LIGHT, height=0.6)
        ax.barh(i, len(x) - txt, left=txt, color=OI_ORANGE, height=0.6)
        ax.text(len(x) + 20, i, f'{len(x) - txt:,} of {len(x):,} without an indicator', va='center', fontsize=4.9)
        rows.append(dict(phase=ph, user_defined_tool=udt, failed_job_calls=len(x), with_error_text=txt, without_error_text=len(x) - txt))
    ax.set_yticks(range(4))
    ax.set_yticklabels(['Before execution, user-defined tool', 'Before execution, installed tool', 'At run time, user-defined tool',
                        'At run time, installed tool'], fontsize=5)
    ax.set_ylim(3.6, -0.6)
    ax.set_xlim(0, 2600)
    ax.set_xlabel('Interface calls that returned a failed job')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=NEUTRAL_LIGHT, label='Diagnostic indicator in excerpt'), Patch(fc=OI_ORANGE, label='No diagnostic indicator in excerpt')],
              loc='lower left', bbox_to_anchor=(0, 1.0), ncol=2, fontsize=4.8)
    sd['c_diagnostics'] = pd.DataFrame(rows)
    pre_udt = [r for r in rows if r['phase'] == 'Before execution' and r['user_defined_tool']][0]
    put('pre_udt_notext', f'{pre_udt["without_error_text"]:,} of {pre_udt["failed_job_calls"]:,}')
    run_ = [r for r in rows if r['phase'] == 'At run time']
    put('runtime_notext', f'{sum(r["without_error_text"] for r in run_):,} of {sum(r["failed_job_calls"] for r in run_):,}')
    # ---------------- d: operational versus scientific recovery
    panel_label(fig, 0.53, 0.40, 'd')
    panel_title(fig, 0.53, 0.40, 'After a non-ok tool call: later status and final evaluator outcome')
    grades = nc.graded_runs()
    grades = grades.rename(columns={'score': 'grade'})
    runs_['failed_call'] = ~runs_.ok
    rec = []
    runs_['tool_key'] = np.where(runs_.tool == 'run_galaxy_udt_and_wait', 'user-defined tool', runs_.tool_id_base.fillna('unknown'))
    for (b, t, rid, tid), x in runs_.sort_values('line').groupby(['benchmark', 'task', 'run_id', 'tool_key']):
        fails = x[x.failed_call]
        if fails.empty:
            continue
        first_fail_line = fails.line.min()
        later_ok = bool(((x.line > first_fail_line) & x.ok).any())
        rec.append(dict(benchmark=b, task=t, run_id=rid, tool_id=tid, model=x.model.iloc[0], replicate=x.replicate.iloc[0],
                        first_non_ok_line=int(first_fail_line), first_non_ok_status=fails.iloc[0].result_status,
                        later_ok=later_ok))
    rec = pd.DataFrame(rec)
    rec['cfg'] = rec.model.map(nc.CFG)
    rec = rec.merge(grades[grades.env == 'galaxy'][['benchmark', 'task', 'cfg', 'replicate', 'grade']], on=['benchmark', 'task', 'cfg', 'replicate'],
                    how='left')
    rec['run_correct'] = rec.grade.apply(lambda v: np.nan if pd.isna(v) else float(v >= (0.95 if v < 1 and v > 0 else 1)))
    ax = fig.add_axes([0.66, 0.07, 0.24, 0.20])
    rows = []
    for i, b in enumerate(BENCHES):
        x = rec[(rec.benchmark == b) & rec.run_correct.notna()]
        cats = [('later_ok', 1, 'Later ok in tool family;\nfinal outcome accepted', NEUTRAL_LIGHT),
                ('later_ok', 0, 'Later ok in tool family;\nfinal outcome not accepted', OI_ORANGE),
                ('not', 1, 'No later ok in tool family;\nfinal outcome accepted', '#BBBBBB'),
                ('not', 0, 'No later ok in tool family;\nfinal outcome not accepted', NEUTRAL_DARK)]
        left = 0
        for k, (lk, rc, lab, col) in enumerate(cats):
            m = (x.later_ok == (lk == 'later_ok')) & (x.run_correct == rc)
            v = 100 * m.mean()
            ax.barh(i, v, left=left, color=col, edgecolor='white', lw=0.4, height=0.6)
            if v > 7:
                ax.text(left + v / 2, i, fmt(v, 0), ha='center', va='center', fontsize=4.9, color='white' if col == NEUTRAL_DARK else INK)
            left += v
            rows.append(dict(benchmark=BL[b], category=lab.replace('\n', ' '), episodes=int(m.sum()), total=len(x), percent=v))
        ax.text(101, i, f'{len(x):,}', va='center', fontsize=4.8, color=INK2)
        lo = int((x.later_ok).sum())
        put(f'recover_{b}', f'{pct(lo, len(x), 0)}%')
    ax.set_yticks(range(3))
    ax.set_yticklabels([BL2[b] for b in BENCHES], fontsize=5, linespacing=1.05)
    ax.set_ylim(2.6, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Scored non-ok episodes (run × tool family; %)')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=c, label=l) for _, _, l, c in cats], loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=2, fontsize=4.7)
    sd['d_recovery'] = pd.DataFrame(rows)
    sd['d_recovery_episodes'] = rec
    sd['d_episode_eligibility'] = rec.groupby('benchmark').agg(
        all_episodes=('run_id', 'size'), scored_episodes=('grade', 'count')).reset_index()
    nc.save_figure(fig, PAPER, 'Fig2', TITLES['Fig2'])
    nc.source_data(PAPER, 'Fig2', sd, TITLES['Fig2'])


# ---------------------------------------------------------------------------------------------------- Figure 3
MECH = [
    ('Conditional parameter rebound to its default', 'bix-35-q1',
     'Requested: metric "evolutionary rate". Resolved and executed: default\n"total tree length"; job state ok. A resubmission that named the branch\n'
     'by index sent no comparable parameter, so the check compared none.', '7 of 15 histories held such a\njob; 6 runs resubmitted after\nthe flag; 1 answer wrong'),
    ('Output semantics not declared', 'bix-28-q3',
     'Requested: one summary value per tree. The output was the variance\nunder the metric name. Wrapper parsing is inferred; the wrapper\nsource was not archived.',
     '1 answer wrong: 146.3, outside\nthe range of the four values\n(median −30.5)'),
    ('Underlying software version not exposed', 'bix-45-q1',
     'Search and inspect exposed wrapper versions, not PhyKIT versions.\n13 runs used the wrapper and 2 used Galaxy user-defined tools;\nthe reference encodes a retired definition.',
     'All 15 Galaxy runs gave the same,\nscientifically defensible answer;\nall were scored incorrect'),
    ('Execution environment changed tool behaviour', 'encode-atac-pipeline-q1',
     'Inputs were staged as dataset_*.dat; the pipeline detects\ncompression by file extension, so adapter trimming was skipped\nwithout any error.',
     '7 of 12 computed untrimmed peaks;\n1 additional run copied\na pilot answer'),
    ('Several versions of one tool in the catalog', 'IWC peptide verification',
     'Runs that used the legacy PepQuery 1.6.2 wrapper scored lower than\nruns that used only PepQuery2 2.0.2 (association; search order\nwas not controlled).',
     '4 runs: 0.868-0.908\n8 runs: 0.982-1.000'),
]


def fig3():
    fig = new_fig(165)
    sd = {}
    g = gcalls()
    tr = g[g.tool == 'run_galaxy_tool_and_wait'].copy()
    tr['fid'] = tr.apply(fidelity_class, axis=1)
    # ---------------- a: fidelity classes
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'Installed-tool run calls by parameter-check coverage and outcome')
    ax = fig.add_axes([0.12, 0.79, 0.37, 0.15])
    rows = []
    for i, b in enumerate(BENCHES):
        x = tr[tr.benchmark == b]
        left = 0
        for k, lab, col in FIDELITY:
            v = 100 * (x.fid == k).mean()
            ax.barh(i, v, left=left, color=col, edgecolor='white', lw=0.4, height=0.64)
            if v > 5:
                ax.text(left + v / 2, i, fmt(v, 0), ha='center', va='center', fontsize=4.9, color='white' if col in (OI_PURPLE,) else INK)
            left += v
            rows.append(dict(benchmark=BL[b], fidelity_class=lab.replace('\n', ' '), calls=int((x.fid == k).sum()), total=len(x), percent=v))
        ax.text(101, i, f'{len(x):,}', va='center', fontsize=4.8, color=INK2)
    ax.set_yticks(range(3))
    ax.set_yticklabels([BL2[b] for b in BENCHES], fontsize=5, linespacing=1.05)
    ax.set_ylim(2.5, -0.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Calls (%; total at right)')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=c, label=l) for _, l, c in FIDELITY], loc='upper left', bbox_to_anchor=(-0.27, -0.45), ncol=3, fontsize=4.8,
              columnspacing=0.8)
    sd['a_fidelity'] = pd.DataFrame(rows)
    sd['a_call_coverage'] = tr[['benchmark', 'task', 'run_id', 'cfg', 'replicate', 'line', 'tool_id_full', 'result_status',
                              'prov_status', 'prov_stage', 'checked_parameter_count', 'dataset_prov_status', 'fid']].copy()
    overlap = tr.assign(parameter_mismatch=tr.prov_status.eq('mismatch'), input_mismatch=tr.dataset_prov_status.eq('mismatch'))
    sd['a_mismatch_overlaps'] = overlap.groupby(['benchmark', 'parameter_mismatch', 'input_mismatch']).size().rename('calls').reset_index()
    sd['a_parameter_mismatch_by_status'] = tr[tr.prov_status.eq('mismatch')].groupby(
        ['benchmark', 'prov_stage', 'result_status'], dropna=False).size().rename('calls').reset_index()
    d = pd.DataFrame(rows)
    for k, _, _ in FIDELITY:
        z = d[d.fidelity_class == [l for kk, l, _ in FIDELITY if kk == k][0].replace('\n', ' ')]
        put(f'fid_{k}', f'{fmt(z.percent.min(), 0)}% to {fmt(z.percent.max(), 0)}%')
    mm = tr[tr.prov_status.eq('mismatch')]
    put('mismatch_calls', f'{len(mm):,}')
    put('mismatch_before', f'{int((mm.prov_stage == "validation").sum()):,}')
    put('mismatch_after', f'{int((mm.prov_stage == "post_run").sum()):,}')
    put('mismatch_before_share', f'{pct((mm.prov_stage == "validation").sum(), len(mm), 0)}%')
    put('input_mismatch_calls', f'{int(tr.dataset_prov_status.eq("mismatch").sum()):,}')
    put('any_mismatch_calls', f'{int((tr.prov_status.eq("mismatch") | tr.dataset_prov_status.eq("mismatch")).sum()):,}')
    put('mismatch_with_failed_status', f'{int((mm.result_status == "failed").sum()):,}')
    put('ok_dataset_only', f'{int((tr.fid == "ok_dataset_only").sum()):,}')
    put('ok_unverified', f'{int((tr.fid == "ok_unverified").sum()):,}')
    put('tool_run_calls', f'{len(tr):,}')
    # ---------------- b: tool-normalized mismatch rates
    panel_label(fig, 0.53, 0.995, 'b')
    panel_title(fig, 0.53, 0.995, 'Parameter-mismatch rate by tool (tools with ≥40 run calls)')
    t = tr.groupby('tool_id_base').agg(calls=('fid', 'size'), mism=('prov_status', lambda v: v.eq('mismatch').sum()))
    t = t[t.calls >= 40].assign(rate=lambda z: z.mism / z.calls).sort_values('rate', ascending=False)
    show = pd.concat([t.head(10), t.tail(3)])
    ax = fig.add_axes([0.70, 0.62, 0.20, 0.32])
    for i, (tid, r_) in enumerate(show.iterrows()):
        ax.barh(i, 100 * r_.rate, color=OI_SKY if i < 10 else NEUTRAL_LIGHT, height=0.62)
        ax.text(100 * r_.rate + 1.5, i, f'{fmt(100 * r_.rate, 0)}% of {int(r_.calls):,}', va='center', fontsize=4.8)
    ax.axhline(9.5, color=INK2, lw=0.4, ls=(0, (2, 2)))
    ax.set_yticks(range(len(show)))
    ax.set_yticklabels([str(i).split('/')[-1] if '/' in str(i) else str(i) for i in show.index], fontsize=4.9)
    ax.set_ylim(len(show) - 0.4, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Run calls with a parameter mismatch (%)')
    grid_x(ax)
    ax.text(1.0, len(show) - 0.6, 'lowest three', fontsize=4.7, color=INK2, ha='right', transform=ax.get_yaxis_transform())
    sd['b_tool_rates'] = t.reset_index()
    put('n_tools_40', str(len(t)))
    top = t.head(10)
    put('top10_mismatch_range', f'{fmt(100 * top.rate.min(), 0)}% to {fmt(100 * top.rate.max(), 0)}%')
    put('tools_zero_mismatch', str(int((t.mism == 0).sum())))
    # ---------------- c: mechanisms
    panel_label(fig, 0.005, 0.56, 'c')
    panel_title(fig, 0.005, 0.56, 'Requested, executed and interpreted analysis: five mechanisms that changed or obscured answers')
    ax = fig.add_axes([0.01, 0.215, 0.98, 0.32])
    ax.axis('off')
    h = 0.18
    rows = []
    for i, (name, task, what, effect) in enumerate(MECH):
        y0 = 1 - (i + 1) * (h + 0.016)
        ax.add_patch(FancyBboxPatch((0, y0), 0.25, h, boxstyle='round,pad=0,rounding_size=0.008', fc=LIGHT, ec=INK2, lw=0.5, transform=ax.transAxes))
        ax.text(0.008, y0 + h / 2, f'{name}\n({task})', fontsize=5.0, fontweight='bold', va='center', transform=ax.transAxes, linespacing=1.15)
        box(ax, 0.26, y0, 0.50, h, what, fs=5.0, ha='left')
        box(ax, 0.77, y0, 0.23, h, effect, fs=5.0, ec=GALAXY, ha='left')
        rows.append(dict(mechanism=name, task=task, what_happened=what.replace('\n', ' '), consequence=effect.replace('\n', ' ')))
    sd['c_mechanisms'] = pd.DataFrame(rows)
    # ---------------- d: attribution
    panel_label(fig, 0.005, 0.16, 'd')
    panel_title(fig, 0.005, 0.16, 'Galaxy as a cause of wrong answers (targeted audit)')
    fd = nc.fd()
    tc = pd.DataFrame(fd['task_cases'])
    prim = set(tc[tc.category == 'C4'].task)
    tagged = set(tc[tc.tags.apply(lambda v: 'galaxy-platform-defect' in v)].task)
    e = fd['fig2e']['galaxy']
    div = fd['divergence_by_config']
    div4 = {k: sum(div.get(f'galaxy|{c}', {}).get(k, 0) for c in CONFIGS) for k in ('V1', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8')}
    units = [('Audited task cases (93; all benchmarks)', len(prim), len(tagged - prim), len(tc)),
             ('Scored-incorrect Galaxy runs, BixBench-Verified-50 (all five configurations)', e['primary'].get('PLATFORM', 0),
              e['platform_any'] - e['primary'].get('PLATFORM', 0), e['n']),
             ('Galaxy replicate divergences, BixBench-Verified-50 (four Codex configurations)', div4['V1'], 0, sum(div4.values()))]
    ax = fig.add_axes([0.42, 0.05, 0.25, 0.085])
    rows = []
    for i, (lab, p_, s_, n) in enumerate(units):
        ax.barh(i, 100 * p_ / n, color=NEUTRAL_DARK, height=0.6)
        ax.barh(i, 100 * s_ / n, left=100 * p_ / n, color=NEUTRAL_MID, height=0.6)
        ax.text(100 * (p_ + s_) / n + 1, i, f'{p_} primary + {s_} contributing = {p_ + s_} of {n}', va='center', fontsize=4.9)
        rows.append(dict(unit=lab, galaxy_primary=p_, galaxy_contributing_only=s_, union=p_ + s_, total=n))
    ax.set_yticks(range(3))
    ax.set_yticklabels([u[0] for u in units], fontsize=4.9)
    ax.set_ylim(2.6, -0.6)
    ax.set_xlim(0, 45)
    ax.set_xlabel('Share attributed to Galaxy platform, wrapper or server (%)')
    grid_x(ax)
    sd['d_attribution'] = pd.DataFrame(rows)
    put('attr_cases', f'{len(prim | tagged)} of {len(tc)} ({len(prim)} as primary cause, {len(tagged - prim)} as contributing cause only)')
    put('attr_runs', f'{e["platform_any"]} of {e["n"]} ({e["primary"].get("PLATFORM", 0)} as primary cause, '
                     f'{e["platform_any"] - e["primary"].get("PLATFORM", 0)} as contributing cause only)')
    put('attr_div', f'{div4["V1"]} of {sum(div4.values())}')
    nc.save_figure(fig, PAPER, 'Fig3', TITLES['Fig3'])
    nc.source_data(PAPER, 'Fig3', sd, TITLES['Fig3'])


# ---------------------------------------------------------------------------------------------------- Figure 4
def cell_ratio(df, value, bench, cfgs=CONFIGS):
    """Median over complete task x configuration cells (all six runs observed) of median(Galaxy)/median(code)."""
    r = nc.runs()
    cmap = dict(zip(zip(r.benchmark, r.task), r.cluster))
    x = df[(df.benchmark == bench) & df.cfg.isin(cfgs)]
    n_ok = x.groupby(['task', 'cfg', 'env'])[value].apply(lambda v: v.notna().sum()).unstack('env')
    med = x.groupby(['task', 'cfg', 'env'])[value].median().unstack('env')
    elig = len(med)
    med = med[(n_ok.open_ended_code == 3) & (n_ok.galaxy == 3)].dropna()
    med = med[med.open_ended_code > 0]
    med['ratio'] = med.galaxy / med.open_ended_code
    med = med.reset_index()
    med['cluster'] = [cmap[(bench, t)] for t in med.task]
    return nc.boot_median_ratio([g_.ratio.values for _, g_ in med.groupby('cluster')]), len(med), elig, med


def fig4():
    fig = new_fig(150)
    sd = {}
    S = nc.summaries()
    S = S.assign(uncached=S.input_tokens - S.cached)
    # ---------------- a: tokens
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'Token use, Galaxy ÷ open-ended code (complete cells)')
    ax = fig.add_axes([0.16, 0.62, 0.27, 0.29])
    kinds = [('input_tokens', 'All input (incl. cached)', 'o'), ('uncached', 'Uncached input', 'D'), ('output_tokens', 'Output', 's')]
    rows, cell_obs = [], []
    for i, b in enumerate(BENCHES):
        for k, (col, lab, mk) in enumerate(kinds):
            (est, lo, hi), n, elig, cells = cell_ratio(S, col, b)
            yy = i * 1.3 + (k - 1) * 0.3
            ax.plot([lo, hi], [yy, yy], color=GALAXY, lw=0.8)
            ax.plot(est, yy, mk, ms=3.1, mfc=GALAXY if k == 0 else 'white', mec=GALAXY, mew=0.8)
            ax.text(1.02, yy, fmt(est), transform=ax.get_yaxis_transform(), fontsize=4.9, va='center')
            rows.append(dict(benchmark=BL[b], token_kind=lab, median_ratio=est, ci95_low=lo, ci95_high=hi, complete_cells=n, eligible_cells=elig))
            cell_obs.extend(cells.assign(benchmark=BL[b], token_kind=lab).to_dict('records'))
            put(f'tok_{b}_{col}', f'{fmt(est)} ({fmt(lo)} to {fmt(hi)})')
    ax.axvline(1, color=INK2, lw=0.6, ls=(0, (2, 2)))
    ax.set_xscale('log')
    ax.set_xlim(0.5, 10)
    plain_log(ax, [0.5, 1, 2, 5, 10])
    ax.set_yticks([0, 1.3, 2.6])
    ax.set_yticklabels([BL2[b] for b in BENCHES], fontsize=5.2, linespacing=1.05)
    ax.set_ylim(3.05, -0.45)
    ax.set_xlabel('Median within task × configuration (log; 95% CI)')
    grid_x(ax)
    ax.legend(handles=[Line2D([], [], marker=m, ls='', mfc=GALAXY if k == 0 else 'white', mec=GALAXY, ms=3.2, label=l)
                       for k, (_, l, m) in enumerate(kinds)], loc='upper left', bbox_to_anchor=(-0.45, -0.24), ncol=3, fontsize=5)
    sd['a_tokens'] = pd.DataFrame(rows)
    sd['a_complete_cell_observations'] = pd.DataFrame(cell_obs)
    # ---------------- b: returned text by call class
    panel_label(fig, 0.53, 0.995, 'b')
    panel_title(fig, 0.53, 0.995, 'Interface calls and returned text by call class')
    g = gcalls()
    g['cls'] = g.tool.map(CALL_CLASS).fillna('other')
    classes = [('discovery', 'Tool discovery (search, inspect tool)', OI_SKY), ('inspection', 'History and dataset inspection', OI_GREEN),
               ('execution', 'Execution (run, user-defined tool, wait)', OI_ORANGE), ('staging', 'Staging and other', NEUTRAL_LIGHT)]
    g['cls'] = g.cls.replace({'other': 'staging'})
    ax = fig.add_axes([0.64, 0.62, 0.26, 0.29])
    rows, y = [], 0
    for b in BENCHES:
        x = g[g.benchmark == b]
        for kind, lab_ in [('calls', 'Calls'), ('chars', 'Returned text')]:
            tot = len(x) if kind == 'calls' else x.chars_returned.sum()
            left = 0
            for k, lab, col in classes:
                z = x[x.cls == k]
                v = 100 * (len(z) if kind == 'calls' else z.chars_returned.sum()) / tot
                ax.barh(y, v, left=left, color=col, edgecolor='white', lw=0.4, height=0.7)
                if v > 7:
                    ax.text(left + v / 2, y, fmt(v, 0), ha='center', va='center', fontsize=4.9)
                left += v
                rows.append(dict(benchmark=BL[b], measure=lab_, call_class=lab, percent=v))
                if k == 'discovery':
                    put(f'disc_{kind}_{b}', f'{fmt(v, 0)}%')
            y += 1
        y += 0.6
    ax.set_yticks([0, 1, 2.6, 3.6, 5.2, 6.2])
    ax.set_yticklabels(['Calls', 'Returned text'] * 3, fontsize=5.1)
    for yy, b in zip([-0.62, 1.98, 4.58], BENCHES):
        ax.text(0, yy, BL[b], fontsize=5.3, fontweight='bold', va='center')
    ax.set_ylim(6.8, -1.0)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Share of Galaxy-interface calls or characters (%)')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=c, label=l) for _, l, c in classes], loc='upper left', bbox_to_anchor=(-0.30, -0.22), ncol=2, fontsize=4.8)
    sd['b_call_classes'] = pd.DataFrame(rows)
    # ---------------- c: actions vs tokens
    panel_label(fig, 0.005, 0.44, 'c')
    panel_title(fig, 0.005, 0.44, 'Input tokens and actions per Galaxy run')
    from scipy.stats import spearmanr
    counts = g.groupby(['benchmark', 'task', 'cfg', 'replicate']).size().rename('n_galaxy_interface').reset_index()
    gs = S[(S.env == 'galaxy') & S.has_trace & S.cfg.isin(CONFIGS)].merge(
        counts, on=['benchmark', 'task', 'cfg', 'replicate'], how='left').dropna(subset=['input_tokens', 'n_galaxy_interface', 'n_shell'])
    ax = fig.add_axes([0.08, 0.08, 0.24, 0.27])
    marks = {'BixBench50': 'o', 'CompBio': '^', 'IWC': 's'}
    rows, obs = [], []
    for b in BENCHES:
        x = gs[gs.benchmark == b]
        act = x.n_galaxy_interface + x.n_shell
        ax.scatter(act, x.input_tokens / 1e6, s=2.5, marker=marks[b], c=GALAXY, alpha=0.25, lw=0)
        rho = spearmanr(act, x.input_tokens).statistic
        rows.append(dict(benchmark=BL[b], runs=len(x), spearman_rho=rho))
        obs += [dict(benchmark=BL[b], task=t, cfg=c, replicate=rp, actions=int(a), galaxy_interface_calls=int(gi),
                     shell_commands=int(sh), input_tokens=int(it))
                for t, c, rp, a, gi, sh, it in zip(x.task, x.cfg, x.replicate, act, x.n_galaxy_interface, x.n_shell, x.input_tokens)]
        put(f'rho_{b}', fmt(rho, 2))
    ax.set_xscale('log'), ax.set_yscale('log')
    ax.set_xlim(3, 800), ax.set_ylim(0.05, 200)
    plain_log(ax, [3, 10, 30, 100, 300])
    plain_log(ax, [0.1, 1, 10, 100], axis='y')
    ax.set_xlabel('Galaxy-interface calls + shell commands per run')
    ax.set_ylabel('Input tokens per run (millions)')
    ax.text(0.03, 0.97, '\n'.join(f'{r["benchmark"]}: Spearman {fmt(r["spearman_rho"], 2)}' for r in rows), transform=ax.transAxes,
            fontsize=4.9, va='top', linespacing=1.3)
    ax.legend(handles=[Line2D([], [], marker=marks[b], ls='', mfc=GALAXY, mec='none', ms=3, label=BL[b]) for b in BENCHES],
              loc='lower right', fontsize=4.8, handletextpad=0.2)
    sd['c_correlation'] = pd.DataFrame(rows)
    sd['c_observations'] = pd.DataFrame(obs)
    # ---------------- d: discovery
    panel_label(fig, 0.38, 0.44, 'd')
    panel_title(fig, 0.38, 0.44, 'Tools inspected and later run')
    scan = nc.fd()['scan']
    f = nc.galaxy_failures()
    ax = fig.add_axes([0.48, 0.08, 0.16, 0.27])
    rows = []
    for i, b in enumerate(BENCHES):
        ins, nev = scan['inspected'][b], scan['inspected_never_run'][b]
        ax.barh(i, 100 * (ins - nev) / ins, color=GALAXY, height=0.6)
        ax.barh(i, 100 * nev / ins, left=100 * (ins - nev) / ins, color=ENV_TINT['galaxy'], edgecolor=GALAXY, lw=0.5, height=0.6)
        ax.text(100 * (ins - nev) / ins + 50 * nev / ins, i, f'{fmt(100 * nev / ins, 0)}%', ha='center', va='center', fontsize=4.9)
        guessed = int(((f.benchmark == b) & f.failure_class.str.startswith('A2')).sum())
        ax.text(101, i, f'{ins:,} tools\n{scan["searches"][b]["median"]:.0f} searches/run\n{guessed} identifiers\nnot found',
                fontsize=4.6, va='center', linespacing=1.05, color=INK2)
        rows.append(dict(benchmark=BL[b], tools_inspected=ins, inspected_not_run=nev, median_searches=scan['searches'][b]['median'],
                         max_searches=scan['searches'][b]['max'], identifiers_not_found=guessed))
        put(f'inspect_not_run_{b}', f'{fmt(100 * nev / ins, 0)}%')
    ax.set_yticks(range(3))
    ax.set_yticklabels([BL2[b] for b in BENCHES], fontsize=5, linespacing=1.05)
    ax.set_ylim(2.5, -0.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Distinct inspected tools (%)')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=GALAXY, label='Later run'), Patch(fc=ENV_TINT['galaxy'], ec=GALAXY, lw=0.5, label='Not run')],
              loc='lower left', bbox_to_anchor=(0, 1.0), ncol=2, fontsize=4.8)
    sd['d_discovery'] = pd.DataFrame(rows)
    # ---------------- e: tokens by outcome within task
    panel_label(fig, 0.78, 0.44, 'e')
    panel_title(fig, 0.78, 0.44, 'Tokens of incorrect vs\ncorrect sibling runs')
    w = nc.od(3, 'ab_within_task_test')
    ax = fig.add_axes([0.84, 0.08, 0.13, 0.25])
    rows = []
    for i, e in enumerate(ENVS):
        q = w[w.env == e].iloc[0]
        ax.plot(q.median_ratio, i, ENV_MARKER[e], ms=4, mfc=ENV_COLOR[e], mec='white')
        ax.text(q.median_ratio + 0.06, i, f'{fmt(q.median_ratio, 2)}\nP = {fmt(q.p_two_sided, 2)}\n{int(q.split_replicate_sets)} sets',
                fontsize=4.8, va='center', linespacing=1.05)
        rows.append(dict(env=e, split_replicate_sets=q.split_replicate_sets, median_ratio=q.median_ratio, p_two_sided=q.p_two_sided))
        put(f'sib_tok_{e}', f'{fmt(q.median_ratio, 2)} (P = {fmt(q.p_two_sided, 2)}; {int(q.split_replicate_sets)} sets)')
    ax.axvline(1, color=INK2, lw=0.6, ls=(0, (2, 2)))
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['Code', 'Galaxy'], fontsize=5.1)
    ax.set_ylim(1.6, -0.6)
    ax.set_xlim(0.5, 1.6)
    ax.set_xlabel('Ratio, BixBench-\nVerified-50 (Wilcoxon)')
    grid_x(ax)
    sd['e_within_task_tokens'] = pd.DataFrame(rows)
    nc.save_figure(fig, PAPER, 'Fig4', TITLES['Fig4'])
    nc.source_data(PAPER, 'Fig4', sd, TITLES['Fig4'])


# ---------------------------------------------------------------------------------------------------- Figure 5
BYPASS = [('download', 'Download full datasets', 'permitted'), ('copy_history', 'Copy the seed history', 'permitted'),
          ('tool_schema', 'Fetch tool schemas', 'permitted'), ('job_polling', 'Poll job state', 'permitted'),
          ('raw_submission', 'Submit jobs by raw request\n(skips the parameter check)', 'bypass')]


def fig5():
    fig = new_fig(160)
    sd = {}
    fd = nc.fd()
    scan = fd['scan']
    A = nc.analysis()
    # ---------------- a: shell-side API use
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'Direct Galaxy API use from the shell (Codex traces)')
    rows = []
    for j, b in enumerate(BENCHES):
        ax = fig.add_axes([0.18 + j * 0.10, 0.68, 0.075, 0.24])
        n = scan['codex_galaxy_runs'][b]
        for i, (k, lab, kind) in enumerate(BYPASS):
            v = scan['bypass'][b].get(k)
            if v is None:
                ax.text(3, i, 'not\nmeasured', fontsize=4.6, va='center', color=INK2, linespacing=1.0)
                rows.append(dict(benchmark=BL[b], operation=lab.replace('\n', ' '), kind=kind, runs=None, codex_galaxy_runs=n))
                continue
            ax.barh(i, 100 * v / n, color=CODE if kind == 'bypass' else GALAXY, height=0.62)
            ax.text(100 * v / n + 3, i, f'{fmt(100 * v / n, 0)}%', va='center', fontsize=4.8)
            rows.append(dict(benchmark=BL[b], operation=lab.replace('\n', ' '), kind=kind, runs=v, codex_galaxy_runs=n, percent=100 * v / n))
        ax.set_ylim(len(BYPASS) - 0.4, -0.6)
        ax.set_yticks(range(len(BYPASS)))
        ax.set_yticklabels([x[1] for x in BYPASS] if j == 0 else [], fontsize=5, linespacing=1.05)
        ax.set_xlim(0, 125)
        ax.set_xticks([0, 50, 100])
        share = 100 * scan['api_shell'][b] / scan['all_shell'][b]
        ax.set_title(f'{BL2[b]}\n{fmt(share, 0)}% of shell\ncommands', fontsize=5, loc='left', linespacing=1.05)
        grid_x(ax)
        if j == 1:
            ax.set_xlabel('Galaxy-condition runs (%)')
        put(f'api_shell_{b}', f'{fmt(share, 0)}%')
    put('raw_post_runs', str(sum(scan['bypass'][b].get('raw_submission', 0) for b in BENCHES)))
    sd['a_shell_api'] = pd.DataFrame(rows)
    # ---------------- b: run-level attribution coverage
    panel_label(fig, 0.53, 0.995, 'b')
    panel_title(fig, 0.53, 0.995, 'Run-level coverage of where computation happened')
    rows = []
    cls_rows = []
    for r in A['runs']:
        if r['condition'] != 'galaxy':
            continue
        cov = r.get('coverage') or {}
        hist = cov.get('public_history_contents') == 'retrieved'
        ind = bool(r.get('software_command_indicators'))
        cls = 'No detailed history' if not hist else ('History; shell named an\nanalysis program (location uncertain)' if ind else
                                                      'History; no analysis program\nnamed in the shell')
        cls_rows.append(dict(benchmark=r['benchmark'], task=r['task'], run_id=r['run_id'], cfg=nc.CFG[r['model']], category=cls.replace('\n', ' ')))
    cr = pd.DataFrame(cls_rows)
    cats = [('History; no analysis program named in the shell', NEUTRAL_LIGHT), ('History; shell named an analysis program (location uncertain)', OI_SKY),
            ('No detailed history', NEUTRAL_DARK)]
    ax = fig.add_axes([0.64, 0.74, 0.26, 0.16])
    for i, b in enumerate(BENCHES):
        x = cr[cr.benchmark == b]
        left = 0
        for k, col in cats:
            v = 100 * (x.category == k).mean()
            ax.barh(i, v, left=left, color=col, edgecolor='white', lw=0.4, height=0.62)
            if v > 6:
                ax.text(left + v / 2, i, fmt(v, 0), ha='center', va='center', fontsize=4.9, color='white' if col == NEUTRAL_DARK else INK)
            left += v
            rows.append(dict(benchmark=BL[b], category=k, runs=int((x.category == k).sum()), total=len(x), percent=v))
        put(f'attest_{b}', f'{fmt(100 * (x.category == cats[0][0]).mean(), 0)}%')
    ax.set_yticks(range(3))
    ax.set_yticklabels([BL2[b] for b in BENCHES], fontsize=5, linespacing=1.05)
    ax.set_ylim(2.5, -0.5)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Galaxy-condition runs (%)')
    grid_x(ax)
    ax.legend(handles=[Patch(fc=c, label=k) for k, c in cats], loc='upper left', bbox_to_anchor=(-0.35, -0.40), ncol=1, fontsize=4.8)
    integ = fd['integrity']
    put('local_answers', str(len(integ['local_fallback_correct']) + len(integ['local_fallback_incorrect'])))
    put('cross_run', str(len(integ['cross_run'])))
    fig.text(0.555, 0.60, f"Confirmed in the targeted audit: {len(integ['local_fallback_correct']) + len(integ['local_fallback_incorrect'])} answers computed locally;\n"
             f"{len(integ['cross_run'])} copied across runs via the shared account", fontsize=4.8, va='top', color=INK2)
    sd['b_location_coverage'] = pd.DataFrame(rows)
    sd['b_run_categories'] = cr
    # ---------------- c: user-defined tool requests
    panel_label(fig, 0.005, 0.47, 'c')
    panel_title(fig, 0.005, 0.47, 'Agent-written code inside the boundary: user-defined tool requests')
    cmap = {'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro', 'DeepSeek V4 Pro 0813 (Codex)': 'DeepSeek V4 Pro',
            'DeepSeek V4 Pro (Claude Code, superseded)': SUPERSEDED}
    labs = CONFIGS + [SUPERSEDED]
    ax = fig.add_axes([0.20, 0.08, 0.22, 0.32])
    rows = []
    for r in fd['fig3c']:
        c = cmap.get(r['config'], r['config'])
        if c not in labs or r['benchmark'] == 'IWC':
            continue
        n, d = r['requesting']
        mk = 'o' if r['benchmark'] == 'BixBench50' else '^'
        ax.plot(100 * n / d, labs.index(c), mk, ms=3.6, mfc=GALAXY if mk == 'o' else 'white', mec=GALAXY, mew=0.8)
        rows.append(dict(benchmark=BL[r['benchmark']], cfg=c, requesting_runs=n, galaxy_runs=d, percent=100 * n / d))
        UDT_REQ.setdefault((r['benchmark'], c in CONFIGS), []).append(100 * n / d)
    ax.set_ylim(len(labs) - 0.4, -0.6)
    ax.set_yticks(range(len(labs)))
    ax.set_yticklabels([CFG_SHORT[c] for c in labs], fontsize=5.1, linespacing=1.05)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Galaxy-condition runs requesting\na user-defined tool (%)')
    grid_x(ax)
    ax.legend(handles=[Line2D([], [], marker='o', ls='', mfc=GALAXY, mec=GALAXY, ms=3.4, label='BixBench-Verified-50'),
                       Line2D([], [], marker='^', ls='', mfc='white', mec=GALAXY, ms=3.6, label='CompBioBench')], loc='lower right', fontsize=4.8)
    sd['c_udt_requests'] = pd.DataFrame(rows)
    for b in ['BixBench50', 'CompBio']:
        v = UDT_REQ[(b, True)]
        put(f'udt_req_{b}', f'{fmt(min(v), 0)}% to {fmt(max(v), 0)}%')
    # ---------------- d: user-defined tool outcomes and accuracy
    panel_label(fig, 0.53, 0.47, 'd')
    panel_title(fig, 0.53, 0.47, 'User-defined tool calls and final benchmark outcomes')
    g = gcalls()
    u = g[g.tool == 'run_galaxy_udt_and_wait']
    ax = fig.add_axes([0.66, 0.30, 0.24, 0.10])
    rows = []
    for i, b in enumerate(['BixBench50', 'CompBio']):
        x = u[u.benchmark == b]
        okp = 100 * (x.result_status == 'ok').mean()
        ax.barh(i, okp, color=GALAXY, height=0.6)
        ax.barh(i, 100 - okp, left=okp, color=OI_ORANGE, height=0.6)
        ax.text(okp / 2, i, f'{fmt(okp, 0)}% ok', ha='center', va='center', fontsize=4.9, color='white')
        ax.text(101, i, f'{len(x):,} calls', va='center', fontsize=4.8, color=INK2)
        rows.append(dict(benchmark=BL[b], udt_calls=len(x), returned_ok=int((x.result_status == 'ok').sum()), percent_ok=okp))
        put(f'udt_ok_{b}', f'{fmt(okp, 0)}%')
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['BixBench-Verified-50', 'CompBioBench'], fontsize=5)
    ax.set_ylim(1.6, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel('User-defined tool calls (%)')
    sd['d_udt_calls'] = pd.DataFrame(rows)
    tr = nc.od(7, 'b_accuracy_by_udt_trajectory')
    order = ['No UDT requested', 'UDT requested; a UDT job succeeded', 'UDT requested; every UDT job failed']
    names = {order[0]: 'No user-defined tool', order[1]: 'A user-defined tool job succeeded', order[2]: 'Every user-defined tool job failed'}
    ax = fig.add_axes([0.66, 0.08, 0.24, 0.15])
    rows = []
    y = 0
    for b in ['BixBench50', 'CompBio']:
        for t in order:
            q = tr[(tr.benchmark == b) & (tr.trajectory == t)].iloc[0]
            if q.runs >= 5:
                ax.barh(y, q.percent_correct, color=GALAXY, height=0.66)
                ax.text(q.percent_correct + 1, y, f'{fmt(q.percent_correct, 0)}% (n = {int(q.runs)})', va='center', fontsize=4.8)
            else:
                ax.text(1, y, f'{int(q.runs)} runs (too few)', va='center', fontsize=4.8, color=INK2)
            rows.append(dict(benchmark=BL[b], trajectory=names[t], runs=int(q.runs), percent_correct=q.percent_correct))
            put(f'udt_traj_{b}_{order.index(t)}', f'{fmt(q.percent_correct, 0)}% (n = {int(q.runs)})')
            y += 1
        y += 0.5
    ax.set_yticks([0, 1, 2, 3.5, 4.5, 5.5])
    ax.set_yticklabels([f'{"BixBench" if i < 3 else "CompBio"}: {names[t]}' for i, t in enumerate(order * 2)], fontsize=4.8)
    ax.set_ylim(6.0, -0.6)
    ax.set_xlim(0, 125)
    ax.set_xticks([0, 50, 100])
    ax.set_xlabel('Accepted benchmark outcomes (%)')
    grid_x(ax)
    sd['d_udt_trajectories'] = pd.DataFrame(rows)
    nc.save_figure(fig, PAPER, 'Fig5', TITLES['Fig5'])
    nc.source_data(PAPER, 'Fig5', sd, TITLES['Fig5'])


# ---------------------------------------------------------------------------------------------------- Figure 6
REQ = [
    ('Bind parameters strictly and\nreturn what will run', 'Run calls with a recorded\nparameter mismatch', 'Reject unbound keys; return the\nresolved state before submission'),
    ('Explain every failure in a\nstructured form', 'Failed jobs with no diagnostic\nindicator in returned excerpt', 'Return phase, message and excerpt\nfor every failed job'),
    ('Expose versions and output\nsemantics as tool metadata', 'No systematic baseline;\nfive mechanism case studies', 'Add versions and per-output\ndefinitions to search and inspect'),
    ('Make discovery compact and\ncontext-free', 'Returned text spent on\ndiscovery', 'Ranked tool cards; schemas\nwithout a history'),
    ('Cover the analysis life cycle\nin the agent interface', 'Shell commands calling the\nGalaxy API directly', 'History copy, full download and\nresumable waits in the interface'),
    ('Attest where computation ran\nand isolate runs', 'History coverage and\nlocation-uncertain cases (Fig. 5)', 'Per-run accounts; execution-\nlocation record in the history'),
]


def readiness_measures():
    g = gcalls()
    fd = nc.fd()
    scan, inv = fd['scan'], fd['inventory']
    f = nc.galaxy_failures()
    tr = g[g.tool == 'run_galaxy_tool_and_wait'].copy()
    tr['fid'] = tr.apply(fidelity_class, axis=1)
    jf = g[g.any_job_error == True]  # noqa: E712
    out = []
    out.append(('Run calls whose requested and resolved\nparameters were compared and matched', 'higher',
                {b: 100 * (tr[tr.benchmark == b].fid == 'ok_checked').mean() for b in BENCHES}))
    out.append(('Run calls with a recorded\nparameter mismatch', 'lower',
                {b: 100 * tr[tr.benchmark == b].prov_status.eq('mismatch').mean() for b in BENCHES}))
    out.append(('Galaxy-interface calls that failed', 'lower', {b: 100 * (f.benchmark == b).sum() / (g.benchmark == b).sum() for b in BENCHES}))
    out.append(('Failed jobs with no diagnostic\nindicator in returned excerpt', 'lower',
                {b: 100 * (~jf[jf.benchmark == b].error_excerpt.fillna('').str.contains(DIAG_RX, regex=True)).mean() for b in BENCHES}))
    gg = g.assign(cls=g.tool.map(CALL_CLASS))
    out.append(('Returned text spent on tool discovery', 'lower',
                {b: 100 * gg[(gg.benchmark == b) & (gg.cls == 'discovery')].chars_returned.sum() / gg[gg.benchmark == b].chars_returned.sum()
                 for b in BENCHES}))
    out.append(('Shell commands calling the\nGalaxy API directly', 'lower', {b: 100 * scan['api_shell'][b] / scan['all_shell'][b] for b in BENCHES}))
    out.append(('Runs with a detailed analysis history', 'higher',
                {b: 100 * inv[b]['detailed_histories'][0] / inv[b]['detailed_histories'][1] for b in BENCHES}))
    u = g[g.tool == 'run_galaxy_udt_and_wait']
    out.append(('User-defined tool calls returning "ok"', 'higher',
                {b: 100 * (u[u.benchmark == b].result_status == 'ok').mean() for b in ['BixBench50', 'CompBio']}))
    return out


def fig6():
    fig = new_fig(150)
    sd = {}
    mets = readiness_measures()
    panel_label(fig, 0.005, 0.995, 'a')
    panel_title(fig, 0.005, 0.995, 'Baseline measures (Galaxy condition; arrows: direction of improvement)')
    ax = fig.add_axes([0.25, 0.52, 0.40, 0.42])
    marks = {'BixBench50': 'o', 'CompBio': '^', 'IWC': 's'}
    rows = []
    for i, (lab, direction, vals) in enumerate(mets):
        for b, v in vals.items():
            ax.plot(v, i, marks[b], ms=3.6, mfc=GALAXY, mec='white', mew=0.3, ls='')
            rows.append(dict(measure=lab.replace('\n', ' '), better=direction, benchmark=BL[b], percent=v))
        lo, hi = min(vals.values()), max(vals.values())
        ax.plot([lo, hi], [i, i], color=GALAXY, lw=0.6, zorder=0)
        ax.annotate('', xy=(100 if direction == 'higher' else 0, i), xytext=(hi if direction == 'higher' else lo, i),
                    arrowprops=dict(arrowstyle='-|>', lw=0.5, color=NEUTRAL_MID, ls=(0, (2, 2)), mutation_scale=5))
        ax.text(1.02, i, ', '.join(fmt(v, 0) for v in vals.values()), transform=ax.get_yaxis_transform(), fontsize=4.9, va='center')
    ax.set_yticks(range(len(mets)))
    ax.set_yticklabels([m[0] for m in mets], fontsize=5, linespacing=1.05)
    ax.set_ylim(len(mets) - 0.4, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel('Percent')
    grid_x(ax)
    ax.legend(handles=[Line2D([], [], marker=marks[b], ls='', mfc=GALAXY, mec='white', ms=3.6, label=BL[b]) for b in BENCHES],
              loc='upper left', bbox_to_anchor=(1.15, 1.0), fontsize=5, title='Values at right in\nbenchmark order', title_fontsize=4.9,
              alignment='left')
    sd['a_baseline'] = pd.DataFrame(rows)
    keys = ['checked_matched', 'unbound', 'failed_calls', 'notext', 'discovery_text', 'shell_api', 'history', 'udt_ok']
    for key, (_, _, vals) in zip(keys, mets):
        put(f'base_{key}', ', '.join(f'{fmt(v, 0)}%' for v in vals.values()))
    # ---------------- b: requirements
    panel_label(fig, 0.005, 0.44, 'b')
    panel_title(fig, 0.005, 0.44, 'Requirements motivated by the audit, their baseline measure and the intervention needed to validate them')
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.38])
    ax.axis('off')
    cols = ['Requirement', 'Baseline or supporting evidence', 'Intervention to test on held-out tasks']
    xs = [0.0, 0.30, 0.60]
    for x, c in zip(xs, cols):
        ax.text(x, 0.99, c, fontsize=5.4, fontweight='bold', va='top', transform=ax.transAxes)
    ax.plot([0, 1], [0.92, 0.92], color=INK2, lw=0.5, transform=ax.transAxes, clip_on=False)
    rows = []
    for i, (req, meas, inter) in enumerate(REQ):
        y = 0.88 - i * 0.145
        for x, t in zip(xs, (req, meas, inter)):
            ax.text(x, y, t, fontsize=5.1, va='top', transform=ax.transAxes, linespacing=1.12)
        rows.append(dict(requirement=req.replace('\n', ' '), baseline_measure=meas.replace('\n', ' '), intervention=inter.replace('\n', ' ')))
    ax.text(0.0, 0.0, 'None of these interventions was tested in this study. Measures describe archived adapter deployments on one server, '
            'July to September 2026.', fontsize=4.9, color=INK2, transform=ax.transAxes, va='bottom')
    sd['b_requirements'] = pd.DataFrame(rows)
    nc.save_figure(fig, PAPER, 'Fig6', TITLES['Fig6'])
    nc.source_data(PAPER, 'Fig6', sd, TITLES['Fig6'])


# ---------------------------------------------------------------------------------------------------- Extended Data
def save_ed(fig, name, sheets):
    nc.save_figure(fig, PAPER, name, TITLES[name])
    nc.source_data(PAPER, name, sheets, TITLES[name])


def figed():
    fd = nc.fd()
    # ---------------- ED1: capabilities
    fig = new_fig(55)
    ops = fd['fig3a']
    names = {'Tool discovery': 'Tool discovery', 'Parameter/schema inspection': 'Tool parameter inspection', 'History inspection': 'History inspection',
             'Ordinary-tool submission requests': 'Installed-tool submission', 'User-defined-tool submission requests': 'User-defined tool submission',
             'Explicit waiting/status requests': 'Explicit waiting for jobs'}
    ax = fig.add_axes([0.25, 0.08, 0.40, 0.78])
    rows = []
    for i, o in enumerate(ops):
        for j, (n, d) in enumerate(o['values']):
            v = 100 * n / d
            ax.add_patch(Rectangle((j, i - 0.5), 1, 1, fc=GALAXY, alpha=0.08 + 0.75 * v / 100, ec='white', lw=0.8))
            lab = 'not offered' if (BENCHES[j] == 'IWC' and 'User-defined' in o['operation']) else f'{fmt(v, 0)}%'
            ax.text(j + 0.5, i, lab, ha='center', va='center', fontsize=5.1, color='white' if v > 60 else INK)
            rows.append(dict(operation=names[o['operation']], benchmark=BL[BENCHES[j]], runs=n, galaxy_runs=d, percent=v))
    ax.set_xlim(0, 3), ax.set_ylim(len(ops) - 0.5, -0.5)
    ax.set_yticks(range(len(ops)))
    ax.set_yticklabels([names[o['operation']] for o in ops], fontsize=5.2)
    ax.set_xticks([0.5, 1.5, 2.5])
    ax.set_xticklabels([BL[b] for b in BENCHES], fontsize=5.2)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.text(1.03, 0.5, 'Share of Galaxy-condition runs that made\nat least one call of each kind', transform=ax.transAxes, fontsize=5, color=INK2)
    save_ed(fig, 'ED_Fig1', {'capabilities': pd.DataFrame(rows)})
    # ---------------- ED2: interaction styles
    fig = new_fig(55)
    s_ = nc.summaries()
    s_ = s_[(s_.benchmark == 'BixBench50') & (s_.env == 'galaxy') & s_.has_trace]
    gc = gcalls()
    cnt = gc.groupby(['benchmark', 'task', 'cfg', 'replicate']).size().rename('n_galaxy_interface').reset_index()
    fail = nc.galaxy_failures().merge(gc[['benchmark', 'task', 'run_id', 'line', 'replicate']],
                                    on=['benchmark', 'task', 'run_id', 'line'], how='left', validate='one_to_one')
    nf = fail.groupby(['benchmark', 'task', 'cfg', 'replicate']).size().rename('n_failed_galaxy_interface').reset_index()
    s_ = s_.merge(cnt, on=['benchmark', 'task', 'cfg', 'replicate'], how='left').merge(
        nf, on=['benchmark', 'task', 'cfg', 'replicate'], how='left').fillna({'n_failed_galaxy_interface': 0})
    skill, core = fd['skill_uptake'], fd['core_library_accuracy']
    cmap = {'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro', 'DeepSeek V4 Pro (Claude Code, superseded)': SUPERSEDED}
    udt = {cmap.get(r['config'], r['config']): 100 * r['requesting'][0] / r['requesting'][1] for r in fd['fig3c'] if r['benchmark'] == 'BixBench50'}
    labs = CONFIGS + [SUPERSEDED]
    cols = [('Galaxy-interface calls\nper run (median)', lambda c: s_[s_.cfg == c].n_galaxy_interface.median(), '{:.0f}'),
            ('Failed Galaxy-interface\ncalls (%)', lambda c: 100 * s_[s_.cfg == c].n_failed_galaxy_interface.sum() / s_[s_.cfg == c].n_galaxy_interface.sum(), '{:.1f}'),
            ('Input tokens per run\n(median, millions)', lambda c: s_[s_.cfg == c].input_tokens.median() / 1e6, '{:.1f}'),
            ('User-defined tool\nrequested (% runs)', lambda c: udt.get(c), '{:.0f}'),
            ('Relevant skill opened\n(% of 114 runs)', lambda c: 100 * skill[f'{c}|galaxy'][0] / skill[f'{c}|galaxy'][1], '{:.0f}'),
            ('Interface library\nscripted (runs)', lambda c: core[c]['scripted'] if c in core else None, '{:.0f}')]
    ax = fig.add_axes([0.24, 0.05, 0.70, 0.70])
    vals = np.array([[f(c) if f(c) is not None else np.nan for _, f, _ in cols] for c in labs], dtype=float)
    rows = []
    for jj, (lab, f, fm) in enumerate(cols):
        col = vals[:, jj]
        lo, hi = np.nanmin(col), np.nanmax(col)
        for i, c in enumerate(labs):
            v = vals[i, jj]
            a = 0.08 + 0.7 * ((v - lo) / (hi - lo) if hi > lo and not np.isnan(v) else 0)
            ax.add_patch(Rectangle((jj, i - 0.5), 1, 1, fc=GALAXY, alpha=a if not np.isnan(v) else 0, ec='white', lw=0.8))
            ax.text(jj + 0.5, i, 'not recorded' if np.isnan(v) else fm.format(v), ha='center', va='center', fontsize=5, color='white' if a > 0.55 else INK)
    for i, c in enumerate(labs):
        rows.append(dict(cfg=c, **{cols[jj][0].replace('\n', ' '): vals[i, jj] for jj in range(len(cols))}))
    ax.set_xlim(0, len(cols)), ax.set_ylim(len(labs) - 0.5, -0.5)
    ax.set_yticks(range(len(labs)))
    ax.set_yticklabels([CFG_SHORT[c].replace('\n', ' ') for c in labs], fontsize=5.1)
    ax.set_xticks([jj + 0.5 for jj in range(len(cols))])
    ax.set_xticklabels([c[0] for c in cols], fontsize=5, linespacing=1.05)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    for sp in ax.spines.values():
        sp.set_visible(False)
    save_ed(fig, 'ED_Fig2', {'interaction_styles': pd.DataFrame(rows)})
    # ---------------- ED3: user-defined tool outcomes
    g = gcalls()
    u = g[g.tool == 'run_galaxy_udt_and_wait'].copy()
    fig = new_fig(70)
    ax = fig.add_axes([0.20, 0.34, 0.45, 0.58])
    sts = u.result_status.fillna('none').value_counts()
    order = list(sts.index)
    status_colors = [GALAXY, OI_ORANGE, OI_SKY, OI_PURPLE, OI_GREEN, NEUTRAL_MID, NEUTRAL_LIGHT, NEUTRAL_DARK, GRID]
    st_label = {'ok': 'Job ran ("ok")', 'failed': 'Job failed', 'none': 'No status returned (call failed)',
                'udt_creation_failed': 'Tool definition rejected', 'submission_failed': 'Submission failed', 'timeout': 'Wait timed out',
                'dataset_error': 'Input dataset error', 'workspace_staging_failed': 'Workspace staging failed'}
    rows = []
    for i, b in enumerate(['BixBench50', 'CompBio']):
        x = u[u.benchmark == b]
        left = 0
        for k, st in enumerate(order):
            v = 100 * (x.result_status.fillna('none') == st).mean()
            col = status_colors[k % len(status_colors)]
            ax.barh(i, v, left=left, color=col, edgecolor='white', lw=0.4, height=0.6)
            if v > 6:
                ax.text(left + v / 2, i, fmt(v, 0), ha='center', va='center', fontsize=4.9, color='white' if k in (0,) else INK)
            left += v
            rows.append(dict(benchmark=BL[b], status=st, calls=int((x.result_status.fillna('none') == st).sum()), total=len(x), percent=v))
    ax.set_yticks([0, 1])
    ax.set_yticklabels(['BixBench-Verified-50', 'CompBioBench'], fontsize=5.2)
    ax.set_ylim(1.6, -0.6)
    ax.set_xlim(0, 100)
    ax.set_xlabel('User-defined tool calls by returned status (%)')
    ax.legend(handles=[Patch(fc=status_colors[k % len(status_colors)], label=st_label.get(st, st))
                       for k, st in enumerate(order)], loc='upper left', bbox_to_anchor=(1.02, 1.0), fontsize=4.9)
    for r in rows:
        r['status_label'] = st_label.get(r['status'], r['status'])
    summ = json.load(open(os.path.join(nc.NARR, 'derived', 'galaxy_calls', 'summary.json')))
    og = summ['per_benchmark']['CompBio']['failed_udt_outage_signature']
    fig.text(0.02, 0.03, f"CompBioBench server-side signal: {og['in_runs_whose_trace_contains_signature']:,} of {og['failed_udt_calls']:,} failed "
             f"user-defined-tool calls occurred in the {og['runs_whose_trace_contains_signature']} runs whose trace contains the message that no "
             f"execution destination was available;\n{og['linked_to_shell_signature_by_job_or_dataset_id']:,} were linked to that message by job or "
             'dataset identifier. The message never appeared in the text the interface returned to the agent.', fontsize=4.9, color=INK2,
             va='bottom', linespacing=1.25)
    put('outage_udt_in_runs', f"{og['in_runs_whose_trace_contains_signature']:,} of {og['failed_udt_calls']:,}")
    put('outage_runs', str(og['runs_whose_trace_contains_signature']))
    put('outage_linked', f"{og['linked_to_shell_signature_by_job_or_dataset_id']:,}")
    save_ed(fig, 'ED_Fig3', {'udt_status': pd.DataFrame(rows),
                             'outage_signature_compbio': pd.DataFrame([dict(measure=k, value=v) for k, v in og.items()])})


if __name__ == '__main__':
    nc.outdirs(PAPER)
    for w in sys.argv[1:] or ['1', '2', '3', '4', '5', '6', 'ed']:
        globals()[f'fig{w}']()
        print('Fig', w, 'done')
    save_numbers(partial=bool(sys.argv[1:]))
