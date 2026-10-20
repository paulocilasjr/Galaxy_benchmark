import csv
import math
import sys
import zipfile
from collections import Counter

from scipy import stats

animals_zip, fungi_zip, metrics_out, answer_out = sys.argv[1:5]
MISSING = set(['-', '?'])

def read_fasta(text):
    records = []
    name = None
    seq_parts = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith('>'):
            if name is not None:
                records.append((name, ''.join(seq_parts)))
            name = line[1:].strip().split()[0]
            seq_parts = []
        else:
            seq_parts.append(line)
    if name is not None:
        records.append((name, ''.join(seq_parts)))
    return records

def pi_percentage_for_records(records, member):
    if not records:
        raise ValueError('%s has no FASTA records' % member)
    lengths = [len(seq) for _, seq in records]
    if len(set(lengths)) != 1:
        raise ValueError('%s is not an alignment; sequence lengths are %s' % (member, sorted(set(lengths))))
    aln_len = lengths[0]
    if aln_len == 0:
        raise ValueError('%s has zero alignment length' % member)
    informative = 0
    seqs = [seq.upper() for _, seq in records]
    for idx in range(aln_len):
        counts = Counter(seq[idx] for seq in seqs if seq[idx] not in MISSING)
        states_with_two = sum(1 for count in counts.values() if count >= 2)
        if states_with_two >= 2:
            informative += 1
    return informative, aln_len, 100.0 * informative / aln_len, len(records)

def process_archive(path, group):
    rows = []
    values = []
    with zipfile.ZipFile(path) as zf:
        members = sorted(name for name in zf.namelist() if name.endswith('.faa.mafft') and not name.endswith('/'))
        if not members:
            raise ValueError('%s archive has no .faa.mafft members' % group)
        for member in members:
            text = zf.read(member).decode('utf-8')
            records = read_fasta(text)
            informative, aln_len, pct, nseq = pi_percentage_for_records(records, member)
            rows.append({
                'group': group,
                'member': member,
                'nseq': nseq,
                'alignment_length': aln_len,
                'parsimony_informative_sites': informative,
                'parsimony_informative_pct': pct,
            })
            values.append(pct)
    return rows, values

animal_rows, animal_values = process_archive(animals_zip, 'animals')
fungi_rows, fungi_values = process_archive(fungi_zip, 'fungi')

# Report the U statistic for the first sample named in the question: animals.
try:
    mwu = stats.mannwhitneyu(animal_values, fungi_values, alternative='two-sided')
    u_stat = float(mwu.statistic if hasattr(mwu, 'statistic') else mwu[0])
    method = 'scipy.stats.mannwhitneyu(alternative=two-sided)'
except TypeError:
    ranks = stats.rankdata(animal_values + fungi_values, method='average')
    n1 = len(animal_values)
    u_stat = float(sum(ranks[:n1]) - n1 * (n1 + 1) / 2.0)
    method = 'scipy.stats.rankdata average-tie U1 fallback'

with open(metrics_out, 'w', newline='') as handle:
    fieldnames = ['group', 'member', 'nseq', 'alignment_length', 'parsimony_informative_sites', 'parsimony_informative_pct']
    writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    for row in animal_rows + fungi_rows:
        writer.writerow(row)
    handle.write('# animals_n\t%d\n' % len(animal_values))
    handle.write('# fungi_n\t%d\n' % len(fungi_values))
    handle.write('# mann_whitney_u_animals_first\t%.17g\n' % u_stat)
    handle.write('# method\t%s\n' % method)

with open(answer_out, 'w') as handle:
    handle.write('%.17g\n' % u_stat)
