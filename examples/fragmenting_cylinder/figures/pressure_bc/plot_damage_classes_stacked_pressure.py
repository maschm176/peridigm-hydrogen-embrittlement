"""Stacked bars for the pressurized-pipe runs: each bar is 100% of the points (whole cylinder, all heights), split into
four damage classes (same layout as the fragment-size stacked figure in velocity_bc).
Run:  python3 figures/pressure_bc/plot_damage_classes_stacked_pressure.py              -> t = 331 us
      TIME_US=318 python3 figures/pressure_bc/plot_damage_classes_stacked_pressure.py  -> another saved time (290, 304, 318, 331)
      VAR=B python3 ...                                                                 -> broken-bond fraction instead of accumulated damage D
Reads damage_classes_pressure.json (compute_damage_classes_pressure.py). Edit the STYLE block to restyle.
Writes damage_classes_stacked_pressure_<time>us.png  (VAR=B: damage_classes_stacked_pressure_B_<time>us.png)
Note: after ~331 us the pressure body force keeps pushing detached points, so later frames are not physical.
"""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- STYLE (edit me) ----------------
CLASS_LABELS = ["0–0.25", "0.25–0.50", "0.50–0.75", "0.75–1.0"]      # must match EDGES in the compute script
CLASS_COLORS = ["#fdd0a2", "#fd8d3c", "#d94801", "#7f2704"]          # low -> high damage
MIN_LABEL_PCT = 3.5
BG, TEXT, MUTED = "#fcfaf8", "#2b2b2b", "#666666"
FIGSIZE, DPI = (6.6, 5.6), 150
# --------------------------------------------------

here = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(here, "damage_classes_pressure.json")))
tkey = os.environ.get("TIME_US", "331"); var = os.environ.get("VAR", "D")
vname = {"D": "accumulated damage D", "B": "broken-bond fraction"}[var]
fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BG); ax.set_facecolor(BG)
for xi, c in enumerate((0, 30, 60)):
    rec = data[str(c)][tkey]; n = rec["n_points"]; bottom = 0
    for k, cnt in enumerate(rec[var + "_counts"]):
        v = 100 * cnt / n
        ax.bar(xi, v, bottom=bottom, width=0.62, color=CLASS_COLORS[k], edgecolor=BG, lw=1.5, label=CLASS_LABELS[k] if xi == 0 else None)
        if v >= MIN_LABEL_PCT:
            ax.text(xi, bottom + v/2, f"{v:.0f}%", ha="center", va="center", fontsize=10.5, fontweight="bold", color="white" if k >= 2 else TEXT)
        bottom += v
ax.set_xticks(range(3)); ax.set_xticklabels(["HE_0", "HE_30", "HE_60"], fontsize=12.5, color=TEXT)
ax.set_ylim(0, 100); ax.set_ylabel("% of all points", fontsize=11.5, color=TEXT)
ax.set_title(f"t = {data['0'][tkey]['t_us']:.0f} µs  (pressure ≈ {data['0'][tkey]['pressure_MPa']:.0f} MPa)", fontsize=12, color=TEXT, pad=10)
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
for sp in ("left", "bottom"): ax.spines[sp].set_color("#bbb")
ax.tick_params(colors=MUTED, length=0, axis="x")
h, l = ax.get_legend_handles_labels()
fig.legend(h[::-1], l[::-1], title="damage level", loc="center right", frameon=False, fontsize=10.5, title_fontsize=10)
fig.suptitle(f"Pressurized pipe: share of points by {vname}\n4-point mesh, horizon 4.17 mm,\n10% jitter, pressure ramp 0 → 500 MPa over 400 µs", fontsize=11.5, color=TEXT)
fig.tight_layout(rect=(0, 0, 0.76, 0.90))
out = f"damage_classes_stacked_pressure{'_B' if var == 'B' else ''}_{tkey}us.png"
fig.savefig(os.path.join(here, out), dpi=DPI, facecolor=BG); print("wrote", out)
