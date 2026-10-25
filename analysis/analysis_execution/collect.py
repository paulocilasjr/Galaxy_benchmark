"""Read-only source capture for a spreadsheet-described retrospective audit."""
from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import ssl
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from workbook import RunLink, galaxy_history_id, huggingface_source


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def write_source_manifest(path: Path, value) -> None:
    write_json(path, value)


SENSITIVE_KEYS = {"user_email", "user_id", "username", "username_and_slug"}
TEXT_REDACTIONS = [
    (re.compile(rb"hf_[A-Za-z0-9]{20,}"), b"[redacted-hf-token]"),
    (re.compile(rb"sk-[A-Za-z0-9_-]{20,}"), b"[redacted-api-key]"),
    (re.compile(rb"Bearer\s+[A-Za-z0-9._-]{20,}", re.I), b"Bearer [redacted]"),
    (re.compile(rb"GALAXY_API_KEY\s*[=:]\s*[A-Za-z0-9._-]{20,}"), b"GALAXY_API_KEY=[redacted]"),
    (re.compile(rb"/Users/[^/\s\"']+"), b"/Users/[redacted]"),
    (re.compile(rb'("(?:user_email|user_id|username|username_and_slug)"\s*:\s*)"[^"\\]*(?:\\.[^"\\]*)*"'), rb'\1"[redacted]"'),
]


def redact_bytes(data: bytes, filename: str) -> tuple[bytes, list[str]]:
    compressed = filename.endswith(".gz")
    if filename.lower().endswith((".pdf", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".xlsx", ".xls", ".bam", ".h5", ".hdf5")) or data.startswith((b"%PDF-", b"\x89PNG", b"PK\x03\x04")):
        raise ValueError("binary_or_unsupported_encoding")
    try:
        plain = gzip.decompress(data) if compressed else data
        if b"\x00" in plain:
            raise UnicodeDecodeError("utf-8", plain, plain.index(b"\x00"), plain.index(b"\x00") + 1, "NUL byte")
        plain.decode("utf-8")
    except (UnicodeDecodeError, OSError):
        # Unknown binary evidence is not retained: it might conceal credentials.
        raise ValueError("binary_or_unsupported_encoding")
    scopes = []
    for regex, replacement in TEXT_REDACTIONS:
        plain, count = regex.subn(replacement, plain)
        if count:
            scopes.append(regex.pattern.decode("ascii")[:48] + f":{count}")
    return (gzip.compress(plain, mtime=0) if compressed and scopes else plain if not compressed else data), scopes


def redact_json(value):
    if isinstance(value, dict):
        return {k: ("[redacted]" if k in SENSITIVE_KEYS else redact_json(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact_json(v) for v in value]
    if isinstance(value, str):
        return redact_bytes(value.encode(), ".txt")[0].decode()
    return value


class Client:
    def __init__(self, *, hf_token: str | None = None, galaxy_key: str | None = None, timeout: int = 35, insecure_tls: bool = False, galaxy_requests_per_second: float = 5.0):
        self.hf_token = hf_token
        self.galaxy_key = galaxy_key
        self.timeout = timeout
        self.insecure_tls = insecure_tls
        self.ssl_context = ssl._create_unverified_context() if insecure_tls else ssl.create_default_context()
        self._galaxy_interval = 1.0 / galaxy_requests_per_second
        self._galaxy_lock = threading.Lock()
        self._galaxy_next_at = 0.0

    def get(self, url: str, *, service: str) -> tuple[bytes, dict[str, str]]:
        host = urllib.parse.urlparse(url).hostname
        if not url.startswith("https://") or (service == "hf" and host != "huggingface.co") or (service == "galaxy" and host != "usegalaxy.org"):
            raise ValueError("Source request outside the allowlisted HTTPS host")
        headers = {"User-Agent": "Galaxy-benchmark-retrospective-audit/2"}
        if service == "hf" and self.hf_token:
            headers["Authorization"] = "Bearer " + self.hf_token
        if service == "galaxy" and self.galaxy_key:
            headers["x-api-key"] = self.galaxy_key
        last = None
        class NoCrossHostCredentialRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, req, fp, code, msg, redirect_headers, newurl):
                if urllib.parse.urlparse(newurl).scheme != "https":
                    raise ValueError("Refusing non-HTTPS source redirect")
                redirected = super().redirect_request(req, fp, code, msg, redirect_headers, newurl)
                if redirected and urllib.parse.urlparse(newurl).hostname != urllib.parse.urlparse(req.full_url).hostname:
                    for name in ("Authorization", "X-api-key", "x-api-key"):
                        redirected.headers.pop(name, None)
                        redirected.unredirected_hdrs.pop(name, None)
                return redirected
        opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=self.ssl_context), NoCrossHostCredentialRedirect())
        for attempt in range(5):
            try:
                if service == "galaxy":
                    with self._galaxy_lock:
                        now = time.monotonic()
                        scheduled = max(now, self._galaxy_next_at)
                        self._galaxy_next_at = scheduled + self._galaxy_interval
                    if scheduled > now:
                        time.sleep(scheduled - now)
                req = urllib.request.Request(url, headers=headers)
                with opener.open(req, timeout=self.timeout) as response:
                    return response.read(), dict(response.headers.items())
            except urllib.error.HTTPError as exc:
                last = exc
                if exc.code in {400, 401, 403, 404}:
                    break
                if exc.code == 429:
                    retry_after = exc.headers.get("Retry-After")
                    try:
                        delay = min(30.0, float(retry_after)) if retry_after else min(30.0, 2.0 * (attempt + 1))
                    except ValueError:
                        delay = min(30.0, 2.0 * (attempt + 1))
                    time.sleep(delay)
            except (urllib.error.URLError, TimeoutError) as exc:
                last = exc
            if attempt < 4:
                time.sleep(1 + attempt * 2)
        raise last


