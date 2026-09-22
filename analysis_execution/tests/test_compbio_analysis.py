"""Regression checks for CompBio missing scores, usage and unpaired replicates."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from enrich_compbio_evidence import trace_usage

spec=importlib.util.spec_from_file_location('compbio_paths',ROOT/'CompBio/solution_path_consistency_analysis.py')
paths=importlib.util.module_from_spec(spec)
spec.loader.exec_module(paths)


class CompBioAnalysisTest(unittest.TestCase):
    def test_usage_does_not_add_cumulative_snapshots_or_cached_input(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'trace.jsonl'
            records=[{'type':'usage.updated','usage':{'input_tokens':50}},
                     {'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':70,'output_tokens':5}}]
            p.write_text('\n'.join(map(json.dumps,records)))
            totals,lines,missing,_=trace_usage(p)
            self.assertEqual(totals['input_tokens'],100)
            self.assertEqual(lines,[2])
            self.assertIsNone(missing)
            p.write_text(p.read_text()+'\n'+json.dumps(records[-1]))
            self.assertEqual(trace_usage(p)[0],{})
            self.assertEqual(trace_usage(p)[2],'ambiguous_multiple_turn_totals')

    def test_unknown_acceptance_and_missing_fingerprints_remain_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);p=root/'analysis/task';p.mkdir(parents=True)
            runs=[]
            for n in (1,2,3):
                runs.append({'run_id':f'galaxy_codex_gpt_5_5_r{n}','condition':'galaxy','replicate_id':n,
                    'events':[{'execution_location':'galaxy_job','tool':'cut1'}] if n<3 else [],
                    'evidence_completeness':{'public_history_contents':'retrieved' if n<3 else 'history_metadata_only'},
                    'derived_metrics':{'analytical_job_count':1 if n<3 else None,'total_failed_jobs':0 if n<3 else None},
                    'outcome':{'original_evaluator_score':None,'submitted_answer':'A'}})
            (p/'history_analysis_evidence.json').write_text(json.dumps({'task':{'task_id':'task'},'runs':runs}))
            original=paths.HERE
            try:
                paths.HERE=root
                cell=paths.load_cells()[0]
                (p/'history_analysis_evidence.json').write_text(json.dumps({'task':{'task_id':'task'},'runs':runs[:1]}))
                single=paths.load_cells()[0]
            finally:
                paths.HERE=original
            self.assertIsNone(cell['accepted'])
            self.assertFalse(cell['eligible'])
            self.assertIsNone(cell['any_failed_job'])
            self.assertEqual(cell['agreement'],'not_evaluable')
            self.assertEqual(single['exclusion'],'insufficient_replicates')
            self.assertIsNone(single['mean_jaccard'])

    def test_bixbench_instrument_is_reused(self):
        self.assertEqual(paths.bix.galaxy_tool('toolshed.g2.bx.psu.edu/repos/iuc/bedtools/bedtools_intersectbed/2.31.1'),'bedtools_intersectbed')
        self.assertIsNone(paths.bix.galaxy_tool('__DATA_FETCH__'))
        self.assertIsNone(paths.bix.jaccard(set(),set()))
        self.assertEqual(paths.bix.jaccard({'numpy'},{'numpy','scipy'}),.5)


if __name__=='__main__':
    unittest.main()
