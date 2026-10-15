# A product studio for glass and polished metal, built into the test scene (replaces the flat floor and the HDRI look):
# a curved seamless cyc the camera sees, two tall strip lights at the sides and slightly behind (bright edge lines on glass),
# a large soft top light, black flags just out of frame (dark edges in the glass), AgX so highlights roll off instead of clipping.
# Usage (with test_materials.py after it):  Blender -b 3d/lansy-3d-test.blend -P 3d/studio_glass.py -P 3d/test_materials.py
import bpy, bmesh, math
from mathutils import Vector

sc = bpy.context.scene
tubes = bpy.data.objects['icon_alone_relief']
for name in ('floor', 'key'):
    o = bpy.data.objects.get(name)
    if o: bpy.data.objects.remove(o, do_unlink=True)
coll = bpy.data.collections.get('studio') or sc.collection
pts = [tubes.matrix_world @ v.co for v in tubes.data.vertices]
cx = sum(p.x for p in pts) / len(pts); cy = sum(p.y for p in pts) / len(pts); top = max(p.z for p in pts)
C = Vector((cx, cy, top / 2))
import os
STRIP, TOP, FILL, CYC = (float(x) for x in os.environ.get('RIG', '4,3,.6,.35').split(','))   # light watts and cyc grey

def mesh_obj(name, bm, mat):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); coll.objects.link(o)
    o.data.materials.append(mat); return o
def material(name, rgb, rough=.6, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
    if emit: b.inputs['Emission Color'].default_value = (1, 1, 1, 1); b.inputs['Emission Strength'].default_value = emit
    return m

# the cyc: floor running into a back wall through a 25 cm radius curve, 1.6 m wide, centred behind the object
bm = bmesh.new(); R = .25; prof = [(-.8, 0)] + [(.15 + R * math.sin(math.radians(a)), R - R * math.cos(math.radians(a))) for a in range(0, 91, 5)] + [(.15 + R, 1.2)]
W = 1.6; cols = []
for (y, z) in prof: cols.append((bm.verts.new((cx - W / 2, cy + y, z)), bm.verts.new((cx + W / 2, cy + y, z))))
for a, b in zip(cols, cols[1:]): bm.faces.new((a[0], a[1], b[1], b[0]))
cyc = mesh_obj('cyc', bm, material('M_cyc', (CYC, CYC, CYC * .99), .85))
for p in cyc.data.polygons: p.use_smooth = True

def area(name, size, energy, loc, shape='RECTANGLE', sx=None, sy=None):
    L = bpy.data.objects.new(name, bpy.data.lights.new(name, 'AREA')); coll.objects.link(L)
    L.data.shape = shape; L.data.size = sx or size; L.data.size_y = sy or size; L.data.energy = energy
    L.location = loc; L.rotation_euler = (C - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    L.data.spread = math.radians(60); return L
# strips: tall and narrow, at the sides and a bit behind → long clean highlights along the tubes' edges
area('strip_L', 0, STRIP, (cx - .38, cy + .10, C.z + .05), sx=.06, sy=.6)
area('strip_R', 0, STRIP, (cx + .38, cy + .10, C.z + .05), sx=.06, sy=.6)
area('top', 0, TOP, (cx - .05, cy - .15, C.z + .55), sx=.6, sy=.4)   # a soft top/front key
area('fill', 0, FILL, (cx, cy - .6, C.z + .1), sx=.5, sy=.3)          # a weak front fill so the front faces aren't black
# black flags: tall dark cards just outside the frame, so the glass edges reflect dark and keep their outline
blk = material('M_flag', (.005, .005, .005), .4)
for side in (-1, 1):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=.25)
    f = mesh_obj(f'flag_{"L" if side < 0 else "R"}', bm, blk)
    f.location = (cx + side * .28, cy - .18, C.z); f.rotation_euler = (math.radians(90), 0, math.radians(side * 70))
    f.visible_camera = False

# emissive strip cards: invisible to the camera, very bright, thin → crisp highlight lines in the glass without lighting the cyc much
EM = float(os.environ.get('EM', 25))
def card(name, w_, h_, loc, emit):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=.5)
    for v in bm.verts: v.co.x *= w_; v.co.y *= h_
    m = bpy.data.materials.new('M_' + name); m.use_nodes = True; nt_ = m.node_tree; nt_.nodes.clear()
    o_ = nt_.nodes.new('ShaderNodeOutputMaterial'); e = nt_.nodes.new('ShaderNodeEmission'); e.inputs[1].default_value = emit
    nt_.links.new(e.outputs[0], o_.inputs[0])
    o = mesh_obj(name, bm, m); o.location = loc
    o.rotation_euler = (C - Vector(loc)).to_track_quat('Z', 'Y').to_euler(); o.visible_camera = False; o.visible_shadow = False
    return o
for side in (-1, 1):
    card(f'em_strip_{side}', .015, .35, (cx + side * .22, cy + .02, C.z + .03), EM)        # side strips: the long edge lines
    card(f'em_rim_{side}', .01, .3, (cx + side * .12, cy + .25, C.z + .05), EM * .8)      # behind: thin rims on the far edges
card('em_top', .25, .04, (cx, cy - .05, C.z + .28), EM * .5)                                # a soft line across the tops
w = sc.world; nt = w.node_tree   # the world: darker, so lighting comes from the rig; the HDRI stays only as faint reflections
for n in nt.nodes:
    if n.type == 'BACKGROUND': n.inputs[1].default_value = .15

v = sc.view_settings; v.view_transform = 'AgX'; v.look = 'AgX - Medium High Contrast'
c = sc.cycles; c.caustics_reflective = False; c.caustics_refractive = False; c.sample_clamp_indirect = 10; c.blur_glossy = .5
sc.render.film_transparent = False
cam = bpy.data.objects['icon_alone_hero']; cam.data.lens = 70
print('STUDIO ready', tuple(round(x, 3) for x in C))
