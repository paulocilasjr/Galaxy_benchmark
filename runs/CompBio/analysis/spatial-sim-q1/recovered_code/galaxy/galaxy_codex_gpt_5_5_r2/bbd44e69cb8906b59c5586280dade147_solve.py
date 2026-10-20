
import sys, tarfile, gzip, csv, io, json, math, itertools, collections
archive=sys.argv[1]; TARGET='Spot_710-1'

def gaussian_solve(M,b):
    n=len(b); A=[list(M[i])+[b[i]] for i in range(n)]
    for col in range(n):
        piv=max(range(col,n), key=lambda r: abs(A[r][col]))
        if abs(A[piv][col]) < 1e-9: return None
        A[col],A[piv]=A[piv],A[col]
        pv=A[col][col]
        for j in range(col,n+1): A[col][j]/=pv
        for r in range(n):
            if r==col: continue
            fac=A[r][col]
            if fac:
                for j in range(col,n+1): A[r][j]-=fac*A[col][j]
    return [A[i][n] for i in range(n)]

def fit_subset(Acols,y,idx):
    k=len(Acols); n=len(idx); G=[[0.0]*k for _ in range(k)]; c=[0.0]*k; yy=0.0
    for g in idx:
        yg=y[g]; yy+=yg*yg; vals=[Acols[j][g] for j in range(k)]
        for i,v in enumerate(vals):
            c[i]+=v*yg
            for j in range(i,k): G[i][j]+=v*vals[j]
    for i in range(k):
        for j in range(i): G[i][j]=G[j][i]
        G[i][i]+=1e-8
    w=gaussian_solve(G,c)
    if w is None or min(w) < -1e-6: return None
    w=[0.0 if x<0 else x for x in w]
    sse=0.0
    for g in idx:
        d=y[g]-sum(w[j]*Acols[j][g] for j in range(k)); sse+=d*d
    bic=n*math.log(max(sse/n,1e-12))+k*math.log(n); rel=math.sqrt(sse/max(yy,1e-12))
    return w,sse,bic,rel

def subset_results(type_names,means,y,idx):
    res=[]
    for r in range(1,len(type_names)+1):
        for combo in itertools.combinations(range(len(type_names)), r):
            fit=fit_subset([means[i] for i in combo],y,idx)
            if fit is None: continue
            w,sse,bic,rel=fit
            res.append({'types':[type_names[i] for i in combo], 'weights':w, 'sse':sse, 'bic':bic, 'rel_rmse':rel})
    by_bic=sorted(res,key=lambda x:x['bic']); by_sse=sorted(res,key=lambda x:x['sse'])
    return by_bic, by_sse

