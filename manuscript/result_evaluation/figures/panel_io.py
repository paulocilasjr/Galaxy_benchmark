"""Record the data each figure panel is drawn from, so the figures can be redrawn outside this archive.

With the environment variable PANEL_DATA set, `record(namespace, script)` wraps a figure script's drawing functions.
Every call then appends its arguments (all but the matplotlib figure) to figures/panel_data/<script>.json, in call
order, with each new figure's size, the state of the script's jitter generator before the call, and each save.
The manuscript repository (agent-galaxy-benchmark-manuscript, figures/*/make_figure.py) replays these calls with the
same drawing code, so its figures are the archive's figures; no estimate is recomputed there.

Tables keep their index and column labels and value types. Columns that hold answers, references, prompts or trace
text are never written (DROP_COLUMNS); a replay that needed one would fail, so their absence is checked by redrawing.
"""
import atexit
import functools
import inspect
import json
import math
import os

import numpy as np
import pandas as pd

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'panel_data')
DROP_COLUMNS = {'answer', 'answers', 'expected', 'expected_answer', 'reference', 'ideal', 'prompt', 'text',
                'submitted_answer', 'final_answer', 'rationale', 'command', 'evidence'}


def encode(o):
    if isinstance(o, pd.DataFrame):
        o = o[[c for c in o.columns if not (isinstance(c, str) and c in DROP_COLUMNS)]]
        return {'__frame__': {'index': encode_index(o.index), 'columns': encode_index(o.columns),
                              'dtypes': [str(t) for t in o.dtypes],
                              'data': [[encode(v) for v in row] for row in o.itertuples(index=False, name=None)]}}
    if isinstance(o, pd.Series):
        return {'__series__': {'index': encode_index(o.index), 'name': encode(o.name), 'dtype': str(o.dtype),
                               'data': [encode(v) for v in o.tolist()]}}
    if isinstance(o, pd.Index):
        return {'__index__': encode_index(o)}
    if isinstance(o, np.ndarray):
        return {'__array__': [encode(v) for v in o.tolist()], 'dtype': str(o.dtype), 'shape': list(o.shape)}
    if isinstance(o, dict):
        return {'__dict__': [[encode(k), encode(v)] for k, v in o.items()]}
    if isinstance(o, tuple):
        return {'__tuple__': [encode(v) for v in o]}
    if isinstance(o, (set, frozenset)):
        return {'__set__': [encode(v) for v in sorted(o, key=str)]}
    if isinstance(o, list):
        return [encode(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating, float)):
        f = float(o)
        return {'__float__': repr(f)} if (math.isnan(f) or math.isinf(f)) else f
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if o is pd.NA or o is pd.NaT:
        return None
    if isinstance(o, pd.Timestamp):
        return {'__timestamp__': o.isoformat()}
    if o is None or isinstance(o, (bool, int, str)):
        return o
    raise TypeError(f'panel_io cannot record {type(o).__name__}')


def encode_index(ix):
    return {'names': [encode(n) for n in ix.names], 'multi': isinstance(ix, pd.MultiIndex),
            'values': [encode(v) for v in ix.tolist()], 'dtype': str(ix.dtype)}


def decode(o):
    if isinstance(o, list):
        return [decode(v) for v in o]
    if not isinstance(o, dict):
        return o
    if '__frame__' in o:
        f = o['__frame__']
        cols = decode_index(f['columns'])
        df = pd.DataFrame([[decode(v) for v in row] for row in f['data']], columns=range(len(cols)))
        for i, t in enumerate(f['dtypes']):
            try:
                df[i] = df[i].astype(t)
            except (TypeError, ValueError):
                pass
        df.columns = cols
        df.index = decode_index(f['index'])
        return df
    if '__series__' in o:
        s = o['__series__']
        out = pd.Series([decode(v) for v in s['data']], index=decode_index(s['index']), name=decode(s['name']))
        try:
            return out.astype(s['dtype'])
        except (TypeError, ValueError):
            return out
    if '__index__' in o:
        return decode_index(o['__index__'])
    if '__array__' in o:
        return np.array([decode(v) for v in o['__array__']], dtype=o['dtype']).reshape(o['shape'])
    if '__dict__' in o:
        return {decode(k): decode(v) for k, v in o['__dict__']}
    if '__tuple__' in o:
        return tuple(decode(v) for v in o['__tuple__'])
    if '__set__' in o:
        return set(decode(v) for v in o['__set__'])
    if '__float__' in o:
        return float(o['__float__'])
    if '__timestamp__' in o:
        return pd.Timestamp(o['__timestamp__'])
    return {k: decode(v) for k, v in o.items()}


