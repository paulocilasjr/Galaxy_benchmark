import sys, json
import h5py
path,out=sys.argv[1],sys.argv[2]
def dec(v):
    if isinstance(v, bytes): return v.decode('utf-8','replace')
    if hasattr(v,'tolist'):
        try: return v.tolist()
        except Exception: pass
    return str(v)
def attrs(obj):
    d={}
    for k,v in obj.attrs.items():
        try: d[k]=dec(v)
        except Exception as e: d[k]='ERR:'+repr(e)
    return d
def visit(name,obj):
    typ='GROUP' if isinstance(obj,h5py.Group) else 'DATASET'
    shape=getattr(obj,'shape','')
    dtype=str(getattr(obj,'dtype',''))
    line=[name or '/',typ,str(shape),dtype,json.dumps(attrs(obj),ensure_ascii=True,sort_keys=True)]
    lines.append('\t'.join(line))
lines=[]
with h5py.File(path,'r') as f:
    f.visititems(visit)
with open(out,'w') as fh:
    for line in lines[:1000]: fh.write(line+'\n')
    fh.write('TOTAL_ITEMS\t%d\n' % len(lines))