def coefficient_map(type_names, result):
    d={t:0.0 for t in type_names}
    for t,w in zip(result['types'],result['weights']): d[t]=w
    return d

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
    counts=pick('spatial_q_sc_counts.csv','sc_counts.csv'); meta=pick('spatial_q_sc_metadata.csv','sc_metadata.csv')
    featsn=pick('features.tsv.gz','spatial_q_features.tsv.gz'); barsn=pick('barcodes.tsv.gz','spatial_q_barcodes.tsv.gz'); mtxn=pick('matrix.mtx.gz','spatial_q_matrix.mtx.gz')
    def text(name,gz=False):
        f=tar.extractfile(name); return io.TextIOWrapper(gzip.GzipFile(fileobj=f),encoding='utf-8') if gz else io.TextIOWrapper(f,encoding='utf-8')
    cell_type={}
    with text(meta) as fh:
        rdr=csv.reader(fh); hdr=next(rdr); tc=hdr.index('cell_type') if 'cell_type' in hdr else 1
        for r in rdr: cell_type[r[0]]=r[tc]
    with text(counts) as fh:
        rdr=csv.reader(fh); header=next(rdr); genes=header[1:]; sums={}; nct=collections.Counter()
        for row in rdr:
            ct=cell_type[row[0]]; nct[ct]+=1
            if ct not in sums: sums[ct]=[0.0]*len(genes)
            acc=sums[ct]
            for i,v in enumerate(row[1:]): acc[i]+=float(v)
    type_names=sorted(sums); means=[[v/nct[ct] for v in sums[ct]] for ct in type_names]
    feature_genes=[]
    with text(featsn, True) as fh:
        for line in fh:
            p=line.rstrip('\n').split('\t'); feature_genes.append(p[1] if len(p)>1 else p[0])
    gindex={g:i for i,g in enumerate(genes)}; map_idx=[]; mismatches=0
    for fg in feature_genes:
        gi=gindex.get(fg); map_idx.append(gi); mismatches += 1 if gi is None else 0
    target_col=None
    with text(barsn, True) as fh:
        for i,line in enumerate(fh,start=1):
            if line.strip()==TARGET: target_col=i
    y=[0.0]*len(genes); nnz=0
    with text(mtxn, True) as fh:
        for line in fh:
            if line.startswith('%'): continue
            dims=line.split(); break
        for line in fh:
            r,c,v=line.split()
            if int(c)==target_col:
                gi=map_idx[int(r)-1]
                if gi is not None: y[gi]=float(v); nnz+=1
    scores=[]
    for g in range(len(genes)):
        vals=[m[g] for m in means]; mu=sum(vals)/len(vals); var=sum((x-mu)**2 for x in vals)/len(vals)
        scores.append((var/(mu+1.0),g))
    var_idx=[g for _,g in sorted(scores, reverse=True)[:300]]
    all_idx=list(range(len(genes)))
    var_bic,var_sse=subset_results(type_names,means,y,var_idx)
    all_bic,all_sse=subset_results(type_names,means,y,all_idx)
    best_var_bic=var_bic[0]; best_all_bic=all_bic[0]; nnls_var=var_sse[0]; nnls_all=all_sse[0]
    cm_var=coefficient_map(type_names, nnls_var); cm_all=coefficient_map(type_names, nnls_all)
    chosen_nnls_var=sorted([t for t,w in cm_var.items() if w>=0.25])
    chosen_nnls_all=sorted([t for t,w in cm_all.items() if w>=0.25])
    # Prefer agreement of all-gene and variable-gene exact NNLS coefficients; BIC lines are diagnostics for overfit control.
    chosen=chosen_nnls_var if chosen_nnls_var==chosen_nnls_all else sorted(set(chosen_nnls_var).intersection(chosen_nnls_all))
    if not chosen: chosen=sorted(set(chosen_nnls_var).union(chosen_nnls_all))
    def compact(rows):
        return [{'types':r['types'],'weights':[round(x,4) for x in r['weights']],'sse':round(r['sse'],3),'bic':round(r['bic'],3),'rel_rmse':round(r['rel_rmse'],6)} for r in rows[:12]]
    out.append('cell_type_order\t'+','.join(type_names))
    out.append('gene_match_mismatches\t'+str(mismatches))
    out.append('target\t%s\tcolumn_1based=%s\tnnz=%d\ttotal_counts=%.3f'%(TARGET,target_col,nnz,sum(y)))
    out.append('nnls_variable_coefficients\t'+json.dumps({t:round(cm_var[t],4) for t in type_names}, sort_keys=True))
    out.append('nnls_all_gene_coefficients\t'+json.dumps({t:round(cm_all[t],4) for t in type_names}, sort_keys=True))
    out.append('chosen_from_nnls_variable\t'+','.join(chosen_nnls_var))
    out.append('chosen_from_nnls_all\t'+','.join(chosen_nnls_all))
    out.append('best_variable_bic\t'+json.dumps(compact(var_bic)))
    out.append('best_all_gene_bic\t'+json.dumps(compact(all_bic)))
    out.append('best_variable_sse\t'+json.dumps(compact(var_sse)))
    out.append('best_all_gene_sse\t'+json.dumps(compact(all_sse)))
    out.append('ANSWER\t'+','.join(chosen))
print('\n'.join(out))

