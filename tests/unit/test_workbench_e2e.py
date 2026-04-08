from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark.agents import EchoAgentAdapter, HeuristicAgentAdapter
from galaxy_benchmark.application.orchestrator import BenchmarkWorkbench
from galaxy_benchmark.environments import GalaxyEnvironmentRunner, OpenEnvironmentRunner


class WorkbenchE2ETest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="workbench-test-"))
        self.output_root = self.temp_dir / "outputs"
        self.output_root.mkdir()
        self.workbench = BenchmarkWorkbench(ROOT_DIR)

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def test_execute_task_writes_required_artifacts(self) -> None:
        task = json.loads((ROOT_DIR / "experiments" / "low_context" / "experiment_1.json").read_text(encoding="utf-8"))
        run_dir = self.workbench.execute_task(
            task=task,
            environment=GalaxyEnvironmentRunner(),
            agent=HeuristicAgentAdapter(),
            output_root=self.output_root,
        )
        self.assertTrue((run_dir / "plan" / "saved.md").exists())
        self.assertTrue((run_dir / "reasoning" / "reasoning.md").exists())
        self.assertTrue((run_dir / "errors" / "error.json").exists())
        self.assertTrue((run_dir / "results" / "result.json").exists())
        self.assertTrue((run_dir / "results" / "reproduce_experiment_1.py").exists())
        self.assertTrue((run_dir / "results" / "activity_log.jsonl").exists())
        self.assertTrue((run_dir / "results" / "run_record.json").exists())

        result = json.loads((run_dir / "results" / "result.json").read_text(encoding="utf-8"))
        self.assertIn("scientific_answer", result)
        self.assertIn("galaxy_execution", result)
        self.assertEqual(result["scientific_answer"]["target"], "Response")

    def test_execute_open_environment_generates_partial_run_record(self) -> None:
        task = json.loads((ROOT_DIR / "experiments" / "low_context" / "experiment_1.json").read_text(encoding="utf-8"))
        run_dir = self.workbench.execute_task(
            task=task,
            environment=OpenEnvironmentRunner(),
            agent=EchoAgentAdapter(),
            output_root=self.output_root,
        )
        run_record = json.loads((run_dir / "results" / "run_record.json").read_text(encoding="utf-8"))
        self.assertEqual(run_record["environment"], "open")
        self.assertEqual(run_record["status"], "partial")


if __name__ == "__main__":
    unittest.main()
