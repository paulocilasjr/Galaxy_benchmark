import csv
import itertools
import math
import statistics
import sys
import zipfile
from io import StringIO
import Bio
from Bio import Phylo

sources = [("animals", sys.argv[1]), ("fungi", sys.argv[2])]
rows = []
summary = [("biopython_version", Bio.__version__)]
medians = {}

for group, path in sources:
    with zipfile.ZipFile(path) as archive:
        names = sorted(n for n in archive.namelist() if n.endswith(".treefile") and not n.endswith("/"))
        if not names:
            raise RuntimeError(f"{group}: no .treefile members found")
        values = []
        for name in names:
            tree_text = archive.read(name).decode("utf-8").strip()
            tree = Phylo.read(StringIO(tree_text), "newick")
            tips = tree.get_terminals()
            tip_names = [tip.name for tip in tips]
            if len(tips) < 2:
                raise RuntimeError(f"{group}/{name}: fewer than two tips")
            if any(x is None or x == "" for x in tip_names) or len(set(tip_names)) != len(tip_names):
                raise RuntimeError(f"{group}/{name}: missing or duplicate tip names")
            missing = [clade for clade in tree.find_clades() if clade is not tree.root and clade.branch_length is None]
            if missing:
                raise RuntimeError(f"{group}/{name}: missing branch length")
            distances = [tree.distance(a, b) for a, b in itertools.combinations(tips, 2)]
            if not distances or any(not math.isfinite(x) or x < -1e-12 for x in distances):
                raise RuntimeError(f"{group}/{name}: invalid patristic distance")
            mean_distance = statistics.fmean(distances)
            values.append(mean_distance)
            rows.append((group, name, len(tips), len(distances), format(mean_distance, ".17g")))
        medians[group] = statistics.median(values)
        summary.extend([
            (f"{group}_selected_treefiles", str(len(names))),
            (f"{group}_processed_treefiles", str(len(values))),
            (f"{group}_median_mean_patristic_distance", format(medians[group], ".17g")),
        ])

ratio = medians["fungi"] / medians["animals"]
summary.append(("fungi_over_animals_ratio", format(ratio, ".17g")))

with open("per_tree.tsv", "w", newline="") as handle:
    writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    writer.writerow(["group", "tree", "n_tips", "n_pairs", "mean_patristic_distance"])
    writer.writerows(rows)

with open("summary.tsv", "w", newline="") as handle:
    writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    writer.writerow(["metric", "value"])
    writer.writerows(summary)
