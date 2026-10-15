# Rubric icons in 3D, the same build as the café icon (disc_icon_full): Hugeicons paths (from the landing's industry chips, an
# 18-unit grid scaled to 24), the true outline of the strokes at the coin's stroke (2.4 units at 4 mm), raised as a rounded
# relief on both sides, set in exactly the café icon's place. Saved to 3d/models/rubric_icons.blend as disc_icon_<name>;
# studio_bk.py loads them with TARGET=icon ICON=<name>.
#   Blender -b 3d/lansy-3d-test.blend -P 3d/rubric_icons.py
import bpy, re, os
from mathutils import Matrix, Vector
ROOT = os.path.dirname(os.path.abspath(__file__))
src = open(f'{ROOT}/build_meshes.py').read(); ns = {}
exec(compile(src[:src.index('# ---- scene')], 'build_meshes', 'exec'), ns)   # the builders, not the scene
ns['oval_ring'] = lambda *a, **k: None                                         # the café icon's oval: not these icons'
ICONS = {   # @hugeicons/core-free-icons via the landing's chips (viewBox 18)
 'retail': ["M2.49264 9.75848C2.75543 7.50675 3.1394 5.81838 3.49547 4.61888C3.78746 3.63533 3.93344 3.14356 4.53212 2.69678C5.1308 2.25 5.74273 2.25 6.96657 2.25H11.0335C12.2573 2.25 12.8693 2.25 13.4679 2.69678C14.0666 3.14356 14.2126 3.63533 14.5046 4.61888C14.8607 5.81838 15.2446 7.50675 15.5074 9.75848C15.8171 12.4123 15.9719 13.7392 15.077 14.7446C14.1821 15.75 12.7319 15.75 9.8313 15.75H8.1687C5.26817 15.75 3.81789 15.75 2.92298 14.7446C2.02808 13.7392 2.18294 12.4123 2.49264 9.75848Z", "M6.75 5.25C6.75 6.49264 7.75732 7.5 9 7.5C10.2427 7.5 11.25 6.49264 11.25 5.25"],
 'clinics': ["M2 12.5625C2 9.46891 2 7.92211 3.02513 6.96106C4.05025 6 5.70017 6 9 6H15C18.2998 6 19.9497 6 20.9749 6.96106C22 7.92211 22 9.46891 22 12.5625V14.4375C22 17.5311 22 19.0779 20.9749 20.0389C19.9497 21 18.2998 21 15 21H9C5.70017 21 4.05025 21 3.02513 20.0389C2 19.0779 2 17.5311 2 14.4375V12.5625Z", "M9 13.5H15M12 10.5L12 16.5", "M17 6C17 3.518 16.482 3 14 3H10C7.518 3 7 3.518 7 6"],
 'schools': ["M1.49805 5.99958C1.49805 7.00606 7.57023 9.75012 8.98878 9.75012C10.4074 9.75012 16.4796 7.00606 16.4796 5.99958C16.4796 4.99309 10.4074 2.24902 8.98878 2.24902C7.57023 2.24902 1.49805 4.99309 1.49805 5.99958Z", "M4.49414 8.25L5.43261 12.6001C5.49689 12.8981 5.64527 13.1765 5.89272 13.3541C7.55902 14.5499 10.4181 14.5499 12.0844 13.3541C12.3319 13.1765 12.4803 12.8981 12.5446 12.6001L13.483 8.25", "M15.3576 7.12451V12.3753M15.3576 12.3753C14.7643 13.4602 14.502 14.0415 14.2355 15.0007C14.1777 15.342 14.2236 15.514 14.4585 15.6667C14.5539 15.7287 14.6686 15.7508 14.7823 15.7508H15.9213C16.0423 15.7508 16.1645 15.7255 16.2642 15.6567C16.4826 15.5059 16.5387 15.3405 16.4796 15.0007C16.246 14.11 15.9485 13.5011 15.3576 12.3753Z"],
 'callcenters': ["M15 12C15 10.8954 15.8954 10 17 10C19.2091 10 21 11.7909 21 14C21 16.2091 19.2091 18 17 18C15.8954 18 15 17.1046 15 16V12Z", "M9 12C9 10.8954 8.10457 10 7 10C4.79086 10 3 11.7909 3 14C3 16.2091 4.79086 18 7 18C8.10457 18 9 17.1046 9 16V12Z", "M3 14V11C3 6.02944 7.02944 2 12 2C16.9706 2 21 6.02944 21 11V15.8462C21 17.8545 21 18.8586 20.6476 19.6417C20.2465 20.5329 19.5329 21.2465 18.6417 21.6476C17.8586 22 16.8545 22 14.8462 22H12"],
 'hotels': ["M22 17.5H2", "M22 21V16C22 14.1144 22 13.1716 21.4142 12.5858C20.8284 12 19.8856 12 18 12H6C4.11438 12 3.17157 12 2.58579 12.5858C2 13.1716 2 14.1144 2 16V21", "M11 12V10.2134C11 9.83272 10.9428 9.70541 10.6497 9.55538C10.0395 9.24292 9.29865 9 8.5 9C7.70135 9 6.96055 9.24292 6.35025 9.55538C6.05721 9.70541 6 9.83272 6 10.2134L6 12", "M18 12V10.2134C18 9.83272 17.9428 9.70541 17.6497 9.55538C17.0395 9.24292 16.2987 9 15.5 9C14.7013 9 13.9605 9.24292 13.3503 9.55538C13.0572 9.70541 13 9.83272 13 10.2134L13 12", "M21 12V7.36057C21 6.66893 21 6.32311 20.8079 5.99653C20.6157 5.66995 20.342 5.50091 19.7944 5.16283C17.5869 3.79978 14.8993 3 12 3C9.10067 3 6.41314 3.79978 4.20558 5.16283C3.65804 5.50091 3.38427 5.66995 3.19213 5.99653C3 6.32311 3 6.66893 3 7.36057V12"],
}
GRID = {'hotels': 24, 'clinics': 24, 'callcenters': 24}   # straight from the package (BedDoubleIcon, FirstAidKitIcon, HeadsetIcon), on the 24 grid
SWS = {'clinics': float(os.environ.get('SW_CLINICS', 2.4))}   # a stroke per icon where 2.4 would close a gap
def to24(paths, grid=18):   # 18 → 24 grid; each subpath its own polyline; Z closes back to its start
    out = []
    for d in paths:
        d = re.sub(r'-?\d*\.?\d+', lambda m: f'{float(m.group()) * 24 / grid:.5f}', d)
        for sub in re.split(r'(?=M)', d):
            sub = sub.strip()
            if not sub: continue
            if 'Z' in sub:
                x, y = re.findall(r'-?\d*\.?\d+', sub)[:2]; sub = sub.replace('Z', f'L{x} {y}')
            out.append(sub)
    return out
