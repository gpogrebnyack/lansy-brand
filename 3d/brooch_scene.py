# The "brooch" composition from the Codex board (3d/gen/ref-fav-6.png), rebuilt with our meshes and materials: our blob
# (blobs/blob-<BLOB>-brush.geojson) as a flat slab in Ceramic Unglazed against the wall, the Lansy icon's body (the squircle)
# in our lime frosted glass 80%, a ring in Brushed aluminium as thick as our icons' strokes, and an arc in Porcelain.
# The wall is a shadow catcher: the image is on alpha, the objects' soft shadows stay in it. Light: BlenderKit's
# material-preview studio (its world and sun), as in studio_bk.py. Frontal camera, 200 mm, square.
# Blender -b --factory-startup -P 3d/brooch_scene.py      env: OUT RES SAMPLES BLOB CLAY=1 WALL=hex (what the glass sees)
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
def place(o, centre, y_back):   # its bbox centre to (x, z) of centre, its back face at y = y_back (the wall is y = 0, camera at −y)
    lo, hi = bbox([o]); c = (lo + hi) / 2
    o.data.transform(Matrix.Translation(Vector((centre.x - c.x, y_back - hi.y, centre.y - c.z))))
def torus(name, R, r, a0=0, a1=360, seg=256, rseg=32):   # in the xz plane, facing −y; a partial one gets round caps
    bm = bmesh.new(); full = (a1 - a0) >= 360; n = seg if full else seg + 1; rings = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / seg); c = Vector((R * math.cos(a), 0, R * math.sin(a))); d = Vector((math.cos(a), 0, math.sin(a)))
        rings.append([bm.verts.new(c + r * (math.cos(b) * d + math.sin(b) * Vector((0, 1, 0)))) for b in (2 * math.pi * j / rseg for j in range(rseg))])
    for i in range(n if full else n - 1):
        A, B = rings[i], rings[(i + 1) % n]
        for j in range(rseg): bm.faces.new((A[j], A[(j + 1) % rseg], B[(j + 1) % rseg], B[j]))
    if not full:   # hemispherical caps
        for end, sgn in ((0, -1), (n - 1, 1)):
            a = math.radians(a0 if end == 0 else a1); c = Vector((R * math.cos(a), 0, R * math.sin(a)))
            t = Vector((-math.sin(a), 0, math.cos(a))) * sgn; d = Vector((math.cos(a), 0, math.sin(a))); prev = rings[end]
            for k in range(1, 9):
                ph = math.pi / 2 * k / 8
                if k < 8:
                    cur = [bm.verts.new(c + t * r * math.sin(ph) + r * math.cos(ph) * (math.cos(b) * d + math.sin(b) * Vector((0, 1, 0)))) for b in (2 * math.pi * j / rseg for j in range(rseg))]
                    for j in range(rseg):
                        q = (prev[j], prev[(j + 1) % rseg], cur[(j + 1) % rseg], cur[j]); bm.faces.new(q if sgn > 0 else q[::-1])
                    prev = cur
                else:
                    tip = bm.verts.new(c + t * r)
                    for j in range(rseg):
                        q = (prev[j], prev[(j + 1) % rseg], tip); bm.faces.new(q if sgn > 0 else q[::-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth = True
    return link_mesh(name, me)

# layout, in metres: x right, z up, centres measured off the reference (3d/gen/ref-fav-6.png), the composition ~8 cm across
# ---- the blob: a ceramic slab flat on the wall, its stepped edge up
if E('SLAB', 'stairs') == 'stairs':   # the reference's stepped slab: a staircase band, outline traced off it (px, 1 px = 0.1 mm)
    ring = [(170, 665), (170, 425), (295, 425), (295, 305), (390, 305), (390, 180), (540, 180), (540, 55), (735, 55), (735, 480),
            (600, 480), (600, 560), (460, 560), (460, 620), (330, 620), (330, 665)]
    ring = [(x, -y) for x, y in ring]   # y up
else:   # or one of our blobs (BLOB)
    ring = json.load(open(f"{ROOT}/blobs/blob-{E('BLOB', 'b')}-brush.geojson"))['features'][0]['geometry']['coordinates'][0]
    if ring[0] == ring[-1]: ring = ring[:-1]
a_ = math.radians(float(E('BLOB_ROT', 0)))
ring = [(x * math.cos(a_) - y * math.sin(a_), x * math.sin(a_) + y * math.cos(a_)) for x, y in ring]
xs = [q[0] for q in ring]; ys = [q[1] for q in ring]; kb = float(E('BLOB_W', .0565)) / (max(xs) - min(xs)); T = float(E('BLOB_T', .006))
bm = bmesh.new()
vs = [bm.verts.new(((x - min(xs)) * kb, 0, (y - min(ys)) * kb)) for x, y in ring]
es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=es)
ex = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
bmesh.ops.translate(bm, verts=[v for v in ex['geom'] if isinstance(v, bmesh.types.BMVert)], vec=(0, T, 0))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new('blob'); bm.to_mesh(me); bm.free(); blob = link_mesh('blob', me)
bv = blob.modifiers.new('bevel', 'BEVEL'); bv.width = T * .3; bv.segments = 5; bv.limit_method = 'ANGLE'
with bpy.context.temp_override(object=blob, active_object=blob, selected_objects=[blob]): bpy.ops.object.modifier_apply(modifier=bv.name)
for f in me.polygons: f.use_smooth = True
wn = blob.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.mode = 'FACE_AREA'; wn.weight = 100; wn.keep_sharp = True
with bpy.context.temp_override(object=blob, active_object=blob, selected_objects=[blob]): bpy.ops.object.modifier_apply(modifier=wn.name)
place(blob, vec(E('BLOB_AT', '-0.012,0.0104')), 0.0)

# ---- the squircle: a superellipse slab (n = 4, the Lansy icon's corner), pillowy rounded edges, face to the camera
SQW = float(E('SQ', .042)); SQT = float(E('SQ_T', .010)); nexp = float(E('SQ_N', 4)); bm = bmesh.new(); pts = []
for i in range(256):
    t = 2 * math.pi * i / 256; c_, s_ = math.cos(t), math.sin(t)
    pts.append(bm.verts.new((SQW / 2 * math.copysign(abs(c_) ** (2 / nexp), c_), 0, SQW / 2 * math.copysign(abs(s_) ** (2 / nexp), s_))))
es = [bm.edges.new((pts[i], pts[(i + 1) % len(pts)])) for i in range(len(pts))]
bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=es)
ex = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
bmesh.ops.translate(bm, verts=[v for v in ex['geom'] if isinstance(v, bmesh.types.BMVert)], vec=(0, SQT, 0))
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new('squircle'); bm.to_mesh(me); bm.free(); sq = link_mesh('squircle', me)
bv = sq.modifiers.new('bevel', 'BEVEL'); bv.width = SQT * .42; bv.segments = 10; bv.limit_method = 'ANGLE'; bv.profile = .5
with bpy.context.temp_override(object=sq, active_object=sq, selected_objects=[sq]): bpy.ops.object.modifier_apply(modifier=bv.name)
for f in me.polygons: f.use_smooth = True
wn = sq.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.mode = 'FACE_AREA'; wn.weight = 100; wn.keep_sharp = True
with bpy.context.temp_override(object=sq, active_object=sq, selected_objects=[sq]): bpy.ops.object.modifier_apply(modifier=wn.name)
place(sq, vec(E('SQ_AT', '0.0144,0.0077')), -T - .0008)

