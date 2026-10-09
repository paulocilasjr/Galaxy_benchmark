"""Collect the October 2026 BixBench token-optimization experiment into token_improvment/.

The experiment (goeckslab.github.io/galaxy-agent-benchmark/bixbench/token-optimization-oct2026/) reran GPT-5.6 Sol in
the Galaxy-API code condition on the 50 BixBench-Verified-50 tasks, three replicates, with a reduced-token Galaxy
interface. It is kept apart from the main archive: nothing outside token_improvment/ is written.

Steps (run from the repository root; each step can be repeated):
  snapshot   save the public index page, summary.json and the 50 item pages        -> site_snapshot/
  inventory  parse every run card (1,650: 150 new runs, plus 1,500 archived runs of five
             model configurations in both conditions) and link each archived run to
             its local copy in BixBench_50/analysis; write the collector workbook  -> run_inventory.csv,
                                                                                      token_optimization_runs.csv,
                                                                                      token_optimization_oct2026_links.xlsx
  batch      fetch the batch-level files of the HF run folder (README, comparison,
             file and run indexes, protocol)                                       -> hf_batch/
  collect    collect the 150 new runs with analysis_execution/run.py (trace folder,
             Galaxy history snapshot, evidence JSON, report)                       -> analysis/<task>/
  verify     check the collected runs against summary.json                         -> verification.json

Tokens are read from the environment only: HF_TOKEN (private trace dataset) and GALAXY_API_KEY (history snapshots).
Usage: python token_improvment/collect_token_optimization.py snapshot inventory batch collect verify
"""
import csv
import gzip
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO / "analysis_execution"))
from collect import Client, _hf_listing, digest, redact_bytes, utc, write_json  # noqa: E402
from workbook import RunLink, load_inventory  # noqa: E402

SITE = "https://goeckslab.github.io/galaxy-agent-benchmark/bixbench"
PAGE = f"{SITE}/token-optimization-oct2026/index.html"
SNAP = HERE / "site_snapshot"
REPO_ID = "goeckslab/galaxy-agent-benchmark-run-traces"
NEW_MODEL = "Codex GPT-5.6 Sol token optimization Oct 2026"   # run_id galaxy_codex_gpt_5_6_sol_token_optimization_oct_2026_rN
CONDITION = {"Galaxy-API code with skills": "galaxy", "Open-ended code with skills": "open_ended_code"}
WORKBOOK = HERE / "token_optimization_oct2026_links.xlsx"
ARCHIVE_WORKBOOK = REPO / "BixBench_50/bixbench_execution_condition_links.xlsx"
SUMMARIES = REPO / "manuscript_material/source_data/derived/run_summaries.jsonl.gz"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Galaxy-benchmark-retrospective-audit/2"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def snapshot():
    SNAP.mkdir(exist_ok=True)
    index = fetch(PAGE)
    (SNAP / "index.html").write_bytes(index)
    (SNAP / "summary.json").write_bytes(fetch(f"{SITE}/token-optimization-oct2026/summary.json"))
    tasks = sorted(set(re.findall(r"\.\./(bix-\d+-q\d+)/index\.html#token-optimization-oct2026", index.decode())))
    for task in tasks:
        (SNAP / f"{task}.html").write_bytes(fetch(f"{SITE}/{task}/index.html"))
    files = sorted(p.name for p in SNAP.iterdir() if p.name != "manifest.json")
    write_json(SNAP / "manifest.json", {"retrieved_at_utc": utc(), "source": PAGE,
                                        "files": {f: digest((SNAP / f).read_bytes()) for f in files}})
    print(f"snapshot: index, summary.json and {len(tasks)} item pages")


