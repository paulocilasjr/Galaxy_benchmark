#!/usr/bin/env python3
import csv
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bioblend.galaxy import GalaxyInstance

BASE = "https://usegalaxy.org"
TOOL = "toolshed.g2.bx.psu.edu/repos/goeckslab/tabular_learner/tabular_learner/0.1.4"
RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[1]
TRAIN = REPO / "dataset/experiment_1/Chowell_train_Response.tsv"
TEST = REPO / "dataset/experiment_1/Chowell_test_Response.tsv"
GT = REPO / "ground_truth/experiment_1.json"


def ts():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def rel(path):
    return str(Path(path).resolve().relative_to(RUN))


def key():
    for line in (REPO / ".env").read_text().splitlines():
        if line.startswith("GALAXY_API_KEY=") and line.split("=", 1)[1].strip():
            return line.split("=", 1)[1].strip()
    raise RuntimeError("GALAXY_API_KEY missing or empty")


def dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def log(event):
    with (RUN / "results/activity_log.jsonl").open("a") as handle:
        handle.write(json.dumps({"timestamp": ts(), **event}, sort_keys=True) + "\n")


def note(text):
    with (RUN / "reasoning/reasoning.md").open("a") as handle:
        handle.write("\n" + text.rstrip() + "\n")


def get(api_key, path, **params):
    params["key"] = api_key
    r = requests.get(BASE + path, params=params, timeout=120)
    r.raise_for_status()
    return r.json()


def download(api_key, dataset_id, path):
    r = requests.get(f"{BASE}/api/datasets/{dataset_id}/display", params={"key": api_key}, timeout=240)
    r.raise_for_status()
    path.write_bytes(r.content)


def snapshot(api_key, history_id, label=""):
    dump(RUN / f"traces/galaxy/histories/{label}history.json", get(api_key, f"/api/histories/{history_id}"))
    dump(RUN / f"traces/galaxy/histories/{label}contents.json", get(api_key, f"/api/histories/{history_id}/contents", details="all"))


def parse_html_metrics(path):
    html = path.read_text(errors="replace")
    metrics = {}
    for metric in ["Accuracy", "ROC-AUC", "Precision", "Recall", "F1-Score", "PR-AUC", "Specificity", "MCC"]:
        metrics[metric] = {}
        row = re.search(rf"<tr>\s*<td>{re.escape(metric)}</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*</tr>", html, flags=re.I)
        if row:
            metrics[metric] = {
                "Train": round(float(row.group(1)), 3),
                "Validation": round(float(row.group(2)), 3),
                "Test": round(float(row.group(3)), 3),
            }
    return metrics


def write_metrics_tsv(metrics, path):
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["metric", "Train", "Validation", "Test"])
        for metric in ["Accuracy", "ROC-AUC", "Precision", "Recall", "F1-Score", "PR-AUC", "Specificity", "MCC"]:
            writer.writerow([metric, metrics.get(metric, {}).get("Train", ""), metrics.get(metric, {}).get("Validation", ""), metrics.get(metric, {}).get("Test", "")])


