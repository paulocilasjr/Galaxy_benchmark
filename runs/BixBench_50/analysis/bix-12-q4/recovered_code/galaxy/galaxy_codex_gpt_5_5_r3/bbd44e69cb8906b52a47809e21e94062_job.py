import pathlib
import re
import subprocess
import sys
import tempfile
import zipfile


def run_phykit_pis(fasta_path):
    attempts = [
        ['phykit', 'pis', str(fasta_path)],
        ['phykit', 'parsimony_informative_sites', str(fasta_path)],
    ]
    errors = []
    for cmd in attempts:
        try:
            run = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return run.stdout.strip()
        except Exception as exc:
            detail = getattr(exc, 'stderr', '') or str(exc)
            errors.append(' '.join(cmd) + ': ' + detail.replace('\n', ' '))
    raise RuntimeError('PhyKit PIS failed: ' + ' | '.join(errors))


def parse_pis_output(text):
    nums = re.findall(r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?', text)
    if len(nums) < 3:
        raise ValueError('Cannot parse PhyKit PIS output: ' + repr(text))
    return int(float(nums[0])), int(float(nums[1])), float(nums[2])


def process_archive(zip_path, group, metrics):
    values = []
    failed = []
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        with zipfile.ZipFile(zip_path) as zf:
            names = sorted(name for name in zf.namelist() if (not name.endswith('/')) and name.endswith('.mafft'))
            for name in names:
                target = td / pathlib.Path(name).name
                target.write_bytes(zf.read(name))
                try:
                    pis, total, pct = parse_pis_output(run_phykit_pis(target))
                    values.append(pct)
                    metrics.write(f'{group}\t{name}\t{pis}\t{total}\t{pct:.15g}\n')
                except Exception as exc:
                    failed.append((name, str(exc)))
    return values, failed


def average_ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i + 1
        while j < len(order) and values[order[j]] == values[order[i]]:
            j += 1
        avg = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[order[k]] = avg
        i = j
    return ranks


def mann_whitney_u_first(a, b):
    n1 = len(a)
    ranks = average_ranks(list(a) + list(b))
    r1 = sum(ranks[:n1])
    return r1 - (n1 * (n1 + 1) / 2.0)


def fmt(x):
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f'{x:.15g}'


animals_path, fungi_path = sys.argv[1], sys.argv[2]
with open('metrics.tsv', 'w') as metrics:
    metrics.write('group\tfile\tpis_sites\ttotal_sites\tpis_percent\n')
    animals, animals_failed = process_archive(animals_path, 'animals', metrics)
    fungi, fungi_failed = process_archive(fungi_path, 'fungi', metrics)

with open('failed.tsv', 'w') as out:
    out.write('group\tfile\terror\n')
    for group, failed in [('animals', animals_failed), ('fungi', fungi_failed)]:
        for name, err in failed:
            out.write(f'{group}\t{name}\t{err.replace(chr(9), " ")}\n')

if animals_failed or fungi_failed:
    raise RuntimeError(f'Failed files: {len(animals_failed)} animals, {len(fungi_failed)} fungi')
if not animals or not fungi:
    raise RuntimeError('No .mafft parsimony-informative-site percentages were computed for one or both groups')

u1 = mann_whitney_u_first(animals, fungi)
with open('answer.txt', 'w') as out:
    out.write(fmt(u1) + '\n')

with open('summary.tsv', 'w') as out:
    out.write('group\tn\tmin\tmax\tmean\n')
    for group, values in [('animals', animals), ('fungi', fungi)]:
        out.write(f'{group}\t{len(values)}\t{min(values):.15g}\t{max(values):.15g}\t{(sum(values)/len(values)):.15g}\n')
    out.write(f'U1_animals_vs_fungi\t{len(animals)},{len(fungi)}\t{fmt(u1)}\t\t\n')