def decode_index(d):
    vals = [decode(v) for v in d['values']]
    names = [decode(n) for n in d['names']]
    if d['multi']:
        return pd.MultiIndex.from_tuples([tuple(v) for v in vals], names=names)
    ix = pd.Index(vals, name=names[0] if names else None)
    try:
        return ix.astype(d['dtype'])
    except (TypeError, ValueError):
        return ix


def record(namespace, script, names=None):
    """Wrap the drawing functions (draw_*, ed_* that take a figure, and save) of a figure script."""
    if not os.environ.get('PANEL_DATA'):
        return
    import matplotlib.figure
    import matplotlib.pyplot as plt
    calls = []
    figures = {}
    depth = [0]                                   # record top-level calls only (a drawing function may call another)
    original_figure = plt.figure

    def figure(*args, **kwargs):
        f = original_figure(*args, **kwargs)
        figures[id(f)] = len(figures)
        calls.append({'call': 'figure', 'figure': figures[id(f)], 'size_inches': [float(x) for x in f.get_size_inches()],
                      'nested': depth[0] > 0})
        return f
    plt.figure = figure
    names = names or [n for n, v in namespace.items() if callable(v) and getattr(v, '__module__', None) == namespace['__name__']
                      and (n.startswith(('draw_', 'ed_')) or n == 'save')
                      and 'fig' in inspect.signature(v).parameters]
    for name in names:
        fn = namespace[name]
        sig = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapper(*args, __fn=fn, __name=name, __sig=sig, **kwargs):
            bound = __sig.bind(*args, **kwargs)
            if depth[0]:                          # inside a recorded call: note saves (for names), do not replay
                if __name == 'save':
                    fig = next(v for v in bound.arguments.values() if isinstance(v, matplotlib.figure.Figure))
                    calls.append({'call': 'save', 'figure': figures.get(id(fig)), 'nested': True,
                                  'args': {k: encode(v) for k, v in bound.arguments.items()
                                           if not isinstance(v, matplotlib.figure.Figure)}})
                return __fn(*args, **kwargs)
            entry = {'call': __name, 'args': {}}
            for k, v in bound.arguments.items():
                if isinstance(v, matplotlib.figure.Figure):
                    entry['figure'] = figures.get(id(v))
                    entry['args'][k] = {'__figure__': True}
                else:
                    entry['args'][k] = encode(v)
            rng = namespace.get('rng')
            if isinstance(rng, np.random.Generator):
                entry['rng_state'] = encode(rng.bit_generator.state)
            calls.append(entry)
            before = len(figures)
            depth[0] += 1
            try:
                return __fn(*args, **kwargs)
            finally:
                depth[0] -= 1
                if 'figure' not in entry and len(figures) > before:
                    entry['figure'] = before      # the call drew its own figure
        namespace[name] = wrapper

    def write():
        os.makedirs(OUT, exist_ok=True)
        with open(os.path.join(OUT, f'{script}.json'), 'w') as fh:
            json.dump({'script': script, 'note': __doc__.split('\n\n')[1].replace('\n', ' '), 'calls': calls}, fh,
                      separators=(',', ':'))
    atexit.register(write)


def replay(path, namespace, names=None):
    """Redraw the figures recorded in path (only those saved under `names`, if given) with the drawing functions in
    namespace; used by the manuscript scripts."""
    import matplotlib.pyplot as plt
    calls = json.load(open(path))['calls']
    saved = {c['figure']: c['args']['name'] for c in calls if c['call'] == 'save'}
    keep = {k for k, v in saved.items() if names is None or v in names}
    figs = {}
    for c in calls:
        if c.get('nested') or c.get('figure') not in keep:
            continue
        if c['call'] == 'figure':
            figs[c['figure']] = plt.figure(figsize=tuple(c['size_inches']))
            continue
        args = {k: (figs[c['figure']] if isinstance(v, dict) and v.get('__figure__') else decode(v)) for k, v in c['args'].items()}
        if 'rng_state' in c and isinstance(namespace.get('rng'), np.random.Generator):
            namespace['rng'].bit_generator.state = decode(c['rng_state'])
        namespace[c['call']](**args)