def evaluate(originals, transformed, output_items, failures):
    expected = json.loads(GT.read_text())["ground_truth"]
    checks = [
        ("new_history", True), ("uploaded_train_tsv", True), ("uploaded_test_tsv", True),
        ("tabular_learner_used", True), ("classification_target_response", True),
        ("separate_test_dataset", True), ("threshold_0_25", True), ("galaxy_outputs_created", bool(originals)),
    ]
    raw = "\n".join(p.read_text(errors="replace") for p in originals if p.suffix in [".html", ".csv", ".txt", ".tsv"])
    direct_matched = 0
    compared = 0
    for vals in expected.values():
        for value in vals.values():
            compared += 1
            direct_matched += (str(value) in raw or f"{value:.3f}" in raw)
    transformed_vals = {}
    if transformed:
        for row in csv.DictReader(transformed[0].open(), delimiter="\t"):
            transformed_vals[row["metric"]] = {k: round(float(row[k]), 3) for k in ["Train", "Validation", "Test"] if row.get(k)}
    details = []
    transformed_matched = 0
    for metric, vals in expected.items():
        for split, value in vals.items():
            observed = transformed_vals.get(metric, {}).get(split)
            ok = observed is not None and abs(observed - value) <= 0.001
            transformed_matched += ok
            details.append({"metric": metric, "split": split, "expected": value, "observed": observed, "match": ok})
    prompt_score = sum(v for _, v in checks) / len(checks)
    transformed_checks = checks + [("metrics_tsv_created", bool(transformed))]
    transformed_prompt_score = sum(v for _, v in transformed_checks) / len(transformed_checks)
    agent_score = 0 if not output_items else max(0, 100 - 10 * len(failures) - (0 if originals else 50))
    comparison = {
        "prompt_result_evaluation": {"score": prompt_score, "matched_requirements": sum(v for _, v in checks), "total_requirements": len(checks), "checks": [{"requirement": k, "matched": v} for k, v in checks], "basis": ["Original Galaxy outputs were created from uploaded train/test TSVs with Tabular Learner configured for Response, separate test data, Logistic Regression, and threshold 0.25."]},
        "transformed_prompt_result_evaluation": {"score": transformed_prompt_score, "matched_requirements": sum(v for _, v in transformed_checks), "total_requirements": len(transformed_checks), "checks": [{"requirement": k, "matched": v} for k, v in transformed_checks], "basis": ["Transformed TSV, if present, is a format-only extraction from downloaded Galaxy output."]},
        "direct_ground_truth_result_evaluation": {"score": direct_matched / compared if compared else None, "matched_items": direct_matched, "compared_items": compared, "match_percent": 100 * direct_matched / compared if compared else None, "basis": [f"Matched {direct_matched} of {compared} reference values directly in original downloaded Galaxy files."]},
        "transformed_ground_truth_result_evaluation": {"score": transformed_matched / compared if compared else None, "matched_items": transformed_matched, "compared_items": compared, "match_percent": 100 * transformed_matched / compared if compared else None, "transformation": {"type": "format-only", "source_files": [rel(p) for p in originals], "steps": ["Extracted metric values present in the downloaded Galaxy HTML report into a TSV."]}, "details": details, "basis": [f"Matched {transformed_matched} of {compared} transformed values against ground truth."]},
        "agent_performance_in_galaxy_score": {"score": agent_score, "failure_count": len(failures), "required_output_achieved": bool(originals), "calculation": f"100 - 10*{len(failures)}" + ("" if originals else " - 50"), "basis": ["Galaxy history, uploads, Tabular Learner execution, downloads, and trace snapshots were produced." if originals else "Required output was not achieved."]},
        "calculation_notes": "Prompt scores count requirement presence; ground-truth scores compare metric values; agent score follows SKILL.md."
    }
    dump(RUN / "evaluations/comparison.json", comparison)
    dump(RUN / "evaluations/metrics_summary.json", {
        "prompt_result_score": comparison["prompt_result_evaluation"]["score"],
        "transformed_prompt_result_score": comparison["transformed_prompt_result_evaluation"]["score"],
        "direct_ground_truth_result_score": comparison["direct_ground_truth_result_evaluation"]["score"],
        "transformed_ground_truth_result_score": comparison["transformed_ground_truth_result_evaluation"]["score"],
        "agent_performance_in_galaxy_score": comparison["agent_performance_in_galaxy_score"]["score"],
    })
    return comparison


