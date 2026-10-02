"""Per-call table of Galaxy MCP interface activity from archived agent traces.

Read-only on the repository. Streams each primary trace listed in
manuscript_material/source_data/derived/run_summaries.jsonl.gz (condition == galaxy)
and writes calls.csv.gz, salvaged_calls.csv.gz, tool_mismatch_rates.csv and
summary.json next to this script.

Event parsing and the legacy failure classification (`extract_class`) are copied from
analysis_reports/galaxy_improvement_20260924/v2_trace_friction/extract.py so that call
and failure totals reconcile with run_summaries n_mcp / n_mcp_fail.
"""
import collections
import gzip
import json
import os
import re
import sys
from multiprocessing import Pool

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
RUN_SUMMARIES = f'{ROOT}/manuscript_material/source_data/derived/run_summaries.jsonl.gz'
OUT = os.path.dirname(os.path.abspath(__file__))

# Galaxy MCP server namespaces exposed to agents (one execute + one wait server per benchmark).
GALAXY_SERVERS = {'bixbench_galaxy_execute', 'bixbench_galaxy_wait', 'galaxy_execute', 'galaxy_wait',
                  'iwc_galaxy_execute', 'iwc_galaxy_wait'}
# Galaxy interface tool functions.
GALAXY_TOOLS = {'run_galaxy_tool_and_wait', 'run_galaxy_udt_and_wait', 'search_galaxy_tools', 'inspect_galaxy_tool',
                'inspect_galaxy_history', 'wait_for_galaxy_jobs', 'inspect_archive_inventory', 'peek_galaxy_dataset',
                'stage_workspace_file'}
# Codex client built-ins that are logged as mcp_tool_call items but are not Galaxy interface functions.
CODEX_BUILTINS = {'list_mcp_resources', 'list_mcp_resource_templates'}

OUTAGE_SIG = re.compile(r'no destinations are available|no execution destination|training_tag_small_rule', re.I)
HEXID = re.compile(r'\b[0-9a-f]{16,32}\b')
MCP_ITEM_START = re.compile(r'\{"type":"item\.completed","item":\{"id":"[^"]*","type":"mcp_tool_call"')
STDERR_REJECT = re.compile(r'ERROR codex_core::(?:tools::router: error=unsupported call: mcp__|mcp_tool_call: failed to parse tool call arguments)')


# ---------------------------------------------------------------- legacy logic (extract.py)
def parse_mcp_result(res):
    """Return (status, error, text, sc) from an MCP result payload (extract.py logic + sc)."""
    if res is None:
        return None, None, '', None
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
        if status is None and 'state' in sc:
            status = sc.get('state')
    return status, err, text, (sc if isinstance(sc, dict) else None)


FAIL_STATUSES = {'failed', 'submission_failed', 'error', 'validation_failed', 'invalid', 'job_failed',
                 'rejected', 'tool_not_found', 'not_found', 'blocked', 'denied', 'cancelled', 'timeout'}


def job_states_re(text):
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
        st = job_states_re(text[:20000])
        if 'error' in st or 'failed' in st:
            return 'job_error'
    return 'ok'


# ---------------------------------------------------------------- helpers
def opener(p):
    # newline='\n' keeps physical line numbers identical to `sed -n Np` on the decompressed file.
    if p.endswith('.gz'):
        return gzip.open(p, 'rt', errors='replace', newline='\n')
    return open(p, errors='replace', newline='\n')


def split_version(tid):
    if not isinstance(tid, str) or not tid:
        return None, None
    parts = tid.split('/')
    if '/repos/' in tid and len(parts) >= 6:
        return '/'.join(parts[:-1]), parts[-1]
    return tid, None


def as_dict(a):
    if isinstance(a, dict):
        return a
    if isinstance(a, str):
        try:
            v = json.loads(a)
            return v if isinstance(v, dict) else {}
        except Exception:
            return {}
    return {}


def jdump(x):
    return x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)


def norm_ws(s):
    return re.sub(r'\s+', ' ', s).strip()


