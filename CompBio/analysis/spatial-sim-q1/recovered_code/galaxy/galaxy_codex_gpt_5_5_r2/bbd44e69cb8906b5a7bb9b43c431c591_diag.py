
import sys, tarfile, gzip, csv, json, io, collections
archive=sys.argv[1]
out=[]
with tarfile.open(archive,'r:*') as tar:
    names=[m.name for m in tar.getmembers() if m.isfile()]
    out.append('FILES\t'+','.join(names))
    def pick(*cands):
        for c in cands:
            if c in names: return c
        # suffix fallback
        for c in cands:
            for n in names:
                if n.endswith('/'+c) or n.endswith(c): return n
        raise KeyError(cands)
    counts=pick('spatial_q_sc_counts.csv')
    meta=pick('spatial_q_sc_metadata.csv')
    featsn=pick('spatial_q_features.tsv.gz','features.tsv.gz')
    barsn=pick('spatial_q_barcodes.tsv.gz','barcodes.tsv.gz')
    mtxn=pick('spatial_q_matrix.mtx.gz','matrix.mtx.gz')
    posn=pick('spatial_q_tissue_positions.csv')
    out.append('RESOLVED\t'+json.dumps({'counts':counts,'metadata':meta,'features':featsn,'barcodes':barsn,'matrix':mtxn,'positions':posn}, sort_keys=True))
    def text(name,gz=False):
        f=tar.extractfile(name)
        return io.TextIOWrapper(gzip.GzipFile(fileobj=f),encoding='utf-8') if gz else io.TextIOWrapper(f,encoding='utf-8')
    with text(counts) as fh:
        reader=csv.reader(fh); header=next(reader); rows=[]
        for i,r in enumerate(reader):
            if i<3: rows.append(r[:8])
            last_i=i+1
        out.append('SC_COUNTS_SHAPE_HEADERCOLS_ROWS\t%d|%d'%(len(header), last_i))
        out.append('SC_COUNTS_HEADER_HEAD\t'+'|'.join(header[:8]))
        out.append('SC_COUNTS_FIRST_ROWS_HEAD\t'+json.dumps(rows))
    with text(meta) as fh:
        reader=csv.reader(fh); mh=next(reader); first=[]; ct=collections.Counter(); n=0
        idx=None
        for h in ['cell_type','celltype','type','CellType','cell types','cell_type_name','annotation']:
            if h in mh: idx=mh.index(h); break
        if idx is None and len(mh)>=2: idx=1
        for r in reader:
            if n<5: first.append(r)
            if len(r)>idx: ct[r[idx]]+=1
            n+=1
        out.append('SC_METADATA_HEADER\t'+'|'.join(mh))
        out.append('SC_METADATA_ROWS\t'+str(n))
        out.append('SC_METADATA_FIRST_ROWS\t'+json.dumps(first))
        out.append('SC_CELLTYPE_COUNTS\t'+json.dumps(dict(sorted(ct.items()))))
    with text(featsn,True) as fh:
        feats=[line.rstrip('\n').split('\t') for _,line in zip(range(5),fh)]
        out.append('FEATURES_FIRST\t'+json.dumps(feats))
    nbar=0; target_i=None; head=[]
    with text(barsn,True) as fh:
        for i,line in enumerate(fh,start=1):
            b=line.strip()
            if i<=5: head.append(b)
            if b=='Spot_710-1': target_i=i
            nbar=i
    out.append('BARCODES_N\t'+str(nbar))
    out.append('BARCODES_FIRST\t'+json.dumps(head))
    out.append('TARGET_BARCODE_1BASED_INDEX\t'+str(target_i))
    with text(mtxn,True) as fh:
        comments=[]
        for line in fh:
            if line.startswith('%'):
                comments.append(line.strip()); continue
            dims=line.strip().split(); break
        coords=[]
        for _,line in zip(range(5),fh): coords.append(line.strip().split())
        out.append('MTX_COMMENTS\t'+json.dumps(comments[:3]))
        out.append('MTX_DIMS\t'+'|'.join(dims))
        out.append('MTX_FIRST_COORDS\t'+json.dumps(coords))
    with text(posn) as fh:
        reader=csv.reader(fh); rows=[]; found=[]
        for i,r in enumerate(reader):
            if i<5: rows.append(r)
            if r and r[0]=='Spot_710-1': found.append(r)
        out.append('POSITIONS_FIRST_ROWS\t'+json.dumps(rows))
        out.append('TARGET_POSITION\t'+json.dumps(found))
print('\n'.join(out))

