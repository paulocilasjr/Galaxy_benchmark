"""Score recorded adapter responses against the conformance fixtures.

    python score.py observations.jsonl [--freeze freeze_values.json] [--out report.json]

observations.jsonl has one JSON object per line: {"fixture_id": "R1-01", "deployment": "...", "adapter_version": "...",
"response": {...}}. The response fields a driver must record are described in observation.schema.json.

A fixture passes when every check in it holds (an "any_of" check holds when every check in one alternative holds).
Fixtures whose request or checks still contain "<freeze:NAME>" values are reported as unfrozen and not scored unless the
values are supplied with --freeze, or the caller is the self-test. Missing observations count as failures.

The report keeps refusal and completion together: a deployment that rejects every request fails the positive controls,
and one that accepts every request fails the negative controls, so neither can improve apparent fidelity.
"""
import argparse
import copy
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
FREEZE = re.compile(r'<freeze:([A-Za-z0-9_]+)>')
INPUT = re.compile(r'<input:([^>]+)>')
_MISSING = object()


def load_fixtures(path=HERE / 'fixtures.json'):
    return json.load(open(path))


def substitute(obj, freeze):
    s = json.dumps(obj)
    s = FREEZE.sub(lambda m: str(freeze[m.group(1)]) if m.group(1) in freeze else m.group(0), s)
    return json.loads(s)


def unresolved(obj):
    return sorted(set(FREEZE.findall(json.dumps(obj))))


def get(obj, path):
    cur = obj
    for part in path.split('.'):
        if isinstance(cur, dict):
            if part not in cur:
                return _MISSING
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return _MISSING
    return cur


def _nonempty(v):
    return v is not _MISSING and v is not None and v != '' and v != [] and v != {}


def check(c, obs, fx):
    """Return None if the check holds, else a short reason."""
    t = c['type']
    if t == 'any_of':
        reasons = []
        for alt in c['alternatives']:
            r = [x for x in (check(cc, obs, fx) for cc in alt) if x]
            if not r:
                return None
            reasons.append('; '.join(r))
        return 'no alternative held: ' + ' | '.join(reasons)
    v = get(obs, c['path'])
    p = c['path']
    if t == 'equals':
        return None if v == c['value'] else f'{p} is {v if v is not _MISSING else "missing"}, expected {c["value"]!r}'
    if t == 'in':
        return None if v in c['values'] else f'{p} is {v if v is not _MISSING else "missing"}, expected one of {c["values"]}'
    if t == 'nonempty':
        return None if _nonempty(v) else f'{p} is empty or missing'
    if t == 'contains_all':
        have = v if isinstance(v, list) else []
        miss = [x for x in c['values'] if x not in have]
        return None if not miss else f'{p} lacks {miss}'
    if t == 'subset_equal':
        have = v if isinstance(v, dict) else {}
        bad = {k: have.get(k, 'missing') for k, x in c['value'].items() if have.get(k, _MISSING) != x}
        return None if not bad else f'{p} differs at {bad}'
    if t == 'matches':
        return None if isinstance(v, str) and re.search(c['regex'], v) else f'{p} does not match /{c["regex"]}/'
    if t == 'max':
        return None if isinstance(v, (int, float)) and v <= c['value'] else f'{p} is {v if v is not _MISSING else "missing"}, limit {c["value"]}'
    if t == 'max_len':
        return None if isinstance(v, list) and len(v) <= c['value'] else f'{p} has {len(v) if isinstance(v, list) else "no"} items, limit {c["value"]}'
    if t == 'min_len':
        return None if isinstance(v, list) and len(v) >= c['value'] else f'{p} has {len(v) if isinstance(v, list) else "no"} items, need {c["value"]}'
    if t == 'all_have':
        if not isinstance(v, list) or not v:
            return f'{p} is empty or missing'
        bad = [i for i, x in enumerate(v) if not all(_nonempty(x.get(k, _MISSING)) for k in c['keys'])]
        return None if not bad else f'{p} items {bad} lack {c["keys"]}'
    if t == 'contains_item':
        return None if isinstance(v, list) and c['value'] in v else f'{p} lacks {c["value"]}'
    if t == 'max_item_bytes':
        if not isinstance(v, list):
            return f'{p} missing'
        big = [i for i, x in enumerate(v) if len(json.dumps(x).encode()) > c['value']]
        return None if not big else f'{p} items {big} exceed {c["value"]} bytes'
    if t == 'rank_within':
        ids = [x.get(c['key']) for x in v] if isinstance(v, list) else []
        return None if c['value'] in ids[:c['k']] else f'{c["value"]} not in the top {c["k"]} of {p}'
    if t == 'equals_inputs':
        want = fx.get('input_hashes', {})
        have = v if isinstance(v, dict) else {}
        bad = {k: have.get(k, 'missing') for k, h in want.items() if str(have.get(k, '')).removeprefix('sha256:') != h}
        return None if not bad else f'{p} does not attest inputs {sorted(bad)}'
    if t == 'equals_input_hash':
        want = fx.get('input_hashes', {}).get(c['input'])
        return None if isinstance(v, str) and v.removeprefix('sha256:') == want else f'{p} is not the hash of {c["input"]}'
    return f'unknown check type {t}'


