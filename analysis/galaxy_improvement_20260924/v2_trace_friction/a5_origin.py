import json, gzip, re, collections, random
S=[json.loads(l) for l in open('run_summaries.jsonl')]
def opener(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
res=collections.Counter(); ex=[]
random.seed(3)
cands=[s for s in S if any('invalid dataset id' in (e.get('err') or '') for e in s.get('errors') or [])]
for s in cands:
    lines=list(opener(s['trace']))
    for e in s['errors']:
        if 'invalid dataset id' not in (e.get('err') or ''): continue
        ids=set(re.findall(r"invalid dataset id '([0-9a-f]+)'",e['err']))
        for i in ids:
            prior=''.join(lines[:e['line']-1])
            if i not in prior: res['never seen before in run (hallucinated/typo)']+=1; kind='never'
            else:
                # find context of first occurrence
                j=prior.find(i); ctx=prior[max(0,j-160):j+40]
                if re.search(r'hdca|collection',ctx,re.I): res['first seen as collection/element']+=1; kind='coll'
                elif re.search(r'history_id|"histories',ctx): res['seen as history id']+=1; kind='hist'
                else: res['seen earlier as dataset (other history/deleted?)']+=1; kind='ds'
            if len(ex)<8 and random.random()<0.3: ex.append((kind,s['task'],s['run_id'],e['line'],i,e['args'][:160]))
print(res)
for x in ex: print(x)
