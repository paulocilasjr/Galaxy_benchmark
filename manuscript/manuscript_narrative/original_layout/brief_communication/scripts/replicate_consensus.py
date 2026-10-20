#!/usr/bin/env python3
"""Error analysis across replicate runs, and how much consensus would change accuracy.

Usage:
    python analysis/replicate_consensus.py

Inputs (all in data/): run_scores.csv, replicate_answer_agreement.csv,
bixbench_failure_causes.csv, run_execution_errors.csv and
compbiobench_task_domains.csv.

Outputs (all in data/):

- replicate_consensus.csv: one row per benchmark and condition. Accuracy of a
  single run; of a majority vote over the 3 replicates of each task and model,
  computed two ways (from correctness, and from the submitted answers); of at
  least 1 correct replicate (the ceiling a validation step that picks the
  correct run could reach); and of a majority over all 12 runs of a task
  (4 models x 3 replicates). Also how often replicates agree, where the
  incorrect runs fall, and how concentrated they are in a few tasks. IWC rows
  add the same quantities on the continuous agreement score.
- bixbench_causes_by_agreement.csv: incorrect BixBench-Verified-50 runs by
  primary cause and by how many of the other replicates were correct.
- run_errors_by_correctness.csv: execution errors in correct and incorrect
  runs, per benchmark and condition.
- compbiobench_errors_by_domain.csv: incorrect CompBioBench runs by task domain.

A run is correct when accepted (BixBench-Verified-50, CompBioBench) or, for IWC,
at output agreement >= 0.99, the threshold used in the figures.
A replicate group is the 3 replicate runs of one task, model and condition.

Majority votes from correctness count a group as correct when at least 2 of its
3 runs are correct, which assumes correct answers agree with each other.
Majority votes from answers use replicate_answer_agreement.csv, which compares
the 3 submitted answers as text after trimming and lower-casing, with numbers
rounded to 3 significant digits. A group is correct under that vote when a
strict majority of its answers is identical and correct: 3 correct runs with at
most 2 distinct answers, or 2 correct runs with 2 distinct answers. The second
case assumes the 2 correct answers are the identical pair, since the incorrect
answer must differ from at least one of them. Ties count as incorrect, so the
12-run vote is conservative. IWC has no answer text, so it has only the vote
from correctness.
"""
import argparse
import sys

import pandas as pd

RUN_KEYS = ["benchmark", "task_id", "model", "track", "replicate"]
GROUP_KEYS = ["benchmark", "track", "model", "task_id"]
CORRECT_AT = {"BixBench-Verified-50": 1.0, "CompBioBench": 1.0, "IWC": 0.99}
BINARY_BENCHMARKS = ["BixBench-Verified-50", "CompBioBench"]
N_REPLICATES = 3
TOP_TASKS = 5


def replicate_groups(scores: pd.DataFrame) -> pd.DataFrame:
    """One row per benchmark, condition, model and task, with the number of correct replicates."""
    groups = (
        scores.groupby(GROUP_KEYS)
        .agg(n_runs=("correct", "size"), n_correct=("correct", "sum"),
             median_score=("score", "median"), best_score=("score", "max"))
        .reset_index()
    )
    bad = groups[groups.n_runs != N_REPLICATES]
    if not bad.empty:
        sys.exit(f"Expected {N_REPLICATES} replicates per group; found:\n{bad.head()}")
    return groups


def add_answer_agreement(groups: pd.DataFrame, agreement: pd.DataFrame) -> pd.DataFrame:
    a = agreement[["benchmark", "track", "model", "task_id", "distinct_answers"]]
    merged = groups.merge(a, on=GROUP_KEYS, how="left", indicator=True)
    binary = merged.benchmark.isin(BINARY_BENCHMARKS)
    if (merged.loc[binary, "_merge"] != "both").any() or len(a) != binary.sum():
        sys.exit("Replicate groups and replicate_answer_agreement.csv do not match one to one.")
    k, d = merged.n_correct, merged.distinct_answers
    vote = ((k == 3) & (d <= 2)) | ((k == 2) & (d == 2))
    merged["answer_vote_correct"] = vote.astype(float).where(binary)
    return merged.drop(columns="_merge")