def cards():
    """Every run card on the 50 item pages, tagged with its page section."""
    out = []
    for page in sorted(SNAP.glob("bix-*.html")):
        task, section = page.stem, None
        for part in re.split(r"(<h2[^>]*>.*?</h2>)", page.read_text(), flags=re.S):
            head = re.match(r"<h2[^>]*>(.*?)</h2>", part, re.S)
            if head:
                section = html.unescape(re.sub("<[^>]+>", "", head.group(1))).strip()
                continue
            for _, body in re.findall(r'<article class="run([^"]*)"[^>]*>(.*?)</article>', part, re.S):
                get = lambda p: (lambda m: html.unescape(m.group(1)).strip() if m else None)(re.search(p, body, re.S))
                links = {html.unescape(re.sub("<[^>]+>", "", lab)).strip(): url
                         for url, lab in re.findall(r'<a href="([^"]+)"[^>]*>(.*?)</a>', body, re.S)}
                usage = {html.unescape(k).strip(): html.unescape(v).strip() for k, v in re.findall(r"<dt>(.*?)</dt><dd>(.*?)</dd>", body, re.S)}
                out.append(dict(task=task, section=section, model=get(r'<div class="run-head"><div><span>(.*?)</span>'),
                                replicate=int(get(r"<h3>replicate (\d+)</h3>")), status=get(r'<span class="status ([a-z_-]+)"'),
                                answer=get(r'<div class="answer-line"><span>Answer</span><code>(.*?)</code>'),
                                page_total_tokens=usage.get("Total tokens"), page_output_tokens=usage.get("Output"),
                                history_url=links.get("Galaxy history"), trace_url=links.get("Run trace")))
    return out


