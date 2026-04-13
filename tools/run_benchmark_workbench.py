#!/usr/bin/env python3
"""Execute the internal benchmark workbench over task and environment combinations.

The resulting runs are harness artifacts for development and are marked as non-publication-eligible.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark.agents import BUILTIN_AGENTS
from galaxy_benchmark.application.orchestrator import BenchmarkWorkbench
from galaxy_benchmark.application.registry import BenchmarkRegistry
from galaxy_benchmark.application.reporting import benchmark_report_as_dict, build_benchmark_report
from galaxy_benchmark.environments import BUILTIN_ENVIRONMENTS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment-id", action="append", help="Experiment id to run. Pass multiple times to run several.")
    parser.add_argument(
        "--level",
        action="append",
        choices=["low_context", "medium_context", "high_context"],
        help="Prompt level(s) to run. Defaults to all.",
    )
    parser.add_argument(
        "--environment",
        action="append",
        choices=sorted(BUILTIN_ENVIRONMENTS),
        help="Environment(s) to run. Defaults to `galaxy` for benchmark-aligned execution.",
    )
    parser.add_argument(
        "--agent",
        choices=sorted(BUILTIN_AGENTS),
        default="heuristic",
        help="Built-in harness agent adapter to use.",
    )
    parser.add_argument("--output-root", help="Optional output root. Defaults to outputs/.")
    parser.add_argument("--benchmark-id", default="galaxy_benchmark_workbench_run")
    parser.add_argument(
        "--report-output",
        help="Optional path to write an aggregated report for the generated run records.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    registry = BenchmarkRegistry(ROOT_DIR)
    tasks = registry.load_task_matrix(experiment_ids=args.experiment_id, levels=args.level)
    environments = [BUILTIN_ENVIRONMENTS[name]() for name in (args.environment or ["galaxy"])]
    workbench = BenchmarkWorkbench(ROOT_DIR)
    agent_cls = BUILTIN_AGENTS[args.agent]
    run_dirs = workbench.execute_matrix(
        tasks=tasks,
        environments=environments,
        agent_factory=agent_cls,
        output_root=args.output_root,
    )
    run_records = []
    for run_dir in run_dirs:
        payload = json.loads((run_dir / "results" / "run_record.json").read_text(encoding="utf-8"))
        run_records.append(payload)
    report = build_benchmark_report(args.benchmark_id, run_records)
    if args.report_output:
        Path(args.report_output).write_text(
            json.dumps(benchmark_report_as_dict(report), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    else:
        json.dump(benchmark_report_as_dict(report), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