def build_call(tool, server, args, status, err, text, sc, is_error_flag, transport_error, call_failed):
    """Derive all per-call fields that depend only on the call itself."""
    args = as_dict(args)
    udt = tool == 'run_galaxy_udt_and_wait'
    row = dict(server=server, tool=tool, udt=udt)
    row['galaxy_namespace'] = server in GALAXY_SERVERS
    row['galaxy_server'] = bool(server in GALAXY_SERVERS and tool not in CODEX_BUILTINS)
    row['call_status'] = 'failed' if call_failed else 'completed'
    row['client_rejected'] = bool('<tool_use_error>' in (text or '')[:200])
    row['extract_class'] = classify(tool, status, err, text, is_error_flag)
    row['extract_fail'] = row['extract_class'] != 'ok'
    row['chars_returned'] = len(text or '') if (text or not transport_error) else len(transport_error)
    s = sc or {}
    row['result_status'] = s.get('status') if sc is not None else None
    row['submitted'] = s.get('submitted')
    row['validation_status'] = s.get('validation_status')
    row['elapsed_seconds'] = s.get('elapsed_seconds')
    # tool id: requested (arguments) first, then reported by the result; UDTs use the representation id
    if udt:
        rep = args.get('representation')
        tid = rep.get('id') if isinstance(rep, dict) else None
        if not tid:
            jt = [j.get('tool_id') for j in (s.get('jobs') or []) if isinstance(j, dict) and j.get('tool_id')]
            tid = jt[0] if jt else None
    else:
        tid = args.get('tool_id') or s.get('tool_id')
    tid = tid if isinstance(tid, str) and tid else None
    base, ver = split_version(tid) if not udt else (tid, None)
    row['tool_id_full'] = tid
    row['tool_id_base'] = base
    row['tool_version'] = ver
    # parameter provenance
    pp = s.get('parameter_provenance')
    mism, missing = [], []
    stage = None
    if isinstance(pp, dict):
        row['prov_status'] = pp.get('status')
        row['checked_parameter_count'] = pp.get('checked_parameter_count')
        if 'mismatches' in pp or 'missing_paths' in pp:
            stage = 'validation'
            mism += [m for m in (pp.get('mismatches') or []) if isinstance(m, dict)]
            missing += list(pp.get('missing_paths') or [])
        if isinstance(pp.get('jobs'), list):
            stage = stage or 'post_run'
            for j in pp['jobs']:
                if isinstance(j, dict):
                    mism += [m for m in (j.get('mismatches') or []) if isinstance(m, dict)]
                    missing += list(j.get('missing_paths') or [])
    else:
        row['prov_status'] = None
        row['checked_parameter_count'] = None
    row['prov_stage'] = stage
    row['n_mismatches'] = len(mism) if isinstance(pp, dict) else None
    row['n_substituted'] = sum(1 for m in mism if m.get('resolved') is not None) if isinstance(pp, dict) else None
    row['n_missing_paths'] = len(missing) if isinstance(pp, dict) else None
    mp = ';'.join(sorted({str(m.get('path')) for m in mism}))
    row['mismatch_paths'] = mp[:400] if mp else None
    dp = s.get('provenance')
    row['dataset_prov_status'] = dp.get('status') if isinstance(dp, dict) else None
    # jobs
    jobs = [j for j in (s.get('jobs') or []) if isinstance(j, dict)] if isinstance(s.get('jobs'), list) else []
    row['n_jobs'] = len(jobs) if isinstance(s.get('jobs'), list) else None
    states = [str(j.get('state')) for j in jobs]
    row['job_states'] = ';'.join(states) if states else None
    row['any_job_error'] = any(st in ('error', 'failed') for st in states)
    row['job_ids'] = ';'.join(str(j.get('id')) for j in jobs if j.get('id')) or None
    phases, exits, fails = [], [], []
    for j in jobs:
        fd = j.get('failure_diagnostic') or {}
        if isinstance(fd, dict):
            if fd.get('phase'):
                phases.append(str(fd['phase']))
            if fd.get('exit_code') is not None:
                exits.append(str(fd['exit_code']))
        msg = j.get('failure') or (fd.get('message') if isinstance(fd, dict) else None)
        if msg and msg not in fails:
            fails.append(str(msg))
    row['job_failure_phases'] = ';'.join(sorted(set(phases))) or None
    row['job_exit_codes'] = ';'.join(exits) or None
    # error / diagnostic text
    pieces = []
    if transport_error:
        pieces.append(transport_error)
    if sc is not None:
        if s.get('error'):
            pieces.append(jdump(s['error']))
        if s.get('errors'):
            pieces.append('VALIDATION ' + jdump(s['errors']))
        pieces += fails[:2]
        if not fails and phases:
            pieces.append('phase=' + ','.join(sorted(set(phases))))
        if s.get('failure_summary'):
            pieces.append(jdump(s['failure_summary']))
        if s.get('history_error'):
            pieces.append(jdump(s['history_error']))
        if s.get('failed_input'):
            pieces.append('failed_input ' + jdump(s['failed_input']))
        if call_failed and not pieces:
            pieces.append(text or '')
    elif text and (call_failed or is_error_flag or text.lstrip().startswith(('Error', '<tool_use_error>', 'MCP server'))):
        pieces.append(text)
    pieces = [norm_ws(p) for p in pieces if p]
    row['has_error_text'] = bool(pieces)
    row['error_excerpt'] = ' | '.join(pieces)[:240] if pieces else None
    full = ' '.join(pieces) + ' ' + (text or '')
    row['outage_sig_in_result'] = bool(OUTAGE_SIG.search(full))
    # ids for linking to shell-side outage evidence
    ids = set(j.get('id') for j in jobs if j.get('id'))
    for ref in (s.get('output_dataset_refs') or []):
        if isinstance(ref, dict) and ref.get('id'):
            ids.add(ref['id'])
    for j in jobs:
        for ref in (j.get('output_dataset_refs') or []):
            if isinstance(ref, dict) and ref.get('id'):
                ids.add(ref['id'])
    row['_ids'] = ids
    return row


