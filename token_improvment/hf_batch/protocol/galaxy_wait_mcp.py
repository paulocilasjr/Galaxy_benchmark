#!/usr/bin/env python3
"""Minimal MCP server that waits for Galaxy jobs outside the model loop."""

from __future__ import annotations

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


SUCCESS_STATES = frozenset({"ok"})
FAILURE_STATES = frozenset(
    {
        "cancelled",
        "deleted",
        "deleted_new",
        "error",
        "failed",
        "paused",
        "stopped",
    }
)
TERMINAL_STATES = SUCCESS_STATES | FAILURE_STATES
JOB_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,256}$")
MAX_JOB_IDS = 30
MAX_POLL_INTERVAL_SECONDS = 60.0
MAX_FAILURE_TEXT_CHARS = 2000


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, value: Any) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")


def _redact(value: Any, secrets: Sequence[str]) -> Any:
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            if secret:
                redacted = redacted.replace(secret, "[REDACTED_GALAXY_API_KEY]")
        return redacted
    if isinstance(value, Mapping):
        return {str(key): _redact(item, secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item, secrets) for item in value]
    if isinstance(value, tuple):
        return [_redact(item, secrets) for item in value]
    return value


def _validated_job_ids(job_ids: Sequence[str]) -> list[str]:
    if not job_ids:
        raise ValueError("job_ids must contain at least one Galaxy job ID")
    if len(job_ids) > MAX_JOB_IDS:
        raise ValueError(f"job_ids may contain at most {MAX_JOB_IDS} IDs")

    validated: list[str] = []
    seen: set[str] = set()
    for raw_job_id in job_ids:
        job_id = str(raw_job_id)
        if not JOB_ID_PATTERN.fullmatch(job_id):
            raise ValueError(f"invalid Galaxy job ID: {job_id!r}")
        if job_id not in seen:
            validated.append(job_id)
            seen.add(job_id)
    return validated


def _resolve_evidence_directory(workspace_root: Path, requested: str) -> Path:
    relative = Path(requested)
    if relative.is_absolute() or not relative.parts:
        raise ValueError("evidence_directory must be a workspace-relative path")
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise ValueError("evidence_directory may not contain '.', '..', or empty parts")

    root = workspace_root.resolve()
    destination = (root / relative).resolve()
    if destination == root or root not in destination.parents:
        raise ValueError("evidence_directory must resolve below the workspace root")
    destination.mkdir(parents=True, exist_ok=True)
    return destination


def _next_evidence_directory(workspace_root: Path, base: str) -> str:
    if not (workspace_root / base).exists():
        return base
    for index in range(2, 10_000):
        candidate = f"{base}_{index:03d}"
        if not (workspace_root / candidate).exists():
            return candidate
    raise RuntimeError(f"No available evidence directory for {base}")


def _extract_dataset_refs(value: Any) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []

    def visit(item: Any) -> None:
        if isinstance(item, Mapping):
            object_id = item.get("id")
            src = item.get("src")
            if isinstance(object_id, str):
                ref = {"id": object_id}
                if isinstance(src, str):
                    ref["src"] = src
                if ref not in refs:
                    refs.append(ref)
            for nested in item.values():
                visit(nested)
        elif isinstance(item, (list, tuple)):
            for nested in item:
                visit(nested)

    visit(value)
    return refs


def _failure_text(detail: Mapping[str, Any], secrets: Sequence[str]) -> str | None:
    fragments: list[str] = []
    for key in (
        "info",
        "message",
        "error",
        "job_stderr",
        "tool_stderr",
        "stderr",
        "exit_code",
    ):
        value = detail.get(key)
        if value in (None, "", [], {}):
            continue
        text = str(_redact(value, secrets)).strip()
        if text:
            fragments.append(f"{key}: {text}")
    if not fragments:
        return None
    return " | ".join(fragments)[-MAX_FAILURE_TEXT_CHARS:]


def _bounded_failure_diagnostic(
    detail: Mapping[str, Any],
    secrets: Sequence[str],
) -> dict[str, Any]:
    """Return enough terminal context to choose the next action once."""

    command_rendered = bool(str(detail.get("command_line") or "").strip())
    state = str(detail.get("state") or "unknown").lower()
    combined = "\n".join(
        str(detail.get(key) or "")
        for key in ("job_stderr", "tool_stderr", "stderr", "info", "message")
    ).lower()
    if not command_rendered:
        phase = "pre_execution_or_command_rendering"
        next_check = (
            "No command line was returned. Inspect the job error messages, "
            "tool inputs, and parameters before resubmitting."
        )
    elif state in {"cancelled", "deleted", "deleted_new", "stopped"}:
        phase = "cancelled_or_deleted"
        next_check = "Confirm why the existing job was stopped before replacing it."
    elif any(token in combined for token in ("out of memory", "oom", "memoryerror")):
        phase = "resource_runtime"
        next_check = "Inspect the recorded resource request and job metrics."
    elif any(
        token in combined
        for token in ("modulenotfounderror", "no module named", "command not found")
    ):
        phase = "dependency_runtime"
        next_check = "Use a runtime-smoke-tested container that provides the missing dependency."
    else:
        phase = "command_runtime"
        next_check = "Use the bounded stderr and job messages to correct the executed command."

    diagnostic: dict[str, Any] = {
        "command_line_rendered": command_rendered,
        "phase": phase,
        "next_check": next_check,
    }
    if detail.get("exit_code") is not None:
        diagnostic["exit_code"] = detail["exit_code"]
    failure = _failure_text(detail, secrets)
    if failure:
        diagnostic["message"] = failure
    job_messages = detail.get("job_messages")
    if job_messages not in (None, "", [], {}):
        diagnostic["job_messages"] = str(_redact(job_messages, secrets))[
            -MAX_FAILURE_TEXT_CHARS:
        ]
    return _redact(diagnostic, secrets)


