# The cup scene from the Codex draft (3d/gen/cup-scene.png), rebuilt with our meshes and materials, on alpha (the background
# is set later, outside): our to-go cup (cup_tripo) in Ceramic Unglazed, the Lansy icon (body in our lime frosted glass 80%,
# palm in Porcelain) leaning on it, our blob (blobs/blob-<BLOB>-brush.geojson, traced from the pen SVG) as a frosted-glass slab
# behind them, a soft voice-wave wire in Brushed aluminium, and a floor in Chromatic Rainbow Spectrum Metal.
# Light: BlenderKit's material-preview studio (its world and sun), as in studio_bk.py, so the materials read as on their previews.
# Blender -b --factory-startup -P 3d/cup_scene.py
#   env: OUT RES SAMPLES  BLOB=kept|a|b  BG=hex (what the glass refracts: the backdrop the image will sit on; never seen by the camera)
#        CUP_MAT FLOOR_MAT BLOB_MAT (path::name)  CAM=x,y,z  LOOK=x,y,z  LENS  CLAY=1 (all matte grey, for the layout)
import bpy, bmesh, json, math, os
from mathutils import Vector, Matrix
ROOT = os.path.dirname(os.path.abspath(__file__)); MATS = ROOT + '/dl/mats'
ICON = ROOT + '/icon/lansy-icon.blend'   # the landing's icon model, copied from artfc-lansy-site/3d/icon
THUMB = ROOT + '/dl/thumbnailer/material_thumbnailer_cycles.blend'
E = os.environ.get
vec = lambda s: Vector([float(v) for v in s.split(',')])
lin = lambda c: c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
sc = bpy.context.scene; col = sc.collection
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)

def link_mesh(name, me):
    o = bpy.data.objects.new(name, me); col.objects.link(o); return o
def bbox(objs):
    pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
    return Vector([min(p[i] for p in pts) for i in range(3)]), Vector([max(p[i] for p in pts) for i in range(3)])
def bake(o):   # world transform into the mesh, origin at the bbox centre (materials' object space is centred on it)
    bpy.context.view_layer.update(); o.data.transform(o.matrix_world.copy()); o.matrix_world = Matrix()
    lo, hi = bbox([o]); c = (lo + hi) / 2; o.data.transform(Matrix.Translation(-c)); o.matrix_world = Matrix.Translation(c)

# ---- the cup: prepared by prep_cup.py (12 cm tall, base on z = 0, sip slot to −y)
with bpy.data.libraries.load(f'{ROOT}/models/cup_tripo.blend') as (s, d): d.objects = ['cup_tripo']
cup = d.objects[0]; col.objects.link(cup)
# its cardboard sleeve (a 3 mm band, z 21–76 mm) pressed back onto the body: the wall tapers linearly between the radius just
# below the band and just above it; every vertex standing out of that line inside the band goes onto it (0.15 mm inside)
if E('SLEEVE', '0') != '1':
    rz = lambda a, b: max(math.hypot(v.co.x, v.co.y) for v in cup.data.vertices if a <= v.co.z <= b)
    z0, z1 = .0195, .077; r0, r1 = rz(.016, .0195), rz(.077, .084)
    body_r = lambda z: r0 + (r1 - r0) * (z - z0) / (z1 - z0); n = 0
    for v in cup.data.vertices:
        z = v.co.z
        if z0 < z < z1:
            r = math.hypot(v.co.x, v.co.y); rb = body_r(z)
            if r > rb - .0004: v.co.x *= (rb - .00015) / r; v.co.y *= (rb - .00015) / r; n += 1
    print('SLEEVE off:', n, 'verts, r', round(r0 * 1000, 2), '→', round(r1 * 1000, 2), 'mm')
cup.location = vec(E('CUP_AT', '-0.075,0.0,0'))
for p in cup.data.polygons: p.use_smooth = True
bake(cup)

