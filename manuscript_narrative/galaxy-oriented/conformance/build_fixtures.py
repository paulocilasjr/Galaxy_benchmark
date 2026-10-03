"""Build the conformance fixtures for Supplementary Note 1, section 3 (Galaxy-oriented manuscript).

Run from the repository root:
    python manuscript_narrative/galaxy-oriented/conformance/build_fixtures.py

Writes inputs/ (small synthetic input files with fixed bytes), fixtures.json and archive_basis_check.json. Every fixture
states its requirement (R1-R6), category, control type, the request, its input hashes, machine-checkable expectations
and one reference response that satisfies them (used by selftest.py). Fixtures marked with an archive basis reproduce a
request shape observed in the archived runs; the builder checks that the cited job-ledger event contains that shape.

Values written as "<freeze:NAME>" must be filled in when the study's tool catalogue is frozen (registration); score.py
refuses to score a fixture with an unresolved freeze value outside self-test mode. Nothing here contacts a server.
"""
import gzip
import hashlib
import io
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
INPUTS = HERE / 'inputs'
PHYKIT = 'toolshed.g2.bx.psu.edu/repos/goeckslab/phykit_metrics/phykit_metrics/0.2.0+galaxy0'
LEDGER = 'BixBench_50/analysis/bix-35-q1/job_ledgers/galaxy/{}.json'
DISCOVERY_LIMIT = 16384
CARD_LIMIT = 1024


# ---------------------------------------------------------------------------------------------------- inputs
def _zip(members):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in members:
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    return buf.getvalue()


def _gz(data):
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', mtime=0) as g:
        g.write(data)
    return buf.getvalue()


TREE_A = b'((A:0.1,B:0.2):0.05,(C:0.3,D:0.4):0.06);\n'
TREE_B = b'((A:0.2,C:0.1):0.07,(B:0.25,D:0.35):0.02);\n'
FASTQ = b'@r1\nACGTACGTAC\n+\nIIIIIIIIII\n@r2\nTTGCATGCAA\n+\nIIIIIIIIII\n'
INPUT_FILES = {
    'single.treefile': TREE_A,
    'trees.zip': _zip([('156083at2759.faa.mafft.clipkit.treefile', TREE_A), ('200000at2759.faa.mafft.clipkit.treefile', TREE_B)]),
    'values_a.tsv': b'value\n1.2\n3.4\n2.2\n5.1\n',
    'values_b.tsv': b'value\n0.4\n0.9\n1.1\n0.7\n',
    'reads.fastq.gz': _gz(FASTQ),
    'corrupt.fastq.gz': b'\x1f\x8b\x08\x00not-a-valid-gzip-stream\n',
    'table.xlsx.txt': b'placeholder: replaced by a real one-sheet .xlsx at registration\n',
}


def write_inputs():
    INPUTS.mkdir(exist_ok=True)
    hashes = {}
    for name, data in INPUT_FILES.items():
        (INPUTS / name).write_bytes(data)
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


# ---------------------------------------------------------------------------------------------------- helpers
def ds(name):
    return {'src': 'fixture_input', 'name': name}


def chk(kind, path=None, **kw):
    return dict(type=kind, path=path, **kw)


ACCEPTED_JOB = [chk('equals', 'response.outcome', value='accepted'), chk('equals', 'response.job_created', value=True)]
REJECTED_EARLY = [chk('equals', 'response.outcome', value='rejected'), chk('equals', 'response.job_created', value=False),
                  chk('in', 'response.phase', values=['validation', 'pre_dispatch'])]


def receipt(inputs, location='workbench_job', checked=True):
    return {'run_id': 'run-0001', 'account': 'fixture-account-1', 'job_ids': ['job-1'], 'execution_location': location,
            'checked_by_interface': checked, 'input_hashes': {k: f'<input:{k}>' for k in inputs},
            'output_hashes': {'output1': 'sha256:<observed>'}}


RECEIPT_CHECKS = [chk('nonempty', 'response.receipt.run_id'), chk('nonempty', 'response.receipt.account'),
                  chk('nonempty', 'response.receipt.job_ids'), chk('nonempty', 'response.receipt.output_hashes'),
                  chk('equals_inputs', 'response.receipt.input_hashes')]


def basis(run_id, contains, observed):
    return {'ledger': LEDGER.format(run_id), 'run_id': run_id, 'event_tool': 'run_galaxy_tool_and_wait',
            'request_contains': contains, 'archived_outcome': observed}


