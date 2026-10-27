"""Stacked bars: each bar is 100% of the cylinder's material (points) at one time, split by the size
of the fragment the points belong to. One panel per time; bars = HE_0 / HE_30 / HE_60.
Run:  python3 figures/velocity_bc/plot_fragment_mass_stacked.py    (reads fragment_sizes.json; edit STYLE below)
Writes fragment_mass_stacked.png (3 panels) and fragment_mass_stacked_end.png (end of run only)
"""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- STYLE (edit me) ----------------
CLASSES = [(1,1,"1 (dust)"),(2,9,"2–9"),(10,99,"10–99"),(100,999,"100–999"),(1000,9999,"1k–9.9k"),(10000,19999,"10k–19.9k"),(20000,10**9,"≥20k")]
CLASS_COLORS = ["#d9d4cc","#c6dbef","#9ecae1","#6baed6","#3182bd","#08519c","#08306b"]   # small -> large pieces (light -> dark blue)
MIN_LABEL_PCT = 3.5          # only label segments at least this tall
BG, TEXT, MUTED = "#fcfaf8", "#2b2b2b", "#666666"
FIGSIZE, DPI = (12.5, 5.6), 150
FIGSIZE_SINGLE = (6.6, 5.6)     # size of the end-of-run-only figure
# --------------------------------------------------

here = os.path.dirname(os.path.abspath(__file__))
data = {int(k): v for k, v in json.load(open(os.path.join(here, "fragment_sizes.json"))).items()}
TIMES = [("0.333", "1/3 of run"), ("0.667", "2/3 of run"), ("1.000", "end of run")]
def draw(times, out, figsize):
    fig, axs = plt.subplots(1, len(times), figsize=figsize, sharey=True, facecolor=BG, squeeze=False)
    axs = axs[0]
    for ax, (rk, tl) in zip(axs, times):
        ax.set_facecolor(BG)
        for xi, c in enumerate((0, 30, 60)):
            s = np.array(data[c][rk]["sizes"]); n = data[c][rk]["n_points"]; bottom = 0
            for k, (lo, hi, lab) in enumerate(CLASSES):
                v = 100*s[(s>=lo)&(s<=hi)].sum()/n
                ax.bar(xi, v, bottom=bottom, width=0.62, color=CLASS_COLORS[k], edgecolor=BG, lw=1.5, label=lab if xi == 0 else None)
                if v >= MIN_LABEL_PCT:
                    ax.text(xi, bottom+v/2, f"{v:.0f}%", ha="center", va="center", fontsize=10.5, fontweight="bold", color="white" if k >= 4 else TEXT)
                bottom += v
        ax.set_xticks(range(3)); ax.set_xticklabels(["HE_0","HE_30","HE_60"], fontsize=12.5, color=TEXT)
        ax.set_ylim(0, 100); ax.set_title(f"{tl}  (t = {data[0][rk]['t_us']:.0f} µs)", fontsize=12.5, color=TEXT, pad=8)
        for sp in ("top","right"): ax.spines[sp].set_visible(False)
        for sp in ("left","bottom"): ax.spines[sp].set_color("#bbb")
        ax.tick_params(colors=MUTED, length=0, axis="x")
    axs[0].set_ylabel("% of all points", fontsize=11.5, color=TEXT)
    h, l = axs[0].get_legend_handles_labels()
    fig.legend(h[::-1], l[::-1], title="fragment size\n(points)", loc="center right", frameon=False, fontsize=10.5, title_fontsize=10.5)
    if len(times) > 1:
        fig.suptitle("Where the material ends up: share of points by fragment size\n4-point mesh, horizon 4.17 mm, 10% jitter + loading perturbation, 1.1× velocity", fontsize=13, color=TEXT)
    else:   # narrow figure: wrap the title
        fig.suptitle("Where the material ends up:\nshare of points by fragment size\n4-point mesh, horizon 4.17 mm,\n10% jitter + loading perturbation, 1.1× velocity", fontsize=11.5, color=TEXT)
    fig.tight_layout(rect=(0, 0, 0.88 if len(times) > 1 else 0.84, 0.88 if len(times) == 1 else 0.91))
    fig.savefig(os.path.join(here, out), dpi=DPI, facecolor=BG); plt.close(fig); print("wrote", out)

draw(TIMES, "fragment_mass_stacked.png", FIGSIZE)
draw(TIMES[-1:], "fragment_mass_stacked_end.png", FIGSIZE_SINGLE)   # end-of-run panel only
