# A ring of our coins (the disc with the icon in relief), as in the hero sketch: COUNT coins round an empty centre, each tilted
# on its own, seen frontally, on a card of one colour lit by the same studio. Run after studio_bk.py set up the coin (NORENDER=1):
#   Blender -b 3d/lansy-3d-test.blend -P 3d/studio_bk.py -P 3d/coin_ring.py
#   env (with studio_bk's MAT, MIRROR…): COUNT, RING (ring radius / coin radius), TILT (deg), CARD=hex, CARD_K=r,g,b, ASPECT, RES, OUT
import bpy, math, os, random
from mathutils import Vector, Matrix
S = bpy.app.driver_namespace['STUDIO']; sc = bpy.context.scene
objs, turn, cam = S['objs'], S['turn'], S['cam']
for o in objs: o.visible_shadow = False
# the coin's own size, in its flat frame (face up, centred at the origin)
flat = turn.inverted()
pts = [flat @ o.matrix_world @ v.co for o in objs for v in o.data.vertices]
rc = max(math.hypot(p.x, p.y) for p in pts)
# THICK_ADD (metres): the coin made thicker by lengthening its straight wall only — its front half moves forward, the back and
# both edge profiles stay as they are (no stretched hump), the icon rides on the moved face
TA = float(os.environ.get('THICK_ADD', 0))
if TA:
    base = objs[0]; F = flat @ base.matrix_world; Fi = F.inverted()
    bz = [(F @ v.co).z for v in base.data.vertices]; zm = (min(bz) + max(bz)) / 2
    for v in base.data.vertices:
        q = F @ v.co
        if q.z > zm: q.z += TA; v.co = Fi @ q
    for o in objs[1:]:
        Fo = flat @ o.matrix_world; o.data.transform(Fo.inverted() @ Matrix.Translation((0, 0, TA)) @ Fo)
# EDGE=1: the coin's wall and bevels split off as their own object in polished silver; a lime light behind the ring is linked to
# the edges only, so the lime gleam sits on the edges, as in the reference, and never on the brushed faces
EDGE_OBJ = None
if os.environ.get('EDGE', '1') == '1':
    import bmesh as _bm
    base = objs[0]; F3 = (flat @ base.matrix_world).to_3x3(); ez = float(os.environ.get('EDGE_Z', .75))
    me_e = base.data.copy(); me_e.name = 'coin_edge'
    for me_, keep_edge in ((me_e, True), (base.data, False)):
        bm = _bm.new(); bm.from_mesh(me_)
        bad = [f for f in bm.faces if (abs((F3 @ f.normal).normalized().z) < ez) != keep_edge]
        _bm.ops.delete(bm, geom=bad, context='FACES'); bm.to_mesh(me_); bm.free()
    EDGE_OBJ = bpy.data.objects.new('coin_edge', me_e); sc.collection.objects.link(EDGE_OBJ); EDGE_OBJ.matrix_world = base.matrix_world
    em = bpy.data.materials.new('M_coin_edge'); em.use_nodes = True; eb = em.node_tree.nodes['Principled BSDF']
    eb.inputs['Base Color'].default_value = (*[float(v) for v in os.environ.get('EDGE_COL', '.86,.83,.77').split(',')], 1)
    eb.inputs['Metallic'].default_value = 1; eb.inputs['Roughness'].default_value = float(os.environ.get('EDGE_R', .2))
    me_e.materials.clear(); me_e.materials.append(em); EDGE_OBJ.visible_shadow = False
    objs = objs + [EDGE_OBJ]
# SPIN=1: radial (spun) brushing on the coin's face — its 'Flat' UVs, which the studio's brushed shaders take their direction
# from, turned polar (u along the circle), so the grooves run in rings round the centre, as on a spun coin. FACE_ANISO: strength
if os.environ.get('SPIN', '1') == '1':
    import bmesh as _bm2
    base = objs[0]; F = flat @ base.matrix_world
    bm = _bm2.new(); bm.from_mesh(base.data); uvf = bm.loops.layers.uv.get('Flat')
    if uvf is not None:
        for f_ in bm.faces:
            for l in f_.loops:
                q = F @ l.vert.co; r_ = math.hypot(q.x, q.y); th = math.atan2(q.y, q.x)
                l[uvf].uv = (th * rc, r_)
        bm.to_mesh(base.data)
    bm.free()
    fa = os.environ.get('FACE_ANISO')
    if fa:
        for s_ in base.material_slots:
            if s_.material and s_.material.name != 'M_coin_edge':
                for n in s_.material.node_tree.nodes:
                    if n.type == 'BSDF_PRINCIPLED' and 'Anisotropic' in n.inputs and not n.inputs['Anisotropic'].is_linked and n.inputs['Anisotropic'].default_value > 0:
                        n.inputs['Anisotropic'].default_value = float(fa)
