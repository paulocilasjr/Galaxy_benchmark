import json, gzip, collections
S=[json.loads(l) for l in open('run_summaries.jsonl')]
def opener(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
st=collections.Counter(); runs=collections.Counter(); tools=collections.Counter(); secs=collections.Counter(); tot=collections.Counter()
outcome=collections.Counter()
for s in S:
    if s['condition']!='galaxy' or not s.get('trace') or 'claude' in s['trace']: continue
    b=s['benchmark']; hit=False
    for l in opener(s['trace']):
        if '"mcp_tool_call"' not in l or '"item.completed"' not in l: continue
        try: it=json.loads(l)['item']
        except: continue
        if not (it.get('tool') or '').startswith('run_galaxy'): continue
        r=it.get('result') or {}
        sc=r.get('structured_content') if isinstance(r,dict) else None
        if not isinstance(sc,dict):
            try: sc=json.loads(r['content'][0]['text'])
            except: sc={}
        status=sc.get('status'); tot[b]+=1
        st[(b,status)]+=1
        if status and 'mismatch' in status:
            hit=True; tools[(it.get('arguments') or {}).get('tool_id','UDT' if 'udt' in it['tool'] else '?').split('/')[-2 if '/' in (it.get('arguments') or {}).get('tool_id','') else 0]]+=1
            secs[b]+=sc.get('elapsed_seconds') or 0
    if hit:
        runs[b]+=1
        if b=='BixBench50': outcome['fail' if s['score']==0 else 'pass']+=1
for b in ['BixBench50','CompBio','IWC']:
    print(b,'run calls',tot[b],{k[1]:v for k,v in st.items() if k[0]==b})
    print('  runs with mismatch',runs[b],'job-seconds in mismatch calls',round(secs[b]))
print('Bix runs with mismatch outcome',outcome)
print(tools.most_common(15))
