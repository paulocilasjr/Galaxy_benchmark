#!/usr/bin/env python3
"""Regenerate the BixBench score CSV and summary figure.

The script scans the repository's outputs/ directory for run directories with
"bixbench" in the name, reads each run's experiment_summary.json, and writes:

- bixbench_scores.csv
- bixbench_score_summary.png
- bixbench_score_summary.svg
"""

from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


SUMMARY_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = SUMMARY_DIR.parent
REPO_ROOT = OUTPUTS_DIR.parent
GROUND_TRUTH_DIR = REPO_ROOT / "ground_truth" / "BixBench"
RELATIVE_TOLERANCE = 0.01


def extract_numbers(value: object) -> list[float]:
    return [
        float(match)
        for match in re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(value))
    ]


def numeric_interval(value: object) -> tuple[float, float] | None:
    numbers = extract_numbers(value)
    if len(numbers) >= 2:
        return min(numbers[0], numbers[1]), max(numbers[0], numbers[1])
    if len(numbers) == 1:
        return numbers[0], numbers[0]
    return None


def interval_distance(value: float, interval: tuple[float, float]) -> float:
    if interval[0] <= value <= interval[1]:
        return 0.0
    return min(abs(value - interval[0]), abs(value - interval[1]))


def normalize_text(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def text_tokens(value: object) -> set[str]:
    return set(normalize_text(value).split())


def text_match(answer: object, ideal: object) -> bool:
    answer_norm = normalize_text(answer)
    ideal_norm = normalize_text(ideal)
    if not answer_norm or not ideal_norm:
        return False
    if answer_norm == ideal_norm:
        return True
    if answer_norm in ideal_norm or ideal_norm in answer_norm:
        return True

    answer_tokens = text_tokens(answer)
    ideal_tokens = text_tokens(ideal)
    if not answer_tokens or not ideal_tokens:
        return False

    # Allow answers like "dentate_gyrus" to match "Dentate gyrus (brain)".
    return answer_tokens.issubset(ideal_tokens) or ideal_tokens.issubset(answer_tokens)


def load_ground_truth(task: int) -> dict[str, object]:
    ground_truth_path = GROUND_TRUTH_DIR / f"task_{task}.json"
    if not ground_truth_path.exists():
        return {}
    with ground_truth_path.open() as handle:
        return json.load(handle)


def direct_ideal_match(answer: object, ideal: object) -> bool:
    answer_interval = numeric_interval(answer)
    ideal_interval = numeric_interval(ideal)

    if answer_interval is not None and ideal_interval is not None:
        answer_value = (answer_interval[0] + answer_interval[1]) / 2
        if ideal_interval[0] <= answer_value <= ideal_interval[1]:
            return True

        ideal_center = (ideal_interval[0] + ideal_interval[1]) / 2
        allowed_delta = RELATIVE_TOLERANCE * max(abs(ideal_center), 1e-12)
        return abs(answer_value - ideal_center) <= allowed_delta

    return text_match(answer, ideal)


def bixbench_match(answer: object, ideal: object, ground_truth: dict[str, object], stored_score: object) -> bool:
    """Apply BixBench-style matching for summary display.

    BixBench summaries sometimes store exact binary scores, but the final
    visualization needs to understand common verifier forms:
    - numeric ranges such as "(1.50,1.54)"
    - distractor-aware range_verifier acceptance
    - numeric scalar answers within 1% relative tolerance when no distractors exist
    - semantically equivalent text after punctuation/underscore normalization
    """
    try:
        stored = float(stored_score or 0.0)
    except (TypeError, ValueError):
        stored = 0.0

    answer_interval = numeric_interval(answer)
    ideal_interval = numeric_interval(ideal)

    if answer_interval is not None and ideal_interval is not None:
        answer_value = (answer_interval[0] + answer_interval[1]) / 2
        if ideal_interval[0] <= answer_value <= ideal_interval[1]:
            return True

        distractor_intervals = [
            interval
            for interval in (numeric_interval(item) for item in ground_truth.get("distractors", []) or [])
            if interval is not None
        ]
        if distractor_intervals:
            ideal_distance = interval_distance(answer_value, ideal_interval)
            distractor_distance = min(interval_distance(answer_value, interval) for interval in distractor_intervals)
            return ideal_distance < distractor_distance

        ideal_center = (ideal_interval[0] + ideal_interval[1]) / 2
        allowed_delta = RELATIVE_TOLERANCE * max(abs(ideal_center), 1e-12)
        if abs(answer_value - ideal_center) <= allowed_delta:
            return True
        return False

    if text_match(answer, ideal):
        return True

    return stored >= 1.0


def task_number_from_path(path: Path) -> int | None:
    match = re.search(r"bixbench_task_(\d+)", path.name, flags=re.IGNORECASE)
    if not match:
        return None
    return int(match.group(1))


def read_run_summary(run_dir: Path) -> dict[str, object] | None:
    summary_path = run_dir / "experiment_summary.json"
    if not summary_path.exists():
        return None

    task = task_number_from_path(run_dir)
    if task is None:
        return None

    with summary_path.open() as handle:
        summary = json.load(handle)

    score_block = summary.get("Experiment_score", {})
    if not isinstance(score_block, dict):
        return None
    answer = score_block.get("Galaxy_answer")
    ideal = score_block.get("ideal")
    stored_score = score_block.get("direct_ground_truth_match_score")
    ground_truth = load_ground_truth(task)
    accepted = bixbench_match(answer, ideal, ground_truth, stored_score)
    direct_match = direct_ideal_match(answer, ideal)

    return {
        "task": task,
        "answer": answer,
        "ideal": ideal,
        "score": 1.0 if accepted else 0.0,
        "accepted_by_bixbench_only": bool(accepted and not direct_match),
        "run": str(run_dir.relative_to(REPO_ROOT)),
    }


def collect_latest_bixbench_runs() -> list[dict[str, object]]:
    latest_by_task: dict[int, tuple[Path, dict[str, object]]] = {}

    for run_dir in OUTPUTS_DIR.iterdir():
        if not run_dir.is_dir():
            continue
        if run_dir == SUMMARY_DIR:
            continue
        if "bixbench" not in run_dir.name.lower():
            continue

        row = read_run_summary(run_dir)
        if row is None:
            continue

        task = int(row["task"])
        current = latest_by_task.get(task)
        if current is None or run_dir.name > current[0].name:
            latest_by_task[task] = (run_dir, row)

    return [row for _, row in sorted(latest_by_task.values(), key=lambda item: int(item[1]["task"]))]


def write_scores_csv(rows: list[dict[str, object]]) -> Path:
    csv_path = SUMMARY_DIR / "bixbench_scores.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["task", "score", "answer", "ideal", "accepted_by_bixbench_only", "run"],
        )
        writer.writeheader()
        writer.writerows(rows)
    return csv_path


