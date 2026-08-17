"""
Aircraft sub-part builders for the X-59 QueSST mockup family.
"""
import numpy as np
import trimesh
from geo import loft, ellipse_ring, point3, biconvex_quad, check

MM = 1.0  # base unit is mm throughout

# ---------------------------------------------------------------------------
# Global scale / station parameters
# ---------------------------------------------------------------------------
L = 200.0 * MM              # overall fuselage length
PIVOT_X = 0.55 * L          # central-wing / pivot station (x from nose)

# Fuselage station table: (x_frac, half_width(Y), half_height(Z), z_center)
# values are fractions of L except z_center also a fraction of L
FUSELAGE_STATIONS = [
    (0.000, 0.0000, 0.0000, 0.000),
    (0.015, 0.0060, 0.0060, 0.000),
    (0.05,  0.0155, 0.0140, 0.001),
    (0.12,  0.0300, 0.0270, 0.002),
    (0.18,  0.0400, 0.0360, 0.004),
    (0.24,  0.0460, 0.0480, 0.008),   # canopy hump start (extra height)
    (0.30,  0.0480, 0.0500, 0.009),   # canopy hump peak
    (0.36,  0.0470, 0.0430, 0.006),   # canopy hump end
    (0.45,  0.0470, 0.0400, 0.003),
    (0.55,  0.0470, 0.0390, 0.002),   # max/parallel section -- wing station
    (0.65,  0.0450, 0.0380, 0.001),
    (0.75,  0.0400, 0.0340, 0.000),
    (0.83,  0.0330, 0.0280, -0.001),
    (0.90,  0.0230, 0.0190, -0.002),
    (0.96,  0.0110, 0.0090, -0.002),
    (1.000, 0.0000, 0.0000, -0.002),
]


def build_fuselage(n_theta=32):
    sections = []
    for (xf, hw, hh, zc) in FUSELAGE_STATIONS:
        x = xf * L
        ry = hw * L
        rz = hh * L
        cz = zc * L
        if ry < 1e-6 and rz < 1e-6:
            sections.append(point3(x, 0.0, cz))
        else:
            sections.append(ellipse_ring(x, 0.0, cz, ry, rz, n=n_theta))
    mesh = loft(sections)
    check(mesh, "fuselage_core")
    return mesh


def fuselage_radius_at(xf):
    """Interpolate half-width/half-height/z-center at a given x fraction."""
    xs = [s[0] for s in FUSELAGE_STATIONS]
    hw = np.interp(xf, xs, [s[1] for s in FUSELAGE_STATIONS]) * L
    hh = np.interp(xf, xs, [s[2] for s in FUSELAGE_STATIONS]) * L
    zc = np.interp(xf, xs, [s[3] for s in FUSELAGE_STATIONS]) * L
    return hw, hh, zc


# ---------------------------------------------------------------------------
# Wing / fin panel builder (spanwise loft of a biconvex diamond section)
# ---------------------------------------------------------------------------

def wing_panel(root_chord, tip_chord, span, sweep_deg, thickness,
               root_le_x, root_y, mount_z, mirror=False, le_bulge=0.35):
    """A single tapered, swept wing panel spanning +Y from root_y."""
    sweep = np.radians(sweep_deg)

    def section(y_local, chord):
        le_x = root_le_x + y_local * np.tan(sweep)
        pts2d = biconvex_quad(chord, thickness, le_bulge)
        xs = le_x + pts2d[:, 0]
        zs = mount_z + pts2d[:, 1]
        ys = np.full(len(xs), root_y + y_local)
        return np.stack([xs, ys, zs], axis=1)

    root = section(0.0, root_chord)
    tip = section(span, tip_chord)
    m = loft([root, tip], cap_start=True, cap_end=True)
    if mirror:
        T = np.diag([1.0, -1.0, 1.0, 1.0])
        m.apply_transform(T)
        trimesh.repair.fix_normals(m, multibody=False)
        if m.volume < 0:
            m.invert()
    check(m, f"wing_panel(mirror={mirror})")
    return m


def fin_panel(root_chord, tip_chord, height, sweep_deg, thickness,
              root_le_x, mount_y, base_z, le_bulge=0.35):
    """A single vertical fin panel spanning +Z from base_z."""
    sweep = np.radians(sweep_deg)

    def section(z_local, chord):
        le_x = root_le_x + z_local * np.tan(sweep)
        pts2d = biconvex_quad(chord, thickness, le_bulge)
        xs = le_x + pts2d[:, 0]
        ys = mount_y + pts2d[:, 1]
        zs = np.full(len(xs), base_z + z_local)
        return np.stack([xs, ys, zs], axis=1)

    root = section(0.0, root_chord)
    tip = section(height, tip_chord)
    m = loft([root, tip], cap_start=True, cap_end=True)
    check(m, "fin_panel")
    return m


# ---------------------------------------------------------------------------
# Oblique bar wing (single continuous straight wing through a central hub)
# ---------------------------------------------------------------------------

