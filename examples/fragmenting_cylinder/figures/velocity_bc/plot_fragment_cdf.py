"""Cumulative fragment-size plots, one panel per time (1/3, 2/3, end of run), one curve per HE level.
Run:  python3 figures/velocity_bc/plot_fragment_cdf.py     (reads fragment_sizes.json; edit STYLE below)
Writes:
  fragment_size_ccdf.png  -- fraction of fragments with size >= s   (complementary CDF, log-log)
  fragment_mass_cdf.png   -- fraction of all points that sit in fragments of size <= s  (cumulative mass)
Size s is in points. Points with no intact bonds count as size-1 fragments ("dust").
"""
import json, os
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- STYLE (edit me) ----------------
COLORS = {0:"#e8943a", 30:"#c8481f", 60:"#6e1d0a"}   # line color per concentration
LW, MARKERS = 2.6, False                            # line width; markers at each step
BG, TEXT, MUTED, GRID = "#fcfaf8", "#2b2b2b", "#666666", "#e6e2dd"
FIGSIZE, DPI = (13, 4.6), 150
FIGSIZE_SINGLE = (7.2, 5.4)       # size of the single-time plots
XLIM = (0.8, 6e4)
OUT_CCDF, OUT_MASS = "fragment_size_ccdf.png", "fragment_mass_cdf.png"
# --------------------------------------------------

here = os.path.dirname(os.path.abspath(__file__))
data = {int(k): v for k, v in json.load(open(os.path.join(here, "fragment_sizes.json"))).items()}
rowkeys = ["0.333", "0.667", "1.000"]
TIME_LABEL = {"0.333": "1/3 of run", "0.667": "2/3 of run", "1.000": "end of run"}

def style(ax, r, ylabel, first):
    ax.set_facecolor(BG); ax.set_xscale("log"); ax.set_xlim(*XLIM)
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    for sp in ("left","bottom"): ax.spines[sp].set_color("#bbb")
    ax.tick_params(colors=MUTED); ax.grid(color=GRID, lw=0.8, which="major"); ax.set_axisbelow(True)
    ax.set_xlabel("fragment size s (points)", fontsize=11, color=MUTED)
    if first: ax.set_ylabel(ylabel, fontsize=11, color=TEXT)

def make(kind, keys=None, suffix=""):
    keys = keys or rowkeys
    fig, axs = plt.subplots(1, len(keys), figsize=FIGSIZE if len(keys) > 1 else FIGSIZE_SINGLE, sharey=True, facecolor=BG, squeeze=False)
    for r, rk in enumerate(keys):
        ax = axs[0, r]
        for c in (0, 30, 60):
            s = np.sort(np.array(data[c][rk]["sizes"])); n = data[c][rk]["n_points"]
            if kind == "ccdf":
                x = np.unique(s); y = np.array([(s >= v).mean() for v in x])      # P(size >= x)
                ax.step(x, y, where="post", color=COLORS[c], lw=LW, label=f"HE_{c}")
                if MARKERS: ax.plot(x, y, "o", color=COLORS[c], ms=3)
            else:
                x = np.unique(s); y = np.array([s[s <= v].sum()/n for v in x])    # mass in fragments <= x
                ax.step(np.r_[0.8, x], np.r_[0, y], where="post", color=COLORS[c], lw=LW, label=f"HE_{c}")
        if kind == "ccdf": ax.set_yscale("log"); ax.set_ylim(2e-4, 1.3)
        else: ax.set_ylim(0, 1.03)
        style(ax, r, "fraction of fragments with size ≥ s" if kind=="ccdf" else "share of all points in fragments ≤ s", r == 0)
        ax.set_title(f"{TIME_LABEL[rk]}  (t = {data[0][rk]['t_us']:.0f} µs)", fontsize=12.5, color=TEXT, pad=8)
        if r == 0: ax.legend(frameon=False, fontsize=11, loc="upper right" if kind=="ccdf" else "center left")
    ttl = ("Fragment size distribution: fraction of fragments at least as large as s" if kind=="ccdf"
           else "Cumulative mass by fragment size: share of material in fragments no larger than s")
    sub = "4-point mesh, horizon 4.17 mm, 10% jitter + loading perturbation, 1.1× velocity"
    if len(keys) == 1:   # narrow figure: wrap the title
        fig.suptitle(ttl.replace(": ", ":\n") + "\n" + sub.replace(", 10%", ",\n10%"), fontsize=11.5, color=TEXT)
    else:
        fig.suptitle(ttl + "\n" + sub, fontsize=13, color=TEXT)
    fig.tight_layout(rect=(0, 0, 1, 0.90 if len(keys) == 1 else 0.91))
    out = (OUT_CCDF if kind == "ccdf" else OUT_MASS).replace(".png", suffix + ".png")
    fig.savefig(os.path.join(here, out), dpi=DPI, facecolor=BG); print("wrote", out)
make("ccdf"); make("mass")
# single-time versions
for kind in ("ccdf", "mass"):
    make(kind, ["0.667"], "_2of3")
    make(kind, ["1.000"], "_end")
