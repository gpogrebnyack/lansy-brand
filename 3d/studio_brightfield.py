# Bright-field glass lighting on top of studio_glass.py: a bright, softly graded wall behind the object (the glass shows it,
# bent), big black flags close at the sides and above (the glass edges refract and reflect them → crisp dark outlines),
# a little front light for the specular highlights.
import bpy, bmesh, math, os
from mathutils import Vector
sc = bpy.context.scene
cyc = bpy.data.objects['cyc']; m = cyc.data.materials[0]; nt = m.node_tree
b = nt.nodes['Principled BSDF']
# the wall glows a little, bright behind the object and falling off upward and to the sides
tc = nt.nodes.new('ShaderNodeTexCoord'); grad = nt.nodes.new('ShaderNodeTexGradient'); grad.gradient_type = 'SPHERICAL'
mp = nt.nodes.new('ShaderNodeMapping'); C = Vector((.25, .3, .06)); mp.inputs['Location'].default_value = -C; mp.inputs['Scale'].default_value = (2.2, 2.2, 2.2)
ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (.18, .18, .18, 1); ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
nt.links.new(tc.outputs['Generated' if False else 'Object'], mp.inputs[0]); nt.links.new(mp.outputs[0], grad.inputs[0]); nt.links.new(grad.outputs[0], ramp.inputs[0])
nt.links.new(ramp.outputs[0], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = float(os.environ.get('WALL', .9))
b.inputs['Base Color'].default_value = (.85, .85, .85, 1)
# big black flags: closer and larger than before
for o in [o for o in bpy.data.objects if o.name.startswith('flag_')]: bpy.data.objects.remove(o, do_unlink=True)
blk = bpy.data.materials['M_flag']
def flag(name, w, h, loc):
    bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=.5)
    for v in bm.verts: v.co.x *= w; v.co.y *= h
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); sc.collection.objects.link(o)
    o.data.materials.append(blk); o.location = loc; tgt = Vector((.25, 0, .06))
    o.rotation_euler = (tgt - Vector(loc)).to_track_quat('Z', 'Y').to_euler(); o.visible_camera = False
for side in (-1, 1): flag(f'flag_{side}', .35, .5, (.25 + side * .16, -.02, .08))
flag('flag_top', .4, .3, (.25, -.02, .3))
# soften the area rig: the wall now does most of the work
for n, e in (('strip_L', 1.5), ('strip_R', 1.5), ('top', .8), ('fill', .4)):
    L = bpy.data.objects.get(n)
    if L: L.data.energy = e
print('BRIGHTFIELD ready')
