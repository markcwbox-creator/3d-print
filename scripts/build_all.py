"""
Generate the full X-59 QueSST 3D-printable mockup family:
  1. Standard fixed swept-wing mockup
  2. Central-pivot rotating oblique wing (3-part assembly)
  3-6. Fixed central oblique wing at 0 / 90 / +45 / -45 degrees
  + a display stand accompanying every variant

Exports .obj for every part (numpy + trimesh + manifold3d, all OSS),
then this script's caller (shell) converts each to .stl with assimp
(OSS, Open Asset Import Library) as a dedicated, independent converter.
"""
import os
import numpy as np
import trimesh

from geo import union, difference, check
from parts import (
    build_fuselage, fuselage_radius_at, wing_panel, fin_panel,
    oblique_wing_bar, oblique_shaft_peg, oblique_socket_hole,
    turret, turret_pocket, retaining_cap,
    L, PIVOT_X, TURRET_HEIGHT, TURRET_POCKET_DEPTH,
)

OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT, exist_ok=True)


def save_obj(mesh, path):
    mesh.export(path, file_type="obj")
    print(f"  wrote {path}  ({len(mesh.vertices)}v {len(mesh.faces)}f)")


def rotate_about_pivot_z(mesh, angle_deg, pivot_point):
    m = mesh.copy()
    Rm = trimesh.transformations.rotation_matrix(np.radians(angle_deg), [0, 0, 1], pivot_point)
    m.apply_transform(Rm)
    return m


# ---------------------------------------------------------------------------
# Shared dressed fuselage: core + canards + vertical tail
# ---------------------------------------------------------------------------
print("== fuselage core ==")
fuselage = build_fuselage()

# canard strakes near the nose (small, mirrored)
hw20, hh20, zc20 = fuselage_radius_at(0.205)
canard_L = wing_panel(root_chord=15, tip_chord=5, span=15, sweep_deg=58, thickness=1.8,
                       root_le_x=0.185 * L, root_y=hw20 * 0.97, mount_z=zc20, mirror=False)
canard_R = wing_panel(root_chord=15, tip_chord=5, span=15, sweep_deg=58, thickness=1.8,
                       root_le_x=0.185 * L, root_y=hw20 * 0.97, mount_z=zc20, mirror=True)

# single vertical tail fin, aft dorsal
hw78, hh78, zc78 = fuselage_radius_at(0.78)
fin_base_z = zc78 + hh78 - 1.0
fin = fin_panel(root_chord=32, tip_chord=11, height=30, sweep_deg=42, thickness=3.0,
                root_le_x=0.75 * L, mount_y=0.0, base_z=fin_base_z)

print("== union: dressed fuselage (core+canards+fin) ==")
fuselage_dressed = union([fuselage, canard_L, canard_R, fin], "fuselage_dressed")

# pivot-station top/bottom skin z (used by turret + wing mounting)
hwP, hhP, zcP = fuselage_radius_at(0.55)
top_z = zcP + hhP
bot_z = zcP - hhP
# The rotating/fixed oblique wing hub sits INSIDE the turret's pocket cavity
# (a dorsal, shoulder-mounted hub on top of the fuselage skin), not buried
# inside the solid fuselage body -- otherwise there'd be no clearance for
# it to spin. Center it mid-depth in the pocket, symmetric clearance top+bottom.
hub_z = top_z + TURRET_POCKET_DEPTH / 2.0


# ---------------------------------------------------------------------------
# Variant 1: standard fixed swept-wing mockup
# ---------------------------------------------------------------------------
print("\n== Variant 1: standard swept wing ==")
delta_L = wing_panel(root_chord=48, tip_chord=11, span=58, sweep_deg=52, thickness=3.2,
                      root_le_x=0.46 * L, root_y=hwP * 0.98, mount_z=zcP, mirror=False)
delta_R = wing_panel(root_chord=48, tip_chord=11, span=58, sweep_deg=52, thickness=3.2,
                      root_le_x=0.46 * L, root_y=hwP * 0.98, mount_z=zcP, mirror=True)
v1_standard = union([fuselage_dressed, delta_L, delta_R], "v1_standard")

d1 = os.path.join(OUT, "01_standard_swept_wing")
os.makedirs(d1, exist_ok=True)
save_obj(v1_standard, os.path.join(d1, "quesst_standard_swept.obj"))


# ---------------------------------------------------------------------------
# Fuselage-with-turret, shared by the pivot + 4 fixed oblique variants
# ---------------------------------------------------------------------------
print("\n== fuselage + turret (shared by oblique variants) ==")
turret_solid = turret(PIVOT_X, top_z)
fuselage_turreted = union([fuselage_dressed, turret_solid], "fuselage_turreted")


