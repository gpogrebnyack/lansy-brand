# Prepare a generated cup mesh (Tripo FBX) for the studio, once: straighten it (its axis from the lid's top and the base),
# turn its sip slot to the front, scale it to a real to-go cup (12 cm tall, base on z = 0, centred), decimate, fix normals.
# Blender -b -P 3d/prep_cup.py -- <cup.fbx>        → 3d/models/cup_tripo.blend (object 'cup_tripo'), mesh check printed
import bpy, bmesh, math, sys, os
from mathutils import Vector, Matrix
ROOT = os.path.dirname(os.path.abspath(__file__)); H = .12
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=sys.argv[-1])
o = next(x for x in bpy.context.scene.objects if x.type == 'MESH'); o.name = 'cup_tripo'; me = o.data; me.name = 'cup_tripo'
for x in list(bpy.context.scene.objects):
    if x is not o: bpy.data.objects.remove(x, do_unlink=True)
me.transform(o.matrix_world); o.matrix_world = Matrix()

def axis():   # area-weighted mean normal of the lid's top minus that of the base: the cup's axis
    bm = bmesh.new(); bm.from_mesh(me); bm.normal_update(); up = Vector(); dn = Vector()
    for f in bm.faces:
        a = f.calc_area()
        if f.normal.z > .8: up += f.normal * a
        elif f.normal.z < -.8: dn += f.normal * a
    bm.free(); return (up.normalized() - dn.normalized()).normalized()
for _ in range(3):
    ax = axis(); me.transform(ax.rotation_difference(Vector((0, 0, 1))).to_matrix().to_4x4())
print('AXIS after', tuple(round(c, 4) for c in axis()))

def frame():   # base on z = 0, centred in x, y, height H
    vs = [v.co for v in me.vertices]; lo = Vector([min(v[i] for v in vs) for i in range(3)]); hi = Vector([max(v[i] for v in vs) for i in range(3)])
    me.transform(Matrix.Scale(H / (hi.z - lo.z), 4) @ Matrix.Translation(Vector(((-(lo.x + hi.x) / 2), -(lo.y + hi.y) / 2, -lo.z))))
frame()

# the sip slot: steep faces in the top band, well inside the lid → their centroid's angle, turned to the front (−y)
vs = [v.co for v in me.vertices]; R = max(math.hypot(v.x, v.y) for v in vs); zt = max(v.z for v in vs)
bm = bmesh.new(); bm.from_mesh(me); bm.normal_update(); c = Vector(); n = 0
for f in bm.faces:
    p = f.calc_center_median()
    if p.z > zt - .06 * H and abs(f.normal.z) < .3 and math.hypot(p.x, p.y) < .6 * R: c += p; n += 1
bm.free()
if n:
    ang = math.atan2(c.x, -c.y); me.transform(Matrix.Rotation(ang + math.radians(float(os.environ.get('SLOT', 0))), 4, 'Z'))
    print('SLOT faces', n, 'at', round(math.degrees(ang), 1), 'deg → front')
frame()

# decimate to ~400k triangles, then normals outward and consistent, smooth by angle
m = o.modifiers.new('d', 'DECIMATE'); m.ratio = min(1, 4e5 / len(me.polygons))
bpy.context.view_layer.objects.active = o
with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o]): bpy.ops.object.modifier_apply(modifier=m.name)
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-7); bmesh.ops.dissolve_degenerate(bm, dist=1e-8, edges=bm.edges)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
for f in bm.faces: f.smooth = True
for e in bm.edges:
    if len(e.link_faces) == 2 and e.calc_face_angle() > math.radians(35): e.smooth = False
nonman = sum(1 for e in bm.edges if not e.is_manifold); bnd = sum(1 for e in bm.edges if e.is_boundary)
flip = sum(1 for e in bm.edges if len(e.link_loops) == 2 and e.link_loops[0].vert == e.link_loops[1].vert)
deg = sum(1 for f in bm.faces if f.calc_area() < 1e-14); vol = bm.calc_volume(signed=True)
bm.to_mesh(me); bm.free(); me.materials.clear()
vs = [v.co for v in me.vertices]
print('CHECK tris', len(me.polygons), 'nonmanifold', nonman, 'boundary', bnd, 'inconsistent', flip, 'degenerate', deg,
      'normals', 'outward' if vol > 0 else 'INWARD', 'dims mm', [round((max(v[i] for v in vs) - min(v[i] for v in vs)) * 1000, 1) for i in range(3)])
os.makedirs(f'{ROOT}/models', exist_ok=True); bpy.ops.wm.save_as_mainfile(filepath=f'{ROOT}/models/cup_tripo.blend'); print('SAVED')
