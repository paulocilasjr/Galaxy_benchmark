"""Replicate-variability analysis: mixed cells per model/track and divergence mechanism of each rejected replicate.

Run after extract.py (needs run_summaries.jsonl). A BixBench cell is task x configuration x track (3 replicates);
it is "mixed" when 1-2 of 3 replicates are accepted. Mechanisms describe what separated the rejected replicate
from its accepted siblings, as established in the trace review (see report addendum).
"""
import collections
import json

S = [json.loads(l) for l in open('run_summaries.jsonl')]
SH = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'Sol', 'codex_gpt_5_6_luna': 'Luna',
      'deepseek_v4_pro_via_codex': 'DS-Codex', 'deepseek_v4_pro_via_claude_code_superseded': 'DS-ClaudeCode'}
MECH = {
    'V1': 'Platform trap hit by this replicate only',
    'V3': 'Environment / package-version drift',
    'V4': 'Convention or definition applied differently',
    'V5': 'Self-implemented method diverged (script or UDT)',
    'V6': 'Final-step slip (sort, count, complement, units)',
    'V7': 'No answer (turn ended / budget)',
    'V8': 'Benchmark-source lookup asymmetry',
}
# (track, task, config-short, replicate) -> mechanism, for rejected replicates in mixed cells
G = {
    ('bix-12-q4', 'DS-ClaudeCode', 1): 'V5', ('bix-12-q4', 'DS-ClaudeCode', 2): 'V5',
    ('bix-14-q1', 'Luna', 2): 'V6',
    ('bix-14-q1', 'DS-Codex', 1): 'V4', ('bix-14-q1', 'DS-Codex', 2): 'V4',
    ('bix-16-q1', 'Luna', 2): 'V6',
    ('bix-16-q1', 'DS-Codex', 1): 'V1', ('bix-16-q1', 'DS-Codex', 3): 'V4',
    ('bix-16-q1', 'DS-ClaudeCode', 2): 'V4', ('bix-16-q1', 'DS-ClaudeCode', 3): 'V4',
    ('bix-16-q3', 'DS-ClaudeCode', 1): 'V6',
    ('bix-22-q1', 'DS-ClaudeCode', 1): 'V4',
    ('bix-24-q2', 'Luna', 3): 'V4',
    ('bix-26-q5', 'DS-Codex', 1): 'V7', ('bix-26-q5', 'DS-Codex', 2): 'V8',
    ('bix-27-q5', 'DS-Codex', 1): 'V7',
    ('bix-27-q5', 'DS-ClaudeCode', 2): 'V5',
    ('bix-28-q3', 'Sol', 1): 'V1',
    ('bix-31-q2', 'DS-Codex', 2): 'V1', ('bix-31-q2', 'DS-Codex', 3): 'V1',
    ('bix-32-q2', 'DS-ClaudeCode', 2): 'V4',
    ('bix-34-q5', 'DS-ClaudeCode', 3): 'V1',
    ('bix-35-q1', 'DS-ClaudeCode', 1): 'V1',
    ('bix-35-q2', 'DS-ClaudeCode', 2): 'V4',
    ('bix-43-q2', 'DS-ClaudeCode', 2): 'V5',
    ('bix-43-q4', 'GPT-5.5', 1): 'V5', ('bix-43-q4', 'DS-ClaudeCode', 2): 'V4',
    ('bix-46-q4', 'DS-Codex', 2): 'V7',
    ('bix-51-q8', 'DS-ClaudeCode', 3): 'V4',
    ('bix-52-q2', 'Luna', 3): 'V4',
    ('bix-52-q7', 'Sol', 3): 'V6', ('bix-52-q7', 'Luna', 2): 'V6', ('bix-52-q7', 'Luna', 3): 'V6',
    ('bix-54-q7', 'DS-Codex', 2): 'V8', ('bix-54-q7', 'DS-Codex', 3): 'V8',
    ('bix-61-q2', 'DS-ClaudeCode', 1): 'V4',
}
C = {
    ('bix-12-q2', 'DS-ClaudeCode', 1): 'V5', ('bix-12-q2', 'DS-ClaudeCode', 2): 'V5',
    ('bix-12-q4', 'Luna', 1): 'V5',
    ('bix-12-q5', 'DS-ClaudeCode', 1): 'V5', ('bix-12-q5', 'DS-ClaudeCode', 3): 'V5',
    ('bix-12-q6', 'Luna', 1): 'V5', ('bix-12-q6', 'DS-ClaudeCode', 2): 'V5', ('bix-12-q6', 'DS-ClaudeCode', 3): 'V5',
    ('bix-16-q1', 'Luna', 3): 'V4', ('bix-16-q1', 'DS-Codex', 1): 'V4', ('bix-16-q1', 'DS-Codex', 2): 'V4',
    ('bix-16-q1', 'DS-ClaudeCode', 2): 'V4', ('bix-16-q1', 'DS-ClaudeCode', 3): 'V4',
    ('bix-16-q4', 'DS-Codex', 2): 'V5', ('bix-16-q4', 'DS-ClaudeCode', 1): 'V5',
    ('bix-24-q2', 'Sol', 1): 'V4',
    ('bix-26-q5', 'DS-ClaudeCode', 1): 'V4', ('bix-26-q5', 'DS-ClaudeCode', 2): 'V4',
    ('bix-27-q5', 'Luna', 3): 'V5', ('bix-27-q5', 'DS-Codex', 2): 'V5',
    ('bix-27-q5', 'DS-ClaudeCode', 1): 'V5', ('bix-27-q5', 'DS-ClaudeCode', 3): 'V5',
    ('bix-30-q3', 'GPT-5.5', 3): 'V4', ('bix-30-q3', 'Luna', 3): 'V4', ('bix-30-q3', 'DS-ClaudeCode', 2): 'V4',
    ('bix-31-q2', 'DS-Codex', 3): 'V5',
    ('bix-32-q2', 'DS-ClaudeCode', 1): 'V5',
    ('bix-35-q2', 'DS-ClaudeCode', 1): 'V5', ('bix-35-q2', 'DS-ClaudeCode', 2): 'V5',
    ('bix-43-q2', 'Sol', 2): 'V3', ('bix-43-q2', 'Sol', 3): 'V3', ('bix-43-q2', 'Luna', 1): 'V3', ('bix-43-q2', 'Luna', 3): 'V3',
    ('bix-43-q4', 'Sol', 3): 'V5', ('bix-43-q4', 'DS-Codex', 1): 'V5',
    ('bix-45-q1', 'Luna', 2): 'V3',
    ('bix-49-q4', 'DS-ClaudeCode', 2): 'V5', ('bix-49-q4', 'DS-ClaudeCode', 3): 'V5',
    ('bix-52-q7', 'DS-ClaudeCode', 3): 'V7',
    ('bix-53-q5', 'DS-ClaudeCode', 3): 'V6',
    ('bix-54-q7', 'DS-Codex', 1): 'V8', ('bix-54-q7', 'DS-Codex', 3): 'V8',
    ('bix-55-q1', 'Sol', 1): 'V3', ('bix-55-q1', 'Luna', 3): 'V3', ('bix-55-q1', 'DS-ClaudeCode', 2): 'V5',
}


