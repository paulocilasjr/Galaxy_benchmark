"""On-demand figures (not part of the submitted display items) and their Source Data.

Run from the repository root:  COMPBIO_KEY_DIR=<folder> python manuscript_material/scripts/fig_on_demand.py
Writes to manuscript_material/on_demand/:
  OD_Fig1  primary cause of every scored-incorrect run, by how many of the three replicate runs were scored incorrect
  OD_Fig2  unanimous accuracy (3/3 replicate runs scored correct) per model configuration, open-ended code then Galaxy
  OD_Fig3  input-token usage per run, scored-correct versus scored-incorrect, per model configuration and condition
  OD_Fig4  majority-vote accuracy per model configuration and condition: pooled (a) and by benchmark (b)
  OD_Fig5  execution errors by type and recovery (the run still ended correct), per benchmark (a IWC, b BixBench, c CompBioBench)
  OD_Fig6  actions (tool calls) per run from start to end of a task, per benchmark (a IWC, b BixBench, c CompBioBench)
  OD_Fig7  user-defined tools (UDTs) and accuracy: association within task, outcomes of UDT runs, and where the error
           happened in scored-incorrect UDT runs (trace-level audit in on_demand/udt_audit/)
Figs 1-3 use BixBench-Verified-50 only. Inputs are the archived files build_data.py reads (analysis.json, the failure
ledger, run_summaries.jsonl.gz); figure_data.json is not changed. All five BixBench model configurations are pooled where
pooling is needed, as in Fig. 4b. Figs 4-5 also grade CompBioBench runs against the lab's score-inferred answer key, read
from COMPBIO_KEY_DIR (kept outside this repository so that agents run from it cannot read the key).
"""
import collections
import gzip
import json
import os
import re
import statistics as st
import sys
import textwrap

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(__file__))
from style import (CFG_LABEL, CONFIGS, ENV_COLOR, ENV_LABEL, ENV_LABEL_LONG, ENV_MARKER, ENV_TINT, ENVS, GALAXY, GRID, INK, INK2, MM,  # noqa: E402
                   NEUTRAL_LIGHT, NEUTRAL_MID, OI_ORANGE, SUPERSEDED, W_DOUBLE, enforce_min_font, grid_x, grid_y, panel_label, panel_title, plt)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'manuscript_material', 'on_demand')
V2 = os.path.join(ROOT, 'analysis_reports', 'galaxy_improvement_20260924', 'v2_trace_friction')

MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
         'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'deepseek_v4_pro_via_claude_code_superseded': SUPERSEDED}
LEDGER_SHORT = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'Sol', 'codex_gpt_5_6_luna': 'Luna',
                'deepseek_v4_pro_via_codex': 'DS-Codex', 'deepseek_v4_pro_via_claude_code_superseded': 'DS-ClaudeCode'}
CFG5 = CONFIGS + [SUPERSEDED]
ROW = {c: CFG_LABEL[c].replace('\n', ' ') for c in CFG5}
ROW[SUPERSEDED] = 'DeepSeek V4 Pro (Claude\nCode, superseded)'
TICK3 = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6\nSol', 'GPT-5.6 Luna': 'GPT-5.6\nLuna', 'DeepSeek V4 Pro': 'DeepSeek V4\nPro (Codex)',
         SUPERSEDED: 'DeepSeek V4 Pro\n(Claude Code,\nsuperseded)'}
# The seven failure-ledger categories, in the order used by Supplementary Table 14e (make_supplement.CAUSE_NAME)
CAUSES = [('SPEC', 'Task under-specified or\nreference ambiguous'), ('RIGOR', 'Statistical or reasoning error'),
          ('EVALUATOR', 'Evaluator rejected a\ncorrect answer'), ('KNOWLEDGE', 'Missing domain knowledge'),
          ('HARNESS', 'No answer submitted'), ('PLATFORM', 'Platform or tool defect\n(Galaxy or local software)'),
          ('CONTRACT', 'Output format violated')]

