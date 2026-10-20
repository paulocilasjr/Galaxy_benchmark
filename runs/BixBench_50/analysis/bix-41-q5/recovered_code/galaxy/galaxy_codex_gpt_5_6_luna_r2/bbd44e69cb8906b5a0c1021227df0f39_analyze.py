import csv
import math
import re
from collections import defaultdict

input_path = "/jetstream2/scratch/main/jobs/78873240/inputs/dataset_780ca9f5-aeb1-4cc9-99e8-a08c124a6c7f.dat"
groups = defaultdict(list)
target = []

with open(input_path, newline="") as fh:
    reader = csv.DictReader(fh)
    required = {"StrainNumber", "Ratio", "Area", "Circularity"}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise SystemExit("missing required columns: " + ",".join(sorted(missing)))
    for row in reader:
        strain = row["StrainNumber"].strip()
        ratio = row["Ratio"].strip()
        area = float(row["Area"])
        circularity = float(row["Circularity"])
        groups[(strain, ratio)].append((area, circularity))
        if strain == "1":
            target.append((area, circularity))

if not target:
    raise SystemExit("no Strain 1 rows found")

target_area = sum(x[0] for x in target) / len(target)
target_circularity = sum(x[1] for x in target) / len(target)

def is_mixed_label(strain):
    nums = re.findall(r"\d+", strain)
    return ("98" in nums and "287" in nums) or ("98" in strain and "287" in strain)

records = []
for (strain, ratio), values in groups.items():
    mean_area = sum(x[0] for x in values) / len(values)
    mean_circularity = sum(x[1] for x in values) / len(values)
    is_target = (strain == "1")
    area_rel = abs(mean_area - target_area) / abs(target_area) if target_area else float("inf")
    circ_rel = abs(mean_circularity - target_circularity) / abs(target_circularity) if target_circularity else float("inf")
    rel_distance = math.sqrt(area_rel * area_rel + circ_rel * circ_rel)
    records.append((strain, ratio, len(values), mean_area, mean_circularity,
                    area_rel, circ_rel, rel_distance, is_target, is_mixed_label(strain)))

records.sort(key=lambda x: (x[0], x[1]))
with open("group_summary.tsv", "w", newline="") as out:
    writer = csv.writer(out, delimiter="\t", lineterminator="\n")
    writer.writerow(["StrainNumber", "Ratio", "N", "MeanArea", "MeanCircularity",
                     "Strain1MeanArea", "Strain1MeanCircularity",
                     "RelativeAreaDifference", "RelativeCircularityDifference",
                     "RelativeEuclideanDistance", "IsStrain1", "IsMixedLabel"])
    for rec in records:
        writer.writerow([rec[0], rec[1], rec[2], f"{rec[3]:.12g}", f"{rec[4]:.12g}",
                         f"{target_area:.12g}", f"{target_circularity:.12g}",
                         f"{rec[5]:.12g}", f"{rec[6]:.12g}", f"{rec[7]:.12g}",
                         "true" if rec[8] else "false", "true" if rec[9] else "false"])
