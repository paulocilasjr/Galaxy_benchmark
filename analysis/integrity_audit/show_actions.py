"""Print normalised actions of a run's trace. Usage: python -I show_actions.py <repo> <run_dir> [from] [to] [--grep REGEX] [--max N]"""
import sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import traces
repo, run_dir = sys.argv[1], sys.argv[2]
args = sys.argv[3:]
grep = None; mx = 1500
if '--grep' in args:
    grep = re.compile(args[args.index('--grep') + 1], re.I); del args[args.index('--grep'):args.index('--grep') + 2]
if '--max' in args:
    mx = int(args[args.index('--max') + 1]); del args[args.index('--max'):args.index('--max') + 2]
lo = int(args[0]) if args else 0; hi = int(args[1]) if len(args) > 1 else 10**9
for p in traces.trace_files(repo, run_dir):
    print('### trace', os.path.relpath(p, repo))
    for a in traces.actions(p):
        if not (lo <= a['i'] <= hi): continue
        if grep and not (grep.search(a['text']) or grep.search(a['out'])): continue
        print(f"[{a['i']}] {a['kind']} {a['server']} {a['tool']} status={a['status']}")
        print('  TEXT:', a['text'][:mx].replace('\n', '\n        '))
        if a['out']: print('  OUT :', a['out'][:mx].replace('\n', '\n        '))
