#!/usr/bin/env python3
"""Check that every Galaxy history link in the run index opens for a reader without an account.

For each link in supplementary/Supplementary_Data_2.xlsx (and the rerun manifest's own history links), the history id is
read from the URL or, for /u/<user>/h/<slug> links, from the redirect usegalaxy.org returns; then the history is fetched
from the public API (/api/histories/<id>) without credentials. Status: accessible (published or importable), not
accessible, deleted, purged or not found. Writes data/galaxy_history_check.csv (url, history_id, status, published,
importable, checked_at_utc); rerun scripts/make_run_index.py afterwards to add the result to the run index.
Usage: python scripts/check_galaxy_histories.py
"""
import concurrent.futures
import datetime
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BC = os.path.dirname(HERE)
ARCHIVE = os.path.abspath(os.path.join(BC, '..', '..', '..', '..'))
GALAXY = 'https://usegalaxy.org'


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


OPENER = urllib.request.build_opener(NoRedirect)


def history_id(url):
    m = re.search(r'[?&]id=([0-9a-f]{16,32})', url)
    if m:
        return m.group(1), ''
    try:
        OPENER.open(urllib.parse.quote(url, safe=':/?&=%'), timeout=60)   # some history slugs are not ASCII
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            m = re.search(r'[?&]id=([0-9a-f]{16,32})', e.headers.get('Location', ''))
            return (m.group(1), '') if m else ('', 'not found')
        return '', 'not found' if e.code == 404 else f'HTTP {e.code}'
    return '', 'no redirect'


def check(url, tries=4):
    for k in range(tries):                       # back off on rate limits and gateway errors
        row = check_once(url)
        if not re.match(r'HTTP (429|5\d\d)', row['status']):
            break
        time.sleep(30 * (k + 1))
    return row


def check_once(url):
    hid, problem = history_id(url)
    row = dict(url=url, history_id=hid, status=problem, published='', importable='')
    if not hid:
        return row
    try:
        with urllib.request.urlopen(f'{GALAXY}/api/histories/{hid}', timeout=60) as r:
            h = json.load(r)
    except urllib.error.HTTPError as e:
        row['status'] = 'not accessible' if e.code in (400, 403, 404) else f'HTTP {e.code}'
        return row
    row.update(published=h.get('published'), importable=h.get('importable'))
    row['status'] = ('purged' if h.get('purged') else 'deleted' if h.get('deleted')
                     else 'accessible' if h.get('published') or h.get('importable') else 'not accessible')
    return row


def main():
    xl = pd.ExcelFile(os.path.join(BC, 'supplementary', 'Supplementary_Data_2.xlsx'))
    urls = set()
    for sheet in ('Primary runs', 'Replaced runs', 'Interface rounds'):
        urls |= set(xl.parse(sheet).galaxy_history.dropna())
    m = pd.read_csv(os.path.join(ARCHIVE, 'runs', 'CompBio', 'reruns_20261005', 'rerun_manifest.csv'))
    urls |= set(m.history_url_rerun.dropna())
    urls = sorted(u for u in urls if isinstance(u, str) and u.startswith(GALAXY))
    path = os.path.join(BC, 'data', 'galaxy_history_check.csv')
    done = pd.DataFrame()
    if os.path.exists(path):                     # keep definite results; recheck errors and new links
        done = pd.read_csv(path, dtype=str).fillna('')
        done = done[done.status.isin(['accessible', 'not accessible', 'deleted', 'purged', 'not found'])
                    & done.url.isin(urls)]
    todo = [u for u in urls if u not in set(done.get('url', []))]
    with concurrent.futures.ThreadPoolExecutor(4 if len(todo) > 50 else 1) as ex:
        rows = list(ex.map(check, todo))
    new = pd.DataFrame(rows, columns=['url', 'history_id', 'status', 'published', 'importable']).assign(
        checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'))
    out = pd.concat([done, new], ignore_index=True).sort_values('url')
    out.to_csv(path, index=False)
    print(f'{len(todo)} links checked now')
    print(len(out), 'links;', out.status.value_counts().to_dict())


if __name__ == '__main__':
    main()
