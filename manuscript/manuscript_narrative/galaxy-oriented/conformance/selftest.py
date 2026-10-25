"""Self-test of the conformance suite: reference responses must pass, and every injected defect must be detected.

    python selftest.py            # writes selftest_report.json; exits non-zero if any expectation fails

Reference ("golden") observations are the reference responses stored in fixtures.json, with <input:NAME> replaced by
the fixture input hashes. Each mutation below simulates an adapter defect named in Supplementary Note 1 (removed
parameter checks, truncated receipts, permitted cross-account reads, and so on) by editing the golden observations.
The suite is valid for interpreting intervention results only if the golden set passes and each mutation makes at
least one fixture of each targeted requirement fail. This tests the fixtures and scorer, not any deployment.
"""
import copy
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import score as S  # noqa: E402


def golden(doc):
    out = []
    for f in doc['fixtures']:
        resp = json.loads(re.sub(r'<input:([^>]+)>', lambda m: f['input_hashes'].get(m.group(1), m.group(0)), json.dumps(f['reference'])))
        out.append({'fixture_id': f['id'], 'deployment': 'reference', 'adapter_version': 'reference', 'response': resp})
    return out


def _op(doc, fid):
    return next(f for f in doc['fixtures'] if f['id'] == fid)['request']['operation']


def m_no_parameter_check(obs, doc):
    for o in obs:
        if _op(doc, o['fixture_id']) not in ('run_tool', 'raw_api_submission'):
            continue
        r = o['response']
        if r.get('outcome') == 'rejected':
            r.update(outcome='accepted', job_created=True, phase='completed', resolved_state={'operation|selector': 'total_tree_length'},
                     diagnostics={'availability': 'none', 'message': ''})
        r['comparison'] = {'status': 'matched', 'compared_paths': [], 'unsupported_paths': []}
    return obs


def m_truncate_receipts(obs, doc):
    for o in obs:
        rc = o['response'].get('receipt')
        if rc:
            for k in ('output_hashes', 'input_hashes', 'execution_location', 'checked_by_interface'):
                rc.pop(k, None)
    return obs


def m_cross_account_read(obs, doc):
    for o in obs:
        if o['fixture_id'] == 'R6-04':
            o['response'].update(outcome='accepted', audit_logged=False, phase='completed')
    return obs


def m_strip_diagnostics(obs, doc):
    for o in obs:
        d = o['response'].get('diagnostics')
        if d:
            d.update(availability='none', message='', exit_code=None)
    return obs


def m_hide_versions(obs, doc):
    for o in obs:
        r = o['response']
        if 'metadata' in r:
            r['metadata']['underlying_software'] = []
            for out in r['metadata'].get('outputs', []):
                out['description'] = ''
        for x in r.get('results', []):
            x.pop('underlying_version', None)
    return obs


def m_bloat_discovery(obs, doc):
    for o in obs:
        r = o['response']
        if _op(doc, o['fixture_id']) in ('search_tools', 'inspect_tool'):
            r['response_bytes'] = 200000
            if 'results' in r:
                r['results'] = [{'tool_id': f'filler_{i}', 'help': 'x' * 2000, 'underlying_version': '1'} for i in range(25)] + r['results']
    return obs


def m_refuse_everything(obs, doc):
    for o in obs:
        o['response'].update(outcome='rejected', job_created=False, phase='validation')
    return obs


def m_accept_everything(obs, doc):
    for o in obs:
        r = o['response']
        if r.get('outcome') == 'rejected':
            r.update(outcome='accepted', job_created=True, phase='completed', audit_logged=False)
    return obs


def m_mislabel_location(obs, doc):
    for o in obs:
        rc = o['response'].get('receipt')
        if rc and 'execution_location' in rc:
            rc['execution_location'] = 'workbench_job'
            rc['checked_by_interface'] = True
    return obs


def m_history_required(obs, doc):
    for o in obs:
        if o['fixture_id'] == 'R4-01':
            o['response'].update(outcome='rejected', phase='validation', schema=None,
                                 diagnostics={'availability': 'structured_reason', 'message': 'History unavailable. Please specify a valid history id'})
    return obs


MUTATIONS = [
    ('remove parameter checks', m_no_parameter_check, ['R1']),
    ('truncate receipts', m_truncate_receipts, ['R6']),
    ('permit cross-account reads', m_cross_account_read, ['R6']),
    ('strip failure diagnostics', m_strip_diagnostics, ['R2']),
    ('hide versions and output semantics', m_hide_versions, ['R3']),
    ('unbounded discovery responses', m_bloat_discovery, ['R4']),
    ('refuse every request', m_refuse_everything, ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']),
    ('accept every request', m_accept_everything, ['R1', 'R6']),
    ('mislabel execution location', m_mislabel_location, ['R6']),
    ('require a history for tool schemas', m_history_required, ['R4']),
]


def main():
    doc = S.load_fixtures()
    gold = golden(doc)
    base = S.score(gold, doc, selftest=True)
    report = {'golden': {k: v for k, v in base.items() if k != 'rows'}, 'golden_failures': [r for r in base['rows'] if r['status'] != 'pass'],
              'mutations': []}
    ok = base['failed'] == 0
    for name, fn, targets in MUTATIONS:
        rep = S.score(fn(copy.deepcopy(gold), doc), doc, selftest=True)
        failed = [r for r in rep['rows'] if r['status'] == 'fail']
        hit = {t: [r['id'] for r in failed if r['requirement'] == t] for t in targets}
        detected = all(hit[t] for t in targets)
        ok &= detected
        report['mutations'].append(dict(mutation=name, targets=targets, detected=detected, failing_fixtures=hit,
                                        completion_rate_positive_controls=rep['completion_rate_positive_controls'],
                                        refusal_or_exact_echo_rate_negative_controls=rep['refusal_or_exact_echo_rate_negative_controls']))
    report['passed'] = bool(ok)
    json.dump(report, open(HERE / 'selftest_report.json', 'w'), indent=1)
    print(f"golden: {base['passed']}/{base['fixtures']} pass")
    for m in report['mutations']:
        print(f"{'detected' if m['detected'] else 'MISSED  '}  {m['mutation']}: " +
              ', '.join(f'{t}:{len(v)}' for t, v in m['failing_fixtures'].items()))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