# FACE_TINT=r,g,b and FACE_ROUGH=+x: the coins' faces a warmer, more satin brushed metal (the reference's): the material's own
# base colour set, and the roughness its map range feeds raised
ft = os.environ.get('FACE_TINT'); fr = float(os.environ.get('FACE_ROUGH', 0))
if ft or fr:
    for m_ in {s_.material for o in objs for s_ in o.material_slots if s_.material and s_.material.name != 'M_coin_edge'}:
        for n in m_.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED' and ft and not n.inputs['Base Color'].is_linked:
                n.inputs['Base Color'].default_value = (*[float(v) for v in ft.split(',')], 1)
            if n.type == 'BSDF_PRINCIPLED' and fr:
                ri = n.inputs['Roughness']
                if ri.is_linked and ri.links[0].from_node.type == 'MAP_RANGE':
                    mr = ri.links[0].from_node; mr.inputs['To Min'].default_value += fr; mr.inputs['To Max'].default_value += fr
                elif not ri.is_linked: ri.default_value += fr
# the layout, read off the reference: each coin's place in the frame (x, y as shares of the frame, y down), where its face
# turns (the screen direction its normal leans to, degrees, 0 = right, 90 = up), how far it turns from the camera (degrees,
# from the ellipse's narrowness) and the icon's turn on the face
REF = [  # x,    y,    dir, tilt, roll   (fitted: ellipse axes and narrowness per coin; the face side from where its edge shows)
    (.350, .133,  65, 57,  -8), (.602, .126,  27, 60,   0), (.798, .234,   0, 58,   2), (.886, .451, -39, 58,  15),
    (.849, .679, 109, 60, -28), (.663, .835,  67, 58, -25), (.423, .844, 217, 58,  20), (.219, .734, 180, 56,   4),
    (.127, .518, 143, 57,  -5), (.173, .280, 108, 56,   6)]
DIAM = float(os.environ.get('DIAM', .22))            # a coin's width as a share of the frame
H = 2 * rc / DIAM * float(os.environ.get('MARGIN', 1.06))
O = Vector((0, 0, 0)); coins = []
ICONS = [o for o in objs if o is not objs[0] and o is not EDGE_OBJ]
ANIM = int(os.environ.get('ANIM', 0)); PIVS = []   # ANIM=frames: the ring's loop (see the end)   # one icon, or RING_ICONS' set: coin k takes ICONS[k % n]
for k, (u, v, a, t, rl) in enumerate(REF):
    p = Vector(((u - .5) * H, 0, (.5 - v) * H))
    n = (Vector((0, -1, 0)) * math.cos(math.radians(t)) + Vector((math.cos(math.radians(a)), 0, math.sin(math.radians(a)))) * math.sin(math.radians(t))).normalized()
    face = Matrix.Rotation(math.radians(90), 4, 'X')                       # face up → toward the camera (−Y), the icon upright
    lean = Vector((0, -1, 0)).rotation_difference(n).to_matrix().to_4x4()   # the shortest turn: the icon stays upright
    CF = Matrix.Translation(p) @ lean @ face @ Matrix.Rotation(math.radians(rl), 4, 'Z')   # the coin's own frame (face up = its z)
    M = CF @ flat
    piv = None
    if ANIM:   # each coin on its own pivot, at its centre, turning about the icon's vertical (the coin frame's y)
        piv = bpy.data.objects.new(f'coin_piv_{k}', None); sc.collection.objects.link(piv); piv.rotation_mode = 'QUATERNION'
        piv.location = p; piv.rotation_quaternion = CF.to_quaternion(); PIVS.append((piv, CF.to_quaternion(), k))
    for o in [objs[0], ICONS[k % len(ICONS)]] + ([EDGE_OBJ] if EDGE_OBJ is not None else []):
        d = o.copy(); d.data = o.data; sc.collection.objects.link(d); coins.append(d)
        if piv is None: d.matrix_world = M @ o.matrix_world
        else: d.parent = piv; d.matrix_parent_inverse = Matrix(); d.matrix_basis = flat @ o.matrix_world
R = H * .36
for o in objs: o.hide_render = True
# the reflector studio_bk made for one coin face is meaningless here; the ring takes the studio's light as it is
for o in sc.objects:
    if o.name.startswith('reflector'): o.hide_render = True
