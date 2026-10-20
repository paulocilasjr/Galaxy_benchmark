import csv
import re
import sys

import scipy
from scipy.stats import hypergeom

if tuple(int(x) for x in scipy.__version__.split(".")[:2]) < (1, 0):
    raise RuntimeError("SciPy version is too old")

def bare_id(token):
    token = token.strip()
    if ":" in token:
        return token.rsplit(":", 1)[1]
    return token

def pathway_number(token):
    token = bare_id(token)
    match = re.search(r"(\d{5})$", token)
    if match is None:
        return None
    return match.group(1)

def read_gene_ids(path):
    genes = set()
    header_tokens = {
        "rowname", "gene", "gene_id", "geneid", "id", "locus_tag",
        "geneid/term", "query"
    }
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            token = line.rstrip("\r\n").split("\t", 1)[0].strip()
            if token and token.lower() not in header_tokens:
                genes.add(bare_id(token))
    return genes

def read_mapping(path):
    pathways = {}
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            fields = line.rstrip("\r\n").split("\t")
            if len(fields) < 2:
                continue
            gene = bare_id(fields[0])
            number = pathway_number(fields[1])
            if gene and number:
                pathways.setdefault(number, set()).add(gene)
    if not pathways:
        raise RuntimeError("The Galaxy KEGG mapping input had no pathway rows")
    return pathways

def benjamini_hochberg(pvalues):
    count = len(pvalues)
    adjusted = [1.0] * count
    order = sorted(range(count), key=lambda index: pvalues[index])
    running = 1.0
    for rank in range(count, 0, -1):
        index = order[rank - 1]
        running = min(running, pvalues[index] * count / float(rank))
        adjusted[index] = min(1.0, running)
    return adjusted

def ora(foreground, background, pathways):
    universe = set()
    for genes in pathways.values():
        universe.update(genes.intersection(background))
    mapped_foreground = foreground.intersection(universe)
    tested = []
    pvalues = []
    hits = {}
    for number in sorted(pathways):
        pathway_genes = pathways[number]
        overlap = len(mapped_foreground.intersection(pathway_genes))
        if overlap == 0:
            continue
        pathway_universe = len(universe.intersection(pathway_genes))
        if pathway_universe == 0:
            continue
        hits[number] = overlap
        pvalues.append(float(hypergeom.sf(
            overlap - 1, len(universe), pathway_universe, len(mapped_foreground)
        )))
        tested.append(number)
    return {
        "universe_size": len(universe),
        "foreground_size": len(mapped_foreground),
        "padj": dict(zip(tested, benjamini_hochberg(pvalues))),
        "hits": hits,
    }

def main():
    if len(sys.argv) != 6:
        raise RuntimeError("Expected four gene-list paths and one KEGG mapping path")
    iron_foreground = read_gene_ids(sys.argv[1])
    iron_background = read_gene_ids(sys.argv[2])
    innate_foreground = read_gene_ids(sys.argv[3])
    innate_background = read_gene_ids(sys.argv[4])
    pathways = read_mapping(sys.argv[5])
    iron = ora(iron_foreground, iron_background, pathways)
    innate = ora(innate_foreground, innate_background, pathways)

    pathway_numbers = sorted(set(iron["padj"]).union(innate["padj"]))
    answer_count = 0
    with open("result.tsv", "w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "pathway_id", "pathway_name", "iron_depleted_padj",
            "innate_media_padj", "iron_depleted_significant",
            "innate_media_significant", "iron_depleted_hits",
            "innate_media_hits", "kegg_organism_code",
            "iron_universe_mapped", "innate_universe_mapped"
        ])
        for number in pathway_numbers:
            iron_padj = iron["padj"].get(number, 1.0)
            innate_padj = innate["padj"].get(number, 1.0)
            iron_sig = iron_padj < 0.05
            innate_sig = innate_padj < 0.05
            if iron_sig and not innate_sig:
                answer_count += 1
            writer.writerow([
                "map" + number,
                "KEGG pathway " + number,
                "%.17g" % iron_padj,
                "%.17g" % innate_padj,
                "1" if iron_sig else "0",
                "1" if innate_sig else "0",
                str(iron["hits"].get(number, 0)),
                str(innate["hits"].get(number, 0)),
                "pau",
                str(iron["universe_size"]),
                str(innate["universe_size"])
            ])
    with open("answer.txt", "w", encoding="utf-8") as answer:
        answer.write(str(answer_count) + "\n")

main()
