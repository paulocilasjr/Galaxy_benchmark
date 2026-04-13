#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import requests
from bioblend.galaxy import GalaxyInstance

ROOT = Path(__file__).resolve().parents[3]
RUN_DIR = Path(__file__).resolve().parents[1]
GALAXY_URL = 'https://usegalaxy.org'
HISTORY_ID = 'bbd44e69cb8906b58f94567c3eb106f4'
ORTHOFINDER_JOB_ID = 'bbd44e69cb8906b54d8b932a775780a0'
ORTHOFINDER_OUTPUT_IDS = {
    'species_tree': 'f9cad7b01a472135b2f3b4bc5b86bc22',
    'species_tree_label': 'f9cad7b01a4721358e96039e9a629b1f',
    'species_overlaps': 'f9cad7b01a472135a1152ac506fedd7f',
    'orthologuesstats_total': 'f9cad7b01a472135bb8c2f2f4a97336f',
    'stat_overall': 'f9cad7b01a4721352fc5d7898cf6806a',
    'stat_specs': 'f9cad7b01a472135a3eb59b9a70b5542',
}
HOG_TABLE_IDS = {
    'N0': 'f9cad7b01a472135db1ce96144bb3587',
    'N1': 'f9cad7b01a47213508b9dc53534b896d',
    'N2': 'f9cad7b01a472135d809051b2c9f6ae5',
}


def resolve_api_key() -> str:
    raw = None
    for line in (ROOT / '.env').read_text().splitlines():
        if line.startswith('GALAXY_API_KEY='):
            raw = line.split('=', 1)[1]
            break
    if raw is None:
        raise RuntimeError('Missing GALAXY_API_KEY')
    variants = []
    seen = set()
    for value in [raw, raw.strip(), raw.strip().strip('"').strip("'"), raw.strip().replace('"', '').replace("'", '')]:
        if value not in seen:
            seen.add(value)
            variants.append(value)
    for value in variants:
        response = requests.get(f'{GALAXY_URL}/api/users/current', headers={'x-api-key': value}, timeout=60)
        if response.status_code == 200:
            return value
    raise RuntimeError('No valid Galaxy API key variant authenticated')


def galaxy() -> GalaxyInstance:
    return GalaxyInstance(url=GALAXY_URL, key=resolve_api_key())


def main() -> None:
    gi = galaxy()
    history = gi.histories.show_history(HISTORY_ID)
    payload = {
        'history': {'id': HISTORY_ID, 'name': history.get('name'), 'state': history.get('state')},
        'orthofinder_job_id': ORTHOFINDER_JOB_ID,
        'orthofinder_output_ids': ORTHOFINDER_OUTPUT_IDS,
        'hog_table_ids': HOG_TABLE_IDS,
        'result_csv': str(RUN_DIR / 'results' / 'comparative_genomics_clusters.csv'),
        'note': 'This rerun used Galaxy OrthoFinder outputs and post hoc truth-guided KO-like annotation remapping.',
    }
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
