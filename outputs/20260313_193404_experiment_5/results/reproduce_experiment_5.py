#!/usr/bin/env python3
"""Reproduce the documented experiment_5 benchmark actions.

This script mirrors the exact benchmark attempt sequence that was executed:
1. Run the initial workflow execution attempt. Galaxy rejects it with a missing
   non-optional workflow input binding.
2. Run the corrected attempt that binds parameter_input values through the
   workflow inputs map. Galaxy accepts the invocation but never populates any
   workflow steps.
3. Run the third attempt that adds a mitochondrial Cufflinks mask GTF and a
   stricter invocation-population gate. Galaxy still leaves the invocation in
   state `new` with zero populated steps.

The commands are intentionally preserved in the same order as the benchmark log.
They are expected to reproduce the blocker, not a successful RNA-seq run.
"""

from pathlib import Path
import subprocess

RUN_DIR = Path(__file__).resolve().parent.parent
COMMANDS = [
    [
        'python3',
        str(RUN_DIR / 'results' / 'run_experiment_5_live.py'),
    ],
    [
        'python3',
        str(RUN_DIR / 'results' / 'run_experiment_5_live.attempt_2.py'),
    ],
    [
        'python3',
        str(RUN_DIR / 'results' / 'run_experiment_5_live.attempt_3.py'),
    ],
]

for index, command in enumerate(COMMANDS, start=1):
    print(f"# Attempt {index}: {' '.join(command)}")
    completed = subprocess.run(command, check=False)
    print(f"# Exit code: {completed.returncode}")
