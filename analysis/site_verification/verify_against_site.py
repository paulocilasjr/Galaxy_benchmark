#!/usr/bin/env python3
"""Check the archive against the public results site (https://goeckslab.github.io/galaxy-agent-benchmark/).

Fetches the three results pages the figures follow and compares them with the archive:

- BixBench-Verified-50 (index.html) and IWC (iwc/<item>/index.html): every run's grade or value, using the fetchers of
  figures/make_scored_runs.py, compared with the snapshot in figures/site_snapshot/ (the snapshot scored_runs.csv uses).
- CompBioBench (compbiobench/index.html and the 100 item pages): the official-leaderboard score of every replicate against
  the per-run grades in figures/scored_runs.csv; every run's submitted answer against the archive's run summaries; the
  per-item grades (which use the site's evidence-based references, not the leaderboard) and rerun labels.
- Token use (compbiobench/data/public_token_usage.tsv, iwc/data/token_usage.tsv, bixbench/tokens/index.html) against the
  archive's per-run token table; UDT use (compbiobench/data/public_udt_usage.tsv, the BixBench page) against the archive's
  UDT table; and the October token-optimization summary.json against runs/token_optimization/site_snapshot/.

No answers are written: the output records only whether each comparison matched, with the run keys that did not.

Usage (from the repository root): python analysis/site_verification/verify_against_site.py [output_dir]
Needs pandas. Writes <output_dir>/site_check.json (default: analysis/site_verification/).
"""
import gzip, hashlib, html, json, os, re, sys, tempfile, urllib.request
from datetime import datetime, timezone

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
SITE = 'https://goeckslab.github.io/galaxy-agent-benchmark'
OUT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, 'figures'))
import make_scored_runs as msr          # noqa: E402  (site fetchers)
import replaced_runs                    # noqa: E402

