"""Read-only source geometry checks, independent of the live Blender scene."""
import json
import pathlib

WORK = pathlib.Path(__file__).resolve().parents[1]
records = json.loads((WORK / 'references/source_meshes.json').read_text(encoding='utf-8'))
source = next(r for r in records if r['source'] == 'keyboardKbkCase.3mf')
verts = [(47.5-z, 47.5-x, y) for x, y, z in source['vertex_data']]
faces = source['triangle_data']

def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))

def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def first_hit(origin, direction):
    hits = []
    for ia, ib, ic in faces:
        a, b, c = verts[ia], verts[ib], verts[ic]
        e1, e2 = sub(b, a), sub(c, a)
        p = cross(direction, e2)
        determinant = dot(e1, p)
        if abs(determinant) < 1e-10:
            continue
        tvec = sub(origin, a)
        u = dot(tvec, p) / determinant
        if u < -1e-8 or u > 1+1e-8:
            continue
        q = cross(tvec, e1)
        v = dot(direction, q) / determinant
        if v < -1e-8 or u+v > 1+1e-8:
            continue
        t = dot(e2, q) / determinant
        if t > 1e-8:
            hits.append(t)
    return round(min(hits), 6) if hits else None

directions = {
    'rear_center_port': ((0, 60, -1.73), (0, -1, 0)),
    'rear_beside_port': ((12, 60, -1.73), (0, -1, 0)),
    'front_center': ((0, -60, -1.73), (0, 1, 0)),
    'left_center': ((-60, 0, -1.73), (1, 0, 0)),
    'right_center': ((60, 0, -1.73), (-1, 0, 0)),
}
hits = {name: first_hit(*ray) for name, ray in directions.items()}
report = {
    'source': source['source'],
    'rigid_transform_mm': '(47.5-z, 47.5-x, y)',
    'first_hit_distance_mm': hits,
    'near_wall_probe_limit_mm': 15,
    'rear_port_open': hits['rear_center_port'] is None or hits['rear_center_port'] > 15,
    'other_probes_closed': all(hits[k] is not None and hits[k] < 15 for k in hits if k != 'rear_center_port'),
    'bounds_mm': [[min(v[i] for v in verts), max(v[i] for v in verts)] for i in range(3)],
    'scope': 'Authoritative source geometry only; does not claim the current Blender scene is corrected or visually accepted.',
}
(WORK / 'references/source_opening_audit.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
