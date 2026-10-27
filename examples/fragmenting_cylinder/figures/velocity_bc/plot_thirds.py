"""Draw the thirds cylinder figure from dsmall_thirds_data.json.
Run from anywhere:  python3 figures/velocity_bc/plot_thirds.py
Edit the STYLE block below to change colors, sizes, labels, title -- no need to
recompute the data (that is compute_thirds_data.py).
"""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse
from matplotlib import cm, colors

# ---------------- STYLE (edit me) ----------------
CMAP        = "Oranges"      # any matplotlib colormap name, e.g. "viridis", "Blues", "magma_r"
VMIN, VMAX  = 0.0, 1.0       # colorbar range
BG          = "#fcfaf8"      # figure background
TEXT        = "#2b2b2b"      # main text color
MUTED       = "#666666"      # side labels / captions
LIGHT_TEXT_ABOVE = 0.55      # cells darker than this get white numbers
FIGSIZE     = (9.2, 6.4)
DPI         = 150
CYL_X       = {0: 2.0, 30: 5.0, 60: 8.0}   # horizontal position of each cylinder
CYL_W       = 1.6            # cylinder width
ELLIPSE_H   = 0.32           # height of the top/bottom ellipse (perspective)
GAP         = 0.03           # white gap between thirds
NUM_FONT    = 19             # numbers in cells
LABEL_FONT  = 17             # HE_xx titles
TITLE_FONT  = 13.5
SHOW_WHOLE  = True           # print whole-cylinder mean under each cylinder
TITLE       = ("Mean broken-bond fraction by third of cylinder height\n"
               "4-point mesh, horizon 4.17 mm, 10% jitter + loading perturbation, "
               "1.1\u00d7 velocity, final frame (t = {t:.0f} \u00b5s)")
OUT         = "broken_fraction_thirds_dsmall_jit10.png"
# --------------------------------------------------

here = os.path.dirname(os.path.abspath(__file__))
res = {int(k): v for k, v in json.load(open(os.path.join(here, "dsmall_thirds_data.json"))).items()}
cmap = plt.get_cmap(CMAP); norm = colors.Normalize(VMIN, VMAX)
H = 1.0
fig, ax = plt.subplots(figsize=FIGSIZE, facecolor=BG); ax.set_facecolor(BG)
for c, x in CYL_X.items():
    vals = res[c]["thirds"]            # bottom, middle, top
    for i, v in enumerate(vals):
        ax.add_patch(Rectangle((x-CYL_W/2, i*H+GAP/2), CYL_W, H-GAP, color=cmap(norm(v)), lw=0))
        ax.text(x, i*H+H/2, f"{v:.2f}", ha="center", va="center", fontsize=NUM_FONT,
                fontweight="bold", color="white" if v > LIGHT_TEXT_ABOVE else TEXT)
    ax.add_patch(Ellipse((x, 3*H), CYL_W, ELLIPSE_H, color=cmap(norm(vals[2])), lw=0))
    ax.add_patch(Ellipse((x, 3*H), CYL_W, ELLIPSE_H, fill=False, ec="white", lw=2.5))
    ax.add_patch(Ellipse((x, 0), CYL_W, ELLIPSE_H, color=cmap(norm(vals[0])), lw=0, clip_on=False))
    ax.text(x, 3.55, f"HE_{c}", ha="center", fontsize=LABEL_FONT, color=TEXT)
    if SHOW_WHOLE:
        ax.text(x, -0.62, f"whole cylinder\n{res[c]['whole']:.2f}", ha="center", va="center", fontsize=12, color="#555")
for i, l in enumerate(["Bottom third\n0\u20133.33 cm", "Middle third\n3.33\u20136.67 cm", "Top third\n6.67\u201310 cm"]):
    ax.text(0.7, i*H+H/2, l, ha="right", va="center", fontsize=12.5, color=MUTED)
ax.set_xlim(-0.8, 11.2); ax.set_ylim(-0.75, 3.95); ax.axis("off")
cb = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax, fraction=0.03, pad=0.01)
cb.set_label("Mean broken-bond fraction", fontsize=12); cb.outline.set_visible(False)
fig.suptitle(TITLE.format(t=res[0]["t"]), fontsize=TITLE_FONT, color=TEXT)
fig.savefig(os.path.join(here, OUT), dpi=DPI, bbox_inches="tight", facecolor=fig.get_facecolor())
print("wrote", os.path.join(here, OUT))
