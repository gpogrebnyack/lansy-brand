# BlenderKit's own material-preview studio (blendfiles/material_thumbnailer_cycles.blend from the add-on), rebuilt around our meshes:
# its world (Blender's interior.exr, desaturated through curves, strength .25), its one soft sun (50° disc, from the left),
# its camera direction and 200 mm lens, Filmic Medium High Contrast, glossy blur 1.5, transparent film → PNG with alpha.
# Blender -b 3d/lansy-3d-test.blend -P 3d/studio_bk.py
#   env: TARGET=icon|disc|disc_flat|cup|blobicon (BLOB=a|b|kept BLOB_W BLOB_T BLOB_GAP BLOB_OFF=x,y BLOB_MAT POSE CAM_EL GLASS_R BLOB_FACE) ASPECT=w/h  MAP=ball|own  REFLECT=1|0  REFLECT_E=strength  TURN=deg  MSCALE=pattern scale  MAT="path.blend::Material name" | clay (default: a neutral polished metal)  TS=texture size, m  OUT=file  RES=px
import bpy, bmesh, math, os
from mathutils import Vector, Matrix, Quaternion
ROOT = os.path.dirname(os.path.abspath(__file__))
THUMB = ROOT + '/dl/thumbnailer/material_thumbnailer_cycles.blend'
sc = bpy.context.scene
TARGET = os.environ.get('TARGET', 'icon')
# the icon alone is the coin's own icon with the coin hidden: the same mesh, place, framing and material space as on the coin
names = {'icon': ['disc_base', 'disc_icon_' + os.environ.get('ICON', 'full')], 'disc': ['disc_base'] + (['disc_icon_' + n for n in os.environ['RING_ICONS'].split(',')] if os.environ.get('RING_ICONS') else ['disc_icon_bevel']),   # RING_ICONS: icons for the coin ring, one per coin in turn 'disc_flat': ['disc_base_flat', 'disc_icon_flat'],
         'cup': ['cup_tripo'], 'blobicon': ['disc_base', 'disc_icon_' + os.environ.get('ICON', 'round')]}[TARGET]
if TARGET == 'cup' and 'cup_tripo' not in bpy.data.objects:   # the generated cup, prepared by prep_cup.py, standing at the origin
    with bpy.data.libraries.load(f'{ROOT}/models/cup_tripo.blend') as (src, dst): dst.objects = ['cup_tripo']
    sc.collection.objects.link(dst.objects[0])
for n in names:   # rubric icons built by rubric_icons.py, loaded on demand
    RB = os.environ.get('RUBRIC_BLEND', f'{ROOT}/models/rubric_icons.blend')
    if n not in bpy.data.objects and os.path.exists(RB):
        with bpy.data.libraries.load(RB) as (src, dst): dst.objects = [n] if n in src.objects else []
        for o in dst.objects: sc.collection.objects.link(o)
objs = [bpy.data.objects[n] for n in names]

