"""Shares of points by damage level for the velocity-loaded runs (4pt, horizon 4.17 mm, 10% jitter, loading
perturbation, 1.1x) at 1/3, 2/3 and the end of the run. Two variables are binned:
  D = "Damage"                      accumulated Brozzo damage averaged over a point's bonds (about plastic strain)
  B = "Broken_Bond_Volume_Averaged" fraction of a point's bonds that are broken (about lost connectivity)
Run from the fragmenting_cylinder/ directory:  python3 figures/velocity_bc/compute_damage_classes.py
Writes damage_classes.json (read by plot_damage_classes_stacked.py). Counts are numbers of points (out of n_points).
"""
import numpy as np, netCDF4 as nc, json
EDGES = [0, 0.25, 0.5, 0.75, 0.9, 1.0001]
FRACS = [1/3, 2/3, 1.0]
def names(d,k): return [bytes(x).split(b"\0")[0].decode() for x in d[k][:].data]
out = {"edges": EDGES}
for c in (0, 30, 60):
    d = nc.Dataset(f"imperfection_test/HE{c}_4pt_dsmall_jit10_load/fcyl4pt_HE{c}_dsmall_jit10_load.e")
    en = names(d, "name_elem_var"); t = np.array(d["time_whole"][:]) * 1e6; nf = len(t)
    ge = lambda n, i: np.array(d[f"vals_elem_var{en.index(n)+1}eb1"][i])
    out[str(c)] = {}
    for fr in FRACS:
        i = min(nf-1, int(round(fr*(nf-1)))); rec = {"t_us": float(t[i]), "frame": i}
        for key, var in (("D", "Damage"), ("B", "Broken_Bond_Volume_Averaged")):
            v = ge(var, i); rec[key+"_counts"] = np.histogram(v, bins=EDGES)[0].tolist()
            rec[key+"_gt05"] = int((v > 0.5).sum()); rec["n_points"] = len(v)
        out[str(c)][f"{fr:.3f}"] = rec
        print(c, f"{fr:.2f}", f"t={t[i]:.0f}us", "D>0.5:", rec["D_gt05"], "B>0.5:", rec["B_gt05"], "of", rec["n_points"])
json.dump(out, open("figures/velocity_bc/damage_classes.json", "w"), indent=1)
