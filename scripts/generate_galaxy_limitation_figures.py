#!/usr/bin/env python3
"""Generate figures showing when Galaxy constrained task accomplishment.

The script reads immutable benchmark run artifacts under outputs/ and writes
derived, reviewer-facing summaries under figures/galaxy_limitation/.
"""

from __future__ import annotations

import json
import re
import textwrap
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
FIGDIR = ROOT / "figures" / "galaxy_limitation"

GALAXY_TERMS = (
    "galaxy",
    "usegalaxy",
    "tool",
    "api",
    "job",
    "upload",
    "queue",
    "dataset entered error",
    "terminal dataset state error",
    "interactive",
    "metadata",
    "wrapper",
)
SCHEMA_TERMS = (
    "parameter",
    "selector",
    "conditional",
    "invalid option",
    "valid options",
    "metadata",
    "payload",
    "column-name",
    "column selectors",
    "space_to_tab",
)
SERVICE_TERMS = (
    "temporarily disabled",
    "queued",
    "zero-byte",
    "did not progress",
    "no stdout",
    "no stderr",
    "upload remained",
)
OUTPUT_TERMS = (
    "probability",
    "probabilities",
    "not available",
    "lacked a suitable",
    "lacked suitable",
    "wide matrices",
    "generic spearman",
)
MATERIAL_EXTERNAL_TERMS = (
    "non-galaxy preparation",
    "computed",
    "derived",
    "parsed",
    "aligned",
    "converted source excel",
    "created a log10",
    "prepared table",
    "task-specific",
    "materially shaped",
)
NO_EXTERNAL_RE = re.compile(r"no external scientific manipulation", re.I)


def load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def flatten_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True, default=str)


def as_list_errors(error_doc: Any) -> list[dict[str, Any]]:
    if not isinstance(error_doc, dict):
        return []
    errors = error_doc.get("errors")
    failures = error_doc.get("failures")
    rows: list[Any] = []
    if isinstance(errors, list):
        rows.extend(errors)
    if isinstance(failures, list):
        rows.extend(failures)
    return [r if isinstance(r, dict) else {"message": r} for r in rows]


def score_from_artifacts(summary: dict[str, Any], metrics: dict[str, Any], run_record: dict[str, Any]) -> float | None:
    exp_score = summary.get("Experiment_score") if isinstance(summary, dict) else None
    candidates: list[Any] = []
    if isinstance(exp_score, dict):
        candidates.extend(
            [
                exp_score.get("direct_ground_truth_match_score"),
                exp_score.get("transformed_ground_truth_match_score"),
                exp_score.get("prompt_score"),
                exp_score.get("bixbench_answer_score"),
            ]
        )
    if isinstance(metrics, dict):
        candidates.extend(
            [
                metrics.get("direct_ground_truth_result_score"),
                metrics.get("transformed_ground_truth_result_score"),
                metrics.get("prompt_result_score"),
                metrics.get("bixbench_answer_score"),
            ]
        )
    if isinstance(run_record, dict):
        candidates.append(run_record.get("score"))
    for value in candidates:
        if value is None:
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def agent_galaxy_score(summary: dict[str, Any], metrics: dict[str, Any]) -> float | None:
    for doc in (summary.get("Experiment_score") if isinstance(summary, dict) else None, metrics):
        if isinstance(doc, dict) and doc.get("agent_performance_in_galaxy_score") is not None:
            try:
                return float(doc["agent_performance_in_galaxy_score"])
            except (TypeError, ValueError):
                pass
    return None


