"""
Foldable cat litter box -- print-in-place hinged wall modules.

Box: 400 x 300 x 150 mm outer, built from four 200 x 150 mm floor tiles.
Each tile carries two print-in-place hinged walls (one 200 mm "long" wall,
one 150 mm "short" wall) printed upright in their deployed position.  Walls
fold inward flat onto their tile: long wall first (lower), short wall second
(higher).  Tiles join with vertical-slide dovetails; four L-shaped clips lock
the corners.

Built with manifold3d (exact CSG).  Units: mm.  Every parameter is in P.
"""
import numpy as np
import manifold3d as m3

M = m3.Manifold

P = dict(
    TILE_X=200.0, TILE_Y=150.0,
    BOX_H=150.0,
    F=4.0,            # floor thickness
    R=4.0,            # hinge barrel radius
    T=4.0,            # wall plate thickness
    YC=4.0,           # hinge axis distance from outer edge
    G=0.4,            # axial gap between knuckles / modules
    CV=0.35,          # radial / vertical print-in-place clearance
    LC=2.5,           # cone pin length (45 deg, base radius == length)
    DELTA=0.5,        # axial offset of cone cavity (=> ~0.35 normal clearance)
    STEP=8.8,         # short-wall hinge axis height above long-wall axis (tab must clear long hinge when folded)
    FRONT_U0=8.8,     # long-wall hinge/plate start (clears short-wall barrels)
    LAP=6.0,          # seam lap length
    ENTRY_X=(225.0, 365.0),  # global x extent of low entry in the front wall
    ENTRY_SILL=70.0,  # height of the entry sill above the floor top
    ENTRY_R=12.0,
    NSEG_LONG=7, NSEG_SHORT=7,
    FIN_GAP=0.35, FIN_T=1.2, FIN_H=14.0,   # hinge stop fin
    SEG=40,
)


# ----------------------------------------------------------------------------
# primitives
# ----------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    return M.cube([x1 - x0, y1 - y0, z1 - z0]).translate([x0, y0, z0])


def cyl_x(x0, x1, y, z, r, seg=None):
    c = M.cylinder(x1 - x0, r, r, seg or P['SEG']).rotate([0, 90, 0])
    return c.translate([x0, y, z])


def cone_x(xbase, length, y, z, r_base, seg=None):
    """Cone with base at xbase, apex at xbase+length (length may be <0)."""
    c = M.cylinder(abs(length), r_base, 0.0, seg or P['SEG'])
    if length >= 0:
        c = c.rotate([0, 90, 0]).translate([xbase, y, z])
    else:
        c = c.rotate([0, -90, 0]).translate([xbase, y, z])
    return c


def union(parts):
    parts = [p for p in parts if p is not None]
    return M.batch_boolean(parts, m3.OpType.Add) if len(parts) > 1 else parts[0]


def diag_swap(m):
    """Swap x and y (mirror across the plane x=y)."""
    return m.mirror([1, -1, 0])


def mirror_x_about(m, xc):
    return m.mirror([1, 0, 0]).translate([2 * xc, 0, 0])


def rot180_about(m, cx, cy):
    return m.rotate([0, 0, 180]).translate([2 * cx, 2 * cy, 0])


def dovetail(base_t, base_n, n_dir, L, wn, ww, c=0.0, extra_in=0.0, z0=-0.5, z1=None):
    """Dovetail prism.  Edge runs along t, base at n=base_n, extends L along
    n_dir (+1/-1) in n.  Returned in (n,t) abstract coords as an M with
    x=n, y=t; caller swaps if edge is along x.  c expands the outline."""
    z1 = P['F'] + 0.5 if z1 is None else z1
    pts = []
    for z in (z0, z1):
        for (n, t) in [(-extra_in, -(wn / 2 + c)), (-extra_in, wn / 2 + c),
                       (L + c, ww / 2 + c), (L + c, -(ww / 2 + c))]:
            pts.append([base_n + n_dir * n, base_t + t, z])
    return M.hull_points(np.array(pts))


# ----------------------------------------------------------------------------
# hinge wall (canonical frame: hinge axis along +x, outer side is -y)
# ----------------------------------------------------------------------------
def split_segments(u0, u1, n, g):
    L = (u1 - u0 - (n - 1) * g) / n
    return [(u0 + i * (L + g), u0 + i * (L + g) + L) for i in range(n)]


