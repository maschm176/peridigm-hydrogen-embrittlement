"""Fragment-size data for the velocity-loaded runs (4pt, horizon 4.17 mm, 10% jitter,
loading perturbation, 1.1x) at 1/3, 2/3 and the end of the run.
Run from the fragmenting_cylinder/ directory:  python3 figures/velocity_bc/compute_fragment_sizes.py
Writes fragment_sizes.json (read by plot_fragment_hist.py).

Fragment = group of surviving points (Weighted_Volume > 0) linked when within LINK*spacing in the
deformed shape. Points with Weighted_Volume == 0 (no intact bonds) are size-1 fragments ("dust").
Size is in number of points (all points have nearly equal volume).
"""
import numpy as np, netCDF4 as nc, json
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
LINK = 1.5
FRACS = [1/3, 2/3, 1.0]
def names(d,k): return [bytes(x).split(b"\0")[0].decode() for x in d[k][:].data]
out = {}
for c in (0, 30, 60):
    d = nc.Dataset(f"imperfection_test/HE{c}_4pt_dsmall_jit10_load/fcyl4pt_HE{c}_dsmall_jit10_load.e")
    en, nn = names(d,"name_elem_var"), names(d,"name_nod_var")
    con = np.array(d["connect1"][:]).reshape(-1)-1
    X = np.c_[[np.array(d[a][:])[con] for a in ("coordx","coordy","coordz")]].T
    o = np.argsort(np.array(d[f"vals_elem_var{en.index('Element_Id')+1}eb1"][0])); X = X[o]
    t = np.array(d["time_whole"][:])*1e6; nf = len(t)
    sp = np.median(cKDTree(X).query(X,k=2)[0][:,1])
    out[c] = {}
    for fr in FRACS:
        i = min(nf-1, int(round(fr*(nf-1))))
        U = np.c_[[np.array(d[f"vals_nod_var{nn.index('Displacement'+a)+1}"][i])[con] for a in "XYZ"]].T[o]
        W = np.array(d[f"vals_elem_var{en.index('Weighted_Volume')+1}eb1"][i])[o]
        P = X+U; idx = np.where(W>0)[0]; m = len(idx)
        pr = cKDTree(P[idx]).query_pairs(LINK*sp, output_type="ndarray")
        _, lab = connected_components(coo_matrix((np.ones(len(pr)),(pr[:,0],pr[:,1])),shape=(m,m)), directed=False)
        sizes = np.bincount(lab).tolist() + [1]*int((W<=0).sum())
        out[c][f"{fr:.3f}"] = dict(frame=i, t_us=float(t[i]), n_points=len(X), sizes=sorted(sizes, reverse=True))
        print(c, f"{fr:.2f}", "frame", i, "t=%.0f us"%t[i], "fragments", len(sizes), "largest", max(sizes))
json.dump(out, open("figures/velocity_bc/fragment_sizes.json","w"))