def sig_ids_from_shell(cmd, out):
    """Hex ids on output lines that carry an outage signature (fallback: ids in the command)."""
    ids, hit = set(), False
    for ln in (out or '').split('\n'):
        if OUTAGE_SIG.search(ln):
            hit = True
            found = HEXID.findall(ln)
            if found:
                ids.update(found)
            else:
                ids.update(HEXID.findall(cmd or ''))
    return hit, ids


# ---------------------------------------------------------------- per-trace parsers
def parse_codex(path):
    calls, salvaged = [], []
    diag = collections.Counter()
    sig_ids = set()
    run_sig = False
    dec = json.JSONDecoder()

    def handle_item(it, ln, sink):
        status, err, text, sc = parse_mcp_result(it.get('result'))
        terr = it.get('error')
        terr_s = None
        if terr:
            err = err or terr
            terr_s = terr.get('message') if isinstance(terr, dict) and terr.get('message') else jdump(terr)
        call_failed = it.get('status') == 'failed'
        row = build_call(it.get('tool'), it.get('server'), it.get('arguments'), status, err, text, sc,
                         bool(terr), terr_s, call_failed)
        row['line'] = ln
        row['result_line'] = ln
        sink.append(row)

    for ln, line in enumerate(opener(path), 1):
        if OUTAGE_SIG.search(line):
            run_sig = True
        try:
            e = json.loads(line)
        except Exception:
            if not line.strip():
                continue
            diag['unparsable_lines'] += 1
            if STDERR_REJECT.search(line):
                diag['stderr_rejected_mcp_attempts'] += 1
            if 'mcp_tool_call' in line:
                diag['unparsable_lines_with_mcp'] += 1
                for m in MCP_ITEM_START.finditer(line):
                    try:
                        o, _ = dec.raw_decode(line, m.start())
                        it = o.get('item') or {}
                        if it.get('type') == 'mcp_tool_call':
                            handle_item(it, ln, salvaged)
                    except Exception:
                        diag['truncated_mcp_completed_fragments'] += 1
            continue
        if e.get('type') != 'item.completed':
            continue
        it = e.get('item') or {}
        ty = it.get('type')
        if ty == 'mcp_tool_call':
            handle_item(it, ln, calls)
        elif ty == 'command_execution':
            hit, ids = sig_ids_from_shell(it.get('command', ''), it.get('aggregated_output', ''))
            if hit:
                diag['shell_outputs_with_outage_sig'] += 1
                sig_ids |= ids
    return calls, salvaged, diag, sig_ids, run_sig


