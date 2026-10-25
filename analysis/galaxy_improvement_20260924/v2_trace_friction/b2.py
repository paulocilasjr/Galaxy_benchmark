import json, gzip, collections, re
S=[json.loads(l) for l in open('run_summaries.jsonl')]
def opener(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
phase=collections.Counter(); udt=collections.Counter(); nxt=collections.Counter(); udt_err=collections.Counter()
for s in S:
    if s['condition']!='galaxy' or not s.get('trace') or 'claude' in s['trace']: continue
    calls=[]
    for l in opener(s['trace']):
        if '"mcp_tool_call"' not in l or '"item.completed"' not in l: continue
        try: it=json.loads(l)['item']
        except: continue
        tool=it.get('tool') or ''
        if not tool.startswith('run_galaxy') and tool!='wait_for_galaxy_jobs': continue
        r=it.get('result') or {}
        sc=r.get('structured_content') if isinstance(r,dict) else None
        if not isinstance(sc,dict):
            try: sc=json.loads(r['content'][0]['text'])
            except: sc={}
        st=sc.get('status'); calls.append((tool,st,it.get('arguments') or {},sc))
        if tool=='run_galaxy_udt_and_wait':
            udt[st]+=1
        if st=='failed':
            for j in sc.get('jobs') or []:
                if j.get('state')!='error': continue
                d=j.get('failure_diagnostic') or {}
                has=bool(j.get('failure'))
                phase[(tool.replace('run_galaxy_','').replace('_and_wait',''), d.get('phase'), 'has_stderr' if has else 'NO_TEXT')]+=1
    # what follows a no-text failure
    for k,(tool,st,args,sc) in enumerate(calls):
        if st=='failed' and all(not j.get('failure') for j in sc.get('jobs') or [] if j.get('state')=='error') and sc.get('jobs'):
            if k+1<len(calls):
                t2,st2,a2,_=calls[k+1]
                same = json.dumps(a2.get('tool_inputs') or a2.get('representation'),sort_keys=True)==json.dumps(args.get('tool_inputs') or args.get('representation'),sort_keys=True)
                nxt[('identical resubmission' if same else 'modified resubmission', st2)]+=1
print('UDT call statuses',udt.most_common())
print('failed-job phases'); [print(' ',v,k) for k,v in phase.most_common(12)]
print('after no-text failure'); [print(' ',v,k) for k,v in nxt.most_common(10)]
