"""Paper version of damage_classes_stacked_pressure_331us.png: share of material points in each accumulated-damage class
(whole cylinder) for the pressurized pipe at TIME_US (default 331). Same data (damage_classes_pressure.json) restyled for the
paper: Computer Modern serif, white background, class colors sampled from the damage colormap used in the cylinder figure
(damage_gradient.png), no in-figure title (use the LaTeX caption).
Run:  python3 plot_paper_damage_classes.py <out_stem>   -> <out_stem>.pdf and .png"""
import sys, os, json
import numpy as np
from PIL import Image
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

TIME_US = os.environ.get("TIME_US", "331")
CLASS_LABELS = [r"$0\,\mathrm{-}\,0.25$", r"$0.25\,\mathrm{-}\,0.50$", r"$0.50\,\mathrm{-}\,0.75$", r"$0.75\,\mathrm{-}\,1.0$"]   # matches EDGES in compute_damage_classes_pressure.py
MIN_LABEL_PCT = 3.5
GRADIENT = "/Users/mschmitz/PD_Modeling_Hydrogen_Embrittlement/figs_HE/damage_gradient.png"   # top = damage 1.0

g = np.array(Image.open(GRADIENT).convert("RGB"))[:, 0, :] / 255.0
colormap_at = lambda d: g[int(round((1 - d) * (len(g) - 1)))]              # damage d in [0, 1] -> RGB
CLASS_COLORS = [colormap_at(m) for m in (0.125, 0.375, 0.625, 0.875)]
lum = lambda c: 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
    "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 9, "axes.labelsize": 9, "legend.fontsize": 8.5, "legend.title_fontsize": 8.5,
    "xtick.labelsize": 9, "ytick.labelsize": 8,
})
here = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(here, "damage_classes_pressure.json")))

fig, ax = plt.subplots(figsize=(4.9, 3.3))
for xi, c in enumerate((0, 30, 60)):
    rec = data[str(c)][TIME_US]; n = rec["n_points"]; bottom = 0
    for k, cnt in enumerate(rec["D_counts"]):
        v = 100 * cnt / n
        ax.bar(xi, v, bottom=bottom, width=0.62, color=CLASS_COLORS[k], edgecolor="white", lw=1.0,
               label=CLASS_LABELS[k] if xi == 0 else None)
        if v >= MIN_LABEL_PCT:
            ax.text(xi, bottom + v / 2, f"{v:.0f}\\%".replace("\\%", "%"), ha="center", va="center", fontsize=9,
                    color="white" if lum(CLASS_COLORS[k]) < 0.55 else "black")
        bottom += v
ax.set_xticks(range(3)); ax.set_xticklabels([r"$\mathrm{HE\_0}$", r"$\mathrm{HE\_30}$", r"$\mathrm{HE\_60}$"])
ax.tick_params(axis="x", length=0)
ax.set_ylim(0, 100); ax.set_ylabel("Percent of all points (%)")
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
h, l = ax.get_legend_handles_labels()
ax.legend(h[::-1], l[::-1], title="Damage level", loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
fig.tight_layout(pad=0.4)
out = sys.argv[1]
fig.savefig(out + ".pdf"); fig.savefig(out + ".png", dpi=300)
print("wrote", out, [tuple(np.round(c, 2)) for c in CLASS_COLORS])
