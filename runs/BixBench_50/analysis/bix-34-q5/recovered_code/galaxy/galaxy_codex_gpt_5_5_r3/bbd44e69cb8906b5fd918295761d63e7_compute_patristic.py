import itertools
import statistics
import sys
import zipfile
from io import StringIO
from Bio import Phylo

animals_zip, fungi_zip, out_path = sys.argv[1:4]


def tree_mean_patristic(newick_text):
    tree = Phylo.read(StringIO(newick_text.strip()), 'newick')
    terms = tree.get_terminals()
    if len(terms) < 2:
        raise ValueError('tree has fewer than two terminals')
    vals = []
    for a, b in itertools.combinations(terms, 2):
        vals.append(float(tree.distance(a, b)))
    return sum(vals) / len(vals), len(terms), len(vals)


def process_archive(path, group):
    rows = []
    failed = []
    with zipfile.ZipFile(path) as zf:
        names = sorted(n for n in zf.namelist() if n.endswith('.treefile') and not n.endswith('/'))
        for name in names:
            try:
                text = zf.read(name).decode('utf-8')
                mean_dist, n_terms, n_pairs = tree_mean_patristic(text)
                rows.append((group, name, n_terms, n_pairs, mean_dist))
            except Exception as exc:
                failed.append((group, name, str(exc)))
    if failed:
        msg = '; '.join(f'{g}:{n}:{e}' for g, n, e in failed[:5])
        raise RuntimeError(f'{len(failed)} failed treefile(s): {msg}')
    if not rows:
        raise RuntimeError(f'no .treefile members found for {group}')
    return rows

animal_rows = process_archive(animals_zip, 'animals')
fungi_rows = process_archive(fungi_zip, 'fungi')
all_rows = animal_rows + fungi_rows
animal_median = statistics.median(r[4] for r in animal_rows)
fungi_median = statistics.median(r[4] for r in fungi_rows)
ratio = fungi_median / animal_median
with open(out_path, 'w', encoding='utf-8') as out:
    out.write('section\tgroup\tfile\tn_terms\tn_pairs\tmean_patristic_distance\n')
    for group, name, n_terms, n_pairs, mean_dist in all_rows:
        out.write(f'per_tree\t{group}\t{name}\t{n_terms}\t{n_pairs}\t{mean_dist:.17g}\n')
    out.write(f'summary\tanimals\tmedian\t{len(animal_rows)}\tNA\t{animal_median:.17g}\n')
    out.write(f'summary\tfungi\tmedian\t{len(fungi_rows)}\tNA\t{fungi_median:.17g}\n')
    out.write(f'answer\tfungi_over_animals\tratio\tNA\tNA\t{ratio:.17g}\n')