# ---------------------------------------------------------------------------
# Variant 2: pivoting oblique wing -- 3-part assembly
# ---------------------------------------------------------------------------
print("\n== Variant 2: pivoting oblique wing (3 parts) ==")
pocket = turret_pocket(PIVOT_X, top_z)
socket_hole = oblique_socket_hole(PIVOT_X, hub_z, top_z + TURRET_HEIGHT, bot_z)
pivot_fuselage = difference(fuselage_turreted, [pocket, socket_hole], "pivot_fuselage")

wing_bar_local = oblique_wing_bar(center_x=PIVOT_X, center_z=hub_z)
shaft = oblique_shaft_peg(PIVOT_X, hub_z, bot_z)
pivot_wing_rotor = union([wing_bar_local, shaft], "pivot_wing_rotor")

pivot_cap = retaining_cap()

d2 = os.path.join(OUT, "02_pivot_rotating_wing")
os.makedirs(d2, exist_ok=True)
save_obj(pivot_fuselage, os.path.join(d2, "quesst_pivot_A_fuselage.obj"))
save_obj(pivot_wing_rotor, os.path.join(d2, "quesst_pivot_B_wing_rotor.obj"))
save_obj(pivot_cap, os.path.join(d2, "quesst_pivot_C_retaining_cap.obj"))


# ---------------------------------------------------------------------------
# Variants 3-6: fixed oblique wing at 0 / 90 / +45 / -45 degrees
# ---------------------------------------------------------------------------
print("\n== Variants 3-6: fixed oblique sweep angles ==")
FIXED_ANGLES = [
    ("03_fixed_0deg_perpendicular", 0, "perpendicular (straight, in line across the body)"),
    ("04_fixed_90deg_parallel", 90, "parallel to the fuselage"),
    ("05_fixed_45deg_aft", 45, "45 degrees swept aft"),
    ("06_fixed_45deg_fwd", -45, "45 degrees swept forward"),
]
pivot_point = np.array([PIVOT_X, 0.0, hub_z])
for dirname, angle, desc in FIXED_ANGLES:
    print(f"-- {dirname}: {desc} --")
    bar = oblique_wing_bar(center_x=PIVOT_X, center_z=hub_z)
    bar_rot = rotate_about_pivot_z(bar, angle, pivot_point)
    v = union([fuselage_turreted, bar_rot], dirname)
    d = os.path.join(OUT, dirname)
    os.makedirs(d, exist_ok=True)
    save_obj(v, os.path.join(d, f"quesst_{dirname}.obj"))


# ---------------------------------------------------------------------------
# Display stand (universal cradle, fits all variants -- same fuselage belly)
# ---------------------------------------------------------------------------
print("\n== Display stand ==")


def build_stand():
    # cradle groove: subtract a horizontal half-cylinder from a block
    groove_r = 10.5
    block_len, block_w, block_h = 70.0, 34.0, 20.0
    block = trimesh.creation.box(extents=(block_len, block_w, block_h))
    block.apply_translation((0, 0, block_h / 2.0))

    cyl = trimesh.creation.cylinder(radius=groove_r, height=block_len + 4, sections=48)
    Rm = trimesh.transformations.rotation_matrix(np.radians(90), [0, 1, 0])
    cyl.apply_transform(Rm)
    cyl.apply_translation((0, 0, block_h - groove_r + 3.0))

    cradle = difference(block, cyl, "stand_cradle")

    # wide flared base for tip-over stability
    base = trimesh.creation.box(extents=(block_len + 20, block_w + 24, 5.0))
    base.apply_translation((0, 0, 2.5))

    stand = union([cradle, base], "stand_universal")
    stand.apply_translation((0, 0, 0))
    # sit flat on Z=0
    stand.apply_translation((0, 0, -stand.bounds[0][2]))
    return stand


stand = build_stand()
stand_dir = os.path.join(OUT, "stands")
os.makedirs(stand_dir, exist_ok=True)
save_obj(stand, os.path.join(stand_dir, "stand_universal.obj"))

# Provide a per-variant-named copy of the same stand file for convenience,
# since every variant shares the identical fuselage belly profile.
variant_dirs = [
    "01_standard_swept_wing", "02_pivot_rotating_wing",
    "03_fixed_0deg_perpendicular", "04_fixed_90deg_parallel",
    "05_fixed_45deg_aft", "06_fixed_45deg_fwd",
]
for vd in variant_dirs:
    d = os.path.join(OUT, vd)
    os.makedirs(d, exist_ok=True)
    save_obj(stand, os.path.join(d, "quesst_display_stand.obj"))

print("\nALL DONE")