# the edge light: a big soft panel straight behind the ring, facing the camera, lime (RIM_COL), linked to the coins' edges only
RIM = float(os.environ.get('RIM', 40))
if RIM and (EDGE_OBJ is not None or os.environ.get('RIM_TEST')):
    ec = bpy.data.collections.new('coin_edges')
    for d in coins:
        if EDGE_OBJ is not None and d.data is EDGE_OBJ.data: ec.objects.link(d)
    L = bpy.data.objects.new('edge_light', bpy.data.lights.new('edge_light', 'AREA')); sc.collection.objects.link(L)
    L.data.shape = 'DISK'; L.data.size = H * float(os.environ.get('RIM_SIZE', 1.6)); L.data.energy = RIM
    L.data.color = [float(v) for v in os.environ.get('RIM_COL', '.61,.87,.27').split(',')]
    L.location = O + Vector((0, H * float(os.environ.get('RIM_D', .9)), 0)); L.rotation_euler = Vector((0, -1, 0)).to_track_quat('-Z', 'Y').to_euler()
    L.light_linking.receiver_collection = ec
    # reflection rays that happen to hit the lamp ignore linking; with MIS off, the lamp lights only by direct sampling, which
    # honours it — so the faces never see the lime
    try: L.data.cycles.use_multiple_importance_sampling = False
    except AttributeError: L.data.use_multiple_importance_sampling = False
# the key: a big soft box up left in front, seen only in the metal (glossy), so each face carries a soft light-to-dark sweep
KEY = float(os.environ.get('KEY', 25))
if KEY:
    K_ = bpy.data.objects.new('key', bpy.data.lights.new('key', 'AREA')); sc.collection.objects.link(K_)
    K_.data.shape = 'DISK'; K_.data.size = R * float(os.environ.get('KEY_SIZE', 1)); K_.data.energy = KEY
    K_.location = O + Vector((-R * 1.6, -R * 2.6, R * 1.8)); K_.rotation_euler = (O - K_.location).to_track_quat('-Z', 'Y').to_euler()
    K_.visible_diffuse = False
S['sun'].data.energy *= float(os.environ.get('SUN_K', 1))   # the studio's sun, dimmable for the ring
# WORLD=grad: a plain studio round the ring instead of the room HDRI — light above, dark below, softly graded, slightly warm,
# so faces turned up read light and faces turned down dark, the same on every side of the ring (as in a product shot)
if os.environ.get('WORLD') == 'grad':
    nt = sc.world.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground'); tc = nt.nodes.new('ShaderNodeTexCoord')
    sp = nt.nodes.new('ShaderNodeSeparateXYZ'); ramp = nt.nodes.new('ShaderNodeValToRGB')
    nt.links.new(tc.outputs['Generated'], sp.inputs[0]); nt.links.new(sp.outputs['Z'], ramp.inputs['Fac'])
    e0, e1 = ramp.color_ramp.elements; e0.position, e1.position = .35, .75
    lo_ = [float(v) for v in os.environ.get('GRAD_LO', '.012,.022,.017').split(',')]; hi_ = [float(v) for v in os.environ.get('GRAD_HI', '1,.97,.92').split(',')]
    e0.color = (*lo_, 1); e1.color = (*hi_, 1)
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = float(os.environ.get('GRAD_E', 1))
    nt.links.new(bg.outputs[0], out.inputs['Surface'])
# the studio's world, dimmed (WORLD_K), so the room's grey reflections don't flatten the metal
for n in sc.world.node_tree.nodes:   # WORLD_ROT/WORLD_TILT (deg): turn the studio round the ring, to even the coins' tones
    if n.type == 'MAPPING':
        n.inputs['Rotation'].default_value[2] += math.radians(float(os.environ.get('WORLD_ROT', 0)))
        n.inputs['Rotation'].default_value[0] += math.radians(float(os.environ.get('WORLD_TILT', 0)))
for n in sc.world.node_tree.nodes:   # WORLD_SAT: the studio's colour (0 = grey), so every coin takes the same hue
    if n.type == 'HUE_SAT' and os.environ.get('WORLD_SAT'): n.inputs['Saturation'].default_value = float(os.environ['WORLD_SAT'])
wk = float(os.environ.get('WORLD_K', 1))
for n in sc.world.node_tree.nodes:
    if n.type == 'BACKGROUND': n.inputs['Strength'].default_value *= wk
# the frontal camera: looking along +Y at the ring's centre, long lens, framing the ring with a margin
asp = float(os.environ.get('ASPECT', 1)); r_ = sc.render; r_.resolution_x = int(os.environ.get('RES', 2064)); r_.resolution_y = int(r_.resolution_x / asp)
cam.data.shift_x = cam.data.shift_y = 0
if os.environ.get('PERSP'):   # a real lens, as in a product shot: the near edges of the ring swell a little
    cam.data.type = 'PERSP'; cam.data.lens = float(os.environ['PERSP']); cam.data.sensor_fit = 'VERTICAL'; cam.data.sensor_height = 24
    dist = (H / 2) / math.tan(math.atan(12 / cam.data.lens))