# TARGET=blobicon: the coin's icon in front of our blob (BLOB=a|b|kept, drawn with our pen, traced to blobs/blob-*-brush.geojson)
# as a thin plate behind it, in the icon's own flat frame; the icon takes MAT, the blob BLOB_MAT (dark frosted glass by default)
BLOB_OBJ = None
if TARGET == 'blobicon':
    import json
    ic = bpy.data.objects['disc_icon_' + os.environ.get('ICON', 'round')]; bpy.context.view_layer.update()
    ipts = [ic.matrix_world @ v.co for v in ic.data.vertices]
    ic0 = (Vector([min(q[i] for q in ipts) for i in range(3)]) + Vector([max(q[i] for q in ipts) for i in range(3)])) / 2
    Li = Matrix.Translation(ic0) @ Matrix.Rotation(math.radians(78), 4, 'X')
    fl = [Li.inverted() @ q for q in ipts]
    iw = max(q.x for q in fl) - min(q.x for q in fl); zb = min(q.z for q in fl)
    ring = json.load(open(f"{ROOT}/blobs/blob-{os.environ.get('BLOB', 'a')}-brush.geojson"))['features'][0]['geometry']['coordinates'][0]
    if ring[0] == ring[-1]: ring = ring[:-1]
    xs = [q[0] for q in ring]; ys = [q[1] for q in ring]; bw = max(xs) - min(xs); bh = max(ys) - min(ys)
    k = iw * float(os.environ.get('BLOB_W', 2.3)) / bw; mx = (max(xs) + min(xs)) / 2; my = (max(ys) + min(ys)) / 2
    T = float(os.environ.get('BLOB_T', .004)); gap = float(os.environ.get('BLOB_GAP', .012))
    ox, oy = (float(v) for v in os.environ.get('BLOB_OFF', '0,0').split(','))
    bm = bmesh.new()
    vs = [bm.verts.new(((x - mx) * k + ox * iw, (y - my) * k + oy * iw, zb - gap)) for x, y in ring]   # geojson y up
    es = [bm.edges.new((vs[i], vs[(i + 1) % len(vs)])) for i in range(len(vs))]
    bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=es)
    ex = bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    bmesh.ops.translate(bm, verts=[v for v in ex['geom'] if isinstance(v, bmesh.types.BMVert)], vec=(0, 0, -T))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new('blob_plate'); bm.to_mesh(me); bm.free(); me.transform(Li)
    BLOB_OBJ = bpy.data.objects.new('blob_plate', me); sc.collection.objects.link(BLOB_OBJ)
    bv = BLOB_OBJ.modifiers.new('bevel', 'BEVEL'); bv.width = T * float(os.environ.get('BLOB_BEVEL', .35)); bv.segments = 6; bv.limit_method = 'ANGLE'
    with bpy.context.temp_override(object=BLOB_OBJ, active_object=BLOB_OBJ, selected_objects=[BLOB_OBJ]): bpy.ops.object.modifier_apply(modifier=bv.name)
    # smooth shading for the bevel, while the big flat faces stay flat: weighted normals by face area (no shading streaks
    # from the long fill triangles)
    for f in me.polygons: f.use_smooth = True
    wn = BLOB_OBJ.modifiers.new('wn', 'WEIGHTED_NORMAL'); wn.mode = 'FACE_AREA'; wn.weight = 100; wn.keep_sharp = True
    with bpy.context.temp_override(object=BLOB_OBJ, active_object=BLOB_OBJ, selected_objects=[BLOB_OBJ]): bpy.ops.object.modifier_apply(modifier=wn.name)
    objs = [ic, BLOB_OBJ]

# the scene: only the target meshes; no lights, floor or cyc of ours
for o in list(sc.objects):
    if o.type == 'LIGHT': bpy.data.objects.remove(o, do_unlink=True)
    elif o.type == 'MESH': o.hide_render = o not in objs
if TARGET in ('icon', 'blobicon'): bpy.data.objects['disc_base'].hide_render = True
bpy.context.view_layer.update()

# the world, appended as is; its image points at Blender's bundled interior.exr
with bpy.data.libraries.load(THUMB) as (src, dst): dst.worlds = ['World.001']
w = dst.worlds[0]; sc.world = w
img = next(n.image for n in w.node_tree.nodes if n.type == 'TEX_ENVIRONMENT')
img.filepath = os.path.join(bpy.utils.resource_path('LOCAL'), 'datafiles/studiolights/world/interior.exr'); img.reload()