def _safe_relative(path: str, prefix: str) -> Path:
    if not path.startswith(prefix + "/"):
        raise ValueError(f"Source path is outside requested prefix: {path}")
    rel = path[len(prefix):].lstrip("/")
    parts = Path(rel).parts
    if not rel or any(p in {"", ".", ".."} for p in parts):
        raise ValueError(f"Unsafe source path: {path}")
    return Path(*parts)


def _hf_listing(client: Client, repo: str, revision: str, prefix: str) -> list[dict]:
    api = f"https://huggingface.co/api/datasets/{repo}/tree/{urllib.parse.quote(revision, safe='')}/{urllib.parse.quote(prefix, safe='/')}?recursive=true&limit=1000"
    entries = []
    seen = set()
    while api:
        if api in seen:
            raise RuntimeError("Hugging Face pagination cycle")
        seen.add(api)
        raw, headers = client.get(api, service="hf")
        page = json.loads(raw)
        if not isinstance(page, list):
            raise ValueError("Unexpected Hugging Face listing format")
        entries.extend(page)
        next_url = None
        for part in headers.get("Link", "").split(","):
            if 'rel="next"' in part:
                next_url = part.split("<", 1)[1].split(">", 1)[0]
                if urllib.parse.urlparse(next_url).hostname != "huggingface.co":
                    raise ValueError("Hugging Face pagination link points outside allowlisted host")
        api = next_url
    return entries


