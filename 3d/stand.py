# The 3D try-on stand: builds a rubric icon in a few compositions and renders every part in every material as its own layer,
# so a page can stack any combination (composition × material per part) without rendering it.
# Run inside Blender (5.x): exec(open(PATH).read()); then build('squircle'); render_layers('squircle') — one composition per call.
import bpy, bmesh, math, os, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON = ROOT + '/3d/icons/cafe.svg'
HDRI = ROOT + '/3d/hdri/studio_small_09_2k.hdr'   # Poly Haven, CC0
HDRI_ROT, HDRI_STRENGTH = 140, .75
LIGHTS = [('key', (-2.4, 2.6, 4.2), 5, 160), ('rim', (2.6, 2.2, 1.0), 2.5, 90)]   # a soft key from top left, a rim from behind right
OUT = ROOT + '/web/labs/3d/renders'
RES = 800
VIEW = 'Standard'
LENS, CAM_Z = 50, 2.75   # a shorter lens, close: the slab's thickness shows, as on the Lansy icon
TILT = (-30, 30, -10)

def lin(h):   # sRGB hex → linear RGBA
    h = h.lstrip('#'); c = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in c) + (1,)

# ---- materials: the brand palette in a few finishes, plus neutral specials that take their surroundings' colour
MATS = {
  'lime-soft':   dict(base='#9CDE45', rough=.38, coat=.45, coat_rough=.22, sss=.1),
  'lime-gloss':  dict(base='#9CDE45', rough=.12, coat=1, coat_rough=.05),
  'lime-jelly':  dict(base='#9CDE45', rough=.12, trans=.85, ior=1.4, sss=.2),
  'green-soft':  dict(base='#33694F', rough=.42, coat=.25, coat_rough=.25),
  'ink-matte':   dict(base='#201F1D', rough=.55),
  'white-clay':  dict(base='#FCF9F3', rough=.5, coat=.2, coat_rough=.3, sss=.12),
  'sand-ceramic':dict(base='#F2EFE9', rough=.18, coat=.8, coat_rough=.08),
  'frost-glass': dict(base='#FFFFFF', rough=.32, trans=1, ior=1.45),
  'chrome':      dict(base='#E6E6E6', rough=.04, metal=1),
  'alu-matte':   dict(base='#C9C7C3', rough=.38, metal=1),
}

def make_mat(name, p):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    o = nt.nodes.new('ShaderNodeOutputMaterial'); b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    nt.links.new(b.outputs[0], o.inputs[0]); I = b.inputs
    I['Base Color'].default_value = lin(p['base']); I['Roughness'].default_value = p.get('rough', .5)
    I['Metallic'].default_value = p.get('metal', 0); I['IOR'].default_value = p.get('ior', 1.5)
    I['Transmission Weight'].default_value = p.get('trans', 0)
    I['Coat Weight'].default_value = p.get('coat', 0); I['Coat Roughness'].default_value = p.get('coat_rough', .03)
    I['Subsurface Weight'].default_value = p.get('sss', 0); I['Subsurface Radius'].default_value = (.1, .1, .1)
    I['Sheen Weight'].default_value = p.get('sheen', 0)
    return m

def clear():
    for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
    for coll in (bpy.data.curves, bpy.data.meshes, bpy.data.lights, bpy.data.cameras):
        for d in list(coll): coll.remove(d)

