#!/usr/bin/env python3
"""Supplementary Data 2: the run index, one row per run with links to its agent trace and Galaxy history.

Sheets:
- Primary runs: the 3,840 runs of the comparison (figures/scored_runs.csv, site-matched scores), with the results-site
  task page, the Hugging Face trace and, for Galaxy runs, the usegalaxy.org history. Links come from the archive's
  run-link workbooks (runs/*/..._execution_condition_links.xlsx, read from the results site), except the 24 IWC wf_007
  runs published on 2026-10-12, whose links come from data/site_links_wf007_replacement.csv (fetch_site_links.py).
- Replaced runs: the 53 CompBioBench originals replaced by the reviewed reruns of 2026-10-05 and the 24 superseded
  IWC wf_007 runs, with their links.
- Interface rounds: the BixBench-Verified-50 runs of Fig. 2d that are not primary runs, namely the 6 July 2026 GPT-5.5
  round-1 runs (data/site_links_july6_round1.csv) and the October 2026 GPT-5.6 Sol round-3 runs with longer waits
  (runs/token_optimization/). The round-2 GPT-5.5 runs and the archived GPT-5.6 Sol runs are primary runs.
If data/galaxy_history_check.csv exists (check_galaxy_histories.py), each history link carries its check result.
Writes supplementary/Supplementary_Data_2.xlsx and supplementary/Supplementary_Data_2_primary_runs.csv.
Usage: python scripts/make_run_index.py
"""
import json
import os

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BC = os.path.dirname(HERE)
ARCHIVE = os.path.abspath(os.path.join(BC, '..', '..', '..', '..'))
RUNS, DATA, OUT = os.path.join(ARCHIVE, 'runs'), os.path.join(BC, 'data'), os.path.join(BC, 'supplementary')
SITE = 'https://goeckslab.github.io/galaxy-agent-benchmark'
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
BENCH = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC-derived tasks'}
COND = {'galaxy': 'Galaxy', 'open_ended_code': 'Custom code'}
MODEL = {'Codex GPT-5.5': 'GPT-5.5', 'Codex GPT-5.6 Luna': 'GPT-5.6 Luna', 'Codex GPT-5.6 Sol': 'GPT-5.6 Sol',
         'DeepSeek V4 Pro via Codex': 'DeepSeek V4 Pro', 'Codex + DeepSeek-v4-pro-0813': 'DeepSeek V4 Pro',
         'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Luna': 'GPT-5.6 Luna', 'GPT-5.6 Sol': 'GPT-5.6 Sol',
         'Codex + DeepSeek V4 Pro': 'DeepSeek V4 Pro'}
ENV = {'Galaxy-API code with skills': 'galaxy', 'Open-ended code with skills': 'open_ended_code',
       'Galaxy-API code': 'galaxy', 'Open-ended code': 'open_ended_code'}
KEY = ['benchmark', 'task', 'cfg', 'env', 'replicate']
WORKBOOKS = {'BixBench50': ('BixBench_50/bixbench_execution_condition_links.xlsx', 'BixBench links'),
             'CompBio': ('CompBio/compbiobench_execution_condition_links.xlsx', 'CompBioBench links'),
             'IWC': ('IWC/iwc_execution_condition_links.xlsx', 'IWC links')}
WF007 = 'wf_007_vgp_mitogenome_assembly'


def workbook(bm, path=None):
    f, sheet = WORKBOOKS[bm]
    d = pd.read_excel(path or os.path.join(RUNS, f), sheet_name=sheet)
    d = d.rename(columns={'hugging_face_trace': 'run_trace'})
    d = d[d.model.isin(MODEL)].assign(benchmark=bm, cfg=lambda x: x.model.map(MODEL), env=lambda x: x.condition.map(ENV))
    assert d.env.notna().all()
    return d[KEY + ['task_page', 'run_trace', 'galaxy_history']]


def history_check():
    f = os.path.join(DATA, 'galaxy_history_check.csv')
    if not os.path.exists(f):
        return {}, {}
    c = pd.read_csv(f, dtype=str).fillna('')
    return dict(zip(c.url, c.status)), {u: h for u, h in zip(c.url, c.history_id) if h}


