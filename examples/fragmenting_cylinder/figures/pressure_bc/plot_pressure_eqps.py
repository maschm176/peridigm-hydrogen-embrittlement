"""CDFs of plastic strain for the pressurized-pipe runs. Reads pressure_eqps.npz (compute_pressure_eqps.py).
Run:  python3 figures/pressure_bc/plot_pressure_eqps.py      Edit the STYLE block to restyle.
Writes:
  pressure_eqps_cdf_time.png     -- one panel per HE level; CDF of plastic strain over all points, one curve per time
                                    (light -> dark = 225 us ... end of run; ramp is quasi-static before ~225 us)
  pressure_eqps_at_failure.png   -- CDF over points of the plastic strain each point had when its broken-bond fraction
                                    first exceeded 0.5 (left) / 0.9 (right); one curve per HE level
"""
import numpy as np, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import cm

# ---------------- STYLE (edit me) ----------------
TIME_CMAP  = "Blues"                  # colormap for the time ramp in the first figure
COLORS     = {0:"#e8943a", 30:"#c8481f", 60:"#6e1d0a"}
BG, TEXT, MUTED, GRID = "#fcfaf8", "#2b2b2b", "#666666", "#e6e2dd"
XMAX       = 0.5                      # plastic-strain axis limit
YMAX_FAIL  = 0.5                      # y-axis top for the plastic-strain-at-failure figure (curves top out near 0.4)
LW         = 2.4
DPI        = 150
LEGEND_PAD = 62                      # space (points) between axes top and panel title, to fit the legend above the plot
CAP_US     = 331                      # draw curves up to this time only (after it the pressure acts on detached points)
# --------------------------------------------------

here = os.path.dirname(os.path.abspath(__file__)); Z = np.load(os.path.join(here, "pressure_eqps.npz"))
cdf = lambda v: (np.sort(v), np.arange(1, len(v)+1)/len(v))
def style(ax):
    ax.set_facecolor(BG)
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    for sp in ("left","bottom"): ax.spines[sp].set_color("#bbb")
    ax.tick_params(colors=MUTED); ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)

# ---- figure 1: CDF of plastic strain vs time, per concentration
fig, axs = plt.subplots(1, 3, figsize=(14, 4.8), sharex=True, sharey=True, facecolor=BG)
for ax, c in zip(axs, (0, 30, 60)):
    t = Z[f"HE{c}_t"]; E = Z[f"HE{c}_eqps"]; keep = [i for i in range(len(t)) if t[i] <= CAP_US]
    cols = cm.get_cmap(TIME_CMAP)(np.linspace(0.25, 1.0, len(keep)))
    for k, i in enumerate(keep):
        x, y = cdf(E[i]); ax.plot(x, y, color=cols[k], lw=1.8)
    ax.set_xlim(0, XMAX); ax.set_ylim(0, 1); style(ax); ax.set_title(f"HE_{c}", fontsize=14, color=TEXT)
    ax.set_xlabel("equivalent plastic strain", fontsize=11, color=MUTED)
axs[0].set_ylabel("fraction of points with plastic strain ≤ value", fontsize=11, color=TEXT)
sm = cm.ScalarMappable(cmap=TIME_CMAP, norm=plt.Normalize(Z["HE0_t"][0], min(CAP_US, Z["HE0_t"][-1])))
fig.colorbar(sm, ax=axs, label="time (µs)", fraction=0.025, pad=0.02)
fig.suptitle("Plastic strain distribution through the pressure ramp after the quasi-static stretch (pressure 280 → 410 MPa)\n4-point mesh, 10% jitter; curves every ~8 µs from 225 µs", fontsize=12.5, color=TEXT, y=1.06)
fig.savefig(os.path.join(here, "pressure_eqps_cdf_time.png"), dpi=DPI, facecolor=BG, bbox_inches="tight"); plt.close(fig)

# ---- figure 2: plastic strain at failure (two panels), and a left-panel-only version
FAIL_PANELS = (("fail05", "broken-bond fraction first > 0.5"), ("fail09", "broken-bond fraction first > 0.9"))
def failure_figure(panels, figsize, outname):
    fig, axs = plt.subplots(1, len(panels), figsize=figsize, sharey=True, facecolor=BG, squeeze=False); axs = axs[0]
    for ax, (key, lab) in zip(axs, panels):
        for c in (0, 30, 60):
            e = Z[f"HE{c}_{key}_eqps"]; tt = Z[f"HE{c}_{key}_t"]; ok = ~np.isnan(e) & (tt <= CAP_US)
            x, y = cdf(e[ok]); frac = ok.mean()
            ax.plot(x, y*frac, color=COLORS[c], lw=LW, label=f"HE_{c}  (median {np.median(e[ok]):.3f}; {frac*100:.0f}% of points by {CAP_US} µs)")
        ax.set_xlim(0, XMAX); ax.set_ylim(0, YMAX_FAIL); style(ax); ax.set_title(lab, fontsize=12, color=TEXT, pad=LEGEND_PAD)
        ax.set_xlabel("plastic strain at failure", fontsize=11, color=MUTED); ax.legend(frameon=False, fontsize=9.5, loc="lower left", bbox_to_anchor=(0.0, 1.0))   # legend sits above the axes, under the panel title
    axs[0].set_ylabel("fraction of all points that have failed\nwith plastic strain ≤ value", fontsize=11, color=TEXT)
    fig.suptitle(f"Plastic strain at failure, pressurized pipe (failures up to {CAP_US} µs)", fontsize=13, color=TEXT, y=1.13)
    fig.savefig(os.path.join(here, outname), dpi=DPI, facecolor=BG, bbox_inches="tight"); plt.close(fig)
failure_figure(FAIL_PANELS, (11, 4.8), "pressure_eqps_at_failure.png")
failure_figure(FAIL_PANELS[:1], (6.2, 4.8), "pressure_eqps_at_failure_B05.png")      # left panel only (broken-bond fraction first > 0.5)
for c in (0, 30, 60):
    for key in ("fail05", "fail09"):
        e = Z[f"HE{c}_{key}_eqps"]; tt = Z[f"HE{c}_{key}_t"]; ok = ~np.isnan(e) & (tt <= CAP_US)
        print(f"HE_{c} {key}: n={ok.sum()} eqps at failure p10/p50/p90 = {np.percentile(e[ok],[10,50,90]).round(3).tolist()}  median time {np.median(tt[ok]):.0f} us")
print("wrote figures")
