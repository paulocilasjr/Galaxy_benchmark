"""On-demand figures (not part of the submitted display items) and their Source Data.

Run from the repository root:  COMPBIO_KEY_DIR=<folder> python manuscript_material/scripts/fig_on_demand.py
Writes to manuscript_material/on_demand/:
  OD_Fig1  primary cause of every scored-incorrect run, by how many of the three replicate runs were scored incorrect
  OD_Fig2  unanimous accuracy (3/3 replicate runs scored correct) per model configuration, open-ended code then Galaxy
  OD_Fig3  input-token usage per run, scored-correct versus scored-incorrect, per model configuration and condition
  OD_Fig4  majority-vote accuracy per model configuration and condition: pooled (a) and by benchmark (b)
Figs 1-3 use BixBench-Verified-50 only. Inputs are the archived files build_data.py reads (analysis.json, the failure
ledger, run_summaries.jsonl.gz); figure_data.json is not changed. All five BixBench model configurations are pooled where
pooling is needed, as in Fig. 4b. Fig. 4 also grades CompBioBench runs against the lab's score-inferred answer key, read
from COMPBIO_KEY_DIR (kept outside this repository so that agents run from it cannot read the key).
"""
import collections
import gzip
import json
import os
import statistics as st
import sys
import textwrap

import numpy as np
import pandas as pd
from matplotlib.patches import Patch

sys.path.insert(0, os.path.dirname(__file__))
from style import (CFG_LABEL, CONFIGS, ENV_COLOR, ENV_LABEL, ENV_LABEL_LONG, ENV_MARKER, ENV_TINT, ENVS, INK, INK2, MM,  # noqa: E402
                   SUPERSEDED, W_DOUBLE, enforce_min_font, grid_x, grid_y, panel_label, panel_title, plt)

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
    print('wrote', sorted(os.listdir(OUT)))
