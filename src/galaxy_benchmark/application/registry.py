from __future__ import annotations

import json
from pathlib import Path
from typing import Any


LEVELS = ("low_context", "medium_context", "high_context")


class BenchmarkRegistry:
    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)

    def list_experiments(self, level: str | None = None) -> list[str]:
        if level:
            return sorted(
                path.stem for path in (self.root_dir / "experiments" / level).glob("*.json")
            )
        experiment_ids: set[str] = set()
        for item in LEVELS:
            experiment_ids.update(self.list_experiments(level=item))
        return sorted(experiment_ids)

    def load_experiment(self, experiment_id: str, level: str) -> dict[str, Any]:
        path = self.root_dir / "experiments" / level / f"{experiment_id}.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def load_task_matrix(
        self,
        experiment_ids: list[str] | None = None,
        levels: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        selected_levels = levels or list(LEVELS)
        selected_ids = experiment_ids or self.list_experiments()
        matrix = []
        for experiment_id in selected_ids:
            for level in selected_levels:
                matrix.append(self.load_experiment(experiment_id, level))
        return matrix
