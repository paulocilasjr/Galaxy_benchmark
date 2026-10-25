#!/opt/conda/bin/python
"""Retain complete primary Bowtie2 pairs meeting the requested ATAC filters."""

import argparse
import json

import pysam


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_bam")
    parser.add_argument("output_bam")
    parser.add_argument("stats_json")
    parser.add_argument("--min-mapq", type=int, default=30)
    parser.add_argument("--mitochondrial-contig", default="chrM")
    args = parser.parse_args()

    counts = {
        "input_query_groups": 0,
        "retained_pairs": 0,
        "rejected_incomplete_or_nonprimary": 0,
        "rejected_not_valid_pair": 0,
        "rejected_low_mapq": 0,
        "rejected_mitochondrial": 0,
    }

    with pysam.AlignmentFile(args.input_bam, "rb") as source:
        with pysam.AlignmentFile(args.output_bam, "wb", template=source) as target:
            current_name = None
            group = []

            def process(records):
                if not records:
                    return
                counts["input_query_groups"] += 1
                primary = [
                    rec
                    for rec in records
                    if not rec.is_secondary and not rec.is_supplementary
                ]
                if (
                    len(primary) != 2
                    or sum(rec.is_read1 for rec in primary) != 1
                    or sum(rec.is_read2 for rec in primary) != 1
                ):
                    counts["rejected_incomplete_or_nonprimary"] += 1
                    return
                if any(
                    rec.is_unmapped
                    or rec.mate_is_unmapped
                    or not rec.is_proper_pair
                    for rec in primary
                ):
                    counts["rejected_not_valid_pair"] += 1
                    return
                if any(rec.mapping_quality < args.min_mapq for rec in primary):
                    counts["rejected_low_mapq"] += 1
                    return
                if any(
                    rec.reference_name == args.mitochondrial_contig
                    or rec.next_reference_name == args.mitochondrial_contig
                    for rec in primary
                ):
                    counts["rejected_mitochondrial"] += 1
                    return
                for rec in primary:
                    target.write(rec)
                counts["retained_pairs"] += 1

            for record in source.fetch(until_eof=True):
                if current_name is None:
                    current_name = record.query_name
                if record.query_name != current_name:
                    process(group)
                    group = []
                    current_name = record.query_name
                group.append(record)
            process(group)

    with open(args.stats_json, "w", encoding="utf-8") as handle:
        json.dump(counts, handle, indent=2, sort_keys=True)
        handle.write("\n")


if __name__ == "__main__":
    main()
