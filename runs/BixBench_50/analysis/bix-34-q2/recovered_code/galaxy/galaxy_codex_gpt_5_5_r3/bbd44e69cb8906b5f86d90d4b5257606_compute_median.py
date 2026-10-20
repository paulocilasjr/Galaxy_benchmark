from Bio import Phylo
from itertools import combinations
import sys

tree_path = sys.argv[1]
out_path = sys.argv[2]
tree = Phylo.read(tree_path, 'newick')
tips = tree.get_terminals()
if len(tips) < 2:
    raise SystemExit('need at least two tips')
values = sorted(tree.distance(a, b) for a, b in combinations(tips, 2))
n = len(values)
if n % 2:
    median = values[n // 2]
else:
    median = (values[n // 2 - 1] + values[n // 2]) / 2.0
with open(out_path, 'w') as out:
    out.write(format(median, '.12g') + '\n')
