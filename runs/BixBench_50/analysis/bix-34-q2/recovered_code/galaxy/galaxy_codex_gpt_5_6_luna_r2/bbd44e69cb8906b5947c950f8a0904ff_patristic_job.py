import csv
import io
import math
import statistics
import sys
import zipfile
from Bio import Phylo

archive_path = sys.argv[1]
gene = sys.argv[2].strip()
expected_member = gene + ".faa.mafft.clipkit.treefile"

with zipfile.ZipFile(archive_path, "r") as archive:
    matches = [name for name in archive.namelist()
               if name == expected_member or name.rsplit("/", 1)[-1] == expected_member]
    if len(matches) != 1:
        raise SystemExit("expected exactly one target tree member, found " + str(len(matches)))
    member = matches[0]
    newick = archive.read(member).decode("utf-8")

tree = Phylo.read(io.StringIO(newick), "newick")
terminals = tree.get_terminals()
labels = [terminal.name for terminal in terminals]
if len(terminals) < 2:
    raise SystemExit("target tree has fewer than two terminal taxa")
if any(label is None or not label.strip() for label in labels):
    raise SystemExit("target tree contains an unlabeled terminal taxon")
if len(set(labels)) != len(labels):
    raise SystemExit("target tree contains duplicate terminal labels")

missing_lengths = []
for clade in tree.find_clades():
    if clade is not tree.root and clade.branch_length is None:
        missing_lengths.append(clade.name or "<internal>")
if missing_lengths:
    raise SystemExit("target tree has missing branch lengths: " + ",".join(missing_lengths))

distances = []
pairs = []
for i, left in enumerate(terminals):
    for right in terminals[i + 1:]:
        distance = float(tree.distance(left, right))
        if not math.isfinite(distance):
            raise SystemExit("non-finite patristic distance encountered")
        distances.append(distance)
        pairs.append(labels[i] + "|" + right.name + "=" + format(distance, ".17g"))

median_distance = statistics.median(distances)
with open("patristic_result.tsv", "w", newline="") as handle:
    writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
    writer.writerow([
        "gene", "tree_member", "terminal_taxa", "unordered_pairs",
        "median_patristic_distance", "taxa", "pairwise_patristic_distances"
    ])
    writer.writerow([
        gene, member, str(len(terminals)), str(len(distances)),
        format(median_distance, ".17g"), "|".join(labels), ";".join(pairs)
    ])
