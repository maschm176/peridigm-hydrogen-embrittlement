"""Fraction of points vs time for the pressurized-pipe runs (HE_0/30/60), every saved frame.
D = "Damage" (accumulated Brozzo damage averaged over a point's bonds); B = Broken_Bond_Volume_Averaged.
Run from imperfection_test/:  python3 ../figures/pressure_bc/compute_damage_timeseries_pressure.py
Writes damage_timeseries_pressure.json (read by plot_paper_damage_timeseries.py).
Per frame: fraction of all points with D > 0.5, D > 0.75, and B > 0.5 ("failed": more than half of the bonds broken).
"""
import numpy as np, netCDF4 as nc, json
def names(d,k): return [bytes(x).split(b"\0")[0].decode() for x in d[k][:].data]
out = {}
for c in (0, 30, 60):
    d = nc.Dataset(f"pressure_HE{c}_4pt/pipe4pt_HE{c}_press.e"); en = names(d, "name_elem_var")
    t = np.array(d["time_whole"][:]) * 1e6
    ge = lambda n, i: np.array(d[f"vals_elem_var{en.index(n)+1}eb1"][i])
    rec = {"t_us": t.tolist(), "D_gt05": [], "D_gt075": [], "B_gt05": []}
    for i in range(len(t)):
        D = ge("Damage", i); B = ge("Broken_Bond_Volume_Averaged", i)
        rec["D_gt05"].append(float((D > 0.5).mean())); rec["D_gt075"].append(float((D > 0.75).mean())); rec["B_gt05"].append(float((B > 0.5).mean()))
    rec["n_points"] = len(D); out[str(c)] = rec
    print(c, len(t), "frames; last t =", round(t[-1], 1))
json.dump(out, open("../figures/pressure_bc/damage_timeseries_pressure.json", "w"))
