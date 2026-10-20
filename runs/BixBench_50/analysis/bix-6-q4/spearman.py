import csv
import math
import sys

def read_pairs(path):
    d = {}
    with open(path, 'r', newline='') as fh:
        reader = csv.reader(fh, delimiter='\t')
        for row in reader:
            if len(row) < 2:
                continue
            refseq = row[0].strip()
            value = row[1].strip()
            if not refseq:
                continue
            try:
                x = float(value)
            except ValueError:
                continue
            if math.isnan(x):
                continue
            d[refseq] = x
    return d

def average_ranks(values):
    ordered = sorted((v, i) for i, v in enumerate(values))
    ranks = [0.0] * len(values)
    pos = 0
    while pos < len(ordered):
        end = pos + 1
        while end < len(ordered) and ordered[end][0] == ordered[pos][0]:
            end += 1
        avg_rank = (pos + 1 + end) / 2.0
        for j in range(pos, end):
            ranks[ordered[j][1]] = avg_rank
        pos = end
    return ranks

def pearson(x, y):
    n = len(x)
    mx = sum(x) / n
    my = sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    denx = sum((a - mx) ** 2 for a in x)
    deny = sum((b - my) ** 2 for b in y)
    if denx == 0.0 or deny == 0.0:
        return float('nan')
    return num / math.sqrt(denx * deny)

a = read_pairs(sys.argv[1])
b = read_pairs(sys.argv[2])
xs = []
ys = []
for key in a:
    if key in b:
        xs.append(a[key])
        ys.append(b[key])
if len(xs) < 3:
    raise SystemExit('fewer than 3 numeric matched pairs')
rho = pearson(average_ranks(xs), average_ranks(ys))
with open(sys.argv[3], 'w') as out:
    out.write('spearman_rho\tn\n')
    out.write(repr(float(rho)) + '\t' + str(len(xs)) + '\n')
