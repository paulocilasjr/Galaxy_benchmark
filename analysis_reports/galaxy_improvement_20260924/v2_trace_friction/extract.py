"""Extract per-run call-level summaries and compact call logs from all archived traces."""
import collections
import gzip
import json
import os
import re
import sys

ROOT = '/Users/4475918/Projects/Galaxy_benchmark'
OUT = os.path.dirname(os.path.abspath(__file__))
BDIR = {'BixBench50': 'BixBench_50/analysis', 'CompBio': 'CompBio/analysis', 'IWC': 'IWC/analysis'}

analysis = json.load(open(f'{ROOT}/BixBench50_CompBio_analysis/analysis.json'))
runs = analysis['runs']


def opener(p):
    return gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')


def find_trace(d):
    for rt in (os.path.join(d, 'agent_workspace', 'run_trace'), os.path.join(d, 'run_trace')):
        for name in ('codex_events.jsonl', 'codex_events.jsonl.gz', 'claude_events.jsonl.gz', 'claude_events.jsonl'):
            p = os.path.join(rt, name)
            if os.path.exists(p):
                return p
    return None


def parse_mcp_result(res):
    """Return (status, error, text) from an MCP result payload."""
    if res is None:
        return None, None, ''
    sc = None
    text = ''
    if isinstance(res, dict):
        sc = res.get('structured_content')
        content = res.get('content') or []
        if isinstance(content, list):
            text = '\n'.join(c.get('text', '') for c in content if isinstance(c, dict))
        elif isinstance(content, str):
            text = content
    elif isinstance(res, str):
        text = res
    elif isinstance(res, list):
        text = '\n'.join(c.get('text', '') if isinstance(c, dict) else str(c) for c in res)
    if not isinstance(sc, dict):
        try:
            sc = json.loads(text)
        except Exception:
            sc = None
    status = err = None
    if isinstance(sc, dict):
        status = sc.get('status')
        err = sc.get('error') or sc.get('failure_summary')
        if not err and sc.get('errors'):
            err = 'VALIDATION ' + json.dumps(sc.get('errors'), ensure_ascii=False)
        if not err and status in ('failed', 'udt_creation_failed') and isinstance(sc.get('jobs'), list):
            diags = [j.get('failure_diagnostic') or {} for j in sc['jobs'] if isinstance(j, dict)]
            phases = sorted({d.get('phase') for d in diags if d.get('phase')})
            err = 'NO_DIAGNOSTIC phase=' + ','.join(phases) if phases else None
        # blocking runs may report job states
        if status is None and 'state' in sc:
            status = sc.get('state')
    return status, err, text


FAIL_STATUSES = {'failed', 'submission_failed', 'error', 'validation_failed', 'invalid', 'job_failed',
                 'rejected', 'tool_not_found', 'not_found', 'blocked', 'denied', 'cancelled', 'timeout'}


def job_states(text):
    return re.findall(r'"state"\s*:\s*"(\w+)"', text)


def classify(tool, status, err, text, is_error_flag):
    if is_error_flag:
        return 'fail'
    if err:
        return 'fail'
    if status and str(status).lower() in FAIL_STATUSES:
        return 'fail'
    if status == 'start_timeout':
        return 'start_timeout'
    if tool and tool.startswith('run_galaxy') or tool == 'wait_for_galaxy_jobs':
        st = job_states(text[:20000])
        if 'error' in st or 'failed' in st:
            return 'job_error'
    return 'ok'


def short(s, n):
    s = '' if s is None else (s if isinstance(s, str) else json.dumps(s, ensure_ascii=False))
    s = s.replace('\n', '\\n')
    return s if len(s) <= n else s[:n] + f'…[+{len(s) - n}]'


def parse_codex(path):
    events = []
    usage = None
    for ln, line in enumerate(opener(path), 1):
        try:
            e = json.loads(line)
        except Exception:
            continue
        t = e.get('type')
        if t == 'turn.completed':
            usage = e.get('usage')
            continue
        if t != 'item.completed':
            continue
        it = e.get('item') or {}
        ty = it.get('type')
        if ty == 'agent_message':
            events.append(dict(kind='msg', line=ln, text=it.get('text', '')))
        elif ty == 'reasoning':
            events.append(dict(kind='reason', line=ln, text=it.get('text', '')))
        elif ty == 'command_execution':
            events.append(dict(kind='shell', line=ln, cmd=it.get('command', ''), exit=it.get('exit_code'),
                               out=it.get('aggregated_output', '') or ''))
        elif ty == 'mcp_tool_call':
            status, err, text = parse_mcp_result(it.get('result'))
            if it.get('error'):
                err = err or it.get('error')
            events.append(dict(kind='mcp', line=ln, tool=it.get('tool'), args=it.get('arguments'),
                               status=status, err=err, text=text, is_error=bool(it.get('error'))))
        elif ty == 'web_search':
            events.append(dict(kind='web', line=ln, query=it.get('query', '')))
        elif ty == 'file_change':
            events.append(dict(kind='file', line=ln, changes=it.get('changes')))
        elif ty == 'error':
            events.append(dict(kind='error', line=ln, text=it.get('message', '')))
    return events, usage


