#!/usr/bin/env python3
"""Aggregate run records into a benchmark report."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark.application.loaders import dump_json, load_run_record
from galaxy_benchmark.application.reporting import benchmark_report_as_dict, build_benchmark_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark-id", required=True, help="Identifier for the generated benchmark report.")
    parser.add_argument(
        "--run-record",
        action="append",
        required=True,
        help="Path to a run record JSON file. Pass this flag multiple times.",
    )
    parser.add_argument(
        "--output",
        help="Where to write the report JSON. Defaults to stdout only when omitted.",
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.70,
        help="Threshold used for user-level confidence aggregation.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_records = [load_run_record(path) for path in args.run_record]
    report = build_benchmark_report(
        args.benchmark_id,
        [asdict(record) for record in run_records],
        confidence_threshold=args.confidence_threshold,
    )
    payload = benchmark_report_as_dict(report)
    if args.output:
        dump_json(payload, args.output)
    else:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