# the sun: same direction, energy and angle as the thumbnailer's
sun = bpy.data.objects.new('bk_sun', bpy.data.lights.new('bk_sun', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 8; sun.data.angle = 0.8726646
sun.matrix_world = Matrix(((0.1443, 0.0178, -0.9894, 0), (-0.2723, 0.962, -0.0224, 0), (0.9513, 0.2726, 0.1437, 0), (0, 0, 0, 1)))

# MIRROR=1 (default): the whole studio mirrored left↔right in 3D, so the object faces left and the light comes from the right:
# the camera and the sun cross over, the world is mirrored (its mapping scaled −1 in x), the turn and the material space too
MX = Matrix.Diagonal((-1, 1, 1)); MIRROR = os.environ.get('MIRROR', '0' if TARGET == 'blobicon' else '1') == '1'   # the composition is frontal: no mirror
if MIRROR:
    sun.matrix_world = (MX @ sun.matrix_world.to_3x3() @ MX).to_4x4()
    for n in w.node_tree.nodes:
        if n.type == 'MAPPING': n.inputs['Scale'].default_value[0] *= -1

# Object space for materials. MAP=ball (default): each target gets exactly the object space the preview ball has in the
# thumbnailer: origin at its centre, the ball's rotation, and its size mapped to radius 1, so a BlenderKit material lands on
# it as on the preview (heat gradients, spin centres, pattern scale). MAP=own: centre as origin, the face normal as local Z.
# Then the same turn about the vertical axis for all (TURN, degrees; +8: the face ~21° off the camera toward the light, so raised edges catch it)
# one pose for all: leaning back 12° (top away from the camera), then the same turn. The coins are built lying flat and stood
# up by 78° about X; the cup is prepared upright, so it gets −12° about X from there
TILT = 0 if TARGET == 'cup' else 78        # how the meshes stand now
POSE = -12 if TARGET == 'cup' else float(os.environ.get('POSE', 90 if TARGET == 'blobicon' else TILT))    # how they stand in the shot
REF_TILT = POSE if TARGET == 'blobicon' else 78                              # the face the reflector serves: the coin's face, the cup's front wall, both leaning back 12°
TURN = float(os.environ.get('TURN', 8)) * (-1 if MIRROR else 1)
pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
c0 = (Vector([min(p[i] for p in pts) for i in range(3)]) + Vector([max(p[i] for p in pts) for i in range(3)])) / 2
L0 = Matrix.Translation(c0) @ Matrix.Rotation(math.radians(TILT), 4, 'X')   # how the meshes stand now
for o in objs: o.data.transform(L0.inverted())                                # → lying flat, face up, centred
turn = Matrix.Translation(c0) @ Matrix.Rotation(math.radians(TURN), 4, 'Z') @ Matrix.Rotation(math.radians(POSE), 4, 'X') @ Matrix.Rotation(math.radians(float(os.environ.get('ROLL', 0))), 4, 'Z')   # ROLL: the object turned on its own face
if os.environ.get('MAP', 'ball') == 'ball':
    BALL = Matrix(((0.167, -0.3411, 0.5323), (-0.6318, -0.1113, 0.1269), (0.0244, -0.5467, -0.358))) * (1 / 0.65395)   # its rotation
    rad = max((v.co).length for o in objs for v in o.data.vertices)
    # mirrored as MX·BALL·MX: a proper rotation (two reflections), never a negative scale. A mirrored object space flips what
    # facing nodes (Layer Weight, Fresnel) take for the outside, so whole surfaces read as their edge colour
    space = Matrix.Translation(c0) @ ((MX @ BALL @ MX) if MIRROR else BALL).to_4x4() @ Matrix.Scale(rad, 4)
    for o in objs: o.data.transform(space.inverted() @ turn); o.matrix_world = space
else:
    for o in objs: o.matrix_world = turn
bpy.context.view_layer.update()

# the camera: the thumbnailer's view direction and lens, pulled back so the object fills the frame as the ball does (~82%)
pts = [o.matrix_world @ v.co for o in objs for v in o.data.vertices]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
C = (lo + hi) / 2; r = max((p - C).length for p in pts)
fwd = Vector((-0.2321 if MIRROR else 0.2321, 0.9606, -0.1471)).normalized()
if TARGET == 'blobicon' and os.environ.get('FRONT') == '1':   # optionally a frontal camera, a touch from above
    fwd = Vector((0, 1, -math.tan(math.radians(float(os.environ.get('CAM_EL', 4)))))).normalized()
cam = bpy.data.objects.new('bk_cam', bpy.data.cameras.new('bk_cam')); sc.collection.objects.link(cam)
cam.data.lens = 200; cam.data.sensor_width = 32; cam.data.clip_start = .01; cam.data.clip_end = 1000
half = math.atan(16 / 200)
cam.location = C - fwd * (r / math.sin(half) / float(os.environ.get('FILL', .82)))
cam.rotation_euler = fwd.to_track_quat('-Z', 'Y').to_euler(); sc.camera = cam
# BLOB_FACE=1: the blob plate turned to face the camera square-on (a flat backdrop, as in a 2D layout), about its own centre
if BLOB_OBJ is not None and os.environ.get('BLOB_FACE', '1') == '1':
    nb = (Matrix.Rotation(math.radians(TURN), 3, 'Z') @ Matrix.Rotation(math.radians(POSE), 3, 'X') @ Vector((0, 0, 1))).normalized()
    Mw = BLOB_OBJ.matrix_world; wp = [Mw @ v.co for v in BLOB_OBJ.data.vertices]; cb = sum(wp, Vector()) / len(wp)
    Rq = nb.rotation_difference(-fwd).to_matrix().to_4x4()
    # BLOB_TILT="yaw,pitch" degrees: turn it a little off square-on, so its thickness and bevel show and catch the light
    ty, tp = (float(v) for v in os.environ.get('BLOB_TILT', '0,0').split(','))
    Rq = Matrix.Rotation(math.radians(ty), 4, 'Z') @ Matrix.Rotation(math.radians(tp), 4, cam.matrix_world.to_3x3() @ Vector((1, 0, 0))) @ Rq
    BLOB_OBJ.data.transform(Mw.inverted() @ Matrix.Translation(cb) @ Rq @ Matrix.Translation(-cb) @ Mw)

# REFLECT=1: a product-shot reflector the camera never sees. A flat face seen through a long lens mirrors almost one direction
# of the world (here: dark), so mirror-like materials go dead on it, though the preview ball, round, always finds the light.
# The card sits where the coin's face looks in reflection; one half lit, a crisp diagonal edge through the face's footprint, so
# the face carries a light/dark split and the strokes' tops a highlight. Mirror-like materials show their character on edges like
# this (the chromatic ones split them into colour, as the preview ball does on the windows of its HDRI). REFLECT_E: strength,
# REFLECT_SOFT: the edge's softness as a share of the footprint
if os.environ.get('REFLECT', '1') == '1':
    nrm = (Matrix.Rotation(math.radians(TURN), 3, 'Z') @ Matrix.Rotation(math.radians(REF_TILT), 3, 'X') @ Vector((0, 0, 1))).normalized()
    rdir = (fwd - 2 * fwd.dot(nrm) * nrm).normalized(); D = .8
    bm_ = bmesh.new(); bmesh.ops.create_grid(bm_, x_segments=1, y_segments=1, size=.6)
    me_ = bpy.data.meshes.new('reflector'); bm_.to_mesh(me_); bm_.free()
    card = bpy.data.objects.new('reflector', me_); sc.collection.objects.link(card)
    card.location = C + rdir * D
    card.rotation_euler = ((-rdir).to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), math.radians(35))).to_euler()   # the edge on a diagonal
    card.visible_camera = False; card.visible_shadow = False
    if os.environ.get("CARD"): card.visible_diffuse = False   # on a card: it only shows in reflections, never lights the card
    mm = bpy.data.materials.new('M_reflector'); mm.use_nodes = True; t_ = mm.node_tree; t_.nodes.clear()
    o_ = t_.nodes.new('ShaderNodeOutputMaterial'); em = t_.nodes.new('ShaderNodeEmission'); tc_ = t_.nodes.new('ShaderNodeTexCoord')
    sx = t_.nodes.new('ShaderNodeSeparateXYZ'); mr = t_.nodes.new('ShaderNodeMapRange')
    fp = r * 1.2   # the face's footprint on the card: about the coin's size (the rays are near parallel)
    soft = fp * float(os.environ.get('REFLECT_SOFT', .08)); mr.inputs['From Min'].default_value = -soft; mr.inputs['From Max'].default_value = soft
    mr.inputs['To Min'].default_value = 0; mr.inputs['To Max'].default_value = float(os.environ.get('REFLECT_E', 3))
    t_.links.new(tc_.outputs['Object'], sx.inputs[0]); t_.links.new(sx.outputs['X'], mr.inputs['Value']); t_.links.new(mr.outputs[0], em.inputs['Strength'])
    t_.links.new(em.outputs[0], o_.inputs['Surface']); me_.materials.append(mm)

