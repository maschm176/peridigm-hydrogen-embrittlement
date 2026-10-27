"""Compute per-third broken-bond fractions and largest-piece sizes for the
4-point / 4.17 mm horizon / 10% jitter / loading-perturbation velocity runs.
Writes dsmall_thirds_data.json (read by plot_thirds.py). Run from the
fragmenting_cylinder/ directory:  python3 figures/velocity_bc/compute_thirds_data.py
Needs: numpy, netCDF4, scipy. Takes a couple of minutes (reads 3 x 1.35 GB files).
"thirds" order in the JSON is [bottom, middle, top]; "pieces" = 3 largest
connected pieces (points within 1.5x spacing in the deformed shape, isolated
points with no intact bonds excluded).
"""
import numpy as np, netCDF4 as nc, json
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
def names(d,k): return [bytes(x).split(b"\0")[0].decode() for x in d[k][:].data]
def load(f):
    d=nc.Dataset(f); en=names(d,"name_elem_var"); nn=names(d,"name_nod_var")
    con=np.array(d["connect1"][:]).reshape(-1)-1
    X=np.c_[[np.array(d[c][:])[con] for c in("coordx","coordy","coordz")]].T
    ge=lambda n,i: np.array(d[f"vals_elem_var{en.index(n)+1}eb1"][i])
    gn=lambda n,i: np.array(d[f"vals_nod_var{nn.index(n)+1}"][i])[con]
    o=np.argsort(ge("Element_Id",0))
    U=np.c_[[gn(f"Displacement{c}",-1) for c in "XYZ"]].T
    return X[o],U[o],ge("Broken_Bond_Volume_Averaged",-1)[o],ge("Weighted_Volume",-1)[o],d["time_whole"][-1]
res={}
for c in (0,30,60):
    X,U,B,W,t=load(f"imperfection_test/HE{c}_4pt_dsmall_jit10_load/fcyl4pt_HE{c}_dsmall_jit10_load.e")
    z=X[:,2]; h=(z-z.min())/(z.max()-z.min()); th=np.minimum((h*3).astype(int),2)
    thirds=[float(B[th==i].mean()) for i in range(3)]       # bottom, middle, top
    sp=np.median(cKDTree(X).query(X,k=2)[0][:,1]); P=X+U; idx=np.where(W>0)[0]
    pr=cKDTree(P[idx]).query_pairs(1.5*sp,output_type="ndarray"); m=len(idx)
    _,lab=connected_components(coo_matrix((np.ones(len(pr)),(pr[:,0],pr[:,1])),shape=(m,m)),directed=False)
    sz=np.sort(np.bincount(lab))[::-1]
    res[c]=dict(whole=float(B.mean()),thirds=thirds,pieces=[int(v) for v in sz[:3]],n=len(X),t=float(t)*1e6)
    print(c,res[c])
json.dump(res,open("figures/velocity_bc/dsmall_thirds_data.json","w"),indent=1)