A = json.load(open(os.path.join(ROOT, 'BixBench50_CompBio_analysis', 'analysis.json')))
RUNS = [r for r in A['runs'] if r['benchmark'] == 'BixBench50']
SUMS = {(s['task'], s['run_id']): s for s in map(json.loads, gzip.open(
    os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt')) if s['benchmark'] == 'BixBench50'}
LEDGER = {(x['task'], x['run']): x for x in json.load(open(os.path.join(V2, 'ledger.json'))) if x['b'] == 'BixBench'}

SETS = collections.defaultdict(list)  # replicate set: task x model configuration x execution condition
for r in RUNS:
    r = dict(r, config=MODEL[r['model']], correct=r['score'] == 1, input_tokens=SUMS[(r['task'], r['run_id'])]['input_tokens'],
             ledger_run=f"{'G' if r['condition'] == 'galaxy' else 'C'} {LEDGER_SHORT[r['model']]} r{r['replicate']}")
    if not r['correct']:
        r['cause'] = LEDGER[(r['task'], r['ledger_run'])]['p']
    SETS[(r['task'], r['config'], r['condition'])].append(r)
assert len(SETS) == 500 and all(len(v) == 3 for v in SETS.values())
assert sum(not r['correct'] for v in SETS.values() for r in v) == len(LEDGER) == 246


def save(fig, name, title):
    enforce_min_font(fig)
    fig.savefig(os.path.join(OUT, f'{name}.pdf'), metadata={'Title': title})
    fig.savefig(os.path.join(OUT, f'{name}.png'), dpi=300)
    plt.close(fig)


def source_data(name, sheets):
    with pd.ExcelWriter(os.path.join(OUT, f'Source_Data_{name}.xlsx'), engine='openpyxl') as xw:
        for sheet, df in sheets.items():
            df.to_excel(xw, sheet_name=sheet[:31], index=False)


def signed(x, nd=1):
    s = f'{x:.{nd}f}'
    return '0.0' if float(s) == 0 else ('+' + s if x > 0 else s.replace('-', '−'))


# =====================================================================================================
def od_fig1():
    """Primary cause of the scored-incorrect runs in replicate sets with 1, 2 and 3 of 3 runs scored incorrect."""
    groups = {(k, e): [] for k in (1, 2, 3) for e in ENVS}
    nsets = collections.Counter()
    for (task, cfg, env), rs in SETS.items():
        k = sum(not r['correct'] for r in rs)
        if k:
            nsets[(k, env)] += 1
            groups[(k, env)] += [r for r in rs if not r['correct']]
    fig = plt.figure(figsize=(W_DOUBLE, 88 * MM))
    titles = {1: 'One of three replicate runs scored\nincorrect: mostly statistical or\nreasoning errors',
              2: 'Two of three replicate runs scored\nincorrect: causes were mixed',
              3: 'All three replicate runs scored\nincorrect: mostly under-specified\ntasks or evaluator rejections'}
    x0s, w, y0, h = [0.205, 0.475, 0.745], 0.225, 0.215, 0.60
    rows, runs_rows = [], []
    for i, k in enumerate((1, 2, 3)):
        ax = fig.add_axes([x0s[i], y0, w, h])
        lx = 0.005 if i == 0 else x0s[i] - 0.03
        panel_label(fig, lx, 0.99, 'abc'[i]); panel_title(fig, lx, 0.99, titles[k])
        fig.text(lx + 0.018, 0.878, '\n'.join(f"{ENV_LABEL[e]}: {len(groups[(k, e)])} runs in {nsets[(k, e)]} replicate sets" for e in ENVS),
                 fontsize=5.0, color=INK2, va='top', linespacing=1.3)
        for j, (key, name) in enumerate(CAUSES):
            for e, dy in zip(ENVS, (-0.19, 0.19)):
                n, tot = sum(r['cause'] == key for r in groups[(k, e)]), len(groups[(k, e)])
                pct = 100 * n / tot
                if n:
                    ax.barh(j + dy, pct, height=0.36, color=ENV_COLOR[e], lw=0)
                ax.text(pct + 1.2, j + dy, str(n), va='center', ha='left', fontsize=5.0, color=INK if n else INK2)
                rows.append(dict(scored_incorrect_replicate_runs_in_set=f'{k} of 3', execution_condition=ENV_LABEL_LONG[e],
                                 primary_cause=name.replace('\n', ' '), scored_incorrect_runs=n, total_scored_incorrect_runs=tot,
                                 percent=round(pct, 1), replicate_sets=nsets[(k, e)]))
        ax.set_yticks(range(len(CAUSES)))
        ax.set_yticklabels([n for _, n in CAUSES] if i == 0 else [], fontsize=5.3, linespacing=1.05)
        ax.tick_params(axis='y', length=0)
        ax.set_ylim(len(CAUSES) - 0.45, -0.55); ax.set_xlim(0, 100); ax.set_xticks(range(0, 101, 25))
        ax.set_xlabel('Share of scored-incorrect runs (%);\nnumber of runs at bar end'); grid_x(ax)
        for e in ENVS:
            for r in groups[(k, e)]:
                runs_rows.append(dict(scored_incorrect_replicate_runs_in_set=f'{k} of 3', execution_condition=ENV_LABEL_LONG[e],
                                      model_configuration=ROW[r['config']].replace('\n', ' '), task=r['task'], replicate=r['replicate'],
                                      answer=r['answer'], primary_cause=dict(CAUSES)[r['cause']].replace('\n', ' '),
                                      secondary_cause=LEDGER[(r['task'], r['ledger_run'])]['s'],
                                      decision_point=LEDGER[(r['task'], r['ledger_run'])]['d'],
                                      adjudication_confidence=LEDGER[(r['task'], r['ledger_run'])]['c']))
    fig.legend(handles=[Patch(fc=ENV_COLOR[e], label=ENV_LABEL_LONG[e]) for e in ENVS], loc='lower left', bbox_to_anchor=(0.005, 0.005),
               ncol=1, fontsize=5.3)
    tot = {e: sum(len(groups[(k, e)]) for k in (1, 2, 3)) for e in ENVS}
    note = (f"BixBench-Verified-50, all five model configurations pooled (250 replicate sets per condition, as in Fig. 4b). Every "
            f"scored-incorrect run ({tot['open_ended_code']} open-ended code, {tot['galaxy']} Galaxy) carries one primary cause from the "
            f"failure ledger (Supplementary Table 14e). Replicate sets with no scored-incorrect run are not shown.")
    fig.text(0.205, 0.075, textwrap.fill(note, 165), fontsize=5.0, color=INK2, va='top', linespacing=1.25)
    save(fig, 'OD_Fig1_error_types_by_incorrect_replicates',
         'Primary cause of scored-incorrect runs by the number of replicate runs scored incorrect (BixBench-Verified-50)')
    source_data('OD_Fig1', {'abc_primary_cause_shares': pd.DataFrame(rows), 'abc_scored_incorrect_runs': pd.DataFrame(runs_rows)})
    return rows


# =====================================================================================================
def od_fig2(n_boot=20000, seed=20260929):
    """Unanimous accuracy per model configuration, with a cluster-bootstrap interval on the condition difference."""
    unan = {(t, c, e): all(r['correct'] for r in rs) for (t, c, e), rs in SETS.items()}
    cluster = {r['task']: r['cluster'] for r in RUNS}
    clusters = sorted(set(cluster.values()))
    tasks_of = {cl: [t for t in sorted(cluster) if cluster[t] == cl] for cl in clusters}
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(clusters), size=(n_boot, len(clusters)))

    def diff_ci(cfgs):
        # per cluster: tasks, and unanimous-set counts in each condition; resample source capsules with replacement
        n_t = np.array([len(tasks_of[cl]) for cl in clusters])
        g = np.array([sum(unan[(t, c, 'galaxy')] for t in tasks_of[cl] for c in cfgs) for cl in clusters])
        o = np.array([sum(unan[(t, c, 'open_ended_code')] for t in tasks_of[cl] for c in cfgs) for cl in clusters])
        den = n_t[draws].sum(1) * len(cfgs)
        d = 100 * (g[draws].sum(1) - o[draws].sum(1)) / den
        est = 100 * (g.sum() - o.sum()) / (n_t.sum() * len(cfgs))
        return est, *np.percentile(d, [2.5, 97.5])

    fig = plt.figure(figsize=(W_DOUBLE * 0.62, 82 * MM))
    ax = fig.add_axes([0.25, 0.225, 0.47, 0.60])
    panel_title(fig, -0.013, 0.985, 'Unanimous accuracy was higher in the Galaxy condition for every\nmodel configuration; every 95% interval '
                                     'included zero')
    rows, ys, labs = [], [], []
    y = 0
    for cfg in CFG5:
        if cfg == SUPERSEDED:
            y += 0.45
        for e, dy in zip(ENVS, (-0.2, 0.2)):
            n = sum(unan[(t, cfg, e)] for t in cluster)
            ax.barh(y + dy, 100 * n / 50, height=0.38, color=ENV_COLOR[e], lw=0)
            ax.text(100 * n / 50 + 1.2, y + dy, f'{100 * n / 50:.0f}% ({n}/50)', va='center', fontsize=5.0, color=INK)
            rows.append(dict(model_configuration=ROW[cfg].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[e],
                             tasks_with_3_of_3_scored_correct=n, tasks=50, unanimous_accuracy_percent=100 * n / 50))
        est, lo, hi = diff_ci([cfg])
        ax.text(1.20, y, f'{signed(est)}\n({signed(lo)} to {signed(hi)})', transform=ax.get_yaxis_transform(), fontsize=5.0,
                va='center', ha='left', linespacing=1.15)
        rows[-1].update(difference_galaxy_minus_open_ended_code_pp=round(est, 2), ci95_low=round(lo, 2), ci95_high=round(hi, 2))
        ys.append(y); labs.append(ROW[cfg]); y += 1
    ax.text(1.20, -0.62, 'Galaxy − open-ended\ncode, points (95% CI)', transform=ax.get_yaxis_transform(), fontsize=5.0,
            fontweight='bold', va='bottom', ha='left', linespacing=1.15)
    ax.set_yticks(ys); ax.set_yticklabels(labs, fontsize=5.3, linespacing=1.05); ax.tick_params(axis='y', length=0)
    ax.set_ylim(y - 0.4, -0.65); ax.set_xlim(0, 100); ax.set_xticks(range(0, 101, 20)); grid_x(ax)
    ax.set_xlabel('Unanimous accuracy (% of 50 tasks with all three\nreplicate runs scored correct)')
    ax.legend(handles=[Patch(fc=ENV_COLOR[e], label=ENV_LABEL_LONG[e]) for e in ENVS], loc='lower left', bbox_to_anchor=(-0.02, 1.0),
              ncol=2, fontsize=5.3)
    four, five = diff_ci(CONFIGS), diff_ci(CFG5)
    note = (f"Pooled condition difference: four Codex model configurations {signed(four[0])} ({signed(four[1])} to {signed(four[2])}); "
            f"all five {signed(five[0])} ({signed(five[1])} to {signed(five[2])}) percentage points. Intervals: 95% percentile "
            f"cluster bootstrap over source capsules ({n_boot:,} resamples). Run-level accuracy is compared with unanimous accuracy in Fig. 4e.")
    fig.text(0.015, 0.085, textwrap.fill(note, 118), fontsize=5.0, color=INK2, va='top', linespacing=1.25)
    save(fig, 'OD_Fig2_unanimous_accuracy', 'Unanimous accuracy per model configuration (BixBench-Verified-50)')
    pooled = [dict(model_configurations=lab, difference_galaxy_minus_open_ended_code_pp=round(v[0], 2), ci95_low=round(v[1], 2),
                   ci95_high=round(v[2], 2)) for lab, v in (('Four Codex model configurations', four), ('All five model configurations', five))]
    source_data('OD_Fig2', {'unanimous_accuracy': pd.DataFrame(rows), 'pooled_difference': pd.DataFrame(pooled)})
    return rows, four, five


# =====================================================================================================
def holm(p):
    """Holm step-down adjustment (family-wise error rate)."""
    p = np.asarray(p, float)
    order, out, run = np.argsort(p), np.empty(len(p)), 0.0
    for k, i in enumerate(order):
        run = max(run, min(1.0, (len(p) - k) * p[i]))
        out[i] = run
    return out


def fmt_p(p):
    return '<0.001' if p < 0.001 else (f'{p:.3f}' if p < 0.1 else f'{p:.2f}')


def fig3_stats(runs, n_boot=20000, seed=20260929):
    """Scored-incorrect versus scored-correct input-token usage.
    Per model configuration and condition: two-sided Mann-Whitney U, Holm-adjusted over the ten comparisons, with the
    rank-biserial correlation and a 95% percentile cluster-bootstrap interval of the median ratio (source capsules resampled,
    because the three replicate runs of a task, and the tasks of a capsule, are not independent).
    Within task: in each split replicate set, the mean log2 ratio of its scored-incorrect run(s) to the median of its
    scored-correct siblings; two-sided Wilcoxon signed-rank test over sets, per condition."""
    from scipy import stats
    cluster = {r['task']: r['cluster'] for r in RUNS}
    caps = sorted(set(cluster.values()))
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, len(caps), size=(n_boot, len(caps)))
    pair = []
    for e in ENVS:
        for cfg in CFG5:
            rr = [r for r in runs if r['config'] == cfg and r['condition'] == e]
            inc = np.array([r['input_tokens'] for r in rr if not r['correct']], float)
            cor = np.array([r['input_tokens'] for r in rr if r['correct']], float)
            u = stats.mannwhitneyu(inc, cor, alternative='two-sided')
            per = [(np.array([r['input_tokens'] for r in rr if cluster[r['task']] == cp and not r['correct']], float),
                    np.array([r['input_tokens'] for r in rr if cluster[r['task']] == cp and r['correct']], float)) for cp in caps]
            boot = []
            for d in draws:
                a = np.concatenate([per[j][0] for j in d]); b = np.concatenate([per[j][1] for j in d])
                if len(a) and len(b):
                    boot.append(np.median(a) / np.median(b))
            lo, hi = np.percentile(boot, [2.5, 97.5])
            pair.append(dict(execution_condition=e, config=cfg, n_correct=len(cor), n_incorrect=len(inc),
                             median_correct=np.median(cor), median_incorrect=np.median(inc), ratio=np.median(inc) / np.median(cor),
                             U=u.statistic, p=u.pvalue, rank_biserial=2 * u.statistic / (len(inc) * len(cor)) - 1,
                             ratio_ci_low=lo, ratio_ci_high=hi, bootstrap_resamples_used=len(boot)))
    for x, pa in zip(pair, holm([x['p'] for x in pair])):
        x['p_holm'] = pa
    within = {}
    for e in ENVS:
        sets_ = []
        for (t, c, ee), rs in SETS.items():
            cor = [r['input_tokens'] for r in rs if r['correct']]
            inc = [r['input_tokens'] for r in rs if not r['correct']]
            if ee == e and cor and inc:
                sets_.append(dict(task=t, config=c, incorrect_runs=len(inc), median_correct_sibling=st.median(cor),
                                  mean_log2_ratio=float(np.mean([np.log2(x / st.median(cor)) for x in inc]))))
        v = np.array([x['mean_log2_ratio'] for x in sets_])
        w = stats.wilcoxon(v, alternative='two-sided')
        within[e] = dict(sets=sets_, n_sets=len(v), n_runs=sum(x['incorrect_runs'] for x in sets_), ratio=2 ** np.median(v),
                         W=w.statistic, p=w.pvalue, higher=int((v > 0).sum()))
    return pair, within


def od_fig3(seed=7):
    """Input-token usage per run, scored-correct versus scored-incorrect, per model configuration; a open-ended code, b Galaxy."""
    runs = [r for rs in SETS.values() for r in rs]
    assert all(r['input_tokens'] for r in runs)
    pair, within = fig3_stats(runs)
    PAIR = {(x['execution_condition'], x['config']): x for x in pair}
    plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold',
                         'mathtext.bfit': 'Arial:italic:bold', 'mathtext.cal': 'Arial', 'mathtext.sf': 'Arial', 'mathtext.tt': 'Arial'})
    P = r'$\mathit{P}$'
    fig = plt.figure(figsize=(W_DOUBLE, 108 * MM))
    rng = np.random.default_rng(seed)
    x0s, w, y0, h = [0.075, 0.565], 0.415, 0.235, 0.54
    rows, runs_rows = [], []
    for i, e in enumerate(ENVS):
        ax = fig.add_axes([x0s[i], y0, w, h])
        for g, cfg in enumerate(CFG5):
            vals = {ok: np.array([r['input_tokens'] / 1e6 for r in runs if r['config'] == cfg and r['condition'] == e and r['correct'] == ok])
                    for ok in (True, False)}
            for ok, dx in ((True, -0.19), (False, 0.19)):
                v = vals[ok]
                bp = ax.boxplot(v, positions=[g + dx], widths=0.3, whis=1.5, showfliers=False, patch_artist=True, manage_ticks=False)
                fc = ENV_TINT[e] if ok else ENV_COLOR[e]
                for b in bp['boxes']:
                    b.set(facecolor=fc, edgecolor=ENV_COLOR[e], lw=0.6)
                for part in ('whiskers', 'caps'):
                    for ln in bp[part]:
                        ln.set(color=ENV_COLOR[e], lw=0.6)
                for ln in bp['medians']:
                    ln.set(color=INK if ok else 'white', lw=0.9)
                ax.scatter(g + dx + rng.uniform(-0.1, 0.1, len(v)), v, s=1.4, color=INK, alpha=0.45, lw=0, zorder=3)
                ax.text(g + dx, 0.022, str(len(v)), ha='center', va='bottom', fontsize=5.0, color=INK2)
                q1, med, q3 = np.percentile(v, [25, 50, 75])
                rows.append(dict(execution_condition=ENV_LABEL_LONG[e], model_configuration=ROW[cfg].replace('\n', ' '),
                                 outcome='Scored correct' if ok else 'Scored incorrect', runs=len(v), median_million=round(med, 3),
                                 q1_million=round(q1, 3), q3_million=round(q3, 3), min_million=round(v.min(), 3), max_million=round(v.max(), 3)))
            x = PAIR[(e, cfg)]
            sig = x['p_holm'] < 0.05
            ax.text(g, 400, f"{x['ratio']:.2f}×\n{r'$\mathbfit{P}$' if sig else P} = {fmt_p(x['p_holm'])}", ha='center', va='bottom', fontsize=5.0,
                    color=INK if sig else INK2, fontweight='bold' if sig else 'normal', linespacing=1.3)
            if sig:  # bracket joining the two boxes that differ
                ax.plot([g - 0.19, g - 0.19, g + 0.19, g + 0.19], [300, 340, 340, 300], color=INK, lw=0.5, clip_on=False)
        for r in runs:
            if r['condition'] == e:
                runs_rows.append(dict(execution_condition=ENV_LABEL_LONG[e], model_configuration=ROW[r['config']].replace('\n', ' '), task=r['task'],
                                      replicate=r['replicate'], scored_correct=r['correct'], input_tokens=r['input_tokens']))
        ax.set_yscale('log'); ax.set_ylim(0.015, 380); ax.set_xlim(-0.6, len(CFG5) - 0.4)
        ax.set_yticks([0.1, 1, 10, 100]); ax.set_yticklabels(['0.1', '1', '10', '100']); ax.minorticks_off()
        ax.set_xticks(range(len(CFG5))); ax.set_xticklabels([TICK3[c] for c in CFG5], fontsize=5.2, linespacing=1.05)
        ax.tick_params(axis='x', length=0)
        ax.set_ylabel('Input-token usage per run (millions, log scale)' if i == 0 else ''); grid_y(ax)
        lx = 0.005 if i == 0 else x0s[i] - 0.05
        sig_cfgs = [ROW[c].replace('\n', ' ') for c in CFG5 if PAIR[(e, c)]['p_holm'] < 0.05]
        higher_all = all(PAIR[(e, c)]['ratio'] > 1 for c in CFG5)
        if sig_cfgs:
            title = (f"{ENV_LABEL_LONG[e]}: scored-incorrect runs used more input\n"
                     f"tokens{'' if higher_all else ' in some model configurations'}, significantly so only for {' and '.join(sig_cfgs)}")
        else:
            title = f'{ENV_LABEL_LONG[e]}: no significant difference between\nscored-incorrect and scored-correct runs'
        panel_label(fig, lx, 0.99, 'ab'[i]); panel_title(fig, lx, 0.99, title)
        wi = within[e]
        fig.text(lx + 0.018, 0.915, f"Same task and model configuration ({wi['n_sets']} split replicate sets): scored-incorrect runs used\n"
                                    f"{wi['ratio']:.2f} times the input tokens of their scored-correct siblings (median; Wilcoxon signed-rank "
                                    f"{P} = {fmt_p(wi['p'])})", fontsize=5.0, color=INK2, va='top', linespacing=1.35)
    fig.legend(handles=[Patch(fc=ENV_TINT[e], ec=ENV_COLOR[e], lw=0.6, label=f'{ENV_LABEL[e]}, scored correct') for e in ENVS] +
               [Patch(fc=ENV_COLOR[e], ec=ENV_COLOR[e], lw=0.6, label=f'{ENV_LABEL[e]}, scored incorrect') for e in ENVS],
               loc='lower left', bbox_to_anchor=(0.07, 0.03), ncol=2, fontsize=5.2, columnspacing=1.4)
    robust = '; '.join(f"for {ROW[x['config']].replace(chr(10), ' ')} it is {x['ratio_ci_low']:.2f} to {x['ratio_ci_high']:.2f}"
                       + (', so this difference does not survive that dependence' if x['ratio_ci_low'] <= 1 else '')
                       for x in pair if x['p_holm'] < 0.05)
    note = ("BixBench-Verified-50; every run is a dot (1,500 runs; numbers along the bottom give the runs per box). Boxes span the "
            "middle 50% of runs and mark the median; whiskers extend to 1.5 times the interquartile range. Above each pair: median "
            "input-token usage, scored incorrect ÷ scored correct, and the two-sided Mann–Whitney U § value, Holm-adjusted over the ten "
            "comparisons (bold with a bracket: § < 0.05). The three replicate runs of a task are not independent, so these § values may be "
            "optimistic. Source Data give each ratio's 95% cluster-bootstrap interval (source capsules, 20,000 resamples)"
            + (f"; {robust}." if robust else '.') + " Input-token usage includes cached input; output tokens (0.6% of input) are not "
            "added. Scored-incorrect runs include runs that submitted no answer.")
    fig.text(0.44, 0.155, textwrap.fill(note, 116).replace('§', P), fontsize=5.0, color=INK2, va='top', linespacing=1.25)
    save(fig, 'OD_Fig3_input_tokens_correct_vs_incorrect',
         'Input-token usage of scored-correct and scored-incorrect runs per model configuration (BixBench-Verified-50)')
    tests = pd.DataFrame([dict(execution_condition=ENV_LABEL_LONG[x['execution_condition']], model_configuration=ROW[x['config']].replace('\n', ' '),
                               scored_correct_runs=x['n_correct'], scored_incorrect_runs=x['n_incorrect'],
                               median_scored_correct=x['median_correct'], median_scored_incorrect=x['median_incorrect'],
                               median_ratio_incorrect_over_correct=round(x['ratio'], 3),
                               ratio_ci95_low_cluster_bootstrap=round(x['ratio_ci_low'], 3), ratio_ci95_high_cluster_bootstrap=round(x['ratio_ci_high'], 3),
                               mann_whitney_U=x['U'], p_two_sided=x['p'], p_holm_10_comparisons=x['p_holm'],
                               significant_holm_0_05=x['p_holm'] < 0.05, rank_biserial_correlation=round(x['rank_biserial'], 3)) for x in pair])
    wtest = pd.DataFrame([dict(execution_condition=ENV_LABEL_LONG[e], split_replicate_sets=within[e]['n_sets'],
                               scored_incorrect_runs=within[e]['n_runs'], sets_with_incorrect_above_correct=within[e]['higher'],
                               median_ratio=round(within[e]['ratio'], 3), wilcoxon_signed_rank_W=within[e]['W'], p_two_sided=within[e]['p'])
                          for e in ENVS])
    wsets = pd.DataFrame([dict(execution_condition=ENV_LABEL_LONG[e], task=x['task'], model_configuration=ROW[x['config']].replace('\n', ' '),
                               scored_incorrect_runs=x['incorrect_runs'], median_scored_correct_sibling_input_tokens=x['median_correct_sibling'],
                               mean_log2_ratio=round(x['mean_log2_ratio'], 4)) for e in ENVS for x in within[e]['sets']])
    source_data('OD_Fig3', {'ab_box_summary': pd.DataFrame(rows), 'ab_tests_incorrect_vs_correct': tests,
                            'ab_within_task_test': wtest, 'ab_within_task_sets': wsets, 'ab_runs': pd.DataFrame(runs_rows)})
    return pair, within