# CARD=hex: the object on a card — a matte plane behind it, square to the camera, CARD_D metres behind its back, in that
# colour (sRGB hex, CARD_K scales it to land on the hex after the view transform), so the card is lit by the same light and
# carries the object's own shadow. SHIFT_Y moves the frame (the object up in the frame for negative values)
cam.data.shift_y = float(os.environ.get('SHIFT_Y', 0)); cam.data.shift_x = float(os.environ.get('SHIFT_X', 0))
if os.environ.get('CARD'):
    hx = os.environ['CARD'].lstrip('#')
    lin = lambda c: c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
    bm_ = bmesh.new(); bmesh.ops.create_grid(bm_, x_segments=1, y_segments=1, size=3)
    me_ = bpy.data.meshes.new('card'); bm_.to_mesh(me_); bm_.free()
    cd_ = bpy.data.objects.new('card', me_); sc.collection.objects.link(cd_)
    # parallel to the object's face (its pose: leaning back, turned), CARD_D behind its back, so its shadow sits close under it
    nf = (Matrix.Rotation(math.radians(TURN), 3, 'Z') @ Matrix.Rotation(math.radians(POSE), 3, 'X') @ Vector((0, 0, 1))).normalized()
    if nf.dot(fwd) > 0: nf = -nf                                   # the face's normal toward the camera
    back = max((p - C).dot(-nf) for p in pts)
    cd_.location = C - nf * (back + float(os.environ.get('CARD_D', .01))); cd_.rotation_euler = nf.to_track_quat('Z', 'Y').to_euler()
    cm = bpy.data.materials.new('M_card'); cm.use_nodes = True; cb_ = cm.node_tree.nodes['Principled BSDF']
    kk = [float(v) for v in os.environ.get('CARD_K', '1,1,1').split(',')]   # per-channel gain, found by calibration
    # the gain may exceed 1 (a card facing away from the light needs it to land on the hex), so it is fed through a node
    vm_ = cm.node_tree.nodes.new('ShaderNodeVectorMath'); vm_.operation = 'MULTIPLY'
    vm_.inputs[0].default_value = [lin(int(hx[i:i + 2], 16) / 255) for i in (0, 2, 4)]; vm_.inputs[1].default_value = kk
    cm.node_tree.links.new(vm_.outputs[0], cb_.inputs['Base Color'])
    cb_.inputs['Roughness'].default_value = .7; cb_.inputs['Specular IOR Level'].default_value = .2
    me_.materials.append(cm); cd_.visible_glossy = False   # the metal keeps reflecting the studio, not the card
    # the soft sun grazes a card square to the camera, so its shadow of the object lands far off to the side; by default the
    # sun casts no shadow here (shadow linking: nothing blocks it), and the object's shadow on the card comes from the studio's
    # surround only — soft, close under it, from the same light (CARD_SUN_SHADOW=1 keeps the sun's)
    # the card shares the light but not the object's shadow: the object casts none (CARD_SHADOW=1 to keep it)
    if os.environ.get('CARD_SHADOW', '0') != '1':
        for o in objs: o.visible_shadow = False

