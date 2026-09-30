"""On-demand BixBench-Verified-50 figures (not part of the submitted display items) and their Source Data.

Run from the repository root:  python manuscript_material/scripts/fig_on_demand.py
Writes to manuscript_material/on_demand/:
  OD_Fig1  primary cause of every scored-incorrect run, by how many of the three replicate runs were scored incorrect
  OD_Fig2  unanimous accuracy (3/3 replicate runs scored correct) per model configuration, open-ended code then Galaxy
  OD_Fig3  input-token usage per run, scored-correct versus scored-incorrect, per model configuration and condition
Inputs are the archived files build_data.py reads (analysis.json, the failure ledger, run_summaries.jsonl.gz);
figure_data.json is not changed. All five BixBench model configurations are pooled where pooling is needed, as in Fig. 4b.
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
from style import (CFG_LABEL, CONFIGS, ENV_COLOR, ENV_LABEL, ENV_LABEL_LONG, ENV_TINT, ENVS, INK, INK2, MM, SUPERSEDED,  # noqa: E402
                   W_DOUBLE, enforce_min_font, grid_x, grid_y, panel_label, panel_title, plt)

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


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    od_fig1()
    r2, four, five = od_fig2()
    pair, within = od_fig3()
    for x in pair:
        print(x['execution_condition'], x['config'], round(x['ratio'], 2), f"p={x['p']:.3g} holm={x['p_holm']:.3g}", f"CI=({x['ratio_ci_low']:.2f}, {x['ratio_ci_high']:.2f})")
    for e, v in within.items():
        print('within', e, v['n_sets'], round(v['ratio'], 2), round(v['p'], 3))
    print('wrote', sorted(os.listdir(OUT)))