def parse_claude(path):
    calls = []
    diag = collections.Counter()
    pending = {}
    bash_pending = {}
    sig_ids = set()
    run_sig = False
    for ln, line in enumerate(opener(path), 1):
        if OUTAGE_SIG.search(line):
            run_sig = True
        try:
            e = json.loads(line)
        except Exception:
            if line.strip():
                diag['unparsable_lines'] += 1
                if 'mcp__' in line:
                    diag['unparsable_lines_with_mcp'] += 1
            continue
        t = e.get('type')
        if t not in ('assistant', 'user'):
            continue
        content = (e.get('message') or {}).get('content')
        if not isinstance(content, list):
            continue
        for b in content:
            if not isinstance(b, dict):
                continue
            bt = b.get('type')
            if t == 'assistant' and bt == 'tool_use':
                name = b.get('name', '')
                if name.startswith('mcp__'):
                    parts = name.split('__')
                    ev = dict(line=ln, tool=parts[-1], server='__'.join(parts[1:-1]), args=b.get('input'),
                              txt=None, is_error=False, result_line=None)
                    calls.append(ev)
                    pending[b.get('id')] = ev
                elif name == 'Bash':
                    bash_pending[b.get('id')] = (b.get('input') or {}).get('command', '')
            elif t == 'user' and bt == 'tool_result':
                c = b.get('content')
                if isinstance(c, list):
                    txt = '\n'.join(x.get('text', '') for x in c if isinstance(x, dict))
                else:
                    txt = c if isinstance(c, str) else json.dumps(c)
                tid = b.get('tool_use_id')
                if tid in pending:
                    ev = pending.pop(tid)
                    ev.update(txt=txt, is_error=bool(b.get('is_error')), result_line=ln)
                elif tid in bash_pending:
                    hit, ids = sig_ids_from_shell(bash_pending.pop(tid), txt)
                    if hit:
                        diag['shell_outputs_with_outage_sig'] += 1
                        sig_ids |= ids
    rows = []
    for ev in calls:
        if ev['txt'] is None:
            diag['mcp_calls_without_result'] += 1
            status, err, text, sc = None, None, '', None
            call_failed = False
        else:
            status, err, text, sc = parse_mcp_result({'content': [{'type': 'text', 'text': ev['txt']}]})
            call_failed = ev['is_error']
        row = build_call(ev['tool'], ev['server'], ev['args'], status, err, text, sc, ev['is_error'], None, call_failed)
        if ev['txt'] is None:
            row['call_status'] = 'no_result'
        row['line'] = ev['line']
        row['result_line'] = ev['result_line']
        rows.append(row)
    return rows, [], diag, sig_ids, run_sig


def finalize(rows, sig_ids, run_sig):
    idx = 0
    seen_full = collections.Counter()
    seen_base = collections.Counter()
    for r in rows:
        ids = r.pop('_ids', set())
        r['outage_sig_linked'] = bool(ids & sig_ids)
        r['run_outage_sig'] = run_sig
        if r['galaxy_server']:
            r['call_index_in_run'] = idx
            idx += 1
            kf = (r['tool'], r['tool_id_full'])
            kb = (r['tool'], r['tool_id_base'])
            r['prior_same_tool_calls'] = seen_full[kf]
            r['prior_same_tool_calls_base'] = seen_base[kb]
            seen_full[kf] += 1
            seen_base[kb] += 1
        else:
            r['call_index_in_run'] = None
            r['prior_same_tool_calls'] = None
            r['prior_same_tool_calls_base'] = None


def process(run):
    p = run['trace']
    meta = {k: run[k] for k in ('benchmark', 'task', 'run_id', 'model', 'replicate')}
    fmt = 'claude_code' if 'claude' in os.path.basename(p) else 'codex'
    try:
        if fmt == 'codex':
            rows, salv, diag, sig_ids, run_sig = parse_codex(p)
        else:
            rows, salv, diag, sig_ids, run_sig = parse_claude(p)
    except Exception as ex:  # unreadable trace
        return dict(meta=meta, fmt=fmt, error=repr(ex), rows=[], salvaged=[], diag={})
    finalize(rows, sig_ids, run_sig)
    for r in salv:
        r.pop('_ids', None)
        r.update(outage_sig_linked=None, run_outage_sig=run_sig, call_index_in_run=None,
                 prior_same_tool_calls=None, prior_same_tool_calls_base=None)
    for r in rows + salv:
        r.update(meta)
        r['trace_format'] = fmt
    return dict(meta=meta, fmt=fmt, error=None, rows=rows, salvaged=salv, diag=dict(diag),
                n_mcp=len(rows), n_fail=sum(r['extract_fail'] for r in rows),
                expected_n_mcp=run.get('n_mcp'), expected_n_fail=run.get('n_mcp_fail'), run_sig=run_sig)


