#!/usr/bin/env python3
import json
import re
import sys
import urllib.parse
import urllib.request


GENOME = "hg38"
CHROM = "chr19"
POS_1BASED = 44907187
REF = "G"
REF_LEN = len(REF)
START0 = POS_1BASED - 1
END0 = START0 + REF_LEN
TRACK = "cCREregistry"


def fetch_json(endpoint, params):
    query = ";".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    url = f"https://api.genome.ucsc.edu/getData/{endpoint}?{query}"
    with urllib.request.urlopen(url, timeout=60) as response:
        payload = response.read().decode("utf-8")
    return url, json.loads(payload)


def find_rows(obj):
    if isinstance(obj, dict):
        if TRACK in obj and isinstance(obj[TRACK], list):
            return obj[TRACK]
        rows = []
        for value in obj.values():
            rows.extend(find_rows(value))
        return rows
    if isinstance(obj, list):
        if all(isinstance(x, dict) for x in obj):
            return obj
        rows = []
        for value in obj:
            rows.extend(find_rows(value))
        return rows
    return []


def value_matching(row, pattern):
    compiled = re.compile(pattern)
    for value in row.values():
        if isinstance(value, str):
            match = compiled.search(value)
            if match:
                return match.group(0)
    return None


def class_value(row):
    for key in (
        "ccreClass",
        "cCRE_class",
        "class",
        "classification",
        "ucscLabel",
        "type",
    ):
        if key in row and isinstance(row[key], str) and row[key]:
            return row[key]
    known = {
        "promoter",
        "proximal enhancer",
        "distal enhancer",
        "CA-H3K4me3",
        "CA-CTCF",
        "CA-TF",
        "CA",
        "TF",
    }
    for value in row.values():
        if isinstance(value, str) and value in known:
            return value
    return None


def accession_value(row):
    for key in ("name", "accession", "id", "ID"):
        value = row.get(key)
        if isinstance(value, str) and value.startswith("EH38E"):
            return value
    return value_matching(row, r"EH38E[0-9]+")


def main():
    seq_url, seq_json = fetch_json(
        "sequence",
        {"genome": GENOME, "chrom": CHROM, "start": START0, "end": END0},
    )
    sequence = seq_json.get("dna") or seq_json.get("sequence")
    if sequence != REF:
        raise SystemExit(f"reference allele check failed: expected {REF}, observed {sequence!r}")

    track_url, track_json = fetch_json(
        "track",
        {
            "genome": GENOME,
            "track": TRACK,
            "chrom": CHROM,
            "start": START0,
            "end": END0,
        },
    )
    rows = []
    for row in find_rows(track_json):
        chrom = row.get("chrom") or row.get("chromosome")
        start = int(row.get("chromStart"))
        end = int(row.get("chromEnd"))
        if chrom == CHROM and start < END0 and end > START0:
            rows.append(row)

    with open("diagnostics.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "variant": {
                    "genome": "GRCh38",
                    "chrom": CHROM,
                    "position_1based": POS_1BASED,
                    "reference_span_1based_inclusive": [POS_1BASED, POS_1BASED + REF_LEN - 1],
                    "query_span_0based_half_open": [START0, END0],
                    "ref": REF,
                    "observed_sequence": sequence,
                },
                "sequence_url": seq_url,
                "track_url": track_url,
                "row_count": len(rows),
                "rows": rows,
            },
            handle,
            indent=2,
            sort_keys=True,
        )

    answers = []
    for row in rows:
        cls = class_value(row)
        acc = accession_value(row)
        if not cls or not acc:
            raise SystemExit(f"could not extract class/accession from row: {row!r}")
        answers.append((int(row.get("chromStart")), int(row.get("chromEnd")), cls, acc))

    if not answers:
        raise SystemExit("no overlapping cCRE rows found")

    answer_lines = [f"{cls},{acc}" for _, _, cls, acc in sorted(answers)]
    with open("answer.txt", "w", encoding="utf-8") as handle:
        handle.write("\n".join(answer_lines) + "\n")


if __name__ == "__main__":
    main()
