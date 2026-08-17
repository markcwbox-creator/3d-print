# NASA X-59 QueSST 3D-Printable Mockup Family

Six stylized, print-ready mockups of NASA's X-59 QueSST (Quiet SuperSonic
Technology) experimental aircraft, generated procedurally with open-source
tooling. Every part is a validated, watertight solid, scaled and sized to
fit a standard 220 x 220 mm FDM print bed.

**These are stylized display mockups, not scale-accurate engineering
replicas.** The fuselage shape (slender pointed nose, raised cockpit
canopy, small nose canards, single swept dorsal tail fin, top-mounted
engine spine) is a recognizable likeness of the real X-59. The "central
pivot wing" variants (2-6) are a deliberate reinterpretation you asked
for -- a single straight wing bar through one central hub, similar in
spirit to NASA's AD-1 oblique-wing research aircraft -- which is not how
the real X-59's fixed delta wings work.

## What's in `models/quesst/`

| Folder | Contents | Description |
|---|---|---|
| `01_standard_swept_wing/` | 1 aircraft + 1 stand | Conventional-looking mockup: fixed, low-mounted swept delta wings, canards, single tail fin. **This is the "just send it to the printer" one.** |
| `02_pivot_rotating_wing/` | 3 parts (A/B/C) + 1 stand | Working rotating-wing assembly (see Assembly below). |
| `03_fixed_0deg_perpendicular/` | 1 aircraft + 1 stand | Central wing bar fixed straight out, perpendicular to the fuselage (0°, conventional cross layout). |
| `04_fixed_90deg_parallel/` | 1 aircraft + 1 stand | Central wing bar fixed parallel to the fuselage (90° rotation). |
| `05_fixed_45deg_aft/` | 1 aircraft + 1 stand | Central wing bar fixed 45° swept aft. |
| `06_fixed_45deg_fwd/` | 1 aircraft + 1 stand | Central wing bar fixed 45° swept forward (mirror of #5). |
| `stands/` | 1 stand | The same universal stand file, standalone. |
| `renders/` | PNGs | Quick orthographic sanity-check renders of every part (top/side/front). |

Every variant folder also contains its own copy of `quesst_display_stand`
so each is a complete, self-contained "aircraft + stand" download -- the
stand is a **separate, accompanying part**, not fused to the model, exactly
as requested. It's the same cradle design in every folder since all
variants share the identical fuselage belly profile.

Every part ships as both **`.obj`** and **`.stl`**, generated in that
order: the `.obj` is the direct export from the modeling step, and the
`.stl` is a straight format conversion of that same `.obj` done by a
second, independent open-source tool (see below) -- not regenerated from
scratch.

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
- Infill: 15-20% is plenty for a display piece; go 30%+ on the fuselage
  parts of variant 2 if you want the pivot socket to feel more rigid.
- **Orientation:** print the aircraft belly-down (as exported) -- this is
  the natural "resting on its landing gear" orientation, and keeps the
  bulk of the model flat against the bed. The wings sit roughly level with
  the fuselage's mid-height and are elevated off the bed, and the swept
  tail fin overhangs backward at ~42-48°, so **turn on supports**
  ("everywhere"/"supports on build plate + model", not just "touching
  buildplate") for the wing undersides and fin. Tree/organic supports
  (Cura, PrusaSlicer, Bambu Studio) give the cleanest result and are
  easiest to remove.
- The `..._pivot_B_wing_rotor` part should be reoriented in your slicer so
  the flat wing panel lies down on the bed and the round shaft peg points
  straight **up** (rotate 180° from how it's exported) -- that way the peg
  prints as a short self-supporting post instead of hanging in mid-air.
  Everything else prints fine in its as-exported orientation.
- The stand needs no supports; print the groove face-up as exported.

## Assembly: the rotating pivot wing (variant 2)

Three separate prints, dry-fit (no glue) so it actually spins:

1. **`quesst_pivot_A_fuselage`** -- fuselage with a raised dorsal turret at
   the wing station. The turret has a shallow circular pocket (13 mm
   pocket, 4.6 mm deep) plus a 9.2 mm-diameter hole straight through the
   turret and fuselage down to the belly.
2. **`quesst_pivot_B_wing_rotor`** -- the single wing bar with an integral
   9.3 mm hub disc and an 8.6 mm-diameter shaft peg hanging off the hub's
   underside. Drop the peg down through part A's hole from the top; the
   hub disc seats in the shallow pocket and should spin freely (there's a
   0.2-0.3 mm design clearance both radially and in pocket depth). The
   shaft protrudes ~6 mm below the fuselage belly.
3. **`quesst_pivot_C_retaining_cap`** -- a small washer-like disc with a
   center hole sized ~0.1 mm undersized for a light interference/press fit
   onto the protruding peg tip. Press it on by hand once the wing is
   seated; it stops the wing from pulling back out while the assembly
   still rotates freely against the fuselage. Add a drop of glue only if
   you want it permanent -- left dry, it's field-serviceable.

If your printer's tolerances run tighter or looser than the ~0.2-0.3 mm
clearances baked in here, ream the pocket/hole lightly with a drill bit or
reprint the rotor at 100.5-101% scale (or 99-99.5%) to dial in the fit --
this is normal for FDM press/rotating fits and varies by printer.

## Family layout notes

All six variants share one fuselage core (same nose, canopy, canards,
single tail fin) so they read as one consistent study, with only the wing
mount changing. Variant 1 is the one to send straight to a printer if you
just want "an X-59 mockup." Variants 2-6 are the oblique-wing sweep-angle
series you asked for, built around the same shared central pivot station.
