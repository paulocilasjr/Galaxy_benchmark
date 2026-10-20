#!/usr/bin/env python3
import collections
import csv
import sys


top_path, pips_path, output_path = sys.argv[1:4]

with open(top_path, encoding="utf-8") as handle:
    reader = csv.DictReader(handle, delimiter="\t")
    top = {row["ID"]: row for row in reader}

matches = []
grouped = collections.Counter()
with open(pips_path, encoding="utf-8") as handle:
    reader = csv.DictReader(handle, delimiter="\t")
    for row in reader:
        if row["rsid"] in top:
            source = top[row["rsid"]]
            grouped[(row["trait"], row["cohort"])] += 1
            matches.append((row["trait"], row["cohort"], row["rsid"],
                            source["rank"], source["P"], row["PIP"]))

with open(output_path, "w", encoding="utf-8") as out:
    out.write("section\ttrait\tcohort\tcount\trsid\tinput_rank\tinput_p\tPIP\n")
    for (trait, cohort), count in sorted(grouped.items(), key=lambda x: (-x[1], x[0])):
        out.write(f"summary\t{trait}\t{cohort}\t{count}\t\t\t\t\n")
    for trait, cohort, rsid, rank, p_value, pip in sorted(matches):
        out.write(f"match\t{trait}\t{cohort}\t\t{rsid}\t{rank}\t{p_value}\t{pip}\n")