def contains_any(text: str, terms: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(term in low for term in terms)


def has_missing_capability_evidence(ext: str, notes: str, calc_notes: str) -> bool:
    text = "\n".join([ext, notes, calc_notes]).lower()
    return (
        "lacked a suitable" in text
        or "lacked suitable" in text
        or "generic spearman" in text
        or "wide matrices" in text
        or ("probabilit" in text and "not available" in text)
    )


def has_galaxy_source_or_step(err: dict[str, Any]) -> bool:
    source = flatten_text(err.get("source")).lower()
    step = flatten_text(err.get("step")).lower()
    endpoint = flatten_text(err.get("tool_or_endpoint")).lower()
    source_step = f"{source} {step} {endpoint}"

    if source.startswith("local_preparation") or source.startswith("local_orchestration"):
        return False
    text = flatten_text(err).lower()
    if source.startswith("local_runner") or source.startswith("local_or_galaxy"):
        return contains_any(
            f"{source_step} {text}",
            (
                "galaxy",
                "dataset state",
                "terminal dataset state",
                "http status code",
                "conditional parameter",
                "tool",
                "api",
                "upload",
                "job",
            ),
        )
    return contains_any(source_step, GALAXY_TERMS)


def classify_run(run_dir: Path) -> dict[str, Any]:
    summary = load_json(run_dir / "experiment_summary.json") or {}
    metrics = load_json(run_dir / "evaluations" / "metrics_summary.json") or {}
    errors_doc = load_json(run_dir / "errors" / "error.json") or {}
    result = load_json(run_dir / "results" / "result.json") or {}
    run_record = load_json(run_dir / "results" / "run_record.json") or {}
    comparison = load_json(run_dir / "evaluations" / "comparison.json") or {}

    errors = as_list_errors(errors_doc)
    ext = flatten_text(summary.get("External_manipulation"))
    notes = flatten_text(result.get("notes"))
    calc_notes = flatten_text(comparison.get("calculation_notes"))
    all_text = "\n".join(
        [flatten_text(summary), flatten_text(metrics), flatten_text(errors_doc), flatten_text(result), flatten_text(run_record), flatten_text(comparison)]
    )

    galaxy_errors = []
    recovered_galaxy_errors = []
    unrecovered_galaxy_errors = []
    schema_or_api = []
    queue_or_disabled = []
    for err in errors:
        text = flatten_text(err)
        is_galaxy = has_galaxy_source_or_step(err) or (
            not flatten_text(err.get("source")).lower().startswith(("local_preparation", "local_orchestration"))
            and contains_any(text, ("usegalaxy.org", "galaxy api", "galaxy job", "galaxy tool", "galaxy upload"))
        )
        if is_galaxy:
            galaxy_errors.append(err)
            if err.get("fixed") is False:
                unrecovered_galaxy_errors.append(err)
            elif err.get("fixed") is True:
                recovered_galaxy_errors.append(err)
        if is_galaxy and contains_any(text, SCHEMA_TERMS):
            schema_or_api.append(err)
        if is_galaxy and contains_any(text, SERVICE_TERMS):
            queue_or_disabled.append(err)

    material_external = bool(ext and not NO_EXTERNAL_RE.search(ext) and contains_any(ext, MATERIAL_EXTERNAL_TERMS))
    missing_tool_or_output = has_missing_capability_evidence(ext, notes, calc_notes)
    service_constraint = bool(queue_or_disabled) or contains_any("\n".join([ext, notes, calc_notes]), SERVICE_TERMS)
    schema_constraint = bool(schema_or_api)
    galaxy_error = bool(galaxy_errors)

    outcome_score = score_from_artifacts(summary, metrics, run_record)
    success = outcome_score is not None and outcome_score >= 0.999
    submitted = "submitted" in flatten_text(result).lower() or "final_answer" in flatten_text(run_record).lower()
    attempted = bool(summary or result or run_record)
    galaxy_tools = summary.get("Galaxy_tools_used") if isinstance(summary, dict) else []
    galaxy_results = summary.get("Galaxy_results") if isinstance(summary, dict) else {}
    has_galaxy_route = bool(galaxy_tools) or bool((galaxy_results or {}).get("files")) or bool((galaxy_results or {}).get("path"))
    scored_galaxy_only_route = has_galaxy_route and outcome_score is not None and not material_external

    if unrecovered_galaxy_errors or (galaxy_error and outcome_score in (None, 0.0) and not material_external):
        limitation_class = "Galaxy-blocked failure"
    elif material_external and success:
        limitation_class = "Galaxy-limited, solved via workaround"
    elif material_external and not success:
        limitation_class = "Galaxy-limited, workaround insufficient"
    elif galaxy_error and success:
        limitation_class = "Galaxy friction recovered"
    elif galaxy_error:
        limitation_class = "Galaxy friction, final failure"
    elif scored_galaxy_only_route:
        limitation_class = "No explicit Galaxy limitation"
    else:
        limitation_class = "Excluded: incomplete/no scored Galaxy-only route"

    if limitation_class == "No explicit Galaxy limitation":
        primary_signal = "none"
    elif material_external:
        primary_signal = "external workaround"
    elif service_constraint:
        primary_signal = "service/queue/disabled"
    elif missing_tool_or_output:
        primary_signal = "missing output/tool capability"
    elif schema_constraint:
        primary_signal = "API/schema friction"
    elif galaxy_error:
        primary_signal = "Galaxy job/tool error"
    else:
        primary_signal = "other"

    return {
        "run_id": run_dir.name,
        "experiment": summary.get("experiment") or result.get("experiment") or run_record.get("experiment") or run_record.get("task") or run_dir.name,
        "outcome_score": outcome_score,
        "success": success,
        "attempted": attempted,
        "submitted": submitted,
        "agent_performance_in_galaxy_score": agent_galaxy_score(summary, metrics),
        "limitation_class": limitation_class,
        "primary_signal": primary_signal,
        "has_galaxy_limitation_evidence": limitation_class != "No explicit Galaxy limitation",
        "material_external_workaround": material_external,
        "missing_tool_or_output_capability": missing_tool_or_output,
        "schema_or_api_constraint": schema_constraint,
        "service_or_queue_constraint": service_constraint,
        "galaxy_error_count": len(galaxy_errors),
        "recovered_galaxy_error_count": len(recovered_galaxy_errors),
        "unrecovered_galaxy_error_count": len(unrecovered_galaxy_errors),
        "total_error_count": len(errors),
        "has_galaxy_route": has_galaxy_route,
        "included_in_figures": limitation_class != "Excluded: incomplete/no scored Galaxy-only route",
        "external_manipulation": ext,
        "notes": notes,
        "evidence_excerpt": evidence_excerpt(ext, notes, galaxy_errors, all_text),
    }


def evidence_excerpt(ext: str, notes: str, galaxy_errors: list[dict[str, Any]], all_text: str) -> str:
    pieces: list[str] = []
    if ext and not NO_EXTERNAL_RE.search(ext):
        pieces.append(ext)
    if notes:
        pieces.append(notes)
    for err in galaxy_errors[:2]:
        pieces.append(flatten_text(err.get("message") or err))
    if not pieces and contains_any(all_text, OUTPUT_TERMS + SERVICE_TERMS):
        pieces.append(all_text[:220])
    text = " | ".join(pieces)
    return re.sub(r"\s+", " ", text).strip()[:600]


def savefig(name: str) -> None:
    for ext in ("png", "svg"):
        plt.savefig(FIGDIR / f"{name}.{ext}", dpi=220, bbox_inches="tight")
    plt.close()


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 10,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#4b5563",
            "axes.grid": False,
            "grid.color": "#e5e7eb",
            "grid.linewidth": 0.8,
            "legend.frameon": False,
        }
    )


