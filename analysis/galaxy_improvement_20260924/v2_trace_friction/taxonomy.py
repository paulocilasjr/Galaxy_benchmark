"""Classify every failed Galaxy MCP call and summarize friction by benchmark and outcome."""
import collections
import json
import re
import statistics as st

S = [json.loads(l) for l in open('run_summaries.jsonl')]

RULES = [
    # pre-submission interface friction
    ('A1 tool-schema needs history context', r'History unavailable\. Please specify a valid history id'),
    ('A5 ID handling (wrong/foreign/truncated IDs)', r'Wrong\s+id|invalid dataset id|History is not owned|unable to decode|not owned by user'),
    ('A2 tool ID not found / guessed', r'Tool not found|Could not find tool with id'),
    ('A6 UDT representation schema', r"\('body', 'representation'|from_work_dir|String should match pattern|Extra inputs are not permitted|discriminator|udt_creation|representation"),
    ('A3 nested-parameter key structure', r'invalid key structure|received conflicting value|must be set for non optional|submitted for conditional parameter'),
    ('A7 upload / datatype registry', r'Requested extension .* unknown|create file url|upload_failed|cannot upload|No data was entered in the upload'),
    ('A8 server / transport / rate-limit', r'<!DOCTYPE HTML|<html|Uncaught exception|Too Many Requests|Transport closed|timed out|Cannot execute tool \[__DATA_FETCH__\]|Required parameter\(s\) kwd'),
    ('A4 parameter value / datatype validation', r'VALIDATION|ParameterValueError|No value provided|invalid option|required format|collection supplied|at least \d+ datasets|Field requires a value|cannot use dataset collection|Parameter validation error|Cannot split collection'),
    # post-submission job failures
    ('B1 UDT container missing dependency', r'there is no package called|ModuleNotFoundError|No module named|externally-managed|command not found|: not found|ImportError|cannot open shared object'),
    ('B4 input format / compression / index', r'gzip|magic|Could not parse|unrecognized|unindexable|index|not a valid|EOF|truncated file|UnicodeDecodeError'),
    ('B5 memory / resource', r'MemoryError|Killed|out of memory|OOM|oom|Cannot allocate'),
    ('B2 job error with no diagnostic', r'NO_DIAGNOSTIC|^[0-9a-f]{32}=error(?! \()'),
    ('B3 tool runtime error (stderr)', r'tool_stderr|stderr|Traceback|recent call last|line \d+|Error in|Exception|exit_code|Error:|error:'),
]


def classify(er):
    txt = (er.get('err') or '') + ' ' + (er.get('status') or '')
    if er['tool'] == 'run_galaxy_udt_and_wait' and er.get('status') == 'udt_creation_failed':
        return 'A6 UDT representation schema'
    for name, rx in RULES:
        if re.search(rx, txt):
            return name
    if er.get('status') in ('validation_failed',):
        return 'A4 parameter value / datatype validation'
    if er.get('status') in ('timeout', 'start_timeout'):
        return 'A8 server / transport / rate-limit'
    if not (er.get('err') or '').strip():
        return 'B2 job error with no diagnostic'
    return 'Z unclassified'


def main():
    cat_bench = collections.Counter()
    cat_tool = collections.Counter()
    examples = collections.defaultdict(list)
    per_run = {}
    for s in S:
        if s['condition'] != 'galaxy' or not s.get('trace'):
            continue
        cats = collections.Counter()
        for er in s.get('errors') or []:
            c = classify(er)
            er['cat'] = c
            cats[c] += 1
            cat_bench[(s['benchmark'], c)] += 1
            cat_tool[(c, er['tool'])] += 1
            if len(examples[c]) < 400:
                examples[c].append(dict(bench=s['benchmark'], task=s['task'], run=s['run_id'], line=er['line'],
                                        tool=er['tool'], args=er['args'], err=er['err']))
        per_run[(s['benchmark'], s['task'], s['run_id'])] = cats
    benches = ['BixBench50', 'CompBio', 'IWC']
    cats = sorted({c for (_, c) in cat_bench})
    print('| Category | ' + ' | '.join(benches) + ' | Total |')
    for c in cats:
        row = [cat_bench[(b, c)] for b in benches]
        print(f'| {c} | ' + ' | '.join(map(str, row)) + f' | {sum(row)} |')
    tot = [sum(cat_bench[(b, c)] for c in cats) for b in benches]
    print('| total | ' + ' | '.join(map(str, tot)) + f' | {sum(tot)} |')
    # MCP call totals
    for b in benches:
        runs = [s for s in S if s['benchmark'] == b and s['condition'] == 'galaxy' and s.get('trace')]
        n = sum(s['n_mcp'] for s in runs)
        f = sum(s['n_mcp_fail'] for s in runs)
        pre = sum(v for s in runs for k, v in per_run[(b, s['task'], s['run_id'])].items() if k.startswith('A'))
        post = sum(v for s in runs for k, v in per_run[(b, s['task'], s['run_id'])].items() if k.startswith('B'))
        runs_with_pre = sum(1 for s in runs if any(k.startswith('A') for k in per_run[(b, s['task'], s['run_id'])]))
        print(b, 'runs', len(runs), 'mcp calls', n, 'failed', f, f'({f / n:.1%})', 'pre-submission', pre, 'post', post,
              'runs with >=1 pre-sub friction', runs_with_pre)
    json.dump({f'{k[0]}|{k[1]}': v for k, v in cat_tool.items()}, open('cat_tool.json', 'w'), indent=1)
    json.dump(examples, open('friction_examples.json', 'w'), indent=1)
    json.dump({'|'.join(k): v for k, v in per_run.items()}, open('per_run_friction.json', 'w'))


if __name__ == '__main__':
    main()
