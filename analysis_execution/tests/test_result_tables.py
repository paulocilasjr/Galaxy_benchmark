"""Check cluster weighting, missingness and traceability of the result tables."""
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('result_tables', ROOT / 'scripts/build_result_tables.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class ClusterBootstrapTest(unittest.TestCase):
    def test_unequal_clusters_keep_all_rows_and_target_row_weighted_mean(self):
        rows = [{'cluster': 'a', 'value': 0}] + [{'cluster': 'b', 'value': 6}] * 3
        with patch.object(builder, 'RESAMPLES', 1000):
            result, draws = builder.bootstrap(rows, 'value', 'fixture')
            _, repeated = builder.bootstrap(rows, 'value', 'fixture')
        self.assertEqual(result['estimate'], 4.5)
        self.assertEqual(result['clusters'], 2)
        self.assertEqual(result['n'], 4)
        self.assertEqual(set(draws), {0.0, 4.5, 6.0})
        self.assertTrue((draws == repeated).all())

    def test_display_names_do_not_corrupt_harness_identity(self):
        self.assertEqual(builder.reader_labels('G / Code; Claude Code; 3 pp'),
                         'Galaxy / open-ended code; Claude Code; 3 percentage points')

    def test_request_and_execution_are_distinct_and_unknown_exits_are_not_zero(self):
        evidence = {'task': {'prompt': 'Count genes'}}
        events = [{'tool': 'run_galaxy_udt_and_wait', 'execution_location': 'agent_runtime', 'event_id': 'request',
                   'parameters': {'representation': {'class':'GalaxyUserTool','id':'custom-count'}}},
                  {'tool': 'shell', 'execution_location': 'agent_runtime', 'exit_code': None}]
        original = {'events':events, 'artifacts':[], 'derived_metrics':{'completed_shell_calls':1}}
        row = {'coverage':{'agent_transcript':'retrieved'}, 'nonzero_shell':0}
        builder.deep.enrich_run(evidence,original,row)
        self.assertTrue(row['udt_requested'])
        self.assertEqual(row['udt_matched_job_ids'],[])
        self.assertIsNone(row['has_nonzero_shell'])
        events.append({'tool':'custom-count','execution_location':'galaxy_job','native_job_id':'job','status':'error'})
        builder.deep.enrich_run(evidence,original,row)
        self.assertEqual(row['udt_matched_job_ids'],['job'])
        self.assertEqual(row['udt_matched_success_ids'],[])
        self.assertEqual(builder.deep.object_value('class: GalaxyUserTool\nid: guessed'),{})


class GeneratedReportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / 'BixBench50_CompBio_analysis/analysis.json').read_text())
        cls.manifest = json.loads((ROOT / 'BixBench50_CompBio_analysis/source_manifest.json').read_text())
        cls.report = (ROOT / 'Result_table.md').read_text()

    def test_four_sections_and_tables_render_the_saved_values(self):
        self.assertEqual(len(re.findall(r'^## ', self.report, re.M)), 4)
        self.assertEqual(len(re.findall(r'^### Table ', self.report, re.M)), len(self.data['tables']))
        for key, table in self.data['tables'].items():
            section = self.report.split(f'### Table {key}. ', 1)[1].split('\n### ', 1)[0]
            for row in table['rows']:
                self.assertEqual(len(row), len(table['headers']))
                line = '| ' + ' | '.join(v.replace('|', '&#124;').replace('\n', ' ') for v in row) + ' |'
                self.assertIn(line, section)
        self.assertFalse(any(line.rstrip() != line for line in self.report.splitlines()))

    def test_unscored_and_unobservable_records_remain_unknown(self):
        for run in self.data['runs']:
            if run['benchmark'] == 'CompBio':
                self.assertIsNone(run['score'])
            if run['condition'] != 'galaxy' or run['coverage']['public_history_contents'] != 'retrieved':
                self.assertIsNone(run['has_error'])
            if run['shell_events_with_exit_code']==0:
                self.assertIsNone(run['has_nonzero_shell'])
        for cell in self.data['cells']:
            if not cell['eligible']:
                self.assertIsNone(cell['jaccard'])
        models = self.data['common_configurations']
        self.assertEqual(models, list(builder.COMMON))
        self.assertNotIn(builder.DEEP_C, models)

    def test_source_hashes_and_job_references_resolve(self):
        refs = {}
        for job in self.data['jobs']:
            for ref in job['refs']:
                refs.setdefault(ref['evidence'], []).append((ref, job))
        for source in self.manifest['sources']:
            self.assertEqual(hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest(), source['sha256'])
        for source in self.manifest['tasks']:
            raw = (ROOT / source['path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
            evidence = json.loads(raw)
            events = {(r['run_id'], e['event_id']): e for r in evidence['runs'] for e in r['events']}
            self.assertEqual(set(source['included_run_ids']), {r['run_id'] for r in evidence['runs']})
            for ref, job in refs.get(source['path'], []):
                event = events[ref['run_id'], ref['event_id']]
                self.assertEqual(event['native_job_id'], job['native_job_id'])
                self.assertEqual(event['status'], job['status'])
                self.assertEqual(event['tool'], job['tool'])

    def test_local_markdown_links_resolve(self):
        for target in re.findall(r'\]\(([^)]+)\)', self.report):
            if not target.startswith('https://'):
                self.assertTrue((ROOT / target.split('#')[0]).exists(), target)

    def test_deeper_findings_and_case_provenance(self):
        udt = self.data['results']['deep']['udt']
        bix = next(x for x in udt if x['benchmark']=='BixBench50' and x['model']=='all')
        comp = next(x for x in udt if x['benchmark']=='CompBio' and x['model']=='all')
        self.assertEqual((bix['request_runs'],len(bix['request_tasks'])),(267,41))
        self.assertEqual((comp['request_runs'],len(comp['request_tasks'])),(808,97))
        for row in udt:
            self.assertEqual(row['zero_request_cells']+row['variable_request_cells']+row['all_request_cells'],row['complete_cells'])
            self.assertLessEqual(row['success_linked_runs'],row['job_linked_runs'])
        for source in self.manifest['reviewed_trace_sources']:
            self.assertEqual(hashlib.sha256((ROOT/source['path']).read_bytes()).hexdigest(),source['sha256'])
        shell = next(x for x in self.data['results']['deep']['shell_comparisons'] if x['benchmark']=='BixBench50')
        self.assertEqual(len(shell['pairs']),200)
        self.assertNotRegex(self.report,r'\bG\b')

    def test_iwc_comparisons_use_explicit_matched_populations(self):
        comparisons = {v['model']: v for v in self.data['results']['iwc']['comparisons']}
        for model, row in zip((*builder.MODELS['IWC'], 'all'), self.data['tables']['I1']['rows']):
            expected = comparisons[model]['common_nine']
            count = 108 if model == 'all' else 27
            self.assertEqual(int(row[1].split(';')[0]), count)
            self.assertEqual(int(row[2].split(';')[0]), count)
            self.assertIn(builder.fmt(expected['galaxy'], 4), row[1])
            self.assertIn(builder.fmt(expected['open_ended_code'], 4), row[2])
            self.assertEqual(row[-1], builder.ci(expected, 4))
        for row in self.data['tables']['I2']['rows']:
            self.assertEqual(row[2], '9/9')
        iwc = self.data['tables']['X20']['rows'][-1]
        self.assertIn('81 runs', iwc[1])
        self.assertIn('1/81', iwc[-1])
        self.assertIn('3/81', iwc[-1])

    def test_claims_do_not_upgrade_detection_or_continuous_scores(self):
        for label in ('I1', 'I2', 'I11', 'I13', 'X20'):
            table = self.data['tables'][label]
            self.assertNotIn('>=0.99', json.dumps(table))
        for row in self.data['tables']['X12']['rows']:
            if row[0] == 'IWC':
                self.assertEqual(row[4], 'Not applicable (no detected requests)')
        for phrase in ('native wrappers were sufficient', 'completed through catalog wrappers alone',
                       'The environment gap stays small in every benchmark', 'Runs failing the endpoint'):
            self.assertNotIn(phrase, self.report)


if __name__ == '__main__':
    unittest.main()
