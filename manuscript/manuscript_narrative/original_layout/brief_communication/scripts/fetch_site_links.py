#!/usr/bin/env python3
"""Run links that the run archive does not hold, read from the public results site.

- The 24 IWC wf_007 runs that the site published on 2026-10-12 (read set ERR12833637), from the task page.
- The 6 July 2026 BixBench-Verified-50 runs with GPT-5.5 (interface round 1, Fig. 2c), from the 50 item pages of
  bixbench/july6/; only the two conditions used in the paper are kept (galaxy_strict_skills, anycode_nongalaxy_skills).

Each run card on a page holds a 'Galaxy history' link (Galaxy runs) and a 'Hugging Face trace' link; condition and
replicate are read from the trace path. Only links to the trace dataset and to usegalaxy.org are kept.
Writes data/site_links_wf007_replacement.csv, data/site_links_july6_round1.csv and data/site_links_SOURCES.json
(page URLs, retrieval time and SHA-256 of each page).
Usage: python scripts/fetch_site_links.py
"""
import csv
import datetime
import hashlib
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), 'data')
SITE = 'https://goeckslab.github.io/galaxy-agent-benchmark'
TRACE = re.compile(r'href="(https://huggingface\.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces/tree/main/'
                   r'[A-Za-z0-9_./-]+/(\w+)/replicate_(\d))"')
HISTORY = re.compile(r'href="(https://usegalaxy\.org/(?:histories/view\?id=[0-9a-f]{16,32}|u/[\w.-]+/h/[\w.-]+))"')
CARD = re.compile(r'<article class="[^"]*\brun\b[^"]*"[^>]*>(.*?)</article>', re.S)
WF007_MODEL = {'gpt55': 'GPT-5.5', 'gpt56_sol': 'GPT-5.6 Sol', 'gpt56_luna': 'GPT-5.6 Luna',
               'deepseek_v4_pro': 'DeepSeek V4 Pro'}
ENV = {'galaxy_strict_skills': 'galaxy', 'anycode_nongalaxy_skills': 'open_ended_code'}
pages = []


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        body = r.read()
    pages.append(dict(url=url, sha256=hashlib.sha256(body).hexdigest(), bytes=len(body)))
    return body.decode('utf-8')


def cards(html):
    for card in CARD.findall(html):
        t = TRACE.search(card)
        if not t:
            continue
        h = HISTORY.search(card)
        yield t.group(1), t.group(2), int(t.group(3)), h.group(1) if h else ''


def wf007():
    rows = []
    for trace, cond, rep, hist in cards(fetch(f'{SITE}/iwc/wf_007_vgp_mitogenome_assembly/index.html')):
        model = re.search(r'run_traces_october2026_wf007_ERR12833637/(\w+)/', trace).group(1)
        rows.append(dict(benchmark='IWC', task='wf_007_vgp_mitogenome_assembly', cfg=WF007_MODEL[model],
                         env=ENV[cond], replicate=rep, run_trace=trace, galaxy_history=hist))
    assert len(rows) == 24 and sum(bool(r['galaxy_history']) for r in rows) == 12, len(rows)
    return rows


def july6():
    index = fetch(f'{SITE}/bixbench/july6/index.html')
    tasks = sorted(set(re.findall(r'href="(bix-\d+-q\d+)/index\.html"', index)))
    assert len(tasks) == 50, len(tasks)
    rows = []
    for task in tasks:
        for trace, cond, rep, hist in cards(fetch(f'{SITE}/bixbench/july6/{task}/index.html')):
            if cond in ENV:
                rows.append(dict(benchmark='BixBench50', task=task, cfg='GPT-5.5', env=ENV[cond], replicate=rep,
                                 run_trace=trace, galaxy_history=hist))
    assert len(rows) == 300, len(rows)
    return rows


def write(name, rows):
    with open(os.path.join(DATA, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    write('site_links_wf007_replacement.csv', wf007())
    write('site_links_july6_round1.csv', july6())
    json.dump(dict(retrieved_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
                   pages=pages), open(os.path.join(DATA, 'site_links_SOURCES.json'), 'w'), indent=1)
    print(f'{len(pages)} pages read')


if __name__ == '__main__':
    main()