# ---------------------------------------------------------------------------------------------------- fixtures
def fixtures():
    F = []

    def add(**f):
        f.setdefault('inputs', [])
        f.setdefault('archive_basis', None)
        f.setdefault('freeze', [])
        F.append(f)

    # ---------------- R1 binding
    nested_single = {'operation': {'selector': 'evolutionary_rate', 'input_mode': {'selector': 'single', 'input': ds('single.treefile')}}}
    add(id='R1-01', requirement='R1', category='binding', control='positive',
        description='Nested request for a conditional branch by name binds, runs and is compared.',
        request={'operation': 'run_tool', 'tool_id': PHYKIT, 'input_format': '21.01', 'inputs': nested_single}, inputs=['single.treefile'],
        archive_basis=basis('galaxy_codex_gpt_5_5_r2', ['"selector": "evolutionary_rate"', '"selector": "single"'],
                            'validation_parameter_mismatch on a first call, then ok and matched'),
        checks=ACCEPTED_JOB + [chk('subset_equal', 'response.resolved_state', value={'operation|selector': 'evolutionary_rate',
                                                                                      'operation|input_mode|selector': 'single'}),
                               chk('equals', 'response.comparison.status', value='matched'),
                               chk('contains_all', 'response.comparison.compared_paths', values=['operation|selector', 'operation|input_mode|selector'])],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed',
                   'resolved_state': {'operation|selector': 'evolutionary_rate', 'operation|input_mode|selector': 'single'},
                   'comparison': {'status': 'matched', 'compared_paths': ['operation|selector', 'operation|input_mode|selector'], 'unsupported_paths': []},
                   'receipt': receipt(['single.treefile'])})
    nested_zip = {'operation': {'selector': 'evolutionary_rate', 'input_mode': {'selector': 'zip_archive', 'archive': ds('trees.zip'),
                                                                               'archive_label': 'animals', 'filter_suffix': '.treefile',
                                                                               'filter_regex': '^156083at2759'}}}
    add(id='R1-02', requirement='R1', category='binding', control='positive',
        description='Nested zip-archive branch with label and filters binds; every non-dataset value is compared.',
        request={'operation': 'run_tool', 'tool_id': PHYKIT, 'input_format': '21.01', 'inputs': nested_zip}, inputs=['trees.zip'],
        archive_basis=basis('galaxy_codex_gpt_5_5_r1', ['"selector": "zip_archive"', '"archive_label": "animals"', '"filter_regex": "^156083at2759"'],
                            'validation_parameter_mismatch on a first call, then ok and matched'),
        checks=ACCEPTED_JOB + [chk('subset_equal', 'response.resolved_state', value={
            'operation|selector': 'evolutionary_rate', 'operation|input_mode|selector': 'zip_archive',
            'operation|input_mode|archive_label': 'animals', 'operation|input_mode|filter_suffix': '.treefile',
            'operation|input_mode|filter_regex': '^156083at2759'}),
            chk('equals', 'response.comparison.status', value='matched'),
            chk('contains_all', 'response.comparison.compared_paths', values=[
                'operation|selector', 'operation|input_mode|selector', 'operation|input_mode|archive_label',
                'operation|input_mode|filter_suffix', 'operation|input_mode|filter_regex'])],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed',
                   'resolved_state': {'operation|selector': 'evolutionary_rate', 'operation|input_mode|selector': 'zip_archive',
                                      'operation|input_mode|archive_label': 'animals', 'operation|input_mode|filter_suffix': '.treefile',
                                      'operation|input_mode|filter_regex': '^156083at2759'},
                   'comparison': {'status': 'matched', 'compared_paths': ['operation|selector', 'operation|input_mode|selector',
                                                                           'operation|input_mode|archive_label', 'operation|input_mode|filter_suffix',
                                                                           'operation|input_mode|filter_regex'], 'unsupported_paths': []},
                   'receipt': receipt(['trees.zip'])})
    flat = {'operation|selector': 'evolutionary_rate', 'operation|input_mode|selector': 'zip_archive', 'operation|input_mode|archive': ds('trees.zip'),
            'operation|input_mode|archive_label': 'animals'}
    add(id='R1-03', requirement='R1', category='binding', control='negative',
        description='Flat pipe-separated keys in the nested input format: reject, or run and echo every requested value exactly.',
        request={'operation': 'run_tool', 'tool_id': PHYKIT, 'input_format': '21.01', 'inputs': flat}, inputs=['trees.zip'],
        archive_basis=basis('galaxy_codex_gpt_5_6_luna_r3', ['"operation|selector": "evolutionary_rate"', '"operation|input_mode|selector": "zip_archive"'],
                            'flat keys submitted in the nested format'),
        checks=[chk('any_of', alternatives=[
            REJECTED_EARLY + [chk('contains_all', 'response.diagnostics.unbound_keys', values=['operation|selector'])],
            ACCEPTED_JOB + [chk('subset_equal', 'response.resolved_state', value={'operation|selector': 'evolutionary_rate',
                                                                                   'operation|input_mode|selector': 'zip_archive',
                                                                                   'operation|input_mode|archive_label': 'animals'}),
                            chk('equals', 'response.comparison.status', value='matched')]])],
        reference={'outcome': 'rejected', 'job_created': False, 'phase': 'validation',
                   'diagnostics': {'availability': 'structured_reason', 'message': 'keys do not bind in input format 21.01',
                                   'unbound_keys': ['operation|selector', 'operation|input_mode|selector', 'operation|input_mode|archive',
                                                    'operation|input_mode|archive_label']}})
    bare = {'operation': {'selector': 'evolutionary_rate', 'input_mode': {'selector': 'zip_archive', 'archive': 'fixture-dataset-id-as-bare-string',
                                                                         'filter_suffix': '.treefile', 'filter_regex': '156083at2759'}}}
    add(id='R1-04', requirement='R1', category='binding', control='negative',
        description='Dataset given as a bare identifier string: must be rejected; running the default branch and metric is a failure.',
        request={'operation': 'run_tool', 'tool_id': PHYKIT, 'input_format': '21.01', 'inputs': bare},
        archive_basis=basis('galaxy_deepseek_v4_pro_via_claude_code_superseded_r2', ['"archive": "', '"filter_suffix": ".treefile"'],
                            'resolved operation|selector total_tree_length and input_mode single; mismatch reported after the job'),
        checks=REJECTED_EARLY + [chk('nonempty', 'response.diagnostics.message')],
        reference={'outcome': 'rejected', 'job_created': False, 'phase': 'validation',
                   'diagnostics': {'availability': 'structured_reason', 'message': 'operation|input_mode|archive must be a dataset reference',
                                   'unbound_keys': ['operation|input_mode|archive']}})
    index_only = {'operation': {'__current_case__': 0, 'input_mode': {'__current_case__': 0, 'input': ds('single.treefile')}}}
    add(id='R1-05', requirement='R1', category='binding', control='negative',
        description='Conditional addressed only by case index (the bix-35-q1 loophole): reject, or return and compare the resolved branch.',
        request={'operation': 'run_tool', 'tool_id': PHYKIT, 'input_format': '21.01', 'inputs': index_only}, inputs=['single.treefile'],
        archive_basis=basis('galaxy_deepseek_v4_pro_via_claude_code_superseded_r1', ['"__current_case__": 0', '"input_mode": {"__current_case__": 0'],
                            'job ok; checked_parameter_count 0; status no_explicit_non_dataset_parameters; default metric ran'),
        checks=[chk('any_of', alternatives=[
            REJECTED_EARLY + [chk('nonempty', 'response.diagnostics.message')],
            ACCEPTED_JOB + [chk('nonempty', 'response.resolved_state.operation|selector'),
                            chk('contains_all', 'response.comparison.compared_paths', values=['operation|selector'])]])],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed',
                   'resolved_state': {'operation|selector': 'total_tree_length', 'operation|input_mode|selector': 'single'},
                   'comparison': {'status': 'matched', 'compared_paths': ['operation|selector', 'operation|input_mode|selector'],
                                  'unsupported_paths': [], 'note': 'branch selected by index; resolved names returned'},
                   'receipt': receipt(['single.treefile'])})
    add(id='R1-06', requirement='R1', category='binding', control='negative',
        description='Unknown parameter name: reject and name the key.',
        request={'operation': 'run_tool', 'tool_id': PHYKIT, 'input_format': '21.01',
                 'inputs': {'operation': {'selector': 'evolutionary_rate', 'metric': 'evolutionary_rate',
                                          'input_mode': {'selector': 'single', 'input': ds('single.treefile')}}}}, inputs=['single.treefile'],
        checks=REJECTED_EARLY + [chk('contains_all', 'response.diagnostics.unbound_keys', values=['operation|metric'])],
        reference={'outcome': 'rejected', 'job_created': False, 'phase': 'validation',
                   'diagnostics': {'availability': 'structured_reason', 'message': 'unknown key', 'unbound_keys': ['operation|metric']}})
    add(id='R1-07', requirement='R1', category='binding', control='negative',
        description='Invalid option value for a select: reject and list the allowed values.',
        request={'operation': 'run_tool', 'tool_id': PHYKIT, 'input_format': '21.01',
                 'inputs': {'operation': {'selector': 'evolutionary-rate', 'input_mode': {'selector': 'single', 'input': ds('single.treefile')}}}},
        inputs=['single.treefile'],
        checks=REJECTED_EARLY + [chk('contains_all', 'response.diagnostics.allowed_values', values=['evolutionary_rate'])],
        reference={'outcome': 'rejected', 'job_created': False, 'phase': 'validation',
                   'diagnostics': {'availability': 'structured_reason', 'message': 'invalid option',
                                   'allowed_values': ['total_tree_length', 'evolutionary_rate', 'relative_composition_variability', '<freeze:phykit_metric_options>']}},
        freeze=['phykit_metric_options'])
    add(id='R1-08', requirement='R1', category='binding', control='positive',
        description='Dry run returns the resolved state, including defaults, without creating a job.',
        request={'operation': 'run_tool', 'tool_id': PHYKIT, 'input_format': '21.01', 'dry_run': True, 'inputs': nested_single},
        inputs=['single.treefile'],
        checks=[chk('equals', 'response.outcome', value='accepted'), chk('equals', 'response.job_created', value=False),
                chk('subset_equal', 'response.resolved_state', value={'operation|selector': 'evolutionary_rate', 'operation|input_mode|selector': 'single'}),
                chk('nonempty', 'response.resolved_defaults')],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'dry_run',
                   'resolved_state': {'operation|selector': 'evolutionary_rate', 'operation|input_mode|selector': 'single'},
                   'resolved_defaults': {'<freeze:phykit_default_path>': '<freeze:phykit_default_value>'}},
        freeze=['phykit_default_path', 'phykit_default_value'])
    add(id='R1-09', requirement='R1', category='binding', control='dataset_only',
        description='Tool with dataset inputs only: zero compared parameters is legitimate and must be declared as such.',
        request={'operation': 'run_tool', 'tool_id': 'toolshed.g2.bx.psu.edu/repos/ufz/xlsx2tsv/xlsx2tsv/<freeze:xlsx2tsv_version>',
                 'input_format': '21.01', 'inputs': {'input': ds('table.xlsx.txt')}}, inputs=['table.xlsx.txt'],
        checks=ACCEPTED_JOB + [chk('equals', 'response.comparison.status', value='dataset_only')] + RECEIPT_CHECKS,
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed', 'resolved_state': {},
                   'comparison': {'status': 'dataset_only', 'compared_paths': [], 'unsupported_paths': []}, 'receipt': receipt(['table.xlsx.txt'])},
        freeze=['xlsx2tsv_version'])
    add(id='R1-10', requirement='R1', category='binding', control='unsupported_comparison',
        description='Collection builder whose parameters cannot be compared: status must say unsupported, not matched.',
        request={'operation': 'run_tool', 'tool_id': '__BUILD_LIST__', 'input_format': '21.01',
                 'inputs': {'datasets': [{'input': ds('values_a.tsv'), 'id_cond': {'id_select': 'idx'}}]}}, inputs=['values_a.tsv'],
        checks=ACCEPTED_JOB + [chk('equals', 'response.comparison.status', value='unsupported'), chk('nonempty', 'response.comparison.unsupported_paths')],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed', 'resolved_state': {},
                   'comparison': {'status': 'unsupported', 'compared_paths': [], 'unsupported_paths': ['datasets_0|id_cond']},
                   'receipt': receipt(['values_a.tsv'])})
    add(id='R1-11', requirement='R1', category='binding', control='positive',
        description='Repeat element given as a list of objects binds and every element is compared.',
        request={'operation': 'run_tool', 'tool_id': 'cat1', 'input_format': '21.01',
                 'inputs': {'input1': ds('values_a.tsv'), 'queries': [{'input2': ds('values_b.tsv')}]}}, inputs=['values_a.tsv', 'values_b.tsv'],
        checks=ACCEPTED_JOB + [chk('equals', 'response.comparison.status', value='dataset_only')],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed', 'resolved_state': {'queries_0|input2': 'values_b.tsv'},
                   'comparison': {'status': 'dataset_only', 'compared_paths': [], 'unsupported_paths': []}, 'receipt': receipt(['values_a.tsv', 'values_b.tsv'])})
    add(id='R1-12', requirement='R1', category='binding', control='negative',
        description='Repeat element given as an object instead of a list: reject and name the key.',
        request={'operation': 'run_tool', 'tool_id': 'cat1', 'input_format': '21.01',
                 'inputs': {'input1': ds('values_a.tsv'), 'queries': {'input2': ds('values_b.tsv')}}}, inputs=['values_a.tsv', 'values_b.tsv'],
        checks=REJECTED_EARLY + [chk('contains_all', 'response.diagnostics.unbound_keys', values=['queries'])],
        reference={'outcome': 'rejected', 'job_created': False, 'phase': 'validation',
                   'diagnostics': {'availability': 'structured_reason', 'message': 'repeat must be a list', 'unbound_keys': ['queries']}})

    # ---------------- R2 failure payloads
    def custom(script, image='<freeze:python_image>', mem=None):
        r = {'operation': 'run_custom_tool', 'container': image, 'command': script}
        if mem:
            r['memory_mb'] = mem
        return r
    runtime_ok = ['stderr', 'tool_message', 'structured_reason']
    add(id='R2-01', requirement='R2', category='failure_payload', control='negative',
        description='Non-zero exit: return phase, exit code and the error text.',
        request=custom("echo 'fixture-error-marker' >&2; exit 3"),
        checks=[chk('equals', 'response.job_created', value=True), chk('equals', 'response.phase', value='runtime'),
                chk('equals', 'response.diagnostics.exit_code', value=3), chk('in', 'response.diagnostics.availability', values=runtime_ok),
                chk('matches', 'response.diagnostics.message', regex='fixture-error-marker')],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'runtime', 'job_state': 'error',
                   'diagnostics': {'availability': 'stderr', 'message': 'fixture-error-marker', 'exit_code': 3}},
        freeze=['python_image'])
    add(id='R2-02', requirement='R2', category='failure_payload', control='negative',
        description='Missing dependency inside the container: return the import error.',
        request=custom("python -c 'import fixture_missing_module_xyz'"),
        checks=[chk('equals', 'response.phase', value='runtime'), chk('in', 'response.diagnostics.availability', values=runtime_ok),
                chk('matches', 'response.diagnostics.message', regex='ModuleNotFoundError|No module named')],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'runtime', 'job_state': 'error',
                   'diagnostics': {'availability': 'stderr', 'message': "ModuleNotFoundError: No module named 'fixture_missing_module_xyz'", 'exit_code': 1}},
        freeze=['python_image'])
    add(id='R2-03', requirement='R2', category='failure_payload', control='negative',
        description='Unreadable compressed input: fail with a message that names the format problem.',
        request={'operation': 'run_tool', 'tool_id': '<freeze:fastq_reader_tool_id>', 'input_format': '21.01', 'inputs': {'input': ds('corrupt.fastq.gz')}},
        inputs=['corrupt.fastq.gz'],
        checks=[chk('in', 'response.phase', values=['validation', 'runtime']), chk('in', 'response.diagnostics.availability', values=runtime_ok),
                chk('matches', 'response.diagnostics.message', regex='(?i)gzip|compress|format|magic|invalid')],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'runtime', 'job_state': 'error',
                   'diagnostics': {'availability': 'stderr', 'message': 'gzip: invalid compressed data--format violated', 'exit_code': 1}},
        freeze=['fastq_reader_tool_id'])
    add(id='R2-04', requirement='R2', category='failure_payload', control='negative',
        description='Memory limit exceeded: report a resource failure even when no exit code exists.',
        request=custom("python -c 'x = bytearray(4 * 1024**3)'", mem=256),
        checks=[chk('equals', 'response.phase', value='runtime'), chk('in', 'response.diagnostics.availability', values=runtime_ok),
                chk('matches', 'response.diagnostics.message', regex='(?i)memory|oom|killed|resource')],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'runtime', 'job_state': 'error',
                   'diagnostics': {'availability': 'structured_reason', 'message': 'job exceeded its memory limit (256 MB)', 'exit_code': None}},
        freeze=['python_image'])
    add(id='R2-05', requirement='R2', category='failure_payload', control='negative',
        description='Job never dispatched (unknown container image): no stderr exists, but a structured reason must.',
        request=custom('true', image='fixture.invalid/no-such-image:0'),
        checks=[chk('equals', 'response.phase', value='pre_dispatch'), chk('equals', 'response.diagnostics.availability', value='structured_reason'),
                chk('nonempty', 'response.diagnostics.message')],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'pre_dispatch', 'job_state': 'error',
                   'diagnostics': {'availability': 'structured_reason', 'message': 'container image could not be resolved: fixture.invalid/no-such-image:0',
                                   'exit_code': None}})
    add(id='R2-06', requirement='R2', category='failure_payload', control='positive',
        description='Successful custom job: diagnostics may be empty, and the job must not be reported as failed.',
        request=custom("echo ok"),
        checks=[chk('equals', 'response.outcome', value='accepted'), chk('equals', 'response.job_state', value='ok')] + RECEIPT_CHECKS,
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed', 'job_state': 'ok',
                   'diagnostics': {'availability': 'none', 'message': ''}, 'receipt': receipt([])},
        freeze=['python_image'])

    # ---------------- R3 metadata
    add(id='R3-01', requirement='R3', category='metadata', control='positive',
        description='Inspection returns the underlying software and version the wrapper pins, and output definitions.',
        request={'operation': 'inspect_tool', 'tool_id': PHYKIT},
        checks=[chk('equals', 'response.outcome', value='accepted'),
                chk('contains_item', 'response.metadata.underlying_software', value={'name': 'phykit', 'version': '<freeze:phykit_requirement_version>'}),
                chk('nonempty', 'response.metadata.outputs')],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed',
                   'metadata': {'underlying_software': [{'name': 'phykit', 'version': '<freeze:phykit_requirement_version>'}],
                                'outputs': [{'name': 'output', 'format': 'tabular', 'description': '<freeze:phykit_output_description>'}]}},
        freeze=['phykit_requirement_version', 'phykit_output_description'])
    add(id='R3-02', requirement='R3', category='metadata', control='positive',
        description='Output semantics are declared per output (bix-28-q3: a variance was returned under the metric name).',
        request={'operation': 'inspect_tool', 'tool_id': PHYKIT, 'context': {'operation|selector': 'long_branch_score'}},
        checks=[chk('equals', 'response.outcome', value='accepted'),
                chk('matches', 'response.metadata.outputs.0.description', regex='(?i)per[- ]taxon|summary|variance|statistic')],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed',
                   'metadata': {'underlying_software': [{'name': 'phykit', 'version': '<freeze:phykit_requirement_version>'}],
                                'outputs': [{'name': 'output', 'format': 'tabular',
                                             'description': 'summary statistic of per-taxon long-branch scores; see column header'}]}},
        freeze=['phykit_requirement_version'])
    add(id='R3-03', requirement='R3', category='metadata', control='positive',
        description='Search distinguishes several catalogue versions of one tool (IWC PepQuery case) with their underlying versions.',
        request={'operation': 'search_tools', 'query': 'pepquery'},
        checks=[chk('equals', 'response.outcome', value='accepted'), chk('min_len', 'response.results', value=2),
                chk('all_have', 'response.results', keys=['tool_id', 'underlying_version'])],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed', 'response_bytes': 2048,
                   'results': [{'tool_id': '<freeze:pepquery2_tool_id>', 'underlying_version': '2.0.2'},
                               {'tool_id': '<freeze:pepquery_tool_id>', 'underlying_version': '1.6.2'}]},
        freeze=['pepquery2_tool_id', 'pepquery_tool_id'])

    # ---------------- R4 discovery
    add(id='R4-01', requirement='R4', category='discovery', control='positive',
        description='Tool schema without a history (the missing-history failure class) succeeds within a size limit.',
        request={'operation': 'inspect_tool', 'tool_id': PHYKIT, 'history_id': None},
        checks=[chk('equals', 'response.outcome', value='accepted'), chk('nonempty', 'response.schema'),
                chk('max', 'response.response_bytes', value=DISCOVERY_LIMIT)],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed', 'schema': {'operation': {'type': 'conditional'}},
                   'response_bytes': 6000})
    add(id='R4-02', requirement='R4', category='discovery', control='positive',
        description='Search returns at most ten ranked cards of bounded size, with the expected tool near the top.',
        request={'operation': 'search_tools', 'query': 'phykit tree metrics'},
        checks=[chk('equals', 'response.outcome', value='accepted'), chk('max_len', 'response.results', value=10),
                chk('max', 'response.response_bytes', value=DISCOVERY_LIMIT), chk('max_item_bytes', 'response.results', value=CARD_LIMIT),
                chk('rank_within', 'response.results', key='tool_id', value=PHYKIT, k=3)],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed', 'response_bytes': 3000,
                   'results': [{'tool_id': PHYKIT, 'name': 'PhyKIT metrics', 'underlying_version': '<freeze:phykit_requirement_version>'}]},
        freeze=['phykit_requirement_version'])
    add(id='R4-03', requirement='R4', category='discovery', control='positive',
        description='A search with no match returns an empty result, not an error.',
        request={'operation': 'search_tools', 'query': 'zzfixture-no-such-tool-qq'},
        checks=[chk('equals', 'response.outcome', value='accepted'), chk('max_len', 'response.results', value=0)],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed', 'results': [], 'response_bytes': 64})

    # ---------------- R5 life cycle
    add(id='R5-01', requirement='R5', category='lifecycle', control='positive',
        description='Copy the seed history through the interface (agents otherwise scripted the API).',
        request={'operation': 'copy_history', 'source': 'fixture-seed-history'},
        checks=[chk('equals', 'response.outcome', value='accepted'), chk('nonempty', 'response.receipt.history_id'),
                chk('equals', 'response.dataset_count', value=2)],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed', 'dataset_count': 2,
                   'receipt': {'history_id': 'history-copy-1', 'account': 'fixture-account-1'}})
    add(id='R5-02', requirement='R5', category='lifecycle', control='positive',
        description='Full dataset download round-trips: the downloaded bytes hash to the staged input.',
        request={'operation': 'download_dataset', 'dataset': ds('reads.fastq.gz'), 'full': True}, inputs=['reads.fastq.gz'],
        checks=[chk('equals', 'response.outcome', value='accepted'), chk('equals_input_hash', 'response.downloaded_sha256', input='reads.fastq.gz')],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed', 'downloaded_sha256': '<input:reads.fastq.gz>'})
    add(id='R5-03', requirement='R5', category='lifecycle', control='positive',
        description='A wait that times out can be resumed and reaches the final state without a duplicate job.',
        request={'operation': 'wait_jobs', 'submit': custom('sleep 120; echo done'), 'timeout_seconds': 5, 'resume': True},
        checks=[chk('equals', 'response.job_state', value='ok'), chk('max_len', 'response.receipt.job_ids', value=1), chk('nonempty', 'response.resume_token')],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed', 'job_state': 'ok', 'resume_token': 'wait-1',
                   'receipt': receipt([])},
        freeze=['python_image'])
    add(id='R5-04', requirement='R5', category='lifecycle', control='positive',
        description='Staging keeps the file name and datatype (encode-atac-pipeline-q1: names staged as dataset_N.dat disabled trimming).',
        request={'operation': 'stage_file', 'path': 'reads.fastq.gz'}, inputs=['reads.fastq.gz'],
        checks=[chk('equals', 'response.outcome', value='accepted'), chk('equals', 'response.dataset.name', value='reads.fastq.gz'),
                chk('equals', 'response.dataset.datatype', value='fastqsanger.gz')],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed',
                   'dataset': {'name': 'reads.fastq.gz', 'datatype': 'fastqsanger.gz', 'sha256': '<input:reads.fastq.gz>'}})

    # ---------------- R6 attestation and isolation
    add(id='R6-01', requirement='R6', category='attestation', control='positive',
        description='A workbench job returns a complete receipt: run, account, job, location, input and output hashes.',
        request={'operation': 'run_tool', 'tool_id': PHYKIT, 'input_format': '21.01', 'inputs': nested_single}, inputs=['single.treefile'],
        checks=ACCEPTED_JOB + RECEIPT_CHECKS + [chk('equals', 'response.receipt.execution_location', value='workbench_job'),
                                                chk('equals', 'response.receipt.checked_by_interface', value=True)],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed',
                   'resolved_state': {'operation|selector': 'evolutionary_rate', 'operation|input_mode|selector': 'single'},
                   'comparison': {'status': 'matched', 'compared_paths': ['operation|selector', 'operation|input_mode|selector'], 'unsupported_paths': []},
                   'receipt': receipt(['single.treefile'])})
    add(id='R6-02', requirement='R6', category='attestation', control='known_location',
        description='A declared local step (answer extraction) is recorded as local, not as a workbench job.',
        request={'operation': 'record_local_step', 'purpose': 'answer_extraction', 'inputs': [ds('values_a.tsv')]}, inputs=['values_a.tsv'],
        checks=[chk('equals', 'response.receipt.execution_location', value='local'), chk('equals_inputs', 'response.receipt.input_hashes')],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed',
                   'receipt': {'run_id': 'run-0001', 'account': 'fixture-account-1', 'execution_location': 'local',
                               'input_hashes': {'values_a.tsv': '<input:values_a.tsv>'}}})
    add(id='R6-03', requirement='R6', category='attestation', control='known_location',
        description='A job submitted by raw API request outside the interface is attested as unchecked.',
        request={'operation': 'raw_api_submission', 'tool_id': PHYKIT, 'inputs': nested_single}, inputs=['single.treefile'],
        checks=[chk('equals', 'response.receipt.execution_location', value='workbench_job'),
                chk('equals', 'response.receipt.checked_by_interface', value=False)],
        reference={'outcome': 'accepted', 'job_created': True, 'phase': 'completed', 'receipt': receipt(['single.treefile'], checked=False)})
    add(id='R6-04', requirement='R6', category='isolation', control='negative',
        description="Reading another run's history is refused and logged.",
        request={'operation': 'inspect_history', 'history_id': 'fixture-history-of-account-2', 'as_account': 'fixture-account-1'},
        checks=[chk('equals', 'response.outcome', value='rejected'), chk('equals', 'response.audit_logged', value=True)],
        reference={'outcome': 'rejected', 'job_created': False, 'phase': 'pre_dispatch', 'audit_logged': True,
                   'diagnostics': {'availability': 'structured_reason', 'message': 'history belongs to another account'}})
    add(id='R6-05', requirement='R6', category='isolation', control='positive',
        description="Reading the run's own history succeeds (so refusing everything cannot pass R6-04).",
        request={'operation': 'inspect_history', 'history_id': 'fixture-history-of-account-1', 'as_account': 'fixture-account-1'},
        checks=[chk('equals', 'response.outcome', value='accepted')],
        reference={'outcome': 'accepted', 'job_created': False, 'phase': 'completed'})
    return F