def main():
    B = [s for s in S if s['benchmark'] == 'BixBench50']
    cells = collections.defaultdict(list)
    for s in B:
        cells[(s['condition'], s['model'], s['task'])].append(s)
    mech = collections.Counter()
    by_model = collections.Counter()
    for (cond, m, t), rs in cells.items():
        k = sum(r['score'] == 1 for r in rs)
        if not 0 < k < 3:
            continue
        by_model[(cond, SH[m])] += 1
        table = G if cond == 'galaxy' else C
        for r in rs:
            if r['score'] == 0:
                key = (t, SH[m], r['replicate'])
                if key not in table:
                    raise SystemExit(f'unclassified {cond} {key}')
                mech[(cond, table[key])] += 1
                mech[(cond, SH[m], table[key])] += 1
    assert sum(v for k, v in mech.items() if len(k) == 2 and k[0] == 'galaxy') == len(G)
    assert sum(v for k, v in mech.items() if len(k) == 2 and k[0] == 'open_ended_code') == len(C)
    print('mixed cells:', {k: v for k, v in sorted(by_model.items())})
    for v, name in MECH.items():
        print(f"| {v} {name} | {mech[('galaxy', v)]} | {mech[('open_ended_code', v)]} |")
    for cond in ['galaxy', 'open_ended_code']:
        for m in SH.values():
            row = {v: mech[(cond, m, v)] for v in MECH if mech[(cond, m, v)]}
            if row:
                print(cond, m, row)


if __name__ == '__main__':
    main()
