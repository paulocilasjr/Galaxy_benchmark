"""Filesystem-backed immutable artifact store."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from galaxy_benchmark.domain.exceptions import ArtifactAlreadyExistsError
from galaxy_benchmark.domain.models import RunConfiguration, RunManifest, RunPaths


class LocalFilesystemArtifactStore:
    """Persist immutable run artifacts on the local filesystem."""

    def __init__(self, base_dir: Path | str = "runs") -> None:
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self._active_root: Path | None = None

    def create_run(self, config: RunConfiguration) -> tuple[RunPaths, RunManifest]:
        root = self.base_dir / config.run_id
        if root.exists():
            raise ArtifactAlreadyExistsError(f"Run directory already exists: {root}")

        subdirs = {
            "input_dir": root / "input",
            "plan_dir": root / "plan",
            "trace_dir": root / "trace",
            "reasoning_dir": root / "reasoning",
            "errors_dir": root / "errors",
            "results_dir": root / "results",
            "artifacts_dir": root / "artifacts",
        }
        for path in [root, *subdirs.values(), root / "artifacts" / "downloaded_reports", root / "artifacts" / "exported_histories", root / "artifacts" / "screenshots"]:
            path.mkdir(parents=True, exist_ok=False)

        manifest = RunManifest(
            run_id=config.run_id,
            task_id=config.task_id,
            agent_id=config.agent_id,
            agent_type=config.agent_type,
            provider=config.provider,
            model_name=config.model_name,
            access_mode=config.access_mode,
            knowledge_condition=config.knowledge_condition,
            mcp_enabled=config.mcp_enabled,
            prompt_variant_id=config.prompt_variant_id,
            prompt_tier=config.prompt_tier,
            prompt_format=config.prompt_format,
            repeat_index=config.repeat_index,
            seed=config.seed,
            artifact_root=root,
        )
        self._active_root = root
        paths = RunPaths(
            root=root,
            manifest=root / "manifest.json",
            input_dir=subdirs["input_dir"],
            plan_dir=subdirs["plan_dir"],
            trace_dir=subdirs["trace_dir"],
            reasoning_dir=subdirs["reasoning_dir"],
            errors_dir=subdirs["errors_dir"],
            results_dir=subdirs["results_dir"],
            artifacts_dir=subdirs["artifacts_dir"],
        )
        self.write_json("manifest.json", manifest.model_dump(mode="json"))
        return paths, manifest

    def write_json(self, relative_path: str | Path, payload: Any) -> Path:
        path = self._resolve(relative_path)
        self._assert_new(path)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return path

    def write_text(self, relative_path: str | Path, content: str) -> Path:
        path = self._resolve(relative_path)
        self._assert_new(path)
        path.write_text(content)
        return path

    def append_jsonl(self, relative_path: str | Path, entries: list[dict[str, Any]]) -> Path:
        path = self._resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for entry in entries:
                handle.write(json.dumps(entry, sort_keys=True) + "\n")
        return path

    def _resolve(self, relative_path: str | Path) -> Path:
        if self._active_root is None:
            raise RuntimeError("create_run must be called before writing artifacts")
        relative = Path(relative_path)
        return self._active_root / relative

    @staticmethod
    def _assert_new(path: Path) -> None:
        if path.exists():
            raise ArtifactAlreadyExistsError(f"Immutable artifact already exists: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
