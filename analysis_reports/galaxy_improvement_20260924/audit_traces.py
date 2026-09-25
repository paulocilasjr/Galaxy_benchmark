"""Parse archived traces as data only; save provenance for every rejected/zero run."""
import collections
import gzip
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]


def scrub(s):
    s = re.sub(r'(?i)(authorization["\s:=]+(?:bearer\s+)?)[A-Za-z0-9_.-]{20,}', r'\1[REDACTED]', s)
    s = re.sub(r'(?i)((?:api[_-]?key|x-api-key)["\s:=]+)[A-Za-z0-9_.-]{20,}', r'\1[REDACTED]', s)
    return s


def main():
    runs = json.loads((HERE / 'run_index.json').read_text())
    summaries = []
    packets = []
    cache = {}
    for r in runs:
        trace_summaries = []
        for name in r['trace_paths']:
            p = BASE / name
            types = collections.Counter()
            malformed = []
            lines = 0
            op = gzip.open if p.suffix == '.gz' else open
            with op(p, 'rt', errors='replace') as f:
                for lines, line in enumerate(f, 1):
                    try:
                        obj = json.loads(line, strict=False)
                    except json.JSONDecodeError:
                        malformed.append(lines)
                        continue
                    types[obj.get('type', 'unknown')] += 1
            trace_summaries.append({'path': name, 'lines': lines, 'types': dict(types), 'malformed_lines': malformed})
        summaries.append({'benchmark': r['benchmark'], 'task': r['task'], 'run_id': r['run_id'], 'traces': trace_summaries})
        if r['outcome_label'] not in ('rejected', 'zero_agreement'):
            continue
        ep = r['evidence_path']
        if ep not in cache:
            cache[ep] = json.loads((BASE / ep).read_text())
        full = next(x for x in cache[ep]['runs'] if x['run_id'] == r['run_id'])
        trace_events = [e for e in full['events'] if e.get('source_line') is not None]
        trace_events.sort(key=lambda e: e['source_line'])
        # Preserve the complete normalized call sequence for individual inspection.
        fields = ['event_id', 'source_line', 'timestamp', 'event_type', 'execution_location', 'tool',
                  'command', 'parameters', 'status', 'exit_code', 'stdout_excerpt', 'stderr_excerpt', 'evidence_refs']
        calls = [{k: e.get(k) for k in fields} for e in trace_events]
        packet = {k: r[k] for k in ['benchmark', 'task', 'run_id', 'condition', 'model', 'replicate',
                                     'score', 'outcome_label', 'answer', 'evidence_path', 'trace_paths', 'evaluator_paths']}
        packet['calls'] = calls
        packet['outcome_record'] = full['outcome']
        packet['warning'] = 'Normalized excerpts can be truncated; open the cited raw trace for complete results. A successful call is not proof of answer correctness.'
        packets.append(json.loads(scrub(json.dumps(packet))))
    (HERE / 'trace_inventory.json').write_text(json.dumps(summaries, indent=2) + '\n')
    (HERE / 'failure_evidence.json').write_text(json.dumps(packets, indent=2) + '\n')
    stats = {'run_records': len(runs), 'runs_with_primary_trace': sum(bool(s['traces']) for s in summaries),
             'traces': sum(len(s['traces']) for s in summaries),
             'lines_read': sum(t['lines'] for s in summaries for t in s['traces']),
             'malformed_lines': sum(len(t['malformed_lines']) for s in summaries for t in s['traces']),
             'failure_packets': len(packets), 'normalized_failure_calls': sum(len(p['calls']) for p in packets)}
    (HERE / 'trace_coverage.json').write_text(json.dumps(stats, indent=2) + '\n')
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