# render: as the thumbnailer
v = sc.view_settings; v.view_transform = 'Filmic'; v.look = 'Medium High Contrast'; v.exposure = float(os.environ.get('EXPO', 0)); v.gamma = 1
r_ = sc.render; r_.engine = 'CYCLES'; r_.film_transparent = True; r_.resolution_x = int(os.environ.get('RES', 1200)); r_.resolution_y = int(r_.resolution_x / float(os.environ.get('ASPECT', 1))); r_.resolution_percentage = 100
r_.image_settings.file_format = 'PNG'; r_.image_settings.color_mode = 'RGBA'; r_.image_settings.color_depth = '16'
c = sc.cycles; c.device = 'GPU'; c.samples = int(os.environ.get('SAMPLES', 256)); c.use_denoising = True
c.max_bounces = 20; c.glossy_bounces = 20; c.transmission_bounces = 40; c.sample_clamp_indirect = 0; c.blur_glossy = 1.5
c.caustics_reflective = False; c.caustics_refractive = False
# glass on alpha: what is seen through clear glass comes out transparent, not as the world (frosted glass, rough, renders as is)
c.film_transparent_glass = True; c.film_transparent_roughness = float(os.environ.get('GLASS_ROUGH', .1))

# UVs, two layers, scaled as the thumbnailer's automap scales the preview ball (our object at the ball's size: radius → 0.654 m,
# in units of the material's texture size TS, metres; BlenderKit's textureSizeMeters, 1 by default):
#   UVMap (active, what textures read): a box projection by each face's main axis in the flat frame, so walls and rims get
#     the texture unstretched;
#   Flat: one flat projection onto the coin's plane (round the cup: cylindrical), no seams; brushed shaders take their
#     direction from it (below), so brushing runs one way and never swirls over the strokes
TS = float(os.environ.get('TS', 1)); rad_ = max((p - C).length for p in pts); k_ = .654 / rad_ / TS
for o in objs:
    for nm in ('UVMap', 'Flat'):
        if nm not in o.data.uv_layers: o.data.uv_layers.new(name=nm)
    o.data.uv_layers['UVMap'].active = True; o.data.uv_layers['UVMap'].active_render = True
    bm = bmesh.new(); bm.from_mesh(o.data); uv = bm.loops.layers.uv['UVMap']; uvf = bm.loops.layers.uv['Flat']
    to_flat = turn.inverted() @ o.matrix_world; R3 = to_flat.to_3x3()
    for f in bm.faces:
        n = (R3 @ f.normal); ax = max(range(3), key=lambda i: abs(n[i])); a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for l in f.loops:
            q = to_flat @ l.vert.co   # flat (the coin lying, the cup standing), centred
            l[uv].uv = (q[a] * k_, q[b] * k_)
            if TARGET == 'cup': l[uvf].uv = (math.atan2(q.x, -q.y) * .7 * .654 / TS, q.z * k_)   # round the cup, the seam at the back
            else: l[uvf].uv = (q.x * k_, q.y * k_)
    bm.to_mesh(o.data); bm.free()

