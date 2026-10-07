"""Build condensed, outcome-blinded transcripts and stratified samples for three AI-assisted coding tasks.

D  verification steps in correct and incorrect runs (coder blind to the grade);
A1 second rater for the failure-class codebook (coder blind to the rule-based class);
A2 second rater for the BixBench-Verified-50 failure-cause audit (coder blind to the audit labels).
Seed 20261002. Writes the keys and items into this folder and the transcripts into ./transcripts (regenerable; not
kept, because they contain the agents' full outputs). A2 transcripts show the BixBench-Verified-50 reference answer
(ground_truth/BixBench, opened only after every answer was fixed).
"""
import glob
import gzip
import json
import os
import re
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))   # keys and items are written here; transcripts to ./transcripts (not kept)
sys.path.insert(0, os.path.join(ROOT, 'manuscript_narrative'))
PRIMARY = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
           'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
           'codex_deepseek_v4_pro': 'DeepSeek V4 Pro'}
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
rng = np.random.default_rng(20261002)


def clip(s, n):
    s = '' if s is None else str(s)
    s = s.replace('\r', '')
    return s if len(s) <= n else s[:n] + f' …[{len(s) - n} more chars]'


def condense(trace, max_cmd=900, max_out=500, max_msg=900):
    """Agent messages, commands with exit codes and output, Galaxy interface calls and file changes, in order."""
    lines, n = [], 0
    path = trace if os.path.exists(trace) else trace + '.gz'
    op = gzip.open if path.endswith('.gz') else open
    for raw in op(path, 'rt'):
        try:
            e = json.loads(raw)
        except ValueError:
            continue
        if e.get('type') != 'item.completed':
            continue
        it = e.get('item') or {}
        t = it.get('type')
        n += 1
        if t == 'agent_message':
            lines.append(f'[{n}] AGENT: {clip(it.get("text"), max_msg)}')
        elif t == 'reasoning':
            lines.append(f'[{n}] REASONING: {clip(it.get("text"), max_msg)}')
        elif t == 'command_execution':
            lines.append(f'[{n}] COMMAND (exit {it.get("exit_code")}): {clip(it.get("command"), max_cmd)}')
            out = it.get('aggregated_output')
            if out:
                lines.append(f'     OUTPUT: {clip(out, max_out)}')
        elif t == 'mcp_tool_call':
            args = json.dumps(it.get('arguments'))
            res = it.get('result')
            if isinstance(res, dict):
                txt = ' '.join(c.get('text', '') for c in (res.get('content') or []) if isinstance(c, dict))
            else:
                txt = str(res)
            err = (it.get('error') or {}).get('message') if isinstance(it.get('error'), dict) else it.get('error')
            lines.append(f'[{n}] GALAXY CALL {it.get("tool")} ({it.get("status")}): ARGS {clip(args, max_cmd)}')
            lines.append(f'     RESULT: {clip(err or txt, max_out)}')
        elif t == 'file_change':
            lines.append(f'[{n}] FILE CHANGE: {", ".join(c.get("path", "") for c in it.get("changes") or [])}')
        elif t == 'web_search':
            lines.append(f'[{n}] WEB SEARCH: {clip(it.get("query"), 300)}')
    return '\n'.join(lines)


def load_summaries():
    rows = []
    for raw in gzip.open(os.path.join(ROOT, 'manuscript_material/source_data/derived/run_summaries.jsonl.gz'), 'rt'):
        s = json.loads(raw)
        if s['model'] in PRIMARY:
            s['cfg'] = PRIMARY[s['model']]
            rows.append(s)
    return rows


