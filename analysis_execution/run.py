"""CLI entry point for XLSX-driven, read-only execution-history audits."""
from __future__ import annotations

import argparse
import getpass
import json
import os
import shutil
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from build import build_evidence
from collect import Client, collect_galaxy, collect_trace, galaxy_credential_gate, write_json
from report import render
from validate import validate
from workbook import load_inventory, galaxy_history_id


HERE = Path(__file__).resolve().parent
REPO = HERE.parent
ROOTS = {"bixbench": REPO / "BixBench_50/analysis", "compbio": REPO / "CompBio/analysis", "iwc": REPO / "IWC/analysis"}


def arguments(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("workbook", type=Path, help="XLSX run-link table")
    p.add_argument("--task", action="append", help="Task ID to process; repeatable. Default: all rows")
    p.add_argument("--benchmark", choices=sorted(ROOTS), help="Optional benchmark filter")
    p.add_argument("--output-root", type=Path, help="Override benchmark output root for a single benchmark")
    p.add_argument("--hf-token-env", default="HF_TOKEN", help="Environment variable containing the HF token (default HF_TOKEN)")
    p.add_argument("--prompt-hf-token", action="store_true", help="Read HF token from a hidden terminal prompt")
    p.add_argument("--insecure-tls", action="store_true", help="Allow source retrieval when the host's TLS proxy has an invalid certificate; record this limitation")
    p.add_argument("--max-trace-mb", type=int, default=10)
    p.add_argument("--max-output-kb", type=int, default=100)
    p.add_argument("--max-history-contents", type=int, default=300, help="Capture detailed Galaxy contents only for histories at or below this count")
    p.add_argument("--hf-workers", type=int, default=8, help="Concurrent Hugging Face run collectors")
    p.add_argument("--galaxy-workers", type=int, default=4, help="Concurrent Galaxy history collectors")
    p.add_argument("--galaxy-rate", type=float, default=5.0, help="Maximum shared Galaxy API request rate per second")
    p.add_argument("--resume", action="store_true", help="Use existing source manifests and replace the current report")
    p.add_argument("--adopt-existing", action="store_true", help="Preserve conflicting legacy task files before generating this audit in an existing task directory")
    p.add_argument("--offline", action="store_true", help="Build from source manifests already in each task directory")
    p.add_argument("--dry-run", action="store_true", help="Validate workbook and print inventory without creating files")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = arguments(argv)
    if min(args.max_trace_mb, args.max_output_kb, args.max_history_contents, args.hf_workers, args.galaxy_workers, args.galaxy_rate) <= 0:
        raise ValueError("Byte caps must be positive")
    workbook = args.workbook.resolve()
    if not workbook.is_file():
        raise FileNotFoundError(workbook)
    inventory = load_inventory(workbook)
    if args.task:
        wanted = set(args.task)
        inventory = [r for r in inventory if r.task in wanted]
    if args.benchmark:
        inventory = [r for r in inventory if r.benchmark == args.benchmark]
    if not inventory:
        raise ValueError("No workbook rows matched the requested task/benchmark")
    run_ids = [r.run_id for r in inventory]
    if len(run_ids) != len(set((r.benchmark, r.task, r.run_id) for r in inventory)):
        raise ValueError("Two model labels normalize to the same run ID; use distinct model labels")
    if args.output_root and len({r.benchmark for r in inventory}) != 1:
        raise ValueError("--output-root requires a single benchmark selection")
    groups = defaultdict(list)
    for run in inventory:
        groups[(run.benchmark, run.task)].append(run)
    for (benchmark, task), rows in sorted(groups.items()):
        base = args.output_root.resolve() if args.output_root else ROOTS[benchmark]
        output = base / task
        print(f"{benchmark}/{task}: {len(rows)} rows -> {output}")
        if args.dry_run:
            for row in rows:
                print(f"  {row.run_id}: Galaxy={'yes' if row.galaxy_url else 'no'} trace={'yes' if row.trace_url else 'no'}")
    if args.dry_run:
        return 0
    try:
        import jsonschema  # noqa: F401
    except ImportError as exc:
        raise RuntimeError("Install analysis_execution/requirements.txt before collecting sources") from exc
    if any(r.galaxy_url for r in inventory) and not args.offline:
        galaxy_key = galaxy_credential_gate(REPO)
    else:
        galaxy_key = None
    hf_token = os.environ.get(args.hf_token_env)
    if args.prompt_hf_token and not args.offline:
        hf_token = getpass.getpass("HF token: ").strip() or hf_token
    client = Client(hf_token=hf_token, galaxy_key=galaxy_key, insecure_tls=args.insecure_tls, galaxy_requests_per_second=args.galaxy_rate)
    outputs = {}
    for (benchmark, task), rows in sorted(groups.items()):
        base = args.output_root.resolve() if args.output_root else ROOTS[benchmark]
        output = base / task
        if output.exists() and any(output.iterdir()) and not (args.resume or args.offline or args.adopt_existing):
            raise FileExistsError(f"{output} already contains files; use --resume, --adopt-existing, or a new output root")
        marker = output / ".analysis_execution.json"
        if output.exists() and any(output.iterdir()) and not marker.exists():
            if not args.adopt_existing:
                raise FileExistsError(f"{output} was not created by analysis_execution; use --adopt-existing or a new output root")
            legacy = output / "legacy_pre_analysis_execution"
            collisions = ["README.md", "history_analysis.md", "history_analysis_evidence.json",
                          "history_analysis_evidence.schema.json", f"{task}.json", "run_manifest.json",
                          "input_manifest.json", "recovered_code/manifest.json",
                          "selected_outputs/galaxy/manifest.json", "selected_outputs/open_ended_code/manifest.json"]
            for relative in collisions:
                original = output / relative
                archived = legacy / relative
                if original.is_file() and not archived.exists():
                    archived.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(original, archived)
        output.mkdir(parents=True, exist_ok=True)
        if not marker.exists():
            write_json(marker, {"generator": "analysis_execution", "format_version": 1})
        (output / "selected_outputs/open_ended_code").mkdir(parents=True, exist_ok=True)
        write_json(output / "selected_outputs/open_ended_code/manifest.json",
                   {"status": "not_collected", "reason": "Trace output files are retained in source_snapshots; no code was replayed"})
        outputs[(benchmark, task)] = output
    if not args.offline:
        hf_jobs, galaxy_jobs = [], []
        for key, rows in sorted(groups.items()):
            output = outputs[key]
            seen_histories = set()
            for row in rows:
                if row.trace_url:
                    manifest = output / "source_snapshots/huggingface_traces/manifests" / f"{row.run_id}.json"
                    prior = json.loads(manifest.read_text()) if manifest.exists() else {}
                    if not (args.resume and prior.get("status") == "retrieved"):
                        hf_jobs.append((row, output))
                if row.galaxy_url:
                    hid = galaxy_history_id(row.galaxy_url)
                    if hid in seen_histories:
                        continue
                    seen_histories.add(hid)
                    manifest = output / "source_snapshots/galaxy" / hid / "manifest.json"
                    prior = json.loads(manifest.read_text()) if manifest.exists() else {}
                    complete_or_bounded = prior.get("status") == "retrieved" or (prior.get("status") == "history_metadata_only" and prior.get("contents_limit_applied") and args.max_history_contents <= prior.get("max_contents", 0))
                    if not (args.resume and complete_or_bounded):
                        galaxy_jobs.append((row, output))
        print(f"Collecting {len(hf_jobs)} trace directories and {len(galaxy_jobs)} Galaxy histories", flush=True)
        status = defaultdict(int)
        with ThreadPoolExecutor(max_workers=args.hf_workers) as hf_pool, ThreadPoolExecutor(max_workers=args.galaxy_workers) as galaxy_pool:
            futures = {}
            for row, output in hf_jobs:
                futures[hf_pool.submit(collect_trace, client, row, output, max_bytes=args.max_trace_mb * 1_000_000)] = ("trace", row.run_id)
            for row, output in galaxy_jobs:
                futures[galaxy_pool.submit(collect_galaxy, client, row, output, max_output_bytes=args.max_output_kb * 1000, max_contents=args.max_history_contents)] = ("galaxy", galaxy_history_id(row.galaxy_url))
            for index, future in enumerate(as_completed(futures), 1):
                kind, identifier = futures[future]
                try:
                    result = future.result()
                    status[(kind, result["status"])] += 1
                except Exception as exc:
                    status[(kind, "worker_error")] += 1
                    print(f"  {kind} {identifier}: {type(exc).__name__}", flush=True)
                if index % 25 == 0 or index == len(futures):
                    print(f"  collected {index}/{len(futures)}; statuses={dict(status)}", flush=True)
    for (benchmark, task), rows in sorted(groups.items()):
        output = outputs[(benchmark, task)]
        hf_root = output / "source_snapshots/huggingface_traces"
        for condition, filename in (("galaxy", "manifest_galaxy.json"), ("open_ended_code", "manifest.json")):
            write_json(hf_root / filename,
                       {"runs": {row.run_id: json.loads((hf_root / "manifests" / f"{row.run_id}.json").read_text())
                                 if (hf_root / "manifests" / f"{row.run_id}.json").exists() else {"status": "not_collected"}
                                 for row in rows if row.condition == condition and row.trace_url},
                        "note": "Task-scoped index; original/retained hashes live in each per-run manifest"})
        galaxy_root = output / "source_snapshots/galaxy"
        history_ids = sorted({galaxy_history_id(row.galaxy_url) for row in rows if row.galaxy_url})
        write_json(galaxy_root / "retrieval_manifest.json",
                   {"server": "https://usegalaxy.org", "histories": {hid: json.loads((galaxy_root / hid / "manifest.json").read_text())
                                                                if (galaxy_root / hid / "manifest.json").exists() else {"status": "not_collected"}
                                                                for hid in history_ids}})
        shutil.copyfile(HERE / "history_analysis_evidence.schema.json", output / "history_analysis_evidence.schema.json")
        evidence = build_evidence(output, rows, REPO, workbook)
        validate(output)
        evidence = json.loads((output / "history_analysis_evidence.json").read_text())
        render(output, evidence)
        validate(output)
        print(f"  wrote {output / 'history_analysis.md'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError, FileExistsError, RuntimeError) as exc:
        print(f"analysis_execution: {exc}", file=sys.stderr)
        raise SystemExit(2)
