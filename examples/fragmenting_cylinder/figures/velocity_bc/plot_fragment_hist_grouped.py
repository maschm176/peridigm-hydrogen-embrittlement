"""Grouped fragment-size histograms: one figure per time (1/3, 2/3, end of run); in each, the three
HE levels sit side by side within every fragment-size class.
Run:  python3 figures/velocity_bc/plot_fragment_hist_grouped.py          (number of fragments per class, log y)
      MODE=mass python3 figures/velocity_bc/plot_fragment_hist_grouped.py (% of all points in each class)
Reads fragment_sizes.json; edit the STYLE block to change colors, size classes, fonts.
Writes fragment_hist_grouped_{1of3,2of3,end}.png  (or fragment_mass_grouped_*.png in mass mode).
"""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- STYLE (edit me) ----------------
MODE     = os.environ.get("MODE", "count")           # "count" or "mass"
CLASSES  = [(1,1,"1\n(dust)"),(2,9,"2–9"),(10,99,"10–99"),(100,999,"100–\n999"),(1000,9999,"1k–\n9.9k"),(10000,10**9,"≥10k")]
COLORS   = {0:"#e8943a", 30:"#c8481f", 60:"#6e1d0a"}
BG, TEXT, MUTED, GRID = "#fcfaf8", "#2b2b2b", "#666666", "#e6e2dd"
FIGSIZE, DPI = (10.5, 5.6), 150
BAR_W, LABEL_FONT = 0.26, 9
# --------------------------------------------------

here = os.path.dirname(os.path.abspath(__file__))
data = {int(k): v for k, v in json.load(open(os.path.join(here, "fragment_sizes.json"))).items()}
TIMES = [("0.333", "1of3", "1/3 of run"), ("0.667", "2of3", "2/3 of run"), ("1.000", "end", "end of run")]
prefix = "fragment_hist_grouped" if MODE == "count" else "fragment_mass_grouped"
for rk, tag, tlabel in TIMES:
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BG); ax.set_facecolor(BG)
    for j, c in enumerate((0, 30, 60)):
        s = np.array(data[c][rk]["sizes"]); n = data[c][rk]["n_points"]
        vals = [int(((s>=lo)&(s<=hi)).sum()) if MODE=="count" else 100*s[(s>=lo)&(s<=hi)].sum()/n for lo,hi,_ in CLASSES]
        x = np.arange(len(CLASSES)) + (j-1)*(BAR_W+0.02)
        ax.bar(x, vals, width=BAR_W, color=COLORS[c], label=f"HE_{c}   ({len(s):,} fragments, largest {s.max():,} pts)")
        for xi, v in zip(x, vals):
            if v <= 0: continue
            txt = f"{v:,}" if MODE=="count" else (f"{v:.0f}" if v >= 0.5 else "<1")
            ax.text(xi, v*1.18 if MODE=="count" else v+1.2, txt, ha="center", va="bottom", fontsize=LABEL_FONT, color=TEXT)
    if MODE == "count": ax.set_yscale("log"); ax.set_ylim(0.6, 8000); ax.set_ylabel("number of fragments", fontsize=11.5, color=TEXT)
    else: ax.set_ylim(0, 108); ax.set_ylabel("% of all points", fontsize=11.5, color=TEXT)
    ax.set_xticks(range(len(CLASSES))); ax.set_xticklabels([l for *_,l in CLASSES], fontsize=10.5)
    ax.set_xlabel("fragment size (points)", fontsize=11.5, color=MUTED)
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    for sp in ("left","bottom"): ax.spines[sp].set_color("#bbb")
    ax.tick_params(colors=MUTED); ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=10, loc="upper right")
    t = data[0][rk]["t_us"]
    what = "Fragment size distribution" if MODE=="count" else "Share of material by fragment size"
    ax.set_title(f"{what} — {tlabel} (t = {t:.0f} µs)\n4-point mesh, horizon 4.17 mm, 10% jitter + loading perturbation, 1.1× velocity", fontsize=12.5, color=TEXT, pad=12)
    fig.tight_layout(); out = f"{prefix}_{tag}.png"
    fig.savefig(os.path.join(here, out), dpi=DPI, facecolor=BG); plt.close(fig); print("wrote", out)