# ---- the ring: brushed aluminium, its tube as thick as our icons' strokes against their size (~7.5 % of the ring)
RD = float(E('RING_D', .044)); rt = RD * float(E('RING_K', .075)) / 2
rg = torus('ring', RD / 2 - rt, rt); place(rg, vec(E('RING_AT', '0.0023,0.0006')), -T - .0008 - SQT - .0015)

# ---- the arc: a thick porcelain tube, 150°, open side up, in front of the slab's foot
AR = float(E('ARC_R', .03)); ar_ = float(E('ARC_T', .0036)); half = float(E('ARC_DEG', 90)) / 2
arc = torus('arc', AR, ar_, 270 - half, 270 + half); place(arc, vec(E('ARC_AT', '0.003,-0.025')), -T - .001)
for o in (blob, sq, rg, arc): bake(o)

# ---- the wall: a shadow catcher (alpha out, shadows kept); what the glass sees is its colour
bm = bmesh.new(); q = [bm.verts.new(p) for p in ((-.5, .0005, -.5), (.5, .0005, -.5), (.5, .0005, .5), (-.5, .0005, .5))]; bm.faces.new(q)
me = bpy.data.meshes.new('wall'); bm.to_mesh(me); bm.free(); wall = link_mesh('wall', me); wall.is_shadow_catcher = True
wm = bpy.data.materials.new('wall'); wm.use_nodes = True; pb = wm.node_tree.nodes['Principled BSDF']; hx = E('WALL', 'F2EFE9')
pb.inputs['Base Color'].default_value = (*[lin(int(hx[i:i + 2], 16) / 255) for i in (0, 2, 4)], 1); pb.inputs['Roughness'].default_value = .8
me.materials.append(wm)