def collect_trace(client: Client, run: RunLink, output: Path, *, max_bytes: int = 10_000_000) -> dict:
    repo, revision, prefix = huggingface_source(run.trace_url)
    root = output / "source_snapshots/huggingface_traces"
    folder = root / "files" / run.run_id
    listing_path = root / "indexes" / f"{run.run_id}.json"
    result = {"source_url": run.trace_url, "repository": repo, "revision": revision, "prefix": prefix,
              "retrieved_at_utc": utc(), "status": "not_collected", "files": [],
              "tls_certificate_verified": not getattr(client, "insecure_tls", False),
              "index_path": str(listing_path.relative_to(output)), "error": None}
    prior = json.loads((root / "manifests" / f"{run.run_id}.json").read_text()) if (root / "manifests" / f"{run.run_id}.json").exists() else {}
    prior_files = {x.get("remote_path"): x for x in prior.get("files", [])}
    try:
        listing = _hf_listing(client, repo, revision, prefix)
        write_source_manifest(listing_path, listing)
        for entry in listing:
            if entry.get("type") != "file":
                continue
            remote = entry["path"]
            relative = _safe_relative(remote, prefix)
            item = {"remote_path": remote, "reported_size": entry.get("size"), "status": "not_collected"}
            if entry.get("size") is not None and entry["size"] > max_bytes:
                item["status"] = "linked_large_file"
            else:
                destination = folder / relative
                old = prior_files.get(remote, {})
                if old.get("status") == "retained" and destination.exists() and digest(destination.read_bytes()) == old.get("retained_sha256"):
                    result["files"].append(old)
                    continue
                raw_url = f"https://huggingface.co/datasets/{repo}/resolve/{urllib.parse.quote(revision, safe='')}/{urllib.parse.quote(remote, safe='/')}"
                try:
                    raw, _ = client.get(raw_url, service="hf")
                    if len(raw) > max_bytes:
                        item["status"] = "linked_large_file"
                    else:
                        retained, redactions = redact_bytes(raw, destination.name)
                        destination.parent.mkdir(parents=True, exist_ok=True)
                        destination.write_bytes(retained)
                        item.update({"status": "retained", "local_path": str(destination.relative_to(output)),
                                     "original_sha256": digest(raw), "original_bytes": len(raw),
                                     "reported_size_matches_download": entry.get("size") in (None, len(raw)),
                                     "retained_sha256": digest(retained), "retained_bytes": len(retained),
                                     "redactions": redactions})
                except Exception as exc:
                    item.update({"status": "unavailable", "error_type": type(exc).__name__, "http_status": getattr(exc, "code", None)})
            result["files"].append(item)
        result["status"] = "retrieved" if result["files"] and all(x["status"] in {"retained", "linked_large_file"} for x in result["files"]) else "partial"
    except Exception as exc:
        result.update({"status": "unavailable", "error": type(exc).__name__, "http_status": getattr(exc, "code", None)})
    write_source_manifest(root / "manifests" / f"{run.run_id}.json", result)
    return result


def _galaxy_json(client: Client, url: str):
    raw, _ = client.get(url, service="galaxy")
    return redact_json(json.loads(raw))


def _contents(client: Client, base: str, history_id: str, reported_count: int | None = None, max_contents: int = 300) -> list[dict]:
    # Avoid enormous responses; never interpret a retrieval limit as zero datasets.
    url = f"{base}/histories/{history_id}/contents?details=all"
    if isinstance(reported_count, int) and reported_count > max_contents:
        raise RuntimeError(f"History has {reported_count} contents, above configured limit {max_contents}; detailed public export deferred")
    if reported_count is None or reported_count <= 300:
        try:
            result = _galaxy_json(client, url)
            if isinstance(result, list):
                return result
        except Exception:
            pass
    for limit in (200, 50):
        out = []
        seen_pages = set()
        try:
            for offset in range(0, 3001, limit):
                page = _galaxy_json(client, f"{url}&limit={limit}&offset={offset}")
                if not isinstance(page, list):
                    raise ValueError("Unexpected Galaxy contents page")
                signature = tuple(d.get("id") for d in page)
                if signature in seen_pages:
                    raise RuntimeError("Galaxy contents pagination repeated a page")
                seen_pages.add(signature)
                out.extend(page)
                if len(page) < limit:
                    return out
        except Exception:
            continue
    raise RuntimeError("Galaxy contents pagination unavailable or exceeded 3,000 records")


