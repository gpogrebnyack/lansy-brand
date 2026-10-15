# The aluminium icon spinning exactly as the Lansy icon does (its Blender animation, see below): a 5 s loop at 30 fps. Run after studio_bk.py set up the shot (NORENDER=1):
#   Blender -b 3d/lansy-3d-test.blend -P 3d/studio_bk.py -P 3d/icon_spin.py   (env: FRAMES_OUT=dir, SPIN_FPS, SPIN_SEC)
import bpy, math, os
from mathutils import Vector
S = bpy.app.driver_namespace['STUDIO']; sc = bpy.context.scene
objs, C = S['objs'], S['C']
fps = int(os.environ.get('SPIN_FPS', 30)); N = int(round(fps * float(os.environ.get('SPIN_SEC', 5))))
# the pivot on the icon's own centre (the visible meshes only: the hidden coin under it would put the axis off the icon,
# and the icon would swing sideways as it turns)
vis = [o for o in objs if not o.hide_render]
pts = [o.matrix_world @ v.co for o in vis for v in o.data.vertices]
C = (Vector([min(p[i] for p in pts) for i in range(3)]) + Vector([max(p[i] for p in pts) for i in range(3)])) / 2
piv = bpy.data.objects.new('spin_pivot', None); sc.collection.objects.link(piv); piv.location = C
bpy.context.view_layer.update()
for o in objs:
    mw = o.matrix_world.copy(); o.parent = piv; o.matrix_parent_inverse = piv.matrix_world.inverted(); o.matrix_world = mw
# the motion is the Lansy icon's own, read off artfc-lansy-site/3d/icon/lansy-icon.blend (its spin empty, frames 1–150 at
# 30 fps; dumped to lansy_spin_curve.json): one turn about the icon's own vertical axis, a small overshoot and a settle
import json
curve = [r[2] for r in json.load(open(os.path.join(os.path.dirname(bpy.data.filepath) or '.', 'lansy_spin_curve.json')))]
up = (S['turn'].to_3x3() @ Vector((0, 1, 0))).normalized()   # the icon's own vertical axis, as it stands in the shot
from mathutils import Quaternion
piv.rotation_mode = 'QUATERNION'; N = len(curve)
for f, ang in enumerate(curve):
    piv.rotation_quaternion = Quaternion(up, ang); piv.keyframe_insert('rotation_quaternion', frame=f)
for fc in piv.animation_data.action.fcurves if hasattr(piv.animation_data.action, 'fcurves') else []:
    for k in fc.keyframe_points: k.interpolation = 'LINEAR'
sc.frame_start, sc.frame_end = 0, N - 1; sc.render.fps = 30
out = os.environ['FRAMES_OUT']; os.makedirs(out, exist_ok=True)
sc.render.filepath = out + '/f_'; sc.render.image_settings.color_depth = '8'
sc.render.use_overwrite = False   # a crashed run resumes where it stopped
bpy.ops.render.render(animation=True); print('RENDERED spin', N, out)
