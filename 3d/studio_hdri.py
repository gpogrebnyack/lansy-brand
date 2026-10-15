# Studio from a real photo-studio HDRI (Poly Haven, CC0): its strip softboxes light the object and show as clean highlight
# lines in glass and chrome. The camera sees a seamless cyc lit by the same HDRI (a natural gradient and a soft shadow);
# black flags out of frame give the glass dark outlines (bright-field). Light paths from the research recipe.
# Blender -b 3d/lansy-3d-test.blend -P 3d/studio_hdri.py -P 3d/test_materials.py   (env: HDRI=name, ROT=deg, EXPO=ev, FLAGS=0/1)
import bpy, bmesh, math, os
from mathutils import Vector
ROOT = os.path.dirname(os.path.abspath(__file__))
sc = bpy.context.scene
tubes = bpy.data.objects['icon_alone_relief']
for name in ('floor', 'key'):
    o = bpy.data.objects.get(name)
    if o: bpy.data.objects.remove(o, do_unlink=True)
pts = [tubes.matrix_world @ v.co for v in tubes.data.vertices]
cx = sum(p.x for p in pts) / len(pts); cy = sum(p.y for p in pts) / len(pts); top = max(p.z for p in pts)
C = Vector((cx, cy, top / 2))

# the world: the HDRI, rotated so its strips sit left and right of the camera
w = sc.world; nt = w.node_tree; nt.nodes.clear()
out = nt.nodes.new('ShaderNodeOutputWorld'); bg = nt.nodes.new('ShaderNodeBackground')
env = nt.nodes.new('ShaderNodeTexEnvironment'); env.image = bpy.data.images.load(f"{ROOT}/hdri/{os.environ.get('HDRI', 'monochrome_studio_02')}_2k.hdr")
mp = nt.nodes.new('ShaderNodeMapping'); tc = nt.nodes.new('ShaderNodeTexCoord')
mp.inputs['Rotation'].default_value = (0, 0, math.radians(float(os.environ.get('ROT', 0))))
nt.links.new(tc.outputs['Generated'], mp.inputs[0]); nt.links.new(mp.outputs[0], env.inputs[0]); nt.links.new(env.outputs[0], bg.inputs[0])
bg.inputs[1].default_value = 1.0; nt.links.new(bg.outputs[0], out.inputs[0])

# the cyc the camera sees: floor curving up into a back wall, a warm light grey, lit by the HDRI
coll = bpy.data.collections.get('studio') or sc.collection
bm = bmesh.new(); R = .3; prof = [(-1.2, 0)] + [(.2 + R * math.sin(math.radians(a)), R - R * math.cos(math.radians(a))) for a in range(0, 91, 3)] + [(.2 + R, 1.5)]
W = 3.0; cols = [(bm.verts.new((cx - W / 2, cy + y, z)), bm.verts.new((cx + W / 2, cy + y, z))) for (y, z) in prof]
for a, b in zip(cols, cols[1:]): bm.faces.new((a[0], a[1], b[1], b[0]))
me = bpy.data.meshes.new('cyc'); bm.to_mesh(me); bm.free(); cyc = bpy.data.objects.new('cyc', me); coll.objects.link(cyc)
for p in me.polygons: p.use_smooth = True
m = bpy.data.materials.new('M_cyc'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
g = float(os.environ.get('CYC', .7)); b.inputs['Base Color'].default_value = (g, g, g * .985, 1); b.inputs['Roughness'].default_value = .9
me.materials.append(m)

# black flags left, right and above, just out of frame: the glass refracts them into dark edge lines
if os.environ.get('FLAGS', '1') == '1':
    blk = bpy.data.materials.new('M_flag'); blk.use_nodes = True; bb = blk.node_tree.nodes['Principled BSDF']
    bb.inputs['Base Color'].default_value = (0, 0, 0, 1); bb.inputs['Roughness'].default_value = 1; bb.inputs['Specular IOR Level'].default_value = 0
    def flag(name, w_, h_, loc):
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=.5)
        for v in bm.verts: v.co.x *= w_; v.co.y *= h_
        me_ = bpy.data.meshes.new(name); bm.to_mesh(me_); bm.free(); o = bpy.data.objects.new(name, me_); coll.objects.link(o)
        me_.materials.append(blk); o.location = loc; o.rotation_euler = (C - Vector(loc)).to_track_quat('Z', 'Y').to_euler()
        o.visible_camera = False; o.visible_shadow = False
    for side in (-1, 1): flag(f'flag_{side}', .12, .3, (cx + side * .13, cy + .02, C.z))

# render: AgX, deep transmission, clamp off for glass, glossy filter
v = sc.view_settings; v.view_transform = 'AgX'; v.look = 'AgX - Base Contrast'; v.exposure = float(os.environ.get('EXPO', 0))
c = sc.cycles; c.max_bounces = 32; c.transmission_bounces = 32; c.glossy_bounces = 12; c.transparent_max_bounces = 24
c.sample_clamp_indirect = 0; c.blur_glossy = .5; c.caustics_reflective = False; c.caustics_refractive = False
cam = bpy.data.objects['icon_alone_hero']; cam.data.lens = 100
d = cam.location - C; cam.location = C + d.normalized() * d.length * 1.18   # keep the framing with the longer lens
cam.rotation_euler = (C - cam.location).to_track_quat('-Z', 'Y').to_euler()
print('HDRI STUDIO ready')
