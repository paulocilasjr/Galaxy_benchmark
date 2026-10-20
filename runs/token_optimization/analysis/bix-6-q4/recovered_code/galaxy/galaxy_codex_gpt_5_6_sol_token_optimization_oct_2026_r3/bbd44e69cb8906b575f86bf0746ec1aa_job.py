import csv
import sys
from scipy.stats import spearmanr

input_path = sys.argv[1]
x = []
y = []
with open(input_path, "r", newline="") as handle:
    reader = csv.DictReader(handle, delimiter="\t")
    required = ["Chronic Round1 S1", "Chronic Round1 S2"]
    if reader.fieldnames is None or any(name not in reader.fieldnames for name in required):
        raise RuntimeError("Required Chronic Round1 columns were not found")
    for row in reader:
        a = row[required[0]]
        b = row[required[1]]
        if a == "" or b == "":
            continue
        x.append(float(a))
        y.append(float(b))
rho, p_value = spearmanr(x, y)
with open("spearman.tsv", "w", newline="") as out:
    out.write("method\tcolumn_x\tcolumn_y\tn_pairs\trho\tp_value\n")
    out.write("spearman\tChronic Round1 S1\tChronic Round1 S2\t{}\t{:.17g}\t{:.17g}\n".format(len(x), float(rho), float(p_value)))
