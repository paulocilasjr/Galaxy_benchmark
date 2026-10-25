import os
import re
import statistics
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

animals_zip, fungi_zip, answer_path, details_path = sys.argv[1:5]
number_re = re.compile(r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?')

def run_treeness(tree_path):
    commands = [
        ['pk_treeness', str(tree_path)],
        ['phykit', 'treeness', str(tree_path)],
        ['phykit', 'tness', str(tree_path)],
    ]
    last_error = None
    for cmd in commands:
        try:
            proc = subprocess.run(cmd, text=True, capture_output=True, check=False)
        except FileNotFoundError as exc:
            last_error = str(exc)
            continue
        if proc.returncode != 0:
            last_error = (proc.stderr or proc.stdout or '').strip()
            continue
        nums = [float(x) for x in number_re.findall(proc.stdout)]
        if nums:
            return nums[-1]
        last_error = 'no numeric treeness in output: ' + proc.stdout.strip()
    raise RuntimeError(last_error or 'no treeness command available')

def values_from_zip(zip_path, group):
    values = []
    failures = []
    with zipfile.ZipFile(zip_path) as zf, tempfile.TemporaryDirectory() as td:
        members = sorted(n for n in zf.namelist() if n.endswith('.treefile') and not n.endswith('/'))
        for idx, name in enumerate(members, start=1):
            target = Path(td) / (group + '_' + str(idx) + '.treefile')
            target.write_bytes(zf.read(name))
            try:
                values.append((name, run_treeness(target)))
            except Exception as exc:
                failures.append((name, str(exc)))
    if failures:
        raise RuntimeError(group + ' failed files: ' + '; '.join(n + '=' + e for n, e in failures[:5]))
    if not values:
        raise RuntimeError(group + ' had no .treefile members')
    return values

animals = values_from_zip(animals_zip, 'animals')
fungi = values_from_zip(fungi_zip, 'fungi')
animal_median = statistics.median(v for _, v in animals)
fungi_median = statistics.median(v for _, v in fungi)
difference = fungi_median - animal_median

with open(answer_path, 'w') as out:
    out.write(format(difference, '.17g') + '\n')
with open(details_path, 'w') as out:
    out.write('group\tcount\tmedian\n')
    out.write('animals\t{}\t{}\n'.format(len(animals), format(animal_median, '.17g')))
    out.write('fungi\t{}\t{}\n'.format(len(fungi), format(fungi_median, '.17g')))
