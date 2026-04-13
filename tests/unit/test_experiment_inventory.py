from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark.application.registry import BenchmarkRegistry


class ExperimentInventoryTest(unittest.TestCase):
    def test_all_context_levels_have_eleven_experiments(self) -> None:
        registry = BenchmarkRegistry(ROOT_DIR)
        self.assertEqual(len(registry.list_experiments(level="low_context")), 11)
        self.assertEqual(len(registry.list_experiments(level="medium_context")), 11)
        self.assertEqual(len(registry.list_experiments(level="high_context")), 11)
        self.assertIn("experiment_9", registry.list_experiments(level="low_context"))
        self.assertIn("experiment_10", registry.list_experiments(level="medium_context"))
        self.assertIn("experiment_11", registry.list_experiments(level="high_context"))


if __name__ == "__main__":
    unittest.main()
