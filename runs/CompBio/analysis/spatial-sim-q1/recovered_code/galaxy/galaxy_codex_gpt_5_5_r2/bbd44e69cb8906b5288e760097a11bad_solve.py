
import sys, tarfile, gzip, csv, io, json, math, itertools, collections
archive=sys.argv[1]
TARGET='Spot_710-1'

def gaussian_solve(M, b):
    n=len(b)
    A=[list(M[i])+[b[i]] for i in range(n)]
    for col in range(n):
        piv=max(range(col,n), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-10:
            return None
        if piv != col:
            A[col],A[piv]=A[piv],A[col]
        pv=A[col][col]
        for j in range(col,n+1): A[col][j] /= pv
        for r in range(n):
            if r==col: continue
            fac=A[r][col]
            if fac:
                for j in range(col,n+1): A[r][j] -= fac*A[col][j]
    return [A[i][n] for i in range(n)]

def fit_subset(Acols, y, gene_idx=None):
    k=len(Acols)
    if gene_idx is None:
        idx=range(len(y)); n=len(y)
    else:
        idx=gene_idx; n=len(gene_idx)
    G=[[0.0]*k for _ in range(k)]
    c=[0.0]*k
    yy=0.0
    for g in idx:
        yg=y[g]; yy += yg*yg
        vals=[Acols[j][g] for j in range(k)]
        for i,v in enumerate(vals):
            c[i] += v*yg
            row=G[i]
            for j in range(i,k): row[j] += v*vals[j]
    for i in range(k):
        for j in range(i): G[i][j]=G[j][i]
        G[i][i] += 1e-8
    w=gaussian_solve(G,c)
    if w is None or min(w) < -1e-7:
        return None
    w=[0.0 if x<0 else x for x in w]
    sse=0.0
    for g in idx:
        pred=sum(w[j]*Acols[j][g] for j in range(k))
        d=y[g]-pred; sse += d*d
    bic=n*math.log(max(sse/n,1e-12)) + k*math.log(n)
    rel=math.sqrt(sse/max(yy,1e-12))
    return w,sse,bic,rel,n

def all_subset_fits(type_names, means, y, gene_idx=None):
    results=[]
    for r in range(1,len(type_names)+1):
        for combo in itertools.combinations(range(len(type_names)), r):
            fit=fit_subset([means[i] for i in combo], y, gene_idx)
            if fit is None: continue
            w,sse,bic,rel,n=fit
            results.append({'types':[type_names[i] for i in combo], 'weights':w, 'sse':sse, 'bic':bic, 'rel_rmse':rel, 'n':n})
    results.sort(key=lambda x: x['bic'])
    return results

out=[]
with tarfile.open(archive,'r:*') as tar:
    names=[m.name for m in tar.getmembers() if m.isfile()]
    def pick(*cands):
        for c in cands:
            if c in names: return c
        for c in cands:
            for n in names:
                if n.endswith('/'+c) or n.endswith(c): return n
        raise KeyError(cands)
    counts=pick('spatial_q_sc_counts.csv','sc_counts.csv')
    meta=pick('spatial_q_sc_metadata.csv','sc_metadata.csv')
    featsn=pick('features.tsv.gz','spatial_q_features.tsv.gz')
    barsn=pick('barcodes.tsv.gz','spatial_q_barcodes.tsv.gz')
    mtxn=pick('matrix.mtx.gz','spatial_q_matrix.mtx.gz')
    def text(name,gz=False):
        f=tar.extractfile(name)
        return io.TextIOWrapper(gzip.GzipFile(fileobj=f), encoding='utf-8') if gz else io.TextIOWrapper(f, encoding='utf-8')
    cell_type={}
    with text(meta) as fh:
        rdr=csv.reader(fh); hdr=next(rdr); type_col=hdr.index('cell_type') if 'cell_type' in hdr else 1
        id_col=0
        for r in rdr:
            cell_type[r[id_col]]=r[type_col]
    with text(counts) as fh:
        rdr=csv.reader(fh); header=next(rdr); genes=header[1:]
        sums={}; counts_by_type=collections.Counter(); total_cells=0
        for row in rdr:
            cid=row[0]; ct=cell_type[cid]
            if ct not in sums: sums[ct]=[0.0]*len(genes)
            vals=row[1:]
            acc=sums[ct]
            for i,v in enumerate(vals): acc[i]+=float(v)
            counts_by_type[ct]+=1; total_cells+=1
    type_names=sorted(sums)
    means=[]
    for ct in type_names:
        n=counts_by_type[ct]
        means.append([v/n for v in sums[ct]])
    # check feature names against sc gene order
    feature_genes=[]
    with text(featsn, True) as fh:
        for line in fh:
            parts=line.rstrip('\n').split('\t')
            feature_genes.append(parts[1] if len(parts)>1 else parts[0])
    gene_index={g:i for i,g in enumerate(genes)}
    map_idx=[]; mismatches=0
    for fg in feature_genes:
        if fg in gene_index: map_idx.append(gene_index[fg])
        else: map_idx.append(None); mismatches+=1
    target_col=None; nbar=0
    with text(barsn, True) as fh:
        for i,line in enumerate(fh, start=1):
            nbar=i
            if line.strip()==TARGET: target_col=i
    if target_col is None: raise SystemExit('target barcode not found')
    y=[0.0]*len(genes)
    nnz=0
    with text(mtxn, True) as fh:
        for line in fh:
            if line.startswith('%'): continue
            nr,nc,nentries=map(int,line.split()[:3]); break
        for line in fh:
            r,c,v=line.split()
            if int(c)==target_col:
                gi=map_idx[int(r)-1]
                if gi is not None:
                    y[gi]=float(v); nnz+=1
    target_total=sum(y)
    type_lib={ct:sum(means[i]) for i,ct in enumerate(type_names)}
    # highly discriminative genes by between-type variance scaled by mean; use top 300 plus any gene with clear marker behavior.
    scores=[]
    for g in range(len(genes)):
        vals=[m[g] for m in means]
        mu=sum(vals)/len(vals)
        var=sum((x-mu)**2 for x in vals)/len(vals)
        scores.append((var/(mu+1.0), g))
    var_idx=[g for _,g in sorted(scores, reverse=True)[:300]]
    all_fits=all_subset_fits(type_names, means, y, None)
    var_fits=all_subset_fits(type_names, means, y, var_idx)
    # Also compute full six-type coefficients on all and variable genes.
    full_all=fit_subset(means, y, None)
    full_var=fit_subset(means, y, var_idx)
    best=var_fits[0]
    # Include coefficients that are biologically nontrivial; weights are estimated cell counts.
    chosen=sorted([t for t,w in zip(best['types'], best['weights']) if w >= 0.25])
    # If BIC chooses a strict subset, confirm no excluded type has >=0.25 in full variable fit.
    if full_var:
        fw=full_var[0]
        for t,w in zip(type_names, fw):
            if w >= 0.25 and t not in chosen:
                chosen.append(t)
        chosen=sorted(chosen)
    out.append('resolved_files\t'+json.dumps({'counts':counts,'metadata':meta,'features':featsn,'barcodes':barsn,'matrix':mtxn}, sort_keys=True))
    out.append('gene_match_mismatches\t'+str(mismatches))
    out.append('cell_type_order\t'+','.join(type_names))
    out.append('single_cell_counts_by_type\t'+json.dumps(dict(sorted(counts_by_type.items()))))
    out.append('mean_library_by_type\t'+json.dumps({ct:round(type_lib[ct],3) for ct in type_names}, sort_keys=True))
    out.append('target_spot\t%s\tcolumn_1based=%d\tnnz=%d\ttotal_counts=%.3f'%(TARGET,target_col,nnz,target_total))
    out.append('top_variable_subset_fits\t'+json.dumps([{ 'types':r['types'], 'weights':[round(x,4) for x in r['weights']], 'bic':round(r['bic'],3), 'rel_rmse':round(r['rel_rmse'],6)} for r in var_fits[:10]]))
    out.append('top_all_gene_subset_fits\t'+json.dumps([{ 'types':r['types'], 'weights':[round(x,4) for x in r['weights']], 'bic':round(r['bic'],3), 'rel_rmse':round(r['rel_rmse'],6)} for r in all_fits[:10]]))
    out.append('full_variable_coefficients\t'+json.dumps({t:round(w,4) for t,w in zip(type_names, full_var[0])}, sort_keys=True))
    out.append('full_all_gene_coefficients\t'+json.dumps({t:round(w,4) for t,w in zip(type_names, full_all[0])}, sort_keys=True))
    out.append('ANSWER\t'+','.join(chosen))
print('\n'.join(out))