def plot_class_counts(df: pd.DataFrame) -> None:
    order = [
        "No explicit Galaxy limitation",
        "Galaxy friction recovered",
        "Galaxy friction, final failure",
        "Galaxy-limited, solved via workaround",
        "Galaxy-limited, workaround insufficient",
        "Galaxy-blocked failure",
    ]
    d = df.copy()
    d["outcome"] = d["success"].map({True: "success", False: "not successful"})
    counts = d.groupby(["limitation_class", "outcome"]).size().unstack(fill_value=0).reindex(order, fill_value=0)
    fig, (ax, ax_note) = plt.subplots(
        ncols=2,
        figsize=(15.5, 7.8),
        gridspec_kw={"width_ratios": [1.35, 1.0], "wspace": 0.2},
    )
    counts[["success", "not successful"]].plot(
        kind="barh",
        stacked=True,
        color=["#2f7d62", "#b64f4f"],
        ax=ax,
    )
    ax.set_title("Run outcomes grouped by Galaxy-limitation evidence")
    ax.set_xlabel("Number of runs")
    ax.set_ylabel("")
    for container in ax.containers:
        ax.bar_label(container, label_type="center", color="white", fontsize=9)
    ax.legend(title="")
    explanation = (
        "Categories are assigned from run artifacts: Galaxy errors, API/schema friction, "
        "disabled/queued services, missing Galaxy capability, or recorded non-Galaxy workarounds.\n"
        "Success/not successful are outcome overlays inside each category: the same limitation type "
        "can end in a correct answer after recovery/workaround, or fail if the workaround/recovery was insufficient."
    )
    ax.text(
        0.0,
        -0.24,
        textwrap.fill(explanation, width=130),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color="#374151",
    )
    ax_note.axis("off")
    category_notes = [
        (
            "Galaxy-blocked failure",
            "Galaxy appears to have prevented normal completion through unrecovered tool/job/API, service, upload, or wrapper constraints.",
        ),
        (
            "Galaxy-limited, workaround insufficient",
            "The agent did material non-Galaxy preparation because Galaxy constrained the route, but the final answer was still unsuccessful.",
        ),
        (
            "Galaxy-limited, solved via workaround",
            "The agent did material non-Galaxy preparation because Galaxy could not carry the full route, and the final answer was successful.",
        ),
        (
            "Galaxy friction, final failure",
            "Galaxy friction remained associated with failure, but evidence did not show a full block or workaround-driven route.",
        ),
        (
            "Galaxy friction recovered",
            "Galaxy/API/tool/upload friction occurred, but the agent recovered and reached a successful final answer.",
        ),
        (
            "No explicit Galaxy limitation",
            "No artifact evidence of a Galaxy-specific blocker, missing Galaxy capability, or material non-Galaxy workaround.",
        ),
    ]
    y = 0.98
    ax_note.text(0, y, "How to read the categories", fontsize=12.5, fontweight="bold", va="top", color="#111827")
    y -= 0.065
    for title, detail in category_notes:
        ax_note.text(0, y, f"- {title}", fontsize=9.7, fontweight="bold", va="top", color="#111827")
        y -= 0.038
        ax_note.text(
            0.035,
            y,
            textwrap.fill(detail, width=58),
            fontsize=8.8,
            va="top",
            color="#374151",
            linespacing=1.18,
        )
        y -= 0.105 if len(detail) < 130 else 0.13
    savefig("01_outcomes_by_limitation_class")