# ---- light: the BlenderKit thumbnailer's world and sun
with bpy.data.libraries.load(THUMB) as (s, d): d.worlds = ['World.001']
w = d.worlds[0]; sc.world = w
img = next(n.image for n in w.node_tree.nodes if n.type == 'TEX_ENVIRONMENT')
img.filepath = os.path.join(bpy.utils.resource_path('LOCAL'), 'datafiles/studiolights/world/interior.exr'); img.reload()
sun = bpy.data.objects.new('bk_sun', bpy.data.lights.new('bk_sun', 'SUN')); col.objects.link(sun)
sun.data.energy = float(E('SUN', 0)); sun.data.angle = 0.8726646
sun.matrix_world = Matrix(((0.1443, 0.0178, -0.9894, 0), (-0.2723, 0.962, -0.0224, 0), (0.9513, 0.2726, 0.1437, 0), (0, 0, 0, 1)))
# the thumbnailer's sun points along the preview's view; here, frontal on a wall, it comes from the upper left and in front
sun.rotation_euler = (math.radians(float(E('SUN_EL', 50))), 0, math.radians(float(E('SUN_AZ', -35))))

# a big soft key from the upper left, in front (the sun alone leaves the faces turned to the camera dim and the shadows hard)
if float(E('KEY', 11)) > 0:
    lo_, hi_ = bbox([blob, sq, rg, arc]); C_ = (lo_ + hi_) / 2
    key = bpy.data.objects.new('key', bpy.data.lights.new('key', 'AREA')); col.objects.link(key)
    key.data.energy = float(E('KEY', 11)); key.data.size = float(E('KEY_SIZE', 1.2)); key.location = C_ + vec(E('KEY_AT', '-0.2,-0.6,0.3'))
    key.rotation_euler = (C_ - key.location).to_track_quat('-Z', 'Y').to_euler()

# ---- materials, each mapped to its object as onto BlenderKit's preview ball (radius .654 m)
def load(spec):
    path, name = spec.split('::')
    with bpy.data.libraries.load(path) as (s, d): d.materials = [name]
    return d.materials[0]
def fit(m, o, aniso=None, k=1.0, relief=1.0):   # k: pattern finer by k; relief: bump depth scaled
    m = m.copy(); K = .654 / max(v.co.length for v in o.data.vertices) * k; groups = set()
    def walk(nt):
        for n in list(nt.nodes):
            if n.type == 'TEX_COORD':
                for l in list(n.outputs['Object'].links):
                    vm = nt.nodes.new('ShaderNodeVectorMath'); vm.operation = 'SCALE'; vm.inputs['Scale'].default_value = K
                    nt.links.new(n.outputs['Object'], vm.inputs[0]); nt.links.new(vm.outputs[0], l.to_socket)
            if n.type == 'BUMP' and not n.inputs['Distance'].is_linked: n.inputs['Distance'].default_value *= relief / K
            if n.type == 'DISPLACEMENT' and not n.inputs['Scale'].is_linked: n.inputs['Scale'].default_value *= relief / K
            if aniso is not None and n.type == 'BSDF_PRINCIPLED' and not n.inputs['Anisotropic'].is_linked:
                n.inputs['Anisotropic'].default_value = aniso
                if not n.inputs['Tangent'].is_linked:   # a ring brushed round, as spun
                    tg = nt.nodes.new('ShaderNodeTangent'); tg.direction_type = 'RADIAL'; tg.axis = 'Y'; nt.links.new(tg.outputs[0], n.inputs['Tangent'])
            if n.type == 'GROUP' and n.node_tree and n.node_tree.name not in groups:
                groups.add(n.node_tree.name); n.node_tree = n.node_tree.copy(); walk(n.node_tree)
    walk(m.node_tree)
    if 'UVMap' not in o.data.uv_layers: o.data.uv_layers.new(name='UVMap')
    bm = bmesh.new(); bm.from_mesh(o.data); uv = bm.loops.layers.uv['UVMap']
    for f in bm.faces:
        ax = max(range(3), key=lambda i: abs(f.normal[i])); a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for l in f.loops: l[uv].uv = (l.vert.co[a] * K, l.vert.co[b] * K)
    bm.to_mesh(o.data); bm.free()
    o.data.materials.clear(); o.data.materials.append(m)