def _has_started(detail: Mapping[str, Any]) -> bool:
    state = str(detail.get("state") or "unknown").lower()
    if state in TERMINAL_STATES or state in {"running", "setting_metadata"}:
        return True
    return any(
        detail.get(key) not in (None, "", [], {})
        for key in (
            "destination_id",
            "external_id",
            "handler",
            "job_runner_external_id",
            "job_runner_name",
        )
    )


def _compact_job(
    job_id: str,
    detail: Mapping[str, Any] | None,
    secrets: Sequence[str],
) -> dict[str, Any]:
    detail = detail or {}
    state = str(detail.get("state") or "unknown").lower()
    compact: dict[str, Any] = {
        "id": job_id,
        "input_dataset_refs": _extract_dataset_refs(detail.get("inputs", {})),
        "state": state,
        "tool_id": detail.get("tool_id"),
        "output_dataset_refs": _extract_dataset_refs(detail.get("outputs", {})),
    }
    if state not in SUCCESS_STATES:
        compact["started"] = _has_started(detail)
        compact["command_line_rendered"] = bool(
            str(detail.get("command_line") or "").strip()
        )
    if state in FAILURE_STATES:
        compact["failure"] = _failure_text(detail, secrets)
        compact["failure_diagnostic"] = _bounded_failure_diagnostic(detail, secrets)
    return _redact(compact, secrets)