# ---- the icon: Hugeicons stroke paths, each stroke a wall standing on the face (the Lansy palm's build): width = the stroke, height = depth
def icon(depth=.075, z=0.0, stroke=1.45, size=1.0):   # size: the icon's 18-unit box, in metres
    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=ICON)
    new = [o for o in bpy.data.objects if o not in before]
    bpy.ops.object.select_all(action='DESELECT')
    for o in new: o.select_set(True)
    bpy.context.view_layer.objects.active = new[0]; bpy.ops.object.join()
    o = bpy.context.view_layer.objects.active; o.name = 'icon'
    for coll in o.users_collection: coll.objects.unlink(o)
    bpy.context.scene.collection.objects.link(o)
    # bake the import's transform into the points, then scale so the icon's 18-unit box is 1 m, centred (operators like
    # transform_apply don't take in a script's context, so the points are moved by hand)
    mw = o.matrix_world.copy(); bps = [bp for s in o.data.splines for bp in s.bezier_points]
    for bp in bps:
        for a in ('co', 'handle_left', 'handle_right'): setattr(bp, a, mw @ getattr(bp, a))
    o.matrix_world = o.matrix_world.__class__.Identity(4)
    xs = [bp.co.x for bp in bps]; ys = [bp.co.y for bp in bps]
    u = (max(xs) - min(xs)) / 12   # the widest stroke (the lid line) runs 12 of the icon's 18 units: one unit in metres
    k = size / (18 * u); cx = (max(xs) + min(xs)) / 2; cy = (max(ys) + min(ys)) / 2
    for bp in bps:
        for a in ('co', 'handle_left', 'handle_right'):
            v = getattr(bp, a); setattr(bp, a, ((v.x - cx) * k, (v.y - cy) * k, 0))
    c = o.data; c.dimensions = '2D'; c.fill_mode = 'NONE'; c.resolution_u = 32; c.use_fill_caps = True
    # each stroke is swept by a flat-topped wall profile (the Lansy palm's build), not a round tube: width = the stroke,
    # height = depth, a narrow fillet on the top edges that catches the light
    w = stroke / 18 * size; c.bevel_mode = 'OBJECT'; c.bevel_object = wall(w, depth, min(w, depth) * .28)
    o.location = (0, 0, z + depth / 2 - depth * .08)   # standing on the face, its foot a little sunk in
    return o

def wall(w, h, r):   # a rounded rectangle w × h (fillet r), as a profile curve; hidden from the render
    cu = bpy.data.curves.new('wall', 'CURVE'); cu.dimensions = '2D'; sp = cu.splines.new('POLY'); pts = []
    for cx, cy, a0 in [(w/2 - r, h/2 - r, 0), (-w/2 + r, h/2 - r, 90), (-w/2 + r, -h/2 + r, 180), (w/2 - r, -h/2 + r, 270)]:
        for i in range(7):
            a = math.radians(a0 + 90 * i / 6); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    sp.points.add(len(pts) - 1)
    for p, (x, y) in zip(sp.points, pts): p.co = (x, y, 0, 1)
    sp.use_cyclic_u = True
    o = bpy.data.objects.new('wall', cu); bpy.context.scene.collection.objects.link(o); o.hide_render = True; o.hide_viewport = True
    return o

def plate(n, w, t, r, name):   # a superellipse slab (n=2 a disc, n≈5 the squircle), edges rounded; side and bevel = the rim (slot 1)
    me = bpy.data.meshes.new(name); bm = bmesh.new(); N = 192
    pts = []
    for i in range(N):
        a = 2 * math.pi * i / N; ca, sa = math.cos(a), math.sin(a)
        pts.append(bm.verts.new((w / 2 * math.copysign(abs(ca) ** (2 / n), ca), w / 2 * math.copysign(abs(sa) ** (2 / n), sa), 0)))
    top = bm.faces.new(pts)
    ext = bmesh.ops.extrude_face_region(bm, geom=[top])
    for v in [e for e in ext['geom'] if isinstance(e, bmesh.types.BMVert)]: v.co.z -= t
    for f in bm.faces: f.material_index = 0 if abs(f.normal.z) > .9 else 1
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location.z = 0
    bv = o.modifiers.new('round', 'BEVEL'); bv.width = r; bv.segments = 10; bv.limit_method = 'ANGLE'; bv.material = 1; bv.harden_normals = False
    me.polygons.foreach_set('use_smooth', [True] * len(me.polygons))
    o.data.materials.append(None); o.data.materials.append(None)
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
    return o

# compositions: name → builder; each returns its parts {part: object}. A plate has two slots: 0 the faces, 1 the rim
def comp_squircle():
    return {'plate': plate(5, 1.12, .22, .09, 'plate'), 'icon': icon(size=.92)}

def comp_disc():
    return {'plate': plate(2, 1.12, .12, .045, 'plate'), 'icon': icon(size=.74)}   # a circle holds less than a squircle; a thin disc, not a button