# =====================================================================================================
KEY_DIR = os.environ.get('COMPBIO_KEY_DIR')
KEY_SHA = {'score_inferred_answers.tsv': '959dd3f2', 'compbiobench_results_score_predicted_answers.tsv': '57a6a92d',
           'paper_site_runs_lab.json': '055cfb18'}  # SHA-256 prefixes recorded in individual_error_analysis.md
MODEL_ALL = dict(MODEL, codex_deepseek_v4_pro_0813='DeepSeek V4 Pro', codex_deepseek_v4_pro='DeepSeek V4 Pro')
BENCH3 = [('BixBench50', 'BixBench-Verified-50'), ('CompBio', 'CompBioBench'), ('IWC', 'IWC')]
IWC_UNMATCHED = 'wf_003_host_contamination_removal'  # not scored for GPT-5.5 open-ended code: nine matched tasks, as in Fig. 2a
LAB_SHORT = {'GPT-5.5': 'GPT-5.5', 'Sol': 'GPT-5.6 Sol', 'Luna': 'GPT-5.6 Luna', 'DeepSeek-v4-pro-0813': 'DeepSeek V4 Pro'}


def compbio_key():
    """Score-inferred answers (54 tasks) over score-predicted answers (46 tasks), genome-coords-q1 = E."""
    import csv
    import hashlib
    if not KEY_DIR:
        raise SystemExit('Set COMPBIO_KEY_DIR to the folder that holds the lab CompBioBench key files (see on_demand/README.md).')
    for f, pre in KEY_SHA.items():
        h = hashlib.sha256(open(os.path.join(KEY_DIR, f), 'rb').read()).hexdigest()
        assert h.startswith(pre), (f, h)
    read = lambda f: {r['question_id']: r['answer'] for r in csv.DictReader(open(os.path.join(KEY_DIR, f)), delimiter='\t')}
    key = read('compbiobench_results_score_predicted_answers.tsv')
    key.update(read('score_inferred_answers.tsv'))
    key['genome-coords-q1'] = 'E'  # the only value that reproduces all 25 official scores (individual_error_analysis.md, check 3)
    assert len(key) == 100
    return key


def answer_id(a):
    """Answer identity for finding a majority: trimmed, case- and space-insensitive; numbers compared to 10 significant digits."""
    a = (a or '').strip().lower().replace(' ', '')
    try:
        return f"{float(a.rstrip('%')):.10g}"
    except ValueError:
        return a


def majority_sets():
    key = compbio_key()
    grade = lambda r: float((r['answer'] or '').replace('Proximal enhancer,EH38E1957012', 'pELS,EH38E1957012').strip() == key[r['task']])
    reps = collections.defaultdict(list)
    for r in A['runs']:
        if r['model'] == 'codex_gpt_6_astra' or (r['benchmark'] == 'IWC' and r['task'] == IWC_UNMATCHED):
            continue  # GPT-6 Astra has one unpaired run per task, so no replicate set
        b = r['benchmark']
        score = float(r['score'] == 1) if b == 'BixBench50' else (grade(r) if b == 'CompBio' else r['score'])
        reps[(b, MODEL_ALL[r['model']], r['condition'], r['task'])].append(
            dict(answer=r['answer'], score=score, replicate=r['replicate'], cluster=r['cluster'] if b == 'BixBench50' else r['task']))
    # the per-run CompBioBench grades must reproduce every official replicate score in the lab results file
    lab = json.load(open(os.path.join(KEY_DIR, 'paper_site_runs_lab.json')))
    checked = 0
    for m in lab['models']:
        if m['short'] not in LAB_SHORT:
            continue
        for c, v in m['conditions'].items():
            env = 'galaxy' if c == 'galaxy' else 'open_ended_code'
            for rep in v['replicates']:
                got = sum(x['score'] for (b, cfg, e, t), rs in reps.items() if b == 'CompBio' and cfg == LAB_SHORT[m['short']] and e == env
                          for x in rs if x['replicate'] == int(rep['id'][1:]))
                assert got == rep['official_score'], (m['short'], c, rep['id'], got, rep['official_score'])
                checked += 1
    assert checked == 24
    out = {}
    for k, rs in reps.items():
        sc = [x['score'] for x in rs]
        assert len(rs) == 3 and None not in sc, k
        if k[0] == 'IWC':  # continuous endpoint: the median of three is the majority value (for 0/1 scores it is the majority vote)
            out[k] = dict(run_level=float(np.mean(sc)), majority=float(np.median(sc)), outcome='', correct_runs=None, cluster=rs[0]['cluster'], scores=sc)
            continue
        cls = collections.Counter('CORRECT' if x['score'] == 1 else answer_id(x['answer']) for x in rs)
        top, n = cls.most_common(1)[0]
        outcome = ('Majority answer correct' if top == 'CORRECT' else 'Majority answer incorrect') if n >= 2 else 'No majority (three different answers)'
        k_ = int(sum(sc))
        assert (outcome == 'Majority answer correct') == (k_ >= 2)  # one reference answer: majority correct <=> at least 2 of 3 correct
        out[k] = dict(run_level=k_ / 3, majority=float(k_ >= 2), outcome=outcome, correct_runs=k_, cluster=rs[0]['cluster'], scores=sc)
    return out