# the material
spec = os.environ.get('MAT')
if spec == 'normals':   # diagnostic: shading normal (world) as colour, unlit
    m = bpy.data.materials.new('normals'); m.use_nodes = True; nt_ = m.node_tree; nt_.nodes.clear()
    o_ = nt_.nodes.new('ShaderNodeOutputMaterial'); e = nt_.nodes.new('ShaderNodeEmission'); g_ = nt_.nodes.new('ShaderNodeNewGeometry')
    vm = nt_.nodes.new('ShaderNodeVectorMath'); vm.operation = 'MULTIPLY_ADD'; vm.inputs[1].default_value = (.5, .5, .5); vm.inputs[2].default_value = (.5, .5, .5)
    nt_.links.new(g_.outputs['Normal'], vm.inputs[0]); nt_.links.new(vm.outputs[0], e.inputs[0]); nt_.links.new(e.outputs[0], o_.inputs[0])
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
elif spec == 'clay':   # a matte grey, to judge the form
    m = bpy.data.materials.new('clay'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (.45, .45, .45, 1); b.inputs['Roughness'].default_value = .55
elif spec:
    path, name = spec.split('::')
    with bpy.data.libraries.load(path) as (src, dst): dst.materials = [name]
    m = dst.materials[0]
    # an optional pattern scale for BlenderKit node-group materials with a Scale input (MSCALE; 1 = as authored, which reads like the preview)
    K = float(os.environ.get('MSCALE', 1))
    for nt in [m.node_tree] + [n.node_tree for n in m.node_tree.nodes if n.type == 'GROUP' and n.node_tree]:
        for n in nt.nodes:
            if n.type == 'GROUP' and 'Scale' in n.inputs and not n.inputs['Scale'].is_linked: n.inputs['Scale'].default_value *= K
    # brushed (anisotropic) shaders with no direction given brush round the object's Z axis by default: on the preview ball that
    # is a spun cap, on our coin a crooked swirl over the strokes. Give them the direction of our flat UVs instead: straight
    # brushing across the coin and the icon, as on a brushed plate (shaders with their own tangent are left as they are)
    seen = set()
    def brush_dir(nt):
        if nt.name in seen: return
        seen.add(nt.name)
        for n in list(nt.nodes):
            if n.type in ('BSDF_PRINCIPLED', 'BSDF_GLOSSY', 'BSDF_ANISOTROPIC') and 'Tangent' in n.inputs and not n.inputs['Tangent'].is_linked:
                an = n.inputs.get('Anisotropic') or n.inputs.get('Anisotropy')
                if an is not None and (an.is_linked or an.default_value > 0):
                    tg = nt.nodes.new('ShaderNodeTangent'); tg.direction_type = 'UV_MAP'; tg.uv_map = 'Flat'
                    nt.links.new(tg.outputs['Tangent'], n.inputs['Tangent']); print('BRUSH DIR → UV on', n.name)
            if n.type == 'GROUP' and n.node_tree: brush_dir(n.node_tree)
    brush_dir(m.node_tree)
    # ANISO=0..1: the brushing's strength on the material's own shaders (straight brushing streaks hard on tight curves);
    # by default the material's own setting in dl/mats/bk.json ('aniso'), if it has one
    if not os.environ.get('ANISO'):
        import json
        try: os.environ['ANISO'] = str(json.load(open(f'{ROOT}/dl/mats/bk.json'))[name]['aniso'])
        except (KeyError, OSError, ValueError): pass
    if os.environ.get('ANISO'):
        seen_a = set()
        def set_aniso(nt):
            if nt.name in seen_a: return
            seen_a.add(nt.name)
            for n in nt.nodes:
                an = n.inputs.get('Anisotropic') if n.type == 'BSDF_PRINCIPLED' else None
                if an is not None and not an.is_linked: an.default_value = float(os.environ['ANISO'])
                if n.type == 'GROUP' and n.node_tree: set_aniso(n.node_tree)
        set_aniso(m.node_tree)
    # bump depth: a Bump node's Distance is in world units, while its pattern is in our ball-sized object space, so on an object
    # ~10× smaller than the preview ball the same pattern makes ~10× steeper slopes. Scale the depth by our size against the
    # ball (RELIEF=0 to keep the authored depth)
    if os.environ.get('RELIEF', '1') == '1':
        KB = abs(objs[0].matrix_world.to_scale()[0]) / .654; seen_b = set()
        def scale_relief(nt, owner=None):   # owner: the group node using nt, whose inputs feed nt's Group Input
            if (nt.name, owner and owner.name) in seen_b: return
            seen_b.add((nt.name, owner and owner.name))
            for n in nt.nodes:
                for typ, sock in (('BUMP', 'Distance'), ('DISPLACEMENT', 'Scale')):
                    if n.type != typ: continue
                    i = n.inputs[sock]
                    if not i.is_linked: i.default_value *= KB
                    elif owner is not None and i.links[0].from_node.type == 'GROUP_INPUT':   # a control knob of the material
                        k = i.links[0].from_socket.name
                        if k in owner.inputs and not owner.inputs[k].is_linked and (owner.name, k) not in seen_b:
                            owner.inputs[k].default_value *= KB; seen_b.add((owner.name, k))
                if n.type == 'GROUP' and n.node_tree: scale_relief(n.node_tree, n)
        scale_relief(m.node_tree); print('RELIEF x', round(KB, 3))
    # MATSET="Input name=value;…": override the material's own controls (its node-group inputs), for a look tuned to our shapes
    for kv in filter(None, os.environ.get('MATSET', '').split(';')):
        k, v = kv.split('=')
        for n in m.node_tree.nodes:
            if n.type == 'GROUP' and k.strip() in n.inputs: n.inputs[k.strip()].default_value = float(v)
else:
    m = bpy.data.materials.new('placeholder metal'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (.9, .9, .9, 1); b.inputs['Metallic'].default_value = 1; b.inputs['Roughness'].default_value = .2
for o in objs:
    if o is BLOB_OBJ: continue
    o.data.materials.clear(); o.data.materials.append(m)
if BLOB_OBJ is not None:   # dark frosted glass, a Principled transmission tinted Primary Dark (#33694F), or BLOB_MAT=path::name
    bs = os.environ.get('BLOB_MAT')
    if bs:
        with bpy.data.libraries.load(bs.split('::')[0]) as (src, dst): dst.materials = [bs.split('::')[1]]
        gm = dst.materials[0]
        tint = os.environ.get('BLOB_TINT')   # a hex colour for the glass's own tint input (BlenderKit 'Glass Tint'), sRGB
        if tint:
            lin = lambda c: c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
            rgb = [lin(int(tint.lstrip('#')[i:i + 2], 16) / 255) for i in (0, 2, 4)]
            for n in gm.node_tree.nodes:
                if n.type == 'GROUP' and 'Glass Tint' in n.inputs: n.inputs['Glass Tint'].default_value = (*rgb, 1)
    else:
        gm = bpy.data.materials.new('dark frosted glass'); gm.use_nodes = True; g = gm.node_tree.nodes['Principled BSDF']
        g.inputs['Base Color'].default_value = (.033, .141, .08, 1); g.inputs['Transmission Weight'].default_value = 1
        g.inputs['Roughness'].default_value = float(os.environ.get('GLASS_R', .35)); g.inputs['IOR'].default_value = 1.45
    # BLOB_BODY=0..1: mix the glass with its own colour body (BLOB_BODY_COL, default Primary Dark #33694F, satin), so a dark
    # glass reads as coloured on alpha (a transparent PNG cannot tint what lies behind it; only its own colour shows)
    body = float(os.environ.get('BLOB_BODY', 0))
    if body > 0:
        nt_ = gm.node_tree; out_ = next(n for n in nt_.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
        src_ = out_.inputs['Surface'].links[0].from_socket
        pb = nt_.nodes.new('ShaderNodeBsdfPrincipled'); hx = os.environ.get('BLOB_BODY_COL', '33694F')
        lin = lambda c: c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
        pb.inputs['Base Color'].default_value = (*[lin(int(hx[i:i + 2], 16) / 255) for i in (0, 2, 4)], 1)
        pb.inputs['Roughness'].default_value = .45; pb.inputs['Coat Weight'].default_value = .3; pb.inputs['Coat Roughness'].default_value = .25
        mx_ = nt_.nodes.new('ShaderNodeMixShader'); mx_.inputs['Fac'].default_value = body
        nt_.links.new(src_, mx_.inputs[1]); nt_.links.new(pb.outputs[0], mx_.inputs[2]); nt_.links.new(mx_.outputs[0], out_.inputs['Surface'])
    BLOB_OBJ.data.materials.clear(); BLOB_OBJ.data.materials.append(gm)

r_.filepath = os.environ.get('OUT', f'{ROOT}/check/metal/{TARGET}.png')
bpy.app.driver_namespace['STUDIO'] = dict(objs=objs, turn=turn, cam=cam, sun=sun, C=C, fwd=fwd)   # for scripts run after this one (NORENDER=1)
if os.environ.get('NORENDER') != '1': bpy.ops.render.render(write_still=True)
print('RENDERED', TARGET, m.name, r_.filepath)
