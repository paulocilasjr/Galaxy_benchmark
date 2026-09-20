from __future__ import print_function
import sys
import zipfile
from collections import Counter
from scipy.stats import mannwhitneyu

MISSING = set(['-', '?', '.', '*'])
try:
    text_type = unicode
except NameError:
    text_type = str


def to_text(data):
    if isinstance(data, text_type):
        return data
    return data.decode('utf-8', 'replace')


def read_fasta(text):
    seqs = []
    name = None
    parts = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith('>'):
            if name is not None:
                seqs.append(''.join(parts))
            name = line[1:]
            parts = []
        else:
            parts.append(line)
    if name is not None:
        seqs.append(''.join(parts))
    return seqs


def pi_count(seqs):
    if not seqs:
        return 0, 0
    lengths = set([len(s) for s in seqs])
    if len(lengths) != 1:
        raise ValueError('non-rectangular alignment')
    total = lengths.pop()
    pi = 0
    for i in range(total):
        states = []
        for seq in seqs:
            char = seq[i].upper()
            if char in MISSING:
                continue
            states.append(char)
        counts = Counter(states)
        repeated = 0
        for value in counts.values():
            if value >= 2:
                repeated += 1
        if repeated >= 2:
            pi += 1
    return pi, total


def process(zip_path, group):
    rows = []
    with zipfile.ZipFile(zip_path, 'r') as archive:
        for name in sorted(archive.namelist()):
            if not name.endswith('.mafft'):
                continue
            seqs = read_fasta(to_text(archive.read(name)))
            pi, total = pi_count(seqs)
            rows.append((group, name, pi, total, len(seqs)))
    return rows


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: job.py ANIMALS_ZIP FUNGI_ZIP')
    animal_rows = process(sys.argv[1], 'animals')
    fungi_rows = process(sys.argv[2], 'fungi')
    animals = [row[2] for row in animal_rows]
    fungi = [row[2] for row in fungi_rows]
    try:
        res = mannwhitneyu(animals, fungi, alternative='two-sided', method='auto')
    except TypeError:
        res = mannwhitneyu(animals, fungi, alternative='two-sided')
    stat = float(res[0])
    pval = float(res[1])
    with open('counts.tsv', 'w') as out:
        out.write('group\tmember\tparsimony_informative_sites\ttotal_sites\tn_sequences\n')
        for row in animal_rows + fungi_rows:
            out.write('%s\t%s\t%d\t%d\t%d\n' % row)
    with open('result.tsv', 'w') as out:
        out.write('statistic\tp_value\tn_animals\tn_fungi\tfirst_sample\talternative\n')
        out.write('%.9g\t%.17g\t%d\t%d\tanimals\ttwo-sided\n' % (stat, pval, len(animals), len(fungi)))


if __name__ == '__main__':
    main()
