import sys, zipfile
from collections import Counter

GAP_MISSING = set('-?.Xx')

def parse_fasta_bytes(data):
    records = []
    name = None
    seq_parts = []
    text = data.decode('utf-8', 'replace')
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if name is not None:
                records.append((name, ''.join(seq_parts)))
            name = line[1:].split()[0]
            seq_parts = []
        else:
            seq_parts.append(line)
    if name is not None:
        records.append((name, ''.join(seq_parts)))
    return records

def pis_count(records, label, member):
    if len(records) < 4:
        raise ValueError(f'{label}:{member}: expected at least 4 sequences, found {len(records)}')
    lengths = {len(seq) for _, seq in records}
    if len(lengths) != 1:
        raise ValueError(f'{label}:{member}: sequences are not aligned; lengths={sorted(lengths)}')
    total = lengths.pop()
    count = 0
    seqs = [seq for _, seq in records]
    for chars in zip(*seqs):
        freqs = Counter(c.upper() for c in chars if c not in GAP_MISSING)
        if sum(1 for n in freqs.values() if n >= 2) >= 2:
            count += 1
    pct = (100.0 * count / total) if total else 0.0
    return count, total, pct

def process(path, label, out):
    selected = 0
    with zipfile.ZipFile(path) as zf:
        for member in sorted(zf.namelist()):
            if member.endswith('/') or not member.endswith('.faa.mafft'):
                continue
            selected += 1
            records = parse_fasta_bytes(zf.read(member))
            count, total, pct = pis_count(records, label, member)
            out.write(f'{label}\t{member}\t{count}\t{total}\t{pct:.10g}\n')
    if selected == 0:
        raise ValueError(f'{label}: no .faa.mafft members found')
    return selected

animals, fungi = sys.argv[1], sys.argv[2]
with open('pis_counts.tsv', 'w', encoding='utf-8') as out:
    out.write('group\talignment\traw_pis\ttotal_sites\tpercent_pis\n')
    na = process(animals, 'animals', out)
    nf = process(fungi, 'fungi', out)
with open('counts_summary.txt', 'w', encoding='utf-8') as out:
    out.write(f'animals_alignments\t{na}\n')
    out.write(f'fungi_alignments\t{nf}\n')
