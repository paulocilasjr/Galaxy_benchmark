import csv
import gzip
import os
import sys


def norm(value):
    return value.strip().lower()


def close_p(left, right):
    try:
        return norm(left) == norm(right)
    except AttributeError:
        return False


def read_target_map(path):
    result = {}
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            result[row["rsid"]] = row
    return result


def read_r37_map(path, wanted):
    result = {}
    with open(path, newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        next(reader, None)
        for row in reader:
            if len(row) >= 3 and row[0] in wanted:
                result[row[0]] = (row[1], row[2])
    return result


def source_rows(path, wanted):
    with gzip.open(path, "rt", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        header = next(reader, None)
        if not header:
            return {}
        columns = {norm(value): index for index, value in enumerate(header)}
        rs_index = columns.get("snp")
        p_index = columns.get("p")
        if rs_index is None or p_index is None:
            return {}
        found = {}
        for row in reader:
            if len(row) <= max(rs_index, p_index):
                continue
            rsid = row[rs_index]
            if rsid in wanted:
                found[rsid] = row[p_index]
        return found


def main(source_dir, target_map_path, r37_map_path, output_path):
    target = read_target_map(target_map_path)
    r37 = read_r37_map(r37_map_path, set(target))
    files = []
    for root, _, names in os.walk(source_dir):
        for name in names:
            if name.endswith(".txt.gz"):
                files.append(os.path.join(root, name))
    files.sort()
    with open(output_path, "w", newline="") as output:
        writer = csv.writer(output, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "source_file", "rsid", "source_chr37", "source_pos37",
            "target_id", "source_p", "target_p", "exact_p_match",
        ])
        for path in files:
            found = source_rows(path, set(target))
            for rsid in sorted(found):
                source_p = found[rsid]
                target_p = target[rsid]["target_p"]
                chr37, pos37 = r37.get(rsid, ("", ""))
                writer.writerow([
                    os.path.basename(path), rsid, chr37, pos37,
                    target[rsid]["target_id"], source_p, target_p,
                    "YES" if close_p(source_p, target_p) else "NO",
                ])
    if not files:
        raise RuntimeError("No .txt.gz trait files were found in the source directory")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("usage: compare_igg_source.py SOURCE_DIR TARGET_MAP MAP_R37 OUTPUT")
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
