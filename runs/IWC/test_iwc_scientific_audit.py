"""Local regression checks for the supplemental extraction and manuscript tables."""

from collections import Counter
import re
import statistics
import unittest

import audit_iwc_results as audit


class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = audit.read(audit.ROOT / "iwc_scientific_audit.json")
        cls.runs = cls.data["runs"]
        cls.by_id = {run["id"]: run for run in cls.runs}
        cls.report = (audit.ROOT / "result_section_iwc.md").read_text()
        # The report uses typographic minus signs in tables; normalize for numeric matching.
        cls.normalized_report = cls.report.replace("−", "-")

    def test_quantiles_and_bootstrap(self):
        self.assertEqual(audit.quantile([0, 1, 2, 3], .25), .75)
        self.assertEqual(audit.bootstrap([.25, .25])["ci95"], [.25, .25])
        self.assertEqual(audit.bootstrap([-.1, .2]), audit.bootstrap([-.1, .2]))

    def test_source_integrity_and_links(self):
        for name, item in self.data["sources"].items():
            path = audit.ROOT / name
            self.assertEqual(path.stat().st_size, item["bytes"], name)
            self.assertEqual(audit.digest(path), item["sha256"], name)
        for name in ("result_section_iwc.md", "iwc_overview.md", "iwc_recovery_summary.md"):
            for target in re.findall(r"\]\(([^)]+)\)", (audit.ROOT / name).read_text()):
                self.assertTrue((audit.ROOT / target.split("#")[0]).exists(), (name, target))

    def test_inventory_and_raw_scores(self):
        self.assertEqual(len(self.by_id), 240)
        self.assertEqual(sum(r["score"] is not None for r in self.runs), 237)
        self.assertEqual(sum(r["score"] == 0 for r in self.runs), 6)
        self.assertEqual(sum(r["score_conflict_gt_1e_9"] for r in self.runs), 17)
        for run in self.runs:
            for path in run["sources"].values():
                if path is not None:
                    self.assertIn(path, self.data["sources"])
            raw = audit.read(audit.ROOT / run["sources"]["evaluation"])
            self.assertEqual(run["score"], raw["reference_accuracy"])
            if run["score"] is None:
                self.assertEqual(raw["route"]["status"], "unsupported_route")
            else:
                self.assertTrue(0 <= run["score"] <= 1)

    def test_task_pairing_and_report_numbers(self):
        for population, models in self.data["comparisons"].items():
            for model, result in models.items():
                for pair in result["pairs"]:
                    members = [self.by_id[key] for key in pair["run_ids"]]
                    self.assertEqual(len(members), 6)
                    self.assertEqual({r["task"] for r in members}, {pair["task"]})
                    self.assertEqual({r["model"] for r in members}, {model})
                    for condition in audit.CONDITIONS:
                        selected = [r for r in members if r["condition"] == condition]
                        self.assertEqual(len(selected), 3)
                        self.assertAlmostEqual(pair[condition], statistics.mean(r["score"] for r in selected))
                    self.assertAlmostEqual(pair["difference"], pair["galaxy"] - pair["open_ended_code"])
                if population == "common_nine_tasks":
                    self.assertEqual(len(result["pairs"]), 9)
                    self.assertNotIn(audit.HOST, {p["task"] for p in result["pairs"]})
                expected = audit.bootstrap(p["difference"] for p in result["pairs"])
                self.assertEqual(result["ci95"], expected["ci95"])
                # The report displays comparison figures to three decimals and task means to
                # four, so that displayed digits do not exceed what nine to ten task units
                # support; exact values stay in this audit JSON. These assertions still catch
                # drift between the report and the audit, at the precision actually published.
                # Unicode minus signs in the report are normalized before matching.
                for number in (result["galaxy"], result["open_ended_code"], result["estimate"], *result["ci95"]):
                    self.assertTrue(f"{number:.3f}" in self.normalized_report, (population, model, number))
        for result in self.data["task_results"].values():
            for condition in audit.CONDITIONS:
                self.assertIn(f"{result[condition]['mean']:.4f}", self.normalized_report)

    def test_archive_jobs_and_recovery(self):
        jobs = self.data["jobs"]
        self.assertEqual(len(jobs), 1607)
        self.assertEqual(sum(j["acquisition"] for j in jobs.values()), 277)
        self.assertEqual(Counter(j["status"] for j in jobs.values()), {"ok": 1389, "error": 202, "deleted": 16})
        self.assertIsNone(self.data["operational"]["open_ended_code"]["runs_with_job_failures"])
        for run in self.runs:
            for key in run["job_refs"]:
                self.assertIn(key, jobs)
        for recovery in self.data["recovery_candidates"]:
            run = self.by_id[recovery["task"] + "/" + recovery["run_id"]]
            original = audit.read(audit.ROOT / run["sources"]["evidence"])
            old = next(r for r in original["runs"] if r["run_id"] == run["run_id"])
            events = {e["event_id"]: e for e in old["events"]}
            for key in recovery["failed_event_ids"] + recovery["recovery_event_ids"]:
                self.assertIn(key, events)
            failed = events[recovery["failed_event_ids"][0]]
            recovered = events[recovery["recovery_event_ids"][0]]
            self.assertLess(failed["timestamp"], recovered["timestamp"])
            self.assertEqual(failed["tool"], recovered["tool"])
            self.assertEqual(set(failed["native_input_hda_ids"]), set(recovered["native_input_hda_ids"]))
        self.assertEqual(sum(f["retained"] for r in self.runs for f in r["final_answer_files"]), 286)
        self.assertEqual(sum(len(r["final_answer_files"]) for r in self.runs), 360)

    def test_routes_and_usage(self):
        complete = [c for c in self.data["route_cells"] if c["complete"]]
        self.assertEqual(len(complete), 31)
        self.assertEqual(Counter(c["distinct_routes"] for c in complete), {1: 13, 2: 15, 3: 3})
        self.assertEqual(sum(bool(r["malformed_trace_lines"]) for r in self.runs), 25)
        self.assertEqual(sum(len(r["malformed_trace_lines"]) for r in self.runs), 25)
        for run in self.runs:
            self.assertGreater(run["usage"]["input_tokens"], 0)
            self.assertGreater(run["usage"]["output_tokens"], 0)
        for ids in self.data["finding_run_sets"].values():
            self.assertTrue(set(ids) <= self.by_id.keys())


if __name__ == "__main__":
    unittest.main()