def consensus_table(scores: pd.DataFrame, groups: pd.DataFrame) -> pd.DataFrame:
    tasks = scores.groupby(["benchmark", "track", "task_id"]).correct.agg(["size", "sum"]).reset_index()
    wrong = scores[~scores.correct].merge(groups, on=GROUP_KEYS)
    rows = []
    for (benchmark, track), g in groups.groupby(["benchmark", "track"]):
        runs = scores[(scores.benchmark == benchmark) & (scores.track == track)]
        t = tasks[(tasks.benchmark == benchmark) & (tasks.track == track)]
        w = wrong[(wrong.benchmark == benchmark) & (wrong.track == track)]
        k = g.n_correct
        binary = benchmark in BINARY_BENCHMARKS
        k0, d = g[k == 0], g.distinct_answers
        rows.append({
            "benchmark": benchmark,
            "track": track,
            "correct_at": CORRECT_AT[benchmark],
            "runs": len(runs),
            "replicate_groups": len(g),
            "tasks": len(t),
            "single_run_accuracy": runs.correct.mean(),
            "majority_of_3_accuracy": (k >= 2).mean(),
            "answer_majority_of_3_accuracy": g.answer_vote_correct.astype(float).mean() if binary else None,
            "any_of_3_accuracy": (k >= 1).mean(),
            "majority_of_12_accuracy": (t["sum"] > t["size"] / 2).mean(),
            "groups_3_of_3": (k == 3).mean(),
            "groups_2_of_3": (k == 2).mean(),
            "groups_1_of_3": (k == 1).mean(),
            "groups_0_of_3": (k == 0).mean(),
            "correct_groups_with_differing_answers": ((k == 3) & (d > 1)).sum() / (k == 3).sum() if binary else None,
            "all_wrong_groups_with_identical_answer": (k0.distinct_answers == 1).mean() if binary else None,
            "incorrect_runs": len(w),
            "incorrect_in_all_wrong_groups": int((w.n_correct == 0).sum()),
            "incorrect_in_majority_correct_groups": int((w.n_correct >= 2).sum()),
            "tasks_with_incorrect_run": int((t["sum"] < t["size"]).sum()),
            "mean_score_single_run": runs.score.mean() if not binary else None,
            "mean_score_median_of_3": g.median_score.mean() if not binary else None,
            "mean_score_best_of_3": g.best_score.mean() if not binary else None,
        })
    out = pd.DataFrame(rows)
    # Concentration: incorrect runs in the TOP_TASKS tasks with the most incorrect runs, both conditions pooled.
    for benchmark, b in scores[~scores.correct].groupby("benchmark"):
        per_task = b.groupby("task_id").size().sort_values(ascending=False)
        out.loc[out.benchmark == benchmark, "incorrect_runs_both_conditions"] = len(b)
        out.loc[out.benchmark == benchmark, f"incorrect_in_top_{TOP_TASKS}_tasks_both_conditions"] = \
            per_task.head(TOP_TASKS).sum()
    return out


def causes_by_agreement(causes: pd.DataFrame, scores: pd.DataFrame, groups: pd.DataFrame) -> pd.DataFrame:
    bix = scores[scores.benchmark == "BixBench-Verified-50"]
    wrong = bix.loc[~bix.correct, RUN_KEYS]
    merged = wrong.merge(causes, on=RUN_KEYS, how="outer", indicator=True)
    if (merged._merge != "both").any():
        sys.exit("Incorrect BixBench runs and failure-cause rows do not match one to one.")
    merged = merged.merge(groups[GROUP_KEYS + ["n_correct"]], on=GROUP_KEYS)
    return (
        merged.groupby(["track", "primary_cause", "n_correct"])
        .size()
        .rename("incorrect_runs")
        .reset_index()
        .rename(columns={"n_correct": "correct_replicates_in_group"})
    )


