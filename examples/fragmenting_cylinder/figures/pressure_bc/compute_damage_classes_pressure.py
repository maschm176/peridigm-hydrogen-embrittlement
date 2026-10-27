"""Shares of points by damage level for the pressurized-pipe runs (HE_0/30/60) at several times.
D = "Damage" (accumulated Brozzo damage averaged over a point's bonds); B = Broken_Bond_Volume_Averaged.
Run from imperfection_test/:  python3 ../figures/pressure_bc/compute_damage_classes_pressure.py
Writes damage_classes_pressure.json (read by plot_damage_classes_stacked_pressure.py).
Frames are the ones nearest to TIMES_US. Counts are numbers of points (all points, whole cylinder).
"""
import numpy as np, netCDF4 as nc, json
EDGES = [0, 0.25, 0.5, 0.75, 1e9]      # last class is open-ended: a few points have Damage slightly above 1
TIMES_US = [290, 304, 318, 331]
def names(d,k): return [bytes(x).split(b"\0")[0].decode() for x in d[k][:].data]
out = {"edges": EDGES}
for c in (0, 30, 60):
    d = nc.Dataset(f"pressure_HE{c}_4pt/pipe4pt_HE{c}_press.e"); en = names(d, "name_elem_var"); t = np.array(d["time_whole"][:]) * 1e6
    ge = lambda n, i: np.array(d[f"vals_elem_var{en.index(n)+1}eb1"][i]); out[str(c)] = {}
    for tt in TIMES_US:
        i = int(np.argmin(abs(t - tt))); rec = {"t_us": float(t[i]), "frame": i, "pressure_MPa": 5e8 * t[i] * 1e-6 / 4e-4 / 1e6}
        for key, var in (("D", "Damage"), ("B", "Broken_Bond_Volume_Averaged")):
            v = ge(var, i); rec[key+"_counts"] = np.histogram(v, bins=EDGES)[0].tolist(); rec[key+"_gt05"] = int((v > 0.5).sum()); rec["n_points"] = len(v)
        out[str(c)][str(tt)] = rec
        print(c, tt, f"t={t[i]:.0f}us", "D>0.5:", rec["D_gt05"], "D classes:", rec["D_counts"])
json.dump(out, open("../figures/pressure_bc/damage_classes_pressure.json", "w"), indent=1)
