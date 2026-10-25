"""For flagged runs: where the submitted answer appears in the trace, in order, and which kind of action produced it.

Used to classify answer-source exposure: whether the answer was first seen in outside content, and whether the run later
produced it from its own Galaxy or local computation."""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import traces
import scan


def timeline(repo, run_dir, answer):
    num = scan.numeric_forms(answer)
    if not answer or not scan.distinctive(answer, num):
        return []
    out = []
    for p in traces.trace_files(repo, run_dir):
        for a in traces.actions(p):
            if a['kind'] in ('msg', 'reasoning', 'file_change'):
                continue
            if scan.contains_answer(a['out'], answer, num):
                src = scan.source_kind(a)
                if src == 'external':
                    src = 'external:answer_source' if any(rx.search(a['text']) for rx, _, c in scan.SOURCES
                                                          if c in ('answer_key', 'other_agents_answers')) else \
                          'external:benchmark_probe' if any(rx.search(a['text']) for rx, _, c in scan.SOURCES) else \
                          'external:search' if scan.SEARCH_ENGINE.search(a['text']) or a['server'] == 'codex_apps' else 'external:data'
                out.append((a['i'], src, a['text'][:160]))
    return out