def errors_by_correctness(scores: pd.DataFrame, errors: pd.DataFrame) -> pd.DataFrame:
    """Runs without an execution-error record are left out and counted in runs_without_record."""
    merged = scores.merge(errors, on=RUN_KEYS, how="left", indicator=True)
    merged["has_record"] = merged._merge == "both"
    merged["any_error"] = (merged.failed_shell_commands > 0) | (merged.galaxy_jobs_in_error_state > 0)
    merged["errors"] = merged.failed_shell_commands + merged.galaxy_jobs_in_error_state
    rows = []
    for (benchmark, track, correct), g in merged.groupby(["benchmark", "track", "correct"]):
        r = g[g.has_record]
        rows.append({
            "benchmark": benchmark, "track": track, "correct": correct,
            "runs": len(g), "runs_without_record": int((~g.has_record).sum()),
            "share_with_any_error": r.any_error.mean(),
            "mean_errors": r.errors.mean(), "median_errors": r.errors.median(),
            "mean_failed_shell_commands": r.failed_shell_commands.mean(),
            "mean_galaxy_jobs_in_error_state": r.galaxy_jobs_in_error_state.mean(),
        })
    return pd.DataFrame(rows)


def errors_by_domain(scores: pd.DataFrame, domains: pd.DataFrame) -> pd.DataFrame:
    cb = scores[scores.benchmark == "CompBioBench"].merge(domains, on="task_id", how="left")
    if cb.domain.isna().any():
        sys.exit("Some CompBioBench tasks have no domain in compbiobench_task_domains.csv.")
    return (
        cb.groupby(["domain", "track"])
        .agg(tasks=("task_id", "nunique"), runs=("correct", "size"), incorrect_runs=("correct", lambda c: (~c).sum()))
        .assign(accuracy=lambda x: 1 - x.incorrect_runs / x.runs)
        .reset_index()
    )


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default="data", help="Directory holding the input tables")
    p.add_argument("--out", default="data", help="Directory for the output tables")
    args = p.parse_args()
    read = lambda name: pd.read_csv(f"{args.data}/{name}")

    scores = read("run_scores.csv")
    unknown = set(scores.benchmark) - set(CORRECT_AT)
    if unknown:
        sys.exit(f"No correctness threshold for {unknown}.")
    for b in BINARY_BENCHMARKS:
        if not scores.loc[scores.benchmark == b, "score"].isin([0, 1]).all():
            sys.exit(f"Expected scores of 0 or 1 for {b}.")
    scores["correct"] = scores.score >= scores.benchmark.map(CORRECT_AT)

    groups = add_answer_agreement(replicate_groups(scores), read("replicate_answer_agreement.csv"))
    causes = read("bixbench_failure_causes.csv")
    tables = {
        "replicate_consensus.csv": consensus_table(scores, groups),
        "bixbench_causes_by_agreement.csv": causes_by_agreement(causes, scores, groups),
        "run_errors_by_correctness.csv": errors_by_correctness(scores, read("run_execution_errors.csv")),
        "compbiobench_errors_by_domain.csv": errors_by_domain(scores, read("compbiobench_task_domains.csv")),
    }
    for name, table in tables.items():
        table.round(4).to_csv(f"{args.out}/{name}", index=False)

    with pd.option_context("display.width", 250, "display.max_columns", None):
        for name, table in tables.items():
            print(f"== {name}")
            print(table.round(3).T.to_string() if name == "replicate_consensus.csv" else table.round(3).to_string(index=False))
            print()
    rigor = (causes.primary_cause == "RIGOR") | (causes.secondary_cause == "RIGOR")
    print(f"Incorrect BixBench runs with RIGOR as primary or secondary cause: {rigor.sum()} of {len(causes)}")
    print(f"Wrote {', '.join(tables)} to {args.out}/")


if __name__ == "__main__":
    main()
