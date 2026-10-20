#!/usr/bin/env python3
"""Every number the Brief Communication cites, computed from its sources and written with them to numbers.json.

Sources:
- the run archive (this repository): figures/scored_runs.csv (site-matched scores, IWC wf_007 as replaced on the results
  site on 2026-10-12) and the figure source data of figures/make_fig2.py and make_fig5.py (fig2, ed_fig2, ed_fig6, fig5);
- data/ in this folder: tables copied from goeckslab/agent-galaxy-benchmark-manuscript (see data/SOURCES.json) and the
  outputs of scripts/replicate_consensus.py rerun on them.

The 90% intervals for the post hoc equivalence check use the paper's cluster bootstrap (BixBench source capsules,
otherwise tasks; 20,000 resamples; seed 20261002).
Usage: python scripts/compute_numbers.py
"""
import json
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BC = os.path.dirname(HERE)
ARCHIVE = os.path.abspath(os.path.join(BC, '..', '..', '..', '..'))
FIG = os.path.join(ARCHIVE, 'figures')
DATA = os.path.join(BC, 'data')
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
N = {}


def put(key, value, source):
    N[key] = dict(value=value, source=source)


def boot_diff(d, value, level, seed=20261002, B=20000):
    cl = d.groupby(['cluster', 'env'])[value].agg(['sum', 'count']).unstack('env')
    sg, ng = cl[('sum', 'galaxy')].values, cl[('count', 'galaxy')].values
    sc, nc = cl[('sum', 'open_ended_code')].values, cl[('count', 'open_ended_code')].values
    w = np.random.default_rng(seed).multinomial(len(cl), np.full(len(cl), 1 / len(cl)), size=B)
    draws = 100 * ((w @ sg) / (w @ ng) - (w @ sc) / (w @ nc))
    a = (100 - level) / 2
    return float(np.percentile(draws, a)), float(np.percentile(draws, 100 - a)), len(cl)


