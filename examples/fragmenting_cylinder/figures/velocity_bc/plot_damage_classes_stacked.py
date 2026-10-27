"""Stacked bars: each bar is 100% of the points; split by damage level. Two panels: accumulated damage D ("Damage")
and broken-bond fraction B. Bold number above each bar = share of points above 0.5 (the dark classes).
Run:  python3 figures/velocity_bc/plot_damage_classes_stacked.py              -> end of run
      TIME=0.667 python3 figures/velocity_bc/plot_damage_classes_stacked.py   -> 2/3 of run  (0.333 = 1/3)
Reads damage_classes.json (compute_damage_classes.py). Edit the STYLE block to restyle.
Writes damage_classes_stacked_{end,2of3,1of3}.png
"""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- STYLE (edit me) ----------------
CLASS_LABELS = ["< 0.25", "0.25–0.5", "0.5–0.75", "0.75–0.9", "≥ 0.9"]      # must match EDGES in compute_damage_classes.py
CLASS_COLORS = ["#feedde", "#fdbe85", "#fd8d3c", "#d94801", "#7f2704"]       # low -> high damage (light -> dark orange)
MIN_LABEL_PCT = 3.5
BG, TEXT, MUTED = "#fcfaf8", "#2b2b2b", "#666666"
FIGSIZE, DPI = (11.5, 5.8), 150
PANELS = [("D", "Accumulated damage D (\"Damage\" field)"), ("B", "Broken-bond fraction")]
# --------------------------------------------------

here = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(here, "damage_classes.json")))
tkey = os.environ.get("TIME", "1.000"); tag = {"0.333": "1of3", "0.667": "2of3", "1.000": "end"}[tkey]
tname = {"0.333": "1/3 of run", "0.667": "2/3 of run", "1.000": "end of run"}[tkey]
fig, axs = plt.subplots(1, 2, figsize=FIGSIZE, sharey=True, facecolor=BG)
for ax, (key, title) in zip(axs, PANELS):
    ax.set_facecolor(BG)
    for xi, c in enumerate((0, 30, 60)):
        rec = data[str(c)][tkey]; n = rec["n_points"]; counts = rec[key + "_counts"]; bottom = 0
        for k, cnt in enumerate(counts):
            v = 100 * cnt / n
            ax.bar(xi, v, bottom=bottom, width=0.62, color=CLASS_COLORS[k], edgecolor=BG, lw=1.5, label=CLASS_LABELS[k] if xi == 0 else None)
            if v >= MIN_LABEL_PCT:
                ax.text(xi, bottom + v/2, f"{v:.0f}%", ha="center", va="center", fontsize=10.5, fontweight="bold", color="white" if k >= 3 else TEXT)
            bottom += v
        ax.text(xi, 102, f"{100*rec[key+'_gt05']/n:.0f}% above 0.5", ha="center", va="bottom", fontsize=11, fontweight="bold", color=TEXT)
    ax.set_xticks(range(3)); ax.set_xticklabels(["HE_0", "HE_30", "HE_60"], fontsize=12.5, color=TEXT)
    ax.set_ylim(0, 100); ax.set_title(title, fontsize=12.5, color=TEXT, pad=28)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"): ax.spines[sp].set_color("#bbb")
    ax.tick_params(colors=MUTED, length=0, axis="x")
axs[0].set_ylabel("% of all points", fontsize=11.5, color=TEXT)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h[::-1], l[::-1], title="damage level", loc="center right", frameon=False, fontsize=10.5, title_fontsize=10.5)
fig.suptitle(f"Share of points by damage level — {tname} (t = {data['0'][tkey]['t_us']:.0f} µs)\n4-point mesh, horizon 4.17 mm, 10% jitter + loading perturbation, 1.1× velocity (velocity BC)", fontsize=13, color=TEXT)
fig.tight_layout(rect=(0, 0, 0.9, 0.91))
out = f"damage_classes_stacked_{tag}.png"
fig.savefig(os.path.join(here, out), dpi=DPI, facecolor=BG); print("wrote", out)
