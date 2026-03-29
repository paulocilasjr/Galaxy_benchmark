"""Typer CLI entrypoints."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

from galaxy_benchmark.application.prompting.services import PromptVariantGenerator
from galaxy_benchmark.application.use_cases.migrate_legacy import LegacyExperimentMigrator
from galaxy_benchmark.infrastructure.repositories.json_task_repository import JsonTaskRepository

app = typer.Typer(help="Galaxy benchmark CLI.")
console = Console()


@app.command("validate")
def validate(
    task_dir: Path = typer.Option(Path("benchmark/tasks/legacy/canonical"), exists=False),
    ground_truth_dir: Path = typer.Option(Path("benchmark/ground_truth/legacy/canonical"), exists=False),
) -> None:
    """Validate canonical tasks and ground truths."""

    repository = JsonTaskRepository()
    task_paths = sorted(task_dir.glob("*.json"))
    ground_truth_paths = sorted(ground_truth_dir.glob("*.json"))
    tasks = [repository.load_task(path) for path in task_paths]
    truths = [repository.load_ground_truth(path) for path in ground_truth_paths]
    console.print(
        f"Validated {len(tasks)} task(s) and {len(truths)} ground-truth file(s).",
    )


@app.command("migrate-legacy")
def migrate_legacy(
    experiments_dir: Path = typer.Option(Path("benchmark/tasks/legacy/raw"), exists=False),
    ground_truth_dir: Path = typer.Option(Path("benchmark/ground_truth/legacy/raw"), exists=False),
) -> None:
    """Preview migration from legacy inputs into canonical models."""

    migrator = LegacyExperimentMigrator()
    migrated = migrator.migrate_directory(experiments_dir, ground_truth_dir)
    console.print(f"Migrated {len(migrated)} legacy experiment(s).")


@app.command("generate-prompts")
def generate_prompts(
    task_dir: Path = typer.Option(Path("benchmark/tasks/legacy/canonical"), exists=False),
    output_dir: Path = typer.Option(Path("benchmark/prompts"), exists=False),
) -> None:
    """Generate prompt variants for canonical tasks."""

    repository = JsonTaskRepository()
    generator = PromptVariantGenerator()
    output_dir.mkdir(parents=True, exist_ok=True)
    total = 0
    for task_path in sorted(task_dir.glob("*.json")):
        task = repository.load_task(task_path)
        variants = generator.generate(task)
        variants_by_tier: dict[str, list[dict[str, object]]] = {}
        for variant in variants:
            variants_by_tier.setdefault(variant.tier.value, []).append(variant.model_dump(mode="json"))
        for tier, tier_variants in variants_by_tier.items():
            tier_dir = output_dir / tier
            tier_dir.mkdir(parents=True, exist_ok=True)
            output_path = tier_dir / f"{task_path.stem}.json"
            output_path.write_text(json.dumps(tier_variants, indent=2) + "\n")
        total += len(variants)
    console.print(f"Generated {total} prompt variant(s).")


@app.command("run-task")
def run_task() -> None:
    """Reserved for trial execution orchestration."""

    console.print("run-task is scaffolded but not implemented yet.")
    raise typer.Exit(code=1)


@app.command("run-suite")
def run_suite() -> None:
    """Reserved for suite execution orchestration."""

    console.print("run-suite is scaffolded but not implemented yet.")
    raise typer.Exit(code=1)


@app.command("score-run")
def score_run() -> None:
    """Reserved for run scoring orchestration."""

    console.print("score-run is scaffolded but not implemented yet.")
    raise typer.Exit(code=1)


@app.command("score-suite")
def score_suite() -> None:
    """Reserved for suite scoring orchestration."""

    console.print("score-suite is scaffolded but not implemented yet.")
    raise typer.Exit(code=1)


@app.command("summarize")
def summarize() -> None:
    """Reserved for summary generation."""

    console.print("summarize is scaffolded but not implemented yet.")
    raise typer.Exit(code=1)


@app.command("leaderboard")
def leaderboard() -> None:
    """Reserved for leaderboard generation."""

    console.print("leaderboard is scaffolded but not implemented yet.")
    raise typer.Exit(code=1)


@app.command("export-report")
def export_report() -> None:
    """Reserved for export reporting."""

    console.print("export-report is scaffolded but not implemented yet.")
    raise typer.Exit(code=1)
