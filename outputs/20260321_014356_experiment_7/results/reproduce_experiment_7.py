#!/usr/bin/env python3
"""Reproduce benchmark experiment_7 for this specific run directory.

This wrapper re-executes the live runner that performed the benchmark actions:
1. validate the local experiment inputs and Galaxy credentials
2. download the pinned metagenomic genes catalogue workflow definition
3. create a fresh Galaxy history, upload reads, and create the list:paired input collection
4. import and invoke the workflow on usegalaxy.org
5. poll Galaxy to terminal completion, then write result and comparison artifacts
"""

from pathlib import Path
import subprocess
import sys

RUNNER = Path(__file__).resolve().parent / "run_experiment_7_live.py"
command = [sys.executable, "-B", str(RUNNER)]
print("# Re-running experiment_7 benchmark workflow")
print("# Command:", " ".join(command))
completed = subprocess.run(command, check=False)
print("# Exit code:", completed.returncode)
raise SystemExit(completed.returncode)
