#!/usr/bin/env python3
"""Replay artifact collection for BioAgent task_1 from an existing Galaxy history."""
from pathlib import Path
import json
from bioblend.galaxy import GalaxyInstance

ROOT = Path(__file__).resolve().parents[2]
RUN_DIR = Path(__file__).resolve().parents[1]
HISTORY_ID = "bbd44e69cb8906b56adf8f3d859d4301"
DATASET_IDS = {
    "deseq2_3xTG_result.tsv": "f9cad7b01a472135a47d8d3d7ca5d9ad",
    "deseq2_5xFAD_result.tsv": "f9cad7b01a4721353ecaa38420ffb8ef",
    "goseq_3xTG_kegg.tsv": "f9cad7b01a472135630f2c60d8a5e597",
    "goseq_5xFAD_kegg.tsv": "f9cad7b01a4721354b1c735968e03172",
    "goseq_PS3O1S_kegg.tsv": "f9cad7b01a47213587bcc44295927895",
}

def load_env(path: Path) -> dict[str, str]:
    vals = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        vals[k] = v
    return vals


def main() -> None:
    env = load_env(ROOT / '.env')
    gi = GalaxyInstance(url='https://usegalaxy.org', key=env['GALAXY_API_KEY'])
    history = gi.histories.show_history(HISTORY_ID, contents=False)
    print(json.dumps({'id': history['id'], 'name': history['name'], 'state': history['state']}, indent=2))
    out_dir = RUN_DIR / 'results' / 'original_galaxy_outputs'
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, dataset_id in DATASET_IDS.items():
        gi.datasets.download_dataset(dataset_id, file_path=str(out_dir / name), use_default_filename=False)
        print(f"downloaded {name}")

if __name__ == '__main__':
    main()
