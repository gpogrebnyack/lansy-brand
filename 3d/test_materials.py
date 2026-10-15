# Try glass materials on the icon-alone tubes, one camera, one render per material.
# /Applications/Blender.app/Contents/MacOS/Blender -b 3d/lansy-3d-test.blend -P 3d/test_materials.py
import bpy, bmesh, os
ROOT = os.path.dirname(os.path.abspath(__file__))
MATS = ROOT + '/dl/mats'
OUT = ROOT + '/check/' + os.environ.get('MATDIR', 'materials'); os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
tubes = bpy.data.objects['icon_alone_relief']
keep = {tubes.name, 'floor', 'key', 'cyc'}
for o in sc.objects:
    if o.type == 'MESH': o.hide_render = o.name not in keep and not o.name.startswith('flag')
sc.camera = bpy.data.objects['icon_alone_hero']

# UVs for texture-based materials (the tubes are built without them): a box projection by each face's main axis, in metres × 20
bm = bmesh.new(); bm.from_mesh(tubes.data); uv = bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    n = f.normal; ax = max(range(3), key=lambda i: abs(n[i])); u_, v_ = [(1, 2), (0, 2), (0, 1)][ax]
    for l in f.loops: l[uv].uv = (l.vert.co[u_] * 20, l.vert.co[v_] * 20)
bm.to_mesh(tubes.data); bm.free()

def append(blend, name):
    with bpy.data.libraries.load(blend) as (src, dst): dst.materials = [name]
    return dst.materials[0]

def textured_frosted():   # 3dtextures.me Glass Frosted 001 (CC0): a transmissive Principled with its roughness and normal maps
    m = bpy.data.materials.new('Glass Frosted 001'); m.use_nodes = True; nt = m.node_tree
    b = nt.nodes['Principled BSDF']; b.inputs['Transmission Weight'].default_value = 1; b.inputs['IOR'].default_value = 1.45
    b.inputs['Base Color'].default_value = (1, 1, 1, 1)
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (4, 4, 4)
    nt.links.new(tc.outputs['UV'], mp.inputs[0])
    def img(name, colour):
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(f'{MATS}/glass-frosted-001/Glass_Frosted_001_{name}.jpg')
        t.image.colorspace_settings.name = 'sRGB' if colour else 'Non-Color'; nt.links.new(mp.outputs[0], t.inputs[0]); return t
    r = img('roughness', False); nt.links.new(r.outputs[0], b.inputs['Roughness'])
    n = img('normal', False); nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(n.outputs[0], nm.inputs['Color']); nt.links.new(nm.outputs[0], b.inputs['Normal'])
    return m

def plain_glass():   # the baseline: Blender's own Principled, clear
    m = bpy.data.materials.new('Principled clear glass'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Transmission Weight'].default_value = 1; b.inputs['Roughness'].default_value = 0; b.inputs['IOR'].default_value = 1.5
    return m

tests = [
    ('1-frosted-glass-02', lambda: append(MATS + '/frosted-glass-02.blend', 'Frosted Glass 02')),
    ('2-procedural-frosted-glass', lambda: append(MATS + '/procedural-frosted-glass.blend', 'Procedural Frosted Glass')),
    ('3-glass-frosted-001', textured_frosted),
    ('4-real-aesthetic-glass', lambda: append(MATS + '/real-aesthetic-glass.blend', 'Real Aesthetic Glass')),
    ('5-principled-clear-glass', plain_glass),
]
r = sc.render; r.resolution_x = r.resolution_y = int(os.environ.get('RES', 1000))
c = sc.cycles; c.samples = 192; c.max_bounces = 24; c.transmission_bounces = 24; c.glossy_bounces = 12; c.transparent_max_bounces = 16; c.use_denoising = True
ONLY = os.environ.get('ONLY')
for name, make in tests:
    if ONLY and ONLY not in name: continue
    m = make(); tubes.data.materials.clear(); tubes.data.materials.append(m)
    r.filepath = f'{OUT}/{name}.png'; bpy.ops.render.render(write_still=True); print('RENDERED', name, m.name)
