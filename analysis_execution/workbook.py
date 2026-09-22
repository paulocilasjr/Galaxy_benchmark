"""Read the run-link workbook with Python's standard library.

The supplied example has a seven-column header and eight-cell data rows.  We
therefore identify task/condition/replicate by value as well as by heading.
No workbook content is executed or treated as an instruction.
"""
from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs
from xml.etree import ElementTree as ET

S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
P = "{http://schemas.openxmlformats.org/package/2006/relationships}"
URL = re.compile(r"https?://[^\s<>\])]+")
REP = re.compile(r"(?:replicate[ _-]*)?(\d+)$", re.I)
TASK = re.compile(r"^(?:bix[-_]\d+[-_]q\d+|[a-z0-9][a-z0-9_-]*[-_]q\d+|wf[_-]\d+[_a-z0-9-]*)$", re.I)
KNOWN = {
    "bixbench": "bixbench",
    "bix": "bixbench",
    "bixbench-verified-50": "bixbench",
    "compbio": "compbio",
    "compbiobench": "compbio",
    "compbiobench v1": "compbio",
    "iwc": "iwc",
}


@dataclass(frozen=True)
class RunLink:
    benchmark: str
    task: str
    model: str
    condition: str
    condition_label: str
    replicate: int
    galaxy_url: str | None
    trace_url: str | None
    sheet: str
    row: int

    @property
    def run_id(self) -> str:
        model_slug = re.sub(r"[^a-z0-9]+", "_", self.model.lower()).strip("_")
        return f"{self.condition}_{model_slug}_r{self.replicate}"


def _col(ref: str) -> int:
    letters = re.match(r"[A-Z]+", ref).group()
    n = 0
    for c in letters:
        n = n * 26 + ord(c) - 64
    return n - 1


def _relationships(z: zipfile.ZipFile, path: str) -> dict[str, str]:
    if path not in z.namelist():
        return {}
    return {e.attrib["Id"]: e.attrib["Target"] for e in ET.fromstring(z.read(path)) if e.tag == P + "Relationship"}


def _sheets(z: zipfile.ZipFile):
    workbook = ET.fromstring(z.read("xl/workbook.xml"))
    rels = _relationships(z, "xl/_rels/workbook.xml.rels")
    for sheet in workbook.find(S + "sheets"):
        target = rels[sheet.attrib[R + "id"]]
        path = target.lstrip("/") if target.startswith("/") else "xl/" + target
        yield sheet.attrib["name"], path


def read_rows(path: Path):
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            shared = ["".join(t.text or "" for t in si.iter(S + "t")) for si in root]
        for sheet_name, sheet_path in _sheets(z):
            root = ET.fromstring(z.read(sheet_path))
            folder, filename = sheet_path.rsplit("/", 1)
            rels = _relationships(z, f"{folder}/_rels/{filename}.rels")
            links = {}
            for h in root.iter(S + "hyperlink"):
                target = rels.get(h.attrib.get(R + "id"), h.attrib.get("location"))
                if target:
                    links[h.attrib["ref"]] = target
            for row in root.iter(S + "row"):
                cells = {}
                for c in row.findall(S + "c"):
                    ref = c.attrib["r"]
                    typ = c.attrib.get("t")
                    if typ == "inlineStr":
                        value = "".join(t.text or "" for t in c.iter(S + "t"))
                    else:
                        v = c.find(S + "v")
                        value = v.text if v is not None and v.text is not None else ""
                        if typ == "s" and value:
                            value = shared[int(value)]
                        if not value:
                            formula = c.find(S + "f")
                            if formula is not None and formula.text and formula.text.upper().startswith("HYPERLINK("):
                                match = re.search(r'"(https?://[^\"]+)"', formula.text)
                                if match:
                                    value = match.group(1)
                    if ref in links:
                        value = f"{value} {links[ref]}".strip()
                    cells[_col(ref)] = value
                if cells:
                    yield sheet_name, int(row.attrib["r"]), [cells.get(i, "") for i in range(max(cells) + 1)]


def _condition(value: str) -> str | None:
    x = re.sub(r"[^a-z]", "", value.lower())
    if x in {"galaxyapi", "galaxy", "galaxystrictskills", "galaxyskills", "galaxyapicode", "galaxyapicodewithskills"}:
        return "galaxy"
    if x in {"opencoded", "openendedcode", "openendedcodewithskills", "anycode", "anycodenongalaxyskills", "unconstrainedcode"}:
        return "open_ended_code"
    return None


