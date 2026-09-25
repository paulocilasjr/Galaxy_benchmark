"""Mechanism of A1: inspect_galaxy_tool 'History unavailable' failures."""
import json, gzip, collections
S=[json.loads(l) for l in open('run_summaries.jsonl')]
def opener(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
argkeys_ok=collections.Counter(); argkeys_fail=collections.Counter()
hist_in_args=collections.Counter()
per_bench=collections.Counter(); runs_a1=collections.Counter(); runs_total=collections.Counter()
recover=collections.Counter()  # after A1, did a later inspect of same tool succeed? via shell show_tool?
first_pos=[]; examples=[]
for s in S:
    if s['condition']!='galaxy' or not s.get('trace') or 'claude' in s['trace']: continue
    b=s['benchmark']; runs_total[b]+=1
    events=[]
    for i,l in enumerate(opener(s['trace']),1):
        if '"item.completed"' not in l: continue
        try: it=json.loads(l)['item']
        except: continue
        if it.get('type')=='mcp_tool_call':
            txt=json.dumps(it.get('result'))
            events.append(('mcp',i,it.get('tool'),it.get('arguments') or {},'History unavailable' in txt, '"status": "ok"' in txt or '\\"status\\": \\"ok\\"' in txt))
        elif it.get('type')=='command_execution':
            events.append(('sh',i,None,it.get('command',''),False,False))
    a1=[e for e in events if e[0]=='mcp' and e[2]=='inspect_galaxy_tool' and e[4]]
    ok=[e for e in events if e[0]=='mcp' and e[2]=='inspect_galaxy_tool' and not e[4]]
    for e in a1: argkeys_fail[tuple(sorted(e[3].keys()))]+=1; hist_in_args['fail_has_history_id' if 'history_id' in e[3] else 'fail_no_history_id']+=1
    for e in ok: argkeys_ok[tuple(sorted(e[3].keys()))]+=1; hist_in_args['ok_has_history_id' if 'history_id' in e[3] else 'ok_no_history_id']+=1
    if a1:
        runs_a1[b]+=1; per_bench[b]+=len(a1)
        # what happened after first A1
        idx=events.index(a1[0])
        after=events[idx+1:idx+6]
        nxt=[('sh:'+('show_tool/build' if any(k in (x[3] if isinstance(x[3],str) else '') for k in ('show_tool','/build','io_details')) else 'other')) if x[0]=='sh' else 'mcp:'+x[2]+(':A1' if x[4] else '') for x in after]
        recover[tuple(nxt[:2])]+=1
        if len(examples)<4: examples.append((b,s['task'],s['run_id'],a1[0][1],a1[0][3],nxt))
print('A1 per bench',dict(per_bench),'runs with A1',dict(runs_a1),'of',dict(runs_total))
print('history_id presence',dict(hist_in_args))
print('fail argkeys',argkeys_fail.most_common(5)); print('ok argkeys',argkeys_ok.most_common(5))
print('next 2 events after first A1:'); [print(v,k) for k,v in recover.most_common(12)]
for e in examples: print(e)