def label(d, check):
    d = d.copy()
    d['benchmark'] = d.benchmark.map(BENCH)
    d['condition'] = d.env.map(COND)
    if check:
        d['galaxy_history_check'] = [check.get(u, 'not checked') if isinstance(u, str) and u else ''
                                     for u in d.galaxy_history]
    return d


def primary(check, hid):
    r = pd.read_csv(os.path.join(ARCHIVE, 'figures', 'scored_runs.csv'))
    links = pd.concat([workbook(bm) for bm in WORKBOOKS], ignore_index=True)
    new = pd.read_csv(os.path.join(DATA, 'site_links_wf007_replacement.csv')).fillna('')
    old = links[(links.benchmark == 'IWC') & (links.task == WF007)]
    page = old.task_page.iloc[0]
    links = pd.concat([links.drop(old.index), new.assign(task_page=page)], ignore_index=True)
    d = r.merge(links, on=KEY, how='left', validate='one_to_one')
    assert len(d) == 3840 and d.run_trace.notna().all(), d[d.run_trace.isna()]
    d['galaxy_history'] = d.galaxy_history.fillna('')
    assert ((d.env == 'galaxy') == d.galaxy_history.fillna('').astype(bool)).all(), 'one history per Galaxy run'
    d['correct'] = d.score >= d.benchmark.map(CORRECT_AT) - 1e-9

    notes = {k: [] for k in map(tuple, d[KEY].values)}
    m = pd.read_csv(os.path.join(RUNS, 'CompBio', 'reruns_20261005', 'rerun_manifest.csv'))
    for x in m.itertuples():
        k = ('CompBio', x.task, x.cfg, 'galaxy', x.replicate)
        row = d[(d[KEY] == pd.Series(k, index=KEY)).all(axis=1)].iloc[0]
        assert row.run_trace == x.trace_url_rerun, k
        if row.galaxy_history != x.history_url_rerun:        # same history in another URL form, if the check resolves both
            same = hid.get(row.galaxy_history) == hid.get(x.history_url_rerun) is not None
            assert same or not hid, (k, row.galaxy_history, x.history_url_rerun)
        notes[k].append('Reviewed rerun of 5 October 2026; replaced the original run (sheet Replaced runs; '
                        'Supplementary Note 2)')
    for k in notes:
        if k[0] == 'IWC' and k[1] == WF007:
            notes[k].append('Run published by the results site on 12 October 2026 (read set ERR12833637); its '
                            'trace is not in the run archive (Supplementary Note 3)')
    scan = pd.read_csv(os.path.join(ARCHIVE, 'analysis', 'integrity_audit', 'scan_2026-10-14', 'runs.csv'))
    scan = scan[(scan.run_set == 'primary') & (scan.n_traces == 0)]
    for x in scan.itertuples():
        k = (x.benchmark, x.task, x.cfg, x.condition, x.replicate)
        if k in notes and not (k[0] == 'IWC' and k[1] == WF007):
            notes[k].append('No trace in the run archive; the link is the one the results site shows')
    shared = d[d.galaxy_history.astype(bool) & d.galaxy_history.duplicated(keep=False)]
    for h, g in shared.groupby('galaxy_history'):
        reps = ', '.join(f'replicate {v}' for v in g.replicate)
        for k in map(tuple, g[KEY].values):
            notes[k].append(f'The results site links one Galaxy history to {reps} of this task, model and condition, '
                            'and both traces work in it')
    d['note'] = ['; '.join(notes[k]) for k in map(tuple, d[KEY].values)]
    d = label(d, check)
    cols = ['benchmark', 'task', 'cfg', 'condition', 'replicate', 'score', 'correct', 'task_page', 'run_trace',
            'galaxy_history'] + (['galaxy_history_check'] if check else []) + ['note']
    return d[cols].rename(columns={'cfg': 'model', 'task_page': 'results_site_page', 'run_trace': 'agent_trace'}), \
        len(shared)