def od_fig4(n_boot=20000, seed=20260929):
    """Majority-vote accuracy per model configuration and condition; a pooled over the two benchmarks with one reference answer, b per benchmark."""
    M = majority_sets()
    level = lambda b, cfg, e, f: 100 * np.mean([v[f] for (bb, c, ee, t), v in M.items() if bb in b and c == cfg and ee == e])
    POOL = ('BixBench50', 'CompBio')
    rng = np.random.default_rng(seed)

    def diff_ci(benches, cfg):
        """Galaxy - open-ended code, majority vote; stratified cluster bootstrap (source capsules for BixBench, tasks otherwise)."""
        per = []
        for b in benches:
            cl = collections.defaultdict(lambda: np.zeros(3))
            for (bb, c, e, t), v in M.items():
                if bb == b and c == cfg:
                    cl[v['cluster']] += [v['majority'] * (e == 'galaxy'), v['majority'] * (e == 'open_ended_code'), 0.5]
            per.append(np.array(list(cl.values())))
        tot = sum(p.sum(0) for p in per)
        est = 100 * (tot[0] - tot[1]) / tot[2]
        sums = sum(p[rng.integers(0, len(p), size=(n_boot, len(p)))].sum(1) for p in per)
        d = 100 * (sums[:, 0] - sums[:, 1]) / sums[:, 2]
        return est, *np.percentile(d, [2.5, 97.5])

    def dumbbell(ax, y, run, maj, env):
        ax.plot([run, maj], [y, y], color=ENV_COLOR[env], lw=0.9, zorder=2, solid_capstyle='butt')
        ax.plot(run, y, ENV_MARKER[env], ms=3.4, mfc='white', mec=ENV_COLOR[env], mew=0.9, zorder=3, clip_on=False)
        ax.plot(maj, y, ENV_MARKER[env], ms=3.4, mfc=ENV_COLOR[env], mec='white', mew=0.4, zorder=4, clip_on=False)

    fig = plt.figure(figsize=(W_DOUBLE, 150 * MM))
    rows_a, rows_b, gains = [], [], collections.defaultdict(list)
    # ---- a: pooled BixBench-Verified-50 and CompBioBench, the four model configurations that ran both
    ax = fig.add_axes([0.175, 0.625, 0.33, 0.215])
    for i, cfg in enumerate(CONFIGS):
        for env, dy in zip(ENVS, (-0.17, 0.17)):
            run, maj = level(POOL, cfg, env, 'run_level'), level(POOL, cfg, env, 'majority')
            dumbbell(ax, i + dy, run, maj, env)
            gains[env].append(maj - run)
            ax.text(1.03, i + dy, f'{maj:.1f} ({signed(maj - run)})', transform=ax.get_yaxis_transform(), fontsize=5.0, va='center')
            n = sum(1 for (b, c, e, t) in M if b in POOL and c == cfg and e == env)
            rows_a.append(dict(model_configuration=ROW[cfg].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[env], tasks=n,
                               run_level_accuracy=round(run, 2), majority_vote_accuracy=round(maj, 2), change_points=round(maj - run, 2)))
        est, lo, hi = diff_ci(POOL, cfg)
        ax.text(1.36, i, f'{signed(est)}\n({signed(lo)} to {signed(hi)})', transform=ax.get_yaxis_transform(), fontsize=5.0, va='center', linespacing=1.15)
        rows_a[-1].update(majority_difference_galaxy_minus_open_ended_code=round(est, 2), ci95_low=round(lo, 2), ci95_high=round(hi, 2))
    ax.text(1.03, -0.55, 'Majority vote, %\n(change from\nsingle run)', transform=ax.get_yaxis_transform(), fontsize=5.0, fontweight='bold', va='bottom', linespacing=1.15)
    ax.text(1.36, -0.55, 'Galaxy − open-ended\ncode, majority vote,\npoints (95% CI)', transform=ax.get_yaxis_transform(), fontsize=5.0, fontweight='bold',
            va='bottom', linespacing=1.15)
    ax.set_yticks(range(len(CONFIGS))); ax.set_yticklabels([ROW[c] for c in CONFIGS], fontsize=5.3); ax.tick_params(axis='y', length=0)
    ax.set_ylim(len(CONFIGS) - 0.5, -0.55); ax.set_xlim(80, 95); ax.set_xticks(range(80, 96, 5)); grid_x(ax)
    ax.set_xlabel('Accuracy (% of 150 tasks: 50 BixBench-Verified-50 and 100 CompBioBench)')
    assert np.mean(gains['open_ended_code']) > np.mean(gains['galaxy'])
    panel_label(fig, 0.005, 0.99, 'a')
    panel_title(fig, 0.005, 0.99, 'Majority voting raised accuracy more in the open-ended code condition than in the Galaxy condition\n'
                                   '(BixBench-Verified-50 and CompBioBench pooled)')
    split = {e: collections.Counter(v['correct_runs'] for (b, c, ee, t), v in M.items() if b in POOL and c in CONFIGS and ee == e) for e in ENVS}
    assert split['open_ended_code'][2] - split['open_ended_code'][1] > split['galaxy'][2] - split['galaxy'][1]
    fig.text(0.023, 0.935, f"Change from single run: open-ended code {signed(min(gains['open_ended_code']))} to {signed(max(gains['open_ended_code']))} points, "
                           f"Galaxy {signed(min(gains['galaxy']))} to {signed(max(gains['galaxy']))}. Majority voting changes accuracy only through split replicate sets: "
                           f"it gains 1/3 of a task for each set with 2 of 3 runs\ncorrect and loses 1/3 for each with 1 of 3. Open-ended code split sets mostly had "
                           f"2 of 3 correct ({split['open_ended_code'][2]} versus {split['open_ended_code'][1]}); Galaxy split sets were balanced "
                           f"({split['galaxy'][2]} versus {split['galaxy'][1]}), so majority voting gained little there.",
             fontsize=5.0, color=INK2, va='top', linespacing=1.3)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker=ENV_MARKER[e], ls='-', color=ENV_COLOR[e], lw=0.9, mfc=f, mec=ENV_COLOR[e] if f == 'white' else 'white', mew=0.9 if f == 'white' else 0.4,
                      ms=3.4, label=f"{ENV_LABEL_LONG[e]}, {lab}") for e in ENVS for f, lab in (('white', 'single run (run-level accuracy)'), (ENV_COLOR[e], 'majority vote'))]
    fig.legend(handles=[Line2D([], [], marker=ENV_MARKER[e], ls='', mfc=f, mec=ENV_COLOR[e] if f == 'white' else 'white', mew=0.9 if f == 'white' else 0.4, ms=3.6,
                               label=f"{ENV_LABEL[e]}: {lab}") for e in ENVS for f, lab in (('white', 'single run (run-level)'), (ENV_COLOR[e], 'majority vote'))],
               loc='upper left', bbox_to_anchor=(0.79, 0.85), ncol=1, fontsize=5.2, handletextpad=0.5, labelspacing=0.8)
    fig.text(0.795, 0.735, textwrap.fill('Majority vote: the answer given by at least two of the three replicate runs of a task; a task whose three runs gave '
                                         'three different answers has no majority and counts as incorrect. With one reference answer per task, the majority '
                                         'answer is correct exactly when at least two replicate runs are scored correct.', 46),
             fontsize=5.0, color=INK2, va='top', linespacing=1.25)
    # ---- b: per benchmark, all model configurations that ran it
    panel_label(fig, 0.005, 0.545, 'b')
    fig.text(0.023, 0.544, 'Per benchmark, majority voting raised open-ended code accuracy on CompBioBench for every model configuration;\n'
                           'elsewhere the change depended on the model configuration', fontsize=6.5, fontweight='bold', va='top', linespacing=1.15)
    x0s, w = [0.175, 0.47, 0.765], 0.19
    for k, (b, bl) in enumerate(BENCH3):
        ax = fig.add_axes([x0s[k], 0.19, w, 0.27])
        for i, cfg in enumerate(CFG5):
            if not any(bb == b and c == cfg for (bb, c, e, t) in M):
                ax.text(0.5, i, 'Not run with this agent harness', transform=ax.get_yaxis_transform(), ha='center', va='center', fontsize=5.0, color=INK2)
                continue
            for env, dy in zip(ENVS, (-0.17, 0.17)):
                run, maj = level((b,), cfg, env, 'run_level'), level((b,), cfg, env, 'majority')
                dumbbell(ax, i + dy, run, maj, env)
                ax.text(1.03, i + dy, signed(maj - run), transform=ax.get_yaxis_transform(), fontsize=5.0, va='center')
                cnt = collections.Counter(v['outcome'] for (bb, c, e, t), v in M.items() if bb == b and c == cfg and e == env)
                rows_b.append(dict(benchmark=bl, model_configuration=ROW[cfg].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[env],
                                   tasks=sum(cnt.values()), run_level=round(run, 2), majority_vote=round(maj, 2), change_points=round(maj - run, 2),
                                   **({} if b == 'IWC' else {o: cnt.get(o, 0) for o in ('Majority answer correct', 'Majority answer incorrect',
                                                                                       'No majority (three different answers)')})))
            est, lo, hi = diff_ci((b,), cfg)
            rows_b[-1].update(majority_difference_galaxy_minus_open_ended_code=round(est, 2), ci95_low=round(lo, 2), ci95_high=round(hi, 2))
        ax.text(1.03, -0.55, 'Change', transform=ax.get_yaxis_transform(), fontsize=5.0, fontweight='bold', va='bottom')
        ax.set_yticks(range(len(CFG5)))
        ax.set_yticklabels([ROW[c] for c in CFG5] if k == 0 else [], fontsize=5.3, linespacing=1.05); ax.tick_params(axis='y', length=0)
        ax.set_ylim(len(CFG5) - 0.5, -0.55); ax.set_xlim(65, 100); ax.set_xticks(range(70, 101, 10)); grid_x(ax)
        ntask = len({t for (bb, c, e, t) in M if bb == b})
        ax.set_xlabel(f'Accuracy (% of {ntask} tasks)' if b != 'IWC' else f'Output agreement (%, {ntask} tasks): open, mean\nof runs; filled, median of three replicate runs')
        ax.set_title(bl, fontsize=6, loc='left', pad=4)
    note = ("Open symbols: single run (run-level accuracy); filled symbols: majority vote; change = majority vote − single run, in points. "
            "BixBench-Verified-50: evaluator scores. CompBioBench: exact string match against the lab's score-inferred answer key (54 tasks) and "
            "score-predicted answers (46 tasks; genome-coords-q1 = E); these grades reproduce all 24 official replicate scores in the lab results file of "
            "17 September 2026, two of which are one point above the archived values used in Fig. 2d. GPT-6 Astra, with one unpaired run per task, is excluded. "
            "IWC has a continuous endpoint, so its majority value is the median of the three replicate runs' output agreement (for a 0/1 score, the median "
            "of three is the majority vote), over the nine tasks scored in both conditions; it is not pooled in a. Intervals: 95% percentile cluster "
            "bootstrap (source capsules for BixBench-Verified-50, tasks for CompBioBench and IWC; 20,000 resamples). Source Data give the Galaxy − open-ended "
            "code difference per benchmark and the outcome of every replicate set (majority correct, majority incorrect, no majority).")
    fig.text(0.023, 0.105, textwrap.fill(note, 215), fontsize=5.0, color=INK2, va='top', linespacing=1.25)
    save(fig, 'OD_Fig4_majority_vote_accuracy', 'Majority-vote accuracy per model configuration and execution condition')
    sets_rows = [dict(benchmark=dict(BENCH3)[b], model_configuration=ROW[c].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[e], task=t,
                      replicate_scores='; '.join(f'{x:g}' for x in v['scores']), run_level=round(v['run_level'], 4), majority=round(v['majority'], 4),
                      outcome=v['outcome']) for (b, c, e, t), v in sorted(M.items())]
    source_data('OD_Fig4', {'a_pooled_majority_vote': pd.DataFrame(rows_a), 'b_by_benchmark': pd.DataFrame(rows_b),
                            'ab_replicate_sets': pd.DataFrame(sets_rows)})
    return rows_a, rows_b


# =====================================================================================================
EXIT_TEXT = re.compile(r'^\s*Exit code (\d+)\s*\n?(.*)', re.S)
# Error types for failed shell commands and failed Galaxy jobs. Rules are applied in order to the error message; the first match wins.
ERROR_TYPES = [('code', 'Code, parameter or syntax error'), ('software', 'Missing software, package\nor container'),
               ('file', 'File, path or input format'), ('time', 'Time or memory limit'), ('network', 'Network or download'),
               ('not_started', 'Galaxy job never started'), ('unclassified', 'No or unclassified message')]
ERROR_RULES = [
    ('time', re.compile(r"KeyboardInterrupt|\bKilled\b|timed? ?out|TimeoutExpired|walltime|Terminated|MemoryError|out of memory|Cannot allocate memory|"
                        r"std::bad_alloc|oom[-_ ]kill|exceeded (the )?(memory|time)|signal 9|SIGKILL|resource limit", re.I)),
    ('network', re.compile(r"Could not resolve host|Temporary failure in name resolution|Name or service not known|Connection (refused|reset|timed out|aborted)|"
                           r"Network is unreachable|Max retries exceeded|urlopen error|HTTP Error \d+|HTTPError|curl: \(\d+\)|SSLError|CERTIFICATE_VERIFY|"
                           r"Remote end closed|RemoteDisconnected|ProxyError|Failed to establish a new connection|503 Service|502 Bad Gateway|429 Too Many", re.I)),
    ('software', re.compile(r"dpkg (frontend )?lock|Unable to acquire the dpkg|E: Unable to|ModuleNotFoundError|No module named|ImportError|command not found|"
                            r": not found\b|executable file not found|Could not find a version that satisfies|No matching distribution|there is no package called|"
                            r"PackagesNotFoundError|PackageNotFoundError|Failed to build|failed building wheel|error: subprocess-exited-with-error|"
                            r"Unable to locate package|could not find function|cannot open shared object file|library not loaded|requires Python|"
                            r"manifest unknown|pull access denied|access to the requested resource is not authorized|failed to pull|Error response from daemon",
                            re.I)),
    ('file', re.compile(r"No such file or directory|FileNotFoundError|does not exist|Permission denied|Operation not permitted|Is a directory|IsADirectoryError|"
                        r"not in gzip format|Invalid gzip|BadGzipFile|EOFError|truncated|unexpected end of (file|data)|Unrecognized or unindexable|"
                        r"unknown file type|does not look like a tar archive|could not open|cannot open|Failed to open|can't read|cannot read|unable to open|"
                        r"ParserError|UnicodeDecodeError|EmptyDataError|No columns to parse|empty (file|input)|zero-length|malformed|invalid (file )?format|"
                        r"not a valid (bam|vcf|fasta|fastq|bed|file)|magic number|Read-only file system|No space left", re.I)),
    ('code', re.compile(r"Traceback|Exception|Error in |^Error|\bERROR\b|TypeError|ValueError|KeyError|IndexError|AttributeError|NameError|SyntaxError|"
                        r"IndentationError|ZeroDivisionError|AssertionError|RuntimeError|unrecognized arguments|invalid (option|choice|argument|value)|"
                        r"unknown option|usage: |Usage:|missing (required )?argument|unexpected (EOF|token)|syntax error|subscript out of bounds|"
                        r"object '.*' not found|undefined columns|non-numeric argument|cannot coerce|replacement has|arguments imply differing|duplicate|"
                        r"mismatch|must be|expected|invalid|No columns specified|not preceded with|unknown primary or operator|illegal option|"
                        r"not supported|non float value|out of range|out of bounds|failed with|error: |unbound variable", re.I | re.M)),
]
GALAXY_GENERIC = re.compile(r'\[\{"desc": "Fatal error: Exit code \d+ \(\)".*?\}\]|Fatal error: Exit code \d+ \(\)', re.S)


def classify_error(text, exit_code=None, command=''):
    """Error type of one failed shell command or Galaxy job (first matching rule; see ERROR_RULES)."""
    if exit_code in (124, 130, 137, 143):  # timeout, harness interrupt or kill
        return 'time'
    t = GALAXY_GENERIC.sub('', text or '').strip()
    if exit_code == 127 and (not t or 'not found' in t):
        return 'software'
    if not t:
        return 'network' if re.match(r'\s*(/\S*bash -l?c\s+[\'"]?)?(curl|wget)\b', command or '') else 'unclassified'
    for k, rx in ERROR_RULES:
        if rx.search(t):
            return k
    return 'unclassified'


def shell_failures(trace):
    """(exit code, message, command) for every failed shell command in a trace; a silent exit code 1 (a negative test such as a
    search with no match) is not a failure. Codex traces record the exit code; Claude Code traces record it as 'Exit code N'."""
    opener = lambda p: gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')
    out = []
    if 'claude' in os.path.basename(trace):
        names, cmds = {}, {}
        for line in opener(trace):
            if '"tool_use"' not in line and '"tool_result"' not in line:
                continue
            try:
                content = (json.loads(line).get('message') or {}).get('content')
            except ValueError:
                continue
            for b in content if isinstance(content, list) else []:
                if b.get('type') == 'tool_use':
                    names[b.get('id')] = b.get('name')
                    cmds[b.get('id')] = str((b.get('input') or {}).get('command') or '')
                elif b.get('type') == 'tool_result' and names.get(b.get('tool_use_id')) == 'Bash' and b.get('is_error'):
                    txt = b.get('content')
                    txt = '\n'.join(x.get('text', '') for x in txt if isinstance(x, dict)) if isinstance(txt, list) else str(txt or '')
                    m = EXIT_TEXT.match(txt)
                    ec, msg = (int(m.group(1)), m.group(2)) if m else ((124 if re.search(r'timed out|timeout', txt, re.I) else -1), txt)
                    if not (ec == 1 and not msg.strip()):
                        out.append((ec, msg[-1500:], cmds.get(b.get('tool_use_id'), '')))
    else:
        for line in opener(trace):
            if '"item.completed"' not in line or 'command_execution' not in line:
                continue
            try:
                it = json.loads(line)['item']
            except ValueError:
                continue
            if it.get('type') != 'command_execution':
                continue
            ec, msg = it.get('exit_code'), it.get('aggregated_output') or ''
            if ec not in (0, None) and not (ec == 1 and not msg.strip()):
                out.append((ec, msg[-1500:], it.get('command') or ''))
    return out


def galaxy_error_jobs():
    """Every Galaxy job in the error state, by run: (error type, tool id), classified from the archived job record."""
    import glob
    err = {j['native_job_id']: j for j in A['jobs'] if j['status'] == 'error'}
    rec = {}
    for d in ('BixBench_50', 'CompBio', 'IWC'):
        for f in glob.glob(os.path.join(ROOT, d, 'analysis', '*', 'source_snapshots', 'galaxy', '*', 'jobs', '*.json')):
            jid = os.path.basename(f)[:-5]
            if jid in err and jid not in rec:
                j = json.load(open(f))
                msg = '\n'.join(str(j.get(k) or '') for k in ('tool_stderr', 'job_stderr', 'stderr', 'tool_stdout', 'stdout'))
                jm = j.get('job_messages')
                msg = (msg + '\n' + (jm if isinstance(jm, str) else json.dumps(jm))).strip() if jm and jm != '[]' else msg.strip()
                rec[jid] = 'not_started' if not msg and not j.get('command_line') else classify_error(msg, None)
    assert len(rec) == len(err), (len(rec), len(err))
    by_run = collections.defaultdict(list)
    for jid, j in err.items():
        for ref in j['refs']:
            by_run[(j['benchmark'], ref['task'], ref['run_id'])].append((rec[jid], j['tool']))
    return by_run


