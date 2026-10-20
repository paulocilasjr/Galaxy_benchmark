
import sys, tarfile, gzip, csv, json, os, io, collections
archive = sys.argv[1]
out = []
with tarfile.open(archive, 'r:*') as tar:
    members = [m for m in tar.getmembers() if m.isfile()]
    out.append('FILES\t' + ','.join(m.name for m in members))
    sizes = {m.name: m.size for m in members}
    out.append('SIZES\t' + json.dumps(sizes, sort_keys=True))
    def read_text(name, gz=False):
        f = tar.extractfile(name)
        if gz:
            return io.TextIOWrapper(gzip.GzipFile(fileobj=f), encoding='utf-8')
        return io.TextIOWrapper(f, encoding='utf-8')
    # single cell counts header and first data rows
    with read_text('spatial_q_sc_counts.csv') as fh:
        reader = csv.reader(fh)
        header = next(reader)
        rows = [next(reader) for _ in range(3)]
        out.append('SC_COUNTS_HEADER_LEN\t' + str(len(header)))
        out.append('SC_COUNTS_HEADER_HEAD\t' + '|'.join(header[:8]))
        out.append('SC_COUNTS_FIRST_ROWS_HEAD\t' + json.dumps([r[:8] for r in rows]))
    with read_text('spatial_q_sc_metadata.csv') as fh:
        reader = csv.reader(fh)
        meta_header = next(reader)
        meta_rows = [next(reader) for _ in range(5)]
        out.append('SC_METADATA_HEADER\t' + '|'.join(meta_header))
        out.append('SC_METADATA_FIRST_ROWS\t' + json.dumps(meta_rows))
        # count all cell types and rows
        ct = collections.Counter()
        n=0
        idx = None
        for h in ['cell_type','celltype','type','CellType','cell types','cell_type_name']:
            if h in meta_header: idx=meta_header.index(h); break
        if idx is None and len(meta_header)>=2: idx=1
        for r in meta_rows:
            if len(r)>idx: ct[r[idx]] += 1; n += 1
        for r in reader:
            if len(r)>idx: ct[r[idx]] += 1; n += 1
        out.append('SC_METADATA_ROWS\t' + str(n))
        out.append('SC_CELLTYPE_COUNTS\t' + json.dumps(dict(sorted(ct.items()))))
    with read_text('spatial_q_features.tsv.gz', gz=True) as fh:
        feats=[line.rstrip('\n').split('\t') for _,line in zip(range(5), fh)]
        out.append('FEATURES_FIRST\t' + json.dumps(feats))
    nbar=0; target_i=None; bar_head=[]
    with read_text('spatial_q_barcodes.tsv.gz', gz=True) as fh:
        for i,line in enumerate(fh, start=1):
            b=line.strip()
            if i<=5: bar_head.append(b)
            if b=='Spot_710-1': target_i=i
            nbar=i
    out.append('BARCODES_N\t' + str(nbar))
    out.append('BARCODES_FIRST\t' + json.dumps(bar_head))
    out.append('TARGET_BARCODE_1BASED_INDEX\t' + str(target_i))
    with read_text('spatial_q_matrix.mtx.gz', gz=True) as fh:
        comments=[]
        for line in fh:
            if line.startswith('%'):
                comments.append(line.strip())
                continue
            dims=line.strip().split()
            break
        coords=[]
        for _,line in zip(range(5), fh): coords.append(line.strip().split())
        out.append('MTX_COMMENTS\t' + json.dumps(comments[:3]))
        out.append('MTX_DIMS\t' + '|'.join(dims))
        out.append('MTX_FIRST_COORDS\t' + json.dumps(coords))
    with read_text('spatial_q_tissue_positions.csv') as fh:
        reader=csv.reader(fh)
        rows=[]; found=[]
        for i,r in enumerate(reader):
            if i<5: rows.append(r)
            if r and r[0]=='Spot_710-1': found.append(r)
        out.append('POSITIONS_FIRST_ROWS\t' + json.dumps(rows))
        out.append('TARGET_POSITION\t' + json.dumps(found))
print('\n'.join(out))