if E('CLAY') == '1':
    clay = bpy.data.materials.new('clay'); clay.use_nodes = True; pb = clay.node_tree.nodes['Principled BSDF']
    pb.inputs['Base Color'].default_value = (.5, .5, .5, 1); pb.inputs['Roughness'].default_value = .6
    for o in (blob, sq, rg, arc): o.data.materials.clear(); o.data.materials.append(clay)
else:
    fit(load(f'{MATS}/ceramic-unglazed.blend::Ceramic Unglazed'), blob, k=float(E('CER_K', 2.5)), relief=float(E('CER_R', .5)))
    # our lime glass is authored on the Lansy icon (4 units across, radius ~2.83): its grain and relief mapped to that size
    fit(load(f'{MATS}/lansy-lime-glass80.blend::LANSY · 87E002 / fine frosted surface'), sq, k=2.83 / .654)
    gm = sq.data.materials[0].node_tree   # GLASS_T: transmission; DENSITY: the inner tint (lower = clearer through thick glass)
    g3 = vec(E('GAIN', '1.30,1.42,0.12'))           # GAIN: per-channel gain on its colour, found by calibration against #9CDE45
    for n in gm.nodes:
        if n.type == 'BSDF_PRINCIPLED': n.inputs['Base Color'].default_value = (*[min(1, n.inputs['Base Color'].default_value[i] * g3[i]) for i in range(3)], 1)
        if n.type == 'BSDF_PRINCIPLED': n.inputs['Transmission Weight'].default_value = float(E('GLASS_T', .55))   # .55: the lime lands on #9CDE45 with the whites unclipped
        if n.type == 'VOLUME_ABSORPTION' and E('DENSITY'): n.inputs['Density'].default_value = float(E('DENSITY'))
    fit(load(f'{MATS}/brushed-aluminium.blend::Brushed aluminium'), rg, aniso=.4)
    fit(load(f'{MATS}/porcelain.blend::Porcelain'), arc)

# ---- camera: frontal, 200 mm, square
cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); col.objects.link(cam); sc.camera = cam
cam.data.lens = 200; cam.data.sensor_width = 32; cam.data.clip_start = .05
lo, hi = bbox([blob, sq, rg, arc]); C = (lo + hi) / 2; span = max(hi.x - lo.x, hi.z - lo.z) * float(E('MARGIN', 1.35))
el = math.radians(float(E('CAM_EL', 4))); dist = span / 32 * 200
cam.location = C + Vector((0, -math.cos(el), math.sin(el))) * dist
cam.rotation_euler = (C - cam.location).to_track_quat('-Z', 'Y').to_euler()

v = sc.view_settings; v.view_transform = E('VIEW', 'Standard'); v.look = E('LOOK_T', 'None')   # Standard: Filmic/AgX dull the lime; v.exposure = float(E('EXPO', 0))
r = sc.render; r.engine = 'CYCLES'; r.film_transparent = True; r.resolution_x = r.resolution_y = int(E('RES', 1200)); r.resolution_percentage = 100
r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'; r.image_settings.color_depth = '16'
c = sc.cycles; c.device = 'GPU'; c.samples = int(E('SAMPLES', 256)); c.use_denoising = True
c.max_bounces = 24; c.glossy_bounces = 16; c.transmission_bounces = 32; c.sample_clamp_indirect = 0; c.blur_glossy = 1.5
c.caustics_reflective = False; c.caustics_refractive = False
r.filepath = E('OUT', f'{ROOT}/check/brooch/draft.png')
if E('NORENDER') != '1': bpy.ops.render.render(write_still=True)
print('RENDERED', r.filepath)
