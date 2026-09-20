import math
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

import numpy as np
import statsmodels.api as sm

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
CELL_RE = re.compile(r"^([A-Z]+)([0-9]+)$")

def cell_value(cell, shared):
    kind = cell.attrib.get("t")
    if kind == "inlineStr":
        return "".join((node.text or "") for node in cell.iter(f"{{{NS}}}t"))
    value_node = cell.find(f"{{{NS}}}v")
    if value_node is None:
        return None
    raw = value_node.text
    if kind == "s":
        return shared[int(raw)]
    if kind == "b":
        return raw == "1"
    return raw

def read_rows(path):
    with zipfile.ZipFile(path) as workbook:
        shared = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            for item in root.findall(f"{{{NS}}}si"):
                shared.append("".join((node.text or "") for node in item.iter(f"{{{NS}}}t")))
        sheet = ET.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
        rows = {}
        for row in sheet.findall(f".//{{{NS}}}row"):
            row_number = int(row.attrib["r"])
            values = {}
            for cell in row.findall(f"{{{NS}}}c"):
                ref = cell.attrib["r"]
                col = re.match(r"^([A-Z]+)", ref).group(1)
                values[col] = cell_value(cell, shared)
            if values:
                rows[row_number] = values
        return rows

def main():
    rows = read_rows(sys.argv[1])
    header = rows.get(1, {})
    by_name = {str(value).strip(): col for col, value in header.items() if value is not None}
    if "Efficacy" not in by_name or "BMI" not in by_name:
        raise RuntimeError("required Efficacy and BMI columns are missing")
    efficacy_col = by_name["Efficacy"]
    bmi_col = by_name["BMI"]
    x_values = []
    y_values = []
    for row_number in sorted(rows):
        if row_number == 1:
            continue
        row = rows[row_number]
        if row.get("A") in (None, ""):
            continue
        efficacy = row.get(efficacy_col)
        bmi = row.get(bmi_col)
        if efficacy in (None, "") or bmi in (None, ""):
            continue
        try:
            bmi_value = float(bmi)
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"non-numeric BMI at worksheet row {row_number}") from exc
        x_values.append(bmi_value)
        y_values.append(1.0 if str(efficacy).strip().upper() == "PR" else 0.0)
    if not x_values or len(set(y_values)) != 2:
        raise RuntimeError("invalid complete-case PR indicator")
    design = sm.add_constant(np.asarray(x_values, dtype=float), has_constant="add")
    fitted = sm.GLM(
        np.asarray(y_values, dtype=float),
        design,
        family=sm.families.Binomial(),
    ).fit()
    aic = float(fitted.aic)
    if not math.isfinite(aic):
        raise RuntimeError("fitted AIC is not finite")
    pr_count = int(sum(y_values))
    with open("result.tsv", "w", encoding="utf-8") as output:
        output.write("metric\tvalue\n")
        output.write(f"aic\t{aic:.17g}\n")
        output.write(f"effective_n\t{len(y_values)}\n")
        output.write(f"pr_count\t{pr_count}\n")
        output.write(f"non_pr_count\t{len(y_values) - pr_count}\n")
        output.write("model\tBinomial logistic regression: PR indicator ~ BMI\n")
        output.write(f"statsmodels_version\t{sm.__version__}\n")

if __name__ == "__main__":
    main()
