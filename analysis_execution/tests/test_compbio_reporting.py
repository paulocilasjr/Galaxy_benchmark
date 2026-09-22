"""Guard evidence distinctions in the generated CompBio manuscript tables."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('compbio_audit', ROOT / 'scripts/audit_compbio_overview.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class CompBioReportingTest(unittest.TestCase):
    def test_history_state_ids_preserve_errors_hidden_by_summary_counts(self):
        history = {
            'count': 6,
            'state_details': {'ok': 2, 'error': 0},
            'state_ids': {'ok': ['a', 'b'], 'error': ['c', 'd', 'e']},
        }
        summary = audit.history_state_summary(history)
        self.assertEqual(summary['state_id_counts'], {'ok': 2, 'error': 3})
        self.assertEqual(summary['elements_without_state_id'], 1)
        self.assertEqual(summary['state_count_disagreements'], {
            'error': {'state_details': 0, 'state_ids_count': 3},
        })
        self.assertEqual(history['state_details']['error'], 0)

    def test_missing_history_states_are_unknown(self):
        summary = audit.history_state_summary({'count': 6})
        self.assertIsNone(summary['state_id_counts'])
        self.assertIsNone(summary['elements_without_state_id'])

    def test_top_tools_include_all_cutoff_ties_in_stable_order(self):
        counts = {'top': 19, 'z': 4, 'b': 4, 'a': 4, 'low': 3}
        expected = [('top', 19), ('a', 4), ('b', 4), ('z', 4)]
        self.assertEqual(audit.top_tools_with_ties(counts), expected)
        self.assertEqual(audit.top_tools_with_ties(dict(reversed(list(counts.items())))), expected)
        self.assertEqual(audit.top_tools_with_ties({}), [])

    def test_archived_report_preserves_provenance_and_fractional_statistics(self):
        data = json.loads((ROOT / 'CompBio/compBio_overview_audit.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            with patch.object(audit, 'BASE', folder):
                audit.write_reports(data)
            report = (folder / 'result_section_compbio.md').read_text()
            overview = (folder / 'compBio_overview.md').read_text()

        score_section = report.split('**Table 1.', 1)[1].split('**Table 2.', 1)[0]
        score_table = '\n'.join(line for line in score_section.splitlines() if line.startswith('|'))
        self.assertEqual(score_table.count('; hash mismatch'), 9)
        self.assertEqual(score_table.count('; vector unavailable'), 3)
        self.assertIn('r1: 93/100 (O; previously 92/100 P)', score_table)
        self.assertIn('r3: 91/100 (O; hash mismatch; previously 92/100 P)', score_table)
        examples = report.split('**Table 5.', 1)[1].split('**Table 6.', 1)[0]
        atac_row = next(line for line in examples.splitlines() if '| [sample-swap-atac-q1]' in line)
        for tool in ['Summary_Statistics1 (19)', 'Cut1 (4)', 'axolotl-atac-swap-diagnostic-v1 (4)', 'filter_tabular/3.3.1 (4)']:
            self.assertIn(tool, atac_row)
        self.assertIn('3748257.5 | 1438300.00-10355795.75 | 13832.5', report)
        self.assertIn('`run_summaries.answer_sha256` hashes raw answer-file bytes', report)
        for text in (report, overview):
            self.assertIn('676/1188', text)
            self.assertIn('882/1200', text)
            self.assertIn('196 error-state elements and 17 elements without a listed state ID', text)
            self.assertIn('Spearman rho = -0.105, n = 97 tasks', text)


if __name__ == '__main__':
    unittest.main()