# ---- the Lansy icon: body and palm, the face (+z) stood up toward the camera (−y), leaning back on the cup
with bpy.data.libraries.load(ICON) as (s, d): d.objects = ['LANSY · continuous rounded body', 'LANSY · embedded hand sign']
body, hand = d.objects
for o in (body, hand): col.objects.link(o)
bpy.context.view_layer.update()
for o in (body, hand): mw = o.matrix_world.copy(); o.parent = None; o.data.transform(mw); o.matrix_world = Matrix()
W = float(E('ICON_W', .062)); k = W / 4.0   # the body is 4 units wide
R = (Matrix.Rotation(math.radians(float(E('ICON_ROLL', -5))), 4, 'Y') @ Matrix.Rotation(math.radians(90 - float(E('ICON_LEAN', 14))), 4, 'X')
     @ Matrix.Scale(k, 4))
for o in (body, hand): o.data.transform(R)
lo, hi = bbox([body, hand]); at = vec(E('ICON_AT', '-0.011,-0.046'))
for o in (body, hand): o.data.transform(Matrix.Translation(Vector((at.x - (lo.x + hi.x) / 2, at.y - (lo.y + hi.y) / 2, -lo.z))))
for o in (body, hand): bake(o)

# ---- the blob: our traced pen shape, a glass slab standing upright behind the cup and the icon, its foot sunk into the floor
ring = json.load(open(f"{ROOT}/blobs/blob-{E('BLOB', 'b')}-brush.geojson"))['features'][0]['geometry']['coordinates'][0]
if ring[0] == ring[-1]: ring = ring[:-1]
xs = [q[0] for q in ring]; ys = [q[1] for q in ring]; mx = (max(xs) + min(xs)) / 2
if E('BLOB_FLIP', '0') == '1': ring = [(2 * mx - x, y) for x, y in ring]
a_ = math.radians(float(E('BLOB_ROT', 0)))   # turned in its own plane (counter-clockwise), so its stepped edges face the sky
ring = [(x * math.cos(a_) - y * math.sin(a_), x * math.sin(a_) + y * math.cos(a_)) for x, y in ring]
xs = [q[0] for q in ring]; ys = [q[1] for q in ring]; mx = (max(xs) + min(xs)) / 2; T = float(E('BLOB_T', .008))
kb = float(E('BLOB_H')) / (max(ys) - min(ys)) if E('BLOB_H') else float(E('BLOB_W', .30)) / (max(xs) - min(xs))
bm = bmesh.new()
vs = [bm.verts.new(((x - mx) * kb, (y - min(ys)) * kb, 0)) for x, y in ring]
es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=es)
ex = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
bmesh.ops.translate(bm, verts=[v for v in ex['geom'] if isinstance(v, bmesh.types.BMVert)], vec=(0, 0, -T))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new('blob'); bm.to_mesh(me); bm.free(); blob = link_mesh('blob', me)
bc = vec(E('BLOB_AT', '0.0,0.06,0'))   # x, y of its centre; z of its lowest point (below the floor)
if E('BLOB_TOP', '.175'): bc.z = float(E('BLOB_TOP', '.175')) - (max(ys) - min(ys)) * kb   # or: its highest point, the rest sunk into the floor
blob.matrix_world = Matrix.Translation(bc) @ Matrix.Rotation(math.radians(float(E('BLOB_YAW', -6))), 4, 'Z') @ Matrix.Rotation(math.radians(90), 4, 'X')
bv = blob.modifiers.new('bevel', 'BEVEL'); bv.width = T * .35; bv.segments = 6; bv.limit_method = 'ANGLE'
with bpy.context.temp_override(object=blob, active_object=blob, selected_objects=[blob]): bpy.ops.object.modifier_apply(modifier=bv.name)
for f in me.polygons: f.use_smooth = True
wn = blob.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.mode = 'FACE_AREA'; wn.weight = 100; wn.keep_sharp = True
with bpy.context.temp_override(object=blob, active_object=blob, selected_objects=[blob]): bpy.ops.object.modifier_apply(modifier=wn.name)
bake(blob)

