#!/usr/bin/env python3
import io
import json
import os
import sys
import zipfile


QUERY_PATH, ARCHIVE_PATH, METADATA_PATH, PUBMED_PATH, REPORT_PATH, ANSWER_PATH = sys.argv[1:]

TARGETS = {
    "chr1:14671:G:C",
    "chr1:64649:A:C",
    "chr1:161530617:CTT:C",
    "chr17:16939677:G:A",
}
EXPECTED_TITLE = "MultiSuSiE improves multi-ancestry fine-mapping in All of Us whole-genome sequencing data"
EXPECTED_DOI = "10.1038/s41588-025-02450-5"


def read_selected_rows(path, targets):
    found = {}
    with open(path, "rb") as handle:
        header = handle.readline().rstrip(b"\r\n").decode("utf-8").split("\t")
        index = {name: i for i, name in enumerate(header)}
        id_i = index["ID"]
        for raw_line in handle:
            fields = raw_line.rstrip(b"\r\n").decode("utf-8").split("\t")
            variant_id = fields[id_i]
            if variant_id in targets:
                found[variant_id] = {name: fields[i] for name, i in index.items()}
                if len(found) == len(targets):
                    break
    return header, found


def read_archive_rows(archive, targets):
    found = {}
    chromosomes = sorted({variant_id.split(":", 2)[0].removeprefix("chr") for variant_id in targets}, key=int)
    for chromosome in chromosomes:
        member = f"eur115620/ss_eur115620_{chromosome}.tsv"
        chromosome_targets = {v for v in targets if v.startswith(f"chr{chromosome}:")}
        with archive.open(member, "r") as binary_handle:
            header = binary_handle.readline().rstrip(b"\r\n").decode("utf-8").split("\t")
            index = {name: i for i, name in enumerate(header)}
            id_i = index["ID"]
            for raw_line in binary_handle:
                fields = raw_line.rstrip(b"\r\n").decode("utf-8").split("\t")
                variant_id = fields[id_i]
                if variant_id in chromosome_targets:
                    found[variant_id] = {name: fields[i] for name, i in index.items()}
                    if chromosome_targets.issubset(found):
                        break
    return found


with open(METADATA_PATH, encoding="utf-8") as handle:
    metadata = json.load(handle)
with open(PUBMED_PATH, encoding="utf-8") as handle:
    pubmed = json.load(handle)

record_id = str(metadata["id"])
release_doi = metadata["doi"]
release_title = metadata["metadata"]["title"]
archive_manifest = next(item for item in metadata["files"] if item["key"] == "eur115620.zip")
manifest_size = int(archive_manifest["size"])
actual_size = os.path.getsize(ARCHIVE_PATH)

uid_list = pubmed["result"]["uids"]
if len(uid_list) != 1:
    raise RuntimeError(f"Expected one PubMed result, received {uid_list!r}")
pmid = uid_list[0]
publication = pubmed["result"][pmid]
publication_title = publication["title"].rstrip(".")
publication_doi = publication["elocationid"].removeprefix("doi: ")

query_header, query_rows = read_selected_rows(QUERY_PATH, TARGETS)

with zipfile.ZipFile(ARCHIVE_PATH) as archive:
    source_members = sorted(name for name in archive.namelist() if name.endswith(".tsv"))
    expected_members = sorted(f"eur115620/ss_eur115620_{chromosome}.tsv" for chromosome in range(1, 23))
    source_rows = read_archive_rows(archive, TARGETS)

checks = []


def check(item, observed, expected):
    matches = observed == expected
    checks.append((item, str(observed), str(expected), "PASS" if matches else "FAIL"))
    return matches


check("Zenodo record ID", record_id, "17370173")
check("Zenodo DOI", release_doi, "10.5281/zenodo.17370173")
check("Release title identifies MultiSuSiE study", EXPECTED_TITLE in release_title, True)
check("Archive byte size", actual_size, manifest_size)
check("Archive chromosome member count", len(source_members), 22)
check("Archive members chr1-chr22", source_members, expected_members)
check("Query header", query_header, ["#CHROM", "POS", "ID", "REF", "ALT", "A1", "TEST", "P"])
check("Query target count", len(query_rows), len(TARGETS))
check("Source target count", len(source_rows), len(TARGETS))
check("PubMed result count", len(uid_list), 1)
check("Publication title", publication_title, EXPECTED_TITLE)
check("Publication DOI", publication_doi, EXPECTED_DOI)

for variant_id in sorted(TARGETS):
    query_row = query_rows.get(variant_id, {})
    source_row = source_rows.get(variant_id, {})
    for field in ("ID", "REF", "ALT", "A1", "TEST"):
        check(f"{variant_id} {field}", query_row.get(field), source_row.get(field))
    check(f"{variant_id} P equals protein_density_P", query_row.get("P"), source_row.get("protein_density_P"))

all_pass = all(status == "PASS" for _, _, _, status in checks)
with open(REPORT_PATH, "w", encoding="utf-8") as handle:
    handle.write("item\tobserved\texpected\tstatus\n")
    for item, observed, expected, status in checks:
        handle.write(f"{item}\t{observed}\t{expected}\t{status}\n")
    handle.write(f"summary\tall checks pass\tTrue\t{'PASS' if all_pass else 'FAIL'}\n")
    handle.write(f"identified_pmid\t{pmid}\tPubMed UID for DOI {EXPECTED_DOI}\t{'PASS' if all_pass else 'FAIL'}\n")

if not all_pass:
    raise RuntimeError("Source identity verification failed; inspect the report")

with open(ANSWER_PATH, "w", encoding="utf-8") as handle:
    handle.write(pmid + "\n")
