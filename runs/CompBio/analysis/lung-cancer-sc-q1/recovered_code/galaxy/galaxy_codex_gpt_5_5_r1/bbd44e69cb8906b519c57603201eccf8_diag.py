import sys, json
from collections import Counter
import h5py
path=sys.argv[1]
out=sys.argv[2]
patients={'Patient_005','Patient_006','Patient_007','Patient_018','Patient_040'}

def decode(x):
    if isinstance(x, bytes):
        return x.decode('utf-8', 'replace')
    return str(x)

def read_col(obs, name):
    obj=obs[name]
    if isinstance(obj, h5py.Dataset):
        return [decode(x) for x in obj[()]]
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
    raise ValueError('unsupported column '+name+' type '+str(type(obj)))

with h5py.File(path,'r') as f:
    obs=f['obs']
    colnames=[]
    if '_index' in obs:
        n=len(obs['_index'])
    else:
        first=next(iter(obs.keys()))
        n=len(read_col(obs, first))
    for k in obs.keys():
        if k == '_index':
            continue
        try:
            vals=read_col(obs,k)
            if len(vals)==n:
                colnames.append(k)
        except Exception:
            pass
    summary=[]
    for k in colnames:
        vals=read_col(obs,k)
        uniq=Counter(v for v in vals if v is not None)
        low=[str(x).lower() for x in uniq.keys()]
        interesting = any(term in k.lower() for term in ['patient','sample','tumor','type','cell','immune','malig','subtype','hist']) or any(term in ' '.join(low[:200]) for term in ['patient_005','patient_006','patient_007','patient_018','patient_040','lusc','luad','dendritic','malignant','basal','immune'])
        if interesting:
            summary.append({'column':k,'n_unique':len(uniq),'top':uniq.most_common(30)})
    # candidate per-patient cross tabs for columns likely sample/patient and cell type
    vals_by_col={k:read_col(obs,k) for k in colnames}
    sample_cols=[k for k,v in vals_by_col.items() if patients & set(v)]
    cell_cols=[k for k,v in vals_by_col.items() if any('dendritic' in str(x).lower() or 'basal' in str(x).lower() or 'malignant' in str(x).lower() for x in set(v))]
    tumor_cols=[k for k,v in vals_by_col.items() if {'LUSC','LUAD'} & set(v)]
    with open(out,'w') as fh:
        fh.write('n_obs\t%d\n' % n)
        fh.write('sample_cols\t%s\n' % ','.join(sample_cols))
        fh.write('cell_cols\t%s\n' % ','.join(cell_cols))
        fh.write('tumor_cols\t%s\n' % ','.join(tumor_cols))
        fh.write('interesting_columns_json\t%s\n' % json.dumps(summary, sort_keys=True))
        for sc in sample_cols:
          for tc in tumor_cols:
            pairs=Counter(zip(vals_by_col[sc], vals_by_col[tc]))
            rows=[(a,b,c) for (a,b),c in pairs.items() if a in patients]
            fh.write('sample_tumor\t%s\t%s\t%s\n' % (sc,tc,json.dumps(rows, sort_keys=True)))
        for sc in sample_cols:
          for cc in cell_cols:
            ct=Counter((s,c) for s,c in zip(vals_by_col[sc], vals_by_col[cc]) if s in patients)
            rows=[(s,c,nc) for (s,c),nc in ct.items() if 'dendritic' in str(c).lower() or 'basal' in str(c).lower() or 'malignant' in str(c).lower()]
            fh.write('sample_cell\t%s\t%s\t%s\n' % (sc,cc,json.dumps(rows, sort_keys=True)))
