import re, sys, hashlib, json
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[3]; OUT=Path(sys.argv[1])
FOLDERS={'BixBench50':'BixBench_50','CompBio':'CompBio','IWC':'IWC'}
df=pd.read_csv(OUT/'per_run_design_metadata.csv',low_memory=False)
ev_prompts={}
for b,f in FOLDERS.items():
    for p in (ROOT/f/'analysis').glob('*/history_analysis_evidence.json'):
        d=json.load(open(p)); ev_prompts[(b,d['task']['task_id'])]=d['task'].get('prompt')
rows=[]
for r in df.itertuples():
    snap=ROOT/FOLDERS[r.benchmark]/'analysis'/r.task/'source_snapshots/huggingface_traces/files'/r.run_id
    p=snap/'prompt.txt'
    if not p.exists(): p=snap/'agent_workspace/prompt.txt'
    t=p.read_text(errors='replace')
    q=ev_prompts.get((r.benchmark,r.task))
    body=t
    if q and q in body: body=body.replace(q,'<TASK>')
    # strip task-specific lines: input listings, seed history details, history IDs, sizes
    lines=[l for l in body.splitlines() if not re.match(r'\s*- (inputs/|ID:|Name:|Input datasets:|History ID:)',l) and not re.search(r'\(\d+ bytes\)',l)]
    if r.benchmark=='CompBio':
        lines=[l for l in lines if not l.startswith('QUESTION:')]
    sig='\n'.join(lines)
    m=re.search(r'You have (\d+) minutes',t)
    rows.append({'benchmark':r.benchmark,'task':r.task,'run_id':r.run_id,
        'stated_minutes':int(m.group(1)) if m else None,
        'no_local_inputs_staged':'No local input files were staged' in t,
        'galaxy_not_required':'Galaxy is not required' in t,
        'mentions_skills':'skill' in t.lower(),
        'udt_mentioned':bool(re.search(r'\bUDTs?\b',t)) or ('user-defined tool' in t.lower()),
        'start_timeout_300':'start_timeout_seconds=300' in t,
        'iwc_analysis_steps_jsonl':'analysis_steps.jsonl' in t,
        'iwc_concise_log':'concise execution log' in t,
        'compbio_galaxy_promptv2_marker':'Your objective is to solve the scientific problem correctly' in t,
        'compbio_galaxy_old_marker':'Galaxy is the execution environment for this task, not the scientific method' in t,
        'no_wallclock_limit_instruction':'do not set a wall-clock time limit' in t,
        'mentions_internet':'internet' in t.lower(),
        'signature_sha256':hashlib.sha256(sig.encode()).hexdigest()[:12],
        'signature_words':len(re.findall(r'\b\w+\b',sig))})
pd.DataFrame(rows).to_csv(OUT/'prompt_phrases.csv',index=False)
