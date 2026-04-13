#!/usr/bin/env python3
"""Stage publication release packages for blind public use, publication companion docs, and hidden scoring."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark.application.publication import build_release_packages


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where the staged release packages should be created.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = build_release_packages(ROOT_DIR, Path(args.output_dir))
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
