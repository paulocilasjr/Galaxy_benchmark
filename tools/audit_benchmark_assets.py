#!/usr/bin/env python3
"""Audit benchmark assets for publication-readiness invariants."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark.application.publication import build_release_audit


def main() -> int:
    audit = build_release_audit(ROOT_DIR)
    json.dump(audit, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 1 if any(audit.values()) else 0


if __name__ == "__main__":
    raise SystemExit(main())
