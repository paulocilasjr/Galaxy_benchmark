import io
import json
import posixpath
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


NS_REL = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
NS_MAIN = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def col_index(cell_ref):
    letters = "".join(ch for ch in cell_ref if ch.isalpha())
    value = 0
    for ch in letters:
        value = value * 26 + ord(ch.upper()) - 64
    return value - 1


def shared_strings(zf):
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    out = []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    for si in root:
        if local_name(si.tag) == "si":
            out.append("".join(t.text or "" for t in si.iter() if local_name(t.tag) == "t"))
    return out


def first_sheet_path(zf):
    rels = {}
    rel_root = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    for rel in rel_root:
        if rel.tag == NS_REL:
            target = rel.attrib["Target"]
            if not target.startswith("/"):
                target = posixpath.normpath(posixpath.join("xl", target))
            else:
                target = target.lstrip("/")
            rels[rel.attrib["Id"]] = target

    wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
    for node in wb_root.iter():
        if local_name(node.tag) == "sheet":
            rid = node.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
            if rid in rels:
                return rels[rid]
    return "xl/worksheets/sheet1.xml"


def cell_value(cell, strings):
    typ = cell.attrib.get("t")
    if typ == "inlineStr":
        return "".join(t.text or "" for t in cell.iter() if local_name(t.tag) == "t")
    value_node = None
    for child in cell:
        if local_name(child.tag) == "v":
            value_node = child
            break
    if value_node is None or value_node.text is None:
        return ""
    raw = value_node.text
    if typ == "s":
        try:
            return strings[int(raw)]
        except Exception:
            return raw
    return raw


def read_xlsx_rows(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        strings = shared_strings(zf)
        sheet = first_sheet_path(zf)
        rows = []
        for _, row in ET.iterparse(io.BytesIO(zf.read(sheet)), events=("end",)):
            if local_name(row.tag) != "row":
                continue
            vals = []
            for cell in row:
                if local_name(cell.tag) != "c":
                    continue
                idx = col_index(cell.attrib.get("r", "A1"))
                while len(vals) <= idx:
                    vals.append("")
                vals[idx] = cell_value(cell, strings)
            rows.append(vals)
            row.clear()
        return rows


def norm_id(value):
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    return text


def truthy(value):
    return str(value).strip().lower() in {"true", "t", "1", "yes", "y"}


def as_float(value):
    text = str(value).strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def split_genes(value):
    return {x.strip() for x in re.split(r"[,;|\s]+", str(value)) if x.strip()}


def so_terms(value):
    return {x.strip() for x in re.split(r"[,;&|\s]+", str(value)) if x.strip()}


CODING_TERMS = {
    "coding_sequence_variant",
    "frameshift_variant",
    "incomplete_terminal_codon_variant",
    "inframe_deletion",
    "inframe_insertion",
    "initiator_codon_variant",
    "missense_variant",
    "protein_altering_variant",
    "start_lost",
    "stop_gained",
    "stop_lost",
    "stop_retained_variant",
    "synonymous_variant",
}


def table_records(rows, required):
    for i, row in enumerate(rows):
        header = [str(x).strip() for x in row]
        if all(col in header for col in required):
            index = {name: header.index(name) for name in header if name}
            for data in rows[i + 1 :]:
                yield {name: data[idx] if idx < len(data) else "" for name, idx in index.items()}
            return
    raise RuntimeError("Could not find header with required columns: " + ", ".join(required))


def main():
    archive_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    with zipfile.ZipFile(archive_path) as outer:
        members = [n for n in outer.namelist() if n.lower().endswith(".xlsx")]

        status_name = next(n for n in members if n.endswith("230215_Trio_Status.xlsx"))
        gene_name = next(n for n in members if n.endswith("230214_Schenz_et_al_2022_CHIP_Genes.xlsx"))

        status_rows = read_xlsx_rows(outer.read(status_name))
        carriers = set()
        for rec in table_records(status_rows, ["Sample ID", "BLM Mutation Status"]):
            if str(rec.get("BLM Mutation Status", "")).strip() == "Carrier":
                carriers.add(norm_id(rec.get("Sample ID", "")))

        gene_rows = read_xlsx_rows(outer.read(gene_name))
        chip_genes = {str(row[0]).strip() for row in gene_rows if row and str(row[0]).strip()}

        variant_members = [
            n
            for n in members
            if "/CHIP_DP10_GQ20_PASS/" in n and Path(n).name.startswith("230209_Exome_GRCh38_CHIP_")
        ]

        total_coding = 0
        synonymous = 0
        used_samples = set()
        missing_carriers = set(carriers)
        skipped_noncarrier_files = 0

        required = ["Gene Names", "Sequence Ontology (Combined)", "Variant Allele Freq", "In_CHIP"]
        for name in sorted(variant_members):
            sample = Path(name).name.rsplit(".xlsx", 1)[0].replace("230209_Exome_GRCh38_CHIP_", "", 1)
            sample = sample.split("-", 1)[0].strip()
            if sample not in carriers:
                skipped_noncarrier_files += 1
                continue
            used_samples.add(sample)
            missing_carriers.discard(sample)

            rows = read_xlsx_rows(outer.read(name))
            for rec in table_records(rows, required):
                vaf = as_float(rec.get("Variant Allele Freq", ""))
                if vaf is None or not vaf < 0.3:
                    continue

                gene_match = bool(split_genes(rec.get("Gene Names", "")) & chip_genes)
                if not (truthy(rec.get("In_CHIP", "")) or gene_match):
                    continue

                terms = so_terms(rec.get("Sequence Ontology (Combined)", ""))
                if not (terms & CODING_TERMS):
                    continue

                total_coding += 1
                if "synonymous_variant" in terms:
                    synonymous += 1

        if total_coding == 0:
            raise RuntimeError("No coding carrier variants with VAF below 0.3 were found")

    fraction = synonymous / total_coding
    output = {
        "fraction": format(fraction, ".12g"),
        "synonymous_count": synonymous,
        "coding_vaf_lt_0_3_count": total_coding,
        "carrier_samples_in_status": len(carriers),
        "carrier_samples_with_variant_workbooks": len(used_samples),
        "missing_carrier_variant_workbooks": sorted(missing_carriers),
        "skipped_noncarrier_variant_workbooks": skipped_noncarrier_files,
        "coding_terms": sorted(CODING_TERMS),
    }
    output_path.write_text(json.dumps(output, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
