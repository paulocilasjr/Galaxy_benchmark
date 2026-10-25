#!/usr/bin/env python3
"""Verify preserved archive files and restore the split dataset after cloning."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def verify(record):
    path = ROOT / record['path']
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    if path.stat().st_size != record['bytes'] or digest.hexdigest() != record['sha256']:
        raise ValueError(f'Checksum or size mismatch: {path}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true', help='Check archived files and dataset parts without restoring the dataset')
    args = parser.parse_args()
    records = json.loads((HERE / 'preserved_files.json').read_text())
    dataset = json.loads((HERE / 'large_dataset.json').read_text())
    for record in records + dataset['parts']:
        verify(record)
    print(f"Verified {len(records)} archive files and {len(dataset['parts'])} dataset parts.")
    target = ROOT / dataset['path']
    if target.exists():
        verify(dataset)
        print(f'Dataset already present and verified: {target}')
    elif not args.verify_only:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as output:
                temporary = Path(output.name)
                digest = hashlib.sha256()
                size = 0
                for part in dataset['parts']:
                    with (ROOT / part['path']).open('rb') as stream:
                        for block in iter(lambda: stream.read(1024 * 1024), b''):
                            output.write(block)
                            digest.update(block)
                            size += len(block)
            if size != dataset['bytes'] or digest.hexdigest() != dataset['sha256']:
                raise ValueError('Reassembled dataset failed checksum verification')
            os.replace(temporary, target)
            print(f'Restored and verified: {target}')
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()


if __name__ == '__main__':
    main()
