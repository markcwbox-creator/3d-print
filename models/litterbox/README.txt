FOLDABLE CAT LITTER BOX - print-in-place hinged walls
======================================================
Outer size 400 x 300 x 150 mm (deployed). Folded: four 200 x 150 x ~20 mm
tiles. Built from 4 floor tiles; each tile prints with its two walls already
hinged (print-in-place), standing upright exactly as exported.

ASSUMPTIONS (change in scripts/litterbox.py -> P, then re-run the build)
- Print bed >= 210 x 160 mm, Z >= 150 mm. (Largest part: 206 x 156 x 150.)
- Low entry: 140 mm wide, 70 mm sill, in the front wall (tile B_entry only).
- PLA/PETG, 0.4 mm nozzle, 0.2 mm layers. Clearances: 0.35-0.4 mm.
- NOT test-printed. Geometry is verified by code (see below), not by a real
  print. Expect to tune clearances (P['CV'], P['G']) for your printer.

PARTS TO PRINT
  module_A_print_x2.stl         x2   front-left and back-right tiles
  module_B_entry_print_x1.stl   x1   front-right tile (has the low entry)
  module_B_plain_print_x1.stl   x1   back-left tile (no entry)
  corner_clip_A_print_x2.stl    x2   corners FL, BR
  corner_clip_B_print_x2.stl    x2   corners FR, BL (mirror of A)
Each module STL contains 3 separate shells (floor tile + long wall + short
wall). Import as ONE object; do not let the slicer merge/"fix" them.

PRINT SETTINGS
- Print as exported (walls upright, clip opening down).
- NO supports. If your slicer adds any, add support blockers around hinges.
- Brim 5-8 mm on the floor tile (tall thin walls). Walls are solid 4 mm: 3+
  perimeters, 25%+ infill. Slow the first layers over the hinge gaps.
- Hinge gaps are 0.35-0.4 mm. After printing, flex each wall through its full
  90 deg range to break the layer bridges free.

ASSEMBLY (deployed)
1. Raise every wall to vertical; each hinge has a stop just past vertical.
2. Lay out the tiles: FL = A, FR = B_entry, BL = B_plain, BR = A rotated 180.
   Tiles drop together with dovetails (slide DOWN, not sideways).
3. Wall seams overlap in a half-thickness lap; corners hang together with the
   4 corner clips pushed down over the wall tops.

FOLD
1. Lift off the 4 corner clips.
2. Fold all four LONG (200 mm) walls inward flat first (lower hinge).
3. Then fold the four SHORT (150 mm) walls over them (higher hinge).
   Folded thickness ~20 mm. Fold the two walls on one side together (they
   share a hinge line and a lap seam).
4. Optionally pull the tiles apart and stack them.
Walls MUST fold in this order; the reverse order collides (by design the
short-wall hinge sits 8.8 mm higher so it clears the folded long wall).

WHAT IS VERIFIED (python3 scripts/litterbox_build.py, 45 checks)
- Deployed: every shell clears its neighbours by >= 0.35 mm. Folded: >= 0.25 mm.
  No overlaps in deployed or fully folded states.
- Continuous fold sweep 0..90 deg in 3-5 deg steps for every wall, in the
  documented order, with all four tiles present: zero collision volume.
- Hinge stops: no collision at -0.3 deg, collision at -4 deg.
- Corner clips clear the deployed walls; all STLs watertight.

KNOWN LIMITS
- Floor is not foldable; the tiles are rigid and dovetailed. "Foldable" =
  walls fold flat, tiles separate.
- Outward lean at the hinge stop is ~1.5 deg (the clips pull the top corners
  true). Litter pressure pushes walls into their stops, which is what holds
  them.
- Seam laps and tile joints are not sealed; fine clumping litter dust may
  escape through 0.4 mm seams. Line with a bag.
- 70 mm sill is low for a big cat to climb; raise ENTRY_SILL for 100+ mm.

FILES
  scripts/litterbox.py         geometry (manifold3d CSG; all dimensions in P)
  scripts/litterbox_verify.py  clearance + fold-sweep checks
  scripts/litterbox_build.py   verify, then export STLs (aborts on failure)
  scripts/litterbox_render.py  oblique sanity renders -> renders/
  Requires: pip install numpy trimesh manifold3d matplotlib
