"""Preserve small analytical outputs from already-snapshotted public histories."""
import hashlib
import json
import pathlib
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = pathlib.Path(__file__).resolve().parent
SNAP = ROOT / "source_snapshots" / "galaxy"
OUT = ROOT / "selected_outputs" / "galaxy"


def fetch(label, d):
    url = "https://usegalaxy.org" + d["download_url"]
    result = subprocess.run(["curl", "-ksS", "--fail", "--retry", "3", "--retry-all-errors", "--retry-delay", "1", "--max-time", "20", url], capture_output=True, timeout=100)
    result.check_returncode()
    data = result.stdout
    dest = OUT / label / f"hid_{d['hid']}_{d['id']}.dat"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return {"history_label": label, "hid": d["hid"], "hda_id": d["id"], "path": str(dest.relative_to(ROOT)), "source_url": url, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "expected_file_size": d.get("file_size")}


def main():
    todo = []
    for folder in sorted(SNAP.iterdir()):
        if not folder.is_dir() or not (folder / "contents.json").exists():
            continue
        for d in json.loads((folder / "contents.json").read_text()):
            if d.get("history_content_type") == "dataset" and d.get("hid", 0) > 20 and d.get("file_size", 0) <= 100000 and d.get("accessible") and not d.get("purged"):
                todo.append((folder.name, d))
    results, errors = [], []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch, label, d): (label, d["id"]) for label, d in todo}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as exc:
                errors.append({"label": futures[future][0], "hda_id": futures[future][1], "error": str(exc)})
    (OUT / "manifest.json").write_text(json.dumps({"outputs": sorted(results, key=lambda x: (x["history_label"], x["hid"])), "errors": errors}, indent=2) + "\n")
    print(len(results), "outputs preserved;", len(errors), "errors")


if __name__ == "__main__":
    main()
