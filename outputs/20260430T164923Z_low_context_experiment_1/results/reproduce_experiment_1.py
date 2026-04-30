#!/usr/bin/env python3
"""Replay Galaxy execution for low_context experiment_1."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from bioblend.galaxy import GalaxyInstance

RUN_DIR = Path(__file__).resolve().parents[1]
ROOT = RUN_DIR.parents[1]
GALAXY_URL = os.environ.get("GALAXY_URL", "https://usegalaxy.org")
TRAIN = ROOT / "dataset/experiment_1/Chowell_train_Response.tsv"
TEST = ROOT / "dataset/experiment_1/Chowell_test_Response.tsv"
CUT_TOOL = "Cut1"
DROP_HEADER_TOOL = "Remove beginning1"
TRAIN_TOOL = "toolshed.g2.bx.psu.edu/repos/bgruening/sklearn_generalized_linear/sklearn_generalized_linear/1.0.7.12"
PREDICT_TOOL = "toolshed.g2.bx.psu.edu/repos/bgruening/model_prediction/model_prediction/1.0.8.4"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_key() -> str:
    if os.environ.get("GALAXY_API_KEY"):
        return os.environ["GALAXY_API_KEY"]
    for line in (ROOT / ".env").read_text().splitlines():
        if line.startswith("GALAXY_API_KEY=") and line.split("=", 1)[1].strip():
            return line.split("=", 1)[1].strip()
    raise RuntimeError("GALAXY_API_KEY is missing")


def ref(dataset_id: str) -> dict:
    return {"src": "hda", "id": dataset_id}


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True))


def append_log(event: str, outcome: str, **extra) -> None:
    rec = {"timestamp": now(), "event": event, "outcome": outcome}
    rec.update(extra)
    with (RUN_DIR / "results/activity_log.jsonl").open("a") as handle:
        handle.write(json.dumps(rec, sort_keys=True) + "\n")


def wait_new_outputs(gi: GalaxyInstance, history_id: str, min_ok_hids: int, label: str) -> list[dict]:
    waited = 0
    sleep_seconds = 60
    while True:
        contents = gi.histories.show_history(history_id, contents=True)
        write_json(RUN_DIR / f"traces/galaxy/histories/contents_{label}_{waited}.json", contents)
        ok = [item for item in contents if item.get("state") == "ok"]
        append_log("check", f"poll {label}", waited_seconds=waited, ok_count=len(ok))
        if len(ok) >= min_ok_hids:
            return contents
        terminal_new_errors = [item for item in contents if item.get("state") == "error" and item.get("hid", 0) >= min_ok_hids]
        if terminal_new_errors:
            raise RuntimeError(f"Galaxy step {label} produced error datasets: {terminal_new_errors}")
        time.sleep(sleep_seconds)
        waited += sleep_seconds
        if waited >= 360:
            sleep_seconds = 900


def main() -> None:
    gi = GalaxyInstance(url=GALAXY_URL, key=load_key())
    history = gi.histories.create_history(name=f"GalaxyBench experiment_1 {now()}")
    history_id = history["id"]
    write_json(RUN_DIR / "traces/galaxy/histories/created_history_replay.json", history)
    append_log("execute", "created Galaxy history", history_id=history_id)

    train_upload = gi.tools.upload_file(str(TRAIN), history_id, file_type="tabular")
    test_upload = gi.tools.upload_file(str(TEST), history_id, file_type="tabular")
    write_json(RUN_DIR / "traces/galaxy/datasets/replay_upload_train.json", train_upload)
    write_json(RUN_DIR / "traces/galaxy/datasets/replay_upload_test.json", test_upload)
    contents = wait_new_outputs(gi, history_id, 2, "replay_upload")
    by_hid = {item["hid"]: item for item in contents}

    for label, dataset_id, columns in [
        ("train_features", by_hid[1]["id"], ",".join(f"c{i}" for i in range(1, 22))),
        ("train_labels", by_hid[1]["id"], "c22"),
        ("test_features", by_hid[2]["id"], ",".join(f"c{i}" for i in range(1, 22))),
    ]:
        params = {"columnList": columns, "delimiter": "T", "input": ref(dataset_id)}
        write_json(RUN_DIR / f"traces/galaxy/jobs/replay_cut_{label}_submission.json", gi.tools.run_tool(history_id, CUT_TOOL, params))
        append_log("execute", f"submitted cut {label}", parameters=params)
    contents = wait_new_outputs(gi, history_id, 5, "replay_cut")
    by_hid = {item["hid"]: item for item in contents}

    for label, hid in [("train_features", 3), ("train_labels", 4), ("test_features", 5)]:
        params = {"num_lines": "1", "input": ref(by_hid[hid]["id"])}
        write_json(RUN_DIR / f"traces/galaxy/jobs/replay_drop_header_{label}_submission.json", gi.tools.run_tool(history_id, DROP_HEADER_TOOL, params))
        append_log("execute", f"submitted header removal {label}", parameters=params)
    contents = wait_new_outputs(gi, history_id, 8, "replay_drop_header")
    by_hid = {item["hid"]: item for item in contents}

    train_params = {
        "selected_tasks|selected_task": "train",
        "selected_tasks|selected_algorithms|selected_algorithm": "LogisticRegression",
        "selected_tasks|selected_algorithms|input_options|selected_input": "tabular",
        "selected_tasks|selected_algorithms|input_options|infile1": ref(by_hid[6]["id"]),
        "selected_tasks|selected_algorithms|input_options|header1": "boolfalse",
        "selected_tasks|selected_algorithms|input_options|column_selector_options_1|selected_column_selector_option": "all_columns",
        "selected_tasks|selected_algorithms|input_options|infile2": ref(by_hid[7]["id"]),
        "selected_tasks|selected_algorithms|input_options|header2": "boolfalse",
        "selected_tasks|selected_algorithms|input_options|column_selector_options_2|selected_column_selector_option2": "all_columns",
        "selected_tasks|selected_algorithms|options|penalty": "l2",
        "selected_tasks|selected_algorithms|options|dual": "boolfalse",
        "selected_tasks|selected_algorithms|options|tol": "0.0001",
        "selected_tasks|selected_algorithms|options|C": "1.0",
        "selected_tasks|selected_algorithms|options|fit_intercept": "booltrue",
        "selected_tasks|selected_algorithms|options|max_iter": "100",
        "selected_tasks|selected_algorithms|options|warm_start": "boolfalse",
        "selected_tasks|selected_algorithms|options|solver": "liblinear",
        "selected_tasks|selected_algorithms|options|intercept_scaling": "1.0",
        "selected_tasks|selected_algorithms|options|multi_class": "ovr",
        "selected_tasks|selected_algorithms|options|random_state": "42",
    }
    write_json(RUN_DIR / "traces/galaxy/jobs/replay_train_submission.json", gi.tools.run_tool(history_id, TRAIN_TOOL, train_params))
    append_log("execute", "submitted logistic regression training", tool_id=TRAIN_TOOL)
    contents = wait_new_outputs(gi, history_id, 9, "replay_train")
    by_hid = {item["hid"]: item for item in contents}

    predict_params = {
        "infile_estimator": ref(by_hid[9]["id"]),
        "method": "predict",
        "input_options|selected_input": "tabular",
        "input_options|infile1": ref(by_hid[8]["id"]),
        "input_options|header1": "boolfalse",
        "input_options|column_selector_options_1|selected_column_selector_option": "all_columns",
    }
    write_json(RUN_DIR / "traces/galaxy/jobs/replay_prediction_submission.json", gi.tools.run_tool(history_id, PREDICT_TOOL, predict_params))
    append_log("execute", "submitted model prediction", tool_id=PREDICT_TOOL)
    contents = wait_new_outputs(gi, history_id, 10, "replay_prediction")
    by_hid = {item["hid"]: item for item in contents}
    out = RUN_DIR / "results/galaxy_prediction_output_original.tsv"
    gi.datasets.download_dataset(by_hid[10]["id"], file_path=str(out), use_default_filename=False)
    append_log("snapshot", "downloaded final Galaxy prediction output", path=str(out.relative_to(RUN_DIR)))


if __name__ == "__main__":
    main()
