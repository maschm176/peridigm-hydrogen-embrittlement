"""Paper figure: simulated vs. experimental fracture strain against hydrogen concentration (embrittlement trend).
Values: final calibrated dogbone results (dogbone_tensile_test/calibration/CLAUDE.md; HE_60 = current best, polish unfinished).
Run:  python3 plot_paper_fracture_strain_trend.py <out_stem>   -> <out_stem>.pdf and .png"""
import sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

conc = [0, 30, 60]                       # hydrogen concentration (HE_<n>)
sim  = [15.87, 13.23, 7.80]              # simulated fracture strain (%)
exp  = [15.37, 13.27, 7.68]              # experimental fracture strain (%)

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8,
})
fig, ax = plt.subplots(figsize=(3.6, 2.9))
ax.plot(conc, sim, "s-", color="#2e8b57", ms=5, lw=1.4, label="Simulation", zorder=2)
ax.plot(conc, exp, "o", color="0.15", mfc="none", mec="0.15", ms=10, mew=1.1, label="Experiment", zorder=3)   # larger open circle around the sim marker
ax.set_xlabel("Hydrogen concentration (ppm)")
ax.set_ylabel("Fracture strain (%)")
ax.set_xticks(conc); ax.set_xlim(-4, 64); ax.set_ylim(0, 18)
ax.grid(True, alpha=0.25, lw=0.4)
ax.legend(loc="lower left", frameon=False)
fig.tight_layout(pad=0.4)
out = sys.argv[1]
fig.savefig(out + ".pdf"); fig.savefig(out + ".png", dpi=300)
print("wrote", out)
