#!/usr/bin/env python3
"""Build the publication-facing benchmark results bundle and summary artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark import __version__
from galaxy_benchmark.application.publication import (
    PUBLICATION_RESULTS_PATH,
    PUBLICATION_RESULTS_SUMMARY_PATH,
    build_publication_results_bundle,
    build_publication_results_markdown,
    collect_scored_run_snapshots,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", action="append", help="Run directory to include. Defaults to checked-in outputs/ runs.")
    parser.add_argument(
        "--release-stage",
        default="public_release_candidate",
        choices=["public_release_candidate", "published"],
        help="Release stage label to embed in the bundle.",
    )
    parser.add_argument(
        "--json-output",
        default=str(ROOT_DIR / PUBLICATION_RESULTS_PATH),
        help="Path to write the JSON publication bundle.",
    )
    parser.add_argument(
        "--markdown-output",
        default=str(ROOT_DIR / PUBLICATION_RESULTS_SUMMARY_PATH),
        help="Path to write the Markdown publication summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    scored_runs = collect_scored_run_snapshots(ROOT_DIR, run_dirs=args.run_dir)
    bundle = build_publication_results_bundle(
        ROOT_DIR,
        benchmark_version=__version__,
        release_stage=args.release_stage,
        scored_runs=scored_runs,
    )
    json_output = Path(args.json_output)
    markdown_output = Path(args.markdown_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(build_publication_results_markdown(bundle) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
