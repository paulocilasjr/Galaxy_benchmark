#!/usr/bin/env python3
"""Per-run scores for the result-evaluation figures, matched to the public results site.

Every scored primary run (four model configurations, two conditions, three replicates) gets the score the results site
displays (https://goeckslab.github.io/galaxy-agent-benchmark/):
- BixBench-Verified-50: the site's grade of each run (its BixBench table). It differs from the original evaluator
  (evaluation.json, the archive's accuracy_primary_runs.csv) on three items whose scoring the site corrected:
  bix-53-q2 ("increase" and equivalent statements accepted), bix-43-q2 (platform-specific two-decimal scoring) and
  bix-53-q5 (superseded harness only, not in this table). Cells are taken exactly as displayed.
- CompBioBench: unchanged. The archive's grades sum to the official-leaderboard score of every replicate, which is the
  site's headline score; the site's per-item table, which uses alternative references on seven items, is not used.
- IWC: the value shown for each run on the site's item pages. The host-read removal task (wf_003), excluded from the
  archive's primary comparison, is included with its run_record.json value (the site's value); the other nine tasks keep
  the archive's value, which the site displays.

The site results are read from site_snapshot/ (written by --fetch from the live site; no answers are stored). The script
checks every run against the snapshot and stops on any mismatch.

Writes scored_runs.csv: the columns of the archive's accuracy_primary_runs.csv, plus archive_score (the archive's value;
empty for wf_003) and score_source.

Usage: python result_evaluation/figures/make_scored_runs.py [--fetch]
"""
import glob
import html
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SITE = 'https://goeckslab.github.io/galaxy-agent-benchmark'
SNAP = os.path.join(HERE, 'site_snapshot')
ARCHIVE = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis', 'accuracy_primary_runs.csv')
DESIGN = os.path.join(ROOT, 'manuscript_narrative', 'derived', 'design', 'per_run_design_metadata.csv')
WF003 = 'wf_003_host_contamination_removal'
BIX_MODEL = {'Codex GPT-5.5': 'GPT-5.5', 'Sol': 'GPT-5.6 Sol', 'Luna': 'GPT-5.6 Luna', 'DeepSeek V4 Pro': 'DeepSeek V4 Pro',
             'DeepSeek preview': None}                       # superseded harness: not a primary configuration
IWC_MODEL = {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6 Sol', 'GPT-5.6 Luna': 'GPT-5.6 Luna',
             'Codex + DeepSeek V4 Pro': 'DeepSeek V4 Pro'}
RR_MODEL = {'gpt-5.5': 'GPT-5.5', 'gpt-5.6-sol': 'GPT-5.6 Sol', 'gpt-5.6-luna': 'GPT-5.6 Luna',
            'deepseek-v4-pro': 'DeepSeek V4 Pro'}
DESIGN_MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
                'codex_deepseek_v4_pro': 'DeepSeek V4 Pro'}


# ---------------------------------------------------------------- site snapshot
def get(url):
    return urllib.request.urlopen(url, timeout=120).read().decode('utf-8')


def text_lines(page):
    s = re.sub(r'<script.*?</script>|<style.*?</style>', '', page, flags=re.S)
    s = re.sub(r'<(br|/p|/tr|/h\d|/li|/div|/summary)[^>]*>', '\n', s)
    return [x.strip() for x in html.unescape(re.sub(r'<[^>]+>', '', s)).splitlines() if x.strip()]


def fetch_bixbench():
    """Grade of every run in the BixBench table of the site's index page (status only; answers are not kept)."""
    page, runs = get(f'{SITE}/index.html'), []
    table = next(t for t in re.findall(r'<table[^>]*>.*?</table>', page, flags=re.S) if 'data-item=' in t)
    head = re.findall(r'<tr>(.*?)</tr>', re.search(r'<thead>(.*?)</thead>', table, flags=re.S).group(1), flags=re.S)
    top = [(html.unescape(re.sub(r'<small>.*?</small>|<[^>]+>', '', c)).strip(), int((re.search(r'colspan="(\d+)"', a)
            or re.search('(1)', '1')).group(1)), 'rowspan' in a) for a, c in re.findall(r'<th([^>]*)>(.*?)</th>', head[0], flags=re.S)]
    sub = [html.unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in re.findall(r'<th[^>]*>(.*?)</th>', head[1], flags=re.S)]
    cols, k = [], 0
    for name, span, rowspan in top:
        if not rowspan:
            for _ in range(span):
                cols.append((name, sub[k]))
                k += 1
    for item, body in re.findall(r'<tr data-item="([^"]+)"[^>]*>(.*?)</tr>', table, flags=re.S):
        for (model, cond), td in zip(cols, re.findall(r'<td[^>]*>(.*?)</td>', body, flags=re.S)[2:]):
            for cls, label in re.findall(r'<span class="rep ([^"]+)"[^>]*aria-label="([^"]+)"', td):
                runs.append(dict(item=item, model=model, condition=cond,
                                 replicate=int(re.search(r'(?i)replicate (\d+)', label).group(1)),
                                 status=label.split(',')[1].strip(), passed=cls.split()[0] == 'pass'))
    return runs


