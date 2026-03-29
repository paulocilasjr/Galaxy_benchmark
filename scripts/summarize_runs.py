#!/usr/bin/env python3
"""Summarize immutable benchmark runs from the local filesystem."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    runs_dir = root / "runs"
    manifests = sorted(runs_dir.glob("*/manifest.json"))
    statuses: Counter[str] = Counter()
    for manifest_path in manifests:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        statuses.update([payload.get("status", "unknown")])

    summary = {
        "run_count": len(manifests),
        "status_counts": dict(sorted(statuses.items())),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
