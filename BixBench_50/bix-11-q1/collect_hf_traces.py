"""Inventory and collect user-authorized Hugging Face run traces.

Reads a token interactively without echo. Never saves the token or request headers.
Does not execute recovered agent code or open hidden answer references.
"""
import getpass
import hashlib
import json
import pathlib
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "source_snapshots" / "huggingface_traces"
REPO = "goeckslab/galaxy-agent-benchmark-run-traces"
ROOTS = {
    "gpt55": "run_traces_tokens_cut_jul14",
    "sol": "run_traces_july31_codex_gpt56_sol",
    "luna": "run_traces_july31_codex_gpt56_luna",
    "deepseek": "run_traces_august15_codex_deepseek_v4pro",
}


def request(url, token):
    for attempt in range(4):
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + token, "User-Agent": "Galaxy-benchmark-retrospective-audit/1"})
        try:
            with urllib.request.urlopen(req, context=ssl._create_unverified_context(), timeout=60) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code in (401, 403, 404):
                raise
            if attempt == 3:
                raise
        except Exception:
            if attempt == 3:
                raise
        time.sleep(2 * (attempt + 1))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "inventory"
    condition = sys.argv[2] if len(sys.argv) > 2 else "code"
    if mode not in {"inventory", "download"}:
        raise SystemExit("mode must be inventory or download")
    if condition not in {"code", "galaxy"}:
        raise SystemExit("condition must be code or galaxy")
    token = getpass.getpass("HF token: ")
    if not token:
        raise SystemExit("empty token")
    manifest = {"retrieved_at_utc": datetime.now(timezone.utc).isoformat(), "repository": REPO, "mode": mode, "condition": condition, "runs": {}, "token_saved": False}
    manifest_path = OUT / ("manifest_galaxy.json" if condition == "galaxy" else "manifest.json")
    for model, run_root in ROOTS.items():
        for rep in (1, 2, 3):
            label = f"{model}_r{rep}" if condition == "code" else f"galaxy_{model}_r{rep}"
            branch = "anycode_nongalaxy_skills" if condition == "code" else "galaxy_strict_skills"
            prefix = f"bixbench/{run_root}/bix_11_q1/{branch}/replicate_{rep}"
            url = f"https://huggingface.co/api/datasets/{REPO}/tree/main/{urllib.parse.quote(prefix, safe='/')}?recursive=true"
            try:
                entries = json.loads(request(url, token))
            except Exception as exc:
                manifest["runs"][label] = {"prefix": prefix, "error_type": type(exc).__name__, "http_status": getattr(exc, "code", None)}
                print(label, "listing failed", type(exc).__name__, getattr(exc, "code", None), flush=True)
                continue
            if not isinstance(entries, list):
                manifest["runs"][label] = {"prefix": prefix, "error": "unexpected listing format"}
                continue
            index_path = OUT / "indexes" / f"{label}.json"
            write_json(index_path, entries)
            files = [e for e in entries if e.get("type") == "file"]
            manifest["runs"][label] = {"prefix": prefix, "index_path": str(index_path.relative_to(ROOT)), "file_count": len(files), "total_reported_bytes": sum(e.get("size") or 0 for e in files), "files": []}
            print(label, len(files), "files", flush=True)
            if mode == "inventory":
                continue
            for entry in files:
                path = entry["path"]
                size = entry.get("size")
                item = {"path": path, "reported_size": size, "downloaded": False}
                # The audit retains logs/results; very large input artifacts are linked.
                if size is not None and size > 10_000_000:
                    item["reason"] = "larger than 10 MB; source link retained"
                    manifest["runs"][label]["files"].append(item)
                    continue
                rel = pathlib.PurePosixPath(path).relative_to(prefix)
                local = OUT / "files" / label / pathlib.Path(*rel.parts)
                local.parent.mkdir(parents=True, exist_ok=True)
                if local.exists() and (size is None or local.stat().st_size == size):
                    data = local.read_bytes()
                else:
                    raw = f"https://huggingface.co/datasets/{REPO}/resolve/main/{urllib.parse.quote(path, safe='/')}"
                    try:
                        data = request(raw, token)
                        local.write_bytes(data)
                    except Exception as exc:
                        item["error_type"] = type(exc).__name__
                        item["http_status"] = getattr(exc, "code", None)
                        manifest["runs"][label]["files"].append(item)
                        continue
                item.update({"downloaded": True, "local_path": str(local.relative_to(ROOT)), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
                manifest["runs"][label]["files"].append(item)
            write_json(manifest_path, manifest)
    write_json(manifest_path, manifest)


if __name__ == "__main__":
    main()