def wait_for_jobs(
    job_ids: Sequence[str],
    *,
    fetch_job: Callable[[str], Mapping[str, Any]],
    workspace_root: Path,
    evidence_directory: str = "run_trace/galaxy_wait",
    timeout_seconds: float | None = None,
    start_timeout_seconds: float | None = None,
    poll_interval_seconds: float = 10.0,
    secrets: Sequence[str] = (),
    monotonic: Callable[[], float] = time.monotonic,
    sleep: Callable[[float], None] = time.sleep,
    utc_now: Callable[[], str] = _utc_now,
) -> dict[str, Any]:
    """Wait for Galaxy jobs and return one compact terminal result."""

    validated_ids = _validated_job_ids(job_ids)
    if timeout_seconds is not None and timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero or null")
    if start_timeout_seconds is not None and start_timeout_seconds <= 0:
        raise ValueError("start_timeout_seconds must be greater than zero or null")
    if (
        timeout_seconds is not None
        and start_timeout_seconds is not None
        and start_timeout_seconds > timeout_seconds
    ):
        raise ValueError("start_timeout_seconds may not exceed timeout_seconds")
    if not 0.1 <= poll_interval_seconds <= MAX_POLL_INTERVAL_SECONDS:
        raise ValueError(
            "poll_interval_seconds must be between 0.1 and "
            f"{MAX_POLL_INTERVAL_SECONDS}"
        )

    evidence_path = _resolve_evidence_directory(workspace_root, evidence_directory)
    request_path = evidence_path / "request.json"
    events_path = evidence_path / "state_changes.jsonl"
    final_path = evidence_path / "final_jobs.json"
    summary_path = evidence_path / "summary.json"
    if events_path.exists():
        events_path.unlink()

    _write_json(
        request_path,
        {
            "job_ids": validated_ids,
            "poll_interval_seconds": poll_interval_seconds,
            "requested_at": utc_now(),
            "start_timeout_seconds": start_timeout_seconds,
            "timeout_seconds": timeout_seconds,
        },
    )

    started = monotonic()
    pending = set(validated_ids)
    started_jobs: set[str] = set()
    last_details: dict[str, Mapping[str, Any]] = {}
    last_observation: dict[str, tuple[str, str | None]] = {}
    start_timed_out: set[str] = set()
    timed_out = False

    while pending:
        fetch_results: dict[str, Mapping[str, Any] | Exception] = {}
        worker_count = min(len(pending), 8)
        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            futures = {executor.submit(fetch_job, job_id): job_id for job_id in pending}
            for future in as_completed(futures):
                job_id = futures[future]
                try:
                    detail = future.result()
                    if not isinstance(detail, Mapping):
                        raise TypeError("Galaxy job detail response is not an object")
                    fetch_results[job_id] = detail
                except Exception as exc:  # Preserve transient API failures as evidence.
                    fetch_results[job_id] = exc

        for job_id in validated_ids:
            if job_id not in pending:
                continue
            result = fetch_results[job_id]
            observed_at = utc_now()
            if isinstance(result, Exception):
                error_text = str(_redact(str(result), secrets))[-MAX_FAILURE_TEXT_CHARS:]
                observation = ("fetch_error", error_text)
                if last_observation.get(job_id) != observation:
                    _append_jsonl(
                        events_path,
                        {
                            "error": error_text,
                            "event": "fetch_error",
                            "job_id": job_id,
                            "observed_at": observed_at,
                        },
                    )
                    last_observation[job_id] = observation
                if getattr(result, "status_code", None) == 400:
                    raise ValueError(f"Galaxy rejected job ID {job_id}: {error_text}")
                continue

            redacted_detail = _redact(dict(result), secrets)
            state = str(redacted_detail.get("state") or "unknown").lower()
            observation = (state, None)
            last_details[job_id] = redacted_detail
            if _has_started(redacted_detail):
                started_jobs.add(job_id)
            if last_observation.get(job_id) != observation:
                _append_jsonl(
                    events_path,
                    {
                        "detail": redacted_detail,
                        "event": "state_change",
                        "job_id": job_id,
                        "observed_at": observed_at,
                        "state": state,
                    },
                )
                last_observation[job_id] = observation
            if state in TERMINAL_STATES:
                pending.remove(job_id)

        if not pending:
            break
        elapsed = monotonic() - started
        if timeout_seconds is not None and elapsed >= timeout_seconds:
            timed_out = True
            break
        if start_timeout_seconds is not None and elapsed >= start_timeout_seconds:
            start_timed_out = pending - started_jobs
            if start_timed_out:
                break
        sleep_seconds = poll_interval_seconds
        if timeout_seconds is not None:
            sleep_seconds = min(sleep_seconds, timeout_seconds - elapsed)
        if sleep_seconds > 0:
            sleep(sleep_seconds)

    elapsed_seconds = round(max(0.0, monotonic() - started), 3)
    final_details = {
        job_id: last_details.get(job_id, {"id": job_id, "state": "unknown"})
        for job_id in validated_ids
    }
    _write_json(final_path, final_details)

    jobs = [
        _compact_job(job_id, last_details.get(job_id), secrets) for job_id in validated_ids
    ]
    failed_jobs = [job for job in jobs if job["state"] in FAILURE_STATES]
    if start_timed_out:
        status = "start_timeout"
        failure_summary = (
            f"Start timeout with {len(start_timed_out)} of {len(validated_ids)} jobs "
            "not observed running or assigned: "
            + ", ".join(sorted(start_timed_out))
        )
    elif timed_out:
        status = "timeout"
        failure_summary = (
            f"Timed out with {len(pending)} of {len(validated_ids)} jobs non-terminal: "
            + ", ".join(sorted(pending))
        )
    elif failed_jobs:
        status = "failed"
        failure_summary = "; ".join(
            f"{job['id']}={job['state']}"
            + (f" ({job['failure']})" if job.get("failure") else "")
            for job in failed_jobs
        )
    else:
        status = "ok"
        failure_summary = None

    summary = _redact(
        {
            "elapsed_seconds": elapsed_seconds,
            "evidence_directory": evidence_directory,
            "failure_summary": failure_summary,
            "jobs": jobs,
            "status": status,
        },
        secrets,
    )
    _write_json(summary_path, summary)
    return summary


def _read_api_key() -> str:
    key_file = os.environ.get("GALAXY_API_KEY_FILE")
    if key_file:
        key = Path(key_file).read_text(encoding="utf-8").strip()
    else:
        key = os.environ.get("GALAXY_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Galaxy API key is not configured")
    return key


def wait_for_galaxy_jobs(
    job_ids: list[str],
) -> dict[str, Any]:
    """Block on existing jobs until terminal state without resubmission."""

    from bioblend.galaxy import GalaxyInstance

    api_key = _read_api_key()
    galaxy_url = os.environ.get("GALAXY_URL", "https://usegalaxy.org").rstrip("/")
    workspace_root = Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace"))
    galaxy = GalaxyInstance(galaxy_url, key=api_key)
    return wait_for_jobs(
        job_ids,
        fetch_job=lambda job_id: galaxy.jobs.show_job(job_id, full_details=True),
        workspace_root=workspace_root,
        evidence_directory=_next_evidence_directory(
            workspace_root,
            "run_trace/galaxy_wait",
        ),
        timeout_seconds=None,
        start_timeout_seconds=None,
        poll_interval_seconds=10.0,
        secrets=(api_key,),
    )


def serve() -> None:
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("galaxy-wait")
    server.tool(name="wait_for_galaxy_jobs")(wait_for_galaxy_jobs)
    server.run(transport="stdio")


if __name__ == "__main__":
    serve()