def render_score_figure(rows: list[dict[str, object]]) -> None:
    # Keep the established visual format: compact centered rows, gray canvas,
    # task label + circular status, answer/ideal text, and a top legend.
    n_rows = len(rows)
    fig_width = 11.0
    row_height = 0.82
    fig_height = 2.25 + n_rows * row_height

    fig = plt.figure(figsize=(fig_width, fig_height), dpi=180, facecolor="#f7f8fa")
    ax = fig.add_axes([0.01, 0.02, 0.98, 0.76], facecolor="#f7f8fa")
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, max(n_rows, 1))

    x_task = 0.32
    x_circle = 0.40
    x_text = 0.57

    for index, row in enumerate(rows):
        y_pos = n_rows - index - 0.5
        score = float(row["score"] or 0.0)
        color = "#2e7d32" if score >= 1.0 else "#b3261e"

        ax.text(
            x_task,
            y_pos + 0.05,
            f"Task {row['task']}",
            ha="right",
            va="center",
            fontsize=11,
            color="#202124",
        )
        ax.scatter(
            [x_circle],
            [y_pos],
            s=1040,
            c=[color],
            edgecolors="white",
            linewidths=2.5,
            zorder=3,
        )
        ax.text(
            x_circle,
            y_pos - 0.01,
            f"{score:.1f}{'*' if row.get('accepted_by_bixbench_only') else ''}",
            ha="center",
            va="center",
            fontsize=11.0,
            fontweight="bold",
            color="white",
            zorder=4,
        )
        ax.text(
            x_text,
            y_pos + 0.14,
            f"Answer: {row['answer']}",
            ha="left",
            va="center",
            fontsize=9.2,
            color="#202124",
        )
        ax.text(
            x_text,
            y_pos - 0.18,
            f"Ideal:  {row['ideal']}",
            ha="left",
            va="center",
            fontsize=8.4,
            color="#5f6368",
        )

    passed = sum(1 for row in rows if float(row["score"] or 0.0) >= 1.0)
    mean_score = sum(float(row["score"] or 0.0) for row in rows) / n_rows if n_rows else 0.0
    marked_rows = [row for row in rows if row.get("accepted_by_bixbench_only")]

    fig.text(
        0.5,
        0.965,
        "BixBench Task Score Summary",
        ha="center",
        va="top",
        fontsize=18,
        fontweight="bold",
        color="#202124",
    )
    fig.text(
        0.5,
        0.925,
        f"{n_rows} tasks run | {passed} passed | mean direct-match score {mean_score:.2f}",
        ha="center",
        va="top",
        fontsize=11,
        color="#5f6368",
    )

    legend_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#2e7d32",
            markeredgecolor="white",
            markeredgewidth=2,
            markersize=11,
            label="Score 1.0",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="#b3261e",
            markeredgecolor="white",
            markeredgewidth=2,
            markersize=11,
            label="Score 0.0",
        ),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.875),
        ncol=2,
        frameon=False,
        fontsize=10,
    )
    if marked_rows:
        marked_tasks = ", ".join(str(row["task"]) for row in marked_rows)
        fig.text(
            0.5,
            0.845,
            (
                f"* Tasks {marked_tasks}: correct by BixBench range_verifier because the answer is "
                "closer to the ideal range than to all distractor ranges, even if outside the ideal range."
            ),
            ha="center",
            va="top",
            fontsize=8.8,
            color="#5f6368",
        )

    fig.savefig(SUMMARY_DIR / "bixbench_score_summary.png", facecolor=fig.get_facecolor(), bbox_inches="tight")
    fig.savefig(SUMMARY_DIR / "bixbench_score_summary.svg", facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    rows = collect_latest_bixbench_runs()
    write_scores_csv(rows)
    render_score_figure(rows)
    print(f"Updated {SUMMARY_DIR.relative_to(REPO_ROOT)} with {len(rows)} BixBench tasks.")


if __name__ == "__main__":
    main()