def _links(values: list[str]) -> tuple[str | None, str | None]:
    urls = []
    for v in values:
        for raw in URL.findall(v.replace("\\_", "_")):
            url = raw.rstrip(".,;")
            if url not in urls:
                urls.append(url)
    galaxy = [u for u in urls if urlparse(u).hostname and urlparse(u).hostname.endswith("usegalaxy.org")]
    trace = [u for u in urls if urlparse(u).hostname == "huggingface.co"]
    if len(galaxy) > 1 or len(trace) > 1:
        raise ValueError(f"More than one Galaxy or Hugging Face link in row: {urls}")
    return (galaxy[0] if galaxy else None, trace[0] if trace else None)


def galaxy_history_id(url: str) -> str:
    p = urlparse(url)
    if p.scheme != "https" or not (p.hostname == "usegalaxy.org" or p.hostname.endswith(".usegalaxy.org")):
        raise ValueError(f"Not an authorized usegalaxy.org HTTPS link: {url}")
    ids = parse_qs(p.query).get("id", [])
    if len(ids) != 1 or not re.fullmatch(r"[a-fA-F0-9]{32}", ids[0]):
        raise ValueError(f"Galaxy link lacks a 32-character history ID: {url}")
    return ids[0].lower()


def huggingface_source(url: str) -> tuple[str, str, str]:
    p = urlparse(url)
    if p.scheme != "https" or p.hostname != "huggingface.co":
        raise ValueError(f"Not a Hugging Face HTTPS link: {url}")
    parts = [unquote(x) for x in p.path.strip("/").split("/")]
    if len(parts) < 6 or parts[0] != "datasets" or parts[3] not in {"tree", "resolve"}:
        raise ValueError(f"Expected a Hugging Face dataset tree URL: {url}")
    repo = "/".join(parts[1:3])
    revision = parts[4]
    prefix = "/".join(parts[5:])
    if not all(re.fullmatch(r"[A-Za-z0-9._-]+", x) for x in [*parts[1:3], revision, *parts[5:]]):
        raise ValueError(f"Unsafe Hugging Face path component: {url}")
    return repo, revision, prefix


def load_inventory(path: Path) -> list[RunLink]:
    result = []
    seen = set()
    workbook_rows = list(read_rows(path))
    data_sheets = {sheet for sheet, _, raw in workbook_rows
                   if {"benchmark", "task", "model", "condition", "replicate"} <= {str(v).strip().lower() for v in raw}}
    if not data_sheets:
        raise ValueError("No worksheet has benchmark/task/model/condition/replicate headers")
    for sheet, number, raw in workbook_rows:
        if sheet not in data_sheets:
            continue
        values = [str(v).strip() for v in raw]
        bench_idx = next((i for i, v in enumerate(values) if v.lower() in KNOWN), None)
        if bench_idx is None:
            continue
        benchmark = KNOWN[values[bench_idx].lower()]
        task_idx = next((i for i, v in enumerate(values) if TASK.fullmatch(v)), None)
        if task_idx is None:
            raise ValueError(f"{sheet}!{number}: missing task ID")
        task = values[task_idx].replace("_", "-") if benchmark == "bixbench" else values[task_idx]
        condition_idx = next((i for i, v in enumerate(values) if _condition(v)), None)
        if condition_idx is None:
            raise ValueError(f"{sheet}!{number}: missing condition")
        condition_label = values[condition_idx]
        condition = _condition(condition_label)
        model_candidates = [v for v in values[task_idx + 1:condition_idx] if v and not URL.search(v)]
        if not model_candidates:
            raise ValueError(f"{sheet}!{number}: missing model between task and condition")
        model = model_candidates[-1]
        replicate_idx = next((i for i, v in enumerate(values[condition_idx + 1:], condition_idx + 1) if REP.fullmatch(v)), None)
        if replicate_idx is None:
            raise ValueError(f"{sheet}!{number}: missing replicate")
        replicate = int(REP.fullmatch(values[replicate_idx]).group(1))
        galaxy, trace = _links(values)
        if condition == "galaxy" and not galaxy and not trace:
            raise ValueError(f"{sheet}!{number}: Galaxy row needs a history or trace link")
        if condition == "open_ended_code" and not trace:
            raise ValueError(f"{sheet}!{number}: code row needs a trace link")
        if galaxy:
            galaxy_history_id(galaxy)
        if trace:
            repo, _, prefix = huggingface_source(trace)
            if task.lower().replace("-", "_") not in prefix.lower().replace("-", "_"):
                raise ValueError(f"{sheet}!{number}: trace path does not contain task {task}")
        key = (benchmark, task, model.casefold(), condition, replicate)
        if key in seen:
            raise ValueError(f"{sheet}!{number}: duplicate benchmark/task/model/condition/replicate")
        seen.add(key)
        result.append(RunLink(benchmark, task, model, condition, condition_label, replicate, galaxy, trace, sheet, number))
    if not result:
        raise ValueError("No run rows found in workbook")
    return result
