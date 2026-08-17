"""
Shared geometry helpers for the X-59 QueSST 3D-printable mockup family.
Built with numpy + trimesh (MIT) + manifold3d (Apache-2.0) -- all OSS.
Units: millimeters.
"""
import numpy as np
import trimesh


# ---------------------------------------------------------------------------
# Low-level loft engine
# ---------------------------------------------------------------------------

def _fan_faces_point_to_ring(apex_idx, ring_idx, n, apex_first=True):
    faces = []
    for j in range(n):
        j2 = (j + 1) % n
        if apex_first:
            faces.append([apex_idx, ring_idx + j, ring_idx + j2])
        else:
            faces.append([apex_idx, ring_idx + j2, ring_idx + j])
    return faces


def _flat_cap_faces(ring_idx, n, reverse=False):
    faces = []
    for j in range(1, n - 1):
        if not reverse:
            faces.append([ring_idx, ring_idx + j, ring_idx + j + 1])
        else:
            faces.append([ring_idx, ring_idx + j + 1, ring_idx + j])
    return faces


def loft(sections, cap_start=False, cap_end=False, process=True):
    """Build a watertight tube by lofting between consecutive cross-sections.

    sections: list of (n,3) arrays (rings, same n between consecutive
    ring-ring transitions) or (1,3) arrays (a point, which auto-caps the
    tube with a fan -- used for fuselage nose/tail tips).

    cap_start/cap_end: if the first/last section is a ring (n>1) and not
    a point, close it with a flat fan cap (used for prism-like wings).
    """
    verts = []
    offsets = []
    for s in sections:
        offsets.append(len(verts))
        verts.extend(np.asarray(s).tolist())
    verts = np.array(verts, dtype=float)

    faces = []
    for i in range(len(sections) - 1):
        a_off, b_off = offsets[i], offsets[i + 1]
        na, nb = len(sections[i]), len(sections[i + 1])
        if na == nb and na > 1:
            n = na
            for j in range(n):
                j2 = (j + 1) % n
                a0, a1 = a_off + j, a_off + j2
                b0, b1 = b_off + j, b_off + j2
                faces.append([a0, b0, b1])
                faces.append([a0, b1, a1])
        elif na == 1 and nb > 1:
            faces += _fan_faces_point_to_ring(a_off, b_off, nb, apex_first=True)
        elif nb == 1 and na > 1:
            faces += _fan_faces_point_to_ring(b_off, a_off, na, apex_first=False)
        else:
            raise ValueError(f"Unsupported section transition na={na} nb={nb}")

    if cap_start and len(sections[0]) > 1:
        faces += _flat_cap_faces(offsets[0], len(sections[0]), reverse=True)
    if cap_end and len(sections[-1]) > 1:
        faces += _flat_cap_faces(offsets[-1], len(sections[-1]), reverse=False)

    mesh = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=process)
    mesh.merge_vertices()
    trimesh.repair.fix_normals(mesh, multibody=False)
    return mesh


def ellipse_ring(x, cy, cz, ry, rz, n=28):
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    y = cy + ry * np.cos(theta)
    z = cz + rz * np.sin(theta)
    xs = np.full(n, x)
    return np.stack([xs, y, z], axis=1)


def point3(x, y, z):
    return np.array([[x, y, z]])


def biconvex_quad(chord, thickness, le_bulge=0.35):
    """4-point diamond (biconvex airfoil-like) cross section in local
    (chordwise, thickness) coordinates, leading edge at (0,0)."""
    return np.array([
        [0.0, 0.0],
        [chord * le_bulge, thickness / 2.0],
        [chord, 0.0],
        [chord * le_bulge, -thickness / 2.0],
    ])


def check(mesh, name):
    ok = mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    print(f"[{name}] watertight={mesh.is_watertight} winding_ok={mesh.is_winding_consistent} "
          f"volume={mesh.volume:.1f}mm3 bounds={mesh.bounds.tolist()}")
    if not ok:
        print(f"  !! WARNING: {name} failed validation")
    return ok


def union(parts, name="union"):
    m = trimesh.boolean.union(parts, engine="manifold")
    m.merge_vertices()
    trimesh.repair.fix_normals(m, multibody=False)
    check(m, name)
    return m


def difference(a, subtract, name="difference"):
    """a - subtract, where subtract is a mesh or list of meshes."""
    if not isinstance(subtract, (list, tuple)):
        subtract = [subtract]
    m = trimesh.boolean.difference([a] + list(subtract), engine="manifold")
    m.merge_vertices()
    trimesh.repair.fix_normals(m, multibody=False)
    check(m, name)
    return m
