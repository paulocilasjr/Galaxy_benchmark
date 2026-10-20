"""Read-only helpers: discover archived runs and normalise their agent traces into a list of actions."""
import glob, gzip, json, os, re

# archive roots (old layout -> new layout); the first existing one is used
ROOTS = {'BixBench50': ['runs/BixBench_50', 'BixBench_50'], 'CompBio': ['runs/CompBio', 'CompBio'],
         'IWC': ['runs/IWC', 'IWC'], 'TokenOpt': ['runs/token_optimization', 'token_improvment']}
PRIMARY_MODELS = {'codex_gpt_5_5': 'GPT-5.5', 'gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'gpt_5_6_sol': 'GPT-5.6 Sol',
                  'codex_gpt_5_6_luna': 'GPT-5.6 Luna', 'gpt_5_6_luna': 'GPT-5.6 Luna',
                  'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
                  'codex_deepseek_v4_pro': 'DeepSeek V4 Pro'}
OTHER_MODELS = {'deepseek_v4_pro_via_claude_code_superseded': 'DeepSeek V4 Pro (Claude Code, superseded)',
                'codex_gpt_6_astra': 'GPT-6 Astra', 'codex_gpt_5_6_sol_token_optimization_oct_2026': 'GPT-5.6 Sol (token optimization)'}


def root(repo, bench):
    for r in ROOTS[bench]:
        if os.path.isdir(os.path.join(repo, r)):
            return r
    raise FileNotFoundError(bench)


def parse_run_id(run_id):
    m = re.match(r'^(galaxy|open_ended_code)_(.+)_r(\d+)$', run_id)
    cond, model, rep = m.group(1), m.group(2), int(m.group(3))
    cfg = PRIMARY_MODELS.get(model) or OTHER_MODELS.get(model) or model
    return cond, model, cfg, rep


def discover(repo):
    """Every archived run folder, with the run set it belongs to."""
    out = []
    for bench in ROOTS:
        base = root(repo, bench)
        pats = [(f'{base}/analysis/*/source_snapshots/huggingface_traces/files/*', None)]
        if bench == 'CompBio':
            pats.append((f'{base}/analysis/*/versions/pre_rerun_20261005/source_snapshots/huggingface_traces/files/*',
                         'original run, replaced by the 2026-10-05 reviewed rerun'))
        for pat, note in pats:
            for d in sorted(glob.glob(os.path.join(repo, pat))):
                if not os.path.isdir(d):
                    continue
                rel = os.path.relpath(d, repo)
                task = rel.split('/analysis/')[1].split('/')[0]
                cond, model, cfg, rep = parse_run_id(os.path.basename(d))
                if note:
                    rset = note
                elif bench == 'TokenOpt':
                    rset = 'token-optimization batch (Oct 2026)'
                elif 'superseded' in model:
                    rset = 'superseded configuration (DeepSeek preview via Claude Code)'
                elif 'astra' in model:
                    rset = 'extra configuration (GPT-6 Astra, open-ended code only)'
                elif bench == 'IWC' and task.startswith('wf_007'):
                    rset = 'superseded run (site replaced wf_007 on 2026-10-12)'
                else:
                    rset = 'primary'
                out.append(dict(benchmark='BixBench50' if bench == 'TokenOpt' else bench, archive=bench, task=task,
                                run_id=os.path.basename(d), condition=cond, model=model, cfg=cfg, replicate=rep,
                                run_set=rset, run_dir=rel))
    return out


def trace_files(repo, run_dir):
    fs = []
    for dp, _, names in os.walk(os.path.join(repo, run_dir)):
        for n in names:
            if re.match(r'^(codex|claude)_events\.jsonl(\.gz)?$', n):
                fs.append(os.path.join(dp, n))
    # an uncompressed and a compressed copy of the same trace: keep both only if they differ in size after reading
    return sorted(fs)


def _open(p):
    return gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')


def _result_text(res):
    if res is None:
        return ''
    if isinstance(res, str):
        return res
    if isinstance(res, dict):
        parts = []
        for c in res.get('content') or []:
            if isinstance(c, dict) and c.get('type') == 'text':
                parts.append(c.get('text', ''))
        if res.get('structured_content') and not parts:
            parts.append(json.dumps(res['structured_content']))
        return '\n'.join(parts) if parts else json.dumps(res)[:200000]
    return json.dumps(res)[:200000]


