import concurrent.futures
import json
import sys
import urllib.request


locus_path, output_path, *catalog_paths = sys.argv[1:]

input_loci = []
in_ranked = False
with open(locus_path, encoding="utf-8") as handle:
    for line in handle:
        fields = line.rstrip("\n\r").split("\t")
        if fields[0] == "rank":
            in_ranked = True
            continue
        if in_ranked and len(fields) >= 10:
            p = float(fields[9])
            if p < 5e-8:
                input_loci.append((fields[2], int(fields[3]), fields[4], p))


def parse_catalog(path):
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    associations = payload.get("_embedded", {}).get("associations", [])
    if not associations:
        raise ValueError(f"No associations in {path}")
    study = associations[0]["study"]
    rsids = set()
    for association in associations:
        for locus in association.get("loci", []):
            for risk in locus.get("strongestRiskAlleles", []):
                rsid = risk.get("riskAlleleName", "").split("-", 1)[0]
                if rsid.startswith("rs"):
                    rsids.add(rsid)
    return {
        "accession": study["accessionId"],
        "trait": study["diseaseTrait"]["trait"],
        "pmid": study["publicationInfo"]["pubmedId"],
        "title": study["publicationInfo"]["title"],
        "rsids": sorted(rsids),
    }


catalogs = [parse_catalog(path) for path in catalog_paths]
all_rsids = sorted({rsid for catalog in catalogs for rsid in catalog["rsids"]})


def resolve_grch38(rsid):
    url = f"https://rest.ensembl.org/variation/human/{rsid}?content-type=application/json"
    request = urllib.request.Request(url, headers={"User-Agent": "Galaxy-GWAS-locus-validator/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.load(response)
    mappings = []
    for mapping in data.get("mappings", []):
        if mapping.get("assembly_name") == "GRCh38" and mapping.get("seq_region_name") in {str(i) for i in range(1, 23)}:
            mappings.append((mapping["seq_region_name"], int(mapping["start"])))
    return rsid, sorted(set(mappings))


resolved = {}
failed = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
    futures = {executor.submit(resolve_grch38, rsid): rsid for rsid in all_rsids}
    for future in concurrent.futures.as_completed(futures):
        rsid = futures[future]
        try:
            _, mappings = future.result()
            resolved[rsid] = mappings
        except Exception as exc:
            failed[rsid] = type(exc).__name__

rows = []
for catalog in catalogs:
    catalog_variants = []
    for rsid in catalog["rsids"]:
        for chrom, pos in resolved.get(rsid, []):
            catalog_variants.append((chrom, pos, rsid))
    matched_inputs = []
    for chrom, pos, variant, p in input_loci:
        candidates = [(abs(pos - ref_pos), ref_pos, rsid) for ref_chrom, ref_pos, rsid in catalog_variants if ref_chrom == chrom]
        if candidates:
            distance, ref_pos, rsid = min(candidates)
            if distance <= 1_000_000:
                matched_inputs.append((chrom, pos, variant, p, rsid, ref_pos, distance))
    rows.append((catalog, catalog_variants, matched_inputs))

rows.sort(key=lambda x: (-len(x[2]), x[0]["accession"]))
with open(output_path, "w", encoding="utf-8") as out:
    out.write(f"input_significant_locus_count\t{len(input_loci)}\n")
    out.write(f"catalog_variant_resolution_failures\t{len(failed)}\n")
    out.write("accession\ttrait\tpmid\tcatalog_lead_count\tresolved_lead_count\tmatched_input_loci_within_1Mb\ttitle\n")
    for catalog, catalog_variants, matched_inputs in rows:
        out.write("\t".join([
            catalog["accession"], catalog["trait"], catalog["pmid"],
            str(len(catalog["rsids"])), str(len(catalog_variants)), str(len(matched_inputs)), catalog["title"]
        ]) + "\n")
    out.write("match_accession\tinput_chrom\tinput_pos\tinput_variant\tinput_p\tcatalog_rsid\tcatalog_pos_grch38\tdistance_bp\n")
    for catalog, _, matched_inputs in rows:
        for chrom, pos, variant, p, rsid, ref_pos, distance in sorted(matched_inputs, key=lambda x: x[6]):
            out.write(f"{catalog['accession']}\t{chrom}\t{pos}\t{variant}\t{p:.8g}\t{rsid}\t{ref_pos}\t{distance}\n")
