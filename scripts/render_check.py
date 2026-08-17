import sys, os
import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection


def render_view(ax, mesh, axes_pair, view_axis, title):
    v = mesh.vertices
    f = mesh.faces
    tri = v[f]  # (n,3,3)
    depth = tri[:, :, view_axis].mean(axis=1)
    order = np.argsort(depth)
    polys = tri[order][:, :, axes_pair]
    normals = mesh.face_normals[order]
    shade = 0.35 + 0.55 * np.clip(np.abs(normals[:, view_axis]), 0, 1)
    colors = np.stack([shade * 0.55, shade * 0.65, shade * 0.85], axis=1)
    pc = PolyCollection(polys, facecolors=colors, edgecolors=(0, 0, 0, 0.15), linewidths=0.2)
    ax.add_collection(pc)
    allv = v[:, axes_pair]
    pad = 10
    ax.set_xlim(allv[:, 0].min() - pad, allv[:, 0].max() + pad)
    ax.set_ylim(allv[:, 1].min() - pad, allv[:, 1].max() + pad)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=9)
    ax.axis('off')


def render_mesh(mesh, out_png, name):
    fig, axs = plt.subplots(1, 3, figsize=(15, 5))
    render_view(axs[0], mesh, (0, 1), 2, f"{name} - TOP (X,Y)")
    render_view(axs[1], mesh, (0, 2), 1, f"{name} - SIDE (X,Z)")
    render_view(axs[2], mesh, (1, 2), 0, f"{name} - FRONT (Y,Z)")
    plt.tight_layout()
    plt.savefig(out_png, dpi=130)
    plt.close(fig)
    print("wrote", out_png)


if __name__ == "__main__":
    OUT = os.path.join(os.path.dirname(__file__), "output")
    CHK = os.path.join(os.path.dirname(__file__), "renders")
    os.makedirs(CHK, exist_ok=True)
    targets = [
        ("01_standard_swept_wing/quesst_standard_swept.obj", "v1_standard"),
        ("02_pivot_rotating_wing/quesst_pivot_A_fuselage.obj", "v2_pivot_fuselage"),
        ("02_pivot_rotating_wing/quesst_pivot_B_wing_rotor.obj", "v2_pivot_rotor"),
        ("02_pivot_rotating_wing/quesst_pivot_C_retaining_cap.obj", "v2_pivot_cap"),
        ("03_fixed_0deg_perpendicular/quesst_03_fixed_0deg_perpendicular.obj", "v3_0deg"),
        ("04_fixed_90deg_parallel/quesst_04_fixed_90deg_parallel.obj", "v4_90deg"),
        ("05_fixed_45deg_aft/quesst_05_fixed_45deg_aft.obj", "v5_45aft"),
        ("06_fixed_45deg_fwd/quesst_06_fixed_45deg_fwd.obj", "v6_45fwd"),
        ("stands/stand_universal.obj", "stand"),
    ]
    for rel, name in targets:
        mesh = trimesh.load(os.path.join(OUT, rel), process=False)
        render_mesh(mesh, os.path.join(CHK, name + ".png"), name)

    # combined assembly preview of the pivot version (fuselage+rotor@0deg+cap)
    fus = trimesh.load(os.path.join(OUT, "02_pivot_rotating_wing/quesst_pivot_A_fuselage.obj"), process=False)
    rotor = trimesh.load(os.path.join(OUT, "02_pivot_rotating_wing/quesst_pivot_B_wing_rotor.obj"), process=False)
    cap = trimesh.load(os.path.join(OUT, "02_pivot_rotating_wing/quesst_pivot_C_retaining_cap.obj"), process=False)
    cap2 = cap.copy()
    cap2.apply_translation((110.0, 0, -13.4 + 1.5))
    combo = trimesh.util.concatenate([fus, rotor, cap2])
    render_mesh(combo, os.path.join(CHK, "v2_pivot_ASSEMBLED_preview.png"), "v2_pivot_assembled")
