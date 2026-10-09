#!/usr/bin/env python3
"""Build the result-evaluation document: panel images, DOCX and PDF.

Steps:
1. split_panels.py: one image per figure panel (skipped with --skip-panels when panels/ is current);
2. build_document.js: the DOCX, from text/*.md and panels/;
3. LibreOffice: DOCX to PDF;
4. the page of every figure and panel heading is read from the PDF outline into build/pages.json, and steps 2-3 are
   repeated so the contents list carries page numbers (repeated until the pages no longer move).

Writes Galaxy_benchmark_figure_evaluation.docx and .pdf next to this script.
Run from the repository root with the figure environment (manuscript_material/scripts/requirements.txt plus pypdf):
    python result_evaluation/build.py [--skip-panels]
Environment: NODE_PATH must reach the npm package docx (default: the local Codex runtime's node_modules); SOFFICE may
point to the LibreOffice binary (default: soffice on PATH, then the Codex runtime's LibreOffice).
"""
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile

from pypdf import PdfReader

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
NAME = 'Galaxy_benchmark_figure_evaluation'
BUILD = os.path.join(HERE, 'build')
RUNTIME = os.path.expanduser('~/.cache/codex-runtimes/codex-primary-runtime/dependencies')


def soffice():
    found = os.environ.get('SOFFICE') or shutil.which('soffice')
    return found or os.path.join(RUNTIME, 'native/libreoffice-headless/libreoffice/LibreOfficeDev.app/Contents/MacOS/soffice')


def run(cmd, **kw):
    print('$', ' '.join(cmd))
    subprocess.run(cmd, check=True, **kw)


def git(*args):
    return subprocess.run(['git', '-C', ROOT, *args], capture_output=True, text=True).stdout.strip()


def docx_and_pdf(env, profile):
    run(['node', os.path.join(HERE, 'build_document.js')], env=env)
    run([soffice(), f'-env:UserInstallation=file://{profile}', '--headless', '--convert-to', 'pdf', '--outdir', HERE,
         os.path.join(HERE, f'{NAME}.docx')], stdout=subprocess.DEVNULL)


def heading_pages():
    """Page (1-based) of every outline entry, keyed by the bookmark of the heading it starts with."""
    anchors = json.load(open(os.path.join(BUILD, 'anchors.json')))
    reader = PdfReader(os.path.join(HERE, f'{NAME}.pdf'))
    pages = {}

    def walk(items):
        for it in items:
            if isinstance(it, list):
                walk(it)
                continue
            title = it.title.strip()
            for prefix, anchor in anchors.items():
                if title.startswith(prefix):
                    pages[anchor] = reader.get_destination_page_number(it) + 1
    walk(reader.outline)
    missing = set(anchors.values()) - set(pages)
    if missing:
        raise SystemExit(f'headings not found in the PDF outline: {sorted(missing)}')
    return pages


def main():
    os.makedirs(BUILD, exist_ok=True)
    if '--skip-panels' not in sys.argv:
        run([sys.executable, os.path.join(HERE, 'split_panels.py')])
    dirty = git('status', '--porcelain', '--', 'figures', 'manuscript_narrative')
    meta = {'date': datetime.date.today().strftime('%-d %B %Y'), 'commit': git('rev-parse', '--short', 'HEAD') +
            (' + uncommitted changes' if dirty else ''), 'branch': git('rev-parse', '--abbrev-ref', 'HEAD')}
    snap = os.path.join(HERE, 'figures', 'site_snapshot', 'bixbench_runs.json')
    if os.path.exists(snap):
        meta['site'] = datetime.datetime.strptime(json.load(open(snap))['retrieved_at_utc'][:10], '%Y-%m-%d').strftime('%-d %B %Y')
    json.dump(meta, open(os.path.join(BUILD, 'meta.json'), 'w'), indent=1)
    env = dict(os.environ)
    env.setdefault('NODE_PATH', os.path.join(RUNTIME, 'node/node_modules'))
    pages_file = os.path.join(BUILD, 'pages.json')
    if os.path.exists(pages_file):
        os.remove(pages_file)
    with tempfile.TemporaryDirectory() as profile:
        pages = None
        for attempt in range(4):
            docx_and_pdf(env, profile)
            found = heading_pages()
            if found == pages:
                break
            pages = found
            json.dump(pages, open(pages_file, 'w'), indent=1)
        else:
            raise SystemExit('page numbers did not settle')
    n = len(PdfReader(os.path.join(HERE, f'{NAME}.pdf')).pages)
    print(f'{NAME}.docx and .pdf: {n} pages, {len(pages)} headings')


if __name__ == '__main__':
    main()
