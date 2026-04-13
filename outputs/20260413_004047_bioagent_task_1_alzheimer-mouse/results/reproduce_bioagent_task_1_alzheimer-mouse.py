#!/usr/bin/env python3
"""Reproduce the failed live-Galaxy authentication check for BioAgent task 1."""
from pathlib import Path
import os
from bioblend.galaxy import GalaxyInstance

def load_env(path: str) -> None:
    for line in Path(path).read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k, v)

load_env('.env')
gi = GalaxyInstance(url='https://usegalaxy.org', key=os.environ['GALAXY_API_KEY'])
print(gi.users.get_current_user())
