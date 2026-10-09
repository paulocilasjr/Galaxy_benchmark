"""Where a run's input tokens go: an estimate by phase, from the sequence of calls in its agent trace.

The traces record one token total per run (the final `turn.completed` event), not the tokens of each model request.
The split by phase is therefore estimated from how an agent loop consumes input:
- every model request re-reads the whole conversation so far, so request k costs
  (fixed overhead: system prompt, task, tool definitions) + (everything returned and said before k);
- one request is counted per tool call (shell command, Galaxy interface call, web search, file edit), plus the final
  answer; agent messages and reasoning are emitted inside those requests and only add to the conversation.
The estimated input of a run is the sum over its requests; it is fitted to the recorded totals (overhead per request
and tokens per character, by condition) and each run's phase estimates are then scaled to its recorded input tokens.

Phases, assigned to each request by the state of the run when it is made:
- start-up: before the first analysis step (reading the task and inputs, finding tools, planning);
- analysis: between the first and the last successful analysis step, when no failure is pending;
- error correction: after a failed call (non-zero exit, Galaxy validation or job failure), until the next successful
  analysis step;
- output preparation: after the last successful analysis step (extracting the result, writing and checking the answer).
An analysis step is a Galaxy job submission or wait (run_galaxy_tool_and_wait, run_galaxy_udt_and_wait,
wait_for_galaxy_jobs, or a bioblend run_tool / invoke_workflow call) in Galaxy, and a shell command that runs an analysis
program or script (trajectory_steps.shell_label) with custom code.
"""
import gzip
import json
import os
import re

from trajectory_steps import shell_label

GALAXY_ANALYSIS_TOOLS = {'run_galaxy_tool_and_wait', 'run_galaxy_udt_and_wait', 'wait_for_galaxy_jobs'}
GALAXY_SHELL_SUBMIT = re.compile(r'run_tool\(|invoke_workflow\(')
MCP_FAILED = re.compile(r'validation_failed|submitted\\*"?\s*:\s*false|failure_summary\\*"\s*:\s*\\*"|'
                        r'state\\*"\s*:\s*\\*"error')
ITEM_CAP = 40_000               # characters of one item that reach the model (tool output is truncated in the loop)
PHASES = ['start-up', 'analysis', 'error correction', 'output preparation']


def trace_path(base):
    for d, _, fs in os.walk(base):
        for f in sorted(fs):
            if f.startswith('codex_events.jsonl'):
                return os.path.join(d, f)
    return None


def item_chars(it):
    t = it.get('type')
    if t == 'command_execution':
        n = len(str(it.get('command') or '')) + len(str(it.get('aggregated_output') or ''))
    elif t == 'mcp_tool_call':
        n = len(json.dumps(it.get('arguments') or '')) + len(json.dumps(it.get('result') or ''))
    elif t in ('agent_message', 'reasoning'):
        n = len(it.get('text') or '')
    else:
        n = len(json.dumps(it))
    return min(n, ITEM_CAP)


def failed(it):
    t = it.get('type')
    if it.get('status') == 'failed' or it.get('error'):
        return True
    if t == 'command_execution':
        return it.get('exit_code') not in (0, None)
    if t == 'mcp_tool_call':
        return bool(MCP_FAILED.search(json.dumps(it.get('result') or '')[:200_000]))
    return False


def is_analysis(it, env):
    t = it.get('type')
    if env == 'galaxy':
        if t == 'mcp_tool_call':
            return (it.get('tool') or '').split('.')[-1] in GALAXY_ANALYSIS_TOOLS
        if t == 'command_execution':
            return bool(GALAXY_SHELL_SUBMIT.search(str(it.get('command') or '')))
        return False
    return t == 'command_execution' and shell_label(it.get('command') or '') is not None


def requests(path, env):
    """The run's model requests: (characters of conversation before the request, phase), in order."""
    items = []
    opener = gzip.open if path.endswith('.gz') else open
    with opener(path, 'rt', errors='replace') as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get('type') != 'item.completed':
                continue
            it = e.get('item') or {}
            if it.get('type') in (None, 'todo_list', 'error'):
                continue
            items.append(it)
    calls = [i for i, it in enumerate(items) if it.get('type') in
             ('command_execution', 'mcp_tool_call', 'web_search', 'file_change')]
    ana = [i for i in calls if is_analysis(items[i], env)]
    ana_ok = [i for i in ana if not failed(items[i])]
    first = ana[0] if ana else None
    last_ok = ana_ok[-1] if ana_ok else None
    out, chars, pending = [], 0, False
    req_at = calls + [len(items)]                              # the final answer is the last request
    j = 0
    for i in range(len(items) + 1):
        if j < len(req_at) and i == req_at[j]:
            if first is None or i < first:
                phase = 'start-up'
            elif last_ok is not None and i > last_ok:
                phase = 'output preparation'
            elif pending:
                phase = 'error correction'
            else:
                phase = 'analysis'
            out.append((chars, phase))
            j += 1
        if i == len(items):
            break
        it = items[i]
        chars += item_chars(it)
        if i in calls and failed(it):
            pending = True
        elif i in ana_ok:
            pending = False
    return out
