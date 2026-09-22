"""Fetch only archive indexes and small aggregate metadata, never agent code execution."""
import getpass
import json
from pathlib import Path
import ssl
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis_execution"))
from collect import Client, digest, redact_bytes, utc, write_json


def main():
    client = Client(hf_token=getpass.getpass("HF token: "))
    # Retain certificate chain and hostname checks with this host's proxy CA.
    client.ssl_context.verify_flags &= ~ssl.VERIFY_X509_STRICT
    base = "https://huggingface.co"
    repo = "goeckslab/galaxy-agent-benchmark-run-traces"
    dest = ROOT / "CompBio/source_snapshots/aggregate_metadata"
    manifest_path = dest / "manifest.json"
    records = json.loads(manifest_path.read_text())["sources"] if manifest_path.exists() else []
    prefixes = ["", "compbiobench", "compbiobench/replicates"]
    if "--details" in sys.argv:
        prefixes = [x["path"] for name in ("compbiobench_index.json", "compbiobench_replicates_index.json")
                    for x in json.loads((dest / name).read_text()) if x["type"] == "directory" and x["path"] != "compbiobench/replicates"]
    def capture(prefix):
        local_records = []
        url = f"{base}/api/datasets/{repo}/tree/main/{prefix}?recursive=false&limit=1000"
        raw, _ = client.get(url, service="hf")
        listing = json.loads(raw)
        path = dest / ((prefix.replace("/", "_") or "root") + "_index.json")
        write_json(path, listing)
        local_records.append(dict(url=url, path=str(path.relative_to(ROOT / "CompBio")), sha256=digest(path.read_bytes()), retrieved_at=utc()))
        print(prefix or "root", [(x["path"], x.get("size")) for x in listing if x["type"] == "file"], flush=True)
        for entry in listing:
            if entry["type"] != "file" or entry.get("size", 0) > 5_000_000:
                continue
            name = Path(entry["path"]).name
            if not (name.lower().endswith((".md", ".tsv", ".csv", ".json"))):
                continue
            if any(s in name.lower() for s in ("answer", "ground_truth", "reference")):
                continue
            url = f"{base}/datasets/{repo}/resolve/main/{urllib.parse.quote(entry['path'], safe='/')}"
            raw, _ = client.get(url, service="hf")
            retained, scopes = redact_bytes(raw, name)
            path = dest / entry["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(retained)
            local_records.append(dict(url=url, path=str(path.relative_to(ROOT / "CompBio")), sha256=digest(retained), original_sha256=digest(raw), redactions=scopes, retrieved_at=utc()))
            if name.lower().endswith(".md"):
                print(retained.decode()[:6000], flush=True)
        return local_records
    with ThreadPoolExecutor(max_workers=6) as pool:
        for result in pool.map(capture, prefixes):
            records.extend(result)
    write_json(manifest_path, {"sources": list({r['path']: r for r in records}.values()), "tls": "Chain and hostname verified; strict CA extension validation disabled for host proxy", "scope": "Archive listings and aggregate metadata only"})


if __name__ == "__main__":
    main()
