"""Paper version of pressure_eqps_at_failure_B05.png: CDF over points of the plastic strain each point had when its
broken-bond fraction first exceeded 0.5 (pressurized pipe, failures up to CAP_US). Same data as plot_pressure_eqps.py
(pressure_eqps.npz) but restyled for the paper: Computer Modern serif font (matches the LaTeX text), white background,
no in-figure title (use the LaTeX caption).
Run:  python3 plot_paper_eqps_failure.py <out_stem>   -> <out_stem>.pdf and <out_stem>.png"""
import sys, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORS = {0: "#b497dc", 30: "#7a4cb5", 60: "#34135e"}   # purples: not used in the damage colormap (blue-yellow-red)
CAP_US, XMAX, YMAX = 331, 0.5, 0.5

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8,
})
here = os.path.dirname(os.path.abspath(__file__))
Z = np.load(os.path.join(here, "pressure_eqps.npz"))
cdf = lambda v: (np.sort(v), np.arange(1, len(v) + 1) / len(v))

fig, ax = plt.subplots(figsize=(4.9, 3.3))
for c in (0, 30, 60):
    e = Z[f"HE{c}_fail05_eqps"]; tt = Z[f"HE{c}_fail05_t"]
    ok = ~np.isnan(e) & (tt <= CAP_US)
    x, y = cdf(e[ok]); frac = ok.mean()
    ax.plot(x, y * frac, color=COLORS[c], lw=1.5,
            label=rf"$\mathrm{{HE\_{c}}}$")
    # tick on the curve at the mean plastic strain at failure: dashed line down to the x-axis + marker on the axis
    m = e[ok].mean(); ym = np.interp(m, x, y * frac)
    ax.plot([m, m], [0, ym], color=COLORS[c], lw=0.8, ls=(0, (3, 2)))
    ax.plot([m], [0], marker="^", ms=5, color=COLORS[c], clip_on=False, zorder=5)
ax.set_xlim(0, XMAX); ax.set_ylim(0, YMAX)
ax.set_xlabel("Plastic strain at failure")
ax.set_ylabel("Fraction of all points failed\nwith plastic strain $\\leq$ value")
ax.grid(True, alpha=0.25, lw=0.4)
ax.legend(loc="upper right", frameon=False)
fig.tight_layout(pad=0.4)
out = sys.argv[1]
fig.savefig(out + ".pdf"); fig.savefig(out + ".png", dpi=300)
print("wrote", out)