def actions(path, max_out=400000):
    """Normalised actions of one trace: dicts with i, kind, tool, server, text (command/arguments), out, status."""
    acts, pending, is_claude = [], {}, 'claude_events' in path
    with _open(path) as f:
        for ln, raw in enumerate(f):
            raw = raw.strip()
            if not raw.startswith('{'):
                continue
            try:
                e = json.loads(raw)
            except ValueError:
                continue
            if not is_claude:
                if e.get('type') not in ('item.completed', 'item.started'):
                    continue
                it = e.get('item') or {}
                t = it.get('type')
                if e['type'] == 'item.started':
                    if t in ('command_execution', 'mcp_tool_call'):
                        pending[it.get('id')] = (ln, it)
                    continue
                pending.pop(it.get('id'), None)
                acts.append(_codex(it, ln, max_out))
            else:
                msg = e.get('message') or {}
                content = msg.get('content') if isinstance(msg.get('content'), list) else []
                if e.get('type') == 'assistant':
                    for c in content:
                        if c.get('type') == 'tool_use':
                            a = _claude_use(c, ln)
                            pending[c.get('id')] = a
                            acts.append(a)
                        elif c.get('type') == 'text' and c.get('text'):
                            acts.append(dict(line=ln, kind='msg', tool='', server='', text=c['text'][:20000], out='', status=''))
                elif e.get('type') == 'user':
                    for c in content:
                        if c.get('type') == 'tool_result' and c.get('tool_use_id') in pending:
                            a = pending.pop(c['tool_use_id'])
                            cc = c.get('content')
                            if isinstance(cc, list):
                                cc = '\n'.join(x.get('text', '') for x in cc if isinstance(x, dict))
                            a['out'] = str(cc or '')[:max_out]
                            a['status'] = 'error' if c.get('is_error') else 'ok'
    for ln, it in pending.values() if not is_claude else []:
        a = _codex(it, ln, max_out); a['status'] = 'unfinished'; acts.append(a)
    acts.sort(key=lambda a: a['line'])
    for i, a in enumerate(acts):
        a['i'] = i
    return acts


def _codex(it, ln, max_out):
    t = it.get('type')
    if t == 'command_execution':
        return dict(line=ln, kind='shell', tool='shell', server='', text=str(it.get('command') or ''),
                    out=str(it.get('aggregated_output') or '')[:max_out], status=str(it.get('exit_code')))
    if t == 'mcp_tool_call':
        err = it.get('error')
        return dict(line=ln, kind='mcp', tool=str(it.get('tool') or ''), server=str(it.get('server') or ''),
                    text=json.dumps(it.get('arguments'), ensure_ascii=False)[:200000],
                    out=(_result_text(it.get('result')) or (json.dumps(err) if err else ''))[:max_out],
                    status=str(it.get('status') or ''))
    if t == 'web_search':
        act = it.get('action') or {}
        return dict(line=ln, kind='web', tool='web_' + str(act.get('type') or 'search'), server='',
                    text=json.dumps({'query': it.get('query'), **act}, ensure_ascii=False), out='', status='')
    if t == 'file_change':
        return dict(line=ln, kind='file_change', tool='apply_patch', server='',
                    text=json.dumps(it.get('changes'), ensure_ascii=False)[:20000], out='', status=str(it.get('status') or ''))
    if t == 'agent_message':
        return dict(line=ln, kind='msg', tool='', server='', text=str(it.get('text') or '')[:20000], out='', status='')
    if t == 'reasoning':
        return dict(line=ln, kind='reasoning', tool='', server='', text=str(it.get('text') or '')[:20000], out='', status='')
    return dict(line=ln, kind=str(t), tool='', server='', text=json.dumps(it, ensure_ascii=False)[:5000], out='', status='')


def _claude_use(c, ln):
    name, inp = c.get('name') or '', c.get('input') or {}
    kind = {'Bash': 'shell', 'Read': 'file_read', 'Grep': 'search', 'Glob': 'search', 'WebFetch': 'web', 'WebSearch': 'web',
            'Write': 'file_change', 'Edit': 'file_change', 'NotebookEdit': 'file_change'}.get(name, 'mcp' if name.startswith('mcp__') else 'tool')
    text = inp.get('command') if name == 'Bash' else json.dumps(inp, ensure_ascii=False)
    server = name.split('__')[1] if name.startswith('mcp__') else ''
    tool = name.split('__')[-1] if name.startswith('mcp__') else name
    if name == 'WebFetch':
        tool = 'web_open_page'
    elif name == 'WebSearch':
        tool = 'web_search'
    return dict(line=ln, kind=kind, tool=tool, server=server, text=str(text)[:200000], out='', status='')