else:
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = H * max(1, asp); dist = H * 4
dist = dist; cam.location = O + Vector((0, -dist, 0)); cam.rotation_euler = Vector((0, 1, 0)).to_track_quat('-Z', 'Y').to_euler()
# the card: one colour, square to the camera behind the ring, lit by the same studio; calibrated gain lands it on the hex
hx = os.environ.get('RING_CARD', '33694F').lstrip('#'); kk = [float(v) for v in os.environ.get('CARD_K', '1,1,1').split(',')]
lin = lambda c: c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
bpy.ops.mesh.primitive_plane_add(size=H * 4, location=O + Vector((0, rc * 3, 0)), rotation=(math.radians(90), 0, 0))
card = bpy.context.active_object; card.name = 'ring_card'   # the coins reflect it: their faces and edges take its green
cm = bpy.data.materials.new('M_ring_card'); cm.use_nodes = True; cb = cm.node_tree.nodes['Principled BSDF']
vm = cm.node_tree.nodes.new('ShaderNodeVectorMath'); vm.operation = 'MULTIPLY'
vm.inputs[0].default_value = [lin(int(hx[i:i + 2], 16) / 255) for i in (0, 2, 4)]; vm.inputs[1].default_value = kk
cm.node_tree.links.new(vm.outputs[0], cb.inputs['Base Color']); cb.inputs['Roughness'].default_value = .7; cb.inputs['Specular IOR Level'].default_value = 0
card.data.materials.append(cm)
# CARD_CAM=0 (default): the camera does not see the card — the coins keep reflecting it, and the PNG comes out on alpha, so the
# page lays it on the exact flat colour
card.visible_camera = os.environ.get('CARD_CAM', '0') == '1'; card.visible_shadow = False; card.visible_glossy = os.environ.get('CARD_GLOSSY', '0') == '1'   # never blocks the edge light; not mirrored in the metal unless asked
# MASK=1: render the edges' mask instead (edges white, everything else black, flat), to composite the lime-lit edges over a
# render without the lime light — the gleam lands on the edges and nowhere else
if os.environ.get('MASK') == '1' and EDGE_OBJ is not None:
    def flat_mat(name, v):
        m_ = bpy.data.materials.new(name); m_.use_nodes = True; t_ = m_.node_tree; t_.nodes.clear()
        e_ = t_.nodes.new('ShaderNodeEmission'); e_.inputs[0].default_value = (v, v, v, 1); o_ = t_.nodes.new('ShaderNodeOutputMaterial')
        t_.links.new(e_.outputs[0], o_.inputs[0]); return m_
    W_, K_ = flat_mat('mask_w', 1), flat_mat('mask_k', 0)
    for o in sc.objects:
        if o.type != 'MESH' or o.hide_render: continue
        o.material_slots and None
        me_ = o.data
        if me_.users > 1 and o.data is not EDGE_OBJ.data: pass
    EDGE_OBJ.data.materials.clear(); EDGE_OBJ.data.materials.append(W_)
    for me_ in {o.data for o in sc.objects if o.type == 'MESH' and o.data is not EDGE_OBJ.data}:
        me_.materials.clear(); me_.materials.append(K_)
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'; sc.cycles.samples = 16
# ANIM=L: the swirl — a loop of L frames at 30 fps in which every coin makes the Lansy icon's own turn (3d/lansy_spin_curve.json:
# a slow start, one full turn, an overshoot and a settle) about its own vertical axis, one coin after the other round the ring,
# each L/10 frames after the last: a wave of turns runs round and round. A full turn ends where it began, so the loop is seamless
if ANIM:
    import json
    from mathutils import Quaternion
    curve = [r[2] for r in json.load(open(os.path.join(os.path.dirname(os.path.abspath(bpy.data.filepath)), 'lansy_spin_curve.json')))]
    n = len(PIVS); step = ANIM / n
    for piv, q0, k in PIVS:
        for fr in range(ANIM):
            u = int(round((fr - k * step))) % ANIM; ang = curve[u] if u < len(curve) else curve[-1]
            piv.rotation_quaternion = q0 @ Quaternion((0, 1, 0), ang); piv.keyframe_insert('rotation_quaternion', frame=fr)
    sc.frame_start, sc.frame_end = int(os.environ.get('F0', 0)), int(os.environ.get('F1', ANIM - 1)); sc.render.fps = 30
    sc.render.use_overwrite = False   # a crashed run resumes where it stopped
    r_.filepath = os.environ['OUT'] + '/f_'; r_.image_settings.color_depth = '8'
    bpy.ops.render.render(animation=True); print('RENDERED ring', len(REF), 'anim', ANIM, r_.filepath)
else:
    r_.filepath = os.environ['OUT']; bpy.ops.render.render(write_still=True); print('RENDERED ring', len(REF), r_.filepath)
