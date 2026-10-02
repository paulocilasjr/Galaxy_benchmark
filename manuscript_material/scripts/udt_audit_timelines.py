"""Build the evidence for the UDT error audit behind On-demand Fig. 7.

For every scored-incorrect Galaxy-condition run that requested a user-defined tool (UDT), write a compact, ordered timeline
(UDT jobs, Galaxy tool jobs, interface calls, shell commands with exit codes, web look-ups, agent messages; each with its
trace line number) plus the task-level audit entry. Reviewers classify each run with on_demand/udt_audit/CODEBOOK.md.

Run from the repository root:
  COMPBIO_KEY_DIR=<folder> python manuscript_material/scripts/udt_audit_timelines.py <output folder outside the repository>
The timelines contain reference answers and local paths, so write them outside the repository.
"""
import collections, gzip, json, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
os.chdir(ROOT)
import fig_on_demand as F
key = F.compbio_key()
A = F.A
SUMS = {(s['benchmark'], s['task'], s['run_id']): s for s in map(json.loads, gzip.open('manuscript_material/source_data/derived/run_summaries.jsonl.gz', 'rt'))}
LED = {}
for x in json.load(open('analysis_reports/galaxy_improvement_20260924/v2_trace_friction/ledger.json')):
    if x['b'] == 'BixBench':
        LED[(x['task'], x['run'])] = x
SH = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'Sol', 'codex_gpt_5_6_luna': 'Luna', 'deepseek_v4_pro_via_codex': 'DS-Codex',
      'deepseek_v4_pro_via_claude_code_superseded': 'DS-ClaudeCode'}
op = lambda p: gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')
cut = lambda s, n: (s if len(s) <= n else s[:n] + f' …[+{len(s) - n} chars]').replace('\n', '⏎ ')

def ok(r):
    if r['benchmark'] == 'BixBench50':
        return r['score'] == 1
    return (r['answer'] or '').replace('Proximal enhancer,EH38E1957012', 'pELS,EH38E1957012').strip() == key[r['task']]

def sc_of(res):
    if isinstance(res, dict):
        sc = res.get('structured_content')
        if isinstance(sc, dict):
            return sc
        try:
            return json.loads(res['content'][0]['text'])
        except Exception:
            return {}
    if isinstance(res, str):
        try:
            return json.loads(res)
        except Exception:
            return {}
    return {}

def mcp_line(tool, args, sc, raw_text=''):
    status = sc.get('status')
    if 'udt' in tool and tool.startswith('run_galaxy'):
        rep = args.get('representation') if isinstance(args.get('representation'), dict) else {}
        jobs = '; '.join(f"{j.get('tool_id')}:{j.get('state')}" + (f"[{(j.get('failure_diagnostic') or {}).get('phase')}]" if j.get('state') == 'error' else '')
                         for j in (sc.get('jobs') or []) if isinstance(j, dict))
        return (f"UDT RUN id={rep.get('id')} container={rep.get('container')} status={status} jobs=[{jobs}] "
                f"failure={cut(str(sc.get('failure_summary') or ''), 300)} | shell_command={cut(str(rep.get('shell_command') or ''), 500)} "
                f"| inline_outputs={cut(json.dumps(sc.get('inline_outputs'))[:2000], 700)}")
    if tool.startswith('run_galaxy'):
        return (f"GALAXY TOOL RUN tool={cut(str(args.get('tool_id')), 120)} status={status} failure={cut(str(sc.get('failure_summary') or ''), 200)} "
                f"| inline_outputs={cut(json.dumps(sc.get('inline_outputs'))[:1500], 400)}")
    brief = {k: v for k, v in (args or {}).items() if k in ('query', 'tool_id', 'history_id', 'dataset_id', 'job_ids')}
    return f"GALAXY INTERFACE {tool} {cut(json.dumps(brief), 160)} status={status}" + (f" | {cut(raw_text, 200)}" if raw_text and status not in ('ok', 'success', None) else '')

