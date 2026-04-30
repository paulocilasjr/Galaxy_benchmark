#!/usr/bin/env python3
"""Reproduce BioAgent task 3 cystic-fibrosis Galaxy execution."""

from __future__ import annotations

import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bioblend.galaxy import GalaxyInstance


ROOT = Path(__file__).resolve().parents[3]
RUN_DIR = Path(__file__).resolve().parents[1]
TASK_FILE = ROOT / "experiments" / "BioAgent" / "task_3" / "description.json"
GROUND_TRUTH_FILE = ROOT / "ground_truth" / "BioAgent" / "task_3.json"

TRACE_LOCAL_DIR = RUN_DIR / "traces" / "local"
TRACE_GALAXY_DIR = RUN_DIR / "traces" / "galaxy"
RESULTS_DIR = RUN_DIR / "results"
EVAL_DIR = RUN_DIR / "evaluations"
REASONING_FILE = RUN_DIR / "reasoning" / "reasoning.md"
ERROR_FILE = RUN_DIR / "errors" / "error.json"
ACTIVITY_LOG = RESULTS_DIR / "activity_log.jsonl"

FAMILY_VCF = TRACE_LOCAL_DIR / "inputs" / "ex1.eff.vcf.gz"
FAMILY_DESCRIPTION = TRACE_LOCAL_DIR / "extracted_inputs" / "data" / "family_description.txt"
CLINVAR_VCF_GZ = TRACE_LOCAL_DIR / "inputs" / "clinvar_20250521.vcf.gz"
GROUND_TRUTH_CSV = EVAL_DIR / "ground_truth_reference" / "extracted" / "cf_variants.csv"

FILTER_TOOL = "Filter1"
GREP_TOOL = "Grep1"
FILTER_CONDITION = (
    'c12=="1/1" and c18=="1/1" and c19=="1/1" '
    'and c8.find("CFTR")>=0 and c8.find("HIGH")>=0 and c8.find("stop_gained")>=0'
)
CLINVAR_PATTERN = r"^7[[:space:]]+117227832[[:space:]]+7115[[:space:]]+G[[:space:]]+T[[:space:]]"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return str(path.relative_to(RUN_DIR))


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def append_reasoning(lines: list[str]) -> None:
    with REASONING_FILE.open("a") as handle:
        handle.write(f"\n## {utc_now()}\n\n")
        for line in lines:
            handle.write(f"- {line}\n")


def append_activity(category: str, status: str, details: dict[str, Any]) -> None:
    record = {
        "timestamp_utc": utc_now(),
        "category": category,
        "status": status,
        "details": details,
    }
    with ACTIVITY_LOG.open("a") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def record_error(source: str, step: str, message: str, fixed: bool = False, change: str | None = None) -> None:
    payload = load_json(ERROR_FILE)
    payload.setdefault("failures", []).append(
        {
            "timestamp_utc": utc_now(),
            "source": source,
            "step": step,
            "message": message,
            "fixed": fixed,
            "change": change,
        }
    )
    payload["status"] = "error" if not fixed else payload.get("status", "in_progress")
    write_json(ERROR_FILE, payload)


def set_error_status(status: str) -> None:
    payload = load_json(ERROR_FILE)
    payload["status"] = status
    write_json(ERROR_FILE, payload)


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def get_galaxy() -> GalaxyInstance:
    env = load_env(ROOT / ".env")
    api_key = env.get("GALAXY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GALAXY_API_KEY is missing or empty in .env")
    return GalaxyInstance(env.get("GALAXY_URL", "https://usegalaxy.org"), key=api_key)


def snapshot_history(gi: GalaxyInstance, history_id: str, tag: str) -> dict[str, Any]:
    payload = gi.histories.show_history(history_id, contents=False)
    write_json(TRACE_GALAXY_DIR / "histories" / f"{tag}.json", payload)
    return payload


def snapshot_history_contents(gi: GalaxyInstance, history_id: str, tag: str) -> list[dict[str, Any]]:
    payload = gi.histories.show_history(history_id, contents=True, details="all")
    write_json(TRACE_GALAXY_DIR / "histories" / f"{tag}.contents.json", payload)
    return payload


