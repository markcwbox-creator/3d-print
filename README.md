# NASA X-59 QueSST 3D-Printable Mockup Family

Six stylized, print-ready mockups of NASA's X-59 QueSST (Quiet SuperSonic
Technology) experimental aircraft, generated procedurally with open-source
tooling. Every part is a validated, watertight solid, scaled and sized to
fit a standard 220 x 220 mm FDM print bed, and **every variant prints as
one unitary object in one print job** -- including the rotating one.

**These are stylized display mockups, not scale-accurate engineering
replicas.** The fuselage shape (slender pointed nose, raised cockpit
canopy, small nose canards, single swept dorsal tail fin, top-mounted
engine spine) is a recognizable likeness of the real X-59. The "central
pivot wing" variants (2-6) are a deliberate reinterpretation you asked
for -- a single straight wing bar through one central hub, similar in
spirit to NASA's AD-1 oblique-wing research aircraft -- which is not how
the real X-59's fixed delta wings work.

## Two ways to grab the files

- **`models/quesst_stl_only/`** -- just the six print files, one `.stl`
  per variant, nothing else. This is the "email it and go" folder.
- **`models/quesst/`** -- the full kit: `.obj` **and** `.stl` for every
  part, plus a separate accompanying display stand for each variant and
  the sanity-check renders. See the table below.

## What's in `models/quesst/`