def collect_galaxy(client: Client, run: RunLink, output: Path, *, max_output_bytes: int = 100_000, max_contents: int = 300) -> dict:
    hid = galaxy_history_id(run.galaxy_url)
    base = "https://usegalaxy.org/api"
    folder = output / "source_snapshots/galaxy" / hid
    result = {"history_id": hid, "source_url": run.galaxy_url, "retrieved_at_utc": utc(),
              "tls_certificate_verified": not getattr(client, "insecure_tls", False),
              "status": "not_collected", "history_path": None, "contents_path": None,
              "jobs": [], "outputs": [], "skipped_outputs": [], "errors": [], "max_contents": max_contents, "contents_limit_applied": False}
    try:
        history = json.loads((folder / "history.json").read_text()) if (folder / "history.json").exists() else _galaxy_json(client, f"{base}/histories/{hid}")
        if not (folder / "history.json").exists():
            write_json(folder / "history.json", history)
        result["history_path"] = str((folder / "history.json").relative_to(output))
        result["reported_content_count"] = history.get("count")
    except Exception as exc:
        result["errors"].append({"stage": "history", "type": type(exc).__name__, "http_status": getattr(exc, "code", None)})
        result["status"] = "unavailable"
        write_source_manifest(folder / "manifest.json", result)
        return result
    try:
        contents = json.loads((folder / "contents.json").read_text()) if (folder / "contents.json").exists() else _contents(client, base, hid, history.get("count"), max_contents)
        if not (folder / "contents.json").exists():
            write_json(folder / "contents.json", contents)
        result["contents_path"] = str((folder / "contents.json").relative_to(output))
        result["content_count"] = len(contents)
    except Exception as exc:
        result["contents_limit_applied"] = isinstance(history.get("count"), int) and history["count"] > max_contents
        result["errors"].append({"stage": "contents", "type": type(exc).__name__, "http_status": getattr(exc, "code", None), "message": str(exc)[:200]})
        result["status"] = "history_metadata_only"
        write_source_manifest(folder / "manifest.json", result)
        return result
    def fetch_job(job_id):
        path = folder / "jobs" / f"{job_id}.json"
        if not path.exists():
            job = _galaxy_json(client, f"{base}/jobs/{job_id}?full=true")
            write_json(path, job)
        return {"id": job_id, "path": str(path.relative_to(output)), "sha256": digest(path.read_bytes())}
    job_ids = sorted({d.get("creating_job") for d in contents if d.get("creating_job")})
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_job, jid): jid for jid in job_ids}
        for future in as_completed(futures):
            try:
                result["jobs"].append(future.result())
            except Exception as exc:
                result["errors"].append({"stage": "job", "id": futures[future], "type": type(exc).__name__, "http_status": getattr(exc, "code", None)})
    result["jobs"].sort(key=lambda x: x["id"])
    for d in contents:
        if d.get("history_content_type") != "dataset" or not d.get("accessible") or d.get("purged"):
            continue
        if not d.get("creating_job") or d.get("file_size") is None or d["file_size"] > max_output_bytes:
            continue
        if not d.get("download_url") or d.get("state") != "ok":
            continue
        job_path = folder / "jobs" / f"{d['creating_job']}.json"
        if not job_path.exists():
            continue
        job = json.loads(job_path.read_text())
        if job.get("tool_id") == "__DATA_FETCH__":
            continue
        try:
            url = urllib.parse.urljoin("https://usegalaxy.org", d["download_url"])
            if urllib.parse.urlparse(url).hostname != "usegalaxy.org":
                raise ValueError("Galaxy output URL points outside allowlisted host")
            path = output / "selected_outputs/galaxy" / hid / f"{d['id']}.dat"
            prior = json.loads((folder / "manifest.json").read_text()) if (folder / "manifest.json").exists() else {}
            old = next((x for x in prior.get("outputs", []) if x.get("hda_id") == d["id"]), None)
            if old and path.exists() and digest(path.read_bytes()) == old.get("retained_sha256"):
                result["outputs"].append(old)
                continue
            data, _ = client.get(url, service="galaxy")
            if len(data) > max_output_bytes:
                continue
            kept, redactions = redact_bytes(data, d.get("name") or ".txt")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(kept)
            result["outputs"].append({"hda_id": d["id"], "path": str(path.relative_to(output)),
                                      "source_url": url, "reported_size": d["file_size"],
                                      "original_bytes": len(data), "original_sha256": digest(data),
                                      "reported_size_matches_download": d["file_size"] == len(data),
                                      "retained_bytes": len(kept), "retained_sha256": digest(kept), "redactions": redactions})
        except ValueError as exc:
            if str(exc) == "binary_or_unsupported_encoding":
                result["skipped_outputs"].append({"hda_id": d["id"], "reason": "binary_or_unsupported_encoding"})
            else:
                result["errors"].append({"stage": "output", "id": d["id"], "type": type(exc).__name__})
        except Exception as exc:
            result["errors"].append({"stage": "output", "id": d["id"], "type": type(exc).__name__})
    result["status"] = "retrieved" if not result["errors"] else "partial"
    write_source_manifest(folder / "manifest.json", result)
    return result


def galaxy_credential_gate(repo_root: Path) -> str:
    """Honor SKILL.md's gate before even read-only Galaxy API requests."""
    configured = os.environ.get("GALAXY_API_KEY", "").strip()
    if configured:
        return configured
    env_path = repo_root / ".env"
    if not env_path.exists():
        raise RuntimeError("Galaxy credential gate: repository .env is missing")
    for line in env_path.read_text().splitlines():
        if line.startswith("GALAXY_API_KEY="):
            value = line.partition("=")[2].strip().strip('"\'')
            if value:
                return value
    raise RuntimeError("Galaxy credential gate: GALAXY_API_KEY is empty or missing")