def timeline(trace):
    ev = []
    if 'claude' in os.path.basename(trace):
        pend = {}
        for i, line in enumerate(op(trace), 1):
            if '"tool_use"' not in line and '"tool_result"' not in line and '"text"' not in line:
                continue
            try:
                e = json.loads(line)
            except Exception:
                continue
            m = e.get('message') or {}
            for b in m.get('content') or [] if isinstance(m.get('content'), list) else []:
                t = b.get('type')
                if t == 'tool_use':
                    pend[b.get('id')] = (i, b.get('name') or '', b.get('input') or {})
                elif t == 'tool_result' and b.get('tool_use_id') in pend:
                    li, name, inp = pend.pop(b['tool_use_id'])
                    txt = b.get('content')
                    txt = '\n'.join(x.get('text', '') for x in txt if isinstance(x, dict)) if isinstance(txt, list) else str(txt or '')
                    if name == 'Bash':
                        ev.append(f"L{li}-{i} SHELL{' ERROR' if b.get('is_error') else ''} $ {cut(str(inp.get('command')), 400)} => {cut(txt[-300:], 300)}")
                    elif name.startswith('mcp__'):
                        tool = name.split('__')[-1]
                        ev.append(f"L{li}-{i} " + mcp_line(tool, inp, sc_of(txt), txt))
                    elif name in ('Write', 'Edit'):
                        ev.append(f"L{li} FILE {name} {inp.get('file_path')} {cut(str(inp.get('content') or inp.get('new_string') or ''), 300)}")
                    elif name in ('WebSearch', 'WebFetch'):
                        ev.append(f"L{li} WEB {name} {cut(str(inp.get('query') or inp.get('url')), 200)}")
                    elif name not in F.PLANNING_TOOLS:
                        ev.append(f"L{li} {name} {cut(json.dumps(inp), 150)}")
                elif t == 'text' and e.get('type') == 'assistant':
                    ev.append(f"L{i} AGENT: {cut(b.get('text') or '', 400)}")
    else:
        for i, line in enumerate(op(trace), 1):
            if '"item.completed"' not in line:
                continue
            try:
                it = json.loads(line)['item']
            except Exception:
                continue
            t = it.get('type')
            if t == 'command_execution':
                ev.append(f"L{i} SHELL exit={it.get('exit_code')} $ {cut(it.get('command') or '', 400)} => {cut((it.get('aggregated_output') or '')[-300:], 300)}")
            elif t == 'mcp_tool_call':
                res = it.get('result') or {}
                ev.append(f"L{i} " + mcp_line(it.get('tool') or '', it.get('arguments') or {}, sc_of(res)))
            elif t == 'web_search':
                ev.append(f"L{i} WEB search {cut(str(it.get('query')), 200)}")
            elif t == 'file_change':
                ev.append(f"L{i} FILE change {cut(json.dumps(it.get('changes')), 200)}")
            elif t == 'agent_message':
                ev.append(f"L{i} AGENT: {cut(it.get('text') or '', 400)}")
    return ev

# task entries from the task-level audit
IEA = open('individual_error_analysis.md').read()
entries = {}
for m in re.finditer(r'^### (\S+) — .*?(?=^### |\Z)', IEA, re.S | re.M):
    entries[m.group(1)] = m.group(0)[:9000]

targets = [r for r in A['runs'] if r['condition'] == 'galaxy' and r['benchmark'] in ('BixBench50', 'CompBio') and r['udt_requested'] and not ok(r)]
os.makedirs(os.path.join(OUT, 'timelines'), exist_ok=True); os.makedirs(os.path.join(OUT, 'tasks'), exist_ok=True)
index = []
for r in targets:
    s = SUMS[(r['benchmark'], r['task'], r['run_id'])]
    if not s.get('trace'):
        index.append(dict(benchmark=r['benchmark'], task=r['task'], run_id=r['run_id'], timeline=None)); continue
    lab = f"G {SH.get(r['model'], '')} r{r['replicate']}"
    led = LED.get((r['task'], lab)) if r['benchmark'] == 'BixBench50' else None
    ref = key[r['task']] if r['benchmark'] == 'CompBio' else f"expected={s.get('expected')} tolerance={s.get('tolerance')} mode={s.get('eval_mode')}"
    head = [f"BENCHMARK {r['benchmark']} | TASK {r['task']} | RUN {r['run_id']} | MODEL {F.MODEL_ALL[r['model']]} | REPLICATE {r['replicate']}",
            f"SUBMITTED ANSWER: {r['answer']!r}", f"REFERENCE: {ref}", "SCORED: incorrect",
            f"UDT requests: {r['udt_request_count']} ids={r['udt_ids']} ; UDT jobs matched={len(r['udt_matched_job_ids'] or [])} succeeded={len(r['udt_matched_success_ids'] or [])}",
            f"FULL TRACE: {s['trace']}"]
    if led:
        head.append(f"FAILURE LEDGER (run-level adjudication): primary={led['p']} secondary={led['s']} confidence={led['c']} decision_point={led['d']}")
    ev = timeline(s['trace'])
    p = os.path.join(OUT, 'timelines', f"{r['benchmark']}__{r['task']}__{r['run_id']}.txt")
    open(p, 'w').write('\n'.join(head) + '\n\nTIMELINE (L = line in the decompressed trace)\n' + '\n'.join(ev) + '\n')
    tp = os.path.join(OUT, 'tasks', f"{r['task']}.md")
    if not os.path.exists(tp):
        open(tp, 'w').write(entries.get(r['task'], 'No task-level audit entry for this task.'))
    index.append(dict(benchmark=r['benchmark'], task=r['task'], run_id=r['run_id'], model=F.MODEL_ALL[r['model']], timeline=p, events=len(ev),
                      kb=os.path.getsize(p) // 1024, has_entry=r['task'] in entries))
json.dump(index, open(os.path.join(OUT, 'index.json'), 'w'), indent=1)
print(len(index), 'runs;', sum(1 for x in index if x['timeline'] is None), 'without trace;', collections.Counter(x['benchmark'] for x in index))
print('tasks', len({x['task'] for x in index}), 'without entry', sorted({x['task'] for x in index if not x.get('has_entry')}))
print('timeline KB: total', sum(x.get('kb', 0) for x in index), 'max', max(x.get('kb', 0) for x in index))