# ---- the wire: a calm voice wave (quiet, two soft bursts, quiet), drawn left to right between the blob and the icon
x0, x1 = (float(v) for v in E('WIRE_X', '-0.05,0.10').split(',')); wy, wz = (float(v) for v in E('WIRE_YZ', '0.035,0.084').split(','))
lam = float(E('WIRE_LAMBDA', .0062)); amp = float(E('WIRE_AMP', .017))
# a voice recording's look (ref-wire-wave.png): a low ripple, a burst under a bell-shaped envelope, a smaller second burst
bursts = [(float(c), float(w), float(h)) for c, w, h in (b.split(':') for b in E('WIRE_BURSTS', '.47:.11:1;.80:.07:.55').split(';'))]
def wave(t):
    env = float(E('WIRE_FLOOR', .08)) + sum(h * math.exp(-((t - c) / w) ** 2) for c, w, h in bursts)
    ramp = min(1, max(0, (t - .2) / .08))                       # straight out of the cup, then the wave starts
    return amp * env * ramp * math.sin(2 * math.pi * (t * (x1 - x0)) / lam)
N = 3000; cu = bpy.data.curves.new('wire', 'CURVE'); cu.dimensions = '3D'; sp = cu.splines.new('POLY'); sp.points.add(N - 1)
for i in range(N):
    t = i / (N - 1); sp.points[i].co = (x0 + t * (x1 - x0), wy, wz + wave(t), 1)
cu.bevel_depth = float(E('WIRE_R', .0007)); cu.bevel_resolution = 6; cu.use_fill_caps = True
wc = bpy.data.objects.new('wire_curve', cu); col.objects.link(wc); bpy.context.view_layer.update()
me = bpy.data.meshes.new_from_object(wc.evaluated_get(bpy.context.evaluated_depsgraph_get())); bpy.data.objects.remove(wc)
wire = link_mesh('wire', me)
for p in wire.data.polygons: p.use_smooth = True
bake(wire)

# ---- the floor: a table top that ends just behind the blob (above it the image is clear, for the backdrop)
bm = bmesh.new(); fy0, fy1 = -0.5, float(E('FLOOR_BACK', .12))
q = [bm.verts.new(p) for p in ((-.6, fy0, 0), (.6, fy0, 0), (.6, fy1, 0), (-.6, fy1, 0))]; bm.faces.new(q)
me = bpy.data.meshes.new('floor'); bm.to_mesh(me); bm.free(); floor = link_mesh('floor', me); bake(floor)

# ---- what the glass sees behind it: the backdrop's colour, for transmission only (the camera never sees it)
bg = E('BG', '1E3D2F'); bm = bmesh.new()
q = [bm.verts.new(p) for p in ((-1, .4, -.2), (1, .4, -.2), (1, .4, 1), (-1, .4, 1))]; bm.faces.new(q)
me = bpy.data.meshes.new('backdrop'); bm.to_mesh(me); bm.free(); back = link_mesh('backdrop', me)
bmm = bpy.data.materials.new('backdrop'); bmm.use_nodes = True; nt = bmm.node_tree; nt.nodes.clear()
em = nt.nodes.new('ShaderNodeEmission'); em.inputs[0].default_value = (*[lin(int(bg[i:i + 2], 16) / 255) for i in (0, 2, 4)], 1)
em.inputs[1].default_value = float(E('BG_E', 1)); oo = nt.nodes.new('ShaderNodeOutputMaterial'); nt.links.new(em.outputs[0], oo.inputs[0])
me.materials.append(bmm)
back.visible_camera = False; back.visible_diffuse = False; back.visible_glossy = E('BG_GLOSSY', '1') == '1'; back.visible_shadow = False; back.visible_volume_scatter = False

# ---- light: the BlenderKit thumbnailer's world and sun
with bpy.data.libraries.load(THUMB) as (s, d): d.worlds = ['World.001']
w = d.worlds[0]; sc.world = w
img = next(n.image for n in w.node_tree.nodes if n.type == 'TEX_ENVIRONMENT')
img.filepath = os.path.join(bpy.utils.resource_path('LOCAL'), 'datafiles/studiolights/world/interior.exr'); img.reload()
sun = bpy.data.objects.new('bk_sun', bpy.data.lights.new('bk_sun', 'SUN')); col.objects.link(sun)
sun.data.energy = float(E('SUN', 0)); sun.data.angle = 0.8726646
sun.matrix_world = Matrix(((0.1443, 0.0178, -0.9894, 0), (-0.2723, 0.962, -0.0224, 0), (0.9513, 0.2726, 0.1437, 0), (0, 0, 0, 1)))