def plot_signal_counts(df: pd.DataFrame) -> None:
    signal_cols = [
        ("material_external_workaround", "Non-Galaxy workaround"),
        ("schema_or_api_constraint", "API/schema friction"),
        ("service_or_queue_constraint", "Queue/service disabled"),
        ("missing_tool_or_output_capability", "Missing output/tool capability"),
    ]
    rows = []
    for col, label in signal_cols:
        sub = df[df[col]]
        rows.append(
            {
                "signal": label,
                "success": int(sub["success"].sum()),
                "not successful": int((~sub["success"]).sum()),
            }
        )
    table = pd.DataFrame(rows).set_index("signal")
    ax = table[["success", "not successful"]].plot(
        kind="bar",
        stacked=True,
        color=["#2f7d62", "#b64f4f"],
        figsize=(9, 5.5),
        rot=20,
    )
    ax.set_title("What kind of Galaxy constraint appeared in the evidence?")
    ax.set_xlabel("")
    ax.set_ylabel("Runs with signal")
    for container in ax.containers:
        ax.bar_label(container, label_type="center", color="white", fontsize=9)
    savefig("02_limitation_signal_counts")


def plot_workaround_vs_score(df: pd.DataFrame) -> None:
    d = df[df["outcome_score"].notna()].copy()
    d["workaround_intensity"] = (
        d["material_external_workaround"].astype(int) * 2
        + d["schema_or_api_constraint"].astype(int)
        + d["service_or_queue_constraint"].astype(int)
        + d["missing_tool_or_output_capability"].astype(int)
        + d["recovered_galaxy_error_count"].clip(upper=4) * 0.25
        + d["unrecovered_galaxy_error_count"].clip(upper=4) * 0.5
    )
    colors = {
        "No explicit Galaxy limitation": "#6b7280",
        "Galaxy friction recovered": "#5c7cfa",
        "Galaxy friction, final failure": "#c77d20",
        "Galaxy-limited, solved via workaround": "#2f7d62",
        "Galaxy-limited, workaround insufficient": "#b64f4f",
        "Galaxy-blocked failure": "#7c3aed",
    }
    plt.figure(figsize=(9.5, 5.8))
    for cls, sub in d.groupby("limitation_class"):
        plt.scatter(
            sub["workaround_intensity"],
            sub["outcome_score"],
            s=42 + sub["galaxy_error_count"].clip(upper=10) * 10,
            alpha=0.78,
            label=cls,
            color=colors.get(cls, "#111827"),
            edgecolor="white",
            linewidth=0.6,
        )
    plt.title("Outcome score vs. evidence that Galaxy constrained the route")
    plt.xlabel("Constraint/workaround intensity (derived from artifacts)")
    plt.ylabel("Outcome score")
    plt.ylim(-0.06, 1.06)
    plt.legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
    savefig("03_outcome_vs_constraint_intensity")