def inventory():
    summary = json.loads((SNAP / "summary.json").read_text())
    new = {(r["item_id"], r["replicate"]): r for r in summary["runs"]}
    archive = {(r.task, r.condition, r.replicate, r.model.replace(" (superseded)", "")): r for r in load_inventory(ARCHIVE_WORKBOOK)}
    sums = {(s["task"], s["run_id"]): s for s in map(json.loads, gzip.open(SUMMARIES, "rt")) if s["benchmark"] == "BixBench50"}
    rows, wb_rows = [], []
    for c in cards():
        if "token optimization" in c["section"]:
            s = new[(c["task"], c["replicate"])]
            link = RunLink("bixbench", c["task"], NEW_MODEL, "galaxy", "Galaxy-API code with skills", c["replicate"],
                           f"https://usegalaxy.org/histories/view?id={s['history_id']}", c["trace_url"], "token optimization", 0)
            assert c["trace_url"].rstrip("/").endswith(s["trace_path"]), c
            rows.append(dict(c, group="token_optimization_oct2026", model="GPT-5.6 Sol", condition="galaxy", run_id=link.run_id,
                             passed=s["passed"], answer=s["answer"], input_tokens=s["usage"]["input_tokens"],
                             cached_input_tokens=s["usage"]["cached_input_tokens"], output_tokens=s["usage"]["output_tokens"],
                             total_tokens=s["total_tokens"], history_id=s["history_id"],
                             local_path=f"token_improvment/analysis/{c['task']}/source_snapshots/huggingface_traces/files/{link.run_id}"))
            wb_rows.append(["BixBench", c["task"], NEW_MODEL, "Galaxy-API code with skills", str(c["replicate"]), link.trace_url, link.galaxy_url])
        else:
            cond = CONDITION[c["section"]]
            a = archive[(c["task"], cond, c["replicate"], c["model"])]
            same = c["trace_url"].rstrip("/") == a.trace_url.rstrip("/") and (cond == "open_ended_code" or (
                re.search(r"id=([0-9a-f]{32})", c["history_url"] or "") or [None, None])[1] == (re.search(r"id=([0-9a-f]{32})", a.galaxy_url or "") or [None, None])[1])
            s = sums.get((c["task"], a.run_id), {})
            rows.append(dict(c, group=f"archive_{cond}", condition=cond, run_id=a.run_id, passed=(s.get("score") == 1) if s else None,
                             input_tokens=s.get("input_tokens"), output_tokens=s.get("output_tokens"),
                             history_id=(re.search(r"id=([0-9a-f]{32})", a.galaxy_url or "") or [None, None])[1],
                             links_match_archive=same,
                             local_path=f"BixBench_50/analysis/{c['task']}/source_snapshots/huggingface_traces/files/{a.run_id}"))
    cols = ["group", "task", "model", "condition", "replicate", "run_id", "passed", "answer", "input_tokens", "cached_input_tokens",
            "output_tokens", "total_tokens", "page_total_tokens", "page_output_tokens", "status", "history_id", "history_url",
            "trace_url", "links_match_archive", "local_path", "section"]
    with open(HERE / "run_inventory.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with open(HERE / "token_optimization_runs.csv", "w", newline="") as f:
        keys = ["item_id", "replicate", "passed", "answer", "expected_range", "total_tokens", "input_tokens", "cached_input_tokens",
                "output_tokens", "open_ended_mean_tokens", "previous_galaxy_mean_tokens", "trace_path", "history_id",
                "history_url", "history_published", "history_importable", "source_result_sha256"]
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in summary["runs"]:
            w.writerow({**{k: r.get(k) for k in keys if k in r}, **r["usage"], "history_url": r["history_access"]["url"],
                        "history_published": r["history_access"]["published"], "history_importable": r["history_access"]["importable"]})
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Token optimization links"
    ws.append(["benchmark", "task", "model", "condition", "replicate", "run_trace", "galaxy_history"])
    for r in wb_rows:
        ws.append(r)
    wb.save(WORKBOOK)
    groups = {}
    for r in rows:
        groups[r["group"]] = groups.get(r["group"], 0) + 1
    print(f"inventory: {len(rows)} runs {groups}; archive links all match: "
          f"{all(r['links_match_archive'] for r in rows if 'links_match_archive' in r)}")


def batch():
    summary = json.loads((SNAP / "summary.json").read_text())
    rev, prefix = summary["hf_revision"], summary["hf_prefix"]
    client = Client(hf_token=os.environ["HF_TOKEN"])
    root = json.loads(client.get(f"https://huggingface.co/api/datasets/{REPO_ID}/tree/{rev}/{prefix}?recursive=false&limit=1000", service="hf")[0])
    entries = [e for e in root if e["type"] == "file"]
    for d in (e for e in root if e["type"] == "directory" and not e["path"].split("/")[-1].startswith("bix_")):
        entries += [e for e in _hf_listing(client, REPO_ID, rev, d["path"]) if e["type"] == "file"]
    dest, records = HERE / "hf_batch", []
    for e in entries:
        rel = e["path"][len(prefix) + 1:]
        raw = client.get(f"https://huggingface.co/datasets/{REPO_ID}/resolve/{rev}/{e['path']}", service="hf")[0]
        kept, red = redact_bytes(raw, Path(rel).name)
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        (dest / rel).write_bytes(kept)
        records.append(dict(path=rel, original_sha256=digest(raw), retained_sha256=digest(kept), redactions=red))
    write_json(dest / "manifest.json", {"repository": REPO_ID, "revision": rev, "prefix": prefix, "retrieved_at_utc": utc(), "files": records})
    print(f"batch: {len(records)} files")


def collect():
    subprocess.run([sys.executable, "run.py", str(WORKBOOK), "--benchmark", "bixbench", "--output-root", str(HERE / "analysis"), "--resume"],
                   cwd=REPO / "analysis_execution", check=True)


def verify():
    sys.path.insert(0, str(REPO / "scripts"))
    from enrich_compbio_evidence import trace_usage
    from build import locate
    summary = json.loads((SNAP / "summary.json").read_text())
    out, problems = [], []
    for r in summary["runs"]:
        task, rep = r["item_id"], r["replicate"]
        rid = RunLink("bixbench", task, NEW_MODEL, "galaxy", "", rep, None, None, "", 0).run_id
        pkg = HERE / "analysis" / task
        man = json.loads((pkg / f"source_snapshots/huggingface_traces/manifests/{rid}.json").read_text())
        folder = pkg / "source_snapshots/huggingface_traces/files" / rid
        trace = locate(folder, "codex_events.jsonl") or locate(folder, "codex_events.jsonl.gz")
        usage = trace_usage(trace)[0] if trace else {}
        answer = locate(folder, "answer.txt")
        gal = json.loads((pkg / f"source_snapshots/galaxy/{r['history_id']}/manifest.json").read_text())
        rec = dict(task=task, replicate=rep, run_id=rid, trace_status=man["status"],
                   files_not_retained=[f["remote_path"].split("/")[-1] for f in man["files"] if f["status"] != "retained"],
                   answer_matches=(answer.read_text().strip() if answer else None) == str(r["answer"]).strip(),
                   usage_matches=all(usage.get(k) == r["usage"][k] for k in ("input_tokens", "cached_input_tokens", "output_tokens")),
                   history_status=gal["status"], history_jobs=len(gal.get("jobs", [])))
        out.append(rec)
        if not (rec["answer_matches"] and rec["usage_matches"] and rec["history_status"] == "retrieved"):
            problems.append(rec)
    write_json(HERE / "verification.json", {"checked_at_utc": utc(), "runs": out, "problems": problems})
    print(f"verify: {len(out)} runs; {len(problems)} with a mismatch or incomplete history")


if __name__ == "__main__":
    steps = {"snapshot": snapshot, "inventory": inventory, "batch": batch, "collect": collect, "verify": verify}
    for step in sys.argv[1:] or list(steps):
        steps[step]()