# a big soft key from the front left (the faces turned to the camera stay lit, shadows soft), and a light behind the blob,
# unseen, that its frosted glass turns into a milky glow (as the draft's backlit slab)
lo_, hi_ = bbox([cup, body, blob]); C_ = (lo_ + hi_) / 2
key = bpy.data.objects.new('key', bpy.data.lights.new('key', 'AREA')); col.objects.link(key)
key.data.energy = float(E('KEY', 11)); key.data.size = float(E('KEY_SIZE', 1.2)); key.location = C_ + vec(E('KEY_AT', '-0.3,-0.6,0.3'))
key.rotation_euler = (C_ - key.location).to_track_quat('-Z', 'Y').to_euler()
if E('KEY_BLOB', '0') != '1':   # the key lights the blob's glass, never mirrors in it: one huge white panel turns the frost white
    kc = bpy.data.collections.new('key_receivers'); [kc.objects.link(o) for o in (cup, body, hand, wire, floor)]
    key.light_linking.receiver_collection = kc
if float(E('BACK', .08)) > 0:
    bl = bpy.data.objects.new('backlight', bpy.data.lights.new('backlight', 'AREA')); col.objects.link(bl)
    bl.data.energy = float(E('BACK', .08)); bl.data.shape = 'RECTANGLE'; bl.data.size = .5; bl.data.size_y = .3
    bl.location = Vector((C_.x + .05, .25, .12)); bl.rotation_euler = (Vector((C_.x, 0, .1)) - bl.location).to_track_quat('-Z', 'Y').to_euler()
    bl.visible_camera = False; bl.visible_glossy = False

# ---- materials, each mapped to its object as onto BlenderKit's preview ball (radius .654 m): object space and box UVs
# scaled by .654 / the object's radius, bump depths scaled back by the inverse, brushing given a direction
def load(spec):
    path, name = spec.split('::')
    with bpy.data.libraries.load(path) as (s, d): d.materials = [name]
    return d.materials[0]
def rad(o): return max(v.co.length for v in o.data.vertices)
def fit(m, o, tangent=None, k=1.0, relief=1.0):   # k: pattern finer by k; relief: bump depth scaled
    m = m.copy(); K = .654 / rad(o) * k; groups = set()
    def walk(nt):
        for n in list(nt.nodes):
            if n.type == 'TEX_COORD':
                for l in list(n.outputs['Object'].links):
                    vm = nt.nodes.new('ShaderNodeVectorMath'); vm.operation = 'SCALE'; vm.inputs['Scale'].default_value = K
                    nt.links.new(n.outputs['Object'], vm.inputs[0]); nt.links.new(vm.outputs[0], l.to_socket)
            if n.type == 'BUMP' and not n.inputs['Distance'].is_linked: n.inputs['Distance'].default_value *= relief / K
            if n.type == 'DISPLACEMENT' and not n.inputs['Scale'].is_linked: n.inputs['Scale'].default_value *= relief / K
            if tangent is not None and n.type == 'BSDF_PRINCIPLED' and not n.inputs['Tangent'].is_linked:
                cx = nt.nodes.new('ShaderNodeCombineXYZ'); cx.inputs[0].default_value, cx.inputs[1].default_value, cx.inputs[2].default_value = tangent
                nt.links.new(cx.outputs[0], n.inputs['Tangent'])
            if n.type == 'GROUP' and n.node_tree and n.node_tree.name not in groups:
                groups.add(n.node_tree.name); n.node_tree = n.node_tree.copy(); walk(n.node_tree)
    walk(m.node_tree)
    if 'UVMap' not in o.data.uv_layers: o.data.uv_layers.new(name='UVMap')
    bm = bmesh.new(); bm.from_mesh(o.data); uv = bm.loops.layers.uv['UVMap']
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i])); a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for l in f.loops: l[uv].uv = (l.vert.co[a] * K, l.vert.co[b] * K)
    bm.to_mesh(o.data); bm.free()
    o.data.materials.clear(); o.data.materials.append(m); return m
