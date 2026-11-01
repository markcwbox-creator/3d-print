"""Build + verify + export the foldable litter box STLs."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import trimesh
import litterbox as L
import litterbox_verify as V

OUT = os.path.join(os.path.dirname(__file__), '..', 'models', 'litterbox')
os.makedirs(OUT, exist_ok=True)


def to_trimesh(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.array(mesh.vert_properties)[:, :3], np.array(mesh.tri_verts), process=False)


def export(m, name):
    bb = m.bounding_box()
    m = m.translate([-bb[0], -bb[1], -min(bb[2], 0.0)])    # corner to origin, bed at z=0
    t = to_trimesh(m)
    path = os.path.join(OUT, name)
    t.export(path)
    ext = t.bounds[1] - t.bounds[0]
    print(f'{name:42s} {ext[0]:6.1f} x {ext[1]:6.1f} x {ext[2]:6.1f} mm  tris={len(t.faces):7d}  watertight={t.is_watertight}  shells={len(m.decompose())}')


def module_solid(md):
    return L.M.compose([md['tile'], md['long'], md['short']])


if __name__ == '__main__':
    A, Be, Bp = (L.build_module(k) for k in ('A', 'B_entry', 'B_plain'))
    mods = {'FL': dict(A, rot=False), 'FR': dict(Be, rot=False),
            'BR': dict(A, rot=True), 'BL': dict(Bp, rot=True)}

    # --- verification gate -------------------------------------------------
    V.module_checks('A', A)
    V.module_checks('B_entry', Be)
    V.module_checks('B_plain', Bp)
    V.box_checks(mods)
    clipA = L.corner_clip()
    clipB = clipA.mirror([1, 0, 0])
    # clips on the deployed corners
    for nm, clip, md, place in (
            ('FL', clipA, A, lambda m: m.translate([0, 0, 150.3 - 40.0])),
            ('FR', clipB, Be, lambda m: m.translate([2 * L.P['TILE_X'], 0, 150.3 - 40.0]))):
        for part in ('long', 'short'):
            v = V.inter_vol(place(clip), md[part])
            g = place(clip).min_gap(md[part], 3.0)
            V.check(f'clip {nm}/{part}: no overlap, gap>=0.2', v < 1e-6 and g >= 0.2, f'gap {g:.3f}')
    V.check('clip is one watertight shell', len(clipA.decompose()) == 1 and clipA.status() == L.m3.Error.NoError)
    if V.fails:
        print('\nVERIFICATION FAILED -- not exporting'); sys.exit(1)

    # --- export -------------------------------------------------------------
    print()
    export(module_solid(A), 'module_A_print_x2.stl')
    export(module_solid(Be), 'module_B_entry_print_x1.stl')
    export(module_solid(Bp), 'module_B_plain_print_x1.stl')
    export(clipA, 'corner_clip_A_print_x2.stl')
    export(clipB, 'corner_clip_B_print_x2.stl')
