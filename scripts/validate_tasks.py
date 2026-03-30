#!/usr/bin/env python3
"""Validate canonical benchmark tasks and ground truths."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))

    from galaxy_benchmark.infrastructure.repositories.json_task_repository import JsonTaskRepository

    repository = JsonTaskRepository()
    task_dir = root / "benchmark" / "tasks"
    ground_truth_dir = root / "benchmark" / "ground_truth"
    task_paths = sorted(path for path in task_dir.glob("*.json") if path.is_file())
    ground_truth_paths = sorted(path for path in ground_truth_dir.glob("*.json") if path.is_file())
    tasks = [repository.load_task(path) for path in task_paths]
    truths = [repository.load_ground_truth(path) for path in ground_truth_paths]
    print(f"Validated {len(tasks)} task(s) and {len(truths)} ground-truth file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
