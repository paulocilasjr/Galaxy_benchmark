"""Runs the results site replaced after the archive's derived tables were built, and how the figures take them.

IWC wf_007 (VGP mitogenome assembly): on 2026-10-12 the site replaced all 24 runs with new runs on read set ERR12833637
(IWC/replacement_wf007_20261012/: runs.csv, written by build_record.py from the lab repository's commit ff9c4f5). The
archive holds the traces of the superseded runs only. The figures therefore take:
- scores and token counts: the new runs' (scored_runs.csv carries the new scores; replace_tokens() the new usage);
- everything derived from a trace (tool calls, Galaxy jobs, execution errors, actions, answers, UDT definitions, run
  evidence): unavailable for the new runs. drop_replaced() removes the superseded runs' rows from those tables, so they
  are not attributed to the runs that replaced them; the task's runs then count as runs without a trace.
"""
import os

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
RECORD = os.path.join(ROOT, 'IWC', 'replacement_wf007_20261012', 'runs.csv')
REPLACED_TASKS = {'wf_007_vgp_mitogenome_assembly'}                 # IWC; every run of the task was replaced
IWC_LABELS = {'IWC', 'iwc'}
# trace-derived columns of the archive's per-run token table (token_run_observations.csv)
TRACE_COLUMNS = ['n_mcp', 'n_mcp_fail', 'n_shell', 'n_shell_nonzero', 'n_web', 'disc_calls', 'insp_calls', 'exe_calls',
                 'other_calls', 'disc_chars', 'insp_chars', 'exe_chars', 'other_chars', 'shell_chars', 'udt_calls']


def record():
    return pd.read_csv(RECORD)


def is_replaced(benchmark, task):
    """Boolean mask: rows of a replaced task (benchmark labels differ between tables; the task name identifies it)."""
    b = pd.Series(benchmark).astype(str).str.lower().str.startswith('iwc').values
    return b & pd.Series(task).isin(REPLACED_TASKS).values


def drop_replaced(df, benchmark='benchmark', task='task'):
    """A trace-derived table without the superseded runs' rows."""
    return df[~is_replaced(df[benchmark], df[task])]


def replace_tokens(t):
    """The archive's per-run token table with the replaced runs' usage taken from the replacement record.

    Input, cached input and output tokens are the new runs'; trace-derived counts are emptied (no trace in the archive)."""
    t = t.copy()
    rec = record().set_index(['task', 'cfg', 'env', 'replicate'])
    m = is_replaced(t.benchmark, t.task) & t.model_primary.astype(bool).values
    idx = pd.MultiIndex.from_frame(t.loc[m, ['task', 'cfg', 'env', 'replicate']])
    assert idx.isin(rec.index).all() and len(idx) == len(rec), 'every replaced run needs one record row'
    new = rec.reindex(idx)
    t.loc[m, 'input_tokens'] = new.input_tokens.values
    t.loc[m, 'cached'] = new.cached_input_tokens.values
    t.loc[m, 'output_tokens'] = new.output_tokens.values
    if 'uncached_input_tokens' in t:
        t.loc[m, 'uncached_input_tokens'] = (new.input_tokens - new.cached_input_tokens).values
    if 'endpoint_score' in t:
        t.loc[m, 'endpoint_score'] = new.score.values
    if 'has_trace' in t:
        t.loc[m, 'has_trace'] = False
    for c in TRACE_COLUMNS:
        if c in t:
            t.loc[m, c] = np.nan
    return t


def replaced_evidence(path):
    """True for the run-evidence file of a replaced task (it describes the superseded runs)."""
    parts = os.path.normpath(path).split(os.sep)
    return 'IWC' in parts and any(t in parts for t in REPLACED_TASKS)


def superseded_inspection():
    """Distinct tools inspected, and of those never run, summed over the superseded Galaxy runs, counted as
    manuscript_material/scripts/build_data.py counts them for the archive's 'Inspected tools never run in the same run'
    measure (token_interface_friction.csv): the replaced task's share, to be taken out of the IWC count."""
    import gzip
    import json
    inspected = never = 0
    path = os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz')
    for raw in gzip.open(path, 'rt'):
        s = json.loads(raw)
        if s['benchmark'] != 'IWC' or s['task'] not in REPLACED_TASKS or s['condition'] != 'galaxy' \
                or not s.get('trace') or 'claude' in s['trace']:
            continue
        seen, ran = set(), set()
        op = gzip.open if s['trace'].endswith('.gz') else open
        for line in op(s['trace'], 'rt', errors='replace'):
            if '"item.completed"' not in line:
                continue
            try:
                it = json.loads(line)['item']
            except Exception:
                continue
            if it.get('type') != 'mcp_tool_call':
                continue
            tool, args = it.get('tool') or '', it.get('arguments') or {}
            if tool == 'inspect_galaxy_tool' and args.get('tool_id'):
                seen.add(args['tool_id'])
            elif tool == 'run_galaxy_tool_and_wait' and args.get('tool_id'):
                ran.add(args['tool_id'])
        inspected += len(seen)
        never += len(seen - ran)
    return dict(inspected=inspected, never_run=never)