def score(observations, fixtures_doc=None, freeze=None, selftest=False):
    doc = fixtures_doc or load_fixtures()
    freeze = freeze or {}
    obs = {}
    for o in observations:
        obs[o['fixture_id']] = o
    rows = []
    for f0 in doc['fixtures']:
        f = substitute(f0, freeze)
        todo = unresolved({'request': f['request'], 'checks': f['checks']})
        if todo and not selftest:
            rows.append(dict(id=f['id'], requirement=f['requirement'], control=f['control'], status='unfrozen', reasons=[f'freeze: {todo}']))
            continue
        o = obs.get(f['id'])
        if o is None:
            rows.append(dict(id=f['id'], requirement=f['requirement'], control=f['control'], status='fail', reasons=['no observation']))
            continue
        reasons = [r for r in (check(c, o, f) for c in f['checks']) if r]
        rows.append(dict(id=f['id'], requirement=f['requirement'], control=f['control'], status='pass' if not reasons else 'fail',
                         reasons=reasons, outcome=get(o, 'response.outcome') if get(o, 'response.outcome') is not _MISSING else None))
    return summarize(rows)


def summarize(rows):
    reqs = {}
    for r in rows:
        q = reqs.setdefault(r['requirement'], dict(pass_=0, fail=0, unfrozen=0))
        q[{'pass': 'pass_', 'fail': 'fail', 'unfrozen': 'unfrozen'}[r['status']]] += 1
    pos = [r for r in rows if r['control'] in ('positive', 'dataset_only', 'unsupported_comparison') and r['status'] != 'unfrozen']
    neg = [r for r in rows if r['control'] == 'negative' and r['status'] != 'unfrozen']
    loc = [r for r in rows if r['control'] == 'known_location' or r['id'] == 'R6-01']
    loc = [r for r in loc if r['status'] != 'unfrozen']
    return dict(
        fixtures=len(rows), passed=sum(r['status'] == 'pass' for r in rows), failed=sum(r['status'] == 'fail' for r in rows),
        unfrozen=sum(r['status'] == 'unfrozen' for r in rows),
        by_requirement={k: {'pass': v['pass_'], 'fail': v['fail'], 'unfrozen': v['unfrozen']} for k, v in sorted(reqs.items())},
        completion_rate_positive_controls=(sum(r['status'] == 'pass' for r in pos) / len(pos)) if pos else None,
        refusal_or_exact_echo_rate_negative_controls=(sum(r['status'] == 'pass' for r in neg) / len(neg)) if neg else None,
        location_attestation_correct=(sum(r['status'] == 'pass' for r in loc) / len(loc)) if loc else None,
        rows=rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('observations')
    ap.add_argument('--freeze')
    ap.add_argument('--out')
    a = ap.parse_args()
    observations = [json.loads(line) for line in open(a.observations) if line.strip()]
    rep = score(observations, freeze=json.load(open(a.freeze)) if a.freeze else None)
    text = json.dumps(rep, indent=1)
    if a.out:
        Path(a.out).write_text(text)
    print(json.dumps({k: v for k, v in rep.items() if k != 'rows'}, indent=1))


if __name__ == '__main__':
    main()