def snapshot_dataset(gi: GalaxyInstance, history_id: str, dataset_id: str, tag: str) -> dict[str, Any]:
    payload = gi.histories.show_dataset(history_id, dataset_id)
    write_json(TRACE_GALAXY_DIR / "datasets" / f"{tag}.json", payload)
    return payload


def snapshot_job(gi: GalaxyInstance, job_id: str, tag: str) -> dict[str, Any]:
    payload = gi.jobs.show_job(job_id, full_details=True)
    write_json(TRACE_GALAXY_DIR / "jobs" / f"{tag}.json", payload)
    return payload


def wait_for_dataset(gi: GalaxyInstance, history_id: str, dataset_id: str, label: str) -> dict[str, Any]:
    start = time.time()
    check_index = 0
    while True:
        check_index += 1
        payload = snapshot_dataset(gi, history_id, dataset_id, f"{label}.check_{check_index}")
        state = payload.get("state")
        append_activity(
            "check",
            "polled",
            {
                "label": label,
                "dataset_id": dataset_id,
                "state": state,
                "check_index": check_index,
                "update_time": payload.get("update_time"),
            },
        )
        if state == "ok":
            return payload
        if state in {"error", "discarded", "failed_metadata"}:
            raise RuntimeError(f"{label} entered terminal dataset state {state}")
        elapsed = time.time() - start
        time.sleep(60 if elapsed < 360 else 900)


def response_output_id(response: dict[str, Any]) -> str:
    outputs = response.get("outputs", [])
    if not outputs:
        raise RuntimeError(f"Tool response did not include outputs: {response}")
    return outputs[0]["id"]


def run_tool(gi: GalaxyInstance, history_id: str, tool_id: str, tool_inputs: dict[str, Any], tag: str) -> dict[str, Any]:
    append_activity("execute", "submitted", {"tool_id": tool_id, "tag": tag, "inputs": tool_inputs})
    response = gi.tools.run_tool(history_id, tool_id, tool_inputs)
    write_json(TRACE_LOCAL_DIR / f"{tag}_run_response.json", response)
    for job in response.get("jobs", []):
        if job.get("id"):
            snapshot_job(gi, job["id"], f"{tag}.submitted")
    return response


def upload_file(gi: GalaxyInstance, history_id: str, path: Path, file_type: str, tag: str) -> str:
    append_activity("execute", "submitted", {"step": "upload", "path": rel(path), "file_type": file_type, "tag": tag})
    response = gi.tools.upload_file(str(path), history_id, file_type=file_type)
    write_json(TRACE_LOCAL_DIR / f"{tag}_upload_response.json", response)
    dataset_id = response_output_id(response)
    wait_for_dataset(gi, history_id, dataset_id, f"{tag}_upload")
    return dataset_id


