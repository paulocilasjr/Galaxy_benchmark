#!/usr/bin/env python3
"""Reproduce the blind first-pass BioAgent task 3 result."""

from __future__ import annotations

import csv
import gzip
import os
import time
from pathlib import Path

from bioblend.galaxy import GalaxyInstance


ROOT = Path(__file__).resolve().parents[3]
RUN = Path(__file__).resolve().parents[1]
VCF_PATH = RUN / "inputs" / "data" / "ex1.eff.vcf"
CLINVAR_PATH = RUN.parent / "public_reference_bundle"
DERIVED_CANDIDATES = RUN.parent / "segregation_candidates.tsv"
GALAXY_RESULT = RUN.parent / "galaxy_cftr_high_candidates.tsv"

AFFECTED = ["NA12879", "NA12885", "NA12886"]
PARENTS = ["NA12877", "NA12878"]
UNAFFECTED = [
    "NA12880",
    "NA12881",
    "NA12882",
    "NA12883",
    "NA12884",
    "NA12887",
    "NA12888",
    "NA12893",
    "NA12889",
    "NA12890",
    "NA12891",
    "NA12892",
]


def load_env() -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key] = value.strip().strip('"').strip("'")


def gt_class(gt: str) -> str:
    if gt in {".", "./.", ".|.", ""} or "." in gt:
        return "missing"
    values = gt.replace("|", "/").split("/")
    if len(values) == 1:
        return "hom_ref" if values[0] == "0" else "hom_alt"
    a, b = values[:2]
    if a == b == "0":
        return "hom_ref"
    if a == b and a != "0":
        return "hom_alt"
    return "het"


def parse_info_field(payload: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for token in payload.split(";"):
        if "=" in token:
            key, value = token.split("=", 1)
            parsed[key] = value
    return parsed


def build_candidate_table() -> None:
    clinvar_index: dict[tuple[str, str, str, str], tuple[str, dict[str, str]]] = {}
    with gzip.open(CLINVAR_PATH, "rt", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            chrom, pos, variant_id, ref, alt, _qual, _filt, info = line.rstrip("\n").split("\t")[:8]
            clinvar_index[(chrom, pos, ref, alt)] = (variant_id, parse_info_field(info))

    rows: list[dict[str, str]] = []
    with VCF_PATH.open(encoding="utf-8") as handle:
        samples: list[str] = []
        sample_index: dict[str, int] = {}
        for line in handle:
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                header = line.rstrip("\n").split("\t")
                samples = header[9:]
                sample_index = {sample: idx for idx, sample in enumerate(samples)}
                continue

            fields = line.rstrip("\n").split("\t")
            chrom, pos, variant_id, ref, alt, _qual, _filt, info, _fmt = fields[:9]
            genotype_fields = fields[9:]
            genotypes = {
                sample: genotype_fields[sample_index[sample]].split(":")[0]
                for sample in samples
            }
            if not all(gt_class(genotypes[sample]) == "hom_alt" for sample in AFFECTED):
                continue
            if not all(gt_class(genotypes[sample]) == "het" for sample in PARENTS):
                continue
            if any(gt_class(genotypes[sample]) == "hom_alt" for sample in UNAFFECTED):
                continue

            info_map = parse_info_field(info)
            annotations = info_map.get("ANN", "").split(",") if "ANN" in info_map else [""]
            clinvar_id, clinvar_info = clinvar_index.get((chrom, pos, ref, alt), ("", {}))

            for ann in annotations:
                columns = ann.split("|")
                while len(columns) < 16:
                    columns.append("")
                rows.append(
                    {
                        "chromosome": chrom,
                        "position": pos,
                        "variant_id": clinvar_id or variant_id,
                        "reference": ref,
                        "alternate": alt,
                        "gene_name": columns[3],
                        "gene_id": columns[4],
                        "annotation": columns[1],
                        "impact": columns[2],
                        "transcript_id": columns[6],
                        "hgvs_c": columns[9],
                        "hgvs_p": columns[10],
                        "clinical_significance": clinvar_info.get("CLNSIG", ""),
                        "diseases": clinvar_info.get("CLNDN", ""),
                        "review_status": clinvar_info.get("CLNREVSTAT", ""),
                        "rs_id": clinvar_info.get("RS", ""),
                        "affected_genotypes": ";".join(f"{sample}={genotypes[sample]}" for sample in AFFECTED),
                        "parent_genotypes": ";".join(f"{sample}={genotypes[sample]}" for sample in PARENTS),
                        "unaffected_hom_alt_count": str(
                            sum(gt_class(genotypes[sample]) == "hom_alt" for sample in UNAFFECTED)
                        ),
                    }
                )

    impact_rank = {"HIGH": 0, "MODERATE": 1, "LOW": 2, "MODIFIER": 3, "": 4}
    rows.sort(
        key=lambda row: (
            impact_rank.get(row["impact"], 9),
            row["gene_name"] != "CFTR",
            row["clinical_significance"] != "Pathogenic",
            row["chromosome"],
            int(row["position"]),
            row["transcript_id"],
        )
    )

    with DERIVED_CANDIDATES.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def wait_for_dataset(gi: GalaxyInstance, history_id: str, dataset_id: str) -> None:
    while True:
        dataset = gi.histories.show_dataset(history_id, dataset_id)
        state = dataset.get("state")
        if state == "ok":
            return
        if state == "error":
            raise RuntimeError(f"Galaxy dataset {dataset_id} failed")
        time.sleep(5)


def galaxy_select_top_candidate() -> None:
    load_env()
    gi = GalaxyInstance(url="https://usegalaxy.org", key=os.environ["GALAXY_API_KEY"])
    gi.verify = False
    history = gi.histories.create_history(name="reproduce task3 derived-candidates")
    upload = gi.tools.upload_file(
        str(DERIVED_CANDIDATES),
        history["id"],
        file_name=DERIVED_CANDIDATES.name,
        file_type="tabular",
    )
    upload_id = upload["outputs"][0]["id"]
    wait_for_dataset(gi, history["id"], upload_id)

    tool_inputs = {
        "tables_0|table": {"src": "hda", "id": upload_id},
        "tables_0|tbl_opts|table_name": "candidates",
        "tables_0|tbl_opts|column_names_from_first_line": True,
        "sqlquery": (
            "SELECT chromosome, position, variant_id, reference, alternate, gene_name, gene_id, "
            "annotation, impact, transcript_id, hgvs_c, hgvs_p, clinical_significance, diseases, "
            "review_status, rs_id "
            "FROM candidates WHERE gene_name = 'CFTR' AND impact = 'HIGH' ORDER BY position LIMIT 1"
        ),
        "query_result|header": "yes",
        "query_result|header_prefix": "",
    }
    query = gi.tools.run_tool(
        history["id"],
        "toolshed.g2.bx.psu.edu/repos/iuc/query_tabular/query_tabular/3.3.2",
        tool_inputs,
    )
    result_id = query["outputs"][0]["id"]
    wait_for_dataset(gi, history["id"], result_id)
    gi.datasets.download_dataset(result_id, file_path=str(GALAXY_RESULT), use_default_filename=False)


if __name__ == "__main__":
    build_candidate_table()
    galaxy_select_top_candidate()
