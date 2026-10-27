"""ParaView (pvbatch) views of the deformed cylinders: half-cylinder cutaway, fragments only, and crack network.
Run:  /Applications/ParaView-6.2.0.app/Contents/bin/pvbatch figures/paraview_views.py <pressure|velocity> <time_us> [mode ...]
      modes (default: all):  half | fragments | cracks
Examples:
      pvbatch figures/paraview_views.py pressure 331
      pvbatch figures/paraview_views.py velocity 250 half cracks
Writes PNGs into figures/pressure_bc/ or figures/velocity_bc/ as paraview_<mode>_HE{0,30,60}_<time>us.png and a side-by-side
paraview_<mode>_<time>us.png (needs PIL/matplotlib's Pillow for the montage; skipped if unavailable).
  half       -- Clip with a plane through the cylinder axis (keeps y < 0), viewed from +y so you look into the cut wall.
                Points colored by Damage (accumulated D).
  fragments  -- Threshold: keeps only points with Broken_Bond_Volume_Averaged <= FRAG_MAX_B and Weighted_Volume > 0
                (drops the cracked/dust points), colored by Damage -> fragments show as islands separated by gaps.
  cracks     -- only points with broken-bond fraction >= CRACK_MIN_B, drawn dark on white: the fracture network.
Edit the STYLE block below to change colors, point size, thresholds, camera, background.
"""
import os, sys
from paraview.simple import *

# ---------------- STYLE (edit me) ----------------
COLORMAP     = "Cool to Warm"       # any ParaView colormap name; applied to Damage
DAMAGE_RANGE = (0.0, 1.0)
POINT_SIZE   = 4
BACKGROUND   = [1.0, 1.0, 1.0]
HIDE_DUST    = True                 # drop isolated points (Weighted_Volume == 0: no intact bonds) in the half and fragments views
FRAG_MAX_B   = 0.5                  # 'fragments': keep points with broken-bond fraction <= this
CRACK_MIN_B  = 0.9                  # 'cracks': keep points with broken-bond fraction >= this
CRACK_COLOR  = [0.1, 0.1, 0.1]
IMG_SIZE     = [900, 1000]
LEVELS       = (0, 30, 60)
# --------------------------------------------------

here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
case = sys.argv[1]; t_us = float(sys.argv[2]); modes = sys.argv[3:] or ["half", "fragments", "cracks"]
if case == "pressure":
    f = lambda c: f"{root}/imperfection_test/pressure_HE{c}_4pt/pipe4pt_HE{c}_press.e"; outdir = f"{here}/pressure_bc"
else:
    f = lambda c: f"{root}/imperfection_test/HE{c}_4pt_dsmall_jit10_load/fcyl4pt_HE{c}_dsmall_jit10_load.e"; outdir = f"{here}/velocity_bc"
tag = f"{t_us:.0f}us"

def load(c):
    r = ExodusIIReader(registrationName=f"HE{c}", FileName=[f(c)])
    r.ElementVariables = ["Damage", "Broken_Bond_Volume_Averaged", "Weighted_Volume"]
    r.PointVariables = ["Displacement"]; r.ApplyDisplacements = 1
    r.UpdatePipelineInformation(); ts = list(r.TimestepValues)
    return r, min(ts, key=lambda x: abs(x*1e6 - t_us))

def style_display(d, color_damage=True):
    d.SetRepresentationType("Points"); d.PointSize = POINT_SIZE; d.RenderPointsAsSpheres = 1
    if color_damage:
        ColorBy(d, ("CELLS", "Damage")); lut = GetColorTransferFunction("Damage"); lut.ApplyPreset(COLORMAP, True)
        lut.RescaleTransferFunction(*DAMAGE_RANGE); d.SetScalarBarVisibility(GetActiveView(), False)
    else:
        d.ColorArrayName = ["POINTS", ""]; d.AmbientColor = CRACK_COLOR; d.DiffuseColor = CRACK_COLOR

def thr(src, name, lo, hi):
    t = Threshold(Input=src); t.Scalars = ["CELLS", name]; t.LowerThreshold = lo; t.UpperThreshold = hi
    t.ThresholdMethod = "Between"; return t

written = {m: [] for m in modes}
for c in LEVELS:
    reader, tv = load(c)
    for mode in modes:
        view = CreateView("RenderView"); view.ViewSize = IMG_SIZE; view.UseColorPaletteForBackground = 0; view.Background = BACKGROUND; view.OrientationAxesVisibility = 0
        view.ViewTime = tv
        if mode == "half":
            base = thr(reader, "Weighted_Volume", 1e-12, 1e30) if HIDE_DUST else reader
            src = Clip(Input=base); src.ClipType = "Plane"; src.ClipType.Normal = [0, 1, 0]
            src.UpdatePipeline(tv); b = src.GetDataInformation().GetBounds(); src.ClipType.Origin = [0, 0, 0.5*(b[4]+b[5])]
        elif mode == "fragments":
            a = thr(reader, "Weighted_Volume", 1e-12, 1e30) if HIDE_DUST else reader; src = thr(a, "Broken_Bond_Volume_Averaged", -1.0, FRAG_MAX_B)
        elif mode == "cracks":
            src = thr(reader, "Broken_Bond_Volume_Averaged", CRACK_MIN_B, 1e30)
        d = Show(src, view); style_display(d, color_damage=(mode != "cracks"))
        view.ResetCamera(); src.UpdatePipeline(tv); b = src.GetDataInformation().GetBounds()
        cx, cy, cz = 0.5*(b[0]+b[1]), 0.5*(b[2]+b[3]), 0.5*(b[4]+b[5]); h = b[5]-b[4]; w = max(b[1]-b[0], b[3]-b[2])
        view.CameraFocalPoint = [cx, cy, cz]; view.CameraViewUp = [0, 0, 1]
        view.CameraPosition = [cx, cy + 3.0*max(h, w), cz] if mode == "half" else [cx, cy - 3.0*max(h, w), cz]
        view.CameraParallelProjection = 1; view.CameraParallelScale = 0.55*max(h, w*1.25)
        Render(view); out = f"{outdir}/paraview_{mode}_HE{c}_{tag}.png"
        SaveScreenshot(out, view, ImageResolution=IMG_SIZE); written[mode].append(out); print("wrote", out)
        Delete(d) if False else None
        Hide(src, view); Delete(view); del view

try:
    from PIL import Image, ImageDraw
    for mode, paths in written.items():
        ims = [Image.open(p) for p in paths]; W = sum(i.width for i in ims); H = ims[0].height + 60
        m = Image.new("RGB", (W, H), tuple(int(255*x) for x in BACKGROUND)); x = 0; dr = ImageDraw.Draw(m)
        for i, c in zip(ims, LEVELS):
            m.paste(i, (x, 60)); dr.text((x + i.width//2 - 20, 20), f"HE_{c}", fill=(0, 0, 0)); x += i.width
        m.save(f"{outdir}/paraview_{mode}_{tag}.png"); print("wrote montage", mode)
except Exception as e:
    print("montage skipped:", e)
