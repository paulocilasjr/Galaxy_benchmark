import sys,json,h5py,collections,re
path,out=sys.argv[1],sys.argv[2]
def dec(x): return x.decode('utf-8','replace') if isinstance(x,bytes) else str(x)
with h5py.File(path,'r') as f:
    idx=[dec(x) for x in f['obs/_index'][:200]]
    samp_cats=[dec(x) for x in f['obs/sampleID/categories'][()]]
    codes=f['obs/sampleID/codes'][()]
    examples={}
    for cat_i,cat in enumerate(samp_cats):
        pos=(codes==cat_i).nonzero()[0]
        if len(pos): examples[cat]=[dec(f['obs/_index'][int(i)]) for i in pos[:5]]
with open(out,'w') as fh:
    fh.write('first200\t%s\n' % json.dumps(idx))
    for k in sorted(examples):
        fh.write('EX\t%s\t%s\n' % (k,json.dumps(examples[k])))
