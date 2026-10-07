#!/usr/bin/env python3
"""List every Source Data value that changed between two figure sets.

Default: the figures before site-matched scores (figures/archive/2026-10-07_before_site_scores/) against the figures next
to this script. Writes source_data_changes/<figure>.csv next to this script (one row per changed, added or removed value)
and prints a count per figure.
Usage: python compare_source_data.py [OLD_DIR]
"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
OLD = os.path.join(ROOT, 'figures', 'archive', '2026-10-07_before_site_scores')
OUT = os.path.join(HERE, 'source_data_changes')
FIGS = ['fig2', 'fig3', 'fig4', 'fig5', 'ed_fig2', 'ed_fig3', 'ed_fig4', 'ed_fig5', 'ed_fig6', 'ed_fig7']
VALUES = {'value', 'ci95_low', 'ci95_high', 'n', 'p', 'p_holm', 'runs', 'tasks', 'clusters', 'share', 'count'}


def keyed(df):
    keys = [c for c in df.columns if c not in VALUES]
    df = df.copy()
    df[keys] = df[keys].astype(str)
    df['_k'] = df.groupby(keys, dropna=False).cumcount()
    return df.set_index(keys + ['_k'])


def main():
    global OLD
    if len(sys.argv) > 1:
        OLD = sys.argv[1]
    os.makedirs(OUT, exist_ok=True)
    for f in FIGS:
        old_p, new_p = os.path.join(OLD, f'{f}_source_data.csv'), os.path.join(HERE, f'{f}_source_data.csv')
        if not os.path.exists(new_p):
            print(f'{f}: no new source data yet')
            continue
        old, new = keyed(pd.read_csv(old_p, low_memory=False)), keyed(pd.read_csv(new_p, low_memory=False))
        cols = [c for c in new.columns if c in VALUES and c in old.columns]
        j = old[cols].join(new[cols], how='outer', lsuffix='_old', rsuffix='_new')
        rows = []
        for idx, r in j.iterrows():
            for c in cols:
                a, b = r[f'{c}_old'], r[f'{c}_new']
                same = (pd.isna(a) and pd.isna(b)) or (not pd.isna(a) and not pd.isna(b) and
                                                       (a == b or (isinstance(a, float) and abs(a - b) < 5e-5)))
                if not same:
                    rows.append(dict(zip(j.index.names, idx), field=c, old=a, new=b))
        out = pd.DataFrame(rows).drop(columns='_k', errors='ignore')
        out.to_csv(os.path.join(OUT, f'{f}.csv'), index=False)
        print(f'{f}: {len(out)} changed values')


if __name__ == '__main__':
    main()
