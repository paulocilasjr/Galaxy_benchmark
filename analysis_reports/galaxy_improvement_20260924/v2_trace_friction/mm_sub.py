import json, gzip, collections
S=[json.loads(l) for l in open('run_summaries.jsonl')]
def opener(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
c=collections.Counter(); jobs=collections.Counter(); mmkind=collections.Counter(); subst=[]
for s in S:
    if s['condition']!='galaxy' or not s.get('trace') or 'claude' in s['trace']: continue
    for l in opener(s['trace']):
        if 'mismatch' not in l or '"mcp_tool_call"' not in l or '"item.completed"' not in l: continue
        try: it=json.loads(l)["item"]
        except Exception: continue
        r=it.get("result") or {}
        sc=r.get('structured_content') if isinstance(r,dict) else None
        if not isinstance(sc,dict):
            try: sc=json.loads(r['content'][0]['text'])
            except: continue
        stt=sc.get('status')
        if stt not in ('parameter_mismatch','validation_parameter_mismatch'): continue
        c[(stt,sc.get('submitted'),bool(sc.get('jobs')))]+=1
        pp=sc.get('parameter_provenance') or {}
        mms=list(pp.get('mismatches') or []); miss=list(pp.get('missing_paths') or [])
        for j in pp.get('jobs') or []: mms+=j.get('mismatches') or []; miss+=j.get('missing_paths') or []
        if mms: mmkind[(stt,'value substituted')]+=1
        if miss and not mms: mmkind[(stt,'paths missing only')]+=1
        for m in mms:
            if len(subst)<400: subst.append((s['task'],(it.get('arguments') or {}).get('tool_id','')[-45:],m.get('path'),m.get('expected'),m.get('resolved')))
print(c); print(mmkind)
import random; random.seed(5)
for x in random.sample(subst,25): print(x)
