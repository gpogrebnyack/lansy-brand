# BlenderKit's own material preview: the "Ball complex" in the add-on's thumbnailer scene, with a material (env MAT, OUT)
import bpy, os
s = bpy.context.scene; BALL = os.environ.get('BALL', 'complex')   # BALL=simple: the plain sphere
s.collection.children['Ball' if BALL == 'simple' else 'Ball complex'].hide_render = False
img = bpy.data.images['interior.exr']; img.filepath = os.path.join(bpy.utils.resource_path('LOCAL'), 'datafiles/studiolights/world/interior.exr'); img.reload()
path, name = os.environ['MAT'].split('::')
with bpy.data.libraries.load(path) as (src, dst): dst.materials = [name]
# KEEP_INNER=1: the complex ball's inner core keeps its checker, so a glass shows what is behind it
parts = ('MaterialPreview.005',) if BALL == 'simple' else (('MaterialPreview.008',) if os.environ.get('KEEP_INNER') else ('MaterialPreview.008', 'inner'))
for n in parts: bpy.data.objects[n].material_slots[0].material = dst.materials[0]
if os.environ.get('ANISO'):   # the brushing strength we use for this material (bk.json 'aniso')
    def _a(nt):
        for n in nt.nodes:
            if n.type == 'BSDF_PRINCIPLED' and not n.inputs['Anisotropic'].is_linked: n.inputs['Anisotropic'].default_value = float(os.environ['ANISO'])
            if n.type == 'GROUP' and n.node_tree: _a(n.node_tree)
    _a(dst.materials[0].node_tree)
if os.environ.get('INNER') and BALL == 'simple':   # a white ball inside, so a frosted glass shows its depth
    ob = bpy.data.objects['MaterialPreview.005']
    s.collection.children['Ball'].hide_viewport = False; bpy.context.view_layer.update()   # hidden collections aren't evaluated
    from mathutils import Vector
    dg = bpy.context.evaluated_depsgraph_get(); oe = ob.evaluated_get(dg); me = oe.to_mesh()
    P = [oe.matrix_world @ v.co for v in me.vertices]; oe.to_mesh_clear()
    lo = Vector([min(p[i] for p in P) for i in range(3)]); hi = Vector([max(p[i] for p in P) for i in range(3)])
    c = (lo + hi) / 2; R = (hi.x - lo.x) / 2 * float(os.environ['INNER'])
    bpy.ops.mesh.primitive_uv_sphere_add(radius=R, location=c, segments=96, ring_count=48); inn = bpy.context.active_object
    bpy.ops.object.shade_smooth()
    wm = bpy.data.materials.new('inner white'); wm.use_nodes = True; wb = wm.node_tree.nodes['Principled BSDF']
    wb.inputs['Base Color'].default_value = (.9, .9, .9, 1); wb.inputs['Roughness'].default_value = .35
    wb.inputs['Emission Color'].default_value = (1, 1, 1, 1); wb.inputs['Emission Strength'].default_value = float(os.environ.get('INNER_GLOW', 0))
    if os.environ.get('GLASS_T'):   # the glass's transmission, raised so what is inside shows
        for n in dst.materials[0].node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED': n.inputs['Transmission Weight'].default_value = float(os.environ['GLASS_T'])
    inn.data.materials.append(wm)
if os.environ.get('GLASS_T') and not os.environ.get('INNER'):
    for n in dst.materials[0].node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED': n.inputs['Transmission Weight'].default_value = float(os.environ['GLASS_T'])
s.cycles.device = 'GPU'; s.render.resolution_x = s.render.resolution_y = 1200
s.render.image_settings.file_format = 'PNG'; s.render.image_settings.color_mode = 'RGBA'
s.render.filepath = os.environ['OUT']; bpy.ops.render.render(write_still=True); print('RENDERED ball')
