"""Check that swapping in the 53 reviewed reruns changed no other run.

Compares per-run records in the working tree with the last commit before the swap (BASE, default 7ed8048c9) for every
per-run table that the rebuild regenerates. A record may differ only if it belongs to one of the 53 reruns in
rerun_manifest.csv. Aggregates (totals, model summaries, figures) are expected to move and are not compared here.

Usage: python CompBio/reruns_20261005/check_unchanged.py [BASE]
"""
import csv
import gzip
import io
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = sys.argv[1] if len(sys.argv) > 1 else "7ed8048c9"
RERUNS = {(r["task"], r["run_id"]) for r in csv.DictReader((HERE / "rerun_manifest.csv").open())}
TASKS = {t for t, _ in RERUNS}
failures = []


def old_bytes(path):
    out = subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=REPO, capture_output=True)
    return out.stdout if out.returncode == 0 else None


def compare(name, old, new, key):
    """old/new: iterables of records; key(record) -> (task, run_id, ...) whose first two fields identify the run."""
    o, n = {}, {}
    for r in old:
        o.setdefault(key(r), []).append(r)
    for r in new:
        n.setdefault(key(r), []).append(r)
    changed = [k for k in set(o) | set(n) if o.get(k) != n.get(k)]
    bad = [k for k in changed if (k[0], k[1]) not in RERUNS]
    rerun_changed = len({(k[0], k[1]) for k in changed if (k[0], k[1]) in RERUNS})
    print(f"{name}: {len(set(o) | set(n))} keys; reruns changed {rerun_changed}; other records changed {len(bad)}")
    if bad:
        failures.append((name, sorted(bad)[:5]))


def jsonl_gz(raw):
    return [json.loads(x) for x in gzip.decompress(raw).decode().splitlines() if x.strip()]


def csv_rows(raw, gz=False):
    text = gzip.decompress(raw).decode() if gz else raw.decode()
    return list(csv.DictReader(io.StringIO(text)))


# Task packages: untouched tasks must be byte-identical; in rerun tasks every other run must be identical.
diff = subprocess.run(["git", "diff", "--name-only", BASE, "--", "CompBio/analysis"], cwd=REPO, capture_output=True, text=True).stdout.split()
outside = sorted({p.split("/")[2] for p in diff} - TASKS)
print(f"task packages changed outside the rerun tasks: {len(outside)}")
if outside:
    failures.append(("task packages", outside[:5]))
old_runs, new_runs = [], []
for task in sorted(TASKS):
    rel = f"CompBio/analysis/{task}/history_analysis_evidence.json"
    for runs, data in ((old_runs, json.loads(old_bytes(rel))), (new_runs, json.loads((REPO / rel).read_text()))):
        runs.extend(dict(r, _task=task) for r in data["runs"])
compare("evidence runs", old_runs, new_runs, lambda r: (r["_task"], r["run_id"]))

# Run-link workbook: only the 53 Galaxy rows may point elsewhere.
sys.path.insert(0, str(REPO / "analysis_execution"))
from workbook import load_inventory  # noqa: E402
inv = lambda p: [dict(task=r.task, run_id=r.run_id, galaxy=r.galaxy_url, trace=r.trace_url) for r in load_inventory(p)]
compare("workbook rows", inv(HERE / "compbiobench_execution_condition_links.pre_rerun_20261005.xlsx"),
        inv(REPO / "CompBio/compbiobench_execution_condition_links.xlsx"), lambda r: (r["task"], r["run_id"]))

analysis = "BixBench50_CompBio_analysis/analysis.json"
a_old, a_new = json.loads(old_bytes(analysis)), json.loads((REPO / analysis).read_text())
compare("analysis.json runs", a_old["runs"], a_new["runs"], lambda r: (r["task"], r["run_id"], r["benchmark"]))
jobs_old = {(j["server"], j["native_job_id"]): j for j in a_old["jobs"]}
jobs_new = {(j["server"], j["native_job_id"]): j for j in a_new["jobs"]}
refs = lambda j: {(x["task"], x["run_id"]) for x in (j or {}).get("refs", [])}
moved = [k for k in set(jobs_old) | set(jobs_new) if jobs_old.get(k) != jobs_new.get(k)
         and not (refs(jobs_old.get(k)) | refs(jobs_new.get(k))) & RERUNS]
print(f"analysis.json jobs: {len(set(jobs_old) | set(jobs_new))} jobs; changed without a rerun reference {len(moved)}")
if moved:
    failures.append(("analysis.json jobs", moved[:5]))

summ = "manuscript_material/source_data/derived/run_summaries.jsonl.gz"
compare("run summaries", jsonl_gz(old_bytes(summ)), jsonl_gz((REPO / summ).read_bytes()), lambda r: (r["task"], r["run_id"], r["benchmark"]))

calls = "manuscript_narrative/derived/galaxy_calls/calls.csv.gz"
compare("Galaxy calls", csv_rows(old_bytes(calls), gz=True), csv_rows((REPO / calls).read_bytes(), gz=True),
        lambda r: (r["task"], r["run_id"], r["benchmark"], r["line"]))

design = "manuscript_narrative/derived/design/per_run_design_metadata.csv"
compare("design metadata", csv_rows(old_bytes(design)), csv_rows((REPO / design).read_bytes()), lambda r: (r["task"], r["run_id"], r["benchmark"]))

audit = "CompBio/compBio_overview_audit.json"
au_old, au_new = json.loads(old_bytes(audit)), json.loads((REPO / audit).read_text())
compare("CompBio audit run summaries", au_old["run_summaries"], au_new["run_summaries"], lambda r: (r["task"], r["run_id"]))
vec = lambda v: {k: x for k, x in v.items() if k != "rerun_answers_applied"}
reps_with_reruns = {rid for _, rid in RERUNS}
sv_old = {(v["condition"], v["model"], v["replicate"]): vec(v) for v in au_old["score_vectors"]}
sv_new = {(v["condition"], v["model"], v["replicate"]): vec(v) for v in au_new["score_vectors"]}
moved = [k for k in sv_old if sv_old[k] != sv_new.get(k) and f"{k[0]}_{k[1]}_{k[2]}" not in reps_with_reruns]
print(f"CompBio score vectors: {len(sv_old)} replicates; changed outside replicates with reruns {len(moved)}")
if moved:
    failures.append(("score vectors", moved))

SLUG = {"GPT-5.5": "codex_gpt_5_5", "GPT-5.6 Sol": "codex_gpt_5_6_sol", "GPT-5.6 Luna": "codex_gpt_5_6_luna",
        "DeepSeek V4 Pro": "codex_deepseek_v4_pro_0813"}


def run_key(r):
    """(task, run_id) from a run_id column, or from cfg/env/replicate for CompBio tables that lack one."""
    if r.get("run_id"):
        return (r["task"], r["run_id"], r.get("benchmark"))
    if r.get("benchmark") == "CompBio" and r.get("cfg") in SLUG:
        return (r["task"], f"{r['env']}_{SLUG[r['cfg']]}_r{int(float(r['replicate']))}", "CompBio")
    return (r["task"], f"{r.get('env')}|{r.get('cfg')}|{r.get('replicate')}", r.get("benchmark"))


for rel in sys.argv[2:]:  # optional extra per-run CSVs (e.g. the analysis tables built after the swap)
    o = old_bytes(rel)
    if o is not None:
        compare(rel, csv_rows(o), csv_rows((REPO / rel).read_bytes()), run_key)

print("PASS" if not failures else f"FAIL: {failures}")
sys.exit(1 if failures else 0)
