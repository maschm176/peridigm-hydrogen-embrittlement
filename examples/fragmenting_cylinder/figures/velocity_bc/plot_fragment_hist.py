"""Histogram of fragment sizes (number of fragments per size class), rows = time, columns = HE level.
Run:  python3 figures/velocity_bc/plot_fragment_hist.py     (reads fragment_sizes.json; edit STYLE below)
Set MODE = "count" (fragments per class) or "mass" (share of all points sitting in fragments of that class).
"""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- STYLE (edit me) ----------------
MODE     = os.environ.get("MODE", "count")           # "count" or "mass" (or run: MODE=mass python3 plot_fragment_hist.py)
CLASSES  = [(1,1,"1\n(dust)"),(2,9,"2–9"),(10,99,"10–99"),(100,999,"100–\n999"),(1000,9999,"1k–\n9.9k"),(10000,10**9,"≥10k")]
COLORS   = {0:"#f2a65a", 30:"#d9622b", 60:"#8f2d0f"} # bar color per concentration
BG, TEXT, MUTED = "#fcfaf8", "#2b2b2b", "#666666"
FIGSIZE, DPI = (11.5, 8.6), 150
BAR_LABEL_FONT = 9.5
OUT = {"count":"fragment_size_hist.png","mass":"fragment_mass_hist.png"}[MODE]
# --------------------------------------------------

here = os.path.dirname(os.path.abspath(__file__))
data = {int(k): v for k, v in json.load(open(os.path.join(here, "fragment_sizes.json"))).items()}
rowkeys = ["0.333", "0.667", "1.000"]; rowlab = ["1/3 of run", "2/3 of run", "end of run"]
fig, axs = plt.subplots(3, 3, figsize=FIGSIZE, sharex=True, sharey=True, facecolor=BG)
for r, rk in enumerate(rowkeys):
    for ci, c in enumerate((0, 30, 60)):
        ax = axs[r, ci]; ax.set_facecolor(BG)
        s = np.array(data[c][rk]["sizes"]); n = data[c][rk]["n_points"]
        if MODE == "count": vals = [int(((s>=lo)&(s<=hi)).sum()) for lo,hi,_ in CLASSES]
        else:               vals = [100*s[(s>=lo)&(s<=hi)].sum()/n for lo,hi,_ in CLASSES]
        b = ax.bar(range(len(CLASSES)), vals, color=COLORS[c], width=0.72)
        for x, v in enumerate(vals):
            ax.text(x, (v*1.15 if MODE=="count" else v+1.5), (f"{v:,}" if MODE=="count" else (f"{v:.0f}%" if v>=0.5 else "<1%")) if v>0 else "",
                    ha="center", va="bottom", fontsize=BAR_LABEL_FONT, color=TEXT)
        if MODE == "count": ax.set_yscale("log"); ax.set_ylim(0.6, 6000)
        else: ax.set_ylim(0, 105)
        for sp in ("top","right"): ax.spines[sp].set_visible(False)
        for sp in ("left","bottom"): ax.spines[sp].set_color("#bbb")
        ax.tick_params(colors=MUTED); ax.set_xticks(range(len(CLASSES))); ax.set_xticklabels([l for *_,l in CLASSES], fontsize=9.5)
        ax.grid(axis="y", color="#e6e2dd", lw=0.8); ax.set_axisbelow(True)
        if r == 0: ax.set_title(f"HE_{c}", fontsize=15, color=TEXT, pad=10)
        if ci == 0: ax.set_ylabel(f"{rowlab[r]}\n(t = {data[c][rk]['t_us']:.0f} µs)\n" + ("number of fragments" if MODE=="count" else "% of all points"), fontsize=10.5, color=TEXT)
        if r == 2: ax.set_xlabel("fragment size (points)", fontsize=10.5, color=MUTED)
        ax.text(*((0.98,0.95,"right") if MODE=="count" else (0.02,0.95,"left"))[:2], f"{len(s):,} fragments\nlargest {s.max():,} pts", transform=ax.transAxes, ha=("right" if MODE=="count" else "left"), va="top", fontsize=9, color=MUTED)
ttl = "Fragment size distribution" if MODE=="count" else "Where the material ends up: share of points by fragment size"
fig.suptitle(ttl + "\n4-point mesh, horizon 4.17 mm, 10% jitter + loading perturbation, 1.1× velocity", fontsize=13.5, color=TEXT)
fig.tight_layout(rect=(0,0,1,0.95))
fig.savefig(os.path.join(here, OUT), dpi=DPI, facecolor=BG); print("wrote", OUT)