def hinge_wall(u0, u1, n, a, ped_top, plate_u0, full_end, thin_end, lap,
               tab=False, s0_web_v1=None, entry=None):
    """Returns (static, moving) solids in canonical coordinates (u=x, v=y, w=z).
    static is meant to be unioned into the floor tile."""
    R, T, YC, G, CV, F = (P[k] for k in ('R', 'T', 'YC', 'G', 'CV', 'F'))
    top = P['BOX_H']
    segs = split_segments(u0, u1, n, G)
    sc = a + R + CV                      # plate bottom over static knuckles
    rc = P['LC']
    st, mv = [], []
    for i, (s0, s1) in enumerate(segs):
        is_static = (i % 2 == 0)
        if is_static:
            v1 = s0_web_v1 if (i == 0 and s0_web_v1) else YC + 3.0
            parts = [cyl_x(s0, s1, YC, a, R),
                     box(s0, s1, YC - 3.0, v1, F - 0.5, a),
                     # hinge stop fin (outboard of the plate's outer face)
                     box(s0 + 2, s1 - 2, YC - T / 2 - P['FIN_GAP'] - P['FIN_T'],
                         YC - T / 2 - P['FIN_GAP'], a - 1, a + P['FIN_H'])]
            # cone pins pointing into moving neighbours
            if i + 1 < n:
                parts.append(cone_x(s1, P['LC'], YC, a, rc))
            if i > 0:
                parts.append(cone_x(s0, -P['LC'], YC, a, rc))
            st.append(union(parts))
        else:
            parts = [cyl_x(s0, s1, YC, a, R)]
            # plate root bonded to this barrel
            parts.append(box(s0, s1, YC - T / 2, YC + T / 2, a, sc + 0.5))
            body = union(parts)
            # conical cavities at both ends
            cav_len = P['LC'] - G + P['DELTA']
            cav_r = cav_len * rc / P['LC']
            body = body - cone_x(s0, cav_len, YC, a, cav_r) \
                        - cone_x(s1, -cav_len, YC, a, cav_r)
            mv.append(body)
            if ped_top > F + 0.01:
                st.append(box(s0, s1, YC - 3.0, YC + 3.0, F - 0.5, ped_top))
    static = union(st)

    # plate (above the knuckle scallop line)
    pl = [box(plate_u0, full_end, YC - T / 2, YC + T / 2, sc, top)]
    half = T / 2 - 0.2
    if lap == 'outer':
        pl.append(box(full_end - 1.0, thin_end, YC - T / 2, YC - T / 2 + half, sc, top))
    else:
        pl.append(box(full_end - 1.0, thin_end, YC + T / 2 - half, YC + T / 2, sc, top))
    if tab:
        pl.append(box(plate_u0, plate_u0 + 4.4, YC + T / 2 - 0.5, YC + T / 2 + 2.4, sc, top))
    plate = union(pl)
    if entry is not None:
        ex0, ex1, sill, er = entry
        cut = [box(ex0 + er, ex1 - er, YC - 5, YC + 5, sill, top + 5),
               box(ex0, ex1, YC - 5, YC + 5, sill + er, top + 5)]
        for cx in (ex0 + er, ex1 - er):
            cut.append(M.cylinder(10.0, er, er, 48).rotate([90, 0, 0])
                       .translate([cx, YC + 5, sill + er]))
        plate = plate - union(cut)
    moving = union(mv + [plate])
    return static, moving


# ----------------------------------------------------------------------------
# module (floor tile + two hinged walls), frame "A" (front-left corner)
# ----------------------------------------------------------------------------
def build_module(kind):
    """kind: 'A' (tongues +x,+y; outer laps) or 'B' (grooves +x,+y; inner laps,
    mirrored in x).  B variants: 'B_entry' (low entry in long wall), 'B_plain'.
    Returns dict(tile, long, short, a_long, a_short, mirrored)."""
    TX, TY, F, YC, G, CV, R, T = (P[k] for k in ('TILE_X', 'TILE_Y', 'F', 'YC', 'G', 'CV', 'R', 'T'))
    a_long = F + CV + R
    a_short = a_long + P['STEP']
    lap = 'outer' if kind == 'A' else 'inner'
    half_lap = P['LAP'] / 2

    entry = None
    if kind == 'B_entry':
        # B is mirrored about x=TX; global x -> pre-mirror x = 2*TX - x
        gx0, gx1 = P['ENTRY_X']
        entry = (2 * TX - gx1, 2 * TX - gx0, F + P['ENTRY_SILL'], P['ENTRY_R'])

    # long wall: axis along x
    l_static, l_moving = hinge_wall(
        u0=P['FRONT_U0'], u1=TX - G / 2, n=P['NSEG_LONG'], a=a_long, ped_top=F,
        plate_u0=P['FRONT_U0'], full_end=TX - half_lap - 0.2 - 0.0,
        thin_end=TX + half_lap - 0.2, lap=lap, tab=False, entry=entry)
    # short wall: canonical then swap x<->y
    s_static, s_moving = hinge_wall(
        u0=YC - T / 2, u1=TY - G / 2, n=P['NSEG_SHORT'], a=a_short,
        ped_top=a_short - R - CV, plate_u0=YC - T / 2,
        full_end=TY - half_lap - 0.2, thin_end=TY + half_lap - 0.2, lap=lap,
        tab=True, s0_web_v1=YC + T / 2 + 2.1)
    s_static, s_moving = diag_swap(s_static), diag_swap(s_moving)

    tile = box(0, TX, 0, TY, 0, F)
    tile = union([tile, l_static, s_static])

    # dovetail seams (vertical-slide, 3 mm lead-in not needed at 0.3 clearance)
    wn, ww, L, c = 8.0, 12.0, 6.0, 0.3
    xs_tongue_y = [45.0, 105.0]     # tongues along the x=TX edge (positions in y)
    ys_tongue_x = [60.0, 140.0]     # tongues along the y=TY edge (positions in x)
    def tongue_x(yc_):   # protrudes in +x from edge x=TX
        return dovetail(yc_, TX - 0.5, +1, L + 0.5, wn, ww, extra_in=0, z0=0.0, z1=F)
    def tongue_y(xc_):
        d = dovetail(xc_, TY - 0.5, +1, L + 0.5, wn, ww, extra_in=0, z0=0.0, z1=F)
        return diag_swap(d)
    def groove_x(yc_):   # cut into tile from edge x=TX going -x
        return dovetail(yc_, TX, -1, L, wn, ww, c=c, extra_in=1.0)
    def groove_y(xc_):
        return diag_swap(dovetail(xc_, TY, -1, L, wn, ww, c=c, extra_in=1.0))
    if kind == 'A':
        tile = union([tile] + [tongue_x(y) for y in xs_tongue_y]
                     + [tongue_y(x) for x in ys_tongue_x])
    else:
        cuts = [groove_x(y) for y in xs_tongue_y] + [groove_y(x) for x in ys_tongue_x]
        tile = tile - union(cuts)

    out = dict(tile=tile, long=l_moving, short=s_moving,
               a_long=a_long, a_short=a_short, mirrored=(kind != 'A'))
    if kind != 'A':
        for k in ('tile', 'long', 'short'):
            out[k] = mirror_x_about(out[k], TX)
    return out