OBLIQUE_HALF_SPAN = 75.0 * MM     # each side, total span 150mm
OBLIQUE_CHORD = 18.0 * MM
OBLIQUE_THK = 4.0 * MM
HUB_RADIUS = 9.3 * MM             # central rotor-hub disc radius (fits turret pocket)
HUB_THK = OBLIQUE_THK             # hub is flush with wing thickness

TURRET_OUTER_R = 11.0 * MM
TURRET_HEIGHT = 6.0 * MM
TURRET_POCKET_R = 9.5 * MM
TURRET_POCKET_DEPTH = OBLIQUE_THK + 0.6 * MM
SHAFT_RADIUS = 4.3 * MM
SOCKET_RADIUS = 4.6 * MM


def oblique_wing_bar(center_x, center_z, n_arc=24):
    """Build the straight constant-chord biconvex bar wing with an
    integrated circular hub in the middle, centered at local origin
    (span along local +/-Y, to be rotated later about Z through the hub
    center and translated to (center_x, 0, center_z))."""
    half = OBLIQUE_HALF_SPAN
    chord = OBLIQUE_CHORD
    thk = OBLIQUE_THK

    def section(y):
        pts2d = biconvex_quad(chord, thk, le_bulge=0.5)
        xs = -chord / 2.0 + pts2d[:, 0]  # center chord on x=0
        zs = pts2d[:, 1]
        ys = np.full(len(xs), y)
        return np.stack([xs, ys, zs], axis=1)

    # Panels overlap 1mm past the hub center on the far side, and the hub
    # cylinder radius is chosen to fully swallow the chord width (18mm
    # half-chord=9mm < HUB_RADIUS=9.3mm) near y=0, so all three solids
    # overlap generously -- no coincident/degenerate boundary faces for
    # the boolean union.
    overlap = 1.0
    left_tip = section(-half)
    left_root = section(overlap)
    right_root = section(-overlap)
    right_tip = section(half)
    left = loft([left_tip, left_root], cap_start=True, cap_end=True)
    right = loft([right_root, right_tip], cap_start=True, cap_end=True)

    # circular hub disc (cylinder) bridging the two panel roots; its flat
    # faces are the top/bottom of the wing (thickness dir = Z), round
    # profile in the XY plane -- that's the trimesh cylinder default.
    hub = trimesh.creation.cylinder(radius=HUB_RADIUS, height=HUB_THK, sections=n_arc)
    hub.apply_translation((0, 0, 0))
    bar = trimesh.boolean.union([left, right, hub], engine="manifold")
    bar.merge_vertices()
    trimesh.repair.fix_normals(bar, multibody=False)
    check(bar, "oblique_wing_bar (local)")

    bar.apply_translation((center_x, 0, center_z))
    return bar


def oblique_shaft_peg(center_x, center_z, fuselage_bottom_z, radius=SHAFT_RADIUS, protrusion=6.0):
    """Vertical cylindrical peg from the hub center down through the
    fuselage belly, protruding below for the retaining cap."""
    top_z = center_z + HUB_THK / 2.0 + 0.5
    bottom_z = fuselage_bottom_z - protrusion
    height = top_z - bottom_z
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    cyl.apply_translation((center_x, 0, (top_z + bottom_z) / 2.0))
    check(cyl, "oblique_shaft_peg")
    return cyl


def oblique_socket_hole(center_x, center_z, fuselage_top_z, fuselage_bottom_z,
                         radius=SOCKET_RADIUS, extra=2.0):
    top_z = fuselage_top_z + extra
    bottom_z = fuselage_bottom_z - extra
    height = top_z - bottom_z
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    cyl.apply_translation((center_x, 0, (top_z + bottom_z) / 2.0))
    check(cyl, "oblique_socket_hole")
    return cyl


def turret(center_x, center_z, outer_r=TURRET_OUTER_R, height=TURRET_HEIGHT, sections=48):
    cyl = trimesh.creation.cylinder(radius=outer_r, height=height, sections=sections)
    cyl.apply_translation((center_x, 0, center_z + height / 2.0))
    check(cyl, "turret")
    return cyl


def turret_pocket(center_x, center_z, pocket_r=TURRET_POCKET_R, depth=TURRET_POCKET_DEPTH, sections=48):
    cyl = trimesh.creation.cylinder(radius=pocket_r, height=depth, sections=sections)
    cyl.apply_translation((center_x, 0, center_z + depth / 2.0))
    check(cyl, "turret_pocket")
    return cyl


def retaining_cap(radius=8.0, thickness=3.0, hole_radius=SHAFT_RADIUS - 0.05, sections=32):
    disc = trimesh.creation.cylinder(radius=radius, height=thickness, sections=sections)
    hole = trimesh.creation.cylinder(radius=hole_radius, height=thickness + 2.0, sections=32)
    m = trimesh.boolean.difference([disc, hole], engine="manifold")
    m.merge_vertices()
    trimesh.repair.fix_normals(m, multibody=False)
    check(m, "retaining_cap")
    return m


