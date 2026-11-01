"""Oblique sanity renders: deployed box, folded stack, one folded module."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, trimesh
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import litterbox as L
from litterbox_build import to_trimesh

OUT = os.path.join(os.path.dirname(__file__), '..', 'models', 'litterbox', 'renders')
os.makedirs(OUT, exist_ok=True)


def oblique(ax, meshes, az, el, title, colors):
    az, el = np.radians(az), np.radians(el)
    right = np.array([np.cos(az), np.sin(az), 0])
    fwd = np.array([-np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), np.sin(el)])
    up = np.cross(right, fwd)
    light = np.array([0.3, -0.5, 0.8]); light /= np.linalg.norm(light)
    polys, cols, depth = [], [], []
    for mesh, col in zip(meshes, colors):
        tri = mesh.vertices[mesh.faces]
        n = mesh.face_normals
        shade = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
        d = tri.mean(1) @ fwd
        p2 = np.stack([tri @ right, tri @ up], axis=2)
        polys.append(p2); depth.append(d)
        cols.append(np.clip(np.array(col)[None, :] * shade[:, None], 0, 1))
    polys = np.concatenate(polys); depth = np.concatenate(depth); cols = np.concatenate(cols)
    o = np.argsort(depth)
    ax.add_collection(PolyCollection(polys[o], facecolors=cols[o], edgecolors='none'))
    ax.set_xlim(polys[..., 0].min() - 5, polys[..., 0].max() + 5)
    ax.set_ylim(polys[..., 1].min() - 5, polys[..., 1].max() + 5)
    ax.set_aspect('equal'); ax.axis('off'); ax.set_title(title, fontsize=10)


def scene(mods, ld, sd):
    tiles, lg, sh = [], [], []
    for k, md in mods.items():
        t, a, b = L.state(md, ld, sd)
        tiles.append(to_trimesh(L.place(t, md['rot'])))
        lg.append(to_trimesh(L.place(a, md['rot'])))
        sh.append(to_trimesh(L.place(b, md['rot'])))
    return tiles + lg + sh, [(0.55, 0.62, 0.7)] * 4 + [(0.9, 0.55, 0.3)] * 4 + [(0.35, 0.65, 0.85)] * 4


if __name__ == '__main__':
    A, Be, Bp = (L.build_module(k) for k in ('A', 'B_entry', 'B_plain'))
    mods = {'FL': dict(A, rot=False), 'FR': dict(Be, rot=False), 'BR': dict(A, rot=True), 'BL': dict(Bp, rot=True)}
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    for ax, (ld, sd, title) in zip(axs, [(0, 0, 'deployed'), (90, 0, 'long walls folded'), (90, 90, 'fully folded')]):
        m, c = scene(mods, ld, sd)
        oblique(ax, m, 200, 30, title, c)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, 'box_deployed_to_folded.png'), dpi=110); plt.close()
    # close-up: one module, folded 90/90, and hinge detail deployed
    fig, axs = plt.subplots(1, 2, figsize=(14, 6))
    md = A
    for ax, (ld, sd, title) in zip(axs, [(0, 0, 'module A deployed (as printed)'), (90, 90, 'module A folded flat')]):
        t, a, b = L.state(md, ld, sd)
        oblique(ax, [to_trimesh(t), to_trimesh(a), to_trimesh(b)], 215, 28, title,
                [(0.55, 0.62, 0.7), (0.9, 0.55, 0.3), (0.35, 0.65, 0.85)])
    plt.tight_layout(); plt.savefig(os.path.join(OUT, 'module_A.png'), dpi=110); plt.close()
    print('ok')