# ---------------------------------------------------------------------------------------------------- archive basis
def check_basis(fx):
    out = []
    for f in fx:
        b = f.get('archive_basis')
        if not b:
            continue
        p = ROOT / b['ledger']
        found = False
        if p.exists():
            for e in json.load(open(p))['events']:
                if e.get('tool') != b['event_tool']:
                    continue
                s = json.dumps(e.get('parameters') or {})
                if all(c in s for c in b['request_contains']):
                    found = e['event_id']
                    break
        out.append(dict(fixture=f['id'], ledger=b['ledger'], verified=bool(found), event_id=found or None))
    return out


def main():
    hashes = write_inputs()
    fx = fixtures()
    for f in fx:
        f['input_hashes'] = {n: hashes[n] for n in f['inputs']}
    ids = [f['id'] for f in fx]
    assert len(ids) == len(set(ids)), 'duplicate fixture id'
    basis_report = check_basis(fx)
    for r in basis_report:
        next(f for f in fx if f['id'] == r['fixture'])['archive_basis']['verified_event_id'] = r['event_id']
    doc = {'suite': 'agent-workbench conformance fixtures', 'version': '0.1.0', 'limits': {'discovery_bytes': DISCOVERY_LIMIT, 'card_bytes': CARD_LIMIT},
           'status': 'Specified and self-tested; not yet run against any deployment.', 'fixtures': fx}
    json.dump(doc, open(HERE / 'fixtures.json', 'w'), indent=1)
    json.dump(basis_report, open(HERE / 'archive_basis_check.json', 'w'), indent=1)
    by = {}
    for f in fx:
        by.setdefault(f['requirement'], []).append(f['control'])
    print(f'{len(fx)} fixtures:', {k: len(v) for k, v in sorted(by.items())})
    print('archive basis verified:', sum(r['verified'] for r in basis_report), 'of', len(basis_report))


if __name__ == '__main__':
    main()