# ----------------------------------------------------------------------------
# fold kinematics (global frame of the module as returned by build_module)
# ----------------------------------------------------------------------------
def fold_long(m, a, deg, mirrored=False, yc=None):
    """Rotate a long-wall solid inward by deg about its hinge axis (along x)."""
    yc = P['YC'] if yc is None else yc
    return m.translate([0, -yc, -a]).rotate([-deg, 0, 0]).translate([0, yc, a])


def fold_short(m, a, deg, mirrored=False):
    """Rotate a short-wall solid inward by deg (axis along y).  For a module
    mirrored in x the inward direction flips."""
    xc = P['YC']
    if mirrored:
        xc = 2 * P['TILE_X'] - xc
        deg = -deg
    return m.translate([-xc, 0, -a]).rotate([0, deg, 0]).translate([xc, 0, a])


def place(m, rotated):
    """Place a module-frame solid into box coordinates (FL/FR identity; BL/BR
    rotated 180 deg about the box centre)."""
    return rot180_about(m, P['TILE_X'], P['TILE_Y']) if rotated else m


def state(md, long_deg=0.0, short_deg=0.0):
    """Module pieces with the walls folded by the given inward angles."""
    lg = fold_long(md['long'], md['a_long'], long_deg) if long_deg else md['long']
    sh = fold_short(md['short'], md['a_short'], short_deg, md['mirrored']) if short_deg else md['short']
    return md['tile'], lg, sh


# ----------------------------------------------------------------------------
# corner clip (slides down over the deployed corner of an "A" module)
# ----------------------------------------------------------------------------
def corner_clip(height=40.0, cap=2.5, wall=3.0, arm=28.0, c=0.25):
    """L-shaped clip for the front-left corner (outer corner at x=y=0), dropped
    over the wall tops.  Clip B (for mirrored corners) is its x-mirror."""
    YC, T = P['YC'], P['T']
    o = YC - T / 2                     # outer face of plates (=2)
    w_short = o + T                    # inner face of short plate (=6)
    w_long = w_short + 0.4             # y extent of tab (=6.4)

    def L_shape(x_out, y_out, grow, z0, z1):
        # two arms around the corner; grow expands the cavity outline
        r1 = box(o - grow, w_short + grow, o - grow, arm, z0, z1)
        r2 = box(o - grow, arm, o - grow, w_long + grow, z0, z1)
        return union([r1, r2])

    # slot is open at the bottom (mouth) and closed by a cap on top, so the
    # clip hangs from the wall tops and the inner/outer jaws stay one piece
    outer = L_shape(0, 0, c + wall, 0.0, height + cap)
    cavity = L_shape(0, 0, c, -1.0, height)
    # lead-in funnel at the mouth (z=0): widen by 1.5 mm tapering to nominal at z=4
    lead = []
    for (xa, xb, ya, yb) in [(o, w_short, o, arm), (o, arm, o, w_long)]:
        pts = []
        for z, g in ((-0.01, c + 1.5), (4.0, c)):
            for (x, y) in [(xa - g, ya - g), (xb + g, ya - g), (xb + g, yb + g), (xa - g, yb + g)]:
                pts.append([x, y, z])
        lead.append(M.hull_points(np.array(pts)))
    return outer - cavity - union(lead)