def parse_claude(path):
    events = []
    pending = {}
    usage = None
    for ln, line in enumerate(opener(path), 1):
        try:
            e = json.loads(line)
        except Exception:
            continue
        t = e.get('type')
        if t == 'result':
            usage = e.get('usage')
        if t not in ('assistant', 'user'):
            continue
        content = (e.get('message') or {}).get('content')
        if not isinstance(content, list):
            continue
        for b in content:
            bt = b.get('type')
            if t == 'assistant' and bt == 'text':
                events.append(dict(kind='msg', line=ln, text=b.get('text', '')))
            elif t == 'assistant' and bt == 'tool_use':
                name = b.get('name', '')
                inp = b.get('input')
                if name.startswith('mcp__'):
                    ev = dict(kind='mcp', line=ln, tool=name.split('__')[-1], args=inp, status=None, err=None, text='',
                              is_error=False)
                elif name == 'Bash':
                    ev = dict(kind='shell', line=ln, cmd=(inp or {}).get('command', ''), exit=None, out='')
                elif name in ('WebSearch', 'WebFetch'):
                    ev = dict(kind='web', line=ln, query=json.dumps(inp))
                else:
                    ev = dict(kind='other', line=ln, tool=name, args=inp, text='')
                events.append(ev)
                pending[b.get('id')] = ev
            elif t == 'user' and bt == 'tool_result':
                ev = pending.get(b.get('tool_use_id'))
                if ev is None:
                    continue
                c = b.get('content')
                if isinstance(c, list):
                    txt = '\n'.join(x.get('text', '') for x in c if isinstance(x, dict))
                else:
                    txt = c if isinstance(c, str) else json.dumps(c)
                if ev['kind'] == 'mcp':
                    status, err, text = parse_mcp_result({'content': [{'type': 'text', 'text': txt}]})
                    ev.update(status=status, err=err, text=txt, is_error=bool(b.get('is_error')))
                elif ev['kind'] == 'shell':
                    ev['out'] = txt
                    ev['exit'] = 1 if b.get('is_error') else 0
                else:
                    ev['text'] = txt
    return events, usage


DISCOVERY = {'search_galaxy_tools', 'inspect_galaxy_tool', 'get_tool_details', 'list_tools', 'search_tools'}
INSPECT = {'inspect_galaxy_history', 'inspect_archive_inventory', 'get_history_contents', 'inspect_galaxy_dataset',
           'inspect_galaxy_job', 'peek_dataset', 'get_dataset', 'download_galaxy_dataset'}


def tool_class(tool):
    if tool in DISCOVERY or (tool and ('search' in tool or tool.startswith('inspect_galaxy_tool'))):
        return 'discovery'
    if tool and tool.startswith('run_galaxy') or tool in ('wait_for_galaxy_jobs', 'run_galaxy_workflow_and_wait'):
        return 'execution'
    if tool and ('inspect' in tool or 'history' in tool or 'dataset' in tool or 'download' in tool or 'peek' in tool):
        return 'inspection'
    return 'other'


def render(meta, events):
    lines = [f"# {meta['benchmark']} {meta['task']} {meta['run_id']}  score={meta.get('score')} answer={short(meta.get('answer'), 200)}"]
    for i, ev in enumerate(events):
        k = ev['kind']
        if k == 'msg':
            lines.append(f"[{i} L{ev['line']}] MSG: {short(ev['text'], 900)}")
        elif k == 'reason':
            lines.append(f"[{i} L{ev['line']}] THINK: {short(ev['text'], 400)}")
        elif k == 'shell':
            lines.append(f"[{i} L{ev['line']}] SHELL exit={ev['exit']}: {short(ev['cmd'], 700)}")
            lines.append(f"      OUT: {short(ev['out'], 700)}")
        elif k == 'mcp':
            cls = ev.get('cls')
            lines.append(f"[{i} L{ev['line']}] MCP {ev['tool']} [{cls}; status={ev['status']}] args={short(ev['args'], 700)}")
            if ev['err']:
                lines.append(f"      ERR: {short(ev['err'], 900)}")
            lines.append(f"      RES: {short(ev['text'], 600)}")
        elif k == 'web':
            lines.append(f"[{i} L{ev['line']}] WEB: {short(ev['query'], 300)}")
        elif k == 'file':
            lines.append(f"[{i} L{ev['line']}] FILE: {short(ev['changes'], 300)}")
        elif k == 'error':
            lines.append(f"[{i} L{ev['line']}] ERROR: {short(ev['text'], 500)}")
        else:
            lines.append(f"[{i} L{ev['line']}] {k.upper()} {ev.get('tool')}: {short(ev.get('args'), 300)} -> {short(ev.get('text'), 300)}")
    return '\n'.join(lines)


