import os
import sys
import zipfile
import tempfile
import subprocess
import shutil
from pathlib import Path

animals_zip = Path(sys.argv[1])
fungi_zip = Path(sys.argv[2])


def safe_members(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        names = []
        for info in zf.infolist():
            if info.is_dir():
                continue
            name = info.filename
            if name.startswith('/') or '..' in Path(name).parts:
                raise ValueError(f'unsafe archive member: {name}')
            if name.endswith('.mafft'):
                names.append(name)
        return sorted(names)


def run_phykit_pis(path):
    attempts = [
        ['phykit', 'pis', str(path)],
        ['phykit', 'parsimony_informative_sites', str(path)],
    ]
    last = None
    for cmd in attempts:
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 0:
            fields = proc.stdout.strip().replace(',', '\t').split()
            if len(fields) < 3:
                raise ValueError(f'unexpected PhyKit output for {path.name}: {proc.stdout!r}')
            return int(float(fields[0])), int(float(fields[1])), float(fields[2])
        last = proc
    raise RuntimeError(f'PhyKit failed for {path.name}: {last.stderr}')


def process_archive(group, zip_path, tmpdir):
    rows = []
    with zipfile.ZipFile(zip_path) as zf:
        for idx, name in enumerate(safe_members(zip_path), 1):
            out = tmpdir / f'{group}_{idx}_{Path(name).name}'
            with zf.open(name) as src, open(out, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            pis, sites, pct = run_phykit_pis(out)
            rows.append((group, name, pis, sites, pct))
    return rows


def mannwhitney_u_animals_first(x, y):
    try:
        from scipy.stats import mannwhitneyu
    except Exception as exc:
        raise RuntimeError('SciPy is required for Mann-Whitney U statistic') from exc
    res = mannwhitneyu(x, y, alternative='two-sided', method='auto', use_continuity=True)
    return float(res.statistic), float(res.pvalue)

with tempfile.TemporaryDirectory() as d:
    tmpdir = Path(d)
    animal_rows = process_archive('animals', animals_zip, tmpdir)
    fungi_rows = process_archive('fungi', fungi_zip, tmpdir)

all_rows = animal_rows + fungi_rows
if not animal_rows or not fungi_rows:
    raise RuntimeError('Both groups must contain at least one .mafft alignment')

x = [r[2] for r in animal_rows]
y = [r[2] for r in fungi_rows]
u, p = mannwhitney_u_animals_first(x, y)

with open('counts.tsv', 'w') as out:
    out.write('group\tmember\traw_parsimony_informative_sites\talignment_sites\tpercent_parsimony_informative\n')
    for row in all_rows:
        out.write(f'{row[0]}\t{row[1]}\t{row[2]}\t{row[3]}\t{row[4]:.12g}\n')

with open('result.tsv', 'w') as out:
    out.write('sample_a\tsample_b\tn_a\tn_b\tstatistic_U\tpvalue\talternative\tmethod\tcontinuity\n')
    out.write(f'animals\tfungi\t{len(x)}\t{len(y)}\t{u:.17g}\t{p:.17g}\ttwo-sided\tauto\ttrue\n')
