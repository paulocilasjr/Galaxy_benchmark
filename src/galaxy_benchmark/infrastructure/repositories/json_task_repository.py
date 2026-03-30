"""JSON-backed repository for canonical benchmark assets."""

from __future__ import annotations

import json
from pathlib import Path

from galaxy_benchmark.domain.models import BenchmarkTask, GroundTruth


class JsonTaskRepository:
    """Load and store canonical tasks and ground truths."""

    def load_task(self, path: str | Path) -> BenchmarkTask:
        return BenchmarkTask.model_validate_json(Path(path).read_text())

    def load_ground_truth(self, path: str | Path) -> GroundTruth:
        return GroundTruth.model_validate_json(Path(path).read_text())

    def list_tasks(self, directory: str | Path) -> list[BenchmarkTask]:
        return [self.load_task(path) for path in sorted(Path(directory).glob("*.json"))]

    def save_task(self, task: BenchmarkTask, path: str | Path) -> Path:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(task.model_dump(mode="json"), indent=2) + "\n")
        return file_path

    def save_ground_truth(self, ground_truth: GroundTruth, path: str | Path) -> Path:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(ground_truth.model_dump(mode="json"), indent=2) + "\n")
        return file_path