def main():
    summaries = []
    os.makedirs(f'{OUT}/logs', exist_ok=True)
    for r in runs:
        d = os.path.join(ROOT, BDIR[r['benchmark']], r['task'], 'source_snapshots', 'huggingface_traces', 'files', r['run_id'])
        tp = find_trace(d)
        s = dict(benchmark=r['benchmark'], task=r['task'], run_id=r['run_id'], model=r['model'], condition=r['condition'],
                 replicate=r['replicate'], score=r['score'], answer=r['answer'], verifier=r.get('verifier'),
                 input_tokens=r.get('input_tokens'), output_tokens=r.get('output_tokens'), trace=tp)
        # evaluation reference
        ep = os.path.join(d, 'evaluation.json')
        if os.path.exists(ep):
            try:
                ev = json.load(open(ep))
                acc = ev.get('accuracy') or {}
                s['expected'] = acc.get('expected_value')
                s['observed'] = acc.get('observed_value')
                s['tolerance'] = acc.get('tolerance')
                s['eval_mode'] = acc.get('mode')
                s['eval_reason'] = acc.get('reason') or ev.get('reason')
                if r['benchmark'] == 'IWC':
                    s['iwc_error'] = ev.get('error')
                    s['iwc_details'] = {k: v for k, v in (ev.get('details') or {}).items() if not isinstance(v, (list, dict))}
            except Exception as ex:
                s['eval_parse_error'] = str(ex)
        if not tp:
            s['trace_missing'] = True
            summaries.append(s)
            continue
        events, usage = (parse_claude if 'claude' in os.path.basename(tp) else parse_codex)(tp)
        mcp_by = collections.Counter()
        fail_by = collections.Counter()
        cls_chars = collections.Counter()
        cls_calls = collections.Counter()
        statuses = collections.Counter()
        errors = []
        for ev in events:
            if ev['kind'] == 'mcp':
                ev['cls'] = classify(ev['tool'], ev['status'], ev['err'], ev['text'], ev['is_error'])
                mcp_by[ev['tool']] += 1
                statuses[f"{ev['tool']}:{ev['cls']}"] += 1
                tc = tool_class(ev['tool'])
                cls_calls[tc] += 1
                cls_chars[tc] += len(ev['text'] or '')
                if ev['cls'] != 'ok':
                    fail_by[ev['tool']] += 1
                    errors.append(dict(line=ev['line'], tool=ev['tool'], cls=ev['cls'], status=ev['status'],
                                       err=short(ev['err'], 600), args=short(ev['args'], 400)))
            elif ev['kind'] == 'shell':
                cls_calls['shell'] += 1
                cls_chars['shell'] += len(ev['out'] or '')
        s.update(
            n_events=len(events),
            n_msg=sum(e['kind'] == 'msg' for e in events),
            n_shell=sum(e['kind'] == 'shell' for e in events),
            n_shell_nonzero=sum(e['kind'] == 'shell' and e['exit'] not in (0, None) for e in events),
            n_web=sum(e['kind'] == 'web' for e in events),
            n_mcp=sum(mcp_by.values()),
            n_mcp_fail=sum(fail_by.values()),
            mcp_by=dict(mcp_by), mcp_fail_by=dict(fail_by), mcp_status=dict(statuses),
            class_calls=dict(cls_calls), class_chars=dict(cls_chars),
            search_queries=[e['args'].get('query') for e in events if e['kind'] == 'mcp' and e['tool'] == 'search_galaxy_tools' and isinstance(e['args'], dict)],
            errors=errors,
            usage=usage,
        )
        summaries.append(s)
        ld = f"{OUT}/logs/{r['benchmark']}/{r['task']}"
        os.makedirs(ld, exist_ok=True)
        with open(f"{ld}/{r['run_id']}.txt", 'w') as fh:
            fh.write(render(r, events))
    with open(f'{OUT}/run_summaries.jsonl', 'w') as fh:
        for s in summaries:
            fh.write(json.dumps(s, default=str) + '\n')
    print('runs', len(summaries), 'missing traces', sum(1 for s in summaries if s.get('trace_missing')))


if __name__ == '__main__':
    main()