# ---------------------------------------------------------------------------
# Print-in-place captured joint: a hidden mushroom-head flange trapped
# inside a fully-enclosed pocket in a small boss under the fuselage belly.
# Printed simultaneously with 0.3mm clearance gaps -- no post-print
# assembly, nothing to lose, still spins freely. Retention happens ONLY
# at this bottom boss (below the belly, where no wing arm ever sweeps),
# not at the top turret -- a full 360-degree external wing can't be
# captured by a continuous stationary wall at its OWN height without
# blocking its own rotation, but the shaft naturally clears that
# constraint on its way down to the belly.
# ---------------------------------------------------------------------------
BOSS_OUTER_R = 11.0 * MM          # matches TURRET_OUTER_R -- enough radius
                                    # margin over the fuselage's local half
                                    # width (~9.4mm) for a clean, robust
                                    # boolean union (a near-zero margin here
                                    # produced a non-manifold union in testing)
BOSS_FLOOR = 1.0 * MM
BOSS_CEIL = 1.0 * MM
FLANGE_R = 6.0 * MM
FLANGE_POCKET_R = 6.3 * MM
FLANGE_THK = 2.0 * MM
FLANGE_CLEARANCE = 0.3 * MM
BOSS_CAVITY_H = FLANGE_THK + 2 * FLANGE_CLEARANCE
BOSS_HEIGHT = BOSS_FLOOR + BOSS_CAVITY_H + BOSS_CEIL


BOSS_EMBED = 4.0 * MM  # extra material sunk up into the solid fuselage core,
                        # well past its curved skin, so the union has a thick
                        # 3D overlap instead of a thin/coincident boundary
                        # (a flush touch at the curved belly surface produced
                        # a non-manifold union in testing).


def belly_boss(center_x, belly_z, outer_r=BOSS_OUTER_R, embed=BOSS_EMBED, sections=48):
    """Solid boss hanging below the fuselage belly skin, extended upward
    into the fuselage core by `embed` for a robust boolean union. Its
    externally-visible protrusion below the belly is unaffected."""
    height = BOSS_HEIGHT + embed
    top_z = belly_z + embed
    cyl = trimesh.creation.cylinder(radius=outer_r, height=height, sections=sections)
    cyl.apply_translation((center_x, 0, top_z - height / 2.0))
    check(cyl, "belly_boss")
    return cyl


def belly_boss_cavity_center_z(belly_z):
    boss_bottom = belly_z - BOSS_HEIGHT
    return boss_bottom + BOSS_FLOOR + BOSS_CAVITY_H / 2.0


def belly_flange_pocket(center_x, belly_z, pocket_r=FLANGE_POCKET_R,
                         cavity_h=BOSS_CAVITY_H, sections=48):
    """Fully-enclosed cavity inside the boss (floor + ceiling both solid)
    that traps the wing rotor's flange -- captured, still free to spin."""
    cz = belly_boss_cavity_center_z(belly_z)
    cyl = trimesh.creation.cylinder(radius=pocket_r, height=cavity_h, sections=sections)
    cyl.apply_translation((center_x, 0, cz))
    check(cyl, "belly_flange_pocket")
    return cyl


def full_shaft_hole(center_x, top_start_z, belly_z, radius=SOCKET_RADIUS):
    """Vertical bore from above the turret pocket down through the
    fuselage body and the boss's ceiling, stopping just inside the top of
    the flange cavity (the boss floor below stays solid, enclosing it)."""
    cavity_top = belly_boss_cavity_center_z(belly_z) + BOSS_CAVITY_H / 2.0
    bottom_z = cavity_top - 0.3  # dip slightly into the cavity for a clean union
    height = top_start_z - bottom_z
    cyl = trimesh.creation.cylinder(radius=radius, height=height, sections=32)
    cyl.apply_translation((center_x, 0, (top_start_z + bottom_z) / 2.0))
    check(cyl, "full_shaft_hole")
    return cyl


def rotor_shaft_and_flange(center_x, hub_z, belly_z, shaft_r=SHAFT_RADIUS,
                            flange_r=FLANGE_R, flange_thk=FLANGE_THK):
    """The wing rotor's shaft + captured mushroom-head flange, as one
    connected body (to be unioned onto the wing bar/hub)."""
    flange_cz = belly_boss_cavity_center_z(belly_z)
    shaft_top = hub_z + HUB_THK / 2.0  # overlaps into the hub disc above
    shaft_bottom = flange_cz - flange_thk / 2.0  # overlaps into the flange below
    shaft_h = shaft_top - shaft_bottom
    shaft = trimesh.creation.cylinder(radius=shaft_r, height=shaft_h, sections=32)
    shaft.apply_translation((center_x, 0, (shaft_top + shaft_bottom) / 2.0))
    flange = trimesh.creation.cylinder(radius=flange_r, height=flange_thk, sections=32)
    flange.apply_translation((center_x, 0, flange_cz))
    m = trimesh.boolean.union([shaft, flange], engine="manifold")
    m.merge_vertices()
    trimesh.repair.fix_normals(m, multibody=False)
    check(m, "rotor_shaft_and_flange")
    return m
