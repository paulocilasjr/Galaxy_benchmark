"""Artifact and definition storage ports."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from galaxy_benchmark.domain.models import BenchmarkTask, GroundTruth, RunConfiguration, RunManifest, RunPaths


class ArtifactStorePort(Protocol):
    """Create and persist immutable run artifacts."""

    def create_run(self, config: RunConfiguration) -> tuple[RunPaths, RunManifest]: ...

    def write_json(self, relative_path: str | Path, payload: Any) -> Path: ...

    def write_text(self, relative_path: str | Path, content: str) -> Path: ...

    def append_jsonl(self, relative_path: str | Path, entries: list[dict[str, Any]]) -> Path: ...


class TaskRepositoryPort(Protocol):
    """Load and persist canonical task definitions."""

    def load_task(self, path: str | Path) -> BenchmarkTask: ...

    def load_ground_truth(self, path: str | Path) -> GroundTruth: ...

    def list_tasks(self, directory: str | Path) -> list[BenchmarkTask]: ...