def main():
    r = pd.read_csv(os.path.join(FIG, 'scored_runs.csv'))
    r['ok'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(float)
    src_runs = 'figures/scored_runs.csv'
    put('runs', len(r), src_runs)
    put('tasks', int(r.task.nunique()), src_runs)
    put('tasks_by_benchmark', r.groupby('benchmark').task.nunique().to_dict(), src_runs)

    # ---- accuracy: condition values (runs accepted; IWC mean agreement), pooled differences and intervals
    f2 = pd.read_csv(os.path.join(FIG, 'fig2_source_data.csv'))
    b = f2[(f2.panel == 'b') & f2.measure.str.contains('mean_score_difference')]
    for bm in ('BixBench50', 'CompBio', 'IWC'):
        d = r[r.benchmark == bm]
        val = 'score' if bm == 'IWC' else 'ok'
        m = d.groupby('env')[val].mean()
        scale = 1 if bm == 'IWC' else 100
        put(f'{bm}_custom_code', float(m.open_ended_code * scale), src_runs)
        put(f'{bm}_galaxy', float(m.galaxy * scale), src_runs)
        row = b[(b.benchmark == bm) & (b.model == 'all four')].iloc[0]
        put(f'{bm}_diff', dict(est=row.value, lo=row.ci95_low, hi=row.ci95_high, p=row.p),
            'figures/fig2_source_data.csv, panel b (Galaxy - custom code, all four models; 95% cluster bootstrap; '
            'paired cluster sign-flip P)')
        lo, hi, k = boot_diff(d, val, 90)
        put(f'{bm}_diff_ci90', dict(lo=lo, hi=hi, clusters=k), 'scripts/compute_numbers.py cluster bootstrap (90%)')
        put(f'{bm}_runs_correct', dict(custom_code=float(100 * d[d.env == 'open_ended_code'].ok.mean()),
                                      galaxy=float(100 * d[d.env == 'galaxy'].ok.mean())), src_runs)
    pm = b[b.model != 'all four']
    put('per_model_min_holm', dict(p_holm=float(pm.p_holm.min()),
                                   where=pm.loc[pm.p_holm.idxmin(), ['benchmark', 'model']].tolist()),
        'figures/fig2_source_data.csv, panel b (12 model comparisons, Holm)')
    put('per_model_outside_5', int(((pm.ci95_low < -5) | (pm.ci95_high > 5)).sum()), 'figures/fig2_source_data.csv')

    # ---- robustness
    e2 = pd.read_csv(os.path.join(FIG, 'ed_fig2_source_data.csv'))
    pop = e2[e2.measure.str.contains('population sensitivity')]
    for g in pop.itertuples():
        put(f'sens_{g.group}', dict(est=g.value, lo=g.ci95_low, hi=g.ci95_high, clusters=g.n, p=g.p),
            'figures/ed_fig2_source_data.csv, panel b')
    e6 = pd.read_csv(os.path.join(FIG, 'ed_fig6_source_data.csv'))
    ex = e6[e6.group.astype(str).str.contains('Without')]
    for g in ex.itertuples():
        put(f'exposure_{g.benchmark}_{g.group}', dict(est=g.value, lo=g.ci95_low, hi=g.ci95_high, runs=g.n),
            'figures/ed_fig6_source_data.csv, panel b')
    # Galaxy runs whose answer the integrity audit traced to local analysis, or with no successful Galaxy job
    v = pd.read_csv(os.path.join(ARCHIVE, 'analysis', 'integrity_audit', 'violations.csv'))
    out = v[(v.run_set == 'primary') & (v.condition == 'galaxy') & v.category.str.startswith(
        ('Computation ran outside Galaxy (trace evidence', 'Answered without any successful Galaxy analysis job'))]
    key = set(zip(out.benchmark, out.task, out.model, out.replicate))
    put('galaxy_runs_local_or_no_job', dict(runs=len(key), by_benchmark=out.drop_duplicates(
        ['benchmark', 'task', 'model', 'replicate']).benchmark.value_counts().to_dict()),
        'analysis/integrity_audit/violations.csv (primary Galaxy runs; automatic trace detections)')
    flag = [(b_, t_, c_, rep) in key and e_ == 'galaxy' for b_, t_, c_, e_, rep in
            zip(r.benchmark, r.task, r.cfg, r.env, r.replicate)]
    kept = r[~np.array(flag)]
    for bm in ('BixBench50', 'CompBio'):
        d = kept[kept.benchmark == bm]
        m = d.groupby('env').ok.mean()
        lo, hi, k = boot_diff(d, 'ok', 95)
        put(f'sens_{bm}_without_local_galaxy_runs', dict(est=float(100 * (m.galaxy - m.open_ended_code)), lo=lo, hi=hi,
                                                         runs_removed=int((r.benchmark == bm).sum() - len(d))),
            'scripts/compute_numbers.py (cluster bootstrap, 95%)')
    allr = e6[(e6.group.astype(str) == 'All runs')]
    exp_runs = {bm: int(allr[allr.benchmark == bm].n.iloc[0] - ex[(ex.benchmark == bm) &
                (ex.group.str.contains('verified or probable'))].n.iloc[0]) for bm in ('BixBench50', 'CompBio')}
    put('exposure_runs_removed', dict(exp_runs, total=sum(exp_runs.values())), 'figures/ed_fig6_source_data.csv')

    # ---- errors (BixBench-Verified-50 failure-cause audit) and replicate agreement
    c = pd.read_csv(os.path.join(DATA, 'bixbench_failure_causes.csv'))
    put('bix_incorrect', len(c), 'data/bixbench_failure_causes.csv')
    put('bix_primary_causes', c.primary_cause.value_counts().to_dict(), 'data/bixbench_failure_causes.csv')
    rigor_any = (c.primary_cause == 'RIGOR') | c.secondary_cause.astype(str).str.contains('RIGOR')
    put('bix_rigor_primary_or_secondary', int(rigor_any.sum()), 'data/bixbench_failure_causes.csv')
    put('bix_spec_with_rigor_secondary', int(((c.primary_cause == 'SPEC') &
                                              c.secondary_cause.astype(str).str.contains('RIGOR')).sum()),
        'data/bixbench_failure_causes.csv')
    ag = pd.read_csv(os.path.join(DATA, 'bixbench_causes_by_agreement.csv'))
    t = ag.groupby(['primary_cause', 'correct_replicates_in_group']).incorrect_runs.sum().unstack(fill_value=0)
    put('bix_causes_by_agreement', {k: {int(j): int(v) for j, v in row.items()} for k, row in t.iterrows()},
        'data/bixbench_causes_by_agreement.csv (replicate_consensus.py)')
    q = pd.read_csv(os.path.join(DATA, 'replicate_consensus.csv'))
    cons = {}
    for row in q.itertuples():
        cons[f'{row.benchmark}|{row.track}'] = dict(
            single=100 * row.single_run_accuracy, vote=100 * row.majority_of_3_accuracy,
            any=100 * row.any_of_3_accuracy, twelve=100 * row.majority_of_12_accuracy,
            split=100 * (row.groups_2_of_3 + row.groups_1_of_3), incorrect=row.incorrect_runs,
            all_wrong=row.incorrect_in_all_wrong_groups)
    put('consensus', cons, 'data/replicate_consensus.csv (replicate_consensus.py rerun on PR #12 data)')
    put('vote_gain_max', max(v['vote'] - v['single'] for k, v in cons.items() if not k.startswith('IWC')),
        'data/replicate_consensus.csv')
    put('any_of_3_range', [min(v['any'] for v in cons.values()), max(v['any'] for v in cons.values())],
        'data/replicate_consensus.csv')

    # ---- what each condition records
    ins = pd.read_csv(os.path.join(DATA, 'inspectability_counts.csv'))
    put('inspectability', {f'{x.track}|{x.element}': dict(with_record=int(x.with_record), total=int(x.total))
                           for x in ins.itertuples()}, 'data/inspectability_counts.csv')

    # ---- tokens: main runs (results site) and interface stages (archive Fig. 5c)
    tm = pd.read_csv(os.path.join(DATA, 'token_ratios_main_runs.csv'))
    put('tokens_main_all_models', tm[tm.model == 'All models'].set_index('benchmark').ratio.to_dict(),
        'data/token_ratios_main_runs.csv (results-site totals, PR #14)')
    f5 = pd.read_csv(os.path.join(FIG, 'fig5_source_data.csv'))
    c5 = f5[(f5.panel == 'c')]
    stages = []
    for grp, g in c5.groupby('group', sort=False):
        if 'pct_change' in ' '.join(g.measure):
            continue
        row = dict(stage=grp)
        for x in g.itertuples():
            key = x.measure.split(' (')[0]
            row[key] = x.value
            if key.startswith('ratio'):
                row['ratio_lo'], row['ratio_hi'] = x.ci95_low, x.ci95_high
        stages.append(row)
    put('token_stages', stages, 'figures/fig5_source_data.csv, panel c (make_fig5.token_rounds)')
    ch = c5[c5.measure.str.contains('pct_change')]
    put('token_change', {x.group: dict(pct=x.value, lo=x.ci95_low, hi=x.ci95_high) for x in ch.itertuples()},
        'figures/fig5_source_data.csv, panel c')
    put('token_drivers_july6', dict(cached_share_galaxy=95, steps_ratio=2.66, steps_galaxy=37.9, steps_code=14.2,
                                    context_per_step_ratio=2.2),
        'goeckslab/agent-galaxy-benchmark-manuscript supplement/notes/token_usage.md (PR #14), 6 July experiment')

    json.dump(N, open(os.path.join(BC, 'numbers.json'), 'w'), indent=1, default=float)
    for k, v in N.items():
        print(k, json.dumps(v['value'], default=float)[:240])


if __name__ == '__main__':
    main()
