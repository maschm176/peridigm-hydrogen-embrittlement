# fragmenting_cylinder/figures

| Folder | Contents |
|---|---|
| `velocity_bc/` | Figures/scripts/data for the Initial Velocity (impact-style) cylinder runs: broken-fraction-by-thirds cylinder, fragment-size histograms / CDFs / mass-stacked bars. `earlier_runs/` holds older figures. See its README. |
| `pressure_bc/` | Figures/scripts/data for the internally pressurized pipe runs (HE_0/30/60): damage map, plastic strain CDFs. See its README. |

Pattern in both: a `compute_*` / `analyze_*` script reads the .e result files and writes a data file (slow); a `plot_*` script reads that data and has a STYLE block at the top for colors/fonts/labels (fast).

## ParaView views (both BC types)
`paraview_views.py` (run with `/Applications/ParaView-6.2.0.app/Contents/bin/pvbatch figures/paraview_views.py <pressure|velocity> <time_us> [half|fragments|cracks]`)
writes `paraview_{half,fragments,cracks}_HE{0,30,60}_<t>us.png` plus a side-by-side `paraview_<mode>_<t>us.png` into `pressure_bc/` or `velocity_bc/`.
half = clip through the axis (looking into the cut wall); fragments = only points with broken-bond fraction <= 0.5 (cracks show as gaps);
cracks = only points with broken-bond fraction >= 0.9. STYLE block at top (colormap, point size, thresholds, background, HIDE_DUST).
Pressure views at 331 us are in `pressure_bc/`. NOTE: the detached rows of points above/below the pressure pipes are the end layers torn off by the end-cap body force (see notes in chat 2026-10-22).