def plot_evidence_heatmap(df: pd.DataFrame) -> None:
    d = df[df["has_galaxy_limitation_evidence"]].copy()
    if d.empty:
        return
    d["sort_key"] = (
        d["material_external_workaround"].astype(int) * 4
        + d["unrecovered_galaxy_error_count"].clip(upper=3)
        + (1 - d["success"].astype(int)) * 2
    )
    d = d.sort_values(["sort_key", "run_id"], ascending=[False, True]).head(45)
    cols = [
        ("material_external_workaround", "external\nworkaround"),
        ("schema_or_api_constraint", "API/schema\nfriction"),
        ("service_or_queue_constraint", "service/queue\nconstraint"),
        ("missing_tool_or_output_capability", "missing\ncapability"),
        ("success", "success"),
    ]
    matrix = d[[c for c, _ in cols]].astype(int).to_numpy()
    labels = [label for _, label in cols]
    ylabels = [short_label(r) for r in d["run_id"]]
    plt.figure(figsize=(8.8, max(6, len(d) * 0.23)))
    plt.imshow(matrix, cmap=plt.get_cmap("YlGnBu", 2), aspect="auto", vmin=0, vmax=1)
    plt.xticks(range(len(labels)), labels)
    plt.yticks(range(len(ylabels)), ylabels, fontsize=7)
    plt.title("Run-level evidence matrix for Galaxy-limited cases")
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            plt.text(j, i, "1" if matrix[i, j] else "", ha="center", va="center", fontsize=7, color="#111827")
    plt.grid(False)
    savefig("04_galaxy_limitation_evidence_matrix")


def benchmark_group(run_id: str, experiment: str) -> str:
    text = f"{run_id} {experiment}".lower()
    if "bioagent" in text:
        return "BioAgent"
    if "low_context" in text or "medium_experiment" in text or "high_context" in text:
        return "GalaxyBench"
    if "bixbench" in text:
        return "BixBench"
    return "Other"


