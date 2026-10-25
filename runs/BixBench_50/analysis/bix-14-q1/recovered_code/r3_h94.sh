set -eu
python -c 'import openpyxl,sys; sys.stderr.write("openpyxl="+openpyxl.__version__+"\n")'
python - "/jetstream2/scratch/main/jobs/78853737/inputs/dataset_bc08b386-69ff-41a8-9171-cb23af41ef43.dat" result.tsv audit.tsv <<'PY'
import csv
import io
import os
import re
import sys
import tarfile
from collections import Counter
from openpyxl import load_workbook

bundle_path, result_path, audit_path = sys.argv[1:4]
CODING_TERMS = {
    "synonymous_variant", "missense_variant", "stop_gained", "stop_lost",
    "start_lost", "frameshift_variant", "inframe_insertion", "inframe_deletion",
    "protein_altering_variant", "coding_sequence_variant",
    "incomplete_terminal_codon_variant", "initiator_codon_variant",
    "feature_elongation", "feature_truncation",
}
def vals(row):
    return [c.value for c in row]
def norm_sample(value):
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    text = str(value).strip()
    return text[:-2] if text.endswith(".0") and text[:-2].isdigit() else text
def load_member(tf, member):
    fh = tf.extractfile(member)
    if fh is None:
        raise RuntimeError("Cannot extract " + member.name)
    return load_workbook(io.BytesIO(fh.read()), read_only=False, data_only=True)
def file_sample(name):
    match = re.search(r"CHIP_(.+)\.xlsx$", os.path.basename(name))
    if not match:
        return ""
    token = match.group(1)
    return token if token.startswith("SRR") else token.split("-", 1)[0]
def terms(value):
    return set() if value is None else {x.strip() for x in re.split(r"[,;&|]+", str(value)) if x.strip()}

with tarfile.open(bundle_path, "r:*") as tf:
    members = [m for m in tf.getmembers() if m.isfile() and m.name.lower().endswith(".xlsx")]
    cohort_members = [m for m in members if os.path.basename(m.name) == "230215_Trio_Status.xlsx"]
    variant_members = [m for m in members if "CHIP_DP10_GQ20_PASS/" in m.name]
    if len(members) != 88 or len(cohort_members) != 1 or len(variant_members) != 86:
        raise RuntimeError("Input inventory mismatch: total=%d cohort=%d variants=%d" % (len(members), len(cohort_members), len(variant_members)))
    cohort_wb = load_member(tf, cohort_members[0])
    ws = cohort_wb[cohort_wb.sheetnames[0]]
    rows = ws.iter_rows()
    header = vals(next(rows))
    sample_idx = header.index("Sample ID")
    blm_idx = header.index("BLM Mutation Status")
    status_idx = header.index("Status")
    cohort = {}
    for row in rows:
        rowv = vals(row)
        sample = norm_sample(rowv[sample_idx]) if sample_idx < len(rowv) else ""
        if sample:
            blm = "" if blm_idx >= len(rowv) or rowv[blm_idx] is None else str(rowv[blm_idx]).strip()
            role = "" if status_idx >= len(rowv) or rowv[status_idx] is None else str(rowv[status_idx]).strip()
            cohort[sample] = (blm, role)
    carriers = {s for s, x in cohort.items() if x[0].casefold() == "carrier"}
    available_samples = {file_sample(m.name) for m in variant_members}
    evaluable_carriers = carriers.intersection(available_samples)
    missing_carrier_files = sorted(carriers - available_samples)
    unmatched_variant_files = sorted(available_samples - set(cohort))
    if unmatched_variant_files:
        raise RuntimeError("Variant workbooks absent from cohort table: " + ",".join(unmatched_variant_files))

    consequence_counts = Counter()
    sample_rows = []
    total_low = total_coding = total_syn = 0
    processed = set()
    for member in sorted(variant_members, key=lambda m: m.name):
        sample = file_sample(member.name)
        if sample not in evaluable_carriers:
            continue
        processed.add(sample)
        wb = load_member(tf, member)
        ws = wb[wb.sheetnames[0]]
        rows = ws.iter_rows()
        vals(next(rows))
        header = vals(next(rows))
        try:
            vaf_idx = header.index("Variant Allele Freq")
            so_idx = header.index("Sequence Ontology (Combined)")
        except ValueError as exc:
            raise RuntimeError("Required column missing in %s: %s" % (member.name, exc))
        sl = sc = ss = 0
        for row in rows:
            rowv = vals(row)
            if max(vaf_idx, so_idx) >= len(rowv):
                continue
            raw = rowv[vaf_idx]
            if raw is None or str(raw).strip() == "":
                continue
            try:
                vaf = float(raw)
            except (TypeError, ValueError):
                continue
            if vaf >= 0.3:
                continue
            sl += 1
            total_low += 1
            ts = terms(rowv[so_idx])
            if ts:
                for term in sorted(ts):
                    consequence_counts[term] += 1
            else:
                consequence_counts["<blank>"] += 1
            if ts.intersection(CODING_TERMS):
                sc += 1
                total_coding += 1
                if "synonymous_variant" in ts:
                    ss += 1
                    total_syn += 1
        sample_rows.append((sample, cohort[sample][1], cohort[sample][0], sl, sc, ss))
    if processed != evaluable_carriers:
        raise RuntimeError("Not all evaluable carriers were processed")
if total_coding == 0:
    raise RuntimeError("No coding variants with VAF < 0.3")
if total_syn > total_coding:
    raise RuntimeError("Synonymous numerator exceeds coding denominator")
fraction = total_syn / float(total_coding)

with open(result_path, "w", newline="") as out:
    w = csv.writer(out, delimiter="\t", lineterminator="\n")
    w.writerow(["cohort", "vaf_rule", "analysis_unit", "carrier_samples", "coding_variants", "synonymous_variants", "fraction"])
    w.writerow(["BLM Mutation Status=Carrier with supplied variant workbook", "VAF<0.3", "sample-variant rows", len(processed), total_coding, total_syn, format(fraction, ".12g")])
with open(audit_path, "w", newline="") as out:
    w = csv.writer(out, delimiter="\t", lineterminator="\n")
    w.writerow(["section", "key", "value1", "value2", "value3", "value4"])
    for key, value in [
        ("xlsx_inputs", len(members)), ("variant_workbooks", len(variant_members)),
        ("cohort_rows", len(cohort)), ("carrier_labels", len(carriers)),
        ("evaluable_carriers", len(evaluable_carriers)), ("processed_carrier_samples", len(processed)),
        ("all_low_vaf_rows_in_carriers", total_low), ("coding_low_vaf_rows", total_coding),
        ("synonymous_coding_low_vaf_rows", total_syn)]:
        w.writerow(["scope", key, value, "", "", ""])
    w.writerow(["scope", "metadata_carriers_without_workbook", ",".join(missing_carrier_files), "", "", ""])
    for sample, role, blm, low, coding, syn in sample_rows:
        w.writerow(["sample", sample, role, blm, low, "%d;%d" % (coding, syn)])
    for term, count in sorted(consequence_counts.items()):
        w.writerow(["consequence", term, count, "coding" if term in CODING_TERMS else "noncoding", "", ""])

PY