| Folder | Contents | Description |
|---|---|---|
| `01_standard_swept_wing/` | 1 aircraft + 1 stand | Conventional-looking mockup: fixed, low-mounted swept delta wings, canards, single tail fin. **The "just send it to the printer" one.** |
| `02_pivot_rotating_wing/` | 1 aircraft + 1 stand | Rotating-wing version -- one STL, prints pre-assembled and already spins (see Mechanism below). |
| `03_fixed_0deg_perpendicular/` | 1 aircraft + 1 stand | Central wing bar fixed straight out, perpendicular to the fuselage (0°, conventional cross layout). |
| `04_fixed_90deg_parallel/` | 1 aircraft + 1 stand | Central wing bar fixed parallel to the fuselage (90° rotation). |
| `05_fixed_45deg_aft/` | 1 aircraft + 1 stand | Central wing bar fixed 45° swept aft. |
| `06_fixed_45deg_fwd/` | 1 aircraft + 1 stand | Central wing bar fixed 45° swept forward (mirror of #5). |
| `stands/` | 1 stand | The same universal stand file, standalone. |
| `renders/` | PNGs | Quick orthographic sanity-check renders of every part (top/side/front), plus a joint close-up for variant 2. |

Every variant folder also contains its own copy of `quesst_display_stand`
so each is a complete, self-contained "aircraft + stand" download -- the
stand is a **separate, accompanying part**, not fused to the model, exactly
as requested. It's the same cradle design in every folder since all
variants share the identical fuselage belly profile.

Every part in `models/quesst/` ships as both **`.obj`** and **`.stl`**,
generated in that order: the `.obj` is the direct export from the
modeling step, and the `.stl` is a straight format conversion of that
same `.obj` done by a second, independent open-source tool (see below) --
not regenerated from scratch. `models/quesst_stl_only/` just has the
`.stl` copies pulled out into one flat folder.

## Every variant is one unitary print

Variants 1 and 3-6 are single fused solids -- straightforward. Variant
2's wing has to move relative to the fuselage to spin, so it can never be
one continuous piece of plastic (if it were fused solid, it couldn't
rotate -- that's just mechanics, not a modeling limitation). What it
*can* be, and is, is **one STL, one print job**: the fuselage and the
wing rotor are two separate watertight shells positioned with tiny
(0.2-0.3 mm) clearance gaps and printed simultaneously in place, so the
model comes off the bed already assembled, captured, and free-spinning --
no separate cap, no post-print assembly, nothing to lose. See "Mechanism"
below for how it's captured.

## Scale

Fuselage length: 200 mm. Standard-wing variant wingspan: ~134 mm.
Oblique-wing-bar variants: 150 mm wing span, fuselage ~47-200 mm footprint
depending on sweep angle. Every part's bounding box is under 220 x 220 mm,
so each prints on one plate without splitting, on essentially any modern
desktop FDM printer.

## Open-source tooling used

- **Generation (`.obj`):** [numpy](https://numpy.org) (BSD) for math,
  [trimesh](https://trimesh.org) (MIT) for mesh construction/repair/export,
  and [manifold3d](https://github.com/elalish/manifold) (Apache-2.0) as the
  exact boolean-geometry engine trimesh calls for every union/difference
  (wing-to-fuselage fusion, socket/pocket cuts, etc).
- **Conversion (`.obj` -> `.stl`):** [Assimp](https://github.com/assimp/assimp)
  (Open Asset Import Library, BSD-3-Clause), via its `assimp export` CLI --
  a dedicated, independent OSS converter, not the same code path used to
  generate the mesh.
- Source: `scripts/geo.py`, `scripts/parts.py`, `scripts/build_all.py`
  (generation) and `scripts/render_check.py` (the sanity-check renders in
  `renders/`). Re-run `python3 scripts/build_all.py` to regenerate every
  `.obj` from scratch, then convert with e.g.
  `assimp export model.obj model.stl -f stlb`.

## Print settings (all variants)

- Material: PLA or PETG, 0.4 mm nozzle, 0.2 mm layer height.
- Infill: 15-20% is plenty for a display piece; go 30%+ on variant 2 if
  you want the pivot joint to feel more rigid.
- **Orientation:** print the aircraft belly-down (as exported) -- this is
  the natural "resting on its landing gear" orientation, and keeps the
  bulk of the model flat against the bed. The wings sit roughly level with
  the fuselage's mid-height and are elevated off the bed, and the swept
  tail fin overhangs backward at ~42-48°, so **turn on supports**
  ("everywhere"/"supports on build plate + model", not just "touching
  buildplate") for the wing undersides and fin. Tree/organic supports
  (Cura, PrusaSlicer, Bambu Studio) give the cleanest result and are
  easiest to remove.
- For variant 2, do **not** let your slicer auto-generate supports
  *inside* the pivot joint gaps (the small clearance around the hub and
  the belly boss) -- that would glue it solid. If your slicer offers a
  "support blocker" / exclusion zone, drop one over the turret and belly
  boss; otherwise it's usually fine as-is since the gaps are only
  0.2-0.3 mm and slicers rarely try to support gaps that thin.
- The stand needs no supports; print the groove face-up as exported.

## Mechanism: how the rotating wing (variant 2) is captured

The wing spins about a vertical axis at a raised hub ("turret") on the
fuselage spine, but it also needs to be trapped so it can't be pulled
back out -- and a stationary wall can't fully enclose that hub without
blocking the wing's own 360° sweep (any solid connecting the turret's
floor to a lid would eventually collide with the wing arm as it rotates
past). The fix: retention happens **below the fuselage**, not at the
hub.

- The wing rotor is one connected body: wing bar + hub disc (spins in an
  open-topped pocket in the turret) + a long shaft running down through
  the fuselage + a wider "mushroom head" flange at the very bottom.
- The fuselage has a small enclosed boss hanging under the belly, with a
  cavity sized for that flange (0.3 mm clearance) that's fully closed on
  top and bottom except for a narrow hole matching the shaft.
- Because the flange is wider than that hole, it can't pass back out --
  captured -- while the round pocket lets it spin freely. This works
  because nothing ever needs to sweep through that lower spot the way the
  wing arm sweeps through the turret, so a fully enclosing wall is
  possible there.
- If your printer's tolerances run tighter or looser than the 0.2-0.3 mm
  clearances baked in here and the joint prints fused or too loose,
  reprint variant 2 at 100.5-101% scale (or 99-99.5%) to dial in the fit
  -- normal for FDM press/rotating fits and varies by printer.

## Family layout notes

All six variants share one fuselage core (same nose, canopy, canards,
single tail fin) so they read as one consistent study, with only the wing
mount changing. Variant 1 is the one to send straight to a printer if you
just want "an X-59 mockup." Variants 2-6 are the oblique-wing sweep-angle
series you asked for, built around the same shared central pivot station.
