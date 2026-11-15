# SPDX-License-Identifier: MIT
"""Independent mesh audit for printed parts: watertight, bodies, volume, overhang area for a given print 'up' axis.
usage: check.py file.stl:up  (up = +z, -z, +y, -y ... the model axis that points UP on the print bed)"""
import json, sys
import numpy as np, trimesh

AX = {"x": 0, "y": 1, "z": 2}
out = {}
for arg in sys.argv[1:]:
    f, up = arg.split(":", 1)
    m = trimesh.load(f); m.merge_vertices(); m.process(validate=True)
    if "," in up:
        u = np.array([float(v) for v in up.split(",")]); u /= np.linalg.norm(u)
    else:
        u = np.zeros(3); u[AX[up[1]]] = 1.0 if up[0] == "+" else -1.0
    n = m.face_normals; a = m.area_faces
    h = m.vertices @ u; zmin = h.min()
    face_h = (m.vertices[m.faces] @ u).min(axis=1)
    down = n @ u                                   # -1 = facing straight down
    on_bed = face_h < zmin + 0.05
    over = (down < -np.sin(np.radians(45))) & ~on_bed   # overhang angle > 45 deg from vertical (down = -sin(angle))
    bad = (down < -np.sin(np.radians(60))) & ~on_bed    # > 60 deg: needs support or a good bridge
    out[arg] = dict(up=up, watertight=bool(m.is_watertight), bodies=len(m.split(only_watertight=False)),
                  volume_cm3=round(m.volume / 1000, 1), height_mm=round(float(h.max() - zmin), 1),
                  bed_contact_cm2=round(float(a[on_bed & (down < -0.99)].sum()) / 100, 1),
                  overhang_gt45_cm2=round(float(a[over].sum()) / 100, 1), overhang_gt60_cm2=round(float(a[bad].sum()) / 100, 1))
print(json.dumps(out, indent=1))