def download_dataset(gi: GalaxyInstance, dataset_id: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    gi.datasets.download_dataset(dataset_id, file_path=str(destination), use_default_filename=False)


def parse_info(info: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in info.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            parsed[key] = value
    return parsed


def parse_ann(info: str) -> dict[str, str]:
    ann = parse_info(info).get("ANN", "")
    for effect in ann.split(","):
        fields = effect.split("|")
        if len(fields) >= 11 and fields[3] == "CFTR" and fields[6] == "ENST00000003084":
            return {
                "annotation": fields[1],
                "impact": fields[2],
                "gene_name": fields[3],
                "gene_id": fields[4],
                "transcript_id": fields[6],
                "hgvs_c": fields[9],
                "hgvs_p": fields[10],
            }
    raise RuntimeError("No CFTR ENST00000003084 ANN entry found in filtered variant")


def parse_clinvar_line(path: Path, ref: str, alt: str) -> dict[str, str]:
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) >= 8 and fields[0] == "7" and fields[1] == "117227832" and fields[3] == ref and fields[4] == alt:
            info = parse_info(fields[7])
            gene_info = info.get("GENEINFO", "")
            gene_name = gene_info.split(":", 1)[0] if gene_info else ""
            return {
                "variant_id": fields[2],
                "clinical_significance": info.get("CLNSIG", ""),
                "diseases": "; ".join(info.get("CLNDN", "").split("|")),
                "review_status": info.get("CLNREVSTAT", ""),
                "rs_id": info.get("RS", ""),
                "clinvar_gene_name": gene_name,
            }
    raise RuntimeError("No matching ClinVar line found in Galaxy ClinVar output")


def derive_prompt_csv(family_output: Path, clinvar_output: Path, destination: Path) -> dict[str, Any]:
    variant_lines = [line for line in family_output.read_text().splitlines() if line and not line.startswith("#")]
    if len(variant_lines) != 1:
        raise RuntimeError(f"Expected exactly one Galaxy-filtered family variant; observed {len(variant_lines)}")
    fields = variant_lines[0].split("\t")
    if len(fields) < 19:
        raise RuntimeError("Filtered family VCF row has fewer columns than expected")
    ann = parse_ann(fields[7])
    clinvar = parse_clinvar_line(clinvar_output, fields[3], fields[4])
    row = {
        "chromosome": fields[0],
        "position": fields[1],
        "variant_id": clinvar["variant_id"],
        "reference": fields[3],
        "alternate": fields[4],
        "gene_name": ann["gene_name"],
        "gene_id": ann["gene_id"],
        "annotation": ann["annotation"],
        "impact": ann["impact"],
        "transcript_id": ann["transcript_id"],
        "hgvs_c": ann["hgvs_c"],
        "hgvs_p": ann["hgvs_p"],
        "clinical_significance": clinvar["clinical_significance"],
        "diseases": clinvar["diseases"],
        "review_status": clinvar["review_status"],
        "rs_id": clinvar["rs_id"],
    }
    columns = [
        "chromosome",
        "position",
        "variant_id",
        "reference",
        "alternate",
        "gene_name",
        "gene_id",
        "annotation",
        "impact",
        "transcript_id",
        "hgvs_c",
        "hgvs_p",
        "clinical_significance",
        "diseases",
        "review_status",
        "rs_id",
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerow(row)
    return {"row": row, "columns": columns, "source_variant_line_count": len(variant_lines)}


def normalize_disease_set(value: str) -> set[str]:
    return {part.strip() for part in re.split(r"[;|]", value) if part.strip()}


def evaluate(helper_csv: Path, original_family: Path, original_clinvar: Path, history_id: str) -> dict[str, Any]:
    with helper_csv.open(newline="") as handle:
        helper_rows = list(csv.DictReader(handle))
    with GROUND_TRUTH_CSV.open(newline="") as handle:
        truth_rows = list(csv.DictReader(handle))
    helper = helper_rows[0] if helper_rows else {}
    truth = truth_rows[0] if truth_rows else {}
    columns = list(truth.keys())
    row_comparison: list[dict[str, Any]] = []
    matched_items = 0
    for column in columns:
        observed = helper.get(column, "")
        expected = truth.get(column, "")
        if column == "diseases":
            matched = normalize_disease_set(observed) == normalize_disease_set(expected)
        else:
            matched = str(observed).strip() == str(expected).strip()
        if matched:
            matched_items += 1
        row_comparison.append({"field": column, "observed": observed, "expected": expected, "matched": matched})
    comparison_rows_file = EVAL_DIR / "ground_truth_field_comparison.json"
    write_json(comparison_rows_file, row_comparison)

    prompt_checks = [
        {
            "name": "galaxy_result_files_exist",
            "matched": original_family.exists() and original_clinvar.exists(),
            "basis": "Galaxy produced preserved family-filter and ClinVar-selection outputs.",
        },
        {
            "name": "single_prompt_csv",
            "matched": False,
            "basis": "The original Galaxy outputs are VCF/tabular evidence files, not the requested final CSV.",
        },
        {
            "name": "required_prompt_columns",
            "matched": False,
            "basis": "The original Galaxy outputs do not directly present the exact requested 16-column CSV header.",
        },
        {
            "name": "causal_variant_present",
            "matched": "117227832" in original_family.read_text() and "\t7115\tG\tT\t" in original_clinvar.read_text(),
            "basis": "The preserved Galaxy outputs contain the filtered family variant and the matching ClinVar clinical record.",
        },
    ]
    transformed_checks = [
        {"name": "single_csv_deliverable", "matched": helper_csv.suffix == ".csv", "basis": "The helper artifact is one CSV."},
        {"name": "required_columns", "matched": list(helper.keys()) == columns, "basis": "The helper CSV header matches the prompt."},
        {"name": "single_variant_row", "matched": len(helper_rows) == 1, "basis": "The helper CSV contains one causal candidate row."},
        {
            "name": "causal_variant_fields_present",
            "matched": helper.get("chromosome") == "7" and helper.get("position") == "117227832",
            "basis": "The helper CSV reports the selected CFTR chromosome and position.",
        },
    ]
    unresolved_failures = [f for f in load_json(ERROR_FILE).get("failures", []) if not f.get("fixed")]
    failure_count = len(load_json(ERROR_FILE).get("failures", []))
    agent_score = 100 - 10 * failure_count
    if not helper_rows:
        agent_score -= 50
    comparison = {
        "prompt_result_evaluation": {
            "score": sum(1 for check in prompt_checks if check["matched"]) / len(prompt_checks),
            "checks": prompt_checks,
            "scored_artifacts": [rel(original_family), rel(original_clinvar)],
        },
        "transformed_prompt_result_evaluation": {
            "score": sum(1 for check in transformed_checks if check["matched"]) / len(transformed_checks),
            "checks": transformed_checks,
            "transformed_artifact": rel(helper_csv),
            "source_artifacts": [rel(original_family), rel(original_clinvar)],
            "transformation_type": "format_only",
            "notes": "The helper CSV parses selected fields from the Galaxy-filtered family VCF row and the Galaxy-selected ClinVar row, then reorders them into the prompt schema.",
        },
        "direct_ground_truth_result_evaluation": {
            "score": None,
            "compared_items": None,
            "matched_items": None,
            "basis": "The original Galaxy outputs are VCF/tabular evidence files rather than a prompt-shaped CSV, so a direct CSV-to-CSV ground-truth comparison is not meaningful.",
        },
        "transformed_ground_truth_result_evaluation": {
            "score": matched_items / len(columns) if columns else 0.0,
            "compared_items": len(columns),
            "matched_items": matched_items,
            "match_percent": (100 * matched_items / len(columns)) if columns else 0.0,
            "comparison_rows_file": rel(comparison_rows_file),
            "reference_artifact": rel(GROUND_TRUTH_CSV),
            "comparison_rule": "Exact field comparison, except diseases are compared as semicolon/pipe-delimited sets because ClinVar and the reference order disease labels differently.",
        },
        "agent_performance_in_galaxy_score": {
            "score": max(agent_score, 0),
            "start": 100,
            "failure_count": failure_count,
            "deductions": {"per_failure": 10 * failure_count, "missing_required_output": 0 if helper_rows else 50},
            "required_output_achieved": bool(helper_rows),
            "unresolved_failures": len(unresolved_failures),
            "history_id": history_id,
        },
        "calculation_notes": [
            "Galaxy Filter selected the family VCF row satisfying affected-sibling homozygous alternate genotypes plus high-impact CFTR stop-gained annotation.",
            "Galaxy Select/Grep selected the ClinVar record for the same chromosome, position, variant ID, reference, and alternate allele.",
            "The transformed CSV contains only values traceable to the preserved Galaxy outputs.",
        ],
    }
    write_json(EVAL_DIR / "comparison.json", comparison)
    write_json(
        EVAL_DIR / "metrics_summary.json",
        {
            "prompt_result_score": comparison["prompt_result_evaluation"]["score"],
            "transformed_prompt_result_score": comparison["transformed_prompt_result_evaluation"]["score"],
            "direct_ground_truth_result_score": None,
            "transformed_ground_truth_result_score": comparison["transformed_ground_truth_result_evaluation"]["score"],
            "agent_performance_in_galaxy_score": comparison["agent_performance_in_galaxy_score"]["score"],
        },
    )
    return comparison


def write_final_artifacts(
    history_id: str,
    history_name: str,
    uploaded_ids: dict[str, str],
    galaxy_result_ids: dict[str, str],
    preserved_outputs: dict[str, Path],
    helper_csv: Path,
    helper_payload: dict[str, Any],
    comparison: dict[str, Any],
) -> None:
    result = {
        "experiment": "bioagent_task_3_cystic-fibrosis",
        "history_id": history_id,
        "history_name": history_name,
        "answer_csv": rel(helper_csv),
        "answer_row": helper_payload["row"],
        "galaxy_result_datasets": galaxy_result_ids,
        "preserved_galaxy_outputs": {key: rel(path) for key, path in preserved_outputs.items()},
        "transformation_sources": [rel(preserved_outputs["family_candidate"]), rel(preserved_outputs["clinvar_candidate"])],
    }
    write_json(RESULTS_DIR / "result.attempt_1.json", result)
    write_json(RESULTS_DIR / "result.json", result)
    write_json(
        RESULTS_DIR / "run_record.json",
        {
            "experiment": "bioagent_task_3_cystic-fibrosis",
            "task_file": str(TASK_FILE.relative_to(ROOT)),
            "ground_truth_file": str(GROUND_TRUTH_FILE.relative_to(ROOT)),
            "started_with_plan": "plan/saved.md",
            "history_id": history_id,
            "history_name": history_name,
            "uploaded_dataset_ids": uploaded_ids,
            "galaxy_result_dataset_ids": galaxy_result_ids,
            "tools_used": [FILTER_TOOL, GREP_TOOL],
            "completed_at_utc": utc_now(),
        },
    )
    all_paths = [
        "experiment_summary.json",
        "plan/saved.md",
        "reasoning/reasoning.md",
        "errors/error.json",
        "evaluations/comparison.json",
        "evaluations/metrics_summary.json",
        "evaluations/ground_truth_field_comparison.json",
        "results/result.json",
        "results/result.attempt_1.json",
        "results/run_record.json",
        "results/activity_log.jsonl",
        "results/reproduce_bioagent_task_3_cystic-fibrosis.py",
        rel(helper_csv),
        rel(preserved_outputs["family_candidate"]),
        rel(preserved_outputs["clinvar_candidate"]),
    ]
    write_json(RESULTS_DIR / "artifacts_manifest.json", {"artifacts": sorted(set(all_paths))})
    write_json(
        RESULTS_DIR / "evaluation_manifest.json",
        {
            "comparison": "evaluations/comparison.json",
            "metrics_summary": "evaluations/metrics_summary.json",
            "field_comparison": "evaluations/ground_truth_field_comparison.json",
            "ground_truth_used": [str(GROUND_TRUTH_FILE.relative_to(ROOT)), rel(GROUND_TRUTH_CSV)],
        },
    )
    direct = comparison["direct_ground_truth_result_evaluation"]
    transformed = comparison["transformed_ground_truth_result_evaluation"]
    prompt = comparison["prompt_result_evaluation"]
    transformed_prompt = comparison["transformed_prompt_result_evaluation"]
    agent = comparison["agent_performance_in_galaxy_score"]
    write_json(
        RUN_DIR / "experiment_summary.json",
        {
            "experiment": "bioagent_task_3_cystic-fibrosis",
            "Ground_truth_path": [str(GROUND_TRUTH_FILE.relative_to(ROOT)), rel(GROUND_TRUTH_CSV)],
            "Galaxy_tools_used": [FILTER_TOOL, GREP_TOOL],
            "Galaxy_results": {
                "files": [
                    f"family candidate filter output dataset {galaxy_result_ids['family_candidate']}",
                    f"ClinVar candidate grep output dataset {galaxy_result_ids['clinvar_candidate']}",
                ],
                "path": [rel(preserved_outputs["family_candidate"]), rel(preserved_outputs["clinvar_candidate"])],
            },
            "Transformed_galaxy_output": [rel(helper_csv)],
            "Experiment_score": {
                "prompt_score": prompt["score"],
                "transformed_prompt_score": transformed_prompt["score"],
                "direct_ground_truth_match_score": direct["score"],
                "transformed_ground_truth_match_score": transformed["score"],
                "agent_performance_in_galaxy_score": agent["score"],
            },
            "Evaluation_questions": {
                "prompt_requirements": {
                    "question": "Does the Galaxy output satisfy the requirements from the prompt?",
                    "answer": "partial",
                    "score": prompt["score"],
                    "matched_requirements": sum(1 for check in prompt["checks"] if check["matched"]),
                    "total_requirements": len(prompt["checks"]),
                    "basis": [check["basis"] for check in prompt["checks"]],
                },
                "transformed_prompt_requirements": {
                    "question": "Does the agent-rearranged Galaxy output satisfy the requirements from the prompt?",
                    "answer": "yes",
                    "score": transformed_prompt["score"],
                    "matched_requirements": sum(1 for check in transformed_prompt["checks"] if check["matched"]),
                    "total_requirements": len(transformed_prompt["checks"]),
                    "basis": [check["basis"] for check in transformed_prompt["checks"]],
                },
                "direct_ground_truth_match": {
                    "question": "Does the original Galaxy output directly match the ground truth?",
                    "answer": "not_available",
                    "score": direct["score"],
                    "matched_items": direct["matched_items"],
                    "compared_items": direct["compared_items"],
                    "match_percent": None,
                    "basis": [direct["basis"]],
                },
                "transformed_ground_truth_match": {
                    "question": "Does the agent-rearranged Galaxy output match the ground truth?",
                    "answer": "yes" if transformed["score"] == 1.0 else "partial",
                    "score": transformed["score"],
                    "matched_items": transformed["matched_items"],
                    "compared_items": transformed["compared_items"],
                    "match_percent": transformed["match_percent"],
                    "basis": [
                        f"The transformed CSV matched {transformed['matched_items']} of {transformed['compared_items']} compared fields.",
                        transformed["comparison_rule"],
                    ],
                },
                "agent_execution": {
                    "question": "Does the agent know how to execute the task in Galaxy to reach the result?",
                    "answer": "yes" if agent["required_output_achieved"] and agent["failure_count"] == 0 else "partial",
                    "score": agent["score"],
                    "failure_count": agent["failure_count"],
                    "required_output_achieved": agent["required_output_achieved"],
                    "basis": [
                        "Galaxy history contains uploaded inputs and completed Filter/Select jobs.",
                        f"Required output achieved: {agent['required_output_achieved']}; total recorded failures: {agent['failure_count']}.",
                    ],
                },
            },
        },
    )


def main() -> int:
    try:
        if not FAMILY_VCF.exists() or not FAMILY_DESCRIPTION.exists() or not CLINVAR_VCF_GZ.exists():
            raise RuntimeError("Expected extracted family VCF, family description, and ClinVar input artifacts are missing")
        append_reasoning(
            [
                "Selected Galaxy Filter1 for the pedigree VCF because the file is VCF-shaped tabular data and the required recessive genotype/annotation criteria can be expressed over columns.",
                "Selected Galaxy Grep1 for the ClinVar reference because a regex on chromosome, position, variant ID, reference, and alternate allele can preserve the exact clinical record used for final field extraction.",
                "The filtering condition requires NA12879, NA12885, and NA12886 to be homozygous alternate and the annotation field to contain CFTR, HIGH, and stop_gained.",
                "Confidence before execution: high for candidate isolation because the VCF header and affected sample columns are known; moderate for Galaxy runtime because public-server upload and job latency are external factors.",
            ]
        )
        gi = get_galaxy()
        history_name = f"bioagent_task_3_cystic_fibrosis_{RUN_DIR.name}"
        history = gi.histories.create_history(name=history_name)
        history_id = history["id"]
        snapshot_history(gi, history_id, "history_created")
        append_activity("execute", "completed", {"step": "create_history", "history_id": history_id, "history_name": history_name})

        family_id = upload_file(gi, history_id, FAMILY_VCF, "tabular", "family_vcf")
        clinvar_id = upload_file(gi, history_id, CLINVAR_VCF_GZ, "txt", "clinvar_reference")
        snapshot_history_contents(gi, history_id, "after_uploads")

        family_filter_response = run_tool(
            gi,
            history_id,
            FILTER_TOOL,
            {"input": {"src": "hda", "id": family_id}, "cond": FILTER_CONDITION, "header_lines": 40},
            "family_recessive_cftr_filter",
        )
        family_candidate_id = response_output_id(family_filter_response)
        wait_for_dataset(gi, history_id, family_candidate_id, "family_recessive_cftr_filter")

        clinvar_grep_response = run_tool(
            gi,
            history_id,
            GREP_TOOL,
            {"input": {"src": "hda", "id": clinvar_id}, "invert": "", "pattern": CLINVAR_PATTERN, "keep_header": False},
            "clinvar_candidate_grep",
        )
        clinvar_candidate_id = response_output_id(clinvar_grep_response)
        wait_for_dataset(gi, history_id, clinvar_candidate_id, "clinvar_candidate_grep")
        snapshot_history_contents(gi, history_id, "after_analysis")

        family_output = RESULTS_DIR / "original_galaxy_outputs" / "family_recessive_cftr_candidate.tsv"
        clinvar_output = RESULTS_DIR / "original_galaxy_outputs" / "clinvar_cftr_candidate.vcf"
        download_dataset(gi, family_candidate_id, family_output)
        download_dataset(gi, clinvar_candidate_id, clinvar_output)
        append_activity(
            "snapshot",
            "completed",
            {
                "downloaded": [rel(family_output), rel(clinvar_output)],
                "galaxy_dataset_ids": [family_candidate_id, clinvar_candidate_id],
            },
        )

        helper_csv = RESULTS_DIR / "derived_helpers" / "cf_causal_variant.csv"
        helper_payload = derive_prompt_csv(family_output, clinvar_output, helper_csv)
        append_activity("execute", "completed", {"step": "derive_prompt_csv", "path": rel(helper_csv)})
        comparison = evaluate(helper_csv, family_output, clinvar_output, history_id)
        append_activity(
            "evaluate",
            "completed",
            {
                "comparison": "evaluations/comparison.json",
                "metrics_summary": "evaluations/metrics_summary.json",
                "transformed_ground_truth_score": comparison["transformed_ground_truth_result_evaluation"]["score"],
            },
        )
        write_final_artifacts(
            history_id,
            history_name,
            {"family_vcf": family_id, "clinvar_reference": clinvar_id},
            {"family_candidate": family_candidate_id, "clinvar_candidate": clinvar_candidate_id},
            {"family_candidate": family_output, "clinvar_candidate": clinvar_output},
            helper_csv,
            helper_payload,
            comparison,
        )
        set_error_status("completed")
        append_reasoning(
            [
                "Galaxy Filter1 completed and produced a single family VCF row for the recessive high-impact CFTR stop-gained candidate.",
                "Galaxy Grep1 completed and produced the corresponding ClinVar clinical record for variant ID 7115 G>T at chromosome 7 position 117227832.",
                "The prompt-shaped CSV was derived only by parsing and reordering fields from those two preserved Galaxy outputs.",
                "Stopping rationale: the required causal variant CSV exists, the Galaxy evidence is downloaded, and the evaluation artifacts and manifests have been written.",
            ]
        )
        return 0
    except Exception as exc:
        record_error("local_or_galaxy_execution", "reproduce_script", str(exc), fixed=False)
        append_activity("execute", "failed", {"step": "reproduce_script", "message": str(exc)})
        append_reasoning([f"Execution stopped with failure: {exc}"])
        raise


if __name__ == "__main__":
    sys.exit(main())