def main():
    summ = load_summaries()
    runs = pd.read_csv(os.path.join(ROOT, 'manuscript_narrative/original_layout/analysis/accuracy_primary_runs.csv'))
    runs['ok'] = (runs.score >= runs.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    key = {(s['benchmark'], s['task'], s['cfg'], s['condition'], int(s['replicate'])): s for s in summ}
    runs['trace'] = [key.get((b, t, c, e, r), {}).get('trace') for b, t, c, e, r in
                     zip(runs.benchmark, runs.task, runs.cfg, runs.env, runs.replicate)]
    runs['run_id'] = [key.get((b, t, c, e, r), {}).get('run_id') for b, t, c, e, r in
                      zip(runs.benchmark, runs.task, runs.cfg, runs.env, runs.replicate)]
    runs = runs[runs.trace.notna()]
    os.makedirs(os.path.join(HERE, 'transcripts'), exist_ok=True)

    # ---- D: verification steps, 10 runs per benchmark x condition x outcome, at most one run per task per stratum
    pool = runs[runs.benchmark.isin(['BixBench50', 'CompBio'])]
    picks = []
    for (bm, env, ok), g in pool.groupby(['benchmark', 'env', 'ok']):
        g = g.sample(frac=1.0, random_state=int(rng.integers(1e9))).drop_duplicates('task')
        picks.append(g.head(10))
    d = pd.concat(picks).reset_index(drop=True)
    d['code'] = [f'D{i:03d}' for i in rng.permutation(len(d)) + 1]        # coder sees only the code
    for t in d.itertuples():
        with open(os.path.join(HERE, 'transcripts', f'{t.code}.txt'), 'w') as f:
            pp = os.path.join(os.path.dirname(os.path.dirname(t.trace)), 'prompt.txt')
            prompt = open(pp).read() if os.path.exists(pp) else ''
            f.write(f'RUN {t.code} | benchmark {t.benchmark} | condition {t.env}\n')
            f.write('TASK PROMPT (as given to the agent):\n' + clip(prompt, 6000) + '\n\nTRANSCRIPT:\n')
            f.write(condense(t.trace))
    d[['code', 'benchmark', 'task', 'cfg', 'env', 'replicate', 'run_id', 'ok']].to_csv(os.path.join(HERE, 'D_key.csv'),
                                                                                     index=False)
    print('D sample', d.groupby(['benchmark', 'env', 'ok']).size().to_dict())

    # ---- A2: second rater for BixBench failure causes, stratified by audit cause and condition
    led = pd.DataFrame(json.load(open(os.path.join(ROOT, 'analysis_reports/galaxy_improvement_20260924/'
                                                         'v2_trace_friction/ledger.json'))))
    led = led[(led.b == 'BixBench') & ~led.run.str.contains('ClaudeCode')].copy()
    cfgmap = {'GPT-5.5': 'GPT-5.5', 'Sol': 'GPT-5.6 Sol', 'Luna': 'GPT-5.6 Luna', 'DS-Codex': 'DeepSeek V4 Pro'}
    led['cfg'] = led.run.str.extract(r'^[CG] (.+) r\d$')[0].map(cfgmap)
    led['replicate'] = led.run.str.extract(r'r(\d)$')[0].astype(int)
    group = {'RIGOR': 'validation', 'SPEC': 'specification', 'EVALUATOR': 'specification', 'CONTRACT': 'specification',
             'KNOWLEDGE': 'knowledge', 'PLATFORM': 'platform', 'HARNESS': 'harness'}
    led['g'] = led.p.map(group)
    picks = []
    for (g_, cond), x in led.groupby(['g', 'cond']):
        k = max(2, int(round(len(x) * 40 / len(led))))
        picks.append(x.sample(n=min(k, len(x)), random_state=int(rng.integers(1e9))))
    a2 = pd.concat(picks).reset_index(drop=True)
    reference = {}
    for path in glob.glob(os.path.join(ROOT, 'ground_truth', 'BixBench', 'task_*.json')):
        g = json.load(open(path))
        reference[g['question_id']] = (g.get('ideal'), g.get('eval_mode'))
    a2['code'] = [f'C{i:03d}' for i in rng.permutation(len(a2)) + 1]
    for t in a2.itertuples():
        s = key[('BixBench50', t.task, t.cfg, t.cond, t.replicate)]
        prompt_path = os.path.join(os.path.dirname(os.path.dirname(s['trace'])), 'prompt.txt')
        prompt = open(prompt_path).read() if os.path.exists(prompt_path) else ''
        ideal, mode = reference[t.task]
        with open(os.path.join(HERE, 'transcripts', f'{t.code}.txt'), 'w') as f:
            f.write(f'RUN {t.code} | BixBench-Verified-50 task {t.task} | condition {t.cond}\n')
            f.write(f'SUBMITTED ANSWER: {s.get("answer")}\n')
            f.write(f'REFERENCE ANSWER: {ideal} | evaluator mode {mode} | tolerance {s.get("tolerance")} | '
                    f'GRADED INCORRECT\n')
            f.write('TASK PROMPT (as given to the agent):\n' + clip(prompt, 6000) + '\n\nTRANSCRIPT:\n')
            f.write(condense(s['trace']))
    a2[['code', 'task', 'cfg', 'cond', 'replicate', 'p', 's']].to_csv(os.path.join(HERE, 'A2_key.csv'), index=False)
    print('A2 sample', a2.groupby(['g', 'cond']).size().to_dict(), len(a2))

    # ---- A1: second rater for failure classes of failed Galaxy requests, about 10 per class
    import narrative_common as nc
    fails = nc.galaxy_failures()
    fails = fails[fails.cfg.isin(['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro'])].copy()
    fails['code'] = fails.failure_class.str.split(' ').str[0]
    errs = {}
    for s in summ:
        if s['condition'] == 'galaxy':
            for er in s.get('errors') or []:
                errs[(s['run_id'], s['task'], er['line'])] = er
    rows = []
    for cls, x in fails.groupby('code'):
        x = x.sample(n=min(10, len(x)), random_state=int(rng.integers(1e9)))
        for t in x.itertuples():
            er = errs.get((t.run_id, t.task, t.line), {})
            rows.append(dict(rule_class=t.failure_class, tool=t.tool, status=er.get('status'),
                             error=clip(er.get('err'), 700), args=clip(er.get('args'), 500)))
    a1 = pd.DataFrame(rows).sample(frac=1.0, random_state=7).reset_index(drop=True)
    a1['code'] = [f'R{i:03d}' for i in range(1, len(a1) + 1)]
    a1[['code', 'tool', 'status', 'error', 'args']].to_json(os.path.join(HERE, 'A1_items.json'), orient='records',
                                                             indent=1)
    a1[['code', 'rule_class']].to_csv(os.path.join(HERE, 'A1_key.csv'), index=False)
    print('A1 items', len(a1))
    sizes = {f: os.path.getsize(os.path.join(HERE, 'transcripts', f)) for f in os.listdir(os.path.join(HERE, 'transcripts'))}
    print('transcript sizes (KB): median', np.median(list(sizes.values())) / 1024, 'max', max(sizes.values()) / 1024)


if __name__ == '__main__':
    main()
