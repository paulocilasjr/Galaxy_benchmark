import csv
import sys


source_path, output_path = sys.argv[1:3]
threshold = 5e-8
window = 1_000_000
max_leads = 50

leads = []
significant_rows = 0
data_rows = 0

with open(source_path, "rt", encoding="utf-8", newline="") as source:
    reader = csv.reader(source, delimiter="\t")
    for row in reader:
        if not row or row[0].startswith("#"):
            continue
        data_rows += 1
        chrom = row[0]
        pos = int(row[1])
        p_value = float(row[7])
        if p_value >= threshold:
            continue
        significant_rows += 1
        if len(leads) >= max_leads:
            continue
        if any(chrom == lead[0] and abs(pos - lead[1]) <= window for lead in leads):
            continue
        leads.append((chrom, pos, row[2], row[3], row[4], row[5], p_value))

with open(output_path, "wt", encoding="utf-8", newline="") as output:
    output.write(f"#diagnostic\tvalue\n")
    output.write(f"#data_rows\t{data_rows}\n")
    output.write(f"#p_lt_5e-8_rows\t{significant_rows}\n")
    output.write(f"#lead_window_bp\t{window}\n")
    output.write("rank\tCHROM\tPOS\tID\tREF\tALT\tA1\tP\n")
    for rank, lead in enumerate(leads, 1):
        chrom, pos, variant_id, ref, alt, a1, p_value = lead
        output.write(
            f"{rank}\t{chrom}\t{pos}\t{variant_id}\t{ref}\t{alt}\t{a1}\t{p_value:.12g}\n"
        )