def od_fig5(n_boot=20000, seed=20260929):
    """Execution errors by type and whether runs recovered from them (the run still ended correct), per benchmark."""
    from matplotlib.lines import Line2D
    key = compbio_key()
    sums = {(s['benchmark'], s['task'], s['run_id']): s for s in map(json.loads, gzip.open(
        os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt'))}
    gjobs = galaxy_error_jobs()
    runs, excluded, errs = [], collections.Counter(), []
    for r in A['runs']:
        b = r['benchmark']
        if r['model'] == 'codex_gpt_6_astra' or (b == 'IWC' and r['task'] == IWC_UNMATCHED):
            continue
        s = sums[(b, r['task'], r['run_id'])]
        if not s.get('trace'):
            excluded[(b, 'no execution trace')] += 1
            continue
        if r['condition'] == 'galaxy' and r['jobs'] is None:
            excluded[(b, 'no detailed analysis history')] += 1
            continue
        if b == 'BixBench50':
            ok = r['score'] == 1
        elif b == 'CompBio':
            ok = (r['answer'] or '').replace('Proximal enhancer,EH38E1957012', 'pELS,EH38E1957012').strip() == key[r['task']]
        else:
            ok = r['score'] >= 0.95
        sf = shell_failures(s['trace'])
        if 'claude' not in s['trace']:  # cross-check: failures + silent exit-1 results = archived non-zero exits
            assert len(sf) <= s['n_shell_nonzero'], (b, r['task'], r['run_id'])
        gj = gjobs.get((b, r['task'], r['run_id']), []) if r['condition'] == 'galaxy' else []
        assert len(gj) == (r['errors'] or 0 if r['condition'] == 'galaxy' else 0), (b, r['task'], r['run_id'])
        x = dict(benchmark=b, config=MODEL_ALL[r['model']], condition=r['condition'], task=r['task'], replicate=r['replicate'],
                 cluster=r['cluster'] if b == 'BixBench50' else r['task'], ok=bool(ok), n_shell=len(sf), n_job=len(gj))
        x['types'] = collections.Counter([classify_error(m, ec, c) for ec, m, c in sf] + [t for t, _ in gj])
        runs.append(x)
        for ec, m, c in sf:
            errs.append(dict(benchmark=b, model_configuration=ROW[x['config']].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[x['condition']],
                             task=x['task'], replicate=x['replicate'], channel='shell command', error_type=dict(ERROR_TYPES)[classify_error(m, ec, c)].replace('\n', ' '),
                             exit_code=ec, run_ended_correct=x['ok']))
        for t, tool in gj:
            errs.append(dict(benchmark=b, model_configuration=ROW[x['config']].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[x['condition']],
                             task=x['task'], replicate=x['replicate'], channel='Galaxy job', error_type=dict(ERROR_TYPES)[t].replace('\n', ' '),
                             tool=tool, run_ended_correct=x['ok']))
    rng = np.random.default_rng(seed)
    TYPES = [k for k, _ in ERROR_TYPES]

    def recovered(rr, types=None):
        """Share of errors (of the given types) that occurred in runs that still ended correct, with a cluster-bootstrap interval."""
        cl = collections.defaultdict(lambda: np.zeros(2))
        for x in rr:
            n = sum(x['types'][t] for t in (types or TYPES))
            cl[x['cluster']] += [n * x['ok'], n]
        arr = np.array(list(cl.values()))
        if arr[:, 1].sum() == 0:
            return float('nan'), float('nan'), float('nan'), 0
        t = arr[rng.integers(0, len(arr), size=(n_boot, len(arr)))].sum(1)
        with np.errstate(invalid='ignore', divide='ignore'):
            d = 100 * t[:, 0] / t[:, 1]
        return 100 * arr[:, 0].sum() / arr[:, 1].sum(), *np.nanpercentile(d, [2.5, 97.5]), int(arr[:, 1].sum())

    PANELS = [('IWC', 'IWC', CONFIGS), ('BixBench50', 'BixBench-Verified-50', CFG5), ('CompBio', 'CompBioBench', CONFIGS)]
    fig = plt.figure(figsize=(W_DOUBLE, 170 * MM))
    tops = {'IWC': 0.99, 'BixBench50': 0.69, 'CompBio': 0.39}
    rows_type, rows_model = [], []
    MIN_N = 10
    for p_i, (b, bl, cfgs) in enumerate(PANELS):
        top = tops[b]
        h = 0.2
        a_top = top - 0.05
        axA = fig.add_axes([0.205, a_top - h, 0.25, h])
        axB = fig.add_axes([0.48, a_top - h, 0.15, h])
        axC = fig.add_axes([0.805, a_top - h * len(cfgs) / 7 - 0.0, 0.17, h * len(cfgs) / 7])
        n_runs = {e: sum(1 for x in runs if x['benchmark'] == b and x['condition'] == e) for e in ENVS}
        per_run = {e: {t: sum(x['types'][t] for x in runs if x['benchmark'] == b and x['condition'] == e) / n_runs[e] for t in TYPES} for e in ENVS}
        xmax = max(max(v.values()) for v in per_run.values())
        for i, t in enumerate(TYPES):
            for e, dy in zip(ENVS, (-0.19, 0.19)):
                v = per_run[e][t]
                axA.barh(i + dy, v, height=0.36, color=ENV_COLOR[e], lw=0)
                axA.text(v + xmax * 0.02, i + dy, f'{v:.2f}' if v else '0', va='center', fontsize=5.0, color=INK if v else INK2)
                est, lo, hi, n = recovered([x for x in runs if x['benchmark'] == b and x['condition'] == e], [t])
                if n >= MIN_N:
                    axB.errorbar(est, i + dy, xerr=[[est - lo], [hi - est]], fmt=ENV_MARKER[e], ms=3.2, mfc=ENV_COLOR[e], mec='white', mew=0.4,
                                 ecolor=ENV_COLOR[e], elinewidth=0.7, capsize=0, zorder=3, clip_on=False)
                elif n:
                    axB.text(3, i + dy, f'{n} errors, too few', va='center', fontsize=5.0, color=INK2)
                rows_type.append(dict(benchmark=bl, execution_condition=ENV_LABEL_LONG[e], error_type=dict(ERROR_TYPES)[t].replace('\n', ' '), errors=n,
                                      runs=n_runs[e], errors_per_run=round(v, 3), recovered_percent=round(est, 1) if n else None,
                                      ci95_low=round(lo, 1) if n >= MIN_N else None, ci95_high=round(hi, 1) if n >= MIN_N else None))
        for ax in (axA, axB):
            ax.set_yticks(range(len(TYPES))); ax.tick_params(axis='y', length=0); ax.set_ylim(len(TYPES) - 0.45, -0.55); grid_x(ax)
        axA.set_yticklabels([l for _, l in ERROR_TYPES], fontsize=5.2, linespacing=1.0); axB.set_yticklabels([])
        axA.set_xlim(0, xmax * 1.18); axA.set_xlabel('Errors per run (mean)')
        axB.set_xlim(0, 100); axB.set_xticks([0, 50, 100]); axB.set_xlabel('Errors recovered (%)')
        # by model configuration, all error types
        for i, cfg in enumerate(cfgs):
            for e, dy in zip(ENVS, (-0.17, 0.17)):
                rr = [x for x in runs if x['benchmark'] == b and x['condition'] == e and x['config'] == cfg]
                est, lo, hi, n = recovered(rr)
                axC.errorbar(est, i + dy, xerr=[[est - lo], [hi - est]], fmt=ENV_MARKER[e], ms=3.2, mfc=ENV_COLOR[e], mec='white', mew=0.4,
                             ecolor=ENV_COLOR[e], elinewidth=0.7, capsize=0, zorder=3, clip_on=False)
                rows_model.append(dict(benchmark=bl, model_configuration=ROW[cfg].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[e], runs=len(rr),
                                       errors=n, errors_per_run=round(n / len(rr), 3), recovered_percent=round(est, 1), ci95_low=round(lo, 1),
                                       ci95_high=round(hi, 1), runs_ended_correct=sum(x['ok'] for x in rr)))
        axC.set_yticks(range(len(cfgs))); axC.set_yticklabels([ROW[c] for c in cfgs], fontsize=5.2, linespacing=1.0)
        axC.tick_params(axis='y', length=0); axC.set_ylim(len(cfgs) - 0.5, -0.5); axC.set_xlim(0, 100); axC.set_xticks([0, 50, 100]); grid_x(axC)
        axC.set_xlabel('Errors recovered (%)')
        for ax, x0, lab in ((axA, 0.205, 'What went wrong: errors per run, by type'), (axB, 0.48, 'Recovered, by type'),
                            (axC, 0.66, 'Recovered, by model configuration')):
            fig.text(x0 if ax is not axC else 0.66, a_top + 0.008, lab, fontsize=5.5, fontweight='bold', va='bottom')
        tot = {e: sum(sum(x['types'].values()) for x in runs if x['benchmark'] == b and x['condition'] == e) for e in ENVS}
        rec = {e: recovered([x for x in runs if x['benchmark'] == b and x['condition'] == e]) for e in ENVS}
        top_t = {e: max(TYPES, key=lambda t: per_run[e][t]) for e in ENVS}
        lab = lambda t: dict(ERROR_TYPES)[t].replace('\n', ' ').lower().replace('galaxy', 'Galaxy')
        eg, ec = tot['galaxy'] / n_runs['galaxy'], tot['open_ended_code'] / n_runs['open_ended_code']
        cmp_ = 'about as many errors as' if abs(eg - ec) < 0.05 * ec else ('fewer errors than' if eg < ec else 'more errors than')
        title = (f"{bl}: Galaxy runs had {cmp_} open-ended code runs ({eg:.2f} versus {ec:.2f} per run) "
                 f"and recovered from {rec['galaxy'][0]:.0f}% versus {rec['open_ended_code'][0]:.0f}% of them")
        panel_label(fig, 0.005, top, 'abc'[p_i]); panel_title(fig, 0.005, top, title)
    fig.legend(handles=[Line2D([], [], marker=ENV_MARKER[e], ls='-', lw=0.7, color=ENV_COLOR[e], ms=3.6, mfc=ENV_COLOR[e], mec='white', mew=0.4,
                               label=ENV_LABEL_LONG[e]) for e in ENVS], loc='lower left', bbox_to_anchor=(0.005, 0.068), ncol=2, fontsize=5.3)
    ex_txt = '; '.join(f"{n} {dict((pb, pl) for pb, pl, _ in PANELS)[bb]} ({why})" for (bb, why), n in sorted(excluded.items()))
    note = ("Error: a shell command that exited with a non-zero code (a silent exit code 1, such as a search with no match, is not counted) or a Galaxy "
            "analysis job that ended in the error state. Its type comes from its error message (ordered rules in fig_on_demand.ERROR_RULES; Galaxy job "
            "messages from the archived job records); 'Galaxy job never started' is a job with neither a command line nor output. Recovered: the error "
            "occurred in a run that still ended correct (BixBench-Verified-50 scored correct; CompBioBench exact match to the reference key; IWC output "
            f"agreement 0.95 or above, nine tasks). Bars: errors per run; points: share recovered with 95% cluster-bootstrap interval (source capsules for "
            f"BixBench-Verified-50, tasks otherwise; 20,000 resamples), shown when at least {MIN_N} errors. Excluded: {ex_txt}; GPT-6 Astra.")
    fig.text(0.005, 0.062, textwrap.fill(note, 220), fontsize=5.0, color=INK2, va='top', linespacing=1.25)
    save(fig, 'OD_Fig5_execution_errors_solved', 'Execution errors by type and recovery, per benchmark and model configuration')
    source_data('OD_Fig5', {'abc_errors_by_type': pd.DataFrame(rows_type), 'abc_recovery_by_model': pd.DataFrame(rows_model),
                            'abc_every_error': pd.DataFrame(errs),
                            'abc_runs': pd.DataFrame([dict(benchmark=dict((pb, pl) for pb, pl, _ in PANELS)[x['benchmark']],
                                                           model_configuration=ROW[x['config']].replace('\n', ' '), execution_condition=ENV_LABEL_LONG[x['condition']],
                                                           task=x['task'], replicate=x['replicate'], failed_shell_commands=x['n_shell'],
                                                           galaxy_jobs_in_error_state=x['n_job'], ended_correct=x['ok'],
                                                           **{dict(ERROR_TYPES)[t].replace('\n', ' '): x['types'][t] for t in TYPES}) for x in runs])})
    return rows_type, rows_model


# =====================================================================================================
PLANNING_TOOLS = {'TaskCreate', 'TaskUpdate', 'TaskList', 'TaskGet', 'TodoWrite'}  # planning-list updates, like Codex todo_list items


def trace_actions(trace):
    """Actions (tool calls) in one execution trace, by kind: shell, galaxy (Galaxy interface), web, file, other."""
    opener = lambda p: gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')
    c = collections.Counter()
    if 'claude' in os.path.basename(trace):
        for line in opener(trace):
            if '"tool_use"' not in line:
                continue
            try:
                content = (json.loads(line).get('message') or {}).get('content')
            except ValueError:
                continue
            for b in content if isinstance(content, list) else []:
                n = b.get('name') or ''
                if b.get('type') != 'tool_use' or n in PLANNING_TOOLS:
                    continue
                if n.startswith('mcp__'):
                    c['galaxy' if 'galaxy' in n else 'other'] += 1
                else:
                    c[{'Bash': 'shell', 'BashOutput': 'shell', 'TaskOutput': 'shell', 'KillShell': 'shell', 'TaskStop': 'shell',
                       'WebSearch': 'web', 'WebFetch': 'web', 'Agent': 'other', 'SearchMcpTool': 'other'}.get(n, 'file')] += 1
    else:
        for line in opener(trace):
            if '"item.completed"' not in line:
                continue
            try:
                it = json.loads(line)['item']
            except ValueError:
                continue
            ty = it.get('type')
            if ty == 'command_execution':
                c['shell'] += 1
            elif ty == 'mcp_tool_call':
                c['galaxy' if 'galaxy' in (it.get('server') or '').lower() else 'other'] += 1
            elif ty == 'web_search':
                c['web'] += 1
            elif ty == 'file_change':
                c['file'] += 1
    return c


def od_fig6(seed=11, n_boot=20000):
    """Actions per run: a, Galaxy / open-ended code ratio for every model configuration and benchmark; b-f, box plots per model
    configuration with the three benchmarks side by side and a paired test per benchmark."""
    from matplotlib.lines import Line2D
    from scipy import stats
    sums = {(s['benchmark'], s['task'], s['run_id']): s for s in map(json.loads, gzip.open(
        os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt'))}
    runs, no_trace, mismatch = [], collections.Counter(), 0
    for r in A['runs']:
        if r['model'] == 'codex_gpt_6_astra':
            continue
        s = sums[(r['benchmark'], r['task'], r['run_id'])]
        if not s.get('trace'):
            no_trace[r['benchmark']] += 1
            continue
        c = trace_actions(s['trace'])
        if 'claude' not in s['trace']:  # cross-check against the archive's per-run interface-call counts (shell + MCP + web)
            mismatch += abs(c['shell'] + c['galaxy'] + c['other'] + c['web'] - sum((r['interface_calls'] or {}).values())) > 1
        runs.append(dict(benchmark=r['benchmark'], config=MODEL_ALL[r['model']], condition=r['condition'], task=r['task'], replicate=r['replicate'],
                         cluster=r['cluster'] if r['benchmark'] == 'BixBench50' else r['task'],
                         actions=sum(c.values()), **{k: c.get(k, 0) for k in ('shell', 'galaxy', 'web', 'file', 'other')}))
    assert mismatch == 0, mismatch
    BEN = [('IWC', 'IWC'), ('BixBench50', 'BixBench-Verified-50'), ('CompBio', 'CompBioBench')]
    BL = dict(BEN)
    ran = {(b, c) for b, c in {(x['benchmark'], x['config']) for x in runs}}
    rng = np.random.default_rng(seed)
    tests = []
    for b, bl in BEN:
        for cfg in CFG5:
            if (b, cfg) not in ran:
                continue
            rr = [x for x in runs if x['benchmark'] == b and x['config'] == cfg]
            med = collections.defaultdict(dict)
            for e in ENVS:
                per = collections.defaultdict(list)
                for x in rr:
                    if x['condition'] == e:
                        per[x['task']].append(x['actions'])
                for t, v in per.items():
                    med[t][e] = st.median(v)
            pairs = [(v['galaxy'], v['open_ended_code']) for v in med.values() if len(v) == 2]
            w = stats.wilcoxon([g - c for g, c in pairs], alternative='two-sided')
            g_all = [x['actions'] for x in rr if x['condition'] == 'galaxy']
            c_all = [x['actions'] for x in rr if x['condition'] == 'open_ended_code']
            # 95% cluster-bootstrap interval of the ratio of medians (tasks, or source capsules for BixBench, resampled with both conditions)
            cl = sorted({x['cluster'] for x in rr})
            pad = {e: [[x['actions'] for x in rr if x['cluster'] == k and x['condition'] == e] for k in cl] for e in ENVS}
            arr = {}
            for e in ENVS:
                m = max(len(v) for v in pad[e])
                arr[e] = np.array([v + [np.nan] * (m - len(v)) for v in pad[e]], float)
            idx = rng.integers(0, len(cl), size=(n_boot, len(cl)))
            with np.errstate(invalid='ignore', divide='ignore'):
                ratio_b = np.nanmedian(arr['galaxy'][idx].reshape(n_boot, -1), 1) / np.nanmedian(arr['open_ended_code'][idx].reshape(n_boot, -1), 1)
            lo, hi = np.nanpercentile(ratio_b[np.isfinite(ratio_b)], [2.5, 97.5])
            tests.append(dict(benchmark=b, config=cfg, tasks=len(pairs), median_galaxy=st.median(g_all), median_code=st.median(c_all),
                              ratio=st.median(g_all) / st.median(c_all), ratio_lo=lo, ratio_hi=hi, tasks_galaxy_more=sum(g > c for g, c in pairs),
                              W=w.statistic, p=w.pvalue))
    for t_, pa in zip(tests, holm([t_['p'] for t_ in tests])):
        t_['p_holm'] = pa
    T = {(t_['benchmark'], t_['config']): t_ for t_ in tests}
    plt.rcParams.update({'mathtext.fontset': 'custom', 'mathtext.rm': 'Arial', 'mathtext.it': 'Arial:italic', 'mathtext.bf': 'Arial:bold',
                         'mathtext.bfit': 'Arial:italic:bold', 'mathtext.cal': 'Arial', 'mathtext.sf': 'Arial', 'mathtext.tt': 'Arial'})
    P, PB = r'$\mathit{P}$', r'$\mathbfit{P}$'
    plab = lambda p: f"{'<' if p < 0.001 else '='} {fmt_p(p).lstrip('<')}"
    fig = plt.figure(figsize=(W_DOUBLE, 170 * MM))
    # ---- a: ratio of median actions, Galaxy / open-ended code, every model configuration and benchmark
    nsig = {b: (sum(T[(b, c)]['p_holm'] < 0.05 for c in CFG5 if (b, c) in T), sum(1 for c in CFG5 if (b, c) in T)) for b, _ in BEN}
    panel_label(fig, 0.005, 0.99, 'a')
    panel_title(fig, 0.005, 0.99, 'Every model configuration needed more actions in the Galaxy condition on every benchmark; the difference was significant in '
                                   f"all {nsig['BixBench50'][1] + nsig['CompBio'][1]} comparisons on\nBixBench-Verified-50 and CompBioBench and in "
                                   f"{nsig['IWC'][0] or 'none'} of the {nsig['IWC'][1]} on IWC (ten tasks)")
    rows_a = []
    for k, (b, bl) in enumerate(BEN):
        ax = fig.add_axes([0.175 + k * 0.275, 0.785, 0.15, 0.135])
        for i, cfg in enumerate(CFG5):
            if (b, cfg) not in T:
                ax.text(0.5, i, 'Not run with this\nagent harness', transform=ax.get_yaxis_transform(), ha='center', va='center', fontsize=5.0,
                        color=INK2, linespacing=1.0)
                continue
            t_ = T[(b, cfg)]
            sig = t_['p_holm'] < 0.05
            ax.plot([t_['ratio_lo'], t_['ratio_hi']], [i, i], color=INK, lw=0.8, zorder=2)
            ax.plot(t_['ratio'], i, 'D', ms=3.6, mfc=INK if sig else 'white', mec=INK, mew=0.8, zorder=3)
            ax.text(1.04, i, f"{t_['ratio']:.1f}×  {PB if sig else P} {plab(t_['p_holm'])}", transform=ax.get_yaxis_transform(), fontsize=5.0, va='center',
                    color=INK if sig else INK2, fontweight='bold' if sig else 'normal')
            rows_a.append(dict(benchmark=bl, model_configuration=ROW[cfg].replace('\n', ' '), paired_tasks=t_['tasks'],
                               median_actions_open_ended_code=t_['median_code'], median_actions_galaxy=t_['median_galaxy'],
                               median_ratio_galaxy_over_code=round(t_['ratio'], 3), ratio_ci95_low=round(t_['ratio_lo'], 3), ratio_ci95_high=round(t_['ratio_hi'], 3),
                               tasks_with_more_galaxy_actions=t_['tasks_galaxy_more'], wilcoxon_W=t_['W'], p_two_sided=t_['p'], p_holm=t_['p_holm']))
        ax.axvline(1, color=INK2, lw=0.6, zorder=1)
        ax.set_xscale('log'); ax.set_xlim(0.7, 6); ax.set_xticks([1, 2, 4]); ax.set_xticklabels(['1', '2', '4']); ax.xaxis.set_minor_locator(plt.NullLocator())
        ax.set_yticks(range(len(CFG5))); ax.set_yticklabels([ROW[c] for c in CFG5] if k == 0 else [], fontsize=5.2, linespacing=1.0)
        ax.tick_params(axis='y', length=0); ax.set_ylim(len(CFG5) - 0.5, -0.6); grid_x(ax)
        ax.set_xlabel('Median actions, Galaxy ÷ open-ended code')
        ax.set_title(bl, fontsize=6, loc='left', pad=3)
    fig.legend(handles=[Line2D([], [], marker='D', ls='-', lw=0.8, color=INK, ms=3.6, mfc=INK, mec=INK, label=f'Significant (Holm-adjusted {P} < 0.05)'),
                        Line2D([], [], marker='D', ls='-', lw=0.8, color=INK, ms=3.6, mfc='white', mec=INK, label='Not significant')],
               loc='upper right', bbox_to_anchor=(0.995, 0.972), ncol=2, fontsize=5.2)
    # ---- b-f: one panel per model configuration, benchmarks side by side
    slots = [(0.065, 0.43), (0.395, 0.43), (0.725, 0.43), (0.065, 0.1), (0.395, 0.1)]
    rows_b = []
    for p_i, cfg in enumerate(CFG5):
        x0, y0 = slots[p_i]
        ax = fig.add_axes([x0, y0, 0.255, 0.215])
        for g, (b, bl) in enumerate(BEN):
            if (b, cfg) not in T:
                ax.text(g, 3, 'Not run with\nthis agent\nharness', ha='center', va='center', fontsize=5.0, color=INK2, linespacing=1.05)
                continue
            for e, dx in zip(ENVS, (-0.19, 0.19)):
                v = np.array([x['actions'] for x in runs if x['benchmark'] == b and x['config'] == cfg and x['condition'] == e])
                bp = ax.boxplot(v, positions=[g + dx], widths=0.3, whis=1.5, showfliers=False, patch_artist=True, manage_ticks=False)
                for bx in bp['boxes']:
                    bx.set(facecolor=ENV_TINT[e], edgecolor=ENV_COLOR[e], lw=0.6)
                for part in ('whiskers', 'caps'):
                    for ln in bp[part]:
                        ln.set(color=ENV_COLOR[e], lw=0.6)
                for ln in bp['medians']:
                    ln.set(color=INK, lw=0.9)
                ax.plot(g + dx + rng.uniform(-0.1, 0.1, len(v)), v, ENV_MARKER[e], ms=1.1, mfc=ENV_COLOR[e], mec='none', alpha=0.5, zorder=3)
                q1, med, q3 = np.percentile(v, [25, 50, 75])
                rows_b.append(dict(model_configuration=ROW[cfg].replace('\n', ' '), benchmark=bl, execution_condition=ENV_LABEL_LONG[e], runs=len(v),
                                   median_actions=med, q1=q1, q3=q3, min=int(v.min()), max=int(v.max()),
                                   median_shell_commands=st.median([x['shell'] for x in runs if x['benchmark'] == b and x['config'] == cfg and x['condition'] == e]),
                                   median_galaxy_interface_calls=st.median([x['galaxy'] for x in runs if x['benchmark'] == b and x['config'] == cfg and x['condition'] == e])))
            t_ = T[(b, cfg)]
            sig = t_['p_holm'] < 0.05
            ax.plot([g - 0.19, g - 0.19, g + 0.19, g + 0.19], [2300, 2700, 2700, 2300], color=INK if sig else INK2, lw=0.5)
            ax.text(g, 3000, f"{t_['ratio']:.1f}×, {PB if sig else P} {plab(t_['p_holm'])}", ha='center', va='bottom', fontsize=5.0,
                    color=INK if sig else INK2, fontweight='bold' if sig else 'normal')
        ax.set_yscale('symlog', linthresh=1, linscale=0.25); ax.set_ylim(0, 9000)
        ax.set_yticks([0, 1, 10, 100, 1000]); ax.set_yticklabels(['0', '1', '10', '100', '1,000']); ax.yaxis.set_minor_locator(plt.NullLocator())
        ax.set_xlim(-0.6, 2.6); ax.set_xticks(range(3)); ax.set_xticklabels(['IWC', 'BixBench-\nVerified-50', 'CompBioBench'], fontsize=5.3, linespacing=1.0)
        ax.tick_params(axis='x', length=0); grid_y(ax)
        if x0 < 0.1:
            ax.set_ylabel('Actions per run (log scale above 1)')
        done = [(b, T[(b, cfg)]) for b, _ in BEN if (b, cfg) in T]
        more = sum(t_['ratio'] > 1 for _, t_ in done)
        sigc = [BL[b] for b, t_ in done if t_['p_holm'] < 0.05]
        if len(done) == 1:
            sub = f"Galaxy needed {done[0][1]['ratio']:.1f} times as many actions\n(BixBench-Verified-50 only)"
        else:
            sub = (f"Galaxy needed more actions on {'all ' + str(len(done)) if more == len(done) else f'{more} of {len(done)}'} benchmarks;\n"
                   f"significant on {len(sigc)} ({', '.join(sigc) if sigc else 'none'})")
        panel_label(fig, x0 - 0.06, y0 + 0.285, 'bcdef'[p_i])
        fig.text(x0 - 0.042, y0 + 0.284, ROW[cfg].replace('\n', ' '), fontsize=6.5, fontweight='bold', va='top')
        fig.text(x0 - 0.042, y0 + 0.263, sub, fontsize=5.2, color=INK2, va='top', linespacing=1.25)
    fig.legend(handles=[Patch(fc=ENV_TINT[e], ec=ENV_COLOR[e], lw=0.6, label=ENV_LABEL_LONG[e]) for e in ENVS], loc='upper left',
               bbox_to_anchor=(0.72, 0.335), ncol=1, fontsize=5.3, labelspacing=0.8)
    tot_nt = ', '.join(f"{n} {BL[bb]}" for bb, n in no_trace.items())
    side = ("Action: one tool call by the agent (shell command, Galaxy interface call, web search or fetch, file read, write or edit); planning-list "
            "updates and reasoning steps are not counted. Boxes: middle 50% of runs and median; whiskers: 1.5 times the interquartile range; points: runs "
            "(squares open-ended code, circles Galaxy). Ratio: median actions, Galaxy ÷ open-ended code, with a 95% cluster-bootstrap interval (tasks, or "
            "source capsules for BixBench-Verified-50; 20,000 resamples). § value: two-sided Wilcoxon signed-rank test on per-task median actions (each "
            f"task paired across conditions), Holm-adjusted over the {len(tests)} comparisons. IWC: all ten tasks. Excluded: runs without an execution "
            f"trace ({tot_nt}), GPT-6 Astra.")
    fig.text(0.725, 0.27, textwrap.fill(side, 56).replace('§', P), fontsize=5.0, color=INK2, va='top', linespacing=1.25)
    save(fig, 'OD_Fig6_actions_per_run', 'Actions per run from start to end of a task, per model configuration and benchmark')
    source_data('OD_Fig6', {'a_ratio_galaxy_over_code': pd.DataFrame(rows_a), 'b_f_box_summary': pd.DataFrame(rows_b),
                            'abf_runs': pd.DataFrame([dict(benchmark=BL[x['benchmark']], model_configuration=ROW[x['config']].replace('\n', ' '),
                                                           execution_condition=ENV_LABEL_LONG[x['condition']], task=x['task'], replicate=x['replicate'],
                                                           actions=x['actions'], shell_commands=x['shell'], galaxy_interface_calls=x['galaxy'],
                                                           web_searches_or_fetches=x['web'], file_reads_writes_edits=x['file'], other_tool_calls=x['other'])
                                                      for x in runs])})
    return tests


# =====================================================================================================
UDT_AUDIT = os.path.join(OUT, 'udt_audit', 'udt_error_audit.jsonl')
UDT_CATS = [('UDT_EXECUTION', 'The UDT failed to run, and the failure\ncaused the wrong answer'),
            ('UDT_CODE', "The UDT ran, but the agent's code in it\ncomputed the wrong quantity"),
            ('BEFORE_UDT', 'Error before the UDT (its inputs\nwere already wrong)'),
            ('AFTER_UDT', 'Error after the UDT (its output\nwas right)'),
            ('UDT_FAILED_NOT_DECISIVE', 'The UDT failed, but the fallback made\nthe same error (failure not decisive)'),
            ('NOT_ON_PATH', 'The UDT was not on the path to the\nanswer (side task only)'),
            ('REFERENCE_OR_EVALUATOR', 'No execution error: the answer is\ndefensible (reference or evaluator)')]
UDT_STEP = {'UDT_EXECUTION', 'UDT_CODE'}


def od_fig7(n_boot=20000, seed=20260929):
    """User-defined tools (UDTs) and accuracy in the Galaxy condition (UDTs were not offered for IWC tasks).
    a, forest plot: accuracy difference with - without a UDT, within task (Mantel-Haenszel), per model configuration and pooled.
    b, accuracy by UDT trajectory: no UDT, UDT job succeeded, every UDT job failed; incorrect runs split by where the error happened.
    c, where the error happened in every scored-incorrect UDT run, laid out along the run's stages (trace-level audit)."""
    from matplotlib.lines import Line2D
    from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle
    key = compbio_key()
    sums = {(s['benchmark'], s['task'], s['run_id']): s for s in map(json.loads, gzip.open(
        os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt'))}
    audit = {(x['benchmark'], x['task'], x['run_id']): x for x in map(json.loads, open(UDT_AUDIT))}
    BEN = [('BixBench50', 'BixBench-Verified-50', CFG5), ('CompBio', 'CompBioBench', CONFIGS)]
    BL = {b: bl for b, bl, _ in BEN}
    runs, no_trace = [], 0
    for r in A['runs']:
        b = r['benchmark']
        if r['condition'] != 'galaxy' or b not in BL:
            continue
        if not sums[(b, r['task'], r['run_id'])].get('trace'):
            no_trace += 1  # UDT use cannot be observed without the execution trace
            continue
        ok = r['score'] == 1 if b == 'BixBench50' else \
            (r['answer'] or '').replace('Proximal enhancer,EH38E1957012', 'pELS,EH38E1957012').strip() == key[r['task']]
        udt = bool(r['udt_requested'])
        x = dict(benchmark=b, task=r['task'], run_id=r['run_id'], config=MODEL_ALL[r['model']], replicate=r['replicate'], udt=udt, correct=bool(ok),
                 cluster=r['cluster'] if b == 'BixBench50' else r['task'], udt_requests=r['udt_request_count'] or 0,
                 trajectory=('no UDT' if not udt else ('not recorded' if r['jobs'] is None else ('succeeded' if r['udt_matched_success_ids'] else 'all failed'))))
        if udt and not ok:
            x.update({k: audit[(b, r['task'], r['run_id'])][k] for k in ('category', 'udt_role', 'answer_source', 'confidence', 'rationale',
                                                                          'decisive_error_lines', 'udt_lines')})
        runs.append(x)
    assert sum(1 for x in runs if x['udt'] and not x['correct']) == len(audit) == 130
    rng = np.random.default_rng(seed)

    def mh(rr, stratum):
        """Mantel-Haenszel risk difference (UDT - no UDT, points) within strata, with a cluster bootstrap (strata nest in clusters)."""
        st_ = collections.defaultdict(lambda: np.zeros(4))
        for x in rr:
            st_[(x['cluster'], stratum(x))] += [x['correct'] * x['udt'], x['udt'], x['correct'] * (1 - x['udt']), 1 - x['udt']]
        per = collections.defaultdict(lambda: np.zeros(2))
        informative = 0
        for (cl, _), (a, n1, c, n0) in st_.items():
            if n1 and n0:
                per[cl] += [(a * n0 - c * n1) / (n1 + n0), n1 * n0 / (n1 + n0)]
                informative += 1
        clusters = sorted({x['cluster'] for x in rr})
        arr = np.array([per[c] if c in per else np.zeros(2) for c in clusters])
        t = arr[rng.integers(0, len(arr), size=(n_boot, len(arr)))].sum(1)
        with np.errstate(invalid='ignore', divide='ignore'):
            d = 100 * t[:, 0] / t[:, 1]
        est = 100 * arr[:, 0].sum() / arr[:, 1].sum() if arr[:, 1].sum() else float('nan')
        return est, *np.nanpercentile(d, [2.5, 97.5]), informative

    fig = plt.figure(figsize=(W_DOUBLE, 170 * MM))
    rows_a, rows_b, rows_c = [], [], []
    # ---- a: forest plot
    pooled = {}
    for k, (b, bl, cfgs) in enumerate(BEN):
        ax = fig.add_axes([0.2 + k * 0.415, 0.74, 0.15, 0.165])
        labels = CFG5 + ['All model configurations']
        for i, cfg in enumerate(labels):
            y = i + (0.35 if cfg == labels[-1] else 0)
            if cfg not in cfgs and cfg != labels[-1]:
                ax.text(0, y, 'Not run with this agent harness', ha='center', va='center', fontsize=5.0, color=INK2,
                        bbox=dict(boxstyle='square,pad=0.15', fc='white', ec='none'), zorder=4)
                continue
            rr = [x for x in runs if x['benchmark'] == b and (cfg == labels[-1] or x['config'] == cfg)]
            est, lo, hi, inf = mh(rr, (lambda x: (x['task'], x['config'])) if cfg == labels[-1] else (lambda x: x['task']))
            acc = {u: 100 * np.mean([x['correct'] for x in rr if x['udt'] == u]) for u in (False, True)}
            n = {u: sum(x['udt'] == u for x in rr) for u in (False, True)}
            if cfg == labels[-1]:
                pooled[b] = (est, lo, hi)
                ax.add_patch(Polygon([[lo, y], [est, y - 0.32], [hi, y], [est, y + 0.32]], closed=True, fc=GALAXY, ec=GALAXY, lw=0.6, zorder=3))
            elif lo == hi == est == 0:
                ax.plot(0, y, 's', ms=3.2, mfc='white', mec=GALAXY, mew=0.8, zorder=3)
            else:
                ax.plot([lo, hi], [y, y], color=GALAXY, lw=0.8, zorder=2)
                ax.plot(est, y, 's', ms=3.4 * (0.75 + 0.5 * min(inf, 30) / 30), mfc=GALAXY, mec=GALAXY, zorder=3)
            ci = (f"0.0 (same in all {inf} tasks)" if lo == hi == est == 0 else f"{signed(est)} ({signed(lo)} to {signed(hi)})")
            ax.text(1.05, y, ci, transform=ax.get_yaxis_transform(), fontsize=5.0, va='center', fontweight='bold' if cfg == labels[-1] else 'normal')
            ax.text(2.0, y, f"{acc[True]:.0f}% / {acc[False]:.0f}%", transform=ax.get_yaxis_transform(), fontsize=5.0, va='center', color=INK2)
            rows_a.append(dict(benchmark=bl, model_configuration=cfg if cfg == labels[-1] else ROW[cfg].replace('\n', ' '), runs_with_udt=n[True],
                               runs_without_udt=n[False], accuracy_with_udt=round(acc[True], 2), accuracy_without_udt=round(acc[False], 2),
                               raw_difference=round(acc[True] - acc[False], 2), within_task_difference_mantel_haenszel=round(est, 2),
                               ci95_low=round(lo, 2), ci95_high=round(hi, 2),
                               strata=('task x model configuration' if cfg == labels[-1] else 'task'), strata_with_both=inf))
        ax.axvline(0, color=INK, lw=0.7, zorder=1)
        ax.axhline(len(CFG5) - 0.35, color=GRID, lw=0.6)
        ax.set_xlim(-30, 30); ax.set_xticks([-20, -10, 0, 10, 20])
        ax.set_xticklabels(['−20', '−10', '0', '+10', '+20']); grid_x(ax)
        ax.set_yticks([i + (0.35 if c == labels[-1] else 0) for i, c in enumerate(labels)])
        ax.set_yticklabels([ROW[c] if c in ROW else c for c in labels] if k == 0 else [], fontsize=5.2, linespacing=1.0)
        if k == 0:
            ax.get_yticklabels()[-1].set_fontweight('bold')
        ax.tick_params(axis='y', length=0); ax.set_ylim(len(labels) - 0.25, -0.65)
        ax.set_xlabel('Accuracy with − without a UDT,\nsame task (percentage points)\n← lower with a UDT    higher →', linespacing=1.15)
        ax.set_title(bl, fontsize=6, loc='left', pad=4)
        ax.text(1.05, -0.75, 'Difference (95% CI)', transform=ax.get_yaxis_transform(), fontsize=5.0, fontweight='bold', va='bottom')
        ax.text(2.0, -0.75, 'Accuracy, UDT /\nno UDT runs', transform=ax.get_yaxis_transform(), fontsize=5.0, fontweight='bold', va='bottom',
                linespacing=1.1)
    panel_label(fig, 0.005, 0.99, 'a')
    panel_title(fig, 0.005, 0.99, 'Requesting a UDT was not associated with lower accuracy once the task is held fixed: pooled difference '
                                   f"{signed(pooled['BixBench50'][0])} points\n({signed(pooled['BixBench50'][1])} to {signed(pooled['BixBench50'][2])}; "
                                   f"BixBench-Verified-50) and {signed(pooled['CompBio'][0])} points ({signed(pooled['CompBio'][1])} to "
                                   f"{signed(pooled['CompBio'][2])}; CompBioBench)")
    # ---- b: accuracy by UDT trajectory
    TRAJ = [('no UDT', 'No UDT requested'), ('succeeded', 'UDT requested; a UDT\njob succeeded'),
            ('all failed', 'UDT requested; every\nUDT job failed'), ('not recorded', 'UDT requested; job\noutcome not recorded')]
    SEG = [('correct', 'Correct', GALAXY), ('udt_step', 'Incorrect: error at the UDT step', OI_ORANGE),
           ('elsewhere', 'Incorrect: error elsewhere (not related to UDT use)', NEUTRAL_MID), ('no_udt_wrong', 'Incorrect (no UDT)', NEUTRAL_LIGHT)]
    acc_traj = {}
    for k, (b, bl, cfgs) in enumerate(BEN):
        ax = fig.add_axes([0.2 + k * 0.415, 0.425, 0.25, 0.14])
        shown = [(t, lab) for t, lab in TRAJ if sum(x['benchmark'] == b and x['trajectory'] == t for x in runs) >= 5]
        for i, (t, lab) in enumerate(shown):
            rr = [x for x in runs if x['benchmark'] == b and x['trajectory'] == t]
            cnt = collections.Counter('correct' if x['correct'] else ('no_udt_wrong' if t == 'no UDT' else
                                                                     ('udt_step' if x['category'] in UDT_STEP else 'elsewhere')) for x in rr)
            left = 0
            for sk, _, col in SEG:
                v = 100 * cnt.get(sk, 0) / len(rr)
                if v:
                    ax.barh(i, v, left=left, height=0.62, color=col, ec='white', lw=0.5)
                    if sk == 'correct':
                        ax.text(left + 2, i, f'{v:.0f}% correct', va='center', ha='left', fontsize=5.0, color='white', fontweight='bold')
                    elif cnt[sk] and v >= 4:
                        ax.text(left + v / 2, i, str(cnt[sk]), va='center', ha='center', fontsize=5.0, color='white' if sk != 'no_udt_wrong' else INK)
                left += v
            ax.text(101.5, i, f'n = {len(rr)}', va='center', fontsize=5.0, color=INK2)
            acc_traj[(b, t)] = 100 * cnt.get('correct', 0) / len(rr)
            rows_b.append(dict(benchmark=bl, trajectory=lab.replace('\n', ' '), runs=len(rr), correct=cnt.get('correct', 0),
                               incorrect_error_at_udt_step=cnt.get('udt_step', 0), incorrect_error_elsewhere=cnt.get('elsewhere', 0),
                               incorrect_no_udt=cnt.get('no_udt_wrong', 0), percent_correct=round(acc_traj[(b, t)], 2)))
        for t, lab in TRAJ:  # rows too small to plot (fewer than 5 runs) are kept in Source Data
            rr = [x for x in runs if x['benchmark'] == b and x['trajectory'] == t]
            if rr and (t, lab) not in shown:
                cnt = collections.Counter('correct' if x['correct'] else ('udt_step' if x['category'] in UDT_STEP else 'elsewhere') for x in rr)
                rows_b.append(dict(benchmark=bl, trajectory=lab.replace('\n', ' '), runs=len(rr), correct=cnt.get('correct', 0),
                                   incorrect_error_at_udt_step=cnt.get('udt_step', 0), incorrect_error_elsewhere=cnt.get('elsewhere', 0),
                                   incorrect_no_udt=0, percent_correct=round(100 * cnt.get('correct', 0) / len(rr), 2), plotted=False))
        ax.set_yticks(range(len(shown))); ax.set_yticklabels([lab for _, lab in shown], fontsize=5.2, linespacing=1.0)
        ax.tick_params(axis='y', length=0); ax.set_ylim(len(shown) - 0.45, -0.55)
        ax.set_xlim(0, 100); ax.set_xticks(range(0, 101, 25)); ax.set_xlabel('Galaxy-condition runs (%)'); grid_x(ax)
        ax.set_title(bl, fontsize=6, loc='left', pad=4)
    fig.legend(handles=[Patch(fc=col, ec='white' if col != NEUTRAL_LIGHT else INK2, lw=0.4, label=lab) for _, lab, col in SEG],
               loc='upper left', bbox_to_anchor=(0.2, 0.62), ncol=4, fontsize=5.2, columnspacing=1.2)
    panel_label(fig, 0.005, 0.655, 'b')
    panel_title(fig, 0.005, 0.655, f"Runs whose UDT jobs succeeded were at least as accurate as runs without a UDT ({acc_traj[('BixBench50', 'succeeded')]:.0f}% versus "
                                   f"{acc_traj[('BixBench50', 'no UDT')]:.0f}%; {acc_traj[('CompBio', 'succeeded')]:.0f}% versus "
                                   f"{acc_traj[('CompBio', 'no UDT')]:.0f}%; BixBench-Verified-50, CompBioBench);\nwhen every UDT job failed, most runs still "
                                   f"reached a correct answer by another route ({acc_traj[('CompBio', 'all failed')]:.0f}% of 240 CompBioBench runs)")
    # ---- c: where the error happened, along the run's stages (layout after the stage-ordered taxonomy of Cemri et al., 2025)
    axc = fig.add_axes([0.0, 0.085, 1.0, 0.22]); axc.axis('off'); axc.set_xlim(0, 1); axc.set_ylim(0, 1)
    bad = {b: [x for x in runs if x['benchmark'] == b and x['udt'] and not x['correct']] for b, _, _ in BEN}
    cc = {b: collections.Counter(x['category'] for x in bad[b]) for b in bad}
    BOXES = [('BEFORE_UDT', 'Before the UDT\n(its inputs were\nalready wrong)'), ('UDT_EXECUTION', 'UDT failed to run,\nand that changed\nthe answer'),
             ('UDT_CODE', "UDT ran; agent's\ncode in it computed\nthe wrong quantity"), ('AFTER_UDT', 'After the UDT\n(its output was\nright)'),
             ('UDT_FAILED_NOT_DECISIVE', 'UDT failed, but\nthe fallback made\nthe same error'), ('NOT_ON_PATH', 'UDT was only a\nside task (probe,\nconversion)'),
             ('REFERENCE_OR_EVALUATOR', 'No execution error:\nanswer defensible\n(reference or\nevaluator)')]
    W, Y0, H = 0.125, 0.03, 0.73
    gaps = [0.0, 0.024, 0.008, 0.024, 0.032, 0.008, 0.008]
    xs, x = [], 0.012
    for g in gaps:
        x += g
        xs.append(x)
        x += W
    for (cat, lab), x in zip(BOXES, xs):
        hi = cat in UDT_STEP
        axc.add_patch(FancyBboxPatch((x, Y0), W, H, boxstyle='round,pad=0,rounding_size=0.012', fc='#FBE7C2' if hi else 'white',
                                     ec=OI_ORANGE if hi else INK2, lw=0.9 if hi else 0.5, transform=axc.transAxes, zorder=1))
        axc.text(x + 0.007, Y0 + H - 0.035, lab, fontsize=5.2, fontweight='bold', va='top', ha='left', linespacing=1.05, zorder=3)
        for j, (b, bl, _) in enumerate(BEN):
            n = cc[b].get(cat, 0); frac = n / len(bad[b])
            yb = Y0 + H * (0.42 if j == 0 else 0.13)
            axc.text(x + 0.007, yb + 0.05, bl, fontsize=5.0, color=INK2, va='bottom', ha='left', zorder=3)
            axc.add_patch(Rectangle((x + 0.007, yb - 0.025), W * 0.4, 0.05, fc=GRID, ec='none', transform=axc.transAxes, zorder=2))
            if n:
                axc.add_patch(Rectangle((x + 0.007, yb - 0.025), W * 0.4 * frac, 0.05, fc=OI_ORANGE if hi else NEUTRAL_MID, ec='none',
                                        transform=axc.transAxes, zorder=3))
            axc.text(x + 0.012 + W * 0.4, yb, f"{n}/{len(bad[b])} ({100 * frac:.0f}%)", fontsize=5.0, va='center', ha='left', zorder=3,
                     color=INK if n else INK2, fontweight='bold' if hi and n else 'normal')
    for i in (0, 2):
        axc.annotate('', xy=(xs[i + 1] - 0.003, Y0 + H / 2), xytext=(xs[i] + W + 0.003, Y0 + H / 2), xycoords='axes fraction',
                     arrowprops=dict(arrowstyle='-|>', color=INK2, lw=0.8, mutation_scale=7))
    def bracket(x0, x1, y, lab, col, bold=True):
        axc.plot([x0, x0, x1, x1], [y - 0.03, y, y, y - 0.03], color=col, lw=0.8, transform=axc.transAxes, clip_on=False)
        axc.text((x0 + x1) / 2, y + 0.015, lab, fontsize=5.4, fontweight='bold' if bold else 'normal', ha='center', va='bottom', color=INK)
    bracket(xs[1], xs[2] + W, Y0 + H + 0.04, 'At the UDT step', OI_ORANGE)
    bracket(xs[0], xs[3] + W, Y0 + H + 0.14, 'Along the answer path', INK2)
    bracket(xs[4], xs[6] + W, Y0 + H + 0.14, 'Off the answer path, or no execution error: not related to UDT use', INK2)
    for b, bl, _ in BEN:
        for cat, lab in UDT_CATS:
            rows_c.append(dict(benchmark=bl, where_the_error_happened=lab.replace('\n', ' '), category_code=cat, runs=cc[b].get(cat, 0),
                               percent_of_incorrect_udt_runs=round(100 * cc[b].get(cat, 0) / len(bad[b]), 2), incorrect_udt_runs=len(bad[b]),
                               high_confidence=sum(1 for x in bad[b] if x['category'] == cat and x['confidence'] == 'high'),
                               counted_as=('at the UDT step' if cat in UDT_STEP else 'not related to UDT use')))
    step = {b: sum(cc[b].get(c, 0) for c in UDT_STEP) for b in bad}
    panel_label(fig, 0.005, 0.37, 'c')
    panel_title(fig, 0.005, 0.37, f"In scored-incorrect UDT runs the error lay at the UDT step in {100 * step['BixBench50'] / len(bad['BixBench50']):.0f}% "
                                   f"(BixBench-Verified-50) and {100 * step['CompBio'] / len(bad['CompBio']):.0f}% (CompBioBench); most of those were the "
                                   "agent's analysis\nwritten into the UDT, and the UDT mechanism itself failed in "
                                   f"{cc['BixBench50'].get('UDT_EXECUTION', 0) + cc['CompBio'].get('UDT_EXECUTION', 0)} of "
                                   f"{len(bad['BixBench50']) + len(bad['CompBio'])}")
    note = ("Galaxy condition only; UDTs (user-defined tools: agent-written code that Galaxy runs as a job) were not offered for IWC tasks (0 of 120 runs). "
            f"Runs without an execution trace are excluded ({no_trace} CompBioBench). a, Mantel–Haenszel risk difference within task (each model "
            "configuration; square size grows with the number of informative tasks) or within task × model configuration (diamond); 95% percentile "
            "cluster bootstrap (source capsules for BixBench-Verified-50, tasks for CompBioBench; 20,000 resamples). b, UDT job outcome from the "
            "archived analysis history (rows with fewer than 5 runs are in Source Data only: BixBench-Verified-50, every UDT job failed, 4 runs; "
            "CompBioBench, outcome not recorded, 1 run); error location from c. c, Trace-level audit of all 130 scored-incorrect UDT runs against a fixed codebook "
            "(on_demand/udt_audit/; layout after the stage-ordered failure taxonomy of Cemri et al., 2025).")
    fig.text(0.005, 0.072, textwrap.fill(note, 220), fontsize=5.0, color=INK2, va='top', linespacing=1.25)
    save(fig, 'OD_Fig7_udt_and_accuracy', 'User-defined tools and accuracy in the Galaxy condition')
    source_data('OD_Fig7', {'a_forest_within_task': pd.DataFrame(rows_a), 'b_accuracy_by_udt_trajectory': pd.DataFrame(rows_b),
                            'c_where_error_happened': pd.DataFrame(rows_c),
                            'c_audit_per_run': pd.DataFrame([dict(benchmark=BL[x['benchmark']], task=x['task'], run_id=x['run_id'],
                                                                  model_configuration=ROW[x['config']].replace('\n', ' '), category=x['category'], udt_role=x['udt_role'],
                                                                  answer_source=x['answer_source'], confidence=x['confidence'],
                                                                  decisive_error_lines='; '.join(map(str, x['decisive_error_lines'])),
                                                                  udt_lines='; '.join(map(str, x['udt_lines'])), rationale=x['rationale'])
                                                             for x in runs if x['udt'] and not x['correct']]),
                            'abc_runs': pd.DataFrame([{k: v for k, v in x.items() if k in ('task', 'run_id', 'replicate', 'udt', 'correct', 'udt_requests', 'trajectory')}
                                                      | dict(benchmark=BL[x['benchmark']], model_configuration=ROW[x['config']].replace('\n', ' '))
                                                      for x in runs])})
    return rows_a, rows_b, rows_c


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    od_fig1()
    r2, four, five = od_fig2()
    pair, within = od_fig3()
    for x in pair:
        print(x['execution_condition'], x['config'], round(x['ratio'], 2), f"p={x['p']:.3g} holm={x['p_holm']:.3g}", f"CI=({x['ratio_ci_low']:.2f}, {x['ratio_ci_high']:.2f})")
    for e, v in within.items():
        print('within', e, v['n_sets'], round(v['ratio'], 2), round(v['p'], 3))
    od_fig4()
    od_fig5()
    od_fig6()
    od_fig7()
    print('wrote', sorted(os.listdir(OUT)))
