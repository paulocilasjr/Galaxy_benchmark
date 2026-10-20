#!/usr/bin/env python3
"""Record the results site's replacement of the 24 IWC wf_007 runs (VGP mitogenome assembly), 2026-10-12.

The site replaced every wf_007 run with a new run on read set ERR12833637 (lab repository
goeckslab/galaxy-agent-benchmark, commit ff9c4f5, "Publish wf007 ERR12833637 results, traces and token accounting").
This script reads that commit's published wf007 analysis and writes runs.csv: for each run, the new run's score (31-mer
F1, as the site shows it) and token usage, beside the superseded archive run it replaces. Nothing else is copied; the
analysis folder also holds the task's reference outputs, which are not read.

Checks before writing:
- the commit's record of the superseded runs' usage equals the archive's token table, run by run;
- the new runs' usage equals the commit's per-run token table;
- 24 runs, one per model, condition and replicate.

Usage (needs the GitHub CLI with read access to the lab repository):
    python runs/IWC/replacement_wf007_20261012/build_record.py
"""
import hashlib
import json
import os
import subprocess

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
REPO = 'goeckslab/galaxy-agent-benchmark'
COMMIT = 'ff9c4f548d23ea48a4f8e2062006b3c2e1e5e039'
ANALYSIS = 'iwc/analyses/wf007_ERR12833637'
FILES = {'summary': f'{ANALYSIS}/results/summary.json',            # per-run scores
         'usage': f'{ANALYSIS}/data/raw_usage.json',               # per-run usage, superseded ('previous') and new
         'token_table': f'{ANALYSIS}/results/wf007_token_usage.tsv',
         'sources': f'{ANALYSIS}/data/sources.json'}               # trace locations on Hugging Face
TASK = 'wf_007_vgp_mitogenome_assembly'
MODEL = {'gpt-5.5': 'GPT-5.5', 'gpt-5.6-sol': 'GPT-5.6 Sol', 'gpt-5.6-luna': 'GPT-5.6 Luna',
         'deepseek-v4-pro': 'DeepSeek V4 Pro'}
ENV = {'galaxy_tools': 'galaxy', 'any_code_no_galaxy_tools': 'open_ended_code'}
KEY = ['cfg', 'env', 'replicate']


def fetch(path):
    return subprocess.run(['gh', 'api', '-H', 'Accept: application/vnd.github.raw', f'repos/{REPO}/contents/{path}?ref={COMMIT}'],
                          check=True, capture_output=True).stdout


def runs_of(records):
    return pd.DataFrame([dict(cfg=MODEL[r['model']], env=ENV[r['condition']], replicate=int(r['replicate']),
                              input_tokens=r['usage']['input_tokens'], cached_input_tokens=r['usage']['cached_input_tokens'],
                              output_tokens=r['usage']['output_tokens'],
                              reasoning_output_tokens=r['usage']['reasoning_output_tokens'],
                              started_at_utc=r['started_at'], finished_at_utc=r['finished_at']) for r in records])


def main():
    raw = {k: fetch(p) for k, p in FILES.items()}
    summary, usage, sources = json.loads(raw['summary']), json.loads(raw['usage']), json.loads(raw['sources'])
    assert summary['dataset_version'] == 'ERR12833637'
    new = runs_of(usage['current'])
    old = runs_of(usage['previous'])
    scores = pd.DataFrame([dict(cfg=MODEL[r['model']], env=ENV[r['condition']], replicate=int(r['replicate']),
                                site_run_id=r['run_id'], score=r['score']) for r in summary['runs']])

    # superseded runs, as the archive holds them
    a = pd.read_csv(os.path.join(ROOT, 'manuscript/manuscript_narrative', 'original_layout', 'analysis', 'accuracy_primary_runs.csv'))
    a = a[(a.benchmark == 'IWC') & (a.task == TASK)][KEY + ['run_id', 'score']]
    t = pd.read_csv(os.path.join(ROOT, 'manuscript/manuscript_narrative', 'original_layout', 'analysis', 'token_run_observations.csv'))
    t = t[t.model_primary & (t.benchmark == 'IWC') & (t.task == TASK)][KEY + ['input_tokens', 'cached', 'output_tokens']]
    j = old.merge(t, on=KEY, suffixes=('', '_archive'))
    assert len(j) == 24 and (j.input_tokens == j.input_tokens_archive).all() and (j.cached_input_tokens == j.cached).all() \
        and (j.output_tokens == j.output_tokens_archive).all(), "the commit's superseded usage must equal the archive"
    tab = pd.read_csv(pd.io.common.BytesIO(raw['token_table']), sep='\t')
    tab = tab.assign(cfg=tab.model_id.map(MODEL), env=tab.condition.map(ENV), replicate=tab.replicate_id.str[1:].astype(int))
    k = new.merge(tab, on=KEY, suffixes=('', '_table'))
    assert len(k) == 24 and (k.input_tokens == k.input_tokens_table).all() and (k.output_tokens == k.output_tokens_table).all()

    out = scores.merge(new, on=KEY, validate='1:1').merge(
        a.rename(columns={'run_id': 'superseded_run_id', 'score': 'superseded_score'}), on=KEY, validate='1:1')
    assert len(out) == 24 and not out.duplicated(KEY).any()
    out.insert(0, 'benchmark', 'IWC')
    out.insert(1, 'task', TASK)
    out['run_id'] = 'ERR12833637_' + out.site_run_id                       # no trace folder in the archive
    cols = ['benchmark', 'task', 'cfg', 'env', 'replicate', 'run_id', 'site_run_id', 'score', 'input_tokens',
            'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens', 'started_at_utc', 'finished_at_utc',
            'superseded_run_id', 'superseded_score']
    out = out[cols].sort_values(KEY).reset_index(drop=True)
    out.to_csv(os.path.join(HERE, 'runs.csv'), index=False)
    record = dict(repository=REPO, commit=COMMIT, dataset_version=summary['dataset_version'],
                  traces=dict(repository=sources['repository'], revision=sources['new_hf_revision'],
                              prefix=sources['current_trace_prefix']),
                  files={k: dict(path=p, sha256=hashlib.sha256(raw[k]).hexdigest()) for k, p in FILES.items()})
    json.dump(record, open(os.path.join(HERE, 'sources.json'), 'w'), indent=1)
    print(f'runs.csv: {len(out)} runs; superseded usage matches the archive; sources.json written')


if __name__ == '__main__':
    main()
