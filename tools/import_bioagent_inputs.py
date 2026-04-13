#!/usr/bin/env python3
"""Import BioAgent Bench task inputs into this repository."""

from __future__ import annotations

import json
import shutil
import tarfile
import urllib.request
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
METADATA_URL = "https://raw.githubusercontent.com/bioagent-bench/bioagent-bench/master/src/task_metadata.json"
OUTPUT_ROOT = ROOT_DIR / "dataset" / "bioagent_inputs"


def download_to(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=3600) as response, destination.open("wb") as handle:
        shutil.copyfileobj(response, handle)


def maybe_extract(archive_path: Path) -> None:
    if not tarfile.is_tarfile(archive_path):
        return
    extract_dir = archive_path.parent / archive_path.name.replace(".tar.gz", "").replace(".tgz", "").replace(".tar", "")
    extract_dir.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "r:*") as tar:
        tar.extractall(extract_dir)


def main() -> int:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    metadata = json.load(urllib.request.urlopen(METADATA_URL))
    for task in metadata:
        task_dir = OUTPUT_ROOT / task["task_id"]
        data_dir = task_dir / "data"
        ref_dir = task_dir / "reference"
        data_dir.mkdir(parents=True, exist_ok=True)
        ref_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "source_manifest.json").write_text(json.dumps(task, indent=2) + "\n", encoding="utf-8")
        for category, subdir in (("data", data_dir), ("reference_data", ref_dir)):
            for item in task["download_urls"].get(category, []):
                destination = subdir / item["filename"]
                if destination.exists():
                    continue
                print(f"Downloading {task['task_id']} {category} {item['filename']}")
                download_to(item["url"], destination)
                maybe_extract(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
