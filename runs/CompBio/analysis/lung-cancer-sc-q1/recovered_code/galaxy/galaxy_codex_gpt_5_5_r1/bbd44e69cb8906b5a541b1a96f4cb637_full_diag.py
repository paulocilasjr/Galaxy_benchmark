import sys, json
from collections import Counter
import h5py
path=sys.argv[1]
out=sys.argv[2]

def decode(x):
    if isinstance(x, bytes):
        return x.decode('utf-8', 'replace')
    try:
        if hasattr(x, 'item'):
            x=x.item()
    except Exception:
        pass
    if isinstance(x, bytes):
        return x.decode('utf-8', 'replace')
    return str(x)

def read_col(obs, name):
    obj=obs[name]
    if isinstance(obj, h5py.Dataset):
        arr=obj[()]
        return [decode(x) for x in arr]
    if isinstance(obj, h5py.Group):
        keys=set(obj.keys())
        if {'codes','categories'} <= keys:
            codes=obj['codes'][()]
            cats=[decode(x) for x in obj['categories'][()]]
            vals=[]
            for c in codes:
                ci=int(c)
                vals.append(None if ci < 0 else cats[ci])
            return vals
        if {'values'} <= keys:
            return [decode(x) for x in obj['values'][()]]
    raise ValueError('unsupported '+name+' '+str(type(obj)))

with h5py.File(path,'r') as f, open(out,'w') as fh:
    fh.write('root_keys\t%s\n' % json.dumps(list(f.keys())))
    obs=f['obs']
    fh.write('obs_keys\t%s\n' % json.dumps(list(obs.keys())))
    for k in obs.keys():
        if k == '_index':
            fh.write('COL\t_index\tindex\t0\t[]\n')
            continue
        try:
            vals=read_col(obs,k)
            cnt=Counter(vals)
            fh.write('COL\t%s\t%s\t%d\t%s\n' % (k, type(obs[k]).__name__, len(cnt), json.dumps(cnt.most_common(50), ensure_ascii=True)))
        except Exception as e:
            fh.write('COLERR\t%s\t%s\n' % (k, repr(e)))
    if 'uns' in f:
        fh.write('uns_keys\t%s\n' % json.dumps(list(f['uns'].keys())))