SCORED = os.path.join(ROOT, 'figures', 'scored_runs.csv')
TOKENS = os.path.join(ROOT, 'manuscript', 'manuscript_narrative', 'original_layout', 'analysis', 'token_run_observations.csv')
UDT = os.path.join(ROOT, 'manuscript', 'manuscript_narrative', 'original_layout', 'analysis', 'accuracy_udt_run_observations.csv')
SUMMARIES = os.path.join(ROOT, 'manuscript', 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz')
RERUNS = os.path.join(ROOT, 'runs', 'CompBio', 'reruns_20261005', 'rerun_manifest.csv')
TOKOPT = os.path.join(ROOT, 'runs', 'token_optimization', 'site_snapshot', 'summary.json')
CB_MODEL = {'Codex GPT-5.5': 'GPT-5.5', 'Codex GPT-5.6 Sol': 'GPT-5.6 Sol', 'Codex + DeepSeek-v4-pro-0813': 'DeepSeek V4 Pro',
            'Codex GPT-5.6 Luna': 'GPT-5.6 Luna', 'Codex GPT-6 Astra': 'GPT-6 Astra'}
CB_SLUG = {'Codex GPT-5.5': 'codex_gpt_5_5', 'Codex GPT-5.6 Sol': 'codex_gpt_5_6_sol', 'Codex GPT-5.6 Luna': 'codex_gpt_5_6_luna',
           'Codex + DeepSeek-v4-pro-0813': 'codex_deepseek_v4_pro_0813', 'Codex GPT-6 Astra': 'codex_gpt_6_astra'}
KEY = ['cfg', 'env', 'replicate']


def get(url):
    return urllib.request.urlopen(url, timeout=120).read().decode('utf-8')


def txt(x):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()


def check(name, ok, **detail):
    print(f"{'OK  ' if ok else 'DIFF'} {name}" + (f": {detail.get('summary')}" if detail.get('summary') else ''))
    return dict(check=name, match=bool(ok), **detail)


def per_run_snapshots():
    """BixBench and IWC per-run grades and the 6 July page, live against figures/site_snapshot/."""
    out, tmp = [], tempfile.mkdtemp()
    msr.SNAP = tmp
    msr.fetch()
    for f in ('bixbench_runs', 'iwc_runs', 'bixbench_july6_runs'):
        old = json.load(open(os.path.join(ROOT, 'figures', 'site_snapshot', f + '.json')))
        new = json.load(open(os.path.join(tmp, f + '.json')))
        o = {json.dumps(r, sort_keys=True) for r in old['runs']}
        n = {json.dumps(r, sort_keys=True) for r in new['runs']}
        out.append(check(f'{f}: live site vs figures/site_snapshot', o == n and old.get('items') == new.get('items'),
                         summary=f'{len(n)} runs live, {len(o)} in snapshot, {len(o ^ n)} differ',
                         snapshot_retrieved=old['retrieved_at_utc'], differing=sorted(o ^ n)[:50]))
    return out


def compbio_runs():
    """Every run card on the 100 CompBioBench item pages (no answers kept beyond this function)."""
    index = get(f'{SITE}/compbiobench/index.html')
    items = sorted(set(re.findall(r'href="([a-zA-Z0-9][^"/]*-q\d+)/index.html"', index)))
    runs = []
    for item in items:
        page = get(f'{SITE}/compbiobench/{item}/index.html')
        heads = [(m.start(), txt(m.group(1))) for m in re.finditer(r'<h2[^>]*>(.*?)</h2>', page, flags=re.S)]
        for m in re.finditer(r'<article class="run([^"]*)">(.*?)</article>', page, flags=re.S):
            body = m.group(2)
            cond = [h for p, h in heads if p < m.start() and h in ('Galaxy', 'Anycode')][-1]
            model = txt(re.search(r'<div class="run-head"><div><span>(.*?)</span>', body).group(1))
            badges = [txt(b) for b in re.findall(r'<span class="(?:route-badge|answer-check)[^"]*"[^>]*>(.*?)</span>', body)]
            ans = re.search(r'<div class="answer-line"><span>Answer</span><code>(.*?)</code>', body, flags=re.S)
            runs.append(dict(item=item, condition=cond, model=model, replicate=int(re.search(r'<h3>Replicate (\d+)</h3>', body).group(1)),
                             status=next((b for b in badges if b in ('Correct', 'Incorrect', 'Matches prediction', 'Differs from prediction')), None),
                             rerun='Rerun' in badges, answer=txt(ans.group(1)) if ans else None))
    return index, pd.DataFrame(runs)


def compbio_checks():
    out = []
    index, site = compbio_runs()
    s = txt(re.sub(r'<script.*?</script>|<style.*?</style>', '', index, flags=re.S))
    head = s[:s.index('How scores are labeled')]
    pos = sorted((head.index(m + ' high reasoning'), m) for m in CB_MODEL)
    official = {}
    for i, (p, m) in enumerate(pos):
        block = head[p:pos[i + 1][0] if i + 1 < len(pos) else len(head)]
        for cond, body in re.findall(r'(Galaxy|Anycode) (\d[\d.]*% official.*?)(?= Galaxy \d| Anycode \d|$)', block):
            for rep, pct, kind in re.findall(r'Replicate (\d) (\d+)% (official leaderboard|predicted)', body):
                official[(CB_MODEL[m], 'galaxy' if cond == 'Galaxy' else 'open_ended_code', int(rep))] = (int(pct), kind)
    a = pd.read_csv(SCORED)
    local = a[a.benchmark == 'CompBio'].groupby(KEY).score.sum()
    diff = [dict(cfg=k[0], env=k[1], replicate=k[2], site=v[0], kind=v[1], archive=None if k not in local.index else round(float(local[k]), 3))
            for k, v in official.items() if k not in local.index or round(float(local[k])) != v[0]]
    astra = [d for d in diff if d['cfg'] == 'GPT-6 Astra']
    out.append(check('CompBioBench replicate scores (site headline) vs figures/scored_runs.csv',
                     len(diff) == len(astra), summary=f'{len(official) - len(diff)}/{len(official)} replicates equal; '
                     f'{len(astra)} GPT-6 Astra replicate(s) are not in the primary table', differing=diff))
    site['run_id'] = [('galaxy_' if c == 'Galaxy' else 'open_ended_code_') + CB_SLUG[m] + f'_r{r}'
                      for c, m, r in zip(site.condition, site.model, site.replicate)]
    summ = pd.DataFrame([x for x in map(json.loads, gzip.open(SUMMARIES, 'rt')) if x['benchmark'] == 'CompBio'])
    m = site.merge(summ[['task', 'run_id', 'answer']], left_on=['item', 'run_id'], right_on=['task', 'run_id'], how='outer', indicator=True)
    norm = lambda x: re.sub(r'\s+', '', str(x)).lower() if x is not None and x == x else ''
    same = [(lambda a_, b_: b_.startswith(a_[:-3]) if a_.endswith('...') else a_ == b_)(norm(x), norm(y)) for x, y in zip(m.answer_x, m.answer_y)]
    bad = m[[not s_ for s_ in same]]
    out.append(check('CompBioBench submitted answers (item pages) vs archive run summaries', len(bad) == 0 and (m._merge == 'both').all(),
                     summary=f'{len(m)} runs, {len(bad)} differ', differing=bad[['item', 'run_id']].to_dict('records')))
    site['cfg'] = site.model.map(CB_MODEL)
    site['env'] = site.condition.map({'Galaxy': 'galaxy', 'Anycode': 'open_ended_code'})
    g = a[a.benchmark == 'CompBio'].merge(site, left_on=['task'] + KEY, right_on=['item'] + KEY)
    graded = g[g.status.isin(['Correct', 'Incorrect'])]
    dg = graded[(graded.status == 'Correct') != (graded.score >= 1)]
    out.append(check('CompBioBench per-item grades (site evidence-based references) vs figures/scored_runs.csv (official leaderboard)',
                     len(dg) == 0, summary=f'{len(graded)} graded cells, {len(dg)} differ on {dg.task.nunique()} item(s): '
                     + ', '.join(sorted(dg.task.unique())), differing=dg[['task'] + KEY].to_dict('records'),
                     note='Expected: the figures use the official-leaderboard grades, which the site headline also uses.'))
    rr = pd.read_csv(RERUNS)
    out.append(check('CompBioBench rerun labels vs runs/CompBio/reruns_20261005/rerun_manifest.csv',
                     set(zip(site[site.rerun].item, site[site.rerun].run_id)) == set(zip(rr.task, rr.run_id)),
                     summary=f'{int(site.rerun.sum())} reruns on the site, {len(rr)} in the manifest'))
    return out


def token_checks():
    out = []
    t = pd.read_csv(TOKENS)
    t = replaced_runs.replace_tokens(t[t.model_primary.astype(bool)])
    # CompBioBench, per replicate
    s = pd.read_csv(f'{SITE}/compbiobench/data/public_token_usage.tsv', sep='\t')
    s = s.assign(cfg=s.model.map(CB_MODEL), env=s.condition.map({'galaxy': 'galaxy', 'anycode': 'open_ended_code'}),
                 replicate=s.replicate_id.str[1:].astype(int))
    loc = t[t.benchmark == 'CompBio'].groupby(KEY).agg(n=('input_tokens', 'count'), inp=('input_tokens', 'sum'), out=('output_tokens', 'sum'))
    m = s.merge(loc.reset_index(), on=KEY, how='left')
    bad = m[(m.input_tokens != m.inp) | (m.output_tokens != m.out)]
    missing = t[(t.benchmark == 'CompBio') & t.input_tokens.isna()][['task'] + KEY]
    out.append(check('CompBioBench tokens per replicate (public_token_usage.tsv) vs archive token table', len(bad) == 0,
                     summary=f'{len(m) - len(bad)}/{len(m)} replicates equal; archive has no token record for {len(missing)} runs',
                     differing=bad[KEY + ['items_with_usage', 'n', 'input_tokens', 'inp']].to_dict('records'),
                     runs_without_tokens=missing.to_dict('records')))
    # IWC, per replicate (wf_007 from the replacement record)
    s = pd.read_csv(f'{SITE}/iwc/data/token_usage.tsv', sep='\t')
    s = s.assign(cfg=s.model.map(lambda x: {'GPT-5.5': 'GPT-5.5', 'GPT-5.6 Sol': 'GPT-5.6 Sol', 'GPT-5.6 Luna': 'GPT-5.6 Luna'}.get(x, 'DeepSeek V4 Pro')),
                 env=s.condition.map(lambda x: 'galaxy' if x == 'galaxy_tools' else 'open_ended_code'), replicate=s.replicate_id.str[1:].astype(int))
    loc = t[t.benchmark == 'IWC'].groupby(KEY).agg(inp=('input_tokens', 'sum'), cached=('cached', 'sum'), out=('output_tokens', 'sum'))
    m = s.merge(loc.reset_index(), on=KEY, how='left')
    bad = m[(m.input_tokens != m.inp) | (m.output_tokens != m.out)]
    badc = m[m.cached_input_tokens != m.cached]
    nan_cached = t[(t.benchmark == 'IWC') & t.cached.isna() & t.input_tokens.notna()][['task'] + KEY]
    out.append(check('IWC input and output tokens per replicate (token_usage.tsv) vs archive token table', len(bad) == 0,
                     summary=f'{len(m) - len(bad)}/{len(m)} replicates equal', differing=bad[KEY].to_dict('records')))
    out.append(check('IWC cached-input tokens per replicate', len(badc) == 0,
                     summary=f'{len(m) - len(badc)}/{len(m)} replicates equal; runs with input tokens but no cached count: {len(nan_cached)}',
                     differing=badc[KEY + ['cached_input_tokens', 'cached']].to_dict('records'), runs_without_cached=nan_cached.to_dict('records')))
    # BixBench, per configuration (tokens page)
    page = get(f'{SITE}/bixbench/tokens/index.html')
    def unit(v):     # displayed value -> (value, scale, decimals), e.g. '1.61M' -> (1.61, 1e6, 2)
        return float(v[:-1]), {'K': 1e3, 'M': 1e6, 'B': 1e9}[v[-1]], len(v[:-1].split('.')[1]) if '.' in v else 0

    def shown(x, d):  # the archive value printed at the site's precision equals the site's value
        return round(x / d[1], d[2]) == d[0]
    site_rows = {}
    for row in re.findall(r'<tr[^>]*>(.*?)</tr>', page, flags=re.S):
        cells = [txt(c) for c in re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, flags=re.S)]
        if cells and re.search(r'Galaxy-API code|Open-ended code', cells[0]):
            name = cells[0]
            cfg = ('DeepSeek V4 Pro (Claude Code, superseded)' if 'Claude Code' in name else 'DeepSeek V4 Pro' if 'DeepSeek' in name
                   else 'GPT-5.6 Sol' if 'Sol' in name else 'GPT-5.6 Luna' if 'Luna' in name else 'GPT-5.5')
            env = 'galaxy' if 'Galaxy-API' in name else 'open_ended_code'
            site_rows[(cfg, env)] = [unit(c.split()[0]) for c in cells[1:6]]       # total, input, cached, uncached, output
    tb = pd.read_csv(TOKENS)
    tb = tb[tb.benchmark == 'BixBench50'].groupby(['cfg', 'env'])[['input_tokens', 'cached', 'output_tokens']].sum()
    rows, bad = [], []
    for (cfg, env), (tot, inp, cac, unc, out_) in site_rows.items():
        li, lc, lo = tb.loc[(cfg, env)]
        r = dict(cfg=cfg, env=env, input_equal=shown(li, inp), output_equal=shown(lo, out_), cached_equal=shown(lc, cac),
                 site_cached=cac[0] * cac[1], archive_cached=float(lc))
        rows.append(r)
        if not (r['input_equal'] and r['output_equal']):
            bad.append(r)
    out.append(check('BixBench input and output tokens per configuration (tokens page) vs archive token table', not bad,
                     summary=f'{len(rows) - len(bad)}/{len(rows)} configurations equal at the displayed precision', differing=bad))
    badc = [r for r in rows if not r['cached_equal']]
    out.append(check('BixBench cached-input tokens per configuration', not badc,
                     summary=f'{len(rows) - len(badc)}/{len(rows)} equal: ' + '; '.join(f"{r['cfg']} {r['env']}: site {r['site_cached'] / 1e6:.2f}M, "
                                                                                       f"archive {r['archive_cached'] / 1e6:.2f}M" for r in badc),
                     differing=badc))
    return out


