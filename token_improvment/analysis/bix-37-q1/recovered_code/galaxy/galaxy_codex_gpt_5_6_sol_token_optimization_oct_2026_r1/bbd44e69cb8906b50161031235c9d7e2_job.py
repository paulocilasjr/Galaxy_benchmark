import csv
import sys
from decimal import Decimal, getcontext

getcontext().prec = 40
input_path = sys.argv[1]
matches = []
with open(input_path, "r", encoding="utf-8-sig", newline="") as handle:
    reader = csv.DictReader(handle, delimiter="\t")
    required = {"gene", "Normal", "Tumor"}
    if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
        raise RuntimeError("Required columns gene, Normal, and Tumor were not found")
    for row in reader:
        if row["gene"].strip() == "ENO1":
            matches.append(row)

if len(matches) != 1:
    raise RuntimeError(f"Expected exactly one ENO1 row, found {len(matches)}")

row = matches[0]
normal = Decimal(row["Normal"].strip())
tumor = Decimal(row["Tumor"].strip())
if normal == 0:
    raise ZeroDivisionError("ENO1 Normal abundance is zero")
fold_change = tumor / normal

with open("eno1_fold_change.tsv", "w", encoding="utf-8", newline="") as out:
    out.write("gene\tnormal_abundance\ttumor_abundance\ttumor_over_normal_fold_change\n")
    out.write(f"ENO1\t{normal}\t{tumor}\t{fold_change}\n")
