"""Paper figure: fraction of points failed (broken-bond fraction > 0.5) vs time for the pressurized pipe, HE_0/30/60.
Data: damage_timeseries_pressure.json (compute_damage_timeseries_pressure.py). Curves are cut at CAP_US because after
that the pressure body force keeps pushing detached points (see README). VAR picks the metric: B_gt05 (failed, default),
D_gt05 or D_gt075 (damage thresholds). Style matches plot_paper_eqps_failure.py.
Run:  python3 plot_paper_damage_timeseries.py <out_stem>   -> <out_stem>.pdf and <out_stem>.png"""
import sys, os, json
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

VAR = os.environ.get("VAR", "B_gt05")
YLABEL = {"B_gt05": "Fraction of all points failed", "D_gt05": "Fraction of points with damage $>0.5$",
          "D_gt075": "Fraction of points with damage $>0.75$"}[VAR]
COLORS = {0: "#b497dc", 30: "#7a4cb5", 60: "#34135e"}
CAP_US, XMIN_US = 331, 270

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8,
})
here = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(here, "damage_timeseries_pressure.json")))

fig, ax = plt.subplots(figsize=(4.9, 3.3))
for c in (0, 30, 60):
    t = np.array(data[str(c)]["t_us"]); v = np.array(data[str(c)][VAR]); ok = (t >= XMIN_US) & (t <= CAP_US)
    ax.plot(t[ok], v[ok], color=COLORS[c], lw=1.5, label=rf"$\mathrm{{HE\_{c}}}$")
ax.set_xlim(XMIN_US, CAP_US); ax.set_ylim(0, None)
ax.set_xlabel(r"Time ($\mu$s)"); ax.set_ylabel(YLABEL)
ax.grid(True, alpha=0.25, lw=0.4)
ax.legend(loc="upper left", frameon=False)
fig.tight_layout(pad=0.4)
out = sys.argv[1]
fig.savefig(out + ".pdf"); fig.savefig(out + ".png", dpi=300)
print("wrote", out)
