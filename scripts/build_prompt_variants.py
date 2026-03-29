#!/usr/bin/env python3
"""Generate deterministic prompt variants grouped by tier."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / "src"))

    from galaxy_benchmark.interfaces.cli.app import generate_prompts

    generate_prompts(
        task_dir=root / "benchmark" / "tasks" / "legacy" / "canonical",
        output_dir=root / "benchmark" / "prompts",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
