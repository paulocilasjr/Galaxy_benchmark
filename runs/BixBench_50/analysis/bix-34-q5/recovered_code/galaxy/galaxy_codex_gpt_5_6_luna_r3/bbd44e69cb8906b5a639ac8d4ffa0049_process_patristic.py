import csv
import sys
import zipfile
import dendropy

def process_archive(archive_path, group, summary_writer, failure_writer):
    with zipfile.ZipFile(archive_path, "r") as archive:
        members = sorted(name for name in archive.namelist() if name.endswith(".treefile"))
        for member in members:
            try:
                newick = archive.read(member).decode("utf-8")
                tree = dendropy.Tree.get(
                    data=newick,
                    schema="newick",
                    preserve_underscores=True,
                )
                taxa = [
                    node.taxon
                    for node in tree.leaf_node_iter()
                    if node.taxon is not None
                ]
                if len(taxa) < 2:
                    raise ValueError("fewer than two terminal taxa")
                distance_matrix = tree.phylogenetic_distance_matrix()
                distances = []
                for i, taxon_a in enumerate(taxa[:-1]):
                    for taxon_b in taxa[i + 1:]:
                        distance = distance_matrix.distance(taxon_a, taxon_b)
                        if distance is None:
                            raise ValueError("missing patristic distance")
                        distances.append(float(distance))
                if not distances:
                    raise ValueError("no tip-to-tip distances")
                mean_distance = sum(distances) / len(distances)
                summary_writer.writerow([
                    group,
                    member,
                    format(mean_distance, ".17g"),
                    len(taxa),
                    len(distances),
                    "ok",
                ])
            except Exception as exc:
                message = f"{type(exc).__name__}: {exc}".replace("\t", " ").replace("\n", " ")
                failure_writer.writerow([group, member, message])

with open("patristic_summary.tsv", "w", newline="") as summary_file, open(
    "patristic_failures.tsv", "w", newline=""
) as failure_file:
    summary_writer = csv.writer(summary_file, delimiter="\t", lineterminator="\n")
    failure_writer = csv.writer(failure_file, delimiter="\t", lineterminator="\n")
    summary_writer.writerow([
        "group",
        "member",
        "mean_patristic_distance",
        "n_taxa",
        "n_pairs",
        "status",
    ])
    failure_writer.writerow(["group", "member", "error"])
    process_archive("/jetstream2/scratch/main/jobs/78878769/inputs/dataset_08ec74c0-a79d-4683-b47a-f894a91d31f7.dat", "animals", summary_writer, failure_writer)
    process_archive("/jetstream2/scratch/main/jobs/78878769/inputs/dataset_feeb634d-25aa-4b7f-b5e9-96db97e1de1f.dat", "fungi", summary_writer, failure_writer)
