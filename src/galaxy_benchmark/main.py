"""CLI main entrypoint."""

from __future__ import annotations

from galaxy_benchmark.interfaces.cli.app import app


def main() -> None:
    """Run the Typer CLI."""

    app()


if __name__ == "__main__":
    main()
