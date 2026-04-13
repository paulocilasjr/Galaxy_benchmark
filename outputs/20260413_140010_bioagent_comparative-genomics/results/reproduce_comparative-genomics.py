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
PROKKA_GFF_IDS = {
    'KBS0714': 'f9cad7b01a472135989e2ae2347214d2',
    'SA211': 'f9cad7b01a472135e9c73f301dd41d89',
    'AS2': 'f9cad7b01a472135ea2114fa7a0d0066',
    'KD33716': 'f9cad7b01a472135cf0a0fc58f9d8b01',
}
ROARY_JOB_ID = 'bbd44e69cb8906b5a35fb97c2361f2af'
ROARY_OUTPUT_IDS = {
    'sumstats': 'f9cad7b01a472135d7015c2a50a4d20e',
    'core_gene_aln': 'f9cad7b01a47213582d7be51b3b9a2ac',
    'gene_p_a': 'f9cad7b01a47213518eae329d97d1787',
    'clust_file': 'f9cad7b01a4721357c63b8c1f40a58a7',
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
        'prokka_gff_ids': PROKKA_GFF_IDS,
        'roary_job_id': ROARY_JOB_ID,
        'roary_output_ids': ROARY_OUTPUT_IDS,
        'result_csv': str(RUN_DIR / 'results' / 'comparative_genomics_clusters.csv'),
        'note': 'Roary job remained stalled on usegalaxy.org; CSV was derived from completed Galaxy Prokka annotations.',
    }
    print(json.dumps(payload, indent=2))


if __name__ == '__main__':
    main()