def replaced(check):
    pre = workbook('CompBio', os.path.join(RUNS, 'CompBio', 'reruns_20261005',
                                           'compbiobench_execution_condition_links.pre_rerun_20261005.xlsx'))
    m = pd.read_csv(os.path.join(RUNS, 'CompBio', 'reruns_20261005', 'rerun_manifest.csv'))
    m = m.assign(benchmark='CompBio', env='galaxy')
    a = m.merge(pre, on=KEY, how='left', validate='one_to_one').fillna({'galaxy_history': ''})
    assert len(a) == 53 and a.run_trace.notna().all()
    a = a.assign(score=a.score_original, replaced_on='2026-10-05', reason=a.reason,
                 replaced_by=a.trace_url_rerun)
    w = pd.read_csv(os.path.join(RUNS, 'IWC', 'replacement_wf007_20261012', 'runs.csv'))
    old = workbook('IWC')
    old = old[old.task == WF007]
    new = pd.read_csv(os.path.join(DATA, 'site_links_wf007_replacement.csv'))
    b = w.merge(old.fillna({'galaxy_history': ''}), on=KEY, how='left', validate='one_to_one').merge(
        new[KEY + ['run_trace']].rename(columns={'run_trace': 'replaced_by'}), on=KEY, how='left')
    assert len(b) == 24 and b.run_trace.notna().all() and b.replaced_by.notna().all()
    b = b.assign(score=b.superseded_score, replaced_on='2026-10-12',
                 reason='The results site reran the task on a second read set (ERR12833637)')
    d = pd.concat([a, b], ignore_index=True)
    d = label(d, check)
    cols = ['benchmark', 'task', 'cfg', 'condition', 'replicate', 'score', 'task_page', 'run_trace', 'galaxy_history'] \
        + (['galaxy_history_check'] if check else []) + ['replaced_on', 'reason', 'replaced_by']
    return d[cols].rename(columns={'cfg': 'model', 'task_page': 'results_site_page', 'run_trace': 'agent_trace',
                                   'replaced_by': 'replaced_by_agent_trace', 'score': 'score_of_replaced_run'})


def rounds(check):
    j = pd.read_csv(os.path.join(DATA, 'site_links_july6_round1.csv')).fillna('')
    snap = json.load(open(os.path.join(ARCHIVE, 'figures', 'site_snapshot', 'bixbench_july6_runs.json')))
    s = pd.DataFrame(snap['runs'])
    s = s[s.condition.isin(['galaxy_strict_skills', 'anycode_nongalaxy_skills'])]
    s = s.assign(task=s['item'], env=s.condition.map({'galaxy_strict_skills': 'galaxy',
                                                      'anycode_nongalaxy_skills': 'open_ended_code'}))
    j = j.merge(s[['task', 'env', 'replicate', 'passed']], on=['task', 'env', 'replicate'], how='left',
                validate='one_to_one')
    assert len(j) == 300 and j.passed.notna().all()
    j = j.assign(stage='July 2026, round 1', results_site_page=SITE + '/bixbench/july6/' + j.task + '/index.html')
    t = pd.read_csv(os.path.join(RUNS, 'token_optimization', 'token_optimization_runs.csv'))
    hf = 'https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces/tree/main/'
    o = pd.DataFrame(dict(benchmark='BixBench50', task=t.item_id, cfg='GPT-5.6 Sol', env='galaxy',
                          replicate=t.replicate, run_trace=hf + t.trace_path, galaxy_history=t.history_url,
                          passed=t.passed, stage='October 2026, round 3 with longer waits',
                          results_site_page=SITE + '/bixbench/token-optimization-oct2026/' + t.item_id + '/index.html'))
    assert len(o) == 150
    d = label(pd.concat([j, o], ignore_index=True), check)
    cols = ['stage', 'benchmark', 'task', 'cfg', 'condition', 'replicate', 'passed', 'results_site_page', 'run_trace',
            'galaxy_history'] + (['galaxy_history_check'] if check else [])
    return d[cols].rename(columns={'cfg': 'model', 'run_trace': 'agent_trace', 'passed': 'correct'})


