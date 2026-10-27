# fragmenting_cylinder/figures/pressure_bc

## Pressurized pipe (HE_30, first test)
Run: `../imperfection_test/pressure_HE30_4pt/` (`input.yaml`, merged result `pipe4pt_HE30_press.e`, 203 frames to 399 us; pressure ramps 0 -> 500 MPa linearly over 400 us).
Analysis scripts (run from that run directory): `analyze_pressure_timehistory.py`, `analyze_pressure_damage_map.py` -> `pressure_HE30_unrolled_damage.png`.
Caveat: the pressure body force stays on after the wall breaks, so results after ~330 us (t) are not physical.

## Pressurized pipe: plastic strain (HE_0, HE_30, HE_60 pressure runs)
`compute_pressure_eqps.py` (run from `imperfection_test/`; needs all three finished runs) -> `pressure_eqps.npz`;
`plot_pressure_eqps.py` -> `pressure_eqps_cdf_time.png` (CDF of plastic strain over all points, one curve per ~8 us from 225 us to 331 us, one panel per HE level)
and `pressure_eqps_at_failure.png` (CDF of the plastic strain each point had when its broken-bond fraction first exceeded 0.5 / 0.9).
Curves are cut at 331 us (CAP_US) because after that the pressure body force keeps pushing detached points. Style block at top of the plot script.

## Damage-level stacked bars (pressure BC)
`compute_damage_classes_pressure.py` (run from `imperfection_test/`) -> `damage_classes_pressure.json` (counts per damage class at 290/304/318/331 us for D = "Damage" and B = broken-bond fraction).
`plot_damage_classes_stacked_pressure.py` -> `damage_classes_stacked_pressure_331us.png`: one bar per HE level = 100% of points (whole cylinder),
split into 0-0.25 / 0.25-0.5 / 0.5-0.75 / 0.75-1.0 (top class open-ended: a few points have D slightly above 1). `TIME_US=318 ...` picks another saved time,
`VAR=B ...` uses the broken-bond fraction instead of D. Style block at top (class labels/colors, sizes).
Finding at 331 us: share of points with D > 0.5 is 99.8% / 94% / 51% for HE_0 / HE_30 / HE_60.

`plot_pressure_eqps.py` also writes `pressure_eqps_at_failure_B05.png`: the plastic-strain-at-failure figure with only the left panel (broken-bond fraction first > 0.5).

## Failure-onset time series (paper figure)
`compute_damage_timeseries_pressure.py` (run from `imperfection_test/`) -> `damage_timeseries_pressure.json` (every saved frame to 399 us: fraction of points with D > 0.5, D > 0.75, and B > 0.5 = "failed").
`plot_paper_damage_timeseries.py <out_stem>` -> line plot of fraction failed (B > 0.5) vs time, 270-331 us (`VAR=D_gt05` / `D_gt075` for damage thresholds). Style block at top; same colors as `plot_paper_eqps_failure.py`.
Onset (first frame with > 1% failed): HE_60 288 us, HE_30 310 us, HE_0 314 us. Note D > 0.5 does NOT give this ordering (HE_30 starts after HE_0), so B > 0.5 is the metric used.