def comp_free():   # no base: the icon alone, deeper, as an object
    return {'icon': icon(depth=.16, stroke=1.4)}

COMPS = {'squircle': comp_squircle, 'disc': comp_disc, 'free': comp_free}

def stage(parts):
    sc = bpy.context.scene
    rig = bpy.data.objects.new('rig', None); sc.collection.objects.link(rig)
    for o in parts.values(): o.parent = rig
    rig.rotation_euler = tuple(math.radians(a) for a in TILT)   # the Lansy icon's tilt: top away, turned to the left
    g = bpy.data.objects.new('ground', bpy.data.meshes.new('ground')); sc.collection.objects.link(g)
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6); bm.to_mesh(g.data); bm.free()
    g.location.z = -.32; g.is_shadow_catcher = True
    cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); sc.collection.objects.link(cam)
    cam.data.lens = LENS; cam.location = (0, 0, CAM_Z); sc.camera = cam
    for nm, loc, size, power in LIGHTS:
        L = bpy.data.objects.new(nm, bpy.data.lights.new(nm, 'AREA')); sc.collection.objects.link(L)
        L.data.size = size; L.data.energy = power; L.location = loc
        L.rotation_mode = 'QUATERNION'; L.rotation_quaternion = (L.location * -1).to_track_quat('-Z', 'Y')
    w = sc.world or bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground'); env = nt.nodes.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(HDRI, check_existing=True); mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord')
    mp.inputs['Rotation'].default_value = (0, 0, math.radians(HDRI_ROT))
    nt.links.new(tc.outputs['Generated'], mp.inputs[0]); nt.links.new(mp.outputs[0], env.inputs[0]); nt.links.new(env.outputs[0], bg.inputs[0]); nt.links.new(bg.outputs[0], out.inputs[0])
    bg.inputs[1].default_value = HDRI_STRENGTH
    r = sc.render; r.engine = 'CYCLES'; sc.cycles.device = 'GPU'; sc.cycles.samples = 96; sc.cycles.use_denoising = True
    r.resolution_x = r.resolution_y = RES; r.film_transparent = True
    sc.view_settings.view_transform = VIEW; sc.view_settings.look = 'None'
    r.image_settings.file_format = 'PNG'; r.image_settings.color_mode = 'RGBA'

CUR = {}
def build(name):
    clear(); parts = COMPS[name](); stage(parts); CUR.clear(); CUR.update(parts=parts, name=name)
    for k, p in MATS.items(): make_mat(k, p)
    return list(parts)

NEUTRAL = 'white-clay'   # what a part looks like to the others while it is not the one being rendered (in reflections)

def paint(part, mats):   # mats: one material, or (faces, rim) for a plate
    o = CUR['parts'][part]; mats = (mats,) if isinstance(mats, str) else mats
    o.data.materials.clear()
    for m in (mats * 2 if o.type == 'MESH' and len(mats) == 1 else mats): o.data.materials.append(bpy.data.materials[m])

def only(part):   # the camera sees one part; the others still cast shadows and show in reflections
    for k, o in CUR['parts'].items(): o.visible_camera = (k == part)

def shot(path):
    bpy.context.scene.render.filepath = path; bpy.ops.render.render(write_still=True); return path

def render_layers(name, mats=None, parts=None, shadow=True):   # the icon in every material; the plate in every faces × rim pair; the shadow
    d = f'{OUT}/{name}'; os.makedirs(d, exist_ok=True); done = []; M = list(mats or MATS); P = CUR['parts']
    for part in (parts or P):
        for k in P: paint(k, NEUTRAL)
        only(part)
        if part == 'icon':
            for m in M: paint('icon', m); done.append(shot(f'{d}/icon-{m}.png'))
        else:
            for f in M:
                for r in M: paint(part, (f, r)); done.append(shot(f'{d}/{part}-{f}--{r}.png'))
    if shadow:
        for k in P: paint(k, NEUTRAL)
        only(None); done.append(shot(f'{d}/shadow.png'))
    for o in P.values(): o.visible_camera = True
    return done
