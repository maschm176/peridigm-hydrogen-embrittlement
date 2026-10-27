"""Plastic-strain data for the pressurized-pipe runs (HE_0/30/60).
Run from imperfection_test/:  python3 ../figures/pressure_bc/compute_pressure_eqps.py   (writes ../figures/pressure_bc/pressure_eqps.npz)
For each run stores:
  t_us          frame times
  eqps[frame]   equivalent plastic strain of every point at frames from T_START on (every STRIDE-th frame)
  fail_t_us     per point: time at which its broken-bond fraction first exceeds 0.5 (and 0.9) -- NaN if never
  fail_eqps_*   per point: plastic strain at that moment ("plastic strain at failure")
  radius_ref    per point reference radius, height (so subsets can be made later)
"""
import numpy as np, netCDF4 as nc, os
T_START, STRIDE = 225.0, 4
def names(d,k): return [bytes(x).split(b"\0")[0].decode() for x in d[k][:].data]
out = {}
for c in (0, 30, 60):
    f = f"pressure_HE{c}_4pt/pipe4pt_HE{c}_press.e"
    if not os.path.exists(f) or not os.path.exists(f"pressure_HE{c}_4pt/done.txt"): print("skip", c); continue
    d = nc.Dataset(f); en = names(d, "name_elem_var")
    con = np.array(d["connect1"][:]).reshape(-1) - 1; t = np.array(d["time_whole"][:]) * 1e6
    X = np.c_[[np.array(d[a][:])[con] for a in ("coordx", "coordy", "coordz")]].T
    ge = lambda n, i: np.array(d[f"vals_elem_var{en.index(n)+1}eb1"][i])
    o = np.argsort(ge("Element_Id", 0)); X = X[o]
    idx = [i for i in range(len(t)) if t[i] >= T_START][::STRIDE]
    E = np.array([ge("Equivalent_Plastic_Strain", i)[o] for i in idx])
    n = len(X); tf5 = np.full(n, np.nan); tf9 = np.full(n, np.nan); ef5 = np.full(n, np.nan); ef9 = np.full(n, np.nan)
    for i in range(len(t)):
        B = ge("Broken_Bond_Volume_Averaged", i)[o]; Ei = ge("Equivalent_Plastic_Strain", i)[o]
        for thr, tf, ef in ((0.5, tf5, ef5), (0.9, tf9, ef9)):
            new = (B > thr) & np.isnan(tf); tf[new] = t[i]; ef[new] = Ei[new]
    out[f"HE{c}_t"] = t[idx]; out[f"HE{c}_eqps"] = E
    out[f"HE{c}_fail05_t"] = tf5; out[f"HE{c}_fail05_eqps"] = ef5; out[f"HE{c}_fail09_t"] = tf9; out[f"HE{c}_fail09_eqps"] = ef9
    out[f"HE{c}_r"] = np.hypot(X[:, 0], X[:, 1]); out[f"HE{c}_z"] = X[:, 2]
    print(c, "frames", len(idx), "failed(B>0.5):", int((~np.isnan(tf5)).sum()), "failed(B>0.9):", int((~np.isnan(tf9)).sum()))
np.savez("../figures/pressure_bc/pressure_eqps.npz", **out)