COLUMNS = ['benchmark', 'task', 'run_id', 'model', 'replicate', 'trace_format', 'line', 'result_line', 'server', 'tool',
           'galaxy_namespace', 'galaxy_server', 'call_index_in_run', 'prior_same_tool_calls',
           'prior_same_tool_calls_base', 'call_status', 'client_rejected', 'result_status', 'submitted',
           'validation_status', 'prov_status', 'prov_stage', 'checked_parameter_count', 'n_mismatches',
           'n_substituted', 'n_missing_paths', 'mismatch_paths', 'dataset_prov_status', 'tool_id_base',
           'tool_id_full', 'tool_version', 'udt', 'n_jobs', 'job_ids', 'job_states', 'any_job_error',
           'job_failure_phases', 'job_exit_codes', 'has_error_text', 'error_excerpt', 'outage_sig_in_result',
           'outage_sig_linked', 'run_outage_sig', 'chars_returned', 'elapsed_seconds', 'extract_class',
           'extract_fail']
INT_COLS = ['line', 'result_line', 'call_index_in_run', 'prior_same_tool_calls', 'prior_same_tool_calls_base',
            'checked_parameter_count', 'n_mismatches', 'n_substituted', 'n_missing_paths', 'n_jobs', 'chars_returned',
            'replicate']


def main():
    runs_all = [json.loads(l) for l in gzip.open(RUN_SUMMARIES, 'rt')]
    galaxy = [r for r in runs_all if r['condition'] == 'galaxy']
    with_trace = [r for r in galaxy if r.get('trace')]
    no_trace = [r for r in galaxy if not r.get('trace')]
    results = []
    with Pool(10) as pool:
        for res in pool.imap_unordered(process, with_trace, chunksize=4):
            results.append(res)
    results.sort(key=lambda x: (x['meta']['benchmark'], x['meta']['task'], x['meta']['run_id']))
    rows = [r for res in results for r in res['rows']]
    salv = [r for res in results for r in res['salvaged']]
    def typed(frame):
        for c in INT_COLS:
            frame[c] = frame[c].astype('Int64')
        frame['submitted'] = frame['submitted'].astype('boolean')
        frame['outage_sig_linked'] = frame['outage_sig_linked'].astype('boolean')
        return frame

    df = typed(pd.DataFrame(rows, columns=COLUMNS))
    df.to_csv(f'{OUT}/calls.csv.gz', index=False, compression='gzip')
    typed(pd.DataFrame(salv, columns=COLUMNS)).to_csv(f'{OUT}/salvaged_calls.csv.gz', index=False, compression='gzip')
    # per-run reconciliation side file
    rec = []
    for res in results:
        m = res['meta']
        rec.append(dict(**m, trace_format=res['fmt'], parse_error=res['error'], n_mcp=res.get('n_mcp'),
                        expected_n_mcp=res.get('expected_n_mcp'), n_extract_fail=res.get('n_fail'),
                        expected_n_mcp_fail=res.get('expected_n_fail'), n_salvaged=len(res['salvaged']),
                        run_outage_sig=res.get('run_sig'), **{f'diag_{k}': v for k, v in res['diag'].items()}))
    pd.DataFrame(rec).to_csv(f'{OUT}/run_coverage.csv', index=False)
    json.dump(dict(no_trace=[{k: r[k] for k in ('benchmark', 'task', 'run_id', 'model', 'replicate')} for r in no_trace],
                   n_galaxy_runs=len(galaxy), n_with_trace=len(with_trace)),
              open(f'{OUT}/_coverage_meta.json', 'w'), indent=1)
    print('rows', len(df), 'salvaged', len(salv), 'runs', len(results),
          'parse errors', sum(1 for r in results if r['error']))


if __name__ == '__main__':
    main()
