import csv
import math
import sys

counts_path, gene_path, sample_path = sys.argv[1:4]

cd14 = set()
with open(sample_path, newline='') as f:
    for row in csv.DictReader(f):
        if row['celltype'].strip() == 'CD14':
            cd14.add(row['sample'].strip())

length_by_gene = {}
with open(gene_path, newline='') as f:
    for row in csv.DictReader(f):
        if row['gene_biotype'].strip() == 'protein_coding':
            gid = row['Geneid'].strip()
            length_by_gene[gid] = float(row['Length'])

xs = []
ys = []
with open(counts_path, newline='') as f:
    reader = csv.reader(f)
    header = next(reader)
    idx = [j for j, name in enumerate(header) if name.strip() in cd14]
    if not idx:
        raise RuntimeError('No CD14 sample columns found in counts matrix')
    n = len(idx)
    for row in reader:
        gid = row[0].strip()
        length = length_by_gene.get(gid)
        if length is None:
            continue
        total = 0.0
        for j in idx:
            total += float(row[j])
        if total >= 10.0:
            xs.append(length)
            ys.append(total / n)

if len(xs) < 2:
    raise RuntimeError('Fewer than two valid protein-coding genes passed filters')

mx = sum(xs) / len(xs)
my = sum(ys) / len(ys)
sxx = sum((x - mx) ** 2 for x in xs)
syy = sum((y - my) ** 2 for y in ys)
sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
if sxx == 0.0 or syy == 0.0:
    raise RuntimeError('Zero variance; Pearson correlation is undefined')

r = sxy / math.sqrt(sxx * syy)
with open('result.tsv', 'w') as out:
    out.write(f'{r:.10f}\n')
