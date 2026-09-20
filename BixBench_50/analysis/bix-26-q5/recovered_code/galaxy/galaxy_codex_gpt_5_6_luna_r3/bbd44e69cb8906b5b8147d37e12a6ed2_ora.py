import csv
import math
import re
import sys
import urllib.error
import urllib.request

import scipy
from scipy.stats import hypergeom

if tuple(int(x) for x in scipy.__version__.split(".")[:2]) < (1, 0):
    raise RuntimeError("SciPy version is too old")

def fetch(path):
    errors = []
    for scheme in ("https", "http"):
        url = scheme + "://rest.kegg.jp/" + path
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "GalaxyUserTool-pa14-kegg-ora/0.1"}
            )
            with urllib.request.urlopen(request, timeout=90) as response:
                body = response.read().decode("utf-8")
            if body.strip():
                return body
            errors.append(url + ": empty response")
        except Exception as exc:
            errors.append(url + ": " + str(exc))
    raise RuntimeError("KEGG REST request failed: " + " | ".join(errors))

def read_gene_ids(path):
    genes = set()
    header_tokens = {
        "rowname", "gene", "gene_id", "geneid", "id", "locus_tag",
        "geneid/term", "query"
    }
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            token = line.rstrip("\r\n").split("\t", 1)[0].strip()
            if not token:
                continue
            if token.lower() in header_tokens:
                continue
            genes.add(token)
    return genes

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

def organism_candidates():
    records = []
    try:
        body = fetch("list/organism")
        for line in body.splitlines():
            fields = line.split("\t")
            if len(fields) >= 3:
                code = fields[1].strip()
                full = line.lower()
                if "pseudomonas aeruginosa" in full:
                    is_pa14 = ("pa14" in full) or ("ucbpp-pa14" in full)
                    records.append((is_pa14, code))
    except Exception:
        records = []
    ordered = []
    for is_pa14, code in sorted(records, key=lambda item: (not item[0], item[1])):
        if code not in ordered:
            ordered.append(code)
    for code in ("paz", "pae"):
        if code not in ordered:
            ordered.append(code)
    return ordered

def load_mapping(code):
    body = fetch("link/pathway/" + code)
    pathways = {}
    for line in body.splitlines():
        fields = line.split("\t")
        if len(fields) < 2:
            continue
        gene = bare_id(fields[0])
        number = pathway_number(fields[1])
        if gene and number:
            pathways.setdefault(number, set()).add(gene)
    return pathways

def load_names(code):
    names = {}
    for endpoint in ("list/pathway/" + code, "list/pathway"):
        try:
            body = fetch(endpoint)
        except Exception:
            continue
        for line in body.splitlines():
            fields = line.split("\t", 1)
            if len(fields) < 2:
                continue
            number = pathway_number(fields[0])
            if number and number not in names:
                names[number] = fields[1].strip()
        if names:
            break
    return names

def benjamini_hochberg(pvalues):
    count = len(pvalues)
    adjusted = [1.0] * count
    order = sorted(range(count), key=lambda index: pvalues[index])
    running = 1.0
    for rank in range(count, 0, -1):
        index = order[rank - 1]
        value = pvalues[index] * count / float(rank)
        running = min(running, value)
        adjusted[index] = min(1.0, running)
    return adjusted

def ora(foreground, background, pathways):
    universe = set()
    for genes in pathways.values():
        universe.update(genes.intersection(background))
    foreground_mapped = foreground.intersection(universe)
    tested = []
    pvalues = []
    counts = {}
    for number in sorted(pathways):
        pathway_genes = pathways[number]
        k = len(foreground_mapped.intersection(pathway_genes))
        if k == 0:
            continue
        K = len(universe.intersection(pathway_genes))
        if K == 0:
            continue
        counts[number] = k
        pvalue = float(hypergeom.sf(k - 1, len(universe), K, len(foreground_mapped)))
        tested.append(number)
        pvalues.append(pvalue)
    adjusted = benjamini_hochberg(pvalues)
    return {
        "universe_size": len(universe),
        "foreground_size": len(foreground_mapped),
        "padj": dict(zip(tested, adjusted)),
        "hits": counts,
    }

def main():
    if len(sys.argv) != 5:
        raise RuntimeError("Expected four Galaxy input paths")
    iron_foreground = read_gene_ids(sys.argv[1])
    iron_background = read_gene_ids(sys.argv[2])
    innate_foreground = read_gene_ids(sys.argv[3])
    innate_background = read_gene_ids(sys.argv[4])
    background_union = iron_background.union(innate_background)
    if not background_union:
        raise RuntimeError("Both supplied backgrounds are empty")

    selected_code = None
    selected_mapping = None
    selected_score = -1
    selected_pa14 = False
    candidates = organism_candidates()
    for code in candidates:
        try:
            mapping = load_mapping(code)
        except Exception:
            continue
        mapped_background = set()
        for genes in mapping.values():
            mapped_background.update(genes.intersection(background_union))
        score = len(mapped_background)
        is_pa14 = code in candidates[:1] and code not in ("paz", "pae")
        if score > 0 and (
            selected_mapping is None
            or (is_pa14 and not selected_pa14)
            or (is_pa14 == selected_pa14 and score > selected_score)
        ):
            selected_code = code
            selected_mapping = mapping
            selected_score = score
            selected_pa14 = is_pa14

    if selected_mapping is None or selected_score == 0:
        raise RuntimeError(
            "No Pseudomonas aeruginosa KEGG mapping overlapped the supplied universe"
        )

    names = load_names(selected_code)
    iron = ora(iron_foreground, iron_background, selected_mapping)
    innate = ora(innate_foreground, innate_background, selected_mapping)
    all_numbers = sorted(set(iron["padj"]).union(innate["padj"]))
    answer_count = 0

    with open("result.tsv", "w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "pathway_id", "pathway_name", "iron_depleted_padj",
            "innate_media_padj", "iron_depleted_significant",
            "innate_media_significant", "iron_depleted_hits",
            "innate_media_hits", "kegg_organism_code"
        ])
        for number in all_numbers:
            iron_padj = iron["padj"].get(number, 1.0)
            innate_padj = innate["padj"].get(number, 1.0)
            iron_sig = iron_padj < 0.05
            innate_sig = innate_padj < 0.05
            if iron_sig and not innate_sig:
                answer_count += 1
            writer.writerow([
                "map" + number,
                names.get(number, "KEGG pathway " + number).replace("\t", " "),
                "%.17g" % iron_padj,
                "%.17g" % innate_padj,
                "1" if iron_sig else "0",
                "1" if innate_sig else "0",
                str(iron["hits"].get(number, 0)),
                str(innate["hits"].get(number, 0)),
                selected_code
            ])

    with open("answer.txt", "w", encoding="utf-8") as answer:
        answer.write(str(answer_count) + "\n")

main()