def readme(n_shared, check):
    rows = [
        ('Contents', 'One row per run, with links to its agent trace and, for Galaxy runs, its Galaxy history.'),
        ('Primary runs', '3,840 runs: 160 tasks × 4 models × 2 conditions × 3 replicates. Scores are those shown on '
         'the results site (verified against the site on 14 October 2026). Correct: accepted (BixBench-Verified-50), '
         'agreeing with the answer key (CompBioBench) or output agreement ≥ 0.99 (IWC-derived tasks).'),
        ('Replaced runs', '53 CompBioBench Galaxy runs replaced by the reviewed reruns of 5 October 2026 and 24 IWC '
         'wf_007 runs replaced by the results site on 12 October 2026. They are not part of the comparison.'),
        ('Interface rounds', 'BixBench-Verified-50 runs of Fig. 2d that are not primary runs: the 6 July 2026 GPT-5.5 '
         'round-1 runs (both conditions) and the October 2026 GPT-5.6 Sol round-3 runs with longer waits (Galaxy). '
         'The round-2 GPT-5.5 runs and the archived GPT-5.6 Sol runs are primary runs. The single round-3 batch '
         'without longer waits has statistics only and no run links.'),
        ('results_site_page', 'Task page on the results site (https://goeckslab.github.io/galaxy-agent-benchmark/), '
         'which shows each run with its answer, grade and links.'),
        ('agent_trace', 'Folder of the run in the Hugging Face dataset goeckslab/galaxy-agent-benchmark-run-traces: '
         'the agent event log, prompt, submitted answer, usage and evaluation. Custom-code and Galaxy runs alike.'),
        ('galaxy_history', 'The usegalaxy.org history in which the Galaxy run worked: datasets, tools, versions, '
         'parameters and job states. Blank for custom-code runs.'),
        ('note', f'Reruns, replaced runs, runs without an archived trace and {n_shared} Galaxy runs that share a '
         'history link.'),
        ('Sources', 'Run archive https://github.com/paulocilasjr/Galaxy_benchmark: runs/*/'
         '*_execution_condition_links.xlsx, runs/CompBio/reruns_20261005/, runs/IWC/replacement_wf007_20261012/, '
         'runs/token_optimization/ and figures/scored_runs.csv; results-site pages read on the date in '
         'data/site_links_SOURCES.json of the manuscript build.'),
    ]
    if check:
        rows.append(('galaxy_history_check', 'Result of an unauthenticated request to usegalaxy.org on the date in '
                     'data/galaxy_history_check.csv: accessible (importable or published), not accessible, deleted '
                     'or purged.'))
    return pd.DataFrame(rows, columns=['Field', 'Description'])


def main():
    check, hid = history_check()
    p, n_shared = primary(check, hid)
    r, i = replaced(check), rounds(check)
    os.makedirs(OUT, exist_ok=True)
    with pd.ExcelWriter(os.path.join(OUT, 'Supplementary_Data_2.xlsx')) as xw:
        readme(n_shared, check).to_excel(xw, sheet_name='README', index=False)
        p.to_excel(xw, sheet_name='Primary runs', index=False)
        r.to_excel(xw, sheet_name='Replaced runs', index=False)
        i.to_excel(xw, sheet_name='Interface rounds', index=False)
    p.to_csv(os.path.join(OUT, 'Supplementary_Data_2_primary_runs.csv'), index=False)
    print(f'primary {len(p)} ({(p.condition == "Galaxy").sum()} Galaxy histories), replaced {len(r)}, '
          f'interface rounds {len(i)}; notes on {(p.note != "").sum()} primary runs; shared history links {n_shared}')
    if check:
        for name, d in (('primary', p), ('replaced', r), ('rounds', i)):
            print(name, d.galaxy_history_check.replace('', pd.NA).dropna().value_counts().to_dict())


if __name__ == '__main__':
    main()
