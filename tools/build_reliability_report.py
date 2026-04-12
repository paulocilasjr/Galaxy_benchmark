#!/usr/bin/env python3
"""Build a reliability and uncertainty report from benchmark run records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark.application.loaders import load_json
from galaxy_benchmark.application.publication import build_reliability_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--run-record",
        action="append",
        required=True,
        help="Path to a run_record.json file. Pass this argument multiple times.",
    )
    parser.add_argument(
        "--confidence",
        type=float,
        default=0.95,
        help="Confidence level used for the reported interval summaries.",
    )
    parser.add_argument("--output", help="Optional output path. Defaults to stdout.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    run_records = [load_json(path) for path in args.run_record]
    payload = build_reliability_report(run_records, confidence=args.confidence)
    if args.output:
        Path(args.output).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