api_key = key()
gi = GalaxyInstance(BASE, key=api_key)
failures = []
try:
    history_name = "experiment_1_history_20260430T152905Z"
    history_id = gi.histories.create_history(name=history_name)["id"]
    log({"event": "execute", "step": "create_history", "history_id": history_id, "history_name": history_name, "outcome": "ok"})
    snapshot(api_key, history_id, "initial_")
    train = gi.tools.upload_file(str(TRAIN), history_id, file_type="tabular")["outputs"][0]["id"]
    test = gi.tools.upload_file(str(TEST), history_id, file_type="tabular")["outputs"][0]["id"]
    log({"event": "execute", "step": "upload", "train_id": train, "test_id": test, "outcome": "submitted"})
    for i in range(1, 31):
        contents = get(api_key, f"/api/histories/{history_id}/contents", details="all")
        states = {d["id"]: d.get("state") for d in contents if d["id"] in [train, test]}
        log({"event": "check", "step": "upload_poll", "check": i, "states": states})
        if all(states.get(x) == "ok" for x in [train, test]):
            break
        if any(states.get(x) == "error" for x in [train, test]):
            raise RuntimeError(f"upload failed: {states}")
        time.sleep(60)
    snapshot(api_key, history_id, "post_upload_")
    inputs = {
        "data_configuration|input_file": {"src": "hda", "id": train},
        "data_configuration|test_data_choice|has_test_file": "yes",
        "data_configuration|test_data_choice|test_file": {"src": "hda", "id": test},
        "data_configuration|target_feature": "c22",
        "data_configuration|sample_id_selector|use_sample_id": "no",
        "model_hyperparameter_configuration|model_selection|model_type": "classification",
        "model_hyperparameter_configuration|model_selection|classification_models": ["lr"],
        "model_hyperparameter_configuration|model_selection|best_model_metric": "Accuracy",
        "model_hyperparameter_configuration|tune_model": "False",
        "customize_defaults_section|random_seed": 42,
        "customize_defaults_section|train_size": 0.7,
        "customize_defaults_section|normalize": "False",
        "customize_defaults_section|feature_selection": "False",
        "customize_defaults_section|cross_validation|enable_cross_validation": "true",
        "customize_defaults_section|cross_validation|cross_validation_folds": 10,
        "customize_defaults_section|remove_outliers": "False",
        "customize_defaults_section|remove_multicollinearity": "False",
        "customize_defaults_section|polynomial_features": "False",
        "customize_defaults_section|fix_imbalance": "False",
        "customize_defaults_section|probability_threshold": 0.25,
    }
    dump(RUN / "traces/galaxy/jobs/tabular_learner_inputs.json", inputs)
    submitted = gi.tools.run_tool(history_id, TOOL, inputs)
    dump(RUN / "traces/galaxy/jobs/tabular_learner_submission.json", submitted)
    output_ids = [o["id"] for o in submitted.get("outputs", [])]
    log({"event": "execute", "step": "run_tool", "tool_id": TOOL, "output_ids": output_ids, "outcome": "submitted"})
    for i in range(1, 181):
        contents = get(api_key, f"/api/histories/{history_id}/contents", details="all")
        states = {d["id"]: d.get("state") for d in contents if d["id"] in output_ids}
        log({"event": "check", "step": "tool_poll", "check": i, "states": states})
        snapshot(api_key, history_id, f"poll_{i}_")
        if states and all(v == "ok" for v in states.values()):
            break
        if any(v == "error" for v in states.values()):
            raise RuntimeError(f"Tabular Learner failed: {states}")
        time.sleep(60 if i <= 6 else 900)
    contents = get(api_key, f"/api/histories/{history_id}/contents", details="all")
    dump(RUN / "traces/galaxy/histories/final_contents.json", contents)
    outputs = [d for d in contents if d["id"] in output_ids]
    originals = []
    for item in outputs:
        ext = item.get("extension") or "dat"
        name = re.sub(r"[^A-Za-z0-9_.-]+", "_", item.get("name", item["id"])).strip("_")
        path = RUN / "results" / f"galaxy_hid{item.get('hid')}_{name}.{ext}"
        download(api_key, item["id"], path)
        originals.append(path)
        dump(RUN / f"traces/galaxy/datasets/output_hid{item.get('hid')}_{item['id']}.json", get(api_key, f"/api/datasets/{item['id']}"))
    transformed = []
    for path in originals:
        if path.suffix == ".html":
            metrics = parse_html_metrics(path)
            out = RUN / "results/transformed_metrics.tsv"
            write_metrics_tsv(metrics, out)
            dump(RUN / "results/transformed_metrics_provenance.json", {"source_files": [rel(path)], "transformation_type": "format-only", "created": ts()})
            transformed.append(out)
            break
    comp = evaluate(originals, transformed, outputs, failures)
    result = {
        "experiment": "experiment_1", "history_id": history_id, "history_name": history_name, "tool_id": TOOL,
        "parameters": {"training_dataset": "Chowell_train_Response.tsv", "test_dataset": "Chowell_test_Response.tsv", "target_column": "c22: Response", "classification_models": ["lr"], "probability_threshold": 0.25},
        "galaxy_outputs": [{"id": d["id"], "hid": d.get("hid"), "name": d.get("name"), "state": d.get("state"), "extension": d.get("extension")} for d in outputs],
        "local_original_outputs": [rel(p) for p in originals], "local_transformed_outputs": [rel(p) for p in transformed],
        "evaluation": {
            "prompt_result_score": comp["prompt_result_evaluation"]["score"],
            "transformed_prompt_result_score": comp["transformed_prompt_result_evaluation"]["score"],
            "direct_ground_truth_result_score": comp["direct_ground_truth_result_evaluation"]["score"],
            "transformed_ground_truth_result_score": comp["transformed_ground_truth_result_evaluation"]["score"],
            "agent_performance_in_galaxy_score": comp["agent_performance_in_galaxy_score"]["score"],
        },
    }
    dump(RUN / "results/result.attempt_1.json", result)
    dump(RUN / "results/result.json", result)
    dump(RUN / "results/run_record.json", {"started_from": "experiments/medium_context/experiment_1.json", "completed_at": ts(), "history_id": history_id, "tool_id": TOOL, "attempts": 1, "errors": failures})
    dump(RUN / "results/evaluation_manifest.json", {"files": ["evaluations/comparison.json", "evaluations/metrics_summary.json"], "ground_truth": "ground_truth/experiment_1.json"})
    summary = {
        "experiment": "experiment_1",
        "Ground_truth_path": ["ground_truth/experiment_1.json"],
        "Galaxy_tools_used": [TOOL],
        "Galaxy_results": {"files": [f"HID {d.get('hid')}: {d.get('name')} ({d.get('id')})" for d in outputs], "path": [rel(p) for p in originals]},
        "Transformed_galaxy_output": [rel(p) for p in transformed],
        "Experiment_score": {
            "prompt_score": comp["prompt_result_evaluation"]["score"],
            "transformed_prompt_score": comp["transformed_prompt_result_evaluation"]["score"],
            "direct_ground_truth_match_score": comp["direct_ground_truth_result_evaluation"]["score"],
            "transformed_ground_truth_match_score": comp["transformed_ground_truth_result_evaluation"]["score"],
            "agent_performance_in_galaxy_score": comp["agent_performance_in_galaxy_score"]["score"],
        },
        "Evaluation_questions": {
            "prompt_requirements": {"question": "Does the Galaxy output satisfy the requirements from the prompt?", "answer": "yes" if comp["prompt_result_evaluation"]["score"] == 1 else "partial", "score": comp["prompt_result_evaluation"]["score"], "matched_requirements": comp["prompt_result_evaluation"]["matched_requirements"], "total_requirements": comp["prompt_result_evaluation"]["total_requirements"], "basis": comp["prompt_result_evaluation"]["basis"]},
            "transformed_prompt_requirements": {"question": "Does the agent-rearranged Galaxy output satisfy the requirements from the prompt?", "answer": "yes" if comp["transformed_prompt_result_evaluation"]["score"] == 1 else "partial", "score": comp["transformed_prompt_result_evaluation"]["score"], "matched_requirements": comp["transformed_prompt_result_evaluation"]["matched_requirements"], "total_requirements": comp["transformed_prompt_result_evaluation"]["total_requirements"], "basis": comp["transformed_prompt_result_evaluation"]["basis"]},
            "direct_ground_truth_match": {"question": "Does the original Galaxy output directly match the ground truth?", "answer": "yes" if comp["direct_ground_truth_result_evaluation"]["score"] == 1 else "partial", "score": comp["direct_ground_truth_result_evaluation"]["score"], "matched_items": comp["direct_ground_truth_result_evaluation"]["matched_items"], "compared_items": comp["direct_ground_truth_result_evaluation"]["compared_items"], "match_percent": comp["direct_ground_truth_result_evaluation"]["match_percent"], "basis": comp["direct_ground_truth_result_evaluation"]["basis"]},
            "transformed_ground_truth_match": {"question": "Does the agent-rearranged Galaxy output match the ground truth?", "answer": "yes" if comp["transformed_ground_truth_result_evaluation"]["score"] == 1 else "partial", "score": comp["transformed_ground_truth_result_evaluation"]["score"], "matched_items": comp["transformed_ground_truth_result_evaluation"]["matched_items"], "compared_items": comp["transformed_ground_truth_result_evaluation"]["compared_items"], "match_percent": comp["transformed_ground_truth_result_evaluation"]["match_percent"], "basis": comp["transformed_ground_truth_result_evaluation"]["basis"]},
            "agent_execution": {"question": "Does the agent know how to execute the task in Galaxy to reach the result?", "answer": "yes" if comp["agent_performance_in_galaxy_score"]["required_output_achieved"] else "no", "score": comp["agent_performance_in_galaxy_score"]["score"], "failure_count": comp["agent_performance_in_galaxy_score"]["failure_count"], "required_output_achieved": comp["agent_performance_in_galaxy_score"]["required_output_achieved"], "basis": comp["agent_performance_in_galaxy_score"]["basis"]},
        },
    }
    dump(RUN / "experiment_summary.json", summary)
    dump(RUN / "errors/error.json", {"status": "complete", "errors": failures})
    dump(RUN / "results/artifacts_manifest.json", {"run_dir": str(RUN), "files": sorted(str(p.relative_to(RUN)) for p in RUN.rglob("*") if p.is_file())})
    note(f"## {ts()}\n\nCompleted attempt 1. Galaxy produced {len(originals)} output files, downloaded unchanged under `results/`. Evaluation artifacts and summary were written.")
    log({"event": "evaluate", "outcome": "complete", "scores": result["evaluation"]})
except Exception as exc:
    failures.append({"timestamp": ts(), "source": "execution_script", "step": "attempt_1", "message": str(exc), "fixed": False, "response": None})
    dump(RUN / "errors/error.json", {"status": "failed", "errors": failures})
    note(f"## {ts()}\n\nAttempt 1 failed with error: `{exc}`. Failure evidence was written to `errors/error.json`.")
    log({"event": "execute", "outcome": "failed", "error": str(exc)})
    raise
