#!/usr/bin/env python3
"""Regression coverage for the benchmark scorer."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools import benchmark_scorer as scorer


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, entries: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _base_error_payload(experiment_id: str) -> dict[str, Any]:
    return {
        "experiment_name": experiment_id,
        "run_status": "completed",
        "started_at": "2026-04-12T12:00:00Z",
        "updated_at": "2026-04-12T12:05:00Z",
        "summary": {"total_errors": 0, "open_errors": 0, "resolved_errors": 0},
        "errors": [],
    }


def _base_activity_log() -> list[dict[str, Any]]:
    return [
        {
            "timestamp": "2026-04-12T12:00:01Z",
            "step": "plan",
            "category": "plan",
            "action": "plan_run",
            "status": "completed",
            "details": {},
        },
        {
            "timestamp": "2026-04-12T12:00:10Z",
            "step": "execute",
            "category": "execute",
            "action": "run_workflow",
            "status": "completed",
            "details": {},
        },
        {
            "timestamp": "2026-04-12T12:01:00Z",
            "step": "check",
            "category": "check",
            "action": "monitor_run",
            "status": "completed",
            "details": {},
        },
    ]


class BenchmarkScorerRegressionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="benchmark-scorer-fixtures-"))

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def _make_run_dir(
        self,
        experiment_id: str,
        result_payload: dict[str, Any],
        *,
        level: str | None = None,
        activity_log: list[dict[str, Any]] | None = None,
        error_payload: dict[str, Any] | None = None,
        plan_text: str = "Use the test dataset and preserve Galaxy provenance.\n",
        reasoning_text: str = "Selected the benchmark-aligned workflow and monitored it to completion.\n",
        reproduce_text: str = "# reproduce fixture\n",
        workflow_export: dict[str, Any] | None = None,
        workflow_metadata: dict[str, Any] | None = None,
        history_contents: dict[str, Any] | None = None,
        tool_outputs: dict[str, Any] | None = None,
        tool_discovery: dict[str, Any] | None = None,
    ) -> Path:
        suffix = level or "fixture"
        run_dir = self.temp_dir / f"{experiment_id}_{suffix}"
        _write_json(run_dir / "results" / "result.json", result_payload)
        _write_jsonl(run_dir / "results" / "activity_log.jsonl", activity_log or _base_activity_log())
        _write_json(run_dir / "errors" / "error.json", error_payload or _base_error_payload(experiment_id))
        _write_text(run_dir / "plan" / "saved.md", plan_text)
        _write_text(run_dir / "reasoning" / "reasoning.md", reasoning_text)
        _write_text(run_dir / "results" / f"reproduce_{experiment_id}.py", reproduce_text)
        if workflow_export is not None:
            _write_json(run_dir / "results" / "workflow_export.json", workflow_export)
        if workflow_metadata is not None:
            _write_json(run_dir / "results" / "workflow_metadata.json", workflow_metadata)
        if history_contents is not None:
            _write_json(run_dir / "results" / "history_contents.json", history_contents)
        if tool_outputs is not None:
            _write_json(run_dir / "results" / "tool_outputs.json", tool_outputs)
        if tool_discovery is not None:
            _write_json(run_dir / "results" / "tool_discovery.json", tool_discovery)
        return run_dir

    def _score_run(self, run_dir: Path, experiment_id: str, level: str | None = None):
        bundle = scorer.build_bundle(run_dir, experiment_id, level)
        normalized_result = scorer.normalize_result(bundle)

        entries = []
        entries.extend(scorer.build_scientific_comparisons(normalized_result, bundle))
        entries.extend(scorer.build_standard_comparisons(normalized_result, bundle))
        entries.extend(scorer.build_galaxy_comparisons(normalized_result, bundle))

        score_summaries = {
            "scientific_solution_score": scorer.summarize_score(
                "scientific_solution_score",
                [entry for entry in entries if entry.score_name == "scientific_solution_score"],
                bundle,
            ),
            "standard_analysis_score": scorer.summarize_score(
                "standard_analysis_score",
                [entry for entry in entries if entry.score_name == "standard_analysis_score"],
                bundle,
            ),
            "galaxy_execution_score": scorer.summarize_score(
                "galaxy_execution_score",
                [entry for entry in entries if entry.score_name == "galaxy_execution_score"],
                bundle,
            ),
        }
        return normalized_result, entries, score_summaries

    def test_experiment_1_normalizes_legacy_metric_object(self) -> None:
        activity_log = _base_activity_log()
        activity_log[-1]["details"] = {"split": "test"}
        run_dir = self._make_run_dir(
            "experiment_1",
            {
                "tool_name": "Tabular Learner",
                "target": "Response",
                "roc-auc": {"value": 0.87, "label": "test ROC-AUC"},
            },
            activity_log=activity_log,
            history_contents={"history_id": "hist-1"},
        )
        normalized, _, summaries = self._score_run(run_dir, "experiment_1")
        self.assertEqual(normalized["scientific_answer"]["primary_metric"]["name"], "ROC-AUC")
        self.assertEqual(normalized["scientific_answer"]["primary_metric"]["split"], "test")
        self.assertEqual(normalized["scientific_answer"]["primary_metric"]["value"], 0.87)
        self.assertEqual(summaries["scientific_solution_score"].value, 1.0)
        self.assertLess(summaries["galaxy_execution_score"].value, 0.95)

    def test_experiment_4_parses_descriptive_step_count_and_input_type(self) -> None:
        run_dir = self._make_run_dir(
            "experiment_4",
            {
                "input": "list:paired collection",
                "last artifact": "bigWig",
                "workflow steps": "Workflow contains 27 tool steps excluding inputs.",
            },
            workflow_export={
                "name": "ATAC-seq Analysis: Chromatin Accessibility Profiling",
                "annotation": "IWC ATAC-seq training workflow for chromatin accessibility profiling",
            },
            workflow_metadata={
                "workflow_name": "ATAC-seq Analysis: Chromatin Accessibility Profiling",
                "counts": {"execution_steps_excluding_inputs": 27},
            },
            history_contents={"datasets": [{"name": "forward.fastqsanger.gz"}]},
            tool_discovery={"tutorial_matches": ["Intergalactic Workflow Commission ATAC tutorial"]},
        )
        normalized, entries, summaries = self._score_run(run_dir, "experiment_4")
        self.assertEqual(normalized["galaxy_execution"]["workflow_tool_step_count"], 27)
        workflow_input_entry = next(
            entry for entry in entries if entry.field_path == "scientific_answer.workflow_input_type"
        )
        self.assertEqual(workflow_input_entry.match_status, "match")
        self.assertEqual(summaries["galaxy_execution_score"].value, 1.0)

    def test_experiment_6_high_context_scores_cleanly(self) -> None:
        run_dir = self._make_run_dir(
            "experiment_6",
            {
                "data_normalization": "scanpy_normalize",
                "list_of_genes": ["LDHB", "NKG7", "FCER1A", "CST3"],
                "total_tool_steps": "Workflow has 18 tool steps.",
            },
            level="high_context",
            workflow_export={
                "name": "Single-cell RNA-seq workflow",
                "annotation": "scanpy normalization Louvain clustering UMAP dotplot marker visualization",
            },
            workflow_metadata={
                "workflow_name": "Single-cell RNA-seq workflow",
                "counts": {"execution_steps_excluding_inputs": 18},
            },
            history_contents={"datasets": [{"name": "matrix.mtx"}]},
        )
        _, _, summaries = self._score_run(run_dir, "experiment_6", level="high_context")
        self.assertEqual(summaries["scientific_solution_score"].value, 1.0)
        self.assertEqual(summaries["standard_analysis_score"].value, 1.0)
        self.assertGreaterEqual(summaries["galaxy_execution_score"].value, 0.93)

    def test_experiment_8_uses_completed_tool_count_and_maker_entity(self) -> None:
        run_dir = self._make_run_dir(
            "experiment_8",
            {
                "tool_name_1": "BUSCO",
                "tool_name_2": "JBrowse",
                "total_tools": "7 completed tool executions",
            },
            level="high_context",
            workflow_export={
                "name": "Maker genome annotation workflow",
                "annotation": "genome annotation workflow",
            },
            tool_outputs={
                "steps": {
                    "Maker": {"name": "Maker", "state": "ok"},
                    "BUSCO": {"name": "BUSCO", "state": "ok"},
                    "JBrowse": {"name": "JBrowse", "state": "ok"},
                    "step4": {"name": "step4", "state": "ok"},
                    "step5": {"name": "step5", "state": "ok"},
                    "step6": {"name": "step6", "state": "ok"},
                    "step7": {"name": "step7", "state": "ok"},
                }
            },
            history_contents={"datasets": [{"name": "S_pombe_chrIII_genome.fasta"}]},
        )
        normalized, _, summaries = self._score_run(run_dir, "experiment_8", level="high_context")
        self.assertEqual(normalized["galaxy_execution"]["total_tool_executions"], 7)
        self.assertIn("maker", normalized["galaxy_execution"]["final_entity_name"].lower())
        self.assertGreaterEqual(summaries["galaxy_execution_score"].value, 0.93)

    def test_experiment_5_medium_context_standard_score_is_active(self) -> None:
        run_dir = self._make_run_dir(
            "experiment_5",
            {
                "analysis_type": "RNA-seq",
                "artifact": "MultiQC HTML Report",
                "workflow steps": "Workflow has 12 tool steps.",
            },
            level="medium_context",
            workflow_export={
                "name": "RNA-seq Analysis Workflow",
                "annotation": "fastp STAR quantification reporting",
            },
            workflow_metadata={
                "workflow_name": "RNA-seq Analysis Workflow",
                "counts": {"execution_steps_excluding_inputs": 12},
            },
            history_contents={"datasets": [{"name": "SRR5085167_forward.fastqsanger.gz"}]},
        )
        _, _, summaries = self._score_run(run_dir, "experiment_5", level="medium_context")
        self.assertEqual(summaries["standard_analysis_score"].value, 1.0)
        self.assertEqual(summaries["standard_analysis_score"].status, "pass")


if __name__ == "__main__":
    unittest.main()
