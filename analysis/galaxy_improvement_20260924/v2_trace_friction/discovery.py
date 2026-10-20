import json, gzip, collections, statistics as st
S=[json.loads(l) for l in open('run_summaries.jsonl')]
def opener(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
out={}
for b in ['BixBench50','CompBio','IWC']:
    R=[s for s in S if s['benchmark']==b and s['condition']=='galaxy' and s.get('trace') and 'claude' not in s['trace']]
    nsearch=[];dup=[];insp_never=[];insp_total=[];share_calls=[];share_chars=[]
    for s in R:
        searches=[];inspected=set();ran=set()
        for l in opener(s['trace']):
            if '"mcp_tool_call"' not in l or '"item.completed"' not in l: continue
            try: it=json.loads(l)['item']
            except: continue
            a=it.get('arguments') or {}; t=it.get('tool')
            if t=='search_galaxy_tools': searches.append((a.get('query') or '').strip().lower())
            elif t=='inspect_galaxy_tool' and a.get('tool_id'): inspected.add(a['tool_id'])
            elif t=='run_galaxy_tool_and_wait' and a.get('tool_id'): ran.add(a['tool_id'])
        nsearch.append(len(searches)); dup.append(len(searches)-len(set(searches)))
        insp_total.append(len(inspected)); insp_never.append(len(inspected-ran))
        cc=s.get('class_calls') or {}; ch=s.get('class_chars') or {}
        mcp=sum(v for k,v in cc.items() if k!='shell')
        if mcp: share_calls.append(cc.get('discovery',0)/mcp)
        tch=sum(v for k,v in ch.items() if k!='shell')
        if tch: share_chars.append(ch.get('discovery',0)/tch)
    q=lambda x: (st.median(x), round(st.mean(x),1), max(x))
    print(b,'runs',len(R))
    print('  searches/run median,mean,max',q(nsearch),' runs with >=20 searches',sum(n>=20 for n in nsearch))
    print('  repeated identical searches total',sum(dup),'runs with any repeat',sum(d>0 for d in dup))
    print('  tools inspected/run',q(insp_total),' inspected-never-run total',sum(insp_never),'of',sum(insp_total))
    print('  discovery share of MCP calls median',round(st.median(share_calls),3),' of MCP-returned chars median',round(st.median(share_chars),3))
