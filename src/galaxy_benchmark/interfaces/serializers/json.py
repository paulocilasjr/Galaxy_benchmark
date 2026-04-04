"""JSON serialization helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def dump_json(path: str | Path, payload: Any) -> Path:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return file_path
