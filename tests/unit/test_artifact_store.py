from __future__ import annotations

import json

import pytest

from galaxy_benchmark.domain.enums import AccessMode, KnowledgeCondition
from galaxy_benchmark.domain.exceptions import ArtifactAlreadyExistsError
from galaxy_benchmark.domain.models import RunConfiguration
from galaxy_benchmark.infrastructure.storage.filesystem import LocalFilesystemArtifactStore


def test_artifact_store_creates_immutable_run_layout(tmp_path) -> None:
    store = LocalFilesystemArtifactStore(tmp_path)
    config = RunConfiguration(
        run_id="20260327_153045_core_tabular_001_openai_api_novice_r1",
        task_id="core_tabular_001",
        agent_id="openai",
        access_mode=AccessMode.API,
        knowledge_condition=KnowledgeCondition.NONE,
        prompt_variant_id="core_tabular_001_novice_brief",
    )

    paths, manifest = store.create_run(config)
    assert paths.root.exists()
    assert paths.trace_dir.exists()
    manifest_payload = json.loads(paths.manifest.read_text())
    assert manifest_payload["run_id"] == manifest.run_id

    result_path = store.write_json("results/result.json", {"tool_name": "Tabular Learner"})
    assert json.loads(result_path.read_text())["tool_name"] == "Tabular Learner"

    activity_log = store.append_jsonl(
        "trace/activity_log.jsonl",
        [{"step": "plan", "category": "plan", "status": "ok", "action": "prepare"}],
    )
    assert activity_log.read_text().count("\n") == 1

    with pytest.raises(ArtifactAlreadyExistsError):
        store.write_json("results/result.json", {"tool_name": "Overwritten"})