def fetch_iwc():
    """Value shown for every run on the site's IWC item pages."""
    items = sorted(set(re.findall(r'href="(wf_[^/"]+)/index.html"', get(f'{SITE}/iwc/index.html'))))
    runs = []
    for item in items:
        lines = text_lines(get(f'{SITE}/iwc/{item}/index.html'))
        model = cond = None
        for i in range(next(i for i, x in enumerate(lines) if x.startswith('Model results')), len(lines)):
            x = lines[i]
            if x in IWC_MODEL:
                model = x
            elif x in ('Open-ended code', 'Galaxy-API code'):
                cond = x
            elif re.match(r'^R(\d)acc', x) and model and cond:
                value = next(v for v in lines[i + 1:i + 4] if re.match(r'^[01](\.\d+)?$', v))
                runs.append(dict(item=item, model=model, condition=cond, replicate=int(x[1]), value=value))
    return items, runs


def fetch_july6():
    """Grade of every run on the site's 6 July 2026 BixBench page (the round-1 batch of Fig. 5c), by condition."""
    page, runs = get(f'{SITE}/bixbench/july6/index.html'), []
    for item, cond, badges in re.findall(r'<a class="mini-link" href="([^/"]+)/index.html#([a-z_]+)">[^<]*</a>'
                                         r'<div class="rep-badges">(.*?)</div>', page, flags=re.S):
        for cls, rep in re.findall(r'<span class="rep ([a-z]+)"[^>]*>rep (\d+)</span>', badges):
            runs.append(dict(item=item, condition=cond, replicate=int(rep), passed=cls == 'pass'))
    return runs


