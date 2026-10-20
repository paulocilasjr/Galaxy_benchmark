"""Classify shell commands in Galaxy-track runs: Galaxy API workarounds vs other."""
import json, gzip, re, collections
S=[json.loads(l) for l in open('run_summaries.jsonl')]
def opener(p): return gzip.open(p,'rt',errors='replace') if p.endswith('.gz') else open(p,errors='replace')
ops={'copy_history':r'copy_history|histories/.+/copy|/api/histories\b.*copy','download':r'download_dataset|/display|datasets/.+/download|get_dataset|show_dataset|download','upload':r'upload_file|tools/fetch|upload','job_status':r'show_job|jobs/|wait_for|get_state|state\b','run_tool':r'run_tool|/api/tools\b','history_contents':r'show_history|contents|history_contents','tool_schema':r'build\b|show_tool|/api/tools/.+\?|io_details|tool_inputs'}
res=collections.defaultdict(lambda: collections.Counter())
runs_with=collections.Counter(); total=collections.Counter()
for s in S:
    if s['condition']!='galaxy' or not s.get('trace') or 'claude' in s['trace']: continue
    b=s['benchmark']; total[b]+=1
    n_api=0; kinds=set()
    for l in opener(s['trace']):
        if '"command_execution"' not in l or '"item.completed"' not in l: continue
        try: it=json.loads(l)['item']
        except: continue
        cmd=it.get('command','')
        if re.search(r'bioblend|GalaxyInstance|usegalaxy\.org/api|/api/(histories|datasets|jobs|tools)',cmd):
            n_api+=1
            for k,rx in ops.items():
                if re.search(rx,cmd): kinds.add(k); res[b][k]+=1
        res[b]['_shell']+=1
    res[b]['_api']+=n_api
    if n_api: runs_with[b]+=1
    for k in kinds: res[b]['runs_'+k]+=1
for b in res:
    r=res[b]
    print(b,'runs',total[b],'runs using BioBlend/raw API from shell',runs_with[b],f'({runs_with[b]/total[b]:.0%})','shell cmds',r['_shell'],'API shell cmds',r['_api'],f"({r['_api']/r['_shell']:.0%})")
    print('   runs by op:',{k[5:]:v for k,v in r.items() if k.startswith('runs_')})
