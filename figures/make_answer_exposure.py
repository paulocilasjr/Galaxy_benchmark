"""Tier each primary run's exposure to benchmark reference answers during the run.

verified  : text the agent received (command output or connector result) contains this task's reference answer next to
            its question or an 'ideal' field (BixBench, where references are public), or other agents' recorded answers;
probable  : the run opened a page or file that publishes reference answers or other agents' answers (BixBench dataset
            files or viewer, published agent-trace datasets), but the content is not in the trace (web pages are not logged);
attempted : the run searched the web for the benchmark, the task or its answer, without opening such a source;
none      : otherwise. Benchmark input-data repositories (no answers) count as attempted only if the query asks for answers.
"""
import gzip, json, os, re, glob
import pandas as pd
ROOT=os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
HERE=os.path.dirname(os.path.abspath(__file__))  # writes figures/answer_exposure_tiers.csv
PRIMARY={'codex_gpt_5_5':'GPT-5.5','codex_gpt_5_6_sol':'GPT-5.6 Sol','codex_gpt_5_6_luna':'GPT-5.6 Luna',
         'deepseek_v4_pro_via_codex':'DeepSeek V4 Pro','codex_deepseek_v4_pro_0813':'DeepSeek V4 Pro','codex_deepseek_v4_pro':'DeepSeek V4 Pro'}
ANSWER_SOURCES=re.compile(r'futurehouse/BixBench|BixBench\.jsonl|phylobio/BixBench|trustworthy-biology-agents-traces|'
                          r'agent[-_]traces|/traces/compbiobench|harbor_base_tasks|harbor_tasks', re.I)
BENCH=re.compile(r'bixbench|compbiobench|compbio[-_ ]?bench|BixBench-Verified|bix-\d+-q\d+', re.I)
ASK_ANSWER=re.compile(r'\banswer|ideal|ground.?truth|solution|key\b', re.I)
gt={}
for f in glob.glob(os.path.join(ROOT,'ground_truth/BixBench/task_*.json')):
    d=json.load(open(f)); gt[d['question_id']]=str(d.get('ideal') or '')
qtext={}
for f in glob.glob(os.path.join(ROOT,'experiments/BixBench/task_*.json')):
    d=json.load(open(f)); qtext[d['question_id']]=re.sub(r'\s+',' ',str(d.get('prompt_task') or ''))[:60]
rows=[]
for raw in gzip.open(os.path.join(ROOT,'manuscript_material/source_data/derived/run_summaries.jsonl.gz'),'rt'):
    s=json.loads(raw)
    if s['model'] not in PRIMARY or not s.get('trace'): continue
    path=s['trace'] if os.path.exists(s['trace']) else s['trace']+'.gz'
    if not os.path.exists(path): continue
    op=gzip.open if path.endswith('.gz') else open
    tier, evidence = 'none', ''
    ideal=gt.get(s['task'],''); q=qtext.get(s['task'],'')
    def bump(t, ev):
        global_rank={'none':0,'attempted':1,'probable':2,'verified':3}
        nonlocal_store.append((t,ev))
    nonlocal_store=[]
    with op(path,'rt',newline='\n') as f:
        for line in f:
            if not (BENCH.search(line) or ANSWER_SOURCES.search(line)): continue
            try: e=json.loads(line)
            except ValueError: continue
            if e.get('type')!='item.completed': continue
            it=e.get('item') or {}; t=it.get('type')
            if t=='web_search':
                act=json.dumps({k:it.get(k) for k in ('query','action')})
                if ANSWER_SOURCES.search(act): nonlocal_store.append(('probable','opened '+ANSWER_SOURCES.search(act).group(0)))
                elif BENCH.search(act) or (q and q[:40].lower() in act.lower()):
                    if ASK_ANSWER.search(act) or BENCH.search(act): nonlocal_store.append(('attempted','search: '+act[:120]))
            elif t in ('command_execution','mcp_tool_call'):
                cmd=str(it.get('command') or json.dumps(it.get('arguments')))
                out=str(it.get('aggregated_output') or json.dumps(it.get('result')))[:2_000_000]
                if t=='mcp_tool_call' and str(it.get('server','')).endswith(('galaxy_execute','galaxy_wait')): continue
                src=ANSWER_SOURCES.search(cmd)
                if src or (BENCH.search(cmd) and re.search(r'https?://|curl|wget|hf_hub|load_dataset|urlopen|requests', cmd)):
                    verified=False
                    if s['benchmark']=='BixBench50' and ideal:
                        for m in re.finditer(re.escape(ideal), out):
                            window=out[max(0,m.start()-3000):m.end()+200]
                            if '"ideal"' in window or (q and q[:40] in window): verified=True; break
                    if src and re.search(r'"(answer|predicted_answer|final_answer|submitted_answer)"\s*:', out): verified=True
                    if verified: nonlocal_store.append(('verified',(src.group(0) if src else 'benchmark source')+' content received'))
                    elif src: nonlocal_store.append(('probable','fetched '+src.group(0)))
                    else: nonlocal_store.append(('attempted','fetched benchmark data source'))
    rank={'none':0,'attempted':1,'probable':2,'verified':3}
    if nonlocal_store:
        tier,evidence=max(nonlocal_store,key=lambda x: rank[x[0]])
    rows.append(dict(benchmark=s['benchmark'],task=s['task'],cfg=PRIMARY[s['model']],env=s['condition'],
                     replicate=int(s['replicate']),score=s['score'],tier=tier,evidence=evidence[:160]))
df=pd.DataFrame(rows)
df.to_csv(os.path.join(HERE,'answer_exposure_tiers.csv'),index=False)
pd.set_option('display.width',250)
print(pd.crosstab([df.benchmark,df.cfg],[df.env,df.tier]))
print(df[df.tier.isin(['verified','probable'])].groupby(['benchmark','tier','evidence']).size().to_string()[:3000])
