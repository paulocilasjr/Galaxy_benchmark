"""Offline end-to-end test using a minimal XLSX and synthetic original records."""
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collect import Client, collect_galaxy, collect_trace, digest, write_json
from build import _recovery_candidates
from run import main
from workbook import RunLink, load_inventory


def xlsx(path: Path, rows, hyperlinks=None):
    hyperlinks = hyperlinks or {}
    cells = []
    for row_number, values in enumerate(rows, 1):
        parts = []
        for col, value in enumerate(values):
            if value is None:
                continue
            ref = chr(65 + col) + str(row_number)
            parts.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(value)}</t></is></c>')
        cells.append(f'<row r="{row_number}">{"".join(parts)}</row>')
    hxml = []
    hrels = []
    for n, ((row, col), url) in enumerate(hyperlinks.items(), 1):
        ref = chr(65 + col) + str(row)
        hxml.append(f'<hyperlink ref="{ref}" r:id="rId{n}"/>')
        hrels.append(f'<Relationship Id="rId{n}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="{escape(url)}" TargetMode="External"/>')
    sheet = '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheetData>' + ''.join(cells) + '</sheetData>' + ('<hyperlinks>' + ''.join(hxml) + '</hyperlinks>' if hxml else '') + '</worksheet>'
    workbook = '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Runs" sheetId="1" r:id="rId1"/></sheets></workbook>'
    rels = '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>'
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", rels)
        z.writestr("xl/worksheets/sheet1.xml", sheet)
        if hrels:
            z.writestr("xl/worksheets/_rels/sheet1.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(hrels) + '</Relationships>')


class PipelineTest(unittest.TestCase):
    def test_recovery_candidate_requires_same_tool_and_input(self):
        failed = {"event_id": "failed", "event_type": "analysis", "execution_location": "galaxy_job", "native_job_id": "j1",
                  "timestamp": "2026-01-01T00:00:00Z", "status": "error", "tool": "datamash", "native_input_hda_ids": ["hda1"], "evidence_refs": ["src:jobs/j1.json"]}
        success = {**failed, "event_id": "success", "native_job_id": "j2", "timestamp": "2026-01-01T00:00:01Z", "status": "ok"}
        run = {"run_id": "r1", "events": [failed, success]}
        self.assertEqual(len(_recovery_candidates(run)), 1)
        success["native_input_hda_ids"] = ["other"]
        self.assertEqual(_recovery_candidates(run), [])

    def test_galaxy_capture_preserves_job_and_output_bytes(self):
        hid = "c" * 32
        class FakeClient(Client):
            def __init__(self):
                pass
            def get(self, url, *, service):
                if url.endswith(f"/histories/{hid}"):
                    obj = {"id": hid, "count": 1}
                elif "/contents?" in url:
                    obj = [{"id": "hda1", "history_content_type": "dataset", "creating_job": "job1",
                            "name": "result.txt", "state": "ok", "file_size": 3,
                            "accessible": True, "purged": False, "download_url": "/api/datasets/hda1/display"}]
                elif "/jobs/job1" in url:
                    obj = {"id": "job1", "tool_id": "phykit_metrics", "state": "ok"}
                elif "/datasets/hda1/display" in url:
                    return b"0.5", {}
                else:
                    raise AssertionError(url)
                return json.dumps(obj).encode(), {}
        row = RunLink("bixbench", "bix-6-q4", "GPT-5.5", "galaxy", "galaxy-api", 1,
                      f"https://usegalaxy.org/histories/view?id={hid}", None, "Runs", 2)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            captured = collect_galaxy(FakeClient(), row, root)
            self.assertEqual(captured["status"], "retrieved")
            self.assertEqual(len(captured["jobs"]), 1)
            self.assertEqual(len(captured["outputs"]), 1)
            self.assertEqual((root / captured["outputs"][0]["path"]).read_bytes(), b"0.5")

    def test_trace_collection_redacts_secret_and_records_both_hashes(self):
        class FakeClient(Client):
            def __init__(self):
                pass
            def get(self, url, *, service):
                if "/api/datasets/" in url:
                    return json.dumps([{"type": "file", "path": "bixbench/run_one/bix_6_q4/anycode/replicate_1/trace.txt", "size": len(payload)}]).encode(), {}
                return payload, {}
        payload = b'"user_email":"person@example.com" hf_' + b"A" * 24
        trace = "https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces/tree/main/bixbench/run_one/bix_6_q4/anycode/replicate_1"
        run = RunLink("bixbench", "bix-6-q4", "GPT-5.5", "open_ended_code", "open-coded", 1, None, trace, "Runs", 2)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = collect_trace(FakeClient(), run, root)
            self.assertEqual(result["status"], "retrieved")
            item = result["files"][0]
            self.assertNotEqual(item["original_sha256"], item["retained_sha256"])
            retained = (root / item["local_path"]).read_bytes()
            self.assertIn(b'"user_email":"[redacted]"', retained)
            self.assertNotIn(b"hf_", retained)

    def test_excel_hyperlink_targets_and_markdown_urls(self):
        with tempfile.TemporaryDirectory() as temp:
            book = Path(temp) / "links.xlsx"
            hid = "b" * 32
            galaxy = f"https://usegalaxy.org/published/history?id={hid}"
            trace = "https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces/tree/main/iwc/run_1/wf_001_short_read_qc_trim/galaxy_strict_skills/replicate_3"
            xlsx(book, [["benchmark", "task", "model", "condition", "replicate", "link1", "link2"],
                        ["iwc", "wf_001_short_read_qc_trim", "Codex + DeepSeek V4 Pro", "galaxy-api", "replicate 3", "Galaxy", "Trace"]],
                 {(2, 5): galaxy, (2, 6): trace})
            row = load_inventory(book)[0]
            self.assertEqual(row.galaxy_url, galaxy)
            self.assertEqual(row.trace_url, trace)
            self.assertEqual(row.replicate, 3)

    def test_offline_xlsx_to_validated_report(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            book = root / "links.xlsx"
            hid = "a" * 32
            g_url = f"https://usegalaxy.org/histories/view?id={hid}"
            t1 = "https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces/tree/main/bixbench/run_one/bix_6_q4/galaxy_strict_skills/replicate_1"
            t2 = "https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces/tree/main/bixbench/run_one/bix_6_q4/anycode_nongalaxy_skills/replicate_1"
            xlsx(book, [
                ["benchmark", "task", "model", "condition", "replicate", "link1", "link2"],
                ["bixbench", "", "bix-6-q4", "Codex GPT-5.5", "galaxy-api", "replicate 1", g_url, t1],
                ["bixbench", "", "bix-6-q4", "Codex GPT-5.5", "open-coded", "replicate 1", t2],
            ])
            rows = load_inventory(book)
            self.assertEqual([r.condition for r in rows], ["galaxy", "open_ended_code"])
            outroot = root / "BixBench_50"
            out = outroot / "bix-6-q4"
            write_json(out / ".analysis_execution.json", {"generator": "analysis_execution", "format_version": 1})
            for row in rows:
                folder = out / "source_snapshots/huggingface_traces/files" / row.run_id
                files = {
                    "prompt.txt": b"Find a value.",
                    "codex_output/answer.txt": b"0.5\n",
                    "evaluation.json": json.dumps({"accuracy": {"score": 1.0, "mode": "test"}, "step_completion": {"score": 1.0}}).encode(),
                    "usage.json": json.dumps({"totals": {"input_tokens": 200 if row.condition == "galaxy" else 100, "output_tokens": 4}}).encode(),
                    "run_trace/docker_invocation.json": json.dumps({"model": "gpt-5.5", "reasoning_effort": "high", "image": "test:1"}).encode(),
                    "run_trace/codex_events.jsonl": (json.dumps({"type": "item.completed", "item": {"id": "item_1", "type": "command_execution", "command": "python analysis.py", "status": "completed", "exit_code": 0}}) + "\n").encode(),
                    "inputs_manifest.json": json.dumps({"inputs": [{"name": "input.txt", "sha256": "a" * 64}]}).encode(),
                    "task.json": json.dumps({"prompt_task": "Find a value."}).encode(),
                }
                manifest_files = []
                for name, content in files.items():
                    path = folder / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
                    manifest_files.append({"status": "retained", "local_path": str(path.relative_to(out)), "retained_bytes": len(content), "retained_sha256": digest(content)})
                write_json(out / "source_snapshots/huggingface_traces/manifests" / f"{row.run_id}.json",
                           {"status": "retrieved", "retrieved_at_utc": "2026-01-01T00:00:00Z", "files": manifest_files})
            gfolder = out / "source_snapshots/galaxy" / hid
            write_json(gfolder / "history.json", {"id": hid, "count": 1, "create_time": "2026-01-01T00:00:00Z"})
            contents = [{"id": "hda1", "history_content_type": "dataset", "creating_job": "job1", "name": "result", "state": "ok", "file_size": 2}]
            write_json(gfolder / "contents.json", contents)
            jobpath = gfolder / "jobs/job1.json"
            write_json(jobpath, {"id": "job1", "tool_id": "phykit_metrics", "state": "ok", "create_time": "2026-01-01T00:00:01Z"})
            output_file = out / "selected_outputs/galaxy" / hid / "hda1.dat"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_bytes(b"ok")
            write_json(gfolder / "manifest.json", {"history_id": hid, "status": "retrieved", "history_path": str((gfolder / "history.json").relative_to(out)),
                        "contents_path": str((gfolder / "contents.json").relative_to(out)),
                        "jobs": [{"id": "job1", "path": str(jobpath.relative_to(out)), "sha256": digest(jobpath.read_bytes())}],
                        "outputs": [{"hda_id": "hda1", "path": str(output_file.relative_to(out)), "retained_bytes": 2,
                                     "retained_sha256": digest(b"ok")} ]})
            self.assertEqual(main([str(book), "--output-root", str(outroot), "--offline"]), 0)
            evidence = json.loads((out / "history_analysis_evidence.json").read_text())
            self.assertEqual(evidence["validation"]["schema"]["validation_status"], "passed")
            self.assertEqual(len(evidence["runs"]), 2)
            self.assertEqual(evidence["comparisons"][0]["estimate_unit"], "percentage points Galaxy minus code")
            self.assertEqual(evidence["comparisons"][1]["estimate"], 2.0)
            self.assertIn("1 distinct analytical creating jobs", (out / "history_analysis.md").read_text())
            self.assertTrue((out / "recovered_code/open_ended_code" / rows[1].run_id / "item_1.command.txt").exists())


if __name__ == "__main__":
    unittest.main()
