"""Scan every scored run's agent trace for access to published benchmark answers (read-only)."""
import csv, gzip, os, re, collections, json
D = {'BixBench50': 'BixBench_50', 'CompBio': 'CompBio', 'IWC': 'IWC'}
SOURCE = re.compile(r'futurehouse/BixBench|trustworthy-biology-agents-traces|compbiobench-(results|submissions|leaderboard)', re.I)
IDEAL = re.compile(r'\\?"ideal\\?"\s*:\s*\\?"')           # a printed BixBench answer field
rows = []
for r in csv.DictReader(open('figures/scored_runs.csv')):
    base = f"{D[r['benchmark']]}/analysis/{r['task']}/source_snapshots/huggingface_traces/files/{r['run_id']}"
    cands = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(base) for f in fs if f.startswith('codex_events'))
    if not cands:
        rows.append(dict(r, trace='missing', source=0, ideal=0)); continue
    p = cands[0]
    txt = (gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')).read()
    rows.append(dict(r, trace='ok', source=int(bool(SOURCE.search(txt))), ideal=int(bool(IDEAL.search(txt)))))
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'answer_source_scan.csv')
with open(out, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
c = collections.Counter((x['benchmark'], x['env'], x['trace']) for x in rows)
print('traces:', dict(c))
s = collections.Counter((x['benchmark'], x['env'], x['cfg']) for x in rows if x['source'] or x['ideal'])
print('runs touching an answer source or printing an ideal field:', sum(s.values()))
for k, v in sorted(s.items()): print('  ', k, v)
i = collections.Counter((x['benchmark'], x['env'], x['cfg'], x['score']) for x in rows if x['ideal'])
print('runs whose trace printed an "ideal" answer field:', sum(i.values()))
for k, v in sorted(i.items()): print('  ', k, v)
