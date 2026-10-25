#!/usr/bin/env python3
import csv
import sys
import xml.etree.ElementTree as ET


match_path, pubmed_path, pmid_path, audit_path = sys.argv[1:5]
with open(match_path, encoding="utf-8") as handle:
    summaries = [row for row in csv.DictReader(handle, delimiter="\t")
                 if row["section"] == "summary"]

traits = {row["trait"] for row in summaries}
cohorts = {row["cohort"] for row in summaries}
if traits != {"protein_density"}:
    raise SystemExit("Fingerprint did not uniquely identify protein_density")
required_v1_cohorts = {"eur94082", "afr47041_eur94082"}
if not required_v1_cohorts.issubset(cohorts):
    raise SystemExit("Fingerprint does not identify the original Eur94k study version")

target_title = "MultiSuSiE improves multi-ancestry fine-mapping in All of Us whole-genome sequencing data"
root = ET.parse(pubmed_path).getroot()
candidates = []
for article in root.findall(".//PubmedArticle"):
    title_node = article.find(".//ArticleTitle")
    title = "".join(title_node.itertext()).rstrip(".") if title_node is not None else ""
    pmid = article.findtext(".//MedlineCitation/PMID")
    types = {"".join(node.itertext()) for node in article.findall(".//PublicationType")}
    if title == target_title:
        candidates.append((pmid, types))

preprints = [pmid for pmid, types in candidates if "Preprint" in types]
if len(preprints) != 1:
    raise SystemExit("Could not uniquely resolve the original PubMed preprint record")

with open(pmid_path, "w", encoding="utf-8") as out:
    out.write(preprints[0] + "\n")
with open(audit_path, "w", encoding="utf-8") as out:
    out.write("check\tvalue\n")
    out.write("matched_trait\tprotein_density\n")
    out.write("matched_original_cohort\teur94082\n")
    out.write("matching_pubmed_title\t" + target_title + "\n")
    out.write("selected_record_type\tPreprint\n")
    out.write("selected_pmid\t" + preprints[0] + "\n")