def plot_galaxy_only_vs_workaround(df: pd.DataFrame, excluded_count: int) -> None:
    d = df[df["outcome_score"].notna()].copy()
    d = d[d["has_galaxy_route"]]
    d["benchmark_group"] = [benchmark_group(r, e) for r, e in zip(d["run_id"], d["experiment"])]
    d["execution_route"] = d["material_external_workaround"].map(
        {
            False: "All inside Galaxy\n(no agent data manipulation)",
            True: "External + Galaxy\n(agent data manipulation)",
        }
    )
    order = [
        "All inside Galaxy\n(no agent data manipulation)",
        "External + Galaxy\n(agent data manipulation)",
    ]
    origins = ["BixBench", "BioAgent", "GalaxyBench", "Other"]
    origin_colors = {
        "BixBench": "#4c78a8",
        "BioAgent": "#f58518",
        "GalaxyBench": "#54a24b",
        "Other": "#9ca3af",
    }
    fig, ax = plt.subplots(figsize=(12.2, 7.2))
    fig.subplots_adjust(left=0.08, right=0.82, top=0.9, bottom=0.28)
    x_positions = [0.0, 0.72, 1.9, 2.62]
    bar_labels = ["Failure", "Success", "Failure", "Success"]
    route_centers = [0.36, 2.26]
    route_totals = []
    bottom = [0, 0, 0, 0]
    for origin in origins:
        heights = []
        for route in order:
            for success_value in [False, True]:
                heights.append(
                    int(
                        (
                            (d["execution_route"] == route)
                            & (d["success"] == success_value)
                            & (d["benchmark_group"] == origin)
                        ).sum()
                    )
                )
        ax.bar(
            x_positions,
            heights,
            bottom=bottom,
            width=0.52,
            color=origin_colors[origin],
            label=origin,
            edgecolor="white",
            linewidth=0.8,
        )
        for x, h, b in zip(x_positions, heights, bottom):
            if h:
                ax.text(x, b + h / 2, str(h), ha="center", va="center", fontsize=9.5, color="white", fontweight="bold")
        bottom = [b + h for b, h in zip(bottom, heights)]
    for route in order:
        route_totals.append(int((d["execution_route"] == route).sum()))
    for x, total in zip(x_positions, bottom):
        ax.text(x, total + 0.65, f"n={int(total)}", ha="center", va="bottom", fontsize=10, color="#111827")
    ax.set_title("Task outcomes by execution route")
    ax.set_xlabel("")
    ax.set_ylabel("Number of scored runs")
    ax.set_xticks(x_positions)
    ax.set_xticklabels(bar_labels, fontsize=10)
    ax.text(route_centers[0], -0.105, order[0], transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=10)
    ax.text(route_centers[1], -0.105, order[1], transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=10)
    ax.axvline(1.31, color="#d1d5db", linewidth=1)
    ax.set_xlim(-0.45, 3.08)
    ax.set_ylim(0, max(bottom) + 4)
    group_counts = Counter(d["benchmark_group"])
    handles, labels = ax.get_legend_handles_labels()
    filtered = [(h, label) for h, label in zip(handles, labels) if group_counts.get(label, 0)]
    ax.legend(
        [h for h, _ in filtered],
        [label for _, label in filtered],
        title="Task origin",
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        borderaxespad=0,
    )
    note = (
        f"BixBench tasks = {group_counts.get('BixBench', 0)}; "
        f"BioAgent = {group_counts.get('BioAgent', 0)}; "
        f"GalaxyBench = {group_counts.get('GalaxyBench', 0)}; "
        f"Unscored/incomplete runs not considered = {excluded_count}."
    )
    ax.text(
        0,
        -0.24,
        textwrap.fill(note, width=135),
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9.2,
        color="#374151",
    )
    savefig("05_galaxy_only_vs_nongalaxy_workaround")


def short_label(run_id: str) -> str:
    label = re.sub(r"^2026\d{4}T?\d*Z?_", "", run_id)
    return label[:58]