if E('CLAY') == '1':
    clay = bpy.data.materials.new('clay'); clay.use_nodes = True; pb = clay.node_tree.nodes['Principled BSDF']
    pb.inputs['Base Color'].default_value = (.5, .5, .5, 1); pb.inputs['Roughness'].default_value = .6
    for o in (cup, body, hand, blob, wire, floor): o.data.materials.clear(); o.data.materials.append(clay)
else:
    fit(load(E('CUP_MAT', f'{MATS}/ceramic-unglazed.blend::Ceramic Unglazed')), cup, k=float(E('CER_K', 2.5)), relief=float(E('CER_R', .5)))
    # our lime glass is authored on the Lansy icon (4 units across, radius ~2.83); GAIN calibrated to #9CDE45 (brooch_scene.py)
    fit(load(f'{MATS}/lansy-lime-glass80.blend::LANSY · 87E002 / fine frosted surface'), body, k=2.83 / .654)
    g3 = vec(E('GAIN', '1.30,1.42,0.12'))
    for n in body.data.materials[0].node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value = (*[min(1, n.inputs['Base Color'].default_value[i] * g3[i]) for i in range(3)], 1)
            n.inputs['Transmission Weight'].default_value = float(E('GLASS_T', .55))   # as in brooch_scene.py: the lime on #9CDE45, whites unclipped
    fit(load(f'{MATS}/porcelain.blend::Porcelain'), hand)
    fit(load(E('BLOB_MAT', f'{MATS}/frosted-glass.blend::Frosted Glass')), blob)
    al = fit(load(f'{MATS}/brushed-aluminium.blend::Brushed aluminium'), wire, tangent=(1, 0, 0))   # drawn wire: streaks along it
    def aniso(nt, seen=set()):
        for n in nt.nodes:
            if n.type == 'BSDF_PRINCIPLED' and not n.inputs['Anisotropic'].is_linked: n.inputs['Anisotropic'].default_value = .4
            if n.type == 'GROUP' and n.node_tree and n.node_tree.name not in seen: seen.add(n.node_tree.name); aniso(n.node_tree)
    aniso(al.node_tree)
    fit(load(E('FLOOR_MAT', f'{MATS}/chromatic-rainbow-spectrum-metal.blend::Chromatic Rainbow Spectrum Metal')), floor)

# ---- camera: low, near frontal, a touch from above; portrait 2:3
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); col.objects.link(cam); sc.camera = cam
cam.data.lens = float(E('LENS', 70)); cam.data.sensor_width = 36; cam.data.clip_start = .01
cam.location = vec(E('CAM', '-0.022,-0.476,0.153')); look = vec(E('LOOK', '-0.022,0.0,0.103'))
cam.rotation_euler = (look - cam.location).to_track_quat('-Z', 'Y').to_euler()

# ---- render, as the thumbnailer: Filmic Medium High Contrast, alpha
v = sc.view_settings; v.view_transform = E('VIEW', 'Standard'); v.look = E('LOOK_T', 'None'); v.exposure = float(E('EXPO', 0))   # Standard: Filmic/AgX dull the lime
r = sc.render; r.engine = 'CYCLES'; r.film_transparent = True
r.resolution_x = int(E('RES', 1000)); r.resolution_y = int(r.resolution_x * 1.5); r.resolution_percentage = 100
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'; r.image_settings.color_depth = '16'
c = sc.cycles; c.device = 'GPU'; c.samples = int(E('SAMPLES', 256)); c.use_denoising = True
c.max_bounces = 24; c.glossy_bounces = 16; c.transmission_bounces = 32; c.sample_clamp_indirect = 0; c.blur_glossy = 1.5
c.caustics_reflective = False; c.caustics_refractive = False
r.filepath = E('OUT', f'{ROOT}/check/cup-scene/draft.png')
if E('SAVE'): bpy.ops.wm.save_as_mainfile(filepath=E('SAVE'))
if E('NORENDER') != '1': bpy.ops.render.render(write_still=True)
print('RENDERED', r.filepath)