# the café icon's build values
S = .004; R, Tk, CH = .065, .020 / 3, .002; SW = 2.4; h = SW / 2 * S; z0 = Tk - .0005; zw = Tk + .0006; a = .9 * h
coll = bpy.data.collections.new('rubric_tmp'); bpy.context.scene.collection.children.link(coll)
# where the café icon stands: the flat disc rebuilt, matched vertex for vertex to the placed one
flat_disc = ns['revolve'](ns['support'](ns['fillet_poly']([(0, 0), (R, 0), (R, Tk - CH), (R - CH, Tk), (0, Tk)], {1: .003, 2: .0006, 3: .0006})), 192, '_flat_disc', coll)
Rx = Matrix.Rotation(__import__('math').radians(78), 4, 'X'); placed = bpy.data.objects['disc_base']
d = placed.matrix_world @ placed.data.vertices[0].co - Rx @ flat_disc.data.vertices[0].co
M = Matrix.Translation(d) @ Rx; print('PLACE offset', tuple(round(v, 6) for v in d))
made = []
ONLY = os.environ.get('ONLY')
for name, paths in ICONS.items():
    if ONLY and name not in ONLY.split(','): continue
    ns['ICON_PATHS'] = to24(paths, GRID.get(name, 18)); sw = SWS.get(name, SW); hh = sw / 2 * S
    loops, inside, _ = ns['icon_outline'](S, sw)
    o = ns['icon_relief'](loops, inside, hh, z0, zw, .9 * hh, coll, f'disc_icon_{name}', both=True)
    o.data.transform(M); ns['smooth'](o, 50); r = ns['check'](o); print('BUILT', name, r['ok'], r['normals'], r['dims_mm']); made.append(o)
os.makedirs(f'{ROOT}/models', exist_ok=True)
OUTB = os.environ.get('OUTB', f'{ROOT}/models/rubric_icons.blend')
if os.path.exists(OUTB) and ONLY:   # keep the icons not rebuilt
    with bpy.data.libraries.load(OUTB) as (src_, dst_): dst_.objects = [n for n in src_.objects if n not in {o.name for o in made}]
    made += [o for o in dst_.objects if o]
bpy.data.libraries.write(OUTB, set(made) | {o.data for o in made}, fake_user=True)
print('SAVED', [o.name for o in made])