def write_methodology(df: pd.DataFrame, excluded_count: int) -> None:
    total = len(df)
    limited = int(df["has_galaxy_limitation_evidence"].sum())
    material = int(df["material_external_workaround"].sum())
    blocked = int((df["limitation_class"] == "Galaxy-blocked failure").sum())
    solved_workaround = int((df["limitation_class"] == "Galaxy-limited, solved via workaround").sum())
    insuff = int((df["limitation_class"] == "Galaxy-limited, workaround insufficient").sum())
    text = f"""# Galaxy Limitation Figure Notes

This directory contains derived figures generated from immutable artifacts under `outputs/`.

Run count read: {total}

Runs excluded from plots because they lacked a scored Galaxy-only route and had no explicit Galaxy-limitation evidence: {excluded_count}

Runs with explicit Galaxy-limitation evidence: {limited}

Runs with material non-Galaxy workaround evidence: {material}

Galaxy-blocked failures: {blocked}

Galaxy-limited runs solved via workaround: {solved_workaround}

Galaxy-limited runs where workaround was insufficient: {insuff}

Classification is evidence-based and conservative. A run is marked as Galaxy-limited when one or more stored artifacts indicate Galaxy-specific constraints, including Galaxy/API/job/upload errors, queue or disabled-service events, wrapper/schema friction, missing Galaxy output capability, or `External_manipulation` text saying non-Galaxy processing materially prepared task-specific inputs before Galaxy performed final extraction. The `No explicit Galaxy limitation` group is reserved for scored runs with Galaxy tools/results and no material non-Galaxy workaround.

These plots are intended to show when Galaxy constrained task accomplishment, not to score ordinary agent mistakes. Local preparation errors without Galaxy evidence remain outside the Galaxy-limitation classes.
"""
    (FIGDIR / "README.md").write_text(text)


def route_summary(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    d = df[df["outcome_score"].notna() & df["has_galaxy_route"]].copy()
    out = {
        "all_inside_galaxy": {"success": 0, "failure": 0},
        "non_galaxy_workaround": {"success": 0, "failure": 0},
    }
    for workaround, sub in d.groupby("material_external_workaround"):
        key = "non_galaxy_workaround" if bool(workaround) else "all_inside_galaxy"
        out[key]["success"] = int(sub["success"].sum())
        out[key]["failure"] = int((~sub["success"]).sum())
    return out


def main() -> None:
    FIGDIR.mkdir(parents=True, exist_ok=True)
    rows = [
        classify_run(p)
        for p in sorted(OUTPUTS.iterdir())
        if p.is_dir() and "paramrerun" not in p.name and (p / "experiment_summary.json").exists()
    ]
    df_all = pd.DataFrame(rows)
    df_all.to_csv(FIGDIR / "galaxy_limitation_run_classification.csv", index=False)
    (FIGDIR / "galaxy_limitation_run_classification.json").write_text(json.dumps(rows, indent=2, sort_keys=True))
    df = df_all[df_all["included_in_figures"]].copy()
    excluded_count = int((~df_all["included_in_figures"]).sum())

    summary = {
        "total_runs": int(len(df)),
        "excluded_unscored_no_limitation_runs": excluded_count,
        "by_limitation_class": Counter(df["limitation_class"]).most_common(),
        "by_primary_signal": Counter(df["primary_signal"]).most_common(),
        "galaxy_only_vs_workaround": route_summary(df),
        "success_by_limitation_class": df.groupby("limitation_class")["success"].sum().astype(int).to_dict(),
    }
    (FIGDIR / "galaxy_limitation_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))

    setup_style()
    plot_class_counts(df)
    plot_signal_counts(df)
    plot_workaround_vs_score(df)
    plot_evidence_heatmap(df)
    plot_galaxy_only_vs_workaround(df, excluded_count)
    write_methodology(df, excluded_count)
    print(f"Wrote {len(rows)} run classifications and figures from {len(df)} included runs to {FIGDIR}")


if __name__ == "__main__":
    main()