def udt_checks():
    out = []
    u = pd.read_csv(UDT)
    s = pd.read_csv(f'{SITE}/compbiobench/data/public_udt_usage.tsv', sep='\t')
    cfg = {'codex-ds-v4pro-galaxy': 'DeepSeek V4 Pro', 'galaxy-gpt55': 'GPT-5.5', 'luna-galaxy': 'GPT-5.6 Luna', 'sol-galaxy': 'GPT-5.6 Sol'}
    s = s.assign(cfg=s.campaign_id.str.replace(r'-r\d$', '', regex=True).map(cfg),
                 replicate=s.campaign_id.str.extract(r'-r(\d)$')[0].fillna(1).astype(int))
    m = u[(u.benchmark == 'CompBio') & (u.env == 'galaxy')].merge(s, left_on=['task', 'cfg', 'replicate'], right_on=['question_id', 'cfg', 'replicate'])
    m['site_udt'] = m.udt_mode.isin(['udt_only', 'udt_and_standard'])
    d = m[m.site_udt != m.udt_attempt_observed.astype(bool)]
    out.append(check('CompBioBench UDT use per Galaxy run (public_udt_usage.tsv) vs archive UDT table', len(d) == 0,
                     summary=f'{len(m) - len(d)}/{len(m)} runs equal; {len(d)} runs are UDT on the site but not in the archive table '
                     f'({int((~d.has_trace.astype(bool)).sum())} without an archived trace)',
                     differing=d[['task', 'cfg', 'replicate', 'udt_mode', 'has_trace']].to_dict('records'),
                     note='The site counts UDTs from traces and Galaxy histories; the archive table counts UDT calls in the trace only.'))
    page = txt(re.sub(r'<script.*?</script>|<style.*?</style>', '', get(f'{SITE}/index.html'), flags=re.S))
    names = {'Codex GPT-5.5': 'GPT-5.5', 'Codex GPT-5.6 Sol': 'GPT-5.6 Sol', 'Codex GPT-5.6 Luna': 'GPT-5.6 Luna', 'DeepSeek V4 Pro via Codex': 'DeepSeek V4 Pro'}
    loc = u[(u.benchmark == 'BixBench50') & (u.env == 'galaxy')].groupby('cfg').udt_attempt_observed.sum()
    rows = []
    for label, c in names.items():
        mm = re.search(re.escape(label) + r' \d+ primary replicates Galaxy-API code .*? UDT usage [\d.]+% (\d+)/150', page)
        rows.append(dict(cfg=c, site=int(mm.group(1)) if mm else None, archive=int(loc.get(c, 0))))
    bad = [r for r in rows if r['site'] != r['archive']]
    out.append(check('BixBench UDT use per configuration (index page) vs archive UDT table', not bad,
                     summary='; '.join(f"{r['cfg']}: site {r['site']}, archive {r['archive']}" for r in rows), differing=bad))
    return out


def tokopt_check():
    live = get(f'{SITE}/bixbench/token-optimization-oct2026/summary.json').encode()
    return [check('Token-optimization summary.json vs runs/token_optimization/site_snapshot',
                  hashlib.sha256(live).hexdigest() == hashlib.sha256(open(TOKOPT, 'rb').read()).hexdigest(),
                  summary='byte-identical' if live == open(TOKOPT, 'rb').read() else 'differs')]


if __name__ == '__main__':
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    results = per_run_snapshots() + compbio_checks() + token_checks() + udt_checks() + tokopt_check()
    os.makedirs(OUT, exist_ok=True)
    json.dump(dict(site=SITE, checked_at_utc=stamp, checks=results), open(os.path.join(OUT, 'site_check.json'), 'w'), indent=1, default=str)
    print(f"{sum(r['match'] for r in results)}/{len(results)} checks match; written to {os.path.join(OUT, 'site_check.json')}")