def fetch():
    os.makedirs(SNAP, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    bix = fetch_bixbench()
    items, iwc = fetch_iwc()
    json.dump(dict(source=f'{SITE}/index.html (BixBench table)', retrieved_at_utc=stamp, runs=bix),
              open(os.path.join(SNAP, 'bixbench_runs.json'), 'w'), indent=0)
    json.dump(dict(source=f'{SITE}/iwc/<item>/index.html', retrieved_at_utc=stamp, items=items, runs=iwc),
              open(os.path.join(SNAP, 'iwc_runs.json'), 'w'), indent=0)
    july = fetch_july6()
    json.dump(dict(source=f'{SITE}/bixbench/july6/index.html', retrieved_at_utc=stamp, runs=july),
              open(os.path.join(SNAP, 'bixbench_july6_runs.json'), 'w'), indent=0)
    print(f'site snapshot: {len(bix)} BixBench runs, {len(iwc)} IWC runs, {len(july)} 6 July BixBench runs ({stamp})')


# ---------------------------------------------------------------- scored runs
def shown(value, displayed):
    """True when value prints as the site's displayed string (the site shows three decimals unless more are needed)."""
    nd = len(displayed.split('.')[1]) if '.' in displayed else 0
    return round(float(value), nd) == float(displayed)


def wf003_runs():
    """run_record.json acc of every host-read removal run (the value the site shows)."""
    rows = []
    for p in glob.glob(os.path.join(ROOT, 'IWC', 'analysis', WF003, 'source_snapshots', 'huggingface_traces', 'files', '*',
                                    'run_record.json')):
        rec = json.load(open(p))
        rows.append(dict(benchmark='IWC', task=WF003, cfg=RR_MODEL[rec['model']],
                         env='galaxy' if rec['condition'].startswith('galaxy') else 'open_ended_code',
                         replicate=int(rec['replicate']), score=float(rec['acc']), cluster=WF003,
                         run_id=os.path.basename(os.path.dirname(p))))
    assert len(rows) == 24, len(rows)
    return pd.DataFrame(rows)


def budget_matched(design):
    """IWC replicate pairs (same task, model and replicate) whose two conditions had the same wall-clock limit."""
    d = design[design.benchmark == 'IWC'].assign(cfg=lambda x: x.model.map(DESIGN_MODEL))
    lim = d.pivot_table(index=['task', 'cfg', 'replicate'], columns='condition', values='iwc_wall_clock_timeout_seconds')
    return (lim['galaxy'] == lim['open_ended_code']).rename('budget_matched')


def build():
    a = pd.read_csv(ARCHIVE)
    bix = pd.DataFrame(json.load(open(os.path.join(SNAP, 'bixbench_runs.json')))['runs'])
    iwc_snap = json.load(open(os.path.join(SNAP, 'iwc_runs.json')))
    iwc = pd.DataFrame(iwc_snap['runs'])
    key = ['task', 'cfg', 'env', 'replicate']

    # BixBench-Verified-50: the site's grade
    bix = bix.assign(cfg=bix.model.map(BIX_MODEL), task=bix['item'],
                     env=bix.condition.map({'Galaxy': 'galaxy', 'Open-ended code': 'open_ended_code'})).dropna(subset=['cfg'])
    site_bix = bix.set_index(key).passed.astype(float)
    b = a.benchmark == 'BixBench50'
    assert len(site_bix) == b.sum() == 1200
    a['archive_score'] = a.score
    a.loc[b, 'score'] = site_bix.reindex(pd.MultiIndex.from_frame(a.loc[b, key])).values
    assert a.loc[b, 'score'].notna().all()
    a['score_source'] = 'archive (shown on site)'
    a.loc[b & (a.score != a.archive_score), 'score_source'] = 'site regrade'
    a.loc[a.benchmark == 'CompBio', 'score_source'] = 'archive (official leaderboard; site headline)'

    # IWC: the archive's nine tasks as shown on the site, plus host-read removal from run_record.json
    iwc = iwc.assign(cfg=iwc.model.map(IWC_MODEL), task=iwc['item'],
                     env=iwc.condition.map({'Galaxy-API code': 'galaxy', 'Open-ended code': 'open_ended_code'}))
    shown_iwc = iwc.set_index(key).value
    assert len(shown_iwc) == 240 and len(iwc_snap['items']) == 10
    host = wf003_runs()
    flags = budget_matched(pd.read_csv(DESIGN, low_memory=False))
    old = a[a.benchmark == 'IWC'].join(flags, on=['task', 'cfg', 'replicate'], rsuffix='_design')
    assert (old.budget_matched.astype(bool) == old.budget_matched_design.astype(bool)).all(), 'budget rule must reproduce the archive'
    host = host.join(flags, on=['task', 'cfg', 'replicate'])
    host = host.assign(udt_requested_archive=False, bix_benchmark_side_task=False, compbio_outcome_named_cell=False,
                       iwc_zero_task=bool((host.score == 0).any()), iwc_atac_task=False, archive_score=float('nan'),
                       score_source='run_record.json (shown on site); excluded from the archive')
    a = pd.concat([a, host[a.columns]], ignore_index=True)
    w = a.benchmark == 'IWC'
    mismatch = [(r.task, r.cfg, r.env, r.replicate) for r in a[w].itertuples()
                if not shown(r.score, shown_iwc[(r.task, r.cfg, r.env, r.replicate)])]
    assert not mismatch, f'IWC runs that differ from the site: {mismatch}'
    a = a.sort_values(['benchmark', 'task', 'cfg', 'env', 'replicate']).reset_index(drop=True)
    a.to_csv(os.path.join(HERE, 'scored_runs.csv'), index=False)

    # summary against the site's displayed totals
    ok = a.assign(ok=a.score >= a.benchmark.map({'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}) - 1e-9)
    print(f'scored_runs.csv: {len(a):,} runs on {a.task.nunique()} tasks')
    print(ok.groupby(['benchmark', 'cfg', 'env']).agg(runs=('ok', 'size'), correct=('ok', 'sum'), mean=('score', 'mean'))
          .round(4).to_string())
    print('runs whose score differs from the archive:', a.score_source.value_counts().to_dict())


if __name__ == '__main__':
    if '--fetch' in sys.argv or not os.path.exists(os.path.join(SNAP, 'iwc_runs.json')):
        fetch()
    build()
