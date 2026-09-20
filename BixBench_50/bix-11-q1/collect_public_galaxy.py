"""Read-only snapshot of the user-linked public Galaxy histories.

Auditor collection only. This script does not submit jobs, inspect hidden reference
material, or execute recovered agent code.
"""
import json
import pathlib
import time
import subprocess
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
BASE = "https://usegalaxy.org/api"
HISTORIES = {
    "gpt55_r1": "bbd44e69cb8906b53984913a9d1111db",
    "gpt55_r2": "bbd44e69cb8906b52cbee1de5593c668",
    "gpt55_r3": "bbd44e69cb8906b5cfafcf561b38e52c",
    "sol_r1": "bbd44e69cb8906b5bd37f3d1f61d3ada",
    "sol_r2_r3": "bbd44e69cb8906b52eb32af3987ce2d2",
    "luna_r1": "bbd44e69cb8906b5edac1453b5609148",
    "luna_r2": "bbd44e69cb8906b59245f6758530c259",
    "luna_r3": "bbd44e69cb8906b5e9a55805a62dfa76",
    "deepseek_r1": "bbd44e69cb8906b53f1ca9589c9ae943",
    "deepseek_r2": "bbd44e69cb8906b52f53fd9503758da2",
    "deepseek_r3": "bbd44e69cb8906b5cfe4f129b06ae828",
}


def get_json(url):
    for attempt in range(3):
        try:
            response = subprocess.run(["curl", "-ksS", "--fail", "--retry", "3", "--retry-all-errors", "--retry-delay", "1", "--max-time", "20", url], capture_output=True, check=True, timeout=100)
            return json.loads(response.stdout)
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 * (attempt + 1))


def save_json(path, obj):
    def redact(value):
        if isinstance(value, dict):
            return {k: ("[redacted]" if k in {"user_email", "user_id", "username", "username_and_slug"} else redact(v)) for k, v in value.items()}
        if isinstance(value, list):
            return [redact(v) for v in value]
        return value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(redact(obj), indent=2, ensure_ascii=False) + "\n")


def main():
    import os
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if not any(line.startswith("GALAXY_API_KEY=") and line.split("=", 1)[1].strip().strip('"\'') for line in (ROOT.parents[1] / ".env").read_text().splitlines()):
        raise RuntimeError("Repository Galaxy credential gate is not met")
    out = ROOT / "source_snapshots" / "galaxy"
    out.mkdir(parents=True, exist_ok=True)
    log = {"retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "server": "https://usegalaxy.org", "request_options": "contents?details=all; jobs?full=true", "histories": {}}
    for label, hid in HISTORIES.items():
        print(label, hid, flush=True)
        folder = out / label
        folder.mkdir(exist_ok=True)
        if label == "luna_r2":
            try:
                h = json.loads((folder / "history.json").read_text()) if (folder / "history.json").exists() else get_json(f"{BASE}/histories/{hid}")
                save_json(folder / "history.json", h)
                log["histories"][label] = {"history_id": hid, "reported_content_count": h.get("count"), "content_fetch_error": "Unpaginated and 5-item paginated contents requests timed out; 8801 reported contents"}
            except Exception as exc:
                log["histories"][label] = {"history_id": hid, "fetch_error": str(exc)}
            save_json(out / "retrieval_manifest.json", log)
            continue
        try:
            h = json.loads((folder / "history.json").read_text()) if (folder / "history.json").exists() else get_json(f"{BASE}/histories/{hid}")
            contents = json.loads((folder / "contents.json").read_text()) if (folder / "contents.json").exists() else get_json(f"{BASE}/histories/{hid}/contents?details=all")
        except Exception as exc:
            log["histories"][label] = {"history_id": hid, "fetch_error": str(exc)}
            save_json(out / "retrieval_manifest.json", log)
            continue
        save_json(folder / "history.json", h)
        save_json(folder / "contents.json", contents)
        jobs = sorted({d.get("creating_job") for d in contents if d.get("creating_job")})
        errors = {}
        with ThreadPoolExecutor(max_workers=6) as pool:
            futs = {pool.submit(get_json, f"{BASE}/jobs/{jid}?full=true"): jid for jid in jobs if not (folder / "jobs" / f"{jid}.json").exists()}
            for future in as_completed(futs):
                jid = futs[future]
                try:
                    save_json(folder / "jobs" / f"{jid}.json", future.result())
                except Exception as exc:
                    errors[jid] = str(exc)
        log["histories"][label] = {"history_id": hid, "content_count": len(contents), "distinct_creating_jobs": len(jobs), "job_fetch_errors": errors}
        save_json(out / "retrieval_manifest.json", log)
    save_json(out / "retrieval_manifest.json", log)


if __name__ == "__main__":
    main()
